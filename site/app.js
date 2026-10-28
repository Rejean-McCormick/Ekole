'use strict';
// Ekole core : aucune hypothèse sur un curriculum; tout est défini par le paquet externe.
const $ = (s)=>document.querySelector(s);
const elt = (tag,cls='',text)=>{const n=document.createElement(tag);if(cls)n.className=cls;if(text!==undefined)n.textContent=String(text);return n;};
const add = (host,tag,cls='',text)=>{const n=elt(tag,cls,text);host.append(n);return n;};
const base=location.pathname.startsWith('/eleve/')?'/eleve/':'/';
const url=(params)=>base+'?'+new URLSearchParams(params).toString();
const a=(host,text,params,cls='')=>{const n=add(host,'a',cls,text);n.href=url(params);return n;};
const fetchJson=async(path)=>{const r=await fetch(path,{cache:'no-store'});if(!r.ok)throw Error('Ressource indisponible : '+r.status);return r.json();};
let pack, courses=new Map(), paths=new Map(), spek=null, graph=null, activities=null;
const current=()=>new URLSearchParams(location.search);

// Compagnons : démonstration TEXTUELLE locale, sans médias ni profil élève.
// Ne jamais utiliser ce choix pour des droits d'accès, des notes ou de la maîtrise.
const COMPAGNON_THEMES=Object.freeze([
 {id:'quotidien',nom:'Mila',univers:'Le quotidien',sigle:'M'},
 {id:'ferme',nom:'Fermier (provisoire)',univers:'La ferme',sigle:'F'},
 {id:'cosmos',nom:'Explorateur (provisoire)',univers:'Le cosmos',sigle:'C'}
]);
const COMPAGNON_FLAG='ekole-demo-compagnon-active-v2';
const COMPAGNON_CHOICE='ekole-demo-compagnon-choice-v2';
function demoStorage(){try{return window.sessionStorage;}catch(_){return null;}}
function demoCompagnonActif(){
 // Verrou de portée : interface élève + paquet Québec + serveur de bouclage uniquement.
 if(base!=='/eleve/'||pack?.id!=='primaire-qc'||!['127.0.0.1','localhost','::1','[::1]'].includes(location.hostname))return false;
 const storage=demoStorage();if(!storage)return false;
 try{
  const flag=current().get('pilote_compagnon');
  if(flag==='0'){storage.removeItem(COMPAGNON_FLAG);storage.removeItem(COMPAGNON_CHOICE);}
  if(flag==='1')storage.setItem(COMPAGNON_FLAG,'1');
  return storage.getItem(COMPAGNON_FLAG)==='1';
 }catch(_){return false;}
}
function anneeParcours(id){const m=/^annee-([1-6])$/.exec(id||'');return m?Number(m[1]):null;}
function lireCompagnon(){
 if(!demoCompagnonActif())return null;
 try{
  const value=JSON.parse(demoStorage().getItem(COMPAGNON_CHOICE)||'null');
  const theme=COMPAGNON_THEMES.find(t=>t.id===value?.theme);
  return theme&&Number.isInteger(value.annee)&&value.annee>=1&&value.annee<=6?{...theme,annee:value.annee}:null;
 }catch(_){return null;}
}
function niveauPage(){
 const q=current();const path=q.get('parcours')||q.get('retour')||(q.get('cours')?getPathFor(q.get('cours')):'');
 return anneeParcours(path)||lireCompagnon()?.annee||3;
}
function enregistrerCompagnon(theme,annee){
 if(!demoCompagnonActif()||!COMPAGNON_THEMES.some(t=>t.id===theme)||!Number.isInteger(annee)||annee<1||annee>6)return;
 try{demoStorage().setItem(COMPAGNON_CHOICE,JSON.stringify({theme,annee}));}catch(_){/* stockage bloqué : aucune sauvegarde */}
}
function synchroniserNiveau(){
 const choisi=lireCompagnon();if(!choisi)return;
 const q=current(),path=q.get('parcours')||q.get('retour')||(q.get('cours')?getPathFor(q.get('cours')):'');
 const grade=anneeParcours(path);
 if(grade&&grade!==choisi.annee)enregistrerCompagnon(choisi.id,grade);
}
function choixCompagnon(root){
 if(!demoCompagnonActif())return;
 const choisi=lireCompagnon(),grade=niveauPage();
 const section=add(root,'section','compagnon-choix');section.setAttribute('aria-label','Choix facultatif du compagnon de démonstration');
 add(section,'h2','','Choisis un compagnon (facultatif)');
 add(section,'p','compagnon-note','Prototype local sans illustrations. Personnages provisoires, sans collecte ni suivi individuel.');
 const niveau=add(section,'label','compagnon-niveau-label','Année scolaire');
 const select=add(niveau,'select','compagnon-niveau');
 for(let i=1;i<=6;i++){const option=add(select,'option','',`${i}${i===1?'re':'e'} année`);option.value=String(i);option.selected=i===grade;}
 const grid=add(section,'div','compagnon-options');
 for(const theme of COMPAGNON_THEMES){
  const bouton=add(grid,'button','compagnon-option'+(choisi?.id===theme.id?' compagnon-selected':''));
  bouton.type='button';bouton.setAttribute('aria-pressed',choisi?.id===theme.id?'true':'false');
  add(bouton,'span','compagnon-sigle',theme.sigle).setAttribute('aria-hidden','true');
  add(bouton,'strong','',theme.nom);add(bouton,'span','compagnon-univers',theme.univers);
  bouton.addEventListener('click',()=>{enregistrerCompagnon(theme.id,Number(select.value));render();});
 }
 select.addEventListener('change',()=>{if(choisi){enregistrerCompagnon(choisi.id,Number(select.value));render();}});
 const actions=add(section,'div','compagnon-actions');
 const sans=add(actions,'button','compagnon-sans','Continuer sans compagnon');sans.type='button';
 sans.addEventListener('click',()=>{try{demoStorage()?.removeItem(COMPAGNON_CHOICE);}catch(_){}render();});
 a(actions,'Quitter la démonstration',{page:'parcours',pilote_compagnon:'0'},'compagnon-sortie');
}
function presenterCompagnon(root,message){
 const choisi=lireCompagnon();if(!choisi)return;
 const grade=niveauPage();
 const box=add(root,'section','compagnon-apercu');box.setAttribute('aria-label','Compagnon textuel de démonstration');
 add(box,'span','compagnon-sigle',choisi.sigle).setAttribute('aria-hidden','true');
 const words=add(box,'div','compagnon-mots');
 add(words,'strong','',`${choisi.nom} · ${grade}${grade===1?'re':'e'} année`);
 add(words,'p','compagnon-message',message).setAttribute('aria-live','polite');
 add(words,'small','compagnon-note','Prototype local sans image · Ne représente pas une évaluation');
}
function reactionCompagnon(reussite){
 if(!lireCompagnon())return;
 const message=document.querySelector('.compagnon-message');
 if(message)message.textContent=reussite?'Bravo, tu as trouvé cette réponse.':'Tu peux réessayer en utilisant les indices.';
}
function compatible(p){return p.format==='ekole.content-pack/0.1'&&Array.isArray(p.cours)&&Array.isArray(p.parcours);}
function getPathFor(id){
 // En démo, garder le niveau déjà choisi lorsque le cours appartient à plusieurs parcours.
 const choice=lireCompagnon();
 if(choice){const preferred=paths.get('annee-'+choice.annee);if(preferred?.cours_ids.includes(id))return preferred.id;}
 return pack.parcours.find(p=>p.cours_ids.includes(id))?.id||'';
}
function ctxLink(c,retour='',extra={}){return {cours:c,...(retour?{retour}:{}),...extra};}
function activeReturn(q,c){const target=q.get('retour');return target&&paths.get(target)?.cours_ids.includes(c)?target:getPathFor(c);}
function crumb(host,parts){const nav=add(host,'nav','breadcrumbs');nav.setAttribute('aria-label','Fil d’Ariane');parts.forEach((p,i)=>{if(i)add(nav,'span','divider-crumb','›');if(p.url){const x=add(nav,'a','',p.text);x.href=p.url;}else add(nav,'span','crumb-current',p.text);});}
function pill(host,title){add(host,'span','chip',title);}
function heading(host,title,lead='',eyebrow=''){if(eyebrow)add(host,'p','eyebrow',eyebrow);add(host,'h1','page-heading',title);if(lead)add(host,'p','intro',lead);}
function buttonlink(host,label,params,cls='button-link'){return a(host,label,params,cls);}
function card(host,c,retour=''){
 const x=a(host,'',ctxLink(c.id,retour),'card');const meta=add(x,'div','card-meta');pill(meta,c.discipline);
 add(x,'strong','card-title',c.titre);add(x,'p','card-description',c.objectif||'Objectif à préciser');add(x,'span','card-next',c.publication_eleve?'Découvrir la leçon →':'Leçon élève en préparation →');
 return x;
}
function grouping(ids){const by=new Map();for(const id of ids){const c=courses.get(id);if(!c)continue;const k=c.discipline||'Autres';if(!by.has(k))by.set(k,[]);by.get(k).push(c);}return [...by.entries()].sort((a,b)=>a[0].localeCompare(b[0],'fr'));}
function pathsHome(root){
 heading(root,'Choisir un parcours','Choisis ton niveau pour retrouver les leçons disponibles.');
 choixCompagnon(root);
 const list=add(root,'div','path-cards');const featured=pack.parcours_mis_en_avant;
 const all=[...pack.parcours].sort((x,y)=>(x.id===featured?-1:0)-(y.id===featured?-1:0));
 for(const p of all){const x=a(list,'',{parcours:p.id},'path-card');add(x,'span','eyebrow',p.id===featured?'À découvrir':'Parcours');add(x,'strong','',p.titre);add(x,'span','hint',p.cours_ids.length+' cours');}
 if(!pack.parcours.length)add(root,'p','empty','Aucun parcours disponible dans ce dépôt.');
}
function home(root){
 const featured=paths.get(pack.parcours_mis_en_avant);
 if(featured){crumb(root,[{text:'Accueil'}]);heading(root,`Bonjour, bienvenue dans ${pack.nom}`,'Commence par choisir une activité ou retrouve ton parcours.');
 presenterCompagnon(root,'Salut ! Découvrons une notion à ton rythme.');
 const hero=add(root,'section','feature-hero');add(hero,'span','eyebrow','Parcours mis en avant');add(hero,'h2','',featured.titre);
 add(hero,'p','',`${featured.cours_ids.length} cours organisés par matière. Tu peux explorer une notion à ton rythme.`);
 buttonlink(hero,`Explorer la ${featured.titre} →`,{parcours:featured.id},'button-link primary');
 }else heading(root,'Bienvenue',pack.description||'');
 add(root,'h2','section-title','Autres parcours');const grid=add(root,'div','path-cards');for(const p of pack.parcours){if(featured&&p.id===featured.id)continue;const item=a(grid,'',{parcours:p.id},'path-card');add(item,'strong','',p.titre);add(item,'span','hint',`${p.cours_ids.length} cours`);}
 if(!pack.parcours.length)add(root,'p','empty','Aucun parcours n’est encore publié.');
 const disclaimer=add(root,'p','disclaimer',`Contenus : ${pack.statut||'statut non précisé'}. Ce portail ne déclare aucune validation pédagogique.`);
}
function pathPage(root,p){
 crumb(root,[{text:'Accueil',url:'./'},{text:p.titre}]);
 heading(root,p.titre,`${p.cours_ids.length} cours · Choisis une matière, puis une notion.`,'Mon parcours');
 presenterCompagnon(root,'Je t’accompagne pendant ce parcours.');
 if(p.id===pack.parcours_mis_en_avant){const actions=add(root,'div','quick-actions');buttonlink(actions,'Explorer les fiches Spek',{parcours:p.id,vue:'spek'},'button-link');buttonlink(actions,'Carte des connaissances',{parcours:p.id,vue:'carte'},'button-link');}
 const q=current(),v=q.get('vue');if(v==='spek'){renderSpek(root,p);return;}if(v==='carte'){renderGraph(root,null,p.id);return;}
 const featured=(p.cours_ids.length>0&&p.id===pack.parcours_mis_en_avant?(pack.cours_a_decouvrir||[]).filter(id=>p.cours_ids.includes(id)):[]);
 if(featured.length){const section=add(root,'section','featured-lessons');add(section,'h2','section-title','Trois notions pour commencer');
 const grid=add(section,'div','cards');featured.forEach(id=>card(grid,courses.get(id),p.id));}
 add(root,'h2','section-title','Toutes les matières');add(root,'p','hint','Ouvre seulement la matière qui t’intéresse. Les autres restent rangées.');
 const groups=grouping(p.cours_ids.filter(id=>!featured.includes(id)));const chips=add(root,'nav','subject-nav');chips.setAttribute('aria-label','Choisir une matière');
 for(const [domain] of groups){const href=add(chips,'a','subject-chip',domain);href.href='#matiere-'+slug(domain);href.addEventListener('click',()=>{const elem=document.getElementById('matiere-'+slug(domain));if(elem)elem.open=true;});}
 for(const [domain,arr] of groups){const sec=add(root,'details','subject-section');sec.id='matiere-'+slug(domain);
 const summary=add(sec,'summary','section-head');add(summary,'span','subject-title',domain);add(summary,'span','count',arr.length+' cours');
 const grid=add(sec,'div','cards');for(const c of arr)card(grid,c,p.id);
 }
}
function slug(text){return text.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().replace(/[^a-z0-9]+/g,'-');}
function catalog(root){
 const search=$('#search').value.trim().toLocaleLowerCase('fr'),d=$('#domain').value;
 const filtered=pack.cours.filter(c=>(!d||c.discipline===d)&&(!search||[c.titre,c.objectif,c.discipline,c.id].join(' ').toLocaleLowerCase('fr').includes(search)));
 crumb(root,[{text:'Accueil',url:'./'},{text:'Bibliothèque'}]);heading(root,'Bibliothèque',`${filtered.length} cours sur ${pack.cours.length}.`);
 presenterCompagnon(root,'Cherche un sujet qui t’intéresse.');
 const grid=add(root,'div','cards');for(const c of filtered)card(grid,c,getPathFor(c.id));if(!filtered.length)add(root,'p','empty','Aucun cours trouvé. Essaie un autre mot.');
}
async function showApprovedImages(host,cid,index){
 let data;try{data=await fetchJson('/api/visuels/'+encodeURIComponent(cid)+'.json');}catch(_){return;}
 const placement=index<2?'decouvrir':index<4?'explorer':'essayer';
 for(const item of (data.visuels||[]).filter(v=>v.placement===placement)){
  const fig=add(host,'figure','lesson-illustration');const image=add(fig,'img');
  image.src=item.url;image.alt=item.alt||'Illustration';image.loading='lazy';
  add(fig,'figcaption','hint',item.alt||'');
 }
}
async function detail(root,c){
 const q=current(),retour=activeReturn(q,c.id),group=paths.get(retour),mode=q.get('vue');
 crumb(root,[{text:'Accueil',url:'./'},...(group?[{text:group.titre,url:url({parcours:group.id})}]:[{text:'Bibliothèque',url:url({page:'cours'})}]),{text:c.titre}]);
 heading(root,c.titre,c.objectif||'',c.discipline);
 presenterCompagnon(root,mode==='pratique'?'Observe les indices et essaie par toi-même.':'Découvrons cette notion ensemble.');
 const status=add(root,'div','course-status');add(status,'span','small-note',c.publication_eleve?'Leçon pilote · À vérifier avec un enseignant':'Leçon élève en préparation');
 const tabs=add(root,'nav','course-tabs');tabs.setAttribute('aria-label','Explorer la notion');
 [['lecon','La leçon'],...(activities?.activites?.some(x=>x.cours_id===c.id)?[['pratique','Je pratique']]:[]),['spek','Fiches Spek'],['carte','Carte des liens']].forEach(([k,label])=>{const x=a(tabs,label,ctxLink(c.id,retour,k==='lecon'?{}:{vue:k}),'tab'+((mode||'lecon')===k?' selected':''));if((mode||'lecon')===k)x.setAttribute('aria-current','page');});
 if(mode==='pratique'){renderPractice(root,c);return;}if(mode==='spek'){renderSpek(root,group||null,c.id);return;}if(mode==='carte'){renderGraph(root,c.id,retour);return;}
 const summary=add(root,'div','course-objective');add(summary,'strong','','Ce que je vais apprendre');add(summary,'p','',c.objectif||'Objectif non renseigné');
 let data;try{data=await fetchJson('/api/cours/'+encodeURIComponent(c.id)+'.json');}catch(e){add(root,'p','warning',e.message);return;}
 if(data.id!==c.id||!Array.isArray(data.modules)){add(root,'p','warning','Modules indisponibles ou incorrects.');return;}
 if(!data.modules.length){add(root,'p','empty',data.message||'Cette leçon est en préparation pour les élèves.');add(root,'p','hint','Le contenu détaillé et les corrigés restent accessibles uniquement dans l’atelier Enseignant.');return;}
 let index=Math.max(0,data.modules.findIndex(m=>m.id===q.get('module')));const mod=data.modules[index];
 const bar=add(root,'div','stage-top');add(bar,'span','stage-counter',`Étape ${index+1} sur ${data.modules.length}`);
 const jump=add(bar,'label','stage-select-label','Aller à une étape');const select=add(jump,'select','stage-picker');select.setAttribute('aria-label','Choisir une étape du cours');
 for(const [i,m] of data.modules.entries()){const op=add(select,'option','',`${i+1}. ${m.titre}`);op.value=m.id;if(i===index)op.selected=true;}
 select.addEventListener('change',()=>{location.href=url(ctxLink(c.id,retour,{module:select.value}));});
 const progress=add(root,'div','step-progress');progress.setAttribute('role','progressbar');progress.setAttribute('aria-valuemin','1');progress.setAttribute('aria-valuemax',String(data.modules.length));progress.setAttribute('aria-valuenow',String(index+1));progress.setAttribute('aria-label','Étape affichée');add(progress,'span','step-progress-bar').style.width=((index+1)/data.modules.length*100)+'%';
 const panel=add(root,'article','lesson-panel');add(panel,'h2','lesson-title',mod.titre||'Étape');
 await showApprovedImages(panel,c.id,index);
 const note=add(panel,'p','lesson-context','Lis une partie à la fois. Tu peux revenir aux autres étapes avec les boutons ci-dessous.');
 renderMarkdown(panel,mod.texte||'',{course:c.id,retour,moduleIds:data.modules.map(m=>m.id)});
 const controls=add(root,'nav','step-controls');controls.setAttribute('aria-label','Navigation dans les étapes');
 if(index>0)buttonlink(controls,'← Étape précédente',ctxLink(c.id,retour,{module:data.modules[index-1].id}),'button-link');
 else add(controls,'span','hint','Début du cours');
 if(index<data.modules.length-1)buttonlink(controls,'Étape suivante →',ctxLink(c.id,retour,{module:data.modules[index+1].id}),'button-link primary');
 else buttonlink(controls,`← Retour au ${group?group.titre:'catalogue'}`,group?{parcours:group.id}:{page:'cours'},'button-link primary');
 /* Aucune note ni critère enseignant dans l’interface ou le DOM de l’élève. */
}
function introNotice(root,msg){add(root,'p','review-note',msg);}
function renderSpek(root,p,courseId=''){
 const returnPath=p?.id||pack.parcours_mis_en_avant;
 add(root,'h2','section-title','Fiches Spek · propositions');
 if(!spek){add(root,'p','empty','Aucune fiche Spek n’est fournie par ce dépôt.');return;}
 introNotice(root,spek.avertissement||'Fiches à valider.');
 const relevant=spek.semaines.filter(s=>!courseId||s.correspondances.some(c=>c.id===courseId));
 if(!relevant.length){add(root,'p','empty','Aucune fiche Spek reliée à ce cours pour le moment.');if(courseId)buttonlink(root,'Voir toutes les fiches Spek',{parcours:returnPath,vue:'spek'});return;}
 const pick=current().get('fiche');const currentWeek=relevant.find(s=>s.id===pick);
 if(currentWeek){buttonlink(root,'← Toutes les fiches',courseId?ctxLink(courseId,returnPath,{vue:'spek'}):{parcours:returnPath,vue:'spek'},'back-link');
 add(root,'h3','week-heading',currentWeek.titre);
 const content=add(root,'article','spek-sheet');
 for(const [label,key] of [['Objectif','objectif'],['Préalables','prerequis'],['Déroulement','etapes'],['Je fais le point','reflexion']]){
 if(currentWeek[key]?.length){add(content,'h4','',label);const lst=add(content,'ul','');currentWeek[key].forEach(t=>add(lst,'li','',t));}}
 const ul=add(content,'div','spek-related');for(const c of currentWeek.correspondances){const found=courses.get(c.id);
 if(found)buttonlink(ul,'Aller à la leçon : '+found.titre,ctxLink(c.id,returnPath),'button-link');}
 if(currentWeek.limites?.length){const warn=add(content,'p','review-note',currentWeek.limites.join(' '));}
 return;}
 const list=add(root,'div','spek-list');for(const w of relevant){const x=a(list,'',courseId?ctxLink(courseId,returnPath,{vue:'spek',fiche:w.id}):{parcours:returnPath,vue:'spek',fiche:w.id},'spek-item');
 add(x,'strong','',w.titre);add(x,'span','hint',w.objectif[0]||'Voir la fiche');add(x,'span','card-next','Lire la fiche →');}
}
function renderPractice(root,c){
 const activity=activities?.activites.find(x=>x.cours_id===c.id);
 add(root,'h2','section-title','Je pratique');
 introNotice(root,activities?.avertissement||'Activité de démonstration.');
 if(!activity){add(root,'p','empty','Pas encore d’activité interactive pour ce cours.');return;}
 const box=add(root,'section','practice-card');add(box,'h3','',activity.titre);if(activity.consigne)add(box,'p','',activity.consigne);
 if(activity.type==='groupes-egaux'){
  const controls=add(box,'div','manip-controls');const groups=add(controls,'label','', 'Nombre de groupes');const a=add(groups,'input');a.type='range';a.min='1';a.max='7';a.value='3';
  const items=add(controls,'label','','Jetons par groupe');const b=add(items,'input');b.type='range';b.min='1';b.max='7';b.value='4';
  const result=add(box,'p','manip-answer');result.setAttribute('aria-live','polite');const board=add(box,'div','group-board');
  const refresh=()=>{const count=Number(a.value),each=Number(b.value);board.replaceChildren();for(let i=0;i<count;i++){
   const g=add(board,'div','single-group');g.setAttribute('aria-label',`Groupe ${i+1} : ${each} jetons`);for(let j=0;j<each;j++)add(g,'span','token','●');}
   result.textContent=`${count} groupes de ${each} jetons = ${count} × ${each} = ${count*each} jetons`;
  };a.addEventListener('input',refresh);b.addEventListener('input',refresh);refresh();
 }else if(activity.type==='question-choix'){
  add(box,'p','practice-text',activity.texte);add(box,'h4','',activity.question);
  const choices=add(box,'div','choices');const feedback=add(box,'p','feedback');feedback.setAttribute('aria-live','polite');
  activity.choix.forEach((option,i)=>{const btn=add(choices,'button','choice',option);btn.type='button';btn.addEventListener('click',()=>{
   for(const n of choices.querySelectorAll('button'))n.classList.remove('good','bad');btn.classList.add(i===activity.reponse?'good':'bad');
   feedback.textContent=(i===activity.reponse?'Oui, bonne interprétation. ':'Pas tout à fait. Essaie d’utiliser les indices. ')+activity.retroaction;
   reactionCompagnon(i===activity.reponse);
  });});
 }
 add(box,'p','practice-privacy','Cet exercice fonctionne uniquement dans le navigateur; il ne crée ni note ni dossier d’élève.');
}
function renderGraph(root,focus,returnPath=''){
 add(root,'h2','section-title','Carte des liens entre notions');
 introNotice(root,'Aperçu léger alimenté par les relations du dépôt. Ce n’est pas le lecteur Konstellation-Light complet et les relations ne remplacent pas une évaluation.');
 if(!graph){add(root,'p','empty','Aucun graphe associé à ce dépôt.');return;}
 const rel=focus?graph.relations.filter(e=>e.from===focus||e.to===focus):graph.relations.filter(e=>graph.noeuds[e.from]?.dans_parcours_3e&&graph.noeuds[e.to]?.dans_parcours_3e);
 if(focus){const main=add(root,'div','graph-focus');add(main,'strong','',courses.get(focus)?.titre||focus);add(main,'span','hint','Notion en cours');}
 if(!rel.length){add(root,'p','empty','Aucun lien pédagogique documenté pour cette sélection. Ce n’est pas une erreur : le graphe est encore partiel.');return;}
 const grid=add(root,'div','relations');for(const e of rel){const other=focus?(e.from===focus?e.to:e.from):e.to;
 const panel=add(grid,'div','relation-card');let meaning=e.type==='requires'?'Préalable':e.type==='reinforces'?'Renforce':'À explorer';
 if(focus&&e.to===focus&&e.type==='requires')meaning='Notion qui utilise celle-ci';
 add(panel,'span','eyebrow',meaning);const t=courses.get(other);
 if(t)buttonlink(panel,t.titre,ctxLink(other,getPathFor(other)||returnPath),'relation-link');else add(panel,'strong','',other);
 if(!focus)add(panel,'p','relation-caption',(courses.get(e.from)?.titre||e.from)+' → '+(courses.get(e.to)?.titre||e.to));
 if(e.justification)add(panel,'p','hint',e.justification);
 }
}
async function main(){try{
 pack=await fetchJson('/api/pack.json');if(!compatible(pack))throw Error('Paquet non compatible');
 courses=new Map(pack.cours.map(x=>[x.id,x]));paths=new Map(pack.parcours.map(x=>[x.id,x]));
 const data=await Promise.allSettled([fetchJson('/api/integrations/spek.json'),fetchJson('/api/integrations/graphe.json'),fetchJson('/api/integrations/activites.json')]);
 if(data[0].status==='fulfilled'&&data[0].value.format==='ekole.spek-preview/1')spek=data[0].value;
 if(data[1].status==='fulfilled'&&data[1].value.format==='ekole.graph-preview/1')graph=data[1].value;
 if(data[2].status==='fulfilled'&&data[2].value.format==='ekole.activities-preview/1')activities=data[2].value;
 $('#ensemble').textContent=pack.nom;$('#ensembleDescription').textContent=pack.description||'';
 $('#sidebarCount').textContent=pack.cours.length+' cours · '+pack.parcours.length+' parcours';document.title=pack.nom+' — Ekole';
 const sel=$('#domain');for(const d of [...new Set(pack.cours.map(c=>c.discipline))].sort((a,b)=>a.localeCompare(b,'fr'))){const o=add(sel,'option','',d);o.value=d;}
 $('#search').addEventListener('input',()=>{history.replaceState(null,'',url({page:'cours'}));render();});
 $('#domain').addEventListener('change',()=>{history.replaceState(null,'',url({page:'cours'}));render();});
 window.addEventListener('popstate',render);await render();
 }catch(e){const root=$('#main');root.replaceChildren();heading(root,'Chargement impossible');add(root,'p','warning',e.message);}}
