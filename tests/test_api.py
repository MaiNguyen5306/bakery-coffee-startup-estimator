import importlib.util
import io
import json
from pathlib import Path
from email.message import Message
import pytest

spec = importlib.util.spec_from_file_location('estimate_api', Path(__file__).resolve().parents[1]/'api/estimate.py')
api = importlib.util.module_from_spec(spec)
spec.loader.exec_module(api)


def invoke(payload, raw=None, length=None):
    body=json.dumps(payload).encode() if raw is None else raw
    h=api.handler.__new__(api.handler)
    h.headers=Message()
    h.headers['Content-Length']=str(len(body) if length is None else length)
    h.rfile=io.BytesIO(body)
    replies=[]
    h.reply=lambda status,data: replies.append((status,data))
    h.do_POST()
    return replies[0]


def test_default_and_bakery_api():
    status,r=invoke({'scenario':{}})
    assert status==200 and r['total']['low']==pytest.approx(179180.3435)
    status,b=invoke({'scenario':{'business_type':'bakery','production':'onsite'}})
    assert status==200 and b['staffing']['baker']==60
    assert any(x['item']=='espresso_machine' for x in b['lines'])


def test_research_blocks_and_annual_schedule():
    assert invoke({'mode':'research'})[0]==400
    _,r=invoke({'scenario':{'reserve_months':13}})
    assert r['cash_schedule'][12]['annual_renewal']
    assert r['cash_schedule'][11]['permit_renewal']
    assert not r['cash_schedule'][11]['insurance_renewal']


@pytest.mark.parametrize('payload',[[],{'scenario':[]},{'scenario':{'days':'six'}},{'scenario':{'reserve_months':-1}},{'overrides':{'wage_service':[20,25]}}])
def test_bad_inputs_are_client_errors(payload):
    assert invoke(payload)[0]==400


def test_invalid_body_and_size():
    assert invoke({},raw=b'{oops')[0]==400
    assert invoke({},raw=b'{"scenario":{"sqft":NaN}}')[0]==400
    assert invoke({},length=600000)[0]==413


def test_export_replay():
    _,result=invoke({})
    status,replayed=invoke({'action':'reproduce','export':result})
    assert status==200 and replayed['total']==result['total']
    result['configuration_fingerprint']='wrong'
    assert invoke({'action':'reproduce','export':result})[0]==400


def test_get_bootstrap_includes_assumptions_sources_and_docs():
    h=api.handler.__new__(api.handler)
    replies=[]
    h.reply=lambda status,data: replies.append((status,data))
    h.do_GET()
    status,data=replies[0]
    assert status==200 and len(data['assumptions'])==22
    assert data['scenario']['city']=='Seattle'
    assert data['sources'] and data['methodology'] and data['limitations']


def test_revenue_endpoint_and_export_replay():
    status,r=invoke({'action':'revenue','revenue':{'cost_basis':'manual','product_cost':4,'fixed_cost':12000,'variable_cost_complete':True}})
    assert status==200 and r['break_even']['low']['sales_month']==20000
    assert invoke({'action':'revenue_reproduce','export':r})[0]==200
    status,r=invoke({'action':'revenue','revenue':{'variable_cost_complete':True},'cost_inputs':{'scenario':{'staffing':'staffed','staff_count':3}}})
    assert status==200 and r['status']=='illustrative' and r['evidence_status']=='demo'
    assert r['adapter']['uncertain_line_ids']
    assert invoke({'action':'revenue_reproduce','export':r})[0]==200
    assert invoke({'action':'revenue','revenue':{'aov':0}})[0]==400


@pytest.mark.parametrize('espresso',[True,False])
@pytest.mark.parametrize('business,production',[('coffee','purchased'),('bakery','onsite')])
def test_open_sessions_with_removed_espresso_field(espresso,business,production):
    scenario={'business_type':business,'production':production,'espresso':espresso}
    status,cost=invoke({'scenario':scenario})
    assert status==200
    assert any(row['item']=='espresso_machine' for row in cost['lines'])
    assert 'espresso' not in cost['scenario']
    clean={k:v for k,v in scenario.items() if k!='espresso'}
    assert cost['total']==invoke({'scenario':clean})[1]['total']
    status,revenue=invoke({'action':'revenue','cost_inputs':{'scenario':scenario}})
    assert status==200 and revenue['sales_month']==30000
    assert revenue['linked_cost']['total']==cost['total']


def test_live_compatibility_does_not_ignore_other_unknown_inputs():
    assert invoke({'scenario':{'unknown_setting':True}})[0]==400
