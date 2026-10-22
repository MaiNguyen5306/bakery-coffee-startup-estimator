# Data contracts
Unknown numeric cells remain blank. Currency is USD. IDs are unique within each file; evidence_ids uses semicolon-separated observation IDs. Dates use ISO YYYY-MM-DD. A blank selector is a wildcard only in assumption tables; observations with unknown selectors do not establish applicability.

## sources
`source_id,publisher,title,url,document_date,accessed_date,local_path,geography,reuse_notes,status`

## observations
`observation_id,source_id,category,item,specification,city,neighborhood,business_type,condition,quality_tier,price,currency,unit,price_period,tax_included,shipping_included,installation_included,effective_start,effective_end,observed_date,notes`

## rent_listings
`listing_id,source_id,address_or_identifier,neighborhood,sqft,base_rent_quote,quote_unit,lease_type,additional_rent_quote,additional_rent_unit,food_service_status,space_condition,observed_date,notes`

## assumptions
`assumption_id,category,item,city,estimate_year,business_type,condition,quality_tier,low,high,unit,calculation_basis,evidence_ids,evidence_status,confidence,effective_start,effective_end,notes`

Enums: evidence_status = observed/derived/assumed/demo; confidence = low/medium/high (editorial, not probability); business_type = coffee/bakery; condition = existing/partial/shell; quality_tier = standard/premium; source status = verified/pending/demo. Boolean inclusion flags = true/false/blank (unknown). quote_unit = USD/sqft/year, USD/sqft/month, USD/month. lease_type = NNN/gross/unknown. Numeric costs must be finite, nonnegative; assumption low <= high. effective dates bound applicability. Research assumptions must carry evidence and derivation notes. Demo assumptions are isolated in data/demo.
