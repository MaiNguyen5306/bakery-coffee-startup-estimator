# Codex Build Brief — Bakery & Coffee Shop Startup Cost Estimator

Prepared for MaiNguyen5306 | October 22, 2026

## 1. Instructions to the implementing Codex agent

Treat this document as the project specification and implementation request. Build a working local application, research pipeline, documented estimation engine, and reproducible validation. Do not stop at proposing a plan. Inspect the repository and applicable AGENTS.md first; preserve existing work and adapt this structure if equivalent components exist. Report material conflicts rather than overwriting unrelated files.

Build the project incrementally. Start with one end-to-end Seattle coffee-shop example, then extend to the supported bakery scenario. Use reasonable implementation choices without repeatedly asking the owner for approval. Do not publish, push, or deploy unless separately requested. Never fabricate source observations, contractor quotes, downloaded data, or completed research. Continue independent engineering if research access is blocked, using conspicuously labeled demo assumptions in a separate mode.

At completion provide the run command, implemented features, actual checks run, unresolved evidence gaps, and next research priorities. The app being runnable is distinct from its estimates being research-ready.

## 2. Business question and intended outcome

How much initial cash might an entrepreneur need to open a leased bakery or coffee shop in Seattle, given their space, production method, equipment, staffing, and desired operating reserve?

Deliver a short interactive quiz producing:
- A low-to-high estimated funding range.
- Cash required before opening, with refundable deposits identified separately.
- Estimated monthly operating outflows under explicit assumptions.
- An optional cash reserve and its calculation.
- Category breakdowns, major cost drivers, scenario comparisons, and editable assumptions.
- Traceable sources, effective dates, missing-data flags, and methodology.

This is a business/financial analytics portfolio project. Demonstrate research, data cleaning, unit normalization, financial modeling, sensitivity analysis, validation, and useful communication. Do not introduce machine learning merely to make the project appear more technical.

## 3. MVP scope and boundaries

Support Seattle, USD, leased storefronts, and two primary business types:
1. Coffee shop, with purchased pastries or optional limited on-site baking.
2. Retail bakery producing on-site, with optional espresso service.

Production method must determine actual equipment and labor requirements. Avoid a single blanket bakery multiplier. Additional cities should be supported by the data architecture but not advertised as available before their local evidence is collected.

Exclude property purchases, franchises, food trucks, home/cottage bakeries, acquisition goodwill, full restaurant menus, alcohol, financing structures, sales forecasts, profitability forecasts, and loan recommendations from the MVP. List material exclusions near the results. Do not infer that existing food-service premises are automatically compliant or require no work.

## 4. Recommended technical setup

Use Python, pandas, Streamlit, Plotly, and pytest. Use CSV for research observations and assumptions; JSON for scenario exports and versioned equipment/staffing mappings. Keep dependencies minimal and pin compatible versions after checking the available runtime. Use a virtual environment and provide Mac-friendly setup instructions. No database, authentication, paid API, or external service should be necessary for local use.

Keep all business calculations independent from Streamlit. A future React/Next.js frontend can reuse the documented data contracts; no frontend migration is required now.

Suggested structure:

```text
app.py
src/estimator/
  schemas.py
  loaders.py
  normalize.py
  research.py
  equipment.py
  staffing.py
  calculate.py
  scenarios.py
  validation.py
data/
  raw/README.md
  raw/wages/
  raw/permits/
  raw/rent/
  raw/equipment/
  raw/buildout/
  raw/other/
  interim/
  processed/
  demo/
config/
  equipment_packages.json
  staffing_presets.json
  model_settings.json
scripts/
  validate_data.py
  build_assumptions.py
  run_example.py
tests/
docs/
  methodology.md
  data_dictionary.md
  source_register.csv
  assumptions_log.md
  limitations.md
  validation_report.md
  research_backlog.md
outputs/
README.md
requirements.txt
.gitignore
```

Do not commit restricted third-party PDFs, large raw archives, personal quotes, secrets, or virtual environments. Document how to obtain excluded raw materials. Check source reuse terms before redistributing observations or documents.

