/* Ekole v15 — atelier d'images pour le seul serveur Enseignant (127.0.0.1:8766).
 * Aucune IA embarquée. Les fichiers déposés par l'auteur sont normalisés côté serveur.
 */
(()=>{'use strict';
let configuration;
const add=(parent,tag,cls='',value)=>{const x=document.createElement(tag);if(cls)x.className=cls;if(value!==undefined)x.textContent=String(value);parent.append(x);return x;};
const getConfig=async()=>{if(!configuration){const res=await fetch('/api/image-editor-config.json',{credentials:'same-origin',cache:'no-store'});if(!res.ok)throw Error('Ouvre Ekole Enseignant avec sa session locale.');configuration=await res.json();}return configuration;};
function attach(parent,courseId,slot,exists,onSaved,onDeleted){
  const wrapper=add(parent,'section','image-editor-v15');
  add(wrapper,'h4','','Déposer une illustration · Ekole Enseignant');
  add(wrapper,'p','image-editor-help','Télécharge ton image de ChatGPT, puis dépose son fichier ici ou utilise « Choisir une image ». Aucune image n’est générée par Ekole.');
  const zone=add(wrapper,'div','image-drop-zone');zone.tabIndex=0;zone.setAttribute('role','group');zone.setAttribute('aria-label','Zone de dépôt image');
  add(zone,'strong','','Glisse ton image ici');add(zone,'small','','PNG · JPEG · WebP · maximum 12 Mo avant optimisation');
  const choose=add(zone,'label','image-file-label','Choisir une image');const input=add(choose,'input');input.type='file';input.accept='image/png,image/jpeg,image/webp';input.setAttribute('aria-label','Choisir une image à déposer');
  const preview=add(wrapper,'img','image-upload-preview');preview.hidden=true;preview.alt='Prévisualisation du fichier choisi';
  preview.onload=()=>{preview.hidden=false;zone.classList.add('file-preview-ready');};
  preview.onerror=()=>{preview.hidden=true;zone.classList.remove('file-preview-ready');feedback.textContent='Aperçu impossible à ouvrir. Vérifie que le fichier est une image valide.';};
  const settings=add(wrapper,'div','image-upload-settings');
  const fmt=add(settings,'label','','Format de sortie');const format=add(fmt,'select');
  for(const [id,label] of [['webp','WebP optimisé'],['png','PNG'],['jpeg','JPEG']]){const o=add(format,'option','',label);o.value=id;}
  const sizeLabel=add(settings,'label','','Largeur maximale');const width=add(sizeLabel,'select');
  for(const n of [768,1024,1536,2048]){const o=add(width,'option','',n+' px');o.value=String(n);}width.value='1536';
  const replaceLabel=add(wrapper,'label','image-replace-label');const replace=add(replaceLabel,'input');replace.type='checkbox';add(replaceLabel,'span','',exists?'Autoriser le remplacement de l’image existante (sauvegarde créée)':'Autoriser le remplacement si une image existe déjà');
  const buttons=add(wrapper,'div','toolbar');const submit=add(buttons,'button','button','Installer dans le Kristal et actualiser Ekole Élève');submit.type='button';submit.disabled=true;
  const erase=add(buttons,'button','button secondary image-delete-button','Effacer l’image');erase.type='button';erase.disabled=!exists;
  erase.setAttribute('aria-label','Effacer l’image déjà enregistrée pour cet emplacement');
  const fileName=add(wrapper,'p','image-file-target','Nom final : '+slot+'.webp · dossier du Kristal '+courseId);
  const feedback=add(wrapper,'p','image-upload-feedback','Aucune image sélectionnée.');feedback.setAttribute('role','status');feedback.setAttribute('aria-live','polite');
  let selected=null,previewURL=null;
  const currentName=()=>slot+({webp:'.webp',png:'.png',jpeg:'.jpg'}[format.value]);
  const refreshName=()=>{fileName.textContent='Fichier final : kristals/'+courseId+'/experience/images/'+currentName();};format.onchange=refreshName;refreshName();
  function pick(file){
    if(!file)return;
    if(!['image/png','image/jpeg','image/webp'].includes(file.type) && !(file.type==='' && /\.(png|jpe?g|webp)$/i.test(file.name))){feedback.textContent='Format non pris en charge : utiliser PNG, JPEG ou WebP.';return;}
    if(file.size>12*1024*1024||file.size<20){feedback.textContent='Fichier invalide ou supérieur à 12 Mo.';return;}
    selected=file;submit.disabled=false;feedback.textContent='Fichier prêt : '+file.name+' ('+Math.ceil(file.size/1024)+' Ko).';
    if(previewURL)URL.revokeObjectURL(previewURL);
    preview.hidden=true;zone.classList.remove('file-preview-ready');
    previewURL=URL.createObjectURL(file);preview.src=previewURL;
  }
  input.addEventListener('change',()=>{pick(input.files?.[0]);input.value='';});
  for(const event of ['dragenter','dragover'])zone.addEventListener(event,e=>{e.preventDefault();zone.classList.add('drag-hover');});
  zone.addEventListener('dragleave',e=>{e.preventDefault();zone.classList.remove('drag-hover');});
  zone.addEventListener('drop',e=>{e.preventDefault();zone.classList.remove('drag-hover');pick(e.dataTransfer?.files?.[0]);});
  submit.addEventListener('click',async()=>{
    if(!selected)return;
    submit.disabled=true;feedback.textContent='Contrôle du fichier, optimisation et installation…';
    try{
      const config=await getConfig();
      const response=await fetch('/api/visual-upload/'+encodeURIComponent(courseId)+'/'+encodeURIComponent(slot),{
        method:'POST',credentials:'same-origin',headers:{'Content-Type':'application/octet-stream','X-Ekole-CSRF':config.csrf,'X-Ekole-Format':format.value,'X-Ekole-Max-Width':width.value,'X-Ekole-Replace':replace.checked?'yes':'no'},body:await selected.arrayBuffer()
      });
      if(!response.ok)throw Error((await response.text()).slice(0,240));
      const data=await response.json();
      feedback.textContent='Image enregistrée : '+data.file_name+' ('+data.width+' × '+data.height+' px). Affichage en cours…';
      selected=null;replace.checked=false;erase.disabled=false;
      replaceLabel.querySelector('span').textContent='Autoriser le remplacement de l’image existante (sauvegarde créée)';
      if(typeof onSaved==='function')onSaved(data,feedback);
      else if(typeof window.ekoleRefreshVisualsV15==='function')await window.ekoleRefreshVisualsV15();
    }catch(err){feedback.textContent='Échec de l’installation : '+err.message;submit.disabled=false;}
  });
  erase.addEventListener('click',async()=>{
    if(erase.disabled)return;
    if(!window.confirm('Effacer l’image enregistrée pour '+courseId+' / '+slot+' ?\nUne sauvegarde privée sera conservée.'))return;
    erase.disabled=true;submit.disabled=true;feedback.textContent='Suppression et actualisation de la fiche…';
    try{
      const config=await getConfig();
      const response=await fetch('/api/visual-image/'+encodeURIComponent(courseId)+'/'+encodeURIComponent(slot),{
        method:'DELETE',credentials:'same-origin',headers:{'X-Ekole-CSRF':config.csrf,'X-Ekole-Delete-Confirm':'yes'}
      });
      if(!response.ok)throw Error((await response.text()).slice(0,240));
      const data=await response.json();
      selected=null;replace.checked=false;input.value='';
      if(previewURL){URL.revokeObjectURL(previewURL);previewURL=null;}
      preview.removeAttribute('src');preview.hidden=true;zone.classList.remove('file-preview-ready');
      replaceLabel.querySelector('span').textContent='Autoriser le remplacement si une image existe déjà';
      feedback.textContent='✓ Image effacée. Sauvegarde privée créée. Tu peux déposer une autre illustration.';
      if(typeof onDeleted==='function')onDeleted(data,feedback);
      else if(typeof window.ekoleRefreshVisualsV15==='function')await window.ekoleRefreshVisualsV15();
    }catch(err){erase.disabled=false;feedback.textContent='Échec de suppression : '+err.message;}
  });
  wrapper.addEventListener('DOMNodeRemoved',()=>{if(previewURL)URL.revokeObjectURL(previewURL);},{once:true});
  if(exists)replace.checked=false;
  return wrapper;
}
window.EkoleImagesV15={attach};
})();
