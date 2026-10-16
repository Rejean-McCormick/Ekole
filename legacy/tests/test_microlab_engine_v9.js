'use strict';
const assert=require('node:assert/strict');const fs=require('node:fs');const path=require('node:path');
const root=process.argv[2]||'.';const engine=require(path.resolve(root,'site/eleve/labo/engine.js'));
const data=JSON.parse(fs.readFileSync(path.resolve(root,'site/eleve/labo/data/catalogue.json'),'utf8'));
assert.ok(data.count>=20);assert.equal(data.items.length,data.count);assert.equal(new Set(data.items.map(x=>x.id)).size,data.count);
const legacy=new Set(['jetons','fraction','droite','ordonner','associer','classer','grille','estimer','suite']);assert.deepEqual(new Set(data.items.filter(x=>legacy.has(x.type)).map(x=>x.type)),legacy);
for(const spec of data.items.filter(x=>legacy.has(x.type))){
 engine.validateSpec(spec);let state=engine.initial(spec);let first=engine.evaluate(spec,state);
 assert.equal(first.correct,false,'initial not solved '+spec.id);
 const p=spec.parameters;
 if(spec.type==='jetons'){
  const q=Math.floor(p.total/p.groups);for(let i=0;i<q*p.groups;i++){state=engine.apply(spec,state,{kind:'select',index:i});state=engine.apply(spec,state,{kind:'place',group:Math.floor(i/q)});}
 }else if(spec.type==='fraction'){
  for(let i=0;i<p.wanted;i++)state=engine.apply(spec,state,{kind:'toggle',index:i});
 }else if(spec.type==='droite')state=engine.apply(spec,state,{kind:'set',value:p.target});
 else if(spec.type==='ordonner'){
  for(let i=0;i<p.correct.length;i++){let j=state.order.indexOf(p.correct[i]);while(j>i){state=engine.apply(spec,state,{kind:'move',index:j,direction:-1});j--;}}
 }else if(spec.type==='associer')for(const pair of p.pairs)state=engine.apply(spec,state,{kind:'set',id:pair.left,value:pair.right});
 else if(spec.type==='classer')for(const obj of p.objects)state=engine.apply(spec,state,{kind:'set',id:obj.id,value:obj.bin});
 else if(spec.type==='grille')state=engine.apply(spec,state,{kind:'set',column:p.target[0],row:p.target[1]});
 else if(spec.type==='estimer')state=engine.apply(spec,state,{kind:'set',value:p.exact});
 else if(spec.type==='suite')state=engine.apply(spec,state,{kind:'set',value:p.answer});
 const result=engine.evaluate(spec,state);assert.equal(result.correct,true,'wrong valid result '+spec.id+': '+JSON.stringify(result));assert.equal(result.proof_of_mastery,false);
 const clone=JSON.stringify(state);
 const impossible=engine.apply(spec,state,{kind:'invalid',index:-999,group:999});assert.equal(JSON.stringify(state),clone,'no mutation '+spec.id);
 assert.equal(typeof result.feedback,'string');assert.ok(result.feedback.length>12);
}
for(const [id,field,val] of [['partage-12','groups',0],['fractions-3-8','wanted',20],['droite-7','target',90],['estime-48','tolerance',-1]]){
 const x=JSON.parse(JSON.stringify(data.items.find(x=>x.id===id)));x.parameters[field]=val;assert.throws(()=>engine.validateSpec(x));
}
for(const name of ['site/eleve/labo/index.html','site/eleve/labo/app.js','site/eleve/labo/lab.css','site/eleve/labo/engine.js']){
 assert.ok(fs.existsSync(path.resolve(root,name)));
}
console.log(`PASS: ${data.count} exercices, ${engine.TYPES.length} moteurs, validations et états vérifiés`);
