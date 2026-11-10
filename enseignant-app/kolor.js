'use strict';

window.EkoleKolorEnseignant = async (root, {make, button, json, cfg, isCurrent}) => {
 const base = '/api/kolor';
 const data = await json(base + '/portraits.json');
 if (!isCurrent()) return;
 make(root, 'h2', '', 'Portraits Kolor Studio');
 make(root, 'p', 'b3-intro', 'Choisis et valide les poses dans Kolor Studio, puis exporte-les. Publie ici les portraits que les élèves pourront voir.');
 if (data.message) make(root, 'p', 'b3-note', data.message);
 const status = make(root, 'p', 'b3-note');
 status.setAttribute('role', 'status');
 const ready = data.roles.filter(item => item.state === 'pret');
 const already = data.roles.filter(item => item.published);
 make(root, 'p', 'b3-note', ready.length + ' prêts dans Kolor Studio · ' + already.length + ' publiés depuis cet atelier.');
 const redraw = () => {
  if (!isCurrent()) return;
  root.replaceChildren();
  window.EkoleKolorEnseignant(root, {make, button, json, cfg, isCurrent})
   .catch(error => { if (isCurrent()) make(root, 'p', 'b3-error', error.message); });
 };
 button(root, 'Actualiser les exports Kolor', redraw, 'b3-secondary');
 const selection = [];
 const list = make(root, 'ul');
 const labels = {absent: 'Sans export', a_verifier: 'À vérifier dans Kolor Studio',
  png_indisponible: 'PNG indisponible', pret: 'Prêt dans Kolor Studio'};
 const send = (path, data) => json(base + path, {method: 'POST',
  headers: {'Content-Type': 'application/json', 'X-Ekole-CSRF': cfg.csrf},
  body: JSON.stringify(data)});
 for (const item of data.roles) {
  const row = make(list, 'li');
  const name = item.name.replace(/^Personnage du rôle\s*:\s*/i, '');
  const label = make(row, 'label', 'b3-check');
  if (item.candidate && item.candidate !== item.published && cfg.edition) {
   const input = make(label, 'input');
   input.type = 'checkbox';
   selection.push([input, item]);
  }
  make(label, 'span', '', name + ' · ' + labels[item.state] + (item.published ? ' · Publié' : ''));
  if (item.candidate) {
   const preview = make(row, 'a', '', 'Voir le portrait de ' + name);
   preview.href = base + '/candidat/' + item.id + '/' + item.candidate;
   preview.target = '_blank';
   preview.rel = 'noopener noreferrer';
  }
  if (item.published && cfg.edition) button(row, 'Retirer le portrait Kolor de ' + name, async event => {
   const control = event.currentTarget;
   control.disabled = true;
   try { await send('/retirer', {role: item.id, sha256: item.published}); redraw(); }
   catch (error) { status.textContent = error.message; control.disabled = false; }
  }, 'b3-secondary');
 }
 if (!selection.length) return;
 button(root, 'Tout sélectionner', () => { for (const [input] of selection) input.checked = true; }, 'b3-secondary');
 button(root, 'Publier les portraits sélectionnés', async event => {
  const selected = selection.filter(([input]) => input.checked);
  if (!selected.length) {
   status.textContent = 'Sélectionne au moins un portrait prêt.';
   return;
  }
  const control = event.currentTarget;
  control.disabled = true;
  try {
   await send('/publier', {portraits: Object.fromEntries(selected.map(([, item]) => [item.id, item.candidate]))});
   redraw();
  } catch (error) { status.textContent = error.message; control.disabled = false; }
 }, 'b3-primary');
};
