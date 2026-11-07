#!/usr/bin/env python3
"""Archive all Argentine INA DSIyAH observed series, respecting the 20k-row API cap."""
from __future__ import annotations
import csv,gzip,hashlib,json,time
from concurrent.futures import ThreadPoolExecutor,as_completed
from datetime import date,timedelta,datetime,timezone
from pathlib import Path
import requests

ROOT=Path("datos/fuentes-externas/hidrologia/ina-dsiyah")
CAT=ROOT/"catalogos"
OUT=ROOT/"series-observadas"
MANIFEST=ROOT/"manifiestos"/"series-argentina.json"
BASE="https://alerta.ina.gob.ar/pub/datos"
LIMIT=20000
WORKERS=5
SESSION=requests.Session()
SESSION.headers.update({"User-Agent":"LaboratorioDatosMeteorologicos/1.0","Accept":"application/json"})

def sha256(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""):h.update(b)
    return h.hexdigest()

def load_gz(name):
    with gzip.open(CAT/f"{name}.json.gz","rt",encoding="utf-8") as f:return json.load(f)

def get_window(series_id,start,end,depth=0):
    url=f"{BASE}/datos&timeStart={start.isoformat()}&timeEnd={end.isoformat()}&seriesId={series_id}&format=json"
    last=None
    for attempt in range(5):
        try:
            r=SESSION.get(url,timeout=120)
            r.raise_for_status()
            payload=r.json()
            data=payload.get("data") if isinstance(payload,dict) else None
            if data is None:
                message=payload.get("mensaje") if isinstance(payload,dict) else str(payload)
                if message and "no se encontraron" in message.lower(): return []
                raise RuntimeError(f"INA respuesta sin data: {str(payload)[:300]}")
            if len(data)>=LIMIT:
                if start>=end or depth>=16:
                    raise RuntimeError(f"INA llegó al límite de {LIMIT} filas en ventana mínima {start}..{end}")
                mid=start+(end-start)//2
                if mid==start:
                    # One-day window: split into adjacent overlapping half-day timestamps.
                    mid_dt=datetime.combine(start,datetime.min.time())+timedelta(hours=12)
                    left=f"{BASE}/datos&timeStart={start.isoformat()}T00:00:00&timeEnd={mid_dt.isoformat()}&seriesId={series_id}&format=json"
                    right=f"{BASE}/datos&timeStart={mid_dt.isoformat()}&timeEnd={end.isoformat()}T23:59:59&seriesId={series_id}&format=json"
                    combined=[]
                    for part in (left,right):
                        rr=SESSION.get(part,timeout=120);rr.raise_for_status()
                        pp=rr.json();combined.extend(pp.get("data") or [])
                    return combined
                # Overlap midpoint by one day; timestamp deduplication below prevents duplicates.
                return get_window(series_id,start,mid,depth+1)+get_window(series_id,mid,end,depth+1)
            return data
        except Exception as exc:
            last=exc
            status=getattr(getattr(exc,"response",None),"status_code",None)
            if status not in (None,429,500,502,503,504) or attempt==4: raise
            delay=min(5*(2**attempt),120)
            print(f"INA series {series_id} retry {attempt+1}/5 in {delay}s: {exc}",flush=True)
            time.sleep(delay)
    raise last

def windows(start,end,obs_count):
    days=(end-start).days
    if obs_count<=18000:
        return [(start,end)]
    years=max(1,days/365.25)
    density=obs_count/years
    step=timedelta(days=365) if density<=18000 else timedelta(days=30)
    result=[]
    cursor=start
    while cursor<=end:
        stop=min(cursor+step,end)
        result.append((cursor,stop))
        if stop==end:break
        cursor=stop
    return result

