#!/usr/bin/env python3
"""Extract daily CHIRPS v3 Final/rnl point series at Argentine IGRA stations."""
import csv,gzip,hashlib,json
from datetime import datetime,timezone
from pathlib import Path
import numpy as np
import dynamical_catalog

DATASET="ucsb-chc-chirps-analysis-final"
STATIONS=Path("datos/fuentes-externas/radiosondeos/igra/estaciones-argentina.csv")
ROOT=Path("datos/fuentes-externas/precipitacion/chirps-v3/argentina")
OUT=ROOT/"puntos-diarios"
MANIFEST=ROOT/"manifiestos"/"chirps-v3-puntos-diarios.json"

def sha(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""):h.update(b)
    return h.hexdigest()

def main():
    with STATIONS.open(encoding="utf-8",newline="") as f:
        stations=list(csv.DictReader(f))
    ds=dynamical_catalog.open(DATASET,chunks=None)
    da=ds["precipitation_surface"]
    OUT.mkdir(parents=True,exist_ok=True)
    files=[]
    for n,s in enumerate(stations,1):
        sid=s["station_id"]
        lat=float(s["latitude"]);lon=float(s["longitude"])
        point=da.sel(latitude=lat,longitude=lon,method="nearest").load()
        values=np.asarray(point.values,dtype=np.float32)*86400.0
        dates=np.asarray(point.time.values)
        selected_lat=float(point.latitude.values);selected_lon=float(point.longitude.values)
        path=OUT/f"chirps-v3-final-diario-{sid}.csv.gz"
        with gzip.open(path,"wt",encoding="utf-8",newline="",compresslevel=9) as f:
            fields=["station_id","station_name","requested_latitude","requested_longitude",
                    "grid_latitude","grid_longitude","date","precipitation_mm_day"]
            w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
            for dt,value in zip(dates,values):
                day=np.datetime_as_string(dt,unit="D")
                w.writerow({"station_id":sid,"station_name":s["station_name"],
                    "requested_latitude":lat,"requested_longitude":lon,
                    "grid_latitude":selected_lat,"grid_longitude":selected_lon,
                    "date":day,"precipitation_mm_day":round(float(value),3) if np.isfinite(value) else None})
        files.append({"station_id":sid,"file":str(path),"rows":len(dates),
            "selected_grid_latitude":selected_lat,"selected_grid_longitude":selected_lon,
            "bytes":path.stat().st_size,"sha256":sha(path)})
        print(f"CHIRPS point {n}/{len(stations)} {sid}: {len(dates)} daily rows",flush=True)
    manifest={
        "dataset":"CHIRPS v3 Final/rnl daily point series at Argentine IGRA stations",
        "source_dataset_id":DATASET,
        "source_provider":"UCSB Climate Hazards Center",
        "cloud_archive":"dynamical.org / AWS Open Data",
        "source_units":"kg m-2 s-1",
        "conversion":"daily_mm = precipitation_surface * 86400",
        "source_temporal_resolution":"daily",
        "source_spatial_resolution":"0.05 degree",
        "sampling":"Nearest native grid cell for each IGRA station coordinate; selected cell coordinates are included per row.",
        "retrieved_utc":datetime.now(timezone.utc).isoformat(),
        "files":files,
        "note":"These are daily point samples from the Final/rnl product (ERA5-based daily disaggregation), not a complete gridded daily Argentina archive. Use alongside the monthly national NetCDF grids. The date is a consistent product label, not a uniform local station observation window."
    }
    MANIFEST.parent.mkdir(parents=True,exist_ok=True)
    MANIFEST.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"stations":len(files),"daily_rows":sum(x["rows"] for x in files),
                      "bytes":sum(x["bytes"] for x in files)},ensure_ascii=False,indent=2))

if __name__=="__main__":main()
