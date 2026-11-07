#!/usr/bin/env python3
"""Normalize Argentine IGRA profiles to annual CSV.gz standard-pressure/surface levels."""
import csv,gzip,hashlib,io,json,zipfile
from contextlib import ExitStack
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path("datos/fuentes-externas/radiosondeos/igra")
RAW=ROOT/"originales"
STATIONS=ROOT/"estaciones-argentina.csv"
OUT=ROOT/"perfiles-estandar"
INDEX=ROOT/"indice-sondeos"
MANIFEST=ROOT/"manifiesto-perfiles-normalizados.json"

LEVEL_FIELDS=[
"station_id","station_name","sounding_time_utc","release_time_utc",
"level_type_major","level_type_minor","elapsed_time_mmss","elapsed_time_seconds",
"pressure_pa","pressure_hpa","pressure_flag","geopotential_height_m","geopotential_flag",
"temperature_c","temperature_flag","relative_humidity_pct","dewpoint_depression_c",
"wind_direction_deg","wind_speed_ms"
]
INDEX_FIELDS=[
"station_id","station_name","sounding_time_utc","observation_hour_utc",
"release_time_utc","num_levels","standard_or_surface_levels",
"pressure_source","nonpressure_source","header_latitude","header_longitude"
]

def integer(line,a,b):
    try:
        n=int(line[a:b].strip())
        return None if n in (-9999,-8888) else n
    except Exception:return None

