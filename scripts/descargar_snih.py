#!/usr/bin/env python3
"""Descarga reproducible del inventario SNIH y sus series nivométricas públicas."""
from __future__ import annotations

import csv
import gzip
import hashlib
import json
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import requests

ROOT = Path("datos/fuentes-externas/hidrologia/snih")
BASE = "https://snih.hidricosargentina.gob.ar"
TIMEOUT = 120
MAX_RETRIES = 4
VARIABLES = {
    70: ("espesor_nieve", "cm"),
    71: ("longitud_nucleo_cateador", "cm"),
    72: ("densidad_nieve", "g/cm3"),
    73: ("equivalente_agua_snow_pillow", "mm"),
    74: ("equivalente_agua_cateos", "mm"),
}
ART = timezone(timedelta(hours=-3))

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def post(endpoint: str, body: dict | None = None):
    url = f"{BASE}/{endpoint}"
    last = None
    for attempt in range(MAX_RETRIES):
        try:
            r = requests.post(url, json=body or {}, timeout=TIMEOUT,
                              headers={"User-Agent":"LaboratorioDatosMeteorologicos/1.0",
                                       "Accept":"application/json"})
            r.raise_for_status()
            payload = r.json()
            if not isinstance(payload, dict) or "d" not in payload:
                raise RuntimeError(f"Respuesta SNIH inesperada en {endpoint}: {str(payload)[:250]}")
            return payload["d"]
        except Exception as exc:
            last = exc
            if attempt + 1 < MAX_RETRIES:
                delay = min(5 * (2 ** attempt), 60)
                print(f"Reintento SNIH {endpoint} en {delay}s: {exc}")
                time.sleep(delay)
    raise last

def parse_dotnet_date(value):
    if not value:
        return None
    m = re.search(r"/Date\((-?\d+)", str(value))
    if not m:
        return None
    return (datetime(1970,1,1,tzinfo=timezone.utc) +
            timedelta(milliseconds=int(m.group(1)))).astimezone(ART)

