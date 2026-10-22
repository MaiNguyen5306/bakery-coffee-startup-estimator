from dataclasses import dataclass
from math import isfinite

@dataclass(frozen=True)
class Scenario:
    business_type: str = "coffee"
    production: str = "purchased"
    espresso: bool = True
    city: str = "Seattle"
    neighborhood: str = "Citywide demo"
    estimate_year: int = 2026
    sqft: float = 1000
    seats: int = 20
    condition: str = "existing"
    tier: str = "standard"
    staffing: str = "owner_operated"
    owner_hours: float = 40
    days: int = 6
    hours: float = 9
    reserve_months: int = 3
    reserve_basis: str = "planned_activity"
    preopening_months: int = 2
    deposit_months: float = 2
    training_hours: float = 80
    contingency: float = .15
    owner_monthly_draw: float = 0
    extra_service_hours: float = 0
    def validate(self):
        allowed = {"business_type": {"coffee", "bakery"}, "production": {"purchased", "limited", "onsite"}, "condition": {"existing", "partial", "shell"}, "tier": {"standard", "premium"}, "staffing": {"owner_operated", "staffed"}, "reserve_basis": {"planned_activity", "fixed_only"}}
        for field, choices in allowed.items():
            if getattr(self, field) not in choices: raise ValueError(f"Invalid {field}")
        for field in ("sqft", "seats", "owner_hours", "days", "hours", "reserve_months", "preopening_months", "deposit_months", "training_hours", "contingency", "owner_monthly_draw", "extra_service_hours"):
            x = getattr(self, field)
            if isinstance(x, bool) or not isfinite(x) or x < 0: raise ValueError(f"Invalid {field}")
        if self.city != "Seattle" or self.estimate_year != 2026: raise ValueError("Only Seattle 2026 demo is supported; year-specific rules are unverified")
        if self.sqft <= 0 or not 1 <= self.days <= 7 or not 1 <= self.hours <= 16: raise ValueError("Invalid operating dimensions")
        if self.owner_hours > 80 or self.contingency > 1 or self.reserve_months > 60: raise ValueError("Input exceeds planning limits")
        for field in ("days", "seats", "reserve_months", "preopening_months"):
            if int(getattr(self, field)) != getattr(self, field): raise ValueError(f"{field} must be an integer")
        if self.business_type == "bakery" and self.production != "onsite": raise ValueError("Retail bakery requires on-site production")
        if self.business_type == "coffee" and self.production == "onsite": raise ValueError("Coffee supports purchased or limited baking")
