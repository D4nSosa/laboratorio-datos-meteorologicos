#!/usr/bin/env python3
"""Valida agregados ERA5 y produce gráficos y estadísticas reproducibles."""
from __future__ import annotations

import json
import math
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "datos" / "virasoro_era5"
FIGURES = ROOT / "investigaciones" / "01-precipitacion-virasoro" / "graficos"


def numeric_finite(series: pd.Series, label: str) -> pd.Series:
    values = pd.to_numeric(series, errors="coerce")
    if values.isna().any() or not values.map(lambda x: math.isfinite(float(x))).all():
        raise SystemExit(f"{label} contiene valores no numéricos o no finitos.")
    if (values < 0).any():
        raise SystemExit(f"{label} contiene precipitaciones negativas.")
    return values


def main() -> None:
    annual_path = DATA / "precipitacion_anual.csv"
    monthly_path = DATA / "precipitacion_mensual.csv"
    if not annual_path.exists() or not monthly_path.exists():
        raise SystemExit("Primero ejecutá descargar_era5.py para generar los CSV.")
    annual = pd.read_csv(annual_path)
    monthly = pd.read_csv(monthly_path)
    if annual.empty or monthly.empty:
        raise SystemExit("Los archivos de entrada están vacíos.")
    required_annual = {"anio", "precipitacion_anual_mm"}
    required_monthly = {"anio", "mes", "precipitacion_mm"}
    if not required_annual.issubset(annual.columns) or not required_monthly.issubset(monthly.columns):
        raise SystemExit("Los CSV no contienen las columnas requeridas.")
    annual["anio"] = pd.to_numeric(annual["anio"], errors="coerce")
    if annual["anio"].isna().any() or annual["anio"].duplicated().any():
        raise SystemExit("El resumen anual contiene años inválidos o duplicados.")
    annual["anio"] = annual["anio"].astype(int)
    if annual["anio"].tolist() != list(range(1991, 2026)):
        raise SystemExit("El resumen anual debe cubrir exactamente los años 1991–2025 en orden.")
    annual["precipitacion_anual_mm"] = numeric_finite(annual["precipitacion_anual_mm"], "Precipitación anual")
    monthly["anio"] = pd.to_numeric(monthly["anio"], errors="coerce")
    monthly["mes"] = pd.to_numeric(monthly["mes"], errors="coerce")
    if monthly[["anio", "mes"]].isna().any().any():
        raise SystemExit("El resumen mensual contiene años o meses inválidos.")
    monthly[["anio", "mes"]] = monthly[["anio", "mes"]].astype(int)
    if monthly.duplicated(["anio", "mes"]).any():
        raise SystemExit("Hay combinaciones año/mes duplicadas.")
    if not monthly["anio"].between(1991, 2025).all() or not monthly["mes"].between(1, 12).all():
        raise SystemExit("Hay años o meses fuera del período esperado.")
    counts = monthly.groupby("anio")["mes"].agg(list)
    if set(counts.index) != set(range(1991, 2026)) or not all(sorted(v) == list(range(1, 13)) for v in counts):
        raise SystemExit("Cada año debe contener exactamente los doce meses.")
    monthly["precipitacion_mm"] = numeric_finite(monthly["precipitacion_mm"], "Precipitación mensual")
    recomputed = monthly.groupby("anio")["precipitacion_mm"].sum().reindex(annual["anio"]).to_numpy()
    if not ((abs(recomputed - annual["precipitacion_anual_mm"].to_numpy()) <= 0.02).all()):
        raise SystemExit("Los totales anuales no coinciden con la suma de los totales mensuales.")

    FIGURES.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(11, 5.5))
    ax.plot(annual["anio"], annual["precipitacion_anual_mm"], linewidth=1.3)
    ax.set(title="Precipitación anual — ERA5, entorno de Gobernador Virasoro", xlabel="Año", ylabel="Precipitación anual (mm)")
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    fig.savefig(FIGURES / "precipitacion_anual_era5.png", dpi=180)
    fig.savefig(FIGURES / "precipitacion_anual_era5.svg")
    plt.close(fig)

    climate = monthly.groupby("mes")["precipitacion_mm"].mean().reindex(range(1, 13))
    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.bar(climate.index, climate.values)
    ax.set(title="Promedio mensual de precipitación — ERA5", xlabel="Mes", ylabel="Promedio del total mensual (mm)", xticks=list(range(1, 13)), xticklabels=["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"])
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(FIGURES / "climatologia_mensual_era5.png", dpi=180)
    fig.savefig(FIGURES / "climatologia_mensual_era5.svg")
    plt.close(fig)

    stats = annual["precipitacion_anual_mm"]
    summary = {
        "periodo": "1991-2025",
        "cantidad_anios": int(len(annual)),
        "media_anual_mm": round(float(stats.mean()), 2),
        "mediana_anual_mm": round(float(stats.median()), 2),
        "minimo": {"anio": int(annual.loc[stats.idxmin(), "anio"]), "precipitacion_anual_mm": round(float(stats.min()), 2)},
        "maximo": {"anio": int(annual.loc[stats.idxmax(), "anio"]), "precipitacion_anual_mm": round(float(stats.max()), 2)},
        "nota": "Estadísticas de reanálisis ERA5, no de una estación pluviométrica.",
    }
    (DATA / "resumen_estadistico.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\\n", encoding="utf-8")
    print("Validación de agregados ERA5 correcta; gráficos y resumen generados.")


if __name__ == "__main__":
    main()
