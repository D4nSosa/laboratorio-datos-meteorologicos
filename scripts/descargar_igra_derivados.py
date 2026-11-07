#!/usr/bin/env python3
"""Download and normalize NOAA IGRA 2.2 sounding-derived parameters and levels."""
import csv,gzip,hashlib,json,re,time,urllib.error,urllib.request,zipfile,io
from datetime import datetime,timezone
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urljoin

BASE="https://www.ncei.noaa.gov/pub/data/igra/derived/derived-por/"
ROOT=Path("datos/fuentes-externas/radiosondeos/igra")
INVENTORY=ROOT/"estaciones-argentina.csv"
OUT=ROOT/"derivados-originales"
LEVEL_OUT=ROOT/"niveles-derivados"
CSV_OUT=ROOT/"parametros-derivados-por-sondeo.csv.gz"
MANIFEST=ROOT/"manifiesto-parametros-derivados.json"
UA="LaboratorioDatosMeteorologicos/1.0"

HEADER_FIELDS=[
"station_id","year","month","day","hour_utc","release_time_hhmm_utc","sounding_time_utc","num_levels",
"precipitable_water_raw","precipitable_water_mm","inversion_pressure_raw","inversion_height_m",
"inversion_temp_difference_raw","inversion_temp_difference_k","mixing_pressure_raw","mixing_height_m",
"freezing_pressure_raw","freezing_height_m","lcl_pressure_raw","lcl_height_m","lfc_pressure_raw",
"lfc_height_m","lnb_pressure_raw","lnb_height_m","lifted_index_c","showalter_index_c","k_index_c",
"total_totals_index_c","cape_j_kg","cin_j_kg","source_file"
]
LEVEL_FIELDS=[
"station_id","sounding_time_utc","year","month","day","hour_utc","release_time_hhmm_utc","level_index",
"pressure_pa","pressure_hpa","reported_geopotential_height_m","calculated_geopotential_height_m",
"temperature_k","temperature_c","temperature_gradient_k_per_km","potential_temperature_k",
"potential_temperature_gradient_k_per_km","virtual_temperature_k","virtual_potential_temperature_k",
"vapor_pressure_mb","saturation_vapor_pressure_mb","relative_humidity_reported_pct",
"relative_humidity_calculated_pct","relative_humidity_gradient_pct_per_km","u_wind_ms",
"u_wind_gradient_ms_per_km","v_wind_ms","v_wind_gradient_ms_per_km","refractive_index"
]

class Parser(HTMLParser):
    def __init__(self):super().__init__();self.hrefs=[]
    def handle_starttag(self,tag,attrs):
        if tag.lower()=="a":
            h=dict(attrs).get("href")
            if h:self.hrefs.append(h)

def req(url,attempts=6):
    last=None
    for i in range(attempts):
        try:
            return urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":UA}),timeout=120)
        except urllib.error.HTTPError as e:
            last=e
            if e.code not in (429,500,502,503,504) or i==attempts-1:raise
            delay=min(30*(2**i),600)
            print(f"IGRA derived HTTP {e.code}; reintento en {delay}s",flush=True)
            time.sleep(delay)
        except Exception as e:
            last=e
            if i==attempts-1:raise
            time.sleep(min(15*(2**i),300))
    raise last

def sha(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""):h.update(b)
    return h.hexdigest()

def val(line,a,b):
    s=line[a:b].strip()
    if not s:return None
    try:
        n=int(s)
        return None if n==-99999 else n
    except ValueError:return None

def scaled(n,divisor,ndigits=3,offset=0.0):
    return round(n/divisor+offset,ndigits) if n is not None else None

def parse_header(line,source_file):
    year=val(line,13,17);month=val(line,18,20);day=val(line,21,23);hour=val(line,24,26)
    release=line[27:31].strip()
    sounding=(f"{year:04d}-{month:02d}-{day:02d}T{hour:02d}:00:00Z"
              if None not in (year,month,day,hour) and hour!=99 else None)
    pw=val(line,37,43);invtemp=val(line,55,61)
    return {
        "station_id":line[1:12].strip(),"year":year,"month":month,"day":day,
        "hour_utc":None if hour==99 else hour,
        "release_time_hhmm_utc":None if not release or release=="9999" else release,
        "sounding_time_utc":sounding,"num_levels":val(line,31,36) or 0,
        "precipitable_water_raw":pw,"precipitable_water_mm":scaled(pw,100,2),
        "inversion_pressure_raw":val(line,43,49),"inversion_height_m":val(line,49,55),
        "inversion_temp_difference_raw":invtemp,"inversion_temp_difference_k":scaled(invtemp,10,1),
        "mixing_pressure_raw":val(line,61,67),"mixing_height_m":val(line,67,73),
        "freezing_pressure_raw":val(line,73,79),"freezing_height_m":val(line,79,85),
        "lcl_pressure_raw":val(line,85,91),"lcl_height_m":val(line,91,97),
        "lfc_pressure_raw":val(line,97,103),"lfc_height_m":val(line,103,109),
        "lnb_pressure_raw":val(line,109,115),"lnb_height_m":val(line,115,121),
        "lifted_index_c":val(line,121,127),"showalter_index_c":val(line,127,133),
        "k_index_c":val(line,133,139),"total_totals_index_c":val(line,139,145),
        "cape_j_kg":val(line,145,151),"cin_j_kg":val(line,151,157),
        "source_file":source_file
    }

