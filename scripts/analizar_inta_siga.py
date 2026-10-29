#!/usr/bin/env python3
"""Audita cobertura del consolidado SIGA-INTA y extrae series útiles para Virasoro.

No imputa faltantes ni transforma los valores originales. Los totales anuales son
exploratorios y solo deben interpretarse después de confirmar unidad/frecuencia.
"""
import csv
import gzip
import json
import math
from collections import defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "datos/fuentes-externas/inta-siga"
SOURCE = DATA / "estaciones-observaciones.csv.gz"
CATALOG = DATA / "estaciones.json"
TARGET_IDS = {"A872909", "A872908", "A872971", "NH0423", "A872910", "NH0460", "A872916"}
OUT_SUMMARY = DATA / "estaciones-cobertura.csv"
OUT_YEARLY = DATA / "precipitacion-anual-estaciones.csv"
OUT_NEAR = DATA / "estaciones-cercanas-virasoro.csv.gz"
OUT_META = DATA / "analisis-cobertura.json"

def number(value):
    if value is None or not value.strip():
        return None
    try:
        x = float(value.replace(",", "."))
        return x if math.isfinite(x) else None
    except (ValueError, AttributeError):
        return None

def parse_date(value):
    if not value:
        return None
    try:
        return date.fromisoformat(value[:10])
    except ValueError:
        return None

with CATALOG.open(encoding="utf-8") as f:
    cat = json.load(f)
station_info = {}
for item in cat.get("estaciones", []):
    m = item.get("metadata_origen", {})
    sid = str(item.get("id_estacion") or m.get("idInterno") or m.get("id") or "")
    if sid:
        station_info[sid] = m

stats = {}
yearly = {}
near_rows = 0
invalid_dates = 0
duplicate_station_dates = 0
seen_station_dates = set()
header = None
with gzip.open(SOURCE, "rt", encoding="utf-8-sig", newline="") as src, \
     OUT_NEAR.open("wb") as raw_out, gzip.GzipFile(fileobj=raw_out, mode="wb", compresslevel=6, mtime=0) as gz_out:
    import io
    text_out = io.TextIOWrapper(gz_out, encoding="utf-8", newline="", write_through=True)
    writer_near = None
    reader = csv.DictReader(src)
    header = reader.fieldnames or []
    writer_near = csv.DictWriter(text_out, fieldnames=header, extrasaction="ignore")
    writer_near.writeheader()
    for row in reader:
        sid = (row.get("id_estacion") or "").strip()
        dt = parse_date(row.get("fecha"))
        if not sid:
            continue
        s = stats.setdefault(sid, {
            "id_estacion": sid, "registros": 0, "fecha_inicial": None, "fecha_final": None,
            "fechas_invalidas": 0, "precip_pluviometrica_validos": 0,
            "precip_pluviometrica_faltantes": 0, "precip_cronologica_validos": 0,
            "precip_cronologica_faltantes": 0, "precip_max30_validos": 0,
            "precip_pluviometrica_min": None, "precip_pluviometrica_max": None,
        })
        s["registros"] += 1
        if dt is None:
            s["fechas_invalidas"] += 1
            invalid_dates += 1
        else:
            ds = dt.isoformat()
            s["fecha_inicial"] = min(s["fecha_inicial"], ds) if s["fecha_inicial"] else ds
            s["fecha_final"] = max(s["fecha_final"], ds) if s["fecha_final"] else ds
            key = (sid, ds)
            if key in seen_station_dates:
                duplicate_station_dates += 1
            else:
                seen_station_dates.add(key)
        p = number(row.get("precipitacion_pluviometrica"))
        pc = number(row.get("precipitacion_cronologica"))
        p30 = number(row.get("precipitacion_maxima_30minutos"))
        for field, val, missing in [
            ("precip_pluviometrica_validos", p, "precip_pluviometrica_faltantes"),
            ("precip_cronologica_validos", pc, "precip_cronologica_faltantes"),
        ]:
            if val is None:
                s[missing] += 1
            else:
                s[field] += 1
        if p30 is not None:
            s["precip_max30_validos"] += 1
        if p is not None:
            s["precip_pluviometrica_min"] = p if s["precip_pluviometrica_min"] is None else min(s["precip_pluviometrica_min"], p)
            s["precip_pluviometrica_max"] = p if s["precip_pluviometrica_max"] is None else max(s["precip_pluviometrica_max"], p)
        if dt:
            ykey = (sid, dt.year)
            y = yearly.setdefault(ykey, {"id_estacion": sid, "anio": dt.year, "registros_fecha": 0, "precip_pluviometrica_validos": 0, "precip_pluviometrica_faltantes": 0, "suma_valores_precip_pluviometrica": 0.0, "max_valor_registro": None})
            y["registros_fecha"] += 1
            if p is not None:
                y["precip_pluviometrica_validos"] += 1
                y["suma_valores_precip_pluviometrica"] += p
                y["max_valor_registro"] = p if y["max_valor_registro"] is None else max(y["max_valor_registro"], p)
            else:
                y["precip_pluviometrica_faltantes"] += 1
        if sid in TARGET_IDS:
            writer_near.writerow(row)
            near_rows += 1
    text_out.flush()
    text_out.detach()

