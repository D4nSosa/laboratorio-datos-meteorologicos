#!/usr/bin/env python3
"""Audita cobertura del consolidado comunitario SIGA-INTA.
Los agregados son exploratorios; se excluyen fechas estación-día duplicadas.
"""
import csv, gzip, json, math, io
from datetime import date
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"datos/fuentes-externas/inta-siga"
SOURCE=DATA/"estaciones-observaciones.csv.gz"
CATALOG=DATA/"estaciones.json"
OUT_SUMMARY=DATA/"estaciones-cobertura.csv"
OUT_YEARLY=DATA/"precipitacion-anual-estaciones.csv"
OUT_NEAR=DATA/"estaciones-cercanas-virasoro.csv.gz"
OUT_META=DATA/"analisis-cobertura.json"
VIRASORO=(-28.05,-56.02)
MAX_DISTANCE_KM=250
MAX_NEAR_STATIONS=12

def number(value):
    if value is None or not value.strip(): return None
    try:
        x=float(value.replace(",","."))
        return x if math.isfinite(x) else None
    except (ValueError,AttributeError): return None

def parse_date(value):
    try: return date.fromisoformat(value[:10]) if value else None
    except (ValueError,TypeError): return None

def distance_km(a,b):
    lat1,lon1=map(math.radians,a); lat2,lon2=map(math.radians,b)
    dlat,dlon=lat2-lat1,lon2-lon1
    h=math.sin(dlat/2)**2+math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    return 6371.0088*2*math.asin(math.sqrt(min(1,h)))

catalog=json.loads(CATALOG.read_text(encoding="utf-8"))
station_info={}
candidates=[]
for item in catalog.get("estaciones",[]):
    m=item.get("metadata_origen",{})
    sid=str(item.get("id_estacion") or m.get("idInterno") or m.get("id") or "")
    if not sid: continue
    station_info[sid]=m
    try:
        d=distance_km(VIRASORO,(float(m["latitud"]),float(m["longitud"])))
        if math.isfinite(d) and d<=MAX_DISTANCE_KM: candidates.append((d,sid))
    except (KeyError,TypeError,ValueError): pass
candidates.sort()
near=candidates[:MAX_NEAR_STATIONS]
near_ids={sid for d,sid in near}
near_distances={sid:round(d,2) for d,sid in near}

stats={}
seen_dates=set()
duplicate_dates=set()
duplicate_rows=invalid_dates=rows_total=near_rows=0
with gzip.open(SOURCE,"rt",encoding="utf-8-sig",newline="") as src, OUT_NEAR.open("wb") as raw, gzip.GzipFile(fileobj=raw,mode="wb",compresslevel=6,mtime=0) as gz:
    reader=csv.DictReader(src)
    header=reader.fieldnames or []
    out=io.TextIOWrapper(gz,encoding="utf-8",newline="",write_through=True)
    writer=csv.DictWriter(out,fieldnames=header,extrasaction="ignore")
    writer.writeheader()
    for row in reader:
        rows_total+=1
        sid=(row.get("id_estacion") or "").strip()
        if not sid: continue
        dt=parse_date(row.get("fecha"))
        s=stats.setdefault(sid,{"id_estacion":sid,"registros":0,"fecha_inicial":None,"fecha_final":None,
            "fechas_invalidas":0,"precip_pluviometrica_validos":0,"precip_pluviometrica_faltantes":0,
            "precip_cronologica_validos":0,"precip_cronologica_faltantes":0,"precip_max30_validos":0,
            "precip_pluviometrica_min":None,"precip_pluviometrica_max":None})
        s["registros"]+=1
        if dt is None:
            s["fechas_invalidas"]+=1; invalid_dates+=1
        else:
            ds=dt.isoformat()
            s["fecha_inicial"]=min(s["fecha_inicial"],ds) if s["fecha_inicial"] else ds
            s["fecha_final"]=max(s["fecha_final"],ds) if s["fecha_final"] else ds
            key=(sid,ds)
            if key in seen_dates:
                duplicate_rows+=1; duplicate_dates.add(key)
            else: seen_dates.add(key)
        p=number(row.get("precipitacion_pluviometrica"))
        pc=number(row.get("precipitacion_cronologica"))
        p30=number(row.get("precipitacion_maxima_30minutos"))
        for field,val,missing in [("precip_pluviometrica_validos",p,"precip_pluviometrica_faltantes"),
                                  ("precip_cronologica_validos",pc,"precip_cronologica_faltantes")]:
            if val is None: s[missing]+=1
            else: s[field]+=1
        if p30 is not None: s["precip_max30_validos"]+=1
        if p is not None:
            s["precip_pluviometrica_min"]=p if s["precip_pluviometrica_min"] is None else min(s["precip_pluviometrica_min"],p)
            s["precip_pluviometrica_max"]=p if s["precip_pluviometrica_max"] is None else max(s["precip_pluviometrica_max"],p)
        if sid in near_ids: writer.writerow(row); near_rows+=1
    out.flush(); out.detach()

