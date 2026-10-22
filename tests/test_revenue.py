from dataclasses import replace
from datetime import date
import copy
import pytest
from estimator.revenue import RevenueScenario, calculate_revenue, basket_average, payment_per_order, recipe_cost, cost_adapter, replay_revenue, validate_revenue_tables
from estimator.calculate import calculate
from estimator.schemas import Scenario
from estimator.permits import permit_timing
from estimator.loaders import ROOT,assumptions


def fixture(**kw):
    return calculate_revenue(RevenueScenario(**{'cost_basis':'manual','fixed_cost':12000,'product_cost':4,'variable_cost_complete':True,**kw}))


def test_hand_fixture():
    r=fixture()
    assert r['orders_month']==3000
    assert r['orders_day']==pytest.approx(115.384615384615)
    assert r['orders_hour']==pytest.approx(14.423076923077)
    assert r['constant_daily_goal']==116
    assert r['whole_month_goal']==3000
    assert r['contribution_order']==6
    assert r['break_even']['low']['orders_month']==2000
    assert r['break_even']['low']['sales_month']==20000
    assert r['break_even']['low']['operating_surplus']==6000
    assert replay_revenue(r)['break_even']==r['break_even']


def test_zero_target_and_expected_orders():
    r=fixture(target_sales=0)
    assert r['orders_month']==r['orders_day']==r['orders_hour']==r['whole_month_goal']==0
    assert fixture(mode='expected',daily_orders=100)['sales_month']==26000
    assert fixture(mode='expected',daily_orders=200)['sales_month']==52000
    assert fixture(open_days=13)['orders_day']==pytest.approx(fixture()['orders_day']*2)
    assert fixture(aov=20)['orders_month']==1500


@pytest.mark.parametrize('kw',[{'aov':0},{'aov':-1},{'open_days':0},{'open_days':32},{'open_days':1.5},{'open_hours':0},{'peak_share':1.1},{'peak_hours':9},{'peak_hours':8},{'product_cost':float('nan')}])
def test_boundaries(kw):
    with pytest.raises(ValueError): fixture(**kw)


def test_mix():
    b=[{'share':.4,'items':[{'quantity':1,'price':5,'cost':1}]},{'share':.6,'items':[{'quantity':1,'price':5,'cost':1},{'quantity':2,'price':4,'cost':2}]}]
    assert basket_average(b)==pytest.approx((9.8,3.4))
    b[0]['share']=.5
    with pytest.raises(ValueError): basket_average(b)
    with pytest.raises(ValueError): basket_average([{'share':1,'items':[{'quantity':-1,'price':5,'cost':1}]}])


def test_channel_fees_and_uplift():
    channels=[{'share':.8,'percentage':.026,'fixed':.15},{'share':.2,'percentage':0,'fixed':0}]
    assert payment_per_order(10,channels)==pytest.approx(.328)
    assert payment_per_order(10,channels,.1)==pytest.approx(.3488)
    unequal=[{'share':.5,'aov':5,'percentage':.02,'fixed':.1},{'share':.5,'aov':15,'percentage':.03,'fixed':.2}]
    assert payment_per_order(10,unequal)==pytest.approx(.425)
    with pytest.raises(ValueError): payment_per_order(12,unequal)
    with pytest.raises(ValueError): payment_per_order(10,[{'share':.5,'percentage':0,'fixed':0}])


def test_recipe_conversion_waste_and_packaging():
    assert recipe_cost(10,1,'kg',100,'g',2,0,.2)==pytest.approx(.7)
    assert recipe_cost(10,1,'kg',100,'g',2,.1,.2)==pytest.approx(1/.9/2+.2)
    assert recipe_cost(4,1,'lb',16,'oz')==pytest.approx(4)
    with pytest.raises(ValueError): recipe_cost(10,1,'kg',100,'ml')
    with pytest.raises(ValueError): recipe_cost(10,1,'kg',100,'g',loss=1)


def test_no_finite_and_missing_evidence():
    r=fixture(product_cost=11) if False else calculate_revenue(RevenueScenario(cost_basis='manual',product_cost=11,variable_cost_complete=True))
    assert r['status']=='no_finite_break_even' and r['break_even']=={}
    r=calculate_revenue(RevenueScenario())
    assert r['status']=='incomplete' and not r['break_even'] and r['sales_month']==30000
    r=calculate_revenue(RevenueScenario(cost_basis='manual'))
    assert r['status']=='incomplete'


