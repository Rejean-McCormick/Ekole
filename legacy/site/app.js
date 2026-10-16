'use strict';
const $ = selector => document.querySelector(selector);
const node = (tag, className = '', value) => {
  const el = document.createElement(tag);
  if (className) el.className = className;
  if (value !== undefined && value !== null) el.textContent = String(value);
  return el;
};
const box = (tag, className, parent) => {const el = node(tag, className); parent.append(el); return el;};
const link = (value, url, className = '') => {const el = node('a', className, value); el.href = url; return el;};
const route = params => './?' + new URLSearchParams(params).toString();
const labelYear = year => Number(year) === 1 ? '1re année' : `${year}e année`;
const DOMAIN_META = Object.freeze({
  'Mathématique': '🔢', 'Français, langue d’enseignement': '📖', 'Français, langue seconde': '📝',
  'Anglais, langue d’enseignement': '🔤', 'Anglais, langue seconde': '🗣️',
  'Science et technologie': '🔬', 'Géographie, histoire et éducation à la citoyenneté': '🗺️',
  'Arts plastiques': '🎨', 'Art dramatique': '🎭', 'Danse': '💃', 'Musique': '🎵',
  'Éducation physique et à la santé': '🏃', 'Culture et citoyenneté québécoise': '🤝',
  'Intégration linguistique, scolaire et sociale': '🌐'
});
const domainIcon = name => node('span', 'domain-icon', DOMAIN_META[name] || '📘');
const domainLabel = name => {const row=node('span','domain-text');row.append(domainIcon(name),node('span','',name));return row;};
const statusMessage = (parent, value, level='note') => parent.append(node('p',level,value));
let catalogue=null, school=null, placements=null, legacyYearMap={};
let propositions=null;
let proposedIds=new Set();
function applySuggestedPlacements(){
  proposedIds=new Set();
  if(!propositions || propositions.format!=='ekole.parcours-propositions/0.1')return;
  const approvals=new Set();
  for(const ids of Object.values(placements.cours_par_etape))for(const id of ids)approvals.add(id);
  for(const [id,value] of Object.entries(legacyYearMap)) if(value!==null && value!==undefined && value!=='') approvals.add(id);
  const valid=new Set(school.annees.flatMap(x=>school.etapes.map(e=>`annee-${x.niveau}-etape-${e.numero}`)));
  for(const [id,p] of Object.entries(propositions.affectations_proposees||{})){
    if(!lookup.has(id))throw Error(`Cours de proposition inconnu : ${id}`);
    if(!valid.has(p.parcours)||!/^annee-[1-6]-etape-[1-4]$/.test(p.parcours))throw Error(`Parcours proposé invalide : ${id}`);
    if(p.statut!=='proposition_non_validee')throw Error(`Statut de proposition incorrect : ${id}`);
    if(approvals.has(id))continue;
    if(!placements.cours_par_etape[p.parcours])placements.cours_par_etape[p.parcours]=[];
    if(!placements.cours_par_etape[p.parcours].includes(id))placements.cours_par_etape[p.parcours].push(id);
    proposedIds.add(id);
  }
}
function proposalWarning(parent){
  if(proposedIds.size) statusMessage(parent,`${proposedIds.size} cours sont placés provisoirement pour exploration. Répartition pédagogique à réviser : ce n'est ni une affectation officielle ni un verrou Moodle. Les affectations manuelles existantes demeurent prioritaires.`,'proposal-notice');
}

let lookup=new Map();

