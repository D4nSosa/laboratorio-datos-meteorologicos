import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "research" / "neural"))

from lnm.catalog import validate_event_catalog, validate_source_catalog
from lnm.manifest import DatasetManifest
from manifest import validate_manifest

class SourceCatalogTests(unittest.TestCase):
    def test_repository_source_catalog_is_valid(self):
        catalog = json.loads((ROOT / "docs/datos/catalogo-fuentes.json").read_text(encoding="utf-8"))
        self.assertEqual(validate_source_catalog(catalog), [])
        self.assertGreaterEqual(len(catalog["sources"]), 10)

    def test_duplicate_source_ids_are_rejected(self):
        source = {"id":"same","name":"X","organization":"Y","type":"z","status":"archived","products":["p"],"variables":["v"],"temporal_resolution":"daily","spatial_resolution":"point","coverage":"test","url":"https://example.org","limitations":"test"}
        self.assertTrue(any("duplicado" in error for error in validate_source_catalog({"schema_version":"1","sources":[source,source]})))

class EventCatalogTests(unittest.TestCase):
    def test_empty_initial_catalog_is_valid(self):
        catalog = json.loads((ROOT / "research/events/catalog.json").read_text(encoding="utf-8"))
        self.assertEqual(validate_event_catalog(catalog), [])

    def test_event_without_evidence_is_rejected(self):
        event = {"event_id":"E1","phenomenon":"convective_candidate","start_time":"2026-01-01T00:00:00Z","end_time":"2026-01-01T01:00:00Z","region":{},"status":"candidate","evidence":[]}
        self.assertTrue(any("evidence" in error for error in validate_event_catalog({"events":[event]})))

class DatasetManifestTests(unittest.TestCase):
    def valid_record(self):
        return {"dataset_id":"demo-001","source_id":"era5","product":"ERA5 daily","variable":"total_precipitation","observation_type":"reanalysis","units":"mm","temporal_resolution":"daily","spatial_resolution":"grid cell","time_start":"2020-01-01T00:00:00Z","time_end":"2020-01-31T00:00:00Z","retrieved_at":"2026-11-01T12:00:00Z","source_url":"https://example.org/data","quality_status":"structural_check_passed","checksum_sha256":"a"*64}

    def test_valid_manifest(self):
        self.assertEqual(DatasetManifest.from_dict(self.valid_record()).source_id, "era5")

    def test_naive_timestamps_are_rejected(self):
        record = self.valid_record(); record["time_start"] = "2020-01-01T00:00:00"
        with self.assertRaisesRegex(ValueError, "zona horaria"):
            DatasetManifest.from_dict(record)

    def test_reversed_time_range_is_rejected(self):
        record = self.valid_record(); record["time_start"], record["time_end"] = record["time_end"], record["time_start"]
        with self.assertRaisesRegex(ValueError, "posterior"):
            DatasetManifest.from_dict(record)

class NeuralManifestTests(unittest.TestCase):
    def test_events_cannot_leak_across_splits(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); (root / "sample.npz").write_bytes(b"placeholder")
            base = {"event_id":"storm-1","asset_path":"sample.npz","label":"convective","source_ids":["goes_abi"],"observed_at":"2026-01-01T00:00:00Z"}
            manifest = {"samples":[dict(base,sample_id="a",split="train"),dict(base,sample_id="b",split="test")]}
            self.assertTrue(any("Fuga" in error for error in validate_manifest(manifest, root)))

    def test_asset_paths_cannot_escape_dataset_root(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            sample = {"sample_id":"a","event_id":"storm-a","asset_path":"../outside.npz","label":"x","split":"train","source_ids":["smn"],"observed_at":"2026-01-01T00:00:00Z"}
            self.assertTrue(any("salir" in error for error in validate_manifest({"samples":[sample]}, root)))

if __name__ == "__main__":
    unittest.main()
