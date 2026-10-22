"""Pure operating arithmetic. Sales are net of modeled discounts/refunds, excluding tax/tips."""
from dataclasses import dataclass, asdict
from math import ceil, isfinite, isclose
from hashlib import sha256
import json
from . import MODEL_VERSION, DATA_VERSION


def finite(value, name, positive=False):
    if isinstance(value, bool) or not isinstance(value, (int,float)) or not isfinite(value) or value < 0 or (positive and value == 0):
        raise ValueError(f"{name} must be a finite {'positive' if positive else 'nonnegative'} number")
    return value


def fingerprint(data):
    return sha256(json.dumps(data, sort_keys=True, allow_nan=False, separators=(",", ":")).encode()).hexdigest()


def basket_average(baskets):
    if not baskets: raise ValueError("At least one basket is required")
    if not isclose(sum(finite(b["share"],"Basket share") for b in baskets),1,abs_tol=1e-9): raise ValueError("Basket shares must sum to 1")
    aov=cost=0
    for b in baskets:
        if "items" in b:
            if not b["items"]: raise ValueError("Empty basket")
            sales=product=0
            for item in b["items"]:
                q=finite(item["quantity"],"Item quantity",True)
                sales+=q*finite(item["price"],"Item price")
                product+=q*finite(item["cost"],"Item cost")
        else:
            sales=finite(b["sales"],"Basket sales",True)
            product=finite(b["cost"],"Basket cost")
        aov+=b["share"]*sales;cost+=b["share"]*product
    return aov,cost


UNIT={"g":("mass",1),"kg":("mass",1000),"oz":("mass",28.349523125),"lb":("mass",453.59237),"ml":("volume",1),"l":("volume",1000),"each":("count",1)}
def recipe_cost(pack_price,pack_quantity,pack_unit,quantity,unit,yield_count=1,loss=0,packaging=0):
    for value,name in [(pack_price,"Pack price"),(quantity,"Recipe quantity"),(packaging,"Packaging")]: finite(value,name)
    finite(pack_quantity,"Pack quantity",True);finite(yield_count,"Sellable yield",True);finite(loss,"Input loss")
    if loss>=1: raise ValueError("Input loss must be below 1")
    if pack_unit not in UNIT or unit not in UNIT or UNIT[pack_unit][0]!=UNIT[unit][0]: raise ValueError("Incompatible ingredient units")
    # Loss is input shrinkage; yield must not already incorporate the same loss.
    base=pack_price*quantity*UNIT[unit][1]/(pack_quantity*UNIT[pack_unit][1])
    return base/(1-loss)/yield_count+packaging


def payment_per_order(aov,channels,fee_base_uplift=0):
    finite(fee_base_uplift,"Fee-base uplift")
    if not channels or not isclose(sum(finite(c["share"],"Channel share") for c in channels),1,abs_tol=1e-9): raise ValueError("Payment channel shares must sum to 1")
    fees=weighted_aov=0
    for c in channels:
        price=finite(c.get("aov",aov),"Channel AOV",True)
        p=finite(c["percentage"],"Fee percentage")
        if p>1: raise ValueError("Fee percentage must be a fraction")
        fees+=c["share"]*(price*(1+fee_base_uplift)*p+finite(c["fixed"],"Fixed transaction fee"))
        weighted_aov+=c["share"]*price
    if not isclose(weighted_aov,aov,rel_tol=1e-9): raise ValueError("Channel-weighted AOV must equal scenario AOV")
    return fees


