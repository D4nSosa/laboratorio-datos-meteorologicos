#!/usr/bin/env python3
"""Build an auditable inventory of public AgroClima station pages."""
from __future__ import annotations
import argparse, concurrent.futures, csv, json, re, time
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin
import requests

BASES=("https://agroclima.com/public/estacion.php?id={station_id}",
       "https://agroclima.com/3/public/estacion.php?id={station_id}")
MAP_URL="https://agroclima.com/3/public/mapa.php"
SEEDS=(1490,1528,1578,1584,1609,1620)
UA="LaboratorioMeteorologicoNacional/1.1 (public research; station catalogue)"
GENERIC=re.compile(r"^(?:estaci[oó]n\s+)?agroclima(?:\s+\d+)?$",re.I)

class Parsed(HTMLParser):
    def __init__(self):
        super().__init__(); self.text=[]; self.scripts=[]; self.titles=[]; self.headings=[]; self.meta={}
        self.mode=None; self.buf=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs); tag=tag.lower()
        if tag in ("script","title","h1","h2"): self.mode=tag; self.buf=[]
        if tag=="meta":
            k=(a.get("property") or a.get("name") or "").lower()
            if k and a.get("content"): self.meta[k]=a["content"]
    def handle_endtag(self,tag):
        if tag==self.mode:
            value="".join(self.buf)
            {"script":self.scripts,"title":self.titles,"h1":self.headings,"h2":self.headings}.get(tag,[]).append(value)
            self.mode=None
    def handle_data(self,data):
        if self.mode: self.buf.append(data)
        if self.mode!="script" and data.strip(): self.text.append(data.strip())

def clean(s):
    return re.sub(r"\s+"," ",s).strip(" \t\r\n:-|") if s else None

def station_name(p,visible):
    candidates=[(p.meta.get(k),k) for k in ("og:title","twitter:title")]
    candidates += [(x,"heading") for x in p.headings]+[(x,"title") for x in p.titles]
    for pat in (r"(?:nombre\s+de\s+la\s+estaci[oó]n|estaci[oó]n)\s*[:：]\s*([^|;]{3,100})",
                r"(?:nombre\s+estaci[oó]n)\s*=\s*['\"]([^'\"]{3,100})"):
        m=re.search(pat,visible,re.I)
        if m: candidates.append((m.group(1),"explicit_label"))
    for raw,src in candidates:
        n=clean(raw)
        if not n: continue
        n=re.sub(r"\s*[|–-]\s*(?:AgroClima.*)?$","",n,flags=re.I).strip()
        if len(n)<=100 and not GENERIC.match(n) and not re.search(r"temperatura|humedad|precipitaci[oó]n|pron[oó]stico|mapa",n,re.I):
            return n,src
    return None,None

def pair(a,b):
    try: x,y=float(a),float(b)
    except ValueError: return None
    if -60<=x<=15 and -85<=y<=-30: return round(x,7),round(y,7)
    if -85<=x<=-30 and -60<=y<=15: return round(y,7),round(x,7)
    return None

def coordinates(src):
    pats=[
      (r"(?:latitude|latitud|lat)\s*['\"]?\s*[:=]\s*['\"]?(-?\d{1,2}\.\d+).*?(?:longitude|longitud|lng|lon)\s*['\"]?\s*[:=]\s*['\"]?(-?\d{1,3}\.\d+)","labelled"),
      (r"(?:longitude|longitud|lng|lon)\s*['\"]?\s*[:=]\s*['\"]?(-?\d{1,3}\.\d+).*?(?:latitude|latitud|lat)\s*['\"]?\s*[:=]\s*['\"]?(-?\d{1,2}\.\d+)","labelled"),
      (r"(?:setView|L\.marker|marker|center)\s*\(\s*\[\s*(-?\d{1,2}\.\d+)\s*,\s*(-?\d{1,3}\.\d+)","map_array"),
      (r"\{\s*lat\s*:\s*(-?\d{1,2}\.\d+)\s*,\s*(?:lng|lon)\s*:\s*(-?\d{1,3}\.\d+)\s*\}","map_object"),
      (r"""["'](?:lat|latitude)["']\s*:\s*(-?\d{1,2}\.\d+)\s*,\s*["'](?:lng|lon|longitude)["']\s*:\s*(-?\d{1,3}\.\d+)""","json_labels")]
    for pat,kind in pats:
        m=re.search(pat,src,re.I|re.S)
        if m:
            xy=pair(m.group(1),m.group(2))
            if xy:return xy[0],xy[1],kind
    for a,b in re.findall(r"(-?\d{1,2}\.\d{4,})\s*[,;]\s*(-?\d{1,3}\.\d{4,})",src):
        xy=pair(a,b)
        if xy:return xy[0],xy[1],"unlabelled_pair"
    return None,None,None

def last_obs(text):
    date=r"((?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}-\d{2}-\d{2})(?:[ T,]+\d{1,2}:\d{2}(?::\d{2})?)?)"
    labels=r"(?:última\s+observaci[oó]n|último\s+registro|datos\s+actualizados?|última\s+actualizaci[oó]n)"
    m=re.search(labels+r"\s*[:：-]?\s*"+date,text,re.I)
    return clean(m.group(1)) if m else None

