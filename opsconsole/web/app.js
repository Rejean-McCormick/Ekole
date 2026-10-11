'use strict';
const $ = id => document.getElementById(id);
const csrf = document.querySelector('meta[name="ekole-csrf"]').content;
let view = 'dashboard';
let busy = false;
let currentCourse = null;
let deployPlan = null;
const descriptions = {
  dashboard: ['Vue d’ensemble', 'État du dépôt local et actions sûres.'],
  inspector: ['Inspecteur Kristals', 'Contenu, dépendances, banques et livraisons des 202 Kristals.'],
  actions: ['Lanceur d’actions', 'Exécuter les contrôles et produire les projections locales.'],
  deployment: ['Déploiement local', 'Simulation, confirmation et copie vers un dossier statique extérieur.'],
  integrations: ['Connexions', 'État des adaptateurs et des dépôts voisins.'],
  logs: ['Rapports & journal', 'Historique clair des opérations de cette session.']
};
function element(tag, className = '', text = '') {
  const el = document.createElement(tag); el.className = className; el.textContent = text; return el;
}
function notice(message, error = false) {
  const el = $('notice'); el.textContent = message; el.classList.remove('hidden'); el.classList.toggle('error', error);
}
function clearNotice() { $('notice').classList.add('hidden'); }
async function get(path) {
  const response = await fetch(path, {cache:'no-store'});
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || 'Requête échouée');
  return data;
}
async function post(data) {
  const response = await fetch('/api/action', {method:'POST',headers:{'Content-Type':'application/json','X-Ekole-Token':csrf},body:JSON.stringify(data)});
  const value = await response.json();
  if (!response.ok) throw new Error(value.error || 'Action refusée');
  return value;
}
function activate(newView) {
  view = newView;
  for (const section of document.querySelectorAll('.panel')) section.classList.toggle('active', section.id === newView);
  for (const button of document.querySelectorAll('.navbtn')) button.classList.toggle('selected', button.dataset.view === newView);
  const [title, desc] = descriptions[newView]; $('view-title').textContent = title; $('view-description').textContent = desc;
  clearNotice();
  if (newView === 'dashboard') loadOverview();
  if (newView === 'inspector') loadCourses();
  if (newView === 'integrations') loadIntegrations();
  if (newView === 'logs') loadRecords();
}
function statusRow(label, value, warning=false) {
  const row = element('div','status-row'); row.append(element('span','',label),element('b',warning?'warn':'',value)); return row;
}
async function loadOverview() {
  try {
    const {overview:o, git, preview} = await get('/api/overview');
    const cells = [[o.catalog.declared,'Kristals au catalogue'],[o.items,'Items (catalogue)'],[o.relations,'Relations pédagogiques'],[o.portal.pages,'Espaces institutionnels']];
    $('stats').replaceChildren(...cells.map(([count,label])=>{const el=element('div','stat');el.append(element('strong','',String(count)),element('span','',label));return el;}));
    $('health').replaceChildren(
      statusRow('Livraisons présentes',`${o.catalog.folders}/${o.catalog.declared}`),
      statusRow('Site local',o.site.html?'Présent':'Manquant',!o.site.html),
      statusRow('Logo officiel',o.site.logo?'Présent':'Absent',!o.site.logo),
      statusRow('Portail de prévisualisation',preview?'Démarré ici':'À lancer'),
      statusRow('Statut pédagogique','À revoir',true),
      statusRow('Publication GitHub v10','Non activée',true),
      statusRow('Git local',git.repository?`Branche ${git.branch}`:'Non configuré')
    );
  } catch (error) { notice(error.message, true); }
}
async function loadCourses() {
  try {
    const params = new URLSearchParams({q:$('find').value, discipline:$('discipline').value, wave:$('wave').value});
    const result = await get('/api/courses?'+params);
    if ($('discipline').options.length === 1) {
      for (const d of result.disciplines) { const option=element('option','',d);option.value=d;$('discipline').append(option); }
    }
    $('count-results').textContent = `${result.total} Kristals trouvés`;
    const rows = result.courses.map(course=>{
      const row=element('button','course-row');row.type='button';row.dataset.id=course.id;
      row.append(element('span','id',course.id),element('strong','',course.titre));
      if (currentCourse===course.id) row.classList.add('selected');
      row.addEventListener('click',()=>loadCourse(course.id));return row;
    });
    $('course-list').replaceChildren(...rows);
  } catch(error) { notice(error.message,true); }
}
function labelled(label,value) {const p=element('p');const b=element('b','',label+' : ');p.append(b,document.createTextNode(String(value)));return p;}
async function loadCourse(id) {
  try {
    currentCourse=id;
    for (const r of document.querySelectorAll('.course-row')) r.classList.toggle('selected',r.dataset.id===id);
    const data = await get('/api/course?id='+encodeURIComponent(id));
    const record=data.record;
    const host=$('course-detail');host.replaceChildren();
    const head=element('div','detail-head'),heading=element('div');heading.append(element('h2','',record.titre),element('p','hint',record.id+' · '+record.discipline));
    const actions=element('div');const open=element('a','btn','Voir dans Ekole ↗');open.href='http://127.0.0.1:8765/?cours='+encodeURIComponent(id);open.target='_blank';open.rel='noopener noreferrer';actions.append(open);head.append(heading,actions);host.append(head);
    const tags=element('div','tags');[`${data.files.count}/${data.files.expected} fichiers`,`${data.evaluation.items} items`,`${data.evaluation.to_review} à revoir`,`Vague ${record.vague}`].forEach(t=>tags.append(element('span','tag',t)));host.append(tags);
    const grid=element('div','detail-grid'),left=element('div'),right=element('div');
    left.append(element('h3','','Contrat pédagogique'),labelled('Objectif',record.objectif),labelled('Preuve attendue',record.preuve),labelled('Famille',record.family_id),labelled('Préalables',record.prerequis.join(', ')||'Aucun'));
    right.append(element('h3','','Intégrité observée'),labelled('Fichiers manquants',data.files.missing.join(', ')||'Aucun'),labelled('Modes d’évaluation',data.evaluation.modes.join(', ')||'Non disponibles'),labelled('Problèmes repérés',data.issues.join('; ')||'Aucun sur les contrôles locaux'));
    grid.append(left,right);host.append(grid);
    host.append(element('h3','','Relations du graphe'));
    const links=element('ul');for(const rel of data.relations) links.append(element('li','',`${rel.type} → ${rel.to}`));
    if(!data.relations.length)links.append(element('li','','Aucune relation sortante.'));
    host.append(links);
  }catch(error){notice(error.message,true);}
}
function busyState(on) { busy=on;for(const b of document.querySelectorAll('[data-action],#simulate,#apply-deploy')) b.disabled=on; }
async function action(name) {
  if(busy)return;
  busyState(true);clearNotice();
  $('output-note').textContent='Exécution en cours : '+name+'…'; $('command-output').textContent='Patiente pendant l’exécution de la commande autorisée.';
  try {
    const result = await post({action:name});
    $('command-output').textContent=result.output || result.message;
    $('output-note').textContent=`${name} · ${result.ok?'réussi':'échec'} · ${result.seconds??0} s`;
    notice(result.message,result.ok===false);
    if(result.url && name==='preview-start' && result.ok) $('output-note').textContent+=' · '+result.url;
    if(name==='pages-zip'&&result.ok)notice('Export créé localement : dist/ekole-site-preview.zip');
  } catch(error) {
    $('command-output').textContent=error.message; $('output-note').textContent='Action interrompue'; notice(error.message,true);
  } finally { busyState(false); if(view==='dashboard')loadOverview(); }
}
async function simulateDeploy() {
  if(busy)return;
  busyState(true);deployPlan=null;$('apply-box').classList.add('hidden');
  $('deploy-plan').textContent='Simulation en cours…';clearNotice();
  try {
    const target=$('deploy-target').value.trim();
    const result=await post({action:'deploy-dry-run',target});
    $('deploy-plan').textContent=result.output || result.message;
    if(!result.ok)throw new Error(result.message);
    deployPlan={target,plan_id:result.plan_id};$('deploy-confirm').value='';$('apply-box').classList.remove('hidden');
    notice('Simulation terminée. Vérifie le rapport avant de confirmer. Aucun fichier copié.');
  }catch(error){$('deploy-plan').textContent=error.message;notice(error.message,true);}
  finally{busyState(false);}
}
async function applyDeploy() {
  if(busy||!deployPlan)return;
  busyState(true);clearNotice();
  try {
    const result=await post({action:'deploy-local-apply',target:deployPlan.target,plan_id:deployPlan.plan_id,confirmation:$('deploy-confirm').value});
    $('deploy-plan').textContent=result.output || result.message;
    notice(result.message,!result.ok);
    deployPlan=null;$('apply-box').classList.add('hidden');
  }catch(error){notice(error.message,true);}
  finally{busyState(false);}
}
async function loadIntegrations() {
  try{
    const [i,{git}]=await Promise.all([get('/api/integrations'),get('/api/overview')]);
    const host=$('connection-list');host.replaceChildren();
    const known=[['Moodle','Plan JSON seulement, sans écriture'],['SemantiK Architect','Adaptateur non branché'],['Konstellation','Adaptateur non branché'],['Médiathèque','Références seulement'],['GitHub / Framework v10','Qualification et publication non branchées']];
    for(const [name,description] of known){const row=element('div','connection-row');const text=element('div');text.append(element('strong','',name),element('small','',description));row.append(text,element('span','tag','Non activé'));host.append(row);}
    for(const n of i.neighbors){const row=element('div','connection-row');const text=element('div');text.append(element('strong','',n.name),element('small','',n.path));row.append(text,element('span','tag',n.present?'Dossier trouvé':'Non trouvé'));host.append(row);}
    const g=$('git-info');g.replaceChildren();g.append(labelled('Git',git.available?'Installé':'Indisponible'));
    g.append(labelled('Dépôt Git Ekole',git.repository?'Oui':'Non'));
    if(git.repository){g.append(labelled('Branche',git.branch),labelled('Fichiers suivis modifiés',git.changed_tracked_files));}
    g.append(element('p','hint','L’inspection Git est en lecture seule : aucune commande commit, push ou pull.'));
  }catch(error){notice(error.message,true);}
}
async function loadRecords() {
  try{
    const {records}=await get('/api/records');const host=$('records');host.replaceChildren();
    if(!records.length){host.textContent='Aucune opération exécutée durant cette session.';return;}
    for(const r of records){const row=element('div','record-row');const info=element('div');info.append(element('strong','',r.action),element('small','',`${r.at} · ${r.seconds} s · ${r.detail}`));row.append(info,element('span','tag',r.ok?'Réussie':'Échec'));host.append(row);}
  }catch(error){notice(error.message,true);}
}
$('menu').addEventListener('click',e=>{const b=e.target.closest('[data-view]');if(b)activate(b.dataset.view);});
$('refresh').addEventListener('click',()=>activate(view));
for(const button of document.querySelectorAll('[data-action]'))button.addEventListener('click',()=>action(button.dataset.action));
for(const el of ['find','discipline','wave']) $(el).addEventListener(el==='find'?'input':'change',loadCourses);
$('simulate').addEventListener('click',simulateDeploy);
$('apply-deploy').addEventListener('click',applyDeploy);
$('deploy-target').addEventListener('input',()=>{deployPlan=null;$('apply-box').classList.add('hidden');$('deploy-plan').textContent='Une nouvelle simulation est requise.';});
$('reload-logs').addEventListener('click',loadRecords);
activate('dashboard');
