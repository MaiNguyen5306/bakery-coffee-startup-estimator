import csv
import shutil
from pathlib import Path
import pytest
from estimator.loaders import ROOT
from estimator.validation import validate_tables
from estimator.calculate import calculate
from estimator.schemas import Scenario

def setup_tables(tmp_path):
    for p in (ROOT/'data/templates').glob('*.csv'): shutil.copy(p,tmp_path/p.name)
    return tmp_path

def put(folder,name,records):
    fields=(ROOT/'data/templates'/f'{name}.csv').read_text().strip().split(',')
    with (folder/f'{name}.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader();w.writerows(records)

@pytest.mark.parametrize('case',['duplicate_id','bad_reference','negative','reversed','missing_evidence','bad_unit','duplicate_listing'])
def test_invalid_data(tmp_path,case):
    folder=setup_tables(tmp_path)
    source={'source_id':'s','status':'verified'}
    put(folder,'sources',[source,source] if case=='duplicate_id' else [source])
    if case=='bad_reference':put(folder,'observations',[dict(observation_id='o',source_id='missing',currency='USD')])
    if case in {'negative','reversed','missing_evidence'}:
        put(folder,'assumptions',[dict(assumption_id='a',low=-1 if case=='negative' else 2,high=1 if case=='reversed' else 3,unit='USD',evidence_status='derived' if case=='missing_evidence' else 'assumed',confidence='low')])
    if case in {'bad_unit','duplicate_listing'}:
        row=dict(listing_id='l',source_id='s',address_or_identifier='123 Main',sqft=1000,base_rent_quote=30,quote_unit='EUR/year' if case=='bad_unit' else 'USD/sqft/year',lease_type='NNN')
        put(folder,'rent_listings',[row,{**row,'listing_id':'l2'}] if case=='duplicate_listing' else [row])
    with pytest.raises(ValueError):validate_tables(folder)

def test_real_tables(): assert validate_tables(ROOT/'data/processed')['observations']>=1

def test_wage_floor_applies_to_overrides():
    with pytest.raises(ValueError,match='wage floor'):calculate(Scenario(),{'wage_service':[20,25]})
    assert calculate(Scenario())['wage_floor']==21.3
