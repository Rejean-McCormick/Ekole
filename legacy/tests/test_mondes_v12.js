const assert=require('node:assert/strict');
const E=require('../site/eleve/mondes-v12/engine.js');
const d=require('../site/eleve/mondes-v12/data/catalogue.json');
assert.equal(d.items.length,7);assert.equal(new Set(d.items.map(x=>x.id)).size,7);
for(const spec of d.items){assert.equal(E.validateSpec(spec),true);const empty=E.initial(spec);assert.equal(E.evaluate(spec,empty).proof_of_mastery,false);assert.equal(E.evaluate(spec,empty).requires_human,true);}
const get=id=>d.items.find(x=>x.id===id);
let a=get('fractions-2-5-multisupport'),s=E.initial(a);
for(const part of ['surface','bande','collection'])for(const i of [0,1])s=E.apply(a,s,{action:'toggle',part,index:i});assert.equal(E.evaluate(a,s).correct,true);
s=E.apply(a,s,{action:'toggle',part:'bande',index:2});assert.equal(E.evaluate(a,s).correct,false);
for(const id of ['division-partage-14-3','division-groupement-12-4']){a=get(id);s=E.initial(a);const per=Math.floor(a.parameters.total/a.parameters.bins);for(let i=0;i<a.parameters.bins*per;i++){s=E.apply(a,s,{action:'select',index:i});s=E.apply(a,s,{action:'place',bin:i%a.parameters.bins});}assert.equal(E.evaluate(a,s).correct,true);if(a.parameters.total%a.parameters.bins){s=E.apply(a,s,{action:'select',index:a.parameters.total-1});s=E.apply(a,s,{action:'place',bin:0});assert.equal(E.evaluate(a,s).correct,false);}}
a=get('recit-liens-causaux');s=E.initial(a);assert.equal(E.evaluate(a,s).correct,false);for(let j=0;j<a.parameters.order.length;j++){const target=a.parameters.order[j];let pos=s.order.indexOf(target);while(pos>j){s=E.apply(a,s,{action:'move',index:pos,direction:-1});pos--;}}a.parameters.links.forEach((x,i)=>{s=E.apply(a,s,{action:'link',index:i,value:x.valid})});assert.equal(E.evaluate(a,s).correct,true);
a=get('sciences-observer-interpreter');s=E.initial(a);for(const x of a.parameters.statements)s=E.apply(a,s,{action:'classify',id:x.id,kind:x.kind});assert.equal(E.evaluate(a,s).correct,true);s=E.apply(a,s,{action:'classify',id:'s1',kind:'interpretation'});assert.equal(E.evaluate(a,s).correct,false);
a=get('theatre-deux-moyens');s=E.initial(a);s=E.apply(a,s,{action:'toggle',gesture:a.parameters.gestures[0]});assert.equal(E.evaluate(a,s).correct,false);assert.equal(E.evaluate(a,s).validation,'observation_humaine');
assert.throws(()=>E.validateSpec({...a,evaluation:'certifie'}));
console.log('v12: 7 types de scénarios, succès et erreurs testés; 0 preuve de maîtrise délivrée.');
