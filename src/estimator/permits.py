"""King County annual permit planning schedule; fee year and calendar timing are separate."""
from datetime import date
from .loaders import config


def permit_fee(s):
    c=config('permit_fees.json')
    if s.permit_risk not in (1,2,3): raise ValueError('Permit risk must be 1, 2 or 3 (scenario assumption, not a regulatory determination)')
    if s.business_type=='bakery' and s.seats==0: row='bakery_no_seating'
    elif s.seats<=12: row='general_0_12'
    elif s.seats<=50: row='general_13_50'
    elif s.seats<=150: row='general_51_150'
    elif s.seats<=250: row='general_151_250'
    else: row='general_over_250'
    amount=c['annual_fees'][row][s.permit_risk-1]
    return amount, row


def calendar_month(start, offset):
    n=start.year*12+start.month-1+offset
    return date(n//12,n%12+1,1)


def permit_timing(opening_date, annual_pair, months):
    start=date.fromisoformat(opening_date)
    # Opening payment covers remainder of Apr–Mar permit year under quarterly proration.
    fraction=1 if start.month in (4,5,6) else .75 if start.month in (7,8,9) else .5 if start.month in (10,11,12) else .25
    deadline=date(start.year+1 if start.month>=4 else start.year,3,31)
    opening_renewal=deadline<=start
    return {'opening_fraction':fraction,'opening_renewal':opening_renewal,'opening':[x*(fraction+int(opening_renewal)) for x in annual_pair],
            'renewals':[m for m in range(1,months+1) if calendar_month(start,m-1).month==3 and date(calendar_month(start,m-1).year,3,31)>start],
            'covered_until':f'{start.year+1 if start.month>=4 else start.year}-03-31',
            'renewal_policy':'Renewal cash allocated to March (before April 1 coverage), following official historical March 31 deadline guidance; exact current invoice date needs confirmation. A March 31 opening includes the same-day renewal before opening, never twice. Future years carry the selected 2026 fee as an explicit scenario assumption, not an observed future rate.'}
