import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from estimator.calculate import calculate
from estimator.schemas import Scenario
from estimator.scenarios import export_json
from estimator.loaders import ROOT
result=calculate(Scenario())
(ROOT/"outputs/demo_coffee.json").write_text(export_json(result))
print("DEMO Seattle coffee scenario:",result["total"])
