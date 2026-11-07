#!/usr/bin/env python3
"""Download and normalize NOAA IGRA 2.2 sounding-derived stability parameters."""
import csv,gzip,hashlib,json,re,time,urllib.error,urllib.request,zipfile,io
from datetime import datetime,timezone
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urljoin

BASE="https://www.ncei.noaa.gov/pub/data/igra/derived/derived-por/"
ROOT=Path("datos/fuentes-externas/radiosondeos/igra")
INVENTORY=ROOT/"estaciones-argentina.csv"
OUT=ROOT/"derivados-originales"
CSV_OUT=ROOT/"parametros-derivados-por-sondeo.csv.gz"
MANIFEST=ROOT/"manifiesto-parametros-derivados.json"
UA="LaboratorioDatosMeteorologicos/1.0"

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

def value(line,a,b):
    s=line[a:b].strip()
    if not s:return None
    try:
        n=int(s)
        return None if n in (-99999,-8888) else n
    except ValueError:return None

def parse_headers(text):
    lines=text.splitlines()
    rows=[];i=0
    while i<len(lines):
        line=lines[i]
        if not line.startswith("#"):
            i+=1;continue
        if len(line)<157:
            i+=1;continue
        try:numlev=int(line[31:36].strip() or "0")
        except ValueError:numlev=0
        row={
            "station_id":line[1:12].strip(),
            "year":value(line,13,17),"month":value(line,18,20),
            "day":value(line,21,23),"hour_utc":value(line,24,26),
            "release_time_hhmm_utc":line[27:31].strip(),
            "num_levels":numlev,
            "precipitable_water_raw":value(line,37,43),
            "inversion_pressure_raw":value(line,43,49),
            "inversion_height_m":value(line,49,55),
            "inversion_temp_difference_raw":value(line,55,61),
            "mixing_pressure_raw":value(line,61,67),
            "mixing_height_m":value(line,67,73),
            "freezing_pressure_raw":value(line,73,79),
            "freezing_height_m":value(line,79,85),
            "lcl_pressure_raw":value(line,85,91),
            "lcl_height_m":value(line,91,97),
            "lfc_pressure_raw":value(line,97,103),
            "lfc_height_m":value(line,103,109),
            "lnb_pressure_raw":value(line,109,115),
            "lnb_height_m":value(line,115,121),
            "lifted_index_raw":value(line,121,127),
            "showalter_index_raw":value(line,127,133),
            "k_index_raw":value(line,133,139),
            "total_totals_index_raw":value(line,139,145),
            "cape_raw":value(line,145,151),
            "cin_raw":value(line,151,157)
        }
        rows.append(row)
        i+=1+max(0,numlev)
    return rows

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
    OUT.mkdir(parents=True,exist_ok=True)
    files=[];all_rows=[];errors=[]
    for n,sid in enumerate(sorted(ids),1):
        url=urls.get(sid)
        if not url:
            errors.append({"station_id":sid,"error":"No derived-por ZIP in official index."})
            continue
        path=OUT/f"{sid}-drvd.txt.zip"
        if not path.exists() or path.stat().st_size==0:
            tmp=path.with_suffix(".zip.part")
            try:
                with req(url) as r,tmp.open("wb") as f:
                    while True:
                        b=r.read(1024*1024)
                        if not b:break
                        f.write(b)
                with zipfile.ZipFile(tmp) as z:
                    bad=z.testzip()
                    if bad:raise RuntimeError(f"ZIP corrupto: {bad}")
                tmp.replace(path)
            except Exception as e:
                tmp.unlink(missing_ok=True);errors.append({"station_id":sid,"error":str(e)});continue
        try:
            with zipfile.ZipFile(path) as z:
                bad=z.testzip()
                if bad:raise RuntimeError(f"ZIP corrupto: {bad}")
                member=next((x for x in z.namelist() if x.endswith(".txt")),None)
                if not member:raise RuntimeError("ZIP sin archivo TXT")
                text=z.read(member).decode("ascii","replace")
            rows=parse_headers(text)
            for row in rows:
                row["source_product"]="IGRA 2.2 derived parameters"
                row["source_file"]=path.name
            all_rows.extend(rows)
            files.append({"station_id":sid,"file":str(path),"bytes":path.stat().st_size,
                "sha256":sha(path),"soundings_with_derived_parameters":len(rows),"url":url})
            print(f"[{n}/{len(ids)}] {sid}: {len(rows)} soundings with derived parameters",flush=True)
            time.sleep(3)
        except Exception as e:errors.append({"station_id":sid,"error":str(e)})
    fields=list(all_rows[0].keys()) if all_rows else []
    with gzip.open(CSV_OUT,"wt",encoding="utf-8",newline="",compresslevel=9) as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(all_rows)
    manifest={
        "dataset":"NOAA/NCEI IGRA 2.2 sounding-derived parameters",
        "source":BASE,"documentation":"https://www.ncei.noaa.gov/pub/data/igra/derived/igra2-derived-format.txt",
        "retrieved_utc":datetime.now(timezone.utc).isoformat(),
        "station_ids_requested":len(ids),"files_downloaded":len(files),
        "soundings_with_derived_parameters":len(all_rows),
        "normalized_csv":{"file":str(CSV_OUT),"bytes":CSV_OUT.stat().st_size,"sha256":sha(CSV_OUT)},
        "files":files,"errors":errors,
        "variables_note":"Raw integer values are preserved. Apply scale factors and units from NOAA's IGRA derived-parameter format documentation before plotting; missing/QA-removed codes -99999 and -8888 are stored as null.",
        "coverage_note":"Derived parameters are available only for a subset of IGRA soundings; absence does not mean no sounding exists."
    }
    MANIFEST.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in manifest.items() if k!="files"},ensure_ascii=False,indent=2))
    if errors:raise SystemExit(1)

if __name__=="__main__":main()
