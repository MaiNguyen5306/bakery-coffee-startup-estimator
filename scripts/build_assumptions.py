import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from estimator.research import inspect_raw
from estimator.loaders import ROOT
inventory=inspect_raw()
print(f"Inspected {len(inventory)} raw files. Outputs in data/interim.")
print("No research assumptions promoted: provenance, applicability and coverage require analyst review.")
