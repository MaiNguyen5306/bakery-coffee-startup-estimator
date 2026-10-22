from pathlib import Path
import csv
import json
from .normalize import number
ROOT = Path(__file__).resolve().parents[2]

def rows(path):
    with Path(path).open(newline="", encoding="utf-8-sig") as f: return list(csv.DictReader(f))

def config(name):
    return json.loads((ROOT / "config" / name).read_text())

def assumptions():
    result = {}
    for r in rows(ROOT / "data/demo/assumptions.csv"):
        if r["assumption_id"] in result: raise ValueError("Duplicate assumption")
        lo, hi = number(r["low"]), number(r["high"])
        if lo > hi: raise ValueError("Reversed range")
        result[r["assumption_id"]] = {**r, "low": lo, "high": hi}
    return result


def configuration_fingerprint():
    import hashlib
    names = ("equipment_packages.json", "staffing_presets.json", "model_settings.json")
    return hashlib.sha256(b"".join((ROOT/"config"/name).read_bytes() for name in names)).hexdigest()
