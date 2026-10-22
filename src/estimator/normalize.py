from math import isfinite

def number(value):
    if value is None or str(value).strip() in {"", "*", "**", "#", "-", "—"}: raise ValueError(f"Missing or suppressed numeric value: {value!r}")
    n = float(str(value).replace(",", ""))
    if not isfinite(n) or n < 0: raise ValueError("Expected finite nonnegative number")
    return n

def monthly_rent(quote, unit, sqft):
    quote, sqft = number(quote), number(sqft)
    if unit == "USD/sqft/year": return quote * sqft / 12
    if unit == "USD/sqft/month": return quote * sqft
    if unit == "USD/month": return quote
    raise ValueError(f"Incompatible rent unit: {unit}")
