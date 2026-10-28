import importlib.util
import math
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load_module(name, relative_path):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

era5 = load_module("descargar_era5", "investigaciones/01-precipitacion-virasoro/scripts/descargar_era5.py")
santo = load_module("analizar_santo_tome", "investigaciones/01-precipitacion-virasoro/scripts/analizar_santo_tome.py")

class Era5ValidationTests(unittest.TestCase):
    def test_accepts_exact_daily_sequence(self):
        import pandas as pd
        dates = pd.date_range(era5.START_DATE, era5.END_DATE, freq="D")
        frame = pd.DataFrame({"fecha": dates, "precipitacion_mm": [0.0] * len(dates)})
        era5.validate_daily(frame)

    def test_rejects_missing_date_even_when_count_is_close(self):
        import pandas as pd
        dates = pd.date_range(era5.START_DATE, era5.END_DATE, freq="D").delete(10)
        frame = pd.DataFrame({"fecha": dates, "precipitacion_mm": [0.0] * len(dates)})
        with self.assertRaises(RuntimeError):
            era5.validate_daily(frame)

    def test_rejects_infinite_precipitation(self):
        import pandas as pd
        dates = pd.date_range(era5.START_DATE, era5.END_DATE, freq="D")
        values = [0.0] * len(dates)
        values[0] = math.inf
        frame = pd.DataFrame({"fecha": dates, "precipitacion_mm": values})
        with self.assertRaises(RuntimeError):
            era5.validate_daily(frame)

    def test_rejects_negative_precipitation(self):
        import pandas as pd
        dates = pd.date_range(era5.START_DATE, era5.END_DATE, freq="D")
        values = [0.0] * len(dates)
        values[0] = -0.1
        frame = pd.DataFrame({"fecha": dates, "precipitacion_mm": values})
        with self.assertRaises(RuntimeError):
            era5.validate_daily(frame)

class SantoTomeValidationTests(unittest.TestCase):
    def test_accepts_twelve_valid_months(self):
        self.assertEqual(len(santo.valid_months({"months": [0.0] * 12})), 12)

    def test_rejects_incomplete_months(self):
        self.assertIsNone(santo.valid_months({"months": [1.0] * 11}))

    def test_rejects_non_numeric_boolean_and_infinite_months(self):
        self.assertIsNone(santo.valid_months({"months": [1.0] * 11 + ["2"]}))
        self.assertIsNone(santo.valid_months({"months": [1.0] * 11 + [True]}))
        self.assertIsNone(santo.valid_months({"months": [1.0] * 11 + [math.inf]}))

if __name__ == "__main__":
    unittest.main()
