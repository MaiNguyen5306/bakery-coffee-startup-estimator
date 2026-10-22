# Opening Day · Seattle startup planner
A React web app prepared for Vercel, backed by the existing independent Python calculation engine. **Demo prices are illustrative; research-ready totals remain blocked.** Supports coffee shops with purchased pastries or limited baking and on-site retail bakeries with optional espresso.

## Local development
Requires Node.js 22.12+ and Python 3.11+. The web app and calculation API need no Python packages or credentials.
```bash
npm ci
npm run dev
```
Open the Vite URL printed in the terminal (usually http://127.0.0.1:5173). This starts Vite and the Python API on port 8000 together. Ctrl+C stops both. Vite proxies `/api/estimate` to the local API. If Python is unavailable as `python3`, create `.venv` first. This replaces the former Streamlit interface completely.

## Vercel
Import this repository into Vercel, select the repository root, and use the Vite framework preset. Tracked `vercel.json` sets `npm run build` and the `dist` output directory. Vercel serves `api/estimate.py` as a Python Function. No environment variables or secrets are needed. No deployment has been performed.

The Python runtime uses only the standard library. The production function reads `src/estimator`, `config`, `data/demo`, and source/methodology documentation; these must stay in the project root. Raw research artifacts, local environments, tests and outputs are excluded from the function bundle. `.vercelignore` also prevents uploading raw evidence. This follows [Vercel's Python Function runtime](https://vercel.com/docs/functions/runtimes/python) and [Vite hosting](https://vercel.com/docs/frameworks/frontend/vite) conventions.

```bash
npm run build
```
`npm run preview` previews static assets only; use `npm run dev` for an end-to-end local experience, or `vercel dev` with the Vercel CLI for platform emulation.

## Features
Responsive shop quiz, production-specific equipment and paid labor, editable assumption ranges, wage-floor enforcement, service staffing gaps, startup funding and refundable deposits, monthly budget, month-by-month reserve, annual payment handling, category bars, baseline comparison, JSON replay and CSV download. Demo labeling persists and no revenue is deducted. Sources and methodology are available in the interface. Estimates are calculated server-side through one tested engine, with no duplicate JavaScript formulas.

## Research and validation
Optional research tooling uses pandas, openpyxl and pypdf. Install separately from the production runtime:
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python scripts/validate_data.py
python -m pytest -q
python scripts/build_assumptions.py
python scripts/run_example.py
```
The research audit preserves supplied files, records hashes, extracts PDF text, inspects BLS columns and selects relevant Seattle metro role records into ignored `data/interim`. It does not promote unverified files to approved default assumptions. Header-only collection templates are in `data/templates`; factual observations and source records live in `data/processed`; demo assumptions live in `data/demo`.

Next evidence priorities: permitted public Seattle lease comparables with additional rent, local commercial buildout scopes, comparable equipment models/tax, permit applicability and calendar proration, role wage provenance, employer-cost components, usage-based utilities and supplier quantities. Raw PDFs/workbooks stay under `data/raw` and out of Git/Vercel until provenance and reuse terms are reviewed.

See `docs/methodology.md`, `docs/limitations.md`, `docs/evidence_coverage.md`, `docs/research_backlog.md` and `docs/validation_report.md`. No actual-business budget validation, live sales model or financing advice is claimed. Matching model/data/configuration versions are required for export replay.
