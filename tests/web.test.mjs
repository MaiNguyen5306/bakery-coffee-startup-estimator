import test from 'node:test';
import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { mkdirSync } from 'node:fs';
import { pathToFileURL } from 'node:url';
import { build } from 'esbuild';
import { Window } from 'happy-dom';
import { act } from 'react';

const python='.venv/bin/python';
function py(code,input=''){return JSON.parse(execFileSync(python,['-c',code],{input,encoding:'utf8'}));}
const bootstrap=py("from api.estimate import handler; import json; h=handler.__new__(handler); h.reply=lambda status,data: print(json.dumps(data)); h.do_GET()");
const window=new Window({url:'http://localhost:5173'});
for(const key of ['window','document','HTMLElement','HTMLInputElement','Event','MouseEvent','File','Blob','MutationObserver'])globalThis[key]=key==='window'?window:window[key];
Object.defineProperty(globalThis,'navigator',{value:window.navigator,configurable:true});
globalThis.IS_REACT_ACT_ENVIRONMENT=true;
globalThis.fetch=async(_url,options)=>{
 try {const data=options?.body?py("import sys,json; from api.estimate import execute; print(json.dumps(execute(json.load(sys.stdin))))",options.body):bootstrap;return {ok:true,json:async()=>data};}
 catch(e){return {ok:false,json:async()=>({error:'Scenario invalid or research incomplete'})};}
};
mkdirSync('node_modules/.cache',{recursive:true});
await build({entryPoints:['web/main.jsx'],bundle:true,platform:'node',format:'esm',packages:'external',loader:{'.css':'empty'},outfile:'node_modules/.cache/opening-ui-test.mjs'});
document.body.innerHTML='<div id="root"></div>';
await act(async()=>{await import(pathToFileURL(process.cwd()+'/node_modules/.cache/opening-ui-test.mjs').href);});
const settle=()=>act(async()=>{await new Promise(r=>setTimeout(r,400))});
const click=async el=>act(async()=>{assert.ok(el,'Missing button');el.click();});
const buttons=(container,text)=>[...container.querySelectorAll('button')].find(b=>b.textContent.includes(text));
const nav=()=>document.querySelector('nav[aria-label="Main navigation"]');
const cost=()=>document.querySelector('main>.home-cards')?.nextElementSibling?.nextElementSibling;
const inputByLabel=(container,text)=>[...container.querySelectorAll('label')].find(l=>l.textContent.includes(text))?.querySelector('input,select');
async function input(el,value){await act(async()=>{assert.ok(el,'Missing field');const proto=el.tagName==='SELECT'?window.HTMLSelectElement.prototype:window.HTMLInputElement.prototype;Object.getOwnPropertyDescriptor(proto,'value').set.call(el,value);el.dispatchEvent(new Event(el.tagName==='SELECT'?'change':'input',{bubbles:true}));});}

