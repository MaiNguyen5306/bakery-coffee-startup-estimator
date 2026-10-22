from datetime import date
from .loaders import rows
from .normalize import number, monthly_rent

class DataError(ValueError): pass

def validate_tables(folder):
    tables = {name: rows(folder / (name+".csv")) for name in ("sources","observations","rent_listings","assumptions")}
    templates = __import__("pathlib").Path(__file__).resolve().parents[2] / "data/templates"
    for name in tables:
        expected = (templates/(name+".csv")).read_text().strip().split(",")
        import csv
        with (folder/(name+".csv")).open() as f:
            if next(csv.reader(f), []) != expected: raise DataError(f"{name}: incompatible CSV headers")
    ids = {}
    for name, records in tables.items():
        key = {"sources":"source_id","observations":"observation_id","rent_listings":"listing_id","assumptions":"assumption_id"}[name]
        ids[name] = set()
        for r in records:
            if not r[key] or r[key] in ids[name]: raise DataError(f"{name}: duplicate or empty ID")
            ids[name].add(r[key])
            for k,v in r.items():
                if v and k in {"document_date","accessed_date","observed_date","effective_start","effective_end"}: date.fromisoformat(v)
            if r.get("effective_start") and r.get("effective_end") and r["effective_start"] > r["effective_end"]: raise DataError("Reversed effective dates")
    for name in ("observations","rent_listings"):
        for r in tables[name]:
            if r["source_id"] not in ids["sources"]: raise DataError("Unresolved source reference")
    for r in tables["observations"]:
        if r["price"]: number(r["price"])
        if r["currency"] != "USD": raise DataError("Only USD supported")
        for k in ("tax_included","shipping_included","installation_included"):
            if r[k] not in {"","true","false"}: raise DataError("Invalid inclusion flag")
    for r in tables["assumptions"]:
        if r["evidence_status"] not in {"observed","derived","assumed","demo"}: raise DataError("Invalid evidence status")
        if r["confidence"] not in {"low","medium","high"}: raise DataError("Invalid confidence")
        lo,hi=number(r["low"]),number(r["high"])
        if lo>hi: raise DataError("Reversed range")
        valid_units = {"USD", "USD/hour", "USD/month", "USD/year", "USD/sqft", "USD/sqft/year", "USD/sqft/month", "USD/item", "fraction", "USD/kWh", "USD/lb"}
        if r["unit"] not in valid_units: raise DataError("Missing or incompatible unit")
        refs=set(filter(None,r["evidence_ids"].split(";")))
        if refs-ids["observations"]: raise DataError("Unresolved evidence reference")
        if r["evidence_status"] in {"observed","derived"} and not refs: raise DataError("Evidence required")
        for k,choices in {"business_type":{"","coffee","bakery"},"condition":{"","existing","partial","shell"},"quality_tier":{"","standard","premium"}}.items():
            if r[k] not in choices: raise DataError("Invalid applicability selector")
    listings=set()
    for r in tables["rent_listings"]:
        identity=(r["address_or_identifier"].strip().casefold(),number(r["sqft"]))
        if identity in listings: raise DataError("Duplicate syndicated listing")
        listings.add(identity)
        if r["base_rent_quote"]: monthly_rent(r["base_rent_quote"],r["quote_unit"],r["sqft"])
        if r["additional_rent_quote"]: monthly_rent(r["additional_rent_quote"],r["additional_rent_unit"],r["sqft"])
        if r["lease_type"] not in {"NNN","gross","unknown"}: raise DataError("Invalid lease basis")
    return {name:len(records) for name,records in tables.items()}
