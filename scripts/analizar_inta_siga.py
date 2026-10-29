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
VIRASORO = (-28.05, -56.02)
MAX_DISTANCE_KM = 250
MAX_NEAR_STATIONS = 12
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
near_candidates = []
def distance_km(a, b):
    lat1, lon1 = map(math.radians, a); lat2, lon2 = map(math.radians, b)
    dlat, dlon = lat2-lat1, lon2-lon1
    h = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    return 6371.0088 * 2 * math.asin(math.sqrt(min(1, h)))

for item in cat.get("estaciones", []):
    m = item.get("metadata_origen", {})
    sid = str(item.get("id_estacion") or m.get("idInterno") or m.get("id") or "")
    if sid:
        station_info[sid] = m
        try:
            d = distance_km(VIRASORO, (float(m["latitud"]), float(m["longitud"])))
            if math.isfinite(d) and d <= MAX_DISTANCE_KM:
                near_candidates.append((d, sid))
        except (KeyError, TypeError, ValueError):
            pass
near_candidates.sort()
near_candidates = near_candidates[:MAX_NEAR_STATIONS]
TARGET_IDS = {sid for _, sid in near_candidates}
near_distances = {sid: round(d, 2) for d, sid in near_candidates}

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
# Recompute yearly summaries using only station-date keys that occur once.
# Any station-date with duplicates is excluded entirely, not arbitrarily deduplicated.
yearly = {}
with gzip.open(SOURCE, "rt", encoding="utf-8-sig", newline="") as src:
    for row in csv.DictReader(src):
        sid = (row.get("id_estacion") or "").strip()
        dt = parse_date(row.get("fecha"))
        if not sid or not dt or (sid, dt.isoformat()) in duplicate_keys:
            continue
        p = number(row.get("precipitacion_pluviometrica"))
        ykey = (sid, dt.year)
        y = yearly.setdefault(ykey, {"id_estacion":sid,"anio":dt.year,"registros_fecha":0,
            "precip_pluviometrica_validos":0,"precip_pluviometrica_faltantes":0,
            "suma_valores_precip_pluviometrica":0.0,"max_valor_registro":None})
        y["registros_fecha"] += 1
        if p is None:
            y["precip_pluviometrica_faltantes"] += 1
        else:
            y["precip_pluviometrica_validos"] += 1
            y["suma_valores_precip_pluviometrica"] += p
            y["max_valor_registro"] = p if y["max_valor_registro"] is None else max(y["max_valor_registro"], p)

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
    "criterio_seleccion_estaciones": {"coordenada_referencia": {"latitud": VIRASORO[0], "longitud": VIRASORO[1]}, "radio_maximo_km": MAX_DISTANCE_KM, "maximo_estaciones": MAX_NEAR_STATIONS, "distancias_km": near_distances},
    "claves_estacion_fecha_duplicadas_excluidas_de_agregados": len(duplicate_keys),
    "archivos_generados": [OUT_SUMMARY.name, OUT_YEARLY.name, OUT_NEAR.name],
    "advertencia": "Las sumas anuales son exploratorias: confirmar frecuencia y unidad de la variable antes de interpretarlas como milímetros acumulados. Los duplicados de estación-fecha se reportan para auditoría, no se eliminan."
}
OUT_META.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(meta, ensure_ascii=False, indent=2))