def cost_adapter(cost):
    if not cost or not cost.get("lines"): return {"complete":False,"reason":"No linked cost result"}
    fixed={"low":0,"high":0};included=[];excluded=[];seen=set();uncertain=[]
    for line in cost["lines"]:
        key=line["line_id"]
        if key in seen: raise ValueError("Duplicate linked cost line ID")
        seen.add(key)
        if line["timing"] not in {"monthly","monthly_equivalent"}: continue
        if line["category"] in {"Replenishment","Owner draw"}:
            excluded.append({"line_id":key,"reason":"Replaced by product cost/order" if line["category"]=="Replenishment" else "Owner draw excluded from operating surplus"});continue
        if line["category"]=="Payroll": kind="stepped base payroll; constant only within assumed capacity"
        else: kind="fixed monthly allocation"
        included.append({"line_id":key,"classification":kind,"low":line["low"],"high":line["high"],"evidence_status":line["evidence_status"]})
        for e in fixed: fixed[e]+=finite(line[e],"Linked recurring cost")
        if line["evidence_status"] in {"demo","assumed"}: uncertain.append(key)
    gaps=cost.get("staffing",{}).get("coverage_gap",0)
    lead_gaps=cost.get("staffing",{}).get("leadership_gap",0)
    production_gaps=cost.get("staffing",{}).get("production_gap",0)
    return {"complete":bool(included) and not gaps and not lead_gaps and not production_gaps,"reason":f"{production_gaps:g} unfunded production hours/week" if production_gaps else f"{gaps:g} unfunded service hours/week" if gaps else f"{lead_gaps:g} staff-led hours lack owner/supervisor coverage" if lead_gaps else "Recurring cost scope included; amounts still subject to evidence gaps", "fixed":fixed,"included":included,"excluded":excluded,"uncertain_line_ids":uncertain,"evidence_status":"demo" if uncertain else "derived","fingerprint":fingerprint(cost),"scope":"Excludes startup, reserve, owner draws, debt service, income tax and depreciation. Replenishment is replaced by explicit product cost; processing added once in Revenue. Services allowance must exclude additional POS subscriptions to avoid overlap."}


@dataclass(frozen=True)
class RevenueScenario:
    mode: str="target"
    target_sales: float=30000
    daily_orders: float=115
    aov: float=10
    open_days: int=26
    open_hours: float=8
    product_cost: float=3.5
    sales_cost_fraction: float=0
    target_surplus: float=0
    fee_base_uplift: float=0
    peak_share: float=.5
    peak_hours: float=2
    capacity_per_hour: float=40
    cost_basis: str="linked"
    fixed_cost: float=12000
    variable_cost_complete: bool=False


