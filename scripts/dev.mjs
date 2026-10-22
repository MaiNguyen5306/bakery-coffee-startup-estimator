import { spawn } from 'node:child_process';
import { existsSync, watch } from 'node:fs';
const python = existsSync('.venv/bin/python') ? '.venv/bin/python' : 'python3';
function port(flag,fallback){const i=process.argv.indexOf(flag);const n=i>=0?Number(process.argv[i+1]):fallback;if(!Number.isInteger(n)||n<1024||n>65535)throw Error(`Invalid ${flag}`);return n;}
const apiPort=port('--api-port',8000),webPort=port('--port',5173);
let stopping=false,api,reloadTimer;
const watchers=[];
const children=new Set();
function start(command,args,options={}){
 const child=spawn(command,args,{stdio:'inherit',...options});children.add(child);
 child.on('error',e=>{console.error(e.message);stop(1)});
 child.on('exit',code=>{children.delete(child);if(!child.restarting&&!stopping)stop(code??1)});
 return child;
}
function startAPI(){api=start(python,['scripts/serve_api.py','--port',String(apiPort)]);}
function stop(code=0){if(stopping)return;stopping=true;clearTimeout(reloadTimer);watchers.forEach(w=>w.close());children.forEach(p=>p.kill('SIGTERM'));process.exitCode=code;}
startAPI();
start(process.execPath,['node_modules/vite/bin/vite.js','--host','127.0.0.1','--port',String(webPort),'--strictPort'],{env:{...process.env,OPENING_DAY_API_PORT:String(apiPort)}});
for(const dir of ['api','src/estimator','config','data/demo','data/processed']){
 watchers.push(watch(dir,{recursive:true},(_event,name)=>{
  if(!name||!(/\.(py|json|csv)$/).test(String(name)))return;
  clearTimeout(reloadTimer);reloadTimer=setTimeout(()=>{
   if(stopping)return;
   console.log('Reloading calculation API after source/data change…');
   const old=api;old.restarting=true;old.once('exit',()=>{if(!stopping)startAPI()});old.kill('SIGTERM');
  },300);
 }));
}
process.on('SIGINT',()=>stop());process.on('SIGTERM',()=>stop());
