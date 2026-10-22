# Opening Day · Bakery & Coffee Shop Business Planner
A React web app prepared for Vercel, backed by the existing independent Python calculation engine. **Evidence-derived wages/food fees coexist with demo costs; research-ready funding remains blocked. Revenue is scenario arithmetic, not a demand forecast.** Supports coffee shops with purchased pastries or limited baking and on-site retail bakeries, with espresso equipment included for both shop types.

## Local development
Requires Node.js 22.12+ and Python 3.11+. The web app and calculation API need no Python packages or credentials.
```bash
npm ci
npm run dev
```
Open the Vite URL printed in the terminal (usually http://127.0.0.1:5173). This starts Vite and the Python API on port 8000 together. Ctrl+C stops both. The API reloads after Python/config/CSV changes. If a dev server from the earlier implementation is still running, restart it once to load the new Revenue endpoints. Vite proxies `/api/estimate` to the local API. If Python is unavailable as `python3`, create `.venv` first. If the usual ports are busy, run `npm run dev -- --api-port 8010 --port 5174` without interrupting another server.

## Vercel
Import this repository into Vercel, select the repository root, and use the Vite framework preset. Tracked `vercel.json` sets `npm run build` and the `dist` output directory. Vercel serves `api/estimate.py` as a Python Function. No environment variables or secrets are needed. No deployment has been performed.

The Python runtime uses only the standard library. The production function reads `src/estimator`, `config`, `data/demo`, `data/processed`, and source/methodology documentation; these must stay in the project root. Raw research artifacts, local environments, tests and outputs are excluded from the function bundle. `.vercelignore` also prevents uploading raw evidence. This follows [Vercel's Python Function runtime](https://vercel.com/docs/functions/runtimes/python) and [Vite hosting](https://vercel.com/docs/frameworks/frontend/vite) conventions.

```bash
npm run build
```
`npm run preview` previews static assets only; use `npm run dev` for an end-to-end local experience, or `vercel dev` with the Vercel CLI for platform emulation.

## Features
Home offers Cost and Revenue with persistent shared shop settings. Views use hash URLs (`#/`, `#/cost`, `#/revenue`) and browser history: Back from either tool returns to Home, including after switching between tools. Forward restores the tool without clearing inputs. Direct tool links also receive a Home history entry; reloads preserve existing history. Revenue supports target monthly sales → required transactions/day/hour, expected daily transactions → sales, editable AOV or purchase baskets, card/cash/channel fees and fee-base uplift, linked or user-entered fixed operating costs, illustrative break-even/operating surplus, capacity/peak checks, sensitivity, baseline comparison and JSON/CSV exports. Cost and Revenue recalculate automatically after a short pause in input. Old results and exports stay hidden during updates; superseded requests cannot replace newer results. Basic sales calculations work without supplier data; incomplete staffing or missing variable-cost confirmation blocks break-even. Research-derived menu facts are references, not automatic AOV or observed demand.

Cost preserves the existing Responsive shop quiz, production-specific equipment and paid labor, editable assumption ranges, wage-floor enforcement, service and working-supervisor coverage gaps,role payroll breakdowns, startup funding and refundable deposits, monthly budget, month-by-month reserve, annual payment handling, category bars, baseline comparison, JSON replay and CSV download. Demo labeling persists and no revenue is deducted. Sources and methodology are available in the interface. Estimates are calculated server-side through one tested engine, with no duplicate JavaScript formulas.

## Research and validation
Optional research tooling uses pandas, openpyxl and pypdf. Install separately from the production runtime:
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python scripts/validate_data.py
python -m pytest -q
python scripts/build_assumptions.py
python scripts/derive_wage_assumptions.py
python scripts/extract_revenue_evidence.py
python scripts/run_example.py
npm run test:web
```
The research audit preserves supplied files, records hashes, extracts PDF text, inspects BLS columns and selects relevant Seattle metro role records into ignored `data/interim`. It does not promote unverified files to approved default assumptions. Header-only collection templates are in `data/templates`; factual observations and source records live in `data/processed`; demo assumptions live in `data/demo`.

Revenue PDFs belong in `data/raw/revenue/menus`, `payments`, `suppliers`, or `methodology`; all originals remain ignored/local-only. `data/templates/revenue` was absent in the supplied checkout, so seven blank schemas were created. Processed facts and source hashes are in `data/processed/revenue`. The extraction script replays curated PDF/page selections and a dated official Square web-rate capture; it does not claim to fetch current web prices every run. Optional DOM tests require the dev dependencies installed by `npm ci` plus the Python test environment. They simulate interactions and do not replace real-browser QA.

Next evidence priorities: permitted public Seattle lease comparables with additional rent, local commercial buildout scopes, comparable equipment models/tax, permit applicability/current invoice dates/future fees,local wage/employer cost evidence, employer-cost components, usage-based utilities and supplier quantities. Raw PDFs/workbooks stay under `data/raw` and out of Git/Vercel until provenance and reuse terms are reviewed.

See `docs/methodology.md`, `docs/limitations.md`, `docs/evidence_coverage.md`, `docs/research_backlog.md` and `docs/validation_report.md`, `docs/revenue_methodology.md`, `docs/revenue_data_dictionary.md` and `docs/location_audit.md`. No actual-business budget validation, live sales model or financing advice is claimed. Matching model/data/configuration versions are required for export replay.

Staffing: select the number of paid employees and Part time (assumed 20 hours/week) or Full time (assumed 40 hours/week). Total contracted employee hours = count × hours. The owner is excluded, and changing owner hours does not reduce the selected employees' paid hours. Supervisors and production staff are roles inside this total; missing role/service coverage is flagged rather than automatically funded. Additional service hours in advanced assumptions are explicitly added beyond the contracted total. All selected employees share one schedule type; mixed rosters are not yet supported. Staffing approach still sets owner/supervisor defaults. No actual shift roster or overtime compliance is implied.
