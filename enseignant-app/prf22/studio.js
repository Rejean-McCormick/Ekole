'use strict';
// PRF-22 teacher-only editorial view; never writes to the versioned bank.
(() => {
  const $ = id => document.getElementById(id);
  const EDITABLE = [
    ['conjecture_statement', 'Hypothèse pédagogique'], ['expected_action', 'Action attendue'],
    ['process', 'Processus à observer'], ['observation', 'Méthode d’observation'],
    ['evidence', 'Preuve candidate'], ['criterion', 'Critère de jugement'],
    ['disconfirmation', 'Signal qui contredirait l’hypothèse'],
    ['alternative', 'Autres explications possibles'],
    ['boundary', 'Conditions et adaptations'], ['interpretation_limit', 'Limites d’interprétation']
  ];
  let index = [], chosen = null, detail = null, cards = {}, activeGoal = null, config = {edition:false};
  const status = (message, isError = false) => { $('status').textContent = message; $('status').className = isError ? 'error' : 'ok'; };
  const text = (id, value) => { $(id).textContent = String(value ?? ''); };
  async function get(url) {
    const r = await fetch(url, {cache:'no-store', credentials:'same-origin'});
    if (!r.ok) throw new Error(`Requête ${r.status} : ${url}`);
    return r.json();
  }
  function make(tag, contents = '', className = '') {
    const e = document.createElement(tag);e.className=className;e.textContent=String(contents);return e;
  }
  function stats(data) {
    $('metrics').replaceChildren();
    for (const [n,label] of [[data.entries_count,'propositions candidates'],[data.sources,'situations sources'],
      [data.activities_used,'activités utilisées'],[data.objectives_used,'objectifs utilisés']]) {
      const b=make('div','','prf-stat');b.append(make('strong',n),make('span',label));$('metrics').append(b);
    }
  }
  function filtered() {
    const query=$('search').value.toLocaleLowerCase('fr-CA');const filter=$('filter').value;const domain=$('domain').value;
    return index.filter(x=> (!filter||x.quality===filter) && (!domain||x.focale===domain) &&
      [x.titre,x.source_ref,x.focale,...x.objective_refs,...x.activity_refs].join(' ').toLocaleLowerCase('fr-CA').includes(query));
  }
  function list() {
    const subset=filtered();
    text('count',`${subset.length} proposition(s) affichée(s)`);
    $('situations').replaceChildren();
    for (const item of subset) {
      const b=make('button','','prf-item');b.type='button';b.setAttribute('role','listitem');b.setAttribute('aria-current',chosen===item.slug?'true':'false');
      b.append(make('strong',item.titre),make('small',`${item.focale} · ${item.source_ref} · ${item.quality==='REVUE_PRIORITAIRE'?'Revue prioritaire':'Revue obligatoire'}`));
      b.addEventListener('click',()=>open(item.slug));$('situations').append(b);
    }
  }
  function captureGoal() {
    if (!activeGoal || !cards[activeGoal]) return;
    for(const [key] of EDITABLE) {
      const e=document.getElementById('field_'+key);if(e)cards[activeGoal][key]=e.value;
    }
  }
  function renderGoal() {
    const goal=$('goal').value;
    captureGoal();activeGoal=goal;
    $('theory-editor').replaceChildren();
    if(!goal || !cards[goal])return;
    for (const [key,label] of EDITABLE) {
      const block=make('div','','prf-field');const lab=make('label',label);lab.htmlFor='field_'+key;
      const field=make('textarea');field.id='field_'+key;field.value=cards[goal][key]||'';field.rows=4;
      field.disabled=!config.edition;block.append(lab,field);$('theory-editor').append(block);
    }
  }
  async function open(slug) {
    try {
      status('Chargement de la conception…');
      const d=await get(`/api/prf22/situation/${encodeURIComponent(slug)}.json`);
      chosen=slug;detail=d;cards=structuredClone(d.authoring.theory_entries);activeGoal=null;
      $('empty').hidden=true;$('content').hidden=false;
      text('source',d.meta.source_ref);text('title',d.meta.titre);text('focus',d.meta.focale);
      text('quality',d.meta.quality==='REVUE_PRIORITAIRE'?'Révision prioritaire':'Révision pédagogique requise');
      text('reason',d.meta.justification_provenance);
      const c=d.design.context;text('context',`${c.epoch} · ${c.place} · ${c.reality_mode} · ${c.cultural_frame}`);
      text('problem',c.narrative_premise);
      const fiche=d.fiche_pedagogique;
      const summary=$('editorial-summary');summary.replaceChildren();
      if(fiche) {
        const block=make('div','','prf-sheet');
        const section=(label,content)=>{const p=make('p');p.append(make('strong',`${label} : `),document.createTextNode(content||'À préparer'));block.append(p);};
        section('Déclencheur',fiche.declencheur_source);
        section('Question à résoudre',fiche.question_motrice);
        section('Informations à préparer',fiche.informations_a_preparer.join(' · '));
        section('Production envisagée',fiche.production_attendue_source);
        if(fiche.rebond_source)section('Imprévu possible',fiche.rebond_source);
        const gaps=make('ul');for(const gap of fiche.lacunes){gaps.append(make('li',gap));}
        block.append(make('h4','À vérifier avant utilisation'),gaps);summary.append(block);
      } else summary.append(make('p','Ancienne banque : justification détaillée non disponible.'));
      $('activity-list').replaceChildren();
      const byref=new Map((fiche?.activites||[]).map(x=>[x.activite_ref,x]));
      for (const a of d.design.activities) {
        const ref=a.exercise_ref.resource_id; const info=byref.get(ref);
        const block=make('article','','prf-activity');
        block.append(make('span',`${a.exercise_ref.owner==='Ékole'?'Patron Ékole proposé':'Activité Kontexte référencée'} · ${ref}`),make('h4',a.contextualization));
        if(info) {
          block.append(make('p',`Objectif : ${info.objectif_ref}`),
            make('p',`Pourquoi : ${info.motif_de_choix}`),
            make('p',`À réaliser : ${info.consigne_contextualisee}`),
            make('p',`Trace : ${info.preuve}`),
            make('p',`Critères candidats : ${info.critere_propose}`));
          if(info.confiance!=='ancrage_direct')block.append(make('p','Ancrage faible : remplacement ou justification exigés.','prf-attention'));
        } else block.append(make('p','Association issue d’une banque antérieure : justification à documenter.'));
        block.append(make('small',`Durée indicative : ${a.duration_minutes} min · Matériel et sécurité à confirmer`));
        $('activity-list').append(block);
      }
      $('goal').replaceChildren();for (const l of d.authoring.draft.learning_objective_links) {
        const option=make('option',`${l.title} — ${l.objective_ref}`);option.value=l.objective_ref;$('goal').append(option);
      }
      $('note').value='';$('revision').replaceChildren(make('option','Banque d’origine'));
      $('revision').firstChild.value='';
      for (const rev of d.revisions) { const opt=make('option',rev);opt.value=rev;$('revision').append(opt); }
      renderGoal();list();
      status('Conception chargée. Les textes restent candidats et non qualifiés.');
    }catch(e){status(`Impossible de charger : ${e.message}`,true);}
  }
  async function loadRevision() {
    if(!chosen || !$('revision').value)return;
    try {
      const d=await get(`/api/prf22/revision/${encodeURIComponent(chosen)}/${encodeURIComponent($('revision').value)}.json`);
      cards=structuredClone(d.authoring.theory_entries);activeGoal=null;$('note').value=d.review.note||'';renderGoal();
      status('Révision locale chargée. Elle n’est pas une approbation pédagogique.');
    }catch(e){status(e.message,true);}
  }
  async function save() {
    if(!config.edition){status('Lancer Ékole avec --edition pour autoriser les révisions locales.',true);return;}
    if(!detail)return;
    try {
      captureGoal();
      const edited={};for(const [goal,card] of Object.entries(cards)) {
        edited[goal]={};for(const [k] of EDITABLE)edited[goal][k]=String(card[k]||'').trim();
      }
      const r=await fetch('/api/prf22/reviser',{method:'POST',credentials:'same-origin',
        headers:{'Content-Type':'application/json','X-Ekole-CSRF':config.csrf},
        body:JSON.stringify({slug:chosen,source_sha256:detail.source_sha256,theory_entries:edited,note:$('note').value})});
      const response=await r.json();
      if(!r.ok)throw new Error(response.error||'Révision refusée');
      status(`Révision enregistrée localement : ${response.revision}. Aucune publication.`);
      if(response.revision){ const opt=make('option',response.revision);opt.value=response.revision;$('revision').prepend(opt);$('revision').value=response.revision; }
    }catch(e){status('Erreur de sauvegarde : '+e.message,true);}
  }
  async function boot(){
    try {
      const [data,editor]=await Promise.all([get('/api/prf22/index.json'),get('/api/editor-config')]);
      config=editor;index=data.entries;stats(data);
      for(const d of [...new Set(index.map(x=>x.focale))].sort()){const o=make('option',d);o.value=d;$('domain').append(o);}
      list();$('save').disabled=!editor.edition;
      status(`${data.entries_count} propositions disponibles. ${editor.edition?'Révision locale autorisée':'Lecture seule : option --edition non activée'}.`);
      if(index.length)await open(index[0].slug);
    }catch(e){status('Banque indisponible ou session enseignant absente : '+e.message,true);}
  }
  function changeFilter() {
    list();
    const subset=filtered();
    if (subset.length && !subset.some(item=>item.slug===chosen)) open(subset[0].slug);
  }
  $('search').addEventListener('input',changeFilter);$('filter').addEventListener('change',changeFilter);$('domain').addEventListener('change',changeFilter);
  $('goal').addEventListener('change',renderGoal);$('save').addEventListener('click',save);
  $('reload').addEventListener('click',()=>{if(chosen)open(chosen);});
  $('openRevision').addEventListener('click',loadRevision);
  boot();
})();