def parse_level(line,header,index):
    p=val(line,0,7);temp=val(line,24,31);ptemp=val(line,40,47)
    vtemp=val(line,56,63);vptemp=val(line,64,71)
    vp=val(line,72,79);sat=val(line,80,87)
    return {
        "station_id":header["station_id"],"sounding_time_utc":header["sounding_time_utc"],
        "year":header["year"],"month":header["month"],"day":header["day"],
        "hour_utc":header["hour_utc"],"release_time_hhmm_utc":header["release_time_hhmm_utc"],
        "level_index":index,
        "pressure_pa":p,"pressure_hpa":scaled(p,100,2),
        "reported_geopotential_height_m":val(line,8,15),
        "calculated_geopotential_height_m":val(line,16,23),
        "temperature_k":scaled(temp,10,1),"temperature_c":scaled(temp,10,2,-273.15),
        "temperature_gradient_k_per_km":scaled(val(line,32,39),10,2),
        "potential_temperature_k":scaled(ptemp,10,1),
        "potential_temperature_gradient_k_per_km":scaled(val(line,48,55),10,2),
        "virtual_temperature_k":scaled(vtemp,10,1),
        "virtual_potential_temperature_k":scaled(vptemp,10,1),
        "vapor_pressure_mb":scaled(vp,1000,3),
        "saturation_vapor_pressure_mb":scaled(sat,1000,3),
        "relative_humidity_reported_pct":scaled(val(line,88,95),10,1),
        "relative_humidity_calculated_pct":scaled(val(line,96,103),10,1),
        "relative_humidity_gradient_pct_per_km":scaled(val(line,104,111),10,2),
        "u_wind_ms":scaled(val(line,112,119),10,1),
        "u_wind_gradient_ms_per_km":scaled(val(line,120,127),10,2),
        "v_wind_ms":scaled(val(line,128,135),10,1),
        "v_wind_gradient_ms_per_km":scaled(val(line,136,143),10,2),
        "refractive_index":val(line,144,151)
    }

