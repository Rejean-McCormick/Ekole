'use strict';

window.EkoleActivitesEnseignant = (() => {
 const base = '/api/activites-locales/';

 function field(host, make, title, element = 'input') {
  const label = make(host, 'label', '', title);
  const input = make(label, element);
  input.required = true;
  return input;
 }

 async function scenarios(root, {make, json}) {
  make(root, 'h2', '', 'Banque de scénarios Kontexte');
  const entries = await json(base + 'scenarios.json');
  const filter = field(root, make, 'Chercher par titre, famille ou production');
  filter.type = 'search';
  const listing = make(root, 'ul');
  const redraw = () => {
   listing.replaceChildren();
   const search = filter.value.toLocaleLowerCase('fr').trim();
   for (const row of entries) {
    if (![row.id,row.titre,row.famille,row.resultat].join(' ').toLocaleLowerCase('fr').includes(search)) continue;
    const item = make(listing, 'li');
    make(item, 'strong', '', row.titre);
    make(item, 'span', '', ' · ' + row.famille + ' · ' + row.resultat);
   }
  };
  filter.addEventListener('input', redraw);
  redraw();
 }

 async function attempts(root, {make, button, json, cfg}) {
  make(root, 'h2', '', 'Tentatives et revue Inkuisite');
  const listing = make(root, 'div', 'b3-toolbar');
  const panel = make(root, 'section');
  const rows = (await json(base + 'tentatives.json')).filter(row => row.submitted);
  const call = (action, data) => json(base + 'tentatives/' + action, {method: 'POST',
   headers: {'Content-Type': 'application/json', 'X-Ekole-CSRF': cfg.csrf}, body: JSON.stringify(data)});
  if (!rows.length) make(listing, 'p', '', 'Aucune tentative remise.');

  function show(detail) {
   panel.replaceChildren();
   make(panel, 'h3', '', detail.title);
   make(panel, 'p', '', detail.released ? 'Résultat diffusé' : 'Résultat privé');
   if (detail.result.score !== null) make(panel, 'p', '', detail.result.score + ' / ' + detail.result.max_points);
   const rubric = [];
   for (const item of detail.items) {
    const card = make(panel, 'article', 'b3-child-card');
    make(card, 'h4', '', item.prompt);
    const answer = Array.isArray(item.answer) ? item.answer : [item.answer];
    const formatted = answer.filter(value => value !== null).map(value => item.option_labels[value] ?? value);
    make(card, 'p', '', formatted.join(' · ') || 'Réponse vide');
    const decision = detail.result.items.find(row => row.item_id === item.id);
    if (decision?.feedback) make(card, 'p', '', decision.feedback);
    if (item.kind !== 'rubric' || !cfg.edition || detail.released) continue;
    const scoreFields = item.criteria.map(criterion => {
     const input = field(card, make, criterion.description);
     input.type = 'number'; input.min = '0'; input.max = String(criterion.max_points); input.step = 'any';
     return [criterion.id, input];
    });
    rubric.push({id:item.id, scoreFields, reason:field(card,make,'Motif de la décision'),
     evidence:field(card,make,'Observation'), feedback:field(card,make,'Rétroaction à l’élève'),
     next:field(card,make,'Prochaine étape')});
   }
   if (!cfg.edition || detail.released) return;
   const reviewer = field(panel, make, 'Nom du relecteur');
   const message = make(panel, 'p');
   message.setAttribute('role', 'status');
   async function change(event, action, payload) {
    const trigger = event.currentTarget;
    trigger.disabled = true;
    try {
     show(await call(action, {attempt_id:detail.attempt_id,
                             result_digest:detail.result.result_digest, ...payload}));
    } catch (error) { message.textContent = error.message; trigger.disabled = false; }
   }
   if (rubric.length) button(panel, 'Enregistrer la revue', event => {
    const fields = [reviewer, ...rubric.flatMap(item => [item.reason, item.evidence, item.feedback, item.next,
     ...item.scoreFields.map(([,input]) => input)])];
    if (!fields.every(input => input.reportValidity())) return;
    const items = Object.fromEntries(rubric.map(item => [item.id, {reviewer:reviewer.value,
     reason:item.reason.value, evidence:item.evidence.value, feedback:item.feedback.value, next_step:item.next.value,
     criteria_scores:Object.fromEntries(item.scoreFields.map(([id,input]) => [id,input.value]))}]));
    change(event, 'review', {reviews:{format:'inkui.reviews/1.0',attempt_digest:detail.result.attempt_digest,items}});
   }, 'b3-secondary');
   if (!detail.result.pending_count) button(panel, 'Diffuser le résultat', event => {
    if (reviewer.reportValidity()) change(event, 'release', {reviewer:reviewer.value});
   }, 'b3-primary');
  }
  for (const row of rows) {
   const date = new Date(row.created_at).toLocaleString('fr-CA');
   button(listing, date + ' · ' + row.id.slice(0, 8), async () => {
    try { show(await call('inspect', {attempt_id: row.id})); }
    catch (error) { panel.textContent = error.message; }
   }, 'b3-secondary');
  }
 }
 async function coverage(root, {make, button, json, selectCourse}) {
  make(root, 'h2', '', 'Couverture du corpus Québec');
  const rows = await json(base + 'couverture.json');
  const counters = (items, predicate) => items.filter(predicate).length;
  make(root, 'p', 'b3-intro',
       rows.length + ' cours · ' + counters(rows, row => row.lecon_eleve) + ' avec leçon élève · ' +
       counters(rows, row => row.activites.length) + ' avec activité structurée · ' +
       rows.reduce((total, row) => total + (row.variantes || []).length, 0) + ' variantes thématiques · ' +
       counters(rows, row => row.micro_mondes.length) + ' avec micro-monde');
  make(root, 'p', 'b3-note', 'Les compteurs indiquent les ressources présentes. La revue pédagogique est distincte.');
  const search = field(root, make, 'Filtrer par cours, identifiant ou discipline');
  search.type = 'search';
  const filter = field(root, make, 'Ressources', 'select');
  for (const [value, label] of [['all','Tous'],['missing','Aucune ressource élève'],
    ['lesson','Leçon élève'],['activity','Activité structurée'],['world','Micro-monde']]) {
   const option = make(filter, 'option', '', label); option.value = value;
  }
  const summary = make(root, 'p');
  summary.setAttribute('role', 'status');
  const table = make(root, 'table', 'b3-md-table');
  const headers = make(make(table, 'thead'), 'tr');
  for (const text of ['Cours', 'Discipline', 'Leçon', 'Activités', 'Variantes', 'Micro-mondes'])
   make(headers, 'th', '', text).scope = 'col';
  const body = make(table, 'tbody');
  const render = () => {
   const query = search.value.trim().toLocaleLowerCase('fr');
   const kind = filter.value;
   const selected = rows.filter(row => {
    const match = [row.titre, row.id, row.discipline].join(' ').toLocaleLowerCase('fr').includes(query);
    if (!match) return false;
    if (kind === 'missing') return !row.lecon_eleve && !row.activites.length && !row.micro_mondes.length;
    if (kind === 'lesson') return row.lecon_eleve;
    if (kind === 'activity') return row.activites.length;
    if (kind === 'world') return row.micro_mondes.length;
    return true;
   });
   body.replaceChildren();
   summary.textContent = selected.length + ' cours affichés';
   for (const item of selected) {
    const row = make(body, 'tr');
    button(make(row, 'td'), item.titre, () => selectCourse(item.id, 'student'), 'b3-secondary');
    make(row, 'td', '', item.discipline);
    make(row, 'td', '', item.lecon_eleve ? 'Présente' : '—');
    make(row, 'td', '', item.activites.length || '—');
    make(row, 'td', '', item.variantes?.length || '—');
    make(row, 'td', '', item.micro_mondes.length || '—');
   }
  };
  search.addEventListener('input', render);
  filter.addEventListener('change', render);
  render();
 }
 async function banks(root, {make, button, json, cfg, courseId}) {
  make(root, 'h2', '', 'Banques de questions du corpus');
  const overview = await json('/api/banques-locales.json');
  make(root, 'p', 'b3-intro', overview.length + ' banques · ' +
       overview.reduce((total, row) => total + row.items, 0) + ' questions candidates importées');
  make(root, 'p', 'b3-note', 'Les brouillons restent privés. Une question relue peut servir à un essai local avec correction humaine.');
  const select = field(root, make, 'Choisir une banque', 'select');
  for (const row of overview) {
   const option = make(select, 'option', '', row.cours + ' · ' + row.titre);
   option.value = row.cours;
  }
  if (overview.some(row => row.cours === courseId)) select.value = courseId;
  const panel = make(root, 'section');
  let epoch = 0;
  async function load(preferred) {
   const current = ++epoch;
   const cid = select.value;
   panel.replaceChildren();
   const data = await json('/api/banques-locales/' + encodeURIComponent(cid) + '.json');
   if (current !== epoch) return;
   const approved = data.items.filter(item => item.reviewed).length;
   make(panel, 'p', '', approved + ' relues pour essai local sur ' + data.items.length + ' questions');
   const chosen = field(panel, make, 'Question', 'select');
   for (const item of data.items) {
    const label = item.id + ' · ' + (item.reviewed ? 'Relue' : 'À examiner');
    make(chosen, 'option', '', label).value = item.id;
   }
   if (data.items.some(item => item.id === preferred)) chosen.value = preferred;
   const target = make(panel, 'div');
   const render = () => {
    target.replaceChildren();
    const item = data.items.find(row => row.id === chosen.value);
    make(target, 'h3', '', item.id);
    make(target, 'p', '', item.prompt);
    const original = make(target, 'details', 'b3-child-card');
    make(original, 'summary', '', 'Contenu et contraintes de la source');
    make(original, 'pre', '', JSON.stringify(item.original, null, 2));
    if (!cfg.edition) return;
    const area = make(target, 'div', 'b3-child-card');
    const review = item.review;
    const prompt = field(area, make, 'Consigne présentée à l’élève', 'textarea');
    prompt.value = review?.prompt ?? item.prompt;
    const stimulus = field(area, make, 'Support facultatif', 'textarea');
    stimulus.required = false;
    stimulus.value = review?.stimulus ?? item.stimulus;
    const criterion = field(area, make, 'Critère de revue observable', 'textarea');
    criterion.value = review?.scoring.criteria[0].description ?? '';
    const feedback = field(area, make, 'Prochaine étape ou rétroaction de référence', 'textarea');
    feedback.value = review?.feedback.next_step ?? '';
    const reviewer = field(area, make, 'Nom du relecteur');
    const reason = field(area, make, 'Motif de la décision', 'textarea');
    const confirm = field(area, make, 'J’ai relu la consigne, le support et le critère pour un essai local.');
    confirm.type = 'checkbox';
    const message = make(area, 'p');
    message.setAttribute('role','status');
    async function save(event, action, payload) {
     const control = event.currentTarget;
     control.disabled = true;
     try {
      await json('/api/banques-locales/' + action, {method:'POST',
       headers:{'Content-Type':'application/json','X-Ekole-CSRF':cfg.csrf},
       body:JSON.stringify({cours:cid, item:item.id, source:data.source, revision:item.revision,
                            reviewer:reviewer.value, reason:reason.value, ...payload})});
      if (select.value === cid) await load(item.id);
     } catch (error) {
      message.textContent = error.message;
      control.disabled = false;
     }
    }
    button(area, 'Valider pour essai local', event => {
     if (![prompt,criterion,feedback,reviewer,reason,confirm].every(input => input.reportValidity())) return;
     save(event,'review',{prompt:prompt.value, stimulus:stimulus.value, criterion:criterion.value,
                          feedback:feedback.value, confirmed:confirm.checked});
    }, 'b3-primary');
    if (item.reviewed) button(area, 'Retirer des prochains essais', event => {
     if ([reviewer,reason].every(input => input.reportValidity())) save(event,'withdraw',{});
    }, 'b3-secondary');
   };
   chosen.addEventListener('change', render);
   render();
  }
  select.addEventListener('change', () => load().catch(error => { panel.textContent = error.message; }));
  if (overview.length) await load();
 }
 return {scenarios, attempts, coverage, banks};
})();
