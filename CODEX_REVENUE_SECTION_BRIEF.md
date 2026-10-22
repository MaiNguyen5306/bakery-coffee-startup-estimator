# Codex implementation brief: Home → Cost / Revenue

Owner: MaiNguyen5306. Prepared October 22, 2026.

## Request and existing project

Extend the existing bakery-coffee-startup-estimator repository. The owner already has a draft. Inspect the code, README, existing build brief, dependencies, AGENTS.md, data, and current UI before editing. Preserve working features and adapt to the actual stack. Do not replace an established implementation with Streamlit merely because the original brief recommended it. Implement this request rather than stopping at a plan. Do not push or deploy unless separately requested.

The original startup-cost brief remains relevant for Cost. This brief adds Revenue and a main landing page. Revenue is a scenario-planning tool: it calculates sales from assumptions or orders required for a target. It does not establish likely customer demand. Do not present synthetic transaction datasets or unrelated stores' sales as observed Seattle shop performance.

## Navigation and main page

Create a main page introducing a Bakery & Coffee Shop Business Planner, with two clear cards:
- Cost: How much money do I need to open and operate?
- Revenue: How many orders would I need to reach my sales goal?

Use Home / Cost / Revenue navigation with persistent business scenario state. Match the current site's visual language and improve accessibility where needed. Preserve the cost estimator. Cost and Revenue should share business type, production method, area, opening schedule, staffing assumptions, and scenario identity where applicable. Show scenario changes and require an explicit refresh/recalculation when linked assumptions change; never show stale linked results without a notice.

Initially support Seattle as a city-level planning location. Audit actual cost inputs and label citywide, metro, neighborhood, unknown, and demo assumptions separately. Do not claim ZIP-code precision or Seattle-wide representativeness from a few menus. A ZIP code alone must not trigger invented rent, conversion, or sales multipliers.

## Revenue functions: implement in order

1. Target sales → required orders per day and hour.
2. Expected orders → monthly sales scenario.
3. Link relevant recurring costs → operating break-even and simplified operating surplus.
4. Compare baseline and alternative assumptions; capacity and peak-hour checks.

Keep target revenue and target operating surplus separate. Sales exclude sales tax and tips and are net of modeled discounts/refunds. Do not label sales as take-home pay. MVP target is monthly sales, not personal income. Operating results exclude income tax, debt service, depreciation, and owner draws unless explicitly modeled; label that scope. Required order counts are transactions, not unique customers or people walking past.

## Data package and required handling

The accompanying ZIP contains blank CSV templates, this brief, and a download checklist. They are schemas, not researched datasets. Empty tables must not be treated as zero costs or evidence of zero demand.

Optional raw reference PDFs should be saved under data/raw/revenue/menus, payments, suppliers, and methodology. Inspect what is actually present. References are starting sources, not a claim that numeric values have been extracted or validated.

Source entry points:
- Macrina cafe menu: https://macrinabakery.com/cafe-menu
- Argentum menu: https://argentumbakery.com/menu
- Pinoyshki menu: https://pinoyshki.com/menu/
- Square pricing: https://squareup.com/us/en/pricing
- SBA break-even method: https://legacy.sba.gov/business-guide/plan-your-business/calculate-your-startup-costs/break-even-point

For the first version, the owner should save two or three local menu pages and the payment-pricing page as PDFs, using their browser's Print → Save as PDF. These are price snapshots, not downloadable sales histories. Menus without visible comparable prices do not qualify as price evidence. Do not bypass blocks; use manual entry and a source backlog if needed. Do not copy entire copyrighted menus into public documentation. Keep raw downloads local unless redistribution is permitted.

For menu observations record store location, channel (in-store/pickup/delivery), size, item category, price, tax basis, access date, source, and limitations. Delivery prices may differ from in-store prices; do not pool them silently. Product prices alone do not reveal average order value: order quantities and purchase mix must be separate editable assumptions. A drink plus pastry bundle should not be treated as one item or inferred to be the typical purchase without evidence.

