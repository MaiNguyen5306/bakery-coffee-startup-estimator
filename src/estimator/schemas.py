from dataclasses import dataclass
from math import isfinite

@dataclass(frozen=True)
class Scenario:
    business_type: str = "coffee"
    production: str = "purchased"
    city: str = "Seattle"
    neighborhood: str = "Citywide demo"
    estimate_year: int = 2026
    sqft: float = 1000
    seats: int = 20
    condition: str = "existing"
    tier: str = "standard"
    staffing: str = "owner_operated"
    staff_count: int = 2
    employment_type: str = "full_time"
    owner_hours: float | None = None
    supervisor_hours: float | None = None
    days: int = 6
    hours: float = 9
    opening_date: str = "2026-04-01"
    permit_risk: int = 2
    plan_review_extra_hours: float = 0
    reserve_months: int = 3
    reserve_basis: str = "planned_activity"
    preopening_months: int = 2
    deposit_months: float = 2
    training_hours: float = 80
    contingency: float = .15
    owner_monthly_draw: float = 0
    extra_service_hours: float = 0
    def validate(self):
        from datetime import date
        opening = date.fromisoformat(self.opening_date)
        if opening.year != self.estimate_year: raise ValueError("Opening date must be in estimate year")
        if isinstance(self.permit_risk,bool) or self.permit_risk not in (1,2,3): raise ValueError("Invalid assumed permit risk")
        if isinstance(self.staff_count,bool) or not isinstance(self.staff_count,int) or not 0 <= self.staff_count <= 100: raise ValueError("Staff count must be an integer from 0 to 100")
        allowed = {"employment_type": {"part_time", "full_time"},"business_type": {"coffee", "bakery"}, "production": {"purchased", "limited", "onsite"}, "condition": {"existing", "partial", "shell"}, "tier": {"standard", "premium"}, "staffing": {"owner_operated", "staffed"}, "reserve_basis": {"planned_activity", "fixed_only"}}
        for field, choices in allowed.items():
            if getattr(self, field) not in choices: raise ValueError(f"Invalid {field}")
        for field in ("plan_review_extra_hours", "sqft", "seats", "owner_hours", "days", "hours", "reserve_months", "preopening_months", "deposit_months", "training_hours", "contingency", "owner_monthly_draw", "extra_service_hours"):
            x = getattr(self, field)
            if field == "owner_hours" and x is None: continue
            if isinstance(x, bool) or not isfinite(x) or x < 0: raise ValueError(f"Invalid {field}")
        if self.city != "Seattle" or self.estimate_year != 2026: raise ValueError("Only Seattle 2026 demo is supported; year-specific rules are unverified")
        if self.sqft > 3000: raise ValueError("Space size must be 3,000 square feet or less")
        if self.sqft <= 0 or not 1 <= self.days <= 7 or not 1 <= self.hours <= 16: raise ValueError("Invalid operating dimensions")
        if self.supervisor_hours is not None and (isinstance(self.supervisor_hours,bool) or not isinstance(self.supervisor_hours,(float,int)) or not isfinite(self.supervisor_hours) or self.supervisor_hours<0): raise ValueError("Invalid supervisor hours")
        if (self.owner_hours is not None and self.owner_hours > 80) or self.contingency > 1 or self.reserve_months > 60: raise ValueError("Input exceeds planning limits")
        for field in ("days", "seats", "reserve_months", "preopening_months"):
            if int(getattr(self, field)) != getattr(self, field): raise ValueError(f"{field} must be an integer")
        if self.permit_risk == 1 and self.production != "purchased": raise ValueError("Risk 1 does not permit on-site baking; choose a documented planning risk and confirm with King County")
        if self.business_type == "bakery" and self.production != "onsite": raise ValueError("Retail bakery requires on-site production")
        if self.business_type == "coffee" and self.production == "onsite": raise ValueError("Coffee supports purchased or limited baking")
