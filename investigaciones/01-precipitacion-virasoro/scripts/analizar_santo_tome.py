#!/usr/bin/env python3
"""Reproduce estadísticas del archivo público rainfall.json para Santo Tomé."""
from __future__ import annotations

import csv
import json
import math
import statistics
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "datos" / "fuente" / "rainfall.json"
OUT = ROOT / "datos"
SOURCE_URL = "https://raw.githubusercontent.com/deaeconomiactes/Precipitaciones-Lluvias/main/data/rainfall.json"
MONTHS = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]


def load_rows() -> list[dict]:
    if not SOURCE.exists():
        SOURCE.parent.mkdir(parents=True, exist_ok=True)
        try:
            response = requests.get(SOURCE_URL, timeout=45)
            response.raise_for_status()
            rows = response.json()
        except (requests.RequestException, ValueError) as exc:
            raise SystemExit(f"No se pudo descargar/decodificar la fuente: {exc}") from exc
        if not isinstance(rows, list):
            raise SystemExit("La fuente no devolvió una lista JSON.")
        SOURCE.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\\n", encoding="utf-8")
        print(f"Fuente descargada y guardada en: {SOURCE}")
    else:
        try:
            rows = json.loads(SOURCE.read_text(encoding="utf-8-sig"))
        except (OSError, json.JSONDecodeError) as exc:
            raise SystemExit(f"El archivo local rainfall.json no es JSON válido: {exc}") from exc
    if not isinstance(rows, list):
        raise SystemExit("rainfall.json debe contener una lista JSON.")
    return rows


def valid_months(row: dict) -> list[float] | None:
    values = row.get("months")
    if not isinstance(values, list) or len(values) != 12:
        return None
    parsed = []
    for value in values:
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(float(value)) or value < 0:
            return None
        parsed.append(float(value))
    return parsed


def main() -> None:
    rows = load_rows()
    filtered = []
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("department"), str):
            continue
        year = row.get("year")
        if isinstance(year, bool) or not isinstance(year, int):
            continue
        if "".join(row["department"].lower().split()) != "santotome":
            continue
        filtered.append((year, valid_months(row)))
    filtered.sort(key=lambda item: item[0])
    years = [year for year, _ in filtered]
    if len(years) != len(set(years)):
        raise SystemExit("La fuente contiene más de un registro para un año de Santo Tomé.")
    complete = [(year, months) for year, months in filtered if months is not None]
    if not complete:
        raise SystemExit("No hay años completos y válidos para Santo Tomé.")

    OUT.mkdir(parents=True, exist_ok=True)
    annual = [(year, round(sum(months), 2)) for year, months in complete]
    with (OUT / "santo_tome_totales_anuales.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f); writer.writerow(["anio", "precipitacion_total_mm"]); writer.writerows(annual)
    monthly_means = [round(statistics.mean(months[i] for _, months in complete), 2) for i in range(12)]
    with (OUT / "santo_tome_promedios_mensuales.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f); writer.writerow(["mes", "mes_nombre", "promedio_mm"]); writer.writerows((i + 1, MONTHS[i], monthly_means[i]) for i in range(12))
    with (OUT / "santo_tome_mayo_por_anio.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f); writer.writerow(["anio", "mayo_mm"]); writer.writerows((year, months[4]) for year, months in complete)

    values = [value for _, value in annual]
    print(f"Registros anuales Santo Tomé: {len(filtered)}")
    print(f"Años completos válidos usados: {len(complete)} ({complete[0][0]}–{complete[-1][0]})")
    print(f"Media anual: {statistics.mean(values):.2f} mm")
    print(f"Mediana anual: {statistics.median(values):.2f} mm")
    print(f"Mínimo: {min(annual, key=lambda item: item[1])}")
    print(f"Máximo: {max(annual, key=lambda item: item[1])}")


if __name__ == "__main__":
    main()
