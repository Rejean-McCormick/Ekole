'use strict';
const $=s=>document.querySelector(s);
const el=(host,tag,cl='',text)=>{const node=document.createElement(tag);if(cl)node.className=cl;if(text!==undefined)node.textContent=String(text);host.append(node);return node;};
const tell=(msg)=>{$('#status').textContent=msg;};
let cfg,pack,course,revision='',section='text',urlDrafts=new Set();
const get=async url=>{const r=await fetch(url,{cache:'no-store'});if(!r.ok)throw Error('Erreur HTTP '+r.status);return r.json();};
async function start(){try{
 [cfg,pack]=await Promise.all([get('/api/editor-config'),get('/api/pack.json')]);
 $('#publicHome').href='http://127.0.0.1:'+cfg.port_public+'/eleve/';
 document.title=pack.nom+' — Atelier Enseignant';
 tell(pack.nom+' · '+pack.cours.length+' cours · '+(cfg.edition?'Édition locale activée.':'Lecture seule. Lancer avec --edition pour importer ou publier.'));
 for(const c of pack.cours){const o=el($('#cours'),'option','',(c.discipline||'Cours')+' · '+c.titre);o.value=c.id;}
 $('#cours').addEventListener('change',open);
 [['Text','text'],['Visuals','visuals'],['Student','student']].forEach(([id,val])=>$('#tab'+id).addEventListener('click',()=>{section=val;refresh();}));
 }catch(e){tell('Impossible d’ouvrir l’atelier : '+e.message);}}
async function open(){const cid=$('#cours').value;course=null;$('#editor').replaceChildren();if(!cid)return;
 try{const r=await fetch('/api/cours/'+encodeURIComponent(cid)+'.json',{cache:'no-store'});if(!r.ok)throw Error('Erreur HTTP '+r.status);
 const raw=await r.text();course=JSON.parse(raw);const sha=await crypto.subtle.digest('SHA-256',new TextEncoder().encode(raw));revision=Array.from(new Uint8Array(sha)).map(v=>v.toString(16).padStart(2,'0')).join('');
 await refresh();}catch(e){tell('Erreur de lecture : '+e.message);}}
async function refresh(){const root=$('#editor');root.replaceChildren();for(const [id,val] of [['Text','text'],['Visuals','visuals'],['Student','student']]){const b=$('#tab'+id);b.setAttribute('aria-current',section===val?'page':'false');}
 if(!course){el(root,'p','','Choisis un cours.');return;}
 if(section==='text')renderText(root);else if(section==='visuals')await renderVisuals(root);else await renderStudent(root);
}
function renderText(root){el(root,'h2','',course.titre);el(root,'p','tip','Ces textes sont les sources détaillées pour l’enseignant. Ils ne sont pas servis directement aux élèves.');
 for(const mod of course.modules||[]){const wrapper=el(root,'div','expert-module');const l=el(wrapper,'label','',mod.titre);const t=el(wrapper,'textarea');t.value=mod.texte||'';t.disabled=!cfg.edition;t.dataset.mid=mod.id;l.htmlFor='text-'+mod.id;t.id='text-'+mod.id;}
 if(cfg.edition){const save=el(root,'button','primary','Enregistrer les textes experts');save.type='button';save.addEventListener('click',saveText);}
}
async function saveText(){const updated={...course,_revision:revision,modules:course.modules.map((m,i)=>({...m,texte:document.querySelectorAll('textarea[data-mid]')[i].value}))};
 try{const result=await postJson('/api/cours/'+encodeURIComponent(course.id)+'.json',updated);revision=result._revision;course.modules=updated.modules;
 tell('Textes experts sauvegardés. Copie créée : '+result.copie);}catch(e){tell(e.message);}}