def calculate_revenue(s,channels=None,baskets=None,cost=None,linked_fingerprint=None):
    if isinstance(s,dict): s=RevenueScenario(**s)
    values=asdict(s)
    if s.mode not in {"target","expected"} or s.cost_basis not in {"linked","manual"}: raise ValueError("Invalid revenue mode or cost basis")
    for key in ("target_sales","daily_orders","product_cost","sales_cost_fraction","target_surplus","fee_base_uplift","peak_share","fixed_cost"): finite(values[key],key)
    for key in ("aov","open_days","open_hours","peak_hours","capacity_per_hour"): finite(values[key],key,True)
    if s.open_days>31 or int(s.open_days)!=s.open_days or s.open_hours>24: raise ValueError("Use exact open days (1–31) and hours (0–24]")
    if s.peak_share>1 or s.sales_cost_fraction>1 or s.peak_hours>s.open_hours: raise ValueError("Invalid peak share/hours or sales-cost fraction")
    if s.peak_hours==s.open_hours and s.peak_share!=1: raise ValueError("All-day peak period must include all daily orders")
    if not isinstance(s.variable_cost_complete,bool): raise ValueError("Variable completeness must be a boolean")
    aov,product=(basket_average(baskets) if baskets else (s.aov,s.product_cost))
    finite(aov,"Weighted AOV",True)
    channels=channels if channels is not None else [{"share":1,"percentage":0,"fixed":0,"evidence_status":"assumed","channel":"cash or user-entered zero-fee channel"}]
    fee=payment_per_order(aov,channels,s.fee_base_uplift)
    n=s.target_sales/aov if s.mode=="target" else s.daily_orders*s.open_days
    sales=n*aov;daily=n/s.open_days;hourly=daily/s.open_hours
    contribution=aov*(1-s.sales_cost_fraction)-product-fee
    adapter=cost_adapter(cost) if s.cost_basis=="linked" else {"complete":True,"fixed":{"low":s.fixed_cost,"high":s.fixed_cost},"evidence_status":"assumed","scope":"User-entered fixed operating costs; completeness is user's responsibility","uncertain_line_ids":[]}
    if s.cost_basis=="linked" and cost:
        schedule=cost["scenario"]
        if s.open_hours>schedule["hours"] or s.open_days>ceil(schedule["days"]*52/12):
            adapter["complete"]=False
            adapter["reason"]="Revenue schedule exceeds linked staffing schedule; revise Cost staffing before relying on break-even"
    stale=s.cost_basis=="linked" and linked_fingerprint is not None and adapter.get("fingerprint")!=linked_fingerprint
    complete=adapter.get("complete",False) and s.variable_cost_complete and not stale
    status="stale" if stale else "incomplete" if not complete else "no_finite_break_even" if contribution<=0 else "illustrative"
    be={}
    if complete and contribution>0:
        for e,f in adapter["fixed"].items():
            be[e]={"orders_month":f/contribution,"sales_month":f/contribution*aov,"orders_day":f/contribution/s.open_days,"target_surplus_orders":(f+s.target_surplus)/contribution,"operating_surplus":sales-n*(product+fee)-sales*s.sales_cost_fraction-f}
    peak=daily*s.peak_share/s.peak_hours
    nonpeak=daily*(1-s.peak_share)/(s.open_hours-s.peak_hours) if s.open_hours>s.peak_hours else None
    return {"model_version":MODEL_VERSION,"data_version":DATA_VERSION,"evidence_status":"demo" if adapter.get("evidence_status")=="demo" else "assumed","label":"ILLUSTRATIVE SCENARIO — no demand forecast; linked break-even inherits demo/user cost uncertainty","scenario":values,"aov":aov,"product_cost_order":product,"channels":channels,"baskets":baskets,"linked_cost":cost,"linked_fingerprint":adapter.get("fingerprint"),"adapter":adapter,"status":status,"orders_month":n,"whole_month_goal":ceil(n),"constant_daily_goal":ceil(daily),"orders_day":daily,"orders_hour":hourly,"sales_month":sales,"payment_fees_month":fee*n,"fee_order":fee,"contribution_order":contribution,"break_even":be,"capacity":{"peak_rate":peak,"nonpeak_rate":nonpeak,"target_surplus_exceeds_capacity":any(b["target_surplus_orders"]/s.open_days/s.open_hours>s.capacity_per_hour or b["target_surplus_orders"]/s.open_days*s.peak_share/s.peak_hours>s.capacity_per_hour or (s.open_hours>s.peak_hours and b["target_surplus_orders"]/s.open_days*(1-s.peak_share)/(s.open_hours-s.peak_hours)>s.capacity_per_hour) for b in be.values()),"capacity_per_hour":s.capacity_per_hour,"exceeds_capacity":max(hourly,peak,nonpeak or 0)>s.capacity_per_hour,"break_even_exceeds_capacity":any(max(b["orders_day"]*s.peak_share/s.peak_hours,b["orders_day"]*(1-s.peak_share)/(s.open_hours-s.peak_hours) if s.open_hours>s.peak_hours else 0)>s.capacity_per_hour for b in be.values())},"sensitivity":[{"aov":aov*f,"daily_orders":daily*g,"sales":aov*f*daily*g*s.open_days} for f in (.9,1,1.1) for g in (.8,1,1.2)],"warnings":["Orders are transactions, not unique customers. Daily orders are constant across selected open days.","Sales exclude sales tax/tips and are net of discounts/refunds; payment uplift may include collected tax/tips.","Channel shares are transaction shares; equal AOV assumed unless explicitly provided per channel.","Capacity is a user assumption, not measured demand. Reassess stepped staffing/equipment beyond capacity.","Product cost must include ingredients/purchased pastry, explicit waste and packaging exactly once.","No startup reserve reduction or financing cash offset is made."],"formulas":{"sales":"daily_orders * open_days * AOV","required_orders":"target_sales / AOV","contribution":"AOV * (1 - sales_cost_fraction) - product_cost_order - payment_fee_order","break_even":"fixed_operating_cost / contribution_order","surplus":"sales - variable_costs - fixed_operating_cost"}}