Ingredient/supplier prices are needed for product cost and break-even, but not for the target-orders calculator. Use real supplier listings or user-supplied quotes when available. Do not require paid wholesale accounts to start. Capture unit sizes, yield, delivery/tax inclusion, recipe quantities, and packaging. Label illustrative cost ratios when full recipes are unavailable. Missing evidence should not prevent the basic sales calculator from working.

Template files:
- sources.csv: provenance register.
- menu_prices.csv: comparable observed menu prices.
- supplier_prices.csv: ingredient and packaging price observations.
- recipes.csv: quantities needed for one sellable product, linked to supplier records.
- payment_fees.csv: processor/plan/channel-specific fees.
- order_baskets.csv: scenario purchase baskets and shares.
- revenue_assumptions.csv: explicitly entered assumptions and evidence status.

Retain existing project conventions where equivalent schemas already exist. Convert templates into the project's normalized format instead of maintaining contradictory duplicate data. Write a data dictionary and validators. Stable IDs must resolve across files, currencies and units must be compatible, and source/effective dates must be preserved. Distinguish observed, derived, assumed, and demo values. Confidence labels are qualitative assessments, not probabilities.

## Inputs and basic formulas

Basic inputs: monthly sales target OR expected daily orders, average order value (AOV), exact open days per month, open hours per day. All editable. Offer a consistent weekly schedule helper, but do not silently use 30 calendar days for every scenario. Clearly state whether daily order inputs are constant across open days.

Advanced mode: purchase baskets, card/cash shares, payment channel, processor plan, variable costs, fixed costs, desired simplified operating surplus, peak-hour share, peak hours per day, and service capacity assumptions.

N = daily orders × open days.
Sales = N × AOV.
Required monthly orders = target sales / AOV.
Average required orders/day = target sales / (AOV × open days).
Average required orders/hour = target sales / (AOV × open days × open hours).

Keep unrounded values for financial calculations. Show ceil(required monthly orders) as the minimum whole-month transaction requirement; show ceil(target/(AOV×days)) only as an optional constant daily goal. Label it clearly because repeating an independently rounded hourly target can overshoot. Reject zero/negative AOV, days, or hours. Zero sales target is valid and produces zero required orders.

Optional baskets: each basket contains a transparent list of item quantities or an explicitly entered basket value and cost. Shares sum to 1. AOV = sum(basket share × basket sales value). Variable product cost/order = sum(basket share × basket product cost). Do not sum menu prices then call the result AOV without a purchase-mix model. Separate observed prices from hypothesized basket shares.

For recipe cost, convert supplier pack prices into compatible ingredient units and divide batch cost by sellable yield. Waste must have an explicit basis; if using an input-loss fraction w, effective input cost = base input cost/(1-w), with 0<=w<1. Do not count the same loss both in batch yield and again as waste. Packaging is per applicable sold item or order as defined, never automatically both. Purchased pastries use purchase cost and waste, not fabricated baking recipes.

## Payment fees

Use actual plan, US market, effective date, and payment channel. Store percentage and fixed fee per transaction separately, with applicable conditions and exclusions. Fixed monthly POS fees belong among fixed costs, not in per-order fees. Payment fees may apply to collected tax/tips even though those are excluded from sales; document the modeled fee base and support an editable uplift or explicit amounts rather than hiding the issue.

For a simple single-card-channel scenario with card share s, fee fraction p, fixed fee f, and modeled fee base equal to net sales:
Fees = s × (Sales × p + N × f).
If channels have different average baskets, calculate by channel; do not assume transaction share equals revenue share without disclosure. Multiple channels require shares that sum consistently. Do not hard-code unverified current rates. Permit user-entered rates and demo rates with labels.

## Cost integration and break-even

Inspect the existing monthly cost model and explicitly classify fixed, per-order, sales-percentage, and stepped costs. Preserve line-item IDs. Ingredients, packaging, and processing already included elsewhere must not be counted again. Link base payroll as a cost within a stated capacity range; additional staffing is a stepped cost. Startup deposits, reserve funding, and equipment purchases are not recurring operating expenses. Annual expenses may be monthly allocated for operating break-even, but label the difference from cash timing in Cost.

