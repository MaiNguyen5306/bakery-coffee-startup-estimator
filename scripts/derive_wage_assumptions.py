"""Reproduce reviewed wage promotion from supplied May 2025 metro benchmarks.

This is an editorial derivation, not a statistical interval or a 2026 survey.
"""
from pathlib import Path
import csv
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from estimator.loaders import ROOT, rows, config
from estimator.normalize import number


def derive():
    benchmarks=rows(ROOT/'data/interim/seattle_wages.csv')
    floor=config('model_settings.json')['wage_floor']['Seattle']['2026']
    target=ROOT/'data/processed/assumptions.csv'
    current=rows(target)
    templates={r['assumption_id']:r for r in rows(ROOT/'data/demo/assumptions.csv')}
    for key,soc in [('wage_service','35-3023'),('wage_baker','51-3011'),('wage_supervisor','35-1012')]:
        matches=[r for r in benchmarks if r['AREA']=='42660' and r['OCC_CODE']==soc]
        if len(matches)!=1: raise ValueError(f'Ambiguous role {soc}')
        row=matches[0]
        a=templates.get(key,templates['wage_service']).copy()
        a.update(assumption_id=key,item='Working supervisor hourly wage' if key=='wage_supervisor' else a['item'])
        a.update(low=max(floor,number(row['H_MEDIAN'])),high=max(floor,number(row['H_PCT75'])),calculation_basis='low=max(2026 Seattle floor, May 2025 metro H_MEDIAN); high=max(floor, H_PCT75); role-specific, no inflation assumption',evidence_ids=f'bls25_{soc}_H_MEDIAN;bls25_{soc}_H_PCT75;seattle_min_wage_2026',evidence_status='derived',confidence='low',effective_start='2026-01-01',effective_end='2026-12-31',notes='Metro benchmark adapted to Seattle floor; not a Seattle market quote. Percentiles selected editorially, not a confidence interval. Staffing and employer burden remain demo.')
        current=[r for r in current if r['assumption_id']!=key]+[a]
    fields=list(templates['wage_service'])
    with target.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields,lineterminator="\n");w.writeheader();w.writerows(sorted(current,key=lambda r:r['assumption_id']))
    print('Rebuilt floor-adjusted role wages; employer burden/staffing remain demo.')

if __name__=='__main__': derive()
