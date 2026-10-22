from .loaders import config

def equipment(s):
    c = config("equipment_packages.json")
    names = ["core"]
    if s.espresso: names.append("espresso")
    if s.business_type == "coffee": names.append("coffee")
    if s.production != "purchased": names.append(s.production)
    factor = c["tier_factors"][s.tier]
    rows = []
    for package in names:
        for item, quantity, low, high in c["packages"][package]:
            rows.append(dict(item=item, quantity=quantity, low=low*quantity*factor, high=high*quantity*factor, basis=f"{quantity} × demo {s.tier} item price; package {package}", evidence_id=f"config:{package}:{item}"))
    rows.append(dict(item="service_furniture", quantity=s.seats, low=s.seats*100, high=s.seats*220, basis=f"{s.seats} seats × demo 100–220 USD", evidence_id="demo:furniture"))
    return rows