def extract(sid,session):
    for base in BASES:
        try:
            r=session.get(base.format(station_id=sid),timeout=18)
            if r.status_code!=200 or len(r.text)<300: continue
            p=Parsed();p.feed(r.text); visible=clean(" ".join(p.text)) or ""; low=visible.lower()
            evidence=sum(t in low for t in ("temperatura","humedad","precipitación","precipitacion","presión","presion","estación","estacion","viento","lluvia","meteorológica","meteorologica"))
            if evidence<2 or any(t in low for t in ("estacion no encontrada","estación inexistente","estacion inexistente","access denied","forbidden","internal server error")): continue
            src=r.text+"\n"+"\n".join(p.scripts)
            name,name_src=station_name(p,visible); lat,lon,coord_src=coordinates(src)
            return {"provider":"AgroClima","station_id":sid,"name":name,"name_source":name_src,
              "latitude":lat,"longitude":lon,"coordinate_source":coord_src,"last_observation":last_obs(visible),
              "page_url":r.url,"catalog_status":"page_validated",
              "metadata_quality":"complete" if name and lat is not None and lon is not None else "partial",
              "evidence_terms":evidence,"checked_at_utc":datetime.now(timezone.utc).isoformat(timespec="seconds")}
        except requests.RequestException: pass
    return None

def map_assets(session):
    out={"map_url":MAP_URL,"scripts":[],"candidate_urls":[],"station_ids_in_html":[]}
    try:
        r=session.get(MAP_URL,timeout=18);r.raise_for_status(); html=r.text
        rx=r"(?:estacion(?:_id)?|station(?:_id)?)\D{0,12}(\d{3,5})"
        out["station_ids_in_html"]=sorted({int(x) for x in re.findall(rx,html,re.I)})
        for src in re.findall(r"""<script[^>]+src=["']([^"']+)""",html,re.I):
            u=urljoin(r.url,src);out["scripts"].append(u)
            try:
                js=session.get(u,timeout=18).text
                out["station_ids_in_html"] += [int(x) for x in re.findall(rx,js,re.I)]
                out["candidate_urls"] += [urljoin(u,x) for x in re.findall(r"""["']([^"']*(?:api|estacion|station|mapa)[^"']*)["']""",js,re.I) if x.startswith(("http://","https://","/","./"))]
            except requests.RequestException: pass
    except requests.RequestException as e: out["map_error"]=str(e)
    out["station_ids_in_html"]=sorted(set(out["station_ids_in_html"]));out["candidate_urls"]=sorted(set(out["candidate_urls"]))
    return out

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--min-id",type=int,default=1400);ap.add_argument("--max-id",type=int,default=1700)
    ap.add_argument("--workers",type=int,default=4);ap.add_argument("--output-dir",default="datos/agroclima");a=ap.parse_args()
    if a.min_id<1 or a.max_id<a.min_id or a.max_id-a.min_id>1500: raise SystemExit("Rango inválido: máximo 1501 IDs.")
    s=requests.Session();s.headers.update({"User-Agent":UA,"Accept":"text/html,application/xhtml+xml"})
    mi=map_assets(s);ids=set(range(a.min_id,a.max_id+1))|set(SEEDS)|set(mi["station_ids_in_html"]);found=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1,min(a.workers,5))) as pool:
        fs=[pool.submit(extract,i,s) for i in sorted(ids)]
        for f in concurrent.futures.as_completed(fs):
            x=f.result()
            if x:found.append(x)
            time.sleep(.015)
    found.sort(key=lambda x:x["station_id"]);out=Path(a.output_dir);out.mkdir(parents=True,exist_ok=True)
    summary={"with_name":sum(bool(x["name"]) for x in found),"with_coordinates":sum(x["latitude"] is not None and x["longitude"] is not None for x in found),
      "with_last_observation":sum(bool(x["last_observation"]) for x in found),"complete_metadata":sum(x["metadata_quality"]=="complete" for x in found)}
    data={"dataset":"AgroClima public station page inventory","generated_at_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),
      "source_map":MAP_URL,"scan":{"min_id":a.min_id,"max_id":a.max_id,"candidate_ids":len(ids)},"station_count":len(found),
      "metadata_summary":summary,"stations":found,"limitations":[
      "A validated page proves only that a public page with meteorological evidence exists; it does not prove current operation.",
      "Missing names, coordinates and observation dates remain null rather than being guessed.",
      "Unlabelled coordinate pairs are marked and require manual review.",
      "The bounded ID scan does not guarantee a complete provider catalogue.",
      "This inventory does not download or integrate observations."],"map_inspection":mi}
    (out/"estaciones.json").write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    fields=["provider","station_id","name","name_source","latitude","longitude","coordinate_source","last_observation","page_url","catalog_status","metadata_quality"]
    with (out/"estaciones.csv").open("w",encoding="utf-8",newline="") as h:
        w=csv.DictWriter(h,fieldnames=fields);w.writeheader();w.writerows({k:x.get(k) for k in fields} for x in found)
    print(f"IDs candidatos: {len(ids)} | páginas validadas: {len(found)} | metadatos: {summary}")

if __name__=="__main__":main()
