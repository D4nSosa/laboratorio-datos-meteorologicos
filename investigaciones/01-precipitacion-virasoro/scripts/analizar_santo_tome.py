#!/usr/bin/env python3
"""Reproduce estadísticas del archivo rainfall.json para Santo Tome.

Descarga la fuente pública si no existe una copia local. El script no completa meses faltantes.
"""
import json
from pathlib import Path
import csv
import statistics
import requests

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "datos" / "fuente" / "rainfall.json"
OUT = ROOT / "datos"
SOURCE_URL = "https://raw.githubusercontent.com/deaeconomiactes/Precipitaciones-Lluvias/main/data/rainfall.json"
MONTHS = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
          "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]


def main():
    if not SOURCE.exists():
        SOURCE.parent.mkdir(parents=True, exist_ok=True)
        try:
            response = requests.get(SOURCE_URL, timeout=45)
            response.raise_for_status()
            # Validar JSON antes de guardar para no conservar respuestas HTML/error.
            rows = response.json()
            if not isinstance(rows, list):
                raise ValueError("La fuente no devolvió una lista JSON.")
            SOURCE.write_text(
                json.dumps(rows, ensure_ascii=False),
                encoding="utf-8",
            )
            print(f"Fuente descargada y guardada en: {SOURCE}")
        except (requests.RequestException, ValueError) as exc:
            raise SystemExit(
                f"No se pudo descargar/validar la fuente ({SOURCE_URL}): {exc}"
            ) from exc
    else:
        rows = json.loads(SOURCE.read_text(encoding="utf-8-sig"))
    santo_tome = sorted(
        [
            r for r in rows
            if isinstance(r, dict)
            and isinstance(r.get("department"), str)
            and "".join(r["department"].lower().split()) == "santotome"
            and isinstance(r.get("year"), int)
        ],
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
