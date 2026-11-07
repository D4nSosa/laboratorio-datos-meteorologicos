#!/usr/bin/env python3
import csv,gzip,json,collections
from pathlib import Path
ROOT=Path("datos/fuentes-externas/hidrologia/ina-dsiyah/catalogos")
def load(name):
    with gzip.open(ROOT/f"{name}.json.gz","rt",encoding="utf-8") as f:return json.load(f).get("data",[])
def main():
    stations=load("estaciones")
    series=load("series")
    variables=load("variables")
    by_site={str(x.get("sitecode")):x for x in stations}
    var_names={str(x.get("id")):x.get("nombre") for x in variables}
    selected=[s for s in series if (by_site.get(str(s.get("sitecode")),{}).get("pais") or "").lower()=="argentina"]
    counts=collections.Counter(str(s.get("varid")) for s in selected)
    obs=collections.defaultdict(int)
    for s in selected:
        obs[str(s.get("varid"))]+=int(s.get("obs_count") or 0)
    report={
      "stations_catalog_rows":len(stations),
      "stations_argentina":sum(1 for s in stations if (s.get("pais") or "").lower()=="argentina"),
      "series_catalog_rows":len(series),
      "series_argentina":len(selected),
      "variables":[{"varid":k,"name":var_names.get(k),"series":counts[k],"observations_catalog_sum":obs[k]}
                   for k in sorted(counts,key=lambda x:int(x) if x.isdigit() else 999999)],
      "observations_catalog_sum_argentina":sum(int(s.get("obs_count") or 0) for s in selected),
      "download_strategy":"Use per-series requests with <=20,000 observations; prioritize complete series by variable and station, do not exceed source request limits."
    }
    (ROOT/"resumen-series-argentina.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    with gzip.open(ROOT/"series-argentina.csv.gz","wt",encoding="utf-8",newline="",compresslevel=9) as f:
      fields=list(selected[0].keys()) if selected else []
      w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(selected)
    print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
