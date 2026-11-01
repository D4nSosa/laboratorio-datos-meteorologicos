"""Dataset manifest validation; metadata is kept separate from data payloads."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import Any

OBSERVATION_TYPES = {"station_observation", "satellite_estimate", "radar_product", "reanalysis", "forecast", "derived"}
QUALITY_STATES = {"unreviewed", "structural_check_passed", "scientifically_reviewed", "rejected"}

def _iso(value: Any, field: str) -> datetime:
    if not isinstance(value, str):
        raise ValueError(f"{field} debe ser una fecha ISO 8601.")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{field} no es una fecha ISO 8601 válida.") from exc
    if parsed.tzinfo is None:
        raise ValueError(f"{field} debe incluir zona horaria.")
    return parsed

@dataclass(frozen=True)
class DatasetManifest:
    dataset_id: str
    source_id: str
    product: str
    variable: str
    observation_type: str
    units: str
    temporal_resolution: str
    spatial_resolution: str
    time_start: str
    time_end: str
    retrieved_at: str
    source_url: str
    quality_status: str
    checksum_sha256: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DatasetManifest":
        required = {"dataset_id", "source_id", "product", "variable", "observation_type", "units", "temporal_resolution", "spatial_resolution", "time_start", "time_end", "retrieved_at", "source_url", "quality_status"}
        missing = sorted(required - data.keys())
        if missing:
            raise ValueError("Faltan campos obligatorios: " + ", ".join(missing))
        item = cls(**{key: data.get(key) for key in cls.__dataclass_fields__})
        item.validate()
        return item

    def validate(self) -> None:
        for field in ("dataset_id", "source_id", "product", "variable", "units", "temporal_resolution", "spatial_resolution"):
            value = getattr(self, field)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{field} debe ser texto no vacío.")
        if self.observation_type not in OBSERVATION_TYPES:
            raise ValueError("observation_type no está permitido.")
        if self.quality_status not in QUALITY_STATES:
            raise ValueError("quality_status no está permitido.")
        if not isinstance(self.source_url, str) or not self.source_url.startswith("https://"):
            raise ValueError("source_url debe ser HTTPS.")
        start, end = _iso(self.time_start, "time_start"), _iso(self.time_end, "time_end")
        _iso(self.retrieved_at, "retrieved_at")
        if start > end:
            raise ValueError("time_start no puede ser posterior a time_end.")
        if self.checksum_sha256 is not None and (len(self.checksum_sha256) != 64 or any(c not in "0123456789abcdefABCDEF" for c in self.checksum_sha256)):
            raise ValueError("checksum_sha256 debe contener 64 caracteres hexadecimales.")
