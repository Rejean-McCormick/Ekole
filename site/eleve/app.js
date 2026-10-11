'use strict';
// Ekole Eleve 0.1. No account, tracking, assessment, or gradebook.
const LEVELS=['1re','2e','3e','4e','5e','6e'];
const ICONS={
  'Mathématique':'🔢','Français, langue d’enseignement':'📚','Français, langue seconde':'📗',
  'Anglais, langue d’enseignement':'🔤','Anglais, langue seconde':'🗣️',
  'Arts plastiques':'🎨','Art dramatique':'🎭','Danse':'💃','Musique':'🎵',
  'Science et technologie':'🔬','Géographie, histoire et éducation à la citoyenneté':'🗺️',
  'Culture et citoyenneté québécoise':'🤝','Intégration linguistique, scolaire et sociale':'🌍',
  'Éducation physique et à la santé':'🏃'
};
const GROUPS=[
  {name:'Tous',icon:'🌟',test:()=>true},
  {name:'Maths',icon:'🔢',test:c=>c.subject==='Mathématique'},
  {name:'Lire et écrire',icon:'📚',test:c=>c.subject.startsWith('Français')},
  {name:'Découvrir',icon:'🔬',test:c=>/Science|Géographie|citoyenneté/i.test(c.subject)},
  {name:'Créer',icon:'🎨',test:c=>/Art |Arts |Danse|Musique/.test(c.subject)},
  {name:'Bouger',icon:'🏃',test:c=>c.subject.startsWith('Éducation physique')},
  {name:'Langues',icon:'🗣️',test:c=>/Anglais|Intégration linguistique/.test(c.subject)}
];
const LABELS={'qc-pri-ma-012':'Joue avec les fractions','qc-pri-ma-001':'Compte les objets'};
const STATE={activities:new Map(),approvedImages:new Map(),notebook:[],year:null,stage:0,group:'Tous',more:false,course:null,catalogue:null,byId:new Map(),light:null,visuals:new Map(),kristalVisuals:new Map(),experiences:new Map(),mondesV12:new Map(),labV13:new Map(),associationsV14:new Map()};
const query=()=>new URL(location.href).searchParams;
const el=(tag,klass='',text)=>{const e=document.createElement(tag);if(klass)e.className=klass;if(text!==undefined)e.textContent=String(text);return e;};
function child(parent,tag,klass,text){const e=el(tag,klass,text);parent.append(e);return e;}
function link(parent,title,href,klass='secondary'){const a=el('a',klass,title);a.href=href;parent.append(a);return a;}
function btn(parent,text,callback,klass='chip',pressed=null){const b=el('button',klass,text);b.type='button';if(pressed!==null)b.setAttribute('aria-pressed',String(pressed));b.addEventListener('click',callback);parent.append(b);return b;}
function navigate(params){location.href='./?'+new URLSearchParams(params);}
function clear(){const host=document.querySelector('#app');host.replaceChildren();return host;}
function stageName(i){return ['Étape à préciser','Étape 1','Étape 2','Étape 3','Étape 4'][i]||'';}
function visualPlaceholder(parent,ref,small=false){const item=STATE.visuals.get(ref);if(!item)return null;const approved=STATE.approvedImages.get(ref);if(small&&!approved){const tile=child(parent,'span','visual-tile',item.kind==='symbole'?'✿':item.kind==='diagramme'?'▦':'✦');tile.setAttribute('aria-hidden','true');tile.title=item.alt_fr_CA;return tile;}const fig=child(parent,'figure','visual-placeholder'+(small?' visual-small':''));fig.dataset.visualId=ref;if(approved){const img=child(fig,'img','approved-visual');img.src=approved.path;img.alt=approved.alt_fr_CA||item.alt_fr_CA;img.loading='lazy';return fig;}child(fig,'div','visual-icon',item.kind==='diagramme'?'▦':item.kind==='symbole'?'◈':'✦');child(fig,'div','visual-kicker','Illustration à venir');child(fig,'figcaption','',item.alt_fr_CA);return fig;}
// Couche visuelle déclarée dans chaque Kristal : aucun style ni image générée ici.
function kristalVisual(parent,id,placement,small=false){
 const course=STATE.kristalVisuals.get(id);
 if(!course||!Array.isArray(course.visuels))return false;
 const item=course.visuels.find(x=>x.placement===placement);
 if(!item)return false;
 const fig=child(parent,'figure','kristal-visual'+(small?' kristal-visual-compact':''));
 fig.dataset.kristal=id;fig.dataset.slot=item.slot;
 const missing=child(fig,'div','kristal-prompt');
 const hdr=child(missing,'strong','',small?'Image à venir':'Description de l’image');
 child(missing,'p','kristal-prompt-body',item.alt||item.concept||'Illustration de la notion à venir.');
 // Un manifeste compilé ne publie une URL qu’après la présence et vérification du fichier.
 if(item.url){
  // Ne pas combiner loading="lazy" avec hidden : certains navigateurs ne lancent
  // jamais la requête d'une image masquée, même quand le fichier existe.
  // L'image est chargée hors du DOM et n'est insérée qu'après son chargement.
  const pic=el('img','kristal-visual-img');
  pic.loading='eager';pic.decoding='async';pic.alt=item.alt||item.concept||'Illustration du cours';
  pic.onload=()=>{
   if(!fig.isConnected)return;
   fig.append(pic);fig.classList?.add('has-media');missing.hidden=true;
  };
  pic.onerror=()=>{missing.hidden=false;};
  const version=typeof item.revision==='string'&&/^[a-f0-9]{12,64}$/.test(item.revision)?item.revision:null;
  pic.src=version?item.url+(item.url.includes('?')?'&':'?')+'v='+version:item.url;
 }
 return true;
}
function courseTitle(c){return LABELS[c.id]||c.title;}
function cycle(year){return year<=2?1:year<=4?2:3;}
function coursesFor(year,stage=0,group='Tous'){const g=GROUPS.find(x=>x.name===group)||GROUPS[0];return STATE.catalogue.courses.filter(c=>c.year_suggestion===year && (!stage||c.step_suggestion===stage) && g.test(c));}
function graphAround(id){return {before:STATE.catalogue.links.filter(x=>x.from===id && x.type==='requires').map(x=>x.to),after:STATE.catalogue.links.filter(x=>x.to===id && x.type==='requires').map(x=>x.from)};}
function checkParts(selected,target){return Number.isInteger(selected)&&selected===target;}
function gradeStatusNote(parent){child(parent,'p','hint','Ce classement est proposé pour découvrir les activités. Ton école pourra le confirmer ou le modifier.');}
function breadcrumb(parent,text){const nav=child(parent,'nav','breadcrumbs');nav.setAttribute('aria-label','Fil d’Ariane');link(nav,'← Revenir à mon année','./?annee='+STATE.year,'');child(nav,'span','',` / ${text}`);}
function home(){
 const host=clear();const hero=child(host,'section','hero');const text=child(hero,'div');child(text,'div','eyebrow','Mon école · Mes découvertes');child(text,'h1','','Qu’est-ce qu’on explore aujourd’hui ?');child(text,'p','','Choisis ton année. Tu pourras voir des activités, jouer avec des idées et trouver ce qui vient ensuite.');visualPlaceholder(hero,'accueil-hero');
 child(host,'h2','','Je suis en…');const grid=child(host,'div','grid year-grid');
 for(let y=1;y<=6;y++){const b=btn(grid,'',()=>navigate({annee:y}),'choose-card');visualPlaceholder(b,'annee-'+y,true);const copy=child(b,'span');child(copy,'strong','',LEVELS[y-1]+' année');child(copy,'small','',`${y<=2?'1er':y<=4?'2e':'3e'} cycle`);}
 const tools=child(host,'section','course-intro');child(tools,'h2','','Des petits mondes pour manipuler');child(tools,'p','','Essaie des jetons, des fractions, une droite numérique, des classements et d’autres outils.');link(tools,'🧩 Ouvrir mes outils','./labo/','action');link(tools,'🌱 Micro-mondes approfondis','./mondes-v12/','action');
 const info=child(host,'section','course-intro');child(info,'h2','','Tu préfères explorer une carte ?');child(info,'p','','Regarde ce que tu peux apprendre avant et après une activité.');link(info,'🧭 Voir la carte','./?vue=carte','action');gradeStatusNote(host);
}
function yearHome(year){
 STATE.year=year;STATE.stage=Number(query().get('etape')||0);STATE.group=query().get('groupe')||'Tous';STATE.more=query().get('plus')==='1';const host=clear();link(host,'← Choisir une autre année','./','secondary');
 child(host,'p','eyebrow',`Cycle ${cycle(year)} · ${LEVELS[year-1]} année`);child(host,'h1','','Tes découvertes');child(host,'p','','Choisis une matière ou une période. Chaque carte représente une activité à explorer.');
 child(host,'h2','','Quelle période ?');const srow=child(host,'div','filter-row');for(let s=0;s<=4;s++)btn(srow,s===0?'Toutes les étapes':stageName(s),()=>navigate({annee:year,etape:s,groupe:STATE.group}), 'chip',s===STATE.stage);
 child(host,'h2','','Qu’est-ce qui te tente ?');const grow=child(host,'div','filter-row');for(const g of GROUPS)btn(grow,`${g.icon} ${g.name}`,()=>navigate({annee:year,etape:STATE.stage,groupe:g.name}),'chip',g.name===STATE.group);
 const courses=coursesFor(year,STATE.stage,STATE.group),shown=STATE.more?courses:courses.slice(0,9);child(host,'p','small',`${courses.length} activités proposées pour ces choix.`);
 if(!shown.length){const box=child(host,'section','activity');child(box,'h2','','Pas encore d’activité ici');child(box,'p','','Essaie une autre matière ou une autre période.');btn(box,'Voir toutes les activités',()=>navigate({annee:year}),'action');}
 else {const grid=child(host,'div','lesson-grid');for(const course of shown){const a=link(grid,'','./?cours='+encodeURIComponent(course.id),'lesson-card');a.textContent='';const top=child(a,'div');if(!kristalVisual(top,course.id,'decouvrir',true))visualPlaceholder(top,'cours-'+course.id,true);child(top,'div','tag',stageName(course.step_suggestion));child(top,'strong','',courseTitle(course));child(top,'span','small',course.subject);child(a,'span','small',(STATE.labV13.get(course.id)||[]).length?'🧩 Atelier d’entraînement lié':'🌱 Découverte accompagnée');child(a,'span','eyebrow','Explorer →');}if(courses.length>9 && !STATE.more)btn(host,`Voir les ${courses.length-9} autres activités`,()=>navigate({annee:year,etape:STATE.stage,groupe:STATE.group,plus:1}),'secondary');}
 gradeStatusNote(host);
}
function fractionGame(parent){
 const sec=child(parent,'section','activity');child(sec,'div','eyebrow','Atelier de manipulation · Démonstration');child(sec,'h2','','Colorie les parts égales !');
 child(sec,'p','lead','Voici un rectangle partagé en cinq parts égales. Peux-tu en colorier deux ?');visualPlaceholder(sec,'fractions-2-sur-5',true);
 const row=child(sec,'div','challenge-tiles');const cells=[],chosen=new Set();const feedback=child(sec,'div','feedback','Choisis deux cases en appuyant dessus.');feedback.setAttribute('role','status');
 for(let i=0;i<5;i++){const b=btn(row,'□',()=>{if(chosen.has(i)){chosen.delete(i);b.setAttribute('aria-pressed','false');b.textContent='□';}else{chosen.add(i);b.setAttribute('aria-pressed','true');b.textContent='■';}feedback.textContent=`Tu as colorié ${chosen.size} part${chosen.size>1?'s':''} sur 5.`;},'fraction-cell',false);b.setAttribute('aria-label',`Part ${i+1} sur cinq`);cells.push(b);}
 btn(sec,'Vérifier mon dessin',()=>{feedback.textContent=checkParts(chosen.size,2)?'Bravo ! 2 parts colorées sur 5, c’est 2/5. Essaie maintenant de l’expliquer avec tes mots.':'Observe ton rectangle : il faut exactement 2 parts colorées sur 5.';},'action');
 const more=child(sec,'section','course-intro');child(more,'h3','','Et avec des jetons ?');child(more,'p','','Dix jetons forment le tout. Deux cinquièmes, c’est quatre jetons. Voici quatre jetons coloriés sur dix.');const tokens=child(more,'div','challenge-tiles');for(let i=0;i<10;i++){const t=child(tokens,'span','domain-icon',i<4?'●':'○');t.setAttribute('aria-label',i<4?'Jeton colorié':'Jeton non colorié');}
 child(sec,'p','small','Cette manipulation aide à comprendre les fractions. Elle ne remplace pas les deux preuves de maîtrise prévues dans le Kristal.');
}
function genericExperience(parent,c){const section=child(parent,'section','activity');child(section,'h2','','Une activité à concevoir');child(section,'p','lead',c.objective);child(section,'p','','Aucun exercice avec validation objective n’est encore associé à ce Kristal. La personne enseignante peut préparer une activité spécifique à cette compétence.');}
function restoreNotebook(){try{const entries=JSON.parse(sessionStorage.getItem('ekole_carnet_v8')||'[]');STATE.notebook=Array.isArray(entries)?entries.filter(x=>x&&STATE.byId.has(x.id)).slice(0,202):[];}catch(_){STATE.notebook=[];}}
function rememberCourse(c){if(!STATE.notebook.some(x=>x.id===c.id))STATE.notebook.push({id:c.id,title:courseTitle(c),at:new Date().toLocaleTimeString('fr-CA',{hour:'2-digit',minute:'2-digit'})});try{sessionStorage.setItem('ekole_carnet_v8',JSON.stringify(STATE.notebook));}catch(_){}}