Let F = monthly fixed operating costs.
Let v = variable cost/order including applicable fixed transaction fees.
Let r = sales-dependent variable-cost fraction not already included in v.
Contribution/order = AOV × (1-r) - v.
Break-even orders/month = F / contribution/order.
Break-even sales = break-even orders/month × AOV.
Simplified operating surplus = Sales - modeled variable costs - F.
Orders for target surplus P = (F+P)/contribution/order within the stated staffing/capacity range.

Do not divide by a nonpositive contribution; report no finite break-even under those assumptions and explain which costs exceed sales contribution. If costs are incomplete, mark break-even incomplete rather than showing an apparently validated result. Directly entered F is permitted but labeled as a user assumption. If target exceeds capacity, show that staffing/equipment must be reassessed; do not extrapolate a constant cost structure indefinitely. Do not automatically reduce startup reserve based on hypothetical sales. Keep financing cash schedules and operating metrics separate.

## Capacity and optional footfall

Average orders/hour is not peak demand. Offer optional peak share q of daily orders in h peak hours: peak required rate = daily orders × q/h. Validate 0<=q<=1 and 0<h<=open hours; also show the implied nonpeak rate when nonpeak hours exist. Compare to a user-entered effective shop capacity or explicit station model. Do not multiply employee count by a guessed individual rate as if work were perfectly parallel. Capacity is an assumption unless measured and must not be called actual demand.

Footfall conversion is optional and advanced. Required passing foot traffic = required walk-in orders / assumed conversion fraction, only after separating destination, online, delivery, and repeat-order channels. It is hypothetical arithmetic. Census residents/workers and trail counts are not measured storefront passersby. Do not download unrelated transportation or population files just to make this feature appear validated. Real location-specific observation is future research.

## Output design

Revenue screen has two main modes: Target sales and Expected orders, plus a linked break-even panel when data is sufficient. Show assumptions beside headline figures. Explain sales vs operating surplus in plain language. Show a small sensitivity grid for AOV and orders, and baseline/alternative comparison with changed inputs identified. No unsupported probability-of-success claims.

Provide source detail links, evidence dates, a persistent demo label when applicable, scenario JSON, and calculation CSV exports with model version and data version. Keep internal implementation details out of the normal quiz. Add a short methodology view and list missing evidence. Export assumptions and formulas clearly enough for another analyst to reproduce results.

## Implementation and validation

Separate pure calculation functions from UI. Add loaders/validators, scenario models, cost-to-revenue adapter, calculation functions, views, and targeted tests using the existing stack. Do not rewrite the whole cost engine without necessity.

Hand fixture (illustrative, not researched): AOV=$10, 26 days, 8 hours/day, target=$30,000. Expect 3,000 orders/month, 115.384615 orders/day, 14.423077 orders/hour, and optional 116-order constant daily goal. With F=$12,000 and total variable cost/order=$4 (all modeled variable fees included), contribution=$6, break-even=2,000 orders and $20,000 monthly sales. At 3,000 orders operating surplus=$6,000. Zero reserve and startup amounts do not change these operating figures.

Tests must cover fixture reconciliation, input boundaries, zero target, invalid days/hours, basket shares and quantities, weighted AOV, fee basis/channel mix, nonpositive contribution, duplicate cost prevention, ingredient unit conversion, waste treatment, stale linked scenarios, missing data, and export reproducibility. Verify changes to prices, days, or order counts affect outputs logically while holding other inputs constant. Validate rounding separately from calculations. Exercise Home → Cost → Revenue navigation and persistence. Record actual checks run; do not claim browser verification if unavailable.

## Definition of done

- Main page offers Cost and Revenue with functional navigation.
- Existing Cost features still work and share scenario assumptions predictably.
- Target-sales and expected-orders modes work without external datasets.
- Break-even works with complete cost assumptions and exposes missing inputs.
- Research-derived prices are distinguishable from user/demo assumptions.
- Data provenance, methodology, exclusions, and tests are documented.
- README explains raw-file locations, local run commands, data refresh, and deployment status.
- Final handoff lists changed files, test results, unresolved data gaps, and next steps. Do not claim the owner's local draft was audited before actually inspecting it.
