#!/usr/bin/env python3
"""Discover public AgroClima station pages and build a reproducible station inventory.

The scan is intentionally bounded and polite. It does not scrape measurements or
claim that a page is an active station unless station-specific evidence is found.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import json
import re
import time
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin

import requests

BASES = (
    "https://agroclima.com/public/estacion.php?id={station_id}",
    "https://agroclima.com/3/public/estacion.php?id={station_id}",
)
MAP_URL = "https://agroclima.com/3/public/mapa.php"
SEEDS = (1490, 1528, 1578, 1584, 1609, 1620)
USER_AGENT = "LaboratorioMeteorologicoNacional/1.0 (public research; station catalogue)"
TIMEOUT = 18


class PageText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
        self.scripts = []
        self._script = False
        self._current_script = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() == "script":
            self._script = True
            self._current_script = []

    def handle_endtag(self, tag):
        if tag.lower() == "script" and self._script:
            self.scripts.append("".join(self._current_script))
            self._script = False

    def handle_data(self, data):
        if self._script:
            self._current_script.append(data)
        else:
            value = data.strip()
            if value:
                self.parts.append(value)


def clean(value: str | None) -> str | None:
    if not value:
        return None
    value = re.sub(r"\\s+", " ", value).strip(" \\t\\r\\n:-")
    return value or None


def extract_station(station_id: int, session: requests.Session) -> dict | None:
    for template in BASES:
        url = template.format(station_id=station_id)
        try:
            response = session.get(url, timeout=TIMEOUT)
            if response.status_code == 404:
                continue
            if response.status_code != 200 or len(response.text) < 300:
                continue
            parser = PageText()
            parser.feed(response.text)
            text = clean(" ".join(parser.parts)) or ""
            low = text.lower()
            # Reject generic pages, login pages, and server error templates.
            evidence = sum(token in low for token in (
                "temperatura", "humedad", "precipitación", "precipitacion",
                "presión", "presion", "estación", "estacion", "viento",
                "última actualización", "ultima actualizacion",
            ))
            if evidence < 2 or any(x in low for x in (
                "no se encontró la estación", "estacion no encontrada",
                "estación inexistente", "estacion inexistente", "access denied",
                "forbidden", "internal server error",
            )):
                continue

            name = None
            patterns = (
                r"Estación\\s*:\\s*([^|]{3,100}?)(?=\\s+(?:Temperatura|Humedad|Viento|Presión|Presion|Lluvia|Precipitación))",
                r"(?:Estación|Estacion)\\s+([^|]{3,100}?)(?=\\s+(?:Temperatura|Humedad|Viento|Presión|Presion|Lluvia|Precipitación))",
            )
            for pattern in patterns:
                match = re.search(pattern, text, re.I)
                if match:
                    name = clean(match.group(1))
                    break

            lat = lon = None
            # Coordinate pairs in visible text or embedded scripts/JSON.
            coord_text = response.text
            pairs = re.findall(r"(-?\\d{1,2}\\.\\d{4,})\\s*[,;]\\s*(-?\\d{1,3}\\.\\d{4,})", coord_text)
            for a, b in pairs:
                x, y = float(a), float(b)
                if -60 <= x <= 15 and -85 <= y <= -30:
                    lat, lon = x, y
                    break
                if -85 <= x <= -30 and -60 <= y <= 15:
                    lat, lon = y, x
                    break

            updated = None
            m = re.search(r"(?:última observación|ultima observacion|actualizado|actualización)\\s*:?\\s*([^|]{5,50})", text, re.I)
            if m:
                updated = clean(m.group(1))

            return {
                "provider": "AgroClima",
                "station_id": station_id,
                "name": name or f"Estación AgroClima {station_id}",
                "latitude": lat,
                "longitude": lon,
                "last_observation_label": updated,
                "page_url": response.url,
                "catalog_status": "page_validated",
                "evidence_terms": evidence,
                "checked_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            }
        except requests.RequestException:
            continue
    return None


def discover_map_assets(session: requests.Session) -> dict:
    """Inspect map HTML and linked JS for station/API references (no execution)."""
    result = {"map_url": MAP_URL, "scripts": [], "candidate_urls": [], "station_ids_in_html": []}
    try:
        response = session.get(MAP_URL, timeout=TIMEOUT)
        response.raise_for_status()
        html = response.text
        result["station_ids_in_html"] = sorted({int(x) for x in re.findall(
            r"(?:estacion(?:_id)?|station(?:_id)?)\\D{0,12}(\\d{3,5})", html, re.I
        )})
        parser = PageText()
        parser.feed(html)
        srcs = re.findall(r'<script[^>]+src=[\\"\\']([^\\"\\']+)', html, re.I)
        for src in srcs:
            script_url = urljoin(response.url, src)
            result["scripts"].append(script_url)
            try:
                js = session.get(script_url, timeout=TIMEOUT).text
                # Record likely JSON/API endpoints for later review, without blindly calling them.
                for candidate in re.findall(r'[\\"\\']([^\\"\\']*(?:api|estacion|station|mapa)[^\\"\\']*)[\\"\\']', js, re.I):
                    if candidate.startswith(("http://", "https://", "/", "./")):
                        result["candidate_urls"].append(urljoin(script_url, candidate))
                result["station_ids_in_html"].extend(int(x) for x in re.findall(
                    r"(?:estacion(?:_id)?|station(?:_id)?)\\D{0,12}(\\d{3,5})", js, re.I
                ))
            except requests.RequestException:
                continue
    except requests.RequestException as exc:
        result["map_error"] = str(exc)
    result["station_ids_in_html"] = sorted(set(result["station_ids_in_html"]))
    result["candidate_urls"] = sorted(set(result["candidate_urls"]))
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-id", type=int, default=1400)
    ap.add_argument("--max-id", type=int, default=1700)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--output-dir", default="datos/agroclima")
    args = ap.parse_args()
    if args.min_id < 1 or args.max_id < args.min_id or args.max_id - args.min_id > 1500:
        raise SystemExit("Rango inválido: el máximo permitido es 1501 IDs por ejecución.")

    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT, "Accept": "text/html,application/xhtml+xml"})
    map_assets = discover_map_assets(session)
    ids = set(range(args.min_id, args.max_id + 1)) | set(SEEDS) | set(map_assets["station_ids_in_html"])
    found = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, min(args.workers, 5))) as pool:
        futures = {pool.submit(extract_station, station_id, session): station_id for station_id in sorted(ids)}
        for future in concurrent.futures.as_completed(futures):
            item = future.result()
            if item:
                found.append(item)
            time.sleep(0.015)

    found.sort(key=lambda item: item["station_id"])
    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)
    generated = datetime.now(timezone.utc).isoformat(timespec="seconds")
    payload = {
        "dataset": "AgroClima public station page inventory",
        "generated_at_utc": generated,
        "source_map": MAP_URL,
        "scan": {"min_id": args.min_id, "max_id": args.max_id, "candidate_ids": len(ids)},
        "station_count": len(found),
        "stations": found,
        "limitations": [
            "A validated station page does not prove that observations are current or historically complete.",
            "Coordinates and last-observation labels may be absent when not exposed in page text.",
            "The ID range is bounded and may not include every AgroClima station.",
            "Map JavaScript/API candidates are recorded for inspection; this script does not call undocumented endpoints.",
        ],
        "map_inspection": map_assets,
    }
    (output / "estaciones.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\\n", encoding="utf-8")
    lines = ["provider,station_id,name,latitude,longitude,last_observation_label,page_url,catalog_status"]
    for s in found:
        vals = [s["provider"], s["station_id"], s["name"], s["latitude"], s["longitude"],
                s["last_observation_label"], s["page_url"], s["catalog_status"]]
        import csv
        from io import StringIO
        buf = StringIO()
        csv.writer(buf).writerow(vals)
        lines.append(buf.getvalue().strip())
    (output / "estaciones.csv").write_text("\\n".join(lines) + "\\n", encoding="utf-8")
    print(f"IDs candidatos: {len(ids)} | páginas validadas: {len(found)}")
    print(f"Archivos: {output / 'estaciones.json'} y {output / 'estaciones.csv'}")


if __name__ == "__main__":
    main()