def download_series(s,station):
    sid=int(s["seriesid"])
    start=date.fromisoformat(str(s["from_date"])[:10])
    end=date.fromisoformat(str(s["to_date"])[:10])
    count=int(s.get("obs_count") or 0)
    if count<=0:return {"series_id":sid,"status":"catalog_zero_observations","rows":0}
    collected={}
    chunks=windows(start,end,count)
    for a,b in chunks:
        for row in get_window(sid,a,b):
            ts=row.get("timestart")
            if ts is not None:collected[str(ts)]=row.get("valor")
    if not collected:
        return {"series_id":sid,"status":"no_observations_returned","rows":0}
    rows=sorted(collected.items())
    meta={
        "series_id":sid,"sitecode":s.get("sitecode"),
        "station_name":s.get("estacion_nombre"),
        "variable_id":s.get("varid"),"variable_name":s.get("var_nombre"),
        "unit_id":s.get("unitid"),"unit_name":s.get("unit_nombre")
    }
    path=OUT/f"series-{sid}.csv.gz"
    tmp=path.with_suffix(".csv.gz.part")
    with gzip.open(tmp,"wt",encoding="utf-8",newline="",compresslevel=9) as f:
        fields=["series_id","sitecode","station_name","variable_id","variable_name","unit_id","unit_name","timestart","valor"]
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
        for ts,value in rows:
            w.writerow({**meta,"timestart":ts,"valor":value})
    tmp.replace(path)
    if path.stat().st_size>90*1024*1024:
        path.unlink(missing_ok=True)
        raise RuntimeError(f"Serie {sid} supera 90 MiB comprimidos; requiere partición por período.")
    return {"series_id":sid,"status":"downloaded","rows":len(rows),
        "catalog_obs_count":count,"chunks":len(chunks),"file":str(path),
        "bytes":path.stat().st_size,"sha256":sha256(path),
        "sitecode":s.get("sitecode"),"variable_id":s.get("varid")}

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    MANIFEST.parent.mkdir(parents=True,exist_ok=True)
    stations=load_gz("estaciones").get("data",[])
    series=load_gz("series").get("data",[])
    by_site={str(x.get("sitecode")):x for x in stations}
    arg_series=[s for s in series if (by_site.get(str(s.get("sitecode")),{}).get("pais") or "").lower()=="argentina"]
    existing={}
    if MANIFEST.exists():
        try:existing=json.loads(MANIFEST.read_text(encoding="utf-8"))
        except Exception:existing={}
    completed={str(x["series_id"]):x for x in existing.get("series",[])
               if x.get("status") in ("downloaded","catalog_zero_observations","no_observations_returned")}
    todo=[s for s in arg_series if str(s["seriesid"]) not in completed]
    manifest={
        "dataset":"INA DSIyAH — all Argentine observed series from the public series catalogue",
        "source":"https://alerta.ina.gob.ar/pub/gui",
        "data_endpoint":"https://alerta.ina.gob.ar/pub/datos/datos",
        "catalog_endpoint":"https://alerta.ina.gob.ar/pub/datos/series&format=json",
        "retrieved_utc":datetime.now(timezone.utc).isoformat(),
        "scope":"All series whose station catalogue country is Argentina; every variable exposed by the DSIyAH observed-series catalogue.",
        "api_limit_per_request":LIMIT,
        "download_strategy":"One seriesId at a time; split time windows recursively when the API returns 20,000 rows; deduplicate by timestart.",
        "stations_argentina":sum(1 for x in stations if (x.get("pais") or "").lower()=="argentina"),
        "series_argentina_total":len(arg_series),
        "series_completed_before_run":len(completed),
        "series_completed_this_run":0,
        "observations_downloaded_total":sum(x.get("rows",0) for x in completed.values()),
        "series":list(completed.values()),
        "errors":[],
        "license_note":"Use and cite INA/DSIyAH and the contributing network; preserve source metadata and retrieval date."
    }
    print(f"INA: {len(arg_series)} series argentinas; pendientes {len(todo)}",flush=True)
    # Process in batches so a checkpoint is written frequently and the job can resume.
    batch_size=40
    for start_idx in range(0,len(todo),batch_size):
        batch=todo[start_idx:start_idx+batch_size]
        with ThreadPoolExecutor(max_workers=WORKERS) as pool:
            futures={pool.submit(download_series,s,by_site.get(str(s.get("sitecode")),{})):s for s in batch}
            for future in as_completed(futures):
                s=futures[future]
                try:
                    result=future.result()
                    manifest["series"].append(result)
                    manifest["series_completed_this_run"]+=1
                    manifest["observations_downloaded_total"]+=result.get("rows",0)
                except Exception as exc:
                    manifest["errors"].append({"series_id":s.get("seriesid"),
                        "sitecode":s.get("sitecode"),"error":f"{type(exc).__name__}: {exc}"})
        manifest["series"].sort(key=lambda x:int(x["series_id"]))
        manifest["updated_utc"]=datetime.now(timezone.utc).isoformat()
        MANIFEST.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        print(f"INA checkpoint {min(start_idx+batch_size,len(todo))}/{len(todo)}; completed={len(manifest['series'])}; errors={len(manifest['errors'])}",flush=True)
        time.sleep(1)
    manifest["series_completed_total"]=len(manifest["series"])
    manifest["finished_utc"]=datetime.now(timezone.utc).isoformat()
    MANIFEST.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in manifest.items() if k!="series"},ensure_ascii=False,indent=2))
    if manifest["errors"]:raise SystemExit(1)

if __name__=="__main__":main()
