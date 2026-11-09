'use strict';

window.EkoleLeconsLocales = async (root, {make, button, json, cfg, courseId, renderMarkdown}) => {
 const base = '/api/lecons-locales';
 make(root, 'h2', '', 'Leçons structurées · préparation par parcours');
 make(root, 'p', 'b3-intro', 'Les gabarits et brouillons restent dans l’atelier jusqu’à une revue et une diffusion locale explicites.');
 const controls = make(root, 'div', 'b3-toolbar');
 const pathLabel = make(controls, 'label', '', 'Parcours');
 const paths = make(pathLabel, 'select');
 const courseLabel = make(controls, 'label', '', 'Cours');
 const courses = make(courseLabel, 'select');
 const summary = make(root, 'p', 'b3-note');
 const toolbar = make(root, 'div', 'b3-toolbar');
 const message = make(root, 'p');
 message.setAttribute('role', 'status');
 const panel = make(root, 'section');
 let index = await json(base + '.json');
 let epoch = 0;
 let modified = false;
 const path = () => index.find(row => row.id === paths.value);
 const call = (action, data) => json(base + '/' + action, {method:'POST',
  headers:{'Content-Type':'application/json','X-Ekole-CSRF':cfg.csrf}, body:JSON.stringify(data)});
 for (const row of index) make(paths, 'option', '', row.title).value = row.id;
 const currentPath = index.find(row => row.courses.some(course => course.id === courseId));
 if (currentPath) paths.value = currentPath.id;

 async function refresh(id = courses.value) {
  index = await json(base + '.json');
  await select(id);
 }

 function controlsForPath() {
  toolbar.replaceChildren();
  const row = path();
  const drafts = row.courses.filter(course => course.draft).length;
  const reviewed = row.courses.filter(course => course.reviewed).length;
  const seeded = row.courses.filter(course => course.seeded).length;
  summary.textContent = row.courses.length + ' cours · ' + seeded + ' leçons préremplies · ' +
   drafts + ' brouillons enregistrés · ' + reviewed + ' relus';
  if (!cfg.edition) return;
  button(toolbar, 'Préparer les brouillons du parcours', async event => {
   if (modified) {message.textContent = 'Enregistre les modifications du cours avant de préparer le parcours.';return;}
   const control = event.currentTarget;
   control.disabled = true;
   try {
    const result = await call('prepare', {parcours:row.id});
    await refresh();
    message.textContent = result.created + ' brouillons créés · ' + result.completed +
     ' gabarits intacts complétés. Les brouillons modifiés sont conservés.';
   } catch (error) {message.textContent = error.message;control.disabled = false;}
  }, 'b3-secondary');
  const ready = row.courses.filter(course => course.reviewed);
  if (!ready.length) return;
  const lot = make(toolbar, 'details', 'b3-child-card');
  make(lot, 'summary', '', 'Diffuser un lot de leçons relues');
  const choices = ready.map(course => {
   const label = make(lot, 'label', 'b3-check');
   const input = make(label, 'input');
   input.type = 'checkbox';
   make(label, 'span', '', course.title);
   return [course,input];
  });
  button(lot, 'Diffuser les leçons cochées dans l’espace Élève local', async event => {
   if (modified) {message.textContent = 'Enregistre les modifications du cours avant de diffuser.';return;}
   const selected = choices.filter(([,input]) => input.checked);
   if (!selected.length) {message.textContent = 'Choisis au moins une leçon.';return;}
   if (!window.confirm('Diffuser localement ' + selected.length + ' leçon(s) relue(s) ?')) return;
   const control = event.currentTarget;
   control.disabled = true;
   try {
    const result = await call('publish', {confirmed:true,
     courses:Object.fromEntries(selected.map(([course]) => [course.id,course.revision]))});
    await refresh();
    message.textContent = result.published.length + ' leçon(s) disponible(s) dans l’espace Élève local.';
   } catch (error) {message.textContent = error.message;control.disabled = false;}
  }, 'b3-primary');
 }

 async function select(preferred) {
  const list = path().courses;
  courses.replaceChildren();
  for (const item of list) {
   const state = item.published ? ' · diffusée' : item.reviewed ? ' · relue' :
    item.draft ? ' · brouillon' : item.seeded ? ' · préremplie' : '';
   make(courses, 'option', '', item.title + state).value = item.id;
  }
  if (list.some(item => item.id === preferred)) courses.value = preferred;
  controlsForPath();
  await open();
 }

 async function open() {
  const id = courses.value;
  const current = ++epoch;
  modified = false;
  panel.replaceChildren();
  const response = await json(base + '/' + encodeURIComponent(id) + '.json');
  if (current !== epoch) return;
  make(panel, 'h3', '', response.draft.titre);
  if (response.stale) make(panel, 'p', 'b3-notice', 'La source a changé. Réaligne ce brouillon, puis relis-le de nouveau.');
  const ref = make(panel, 'details', 'b3-child-card');
  make(ref, 'summary', '', 'Repères privés de rédaction');
  make(ref, 'p', '', response.source.objectif_observable);
  make(ref, 'p', '', response.source.preuve_attendue);
  make(ref, 'p', '', (response.source.concepts || []).join(' · '));
  make(ref, 'code', '', response.source.reading);
  const preview = make(panel, 'details', 'b3-child-card');
  make(preview, 'summary', '', 'Aperçu élève privé du brouillon enregistré');
  const previewBody = make(preview, 'div');
  preview.addEventListener('toggle', async () => {
   if (!preview.open) return;
   previewBody.replaceChildren();
   if (modified) {
    make(previewBody, 'p', '', 'Enregistre le brouillon pour revoir les modifications dans cet aperçu.');
    return;
   }
   try {
    const currentPreview = await json(base + '/preview/' + encodeURIComponent(id) + '.json');
    if (currentPreview.revision !== response.revision) throw new Error('Une nouvelle révision existe. Recharge le cours.');
    for (const module of currentPreview.lesson.modules) {
     const card = make(previewBody, 'section', 'b3-child-card');
     make(card, 'h4', '', module.titre);
     renderMarkdown(make(card, 'div', 'b3-markdown'), module.texte);
    }
   } catch (error) { make(previewBody, 'p', 'b3-error', error.message); }
  });
  const href = make(panel, 'a', 'b3-open-child', 'Ouvrir la vue Élève');
  href.href = 'http://127.0.0.1:' + cfg.port_public + '/eleve/?cours=' + encodeURIComponent(id);
  href.target = '_blank'; href.rel = 'noopener noreferrer';
  const edits = response.draft.modules.map((step, index) => {
   const section = make(panel, 'section', 'b3-child-card');
   make(section, 'h4', '', 'Étape ' + (index + 1) + ' · ' + step.kind);
   const label = make(section, 'label', '', 'Titre');
   const title = make(label, 'input', 'b3-title-input');
   title.value = step.titre;
   title.maxLength = 90;
   title.disabled = !cfg.edition || response.stale;
   title.addEventListener('input', () => {modified = true;});
   const blockHost = make(section, 'div');
   const fields = [];
   const appendBlock = (block, focus = false) => {
    const row = make(blockHost, 'div', 'b3-child-card');
    const kindLabel = make(row, 'label', '', 'Type de bloc');
    const kind = make(kindLabel, 'select');
    for (const [key,text] of [['explanation','Explication'],['instruction','Consigne'],['challenge','Défi'],
                             ['hint','Indice'],['reflection','Réflexion']])
     make(kind,'option','',text).value = key;
    kind.value = block.type;
    const textLabel = make(row, 'label', '', 'Texte élève');
    const text = make(textLabel, 'textarea', 'b3-child-source');
    text.value = block.text;
    text.maxLength = 800;
    kind.disabled = text.disabled = !cfg.edition || response.stale;
    for (const field of [kind,text]) field.addEventListener('input', () => {modified = true;});
    const entry = {kind,text};
    fields.push(entry);
    if (cfg.edition && !response.stale) button(row, 'Retirer le bloc', () => {
     if (fields.length <= 1) {message.textContent = 'Garde au moins un bloc par étape.';return;}
     fields.splice(fields.indexOf(entry),1);
     row.remove();
     modified = true;
    }, 'b3-secondary');
    if (focus) text.focus();
   };
   for (const block of step.blocks) appendBlock(block);
   if (cfg.edition && !response.stale) button(section, 'Ajouter un bloc', () => {
    if (fields.length >= 7) {message.textContent = 'Maximum de sept blocs par étape.';return;}
    appendBlock({type:'instruction',text:''},true);
    modified = true;
   }, 'b3-secondary');
   return {step,title,fields};
  });
  if (!cfg.edition) return;
  const bottom = make(panel, 'div', 'b3-publish-box');
  const payload = () => ({course:id, revision:response.revision});
  async function action(event, name, extra, success) {
   const control = event.currentTarget;
   control.disabled = true;
   try {
    await call(name, {...payload(),...extra});
    modified = false;
    if (courses.value === id) await refresh(id);
    message.textContent = success;
   } catch (error) {message.textContent = error.message;control.disabled = false;}
  }
  if (response.stale) {
   button(bottom, 'Réaligner sur la source actuelle', event =>
    action(event,'save',{rebase:true},'Brouillon réaligné. Une nouvelle revue est requise.'), 'b3-primary');
  } else {
   button(bottom, 'Enregistrer le brouillon privé', event => action(event,'save',{
    modules:edits.map(({step,title,fields}) => ({id:step.id,kind:step.kind,titre:title.value,
     blocks:fields.map(({kind,text}) => ({type:kind.value,text:text.value}))}))
   }, 'Brouillon enregistré.'), 'b3-primary');
   if (response.revision) {
    const reviewer = make(make(bottom,'label','','Nom du relecteur'),'input');
    const declaration = make(bottom,'label','b3-check');
    const confirm = make(declaration,'input');confirm.type='checkbox';
    make(declaration,'span','','J’ai relu la totalité du brouillon enregistré et vérifié les contenus privés.');
    button(bottom,'Enregistrer la revue',event => {
     if(modified){message.textContent='Enregistre le brouillon avant la revue.';return;}
     action(event,'review',{reviewer:reviewer.value,confirmed:confirm.checked},'Revue enregistrée. Diffusion locale possible dans le lot.');
    },'b3-secondary');
   }
  }
  if(response.published)button(bottom,'Retirer la diffusion locale',event => {
   if(modified){message.textContent='Enregistre le brouillon avant de retirer la diffusion.';return;}
   if(window.confirm('Retirer la version locale ?'))action(event,'withdraw',{confirmed:true},'Version locale retirée.');
  },'b3-secondary');
 }

 let currentCourse = courseId;
 let activePath = paths.value;
 paths.addEventListener('change',async () => {
  if(modified&&!window.confirm('Changer de parcours sans enregistrer les modifications ?')){paths.value=activePath;return;}
  activePath=paths.value;
  try{await select();currentCourse=courses.value;}catch(error){message.textContent=error.message;}
 });
 courses.addEventListener('change',async () => {
  if(modified&&!window.confirm('Changer de cours sans enregistrer les modifications ?')){courses.value=currentCourse;return;}
  currentCourse=courses.value;
  try{await open();}catch(error){message.textContent=error.message;}
 });
 await select(courseId);
 currentCourse=courses.value;
};
