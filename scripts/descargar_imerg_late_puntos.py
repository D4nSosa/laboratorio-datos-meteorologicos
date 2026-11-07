#!/usr/bin/env python3
"""IMERG Late V07: daily totals at Argentine IGRA reference stations via public point API."""
from __future__ import annotations

import csv
import gzip
import hashlib
import json
import time
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import requests

API="https://api.dynamical.org/v1"
PRODUCT="nasa-imerg-analysis-late"
VARIABLE="precipitation_surface"
STATIONS=Path("datos/fuentes-externas/radiosondeos/igra/estaciones-argentina.csv")
ROOT=Path("datos/fuentes-externas/precipitacion/gpm-imerg/late-v07")
OUT=ROOT/"daily-points-argentina"
MANIFEST=ROOT/"manifiesto-imerg-late-puntos.json"
SESSION=requests.Session()
SESSION.headers.update({"User-Agent":"LaboratorioDatosMeteorologicos/1.0","Accept":"application/json"})

def sha256(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""): h.update(b)
    return h.hexdigest()

def get_json(url,attempts=5):
    last=None
    for i in range(attempts):
        try:
            r=SESSION.get(url,timeout=120)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            last=e
            if i+1<attempts: time.sleep(min(10*(2**i),120))
    raise last

def post_json(url,payload,attempts=5):
    last=None
    for i in range(attempts):
        try:
            r=SESSION.post(url,json=payload,timeout=180)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            last=e
            status=getattr(getattr(e,"response",None),"status_code",None)
            if status not in (None,429,500,502,503,504) or i+1==attempts: raise
            retry=getattr(e,"response",None)
            delay=min(10*(2**i),180)
            if retry is not None and retry.headers.get("Retry-After"):
                try: delay=int(retry.headers["Retry-After"])
                except ValueError: pass
            print(f"IMERG API reintento {i+1}/{attempts} en {delay}s: {e}",flush=True)
            time.sleep(delay)
    raise last

def has_current_schema(path):
    try:
        with gzip.open(path,"rt",encoding="utf-8") as f:
            header=f.readline()
        return "precipitation_sum_valid_intervals_mm" in header
    except Exception:
        return False

def month_iter(start,end):
    y,m=start.year,start.month
    while (y,m)<=(end.year,end.month):
        first=date(y,m,1)
        if m==12: next_first=date(y+1,1,1)
        else: next_first=date(y,m+1,1)
        last=next_first-timedelta(days=1)
        yield first,last
        y,m=(y+1,1) if m==12 else (y,m+1)