## 5. Data acquisition: what to download and collect

There is no supplied unified training dataset. Assemble a cost evidence dataset. Links below are starting sources, not proof that every input has already been researched. Verify current pages, effective years, units, and applicability during implementation. Collection date and effective date are separate fields. Never silently mix estimate-year rules.

### A. Downloadable official wage data

Source: https://www.bls.gov/oes/tables.htm

Download a published Metropolitan and Nonmetropolitan Area XLSX release (often delivered inside a ZIP), or the All Data XLSX release if the area file is inconvenient. Preserve the original filename and release year. Choose the latest actual published release visible on the official page, not a guessed filename. Unzip locally if necessary and place it in data/raw/wages/.

Filter to Seattle–Tacoma–Bellevue and relevant occupations such as bakers, food preparation workers, counter/fast-food workers where appropriate, food-service supervisors, and managers. Inspect actual column names, suppression markers, occupational definitions, and geographic identifiers before writing the loader. Metro wages are benchmarks, not Seattle-only observations. Do not average wages across unrelated roles or use the broad food-service group as the sole baker wage.

Seattle wage rules: https://seattle.gov/laborstandards/ordinances/minimum-wage

Save the fact sheet for the selected estimate year in data/raw/wages/. Use the applicable city wage floor and separately sourced role benchmarks; older survey wages must not produce defaults below the applicable floor. Future-year estimates need explicitly available future-year rules or a disclosed scenario assumption.

### B. Food permits and local opening requirements

Seattle handbook: https://www.seattle.gov/economic-development/start-a-business/food-business-handbook

King County permanent permit entry point:
https://cd.kingcounty.gov/en/dept/dph/certificates-permits-licenses/food-business-permits/permanent-food-business-permit

2026 food fee PDF starting link:
https://cdn.kingcounty.gov/-/media/king-county/depts/dph/documents/health-safety/environmental-health/fees/food-establishment-fees-through-2026.pdf

Download the applicable fee PDF and plan-review guide through the official permit page. If the direct PDF link changes, navigate from that page. Store in data/raw/permits/. Record document year, page/table, risk/seating conditions, initial vs annual fees, and plan-review vs operating permits. Do not assign risk categories as a definitive regulatory determination; use documented scenario assumptions or a user override.

Seattle business license: https://www.seattle.gov/city-finance/business-taxes-and-licenses/business-licenses

Washington business licensing: https://dor.wa.gov/open-business/apply-business-license

Use those official sources for relevant business-registration and license charges. Do not equate formation, state business licensing, city licensing, and food permits. Verify selected business structure and applicable fees; explain any simplified default.

### C. Rent: collect comparable observations, not a ready CSV

Market context: https://kidder.com/market-reports/seattle-retail-market-report/
Listing entry points: https://www.loopnet.com/ and https://www.crexi.com/

Use public broker brochures and permitted public listings. Aim for 20–30 relevant Seattle storefront observations as a practical starting target, not a statistically representative sample requirement. Prioritize food-compatible spaces and clearly identify uncertain suitability. Record neighborhood, address/listing identifier, area, lease basis, quote period, advertised additional charges, condition, observation date, and source URL. Unknown NNN/CAM is missing, not zero. Deduplicate syndicated listings. Do not bypass sign-in restrictions or access controls. Provide a manual CSV-entry workflow when automated access is unavailable.

### D. Equipment: collect product-level prices

https://www.webstaurantstore.com/
https://www.webstaurantstore.com/42715/commercial-ovens.html

Collect model-level listings from vendors/manufacturers/local dealers. Target 2–3 genuinely comparable products per major required item, capacity, and quality tier when feasible. Record new/used status, voltage, capacity, footprint, quantity, freight, tax, installation, and exclusions. Do not compare a countertop appliance with a commercial production oven as interchangeable evidence.

Coffee package: espresso machine if selected, grinder(s), brewer if selected, refrigeration, water treatment, ice equipment if required, washing/sanitation equipment, smallwares, POS, service furniture.

