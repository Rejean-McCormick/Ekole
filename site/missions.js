'use strict';
/* Module élève intégré à Ekole. Sources : projection de rôles Kompose et
   exercices déterministes Kontexte. Aucun indice privé, état Orgo ni donnée enfant. */
(()=>{
  const el=(name,cls,text)=>{const x=document.createElement(name);if(cls)x.className=cls;if(text!==undefined)x.textContent=String(text);return x;};
  const append=(parent,name,cls,text)=>{const x=el(name,cls,text);parent.append(x);return x;};
  const catalogueUrl='/api/demo-missions/catalogue.json';
  const roleUrl=(m,r)=>'/api/demo-missions/role.json?mission='+encodeURIComponent(m)+'&role='+encodeURIComponent(r);
  const request=async(path,options)=>{const r=await fetch(path,{cache:'no-store',...options});const data=await r.json();if(!r.ok)throw Error(data.error||'Ressource indisponible');return data;};
  const state={list:null,mission:null,role:null,done:new Set(),drafts:new Map()};
  let root;
  const jump=()=>window.scrollTo({top:0,behavior:'smooth'});
  function tag(host,text){append(host,'span','mission-tag',text);}
  function notice(host){append(host,'p','mission-warning','Démonstration locale de 3e année · Pas encore une mission de classe publiée. Aucun compte, aucune note ni véritable équipe.');}
  function link(host,label,href){const x=append(host,'a','button-link',label);x.href=href;return x;}
  function btn(host,label,callback,cls='mission-btn'){const x=append(host,'button',cls,label);x.type='button';x.addEventListener('click',callback);return x;}
  function error(e){root.replaceChildren();append(root,'h1','page-heading','Missions indisponibles');append(root,'p','warning',e.message);link(root,'Retour au parcours','/eleve/?parcours=annee-3');}
  function reset(){state.mission=null;state.role=null;state.done.clear();state.drafts.clear();list();}
  function list(){root.replaceChildren();append(root,'p','eyebrow','À toi de jouer · 3e année');append(root,'h1','page-heading','Les missions d’Ekole');append(root,'p','intro','Choisis une histoire, puis un rôle. Tu vas découvrir de vraies consignes de Kontexte, préparées en aperçu par Kompose.');notice(root);
   const grid=append(root,'div','mission-grid');
   for(const m of state.list.missions){const box=append(grid,'article','mission-tile');tag(box,m.nombre_etapes+' étapes');append(box,'h2','',m.titre);append(box,'p','',m.histoire);append(box,'p','mission-muted',m.roles.map(r=>r.name).join(' · '));btn(box,'Découvrir cette mission',()=>chooseMission(m.id),'mission-btn mission-primary');}
   link(root,'Explorer mes cours de 3e','/eleve/?parcours=annee-3');
  }
  async function chooseMission(id){state.mission=state.list.missions.find(m=>m.id===id);state.role=null;state.done.clear();state.drafts.clear();drawMission();jump();}
  function drawMission(){const m=state.mission;root.replaceChildren();btn(root,'← Toutes les missions',reset,'mission-back');append(root,'p','eyebrow','Mission interactive · 3e année');append(root,'h1','page-heading',m.titre);append(root,'p','intro',m.histoire);notice(root);const counter=append(root,'p','mission-progress','Étapes explorées : '+state.done.size+' / '+m.nombre_etapes+' (sans validation scolaire)');counter.id='mission-tries';if(state.done.size===m.nombre_etapes)append(root,'p','mission-celebrate','Bravo ! Tu as essayé toutes les étapes de cette histoire.');append(root,'h2','section-title','Quel rôle veux-tu essayer ?');const roles=append(root,'div','mission-role-row');
   for(const r of m.roles){const b=btn(roles,r.name,async()=>{
     try{state.role=await request(roleUrl(m.id,r.id));drawMission();jump();}catch(e){error(e);}
   },'mission-btn '+(state.role?.role_id===r.id?'mission-primary':''));b.setAttribute('aria-pressed',String(state.role?.role_id===r.id));const portrait=window.EkolePersonnages.role(b,r.id,r.name);b.prepend(portrait);}
   if(state.role)drawRole(root,state.role);
   else append(root,'p','mission-muted','Tu peux essayer plusieurs rôles, un à la fois. Dans une vraie classe, les rôles seraient distribués par une personne responsable.');
  }
  function drawRole(host,r){const section=append(host,'section','mission-play');window.EkolePersonnages.role(section,r.role_id,r.nom,true);append(section,'h2','',`À toi, ${r.nom} !`);append(section,'p','',r.introduction);
   const actions=append(section,'div','mission-actions');append(actions,'strong','', 'Ce rôle peut :');for(const a of r.actions)tag(actions,a);
   append(section,'h3','','Tes défis');for(const step of r.etapes){const block=append(section,'div','mission-step');append(block,'h4','',step.instruction);if(step.depends_on?.length)append(block,'p','mission-muted','Dans une équipe, cette étape dépendrait aussi d’autres rôles.');
    const key=state.mission.id+':'+r.role_id+':'+step.id;
    const choice=append(block,'div','mission-choice');append(choice,'p','mission-muted','Choisis une action pour commencer :');const choiceFeedback=append(choice,'p','mission-muted');
    for(const action of r.actions.slice(0,3))btn(choice,'Je veux '+action,()=>{choiceFeedback.textContent='Ton idée : '+action+'. Comment utiliser cette action pour le défi ?';},'mission-btn mission-action');
    const field=append(block,'textarea','mission-entry');field.rows=2;field.maxLength=500;field.placeholder='Raconte ton idée, fais un calcul ou décris ce que tu ferais…';field.setAttribute('aria-label','Mon idée pour : '+step.instruction);field.value=state.drafts.get(key)||'';
    field.addEventListener('input',()=>state.drafts.set(key,field.value));
    const feedback=append(block,'p','mission-feedback');feedback.setAttribute('role','status');if(state.done.has(key))feedback.textContent='Étape déjà explorée (sans validation).';
    btn(block,'J’ai essayé !',()=>{if(!field.value.trim()){feedback.textContent='Écris ou raconte d’abord ton idée. Rien n’est noté.';return;}state.done.add(key);feedback.textContent='Bravo d’avoir essayé ! Montre ton idée à un adulte pour en discuter.';const counter=document.getElementById('mission-tries');if(counter)counter.textContent='Étapes explorées : '+state.done.size+' / '+state.mission.nombre_etapes+' (sans validation scolaire)';if(state.done.size===state.mission.nombre_etapes)feedback.textContent+=' Tu as essayé toutes les étapes de cette histoire !';});}
   if(r.exercice)drawExercise(section,r);
   const more=append(section,'p','mission-muted','Ces consignes proviennent de Kontexte et sont filtrées par Kompose pour l’aperçu de ce rôle. Une réponse écrite ici reste dans cette page, sans enregistrement.');
   if(state.mission.id==='boulangerie')link(section,'Manipuler les jetons dans ma vraie leçon Ekole','/eleve/?cours=qc-pri-ma-008&retour=annee-3&vue=pratique');
  }
  function drawExercise(host,r){const box=append(host,'section','mission-exercise');append(box,'h3','','Petit défi de calcul');append(box,'p','',r.exercice.question);
   const row=append(box,'div','mission-answer');const input=append(row,'input');input.inputMode='decimal';input.placeholder='Ta réponse';input.maxLength=80;input.setAttribute('aria-label','Réponse au défi de calcul');append(row,'span','',r.exercice.unite);
   const status=append(box,'p','mission-feedback');status.setAttribute('role','status');
   btn(box,'Vérifier mon calcul',async()=>{if(!input.value.trim()){status.textContent='Entre un nombre pour commencer.';return;}
    try{const r2=await request('/api/demo-missions/check',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({mission_id:state.mission.id,exercise_id:r.exercice.id,answer:input.value})});status.textContent=r2.correct?'Bravo, ton calcul est juste ! Essaie aussi d’expliquer comment tu as trouvé.':'Pas tout à fait. Tu peux réessayer en dessinant ou en faisant des groupes.';}catch(e){status.textContent='Vérification impossible : '+e.message;}},'mission-btn mission-primary');
   append(box,'small','mission-muted','Vérification du calcul par Kontexte · Aucun résultat scolaire sauvegardé.');
  }
  async function render(host){root=host;root.replaceChildren();append(root,'p','intro','Chargement des missions…');try{state.list=await request(catalogueUrl);if(state.list.format!=='ekole.missions-demo/1')throw Error('Catalogue de mission incompatible.');list();}catch(e){error(e);}}
  window.EkoleMissions={render};
})();
