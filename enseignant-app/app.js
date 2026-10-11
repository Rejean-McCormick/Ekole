const el=(tag,klass='',text)=>{const e=document.createElement(tag);if(klass)e.className=klass;if(text!==undefined)e.textContent=String(text);return e;};
const $=s=>document.querySelector(s);const store={courses:[],visuals:[],kristalVisuals:new Map(),active:null,tab:'cours',search:'',subject:'',year:''};
function add(parent,tag,klass='',text){const e=el(tag,klass,text);parent.append(e);return e;}
async function get(url){const response=await fetch(url,{cache:'no-store',credentials:'same-origin'});if(!response.ok)throw Error('HTTP '+response.status);return response.json();}
function clear(){const x=$('#main');x.replaceChildren();return x;}
function paragraph(parent,text){return add(parent,'p','',text||'Information non disponible');}
// Visible, accessible confirmation; a failed copy is never presented as success.
const copyTimers=new WeakMap();
async function copyImagePrompt(button,text){
 const reset=()=>{button.textContent='Copier le prompt';button.classList.remove('is-copied','copy-failed');};
 const old=copyTimers.get(button);if(old)clearTimeout(old);
 try{
  if(navigator.clipboard?.writeText){await navigator.clipboard.writeText(text);}
  else {
   const tmp=document.createElement('textarea');tmp.value=text;
   tmp.setAttribute('readonly','');tmp.style.position='fixed';tmp.style.left='-9999px';
   document.body.append(tmp);tmp.select();
   try{if(!document.execCommand('copy'))throw Error('Copie non disponible');}
   finally{tmp.remove();}
  }
  button.textContent='✓ Prompt copié !';button.classList.add('is-copied');button.classList.remove('copy-failed');
 }catch(_){button.textContent='Copie impossible — sélectionner le texte';button.classList.add('copy-failed');button.classList.remove('is-copied');}
 copyTimers.set(button,setTimeout(reset,2800));
}
// Stable production code: metadata for the authoring workflow, never an image element.
function imageProductionCode(kristalId,slot){
 return 'EKOLE-IMG-'+String(kristalId).toUpperCase().replace(/[^A-Z0-9-]/g,'-')+'-'+String(slot).toUpperCase().replace(/[^A-Z0-9_-]/g,'-');
}
function promptWithProductionCode(concept,code){
 return String(concept||'').trim()+'\n\n' +
  'RÉFÉRENCE DE PRODUCTION (hors image) : '+code+'\n'+
  'Ce code sert uniquement à identifier le fichier à remettre à Ekole. Ne jamais représenter ce code, cette référence ou une étiquette d’identification dans les pixels de l’image. Ne pas ajouter de filigrane lié à ce code. Les éléments visuels et les mots éventuellement nécessaires à la notion doivent suivre uniquement la description pédagogique ci-dessus.';
}
const IMAGE_ASSET=/^assets\/kristals\/qc-pri-[a-z]+-[0-9]{3}\/[a-z][a-z0-9_-]{1,48}\.(?:webp|png|jpg|jpeg)$/;
// The picture is replaced in its current slot; never destroy the editor or scroll position.
function paintKristalImage(frame,visual,revision='',feedback=null){
 frame.replaceChildren();
 if(!visual.url){add(frame,'p','image-not-installed','Aucune image installée pour cet emplacement.');return;}
 if(!IMAGE_ASSET.test(visual.url)){
  add(frame,'p','image-load-error','Chemin image non valide.');return;
 }
 const waiting=add(frame,'p','image-loading','Chargement de l’image enregistrée…');
 const image=add(frame,'img','kristal-image-current');image.alt=visual.alt||'Illustration du Kristal';
 image.onload=()=>{waiting.remove();if(feedback)feedback.textContent='✓ Image enregistrée et affichée immédiatement. Elle est également disponible dans Ekole Élève au prochain affichage.';};
 image.onerror=()=>{frame.replaceChildren();add(frame,'p','image-load-error','L’image est enregistrée, mais son aperçu ne se charge pas. Réessaie le bouton « Actualiser les images ».');if(feedback)feedback.textContent='Image enregistrée, mais aperçu indisponible. Vérifie le serveur local.';};
 const path='/api/kristal-image/'+visual.url.slice('assets/kristals/'.length);
 image.src=path+(revision?'?v='+encodeURIComponent(revision):'');
}