async function render(){const root=$('#main');root.replaceChildren();try{synchroniserNiveau();const q=current();const course=q.get('cours'),path=q.get('parcours');
 if(q.get('page')==='missions'){await window.EkoleMissions.render(root);}
 else if(course){const c=courses.get(course);if(!c)throw Error('Cours introuvable');await detail(root,c);}
 else if(path){const p=paths.get(path);if(!p)throw Error('Parcours introuvable');pathPage(root,p);}
 else if(q.get('page')==='cours')catalog(root);else if(q.get('page')==='parcours')pathsHome(root);else home(root);
 }catch(e){heading(root,'Impossible de présenter cette page');add(root,'p','warning',e.message);}}
function escapeHtml(s){return s.replace(/[&<>"']/g,ch=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));}
const moduleNames={'01_':'01','02_':'02','03_':'03','04_':'04','05_':'05','06_':'06'};
function safeHref(dest,context){const value=dest.replace(/&amp;/g,'&').trim();if(!value||/[\u0000-\u001f]/.test(value))return null;
 if(/^https?:\/\//i.test(value)||/^mailto:/i.test(value)){try{const u=new URL(value);return ['https:','http:','mailto:'].includes(u.protocol)?u.href:null;}catch(_){return null;}}
 if(value.startsWith('#')&&/^#[A-Za-z][\w-]*$/.test(value))return value;
 if(context&&/^[A-Za-z0-9_-]+\.md$/i.test(value)){
 const prefix=value.slice(0,2);const found=context.moduleIds.find(x=>x.startsWith(prefix));if(found)return url(ctxLink(context.course,context.retour,{module:found}));
 }
 return null; // legacy attachments and non-published teacher files must not yield broken links
}
function inlineMarkdown(source,context){let html=escapeHtml(source);html=html.replace(/`([^`]+)`/g,'<code>$1</code>')
 .replace(/\*\*([^*]+)\*\*/g,'<strong>$1</strong>').replace(/__([^_]+)__/g,'<strong>$1</strong>')
 .replace(/\*([^*]+)\*/g,'<em>$1</em>');
 html=html.replace(/\[([^\]]+)\]\(([^)]+)\)/g,(_all,label,dest)=>{const href=safeHref(dest,context);return href?`<a href="${escapeHtml(href)}" rel="noopener noreferrer">${label}</a>`:`<span class="unavailable-link" title="Ressource source non publiée dans l’interface">${label} (ressource non disponible ici)</span>`;});
 return html;
}
function isTable(line){return /\|/.test(line)&&/^\s*\|?.*\|.*\|?\s*$/.test(line);}
function splitRow(line){return line.trim().replace(/^\|/,'').replace(/\|$/,'').split('|').map(s=>s.trim());}
function isSep(line){return /^\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?$/.test(line.trim());}
function blockStart(t,next){return !t||/^#{1,6}\s+/.test(t)||/^```/.test(t)||/^>\s?/.test(t)||/^[-*]\s+/.test(t)||/^\d+\.\s+/.test(t)||/^---+$/.test(t)||(isTable(t)&&isSep(next));}
function renderMarkdown(host,text,context){const wrap=add(host,'div','markdown');const lines=text.replace(/\r\n/g,'\n').split('\n');let i=0;
 while(i<lines.length){const t=lines[i].trim(),next=(lines[i+1]||'').trim();if(!t){i++;continue;}
 let match;if((match=t.match(/^(#{1,6})\s+(.*)$/))){const h=add(wrap,'h'+Math.min(6,match[1].length+2));h.innerHTML=inlineMarkdown(match[2],context);i++;continue;}
 if(/^```/.test(t)){i++;const buf=[];while(i<lines.length&&!/^```/.test(lines[i].trim()))buf.push(lines[i++]);if(i<lines.length)i++;add(wrap,'pre','',buf.join('\n'));continue;}
 if(isTable(t)&&isSep(next)){const table=add(wrap,'table');const tr=add(add(table,'thead'),'tr');splitRow(t).forEach(x=>add(tr,'th').innerHTML=inlineMarkdown(x,context));i+=2;const tbody=add(table,'tbody');while(i<lines.length&&isTable(lines[i])){const row=add(tbody,'tr');splitRow(lines[i]).forEach(x=>add(row,'td').innerHTML=inlineMarkdown(x,context));i++;}continue;}
 if(/^[-*]\s+/.test(t)||/^\d+\.\s+/.test(t)){const ordered=/^\d+\./.test(t);const ul=add(wrap,ordered?'ol':'ul');while(i<lines.length && (ordered?/^\s*\d+\.\s+/:/^\s*[-*]\s+/).test(lines[i])){add(ul,'li').innerHTML=inlineMarkdown(lines[i].replace(/^\s*(?:[-*]|\d+\.)\s+/,''),context);i++;}continue;}
 if(/^>\s?/.test(t)){const buf=[];while(i<lines.length&&/^>\s?/.test(lines[i].trim()))buf.push(lines[i++].trim().replace(/^>\s?/,''));add(wrap,'blockquote').innerHTML=inlineMarkdown(buf.join(' '),context);continue;}
 if(/^---+$/.test(t)){add(wrap,'hr');i++;continue;}
 const buf=[];while(i<lines.length&&!blockStart(lines[i].trim(),(lines[i+1]||'').trim())){if(lines[i].trim())buf.push(lines[i].trim());i++;}
 if(buf.length)add(wrap,'p').innerHTML=inlineMarkdown(buf.join(' '),context);else i++;
 }
}
main();
