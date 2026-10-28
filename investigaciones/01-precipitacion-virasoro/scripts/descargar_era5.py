#!/usr/bin/env python3
"""Descarga precipitación diaria ERA5 para el entorno de Gobernador Virasoro.

La serie es de reanálisis, no una observación pluviométrica local.
Coordenadas de consulta aproximadas del casco urbano; revisar la celda devuelta
por la API y documentarla antes de interpretar resultados.
"""
from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "datos" / "virasoro_era5"
LATITUDE = -28.05
LONGITUDE = -56.02
START_DATE = "1991-01-01"
# Usamos años completos hasta el último año cerrado. No mezclar un año parcial
# con totales anuales completos.
END_DATE = "2025-12-31"
API_URL = "https://archive-api.open-meteo.com/v1/archive"


def main() -> int:
    params = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "start_date": START_DATE,
        "end_date": END_DATE,
        "daily": "precipitation_sum",
        "timezone": "America/Argentina/Cordoba",
        "models": "era5",
    }
    response = requests.get(API_URL, params=params, timeout=90)
    response.raise_for_status()
    payload = response.json()
    if "daily" not in payload or not payload["daily"].get("time"):
        raise RuntimeError("La API no devolvió una serie diaria utilizable.")

    daily = pd.DataFrame({
        "fecha": pd.to_datetime(payload["daily"]["time"], errors="raise"),
        "precipitacion_mm": payload["daily"]["precipitation_sum"],
    })
    if daily["fecha"].duplicated().any():
        raise RuntimeError("La respuesta contiene fechas duplicadas.")
    expected_days = len(pd.date_range(START_DATE, END_DATE, freq="D"))
    if len(daily) != expected_days:
        raise RuntimeError(
            f"Serie incompleta: recibidos {len(daily)} de {expected_days} días. "
            "No se generan agregados como si estuviera completa."
        )
    if daily["precipitacion_mm"].isna().any():
        raise RuntimeError("Hay valores faltantes; revisar antes de agregar.")
    if (daily["precipitacion_mm"] < 0).any():
        raise RuntimeError("Hay valores negativos inesperados.")

    daily["anio"] = daily["fecha"].dt.year
    daily["mes"] = daily["fecha"].dt.month
    monthly = (daily.groupby(["anio", "mes"], as_index=False)
               ["precipitacion_mm"].sum())
    annual = (daily.groupby("anio", as_index=False)
              ["precipitacion_mm"].sum()
              .rename(columns={"precipitacion_mm": "precipitacion_anual_mm"}))
    monthly_climatology = (monthly.groupby("mes", as_index=False)
                           ["precipitacion_mm"].mean()
                           .rename(columns={
                               "precipitacion_mm": "media_mensual_mm"
                           }))

    OUT.mkdir(parents=True, exist_ok=True)
    daily.to_csv(OUT / "precipitacion_diaria.csv", index=False, date_format="%Y-%m-%d")
    monthly.to_csv(OUT / "precipitacion_mensual.csv", index=False)
    annual.to_csv(OUT / "precipitacion_anual.csv", index=False)
    monthly_climatology.to_csv(OUT / "climatologia_mensual.csv", index=False)

    metadata = {
        "fuente": "Open-Meteo Historical Weather API",
        "dataset": "ERA5",
        "api_url": API_URL,
        "fecha_consulta_utc": pd.Timestamp.now(tz="UTC").isoformat(),
        "coordenadas_solicitadas": {
            "latitud": LATITUDE, "longitud": LONGITUDE
        },
        "coordenadas_celda_devuelta": {
            "latitud": payload.get("latitude"),
            "longitud": payload.get("longitude"),
            "elevacion_m": payload.get("elevation"),
        },
        "periodo": {"inicio": START_DATE, "fin": END_DATE},
        "variable": "precipitation_sum",
        "unidad": "mm",
        "cantidad_dias": int(len(daily)),
        "licencia_fuente": "CC BY 4.0 (ver documentación de Open-Meteo)",
        "advertencia": (
            "ERA5 es reanálisis: combina observaciones y modelos. No equivale "
            "a una medición de pluviómetro de Gobernador Virasoro."
        ),
    }
    (OUT / "metadatos.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Serie guardada en: {OUT}")
    print(f"Días: {len(daily)} | años completos: {annual['anio'].nunique()}")
    print(f"Celda ERA5 devuelta: {payload.get('latitude')}, {payload.get('longitude')}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except requests.RequestException as exc:
        print(f"Error consultando Open-Meteo: {exc}", file=sys.stderr)
        raise SystemExit(1)
