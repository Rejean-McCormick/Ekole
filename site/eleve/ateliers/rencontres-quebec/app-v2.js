(function(){'use strict';
const d=window.EKOLE_SOC_V2;if(!d){document.body.textContent='Données manquantes. Compiler avec tools/compiler_atelier_histoire_v2.py';return;}
const $=id=>document.getElementById(id),known=new Map(d.faits.map(x=>[x.id,x])),sources=new Map(d.sources.map(x=>[x.id,x]));
const roles=new Map(d.roles.map(x=>[x.id,x])),tasks=new Map(d.taches.map(x=>[x.id,x])),resources=new Map(d.ressources.map(x=>[x.id,x]));
const societies=new Map(d.societes.map(x=>[x.id,x]));let selectedPeriod='periode:1701',current=d.defis[0]?.id||'',picked=null,pairs=[],seq=[];
function E(tag,text,cl){const n=document.createElement(tag);if(text!==undefined)n.textContent=String(text);if(cl)n.className=cl;return n;}
function B(label,fn,pressed=false){let b=E('button',label);b.type='button';b.setAttribute('aria-pressed',String(pressed));b.addEventListener('click',fn);return b;}
function blank(id){let x=$(id);x.replaceChildren();return x;}
function srcMeta(ids){return E('small','Source(s) : '+ids.map(x=>sources.get(x)?.titre||x).join(' · '),'meta');}
function periodName(id){return d.periodes.find(x=>x.id===id)?.label||id;}
function view(name){document.querySelectorAll('.mainnav button').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.view===name)));for(let s of ['decouvrir','relier','exercices','questions','sources'])$('panel-'+s).hidden=s!==name;}
document.querySelectorAll('.mainnav button').forEach(b=>b.addEventListener('click',()=>view(b.dataset.view)));
function choosePeriod(id){selectedPeriod=id;let div=blank('periods');for(let p of d.periodes)div.append(B(p.label,()=>choosePeriod(p.id),p.id===id));$('period-note').textContent=d.periodes.find(p=>p.id===id)?.note||'';renderFacts();renderRelations();renderNormes();renderVisuals();renderChallengeMenu();}
function renderFacts(){const out=blank('facts');let arr=d.faits.filter(f=>f.periode_ref===selectedPeriod);for(let f of arr){let card=E('div',undefined,'card');card.append(E('p',f.texte),srcMeta(f.sources));let details=E('details'),summary=E('summary','Quelles limites ?');details.append(summary,E('p',f.limites),E('small','Repère : '+f.ancrage));card.append(details);out.append(card);}if(!arr.length)out.append(E('p','Pas de fait documenté pour cette période.'));}
function renderRelations(){const out=blank('relations');let arr=d.relations.filter(f=>f.periode_ref===selectedPeriod);for(let r of arr){let card=E('div',undefined,'card');card.append(E('h3',roles.get(r.role_ref)?.label||r.role_ref),E('p','Tâche : '+(tasks.get(r.tache_ref)?.label||r.tache_ref)),E('p','Ressource : '+(resources.get(r.ressource_ref)?.label||r.ressource_ref)),E('small','Contexte : '+(societies.get(r.societe_ref)?.label||r.societe_ref)),srcMeta(r.source_ids));out.append(card);}if(!arr.length)out.append(E('p','Aucune relation détaillée encore documentée pour cette époque. Nous ne déduisons pas de faux rôles.'));}
function renderNormes(){const out=blank('normes');let arr=d.normes.filter(n=>n.periode_ref===selectedPeriod);for(let n of arr){let card=E('div',undefined,'card');card.append(E('h3',n.portee),E('p',n.interpretation),E('small','Statut : '+n.statut),srcMeta(n.source_ids));out.append(card);}if(!arr.length)out.append(E('p','Aucune règle contextualisée attestée dans cette couche. Ce silence ne signifie pas absence de règles historiques.'));}
function renderVisuals(){const out=blank('visuals');let relevant=d.visuels.filter(v=>{let s=v.id.toLowerCase();return selectedPeriod==='periode:1701'?s.includes('diplomatie')||s.includes('sources')||s.includes('traite')||s.includes('roles'):selectedPeriod==='periode:actuel'?s.includes('aujourdhui')||s.includes('wendat-conseil'):selectedPeriod==='periode:1600-1650'?s.includes('echanges')||s.includes('roles'):s.includes('territoires')||s.includes('sources')||s.includes('innus')||s.includes('comparaison')}).slice(0,2);
for(let v of relevant){let c=E('div',undefined,'card');c.append(E('h3',v.titre));let fallback=E('p',v.concept_prompt,'prompt');let img=E('img');img.alt=v.alt_fr;img.hidden=true;img.onload=()=>{fallback.hidden=true;img.hidden=false};img.onerror=()=>{fallback.hidden=false;img.hidden=true};img.src=v.expected_path;c.append(img,fallback,E('small','Fichier attendu : '+v.expected_path));out.append(c);}}
function renderChallengeMenu(){const out=blank('challenge-list');let arr=d.defis.filter(x=>x.periode_ref===selectedPeriod||x.periode_ref==='multi');for(let x of arr)out.append(B(x.titre,()=>{current=x.id;picked=null;pairs=[];seq=[];renderChallenge();renderChallengeMenu();view('exercices')},x.id===current));if(arr.length&&(!d.defis.some(x=>x.id===current)||!arr.some(x=>x.id===current))){current=arr[0].id;picked=null;pairs=[];seq=[]}renderChallenge();}
function giveFeedback(ok,x,extra){const box=$('exercise-feedback');box.replaceChildren();box.className='feedback '+(ok?'good':'try');box.append(E('strong',ok?'Tu as trouvé cette relation.':'Regarde les fiches et réessaie.'),E('p',extra||x.reponse_courte));let actions=E('div',undefined,'actions');let n=0;actions.append(B('Un indice',()=>{if(n<x.indices.length)box.append(E('p','Indice : '+x.indices[n++]));}));actions.append(B('Explication détaillée',()=>{if(!box.querySelector('.extended')){let full=E('div',undefined,'extended');full.append(E('p',x.explication_longue));if(x.prealables?.length){full.append(E('p','Pour réviser : '+x.prealables.map(v=>({'concept:role':'Qui fait quoi ?','concept:tache':'Quelle action ?','concept:epoque':'À quelle époque ?','concept:source':'Qui dit cela ?','concept:siecle':'Avant ou après ?'}[v]||v)).join(' · ')));let rr=B('Revoir les fiches de cette époque',()=>view('relier'));full.append(rr);}box.append(full)}}));actions.append(B('Recommencer',()=>{picked=null;pairs=[];seq=[];renderChallenge()}));box.append(actions);}
function buildOptions(x,node){let div=E('div',undefined,'options');for(let opt of x.options){div.append(B(opt.label,()=>{if(x.type==='choisir_fiche'){
  let r=d.relations.find(y=>y.id===opt.id);let detail=r?('Cette autre fiche documente : '+(tasks.get(r.tache_ref)?.label||'')+' — '+(resources.get(r.ressource_ref)?.label||'')+'.'):'';
  giveFeedback(opt.id===x.correct_ref,x,opt.id===x.correct_ref?x.reponse_courte:detail+' La question porte sur une association précise parmi les fiches sélectionnées.');
}else giveFeedback(opt.id===x.correct_ref,x);},opt.id===picked));}node.append(div);}
function buildPairs(x,node){
 let selected=null;
 let grid=E('div',undefined,'match-cols');
 let left=E('div',undefined,'match-col');
 let right=E('div',undefined,'match-col');
 grid.append(left,right);
 node.append(E('p','Choisis d’abord un rôle, puis la tâche correspondante.'),grid);
 function draw(){
  left.replaceChildren();right.replaceChildren();
  for(const p of x.pairs){
   const done=pairs.some(a=>a.left_id===p.left_id);
   const b=B((done?'✓ ':'')+p.left,()=>{selected=p.left_id;draw()},selected===p.left_id);
   b.disabled=done;left.append(b);
  }
  for(const p of x.pairs.slice().reverse()){
   const done=pairs.some(a=>a.right_id===p.right_id);
   const b=B((done?'✓ ':'')+p.right,()=>{
    if(!selected)return;
    const wanted=x.pairs.find(t=>t.left_id===selected);
    if(wanted?.right_id===p.right_id){
     pairs.push(wanted);selected=null;draw();
     if(pairs.length===x.pairs.length)giveFeedback(true,x);
    }else{
     giveFeedback(false,x,'Les deux cartes ne sont pas associées dans les fiches étudiées. Vérifie leurs tâches.');
    }
   });
   b.disabled=done;right.append(b);
  }
 }
 draw();
}
function buildChrono(x,node){let out=E('div');node.append(out);function draw(){out.replaceChildren();out.append(E('p','Ton ordre : '+(seq.map(i=>i.label).join(' → ')||'Choisis le premier événement')));let div=E('div',undefined,'options');for(let it of x.elements.slice().reverse()){let b=B(it.label,()=>{seq.push(it);draw();if(seq.length===x.elements.length)giveFeedback(seq.every((a,i)=>a.id===x.correct_refs[i]),x)});b.disabled=seq.some(z=>z.id===it.id);div.append(b)}out.append(div)}draw();}
function renderChallenge(){const out=blank('challenge');let x=d.defis.find(x=>x.id===current);if(!x){out.append(E('p','Choisis une activité ci-dessus.'));return}out.append(E('small',(x.periode_ref==='multi'?'Plusieurs époques':periodName(x.periode_ref))+' · '+x.evaluation),E('h3',x.titre),E('p',x.question));if(x.type==='associer')buildPairs(x,out);else if(x.type==='chronologie')buildChrono(x,out);else if(x.type==='observation_humaine'){out.append(E('p','Cette activité se réalise avec un adulte; aucun score automatique.'));let ul=E('ul');for(let c of x.criteres)ul.append(E('li',c));out.append(ul)}else buildOptions(x,out);let fb=E('div');fb.id='exercise-feedback';out.append(fb,srcMeta(x.source_ids));}
function renderQuestions(){let out=blank('question-list');for(let q of d.questions)out.append(B(q.question,()=>{const a=known.get(q.fact_id),box=blank('answer');if(!a){box.append(E('p','Je ne sais pas : ce fait n’est pas documenté dans cette version.'));return;}box.append(E('p',a.texte),srcMeta(a.sources),E('small','Limite : '+a.limites))}));}
function renderSources(){let out=blank('source-list');for(let s of d.sources){let c=E('div',undefined,'card'),a=E('a',s.titre);a.href=s.url;a.target='_blank';a.rel='noopener noreferrer';c.append(a,E('p',s.limites,'meta'));out.append(c)}}
renderSources();renderQuestions();choosePeriod(selectedPeriod);view('decouvrir');
})();
