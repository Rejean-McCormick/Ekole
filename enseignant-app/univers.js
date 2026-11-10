'use strict';

window.EkoleUniversEnseignant = async (root, {make, button, json, cfg}) => {
 const base = '/api/univers';
 const catalogue = await json(base + '.json');
 const themes = catalogue.themes;
 make(root, 'h2', '', 'Univers de la classe');
 make(root, 'p', 'b3-intro', 'Choisis les thèmes que les élèves pourront explorer, un thème de départ et une palette pour toute la classe.');
 const choices = make(root, 'fieldset', 'b3-child-card');
 make(choices, 'legend', '', 'Thèmes proposés');
 const selected = new Map();
 for (const theme of themes) {
  const label = make(choices, 'label', 'b3-check');
  const input = make(label, 'input');
  input.type = 'checkbox';
  input.checked = catalogue.choices.includes(theme.id);
  input.disabled = !cfg.edition;
  make(label, 'span', '', theme.name + ' · ' + theme.intro);
  selected.set(theme.id, input);
 }
 const selection = (host, label, entries) => {
  const select = make(make(host, 'label', '', label), 'select');
  for (const item of entries) make(select, 'option', '', item.name).value = item.id;
  return select;
 };
 const active = () => themes.filter(theme => selected.get(theme.id).checked);
 const defaultTheme = selection(root, 'Thème de départ', []);
 function refreshDefault(preferred) {
  const available = active();
  defaultTheme.replaceChildren();
  for (const item of available) make(defaultTheme, 'option', '', item.name).value = item.id;
  if (available.some(item => item.id === preferred)) defaultTheme.value = preferred;
  defaultTheme.disabled = !cfg.edition || !available.length;
 }
 for (const input of selected.values()) input.addEventListener('change', () => refreshDefault(defaultTheme.value));
 refreshDefault(catalogue.default);
 const style = selection(root, 'Palette de la classe', catalogue.styles);
 style.value = catalogue.style;
 style.disabled = !cfg.edition;
 const status = make(root, 'p', 'b3-note');
 status.setAttribute('role', 'status');
 const post = (path, data) => json(base + path, {
  method: 'POST', headers: {'Content-Type': 'application/json', 'X-Ekole-CSRF': cfg.csrf},
  body: JSON.stringify(data),
 });
 if (cfg.edition) button(root, 'Appliquer à la classe', async event => {
  const control = event.currentTarget;
  control.disabled = true;
  try {
   await post('/publier', {choices: active().map(item => item.id), default: defaultTheme.value, style: style.value});
   status.textContent = 'Choix de classe appliqués.';
  } catch (error) { status.textContent = error.message; }
  finally { control.disabled = false; }
 }, 'b3-primary');

 const panel = make(root, 'section', 'b3-child-card');
 make(panel, 'h3', '', 'Illustration et aperçu d’un univers');
 const previewTheme = selection(panel, 'Univers à préparer', themes);
 if (catalogue.default) previewTheme.value = catalogue.default;
 const prompt = make(make(panel, 'label', '', 'Prompt d’illustration pour la palette'), 'textarea', 'b3-prompt');
 prompt.readOnly = true;
 prompt.rows = 4;
 const frames = make(panel, 'ul');
 let revision = 0;
 async function preview() {
  const id = ++revision;
  const detail = await json(base + '/' + encodeURIComponent(previewTheme.value) + '.json');
  if (id !== revision) return;
  const palette = catalogue.styles.find(item => item.id === style.value);
  prompt.value = [detail.name, detail.intro, palette.prompt,
   'Illustration de primaire, sans texte incrusté, sans réponse visible et sans photographie d’élève.'].join(' ');
  frames.replaceChildren();
  for (const text of Object.values(detail.frames)) make(frames, 'li', '', text);
 }
 const update = () => preview().catch(error => { status.textContent = error.message; });
 previewTheme.addEventListener('change', update);
 style.addEventListener('change', update);
 if (window.EkoleRolesEnseignant) await window.EkoleRolesEnseignant(root, {make, json});
 await update();
 if (!cfg.edition) return;
 make(panel, 'p', 'b3-note', 'Image optimisée de 600 ko maximum, de 120 à 4 096 pixels par côté.');
 const file = make(make(panel, 'label', '', 'Image PNG, JPG ou WebP'), 'input');
 file.type = 'file';
 file.accept = 'image/png,image/jpeg,image/webp';
 const alt = make(make(panel, 'label', '', 'Description de l’image'), 'input');
 alt.maxLength = 240;
 button(panel, 'Approuver et publier l’image de cet univers', async event => {
  const image = file.files[0];
  if (!image || image.size > 600000 || !alt.value.trim()) {
   status.textContent = 'Choisis une image de 600 ko maximum et décris ce qu’elle montre.';
   return;
  }
  const control = event.currentTarget;
  control.disabled = true;
  const data = {theme: previewTheme.value, style: style.value, alt: alt.value};
  try {
   const bytes = new Uint8Array(await image.arrayBuffer());
   let encoded = '';
   for (let offset = 0; offset < bytes.length; offset += 8192) {
    encoded += String.fromCharCode(...bytes.subarray(offset, offset + 8192));
   }
   await post('/image', {...data, image: btoa(encoded)});
   status.textContent = 'Image approuvée pour cet univers et cette palette.';
   file.value = '';
  } catch (error) { status.textContent = error.message; }
  finally { control.disabled = false; }
 }, 'b3-secondary');
};