test('Home / Cost / Revenue state, stale notices, calculations and comparison',async()=>{
 await settle();
 assert.match(document.querySelector('.intro').textContent,/Business Planner/);
 assert.equal(document.querySelectorAll('.home-card').length,2);
 await click(buttons(nav(),'Cost'));await settle();
 const sqft=inputByLabel(document,'Space size');assert.equal(sqft.value,'1000');
 await input(sqft,'1400');await settle();
 assert.match(document.querySelector('.cost-workspace .funding-number').textContent,/\$/);
 await click(buttons(nav(),'Revenue'));
 const revenue=document.querySelector('.revenue-view');
 assert.match(revenue.textContent,/1400 sqft/);
 await settle();
 assert.equal(buttons(revenue,'Refresh & recalculate'),undefined);
 assert.match(revenue.querySelector('.funding-number').textContent,/115.38/);
 assert.match(revenue.textContent,/Break-even incomplete/);
 const revenueTabs=revenue.querySelector('nav[aria-label="Revenue views"]');
 assert.ok(revenueTabs);
 assert.equal(revenue.querySelector('.funding-card').parentElement.hidden,false);
 await click(buttons(revenueTabs,'Break-even & capacity'));
 assert.equal(revenue.querySelector('.funding-card').parentElement.hidden,true);
 assert.equal([...revenue.querySelectorAll('h2')].find(h=>h.textContent==='Break-even incomplete').parentElement.parentElement.hidden,false);
 await click(buttons(revenueTabs,'Method & sources'));
 assert.equal([...revenue.querySelectorAll('h2')].find(h=>h.textContent==='Local menu snapshots').parentElement.parentElement.hidden,false);
 await click(buttons(revenueTabs,'Compare'));
 await click(buttons(revenue,'Save current Revenue baseline'));
 await click(buttons(revenueTabs,'Overview'));
 await input(inputByLabel(revenue,'Target monthly net sales'),'60000');
 assert.match(revenue.textContent,/Previous figures are hidden/);
 assert.equal(revenue.querySelector('.funding-number'),null);
 await settle();
 assert.match(revenue.querySelector('.funding-number').textContent,/230.77/);
 assert.match(revenue.textContent,/30000 → 60000/);
 await click(buttons(nav(),'Cost'));await settle();
 assert.equal(inputByLabel(document,'Space size').value,'1400');
 await input(inputByLabel(document,'Space size'),'1500');await settle();
 await click(buttons(nav(),'Revenue'));
 await settle();
 assert.match(revenue.querySelector('.funding-number').textContent,/230.77/);
 assert.equal(inputByLabel(revenue,'Target monthly net sales').value,'60000');
 await click(buttons(nav(),'Home'));
 assert.equal(document.querySelector('.intro').hidden,false);
 assert.equal(document.querySelector('.home-cards')!==null,true);
 await click(buttons(nav(),'Revenue'));
 await input(inputByLabel(revenue,'Calculator mode'),'expected');
 await input(inputByLabel(revenue,'Fixed cost source'),'manual');
 const completeness=[...revenue.querySelectorAll('label')].find(l=>l.textContent.includes('I have included product cost')).querySelector('input');
 await click(completeness);
 await settle();
 assert.match(revenue.querySelector('.funding-number').textContent,/29,900/);
 assert.match(revenue.textContent,/Illustrative operating break-even/);
 await input(inputByLabel(revenue,'Expected orders / open day'),'0');
 await settle();
 assert.equal(revenue.querySelector('.funding-number').textContent,'$0');
});

test('Back returns from either tool to Home; Forward and sibling navigation preserve inputs',async()=>{
 await click(buttons(nav(),'Home'));
 await click(buttons(nav(),'Cost'));
 assert.equal(window.location.hash,'#/cost');
 const size=inputByLabel(document,'Space size').value;
 // happy-dom does not implement history traversal. Dispatch popstate after
 // moving the URL to simulate the browser's Back/Forward event contract.
 const pop=async(hash)=>act(async()=>{
  window.history.replaceState({openingDay:true},'',hash);
  window.dispatchEvent(new window.PopStateEvent('popstate'));
 });
 await pop('#/');
 assert.equal(document.querySelector('.intro').hidden,false);
 await pop('#/cost');
 assert.equal(document.querySelector('.intro').hidden,true);
 assert.equal(inputByLabel(document,'Space size').value,size);
 const entries=window.history.length;
 await click(buttons(nav(),'Revenue'));
 assert.equal(window.location.hash,'#/revenue');
 assert.equal(window.history.length,entries,'Switching sibling tools keeps Home immediately behind them');
 await pop('#/');
 assert.equal(document.querySelector('.intro').hidden,false);
 await pop('#/revenue');
 assert.equal(document.querySelector('.revenue-view').parentElement.hidden,false);
 assert.equal(inputByLabel(document.querySelector('.revenue-view'),'Expected orders / open day').value,'0');
 await click(document.querySelector('a[aria-label="Opening Day home"]'));
 assert.equal(window.location.hash,'#/');
 assert.equal(document.querySelector('.intro').hidden,false);
});

test('Staff-led defaults, owner overrides and supervisor team totals are visible',async()=>{
 await click(buttons(nav(),'Cost'));await settle();
 const filters=document.querySelector('.cost-filters');
 await input(inputByLabel(filters,'Number of staff'),'3');await settle();
 await input(inputByLabel(filters,'Staffing approach'),'staffed');await settle();
 assert.equal(inputByLabel(filters,'Your service hours / week').value,'0');
 assert.equal(inputByLabel(filters,'Total employee hours / week').value,'120');
 assert.equal(inputByLabel(filters,'Total employee hours / week').readOnly,true);
 assert.match(document.querySelector('.staffing-summary').textContent,/Paid working supervisors60/);
 const summary=()=>document.querySelector('.staffing-summary');
 assert.match(summary().textContent,/All paid employee hours120/);
 assert.match(summary().textContent,/Paid working supervisors60/);
 assert.match(summary().textContent,/not counted twice/);
 await input(inputByLabel(filters,'Your service hours / week'),'40');await settle();
 assert.match(document.querySelector('.staffing-summary').textContent,/Paid working supervisors20/);
 assert.match(summary().textContent,/All paid employee hours120/);
 assert.equal(inputByLabel(filters,'Total employee hours / week').value,'120');
 await input(inputByLabel(filters,'Staffing approach'),'owner_operated');await settle();
 assert.equal(inputByLabel(filters,'Your service hours / week').value,'40');
 assert.match(document.querySelector('.staffing-summary').textContent,/Paid working supervisors0/);
});

