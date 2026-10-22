# Validation report · model0.4.0 ·2026-10-22
Environment: macOS arm64,Python3.14.7,Node24.22.0,Vite7.3.7. Tests establish implementation behavior, not real-world customer demand or cost accuracy.

## Checks actually run
- `python -m pytest -q`:91passed. Covers the existing Cost engine/data/API plus Revenue,permits,unit conversions,evidence validation and export replay.
- `npm run test:web`:three simulated DOM tests passed. It exercises Home→Cost→Revenue navigation,shared space-size persistence,revenue input persistence,stale notices/hidden figures after price or linked-cost changes,explicit refresh,baseline changes,target-sales and expected-orders modes,manual break-even and zero orders. This uses happy-dom with API calls executed against the actual Python handler; it is not a real browser.
- `npm run build`:passed,emitting production HTML,CSS and JavaScript.
- `python scripts/validate_data.py`:passed. Cost:13sources,30observations,1listing and4promoted assumptions. Combined defaults:22rows. Revenue:5sources,8menu prices,6payment fee records;0supplier/recipe/basket/assumption observation rows. These empty schemas do not establish zero cost or demand. Research-ready funding remains incomplete.
- `python scripts/extract_revenue_evidence.py`:inspected all4owner PDFs and regenerated8selected menu facts,PDF hashes/page references and6separately verified dated official-web fee rates. It does not claim a fresh web retrieval during replay.
- `python scripts/derive_wage_assumptions.py`:regenerated reviewed role-specific floor-adjusted wage defaults from the supplied May2025 metro extract.
- `python scripts/run_example.py`:exported current demo/mixed-evidence coffee scenario:169544.2235–329784.8923333333USD.
- `python -m compileall -q src api scripts`:passed.
- `git diff --check`:passed after normalizing authored CSVs to LF; initial CSV CRLF additions were corrected and generators now emit LF.
- HTTP smoke:an independent app instance on127.0.0.1:5174 with API8010 returned the Revenue bootstrap with8menu prices;POST through Vite proxy reproduced3000monthly orders and6000USD surplus;October15opening returned50%permit proration and aMarch2027renewal in reserve month6.
- `.gitignore`/`.vercelignore`:original revenue PDF files remain ignored and raw artifacts excluded from hosting upload. No raw files staged;no push or deployment performed.

The standard8000/5173ports were already occupied by an older user-side process. It was left undisturbed;QA used8010/5174. Restart the existing `npm run dev` once to load the new API/dev runner. The runner now reloads the API after subsequent source/config/CSV changes.

## Independent fixtures
Revenue:10USD AOV,26days,8hours,30000USD target gives3000orders/month,115.384615384615/day,14.423076923077/hour and optional116constant daily goal. With12000USD fixed costs and4USD total variable cost/order,no extra processing fee,contribution=6USD,break-even=2000orders/20000USD sales and operating surplus at3000orders=6000USD. Zero target yields zero required transactions. Rounding is tested separately from financial arithmetic.

Cost hand fixture deliberately pins fees to the previous illustrative values(annual permit900USD,review0)to isolate the ledger:100sqft,no seating/espresso/owner/training/reserve,annual rent12+6USD/sqft,buildout20USD/sqft,24USD service wage,10%employer allowance,zero equipment tax/freight. Opening cash27150USD,eligible contingency basis19900USD,contingency1990USD,total29140USD and monthly operating budget3918.20USD all match. Official fee behavior is checked independently across January,March31,April,June,July,October andDecember openings.

Permit tests assert quarterly initial fractions,March renewal cash,March31same-day renewal exactly once,insurance renewals separately,zero reserve and incremental-month cash equality. Wage tests assert service21.30–21.75and baker23.16–25.80,legal floor enforcement and year rejection.

Revenue checks cover weighted basket quantities/shares,transaction shares with unequal channel baskets,fee-base uplift,supplier mass-unit conversion,waste and packaging,nonpositive contribution,missing cost data,expanded staffing schedules,duplicate linked-line prevention,removal of replenishment/owner draws,capacity/peak/nonpeak and target surplus,version/fingerprint replay and stale linked snapshots. Invalid references,units,dates and duplicate evidence rows are rejected.

## Not verified
No real-browser visual/mobile/keyboard QA or screenshots. No hosted Vercel build/deployment. No actual-business budget/demand validation. Current invoice dates/future fees,real staffing schedules/overtime,contractor scope reconciliation,supplier costs,waste,capacity and storefront demand remain unverified. See research_backlog.md; no predictive accuracy is claimed.

Navigation follow-up: hash URLs now synchronize Home/Cost/Revenue with browser history. The regression check exercises popstate Back/Forward rendering, sibling-tool history replacement, preserved inputs and logo navigation. Happy-dom lacks actual history traversal, so the test moves the URL and dispatches the browser event contract; a real-browser Back/Forward check was not performed. Production build and git diff whitespace checks passed.

Staffing follow-up actual checks:91backend tests and3DOM tests passed. New checks cover Staff led→0owner default,automatic60supervisor/60service team split,40owner hours reducing paid total to80,custom supervisor/leadership gaps,one-position owner cap,separate production,wage derivation29.62–36.57,floor-safe overrides,role-payroll reconciliation and export replay. DOM verifies preset changes,editable owner/supervisor hours,automatic reset and team-total labels. Data validation and byte compilation passed. UI hourly wages retain cents. No real-browser visual inspection was performed.

Staff-count follow-up (model 0.5.0): backend tests now cover explicit headcount and 20/40-hour schedule multiplication, zero/invalid counts, owner independence, production allocation within the budget, missing role coverage, extra-hours accounting, payroll monotonicity and replay. The historical cost hand fixture now explicitly selects zero contracted staff plus three additional service hours to retain its independently calculated ledger. Default scenario funding changes because two selected full-time employees provide 80 hours rather than the previous 50-hour automatic owner-operated budget. Staff-led fixtures that require 120 hours now explicitly select three full-time employees. Existing model/data exports require their matching version; no silent reinterpretation is performed.

Actual checks for model 0.5.0: 103 backend tests and 4 simulated DOM tests passed; production build, data validation, byte compilation and git diff whitespace checks passed. DOM checks cover new staff-count and employment-type controls, owner independence and updated totals. No real-browser visual verification was performed.

Espresso scope update (model 0.5.1): coffee and bakery packages now always include one espresso machine and two grinders. The checkbox and optional scenario flag were removed. The independent hand fixture now includes the 8600USD demo espresso equipment addition: opening cash35750USD,contingency2850USD,total38600USD. Existing fee/tax/freight fixture overrides remain fixed,so the equipment-only change reconciles directly. Default coffee totals are unchanged because espresso was already enabled. Old-version exports require their matching model.

Automatic Revenue follow-up: 109 backend tests and 6 simulated DOM tests passed. Revenue now calculates on initial load and input/linked-cost changes after a 250ms debounce, without a refresh button. Tests verify initial results, automatic target/expected-order updates, hidden old figures/exports while updating, and a deliberately delayed obsolete response that cannot overwrite a newer calculation. The existing manual-refresh assertions were updated to the owner's new interaction requirement. Production build and whitespace checks passed. No real-browser visual QA was performed.

Live-request compatibility also fixes the previously reported retired espresso-field error: Cost and linked Revenue requests discard only the obsolete espresso switch before constructing the current scenario. Both old true/false values still include standard espresso equipment; other unknown fields remain errors. Current exports contain the normalized scenario. Versioned historical-export replay retains its existing strict version/fingerprint checks.
