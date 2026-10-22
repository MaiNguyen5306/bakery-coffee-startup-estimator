"""Weekly team-hour budgets, not individual employee rosters."""
from math import ceil
from .loaders import config


def staffing(s):
    c = config('staffing_presets.json')
    preset = c[s.staffing]
    required = s.days * (s.hours * 2 + 2)
    requested_owner = preset['owner_hours'] if s.owner_hours is None else s.owner_hours
    lead_required = s.days * (s.hours + 1)
    owner = min(requested_owner, lead_required)
    requested_supervisor = (max(0, lead_required-owner) if s.staffing=='staffed' else 0) if s.supervisor_hours is None else s.supervisor_hours
    # The selected headcount is the entire paid team, including production
    # and working supervisors. Owner service hours never reduce paid contracts.
    hours_per_employee = 20 if s.employment_type=='part_time' else 40
    contracted = s.staff_count*hours_per_employee
    production_required = c['production_weekly_hours'][s.production]
    baker = min(contracted, production_required)
    remaining = contracted-baker
    supervisor = min(requested_supervisor, remaining)
    service = remaining-supervisor+s.extra_service_hours
    paid = contracted+s.extra_service_hours
    return {'service':service,'supervisor':supervisor,'baker':baker,
            'paid_service_total':service+supervisor,'total_paid_hours':paid,
            'staff_count':s.staff_count,'employment_type':s.employment_type,'hours_per_employee':hours_per_employee,'contracted_employee_hours':contracted,'additional_service_hours':s.extra_service_hours,'production_required':production_required,'production_gap':max(0,production_required-baker),'required_service':required,'owner_requested':requested_owner,
            'owner_coverage':owner,'supervisor_requested':requested_supervisor,
            'coverage_gap':max(0,required-owner-service-supervisor),
            'leadership_gap':max(0,lead_required-owner-supervisor) if s.staffing=='staffed' else 0,
            'minimum_service_headcount':ceil(service/hours_per_employee),
            'minimum_supervisor_headcount':ceil(supervisor/hours_per_employee),
            'minimum_baker_headcount':ceil(baker/hours_per_employee),
            'minimum_total_headcount':ceil(paid/hours_per_employee),
            'basis':'Paid hours = staff count × 20 (part time) or 40 (full time), plus explicitly entered extra service hours. Owners excluded. Production hours are allocated first, then working supervisors, then regular service; none are added twice. The whole team uses the selected employment type. Two service positions during open hours plus two team hours/day for setup/close. Working supervisor replaces service hours; production is separate. All paid hours are team totals. Staff-led auto supervisor coverage = days × (open hours + 1) minus owner service coverage. No owner production or management-only administration is modeled.'}
