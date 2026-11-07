#!/usr/bin/env python3
"""Normalize the official IGRA 2.2 station inventory for Argentina and South America."""
import csv, json, math, re
from pathlib import Path

ROOT=Path("datos/fuentes-externas/radiosondeos/igra")
SOURCE=Path("datos/fuentes-externas/radiosondeos/igra2-station-list.txt")
PATTERN=re.compile(r"^(\S+)\s+(-?\d+(?:\.\d+)?)\s+(-?\d+(?:\.\d+)?)\s+(-?\d+(?:\.\d+)?)\s+(.*?)\s+(\d{4})\s+(\d{4})\s+(\d+)\s*$")

def parse():
    rows=[]
    for line in SOURCE.read_text(encoding="utf-8",errors="replace").splitlines():
        m=PATTERN.match(line)
        if not m: continue
        sid,lat,lon,elev,name,first,last,count=m.groups()
        rows.append({"station_id":sid,"latitude":float(lat),"longitude":float(lon),
            "elevation_m":None if float(elev)<-900 else float(elev),
            "station_name":name.strip(),"first_year":int(first),"last_year":int(last),
            "observation_count":int(count),"source_version":"IGRA 2.2"})
    return rows

def write_csv(path,rows):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0].keys()))
        w.writeheader();w.writerows(rows)

def main():
    if not SOURCE.exists():
        raise FileNotFoundError(f"Falta inventario original IGRA: {SOURCE}")
    rows=parse()
    argentina=sorted([r for r in rows if r["station_id"].startswith("ARM")],key=lambda x:x["station_id"])
    if not argentina: raise RuntimeError("No se hallaron estaciones ARM en el inventario oficial.")
    write_csv(ROOT/"estaciones-argentina.csv",argentina)
    geo={"type":"FeatureCollection","name":"IGRA_Argentina","features":[
        {"type":"Feature","geometry":{"type":"Point","coordinates":[r["longitude"],r["latitude"]]},
         "properties":{k:v for k,v in r.items() if k not in ("latitude","longitude")}}
        for r in argentina]}
    (ROOT/"estaciones-argentina.geojson").write_text(json.dumps(geo,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

    regional=[{**r,"is_argentina":r["station_id"].startswith("ARM")}
        for r in rows if -60<=r["latitude"]<=-10 and -85<=r["longitude"]<=-30]
    regional.sort(key=lambda x:x["station_id"])
    write_csv(ROOT/"estaciones-contexto-sudamerica.csv",regional)

    nearby=[]
    for i,a in enumerate(argentina):
        for b in argentina[i+1:]:
            p1,p2=math.radians(a["latitude"]),math.radians(b["latitude"])
            dp=math.radians(b["latitude"]-a["latitude"])
            dl=math.radians(b["longitude"]-a["longitude"])
            h=math.sin(dp/2)**2+math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
            km=6371*2*math.asin(math.sqrt(h))
            if km<=25:
                overlap=max(a["first_year"],b["first_year"])<=min(a["last_year"],b["last_year"])
                nearby.append({"station_a":a["station_id"],"name_a":a["station_name"],
                    "station_b":b["station_id"],"name_b":b["station_name"],
                    "distance_km":round(km,2),"periods_overlap":overlap,
                    "review_note":"Proximity candidate only; not a proven duplicate or relocation."})
    if nearby: write_csv(ROOT/"posibles-estaciones-cercanas.csv",nearby)
    summary={"source":str(SOURCE),"source_version":"IGRA 2.2",
        "stations_argentina":len(argentina),"stations_regional_context":len(regional),
        "nearby_pairs_for_review":len(nearby),
        "files":[str(ROOT/"estaciones-argentina.csv"),str(ROOT/"estaciones-argentina.geojson"),
                 str(ROOT/"estaciones-contexto-sudamerica.csv"),
                 str(ROOT/"posibles-estaciones-cercanas.csv")],
        "note":"No station IDs are merged. Nearby pairs are flags for manual review only."}
    (ROOT/"inventario-normalizado.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(summary,ensure_ascii=False,indent=2))

if __name__=="__main__": main()
