# Revenue evidence contracts
Blank CSVs in data/templates/revenue are schemas, not data. The requested template directory was absent at inspection and was created to match the brief. Observations live under data/processed/revenue; full copyrighted originals and extracted text stay local/ignored. Unknown numbers and effective dates are blank, never zero or inferred from file modification time. USD only. Source IDs resolve within the revenue source register; this register uses revenue-specific channel/page/hash fields rather than pretending it is the same schema as the cost register.

| Table | Key | Important fields / interpretation |
|---|---|---|
| sources | source_id | publisher, original URL/path, page reference, snapshot/access/effective dates, geography, channel, status, SHA256, limitations |
| menu_prices | menu_price_id | source_id, item/category/size, price USD/item, store location, transaction channel, tax basis, observation/effective dates, PDF page, evidence status |
| supplier_prices | supplier_price_id | source_id, pack quantity/unit/price, tax and delivery inclusion, observation date/status |
| recipes | recipe_id | supplier_price_id, ingredient quantity/unit, sellable yield, input loss fraction, packaging cost per sellable yield, status |
| payment_fees | payment_fee_id | source_id, processor, plan, US market, channel, percentage fraction, fixed USD/transaction, subscription USD/month, dates, conditions |
| order_baskets | basket_id | scenario_id, semicolon-separated menu_price_ids and quantities, explicit basket sales/product costs, share fraction, status |
| revenue_assumptions | assumption_id | scenario_id, item/value/unit, semicolon-separated evidence IDs, evidence status and notes |

Evidence statuses: observed / derived / assumed / demo. Menu `website_menu_unknown_checkout` intentionally does not mean in-store, pickup or delivery. Tax basis is `unknown` until explicitly established. Observed menu dates are snapshot dates, not verified price-effective periods. Argentum address is specific to Pioneer Square 98104; Macrina's supplied chain cafe menu does not identify a branch. These records confer no ZIP-based costing, neighborhood conversion factor or Seattle-wide representativeness.

Recipe units: g/kg/oz/lb mass, ml/l volume, each count. Cross-dimension conversions fail. Fractions use 0–1; input loss must be below 1. Recipe/pack numeric fields are required when a row is present. Supplier/recipe tables currently contain no rows. Basket quantities must be positive, references resolve and scenario shares sum to 1.

`extract_revenue_evidence.py` checks the selected PDF page text and visible print date, records hashes and regenerates eight selected menu facts plus six separately verified official web processing rates. Only small factual extracts are published, not full menu text. Processing-rate records are curated from the official page observed on 2026-10-22; rerunning the script replays that dated capture rather than claiming a fresh web fetch. The raw PDF contains $0/$49/$149 monthly plan prices, but its captured comparison table omits extractable processing rates. Pinoyshki's single-page viewer snapshot and inspected embedded images contain no usable price list.