function notebookPage(){const host=clear();child(host,'p','eyebrow','Mon carnet de découvertes');child(host,'h1','','Ce que j’ai exploré');child(host,'p','','Ce carnet ne donne pas de notes. Il fonctionne seulement dans cet onglet et se vide quand tu fermes la session.');if(!STATE.notebook.length){child(host,'section','activity','Ton carnet est encore vide. Ouvre une activité et sélectionne « J’ai essayé » pour commencer.');}for(const c of STATE.notebook){const item=child(host,'div','carnet-card');link(item,'🌟 '+c.title,'./?cours='+c.id,'secondary');child(item,'p','tiny','Exploré vers '+c.at+'. Ce n’est pas une preuve de maîtrise.');}if(STATE.notebook.length)btn(host,'Effacer mon carnet',()=>{STATE.notebook=[];try{sessionStorage.removeItem('ekole_carnet_v8');}catch(_){}notebookPage();},'secondary');}
function coursePage(id){const c=STATE.byId.get(id);if(!c){home();return;}STATE.year=c.year_suggestion;const host=clear();const back=child(host,'div','breadcrumbs');link(back,'← Mon année','./?annee='+c.year_suggestion,'secondary');const head=child(host,'section','lesson-head');child(head,'p','eyebrow',(ICONS[c.subject]||'✨')+' '+c.subject+' · '+LEVELS[c.year_suggestion-1]+' année · placement à confirmer');child(head,'h1','',courseTitle(c));const exp=STATE.experiences.get(c.id);const activity=STATE.activities.get(c.id)||{activite_type:'reflexion',consigne_courte:'Activité guidée à concevoir pour cette compétence.'};
 const courseToolsLink='./labo/?cours='+encodeURIComponent(id)+'&annee='+c.year_suggestion;const steps=[['decouvrir','🔎 Découvrir'],['essayer','👐 Essayer'],['expliquer','💬 Expliquer'],['explorer','🧭 Explorer']];
 const player=child(host,'section','lesson-player');const tabs=child(player,'div','lesson-progress');tabs.setAttribute('role','group');tabs.setAttribute('aria-label','Étapes de découverte');const content=child(player,'div','step-area');const tabButtons=[];
 function show(step){content.replaceChildren();tabButtons.forEach((b,i)=>b.setAttribute('aria-pressed',String(steps[i][0]===step)));const h=child(content,'div','eyebrow','Une découverte à la fois');
 if(step==='decouvrir'){child(content,'h2','','Ce que nous allons découvrir');const intro=child(content,'section','course-intro');if(!kristalVisual(intro,id,'decouvrir'))visualPlaceholder(intro,'cours-'+id,true);child(intro,'p','lead',c.objective);if(exp){child(intro,'h3','',exp.phases.decouvrir.titre_enfant);child(intro,'p','lead',exp.phases.decouvrir.consigne_enfant);}child(content,'p','','Observe cette idée. Peux-tu reconnaître un objet, un geste ou une situation qui pourrait t’aider à la comprendre ?');btn(content,'🔊 Écouter l’idée',()=>{if('speechSynthesis'in window){speechSynthesis.cancel();const u=new SpeechSynthesisUtterance(c.objective);u.lang='fr-CA';u.rate=.85;speechSynthesis.speak(u);}},'secondary');}
 if(step==='essayer'){const lab=child(content,'section','course-intro');link(lab,'🧩 Ouvrir ma boîte à outils pour ce cours',courseToolsLink,'secondary');kristalVisual(lab,id,'essayer');if(exp){const mondes=STATE.mondesV12.get(id)||[];if(mondes.length){const labs=child(lab,'section','course-intro');child(labs,'h3','','Mes micro-mondes approfondis');child(labs,'p','', 'Des manipulations à vérifier, pas des examens.');for(const monde of mondes)link(labs,'🌱 '+monde.title,'./mondes-v12/?id='+encodeURIComponent(monde.id),'action');}child(lab,'h2','',exp.phases.essayer.titre_enfant);child(lab,'p','lead',exp.phases.essayer.consigne_enfant);for(const tool of (STATE.labV13.get(id)||[])){link(lab,'🧩 '+tool.title,'./labo/?outil='+encodeURIComponent(tool.id)+'&annee='+c.year_suggestion+'&cours='+encodeURIComponent(id),'action');}if(!(STATE.labV13.get(id)||[]).length&&!mondes.length)child(lab,'p','', 'Cette tâche se fait avec une personne enseignante. Aucun correcteur automatique ne prétend juger cette réalisation.');child(lab,'p','small','Proposition en révision · Entraînement uniquement · Aucun résultat de maîtrise.');}else{const tools=STATE.labV13.get(id)||[];child(lab,'h3','','Mes outils pour cette notion');if(tools.length){child(lab,'p','','Ces entraînements correspondent à certains gestes de la compétence. Ils ne remplacent pas l’objectif complet du Kristal.');for(const tool of tools)link(lab,'🧩 '+tool.title,'./labo/?outil='+encodeURIComponent(tool.id)+'&annee='+c.year_suggestion+'&cours='+encodeURIComponent(id),'action');}else{child(lab,'p','','Aucun outil à validation objective n’est encore lié à ce cours. Une nouvelle activité sera conçue à partir des critères du Kristal.');}child(lab,'p','small','Pas de question ouverte à écrire, ni exercice de niveau débutant attribué automatiquement.');}}
 if(step==='expliquer'){const tools=STATE.labV13.get(id)||[];child(content,'h2','','Je vérifie ce que j’ai compris');if(exp){child(content,'h2','',exp.phases.expliquer.titre_enfant);child(content,'p','small','Cette étape demande un échange accompagné; aucun champ libre ni score automatique.');}if(tools.length){child(content,'p','lead','Choisis une manipulation vérifiable, puis demande une explication plus longue si nécessaire.');for(const tool of tools)link(content,'🧩 '+tool.title,'./labo/?outil='+encodeURIComponent(tool.id)+'&annee='+c.year_suggestion+'&cours='+encodeURIComponent(id),'action');}else if(tools.length){child(content,'p','lead','Choisis un défi qui correspond à cette notion. Tu peux déplacer, classer ou associer des éléments; aucun texte libre à saisir.');for(const tool of tools)link(content,'🧩 '+tool.title,'./labo/?outil='+encodeURIComponent(tool.id)+'&annee='+c.year_suggestion+'&cours='+encodeURIComponent(id),'action');}else{child(content,'p','lead','Le Kristal décrit l’objectif, mais il manque encore une activité structurée dont le système peut vérifier la réponse.');child(content,'p','small','Cette étape est en attente de conception pédagogique; aucune réussite automatique n’est accordée.');}}
 if(step==='explorer'){child(content,'h2','','Les idées se relient');if(exp){child(content,'h3','',exp.phases.explorer.titre_enfant);child(content,'p','lead',exp.phases.explorer.consigne_enfant);}kristalVisual(content,id,'explorer');const graph=graphAround(c.id);if(!graph.before.length&&!graph.after.length)child(content,'p','','Tu peux continuer à explorer les matières de ton année.');for(const [label,refs] of [['Avant, tu peux revoir…',graph.before],['Ensuite, pourquoi pas…',graph.after]]){if(!refs.length)continue;child(content,'h3','',label);const row=child(content,'div','step-action');for(const dep of refs.slice(0,4)){const d=STATE.byId.get(dep);if(d)link(row,courseTitle(d),'./?cours='+d.id,'secondary');}}link(content,'🧭 Toute la carte','./?vue=carte&cours='+id,'action');}
 const nav=child(content,'div','step-action');const i=steps.findIndex(x=>x[0]===step);if(i>0)btn(nav,'← Avant',()=>show(steps[i-1][0]),'secondary');if(i<steps.length-1)btn(nav,'Continuer →',()=>show(steps[i+1][0]),'action');}
 for(const [key,name] of steps){const b=btn(tabs,name,()=>show(key),'');b.setAttribute('aria-label','Étape : '+name);tabButtons.push(b);}show('decouvrir');child(host,'p','hint','Cette activité est une exploration, pas un contrôle de maîtrise. Une personne enseignante peut t’accompagner.');}
