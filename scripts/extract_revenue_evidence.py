"""Rebuild selected factual observations; full copyrighted text remains local interim only."""
from pathlib import Path
import csv, hashlib, re
from pypdf import PdfReader
ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'data/processed/revenue'

def save(name, records):
    fields=(ROOT/f'data/templates/revenue/{name}.csv').read_text().strip().split(',')
    with (DEST/f'{name}.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields,lineterminator="\n");w.writeheader();w.writerows(records)

sources=[];menu=[]
files=[('macrina','Macrina Bakery','https://macrinabakery.com/cafe-menu','menus/Macrina Bakery - Seattle\'s favorite bakery since 1993_.pdf','Seattle cafe menu; individual branch unspecified'),('argentum','Argentum Coffee & Bakery','https://argentumbakery.com/menu','menus/Menu _ Argentine Food & Bakery in Pioneer Square, Seattle _ Argentum Coffee & Bakery.pdf','221 1st Ave S, Seattle, WA 98104; Pioneer Square'),('pinoyshki','Pinoyshki Bakery','https://pinoyshki.com/menu/','menus/The Menu Book _ Pinoyshki Bakery, Seattle.pdf','Seattle; no branch/address established by snapshot'),('square_pdf','Square','https://squareup.com/us/en/pricing','payments/Square Processing Fees, Plans, and Software Pricing _ Square.pdf','US')]
for key,publisher,url,filename,geo in files:
    p=ROOT/'data/raw/revenue'/filename
    reader=PdfReader(p);texts=[page.extract_text() or '' for page in reader.pages]
    out=ROOT/'data/interim/revenue';out.mkdir(parents=True,exist_ok=True)
    for i,t in enumerate(texts,1): (out/f'{key}-page-{i}.txt').write_text(t)
    assert any('10/22/26' in t for t in texts), 'Review snapshot date manually'
    sources.append(dict(source_id=key,publisher=publisher,title=p.stem,url=url,local_path=str(p.relative_to(ROOT)),page_reference=f'1–{len(texts)}',snapshot_date='2026-10-22',accessed_date='2026-10-22',geography=geo,channel='website; transaction channel unconfirmed' if key!='square_pdf' else 'US plan subscription',status='observed_snapshot',sha256=hashlib.sha256(p.read_bytes()).hexdigest(),limitations='Effective price dates and tax basis not stated; website prices do not establish in-store or delivery checkout prices. No demand or purchase mix evidence.' if key not in {'pinoyshki','square_pdf'} else 'No comparable numeric menu prices visible in supplied viewer snapshot.' if key=='pinoyshki' else 'Subscription prices visible; processing-rate table not captured as extractable text. Rates come from separately verified official web page.'))
    selected={'macrina':[(8,'Drip', 'drink','12 oz',4.2),(9,'Latte','drink','12 oz',5.7),(9,'Cold brew','drink','12 oz',6.15),(4,'Bagel with cream cheese','food','one bagel',5.3)],'argentum':[(2,'Cordobés alfajor','pastry','one item',4.5),(13,'Espresso','drink','two shots',3.75),(14,'Cappuccino','drink','unspecified',5.5),(15,'Latte','drink','unspecified',5.75)]}.get(key,[])
    for i,(page,item,category,size,price) in enumerate(selected,1):
        assert str(price) in texts[page-1] or f'{price:.2f}' in texts[page-1],(key,page,price)
        menu.append(dict(menu_price_id=f'{key}_{i}',source_id=key,item=item,category=category,size=size,price=price,currency='USD',unit='USD/item',store_location=geo,channel='website_menu_unknown_checkout',tax_basis='unknown',observed_date='2026-10-22',page_reference=str(page),evidence_status='observed',limitations='Not Seattle-wide evidence or AOV. Confirm checkout channel/tax and availability.'+(' Bar section marked coming soon; availability not confirmed.' if key=='argentum' and category=='drink' else '')))
sources.append(dict(source_id='square_web_20261022',publisher='Square',title='US pricing: plan comparison / Fees / Processing fees',url='https://squareup.com/us/en/pricing',page_reference='Fees: Tap dip swipe / Online; plan columns Free Plus Premium',accessed_date='2026-10-22',geography='United States',channel='in_person and online separately',status='observed_web',limitations='Effective start/end not stated. Standard domestic card rates, subject to plan, custom pricing and additional fees. Not claimed as extracted from PDF.'))
save('sources',sources);save('menu_prices',menu)
fees=[]
for plan,p,online,sub in [('Free',.026,.033,0),('Plus',.025,.029,49),('Premium',.024,.029,149)]:
    for channel,rate,fixed in [('in_person',p,.15),('online',online,.30)]:
        fees.append(dict(payment_fee_id=f'square_{plan.lower()}_{channel}',source_id='square_web_20261022',processor='Square',plan=plan,market='US',channel=channel,percentage=rate,fixed_per_transaction=fixed,monthly_subscription=sub,observed_date='2026-10-22',evidence_status='observed',conditions='Standard domestic card rate; exclude foreign card surcharge, custom volume pricing, Afterpay, API and manual entry. Subscription per location; add once to fixed costs, never per transaction. Rate dates not stated.'))
save('payment_fees',fees)
print(f'Inspected {len(files)} supplied PDFs; saved {len(menu)} menu prices and {len(fees)} separately verified web payment rates. No supplier observations or purchase mix fabricated.')