Bakery additions: appropriately sized oven(s), mixer, proofing/storage requirements, production tables/racks, baking smallwares, display equipment, incremental refrigeration. Requirements depend on the menu and production scale. Equipment packages are planning assumptions, not approved facility designs.

### E. Utilities, POS, employer costs, other overhead

Electricity: https://www.seattle.gov/city-light/business-solutions/business-billing-and-account-information/business-rates
POS: https://squareup.com/us/en/point-of-sale/restaurants/pricing
Workers' compensation rates: https://lni.wa.gov/insurance/rates-risk-classes/rates-for-workers-compensation/
Workers' compensation classes: https://www.lni.wa.gov/insurance/rates-risk-classes/risk-classes-for-workers-compensation/

Save relevant commercial rate sheets and vendor pricing snapshots. Record subscriptions separately from hardware and sales-dependent transaction fees. Utility rates require usage assumptions; a tariff is not a complete monthly bill. Source other employer costs from official IRS, Washington ESD, and relevant state program pages during implementation. Distinguish employee-withheld amounts from employer expenses and hourly premiums from percentage payroll charges. Do not use a generic payroll-burden rate as if it were an official combined tax rate.

Collect insurance estimates, internet, waste, cleaning, accounting, marketing, and supplier prices separately. Quotes and illustrative allowances must be labeled as such. Never submit personal details or contact vendors on the owner's behalf without authorization.

### F. Buildout: research required; no supplied ready dataset

Collect local contractor cost guides, detailed completed-project examples, and voluntarily supplied quotes. Separate existing food-service space, partial conversion, and unfinished shell. Record geography/year, scope, square footage, exclusions, design/permit inclusion, electrical/plumbing/HVAC, accessibility, ventilation, and contingency inclusion. If adequate evidence is unavailable, retain an editable explicitly assumed range and mark the category as low confidence. Do not substitute generic residential renovation costs.

## 6. Data contracts

Create header-only CSV templates and a data dictionary. Unknown numeric values are blank/null, never invented zero. Use stable internal IDs.

sources.csv: source_id, publisher, title, url, document_date, accessed_date, local_path, geography, reuse_notes, status.

observations.csv: observation_id, source_id, category, item, specification, city, neighborhood, business_type, condition, quality_tier, price, currency, unit, price_period, tax_included, shipping_included, installation_included, effective_start, effective_end, observed_date, notes.

rent_listings.csv: listing_id, source_id, address_or_identifier, neighborhood, sqft, base_rent_quote, quote_unit, lease_type, additional_rent_quote, additional_rent_unit, food_service_status, space_condition, observed_date, notes.

assumptions.csv: assumption_id, category, item, city, estimate_year, business_type, condition, quality_tier, low, high, unit, calculation_basis, evidence_ids, evidence_status, confidence, effective_start, effective_end, notes.

Use a normalized assumption-to-evidence bridge table if simpler than storing ID arrays in CSV. Define valid enums and explicit applicability rules. Blank selectors should mean a documented wildcard only, not accidentally match every condition.

evidence_status: observed, derived, assumed, demo. Confidence is a transparent editorial assessment, not a probability. Derivation must record the inclusion criteria and method. Do not label a small convenience sample's min/max as a population confidence interval. Reject incompatible units, duplicate IDs, unresolved evidence references, reversed ranges, and negative costs.

Maintain separate factual source observations and analyst-selected model assumptions. Preserve raw evidence unchanged. Derived files must be reproducible through scripts rather than manual notebook state.

## 7. Quiz and scenario inputs

Use a short progressive quiz with sensible editable defaults:
1. Business type and production method; optional espresso for bakeries.
2. Seattle location/neighborhood, with citywide fallback disclosed.
3. Square footage and seating; presets may populate editable values.
4. Space condition.
5. Equipment tier and optional used equipment if evidence supports it.
6. Staffing preset, owner working hours, opening days/hours.
7. Reserve months: 0, 3, 6, or custom.

