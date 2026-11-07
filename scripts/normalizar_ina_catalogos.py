#!/usr/bin/env python3
"""Normalize the public INA DSIyAH JSON catalogues already archived as gzip."""
import csv, gzip, json
from pathlib import Path

ROOT=Path("datos/fuentes-externas/hidrologia/ina-dsiyah/catalogos")
NAMES=("redes","estaciones","variables","unidades","series")

def records(payload):
    if isinstance(payload,list): return payload
    if isinstance(payload,dict):
        for key in ("data","rows","items","records","results","series","estaciones","redes","variables","unidades"):
            value=payload.get(key)
            if isinstance(value,list): return value
    return []

def clean(v):
    if isinstance(v,(dict,list)): return json.dumps(v,ensure_ascii=False,separators=(",",":"))
    return v

def main():
    summary={}
    for name in NAMES:
        path=ROOT/f"{name}.json.gz"
        if not path.exists():
            summary[name]={"status":"missing"}
            continue
        with gzip.open(path,"rt",encoding="utf-8") as f: payload=json.load(f)
        rows=records(payload)
        keys=sorted({k for row in rows if isinstance(row,dict) for k in row})
        summary[name]={
            "status":"normalized" if rows else "payload_is_object_without_recognized_array",
            "top_level_type":type(payload).__name__,
            "top_level_keys":list(payload.keys()) if isinstance(payload,dict) else None,
            "records":len(rows),"record_fields":keys,
            "sample":rows[0] if rows else payload
        }
        if rows and all(isinstance(row,dict) for row in rows):
            out=ROOT/f"{name}-normalizado.csv.gz"
            with gzip.open(out,"wt",encoding="utf-8",newline="",compresslevel=9) as f:
                w=csv.DictWriter(f,fieldnames=keys,extrasaction="ignore")
                w.writeheader()
                for row in rows: w.writerow({k:clean(row.get(k)) for k in keys})
            summary[name]["normalized_file"]=str(out)
            summary[name]["normalized_rows"]=len(rows)
        print(f"{name}: top={summary[name]['top_level_keys']} records={summary[name]['records']} fields={keys[:20]}",flush=True)
    out=ROOT/"catalogos-normalizados.json"
    out.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:{x:v for x,v in val.items() if x!="sample"} for k,val in summary.items()},ensure_ascii=False,indent=2))

if __name__=="__main__": main()