def replay_revenue(data):
    if data["model_version"]!=MODEL_VERSION or data["data_version"]!=DATA_VERSION: raise ValueError("Revenue version mismatch")
    if data.get("linked_cost"):
        from .scenarios import reproduce
        reproduce(json.dumps(data["linked_cost"]))
    result=calculate_revenue(data["scenario"],data["channels"],data.get("baskets"),data.get("linked_cost"),data.get("linked_fingerprint"))
    for key in ("sales_month","orders_month","break_even"):
        if result[key]!=data[key]: raise ValueError("Revenue export does not reproduce")
    return result


def validate_revenue_tables(folder):
    from .loaders import rows, ROOT
    from datetime import date
    tables={name:rows(folder/f'{name}.csv') for name in ('sources','menu_prices','supplier_prices','recipes','payment_fees','order_baskets','revenue_assumptions')}
    ids={}
    for name,records in tables.items():
        import csv
        with (folder/f'{name}.csv').open() as f: actual=next(csv.reader(f))
        expected=(ROOT/f'data/templates/revenue/{name}.csv').read_text().strip().split(',')
        if actual!=expected: raise ValueError(f'Invalid {name} schema')
        key=expected[0];ids[name]=set()
        for r in records:
            if not r[key] or r[key] in ids[name]: raise ValueError(f'Duplicate/empty {name} ID')
            ids[name].add(r[key])
            for k,v in r.items():
                if v and k in {'snapshot_date','accessed_date','observed_date','effective_start','effective_end'}: date.fromisoformat(v)
            if r.get('effective_start') and r.get('effective_end') and r['effective_start']>r['effective_end']: raise ValueError('Reversed effective dates')
            if 'evidence_status' in r and r['evidence_status'] not in {'observed','derived','assumed','demo'}: raise ValueError('Invalid evidence status')
            if r.get('currency','USD')!='USD': raise ValueError('Unsupported currency')
    for name in ('menu_prices','supplier_prices','payment_fees'):
        for r in tables[name]:
            if r['source_id'] not in ids['sources']: raise ValueError('Unresolved revenue source')
    for r in tables['menu_prices']:
        finite(float(r['price']),'Menu price')
        if r['unit']!='USD/item' or not r['channel'] or not r['tax_basis']: raise ValueError('Missing menu unit/channel/tax basis')
    for r in tables['payment_fees']:
        p=finite(float(r['percentage']),'Fee percentage')
        if p>1: raise ValueError('Invalid fee fraction')
        finite(float(r['fixed_per_transaction']),'Fixed fee');finite(float(r['monthly_subscription']),'Subscription')
        if r['market']!='US' or r['channel'] not in {'in_person','online','cash'}: raise ValueError('Unsupported processor market/channel')
    for r in tables['supplier_prices']:
        if r['pack_unit'] not in UNIT: raise ValueError('Invalid pack unit')
        finite(float(r['pack_quantity']),'Pack quantity',True);finite(float(r['pack_price']),'Pack price')
    for r in tables['recipes']:
        if r['supplier_price_id'] not in ids['supplier_prices']: raise ValueError('Unresolved recipe supplier')
        supplier=next(x for x in tables['supplier_prices'] if x['supplier_price_id']==r['supplier_price_id'])
        recipe_cost(float(supplier['pack_price']),float(supplier['pack_quantity']),supplier['pack_unit'],float(r['ingredient_quantity']),r['ingredient_unit'],float(r['sellable_yield']),float(r['input_loss_fraction']),float(r['packaging_cost_per_yield']))
    groups={}
    for r in tables['order_baskets']:
        refs=list(filter(None,r['menu_price_ids'].split(';')))
        quantities=list(filter(None,r['quantities'].split(';')))
        if set(refs)-ids['menu_prices']: raise ValueError('Unresolved basket menu price')
        if refs and len(refs)!=len(quantities): raise ValueError('Basket quantities do not match items')
        for q in quantities: finite(float(q),'Basket quantity',True)
        groups.setdefault(r['scenario_id'],[]).append({'share':float(r['share']),'sales':float(r['basket_sales_value']),'cost':float(r['basket_product_cost'])})
    for group in groups.values(): basket_average(group)
    known=set().union(*ids.values())
    for r in tables['revenue_assumptions']:
        if set(filter(None,r['evidence_ids'].split(';')))-known: raise ValueError('Unresolved assumption evidence')
        finite(float(r['value']),'Revenue assumption')
    return {k:len(v) for k,v in tables.items()}
