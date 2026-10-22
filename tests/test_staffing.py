from dataclasses import replace
import pytest
from estimator.schemas import Scenario
from estimator.staffing import staffing
from estimator.calculate import calculate
from estimator.loaders import assumptions
from estimator.scenarios import reproduce, export_json
from estimator.revenue import cost_adapter


def test_presets_owner_and_team_hours():
    owner=staffing(Scenario())
    assert owner['owner_coverage']==40 and owner['service']==80
    assert owner['supervisor']==0 and owner['coverage_gap']==0
    staff=staffing(Scenario(staffing='staffed',staff_count=3))
    assert staff['owner_coverage']==0
    assert staff['service']==staff['supervisor']==60
    assert staff['paid_service_total']==staff['total_paid_hours']==120
    assert staff['coverage_gap']==staff['leadership_gap']==0
    assert staff['minimum_total_headcount']==3
    assert staff['minimum_supervisor_headcount']==2


def test_owner_contribution_and_supervisor_no_double_count():
    a=staffing(Scenario(staffing='staffed',owner_hours=40))
    assert a['service']==60 and a['supervisor']==20
    assert a['total_paid_hours']==80
    assert a['owner_coverage']+a['paid_service_total']==a['required_service']
    b=staffing(Scenario(staffing='staffed',staff_count=3,owner_hours=0,supervisor_hours=30))
    assert b['service']==90 and b['supervisor']==30 and b['total_paid_hours']==120
    assert b['coverage_gap']==0 and b['leadership_gap']==30
    assert not cost_adapter(calculate(Scenario(staffing='staffed',staff_count=3,owner_hours=0,supervisor_hours=30)))['complete']


def test_owner_cap_and_production_separate():
    s=Scenario(staffing='staffed',owner_hours=80,production='limited')
    h=staffing(s)
    assert h['owner_requested']==80 and h['owner_coverage']==60
    assert h['baker']==20 and h['service']==60 and h['supervisor']==0
    assert h['total_paid_hours']==80


def test_supervisor_wages_payroll_and_export():
    a=assumptions()['wage_supervisor']
    assert (a['low'],a['high'])==(29.62,36.57)
    assert a['evidence_status']=='derived' and '35-1012' in a['evidence_ids']
    r=calculate(Scenario(staffing='staffed'))
    for e in ('low','high'):
        p=r['payroll_by_role']['supervisor']
        assert p['monthly_base_pay'][e]==pytest.approx(60*52/12*a[e])
        payroll=next(l[e] for l in r['lines'] if l['category']=='Payroll')
        assert payroll==pytest.approx(sum(p['monthly_total'][e] for p in r['payroll_by_role'].values()))
    no_lead=calculate(Scenario(staffing='staffed',supervisor_hours=0))
    assert r['monthly']['low']>no_lead['monthly']['low']
    assert reproduce(export_json(r))['total']==r['total']
    with pytest.raises(ValueError,match='wage floor'):
        calculate(Scenario(),{'wage_supervisor':[20,30]})


@pytest.mark.parametrize('value',[-1,True,'forty',float('nan')])
def test_invalid_supervisor_hours(value):
    with pytest.raises(ValueError): calculate(Scenario(supervisor_hours=value))


@pytest.mark.parametrize('count,kind,hours',[(0,'part_time',0),(1,'part_time',20),(3,'part_time',60),(2,'full_time',80),(3,'full_time',120)])
def test_employee_contract_hours(count,kind,hours):
    h=staffing(Scenario(staff_count=count,employment_type=kind))
    assert h['total_paid_hours']==h['contracted_employee_hours']==hours
    assert h['service']+h['supervisor']+h['baker']==hours
    assert staffing(Scenario(staff_count=count,employment_type=kind,owner_hours=0))['total_paid_hours']==hours
    assert staffing(Scenario(staff_count=count,employment_type=kind,owner_hours=40))['total_paid_hours']==hours


def test_all_roles_within_selected_team_and_missing_production():
    s=Scenario(staff_count=1,employment_type='part_time',business_type='bakery',production='onsite',staffing='staffed')
    r=calculate(s);h=r['staffing']
    assert h['total_paid_hours']==20 and h['baker']==20
    assert h['production_gap']==40 and h['supervisor']==h['service']==0
    assert not cost_adapter(r)['complete']
    assert 'production' in cost_adapter(r)['reason']
    h=staffing(replace(s,staff_count=4,employment_type='full_time'))
    assert h['total_paid_hours']==160
    assert h['baker']==60 and h['supervisor']==60 and h['service']==40


@pytest.mark.parametrize('kw',[{'staff_count':-1},{'staff_count':1.5},{'staff_count':True},{'staff_count':101},{'employment_type':'casual'}])
def test_invalid_employee_contracts(kw):
    with pytest.raises(ValueError):calculate(Scenario(**kw))


def test_additional_service_hours_explicit_and_payroll_monotonic():
    a=calculate(Scenario(staff_count=2,employment_type='part_time'))
    b=calculate(Scenario(staff_count=2,employment_type='full_time'))
    assert a['staffing']['total_paid_hours']==40
    assert b['staffing']['total_paid_hours']==80
    assert b['monthly']['low']>a['monthly']['low']
    h=staffing(Scenario(staff_count=2,extra_service_hours=5))
    assert h['total_paid_hours']==85 and h['additional_service_hours']==5
    assert reproduce(export_json(b))['total']==b['total']
