from .loaders import config

def staffing(s):
    c = config("staffing_presets.json")
    # Two service positions cover open hours plus one hour of setup/close per day.
    required = s.days * (s.hours * 2 + 2)
    owner = min(s.owner_hours, required)
    paid_service = max(0, s.days * (s.hours + 1) * c[s.staffing]["service_workers"] - owner) + s.extra_service_hours
    production = c["production_weekly_hours"][s.production]
    return {"service": paid_service, "baker": production, "required_service": required, "owner_coverage": owner, "coverage_gap": max(0, required-owner-paid_service), "minimum_service_headcount": __import__("math").ceil(paid_service / 40), "minimum_baker_headcount": __import__("math").ceil(production / 40)}