def elapsed_seconds(raw):
    if raw is None:return None
    try:
        n=int(raw)
        if n<0:return None
        return (n//100)*60+(n%100)
    except Exception:return None

def iso_time(year,month,day,hour):
    if None in (year,month,day,hour) or hour==99:return None
    try:return f"{year:04d}-{month:02d}-{day:02d}T{hour:02d}:00:00Z"
    except Exception:return None

def sha(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""):h.update(b)
    return h.hexdigest()

def main():
    OUT.mkdir(parents=True,exist_ok=True);INDEX.mkdir(parents=True,exist_ok=True)
    with STATIONS.open(encoding="utf-8",newline="") as f:
        station_rows=list(csv.DictReader(f))
    names={r["station_id"]:r["station_name"] for r in station_rows}
    counts={};sources=[];missing=[]
    with ExitStack() as stack:
        level_writers={};index_writers={}
        level_files={};index_files={}
        def writer_for(year,kind):
            cache=level_writers if kind=="levels" else index_writers
            files=level_files if kind=="levels" else index_files
            if year not in cache:
                folder=OUT if kind=="levels" else INDEX
                path=folder/f"{year}.csv.gz"
                f=stack.enter_context(gzip.open(path,"wt",encoding="utf-8",newline="",compresslevel=8))
                fields=LEVEL_FIELDS if kind=="levels" else INDEX_FIELDS
                w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
                cache[year]=w;files[year]=path
            return cache[year]
        for sid in sorted(names):
            path=RAW/f"{sid}-data.txt.zip"
            if not path.exists():
                missing.append(sid);continue
            source={"station_id":sid,"file":str(path),"bytes":path.stat().st_size,"sha256":sha(path)}
            try:
                with zipfile.ZipFile(path) as z:
                    bad=z.testzip()
                    if bad:raise RuntimeError(f"ZIP corrupto: {bad}")
                    member=next((x for x in z.namelist() if x.endswith(".txt")),None)
                    if not member:raise RuntimeError("ZIP sin TXT")
                    with z.open(member) as raw:
                        text=io.TextIOWrapper(raw,encoding="ascii",errors="replace")
                        iterator=iter(text)
                        soundings=0;levels=0;standard=0
                        for line in iterator:
                            line=line.rstrip("\r\n")
                            if not line.startswith("#") or len(line)<71:continue
                            year=integer(line,13,17);month=integer(line,18,20)
                            day=integer(line,21,23);hour=integer(line,24,26)
                            release=line[27:31].strip()
                            try:numlev=int(line[31:36].strip() or "0")
                            except ValueError:numlev=0
                            psrc=line[37:45].strip();npsrc=line[46:54].strip()
                            hlat=integer(line,55,62);hlon=integer(line,63,71)
                            sounding=iso_time(year,month,day,hour)
                            level_count=0;selected_count=0
                            for _ in range(max(0,numlev)):
                                raw_level=next(iterator,"")
                                raw_level=raw_level.rstrip("\r\n")
                                if len(raw_level)<51:continue
                                major=integer(raw_level,0,1)
                                minor=integer(raw_level,1,2)
                                etime=integer(raw_level,3,8)
                                pressure=integer(raw_level,9,15)
                                pflag=raw_level[15:16].strip() or None
                                gph=integer(raw_level,16,21)
                                zflag=raw_level[21:22].strip() or None
                                temp=integer(raw_level,22,27)
                                tflag=raw_level[27:28].strip() or None
                                rh=integer(raw_level,28,33)
                                dpdp=integer(raw_level,34,39)
                                wdir=integer(raw_level,40,45)
                                wspd=integer(raw_level,46,51)
                                level_count+=1
                                levels+=1
                                if major!=1 and minor!=1:continue
                                selected_count+=1
                                if year is None:continue
                                writer=writer_for(year,"levels")
                                writer.writerow({
                                    "station_id":sid,"station_name":names[sid],
                                    "sounding_time_utc":sounding,
                                    "release_time_utc":release if release and release!="9999" else None,
                                    "level_type_major":major,"level_type_minor":minor,
                                    "elapsed_time_mmss":etime,"elapsed_time_seconds":elapsed_seconds(etime),
                                    "pressure_pa":pressure,
                                    "pressure_hpa":round(pressure/100,3) if pressure is not None else None,
                                    "pressure_flag":pflag,"geopotential_height_m":gph,
                                    "geopotential_flag":zflag,
                                    "temperature_c":round(temp/10,1) if temp is not None else None,
                                    "temperature_flag":tflag,
                                    "relative_humidity_pct":round(rh/10,1) if rh is not None else None,
                                    "dewpoint_depression_c":round(dpdp/10,1) if dpdp is not None else None,
                                    "wind_direction_deg":wdir,
                                    "wind_speed_ms":round(wspd/10,1) if wspd is not None else None
                                })
                                standard+=1
                            if year is not None:
                                writer_for(year,"index").writerow({
                                    "station_id":sid,"station_name":names[sid],
                                    "sounding_time_utc":sounding,
                                    "observation_hour_utc":hour,
                                    "release_time_utc":release if release and release!="9999" else None,
                                    "num_levels":numlev,"standard_or_surface_levels":selected_count,
                                    "pressure_source":psrc,"nonpressure_source":npsrc,
                                    "header_latitude":hlat/10000 if hlat is not None else None,
                                    "header_longitude":hlon/10000 if hlon is not None else None
                                })
                            soundings+=1
                source.update({"status":"parsed","soundings":soundings,
                    "all_levels_seen":levels,"standard_surface_levels":standard})
                counts[sid]=source
                print(f"IGRA {sid}: {soundings} soundings, {standard} standard/surface rows",flush=True)
            except Exception as e:
                source.update({"status":"failed","error":f"{type(e).__name__}: {e}"})
                counts[sid]=source
    files=[]
    for year,path in sorted(level_files.items()):
        files.append({"type":"standard_surface_levels","year":year,"file":str(path),
                      "bytes":path.stat().st_size,"sha256":sha(path)})
    for year,path in sorted(index_files.items()):
        files.append({"type":"sounding_index","year":year,"file":str(path),
                      "bytes":path.stat().st_size,"sha256":sha(path)})
    manifest={
        "dataset":"NOAA IGRA 2.2 Argentina soundings — normalized standard-pressure and surface levels",
        "source":"https://www.ncei.noaa.gov/pub/data/igra/data/data-por/",
        "format_documentation":"https://www.ncei.noaa.gov/pub/data/igra/data/igra2-data-format.txt",
        "retrieved_utc":datetime.now(timezone.utc).isoformat(),
        "stations_requested":len(names),"stations_parsed":sum(1 for x in counts.values() if x.get("status")=="parsed"),
        "missing_archives":missing,"station_results":list(counts.values()),
        "files":files,
        "level_selection":"Retains LVLTYP1=1 standard pressure levels and LVLTYP2=1 surface levels. All variable/height levels remain in the original ZIP archives.",
        "unit_conversions":{
            "pressure_pa":"raw pressure in Pa; hPa = Pa / 100",
            "temperature_c":"raw tenths of degrees Celsius; °C = raw / 10",
            "relative_humidity_pct":"raw tenths of percent; % = raw / 10",
            "dewpoint_depression_c":"raw tenths of degrees Celsius; °C = raw / 10",
            "wind_speed_ms":"raw tenths of m/s; m/s = raw / 10",
            "geopotential_height_m":"meters","wind_direction_deg":"degrees from north"
        },
        "quality_note":"Raw missing/quality-removed codes -9999 and -8888 become null. PFLAG, ZFLAG and TFLAG are retained. Nominal observation hour and release time are distinct and both preserved.",
        "scope_note":"Structured output covers the 20 Argentine ARM stations. Neighboring South American station archives are retained separately as original ZIPs."
    }
    MANIFEST.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in manifest.items() if k not in ("station_results","files")},ensure_ascii=False,indent=2))
    if any(x.get("status")=="failed" for x in counts.values()):raise SystemExit(1)

if __name__=="__main__":main()
