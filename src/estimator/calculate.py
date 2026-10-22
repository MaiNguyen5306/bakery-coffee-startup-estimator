from dataclasses import asdict
from copy import deepcopy
from . import MODEL_VERSION, DATA_VERSION
from .loaders import assumptions, config, configuration_fingerprint
from .schemas import Scenario
from .equipment import equipment
from .staffing import staffing

class IncompleteEvidence(ValueError): pass

def calculate(s: Scenario, overrides=None, mode="demo"):
    s.validate()
    if mode not in {"demo", "research"}: raise ValueError("Unknown mode")
    if mode == "research": raise IncompleteEvidence("Research-ready totals blocked: rent/CAM, buildout, taxes, employer costs, permits and equipment evidence are not yet validated. Demo values cannot satisfy research requirements.")
    a = deepcopy(assumptions())
    for key, pair in (overrides or {}).items():
        if key not in a or len(pair) != 2: raise ValueError("Unknown override")
        from .normalize import number
        lo, hi = map(number, pair)
        if lo > hi: raise ValueError("Reversed override")
        a[key].update(low=lo, high=hi, notes="User override; unverified", evidence_status="assumed")
    floor = config("model_settings.json")["wage_floor"][s.city][str(s.estimate_year)]
    for key in ("wage_service", "wage_baker"):
        if a[key]["low"] < floor: raise ValueError(f"{key} below Seattle {s.estimate_year} wage floor of ${floor:.2f}")
    lines = []
    def add(item, category, timing, low, high, basis, ids, eligible=False, refundable=False):
        lines.append(dict(item=item, category=category, timing=timing, low=low, high=high, calculation_basis=basis, assumption_ids=ids, contingency_eligible=eligible, refundable=refundable, evidence_status="demo"))
    def pair(key): return [a[key][e] for e in ("low", "high")]
    rent = [s.sqft*(a["rent"][e]+a["cam"][e])/12 for e in ("low", "high")]
    hours = staffing(s)
    payroll = [sum(hours[r]*52/12*a["wage_"+r][e] for r in ("service", "baker"))*(1+a["employer"][e]) for e in ("low", "high")]
    add("Refundable lease deposit", "Deposits", "opening", *[x*s.deposit_months for x in rent], "Monthly base + CAM × deposit months; refundable per assumed lease", "rent;cam", refundable=True)
    add("Preopening occupancy", "Occupancy", "opening", *[x*s.preopening_months for x in rent], "Preopening months only; operation month 1 is paid in reserve", "rent;cam")
    key = "buildout_"+s.condition
    add("Buildout", "Buildout", "opening", *[x*s.sqft for x in pair(key)], "sqft × rate; includes trades and contractor installation; excludes design and equipment hookups", key, True)
    for row in equipment(s):
        add(row["item"], "Equipment", "opening", row["low"], row["high"], row["basis"], row["evidence_id"], True)
    subtotal = [sum(r[e] for r in lines if r["category"] == "Equipment") for e in ("low", "high")]
    add("Equipment freight and hookups", "Equipment", "opening", *[subtotal[i]*pair("freight")[i] for i in (0,1)], "Equipment subtotal × freight/hookup allowance; outside building trades", "freight", True)
    # Demo tax basis includes freight/hookups, explicitly editable pending tax applicability research.
    add("Equipment tax allowance", "Equipment", "opening", *[subtotal[i]*(1+pair("freight")[i])*pair("tax")[i] for i in (0,1)], "Equipment plus freight/hookups × assumed tax; applicability unverified", "tax", True)
    for key, cat in [("fees","Opening fees"),("annual_permit","Annual permit"),("insurance","Insurance"),("inventory","Opening stock"),("professional","Professional services"),("launch","Launch")]:
        add(a[key]["item"], cat, "opening", *pair(key), "One payment at opening; annual items cover operating months 1–12", key, key in {"inventory","professional","launch"})
    add("Paid training", "Training", "opening", *[s.training_hours*a["wage_service"][e]*(1+a["employer"][e]) for e in ("low","high")], "Total team training hours × service wage × employer factor", "wage_service;employer", True)
    add("Operating occupancy", "Occupancy", "monthly", *rent, "sqft × (annual base + additional rent) / 12", "rent;cam")
    add("Payroll and employer allowance", "Payroll", "monthly", *payroll, "Weekly paid role hours × 52/12 × role wage × (1 + approximation)", "wage_service;wage_baker;employer")
    for key,cat in [("utilities","Utilities"),("services","Services"),("maintenance","Maintenance"),("replenishment","Replenishment")]:
        # Additional production utility and ingredient allowances are explicit demo quantities.
        factor = 1 + ({"purchased":0,"limited":.2,"onsite":.6}[s.production] if key in {"utilities","replenishment"} else 0)
        add(a[key]["item"],cat,"monthly",*[x*factor for x in pair(key)], f"Monthly demo allowance × production usage factor {factor}", key)
    if s.owner_monthly_draw:
        add("Owner living-cost funding (not payroll)", "Owner draw", "monthly", s.owner_monthly_draw,s.owner_monthly_draw,"Optional owner cash draw", "scenario:owner_monthly_draw")
    # Monthly equivalents are budget metrics, not cash payments in covered months.
    for key,cat in [("insurance","Insurance"),("annual_permit","Annual permit")]:
        add(a[key]["item"]+" monthly equivalent",cat,"monthly_equivalent",*[x/12 for x in pair(key)],"Annual payment / 12; excluded from ordinary monthly cash while prepaid",key)
    opening = [sum(r[e] for r in lines if r["timing"]=="opening") for e in ("low","high")]
    contingency = [s.contingency*sum(r[e] for r in lines if r["contingency_eligible"]) for e in ("low","high")]
    schedule=[]
    for month in range(1,s.reserve_months+1):
        cash=[sum(r[e] for r in lines if r["timing"]=="monthly" and (s.reserve_basis!="fixed_only" or r["category"]!="Replenishment")) for e in ("low","high")]
        renewal = month > 1 and (month-1)%12==0
        if renewal:
            cash=[cash[i]+pair("insurance")[i]+pair("annual_permit")[i] for i in (0,1)]
        schedule.append(dict(month=month,low=cash[0],high=cash[1],annual_renewal=renewal))
    reserve=[sum(r[e] for r in schedule) for e in ("low","high")]
    monthly=[sum(r[e] for r in lines if r["timing"] in {"monthly","monthly_equivalent"}) for e in ("low","high")]
    return dict(configuration_fingerprint=configuration_fingerprint(),equipment_selection=equipment(s),model_version=MODEL_VERSION,data_version=DATA_VERSION,mode=mode,scenario=asdict(s),assumptions=a,overrides=overrides or {},lines=lines,cash_schedule=schedule,staffing=hours,wage_floor=floor,wage_floor_source="seattle_ols_2026",preopening=dict(zip(("low","high"),opening)),contingency=dict(zip(("low","high"),contingency)),reserve=dict(zip(("low","high"),reserve)),monthly=dict(zip(("low","high"),monthly)),total={e:opening[i]+contingency[i]+reserve[i] for i,e in enumerate(("low","high"))},warnings=["DEMO: illustrative values, not researched Seattle prices. Seattle 2026 wage floor is separately enforced.","Service coverage gap is not automatically funded; add paid hours before relying on this scenario.","Wages assume multiple workers capped at 40 hours/week; scheduling/overtime and benefits require review.","Existing food premises still require compliance review; no tenant allowance assumed.","Planned-activity budget assumes replenishment without collections; fixed-only reserves exclude replenishment."])
