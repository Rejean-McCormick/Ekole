'use strict';

async function requestActivity(id, action, body) {
 const response = await fetch('/api/activite-locale/' + action + '?id=' + encodeURIComponent(id), {
  method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(body)
 });
 const data = await response.json();
 if (!response.ok) throw new Error(data.error || 'Activité indisponible');
 return data;
}

function showInvitationGroups(section, view) {
 const {invitations, per_sheet: perSheet} = view.practice;
 let sheets = 0;
 const controls = add(section, 'div', 'step-controls');
 const more = add(controls, 'button', 'button-link', view.labels.add_sheet);
 const less = add(controls, 'button', 'button-link', view.labels.undo_sheet);
 more.type = less.type = 'button';
 const groups = add(section, 'ol', 'invitation-groups');
 const count = add(section, 'p', 'hint');
 count.setAttribute('role', 'status');
 function renderGroups() {
  groups.replaceChildren();
  for (let i = 0; i < sheets; i++) {
   const size = Math.min(perSheet, invitations - i * perSheet);
   add(groups, 'li', '', '● '.repeat(size).trim()).setAttribute('aria-label', String(size));
  }
  const placed = Math.min(invitations, sheets * perSheet);
  count.textContent = view.labels.placement.replace('{placed}', placed).replace('{total}', invitations);
  more.disabled = placed === invitations;
  less.disabled = sheets === 0;
 }
 more.onclick = () => { sheets++; renderGroups(); };
 less.onclick = () => { sheets--; renderGroups(); };
 renderGroups();
}

