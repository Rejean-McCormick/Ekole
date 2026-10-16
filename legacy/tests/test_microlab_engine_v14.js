'use strict';
const assert=require('node:assert/strict'),fs=require('fs'),path=require('path');const r=path.resolve(process.argv[2]||path.join(__dirname,'..'));const E=require(path.join(r,'site/eleve/labo/engine.js'));const C=JSON.parse(fs.readFileSync(path.join(r,'site/eleve/labo/data/catalogue.json'),'utf8'));const guard=JSON.parse(fs.readFileSync(path.join(r,'site/eleve/labo/data/associations-v14.json'),'utf8'));
assert.equal(C.items.length,51);assert.equal(E.TYPES.length,14);assert.equal(new Set(C.items.map(x=>x.id)).size,51);
for(const q of C.items){E.validateSpec(q);let state=E.initial(q);assert.equal(E.evaluate(q,state).correct,false,'solved before action '+q.id);const p=q.parameters;function step(a){const old=JSON.stringify(state);const updated=E.apply(q,state,a);assert.equal(JSON.stringify(state),old,'mutated state '+q.id);state=updated;}
 switch(q.type){
 case 'jetons':{const n=Math.floor(p.total/p.groups);for(let i=0;i<n*p.groups;i++){step({kind:'select',index:i});step({kind:'place',group:Math.floor(i/n)});}break;}
 case 'fraction':for(let i=0;i<p.wanted;i++)step({kind:'toggle',index:i});break;
 case 'droite':step({kind:'set',value:p.target});break;
 case 'ordonner':for(let i=0;i<p.correct.length;i++){let j=state.order.indexOf(p.correct[i]);while(j>i){step({kind:'move',index:j,direction:-1});j--;}}break;
 case 'associer':for(const x of p.pairs)step({kind:'set',id:x.left,value:x.right});break;
 case 'classer':for(const x of p.objects)step({kind:'set',id:x.id,value:x.bin});break;
 case 'grille':step({kind:'set',column:p.target[0],row:p.target[1]});break;
 case 'estimer':step({kind:'set',value:p.exact});break;
 case 'suite':step({kind:'set',value:p.answer});break;
 case 'position':for(let j=0;j<3;j++){const n=[Math.floor(p.target/100),Math.floor(p.target/10)%10,p.target%10][j];while(state.digits[j]!==n)step({kind:'shift',column:j,direction:1});}break;
 case 'probleme':for(let i=0;i<2;i++)step({kind:'choose',index:i,value:p.steps[i].answer});break;
 case 'diagramme':for(let i=0;i<2;i++)step({kind:'choose',index:i,value:p.questions[i].answer});break;
 case 'equivalence':for(const x of p.choices)if(x.n*p.denominator===x.d*p.numerator)step({kind:'toggle',id:x.id});break;
 case 'duree':{let minutes=p.duration;for(const n of [60,30,15,10,5])while(minutes>=n){step({kind:'shift',minutes:n});minutes-=n;}assert.equal(minutes,0);break;}
 default:assert.fail('Unknown '+q.type);
 }
 const result=E.evaluate(q,state);assert.equal(result.correct,true,q.id+' '+JSON.stringify(result));assert.equal(result.proof_of_mastery,false);assert.deepEqual(E.apply(q,state,{kind:'bogus'}),state);
}
for(const type of ['probleme','diagramme']){const q=C.items.find(x=>x.type===type);const data=type==='probleme'?q.parameters.steps:q.parameters.questions;const state=E.apply(q,E.initial(q),{kind:'choose',index:0,value:data[0].answer});assert.equal(E.evaluate(q,state).correct,false);}
for(const q of C.items.filter(x=>x.type==='equivalence')){const p=q.parameters,wrong=p.choices.find(x=>x.n*p.denominator!==x.d*p.numerator);const state=E.apply(q,E.initial(q),{kind:'toggle',id:wrong.id});assert.equal(E.evaluate(q,state).correct,false);}
for(const [cid,ids] of Object.entries(guard.cours))for(const id of ids){const q=C.items.find(x=>x.id===id);assert.equal(q.source_kristal_id,cid)}
console.log('v14 OK: '+C.items.length+' challenges, 14 deterministic motors, correct and wrong responses');
