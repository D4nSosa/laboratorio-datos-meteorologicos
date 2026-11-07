#!/usr/bin/env python3
"""CHIRPS v3 Final: daily public cloud archive -> annual monthly Argentina grids."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import xarray as xr
import dynamical_catalog
import requests
from shapely.geometry import shape
from shapely import contains_xy

ROOT=Path("datos/fuentes-externas/precipitacion/chirps-v3")
OUT=ROOT/"argentina"/"mensual-netcdf"
OUT.mkdir(parents=True,exist_ok=True)
POLYGON_URL="https://raw.githubusercontent.com/datasets/geo-countries/master/data/countries.geojson"
DATASET_ID="ucsb-chc-chirps-analysis-final"

def sha256(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""):
            h.update(block)
    return h.hexdigest()

def argentina_polygon():
    r=requests.get(POLYGON_URL,timeout=120)
    r.raise_for_status()
    data=r.json()
    for feature in data["features"]:
        props=feature.get("properties",{})
        if props.get("ISO_A3")=="ARG" or props.get("ADMIN")=="Argentina" or props.get("name")=="Argentina":
            return shape(feature["geometry"])
    raise RuntimeError("No se encontró Argentina en el polígono de países.")

def main():
    print(f"Abriendo catálogo público: {DATASET_ID}")
    ds=dynamical_catalog.open(DATASET_ID,chunks=None)
    if "precipitation_surface" not in ds:
        raise RuntimeError(f"Variable precipitation_surface ausente: {list(ds.data_vars)}")
    da=ds["precipitation_surface"]
    required={"time","latitude","longitude"}
    if not required.issubset(set(da.dims)):
        raise RuntimeError(f"Dimensiones inesperadas: {da.dims}")

    # Argentina bounding window, followed by an exact national polygon mask.
    lat_values=np.asarray(da.latitude.values)
    lon_values=np.asarray(da.longitude.values)
    lat_slice=slice(-20,-60) if lat_values[0]>lat_values[-1] else slice(-60,-20)
    lon_slice=slice(-50,-80) if lon_values[0]>lon_values[-1] else slice(-80,-50)
    da=da.sel(latitude=lat_slice,longitude=lon_slice)
    lat=np.asarray(da.latitude.values)
    lon=np.asarray(da.longitude.values)
    polygon=argentina_polygon()
    xx,yy=np.meshgrid(lon,lat)
    spatial_mask=contains_xy(polygon,xx,yy)
    mask_da=xr.DataArray(spatial_mask,dims=("latitude","longitude"),
                         coords={"latitude":da.latitude,"longitude":da.longitude})
    da=da.where(mask_da)

    first=np.datetime_as_string(np.asarray(da.time.values)[0],unit="D")
    last=np.datetime_as_string(np.asarray(da.time.values)[-1],unit="D")
    first_year=int(first[:4]); last_year=int(last[:4])
    print(f"Rango real del archivo: {first} a {last}")
    print(f"Grilla recortada: {len(lat)} x {len(lon)}; celdas nacionales: {int(spatial_mask.sum())}")

    manifest={
        "dataset":"UCSB CHC CHIRPS v3 analysis final — daily archive, monthly aggregation",
        "dataset_id":DATASET_ID,
        "source_provider":"UCSB Climate Hazards Center CHIRPS v3.0",
        "cloud_archive":"dynamical.org / AWS Open Data",
        "catalog_url":"https://dynamical.org/catalog/ucsb-chc-chirps-analysis-final/",
        "stac_url":f"https://stac.dynamical.org/{DATASET_ID}/collection.json",
        "license":"CC BY 4.0",
        "citation":"Funk et al. (2026), CHIRPS v3, https://doi.org/10.15780/G2JQ0P; processed cloud archive by dynamical.org.",
        "retrieved_utc":datetime.now(timezone.utc).isoformat(),
        "source_time_start":first,
        "source_time_end":last,
        "source_resolution_degrees":0.05,
        "source_time_resolution":"daily",
        "source_variable":"precipitation_surface",
        "source_units":"kg m-2 s-1 (equivalent to mm/s)",
        "conversion":"daily_mm = precipitation_surface * 86400; monthly_mm = sum(daily_mm)",
        "spatial_extent":"Argentina national polygon; source grid retained at 0.05 degrees",
        "temporal_note":"Monthly grids are derived by summing CHIRPS v3 Final daily values. They are not the original CHIRPS monthly source rasters.",
        "files":[],
        "errors":[]
    }
    for year in range(first_year,last_year+1):
        path=OUT/f"chirps-v3-final-mensual-argentina-{year}.nc"
        if path.exists() and path.stat().st_size>0:
            with xr.open_dataset(path) as existing:
                existing_months=int(existing.sizes.get("time",0))
            manifest["files"].append({"file":str(path),"year":year,"months":existing_months,
                "status":"already_present","bytes":path.stat().st_size,"sha256":sha256(path)})
            continue
        start=f"{year}-01-01"
        stop=f"{year+1}-01-01"
        year_da=da.where((da.time >= np.datetime64(start)) & (da.time < np.datetime64(stop)),drop=True)
        if year_da.sizes.get("time",0)==0:
            continue
        # The daily product is an average rate over each 24-hour interval.
        monthly=(year_da*86400.0).resample(time="MS").sum(skipna=True,min_count=1)
        monthly=monthly.astype("float32").load()
        if monthly.sizes.get("time",0)==0:
            continue
        values=np.asarray(monthly.values)
        valid=int(np.isfinite(values).sum())
        if valid==0:
            raise RuntimeError(f"CHIRPS {year}: no hay celdas válidas.")
        out=xr.Dataset(
            {"precipitation":(("time","latitude","longitude"),values,
                {"long_name":"Monthly precipitation total derived from CHIRPS v3 Final daily",
                 "units":"mm month-1","cell_methods":"time: sum"})},
            coords={"time":monthly.time.values,"latitude":lat,"longitude":lon},
            attrs={
                "title":f"CHIRPS v3 Final monthly precipitation over Argentina ({year})",
                "source_dataset_id":DATASET_ID,
                "source_provider":"UCSB Climate Hazards Center",
                "cloud_archive":"dynamical.org / AWS Open Data",
                "source_url":f"https://dynamical.org/catalog/{DATASET_ID}/",
                "license":"CC BY 4.0",
                "spatial_subset":"Argentina national polygon",
                "spatial_resolution":"0.05 degree",
                "temporal_aggregation":"sum of daily precipitation totals within calendar month",
                "conversion":"precipitation_surface (kg m-2 s-1) * 86400 seconds/day; sum over month",
                "retrieved_utc":datetime.now(timezone.utc).isoformat(),
                "quality_note":"Derived monthly total from the CHIRPS v3 Final daily product; do not label as the native monthly CHIRPS raster."
            }
        )
        out.to_netcdf(path,engine="netcdf4",encoding={
            "precipitation":{"zlib":True,"complevel":4,"shuffle":True,
                             "dtype":"float32","_FillValue":-9999.0}
        })
        entry={"file":str(path),"year":year,"months":int(monthly.sizes["time"]),
               "valid_grid_values":valid,"bytes":path.stat().st_size,
               "sha256":sha256(path),"status":"downloaded_and_processed"}
        if path.stat().st_size>95*1024*1024:
            raise RuntimeError(f"Archivo excede límite prudente de GitHub: {path} ({path.stat().st_size} bytes)")
        manifest["files"].append(entry)
        print(json.dumps(entry,ensure_ascii=False))
        manifest_path=ROOT/"manifiestos"/"chirps-v3-final-argentina.json"
        manifest_path.parent.mkdir(parents=True,exist_ok=True)
        manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

    manifest["months_total"]=sum(x.get("months",0) for x in manifest["files"])
    manifest["years_total"]=len(manifest["files"])
    manifest["retrieved_utc_finished"]=datetime.now(timezone.utc).isoformat()
    manifest_path=ROOT/"manifiestos"/"chirps-v3-final-argentina.json"
    manifest_path.parent.mkdir(parents=True,exist_ok=True)
    manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"years":manifest["years_total"],"months":manifest["months_total"],
                      "start":first,"end":last,"manifest":str(manifest_path)},ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