Advanced assumptions should include preopening months, paid training hours, lease deposit months, wage overrides, employer cost assumptions, opening/replenishment inventory quantities, utility usage, contingency percentage, and owner cash compensation/draw. Owner labor is not unlimited free staffing. Identify uncovered hours in owner-operated scenarios and distinguish business payroll from optional owner living-cost funding.

Do not expose unsupported neighborhoods or equipment configurations as researched choices. Keep detailed questions outside the short quiz unless required to avoid misleading results.

## 8. Financial calculation specification

Calculate detailed line items with both endpoints. All quantities and selected assumptions must be traceable in exported results. Avoid intermediate rounding; round display only.

Monthly base rent = sqft × annual base rent per sqft ÷ 12. Normalize monthly and annual quotes before use. Add NNN/CAM only when not already included. Deposits use the documented applicable rent basis.

Buildout = sqft × applicable buildout rate, or an explicit user quote. Identify what is included. Do not add electrical, plumbing, installation, or design charges again when already inside the selected package. A tenant allowance reduces cash needs only when payment timing supports it; otherwise show as an optional later reimbursement. Default to no assumed allowance.

Equipment = sum(quantity × matched item price) + separately applicable freight/tax/installation. Purchased vs leased equipment are different cash schedules; support purchase only initially unless leasing is fully modeled. Sales/use tax is item-specific and must not be applied indiscriminately to wages, deposits, or every fee.

Monthly paid hours by role = weekly paid hours × 52/12. Base payroll = sum(monthly paid hours × wage). Add employer costs using their actual basis where researched; allow a disclosed approximation when necessary. Cover opening/closing, prep, production, and training hours. Avoid counting owner coverage and employee coverage twice. Do not assume all worker hours can be assigned to one employee without overtime implications.

Preopening cash includes deposits, applicable prepaid rent, preopening occupancy costs, buildout, equipment/furniture/POS hardware, required opening fees, initial inventory, training payroll, insurance prepayments, professional services, and launch spending.

Monthly operating outflows include occupancy, payroll/employer costs, utilities, insurance, subscriptions, maintenance, recurring services, and an explicit replenishment/consumables scenario. No-sales reserve means no revenue offset; it does not mean physically selling inventory while claiming no transactions. Use a clearly named planned-activity operating budget without assumed collections, or provide a separate fixed-cost-only reserve with exclusions plainly stated. Do not quietly omit variable costs while calling the result full operating costs.

Maintain a month-by-month cash schedule for the selected reserve horizon, so annual insurance/permit charges prepaid at opening are not charged again during covered months. A monthly equivalent may be displayed as a budget metric, but distinguish it from the cash actually payable. Avoid double counting first/last rent, initial stock, and recurring replenishment. Zero reserve must produce zero reserve cash.

Contingency = selected rate × explicitly eligible uncertain startup line items. Default eligibility excludes refundable deposits, reserve cash, and fixed official fees. Explain the selected assumption; never present a conventional percentage as a measured fact. Do not apply contingency twice when already embedded in a quote.

Total funding = preopening cash + contingency + reserve cash. Calculate low and high under consistent documented configurations, not an arbitrary mix of incompatible bargains. This is a scenario range, not an absolute minimum, ceiling, guarantee, or statistical confidence interval. A midpoint, if shown, is not an expected value.

Use three separately displayed quantities: before-opening cash, monthly operating budget, total including chosen reserve. Do not subtract future sales without a separately built revenue model. Funding is not identical to accounting expense; deposits and capital equipment still require cash.

## 9. Output and UX requirements

Design a clean, professional small-business planning interface with warm neutral colors and restrained coffee/bakery accents. Prioritize accessible contrast, readable labels, mobile usability, keyboard interaction, and short explanations. No unnecessary mascot or decorative animation.

Results must include headline range, cash timing breakdown, low/high category bars, top cost drivers, a detailed calculation table, editable assumptions, and source links. Include methodology and sources views. Allow baseline vs alternative comparison with identical unchanged inputs and an explicit list of changed decisions. Offer scenario JSON and line-item CSV downloads. Include model/data version and estimate year in exports.

