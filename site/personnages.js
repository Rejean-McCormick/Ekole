'use strict';
// Ressources facultatives du paquet; repli immédiat si image absente ou illisible.
(()=>{
 let catalogue={compagnons:[],anciens_choix:{},assets:[]};
 const assets=new Map();
 function configure(data){
  assets.clear();
  catalogue=data?.format==='ekole.personnages/1'?data:{compagnons:[],anciens_choix:{},assets:[]};
  for(const a of catalogue.assets||[])assets.set(a.id,a);
 }
 function show(host,id,fallback,large=false){
  const box=document.createElement('span');box.className='personnage-portrait'+(large?' personnage-large':'');
  const initial=document.createElement('span');initial.className='compagnon-sigle';initial.textContent=fallback;initial.setAttribute('aria-hidden','true');box.append(initial);
  const asset=assets.get(id);
  if(asset?.disponible&&asset.url==='/api/personnages/image/'+asset.id){
   const img=document.createElement('img');img.alt=asset.alt||'';img.hidden=true;img.decoding='async';
   img.addEventListener('load',()=>{initial.hidden=true;img.hidden=false;});
   img.addEventListener('error',()=>{img.remove();initial.hidden=false;});
   img.src=asset.url;box.append(img);
  }
  host.append(box);return box;
 }
 function companion(host,personnage,year,pose='debout',large=false){
  const posed=assets.get(`compagnon-${personnage.id}-pose-${pose}`);
  const id=pose!=='debout'&&posed?.disponible?posed.id:`compagnon-${personnage.id}-annee-${String(year).padStart(2,'0')}`;
  const box=show(host,id,personnage.sigle,large);box.dataset.compagnonPortrait='';return box;
 }
 function role(host,id,name,large=false){return show(host,'role-'+id,Array.from(name||'?')[0],large);}
 window.EkolePersonnages={configure,companion,role,get catalogue(){return catalogue;}};
})();