def json_gz(path: Path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(path, "wt", encoding="utf-8", compresslevel=9) as f:
        json.dump(payload, f, ensure_ascii=False, separators=(",",":"))

def csv_gz(path: Path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(path, "wt", encoding="utf-8", newline="", compresslevel=9) as f:
        w=csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

def station_row(row, network_names):
    try:
        lat=float(row.get("Latitud"))
    except (TypeError,ValueError):
        lat=None
    try:
        lon=float(row.get("Longitud"))
    except (TypeError,ValueError):
        lon=None
    try:
        elev=float(row.get("Cota"))
        if elev < -900: elev=None
    except (TypeError,ValueError):
        elev=None
    red=row.get("Red")
    return {
        "station_id": str(row.get("Codigo","")),
        "name": (row.get("Descripcion") or "").strip(),
        "latitude": -abs(lat) if lat not in (None,0) else None,
        "longitude": -abs(lon) if lon not in (None,0) else None,
        "elevation_m": elev,
        "network_id": red,
        "network": network_names.get(red),
        "province_code": row.get("Provincia"),
        "basin_code": row.get("Cuenca"),
        "system_code": row.get("Sistema"),
        "regional_code": row.get("Regional"),
        "river": row.get("Rio"),
        "place": row.get("Lugar"),
        "station_type": row.get("Tipo"),
        "transmission": "telemetric" if row.get("Transmision") == "T" else "conventional",
        "enabled": row.get("Habilitada"),
        "source": "SNIH / Subsecretaría de Recursos Hídricos, Argentina"
    }

def as_geojson(stations):
    features=[]
    for s in stations:
        if s["latitude"] is None or s["longitude"] is None:
            continue
        features.append({
            "type":"Feature",
            "geometry":{"type":"Point","coordinates":[s["longitude"],s["latitude"]]},
            "properties":{k:v for k,v in s.items() if k not in ("latitude","longitude")}
        })
    return {"type":"FeatureCollection","name":"SNIH_estaciones","features":features}

def historical_series(station_id, code, begin="1900-01-01", end=None):
    end=end or (date.today()+timedelta(days=1)).isoformat()
    body={"fechaDesde":begin,"fechaHasta":end,"estacion":str(station_id),
          "codigo":str(code),"validados":"true"}
    payload=post("MuestraDatos.aspx/LeerDatosHistoricos",body)
    if not isinstance(payload,dict) or str(payload.get("RespuestaOK")).lower()!="true":
        raise RuntimeError(f"LeerDatosHistoricos: {str(payload)[:300]}")
    return payload

def recent_window(station_id, begin: date, end: date):
    body={"fechaDesde":begin.isoformat(),"fechaHasta":end.isoformat(),
          "estacion":str(station_id),"codigo":"73"}
    payload=post("MuestraDatos.aspx/LeerUltimosRegistros",body)
    if not isinstance(payload,dict) or str(payload.get("RespuestaOK")).lower()!="true":
        raise RuntimeError(f"LeerUltimosRegistros: {str(payload)[:300]}")
    records=[]
    for item in payload.get("Mediciones") or []:
        ts=parse_dotnet_date(item.get("FechaHora"))
        if ts is None or not (begin <= ts.date() <= end):
            continue
        for m in item.get("Mediciones") or []:
            if str(m.get("Codigo"))=="73":
                records.append({"station_id":str(station_id),"variable_code":73,
                    "variable":VARIABLES[73][0],"units":VARIABLES[73][1],
                    "datetime":ts.isoformat(),"date":ts.date().isoformat(),
                    "value":m.get("Valor"),"validation":"raw_unvalidated",
                    "source_interval":"sub_daily"})
    records.sort(key=lambda x:x["datetime"])
    return records

def raw_telemetry(station_id, start=date(2009,1,1), end=None):
    end=end or date.today()
    found={}
    cursor=start
    while cursor<=end:
        stop=min(cursor+timedelta(days=365),end)
        # The service may return only one contiguous block; continue from the
        # last returned day, and then advance the annual window across gaps.
        block_cursor=cursor
        while block_cursor<=stop:
            rows=recent_window(station_id,block_cursor,stop)
            if not rows:
                break
            new_rows=[row for row in rows if row["datetime"] not in found]
            for row in rows:
                found.setdefault(row["datetime"],row)
            last=date.fromisoformat(rows[-1]["date"])
            if last>=stop:
                break
            # Re-query the last day only when the response contains new data;
            # otherwise advance one day to avoid an endless repeated block.
            next_cursor=last if new_rows and last>block_cursor else last+timedelta(days=1)
            if next_cursor<=block_cursor:
                next_cursor=block_cursor+timedelta(days=1)
            block_cursor=next_cursor
            time.sleep(0.15)
        cursor=stop+timedelta(days=1)
        time.sleep(0.15)
    return [found[k] for k in sorted(found)]

def main():
    stamp=datetime.now(timezone.utc).isoformat()
    raw_dir=ROOT/"originales"
    cat_dir=ROOT/"catalogos"
    hist_dir=ROOT/"series-historicas"
    rawobs_dir=ROOT/"telemetria-cruda"
    for p in (raw_dir,cat_dir,hist_dir,rawobs_dir): p.mkdir(parents=True,exist_ok=True)

    stations_raw=post("Filtros.aspx/LeerEstaciones")
    networks_raw=post("Filtros.aspx/leerListaRedes")
    associations_raw=post("MuestraDatos.aspx/LeerListaAsociaciones")
    if not isinstance(stations_raw,list) or not isinstance(associations_raw,list):
        raise RuntimeError("Los listados SNIH no devolvieron arreglos.")
    json_gz(raw_dir/"estaciones-originales.json.gz",stations_raw)
    json_gz(raw_dir/"redes-originales.json.gz",networks_raw)
    json_gz(raw_dir/"asociaciones-originales.json.gz",associations_raw)

    network_names={}
    for n in networks_raw or []:
        network_names[n.get("Codigo")]=(n.get("Descripcion") or "").strip()
    stations=[]
    seen=set()
    for r in stations_raw:
        sid=str(r.get("Codigo",""))
        if sid and sid not in seen:
            seen.add(sid)
            stations.append(station_row(r,network_names))
    station_by_id={s["station_id"]:s for s in stations}

    associations=[]
    snow_associations=[]
    for a in associations_raw:
        try:
            code=int(a.get("Codigo"))
        except (TypeError,ValueError):
            code=None
        since_dt=parse_dotnet_date(a.get("Desde"))
        row={
            "station_id":str(a.get("Estacion","")),
            "variable_code":code,
            "variable":VARIABLES.get(code,("unknown",""))[0],
            "units":VARIABLES.get(code,("",""))[1],
            "since":since_dt.date().isoformat() if since_dt else None,
            "minimum":a.get("Minimo"),"maximum":a.get("Maximo")
        }
        associations.append(row)
        if code in VARIABLES:
            snow_associations.append(row)

    csv_gz(cat_dir/"estaciones.csv.gz",stations,list(stations[0].keys()) if stations else ["station_id"])
    json_gz(cat_dir/"estaciones.geojson.gz",as_geojson(stations))
    csv_gz(cat_dir/"asociaciones-parametros.csv.gz",associations,
           ["station_id","variable_code","variable","units","since","minimum","maximum"])
    csv_gz(cat_dir/"estaciones-nivometricas.csv.gz",
           [station_by_id[sid] for sid in sorted({a["station_id"] for a in snow_associations}) if sid in station_by_id],
           list(stations[0].keys()) if stations else ["station_id"])
    json_gz(cat_dir/"redes.json.gz",networks_raw)

    # Save one raw JSON response and one normalized CSV per station/parameter.
    jobs=[]
    for a in snow_associations:
        if a["station_id"] in station_by_id:
            jobs.append((a["station_id"],int(a["variable_code"])))
    jobs=sorted(set(jobs))
    historical_results=[]
    def do_history(job):
        sid,code=job
        name,units=VARIABLES[code]
        raw_path=hist_dir/"originales"/f"{sid}-{code}-{name}.json.gz"
        csv_path=hist_dir/"procesadas"/f"{sid}-{code}-{name}.csv.gz"
        if raw_path.exists() and csv_path.exists():
            with gzip.open(csv_path,"rt",encoding="utf-8",newline="") as f:
                existing_count=max(0,sum(1 for _ in f)-1)
            return {"station_id":sid,"variable_code":code,"variable":name,
                "records":existing_count,"raw_file":str(raw_path),"raw_bytes":raw_path.stat().st_size,
                "raw_sha256":sha256(raw_path),"csv_file":str(csv_path),
                "csv_bytes":csv_path.stat().st_size,"csv_sha256":sha256(csv_path),
                "estado":"ya_existia"}
        payload=historical_series(sid,code)
        rows=[]
        for m in payload.get("Mediciones") or []:
            ts=parse_dotnet_date(m.get("FechaHora"))
            if ts is None: continue
            rows.append({"station_id":sid,"variable_code":code,"variable":name,
                "units":units,"datetime":ts.isoformat(),"date":ts.date().isoformat(),
                "value":m.get("Medicion"),"qualifier":m.get("Calificador"),
                "validated":m.get("Validado"),"source_interval":"historical"})
        rows.sort(key=lambda x:x["datetime"])
        slug=f"{sid}-{code}-{name}"
        json_gz(raw_path,payload)
        csv_gz(csv_path,rows,list(rows[0].keys()) if rows else
            ["station_id","variable_code","variable","units","datetime","date","value","qualifier","validated","source_interval"])
        return {"station_id":sid,"variable_code":code,"variable":name,"records":len(rows),
                "raw_file":str(raw_path),"raw_bytes":raw_path.stat().st_size,
                "raw_sha256":sha256(raw_path),"csv_file":str(csv_path),
                "csv_bytes":csv_path.stat().st_size,"csv_sha256":sha256(csv_path)}
    with ThreadPoolExecutor(max_workers=3) as pool:
        futures=[pool.submit(do_history,j) for j in jobs]
        for future in as_completed(futures):
            try: historical_results.append(future.result())
            except Exception as exc:
                historical_results.append({"estado":"fallido","error":str(exc)})
            time.sleep(0.1)

    # Raw snow-pillow telemetry is kept separate from validated historical values.
    pillow_ids=sorted({a["station_id"] for a in snow_associations if int(a["variable_code"])==73 and a["station_id"] in station_by_id})
    telemetry_results=[]
    def do_telemetry(sid):
        path=rawobs_dir/f"{sid}-73-swe-telemetria.csv.gz"
        if path.exists():
            with gzip.open(path,"rt",encoding="utf-8",newline="") as f:
                existing_count=max(0,sum(1 for _ in f)-1)
            return {"station_id":sid,"records":existing_count,"file":str(path),
                    "bytes":path.stat().st_size,"sha256":sha256(path),"estado":"ya_existia"}
        rows=raw_telemetry(sid)
        csv_gz(path,rows,["station_id","variable_code","variable","units","datetime","date","value","validation","source_interval"])
        return {"station_id":sid,"records":len(rows),"file":str(path),
                "bytes":path.stat().st_size,"sha256":sha256(path)}
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures=[pool.submit(do_telemetry,sid) for sid in pillow_ids]
        for future in as_completed(futures):
            try: telemetry_results.append(future.result())
            except Exception as exc: telemetry_results.append({"estado":"fallido","error":str(exc)})

    def file_record(path):
        return {"file":str(path),"bytes":path.stat().st_size,"sha256":sha256(path)}
    catalog_files=[file_record(p) for p in sorted(cat_dir.glob("*.gz"))]
    raw_files=[file_record(p) for p in sorted(raw_dir.glob("*.gz"))]
    errors=[x for x in historical_results+telemetry_results if x.get("estado")=="fallido"]
    manifest={
        "dataset":"SNIH — Sistema Nacional de Información Hídrica",
        "retrieved_utc":stamp,
        "source":"https://snih.hidricosargentina.gob.ar/",
        "terms":"https://snih.hidricosargentina.gob.ar/Terminos.aspx",
        "scope":"Inventario completo de estaciones y asociaciones; series históricas de variables nivométricas 70–74; telemetría cruda SWE código 73 separada.",
        "stations_total_source_rows":len(stations_raw),
        "stations_unique":len(stations),
        "associations_total":len(associations),
        "snow_stations":len({a["station_id"] for a in snow_associations}),
        "snow_station_associations":len(jobs),
        "historical_series":historical_results,
        "historical_records_total":sum(x.get("records",0) for x in historical_results),
        "telemetry_series":telemetry_results,
        "telemetry_records_total":sum(x.get("records",0) for x in telemetry_results),
        "catalog_files":catalog_files,
        "raw_catalog_files":raw_files,
        "errors":errors,
        "quality_notes":[
            "El portal distingue registros históricos validados y telemetría cruda no validada.",
            "Las series diarias/históricas y la telemetría subdiaria se almacenan por separado y no se fusionan.",
            "Las coordenadas publicadas por el portal se expresan positivas; se normalizan al hemisferio sur/oeste para Argentina.",
            "La cobertura corresponde a las redes integradas al SNIH y no implica que todas las estaciones tengan todas las variables o series completas.",
            "Citar a la Subsecretaría de Recursos Hídricos o al organismo de la red y conservar fecha de descarga y condiciones de uso."
        ],
        "license_note":"El portal declara datos públicos, libres y gratuitos sujetos a cita de fuente, fecha de actualización y conservación de metadatos."
    }
    path=ROOT/"manifiestos"/"snih-ingesta.json"
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in manifest.items() if k not in ("historical_series","telemetry_series")},ensure_ascii=False,indent=2))
    if errors: raise SystemExit(1)

if __name__=="__main__":
    main()
