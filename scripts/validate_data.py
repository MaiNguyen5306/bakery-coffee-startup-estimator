import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from estimator.loaders import ROOT, assumptions
from estimator.validation import validate_tables
from estimator.calculate import calculate
from estimator.schemas import Scenario
print("Research table schema validation:",validate_tables(ROOT/"data/processed"))
print("Combined default assumption rows:",len(assumptions()))
calculate(Scenario())
print("Mixed-evidence configuration valid. RESEARCH INCOMPLETE: templates are not evidence coverage.")

from estimator.revenue import validate_revenue_tables
print("Revenue evidence:",validate_revenue_tables(ROOT/"data/processed/revenue"))
