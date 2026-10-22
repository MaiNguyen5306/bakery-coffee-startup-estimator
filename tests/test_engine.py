from dataclasses import replace
import json
import pytest
from estimator.calculate import calculate, IncompleteEvidence
from estimator.schemas import Scenario
from estimator.normalize import monthly_rent, number
from estimator.scenarios import export_json, reproduce
from estimator.equipment import equipment


def test_hand_calculated_fixture():
    # A small independent ledger: 100 sqft, zero seats/owner/training/reserve,
    # standard espresso package; three service hours/week, $24 wage, 10% employer cost.
    s=Scenario(staff_count=0,extra_service_hours=3,sqft=100,seats=0,days=1,hours=1,owner_hours=0,
               preopening_months=1,deposit_months=2,training_hours=0,reserve_months=0,contingency=.1)
    r=calculate(s,{'rent':[12,12],'cam':[6,6],'buildout_existing':[20,20],
                   'wage_service':[24,24],'employer':[.1,.1],'freight':[0,0],'tax':[0,0],'annual_permit':[900,900],'food_review':[0,0]})
    # Core equipment low 10,100 + coffee 2,800 + espresso 8,600 = 21,500.
    # Fees 3,500 + permit 900 + insurance 2,400 + stock 1,500 + design 2,500 + launch 1,000.
    assert r['preopening']['low']==pytest.approx(300+150+2000+21500+3500+900+2400+1500+2500+1000)
    assert r['contingency']['low']==pytest.approx(.1*(2000+21500+1500+2500+1000))
    assert r['total']['low']==pytest.approx(38600)
    assert r['monthly']['low']==pytest.approx(150+3*52/12*24*1.1+550+650+150+1800+2400/12+900/12)

@pytest.mark.parametrize('q,u',[(36,'USD/sqft/year'),(3,'USD/sqft/month'),(3000,'USD/month')])
def test_rent_units(q,u): assert monthly_rent(q,u,1000)==3000

@pytest.mark.parametrize('v',['*','**','#','',None,-1,float('nan'),float('inf')])
def test_missing_and_suppression(v):
    with pytest.raises(ValueError): number(v)

def test_reject_units():
    with pytest.raises(ValueError): monthly_rent(1,'EUR/year',100)

@pytest.mark.parametrize('months',[0,1,3,11,12,24])
def test_one_more_reserve_month(months):
    a=calculate(Scenario(reserve_months=months)); b=calculate(Scenario(reserve_months=months+1))
    for e in ('low','high'):
        assert b['total'][e]-a['total'][e]==pytest.approx(b['cash_schedule'][-1][e])
    if months==0: assert a['reserve']=={'low':0,'high':0}

def test_annual_prepayments():
    r=calculate(Scenario(reserve_months=13))
    for e in ('low','high'):
        annual=r['assumptions']['insurance'][e]
        assert r['cash_schedule'][0][e]+r['assumptions']['annual_permit'][e]==pytest.approx(r['cash_schedule'][11][e])
        assert r['cash_schedule'][12][e]-r['cash_schedule'][0][e]==pytest.approx(annual)
        rent=1000*(r['assumptions']['rent'][e]+r['assumptions']['cam'][e])/12
        assert next(x[e] for x in r['lines'] if x['item']=='Operating occupancy')==rent

def test_paid_hours():
    a=calculate(Scenario()); b=calculate(Scenario(extra_service_hours=10))
    assert b['monthly']['low']>a['monthly']['low']
    assert calculate(Scenario(staff_count=0))['staffing']['coverage_gap']>0

def test_production_and_tier():
    a=calculate(Scenario()); b=calculate(Scenario(production='limited')); c=calculate(Scenario(tier='premium'))
    assert 'commercial_convection_oven' not in [r['item'] for r in a['lines']]
    assert 'commercial_convection_oven' in [r['item'] for r in b['lines']]
    for row in a['lines']:
        other=next(x for x in c['lines'] if x['item']==row['item'])
        if row['category']!='Equipment': assert row['low']==other['low']
    assert b['staffing']['baker']==20
    assert a['staffing']['baker']==0
    bakery=calculate(Scenario(business_type='bakery',production='onsite'))
    assert bakery['staffing']['baker']==60
    assert 'espresso_machine' in [x['item'] for x in bakery['lines']]

def test_reconcile_and_replay():
    for s in [Scenario(),Scenario(production='limited'),Scenario(business_type='bakery',production='onsite')]:
        r=calculate(s)
        for line in r['lines']: assert 0<=line['low']<=line['high']
        for e in ('low','high'):
            assert r['preopening'][e]==pytest.approx(sum(x[e] for x in r['lines'] if x['timing']=='opening'))
            assert r['total'][e]==pytest.approx(r['preopening'][e]+r['contingency'][e]+r['reserve'][e])
        assert reproduce(export_json(r))['total']==r['total']
        assert any(x['evidence_status']=='demo' for x in r['lines'])
        assert next(x for x in r['lines'] if x['category']=='Annual permit')['evidence_status']=='derived'

def test_fixed_only_excludes_only_replenishment():
    a=calculate(Scenario(reserve_months=1)); b=calculate(Scenario(reserve_months=1,reserve_basis='fixed_only'))
    assert a['reserve']['low']-b['reserve']['low']==pytest.approx(1800)
    assert a['preopening']==b['preopening']

@pytest.mark.parametrize('kwargs',[{'estimate_year':2027},{'city':'Portland'},{'sqft':0},{'production':'onsite'},{'reserve_months':1.5}])
def test_unsupported_inputs(kwargs):
    with pytest.raises(ValueError): calculate(Scenario(**kwargs))

def test_research_never_uses_demo():
    with pytest.raises(IncompleteEvidence): calculate(Scenario(),mode='research')
    with pytest.raises(ValueError): calculate(Scenario(),{'rent':[None,None]})
    with pytest.raises(ValueError): calculate(Scenario(),{'rent':[50,20]})


def test_space_size_maximum():
    calculate(Scenario(sqft=3000))
    with pytest.raises(ValueError,match="3,000 square feet"):
        calculate(Scenario(sqft=3001))
