#!/usr/bin/env python3
"""Resume los CSV generados por descargar_era5.py y produce gráficos."""
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "datos" / "virasoro_era5"
FIGURES = ROOT / "investigaciones" / "01-precipitacion-virasoro" / "graficos"


def main() -> None:
    annual_path = DATA / "precipitacion_anual.csv"
    monthly_path = DATA / "precipitacion_mensual.csv"
    if not annual_path.exists() or not monthly_path.exists():
        raise SystemExit(
            "Primero ejecutá: python investigaciones/01-precipitacion-virasoro/"
            "scripts/descargar_era5.py"
        )
    annual = pd.read_csv(annual_path)
    monthly = pd.read_csv(monthly_path)
    if annual.empty or monthly.empty:
        raise SystemExit("Los archivos de entrada están vacíos.")
    if annual["anio"].duplicated().any():
        raise SystemExit("Hay años duplicados en el resumen anual.")
    FIGURES.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(11, 5.5))
    ax.plot(annual["anio"], annual["precipitacion_anual_mm"], linewidth=1.3)
    ax.set(title="Precipitación anual — ERA5, entorno de Gobernador Virasoro",
           xlabel="Año", ylabel="Precipitación anual (mm)")
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    fig.savefig(FIGURES / "precipitacion_anual_era5.png", dpi=180)
    plt.close(fig)

    climate = monthly.groupby("mes")["precipitacion_mm"].mean().reindex(range(1, 13))
    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.bar(climate.index, climate.values)
    ax.set(title="Promedio mensual de precipitación — ERA5",
           xlabel="Mes", ylabel="Promedio del total mensual (mm)",
           xticks=list(range(1, 13)),
           xticklabels=["Ene", "Feb", "Mar", "Abr", "May", "Jun",
                        "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"])
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(FIGURES / "climatologia_mensual_era5.png", dpi=180)
    plt.close(fig)

    summary = {
        "periodo": f"{int(annual['anio'].min())}-{int(annual['anio'].max())}",
        "cantidad_anios": int(annual["anio"].nunique()),
        "media_anual_mm": round(float(annual["precipitacion_anual_mm"].mean()), 2),
        "mediana_anual_mm": round(float(annual["precipitacion_anual_mm"].median()), 2),
        "minimo": annual.loc[annual["precipitacion_anual_mm"].idxmin()].to_dict(),
        "maximo": annual.loc[annual["precipitacion_anual_mm"].idxmax()].to_dict(),
        "nota": "Estadísticas de reanálisis ERA5, no de una estación pluviométrica.",
    }
    pd.Series(summary, dtype="object").to_json(
        DATA / "resumen_estadistico.json", force_ascii=False, indent=2
    )
    print("Gráficos y resumen guardados. Interpretá los resultados junto con los metadatos.")


if __name__ == "__main__":
    main()
