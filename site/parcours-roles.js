'use strict';

window.EkoleParcoursRoles = (() => {
 const base = '/api/parcours-roles';
 const add = (host, tag, text, cls) => {
  const node = document.createElement(tag);
  if (text) node.textContent = text;
  if (cls) node.className = cls;
  host.append(node);
  return node;
 };
 const href = (host, label, url) => {
  const node = add(host, 'a', label, 'button-link');
  node.href = url;
  return node;
 };
 const button = (host, title, action) => {
  const node = add(host, 'button', title, 'button-link');
  node.type = 'button';
  node.addEventListener('click', action);
  return node;
 };
 async function json(url, data) {
  const options = data ? {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data)} : {};
  const response = await fetch(url, {...options, cache: 'no-store'});
  const result = await response.json();
  if (!response.ok) throw Error(result.error || 'Mission indisponible.');
  return result;
 }

 function exercise(host, detail, mode) {
  const box = add(host, 'section', '', 'lesson-panel');
  const practice = mode === 'pratique';
  add(box, 'h3', practice ? 'Essaie le défi' : 'Poursuis avec la banque');
  if (!practice && !detail.reviewed) {
   add(box, 'p', 'Les nouvelles tentatives seront proposées après la revue des questions par l’enseignant.');
  }
  if (!practice) add(box, 'p', 'Tes réponses seront relues avant la diffusion de la rétroaction.');
  const key = 'ekole-role-attempt:' + [detail.theme, detail.role, mode].join(':');
  const notice = add(box, 'p');
  notice.setAttribute('role', 'status');
  const resultBox = add(box, 'div');
  function display(result, token) {
   resultBox.replaceChildren();
   if (result.status === 'awaiting_release') {
    notice.textContent = 'Réponses remises. La rétroaction sera disponible après la revue.';
    button(resultBox, 'Actualiser la rétroaction', async event => {
     const control = event.currentTarget;
     control.disabled = true;
     try { display(await requestActivity('', 'result', {attempt_id: token}), token); }
     catch (error) { notice.textContent = error.message; control.disabled = false; }
    });
    return;
   }
   notice.textContent = 'Résultat · ' + result.score + ' / ' + result.max_points;
   for (const item of result.items) {
    add(resultBox, 'p', item.feedback);
    add(resultBox, 'p', item.next_step, 'hint');
   }
   start.hidden = !practice && !detail.reviewed;
   start.disabled = false;
   start.textContent = 'Réessayer';
  }
  const start = button(box, practice ? 'Commencer le défi' : 'Ouvrir les questions relues', async () => {
   start.disabled = true;
   notice.textContent = '';
   resultBox.replaceChildren();
   try {
    const {exam, attempt_id: token} = await json(base + '/' + mode, {univers: detail.theme, role: detail.role});
    start.hidden = true;
    const form = add(box, 'form', '', 'activity-form');
    form.lang = 'fr-CA';
    const fields = exam.items.map(item => {
     if (!practice && item.stimulus) add(form, 'p', item.stimulus, 'review-note');
     return activityField(form, item);
    });
    const submit = add(form, 'button', 'Remettre', 'button-link primary');
    submit.type = 'submit';
    form.onsubmit = async event => {
     event.preventDefault();
     if (fields.some(field => !field.valid())) return;
     submit.disabled = true;
     try {
      const result = await requestActivity('', 'submit', {
       attempt_id: token,
       attempt: {format: 'inkui.attempt/1.0', exam_id: exam.exam_id, exam_digest: exam.exam_digest,
        answers: Object.fromEntries(fields.map(field => [field.id, field.value()]))},
      });
      try { sessionStorage.setItem(key, token); } catch (_) {}
      form.remove();
      display(result, token);
     } catch (error) { notice.textContent = error.message; submit.disabled = false; }
    };
    fields[0].focus();
   } catch (error) { notice.textContent = error.message; start.disabled = false; }
  });
  start.hidden = !practice && !detail.reviewed;
  let saved;
  try { saved = sessionStorage.getItem(key); } catch (_) {}
  if (saved && !practice) {
   start.disabled = true;
   requestActivity('', 'result', {attempt_id: saved}).then(result => {
    start.hidden = true;
    display(result, saved);
   }).catch(() => { start.disabled = false; });
  }
 }

 async function render(root) {
  const host = add(root, 'section');
  add(host, 'h1', 'Jouer un rôle dans mon univers', 'page-heading');
  try {
   const catalogue = await json(base + '.json');
   if (!host.isConnected || !catalogue.themes.length) {
    if (host.isConnected) add(host, 'p', 'Les missions apparaîtront quand ton enseignant ouvrira un univers.');
    return;
   }
   const params = new URLSearchParams(location.search);
   let saved;
   try { saved = sessionStorage.getItem('ekole-univers'); } catch (_) {}
   const current = catalogue.themes.find(row => row.id === (params.get('univers') || saved))
    || catalogue.themes.find(row => row.id === catalogue.default) || catalogue.themes[0];
   const label = add(host, 'label', 'Univers ', 'stage-select-label');
   const select = add(label, 'select', '', 'stage-picker');
   for (const theme of catalogue.themes) add(select, 'option', theme.name).value = theme.id;
   select.value = current.id;
   select.onchange = () => {
    try { sessionStorage.setItem('ekole-univers', select.value); } catch (_) {}
    location.search = new URLSearchParams({page: 'parcours-roles', univers: select.value});
   };
   add(host, 'h2', current.name, 'section-title');
   const options = add(host, 'div', '', 'mission-role-row');
   const selected = current.roles.find(role => role.id === params.get('role'));
   for (const role of current.roles) {
    const target = href(options, role.name, '?' + new URLSearchParams({
     page: 'parcours-roles', univers: current.id, role: role.id,
    }));
    if (selected === role) target.setAttribute('aria-current', 'page');
    const portrait = window.EkolePersonnages.role(target, role.id, role.name);
    target.prepend(portrait);
   }
   if (!selected) return;
   const detail = await json(base + '/' + current.id + '/' + selected.id + '.json');
   const mission = add(host, 'section', '', 'mission-play');
   add(mission, 'h2', detail.title);
   add(mission, 'p', detail.scene);
   add(mission, 'p', detail.objective, 'review-note');
   const links = add(mission, 'div', '', 'quick-actions');
   href(links, 'Voir le cours', '/eleve/?' + new URLSearchParams({cours: detail.course}));
   if (detail.spek) href(links, 'Fiche Spek du cours dans cet univers', detail.spek);
   exercise(mission, detail, 'pratique');
   add(mission, 'h3', 'À essayer dans ton rôle');
   add(mission, 'p', detail.transfer);
   exercise(mission, detail, 'banque');
  } catch (error) { add(host, 'p', error.message, 'warning'); }
 }
 return {render};
})();
