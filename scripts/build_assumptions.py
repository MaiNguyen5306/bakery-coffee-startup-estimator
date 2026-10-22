import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from estimator.research import inspect_raw
from estimator.loaders import ROOT
inventory=inspect_raw()
print(f"Inspected {len(inventory)} raw files. Outputs in data/interim.")
print("Raw audit complete. Run derive_wage_assumptions.py to reproduce reviewed role wages; other categories still need applicability/coverage review.")