async function renderLocalActivity(root, course, retour) {
 const locale = current().get('langue') === 'en' ? 'en' : 'fr-CA';
 const mode = current().get('mode') === 'bilan' ? 'bilan' : 'pratique';
 const options = course.activites_locales || [];
 const selected = options.find(item => item.id === current().get('activite')) || options[0];
 if (!selected) return;
 const id = selected.id;
 const request = (action, body) => requestActivity(id, action, body);
 const section = add(root, 'section', 'lesson-panel');
 section.lang = locale;
 let view;
 try {
  view = await fetchJson('/api/activite-locale.json?' + new URLSearchParams({locale, id}));
 } catch (_) {
  add(section, 'p', 'warning', 'Activité indisponible.');
  return;
 }
 const link = (host, label, nextMode, nextLocale, activityId = id) =>
  a(host, label, ctxLink(course.id, retour, {vue: 'activite', mode: nextMode, langue: nextLocale,
                                           activite: activityId}), 'button-link');
 if (options.length > 1) {
  const chooser = add(section, 'nav', 'step-controls');
  chooser.setAttribute('aria-label', locale === 'en' ? 'Activities' : 'Activités');
  for (const option of options) {
   const item = link(chooser, option.titre, 'pratique', locale, option.id);
   if (option.id === id) item.setAttribute('aria-current', 'page');
  }
 }
 const nav = add(section, 'nav', 'step-controls');
 link(nav, view.labels.pratique, 'pratique', locale);
 link(nav, view.labels.bilan, 'bilan', locale);
 const language = link(nav, locale === 'en' ? 'Français' : 'English', mode, locale === 'en' ? 'fr-CA' : 'en');
 language.lang = locale === 'en' ? 'fr-CA' : 'en';
 if (selected.spek) {
  const page = add(nav, 'a', 'button-link', locale === 'en' ? 'Spek page' : 'Fiche Spek');
  page.href = '/apercus-spek/' + encodeURIComponent(id) + '/' + (locale === 'en' ? 'en' : 'fr') + '/index.html';
 }

 add(section, 'h2', 'lesson-title', view.title);
 add(section, 'p', 'small-note', view.limits);
 add(section, 'p', '', view.objective);
 if (view.character) add(section, 'p', 'review-note', view.character);
 add(section, 'p', '', view.cases[mode]);
 if (mode === 'pratique') {
  const guide = add(section, 'ol');
  for (const step of [view.group, view.compare, view.reflection]) add(guide, 'li', '', step);
  if (view.practice) showInvitationGroups(section, view);
 }
 const actions = add(section, 'div');
 const result = add(section, 'div');
 result.setAttribute('aria-live', 'polite');
 const start = add(actions, 'button', 'button-link primary', view.labels[mode]);
 start.type = 'button';
 const storageKey = ['ekole-local-activity', view.id, view.revision, locale, mode].join(':');
 const fail = error => { result.textContent = error.message; };

 function display(outcome, token) {
  result.replaceChildren();
  if (outcome.status === 'awaiting_release') {
   add(result, 'p', 'review-note', view.labels.pending);
   const refresh = add(result, 'button', 'button-link', view.labels.refresh);
   refresh.type = 'button';
   refresh.onclick = async () => {
    refresh.disabled = true;
    try { display(await request('result', {attempt_id: token}), token); }
    catch (error) { refresh.disabled = false; add(result, 'p', 'warning', error.message); }
   };
   return;
  }
  if (outcome.score !== null) add(result, 'p', '', view.labels.score + ' · ' + outcome.score + '/' + outcome.max_points);
  for (const item of outcome.items) {
   add(result, 'strong', '', view.prompts[item.item_id]);
   const feedback = item.status === 'pending_review' ? view.labels.review : item.feedback;
   add(result, 'p', '', feedback);
  }
  if (mode === 'pratique') {
   start.textContent = view.labels.restart;
   start.hidden = false;
   start.disabled = false;
  }
 }

 start.onclick = async () => {
  start.disabled = true;
  result.replaceChildren();
  try {
   const {attempt_id, exam} = await request('start', {locale, mode});
   start.hidden = true;
   const form = add(actions, 'form', 'activity-form');
   const fields = exam.items.map(item => activityField(form, item));
   const submit = add(form, 'button', 'button-link primary', view.labels.submit);
   submit.type = 'submit';
   form.onsubmit = async event => {
    event.preventDefault();
    if (fields.some(field => !field.valid())) return;
    submit.disabled = true;
    const attempt = {format: 'inkui.attempt/1.0', exam_id: exam.exam_id, exam_digest: exam.exam_digest,
                     answers: Object.fromEntries(fields.map(field => [field.id, field.value()]))};
    try {
     const outcome = await request('submit', {attempt_id, attempt});
     try { sessionStorage.setItem(storageKey, attempt_id); } catch (_) {}
     form.remove();
     display(outcome, attempt_id);
    } catch (error) {
     fail(error);
     submit.disabled = false;
    }
   };
   fields[0]?.focus();
  } catch (error) {
   fail(error);
   start.disabled = false;
  }
 };

 let previous;
 try { previous = sessionStorage.getItem(storageKey); } catch (_) {}
 if (previous) {
  start.disabled = true;
  try {
   display(await request('result', {attempt_id: previous}), previous);
   if (mode === 'bilan') start.hidden = true;
  } catch (_) {
   start.disabled = false;
  }
 }
}


function activityField(form, item) {
 if (item.kind === 'single_choice' || item.kind === 'multiple_choice') {
  const multiple = item.kind === 'multiple_choice';
  const group = add(form, 'fieldset', 'activity-options');
  add(group, 'legend', '', item.prompt);
  const inputs = item.options.map(option => {
   const label = add(group, 'label');
   const input = add(label, 'input');
   input.type = multiple ? 'checkbox' : 'radio';
   input.name = item.id;
   input.value = option.id;
   input.required = !multiple;
   add(label, 'span', '', option.text);
   return input;
  });
  const values = () => inputs.filter(input => input.checked).map(input => input.value);
  const validate = () => {
   inputs[0].setCustomValidity(multiple && !values().length
    ? (form.closest('[lang]').lang === 'en' ? 'Select at least one option.' : 'Choisis au moins une réponse.') : '');
  };
  for (const input of inputs) input.addEventListener('change', validate);
  return {id:item.id, value:() => multiple ? values() : values()[0],
          valid:() => { validate(); return inputs[0].reportValidity(); }, focus:() => inputs[0].focus()};
 }
 const label = add(form, 'label', '', item.prompt);
 const input = add(label, item.kind === 'rubric' ? 'textarea' : 'input');
 input.required = true;
 input.maxLength = item.kind === 'rubric' ? 2000 : 32;
 if (item.kind === 'numeric') input.inputMode = 'decimal';
 return {id:item.id, value:() => input.value.trim(), valid:() => input.reportValidity(), focus:() => input.focus()};
}

