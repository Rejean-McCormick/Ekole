'use strict';
// B3, couche Enseignant exclusivement : aucun changement des contrats ni de l'API Élève.
// Contrat Ekole v3: /api/editor-config, /api/pack.json, /api/cours/*.json,
// /api/brouillon-eleve/*.json, /api/visuels/*.json et /api/visuels/*/*.
(() => {
  const $ = s => document.querySelector(s);
  const make = (parent,tag,cls='',text) => {
    const node=document.createElement(tag); if(cls)node.className=cls;
    if(text!==undefined)node.textContent=String(text);
    parent.append(node);return node;
  };
  const button=(parent,label,fn,cls='')=>{const b=make(parent,'button',cls,label);b.type='button';b.addEventListener('click',fn);return b;};
  const labelFor=(parent,text,input)=>{const l=make(parent,'label','',text);if(input?.id)l.htmlFor=input.id;return l;};
  const id=()=>crypto.randomUUID?.()||String(Date.now())+String(Math.random()).slice(2);
  const safeId=x=>encodeURIComponent(x);
  const state={pack:null,cfg:null,course:null,revision:null,section:'text',busy:false,visualsCache:new Map(),albumRows:[],albumSubset:[],albumPage:0,albumGrid:true,albumLoading:false,albumEpoch:0,slotToFocus:''};
  const setStatus=(message,kind='')=>{const n=$('#status');n.textContent=message;n.dataset.state=kind;};
  async function json(url,options){const response=await fetch(url,{cache:'no-store',credentials:'same-origin',...options});if(!response.ok)throw Error(`HTTP ${response.status} : ${(await response.text()).slice(0,180)}`);return response.json();}
  async function request(url,body,headers={}){if(!state.cfg.edition)throw Error('Atelier en lecture seule. Relancer en mode édition.');return json(url,{method:'POST',headers:{'Content-Type':'application/json','X-Ekole-CSRF':state.cfg.csrf,...headers},body:JSON.stringify(body)});}
  function clear(){const host=$('#editor');host.replaceChildren();return host;}
  function note(host,text,cls='b3-note'){return make(host,'p',cls,text);}
  function heading(host,title,description){make(host,'h2','',title);if(description)note(host,description,'b3-intro');}
  const courseMeta=cid=>state.pack.cours.find(x=>x.id===cid);
  function sameCourse(cid){return state.course?.id===cid;}

  // Rendu DOM pur : jamais de innerHTML pour du Markdown éditable.
  // Les balises HTML brutes sont affichées comme texte, les liens sont filtrés.
  function safeHref(value){const v=value.trim();if(/[\u0000-\u001f]/.test(v))return null;
    if(/^https?:\/\//i.test(v)||/^mailto:/i.test(v)){try{const u=new URL(v);return ['http:','https:','mailto:'].includes(u.protocol)?u.href:null;}catch{return null;}}
    if(/^#[\w-]+$/.test(v))return v;
    return null; // les chemins des documents experts ne sont pas publics
  }
  function inline(parent,str){
    const patt=/(\*\*[^*]+\*\*|__[^_]+__|\*[^*]+\*|`[^`]+`|\[[^\]]+\]\([^)]+\))/g;
    let i=0,match;
    while((match=patt.exec(str))!==null){if(match.index>i)parent.append(document.createTextNode(str.slice(i,match.index)));
      const v=match[0];if(v.startsWith('**')||v.startsWith('__'))inline(make(parent,'strong'),v.slice(2,-2));
      else if(v.startsWith('*'))inline(make(parent,'em'),v.slice(1,-1));
      else if(v.startsWith('`'))make(parent,'code','',v.slice(1,-1));
      else {const m=/^\[([^\]]+)\]\(([^)]+)\)$/.exec(v);const href=m&&safeHref(m[2]);
        if(href){const a=make(parent,'a','',m[1]);a.href=href;a.rel='noopener noreferrer';if(href.startsWith('http'))a.target='_blank';}
        else make(parent,'span','b3-unavailable-link',m?m[1]+' (référence interne)':'Lien non disponible');}
      i=patt.lastIndex;
    }
    if(i<str.length)parent.append(document.createTextNode(str.slice(i)));
  }
  function renderMarkdown(container,source){container.replaceChildren();const lines=String(source||'').replace(/\r\n?/g,'\n').split('\n');let i=0;
    const tableLine=t=>t.includes('|') && t.replaceAll('|','').trim().length>0;
    const separator=t=>/^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*$/.test(t);
    const cells=t=>t.trim().replace(/^\|/,'').replace(/\|$/,'').split('|').map(x=>x.trim());
    const block=t=>/^#{1,6}\s+|^```|^>\s?|^(?:[-*]|\d+\.)\s+|^---+$/.test(t);
    while(i<lines.length){const t=lines[i].trim();if(!t){i++;continue;}
      let m=t.match(/^(#{1,6})\s+(.*)$/);if(m){const h=make(container,'h'+Math.min(m[1].length+2,6));inline(h,m[2]);i++;continue;}
      if(/^```/.test(t)){i++;const buf=[];while(i<lines.length&&!/^```/.test(lines[i].trim()))buf.push(lines[i++]);if(i<lines.length)i++;make(container,'pre','',buf.join('\n'));continue;}
      if(tableLine(t)&&separator((lines[i+1]||'').trim())){const table=make(container,'table','b3-md-table');const head=make(table,'thead');const tr=make(head,'tr');cells(t).forEach(c=>inline(make(tr,'th'),c));i+=2;
        const body=make(table,'tbody');while(i<lines.length&&tableLine(lines[i])){const row=make(body,'tr');cells(lines[i]).forEach(c=>inline(make(row,'td'),c));i++;}continue;}
      if(/^[-*]\s+/.test(t)||/^\d+\.\s+/.test(t)){const ordered=/^\d+\./.test(t);const ul=make(container,ordered?'ol':'ul');const rx=ordered?/^\s*\d+\.\s+/:/^\s*[-*]\s+/;
        while(i<lines.length&&rx.test(lines[i])){const li=make(ul,'li');inline(li,lines[i].replace(rx,''));i++;}continue;}
      if(/^>\s?/.test(t)){const buf=[];while(i<lines.length&&/^>\s?/.test(lines[i].trim()))buf.push(lines[i++].trim().replace(/^>\s?/,''));const q=make(container,'blockquote');inline(q,buf.join(' '));continue;}
      if(/^---+$/.test(t)){make(container,'hr');i++;continue;}
      const para=[];while(i<lines.length&&lines[i].trim()&&!block(lines[i].trim())&&!(tableLine(lines[i])&&separator(lines[i+1]||''))){para.push(lines[i].trim());i++;}
      if(para.length)inline(make(container,'p'),para.join(' '));else i++;
    }
    if(!container.children.length)note(container,'Aucun texte dans ce module.','b3-empty');
  }

  function initTabs(){const tabs=$('.atelier-tabs');if(!tabs)throw Error('Onglets Enseignant absents de la version de base');
    const all=[['tabText','text'],['tabVisuals','visuals'],['tabStudent','student']];
    for(const [id,value] of all){const b=$('#'+id);if(!b)throw Error('Onglet requis manquant : '+id);b.onclick=()=>{state.section=value;render();};}
    const album=make(tabs,'button','','Album des images');album.id='tabAlbum';album.type='button';album.onclick=()=>{state.section='album';render();};
    // Les handlers originaux ne sont pas chargés dans cette version B3.
  }
  async function bootstrap(){try{
    [state.cfg,state.pack]=await Promise.all([json('/api/editor-config'),json('/api/pack.json')]);
    if(!Array.isArray(state.pack.cours))throw Error('Format de paquet non reconnu');
    $('#publicHome').href='http://127.0.0.1:'+state.cfg.port_public+'/eleve/';
    document.title=state.pack.nom+' — Atelier Enseignant B3';
    initTabs();
    for(const c of [...state.pack.cours].sort((a,b)=>(a.discipline||'').localeCompare(b.discipline||'','fr')||a.titre.localeCompare(b.titre,'fr'))){const o=make($('#cours'),'option','',(c.discipline||'Cours')+' · '+c.titre);o.value=c.id;}
    $('#cours').addEventListener('change',loadCourse);
    setStatus(`${state.pack.cours.length} cours · ${state.cfg.edition?'Édition locale active':'Lecture seule'} · Publication distincte pour l’élève`);
    await render();
  }catch(e){setStatus('Chargement de l’atelier impossible : '+e.message,'error');}}
  async function loadCourse(){const cid=$('#cours').value;state.course=null;state.revision=null;if(!cid){await render();return;}
    try{const response=await fetch('/api/cours/'+safeId(cid)+'.json',{credentials:'same-origin',cache:'no-store'});
      if(!response.ok)throw Error('HTTP '+response.status);const raw=await response.text();const c=JSON.parse(raw);
      if(c.id!==cid||!Array.isArray(c.modules))throw Error('Cours expert invalide');state.course=c;
      if(crypto.subtle){const digest=await crypto.subtle.digest('SHA-256',new TextEncoder().encode(raw));state.revision=Array.from(new Uint8Array(digest),b=>b.toString(16).padStart(2,'0')).join('');}
      else throw Error('Le navigateur doit être ouvert sur localhost pour modifier les textes.');
      await render();
    }catch(e){setStatus('Impossible de charger le cours : '+e.message,'error');}
  }
  async function selectCourse(cid,section='visuals',slot=''){if($('#cours').value!==cid){$('#cours').value=cid;await loadCourse();}state.section=section;state.slotToFocus=slot;await render();}
  async function render(){const root=clear();for(const [id,value] of [['tabText','text'],['tabVisuals','visuals'],['tabStudent','student'],['tabAlbum','album']]){$('#'+id)?.setAttribute('aria-current',state.section===value?'page':'false');}
    try{if(state.section==='album')await renderAlbum(root);else if(!state.course)note(root,'Choisis un cours, ou ouvre l’Album pour explorer les illustrations des autres cours.');
      else if(state.section==='text')renderText(root);else if(state.section==='visuals')await renderVisuals(root);else await renderStudent(root);
    }catch(e){note(root,'Erreur : '+e.message,'b3-error');setStatus(e.message,'error');}
  }
  function renderText(root){heading(root,state.course.titre,'Lecture formatée par défaut. La source Markdown reste éditable et n’est jamais diffusée directement à l’élève.');
    const tools=make(root,'div','b3-toolbar');const showAll=button(tools,'Tout afficher en aperçu',()=>root.querySelectorAll('.b3-expert').forEach(n=>setEditing(n,false)),'b3-secondary');
    const editAll=button(tools,'Éditer les six modules',()=>root.querySelectorAll('.b3-expert').forEach(n=>setEditing(n,true)),'b3-secondary');
    const records=[];
    for(const [index,m] of (state.course.modules||[]).entries()){
      const section=make(root,'section','b3-expert');section.dataset.moduleId=m.id;
      const top=make(section,'div','b3-expert-head');make(top,'h3','',`${index+1}. ${m.titre}`);
      const toggle=button(top,'Modifier le Markdown',()=>setEditing(section,!section.classList.contains('editing')),'b3-secondary b3-mode');toggle.setAttribute('aria-expanded','false');
      const preview=make(section,'div','b3-markdown');preview.setAttribute('aria-label','Aperçu formaté — '+m.titre);renderMarkdown(preview,m.texte||'');
      const edit=make(section,'div','b3-edit-panel');edit.hidden=true;
      const lab=make(edit,'label','','Source Markdown — '+m.titre);const ta=make(edit,'textarea','b3-source');ta.id='b3-src-'+index;lab.htmlFor=ta.id;ta.dataset.mid=m.id;ta.value=m.texte||'';ta.disabled=!state.cfg.edition;
      ta.addEventListener('input',()=>{renderMarkdown(preview,ta.value);section.classList.toggle('changed',ta.value!==(m.texte||''));});
      make(edit,'p','b3-hint','L’aperçu se met à jour pendant l’édition. Le texte expert reste privé.');
      const live=button(edit,'Prévisualiser les changements',()=>setEditing(section,false),'b3-secondary');
      records.push({m,ta});
    }
    if(state.cfg.edition){const group=make(root,'div','b3-save-bar');button(group,'Enregistrer les textes experts',async e=>{const b=e.currentTarget;b.disabled=true;
      try{const updated={...state.course,_revision:state.revision,modules:records.map(({m,ta})=>({...m,texte:ta.value}))};
        const res=await request('/api/cours/'+safeId(state.course.id)+'.json',updated);
        state.course.modules=updated.modules;state.revision=res._revision;
        root.querySelectorAll('.b3-expert.changed').forEach(n=>n.classList.remove('changed'));
        setStatus('Textes experts enregistrés. Copie de sauvegarde : '+(res.copie||'créée côté serveur'),'success');
      }catch(err){setStatus('Enregistrement refusé : '+err.message,'error');}finally{b.disabled=false;}},'b3-primary');}
  }
  function setEditing(section,editing){section.classList.toggle('editing',editing);section.querySelector('.b3-edit-panel').hidden=!editing;
    section.querySelector('.b3-mode').textContent=editing?'Revenir à la lecture':'Modifier le Markdown';
    section.querySelector('.b3-mode').setAttribute('aria-expanded',String(editing));
    // L'aperçu est TOUJOURS visible en édition, pour vérifier le rendu au fil des modifications.
    if(editing)section.querySelector('.b3-source').focus();
  }

  async function renderStudent(root){heading(root,'Préparer la version Élève','Les six étapes destinées à l’enfant sont distinctes du Kristal. Un brouillon n’est pas publié automatiquement.');
    const draft=await json('/api/brouillon-eleve/'+safeId(state.course.id)+'.json');const modules=draft.modules||[];
    note(root,draft._published_exists?'Une version Élève est publiée. Les modifications ci-dessous restent privées jusqu’à approbation.':'Aucune version Élève publiée pour ce cours.','b3-notice');
    const href=make(root,'a','b3-open-child','Voir la leçon dans l’espace Élève ↗');href.href='http://127.0.0.1:'+state.cfg.port_public+'/eleve/?cours='+safeId(state.course.id);href.target='_blank';href.rel='noopener noreferrer';
    const input=[];
    for(const [i,m] of modules.entries()){const card=make(root,'section','b3-child-card');make(card,'h3','',`Étape ${i+1}`);
      const title=make(card,'input','b3-title-input');title.value=m.titre||'';title.disabled=!state.cfg.edition;labelFor(card,'Titre destiné à l’enfant',title);
      const text=make(card,'textarea','b3-child-source');text.value=m.texte||'';text.disabled=!state.cfg.edition;
      const l=make(card,'label','','Explication et consigne (Markdown)');l.htmlFor=text.id='b3-child-'+i;
      const preview=make(card,'div','b3-markdown');renderMarkdown(preview,text.value);text.addEventListener('input',()=>renderMarkdown(preview,text.value));
      input.push({id:m.id,title,text});
    }
    const footer=make(root,'div','b3-publish-box');const notice=make(footer,'p','b3-hint','L’enregistrement conserve le brouillon. La publication requiert une relecture humaine et une confirmation.');
    const revLabel=make(footer,'label','b3-check');const confirm=make(revLabel,'input');confirm.type='checkbox';make(revLabel,'span','','J’ai relu toutes les étapes : vocabulaire adapté, réponses non dévoilées, consignes pour l’enfant uniquement.');
    const result=make(footer,'p','b3-feedback');result.setAttribute('role','status');
    const current=()=>({...draft,modules:input.map(x=>({id:x.id,titre:x.title.value,texte:x.text.value}))});
    const save=async()=>{const response=await request('/api/brouillon-eleve/'+safeId(state.course.id)+'.json',current());draft._revision=response._revision;return response;};
    const saveBtn=button(footer,'Enregistrer le brouillon',async()=>{saveBtn.disabled=true;try{await save();result.textContent='Brouillon enregistré, pas encore publié.';}catch(e){result.textContent='Échec : '+e.message;}finally{saveBtn.disabled=!state.cfg.edition;}},'b3-primary');
    const publish=button(footer,'Publier pour les élèves',async()=>{if(!confirm.checked){result.textContent='Confirme d’abord ta relecture.';return;}publish.disabled=true;
      try{await save();await request('/api/brouillon-eleve/'+safeId(state.course.id)+'/publier',{}, {'X-Ekole-Reviewed':'yes'});
        result.textContent='Version Élève publiée et disponible après actualisation du navigateur Élève.';
      }catch(e){result.textContent='Publication refusée : '+e.message;}finally{publish.disabled=!state.cfg.edition;}},'b3-secondary');
    saveBtn.disabled=publish.disabled=!state.cfg.edition;
  }

  async function getVisuals(cid){if(state.visualsCache.has(cid))return state.visualsCache.get(cid);
    const data=await json('/api/visuels/'+safeId(cid)+'.json');if(!Array.isArray(data.visuels))throw Error('Inventaire visuel invalide');state.visualsCache.set(cid,data);return data;
  }
  async function renderVisuals(root){heading(root,'Illustrations et prompts','Copie une intention visuelle, crée l’image dans un outil externe, puis dépose le fichier ici. Importer n’équivaut PAS à publier.');
    const doc=await getVisuals(state.course.id);if(!doc.visuels.length){note(root,'Aucun emplacement visuel défini dans le Kristal. Il n’est pas possible d’inventer un emplacement depuis cet atelier.','b3-notice');return;}
    for(const visual of doc.visuels){const card=make(root,'section','b3-visual');card.id='b3-slot-'+visual.slot;
      make(card,'h3','',visual.slot==='concept'?'Image de la notion':visual.slot==='situation'?'Image de la situation':visual.slot);
      note(card,`${visual.published?'Publiée pour l’élève':'Non publiée'} · ${visual.file_name||'aucun fichier'}`,'b3-tag');
      const pLabel=make(card,'label','','Prompt du Kristal (non visible aux élèves)');const prompt=make(card,'textarea','b3-prompt');prompt.readOnly=true;prompt.value=visual.prompt||'';prompt.rows=5;
      let feedback=make(card,'p','b3-feedback');feedback.setAttribute('role','status');
      button(card,'Copier le prompt',async()=>{try{await navigator.clipboard.writeText(prompt.value);feedback.textContent='Prompt copié dans le presse-papiers.';}
        catch(e){prompt.select();feedback.textContent='Copie impossible ici. Prompt sélectionné pour copie manuelle.';}},'b3-secondary');
      if(visual.alt)note(card,'Description alternative : '+visual.alt,'b3-hint');
      const existing=make(card,'div','b3-image-holder');if(visual.file_name){const image=make(existing,'img');image.src='/api/media/'+safeId(state.course.id)+'/'+safeId(visual.slot)+'?v='+Date.now();image.alt=visual.alt||'Image du Kristal';
        image.onerror=()=>{image.replaceWith(document.createTextNode('Aperçu de la source indisponible. Le fichier peut encore être présent.'));};}
      else note(existing,'Aucune image installée.','b3-hint');
      const drop=make(card,'div','b3-drop');drop.setAttribute('role','group');drop.setAttribute('aria-label','Déposer une image pour '+visual.slot);
      make(drop,'strong','','Glisse un fichier image ici');note(drop,'ou choisis un PNG, JPG, WebP · maximum 12 Mo. Une URL ne suffit pas.','b3-hint');
      const file=make(drop,'input');file.type='file';file.accept='image/png,image/jpeg,image/webp';file.disabled=!state.cfg.edition;
      const pic=make(card,'img','b3-preview');pic.hidden=true;pic.alt='Aperçu du fichier à importer';
      const repLabel=make(card,'label','b3-check');const replace=make(repLabel,'input');replace.type='checkbox';replace.disabled=!state.cfg.edition;
      make(repLabel,'span','','Je confirme le remplacement du fichier existant (sauvegarde automatique).');
      const upload=button(card,'Installer l’image dans le Kristal',async()=>{if(!selected){feedback.textContent='Sélectionne d’abord une image.';return;}
        if(selected.size>12*1024*1024){feedback.textContent='Fichier trop gros (12 Mo maximum).';return;}
        upload.disabled=true;try{const response=await fetch('/api/visuels/'+safeId(state.course.id)+'/'+safeId(visual.slot),{
          method:'POST',credentials:'same-origin',headers:{'Content-Type':'application/octet-stream','X-Ekole-CSRF':state.cfg.csrf,'X-Ekole-Replace':replace.checked?'yes':'no'},body:await selected.arrayBuffer()});
          if(!response.ok)throw Error('HTTP '+response.status+' : '+(await response.text()).slice(0,200));
          state.visualsCache.delete(state.course.id);await render();setStatus('Image installée. Elle doit être approuvée séparément avant publication.','success');
        }catch(e){feedback.textContent='Import refusé : '+e.message;upload.disabled=!state.cfg.edition;}},'b3-primary');upload.disabled=!state.cfg.edition;
      const publishBox=make(card,'div','b3-review');const checkedLabel=make(publishBox,'label','b3-check');const checked=make(checkedLabel,'input');checked.type='checkbox';checked.disabled=!state.cfg.edition;
      make(checkedLabel,'span','','J’ai vérifié l’exactitude, les droits et l’adaptation pédagogique de cette image.');
      const action=visual.published?'retirer':'publier';const publish=button(publishBox,visual.published?'Retirer de l’espace Élève':'Approuver et publier l’image',async()=>{
        if(!checked.checked){feedback.textContent='Coche la confirmation de relecture avant de publier ou retirer.';return;}publish.disabled=true;
        try{await request('/api/visuels/'+safeId(state.course.id)+'/'+safeId(visual.slot)+'/'+action,{}, {'X-Ekole-Reviewed':'yes'});
          state.visualsCache.delete(state.course.id);await render();setStatus(visual.published?'Image retirée de la vue Élève.':'Image approuvée et publiée pour l’élève.','success');
        }catch(e){feedback.textContent='Validation refusée : '+e.message;publish.disabled=!state.cfg.edition;}},'b3-secondary');publish.disabled=!state.cfg.edition;
      let selected=null,localUrl=null;const choose=f=>{if(!f)return;
        if(!['image/png','image/jpeg','image/webp'].includes(f.type)||f.size>12*1024*1024){feedback.textContent='Choisis PNG/JPEG/WebP de moins de 12 Mo.';return;}
        selected=f;if(localUrl)URL.revokeObjectURL(localUrl);localUrl=URL.createObjectURL(f);pic.src=localUrl;pic.hidden=false;
        feedback.textContent='Fichier sélectionné : '+f.name+'. Aperçu local; non enregistré et non publié.';
      };
      file.addEventListener('change',()=>choose(file.files?.[0]));
      for(const ev of ['dragenter','dragover'])drop.addEventListener(ev,e=>{e.preventDefault();drop.classList.add('over');});
      for(const ev of ['dragleave','drop'])drop.addEventListener(ev,e=>{e.preventDefault();drop.classList.remove('over');});
      drop.addEventListener('drop',e=>{if(!state.cfg.edition)return;choose(e.dataTransfer.files?.[0]);});
    }
    if(state.slotToFocus){const focus=document.getElementById('b3-slot-'+state.slotToFocus);state.slotToFocus='';focus?.scrollIntoView({block:'start'});}
  }

  // Inventaire v21 inspiré des filtres historiques, rebranché sur le contrat local v3.
  async function renderAlbum(root){heading(root,'Album des images pédagogiques','Vue d’ensemble des emplacements déclarés dans les Kristals. Seules les ressources autorisées par les manifestes peuvent être importées.');
    const filters=make(root,'section','b3-album-controls');const gradeLabel=make(filters,'label','','Parcours');const grade=make(filters,'select');
    const grades=state.pack.parcours||[];const feature=state.pack.parcours_mis_en_avant;
    for(const [value,text] of [['','Tous les cours'],...grades.map(g=>[g.id,g.titre])]){const option=make(grade,'option','',text);option.value=value;if(value===feature)option.selected=true;}
    const subjectLabel=make(filters,'label','','Matière');const subject=make(filters,'select');
    for(const value of ['',...[...new Set(state.pack.cours.map(x=>x.discipline).filter(Boolean))].sort((a,b)=>a.localeCompare(b,'fr'))]){const o=make(subject,'option','',value||'Toutes les matières');o.value=value;}
    const statusLabel=make(filters,'label','','Statut');const status=make(filters,'select');for(const [v,text] of [['','Tous'],['published','Publiée'],['installed','Image présente, non publiée'],['missing','Image à créer']]){const o=make(status,'option','',text);o.value=v;}
    const searchLabel=make(filters,'label','','Recherche');const search=make(filters,'input');search.type='search';search.placeholder='Cours, prompt, emplacement…';
    const controls=make(filters,'div','b3-album-actions');const load=button(controls,'Actualiser l’inventaire',()=>loadAlbum(), 'b3-primary');
    const exportBtn=button(controls,'Exporter la sélection CSV',exportCsv,'b3-secondary');
    const counter=make(root,'p','b3-hint');const content=make(root,'div','b3-album-results');const paging=make(root,'div','b3-pagination');
    let selected=grade.value;grade.addEventListener('change',()=>{selected=grade.value;loadAlbum();});
    for(const el of [subject,status,search])el.addEventListener(el===search?'input':'change',()=>{state.albumPage=0;draw();});
    async function loadAlbum(){const generation=++state.albumEpoch;state.albumPage=0;content.replaceChildren();paging.replaceChildren();counter.textContent='Lecture de l’inventaire sur le serveur Enseignant…';
      const ids=selected?grades.find(x=>x.id===selected)?.cours_ids||[]:state.pack.cours.map(c=>c.id);
      const unique=[...new Set(ids.filter(id=>courseMeta(id)))];const rows=[];
      for(let i=0;i<unique.length;i+=6){const batch=unique.slice(i,i+6);const result=await Promise.allSettled(batch.map(cid=>getVisuals(cid)));
        if(state.albumEpoch!==generation)return;
        for(let j=0;j<result.length;j++){const res=result[j],cid=batch[j];if(res.status==='fulfilled')for(const v of res.value.visuels){rows.push({...v,cid,course:courseMeta(cid)});}}
        counter.textContent=`${Math.min(i+6,unique.length)} / ${unique.length} cours examinés…`;
      }
      state.albumRows=rows;draw();
    }
    function filtered(){const q=search.value.toLocaleLowerCase('fr');return state.albumRows.filter(v=>(!subject.value||v.course.discipline===subject.value)
        &&(!status.value||(status.value==='published'?v.published:status.value==='installed'?!!v.file_name&&!v.published:!v.file_name))
        &&(!q||[v.course.titre,v.course.discipline,v.cid,v.slot,v.prompt,v.alt].join(' ').toLocaleLowerCase('fr').includes(q)));}
    function draw(){content.replaceChildren();paging.replaceChildren();const rows=filtered();state.albumSubset=rows;
      const num=(r,cond)=>r.filter(cond).length;counter.textContent=`${rows.length} emplacement(s) · ${num(rows,v=>v.published)} publiés · ${num(rows,v=>v.file_name&&!v.published)} installés non publiés · ${num(rows,v=>!v.file_name)} manquants`;
      const per=18,start=state.albumPage*per;const visible=rows.slice(start,start+per);
      for(const v of visible){const card=make(content,'article','b3-album-card');make(card,'strong','',v.course.titre);
        note(card,v.course.discipline+' · '+v.slot,'b3-hint');note(card,v.published?'Publiée':v.file_name?'À approuver':'À illustrer','b3-tag');
        if(v.file_name){const image=make(card,'img');image.alt=v.alt||'Image actuelle';image.src='/api/media/'+safeId(v.cid)+'/'+safeId(v.slot);image.onerror=()=>{image.hidden=true;};}
        else note(card,(v.alt||v.prompt||'Aucune illustration').slice(0,150),'b3-hint');
        button(card,'Ouvrir la fiche',()=>selectCourse(v.cid,'visuals',v.slot),'b3-secondary');
      }
      const pages=Math.ceil(rows.length/per);if(pages>1){button(paging,'← Précédent',()=>{state.albumPage--;draw();},'b3-secondary').disabled=state.albumPage===0;
        make(paging,'span','',`${state.albumPage+1} / ${pages}`);
        button(paging,'Suivant →',()=>{state.albumPage++;draw();},'b3-secondary').disabled=state.albumPage===pages-1;}
      if(!rows.length)note(content,'Aucun emplacement correspondant aux filtres.','b3-empty');
    }
    function exportCsv(){const headers=['cours_id','cours','matiere','slot','statut','fichier','alt'];const quote=s=>'"'+String(s??'').replaceAll('"','""')+'"';
      const rows=[headers.join(','),...state.albumSubset.map(x=>[x.cid,x.course.titre,x.course.discipline,x.slot,x.published?'publié':x.file_name?'présent non publié':'absent',x.file_name||'',x.alt||''].map(quote).join(','))];
      const blob=new Blob(['\ufeff',rows.join('\r\n')],{type:'text/csv;charset=utf-8'});const url=URL.createObjectURL(blob);const a=make(document.body,'a');a.download='inventaire-ekole-images.csv';a.href=url;a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);
    }
    await loadAlbum();
  }
  bootstrap();
})();