def test_adapter_dedup_and_classification():
    cost=calculate(Scenario(staffing='staffed',staff_count=3,owner_monthly_draw=2000))
    a=cost_adapter(cost)
    assert a['complete']
    assert a['evidence_status']=='demo'
    excluded={r['line_id'] for r in a['excluded']}
    assert any('replenishment' in key for key in excluded)
    assert any('owner' in key for key in excluded)
    for e in ('low','high'):
        assert a['fixed'][e]==pytest.approx(cost['monthly'][e]-next(l[e] for l in cost['lines'] if l['category']=='Replenishment')-2000)
    cost['lines'].append(cost['lines'][0])
    with pytest.raises(ValueError): cost_adapter(cost)


def test_linked_stale_and_independent_startup():
    a=calculate(Scenario(staffing='staffed',reserve_months=0));b=calculate(Scenario(staffing='staffed',reserve_months=6,sqft=1000))
    s=RevenueScenario(variable_cost_complete=True)
    ra=calculate_revenue(s,cost=a);rb=calculate_revenue(s,cost=b)
    assert ra['break_even']==rb['break_even']
    stale=calculate_revenue(s,cost=b,linked_fingerprint=ra['linked_fingerprint'])
    assert stale['status']=='stale' and stale['break_even']=={}
    assert replay_revenue(ra)['break_even']==ra['break_even']
    ra['sales_month']=1
    with pytest.raises(ValueError): replay_revenue(ra)


def test_capacity_nonpeak_and_target_surplus():
    r=fixture(capacity_per_hour=10,target_surplus=6000)
    assert r['capacity']['exceeds_capacity']
    assert r['capacity']['peak_rate']==pytest.approx(r['orders_day']*.5/2)
    assert r['capacity']['nonpeak_rate']==pytest.approx(r['orders_day']*.5/6)
    assert r['break_even']['low']['target_surplus_orders']==3000


@pytest.mark.parametrize('opening,fraction,renewal',[('2026-01-01',.25,3),('2026-03-31',.25,13),('2026-04-01',1,12),('2026-06-30',1,10),('2026-07-01',.75,9),('2026-10-01',.5,6),('2026-12-31',.5,4)])
def test_permit_calendar_boundaries(opening,fraction,renewal):
    p=permit_timing(opening,[756,1008],13)
    assert p['opening']==[756*(fraction+int(p['opening_renewal'])),1008*(fraction+int(p['opening_renewal']))]
    assert p['renewals'][0]==renewal
    assert 1 not in p['renewals']
    r=calculate(Scenario(opening_date=opening,reserve_months=13))
    assert r['cash_schedule'][renewal-1]['permit_renewal']
    assert next(l['low'] for l in r['lines'] if l['category']=='Annual permit' and l['timing']=='opening')==756*(fraction+int(p['opening_renewal']))


def test_wage_derivation_and_permit_selection():
    a=assumptions()
    assert (a['wage_service']['low'],a['wage_service']['high'])==(21.3,21.75)
    assert (a['wage_baker']['low'],a['wage_baker']['high'])==(23.16,25.8)
    r=calculate(Scenario(business_type='bakery',production='onsite',seats=0,permit_risk=3))
    assert r['assumptions']['annual_permit']['low']==945
    assert r['permit_selection']['category']=='bakery_no_seating'
    assert calculate(Scenario(condition='shell'))['assumptions']['food_review']['low']==1008
    assert calculate(Scenario(plan_review_extra_hours=2))['assumptions']['food_review']['low']==1260


def test_revenue_tables_not_empty_schema_as_evidence():
    counts=validate_revenue_tables(ROOT/'data/processed/revenue')
    assert counts['menu_prices']==8 and counts['payment_fees']==6
    assert counts['supplier_prices']==counts['recipes']==0


def test_schedule_expansion_and_risk_applicability():
    cost=calculate(Scenario(staffing='staffed'))
    r=calculate_revenue(RevenueScenario(open_hours=12,variable_cost_complete=True),cost=cost)
    assert r['status']=='incomplete' and 'schedule' in r['adapter']['reason']
    with pytest.raises(ValueError): calculate(Scenario(production='limited',permit_risk=1))


@pytest.mark.parametrize('issue',['duplicate','bad_source','bad_unit','bad_date'])
def test_revenue_evidence_validation(tmp_path,issue):
    import csv,shutil
    for p in (ROOT/'data/processed/revenue').glob('*.csv'): shutil.copy(p,tmp_path/p.name)
    path=tmp_path/'menu_prices.csv'
    with path.open() as f:
        reader=csv.DictReader(f);fields=reader.fieldnames;records=list(reader)
    if issue=='duplicate': records.append(records[0])
    if issue=='bad_source': records[0]['source_id']='missing'
    if issue=='bad_unit': records[0]['unit']='EUR/item'
    if issue=='bad_date': records[0]['observed_date']='not-a-date'
    with path.open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(records)
    with pytest.raises(ValueError): validate_revenue_tables(tmp_path)
