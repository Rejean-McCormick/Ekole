'use strict';
(()=>{
 const ALLOWED=new Map([
  ['epure','Épuré'],['carte','Carte douce'],['galerie','Galerie'],
  ['carnet','Carnet'],['bandeau','Bandeau'],['sombre','Focus sombre'],['bordure','Bordure colorée']]);
 const SIZES=new Set(['compact','normal','grand']);
 const DEFAULT_COLOR='#1e6864';
 const validHex=x=>/^#[0-9a-f]{6}$/i.test(x||'');
 const picker=document.querySelector('#borderColorPicker');
 const hex=document.querySelector('#borderColorHex');
 const colorChoice=document.querySelector('#colorChoice');
 const frame=document.querySelector('#liveFrame');
 const image=document.querySelector('#liveImage');
 const demo=document.querySelector('#demoArt');
 const status=document.querySelector('#status');
 const save=document.querySelector('#saveButton');
 const tokenUrl='/api/image-editor-config.json';
 const configUrl='/api/cadres-images.json';
 let csrf='';let saved=null;
 const checked=name=>document.querySelector('input[name="'+name+'"]:checked')?.value;
 const data=()=>({format:'ekole.image-frames/1.0',style:checked('frameStyle')||'epure',size:checked('frameSize')||'normal',borderColor:hex.value.trim().toLowerCase()});
 function select(name,value){const input=document.querySelector('input[name="'+name+'"][value="'+value+'"]');if(input)input.checked=true;}
 function report(message,state='info'){status.textContent=message;status.dataset.status=state;}
 function setColor(color){const normalized=validHex(color)?color.toLowerCase():DEFAULT_COLOR;picker.value=normalized;hex.value=normalized;hex.setAttribute('aria-invalid','false');}
 function render(){const cfg=data();const colorValid=validHex(cfg.borderColor);
  document.documentElement.dataset.imageFrame=cfg.style;document.documentElement.dataset.imageSize=cfg.size;
  if(colorValid)document.documentElement.style.setProperty('--ekole-image-border-color',cfg.borderColor);
  colorChoice.hidden=cfg.style!=='bordure';
  hex.setAttribute('aria-invalid',String(!colorValid));
  document.querySelector('#styleName').textContent=ALLOWED.get(cfg.style)||'Épuré';
  if(!colorValid){save.disabled=true;report('Code couleur invalide. Utilise # suivi de six chiffres ou lettres hexadécimaux.','error');return;}
  if(saved){const dirty=cfg.style!==saved.style||cfg.size!==saved.size||cfg.borderColor!==saved.borderColor;
   save.disabled=!dirty;
   if(dirty)report('Aperçu non enregistré. Clique sur « Enregistrer » pour appliquer ce style aux élèves.');
   else report('Configuration enregistrée.','saved');}
 }
 document.querySelectorAll('input[name="frameStyle"],input[name="frameSize"]').forEach(x=>x.addEventListener('change',render));
 picker.addEventListener('input',()=>{hex.value=picker.value.toLowerCase();render();});
 hex.addEventListener('input',()=>{const color=hex.value.trim();if(validHex(color))picker.value=color.toLowerCase();render();});
 document.querySelector('#colorResetButton').addEventListener('click',()=>{setColor(DEFAULT_COLOR);render();});
 document.querySelector('#resetButton').addEventListener('click',()=>{select('frameStyle','epure');select('frameSize','normal');setColor(DEFAULT_COLOR);render();});
 save.addEventListener('click',async()=>{
  if(!csrf){report('La session Enseignant est indisponible. Relance Ekole Enseignant.','error');return;}
  const payload=data();if(!ALLOWED.has(payload.style)||!SIZES.has(payload.size)||!validHex(payload.borderColor))return;
  save.disabled=true;report('Enregistrement en cours…');
  try{
   const response=await fetch(configUrl,{method:'POST',credentials:'same-origin',cache:'no-store',headers:{'Content-Type':'application/json','X-Ekole-CSRF':csrf},body:JSON.stringify(payload)});
   if(!response.ok)throw new Error('HTTP '+response.status+' · '+(await response.text()));
   saved=await response.json();report('✓ Enregistré. Le cadre s’appliquera dans Ekole Élève (immédiatement au retour sur l’onglet).','saved');
  }catch(error){report('Impossible d’enregistrer : '+error.message,'error');}
  finally{const current=data();save.disabled=Boolean(saved)&&saved.style===current.style&&saved.size===current.size&&saved.borderColor===current.borderColor;}
 });
 image.addEventListener('load',()=>{image.hidden=false;demo.hidden=true;});
 image.addEventListener('error',()=>{image.hidden=true;demo.hidden=false;});
 // Optional real local image. A self-contained schematic remains if it does not exist.
 image.src='/api/kristal-image/qc-pri-ma-012/concept.webp';
 async function begin(){
  try{
   const [tokenResponse,configResponse]=await Promise.all([
    fetch(tokenUrl,{cache:'no-store',credentials:'same-origin'}),
    fetch(configUrl,{cache:'no-store',credentials:'same-origin'})]);
   if(!tokenResponse.ok||!configResponse.ok)throw new Error('Session ou configuration indisponible');
   csrf=(await tokenResponse.json()).csrf;
   const conf=await configResponse.json();saved={style:ALLOWED.has(conf.style)?conf.style:'epure',size:SIZES.has(conf.size)?conf.size:'normal',borderColor:validHex(conf.borderColor)?conf.borderColor.toLowerCase():DEFAULT_COLOR};
   select('frameStyle',saved.style);select('frameSize',saved.size);setColor(saved.borderColor);render();
  }catch(error){save.disabled=true;report('Impossible de charger le réglage : '+error.message,'error');}
 }
 begin();
})();