test('Staff count and employment type determine paid hours independently of owner',async()=>{
 await click(buttons(nav(),'Cost'));await settle();
 const filters=document.querySelector('.cost-filters');
 await input(inputByLabel(filters,'Number of staff'),'2');
 await input(inputByLabel(filters,'Employment type'),'part_time');await settle();
 assert.equal(inputByLabel(filters,'Total employee hours / week').value,'40');
 await input(inputByLabel(filters,'Your service hours / week'),'0');await settle();
 assert.equal(inputByLabel(filters,'Total employee hours / week').value,'40');
 await input(inputByLabel(filters,'Number of staff'),'3');await settle();
 assert.equal(inputByLabel(filters,'Total employee hours / week').value,'60');
 await input(inputByLabel(filters,'Employment type'),'full_time');await settle();
 assert.equal(inputByLabel(filters,'Total employee hours / week').value,'120');
});

test('Footer notice opens sources for the current tool without clearing inputs',async()=>{
 assert.equal(document.querySelector('.demo-banner'),null);
 const footer=document.querySelector('footer');
 assert.match(footer.textContent,/Some estimates use illustrative assumptions while research is ongoing/);
 await click(buttons(nav(),'Cost'));await settle();
 const count=inputByLabel(document.querySelector('.cost-filters'),'Number of staff').value;
 await click(buttons(footer,'View sources and assumptions'));
 assert.equal(document.querySelector('nav[aria-label="Estimate views"] button[aria-current="page"]').textContent,'Method & sources');
 assert.equal(inputByLabel(document.querySelector('.cost-filters'),'Number of staff').value,count);
 await click(buttons(nav(),'Revenue'));
 await click(buttons(footer,'View sources and assumptions'));
 assert.equal(document.querySelector('nav[aria-label="Revenue views"] button[aria-current="page"]').textContent,'Method & sources');
 await click(buttons(nav(),'Home'));
 await click(buttons(footer,'View sources and assumptions'));
 assert.equal(window.location.hash,'#/cost');
 assert.equal(document.querySelector('nav[aria-label="Estimate views"] button[aria-current="page"]').textContent,'Method & sources');
});

test('Automatic Revenue updates ignore superseded responses',async()=>{
 await click(buttons(nav(),'Revenue'));
 const revenue=document.querySelector('.revenue-view');
 await click(buttons(revenue.querySelector('nav[aria-label="Revenue views"]'),'Overview'));
 await input(inputByLabel(revenue,'Calculator mode'),'target');
 await input(inputByLabel(revenue,'Average order value'),'20');await settle();
 const originalFetch=globalThis.fetch;
 let releaseOld;
 globalThis.fetch=async(url,options)=>{
  const payload=options?.body?JSON.parse(options.body):null;
  const response=await originalFetch(url,options);
  if(payload?.action==='revenue'&&payload.revenue.target_sales===12345){
   return new Promise(resolve=>{releaseOld=()=>resolve(response)});
  }
  return response;
 };
 try {
  await input(inputByLabel(revenue,'Target monthly net sales'),'12345');await settle();
  assert.equal(typeof releaseOld,'function');
  assert.equal(revenue.querySelector('.funding-number'),null);
  assert.equal(buttons(revenue,'Download Revenue JSON'),undefined);
  await input(inputByLabel(revenue,'Target monthly net sales'),'23456');await settle();
  assert.match(revenue.querySelector('.funding-number').textContent,/45.11/);
  await act(async()=>releaseOld());
  assert.match(revenue.querySelector('.funding-number').textContent,/45.11/);
 } finally {globalThis.fetch=originalFetch;}
});
