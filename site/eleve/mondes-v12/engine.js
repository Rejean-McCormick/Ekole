/* Ekole MicroMondes v12 — mécanismes d'entraînement déterministes. Pas un moteur de certification. */
(function(root,factory){const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;if(root)root.EkoleMondesV12=api;})(typeof globalThis!=='undefined'?globalThis:null,function(){
'use strict';
const TYPES=['representations','repartition','causalite','preuves','expression'];
const fail=x=>{throw Error('MicroMonde v12 : '+x);};
const int=x=>Number.isInteger(x);
const distinct=a=>new Set(a).size===a.length;
function validateSpec(s){
 if(!s||typeof s!=='object'||!/^qc-pri-[a-z]+-\d{3}$/.test(s.kristal_id)||!/^[-a-z0-9]{4,64}$/.test(s.id)||!TYPES.includes(s.type))fail('identifiant/type');
 if(!s.title||!s.instruction||s.evaluation!=='entrainement_non_certifiant'||s.source_review!=='revue_requise')fail('statut et texte');
 const p=s.parameters;if(!p||typeof p!=='object')fail('paramètres');
 switch(s.type){
 case 'representations':if(!int(p.parts)||p.parts<2||p.parts>10||!int(p.chosen)||p.chosen<1||p.chosen>=p.parts||!int(p.group_size)||p.group_size<1||p.group_size>5)fail('fraction');break;
 case 'repartition':if(!int(p.total)||!int(p.bins)||p.total<2||p.total>30||p.bins<2||p.bins>6||p.total<p.bins)fail('répartition');break;
 case 'causalite':if(!Array.isArray(p.events)||p.events.length<3||p.events.length>6||!p.events.every(e=>e&&/^e\d+$/.test(e.id)&&typeof e.text==='string'&&e.text.length>5)||!distinct(p.events.map(e=>e.id))||!Array.isArray(p.order)||p.order.length!==p.events.length||!distinct(p.order)||!p.order.every(x=>p.events.some(e=>e.id===x))||!Array.isArray(p.links)||!p.links.every(l=>p.events.some(e=>e.id===l.from)&&p.events.some(e=>e.id===l.to)&&l.from!==l.to))fail('récit');break;
 case 'preuves':if(!Array.isArray(p.statements)||p.statements.length<3||p.statements.length>8||!distinct(p.statements.map(x=>x.id))||!p.statements.every(x=>typeof x.text==='string'&&x.text.length>5&&['observation','interpretation'].includes(x.kind)))fail('démarche');break;
 case 'expression':if(!Array.isArray(p.gestures)||p.gestures.length<2||p.gestures.length>6||!p.gestures.every(x=>typeof x==='string'&&x.trim())||!p.intention||typeof p.intention!=='string')fail('jeu');break;
 }
 return true;
}
function initial(s){validateSpec(s);const p=s.parameters;switch(s.type){
 case 'representations':return {surface:[],bande:[],collection:[]};
 case 'repartition':return {bins:Array(p.total).fill(-1),active:null};
 case 'causalite':return {order:p.events.map(x=>x.id).reverse(),links:{}};
 case 'preuves':return {classifications:{}};
 case 'expression':return {selected:[],comment:''};
 }}
function apply(s,state,a){validateSpec(s);const p=s.parameters;const n=JSON.parse(JSON.stringify(state));if(!a||typeof a!=='object')return n;
 switch(s.type){
 case 'representations':if(['surface','bande','collection'].includes(a.part)&&a.action==='toggle'&&int(a.index)&&a.index>=0&&a.index<p.parts){const set=new Set(n[a.part]);set.has(a.index)?set.delete(a.index):set.add(a.index);n[a.part]=[...set].sort((x,y)=>x-y);}break;
 case 'repartition':if(a.action==='select'&&int(a.index)&&a.index>=0&&a.index<p.total)n.active=a.index;if(a.action==='place'&&int(a.bin)&&a.bin>=-1&&a.bin<p.bins&&int(n.active)&&n.active>=0&&n.active<p.total){n.bins[n.active]=a.bin;n.active=null;}if(a.action==='return'&&int(a.index)&&a.index>=0&&a.index<p.total)n.bins[a.index]=-1;break;
 case 'causalite':if(a.action==='move'&&int(a.index)&&[-1,1].includes(a.direction)){const j=a.index+a.direction;if(a.index>=0&&j>=0&&j<n.order.length&&a.index<n.order.length)[n.order[a.index],n.order[j]]=[n.order[j],n.order[a.index]];}if(a.action==='link'&&int(a.index)&&a.index>=0&&a.index<p.links.length&&typeof a.value==='boolean')n.links[a.index]=a.value;break;
 case 'preuves':if(a.action==='classify'&&p.statements.some(x=>x.id===a.id)&&['observation','interpretation'].includes(a.kind))n.classifications[a.id]=a.kind;break;
 case 'expression':if(a.action==='toggle'&&p.gestures.includes(a.gesture)){const set=new Set(n.selected);set.has(a.gesture)?set.delete(a.gesture):set.add(a.gesture);n.selected=[...set];}break;
 }
 return n;
}
function evaluate(s,state){validateSpec(s);const p=s.parameters;let criteria=[],diagnostic='';let complete=false,correct=false;
 switch(s.type){
 case 'representations':{
  const keys=['surface','bande','collection'];criteria=keys.map(k=>({id:k,ok:state[k].length===p.chosen,detail:`${state[k].length} groupe(s) sur ${p.parts}`}));complete=keys.every(k=>state[k].length>0);correct=criteria.every(c=>c.ok);diagnostic=correct?'Les trois représentations montrent le même rapport. Explique maintenant pourquoi le tout change de support.':!complete?'Tu n’as pas encore utilisé les trois supports.':'Compare les parts choisies et le nombre de parts égales sur chaque support.';break;}
 case 'repartition':{
  const counts=Array(p.bins).fill(0);for(const b of state.bins)if(int(b)&&b>=0&&b<p.bins)counts[b]++;const left=state.bins.filter(x=>x===-1).length;const per=Math.floor(p.total/p.bins),rest=p.total%p.bins;const balanced=counts.every(c=>c===per);criteria=[{id:'objets_uniques',ok:state.bins.length===p.total,detail:'Un objet ne peut être placé qu’une fois'},{id:'parts_egales',ok:balanced,detail:counts.join(' / ')},{id:'reste',ok:left===rest,detail:`${left} non placé(s); reste attendu ${rest}`}];complete=left<=rest;correct=criteria.every(c=>c.ok);diagnostic=correct?'Les parts sont égales et le reste est correct. Peux-tu expliquer comment tu le sais ?':counts.some(c=>c>per)?'Une boîte contient plus que le partage équitable.':left>rest?'Il reste des objets à distribuer.':'Compare le nombre dans chacune des boîtes.';break;}
 case 'causalite':{
  const orderOK=state.order.every((id,i)=>id===p.order[i]);const allLinks=p.links.every((_,i)=>typeof state.links[i]==='boolean');const linksOK=allLinks&&p.links.every((l,i)=>state.links[i]===!!l.valid);criteria=[{id:'ordre',ok:orderOK,detail:'Début, événements, fin'},{id:'liens',ok:linksOK,detail:'Relations proposées'}];complete=allLinks;correct=orderOK&&linksOK;diagnostic=correct?'Tu as ordonné les événements et repéré les relations indiquées. Explique à une personne pourquoi ces liens ont du sens.':!orderOK?'Cherche quel événement permet au suivant d’arriver.':!allLinks?'Indique si chaque relation proposée est justifiée.':'Une relation proposée ne correspond pas à l’histoire.';break;}
 case 'preuves':{
  complete=p.statements.every(x=>state.classifications[x.id]);correct=complete&&p.statements.every(x=>state.classifications[x.id]===x.kind);criteria=p.statements.map(x=>({id:x.id,ok:state.classifications[x.id]===x.kind,detail:x.text}));diagnostic=correct?'Tu distingues les constats des interprétations dans ces exemples. Propose maintenant une observation nouvelle.':!complete?'Classe chaque proposition.':'Une interprétation explique ou suppose; une observation indique ce qui est directement constaté.';break;}
 case 'expression':{
  complete=state.selected.length>0;correct=false;criteria=[{id:'preparation',ok:complete,detail:'Moyens expressifs préparés'}];diagnostic='À jouer devant une personne : le système ne peut pas vérifier l’expression théâtrale. Demande une observation avec la grille enseignante.';break;}
 }
 return {complete,correct,criteria,diagnostic,proof_of_mastery:false,requires_human:true,validation:s.type==='expression'?'observation_humaine':'entrainement_partiel'};
}
return Object.freeze({TYPES,validateSpec,initial,apply,evaluate});
});