/* Intégration Tandem : projection strictement enseignante via l'API Ekole existante.
 * L'absence de projection = aucune carte. Jamais d'accès direct à Orgo. */
(() => {
  async function afficherApercuSorciere() {
    const answer = await fetch('/api/tandem/preview.json', {cache:'no-store', credentials:'same-origin'});
    if (!answer.ok) return;
    const d = await answer.json();
    if (d.format !== 'ekole.tandem-teacher-preview/1.0' || d.mode !== 'synthetic'
        || d.authority !== 'orgo' || d.scenario_ref !== 'fete-sorciere'
        || !Array.isArray(d.tasks) || d.tasks.length !== 11) return;
    const main = document.querySelector('main.container');
    if (!main || document.getElementById('tandem-sorciere')) return;
    const section = document.createElement('section');
    section.id = 'tandem-sorciere';
    section.className = 'tandem-revue';
    section.setAttribute('aria-label', 'Aperçu Tandem de la Fête de la sorcière');
    function add(parent, tag, text, css) {
      const node = document.createElement(tag);
      if (css) node.className = css;
      node.textContent = text;
      parent.appendChild(node);
      return node;
    }
    add(section, 'h2', 'La Fête de la sorcière — parcours Tandem');
    add(section, 'p', 'Projection synthétique de 11 tâches issues de Kontexte, Kompose et Akor. Aucun Case ni Task opérationnel Orgo n’a été créé. Aucun droit enseignant ou élève n’est accordé.', 'tandem-note');
    const list = add(section,'div','', 'tandem-task-grid');
    for (const [index,t] of d.tasks.entries()) {
      if (!t || typeof t.task_ref !== 'string' || typeof t.role_code !== 'string' ||
          !['ready','waiting','in_progress','done','blocked'].includes(t.state)) return;
      const card = add(list,'article','', 'tandem-task');
      add(card,'small',`Étape ${index + 1} · ${t.state}`);
      add(card,'h3',t.task_ref);
      add(card,'p',`Rôle : ${t.role_code}`);
    }
    main.insertBefore(section, main.firstChild);
  }
  const run = () => {afficherApercuSorciere().catch(() => {});};
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded',run,{once:true});
  else run();
})();
