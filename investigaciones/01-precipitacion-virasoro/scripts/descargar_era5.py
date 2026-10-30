#!/usr/bin/env python3
"""Descarga y valida precipitación diaria ERA5 para el entorno de Virasoro.

ERA5 es un reanálisis espacial, no una observación pluviométrica local.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "datos" / "virasoro_era5"
LATITUDE = -28.05
LONGITUDE = -56.02
START_DATE = "1991-01-01"
END_DATE = "2025-12-31"
API_URL = "https://archive-api.open-meteo.com/v1/archive"


def validate_daily(daily: pd.DataFrame) -> None:
    """Fail closed unless every expected date has one finite nonnegative value."""
    expected = pd.date_range(START_DATE, END_DATE, freq="D")
    if daily.empty:
        raise RuntimeError("La respuesta diaria está vacía.")
    if daily["fecha"].duplicated().any():
        raise RuntimeError("La respuesta contiene fechas duplicadas.")
    if not daily["fecha"].equals(pd.Series(expected, name="fecha")):
        received = pd.DatetimeIndex(daily["fecha"])
        missing = expected.difference(received)
        unexpected = received.difference(expected)
        raise RuntimeError(
            "La secuencia de fechas no coincide con el período esperado. "
            f"Faltantes: {len(missing)}; fuera del período: {len(unexpected)}."
        )
    values = pd.to_numeric(daily["precipitacion_mm"], errors="coerce")
    if values.isna().any() or not values.map(lambda x: pd.notna(x) and abs(float(x)) != float("inf")).all():
        raise RuntimeError("La precipitación contiene valores no numéricos o no finitos.")
    if (values < 0).any():
        raise RuntimeError("Hay valores negativos inesperados.")


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
    if not isinstance(payload, dict) or not isinstance(payload.get("daily"), dict):
        raise RuntimeError("La API no devolvió el objeto diario esperado.")
    times = payload["daily"].get("time")
    values = payload["daily"].get("precipitation_sum")
    if not isinstance(times, list) or not isinstance(values, list) or len(times) != len(values):
        raise RuntimeError("La API no devolvió columnas diarias alineadas.")

    daily = pd.DataFrame({
        "fecha": pd.to_datetime(times, errors="raise"),
        "precipitacion_mm": pd.to_numeric(values, errors="coerce"),
    }).sort_values("fecha", kind="stable").reset_index(drop=True)
    validate_daily(daily)

    daily["anio"] = daily["fecha"].dt.year
    daily["mes"] = daily["fecha"].dt.month
    monthly = daily.groupby(["anio", "mes"], as_index=False)["precipitacion_mm"].sum()
    annual = daily.groupby("anio", as_index=False)["precipitacion_mm"].sum().rename(
        columns={"precipitacion_mm": "precipitacion_anual_mm"}
    )
    if annual["anio"].tolist() != list(range(1991, 2026)):
        raise RuntimeError("Los totales anuales no cubren exactamente 1991–2025.")
    monthly_counts = monthly.groupby("anio")["mes"].agg(list)
    if not all(months == list(range(1, 13)) for months in monthly_counts):
        raise RuntimeError("Hay años sin los doce meses esperados.")

    monthly["precipitacion_mm"] = monthly["precipitacion_mm"].round(2)
    annual["precipitacion_anual_mm"] = annual["precipitacion_anual_mm"].round(2)
    climatology = monthly.groupby("mes", as_index=False)["precipitacion_mm"].mean().rename(
        columns={"precipitacion_mm": "media_mensual_mm"}
    )
    climatology["media_mensual_mm"] = climatology["media_mensual_mm"].round(2)
    if climatology["mes"].tolist() != list(range(1, 13)):
        raise RuntimeError("La climatología no contiene los doce meses.")

    OUT.mkdir(parents=True, exist_ok=True)
    DOCS_DATA = ROOT / "docs" / "datos"
    DOCS_DATA.mkdir(parents=True, exist_ok=True)
    daily.to_csv(OUT / "precipitacion_diaria.csv", index=False, date_format="%Y-%m-%d")
    monthly.to_csv(OUT / "precipitacion_mensual.csv", index=False)
    monthly.to_csv(DOCS_DATA / "precipitacion_mensual_era5.csv", index=False)
    annual.to_csv(OUT / "precipitacion_anual.csv", index=False)
    climatology.to_csv(OUT / "climatologia_mensual.csv", index=False)
    metadata = {
        "fuente": "Open-Meteo Historical Weather API",
        "dataset": "ERA5",
        "api_url": API_URL,
        "fecha_consulta_utc": pd.Timestamp.now(tz="UTC").isoformat(),
        "coordenadas_solicitadas": {"latitud": LATITUDE, "longitud": LONGITUDE},
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
        "advertencia": "ERA5 es reanálisis; no equivale a una medición de pluviómetro de Gobernador Virasoro.",
    }
    (OUT / "metadatos.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\\n", encoding="utf-8")
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
