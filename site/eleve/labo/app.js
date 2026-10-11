/* Ekole MiniLab v0.1 — no account, no persistence, no grade. */
(() => {
'use strict';
const E=window.EkoleMiniLabEngine;
if(!E)throw new Error('Missing deterministic mini-lab engine');
const $=sel=>document.querySelector(sel);
const make=(tag,cls='',text)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=String(text);return e;};
const add=(p,tag,cl,text)=>{const e=make(tag,cl,text);p.append(e);return e;};
const button=(p,txt,act,cl='lab-btn')=>{const x=add(p,'button',cl,txt);x.type='button';x.addEventListener('click',act);return x;};
const params=new URL(location.href).searchParams;const grade=Number(params.get('annee'));const course=params.get('cours');const gradeKnown=Number.isInteger(grade)&&grade>=1&&grade<=6;const eligible=spec=>!gradeKnown||!Array.isArray(spec.annees_proposees)||spec.annees_proposees.includes(grade);const path='./?outil=';
const returnHref=()=>course&&/^qc-pri-[a-z]+-\d{3}$/.test(course)?'../?cours='+encodeURIComponent(course):gradeKnown?'../?annee='+grade:'../';
const pathLink=document.querySelector('#backToPath');if(pathLink && gradeKnown){pathLink.href='../?annee='+grade;pathLink.hidden=false;pathLink.textContent='← Parcours de '+grade+'e année';}
const returnLink=document.querySelector('#backToCourse');if(returnLink){returnLink.href=returnHref();returnLink.hidden=false;returnLink.textContent=course?'← Retour au cours et à mon parcours':gradeKnown?'← Retour à mon parcours':'← Retour à Ekole Élève';}
const kinds={'jetons':'🧺 Partages','fraction':'🟩 Fractions','droite':'📏 Droite numérique','ordonner':'🧩 Séquences','associer':'🔗 Associations','classer':'🗂️ Classements','grille':'🧭 Repérage','estimer':'🔍 Estimations','suite':'🔢 Suites','position':'🧮 Valeur de position','probleme':'🧠 Problèmes en étapes','diagramme':'📊 Lecture de données','equivalence':'🟩 Fractions équivalentes','duree':'🕒 Temps et durées'};
let catalog=[];let allowedByCourse=null;let gradeByCourse=null;let active=null;let state=null;let hints=0;let result=null;let lastActionCount=0;
function validURL(u){return /^[a-z0-9-]{3,48}$/.test(u);}
function navTo(id){location.href=path+encodeURIComponent(id)+(gradeKnown?'&annee='+grade:'')+(course?'&cours='+encodeURIComponent(course):'');}
function mountGallery(){const main=$('#main');main.replaceChildren();add(main,'div','overline','La boîte à outils');add(main,'h1','','Choisis un petit monde à explorer');add(main,'p','lead','Ces outils servent à manipuler, essayer et comprendre. Ils ne donnent pas de notes.');const section=add(main,'section','toolbox');
 const courseId=course;const suggestions=catalog.filter(x=>x.source_kristal_id===courseId&&eligible(x)&&allowedByCourse&&(allowedByCourse[courseId]||[]).includes(x.id));if(courseId&&suggestions.length){const context=add(main,'section','toolbox-card');add(context,'h2','','Pour la notion que tu explores');add(context,'p','small','Ces exemples sont proposés à la révision, sans validation de maîtrise.');for(const s of suggestions){const a=add(context,'a','tool-link',s.title+' →');a.href=path+encodeURIComponent(s.id)+(gradeKnown?'&annee='+grade:'')+'&cours='+encodeURIComponent(courseId);}}
 if(gradeKnown)add(main,'p','notice','Outils proposés pour la '+grade+'e année : classement provisoire, à réviser avec l’enseignant.');for(const [kind,name] of Object.entries(kinds)){const count=catalog.filter(x=>x.type===kind&&eligible(x)).length;if(!count)continue;const tile=add(section,'section','toolbox-card');add(tile,'div','emoji',name.split(' ')[0]);add(tile,'h2','',name.substring(name.indexOf(' ')+1));add(tile,'p','small',`${count} défis disponibles`);for(const spec of catalog.filter(x=>x.type===kind&&eligible(x))){const link=add(tile,'a','tool-link',spec.title+' →');link.href=path+encodeURIComponent(spec.id)+(gradeKnown?'&annee='+grade:'');}}
}
function render(){const main=$('#main');main.replaceChildren();if(active&&course&&gradeKnown&&gradeByCourse&&grade!==gradeByCourse[course]){add(main,'h1','','Année incompatible avec ce cours');add(main,'p','lead','Cette année ne correspond pas à la proposition d’affectation du Kristal. Reviens au cours.');const a=add(main,'a','tool-link','← Mon cours');a.href='../?cours='+encodeURIComponent(course);return;}if(active&&course&&(!allowedByCourse||!(allowedByCourse[course]||[]).includes(active.id))){add(main,'h1','','Exercice non associé au Kristal');add(main,'p','lead','Cet exercice ne fait pas partie des activités vérifiées pour ce cours.');const a=add(main,'a','tool-link','← Revenir au cours');a.href='../?cours='+encodeURIComponent(course);return;}if(active&&!eligible(active)){add(main,'h1','','Cette activité vise un autre niveau');add(main,'p','lead','Cet outil n’est pas proposé pour l’année sélectionnée. Reviens aux outils recommandés.');const a=add(main,'a','tool-link','← Voir les outils pour mon année');a.href='./?annee='+grade;return;}if(!active){mountGallery();const back=add(main,'a','back','← Retour à mon cours / parcours');back.href=returnHref();return;}
 const q=add(main,'section','stage');const back=add(q,'a','back','← Retour à mon cours / parcours');back.href=returnHref();const all=add(q,'a','back lab-all','Tous les outils →');all.href='./'+(gradeKnown?'?annee='+grade:'');add(q,'div','overline',kinds[active.type]+' · Atelier d’entraînement');add(q,'h1','',active.title);add(q,'p','lead',active.instruction);const work=add(q,'div','work');
 draw(work);const controls=add(q,'div','actionbar');button(controls,'Vérifier',verify,'check');button(controls,'Indice',()=>{hints=Math.min(hints+1,active.hints.length);setFeedback(active.hints[hints-1]||'Essaie encore.',false);},'lab-btn');button(controls,'Recommencer',()=>{state=E.initial(active);hints=0;result=null;lastActionCount=0;render();},'lab-btn');
 const status=add(q,'p','result'+(result?(result.correct?' success':' retry'):''),result?result.feedback:'Je peux essayer autant de fois que je veux.');status.id='lab-feedback';status.setAttribute('role','status');status.setAttribute('aria-live','polite');
 add(q,'p','notice','Exercice de pratique seulement · Aucun suivi, aucune note et aucune preuve officielle de maîtrise.');
 if(active.source_article_ids?.length){const refs=add(q,'p','notice','Notions issues du Kristal autonome : '+active.source_article_ids.length+' fiches documentées.');const a=add(q,'a','back','Consulter les explications et sources ↗');a.href='../encyclopedie-autochtones/';}if(active.source_kristal_id){const back2=add(q,'a','back','Voir la fiche de découverte liée ↗');back2.href='../?cours='+encodeURIComponent(active.source_kristal_id);add(q,'p','notice','Association provisoire : à valider par une personne enseignante.');}
}
function redraw(){const w=$('.work');if(!w)return;w.replaceChildren();draw(w);if(result)setFeedback(result.feedback,result.correct);}
function setFeedback(text,ok){const p=$('#lab-feedback');if(!p)return;p.textContent=text;p.className='result '+(ok?'success':'retry');}
function action(a){state=E.apply(active,state,a);lastActionCount++;result=null;redraw();}
function verify(){result=E.evaluate(active,state);setFeedback(result.feedback,result.correct);}
function draw(host){const p=active.parameters;
 if(active.type==='jetons'){
  add(host,'h2','','Choisis un jeton, puis une boîte.');const pool=add(host,'div','tokens');const bins=[];
  const groups=add(host,'div','groups');for(let i=0;i<p.groups;i++){bins[i]=add(groups,'div','group-box');add(bins[i],'strong','',`Boîte ${i+1}`);button(bins[i],'Déposer ici',()=>action({kind:'place',group:i}),'put');}
  function tokenTo(box,index){const btn=button(box,'●',()=>{action({kind:'select',index});},'token');btn.setAttribute('aria-label',`Jeton ${index+1}`);btn.setAttribute('aria-pressed',String(state.active===index));btn.classList.toggle('active',state.active===index);if(state.bins[index]!==-1){btn.title='Cliquer pour sélectionner puis déplacer';}}
  add(host,'p','small',`Il y a ${p.total} jetons. Les jetons qui restent hors des boîtes comptent comme reste.`);
  for(let i=0;i<p.total;i++){const b=state.bins[i];if(b===-1)tokenTo(pool,i);else tokenTo(bins[b],i);}
  const returnBtn=button(host,'Sortir le jeton sélectionné',()=>action({kind:'place',group:-1}),'lab-btn');returnBtn.disabled=state.active===null;
  const counts=Array(p.groups).fill(0);state.bins.forEach(n=>{if(n>=0)counts[n]++;});add(host,'p','count-note',counts.map((x,i)=>`Boîte ${i+1} : ${x}`).join(' · ')+` · Restants : ${state.bins.filter(n=>n===-1).length}`);
 }
 if(active.type==='fraction'){
  add(host,'h2','','Des parts toutes égales');const strip=add(host,'div','fraction-strip');strip.style.gridTemplateColumns=`repeat(${p.total},minmax(0,1fr))`;
  for(let i=0;i<p.total;i++){const selected=state.marked.includes(i);const b=button(strip,selected?'■':'□',()=>action({kind:'toggle',index:i}),'frac'+(selected?' on':''));b.setAttribute('aria-label',`Part ${i+1} sur ${p.total}`);b.setAttribute('aria-pressed',String(selected));}
  add(host,'p','count-note',`Tu as colorié ${state.marked.length} part(s) sur ${p.total}.`);
 }
 if(active.type==='droite'){
  add(host,'h2','','Déplace le repère');const row=add(host,'div','line-controls');button(row,'−',()=>action({kind:'shift',direction:-1}),'lab-btn');add(row,'output','big-number',state.value);button(row,'+',()=>action({kind:'shift',direction:1}),'lab-btn');const line=add(host,'div','numberline');
  for(let i=p.min;i<=p.max;i+=p.step){const b=button(line,String(i),()=>action({kind:'set',value:i}),'tick'+(state.value===i?' selected':''));b.setAttribute('aria-pressed',String(state.value===i));}
 }
 if(active.type==='ordonner'){
  add(host,'h2','','Mets les cartes dans l’ordre');const byId=new Map(p.cards.map(x=>[x.id,x]));const box=add(host,'ol','order-cards');state.order.forEach((id,i)=>{const item=add(box,'li','order-card');add(item,'span','order-text',byId.get(id).text);const controls=add(item,'div','move-controls');button(controls,'↑',()=>action({kind:'move',index:i,direction:-1}),'small-control').disabled=i===0;button(controls,'↓',()=>action({kind:'move',index:i,direction:1}),'small-control').disabled=i===state.order.length-1;});
 }
 if(active.type==='associer'){
  add(host,'h2','','Relie chaque élément à sa description');const choices=p.pairs.slice().reverse();for(const pair of p.pairs){const row=add(host,'div','select-row');const label=add(row,'label','',pair.label);const sel=add(label,'select');const blank=add(sel,'option','','Choisir…');blank.value='';for(const x of choices){const o=add(sel,'option','',x.correct_label);o.value=x.right;}sel.value=state.matches[pair.left]||'';sel.addEventListener('change',()=>action({kind:'set',id:pair.left,value:sel.value}));}
 }
 if(active.type==='classer'){
  add(host,'h2','','Range les éléments par catégorie');for(const obj of p.objects){const row=add(host,'div','select-row');const label=add(row,'label','',obj.text);const sel=add(label,'select');add(sel,'option','','Choisir…').value='';for(const name of p.bins)add(sel,'option','',name).value=name;sel.value=state.bins[obj.id]||'';sel.addEventListener('change',()=>action({kind:'set',id:obj.id,value:sel.value}));}
 }
 if(active.type==='grille'){
  add(host,'h2','','Trouve la bonne case');const letters=Array.from({length:p.width},(_,i)=>String.fromCharCode(65+i));const grid=add(host,'div','coord-grid');grid.style.gridTemplateColumns=`repeat(${p.width+1},minmax(0,1fr))`;add(grid,'div','axis','');letters.forEach(x=>add(grid,'div','axis',x));for(let y=1;y<=p.height;y++){add(grid,'div','axis',String(y));for(const x of letters){const on=state.column===x&&state.row===y;const b=button(grid,on?'●':'',()=>action({kind:'set',column:x,row:y}),'cell'+(on?' selected':''));b.setAttribute('aria-label',`Colonne ${x}, ligne ${y}`);b.setAttribute('aria-pressed',String(on));}}
 }
 if(active.type==='estimer'){
  add(host,'h2','','Regarde les paquets');const display=add(host,'div','bundles');const groups=p.display_groups||[p.exact];for(const n of groups){const group=add(display,'div','bundle');for(let i=0;i<n;i++)add(group,'span','dot','●');}
  add(host,'p','small','Choisis une estimation avec les boutons, sans réponse libre à écrire.');const choices=add(host,'div','choices');const values=[p.exact-2*p.tolerance-2,p.exact-p.tolerance-1,p.exact,p.exact+p.tolerance+1,p.exact+2*p.tolerance+2].filter(x=>x>=p.min&&x<=p.max);for(const v of [...new Set(values)]){const b=button(choices,String(v),()=>action({kind:'set',value:v}),'choice'+(state.value===v?' selected':''));b.setAttribute('aria-pressed',String(state.value===v));}

 }
 if(active.type==='suite'){
  add(host,'h2','','Observe la suite');add(host,'p','sequence',p.shown.join('  →  ')+'  →  ?');const choices=add(host,'div','choices');for(const choice of p.choices){const b=button(choices,String(choice),()=>action({kind:'set',value:choice}),'choice'+(state.choice===choice?' selected':''));b.setAttribute('aria-pressed',String(state.choice===choice));}
 }
 if(active.type==='position'){
  add(host,'h2','','Construis le nombre avec les centaines, dizaines et unités');const row=add(host,'div','v14-columns');for(let i=0;i<3;i++){const cell=add(row,'div','v14-digit');add(cell,'strong','',['Centaines','Dizaines','Unités'][i]);button(cell,'▲',()=>action({kind:'shift',column:i,direction:1}),'lab-btn');add(cell,'output','big-number',String(state.digits[i]));button(cell,'▼',()=>action({kind:'shift',column:i,direction:-1}),'lab-btn');}
  add(host,'p','count-note',`Nombre construit : ${state.digits[0]*100+state.digits[1]*10+state.digits[2]}. Chaque chiffre a sa place.`);
 }
 if(active.type==='probleme'||active.type==='diagramme'){
  if(active.type==='diagramme'){add(host,'h2','','Observe le diagramme');const bars=add(host,'div','v14-bars');for(const item of p.bars){const bar=add(bars,'div','v14-bar');const rect=add(bar,'div','v14-bar-fill');rect.style.height=`${item.value*8}px`;rect.setAttribute('aria-label',`${item.label}: ${item.value}`);add(bar,'strong','',item.label);add(bar,'small','',String(item.value));}}
  const qs=active.type==='probleme'?p.steps:p.questions;qs.forEach((q,i)=>{const panel=add(host,'section','v14-question');add(panel,'h2','',`${i+1}. ${q.prompt}`);const choices=add(panel,'div','choices');q.options.forEach(v=>{const b=button(choices,String(v),()=>action({kind:'choose',index:i,value:v}),'choice'+(state.answers[i]===v?' selected':''));b.setAttribute('aria-pressed',String(state.answers[i]===v));});});
 }
 if(active.type==='equivalence'){
  add(host,'h2','','Trouve TOUTES les fractions équivalentes');add(host,'p','sequence',`${p.numerator}/${p.denominator} = ?`);const base=add(host,'div','fraction-strip');base.style.gridTemplateColumns=`repeat(${p.denominator},minmax(0,1fr))`;for(let i=0;i<p.denominator;i++){const b=add(base,'span','frac'+(i<p.numerator?' on':''),i<p.numerator?'■':'□');b.setAttribute('aria-label',`Part ${i+1}`);}const choices=add(host,'div','choices');for(const c of p.choices){const on=state.selected.includes(c.id);const b=button(choices,`${c.n}/${c.d}`,()=>action({kind:'toggle',id:c.id}),'choice'+(on?' selected':''));b.setAttribute('aria-pressed',String(on));}
 }
 if(active.type==='duree'){
  add(host,'h2','','Calcule la durée écoulée');const start=p.start_hour*60+p.start_minute;const stamp=m=>`${String(Math.floor(m/60)).padStart(2,'0')} h ${String(m%60).padStart(2,'0')}`;add(host,'p','lead',`Départ : ${stamp(start)} · Arrivée : ${stamp(start+p.duration)}`);add(host,'output','big-number',`${state.minutes} minutes`);const row=add(host,'div','choices');for(const n of [-60,-30,-15,-10,-5,5,10,15,30,60])button(row,(n>0?'+':'')+n+' min',()=>action({kind:'shift',minutes:n}),'lab-btn');
 }

}
async function start(){try{const r=await fetch('./data/catalogue.json',{cache:'no-store'});if(!r.ok)throw Error('Catalogue d’outils indisponible');const obj=await r.json();if(obj.format!=='ekole.microlab-catalog/0.1')throw Error('Contrat inconnu');catalog=obj.items;catalog.forEach(E.validateSpec);const ref=await fetch('./data/associations-v14.json',{cache:'no-store'});if(!ref.ok)throw Error('Références de cours v14 absentes');const guard=await ref.json();if(guard.format!=='ekole.activities-access/1.0')throw Error('Contrat de liaison non reconnu');allowedByCourse=guard.cours;gradeByCourse=guard.annees_proposees;
 const requested=new URL(location.href).searchParams.get('outil');active=requested&&validURL(requested)?catalog.find(x=>x.id===requested):null;state=active?E.initial(active):null;render();}catch(err){const host=$('#main');host.replaceChildren();add(host,'h1','','Les outils sont temporairement indisponibles');add(host,'p','',String(err.message));}}
window.EkoleMiniLab={mount:(host,spec)=>{E.validateSpec(spec);active=spec;state=E.initial(active);if(!host)throw Error('Missing host');const main=$('#main');if(host!==main){main.replaceWith(host);host.id='main';}render();},catalog:()=>catalog.slice()};
start();
})();