function label(parent,txt,cls='tag'){return add(parent,'span',cls,txt);}
function filtered(){return store.courses.filter(x=>(!store.subject||x.discipline===store.subject)&&(!store.year||String(x.year_suggestion)===store.year)&&(!store.search||[x.id,x.titre,x.discipline,x.objectif].join(' ').toLocaleLowerCase('fr-CA').includes(store.search)));}
function renderList(){const host=clear();add(host,'h2','','Cours et pratiques');paragraph(host,'Chaque fiche est reliée à un Kristal. Les modules d’enseignement sont réservés à la consultation locale.');const grid=add(host,'div','course-grid');for(const c of filtered()){const btn=add(grid,'button','course-link');btn.type='button';label(btn,c.discipline);add(btn,'strong','',c.titre);add(btn,'small','source',c.id);btn.addEventListener('click',()=>openCourse(c.id));}if(!grid.children.length)add(host,'div','empty','Aucun cours pour cette sélection.');}
function safeInline(txt){return txt.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/\*\*([^*]+)\*\*/g,'<strong>$1</strong>').replace(/`([^`]+)`/g,'<code>$1</code>');}
function renderMarkdown(host,raw){const pre=add(host,'div','textblock');const lines=String(raw||'').split(/\r?\n/);let list=null;for(const line of lines){const t=line.trim();if(!t){list=null;continue;}const h=t.match(/^(#{1,4})\s+(.+)$/);if(h){const e=add(pre,'h'+Math.min(4,h[1].length));e.textContent=h[2];list=null;continue;}const bullet=t.match(/^[-*]\s+(.+)$/);if(bullet){if(!list)list=add(pre,'ul');const li=add(list,'li');li.innerHTML=safeInline(bullet[1]);continue;}const e=add(pre,'p');e.innerHTML=safeInline(t);list=null;}}
async function openCourse(id){store.active=id;const meta=store.courses.find(c=>c.id===id),host=clear();const back=add(host,'button','button secondary','← Retour aux cours');back.onclick=()=>{store.active=null;renderList();};const card=add(host,'section','card');add(card,'h2','',meta.titre);label(card,meta.discipline);paragraph(card,'Objectif : '+meta.objectif);paragraph(card,'Preuve attendue : '+meta.preuve);paragraph(card,'Préalables : '+(meta.prerequis||[]).join(', '));paragraph(card,'Affectation scolaire : proposition à valider, année '+meta.year_suggestion+', étape '+meta.step_suggestion);const nav=add(card,'div','toolbar');const go=add(nav,'a','button secondary','Voir l’activité Élève ↗');go.href='http://127.0.0.1:8765/eleve/?cours='+encodeURIComponent(id);try{const course=await get('/api/course/'+encodeURIComponent(id)+'.json');for(const m of course.modules){const sect=add(host,'section','card');const dt=add(sect,'details');const sm=add(dt,'summary','','Afficher : '+m.titre);const body=add(dt,'div','');renderMarkdown(body,m.texte);}}catch(e){add(host,'div','empty','Impossible de charger ce cours : '+e.message);}if(window.EkolePlansV8)window.EkolePlansV8.show(host,meta);renderKristalVisuals(host,id);try{const plan=await get('/api/experience/'+encodeURIComponent(id)+'.json');renderExperienceV11(host,plan);}catch(_){}const visual=store.kristalVisuals.has(id)?null:store.visuals.find(x=>x.visual_id==='cours-'+id);if(visual){const block=add(host,'section','card');add(block,'h2','','Image à produire pour ce cours');renderVisual(block,visual,true);}}
function renderExperienceV11(host,plan){
 const block=add(host,'section','card');add(block,'h2','','Refonte pédagogique v11 · proposition à valider');
 paragraph(block,plan.alias_enfant+' · '+plan.modalite_evaluation);
 paragraph(block,'Objectif source : '+plan.source.objectif_observable);
 paragraph(block,'Preuve source préservée : '+plan.source.preuve_attendue);
 for(const [key,phase] of Object.entries(plan.progression_enfant)){
  const d=add(block,'details');add(d,'summary','',key+' — '+phase.titre_enfant);
  paragraph(d,phase.consigne_enfant);paragraph(d,'Portée : '+phase.statut_validation);
 }
 const note=add(block,'details');add(note,'summary','','Observer et remédier (enseignant seulement)');
 for(const x of plan.erreurs_et_relances)paragraph(note,x.observation+' → '+x.relance);
 for(const x of plan.limitations)paragraph(note,'Limite : '+x);
 paragraph(block,'Aucune approbation automatique. La banque d’items et le contrat source restent de référence.');
}
function renderKristalVisuals(parent,id){
 const entry=store.kristalVisuals.get(id);
 if(!entry)return;
 const block=add(parent,'section','card');
 add(block,'h2','','Couche visuelle du Kristal');
 paragraph(block,'Descriptions conceptuelles sans style. Dépose ici une image téléchargée depuis ChatGPT; le serveur la dimensionne, la nomme et recompile aussitôt la vue Élève.');
 if(entry.statut_source!=='kristal_disponible')paragraph(block,'ATTENTION : Kristal source manquant. Intentions établies uniquement à partir du catalogue.');
 if(entry.composants_envisages?.length)paragraph(block,'Mini-environnements à examiner : '+entry.composants_envisages.map(x=>x.type).join(', ')+'. Aucune validation pédagogique automatique.');
 if(entry.scenarios_existants?.length)paragraph(block,'Scénarios MiniLab candidats : '+entry.scenarios_existants.map(x=>x.id).join(', '));
 for(const v of entry.visuels){
  const panel=add(block,'div','visual-concept-block');add(panel,'h3','',v.role+' · '+v.slot);
  const picture=add(panel,'div','kristal-current-image');
  paintKristalImage(picture,v);
  const update=add(panel,'button','button secondary image-refresh-button','↻ Actualiser les images');update.type='button';
  update.onclick=async()=>{
   update.disabled=true;
   try{const next=await get('/api/kristal-visuals.json');store.kristalVisuals=new Map(Object.entries(next.cours||{}));const fresh=store.kristalVisuals.get(id)?.visuels?.find(x=>x.slot===v.slot);if(fresh){Object.assign(v,fresh);paintKristalImage(picture,v,String(Date.now()));}}
   catch(e){paragraph(picture,'Actualisation impossible : '+e.message);}finally{update.disabled=false;}
  };
  paragraph(panel,v.prompt);
  const code=imageProductionCode(id,v.slot);
  const reference=add(panel,'p','image-production-code','Code de référence (hors image) : '+code);
  reference.title='L’identifiant est dans le prompt copié, pas dans les pixels de l’illustration.';
  paragraph(panel,'Chemin attendu : '+v.fichier_attendu);
  const copy=add(panel,'button','button secondary','Copier le prompt');copy.type='button';copy.onclick=()=>copyImagePrompt(copy,promptWithProductionCode(v.prompt,code));
  if(window.EkoleImagesV15 && entry.statut_source==='kristal_disponible'){
   window.EkoleImagesV15.attach(panel,id,v.slot,Boolean(v.url),(saved,feedback)=>{
    // Data returned by the server is authoritative. Immediate repaint first.
    v.url=saved.public_url;v.format_reel=saved.file_name.split('.').pop();v.statut='image_disponible';
    paintKristalImage(picture,v,saved.sha256.slice(0,24),feedback);
    // Keep other views consistent without rebuilding this card or losing the preview.
    get('/api/kristal-visuals.json').then(next=>{store.kristalVisuals=new Map(Object.entries(next.cours||{}));}).catch(()=>{});
   },(deleted,feedback)=>{
    v.url=null;v.format_reel=null;v.statut='prompt_visible';
    paintKristalImage(picture,v);
    feedback.textContent='✓ Image effacée du Kristal et de la projection Élève. Une sauvegarde privée a été conservée.';
    get('/api/kristal-visuals.json').then(next=>{store.kristalVisuals=new Map(Object.entries(next.cours||{}));}).catch(()=>{});
   });
  }
  if(v.outils?.length)paragraph(panel,'Outils liés / suggérés (à revoir) : '+v.outils.map(x=>x.id||x.type).join(', '));
 }
}

function renderVisual(parent,v,compact=false){const card=compact?parent:add(parent,'section','card');const head=add(card,'div','visual-head');add(head,'strong','',v.visual_id);label(head,v.kind);const frame=add(card,'div','blank-image');add(frame,'div','','✦ Image non générée');add(frame,'small','',v.aspect_ratio+' · '+v.status);paragraph(card,v.alt_fr_CA);const disclosure=add(card,'details');const sum=add(disclosure,'summary','','Voir le prompt pour DALL·E');const prompt=add(disclosure,'div','prompt',v.prompt_image);const ref=imageProductionCode(v.visual_id||'VISUEL','CONCEPT');add(disclosure,'p','image-production-code','Code de référence (hors image) : '+ref);const b=add(disclosure,'button','button secondary','Copier le prompt');b.type='button';b.addEventListener('click',()=>copyImagePrompt(b,promptWithProductionCode(v.prompt_image,ref)));add(disclosure,'p','subtle','Référence : '+v.source_ref+' · Destiné à : '+v.placement+' · Contrôles : '+v.validation_required.join(', '));if(v.exactness)add(disclosure,'p','intent-note','Diagramme exigeant une exactitude vérifiable : privilégier un SVG programmatique.');}
function showVisuals(){
 const host=clear();add(host,'h2','','Concepts d’images par Kristal');
 paragraph(host,'Les prompts sont alignés sur le contrat et les exemples du Kristal. Aucun style n’est fixé. Si le fichier d’image est absent, le texte est affiché tel quel.');
 const matches=store.courses.filter(c=>store.kristalVisuals.has(c.id) &&
   (!store.subject||store.subject===c.discipline) &&
   (!store.year||String(c.year_suggestion)===store.year) &&
   (!store.search||[c.id,c.titre,c.discipline,c.objectif].join(' ').toLocaleLowerCase('fr-CA').includes(store.search)));
 for(const c of matches.slice(0,12)){
  const title=add(host,'h3','',c.titre+' · '+c.id);
  renderKristalVisuals(host,c.id);
 }
 label(host,'Cours affichés : '+Math.min(12,matches.length)+' / '+matches.length+' — filtrer pour trouver un Kristal','source');
}
function showConnectors(){const host=clear();add(host,'h2','','Ponts vers les outils');
const mini=add(host,'section','card');add(mini,'h3','','Bibliothèque de mini-environnements Ekole');
paragraph(mini,'Neuf moteurs vérifiables et 18 scénarios originaux. Leur association aux Kristals est une proposition à revoir. Chaque outil peut être intégré à une page Élève avec une URL ou un iframe.');
const miniLink=add(mini,'a','button secondary','Ouvrir la boîte à outils Élève ↗');miniLink.href='http://127.0.0.1:8765/eleve/labo/';miniLink.target='_blank';miniLink.rel='noopener noreferrer';
get('/api/labo-catalogue.json').then(d=>{if(!d.items)return;for(const item of d.items){const r=add(mini,'details');add(r,'summary','',item.title+' · '+item.type);paragraph(r,item.instruction);add(r,'p','subtle','Statut : pratique illustrative, pas évaluation officielle');const sample='<iframe title="'+item.title.replaceAll('"','')+'" src="/eleve/labo/?outil='+item.id+'" loading="lazy" style="width:100%;min-height:650px;border:0"></iframe>';const b=add(r,'button','button secondary','Copier le code d’intégration');b.type='button';b.onclick=()=>navigator.clipboard?.writeText(sample);}}).catch(()=>paragraph(mini,'Catalogue non disponible sur le serveur Enseignant.'));
const k=add(host,'section','card');add(k,'h3','','Konstellation Light');paragraph(k,'Le navigateur indépendant utilise des collections Kristal v10 publiques vérifiées. Le site actuel dispose d’une carte locale de relations : ce n’est pas une collection v10 publiée.');const a=add(k,'a','button','Ouvrir la démo locale Konstellation Light ↗');a.href='http://127.0.0.1:4177/';a.target='_blank';a.rel='noopener noreferrer';const q=add(host,'section','card');add(q,'h3','','SemantiK Architect');paragraph(q,'L’orchestrateur de phrases n’est pas connecté dans ce prototype. Les prompts d’image restent une couche distincte de la réalisation linguistique.');const m=add(host,'section','card');add(m,'h3','','Moodle (optionnel)');paragraph(m,'Aucune inscription ni création de cours n’est exécutée. Les 202 Kristals restent sources autonomes; Moodle demeure un service externe possible.');}
function tab(name){store.tab=name;for(const [id,val] of [['#tabCourses','cours'],['#tabVisuals','visuels'],['#tabConnectors','outils']])$(id).classList.toggle('selected',name===val);if(name==='cours')renderList();else if(name==='visuels')showVisuals();else showConnectors();}
(async()=>{try{const [d,v,kv]=await Promise.all([get('/api/index.json'),get('/api/visuals.json'),get('/api/kristal-visuals.json')]);if(!Array.isArray(d.courses)||d.courses.length!==202)throw Error('Catalogue de 202 cours absent');store.courses=d.courses;store.visuals=v.intents;store.kristalVisuals=new Map(Object.entries(kv.cours||{}));const domains=[...new Set(d.courses.map(x=>x.discipline))].sort((a,b)=>a.localeCompare(b,'fr'));for(const x of domains){const o=add($('#subject'),'option','',x);o.value=x;}$('#search').addEventListener('input',e=>{store.search=e.target.value.toLocaleLowerCase('fr-CA');tab(store.tab)});$('#subject').addEventListener('change',e=>{store.subject=e.target.value;tab(store.tab)});$('#year').addEventListener('change',e=>{store.year=e.target.value;tab(store.tab)});$('#tabCourses').onclick=()=>tab('cours');$('#tabVisuals').onclick=()=>tab('visuels');$('#tabConnectors').onclick=()=>tab('outils');tab('cours');}catch(e){const x=clear();add(x,'div','empty','Impossible de démarrer Ekole Enseignant : '+e.message);}})();

window.ekoleRefreshVisualsV15=async()=>{const next=await get('/api/kristal-visuals.json');store.kristalVisuals=new Map(Object.entries(next.cours||{}));if(store.active)await openCourse(store.active);else if(store.tab==='visuels')showVisuals();};