def main():
    with INVENTORY.open(encoding="utf-8",newline="") as f:
        ids={r["station_id"] for r in csv.DictReader(f)}
    parser=Parser()
    with req(BASE) as r:parser.feed(r.read().decode("utf-8","replace"))
    urls={}
    for href in parser.hrefs:
        name=href.rsplit("/",1)[-1]
        m=re.fullmatch(r"([A-Z0-9]{11})-drvd\.txt\.zip",name)
        if m and m.group(1) in ids:urls[m.group(1)]=urljoin(BASE,href)
    OUT.mkdir(parents=True,exist_ok=True);LEVEL_OUT.mkdir(parents=True,exist_ok=True)
    files=[];errors=[];not_available=[];soundings_total=0;levels_total=0
    with gzip.open(CSV_OUT,"wt",encoding="utf-8",newline="",compresslevel=9) as header_file:
        header_writer=csv.DictWriter(header_file,fieldnames=HEADER_FIELDS);header_writer.writeheader()
        for n,sid in enumerate(sorted(ids),1):
            url=urls.get(sid)
            if not url:
                not_available.append(sid);continue
            path=OUT/f"{sid}-drvd.txt.zip"
            try:
                if not path.exists() or path.stat().st_size==0:
                    tmp=path.with_suffix(".zip.part")
                    with req(url) as r,tmp.open("wb") as f:
                        while True:
                            b=r.read(1024*1024)
                            if not b:break
                            f.write(b)
                    with zipfile.ZipFile(tmp) as z:
                        bad=z.testzip()
                        if bad:raise RuntimeError(f"ZIP corrupto: {bad}")
                    tmp.replace(path)
                with zipfile.ZipFile(path) as z:
                    bad=z.testzip()
                    if bad:raise RuntimeError(f"ZIP corrupto: {bad}")
                    member=next((x for x in z.namelist() if x.endswith(".txt")),None)
                    if not member:raise RuntimeError("ZIP sin TXT")
                    level_path=LEVEL_OUT/f"{sid}-niveles-derivados.csv.gz"
                    station_soundings=0;station_levels=0
                    with z.open(member) as raw,io.TextIOWrapper(raw,encoding="ascii",errors="replace") as text, gzip.open(level_path,"wt",encoding="utf-8",newline="",compresslevel=8) as level_file:
                        level_writer=csv.DictWriter(level_file,fieldnames=LEVEL_FIELDS);level_writer.writeheader()
                        iterator=iter(text)
                        for line in iterator:
                            line=line.rstrip("\r\n")
                            if not line.startswith("#") or len(line)<157:continue
                            header=parse_header(line,path.name)
                            header_writer.writerow(header)
                            station_soundings+=1
                            numlev=header["num_levels"]
                            for idx in range(numlev):
                                data_line=next(iterator,"").rstrip("\r\n")
                                if len(data_line)<151:continue
                                level_writer.writerow(parse_level(data_line,header,idx))
                                station_levels+=1
                    if level_path.stat().st_size>90*1024*1024:
                        raise RuntimeError(f"Tabla derivada supera 90 MiB: {level_path.stat().st_size}")
                    soundings_total+=station_soundings;levels_total+=station_levels
                    files.append({"station_id":sid,"source_file":str(path),"source_bytes":path.stat().st_size,
                        "source_sha256":sha(path),"soundings":station_soundings,
                        "derived_levels":station_levels,"levels_file":str(level_path),
                        "levels_bytes":level_path.stat().st_size,"levels_sha256":sha(level_path),
                        "source_url":url})
                    print(f"[{n}/{len(ids)}] {sid}: {station_soundings} soundings, {station_levels} derived levels",flush=True)
                    time.sleep(2)
            except Exception as e:
                errors.append({"station_id":sid,"error":f"{type(e).__name__}: {e}"})
                print(f"ERROR {sid}: {e}",flush=True)
    manifest={
        "dataset":"NOAA/NCEI IGRA 2.2 sounding-derived parameters and pressure-level diagnostics",
        "source":BASE,"documentation":"https://www.ncei.noaa.gov/data/integrated-global-radiosonde-archive/doc/igra2-derived-format.txt",
        "retrieved_utc":datetime.now(timezone.utc).isoformat(),
        "station_ids_requested":len(ids),"files_downloaded":len(files),
        "stations_without_derived_product":not_available,
        "soundings_with_derived_parameters":soundings_total,"derived_pressure_levels":levels_total,
        "header_csv":{"file":str(CSV_OUT),"bytes":CSV_OUT.stat().st_size,"sha256":sha(CSV_OUT)},
        "files":files,"errors":errors,
        "header_units":{
            "precipitable_water_mm":"PW raw / 100; source unit mm*100",
            "inversion_temp_difference_k":"raw / 10; source unit K*10",
            "pressure_fields":"raw Pa or mb*100 as specified by NOAA; preserve raw integer",
            "heights":"meters above surface",
            "stability_indices":"degrees Celsius",
            "cape_j_kg":"J/kg","cin_j_kg":"J/kg"
        },
        "level_units":{
            "pressure_hpa":"raw Pa / 100","temperature_k":"raw / 10","temperature_c":"raw / 10 - 273.15",
            "temperature_gradient_k_per_km":"raw / 10","potential_temperature_k":"raw / 10",
            "potential_temperature_gradient_k_per_km":"raw / 10","virtual_temperature_k":"raw / 10",
            "virtual_potential_temperature_k":"raw / 10","vapor_pressure_mb":"raw / 1000",
            "saturation_vapor_pressure_mb":"raw / 1000","relative_humidity_pct":"raw / 10",
            "relative_humidity_gradient_pct_per_km":"raw / 10","u_wind_ms":"raw / 10",
            "u_wind_gradient_ms_per_km":"raw / 10","v_wind_ms":"raw / 10",
            "v_wind_gradient_ms_per_km":"raw / 10","refractive_index":"dimensionless"
        },
        "quality_note":"NOAA missing code -99999 becomes null. Original ZIP files remain archived unchanged.",
        "coverage_note":"Derived parameters are published only for a subset of IGRA soundings. Station IDs absent from the derived index are expected omissions, not failures."
    }
    MANIFEST.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in manifest.items() if k!="files"},ensure_ascii=False,indent=2))
    if errors:raise SystemExit(1)

if __name__=="__main__":main()
