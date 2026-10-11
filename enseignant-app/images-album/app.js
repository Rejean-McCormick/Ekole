(()=>{'use strict';
const $=id=>document.getElementById(id);
const ST={items:[],filtered:[],selected:null,page:0,perPage:30,token:'',config:null,pending:null,objectURL:null};
const LABEL={presente:'Présente',manquante:'Manquante',a_synchroniser:'À synchroniser',source_absente:'Source absente'};
const FRAME={epure:'Épuré',carte:'Carte douce',galerie:'Galerie',carnet:'Carnet',bandeau:'Bandeau',sombre:'Focus sombre',bordure:'Bordure colorée'};
const mk=(tag,parent,cls='',str)=>{let e=document.createElement(tag);if(cls)e.className=cls;if(str!==undefined)e.textContent=str;parent.append(e);return e};
const button=(parent,label,callback,cls='')=>{const e=mk('button',parent,cls,label);e.type='button';e.addEventListener('click',callback);return e};
const status=(msg,cls='')=>{const e=$('globalStatus');e.textContent=msg;e.className='global-status '+cls};
const imageURL=x=>x.public_url?'/api/kristal-image/'+encodeURIComponent(x.course_id)+'/'+encodeURIComponent(x.slot+x.public_url.slice(x.public_url.lastIndexOf('.')))+'?v='+encodeURIComponent(x.revision||Date.now()):'';
const select=(p,values,fmt)=>{const old=p.value;p.replaceChildren();const first=mk('option',p,'',fmt);first.value='';values.forEach(v=>{const opt=mk('option',p,'',v.label);opt.value=String(v.value)});p.value=values.some(v=>String(v.value)===old)?old:''};
const sorted=(vals)=>[...new Set(vals.filter(v=>v!==null&&v!==undefined&&String(v)!==''))].sort((a,b)=>String(a).localeCompare(String(b),'fr',{numeric:true}));
function updateFilters(){const items=ST.items;
 select($('year'),sorted(items.map(x=>x.year)).map(n=>({value:n,label:n+'e année'})),'Toutes les années');
 select($('subject'),sorted(items.map(x=>x.subject)).map(n=>({value:n,label:n})),'Toutes les matières');
 select($('slot'),sorted(items.map(x=>x.slot)).map(n=>({value:n,label:n})),'Tous les emplacements');
 const ids=[...new Map(items.map(x=>[x.course_id,x])).values()].sort((a,b)=>a.course_title.localeCompare(b.course_title,'fr'));
 select($('course'),ids.map(x=>({value:x.course_id,label:x.course_title+' · '+x.course_id})),'Tous les cours');
}
function filter(){const text=$('search').value.trim().toLocaleLowerCase('fr-CA');const get=id=>$(id).value;
 ST.filtered=ST.items.filter(x=>(!get('year')||String(x.year)===get('year'))&&(!get('subject')||x.subject===get('subject'))&&(!get('course')||x.course_id===get('course'))&&(!get('slot')||x.slot===get('slot'))&&(!get('state')||x.status===get('state'))&&(!text||[x.course_id,x.course_title,x.concept,x.slot,x.alt,x.prompt].join(' ').toLocaleLowerCase('fr-CA').includes(text)));
 ST.page=Math.min(ST.page,Math.max(0,Math.ceil(ST.filtered.length/ST.perPage)-1));drawCards();}
function drawCards(){const p=$('cards');p.replaceChildren();p.classList.toggle('list-mode',$('view').value==='list');$('resultCount').textContent=ST.filtered.length+' emplacement(s) trouvé(s)';
 const slice=ST.filtered.slice(ST.page*ST.perPage,(ST.page+1)*ST.perPage);
 for(const x of slice){const b=mk('button',p,'image-card');b.type='button';b.setAttribute('aria-pressed',String(ST.selected===x.key));b.addEventListener('click',()=>{ST.selected=x.key;ST.pending=null;releaseBlob();drawCards();drawDetail()});
  const t=mk('div',b,'thumb');if(x.public_url){const img=mk('img',t);img.src=imageURL(x);img.alt=x.alt||x.concept||'Illustration';img.loading='lazy';img.onerror=()=>{img.remove();mk('span',t,'','Image non chargée')}}else mk('span',t,'',x.status==='a_synchroniser'?'↻ À synchroniser':'✦ Image attendue');
  mk('b',b,'',x.course_title);mk('small',b,'',x.course_id+' · '+x.slot+' · '+(x.year||'?')+'e année');const s=mk('span',b,'pill '+(x.status==='presente'?'':x.status==='manquante'?'missing':'pending'),LABEL[x.status]||x.status);
 }
 if(!slice.length)mk('p',p,'empty','Aucune image pour ces filtres.');
 const total=Math.max(1,Math.ceil(ST.filtered.length/ST.perPage));$('pageInfo').textContent='Page '+(ST.page+1)+' / '+total;$('previous').disabled=ST.page===0;$('next').disabled=ST.page>=total-1;}
function releaseBlob(){if(ST.objectURL){URL.revokeObjectURL(ST.objectURL);ST.objectURL=null;}}
function promptCode(x){return 'EKOLE-IMG-'+x.course_id.toUpperCase().replace(/[^A-Z0-9-]/g,'-')+'-'+x.slot.toUpperCase().replace(/[^A-Z0-9_-]/g,'-')}
function fullPrompt(x){return 'RÉFÉRENCE TECHNIQUE (hors image) : '+promptCode(x)+'\n\n'+x.prompt+'\n\nIMPORTANT : ne pas écrire, dessiner ni intégrer la référence technique, aucun code d’identification ou filigrane dans les pixels de l’image. La référence ne sert qu’à retrouver le bon emplacement Ekole.'}
async function copy(text,btn){const orig=btn.textContent;try{await navigator.clipboard.writeText(text);btn.textContent='✓ Copié !';setTimeout(()=>{if(btn.isConnected)btn.textContent=orig},2600)}catch(e){btn.textContent='Copie impossible : sélectionner le texte';setTimeout(()=>{if(btn.isConnected)btn.textContent=orig},3500)}}
const opt=(el,val,label)=>{let o=mk('option',el,'',label);o.value=val};
function pic(parent,x){const frame=mk('div',parent,'large-preview');if(x.public_url){const img=mk('img',frame);img.src=imageURL(x);img.alt=x.alt||x.concept||'Illustration';img.onerror=()=>{frame.replaceChildren();mk('p',frame,'placeholder','La projection pointe vers une image inaccessible. Essaie de synchroniser.');}}else mk('div',frame,'placeholder',x.status==='a_synchroniser'?'Image présente dans le Kristal mais non publiée.':'Aucune image enregistrée pour cet emplacement.');return frame;}
function makeLabel(parent,label,type='text',value=''){const l=mk('label',parent,'',label);const inp=mk('input',l);inp.type=type;inp.value=value;return inp}
function updateFramePreview(){const preview=$('albumFramePreview');if(!preview)return;preview.dataset.style=$('frameStyle').value;preview.dataset.size=$('frameSize').value;preview.style.setProperty('--preview-border',/^#[0-9a-f]{6}$/i.test($('frameColor').value)?$('frameColor').value:'#1e6864');$('frameColorRow').hidden=$('frameStyle').value!=='bordure';}
function frameSection(parent,x){const wrap=mk('section',parent,'edit-panel');mk('h3',wrap,'','Cadre d’affichage');mk('p',wrap,'hint','Réglage global : il s’applique à toutes les images présentes des fiches Élève.');
 const preview=mk('div',wrap,'frame-preview');preview.id='albumFramePreview';const img=mk('img',preview);if(x.public_url){img.src=imageURL(x);img.alt='Aperçu du cadre'}else{img.hidden=true;mk('p',preview,'','Le cadre apparaît sur les images présentes.');}
 const sl=mk('label',wrap,'','Style');const style=mk('select',sl);style.id='frameStyle';Object.entries(FRAME).forEach(([v,n])=>opt(style,v,n));style.value=ST.config.style;
 const si=mk('label',wrap,'','Taille');const size=mk('select',si);size.id='frameSize';[['compact','Compacte'],['normal','Normale'],['grand','Grande']].forEach(([v,n])=>opt(size,v,n));size.value=ST.config.size;
 const row=mk('label',wrap,'frame-color','Couleur de bordure');row.id='frameColorRow';const color=mk('input',row);color.id='frameColor';color.type='color';color.value=ST.config.borderColor||'#1e6864';
 [style,size,color].forEach(i=>i.addEventListener('input',updateFramePreview));const btn=button(wrap,'Enregistrer le cadre pour Ekole Élève',async()=>{
  const cfg={format:'ekole.image-frames/1.0',style:style.value,size:size.value,borderColor:color.value};btn.disabled=true;try{const r=await fetch('/api/cadres-images.json',{method:'POST',credentials:'same-origin',headers:{'Content-Type':'application/json','X-Ekole-CSRF':ST.token},body:JSON.stringify(cfg)});if(!r.ok)throw Error((await r.text()).slice(0,120));ST.config=await r.json();status('✓ Cadre enregistré et appliqué à la vue Élève.','good')}catch(e){status('Échec du réglage : '+e.message,'error')}finally{btn.disabled=false}
 },'primary');updateFramePreview();}
function uploadSection(parent,x){const s=mk('section',parent,'edit-panel');mk('h3',s,'','Remplacer / ajouter');
 if(!x.editable){mk('p',s,'hint','Ce cours ne dispose pas encore d’un manifeste visuel canonique. Édition désactivée pour éviter de créer une fausse source.');return;}
 const zone=mk('div',s,'upload-drop');mk('b',zone,'','Dépose ton image ici');mk('p',zone,'hint','PNG, JPG ou WebP · maximum 12 Mo');const file=makeLabel(zone,'Ou sélectionner le fichier','file');file.accept='image/png,image/jpeg,image/webp';
 const before=mk('img',s,'selected-preview');before.hidden=true;before.alt='Aperçu local avant enregistrement';const note=mk('p',s,'status','Aucun fichier choisi');
 const formatLabel=mk('label',s,'','Format de sortie');const fmt=mk('select',formatLabel);[['webp','WebP'],['png','PNG'],['jpeg','JPEG']].forEach(([id,l])=>opt(fmt,id,l));
 const widthLabel=mk('label',s,'','Largeur maximale');const width=mk('select',widthLabel);[768,1024,1536,2048].forEach(n=>opt(width,String(n),n+' px'));width.value='1536';
 const replace=makeLabel(s,'Confirmer le remplacement d’une image existante','checkbox');replace.checked=false;
 const b=button(s,'Enregistrer dans le Kristal',async()=>{if(!ST.pending){note.textContent='Choisis une image.';return;}b.disabled=true;note.textContent='Optimisation, contrôle et enregistrement…';
  try{const r=await fetch('/api/visual-upload/'+encodeURIComponent(x.course_id)+'/'+encodeURIComponent(x.slot),{method:'POST',credentials:'same-origin',headers:{'Content-Type':'application/octet-stream','X-Ekole-CSRF':ST.token,'X-Ekole-Format':fmt.value,'X-Ekole-Max-Width':width.value,'X-Ekole-Replace':replace.checked?'yes':'no'},body:await ST.pending.arrayBuffer()});if(!r.ok)throw Error((await r.text()).slice(0,240));await r.json();ST.pending=null;releaseBlob();status('✓ Image enregistrée, projection Élève actualisée.','good');await reload(true)}catch(e){note.textContent='Échec : '+e.message;b.disabled=false}},'primary');b.disabled=true;
 function pick(f){if(!f)return;if(!/\.(png|jpe?g|webp)$/i.test(f.name)||f.size<20||f.size>12*1024*1024){note.textContent='Fichier rejeté (format ou taille).';return;}ST.pending=f;releaseBlob();ST.objectURL=URL.createObjectURL(f);before.src=ST.objectURL;before.hidden=false;note.textContent=f.name+' · '+Math.ceil(f.size/1024)+' Ko';b.disabled=false;}
 file.addEventListener('change',()=>{pick(file.files?.[0]);file.value=''});
 for(const event of ['dragover','dragenter'])zone.addEventListener(event,e=>{e.preventDefault();zone.classList.add('dragover')});
 zone.addEventListener('dragleave',e=>{e.preventDefault();zone.classList.remove('dragover')});
 zone.addEventListener('drop',e=>{e.preventDefault();zone.classList.remove('dragover');pick(e.dataTransfer?.files?.[0])});
 if(x.status==='presente'||x.status==='a_synchroniser'){
  button(s,'Effacer l’image (avec sauvegarde)',async()=>{if(!confirm('Effacer '+x.course_id+' / '+x.slot+' ? Une sauvegarde privée sera créée.'))return;
   try{const r=await fetch('/api/visual-image/'+encodeURIComponent(x.course_id)+'/'+encodeURIComponent(x.slot),{method:'DELETE',credentials:'same-origin',headers:{'X-Ekole-CSRF':ST.token,'X-Ekole-Delete-Confirm':'yes'}});if(!r.ok)throw Error((await r.text()).slice(0,240));status('✓ Image effacée, description restaurée.','good');await reload(true)}catch(e){status('Suppression refusée : '+e.message,'error')}
  },'danger');
 }
}
function drawDetail(){const root=$('details');root.replaceChildren();const x=ST.items.find(v=>v.key===ST.selected);if(!x){mk('h2',root,'','Fiche d’image');mk('p',root,'','Sélectionne une image dans l’album.');return;}
 mk('h2',root,'',x.course_title);mk('p',root,'detail-meta',x.course_id+' · '+(x.year||'?')+'e année · '+x.subject+' · '+x.slot);mk('p',root,'pill '+(x.status==='presente'?'':'missing'),LABEL[x.status]);pic(root,x);
 mk('p',root,'',x.alt||x.concept||'Sans description courte');const links=mk('div',root,'row');const course=mk('a',links,'','Ouvrir la fiche Élève ↗');course.href='http://127.0.0.1:8765/eleve/?cours='+encodeURIComponent(x.course_id);course.target='_blank';course.rel='noopener noreferrer';
 const d=mk('details',root);d.open=true;mk('summary',d,'','Prompt complet et référence');mk('p',d,'detail-meta','Code hors-image : '+promptCode(x));mk('pre',d,'',x.prompt||'Prompt non disponible');const row=mk('div',d,'row');button(row,'Copier le prompt + code',function(){copy(fullPrompt(x),this)},'quiet');button(row,'Copier le code',function(){copy(promptCode(x),this)},'quiet');
 if(!x.editable)mk('p',root,'hint','Ce visuel provient d’un catalogue provisoire; import direct non disponible avant création de la couche Kristal.');
 uploadSection(root,x);frameSection(root,x);
}
async function reload(keep=true){const existing=keep?ST.selected:null;const res=await fetch('/api/images-album.json',{credentials:'same-origin',cache:'no-store'});if(!res.ok)throw Error('Inventaire indisponible ('+res.status+')');const data=await res.json();ST.items=data.items||[];
 $('totalSlots').textContent=data.slot_count;$('presentCount').textContent=data.counts.presente||0;$('missingCount').textContent=data.counts.manquante||0;$('pendingCount').textContent=(data.counts.a_synchroniser||0)+(data.counts.source_absente||0);
 $('orphanNote').textContent=data.orphan_count?data.orphan_count+' fichiers d’images non déclarés détectés. Aucun fichier n’a été supprimé.':'';
 updateFilters();ST.selected=ST.items.some(x=>x.key===existing)?existing:null;filter();drawDetail();}
function csv(){const rows=[['année','matière','cours','id','emplacement','statut','fichier(s)','code']];ST.filtered.forEach(x=>rows.push([x.year||'',x.subject,x.course_title,x.course_id,x.slot,x.status,x.files.join('; '),promptCode(x)]));const cell=v=>{let value=String(v??'');if(/^[=+@-]/.test(value))value="'"+value;return '"'+value.replaceAll('"','""')+'"'};const blob=new Blob(['\ufeff'+rows.map(r=>r.map(cell).join(';')).join('\r\n')],{type:'text/csv;charset=utf-8'});const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download='Ekole-inventaire-images.csv';a.click();setTimeout(()=>URL.revokeObjectURL(url),1500)}
async function boot(){try{const [t,config]=await Promise.all([fetch('/api/image-editor-config.json',{credentials:'same-origin'}),fetch('/api/cadres-images.json',{credentials:'same-origin'})]);if(!t.ok||!config.ok)throw Error('Session Enseignant manquante');ST.token=(await t.json()).csrf;const c=await config.json();ST.config={style:FRAME[c.style]?c.style:'epure',size:['compact','normal','grand'].includes(c.size)?c.size:'normal',borderColor:/^#[0-9a-f]{6}$/i.test(c.borderColor||'')?c.borderColor:'#1e6864'};
 await reload(false);for(const id of ['search','year','subject','course','slot','state','view'])$(id).addEventListener(id==='search'?'input':'change',()=>{ST.page=0;filter()});
 $('rescan').addEventListener('click',async()=>{try{await reload(true);status('Inventaire actualisé.','good')}catch(e){status(e.message,'error')}});
 $('sync').addEventListener('click',async()=>{const btn=$('sync');btn.disabled=true;status('Synchronisation des illustrations en cours…');try{const r=await fetch('/api/images-album/recompiler',{method:'POST',credentials:'same-origin',headers:{'X-Ekole-CSRF':ST.token}});if(!r.ok)throw Error((await r.text()).slice(0,250));const value=await r.json();await reload(true);status('✓ Synchronisation terminée : '+value.image_count+' illustrations publiées.','good')}catch(e){status('Échec de synchronisation : '+e.message,'error')}finally{btn.disabled=false}});
 $('clearFilters').addEventListener('click',()=>{for(const id of ['search','year','subject','course','slot','state'])$(id).value='';ST.page=0;filter()});$('csv').addEventListener('click',csv);
 $('previous').addEventListener('click',()=>{ST.page=Math.max(0,ST.page-1);drawCards()});$('next').addEventListener('click',()=>{ST.page++;drawCards()});
 }catch(e){status('Impossible d’ouvrir l’album : '+e.message,'error');$('resultCount').textContent='Erreur de chargement';}}
boot();
})();
