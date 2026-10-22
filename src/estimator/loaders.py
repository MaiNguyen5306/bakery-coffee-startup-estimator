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
    # Evidence-derived defaults override demo fixtures only after explicit promotion.
    promoted_ids=set()
    for r in rows(ROOT / "data/processed/assumptions.csv"):
        if r["assumption_id"] in promoted_ids: raise ValueError("Duplicate promoted assumption")
        promoted_ids.add(r["assumption_id"])
        if r["city"]!="Seattle" or r["estimate_year"]!="2026": raise ValueError("Inapplicable promoted assumption")
        if number(r["low"])>number(r["high"]): raise ValueError("Reversed promoted range")
        if r["assumption_id"] in result:
            if r["unit"] != result[r["assumption_id"]]["unit"]: raise ValueError("Promoted assumption unit mismatch")
        result[r["assumption_id"]] = {**r,"low":number(r["low"]),"high":number(r["high"])}
    return result


def configuration_fingerprint():
    import hashlib
    names = ("equipment_packages.json", "staffing_presets.json", "model_settings.json", "permit_fees.json")
    return hashlib.sha256(b"".join((ROOT/"config"/name).read_bytes() for name in names)).hexdigest()
