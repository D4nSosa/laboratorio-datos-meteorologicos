"""Command-line checks for laboratory metadata."""
from __future__ import annotations
import argparse
import sys
from pathlib import Path
from .catalog import load_json, validate_event_catalog, validate_source_catalog
ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCES = ROOT / "docs" / "datos" / "catalogo-fuentes.json"
DEFAULT_EVENTS = ROOT / "research" / "events" / "catalog.json"

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validaciones de metadatos del Laboratorio Meteorológico Nacional")
    parser.add_argument("target", choices=("sources", "events"), help="Catálogo a validar")
    parser.add_argument("--path", help="Ruta alternativa al catálogo JSON")
    args = parser.parse_args(argv)
    path = Path(args.path) if args.path else (DEFAULT_SOURCES if args.target == "sources" else DEFAULT_EVENTS)
    try:
        catalog = load_json(path)
        errors = validate_source_catalog(catalog) if args.target == "sources" else validate_event_catalog(catalog)
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    count = len(catalog.get("sources", [])) if args.target == "sources" else len(catalog.get("events", []))
    print(f"OK: {path} — {count} registros validados.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