function getCycle(year) {return school.cycles.find(c => c.annees.includes(Number(year)));}
function getStages(year) {return school.etapes.map(stage => `annee-${year}-etape-${stage.numero}`);}
function stageIds(key) {return placements.cours_par_etape[key] || [];}
function yearFromLegacy(courseId) {
  const value = legacyYearMap[courseId];
  return Number.isInteger(Number(value)) && Number(value)>=1 && Number(value)<=6 && value!==null && value!=='' ? Number(value) : null;
}
function stagePlacements(courseId) {
  const result=[];
  for(const [key, ids] of Object.entries(placements.cours_par_etape)) {
    if(ids.includes(courseId)) {
      const found = /^annee-(\d+)-etape-(\d+)$/.exec(key);
      if(found) result.push({year:Number(found[1]),stage:Number(found[2]),key});
    }
  }
  return result;
}
function courseYears(courseId) {
  const found=new Set(stagePlacements(courseId).map(p => p.year));
  const legacy=yearFromLegacy(courseId);if(legacy)found.add(legacy);
  return [...found].sort((a,b)=>a-b);
}
function yearCourseIds(year) {
  const found=new Set();
  for(const stageKey of getStages(year)) for(const id of stageIds(stageKey))found.add(id);
  for(const [id] of lookup) if(yearFromLegacy(id)===Number(year))found.add(id);
  return [...found].sort();
}
function cycleCourseIds(cycle) {
  return [...new Set(cycle.annees.flatMap(y => yearCourseIds(y)))].sort();
}
function onlyYearWithoutStage(year) {
  const stages=new Set(getStages(year).flatMap(stageIds));
  return yearCourseIds(year).filter(id=>!stages.has(id));
}
function coursePlacementLabel(id) {
  const stages=stagePlacements(id);
  if(stages.length) return stages.map(x=>`${labelYear(x.year)}, étape ${x.stage}`).join(' · ')+(proposedIds.has(id)?' · proposition à valider':'');
  const years=courseYears(id);
  return years.length ? years.map(labelYear).join(' · ')+' · étape à préciser' : 'Année et étape à attribuer';
}
function iconPill(domain){const pill=node('span','subject-pill');pill.append(domainLabel(domain));return pill;}
function renderCourseCards(parent, courses, emptyLabel) {
  if(!courses.length) {statusMessage(parent,emptyLabel||'Aucun cours associé à cette sélection.','empty-state');return;}
  const grid=box('div','cards',parent);
  for(const course of courses) {
    const card=link('',route({cours:course.id}),'card');
    const meta=box('div','meta-row',card);
    meta.append(iconPill(course.discipline),node('span','level-pill',coursePlacementLabel(course.id)));
    card.append(node('small','',course.id),node('strong','',course.titre),node('p','',course.objectif || 'Consulter le contenu du cours'));
    grid.append(card);
  }
}
function coursesByIds(ids){return ids.map(id=>lookup.get(id)).filter(Boolean);}
function filterCourseList(courses) {
  const search=($('#search')?.value||'').trim().toLocaleLowerCase('fr-CA');
  const domain=$('#subject')?.value||'';
  const year=$('#level')?.value||'';
  const stage=$('#stage')?.value||'';
  return courses.filter(course=>{
    if(domain && course.discipline !== domain) return false;
    if(year && !courseYears(course.id).includes(Number(year)))return false;
    if(stage && !stagePlacements(course.id).some(p=>p.stage===Number(stage) && (!year||p.year===Number(year))))return false;
    if(search && ![course.id,course.titre,course.discipline,course.objectif,coursePlacementLabel(course.id)].join(' ').toLocaleLowerCase('fr-CA').includes(search))return false;
    return true;
  });
}
function pageHeader(parent, heading, breadcrumb){
  statusMessage(parent,breadcrumb,'breadcrumbs');
  parent.append(node('h1','',heading));
}
function courseCountBadge(parent, n){parent.append(node('span','count-pill',`${n} cours`));}
function renderCycles(parent) {
  pageHeader(parent,'Parcours scolaires','Ekole / Parcours');
  proposalWarning(parent);
  statusMessage(parent,'Choisis un cycle, puis une année et une étape. Chaque parcours réunit des cours qui y sont explicitement affectés.');
  const grid=box('div','path-grid',parent);
  for(const cycle of school.cycles){
    const item=link('',route({parcours:cycle.id}),'path-card');
    item.append(node('span','eyebrow',cycle.titre),node('h2','',cycle.annees.map(labelYear).join(' + ')));
    statusMessage(item,cycle.fil_conducteur||'Regroupement à qualifier.');
    courseCountBadge(item,cycleCourseIds(cycle).length);grid.append(item);
  }
  const foot=box('div','content',parent);
  foot.append(node('h2','','Bibliothèque des cours'));
  statusMessage(foot,'Les cours demeurent accessibles même lorsqu’ils ne sont pas encore intégrés à un parcours.');
  foot.append(link('Voir tous les cours →',route({page:'cours'}),'inline-link'));
}
function renderYears(parent){
  pageHeader(parent,'Parcours par année','Ekole / Parcours / Années');
  proposalWarning(parent);
  statusMessage(parent,'Chaque année présente quatre étapes pédagogiques Ekole : deux à l’automne et deux pendant la période hiver. Les bulletins officiels du Québec comportent, séparément, trois étapes.');
  const grid=box('div','path-grid',parent);
  for(const year of school.annees){
    const item=link('',route({parcours:year.id}),'path-card');
    const cycle=getCycle(year.niveau);
    item.append(node('span','eyebrow',cycle?.titre||'Cycle à définir'),node('h2','',year.libelle));
    statusMessage(item,'Étapes pédagogiques 1 à 4');courseCountBadge(item,yearCourseIds(year.niveau).length);grid.append(item);
  }
}
function renderPath(parent,id){
  if(id.startsWith('cycle-')){
    const cycle=school.cycles.find(c=>c.id===id);if(!cycle)return renderNotFound(parent,id);
    parent.append(link('← Tous les cycles',route({page:'parcours'})));
    pageHeader(parent,cycle.titre,`Ekole / Parcours / ${cycle.titre}`);
    proposalWarning(parent);
    statusMessage(parent,cycle.fil_conducteur);
    const grid=box('div','path-grid',parent);
    for(const year of cycle.annees){
      const item=link('',route({parcours:`annee-${year}`}),'path-card');
      item.append(node('span','eyebrow',cycle.titre),node('h2','',labelYear(year)));
      statusMessage(item,'Quatre étapes pédagogiques');courseCountBadge(item,yearCourseIds(year).length);grid.append(item);
    }
    return;
  }
  let m=/^annee-(\d+)$/.exec(id);
  if(m){
    const year=Number(m[1]);const cycle=getCycle(year);
    if(!school.annees.some(a=>a.niveau===year))return renderNotFound(parent,id);
    parent.append(link('← '+(cycle?.titre||'Parcours'),route({parcours:cycle?.id||'cycle-1'})));
    pageHeader(parent,`Parcours de ${labelYear(year)}`,`Ekole / ${cycle?.titre||'Cycle'} / ${labelYear(year)}`);
    proposalWarning(parent);
    statusMessage(parent,`Cette année comprend ${school.etapes.length} étapes pédagogiques Ekole : deux à l’automne et deux en hiver. Leurs dates relèvent du calendrier de l’établissement. Les trois bulletins officiels sont une structure distincte.`);
    const grid=box('div','path-grid',parent);
    for(const stage of school.etapes){
      const key=`annee-${year}-etape-${stage.numero}`;
      const item=link('',route({parcours:key}),'path-card');
      item.append(node('span','eyebrow',labelYear(year)),node('h2','',stage.libelle));
      statusMessage(item,`${stage.periode==='automne'?'Automne':'Hiver'} · dates à préciser`);
      courseCountBadge(item,stageIds(key).length);grid.append(item);
    }
    const pending=onlyYearWithoutStage(year);
    if(pending.length){
      const c=box('section','content',parent);
      c.append(node('h2','','Cours de l’année — étape à préciser'));
      renderCourseCards(c,filterCourseList(coursesByIds(pending)),'Aucun cours dans ce filtre.');
    }else statusMessage(parent,'Aucun cours de cette année n’attend une étape dans les affectations actuelles.');
    return;
  }
  m=/^annee-(\d+)-etape-(\d+)$/.exec(id);
  if(m){
    const year=Number(m[1]),stage=Number(m[2]),key=`annee-${year}-etape-${stage}`;
    if(!school.annees.some(a=>a.niveau===year)||!school.etapes.some(s=>s.numero===stage))return renderNotFound(parent,id);
    parent.append(link(`← ${labelYear(year)}`,route({parcours:`annee-${year}`})));
    pageHeader(parent,`${labelYear(year)} — Étape ${stage}`,`Ekole / ${getCycle(year)?.titre||'Cycle'} / ${labelYear(year)} / Étape ${stage}`);
    proposalWarning(parent);
    statusMessage(parent,'Une étape pédagogique est un regroupement de cours planifié par Ekole. Elle n’est pas une étape officielle du bulletin; aucun placement n’est déduit des vagues de rédaction.');
    const selected=filterCourseList(coursesByIds(stageIds(key)));
    renderCourseCards(parent,selected,'Aucun cours validé pour cette étape. Consulte le catalogue des cours ou complète les affectations.');
    parent.append(link('Explorer la bibliothèque de cours →',route({page:'cours'}),'inline-link'));
    return;
  }
  renderNotFound(parent,id);
}
function renderNotFound(parent,id){pageHeader(parent,'Page introuvable',id);parent.append(link('Retour aux parcours',route({page:'parcours'})));}
function renderLibrary(parent){
  pageHeader(parent,'Bibliothèque des cours','Ekole / Cours');
  proposalWarning(parent);
  statusMessage(parent,'La bibliothèque présente des fiches pédagogiques issues des Kristals. Les parcours rassemblent ces cours par étape, année et cycle. Dans Moodle, un cours opérationnel peut regrouper plusieurs Kristals ou avoir plusieurs projections; aucune équivalence 1:1 n’est présumée.');
  const courses=filterCourseList(catalogue.courses);
  const totalUnassigned=catalogue.courses.filter(c=>!courseYears(c.id).length).length;
  statusMessage(parent,`${courses.length} cours affichés sur ${catalogue.courses.length} · ${totalUnassigned} sans attribution, dont ${proposedIds.size} affectations provisoires à valider.`);
  if(!courses.length){
    statusMessage(parent,'Aucun cours affecté à cette sélection. Les affectations pédagogiques aux années et aux étapes n’ont pas encore été approuvées. Tu peux consulter les 202 cours sans filtre.', 'empty-state');
    const btn=node('button','reset-filters','Voir tous les cours');
    btn.type='button';btn.addEventListener('click',()=>{
      for(const name of ['search','subject','level','stage']){const input=$('#'+name);if(input)input.value='';}
      history.replaceState({},'',route({page:'cours'}));dispatch();
    });parent.append(btn);
    return;
  }
  renderCourseCards(parent,courses);
}
function renderDomains(parent){
  pageHeader(parent,'Domaines et matières','Ekole / Domaines');
  proposalWarning(parent);
  const domains=[...new Set(catalogue.courses.map(c=>c.discipline))].sort((a,b)=>a.localeCompare(b,'fr'));
  const grid=box('div','path-grid',parent);
  for(const name of domains){
    const item=link('',route({page:'cours',d:name}),'path-card');
    const label=box('div','domain-heading',item);label.append(domainLabel(name));
    statusMessage(item,'Bibliothèque de cours');
    courseCountBadge(item,catalogue.courses.filter(c=>c.discipline===name).length);
    grid.append(item);
  }
}
function renderHome(parent){
  const hero=box('div','hero',parent);hero.append(node('div','sub','Ekole · École primaire · Québec'));
  hero.append(node('h1','','Apprendre, année après année.'));
  statusMessage(hero,'Les parcours d’étape rassemblent des cours issus des Kristals pédagogiques; les parcours d’année et de cycle regroupent ces ensembles. Les cours Moodle ne sont pas créés automatiquement.');
  proposalWarning(parent);
  const stats=box('div','stats',parent);
  [[catalogue.courses.length,'cours'],[school.cycles.length,'cycles'],[school.annees.length*school.etapes.length,'parcours d’étape structurés']].forEach(([n,label])=>{
    const card=box('div','stat',stats);card.append(node('b','',n),node('span','',label));
  });
  parent.append(node('h2','','Choisir un cycle'));
  const grid=box('div','path-grid',parent);
  for(const cycle of school.cycles){
    const item=link('',route({parcours:cycle.id}),'path-card');
    item.append(node('span','eyebrow',cycle.titre),node('h2','',cycle.annees.map(labelYear).join(' et ')));
    courseCountBadge(item,cycleCourseIds(cycle).length);grid.append(item);
  }
  const panel=box('section','content',parent);
  panel.append(node('h2','','Explorer tous les cours'));
  statusMessage(panel,'Le catalogue demeure complet, même avant l’attribution des cours aux années et aux étapes.');
  panel.append(link('Ouvrir les 202 cours →',route({page:'cours'}),'inline-link'));
}
function renderGenericPage(parent,slug){
  const item=catalogue.pages.find(p=>p.slug===slug);
  if(!item)return renderNotFound(parent,slug);
  pageHeader(parent,item.titre,`Ekole / ${item.titre}`);
  const card=box('section','content',parent);
  for(const sentence of item.utterances)card.append(node('p','sentence',sentence));
  card.append(link('Voir les parcours scolaires →',route({page:'parcours'}),'inline-link'));
}
async function renderCourse(parent,id) {
  const course=lookup.get(id);if(!course)return renderNotFound(parent,id);
  parent.append(link('← Bibliothèque des cours',route({page:'cours'})));
  pageHeader(parent,course.titre,`${course.discipline} / ${course.id}`);
  if(proposedIds.has(id))proposalWarning(parent);
  const info=box('div','content',parent);
  const intro=box('div','meta-row',info);intro.append(iconPill(course.discipline),node('span','level-pill',coursePlacementLabel(id)));
  info.append(node('h2','','Fiche pédagogique · Kristal source'));
  const fields=box('div','summary-grid',info);
  for(const [label,value] of [['Objectif',course.objectif],['Preuve de maîtrise',course.preuve],['Préalables',course.prerequis?.join(', ')||'Aucun préalable strict']]){
    const card=box('div','summary-card',fields);card.append(node('h3','',label),node('p','',value||'Non renseigné'));
  }
  statusMessage(info,'Cette fiche pédagogique est distincte des parcours qui la regroupent. Son contenu demeure à revoir; sa projection en cours Moodle est indépendante et nécessite des correspondances approuvées.');
  const stageRefs=stagePlacements(id);
  if(stageRefs.length) {
    const area=box('div','related-paths',info);
    area.append(node('strong','','Dans les parcours :'));
    for(const ref of stageRefs)area.append(link(`${labelYear(ref.year)} · étape ${ref.stage}`,route({parcours:ref.key}),'inline-link'));
  } else if(courseYears(id).length){
    statusMessage(info,'Affecté à une année, mais aucune étape précise n’a encore été qualifiée.','notice');
  }else statusMessage(info,'Ce cours n’a pas encore été placé dans un parcours d’année ni d’étape.','notice');
  try {
    const response=await fetch(`data/cours/${encodeURIComponent(id)}.json`);
    if(!response.ok)throw Error(`Lecture indisponible (${response.status})`);
    const body=await response.json();
    for(const module of body.modules||[]) {
      const card=box('section','content',parent);
      card.append(node('h2','',module.titre));
      const inner=box('div','course-block',card);
      renderMarkdown(inner,module.texte);
    }
  }catch(error){statusMessage(parent,'Les modules de ce cours ne sont pas disponibles dans cette projection.','notice');}
}
function validateLoadedConfiguration(){
  if(!Array.isArray(school.cycles)||!Array.isArray(school.annees)||!Array.isArray(school.etapes))throw Error('Structure cycles/années/étapes invalide');
  const years=school.annees.map(x=>x.niveau);
  if(years.length!==6||new Set(years).size!==6||!years.every(n=>Number.isInteger(n)&&n>=1&&n<=6))throw Error('Les six années du primaire sont requises');
  if(school.etapes.length!==4||school.etapes.some((e,i)=>e.numero!==i+1 || e.periode!==(i<2?'automne':'hiver')))throw Error('Quatre étapes pédagogiques attendues : deux à l’automne et deux en hiver');
  const occupied=[];
  for(const cycle of school.cycles){
    if(cycle.annees.length<2||cycle.annees.length>3)throw Error('Chaque cycle doit compter deux ou trois années');
    occupied.push(...cycle.annees);
  }
  if(occupied.length!==6||new Set(occupied).size!==6||occupied.some(y=>!years.includes(y)))throw Error('Tous les niveaux doivent appartenir à un cycle unique');
  const keys=new Set(years.flatMap(getStages));
  const groups=placements.cours_par_etape;
  if(!groups || typeof groups!=='object' || Object.keys(groups).some(k=>!keys.has(k)))throw Error('Clés de parcours année-étape invalides');
  // Migration compatible v3 : l'étape 4 absente est ajoutée uniquement en mémoire, jamais écrite à l'insu de l'utilisateur.
  for(const key of keys) if(!Object.prototype.hasOwnProperty.call(groups,key))groups[key]=[];
  if(Object.keys(groups).length!==keys.size)throw Error('24 parcours pédagogiques attendus');
  for(const [key,ids] of Object.entries(groups)) {
    if(!Array.isArray(ids)||new Set(ids).size!==ids.length||ids.some(id=>!lookup.has(id)))throw Error(`Affectations invalides : ${key}`);
  }
}
function populateNavigation(){
  const subjects=[...new Set(catalogue.courses.map(c=>c.discipline))].sort((a,b)=>a.localeCompare(b,'fr'));
  const select=$('#subject');
  for(const subject of subjects){const option=node('option','',`${DOMAIN_META[subject]||'📘'} ${subject}`);option.value=subject;select.append(option);}
  const domains=$('#domainLegend');
  for(const subject of subjects){const a=link('',route({page:'cours',d:subject}),'legend-item');a.append(domainLabel(subject));domains.append(a);}
  const menu=$('#pageLinks');menu.replaceChildren();
  for(const [title,href] of [['Parcours par cycle',route({page:'parcours'})],['Parcours par année',route({page:'annees'})],['Bibliothèque des cours',route({page:'cours'})],['Domaines et matières',route({page:'disciplines'})]]){
    menu.append(link(title,href));
  }
  for(const page of catalogue.pages){
    if(!['annees','parcours','disciplines','accueil','offre'].includes(page.slug))menu.append(link(page.titre,route({page:page.slug})));
  }
}
async function getJSON(file) {
  const response=await fetch(file,{cache:'no-store'});
  if(!response.ok)throw Error(`Chargement impossible : ${file} (${response.status})`);
  return await response.json();
}
function dispatch(){
  const parent=$('#main'); parent.replaceChildren();
  const q=new URL(location.href).searchParams;
  const path=q.get('parcours'), course=q.get('cours'),page=q.get('page');
  if(course){renderCourse(parent,course);return;}
  if(path){renderPath(parent,path);return;}
  if(page==='parcours'){renderCycles(parent);return;}
  if(page==='annees'){renderYears(parent);return;}
  if(page==='cours'){renderLibrary(parent);return;}
  if(page==='disciplines'){renderDomains(parent);return;}
  if(!page || page==='accueil'){renderHome(parent);return;}
  if(page==='offre'){renderLibrary(parent);return;}
  renderGenericPage(parent,page);
}
async function main(){
  const parent=$('#main');parent.replaceChildren();parent.append(node('h1','','Chargement des parcours…'));
  try {
    [catalogue,school,placements]=await Promise.all([
      getJSON('data/index.json'),getJSON('data/organisation-parcours.json'),getJSON('data/parcours-affectations.json').catch(()=>getJSON('data/parcours-affectations.4-etapes.exemple.json'))
    ]);
    try {
      const legacy=await getJSON('data/niveaux-manuel.json');
      legacyYearMap=legacy.levels_by_course||{};
    } catch (_) {legacyYearMap={};}
    if(!Array.isArray(catalogue.courses))throw Error('Catalogue de cours invalide');
    lookup=new Map(catalogue.courses.map(c=>[c.id,c]));
    if(lookup.size!==catalogue.courses.length)throw Error('Le catalogue contient des IDs de cours dupliqués');
    validateLoadedConfiguration();
    propositions=await getJSON('data/parcours-propositions.json').catch(()=>null);
    applySuggestedPlacements();
    populateNavigation();
    const query=new URL(location.href).searchParams;
    if(query.get('d'))$('#subject').value=query.get('d');
    for(const id of ['search','subject','level','stage']){
      $(`#${id}`).addEventListener(id==='search'?'input':'change',()=>{
        const current=new URL(location.href);
        if(current.searchParams.has('cours')||current.searchParams.has('parcours')||current.searchParams.get('page')!=='cours'){
          history.replaceState({},'',route({page:'cours'}));
        }
        dispatch();
      });
    }
    dispatch();
  } catch(error) {
    parent.replaceChildren(); parent.append(node('h1','','Chargement impossible'));
    statusMessage(parent,`Le catalogue ou l’assemblage est invalide : ${error.message}`,'notice');
  }
}


