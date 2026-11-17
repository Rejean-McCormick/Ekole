'use strict';
// Ressources facultatives du paquet; repli immédiat si image absente ou illisible.
(()=>{
 let catalogue={compagnons:[],anciens_choix:{},assets:[]};
 const assets=new Map();
 function configure(data){
  assets.clear();
  catalogue=['ekole.personnages/1','ekole.personnages/2','ekole.personnages/3','ekole.personnages/4'].includes(data?.format)?data:{compagnons:[],anciens_choix:{},assets:[]};
  for(const a of catalogue.assets||[])assets.set(a.id,a);
 }
 function ready(a){return Boolean(a?.disponible&&a.url==='/api/personnages/image/'+a.id);}
 function show(host,id,fallback,large=false,decorative=false){
  const box=document.createElement('span');box.className='personnage-portrait'+(large?' personnage-large':'');
  const initial=document.createElement('span');initial.className='compagnon-sigle';initial.textContent=fallback;initial.setAttribute('aria-hidden','true');box.append(initial);
  const asset=assets.get(id);
  if(ready(asset)){
   const img=document.createElement('img');img.alt=decorative?'':asset.alt||'';img.hidden=true;img.decoding='async';
   img.addEventListener('load',()=>{initial.hidden=true;img.hidden=false;});
   img.addEventListener('error',()=>{img.remove();initial.hidden=false;});
   img.src=asset.url;box.append(img);
  }
  host.append(box);return box;
 }
 function companion(host,personnage,year,pose='neutre',large=false){
  let id;
  if(['ekole.personnages/2','ekole.personnages/3','ekole.personnages/4'].includes(catalogue.format)){
   // Une identité = un rôle = un compagnon. Le portrait neutre est partagé.
   const freeId=`libre-${personnage.role_id||personnage.id.replace(/-fille$/, '')}-${pose}`;
   if(ready(assets.get(freeId))){const box=show(host,freeId,personnage.sigle,large);box.dataset.compagnonPortrait='';return box;}
   const variant=`compagnon-${personnage.id}-pose-${pose}`;
   id=pose!=='neutre'&&ready(assets.get(variant))?variant:`role-${personnage.id}`;
  }else{
   const posed=assets.get(`compagnon-${personnage.id}-pose-${pose}`);
   id=pose!=='debout'&&posed?.disponible?posed.id:`compagnon-${personnage.id}-annee-${String(year).padStart(2,'0')}`;
   const roleId=personnage.role_id&&'role-'+personnage.role_id;
   if(!assets.get(id)?.disponible&&assets.get(roleId)?.disponible)id=roleId;
  }
  const box=show(host,id,personnage.sigle,large);box.dataset.compagnonPortrait='';return box;
 }
 function role(host,id,name,large=false){
  if(['ekole.personnages/3','ekole.personnages/4'].includes(catalogue.format)){
   const freeId=`libre-${id}-neutre`;
   if(ready(assets.get(freeId)))return show(host,freeId,Array.from(name||'?')[0],large,host.matches('a,button'));
   const duo=document.createElement('span');duo.className='personnage-duo';
   show(duo,'role-'+id,Array.from(name||'?')[0],large,true);
   show(duo,'role-'+id+'-fille',Array.from(name||'?')[0],large,true);
   host.append(duo);return duo;
  }
  return show(host,'role-'+id,Array.from(name||'?')[0],large,host.matches('a,button'));
 }
 window.EkolePersonnages={configure,companion,role,get catalogue(){return catalogue;}};
})();
