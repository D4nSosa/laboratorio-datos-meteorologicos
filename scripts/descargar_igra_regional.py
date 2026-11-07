#!/usr/bin/env python3
"""Download IGRA 2.2 sounding archives for Argentina and nearby South America."""
import csv, hashlib, json, re, time, urllib.error, urllib.request, zipfile
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin

BASE="https://www.ncei.noaa.gov/pub/data/igra/data/data-por/"
ROOT=Path("datos/fuentes-externas/radiosondeos/igra")
INVENTORY=ROOT/"estaciones-contexto-sudamerica.csv"
OUT=ROOT/"originales"
MANIFEST=ROOT/"manifiesto-perfiles-sudamerica.json"
USER_AGENT="LaboratorioDatosMeteorologicos/1.0 (research; public-data-ingestion)"

class LinkParser(HTMLParser):
    def __init__(self): super().__init__(); self.hrefs=[]
    def handle_starttag(self,tag,attrs):
        if tag.lower()=="a":
            href=dict(attrs).get("href")
            if href: self.hrefs.append(href)

def request(url,attempts=7):
    last=None
    for i in range(attempts):
        try:
            req=urllib.request.Request(url,headers={"User-Agent":USER_AGENT})
            return urllib.request.urlopen(req,timeout=120)
        except urllib.error.HTTPError as e:
            last=e
            if e.code not in (429,500,502,503,504) or i==attempts-1: raise
            retry=e.headers.get("Retry-After")
            try: delay=int(retry) if retry else min(30*(2**i),600)
            except ValueError: delay=min(30*(2**i),600)
            print(f"HTTP {e.code}; reintento en {delay}s: {url}",flush=True)
            time.sleep(delay)
        except Exception as e:
            last=e
            if i==attempts-1: raise
            delay=min(15*(2**i),300)
            print(f"Error de red; reintento en {delay}s: {e}",flush=True)
            time.sleep(delay)
    raise last

def sha256(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""): h.update(b)
    return h.hexdigest()

def main():
    if not INVENTORY.exists(): raise FileNotFoundError(INVENTORY)
    with INVENTORY.open(encoding="utf-8",newline="") as f:
        rows=list(csv.DictReader(f))
    ids=sorted({r["station_id"] for r in rows})
    OUT.mkdir(parents=True,exist_ok=True)
    parser=LinkParser()
    with request(BASE) as r: parser.feed(r.read().decode("utf-8","replace"))
    available={}
    for href in parser.hrefs:
        name=href.rsplit("/",1)[-1]
        m=re.fullmatch(r"([A-Z0-9]{11})-data\.txt\.zip",name)
        if m and m.group(1) in ids: available[m.group(1)]=urljoin(BASE,href)
    results=[]
    errors=[]
    for n,sid in enumerate(ids,1):
        name=f"{sid}-data.txt.zip"
        path=OUT/name
        url=available.get(sid)
        if not url:
            errors.append({"station_id":sid,"error":"No aparece archivo period-of-record en índice oficial."})
            continue
        if path.exists() and path.stat().st_size>0:
            try:
                with zipfile.ZipFile(path) as z:
                    bad=z.testzip()
                if bad is None:
                    results.append({"station_id":sid,"file":str(path),"bytes":path.stat().st_size,
                        "sha256":sha256(path),"status":"already_present","url":url})
                    continue
            except Exception: pass
            path.unlink(missing_ok=True)
        tmp=path.with_suffix(path.suffix+".part")
        try:
            total=0
            with request(url) as r, tmp.open("wb") as f:
                while True:
                    chunk=r.read(1024*1024)
                    if not chunk: break
                    total+=len(chunk)
                    if total>90*1024*1024:
                        raise RuntimeError("Archivo supera 90 MiB; no se sube a GitHub sin revisar.")
                    f.write(chunk)
            with zipfile.ZipFile(tmp) as z:
                bad=z.testzip()
                if bad: raise RuntimeError(f"ZIP corrupto, miembro {bad}")
            tmp.replace(path)
            result={"station_id":sid,"file":str(path),"bytes":path.stat().st_size,
                    "sha256":sha256(path),"status":"downloaded_and_zip_validated","url":url}
            results.append(result)
            print(f"[{n}/{len(ids)}] OK {sid} {path.stat().st_size} bytes",flush=True)
            time.sleep(4)
        except Exception as e:
            tmp.unlink(missing_ok=True)
            errors.append({"station_id":sid,"url":url,"error":f"{type(e).__name__}: {e}"})
            print(f"[{n}/{len(ids)}] ERROR {sid}: {e}",flush=True)
            time.sleep(10)
    manifest={
        "dataset":"NOAA/NCEI IGRA 2.2 period-of-record sounding files",
        "retrieved_utc":datetime.now(timezone.utc).isoformat(),
        "source_index":BASE,
        "source_inventory":"https://www.ncei.noaa.gov/pub/data/igra/igra2-station-list.txt",
        "region":"South America context bbox lat -60..-10, lon -85..-30; includes all Argentine ARM stations in that window",
        "inventory_station_count":len(ids),
        "files":results,
        "files_validated":len(results),
        "errors":errors,
        "not_downloaded":[sid for sid in ids if not any(x["station_id"]==sid for x in results)],
        "validation":"Each ZIP was opened and testzip() checked; SHA-256 recorded.",
        "note":"Station IDs and source files are preserved. Nearby IDs are not merged; regional inventory is a geographic context set, not a claim of uniform radiosonde coverage."
    }
    MANIFEST.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in manifest.items() if k!="files"},ensure_ascii=False,indent=2))
    if errors: raise SystemExit(1)

if __name__=="__main__": main()
