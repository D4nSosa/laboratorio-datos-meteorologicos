#!/usr/bin/env python3
"""Reproduce estadísticas del archivo rainfall.json para Santo Tome.

Descarga manualmente el archivo desde:
https://raw.githubusercontent.com/deaeconomiactes/Precipitaciones-Lluvias/main/data/rainfall.json
y guárdalo como datos/fuente/rainfall.json. El script no completa meses faltantes.
"""
import json
from pathlib import Path
import csv
import statistics

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "datos" / "fuente" / "rainfall.json"
OUT = ROOT / "datos"
MONTHS = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
          "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]


def main():
    if not SOURCE.exists():
        raise SystemExit(
            f"No se encontró {SOURCE}. Descargá rainfall.json desde el repositorio "
            "fuente y guardalo en esa ruta."
        )
    rows = json.loads(SOURCE.read_text(encoding="utf-8-sig"))
    santo_tome = sorted(
        [r for r in rows if "".join(r["department"].lower().split()) == "santotome"],
        key=lambda r: r["year"],
    )
    complete = [
        r for r in santo_tome
        if len(r.get("months", [])) == 12
        and all(v is not None for v in r["months"])
    ]
    if not complete:
        raise SystemExit("No hay años completos para Santo Tome.")

    OUT.mkdir(parents=True, exist_ok=True)
    annual = []
    for row in complete:
        # Se recalcula desde los meses en lugar de confiar en el total precalculado.
        annual.append((row["year"], round(sum(row["months"]), 2)))
    with (OUT / "santo_tome_totales_anuales.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["anio", "precipitacion_total_mm"])
        writer.writerows(annual)

    monthly_means = [
        round(statistics.mean(row["months"][i] for row in complete), 2)
        for i in range(12)
    ]
    with (OUT / "santo_tome_promedios_mensuales.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["mes", "mes_nombre", "promedio_mm"])
        writer.writerows((i + 1, MONTHS[i], monthly_means[i]) for i in range(12))

    with (OUT / "santo_tome_mayo_por_anio.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["anio", "mayo_mm"])
        writer.writerows((row["year"], row["months"][4]) for row in complete)

    values = [v for _, v in annual]
    print(f"Registros anuales Santo Tome: {len(santo_tome)}")
    print(f"Años completos usados: {len(complete)} ({complete[0]['year']}–{complete[-1]['year']})")
    print(f"Media anual: {statistics.mean(values):.2f} mm")
    print(f"Mediana anual: {statistics.median(values):.2f} mm")
    print(f"Mínimo: {min(annual, key=lambda x: x[1])}")
    print(f"Máximo: {max(annual, key=lambda x: x[1])}")
    print("Archivos CSV escritos en", OUT)


if __name__ == "__main__":
    main()
