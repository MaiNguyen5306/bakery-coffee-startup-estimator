# Raw evidence
Preserve owner-supplied originals. Do not edit workbooks/PDFs. Raw files are ignored by Git to avoid redistributing material before reuse review. Place BLS metro workbooks under wages/, fee PDFs under permits/, and permitted brochures in rent/. Record source URL, effective date and actual download date in sources.csv; never infer the download date from file modification time.

Run `python scripts/build_assumptions.py` to inspect workbook columns, filter Seattle role benchmarks, extract PDF text and generate SHA256 inventory. Outputs are interim review materials, not automatically approved assumptions. Unknown/suppressed numeric data stays missing.