function escapeHtml(s){return s.replace(/[&<>"']/g,ch=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));}
function parseInline(text){let html=escapeHtml(text);html=html.replace(/`([^`]+)`/g,'<code>$1</code>');html=html.replace(/\*\*([^*]+)\*\*/g,'<strong>$1</strong>');html=html.replace(/__([^_]+)__/g,'<strong>$1</strong>');html=html.replace(/\*([^*]+)\*/g,'<em>$1</em>');html=html.replace(/_([^_]+)_/g,'<em>$1</em>');html=html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, (_whole,caption,destination)=>{
    const safe=safeMarkupLink(destination);
    return safe?`<a href="${safe}" rel="noopener noreferrer">${caption}</a>`:caption;
  });return html;}
// Never allow javascript: or other unsafe schemes from Markdown link destinations.
function safeMarkupLink(value) {
  const cleaned=value.replace(/&amp;/g, '&').trim();
  if (!cleaned || /[\u0000-\u001f]/.test(cleaned)) return null;
  try {
    const resolved=new URL(cleaned, document.baseURI);
    if(!['https:', 'http:', 'mailto:'].includes(resolved.protocol))return null;
    return resolved.href.replace(/&/g,'&amp;').replace(/"/g,'&quot;').replace(/</g,'&lt;');
  }catch(_){return null;}
}
function isTableSeparator(line){return /^\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?$/.test(line.trim());}
function isTableRow(line){return /\|/.test(line) && /^\s*\|?.*\|.*\|?\s*$/.test(line);}
function splitTableRow(line){let s=line.trim();if(s.startsWith('|'))s=s.slice(1);if(s.endsWith('|'))s=s.slice(0,-1);return s.split('|').map(x=>x.trim());}
function isBlockStart(line,next){const t=line.trim();return !t||/^#{1,6}\s+/.test(t)||/^```/.test(t)||/^>\s?/.test(t)||/^[-*]\s+/.test(t)||/^\d+\.\s+/.test(t)||/^---+$/.test(t)||(isTableRow(t)&&next&&isTableSeparator(next));}
function renderMarkdown(host,source){const wrap=node('div','markdown');const lines=(source||'').replace(/\r\n/g,'\n').split('\n');let i=0;while(i<lines.length){const line=lines[i],t=line.trim(),next=(i+1<lines.length?lines[i+1].trim():'');if(!t){i++;continue;}let m;if((m=t.match(/^(#{1,6})\s+(.*)$/))){const h=node('h'+m[1].length,'');h.innerHTML=parseInline(m[2]);wrap.append(h);i++;continue;}if(/^```/.test(t)){const buf=[];i++;while(i<lines.length&&!/^```/.test(lines[i].trim())){buf.push(lines[i]);i++;}if(i<lines.length)i++;const pre=node('pre','');pre.textContent=buf.join('\n');wrap.append(pre);continue;}if(isTableRow(t)&&next&&isTableSeparator(next)){const table=node('table',''),thead=node('thead',''),trh=node('tr','');splitTableRow(t).forEach(cell=>{const th=node('th','');th.innerHTML=parseInline(cell);trh.append(th);});thead.append(trh);table.append(thead);i+=2;const tbody=node('tbody','');while(i<lines.length&&isTableRow(lines[i].trim())){const tr=node('tr','');splitTableRow(lines[i]).forEach(cell=>{const td=node('td','');td.innerHTML=parseInline(cell);tr.append(td);});tbody.append(tr);i++;}table.append(tbody);wrap.append(table);continue;}if(/^[-*]\s+/.test(t)){const ul=node('ul','');while(i<lines.length&&/^\s*[-*]\s+/.test(lines[i])){const li=node('li','');li.innerHTML=parseInline(lines[i].replace(/^\s*[-*]\s+/,''));ul.append(li);i++;}wrap.append(ul);continue;}if(/^\d+\.\s+/.test(t)){const ol=node('ol','');while(i<lines.length&&/^\s*\d+\.\s+/.test(lines[i])){const li=node('li','');li.innerHTML=parseInline(lines[i].replace(/^\s*\d+\.\s+/,''));ol.append(li);i++;}wrap.append(ol);continue;}if(/^>\s?/.test(t)){const block=node('blockquote',''),buf=[];while(i<lines.length&&/^\s*>\s?/.test(lines[i])){buf.push(lines[i].replace(/^\s*>\s?/,''));i++;}block.innerHTML='<p>'+parseInline(buf.join(' '))+'</p>';wrap.append(block);continue;}if(/^---+$/.test(t)){wrap.append(node('hr',''));i++;continue;}const buf=[];while(i<lines.length&&!isBlockStart(lines[i],i+1<lines.length?lines[i+1].trim():'')){if(lines[i].trim())buf.push(lines[i].trim());i++;}if(buf.length){const p=node('p','');p.innerHTML=parseInline(buf.join(' '));wrap.append(p);}else{i++;}}host.append(wrap);}
main();