function mapPage(){const host=clear();child(host,'p','eyebrow','Carte des découvertes');child(host,'h1','','Les idées se relient');child(host,'p','','Certaines activités t’aident à en comprendre d’autres. Ces liens ne sont pas des barrières.');const list=STATE.catalogue.courses.filter(c=>STATE.year?c.year_suggestion===STATE.year:true);const select=child(host,'select');select.setAttribute('aria-label','Choisir une activité à explorer');for(const c of list){const o=child(select,'option','',courseTitle(c));o.value=c.id;}
 visualPlaceholder(host,'carte-concepts',true);const map=child(host,'div','concept-map');function draw(id){map.replaceChildren();const c=STATE.byId.get(id);if(!c)return;const around=graphAround(id);const before=child(map,'div','map-column');child(before,'h3','','Avant');if(!around.before.length)child(before,'p','small','Tu peux commencer ici.');around.before.slice(0,4).forEach(dep=>{const d=STATE.byId.get(dep);if(d)link(before,courseTitle(d),'./?cours='+dep,'map-node');});const center=child(map,'div','map-current',courseTitle(c));const after=child(map,'div','map-column');child(after,'h3','','Après');if(!around.after.length)child(after,'p','small','D’autres découvertes arrivent !');around.after.slice(0,4).forEach(dep=>{const d=STATE.byId.get(dep);if(d)link(after,courseTitle(d),'./?cours='+dep,'map-node');});}
 select.addEventListener('change',()=>draw(select.value));const q=query().get('cours');if(q&&STATE.byId.has(q))select.value=q;else if(STATE.byId.has('qc-pri-ma-012'))select.value='qc-pri-ma-012';draw(select.value);child(host,'p','hint','Carte locale basée sur les relations du graphe pédagogique. Le véritable lecteur Konstellation Light nécessite une collection Kristal v10 publique, épinglée et vérifiée.');
}
async function fetchJSON(path){const r=await fetch(path,{cache:'no-store'});if(!r.ok)throw new Error('Fichier indisponible : '+path);return r.json();}
async function start(){try{const [catalogue,visuels,ateliers,approved,integrations,kristalVisuals,experiences,mondes,labsV13,associationsV14,frameConfig]=await Promise.all([
 fetchJSON('data/eleves/catalogue.json'),fetchJSON('data/visuels_public.json'),fetchJSON('data/eleves/ateliers-v8.json'),fetchJSON('data/assets-manifest.json'),fetchJSON('data/eleves/integrations.json'),fetchJSON('data/kristals-visuels.json'),fetchJSON('data/kristals-experiences.json').catch(()=>({cours:{}})),fetchJSON('mondes-v12/data/catalogue.json').catch(()=>({items:[]})),fetchJSON('labo/data/catalogue.json').catch(()=>({items:[]})),fetchJSON('data/activites-v14.json'),fetchJSON('data/cadres-images.json').catch(()=>({style:'epure',size:'normal'}))]);
 const frameStyles=['epure','carte','galerie','carnet','bandeau','sombre','bordure'];const frameSizes=['compact','normal','grand'];
 document.documentElement.dataset.imageFrame=frameStyles.includes(frameConfig.style)?frameConfig.style:'epure';
 document.documentElement.dataset.imageSize=frameSizes.includes(frameConfig.size)?frameConfig.size:'normal';
 document.documentElement.style.setProperty('--ekole-image-border-color',/^#[0-9a-f]{6}$/i.test(frameConfig.borderColor||'')?frameConfig.borderColor.toLowerCase():'#1e6864');
 if(catalogue.format!=='ekole.student-navigation/0.1'||catalogue.count!==202)throw Error('Catalogue incomplet');if(ateliers.count!==202||!Array.isArray(ateliers.activities))throw Error('Activités incomplètes');STATE.catalogue=catalogue;STATE.byId=new Map(catalogue.courses.map(c=>[c.id,c]));STATE.activities=new Map(ateliers.activities.map(a=>[a.id,a]));STATE.visuals=new Map(visuels.placeholders.map(v=>[v.visual_id,v]));STATE.kristalVisuals=new Map(Object.entries(kristalVisuals.cours||{}));STATE.experiences=new Map(Object.entries(experiences.cours||{}));STATE.mondesV12=new Map();for(const m of mondes.items||[]){const a=STATE.mondesV12.get(m.kristal_id)||[];a.push(m);STATE.mondesV12.set(m.kristal_id,a);}
 STATE.labV13=new Map();STATE.associationsV14=new Map();
 if(associationsV14.format!=='ekole.activities-references/1.0')throw Error('Contrat d’activités v14 absent');
 const specsById=new Map((labsV13.items||[]).map(x=>[x.id,x]));
 for(const [id,associations] of Object.entries(associationsV14.cours||{})){
   const c=STATE.byId.get(id);if(!c)throw Error('Cours inconnu dans associations v14');const list=[];
   for(const assoc of associations){const spec=specsById.get(assoc.id);if(!spec||spec.source_kristal_id!==id||!spec.annees_proposees?.includes(c.year_suggestion))throw Error('Association v14 invalide '+id+'/'+assoc.id);list.push(spec);}
   STATE.labV13.set(id,list);STATE.associationsV14.set(id,associations);
 }

 restoreNotebook();STATE.approvedImages=new Map((approved.assets||[]).filter(a=>/^assets\/images\/[a-z0-9_-]+\.(webp|png)$/.test(a.path)).map(a=>[a.visual_id,a]));
 // Konstellation link is external ONLY after explicit publication approval. The local map always works.
 const k=integrations.konstellation_light;const a=document.querySelector('#konstellationExternal');if(k&&k.enabled===true&&k.verified_collection===true&&typeof k.public_url==='string'&&/^https:\/\//.test(k.public_url)){a.href=k.public_url;a.hidden=false;}
 const q=query();const course=q.get('cours'),year=Number(q.get('annee'));if(course)coursePage(course);else if(q.get('vue')==='carte')mapPage();else if(q.get('vue')==='carnet')notebookPage();else if(Number.isInteger(year)&&year>=1&&year<=6)yearHome(year);else home();}catch(error){const host=clear();child(host,'h1','','Impossible d’ouvrir les découvertes');child(host,'p','',error.message);child(host,'p','','La personne responsable peut reconstruire la vue Élève, puis réessayer.');}}
// Un réglage changé depuis Ekole Enseignant se reflète quand on revient
// à l'onglet Élève, sans devoir reconstruire la fiche ou modifier le Kristal.
async function refreshImageFrameSettings(){
 try{
  const cfg=await fetchJSON('data/cadres-images.json');
  document.documentElement.dataset.imageFrame=['epure','carte','galerie','carnet','bandeau','sombre','bordure'].includes(cfg.style)?cfg.style:'epure';
  document.documentElement.dataset.imageSize=['compact','normal','grand'].includes(cfg.size)?cfg.size:'normal';
  document.documentElement.style.setProperty('--ekole-image-border-color',/^#[0-9a-f]{6}$/i.test(cfg.borderColor||'')?cfg.borderColor.toLowerCase():'#1e6864');
 }catch(_error){} // Préserve le réglage courant hors ligne ou sur ancienne installation.
}
if(typeof window!=='undefined'&&typeof document!=='undefined'){
 window.addEventListener('focus',refreshImageFrameSettings);
 document.addEventListener('visibilitychange',()=>{if(!document.hidden)refreshImageFrameSettings();});
 start();
}
if(typeof module!=='undefined'&&module.exports)module.exports={LEVELS,stageName,cycle,checkParts,ICONS,GROUPS};
