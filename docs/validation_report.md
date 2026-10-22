# Validation report · 2026-10-22
Environment: macOS arm64, Python 3.14.7. Installed versions are pinned in requirements.txt. This report records engineering checks; it does not validate estimates against real opened businesses.

The independent hand-worked coffee fixture uses 100 sqft, no espresso or seating, one open day/hour, no owner/training/reserve, $12 annual base + $6 additional rent per sqft, $20/sqft buildout, $24 service wage, 10% employer allowance and zero equipment tax/freight. Monthly rent = $150; deposit = $300; preopening rent = $150; equipment = $12,900; preopening cash = $27,150; eligible contingency basis = $19,900; contingency = $1,990; funding = $29,140. Paid service hours = 3/week. Monthly planned-activity budget = $3,918.20, including annual equivalents. Engine matches each asserted quantity. The initial fixture's handwritten total had a $500 arithmetic error; the ledger and engine agreed, and the expected total was corrected.

Current implementation checks (React/Vite + Vercel Python Function):
- `npm run build`: passed with Vite 7.3.7; emitted production HTML/CSS/JS into dist/.
- `python -m pytest -q`: 49 passed. The former Streamlit UI test was removed; ten API tests were added.
- `python scripts/validate_data.py`: passed registered table schemas and 20 demo assumptions; research completeness remains explicitly blocked.
- `python -m compileall -q api src scripts`: passed.
- `git diff --check`: passed.
- `npm run dev`: React frontend and Python API started together. A GET to the frontend returned the app HTML. A POST through the frontend proxy to /api/estimate returned a valid on-site bakery scenario with zero reserve cash when reserve_months=0. Local binding required sandbox approval.
- Prior raw-file audit inspected five artifacts, generated hashes, extracted PDFs and five Seattle metro occupation records. No original research artifacts were modified.

API tests exercise bootstrap data, default coffee and bakery calculations, research-mode blocking, annual renewal schedules, malformed bodies, request size limits, invalid types/values, wage-floor overrides and export replay/fingerprint mismatch. The calculation tests retain the hand-worked fixture, unit normalization, payroll and reserve sensitivity, production/tier isolation, coverage gaps, range reconciliation and invalid research-data checks.

No Vercel deployment or hosted build was performed. No real-browser visual, mobile, keyboard or React interaction tests were run; the production build and HTTP smoke do not establish those checks. The former Streamlit implementation and its UI test have been removed, and its earlier checks do not validate this frontend.

Remaining validation: full browser interactions, actual shift rosters/overtime, calendar-specific permit proration, quote inclusion reconciliation, supplier quantities, utility usage and real-world comparable budgets. These are not represented as completed checks.