def station_row(s):
    m = station_info.get(s["id_estacion"], {})
    return {
        "id_estacion": s["id_estacion"], "nombre": m.get("nombre", ""),
        "localidad": m.get("localidad", ""), "provincia": m.get("provincia", ""),
        "latitud": m.get("latitud", ""), "longitud": m.get("longitud", ""),
        "tipo": m.get("tipo", ""), **s
    }

station_fields = ["id_estacion","nombre","localidad","provincia","latitud","longitud","tipo","registros","fecha_inicial","fecha_final","fechas_invalidas","precip_pluviometrica_validos","precip_pluviometrica_faltantes","precip_cronologica_validos","precip_cronologica_faltantes","precip_max30_validos","precip_pluviometrica_min","precip_pluviometrica_max"]
with OUT_SUMMARY.open("w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=station_fields, extrasaction="ignore")
    w.writeheader()
    for sid in sorted(stats):
        w.writerow(station_row(stats[sid]))
year_fields = ["id_estacion","nombre","localidad","provincia","anio","registros_fecha","precip_pluviometrica_validos","precip_pluviometrica_faltantes","suma_valores_precip_pluviometrica","max_valor_registro"]
with OUT_YEARLY.open("w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=year_fields, extrasaction="ignore")
    w.writeheader()
    for key in sorted(yearly):
        y = yearly[key]
        m = station_info.get(y["id_estacion"], {})
        y = {**y, "nombre": m.get("nombre",""), "localidad": m.get("localidad",""), "provincia": m.get("provincia","")}
        y["suma_valores_precip_pluviometrica"] = round(y["suma_valores_precip_pluviometrica"], 3)
        w.writerow(y)
meta = {
    "fuente": "estaciones-observaciones.csv.gz / consolidado comunitario basado en SIGA-INTA",
    "catalogo_estaciones": len(station_info),
    "estaciones_con_registros": len(stats),
    "filas_con_fecha_invalida": invalid_dates,
    "repeticiones_de_id_estacion_fecha_detectadas": duplicate_station_dates,
    "filas_extraidas_estaciones_cercanas_a_virasoro": near_rows,
    "ids_estaciones_extraidas": sorted(TARGET_IDS),
    "archivos_generados": [OUT_SUMMARY.name, OUT_YEARLY.name, OUT_NEAR.name],
    "advertencia": "Las sumas anuales son exploratorias: confirmar frecuencia y unidad de la variable antes de interpretarlas como milímetros acumulados. Los duplicados de estación-fecha se reportan para auditoría, no se eliminan."
}
OUT_META.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(meta, ensure_ascii=False, indent=2))
