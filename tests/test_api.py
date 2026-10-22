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
    assert status==200 and r['total']['low']==pytest.approx(170395.4475)
    status,b=invoke({'scenario':{'business_type':'bakery','production':'onsite','espresso':False}})
    assert status==200 and b['staffing']['baker']==60
    assert all(x['item']!='espresso_machine' for x in b['lines'])


def test_research_blocks_and_annual_schedule():
    assert invoke({'mode':'research'})[0]==400
    _,r=invoke({'scenario':{'reserve_months':13}})
    assert r['cash_schedule'][12]['annual_renewal']
    assert not r['cash_schedule'][11]['annual_renewal']


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
    assert status==200 and len(data['assumptions'])==20
    assert data['scenario']['city']=='Seattle'
    assert data['sources'] and data['methodology'] and data['limitations']
