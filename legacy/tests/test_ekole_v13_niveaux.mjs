import fs from 'node:fs';import assert from 'node:assert/strict';
import vm from 'node:vm';
const file=new URL('../site/eleve/labo/data/catalogue.json',import.meta.url);const data=JSON.parse(fs.readFileSync(file,'utf8'));
const engineFile='/mnt/data/ekole_v13_workspace/site/eleve/labo/engine.js';
// On a full Ekole installation, engine.js is alongside the new data catalog. No absolute path dependency.
const local=new URL('../site/eleve/labo/engine.js',import.meta.url);
if(fs.existsSync(local)){
 const sandbox={module:{exports:{}},globalThis:{}};vm.runInNewContext(fs.readFileSync(local,'utf8'),sandbox);const E=sandbox.module.exports;
 for(const q of data.items){assert.equal(E.validateSpec(q),true,q.id); const state=E.initial(q);assert.ok(E.evaluate(q,state));}
}
assert.ok(data.items.length>=27);assert.ok(data.items.some(x=>x.id==='histoire-faits-limites'));
for(const m of data.items.filter(x=>x.annees_proposees.includes(3))){assert.notEqual(m.id,'droite-12');}
console.log('V13: schema exercise cases passed, '+data.items.length+' scenarios');
