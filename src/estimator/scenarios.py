import json
from .schemas import Scenario
from .loaders import configuration_fingerprint
from .calculate import calculate
from . import MODEL_VERSION, DATA_VERSION

def export_json(result):
    return json.dumps(result, indent=2, allow_nan=False)

def reproduce(payload):
    data = json.loads(payload)
    if data["model_version"] != MODEL_VERSION or data["data_version"] != DATA_VERSION: raise ValueError("Version mismatch")
    if data.get("configuration_fingerprint") != configuration_fingerprint(): raise ValueError("Configuration fingerprint mismatch")
    result = calculate(Scenario(**data["scenario"]), {k:[v["low"],v["high"]] for k,v in data["assumptions"].items()}, data["mode"])
    if result["total"] != data["total"]: raise ValueError("Export does not reproduce with this configuration")
    return result

def changed_inputs(baseline, alternative):
    return {k: {"baseline": v,"alternative": alternative["scenario"][k]} for k,v in baseline["scenario"].items() if alternative["scenario"][k]!=v}
