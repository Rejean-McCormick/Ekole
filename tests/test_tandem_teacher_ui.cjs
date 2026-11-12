/* Aperçu synthétique multi-mission, sans navigateur, sans connexion Orgo. */
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const source = fs.readFileSync(path.resolve(__dirname, '../enseignant-app/app.js'), 'utf8');
const marker = '/* Intégration Tandem :';
const script = source.slice(source.indexOf(marker));
assert.ok(script.startsWith(marker));
function element(tag) {
  return {tag, children:[], className:'', textContent:'', id:'',
    appendChild(child) {this.children.push(child);},
    insertBefore(child) {this.children.unshift(child);},
    setAttribute(key,value) {this[key]=value;}};
}
async function render(tasks, ref='fete-sorciere', valid=true) {
  const main = element('main');
  const document = {readyState:'complete', createElement:element,
    querySelector:(selector)=>selector==='main.container' ? main : null,
    getElementById:()=>null};
  const fetch = async()=>({ok:true,json:async()=>({
    format:'ekole.tandem-teacher-preview/1.0',mode:valid?'synthetic':'live',
    authority:'orgo',scenario_ref:ref,tasks,
  })});
  vm.runInNewContext(script, {fetch, document, Set});
  await new Promise(resolve=>setImmediate(resolve));
  return main;
}
function rows(n) {return Array.from({length:n},(_,i)=>({
  task_ref:`tache-${i+1}`,role_code:'fermier',state:'ready',fragment_refs:[],
}));}
test('ancien aperçu 4 tâches accepté sans texte de fragments',async()=>{
  const root=await render(rows(4),'fete-sorciere-synthetique');
  assert.equal(root.children.length,1);
  assert.equal(root.children[0].children[2].children.length,4);
});
test('mission complète 11 et nouvelle mission 10 étapes prises en charge',async()=>{
  for(const [n,ref] of [[11,'fete-sorciere'],[10,'randonnee-a-velo']]) {
    const root=await render(rows(n),ref);
    assert.equal(root.children[0].children[2].children.length,n);
    assert.match(root.children[0].children[0].textContent,new RegExp(ref.replaceAll('-',' ')));
    assert.match(root.children[0].children[1].textContent,/Aucune Case ni Task/);
  }
});
test('mode live et tâches corrompues refusés',async()=>{
  assert.equal((await render(rows(11),'fete-sorciere',false)).children.length,0);
  const bad=rows(4);bad[0].role_code='<script>alert(1)</script>';
  assert.equal((await render(bad)).children.length,0);
});
