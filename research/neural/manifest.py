"""Validation for event-aware ML sample manifests; no ML dependencies required."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any

SPLITS = {"train", "validation", "test"}
REQUIRED = {"sample_id", "event_id", "asset_path", "label", "split", "source_ids", "observed_at"}

def validate_manifest(manifest: dict[str, Any], root: str | Path) -> list[str]:
    errors: list[str] = []
    samples = manifest.get("samples") if isinstance(manifest, dict) else None
    if not isinstance(samples, list):
        return ["samples debe ser una lista."]
    sample_ids: set[str] = set()
    event_splits: dict[str, str] = {}
    base = Path(root).resolve()
    for index, sample in enumerate(samples):
        prefix = f"samples[{index}]"
        if not isinstance(sample, dict):
            errors.append(f"{prefix} debe ser un objeto.")
            continue
        missing = sorted(REQUIRED - sample.keys())
        if missing:
            errors.append(f"{prefix} no contiene: {', '.join(missing)}.")
            continue
        sid, eid, split = sample["sample_id"], sample["event_id"], sample["split"]
        if not isinstance(sid, str) or not sid or sid in sample_ids:
            errors.append(f"{prefix}.sample_id debe ser único y no vacío.")
        sample_ids.add(sid)
        if split not in SPLITS:
            errors.append(f"{prefix}.split no es válido.")
        if eid in event_splits and event_splits[eid] != split:
            errors.append(f"Fuga entre particiones: event_id {eid} aparece en {event_splits[eid]} y {split}.")
        event_splits[eid] = split
        if not isinstance(sample["source_ids"], list) or not sample["source_ids"]:
            errors.append(f"{prefix}.source_ids debe ser una lista no vacía.")
        if not isinstance(sample["observed_at"], str) or "T" not in sample["observed_at"] or not (sample["observed_at"].endswith("Z") or "+" in sample["observed_at"][10:]):
            errors.append(f"{prefix}.observed_at debe incluir fecha, hora y zona horaria.")
        asset = Path(str(sample["asset_path"]))
        resolved = (base / asset).resolve()
        if not resolved.is_relative_to(base):
            errors.append(f"{prefix}.asset_path intenta salir del directorio del dataset.")
        elif not resolved.is_file():
            errors.append(f"{prefix}.asset_path no existe: {sample['asset_path']}.")
    return errors

def load_manifest(path: str | Path) -> dict[str, Any]:
    with Path(path).open(encoding="utf-8") as stream:
        return json.load(stream)
