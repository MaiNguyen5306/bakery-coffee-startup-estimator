"""Reproducible raw-file inspection. Does not infer provenance from filenames."""
from pathlib import Path
import hashlib
import pandas as pd
from pypdf import PdfReader
from .loaders import ROOT
from .normalize import number

ROLES = {"51-3011", "35-2021", "35-3023", "35-1012", "11-9051"}

def inspect_raw():
    inventory=[]
    for path in sorted((ROOT/"data/raw").rglob("*")):
        if path.suffix.lower() not in {".pdf",".xlsx",".zip"}: continue
        inventory.append({"path":str(path.relative_to(ROOT)),"bytes":path.stat().st_size,"sha256":hashlib.sha256(path.read_bytes()).hexdigest(),"provenance":"owner supplied; download date and source confirmation needed"})
    pd.DataFrame(inventory).to_csv(ROOT/"data/interim/raw_inventory.csv",index=False)
    for path in (ROOT/"data/raw").rglob("*.pdf"):
        text="\n".join(page.extract_text() or "" for page in PdfReader(path).pages)
        (ROOT/"data/interim"/(path.stem+".txt")).write_text(text)
    for path in (ROOT/"data/raw/wages").rglob("MSA*.xlsx"):
        frame=pd.read_excel(path)
        (ROOT/"data/interim/bls_columns.txt").write_text("\n".join(map(str,frame.columns)))
        required={"AREA_TITLE","OCC_CODE","OCC_TITLE","H_MEDIAN"}
        if not required.issubset(frame.columns): raise ValueError(f"Unexpected BLS schema: {list(frame.columns)}")
        selected=frame[frame.AREA_TITLE.astype(str).str.contains("Seattle",case=False) & frame.OCC_CODE.isin(ROLES)].copy()
        if selected.empty: raise ValueError("No matching Seattle role records")
        # Suppression stays missing; do not replace it with zero.
        def parse(v):
            try: return number(v)
            except ValueError: return None
        selected["hourly_median_numeric"]=selected.H_MEDIAN.map(parse)
        selected.to_csv(ROOT/"data/interim/seattle_wages.csv",index=False)
    return inventory
