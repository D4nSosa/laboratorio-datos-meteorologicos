"""Validation helpers for the public source and event catalogues."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any

ALLOWED_SOURCE_STATUSES = {"archived", "documented", "not_integrated", "investigation_required"}
REQUIRED_SOURCE_FIELDS = {"id", "name", "organization", "type", "status", "products", "variables", "temporal_resolution", "spatial_resolution", "coverage", "url", "limitations"}

def load_json(path: str | Path) -> Any:
    with Path(path).open(encoding="utf-8") as stream:
        return json.load(stream)

def validate_source_catalog(catalog: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not isinstance(catalog, dict):
        return ["El catálogo debe ser un objeto JSON."]
    if not catalog.get("schema_version"):
        errors.append("Falta schema_version.")
    sources = catalog.get("sources")
    if not isinstance(sources, list):
        return errors + ["sources debe ser una lista."]
    seen: set[str] = set()
    for index, source in enumerate(sources):
        prefix = f"sources[{index}]"
        if not isinstance(source, dict):
            errors.append(f"{prefix} debe ser un objeto.")
            continue
        missing = sorted(REQUIRED_SOURCE_FIELDS - source.keys())
        if missing:
            errors.append(f"{prefix} no contiene: {', '.join(missing)}.")
        source_id = source.get("id")
        if not isinstance(source_id, str) or not source_id.strip():
            errors.append(f"{prefix}.id debe ser texto no vacío.")
        elif source_id in seen:
            errors.append(f"Identificador de fuente duplicado: {source_id}.")
        else:
            seen.add(source_id)
        if source.get("status") not in ALLOWED_SOURCE_STATUSES:
            errors.append(f"{prefix}.status no pertenece al vocabulario permitido.")
        for field in ("products", "variables"):
            if not isinstance(source.get(field), list) or not source.get(field):
                errors.append(f"{prefix}.{field} debe ser una lista no vacía.")
        url = source.get("url", "")
        if not isinstance(url, str) or not url.startswith("https://"):
            errors.append(f"{prefix}.url debe ser una URL HTTPS.")
    return errors

def validate_event_catalog(catalog: dict[str, Any]) -> list[str]:
    if not isinstance(catalog, dict):
        return ["El catálogo de eventos debe ser un objeto JSON."]
    events = catalog.get("events")
    if not isinstance(events, list):
        return ["events debe ser una lista."]
    errors: list[str] = []
    seen: set[str] = set()
    required = {"event_id", "phenomenon", "start_time", "end_time", "region", "status", "evidence"}
    for index, event in enumerate(events):
        prefix = f"events[{index}]"
        if not isinstance(event, dict):
            errors.append(f"{prefix} debe ser un objeto.")
            continue
        missing = sorted(required - event.keys())
        if missing:
            errors.append(f"{prefix} no contiene: {', '.join(missing)}.")
            continue
        event_id = event["event_id"]
        if not isinstance(event_id, str) or not event_id.strip() or event_id in seen:
            errors.append(f"{prefix}.event_id debe ser único y no vacío.")
        seen.add(event_id)
        if event["status"] not in {"candidate", "reviewed", "confirmed", "rejected"}:
            errors.append(f"{prefix}.status no es válido.")
        if not isinstance(event["evidence"], list) or not event["evidence"]:
            errors.append(f"{prefix}.evidence debe contener al menos una evidencia.")
    return errors
