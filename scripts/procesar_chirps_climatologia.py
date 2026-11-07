#!/usr/bin/env python3
"""Build CHIRPS v3 Argentina 1991-2020 climatology and monthly anomalies."""
import hashlib,json,warnings
warnings.filterwarnings("ignore",message="All-NaN slice encountered")
from datetime import datetime,timezone
from pathlib import Path
import numpy as np
import xarray as xr

ROOT=Path("datos/fuentes-externas/precipitacion/chirps-v3/argentina")
INPUT=ROOT/"mensual-netcdf"
CLIM_DIR=ROOT/"climatologia"
ANOM_DIR=ROOT/"anomalias"
MANIFEST=ROOT/"manifiestos"/"chirps-v3-productos-derivados.json"

def sha(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""):h.update(b)
    return h.hexdigest()

def main():
    files=sorted(INPUT.glob("chirps-v3-final-mensual-argentina-*.nc"))
    if not files:raise RuntimeError("No existen los NetCDF anuales CHIRPS.")
    arrays=[]
    for path in files:
        with xr.open_dataset(path) as ds:
            arrays.append(ds["precipitation"].load())
    precip=xr.concat(arrays,dim="time").sortby("time")
    if precip.time.to_index().duplicated().any():raise RuntimeError("Hay meses duplicados en CHIRPS.")
    baseline=precip.sel(time=slice("1991-01-01","2020-12-31"))
    if baseline.sizes.get("time",0)!=360:
        raise RuntimeError(f"El período base debería tener 360 meses; tiene {baseline.sizes.get('time',0)}.")
    grouped=baseline.groupby("time.month")
    mean=grouped.mean("time",skipna=True)
    std=grouped.std("time",skipna=True)
    p10=grouped.quantile(0.10,dim="time",skipna=True).drop_vars("quantile")
    p50=grouped.quantile(0.50,dim="time",skipna=True).drop_vars("quantile")
    p90=grouped.quantile(0.90,dim="time",skipna=True).drop_vars("quantile")
    clim=xr.Dataset({
        "precipitation_mean_mm":mean.astype("float32"),
        "precipitation_std_mm":std.astype("float32"),
        "precipitation_p10_mm":p10.astype("float32"),
        "precipitation_p50_mm":p50.astype("float32"),
        "precipitation_p90_mm":p90.astype("float32")
    },attrs={
        "title":"CHIRPS v3 Final Argentina monthly precipitation climatology",
        "baseline_period":"1991-01 to 2020-12",
        "source":"UCSB CHC CHIRPS v3 Final/rnl daily (ERA5-based), aggregated to monthly",
        "spatial_subset":"Argentina national polygon; 0.05 degree",
        "units":"mm month-1",
        "retrieved_utc":datetime.now(timezone.utc).isoformat(),
        "note":"Climatology statistics are computed across the 30 calendar years 1991-2020 for each calendar month."
    })
    CLIM_DIR.mkdir(parents=True,exist_ok=True);ANOM_DIR.mkdir(parents=True,exist_ok=True)
    clim_path=CLIM_DIR/"chirps-v3-climatologia-mensual-1991-2020.nc"
    clim.to_netcdf(clim_path,engine="netcdf4",encoding={
        v:{"zlib":True,"complevel":4,"shuffle":True,"dtype":"float32","_FillValue":-9999.0}
        for v in clim.data_vars
    })
    files_out=[{"file":str(clim_path),"bytes":clim_path.stat().st_size,"sha256":sha(clim_path)}]
    for year in sorted(set(int(x) for x in precip.time.dt.year.values)):
        year_data=precip.sel(time=slice(f"{year}-01-01",f"{year}-12-31"))
        month_values=year_data.time.dt.month.values
        clim_mean=xr.concat([mean.sel(month=int(m)) for m in month_values],dim="time").assign_coords(time=year_data.time)
        clim_std=xr.concat([std.sel(month=int(m)) for m in month_values],dim="time").assign_coords(time=year_data.time)
        anomaly=year_data-clim_mean
        standardized=xr.where(clim_std>0,anomaly/clim_std,np.nan)
        out=xr.Dataset({
            "precipitation_mm":year_data.astype("float32"),
            "anomaly_mm":anomaly.astype("float32"),
            "standardized_anomaly":standardized.astype("float32")
        },attrs={
            "title":f"CHIRPS v3 Argentina monthly precipitation anomalies ({year})",
            "baseline_period":"1991-2020",
            "source":"UCSB CHC CHIRPS v3 Final/rnl daily (ERA5-based), aggregated to monthly",
            "units":"precipitation and anomaly: mm month-1; standardized anomaly: dimensionless",
            "retrieved_utc":datetime.now(timezone.utc).isoformat(),
            "note":"Anomaly = monthly total minus the 1991-2020 climatological mean for the same calendar month. Standardized anomaly = anomaly / 1991-2020 standard deviation."
        })
        path=ANOM_DIR/f"chirps-v3-anomalias-mensuales-argentina-{year}.nc"
        out.to_netcdf(path,engine="netcdf4",encoding={
            v:{"zlib":True,"complevel":4,"shuffle":True,"dtype":"float32","_FillValue":-9999.0}
            for v in out.data_vars
        })
        files_out.append({"file":str(path),"year":year,"months":int(out.sizes["time"]),
                          "bytes":path.stat().st_size,"sha256":sha(path)})
        print(f"CHIRPS anomalies {year}: {path.stat().st_size} bytes",flush=True)
    manifest={
        "dataset":"CHIRPS v3 Final Argentina climatology and monthly anomalies",
        "source_dataset":"UCSB CHC CHIRPS v3 Final/rnl daily (ERA5-based), monthly sums derived",
        "baseline_period":"1991-2020",
        "input_months":int(precip.sizes["time"]),
        "climatology_variables":list(clim.data_vars),
        "anomaly_variables":["precipitation_mm","anomaly_mm","standardized_anomaly"],
        "files":files_out,
        "created_utc":datetime.now(timezone.utc).isoformat()
    }
    MANIFEST.parent.mkdir(parents=True,exist_ok=True)
    MANIFEST.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"input_months":manifest["input_months"],"output_files":len(files_out),
                      "total_bytes":sum(x["bytes"] for x in files_out)},ensure_ascii=False,indent=2))

if __name__=="__main__":main()