def main():
    if not STATIONS.exists(): raise FileNotFoundError(STATIONS)
    with STATIONS.open(encoding="utf-8",newline="") as f:
        stations=list(csv.DictReader(f))
    points=[]
    for s in stations:
        points.append({"station_id":s["station_id"],"name":s["station_name"],
            "geographic_scope":s.get("geographic_scope",""),
            "latitude":float(s["latitude"]),"longitude":float(s["longitude"])})
    if not points: raise RuntimeError("No hay estaciones IGRA para muestrear IMERG.")

    meta=get_json(f"{API}/data-products/{PRODUCT}")
    dims=meta.get("dimensions",{})
    time_dim=dims.get("time") or dims.get("analysis_time")
    if not time_dim or not time_dim.get("extent"):
        raise RuntimeError(f"El catálogo IMERG no publicó extensión temporal reconocible: {list(dims)}")
    start=date.fromisoformat(str(time_dim["extent"][0])[:10])
    upper=time_dim["extent"][1]
    end=date.fromisoformat(str(upper)[:10]) if upper else date.today()
    if start>date(1998,1,1): print(f"El archivo comienza más tarde que 1998: {start}",flush=True)
    OUT.mkdir(parents=True,exist_ok=True)

    manifest={
        "dataset":"NASA GPM IMERG Late Run V07 (dynamical.org public analysis point API)",
        "data_product_id":PRODUCT,
        "source_provider":"NASA GPM / NASA GES DISC",
        "archive_provider":"dynamical.org; public point API",
        "api_docs":"https://dynamical.org/api/",
        "catalog_url":"https://dynamical.org/catalog/nasa-imerg-analysis-late/",
        "source_extent_start":str(start),"source_extent_end":str(end),
        "variable":VARIABLE,"source_units":"kg m-2 s-1",
        "conversion":"precipitation_mm_day = mean(valid half-hourly rate) * 86400 seconds; precipitation_sum_valid_intervals_mm = sum(rate * 1800 seconds). Both fields and valid interval count are retained; the first is an IMERG-style daily mean-rate estimate, not a separate official Daily file.",
        "source_temporal_resolution":"30 minutes",
        "source_spatial_resolution":"0.1 degree",
        "sampling":"Nearest 0.1-degree grid cell to each IGRA radiosonde station; includes one Argentine-operated South Orkney Islands reference station; not a complete gridded Argentina download.",
        "license":"CC BY 4.0 per dynamical.org catalog",
        "retrieved_utc":datetime.now(timezone.utc).isoformat(),
        "stations_requested":len(points),
        "files":[],"errors":[],
        "quality_note":"IMERG Late is a lower-latency product and is not interchangeable with IMERG Final. Daily mean-rate estimates are derived from valid half-hourly rates using the product's daily scaling approach; raw valid-interval sums and completeness are also retained. Incomplete days remain identifiable.",
        "imerg_final_status":"not_downloaded",
        "imerg_final_note":"NASA IMERG Final V07B bulk access requires NASA Earthdata authentication. This archive is explicitly Late V07 and must not be relabeled Final."
    }

    for first,last in month_iter(start,end):
        # Avoid asking beyond the last published source date.
        if first>end: break
        last=min(last,end)
        month_key=f"{first.year}-{first.month:02d}"
        path=OUT/f"imerg-late-daily-argentina-{month_key}.csv.gz"
        if path.exists() and path.stat().st_size>0 and has_current_schema(path):
            manifest["files"].append({"file":str(path),"month":month_key,
                "status":"already_present","bytes":path.stat().st_size,"sha256":sha256(path)})
            continue
        start_iso=first.isoformat()+"T00:00:00Z"
        end_iso=(last+timedelta(days=1)).isoformat()+"T00:00:00Z"
        rows=[]
        point_meta={}
        month_errors=[]
        for offset in range(0,len(points),10):
            group=points[offset:offset+10]
            queries=[{
                "queryId":p["station_id"],
                "dataProductId":PRODUCT,
                "location":{"latitude":p["latitude"],"longitude":p["longitude"]},
                "startTime":start_iso,"endTime":end_iso,
                "variables":[VARIABLE]
            } for p in group]
            try:
                payload=post_json(f"{API}/analyses",{"queries":queries})
                results=payload.get("results",[])
                if len(results)!=len(group):
                    raise RuntimeError(f"Respuesta con {len(results)} resultados para {len(group)} puntos.")
                for p,result in zip(group,results):
                    if result.get("error"):
                        raise RuntimeError(f"{p['station_id']}: {result['error']}")
                    times=result.get("analysisTimes") or []
                    vals=(result.get("data") or {}).get(VARIABLE) or []
                    if len(times)!=len(vals):
                        raise RuntimeError(f"{p['station_id']}: ejes y valores no coinciden.")
                    daily={}
                    for ts,value in zip(times,vals):
                        day=str(ts)[:10]
                        rec=daily.setdefault(day,{"sum":0.0,"valid":0,"expected":48})
                        if value is not None:
                            rec["sum"]+=float(value)*1800.0
                            rec["valid"]+=1
                    selected=(result.get("point") or {}).get("selected") or {}
                    grid=selected.get("grid") or {}
                    point_meta[p["station_id"]]={
                        "requested_latitude":p["latitude"],"requested_longitude":p["longitude"],
                        "geographic_scope":p["geographic_scope"],
                        "selected_latitude":selected.get("latitude"),
                        "selected_longitude":selected.get("longitude"),
                        "latitude_index":grid.get("latitudeIndex"),
                        "longitude_index":grid.get("longitudeIndex"),
                        "snapshot_id":result.get("snapshotId"),
                        "data_product_version":(result.get("dataProduct") or {}).get("version")
                    }
                    for day,rec in sorted(daily.items()):
                        d=date.fromisoformat(day)
                        if first<=d<=last:
                            rows.append({
                                "station_id":p["station_id"],"station_name":p["name"],"geographic_scope":p["geographic_scope"],
                                "date":day,
                                "precipitation_mm_day":round(rec["sum"]*48/rec["valid"],4) if rec["valid"] else None,
                                "precipitation_sum_valid_intervals_mm":round(rec["sum"],4) if rec["valid"] else None,
                                "valid_half_hour_intervals":rec["valid"],
                                "expected_half_hour_intervals":48,
                                "completeness_pct":round(rec["valid"]/48*100,2),
                                "selected_latitude":selected.get("latitude"),
                                "selected_longitude":selected.get("longitude"),
                                "product":PRODUCT,"run":"Late","version":(result.get("dataProduct") or {}).get("version")
                            })
                time.sleep(0.5)
            except Exception as exc:
                month_errors.append({"batch_start":offset,"error":f"{type(exc).__name__}: {exc}"})
        if month_errors:
            manifest["errors"].append({"month":month_key,"errors":month_errors})
            print(f"IMERG {month_key} incompleto: {month_errors}",flush=True)
            continue
        rows.sort(key=lambda x:(x["station_id"],x["date"]))
        with path.open("wb") as raw:
            with gzip.GzipFile(fileobj=raw,mode="wb",compresslevel=9,mtime=0) as gz:
                import io
                buf=io.StringIO()
                fields=list(rows[0].keys()) if rows else [
                    "station_id","station_name","geographic_scope","date","precipitation_mm_day",
                    "precipitation_sum_valid_intervals_mm","valid_half_hour_intervals","expected_half_hour_intervals","completeness_pct",
                    "selected_latitude","selected_longitude","product","run","version"]
                w=csv.DictWriter(buf,fieldnames=fields)
                w.writeheader();w.writerows(rows)
                gz.write(buf.getvalue().encode("utf-8"))
        entry={"file":str(path),"month":month_key,"rows":len(rows),
               "stations":len({r["station_id"] for r in rows}),
               "bytes":path.stat().st_size,"sha256":sha256(path),
               "snapshot_ids":sorted({v["snapshot_id"] for v in point_meta.values() if v.get("snapshot_id")}),
               "selected_points":point_meta,"status":"downloaded_and_daily_aggregated"}
        manifest["files"].append(entry)
        MANIFEST.parent.mkdir(parents=True,exist_ok=True)
        MANIFEST.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        print(f"IMERG {month_key}: {len(rows)} daily station rows",flush=True)

    manifest["months_downloaded"]=sum(1 for x in manifest["files"] if x.get("status")=="downloaded_and_daily_aggregated")
    manifest["daily_rows"]=sum(x.get("rows",0) for x in manifest["files"])
    manifest["finished_utc"]=datetime.now(timezone.utc).isoformat()
    MANIFEST.parent.mkdir(parents=True,exist_ok=True)
    MANIFEST.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in manifest.items() if k not in ("files",)},ensure_ascii=False,indent=2))
    if manifest["errors"]: raise SystemExit(1)

if __name__=="__main__": main()