def station_row(s):
    m=station_info.get(s["id_estacion"],{})
    return {"id_estacion":s["id_estacion"],"nombre":m.get("nombre",""),"localidad":m.get("localidad",""),
        "provincia":m.get("provincia",""),"latitud":m.get("latitud",""),"longitud":m.get("longitud",""),
        "tipo":m.get("tipo",""),**s}

station_fields=["id_estacion","nombre","localidad","provincia","latitud","longitud","tipo","registros",
"fecha_inicial","fecha_final","fechas_invalidas","precip_pluviometrica_validos","precip_pluviometrica_faltantes",
"precip_cronologica_validos","precip_cronologica_faltantes","precip_max30_validos","precip_pluviometrica_min","precip_pluviometrica_max"]
with OUT_SUMMARY.open("w",encoding="utf-8",newline="") as f:
    w=csv.DictWriter(f,fieldnames=station_fields,extrasaction="ignore"); w.writeheader()
    for sid in sorted(stats): w.writerow(station_row(stats[sid]))

# Aggregate only station-dates that appear once. If a key is duplicated, exclude all
# occurrences rather than silently choosing one or potentially double-counting rainfall.
yearly={}
with gzip.open(SOURCE,"rt",encoding="utf-8-sig",newline="") as src:
    for row in csv.DictReader(src):
        sid=(row.get("id_estacion") or "").strip()
        dt=parse_date(row.get("fecha"))
        if not sid or not dt or (sid,dt.isoformat()) in duplicate_dates: continue
        p=number(row.get("precipitacion_pluviometrica"))
        key=(sid,dt.year)
        y=yearly.setdefault(key,{"id_estacion":sid,"anio":dt.year,"registros_fecha":0,
            "precip_pluviometrica_validos":0,"precip_pluviometrica_faltantes":0,
            "suma_valores_precip_pluviometrica":0.0,"max_valor_registro":None})
        y["registros_fecha"]+=1
        if p is None: y["precip_pluviometrica_faltantes"]+=1
        else:
            y["precip_pluviometrica_validos"]+=1
            y["suma_valores_precip_pluviometrica"]+=p
            y["max_valor_registro"]=p if y["max_valor_registro"] is None else max(y["max_valor_registro"],p)
year_fields=["id_estacion","nombre","localidad","provincia","anio","registros_fecha","precip_pluviometrica_validos",
"precip_pluviometrica_faltantes","suma_valores_precip_pluviometrica","max_valor_registro"]
with OUT_YEARLY.open("w",encoding="utf-8",newline="") as f:
    w=csv.DictWriter(f,fieldnames=year_fields,extrasaction="ignore"); w.writeheader()
    for key in sorted(yearly):
        y=yearly[key]; m=station_info.get(y["id_estacion"],{})
        y={**y,"nombre":m.get("nombre",""),"localidad":m.get("localidad",""),"provincia":m.get("provincia",""),
           "suma_valores_precip_pluviometrica":round(y["suma_valores_precip_pluviometrica"],3)}
        w.writerow(y)

meta={"fuente":"estaciones-observaciones.csv.gz / consolidado comunitario basado en SIGA-INTA",
"filas_fuente_procesadas":rows_total,"catalogo_estaciones":len(station_info),"estaciones_con_registros":len(stats),
"filas_con_fecha_invalida":invalid_dates,"repeticiones_de_id_estacion_fecha":duplicate_rows,
"claves_estacion_fecha_duplicadas_excluidas_de_agregados":len(duplicate_dates),
"criterio_estaciones_cercanas":{"coordenada_referencia":{"latitud":VIRASORO[0],"longitud":VIRASORO[1]},
"radio_maximo_km":MAX_DISTANCE_KM,"maximo_estaciones":MAX_NEAR_STATIONS,
"distancias_km":{sid:near_distances[sid] for sid in sorted(near_ids)}},
"filas_extraidas_estaciones_cercanas_a_virasoro":near_rows,"ids_estaciones_extraidas":sorted(near_ids),
"archivos_generados":[OUT_SUMMARY.name,OUT_YEARLY.name,OUT_NEAR.name],
"advertencia":"Agregados exploratorios. Se excluyen de las sumas todas las fechas estación-día duplicadas. Confirmar frecuencia, unidades y significado de variables antes de interpretar sumas como mm acumulados; la fuente es una consolidación comunitaria."}
OUT_META.write_text(json.dumps(meta,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps(meta,ensure_ascii=False,indent=2))
