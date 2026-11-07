#!/usr/bin/env python3
"""Ingesta reproducible de IGRA, CHIRPS mensual LATAM recortado a Argentina e INA-DSIyAH."""
from __future__ import annotations

import gzip
import hashlib
import json
import re
import time
import zipfile
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin

import numpy as np
import pandas as pd
import rasterio
import requests
import xarray as xr
from rasterio.mask import mask
from shapely.geometry import shape, mapping

ROOT = Path("datos/fuentes-externas")
SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "LaboratorioDatosMeteorologicos/1.0 (research; public-data-ingestion)"})
TIMEOUT = 90

class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.hrefs = []
    def handle_starttag(self, tag, attrs):
        if tag.lower() == "a":
            href = dict(attrs).get("href")
            if href:
                self.hrefs.append(href)

def get(url: str, *, stream: bool = False):
    response = SESSION.get(url, timeout=TIMEOUT, stream=stream)
    response.raise_for_status()
    return response

def links(url: str) -> list[str]:
    parser = Links()
    parser.feed(get(url).text)
    return [urljoin(url, h) for h in parser.hrefs]

def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()

def save_json(path: Path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def ingest_igra(manifest: dict):
    base = "https://www.ncei.noaa.gov/pub/data/igra/data/data-por/"
    out = ROOT / "radiosondeos" / "igra" / "originales"
    out.mkdir(parents=True, exist_ok=True)
    station_files = sorted(
        u for u in links(base)
        if re.search(r"/ARM[A-Z0-9]{8}-data\.txt\.zip$", u)
    )
    if not station_files:
        raise RuntimeError("No se encontraron archivos ARM en el índice oficial IGRA data-por")
    downloaded = []
    for url in station_files:
        name = url.rsplit("/", 1)[-1]
        target = out / name
        if not target.exists() or target.stat().st_size == 0:
            tmp = target.with_suffix(target.suffix + ".part")
            with get(url, stream=True) as r, tmp.open("wb") as f:
                for chunk in r.iter_content(1024 * 1024):
                    if chunk:
                        f.write(chunk)
            tmp.replace(target)
        with zipfile.ZipFile(target) as zf:
            bad = zf.testzip()
            if bad:
                raise RuntimeError(f"ZIP IGRA corrupto: {name}, miembro {bad}")
        downloaded.append({
            "archivo": name, "bytes": target.stat().st_size,
            "sha256": sha256(target), "url": url
        })
        time.sleep(0.25)
    station_list_url = "https://www.ncei.noaa.gov/pub/data/igra/igra2-station-list.txt"
    station_list = out.parent / "igra2-station-list.txt"
    station_list.write_bytes(get(station_list_url).content)
    manifest["IGRA"] = {
        "estado": "descargado_y_validado",
        "producto": "IGRA 2.2 period-of-record sounding files",
        "estaciones_archivo": len(downloaded),
        "archivos": downloaded,
        "inventario_oficial": {
            "archivo": str(station_list.relative_to(Path.cwd())),
            "bytes": station_list.stat().st_size,
            "sha256": sha256(station_list),
            "url": station_list_url
        },
        "fuente": base,
        "nota": "Se descargaron todos los ficheros cuyo identificador comienza con ARM en el directorio oficial. Los identificadores se conservan separados; no se fusionan automáticamente estaciones cercanas o trasladadas."
    }

def argentina_geometry():
    url = "https://raw.githubusercontent.com/datasets/geo-countries/master/data/countries.geojson"
    data = get(url).json()
    for feature in data["features"]:
        props = feature.get("properties", {})
        if props.get("ISO_A3") == "ARG" or props.get("ADMIN") == "Argentina" or props.get("name") == "Argentina":
            return shape(feature["geometry"])
    raise RuntimeError("No se encontró el polígono de Argentina en geo-countries")

def ingest_chirps(manifest: dict):
    index = "https://data.chc.ucsb.edu/products/CHIRPS/v3.0/monthly/latam/tifs/"
    out = ROOT / "precipitacion" / "chirps-v3" / "argentina" / "mensual-netcdf"
    out.mkdir(parents=True, exist_ok=True)
    candidates = []
    for url in links(index):
        name = url.rsplit("/", 1)[-1]
        m = re.fullmatch(r"chirps-v3\.0\.(\d{4})\.(\d{2})\.tif", name)
        if m:
            candidates.append((int(m.group(1)), int(m.group(2)), url))
    candidates.sort()
    if not candidates:
        raise RuntimeError("No se encontraron GeoTIFF mensuales CHIRPS v3 LATAM")
    argentina = argentina_geometry()
    by_year: dict[int, list[tuple[pd.Timestamp, np.ndarray, tuple, dict]]] = {}
    tmp_dir = Path("/tmp/chirps")
    tmp_dir.mkdir(exist_ok=True)
    for year, month, url in candidates:
        target = tmp_dir / url.rsplit("/", 1)[-1]
        with get(url, stream=True) as r, target.open("wb") as f:
            for chunk in r.iter_content(1024 * 1024):
                if chunk:
                    f.write(chunk)
        with rasterio.open(target) as src:
            if src.crs is None:
                raise RuntimeError(f"CHIRPS sin CRS: {target.name}")
            geom = argentina
            if src.crs.to_string() != "EPSG:4326":
                from rasterio.warp import transform_geom
                geom = transform_geom("EPSG:4326", src.crs, mapping(argentina))
            arr, transform = mask(src, [mapping(geom) if hasattr(geom, "geom_type") else geom],
                                  crop=True, filled=True, nodata=np.nan, indexes=1)
            if arr.ndim == 3:
                arr = arr[0]
            arr = np.asarray(arr, dtype=np.float32)
            lat = transform.f + (np.arange(arr.shape[0]) + 0.5) * transform.e
            lon = transform.c + (np.arange(arr.shape[1]) + 0.5) * transform.a
            by_year.setdefault(year, []).append(
                (pd.Timestamp(year=year, month=month, day=1), arr, lat, lon)
            )
        target.unlink()
        time.sleep(0.5)
    outputs = []
    for year, records in sorted(by_year.items()):
        records.sort(key=lambda x: x[0])
        lat, lon = records[0][2], records[0][3]
        for rec in records[1:]:
            if rec[1].shape != records[0][1].shape:
                raise RuntimeError(f"Grilla CHIRPS inconsistente en {year}")
        cube = np.stack([r[1] for r in records], axis=0)
        times = pd.DatetimeIndex([r[0] for r in records])
        ds = xr.Dataset(
            {"precipitation": (("time", "lat", "lon"), cube,
              {"long_name": "Monthly precipitation", "units": "mm/month"})},
            coords={"time": times, "lat": lat, "lon": lon},
            attrs={
                "title": f"CHIRPS v3 monthly precipitation clipped to Argentina ({year})",
                "source": "Climate Hazards Center UCSB",
                "source_product": "CHIRPS v3 monthly LATAM GeoTIFF",
                "source_url": index,
                "spatial_subset": "Argentina polygon; native 0.05 degree grid",
                "created_utc": datetime.now(timezone.utc).isoformat(),
                "temporal_note": "Monthly final product; values are not daily observations."
            }
        )
        path = out / f"chirps-v3-mensual-argentina-{year}.nc"
        ds.to_netcdf(path, engine="netcdf4", encoding={
            "precipitation": {"zlib": True, "complevel": 4, "dtype": "float32", "_FillValue": -9999.0}
        })
        outputs.append({
            "archivo": str(path), "meses": len(records), "bytes": path.stat().st_size,
            "sha256": sha256(path), "desde": str(times.min().date()), "hasta": str(times.max().date())
        })
    manifest["CHIRPS_v3"] = {
        "estado": "descargado_y_recortado",
        "producto": "CHIRPS v3 monthly final, LATAM subset",
        "archivos_anuales": outputs,
        "meses_totales": sum(x["meses"] for x in outputs),
        "fuente": index,
        "limite_espacial": "Polígono nacional de Argentina, resolución nativa 0.05°",
        "nota": "Se conserva la precipitación mensual en NetCDF. No se infieren valores diarios. La versión diaria CHIRPS sat se deriva de IMERG Late y no se considera una descarga independiente de IMERG."
    }

def fetch_ina_catalog(name: str, base: str, out: Path):
    attempts = [f"{base}/{name}?format=json", f"{base}/{name}&format=json"]
    last_error = None
    for url in attempts:
        try:
            response = get(url)
            payload = response.json()
            raw = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
            out.parent.mkdir(parents=True, exist_ok=True)
            with gzip.open(out, "wb", compresslevel=9) as f:
                f.write(raw)
            return {
                "estado": "descargado",
                "url": url,
                "archivo": str(out),
                "bytes_comprimidos": out.stat().st_size,
                "sha256": sha256(out),
                "tipo": type(payload).__name__,
                "registros": len(payload) if isinstance(payload, (list, dict)) else None
            }
        except Exception as exc:
            last_error = str(exc)
    return {"estado": "fallido", "error": last_error, "endpoints_probados": attempts}

def ingest_ina(manifest: dict):
    base = "https://alerta.ina.gob.ar/pub/datos"
    out = ROOT / "hidrologia" / "ina-dsiyah" / "catalogos"
    catalogues = {}
    for name in ("redes", "estaciones", "variables", "unidades", "series"):
        catalogues[name] = fetch_ina_catalog(name, base, out / f"{name}.json.gz")
        time.sleep(0.4)
    manifest["INA_DSIYAH"] = {
        "estado": "catalogos_descargados" if any(x.get("estado") == "descargado" for x in catalogues.values()) else "sin_descarga",
        "catalogos": catalogues,
        "fuente": "https://alerta.ina.gob.ar/pub/gui",
        "nota": "El portal consultado corresponde al sistema DSIyAH de la cuenca del Plata; no equivale por sí solo a cobertura hidrológica nacional completa. Se archivan catálogos de redes, estaciones, variables, unidades y series. Las observaciones de cada serie requieren una extracción posterior con rangos temporales y control de volumen."
    }

def main():
    manifest = {
        "titulo": "Ingesta inicial de datasets meteorológicos e hidrológicos",
        "creado_utc": datetime.now(timezone.utc).isoformat(),
        "repositorio": "D4nSosa/laboratorio-datos-meteorologicos",
        "alcance": "Argentina; archivos fuente originales y subconjuntos procesados",
        "datasets": {}
    }
    errors = {}
    for name, fn in (("IGRA", ingest_igra), ("CHIRPS_v3", ingest_chirps), ("INA_DSIYAH", ingest_ina)):
        try:
            fn(manifest["datasets"])
        except Exception as exc:
            errors[name] = f"{type(exc).__name__}: {exc}"
            manifest["datasets"][name] = {"estado": "fallido", "error": errors[name]}
            print(f"ERROR {name}: {errors[name]}")
    manifest["errores"] = errors
    manifest["estado_general"] = "completo_sin_errores" if not errors else "parcial_con_errores"
    manifest_path = ROOT / "manifiestos" / "ingesta-meteorologica-hidrologica.json"
    save_json(manifest_path, manifest)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    if errors:
        raise SystemExit(1)

if __name__ == "__main__":
    main()
