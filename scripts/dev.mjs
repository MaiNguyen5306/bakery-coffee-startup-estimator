import { spawn } from 'node:child_process';
import { existsSync } from 'node:fs';
const python = existsSync('.venv/bin/python') ? '.venv/bin/python' : 'python3';
const children = [spawn(python,['scripts/serve_api.py'],{stdio:'inherit'}),spawn(process.execPath,['node_modules/vite/bin/vite.js','--host','127.0.0.1'],{stdio:'inherit'})];
let stopping = false;
function stop(code=0) { if(stopping)return; stopping=true; children.forEach(p=>p.kill('SIGTERM')); process.exitCode=code; }
for(const p of children){p.on('error',e=>{console.error(e.message);stop(1)});p.on('exit',code=>stop(code??1));}
process.on('SIGINT',()=>stop());process.on('SIGTERM',()=>stop());