async function renderStudent(root){
 el(root,'h2','','Préparer la version pour l’élève');
 el(root,'p','tip','Rédige un brouillon adapté à l’âge des élèves. Enregistrer le brouillon ne publie rien. La publication exige une confirmation après relecture. Le Kristal original ne change pas.');
 let draft;try{draft=await get('/api/brouillon-eleve/'+encodeURIComponent(course.id)+'.json');}
 catch(e){el(root,'p','notice','Impossible de charger le brouillon : '+e.message);return;}
 const published=draft._published_exists;
 el(root,'p','badge',published?'Une version Élève est publiée pour ce cours.':'Aucune version Élève publiée pour ce cours.');
 const link=el(root,'a','student-preview','Voir le résultat dans Ekole Élève ↗');
 link.href='http://127.0.0.1:'+cfg.port_public+'/eleve/?cours='+encodeURIComponent(course.id);link.target='_blank';link.rel='noopener noreferrer';
 const inputs=[];
 for(let i=0;i<draft.modules.length;i++){
  const mod=draft.modules[i];const unit=el(root,'div','expert-module');el(unit,'h3','','Étape '+(i+1));
  const titleLabel=el(unit,'label','','Titre pour l’enfant');const title=el(unit,'input','text-field');title.value=mod.titre;title.disabled=!cfg.edition;
  const textLabel=el(unit,'label','','Explication et consigne destinées à l’enfant');const area=el(unit,'textarea','child-text');area.value=mod.texte;area.disabled=!cfg.edition;
  inputs.push({title,area,id:mod.id});
 }
 const reviewPanel=el(root,'div','publication');
 const confirmLabel=el(reviewPanel,'label','checkbox-label');const confirm=el(confirmLabel,'input');confirm.type='checkbox';
 el(confirmLabel,'span','','J’ai relu les six étapes : langage d’enfant, pas de corrigé anticipé, pas de consignes pour l’enseignant.');
 const save=el(reviewPanel,'button','primary','Enregistrer le brouillon');save.type='button';save.disabled=!cfg.edition;
 const publish=el(reviewPanel,'button','secondary','Publier la version Élève');publish.type='button';publish.disabled=!cfg.edition;
 const feedback=el(reviewPanel,'p','status');feedback.setAttribute('role','status');
 const collect=()=>({...draft,modules:inputs.map(x=>({id:x.id,titre:x.title.value,texte:x.area.value}))});
 save.addEventListener('click',async()=>{save.disabled=true;try{
  const result=await postJson('/api/brouillon-eleve/'+encodeURIComponent(course.id)+'.json',collect());
  draft._revision=result._revision;feedback.textContent='Brouillon enregistré. Non visible dans l’espace Élève.';
 }catch(e){feedback.textContent=e.message;}finally{save.disabled=!cfg.edition;}});
 publish.addEventListener('click',async()=>{
  if(!confirm.checked){feedback.textContent='Confirme d’abord ta revue pédagogique.';return;}
  publish.disabled=true;
  try{
   // On sauve explicitement les changements avant la publication.
   const doc=collect();const saving=await postJson('/api/brouillon-eleve/'+encodeURIComponent(course.id)+'.json',doc);
   draft._revision=saving._revision;
   const r=await fetch('/api/brouillon-eleve/'+encodeURIComponent(course.id)+'/publier',{
     method:'POST',headers:{'Content-Type':'application/json','X-Ekole-CSRF':cfg.csrf,'X-Ekole-Reviewed':'yes'},body:'{}'});
   if(!r.ok)throw Error('Publication refusée : '+await r.text());
   feedback.textContent='Version Élève publiée. Le texte expert original est conservé.';
   tell('Publication élève mise à jour. Recharge le portail public pour la voir.');
  }catch(e){feedback.textContent=e.message;}finally{publish.disabled=!cfg.edition;}
 });
}
async function renderVisuals(root){el(root,'h2','','Illustrations du Kristal');el(root,'p','tip','Copie un prompt, produis l’image dans l’outil de ton choix, puis dépose le fichier ici. Ekole ne génère pas l’image. Publication volontaire après revue.');
 let data;try{data=await get('/api/visuels/'+encodeURIComponent(course.id)+'.json');}catch(e){el(root,'p','notice','Inventaire visuel indisponible : '+e.message);return;}
 if(!data.visuels.length){el(root,'p','notice','Aucun emplacement visuel défini pour ce Kristal.');return;}
 for(const item of data.visuels)renderSlot(root,item);
}
function renderSlot(root,item){const wrap=el(root,'section','visual-slot');
 const heading=el(wrap,'h3','',item.slot==='concept'?'Image de la notion':item.slot==='situation'?'Image de situation':item.slot);
 el(wrap,'p','small','Emplacement '+item.slot+' · '+(item.published?'Publié pour les élèves':'Non publié pour les élèves'));
 const text=el(wrap,'label','', 'Prompt conceptuel à copier');const prompt=el(wrap,'textarea','prompt-field');prompt.readOnly=true;prompt.value=item.prompt||'';prompt.rows=5;
 const copy=el(wrap,'button','secondary','Copier le prompt');copy.type='button';copy.addEventListener('click',async()=>{try{await navigator.clipboard.writeText(prompt.value);feedback.textContent='Prompt copié.';}catch(_){prompt.select();document.execCommand('copy');feedback.textContent='Prompt sélectionné et copié si le navigateur l’autorise.';}});
 const info=el(wrap,'p','tip','Image destinée à : '+(item.alt||'Illustration de la leçon'));
 const existing=el(wrap,'div','existing-image');if(item.file_name){const img=el(existing,'img');img.src='/api/media/'+encodeURIComponent(course.id)+'/'+encodeURIComponent(item.slot)+'?v='+Date.now();img.alt=item.alt||'Aperçu';el(existing,'p','small','Fichier : '+item.file_name);}else el(existing,'p','small','Aucune image enregistrée.');
 const drop=el(wrap,'div','dropzone');drop.tabIndex=0;drop.setAttribute('role','group');drop.setAttribute('aria-label','Déposer une image pour '+item.slot);
 el(drop,'strong','','Glisse une image ici');el(drop,'p','small','ou utilise le sélecteur · PNG, JPEG, WebP · 12 Mo max');
 const input=el(drop,'input');input.type='file';input.accept='image/png,image/jpeg,image/webp';input.setAttribute('aria-label','Choisir une image '+item.slot);
 const preview=el(wrap,'img','image-preview');preview.hidden=true;preview.alt='Prévisualisation avant import';
 const upload=el(wrap,'button','primary','Installer l’image dans le Kristal');upload.type='button';upload.disabled=!cfg.edition;
 const replaceLabel=el(wrap,'label','checkbox-label');const replace=el(replaceLabel,'input');replace.type='checkbox';el(replaceLabel,'span','','Autoriser le remplacement de l’image existante (sauvegarde)');
 const publication=el(wrap,'div','publication');const reviewedLabel=el(publication,'label','checkbox-label');const reviewed=el(reviewedLabel,'input');reviewed.type='checkbox';el(reviewedLabel,'span','','J’ai vérifié l’exactitude et l’adaptation de cette image à l’enfant.');
 const publish=el(publication,'button','secondary',item.published?'Retirer de l’espace Élève':'Approuver et publier pour l’élève');publish.type='button';publish.disabled=!cfg.edition;
 const feedback=el(wrap,'p','status');feedback.setAttribute('role','status');feedback.setAttribute('aria-live','polite');
 let chosen=null,blobUrl=null;
 function choose(file){if(!file)return;chosen=file;if(blobUrl)URL.revokeObjectURL(blobUrl);blobUrl=URL.createObjectURL(file);preview.src=blobUrl;preview.hidden=false;feedback.textContent='Image choisie : '+file.name+' ('+Math.round(file.size/1024)+' Ko).';}
 input.addEventListener('change',()=>choose(input.files[0]));
 ['dragenter','dragover'].forEach(type=>drop.addEventListener(type,e=>{e.preventDefault();drop.classList.add('over');}));
 ['dragleave','drop'].forEach(type=>drop.addEventListener(type,e=>{e.preventDefault();drop.classList.remove('over');}));
 drop.addEventListener('drop',e=>choose(e.dataTransfer.files[0]));
 upload.addEventListener('click',async()=>{if(!chosen){feedback.textContent='Choisis d’abord une image.';return;}if(!cfg.edition)return;
 upload.disabled=true;try{const res=await fetch('/api/visuels/'+encodeURIComponent(course.id)+'/'+encodeURIComponent(item.slot),{
 method:'POST',headers:{'Content-Type':'application/octet-stream','X-Ekole-CSRF':cfg.csrf,'X-Ekole-Replace':replace.checked?'yes':'no'},body:await chosen.arrayBuffer()});
 if(!res.ok)throw Error('Import refusé : '+await res.text());const value=await res.json();feedback.textContent='Image importée : '+value.file_name+' ('+value.width+' × '+value.height+' px). Non publiée : validation nécessaire.';
 if(blobUrl)URL.revokeObjectURL(blobUrl);await renderVisualsAfterChange();
 }catch(e){feedback.textContent=e.message;upload.disabled=false;}});
 publish.addEventListener('click',async()=>{
 if(!reviewed.checked){feedback.textContent='Coche d’abord la confirmation de revue pédagogique.';return;}
 if(!cfg.edition)return;publish.disabled=true;try{
 const route='/api/visuels/'+encodeURIComponent(course.id)+'/'+encodeURIComponent(item.slot)+'/'+(item.published?'retirer':'publier');
 const r=await fetch(route,{method:'POST',headers:{'X-Ekole-CSRF':cfg.csrf,'X-Ekole-Reviewed':'yes','Content-Type':'application/json'},body:'{}'});
 if(!r.ok)throw Error('Publication refusée : '+await r.text());await renderVisualsAfterChange();tell(item.published?'Image retirée de la publication élève.':'Image approuvée et publiée.');
 }catch(e){feedback.textContent=e.message;publish.disabled=false;}});
}
async function renderVisualsAfterChange(){await renderVisuals($('#editor').replaceChildren()||$('#editor'));}
async function postJson(url,data){const r=await fetch(url,{method:'POST',headers:{'Content-Type':'application/json','X-Ekole-CSRF':cfg.csrf},body:JSON.stringify(data)});
 if(!r.ok)throw Error('Enregistrement refusé : '+await r.text());return r.json();}
start();