function renderReviewedBank(root, course, canStart) {
 const section = add(root, 'section', 'lesson-panel');
 section.lang = 'fr-CA';
 add(section, 'h2', 'lesson-title', 'Questions relues pour essai local');
 add(section, 'p', 'small-note', 'Tes réponses seront lues par la personne responsable de cet essai.');
 const start = add(section, 'button', 'button-link primary', 'Commencer');
 start.type = 'button';
 start.hidden = !canStart;
 const result = add(section, 'div');
 result.setAttribute('aria-live', 'polite');
 const key = 'ekole-reviewed-bank:' + course.id;
 function show(outcome, token) {
  result.replaceChildren();
  if (outcome.status === 'awaiting_release') {
   add(result, 'p', '', 'Réponses remises. La rétroaction sera disponible après la revue.');
   const refresh = add(result, 'button', 'button-link', 'Actualiser le résultat');
   refresh.type = 'button';
   refresh.onclick = async () => {
    refresh.disabled = true;
    try { show(await requestActivity('', 'result', {attempt_id: token}), token); }
    catch (error) { add(result, 'p', 'warning', error.message); refresh.disabled = false; }
   };
  } else {
   add(result, 'p', '', 'Résultat de l’essai · ' + outcome.score + '/' + outcome.max_points);
   for (const item of outcome.items) {
    add(result, 'p', '', item.feedback);
    add(result, 'p', 'hint', item.next_step);
   }
   start.hidden = !canStart;
  }
 }
 start.onclick = async () => {
  start.disabled = true;
  result.replaceChildren();
  try {
   const response = await fetch('/api/banques-locales/start', {method:'POST',
    headers:{'Content-Type':'application/json'}, body:JSON.stringify({cours:course.id})});
   const {exam, attempt_id: token, error} = await response.json();
   if (!response.ok) throw new Error(error);
   start.hidden = true;
   const form = add(section, 'form', 'activity-form');
   const fields = exam.items.map(item => {
    if (item.stimulus) add(form, 'p', 'review-note', item.stimulus);
    return activityField(form, item);
   });
   const submit = add(form, 'button', 'button-link primary', 'Remettre');
   submit.type = 'submit';
   form.onsubmit = async event => {
    event.preventDefault();
    if (fields.some(field => !field.valid())) return;
    submit.disabled = true;
    try {
     const attempt = {format:'inkui.attempt/1.0', exam_id:exam.exam_id, exam_digest:exam.exam_digest,
                      answers:Object.fromEntries(fields.map(field => [field.id, field.value()]))};
     const outcome = await requestActivity('', 'submit', {attempt_id:token, attempt});
     try { sessionStorage.setItem(key, token); } catch (_) {}
     form.remove();
     show(outcome, token);
    } catch (error) { result.textContent = error.message; submit.disabled = false; }
   };
   fields[0]?.focus();
  } catch (error) { result.textContent = error.message; }
  finally { start.disabled = false; }
 };
 let previous;
 try { previous = sessionStorage.getItem(key); } catch (_) {}
 if (previous) {
  start.hidden = true;
  requestActivity('', 'result', {attempt_id: previous}).then(outcome => show(outcome, previous),
                                                           () => {start.hidden = !canStart;});
 }
}
