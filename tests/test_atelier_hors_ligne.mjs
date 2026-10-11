// Contrôles du jeu compilé sans réseau ni IA.
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import assert from 'node:assert/strict';
import {fileURLToPath} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const target=path.join(root,'site/eleve/ateliers/rencontres-quebec');
const sandbox={window:{}};
vm.runInNewContext(fs.readFileSync(path.join(target,'donnees.js'),'utf8'),sandbox,{timeout:1500});
const data=sandbox.window.EKOLE_HISTOIRE;
assert.equal(data.faits.length,23);
assert.equal(data.exercices.length,22);
assert.equal(data.visuels.length,6);
const facts=new Map(data.faits.map(x=>[x.id,x]));
const sourceIds=new Set(data.sources.map(x=>x.id));
const periods=new Set(Object.keys(data.periodes));
for(const f of data.faits){
 assert.ok(periods.has(f.periode_ref),`${f.id}: période non résolue`);
 assert.ok(f.sources.length,`${f.id}: source manquante`);
 for(const x of f.sources)assert.ok(sourceIds.has(x),`${f.id}: source ${x}`);
}
for(const e of data.exercices){
 assert.ok(periods.has(e.periode_ref),`${e.id}: période non résolue`);
 assert.ok(e.explication_courte && e.explication_longue,`${e.id}: rétroaction absente`);
 for(const fid of (e.fact_ids||[e.fact_id]))assert.ok(facts.has(fid),`${e.id}: fait ${fid}`);
 if(['cloze','choix'].includes(e.mode)){
  assert.equal(e.options.filter(o=>o.ref===e.reponse_ref).length,1,`${e.id}: réponse ambigüe`);
 }
 if(e.mode==='humain')assert.equal(e.type_validation,'humaine');
 else assert.equal(e.type_validation,'deterministe_entraînement');
}
for(const v of data.visuels){
 assert.ok(v.concept_prompt.length>50,`${v.id}: prompt incomplet`);
 assert.ok(v.expected_path.endsWith('.webp'),`${v.id}: chemin d'image non défini`);
 assert.ok(!fs.existsSync(path.join(target,v.expected_path)),`${v.id}: image non attendue`);
}
assert.ok(fs.readFileSync(path.join(target,'app.js'),'utf8').includes('fallback=el(\'div\',v.concept_prompt'), 'Aucun rendu du prompt si image absente');
console.log('OK — 23 faits, 22 activités, 6 prompts; sources et rétroactions résolues.');