Support research-ready mode and demo mode. Demo mode must have a persistent banner, label exports, and never imply researched Seattle prices. Missing required inputs must block research-ready totals or clearly mark them incomplete. Do not silently treat missing buildout, taxes, wages, or additional rent as zero. Lack of optional cost applicability is different from missing evidence.

## 10. Implementation milestones

1. Inspect repository, create structure, dependencies, README, CSV templates, and data dictionary.
2. Audit supplied raw files; write an evidence-coverage report and prioritized research backlog. Obtain accessible public evidence when authorized, but do not claim blocked sources were downloaded.
3. Implement loaders/normalization and one hand-worked coffee-shop scenario using clearly labeled fixtures.
4. Build independent line-item engine, cash schedule, validation, and meaningful automated tests.
5. Add actual evidence-derived assumptions, equipment mappings, bakery production, and staffing presets.
6. Implement quiz, results, comparison, overrides, source views, and exports.
7. Run checks, inspect the app if browser tools are available, document limitations, and provide a reproducible handoff.

Complete engineering despite missing research using demo fixtures, but do not claim the research milestone passed until evidence is sufficient. Do not halt the entire build simply because one raw PDF has not been provided.

## 11. Required validation and acceptance checks

- A hand-calculated fixture must match engine outputs for line items and totals.
- Annual per-square-foot rent and monthly total rent normalize correctly.
- Increasing reserve by one month adds exactly that month's cash schedule outflow under unchanged inputs.
- Prepaid annual fees and opening rent are not duplicated in reserve months.
- Increased paid hours increase payroll when all other inputs remain unchanged.
- Turning off on-site baking removes only applicable production items and related labor/usage assumptions.
- Owner-operated presets reveal staffing coverage gaps instead of assuming free unlimited work.
- Every low endpoint is <= its high endpoint, and category totals reconcile with the headline.
- Missing required evidence cannot silently enter research-ready estimates as zero.
- Wage defaults respect the selected year/location floor; unsupported years are flagged.
- Mixed units, suppressed BLS values, duplicate listings, and invalid references are caught.
- Changing equipment tier selects relevant packages instead of multiplying every cost category.
- Demo sources and values never masquerade as observed evidence.
- Scenario exports reproduce results with their model version and assumptions.
- Sensitivity comparisons hold other inputs constant; monotonic behavior is asserted only where the formulas justify it.

Run pytest and the data-validation command; record actual results. Run a Streamlit smoke check and inspect key quiz/result states when tools permit. Document checks not run rather than claiming they passed.

## 12. Documentation and final handoff

README: purpose, scope, environment setup, data download checklist, file placement, commands, demo/research distinction, screenshots if actually captured, and limitations.

Methodology: formulas, units, evidence-selection rules, cash timing, uncertainty, staffing assumptions, inventory basis, tax treatment, and contingency eligibility.

Research backlog: category, missing evidence, consequence, interim assumption, priority, and action needed. Missing buildout and occupancy charges should rank highly when material.

Validation report: fixture results, automated checks, scenario comparisons, and unresolved issues. Do not invent validation against actual opened businesses unless real comparable budgets are obtained.

The initial user should be able to run:
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/validate_data.py
python -m pytest
python -m streamlit run app.py
```

Adapt commands to actual implementation and distinguish template validation from research-data completeness. No credentials should be required for the demo.

## 13. What the owner should gather before starting

Minimum useful materials: this brief, one published BLS metro/all-data wage download, and the applicable King County fee PDF. These are helpful but not prerequisites for scaffolding.

Next collect: selected-year Seattle wage fact sheet, a few relevant lease brochures, initial equipment product links, and any credible Seattle buildout examples. The agent should create collection templates for everything else. No coffee-sales/Kaggle dataset is required for this scope.

Preserve original filenames and put files in the raw folders above. Add source URLs and download dates; a local PDF without provenance is insufficient. Do not spend time downloading large unrelated sales datasets before the cost model works.
