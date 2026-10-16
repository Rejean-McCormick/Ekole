/* Ekole Élève v12 : interactions déterministes et non certifiantes, commandes accessibles au clavier. */
(()=>{'use strict';
const E=window.EkoleMondesV12,root=document.querySelector('#contenu');if(!E||!root)return;
const el=(tag,text,cls)=>{const x=document.createElement(tag);if(text!==undefined)x.textContent=String(text);if(cls)x.className=cls;return x;};
const put=(p,tag,text,cls)=>{const x=el(tag,text,cls);p.append(x);return x;};
const button=(p,label,fn,cl='btn')=>{const b=put(p,'button',label,cl);b.type='button';b.onclick=fn;return b;};
const box=(p,title)=>{const c=put(p,'section',undefined,'card');put(c,'h2',title);return c;};
let catalog=[],spec=null,state=null,trials=0,shown=0;
const link=(p,txt,href)=>{const a=put(p,'a',txt,'btn');a.href=href;return a;};
function visual(p,s){const fig=put(p,'figure');put(fig,'strong','Illustration à venir');const description=put(fig,'p',s.image_alt||s.alt_visuel||s.description_visuelle||'Illustration associée à « '+s.title+' ».');if(s.image_url){const image=put(fig,'img');image.alt=s.image_alt||'Illustration de la situation';image.hidden=true;image.onload=()=>{image.hidden=false;description.hidden=true;};image.onerror=()=>{image.hidden=true;description.hidden=false;};image.src=s.image_url;}}
function section(p,heading,info){const x=put(p,'div',undefined,'stage');put(x,'h3',heading);if(info)put(x,'p',info);return x;}
function renderInteraction(p){const s=spec,pr=s.parameters;
 if(s.type==='representations')for(const [key,label] of [['surface','La surface'],['bande','La bande'],['collection','Les groupes d’objets']]){const f=section(p,label,'Choisis les parts du tout.');const cells=put(f,'div',undefined,'unit-grid');for(let i=0;i<pr.parts;i++){const symbol=key==='collection'?('●'.repeat(pr.group_size)):key==='bande'?'▰':'■';const b=button(cells,symbol,()=>change({action:'toggle',part:key,index:i}),'unit');b.setAttribute('aria-pressed',String(state[key].includes(i)));b.setAttribute('aria-label',`${label} : partie ${i+1} sur ${pr.parts}${state[key].includes(i)?' choisie':''}`);}}
 if(s.type==='repartition'){
  const source=section(p,'Jetons disponibles','Choisis un jeton, puis une boîte.');const sourceRow=put(source,'div',undefined,'pills');pr.total>0&&state.bins.forEach((v,i)=>{if(v===-1){const b=button(sourceRow,'● '+(i+1),()=>change({action:'select',index:i}));b.setAttribute('aria-pressed',String(state.active===i));}});
  for(let bin=0;bin<pr.bins;bin++){const x=section(p,'Boîte '+(bin+1),'');const line=put(x,'div',undefined,'basket');state.bins.forEach((n,i)=>{if(n===bin)button(line,'● '+(i+1)+' ↩',()=>change({action:'return',index:i}));});button(x,'Déposer le jeton choisi ici',()=>change({action:'place',bin}), 'btn primary');}
 }
 if(s.type==='causalite'){
  const f=section(p,'Ordre des événements','Utilise les flèches pour organiser le récit.');state.order.forEach((id,i)=>{const card=pr.events.find(e=>e.id===id),r=put(f,'div',undefined,'row-item');put(r,'strong',(i+1)+'. '+card.text);button(r,'↑',()=>change({action:'move',index:i,direction:-1})).disabled=i===0;button(r,'↓',()=>change({action:'move',index:i,direction:1})).disabled=i===state.order.length-1;});
  const g=section(p,'Cause ou simple coïncidence ?','Les phrases suivantes expriment-elles une relation justifiée ?');pr.links.forEach((l,i)=>{const r=put(g,'div',undefined,'row-item');put(r,'strong',l.statement);for(const [v,t] of [[true,'Oui'],[false,'Non']]){const b=button(r,t,()=>change({action:'link',index:i,value:v}));b.setAttribute('aria-pressed',String(state.links[i]===v));}});
 }
 if(s.type==='preuves'){const f=section(p,'Observation ou interprétation ?','Une observation est un constat. Une interprétation propose une explication.');for(const row of pr.statements){const r=put(f,'div',undefined,'row-item');put(r,'strong',row.text);for(const [kind,text] of [['observation','J’observe'],['interpretation','Je suppose']]){const b=button(r,text,()=>change({action:'classify',id:row.id,kind}));b.setAttribute('aria-pressed',String(state.classifications[row.id]===kind));}}}
 if(s.type==='expression'){const f=section(p,'Prépare ta scène','Sélectionne les moyens que tu vas utiliser. Tu les présenteras devant une personne.');for(const g of pr.gestures){const b=button(f,g,()=>change({action:'toggle',gesture:g}),'choice');b.setAttribute('aria-pressed',String(state.selected.includes(g)));}put(f,'p','Aucun score automatique : une personne observe l’expression, l’intention et les deux moyens employés.','teacher');}
}
function render(){root.replaceChildren();link(root,'← Tous les micro-mondes','./');put(root,'p','Entraînement · Pas de note scolaire','eyebrow');put(root,'h1',spec.title);put(root,'p',spec.instruction);visual(root,spec);const area=box(root,'À toi de manipuler');renderInteraction(area);const c=put(root,'div',undefined,'actions');button(c,'Vérifier mon essai',()=>{trials++;const result=E.evaluate(spec,state);shown++;showFeedback(result);},'btn primary');button(c,'Un indice',()=>showHint());button(c,'Recommencer',()=>{state=E.initial(spec);trials=0;shown=0;render();});put(root,'p','Chaque réussite vérifie seulement cette construction. Explique tes choix à une personne pour montrer ce que tu comprends.','muted');}
function change(a){
 const buttons=[...root.querySelectorAll('button')];
 const focusIndex=buttons.indexOf(document.activeElement);
 state=E.apply(spec,state,a);render();
 if(focusIndex>=0){const next=root.querySelectorAll('button');
  if(next.length)next[Math.min(focusIndex,next.length-1)].focus({preventScroll:true});}
}
function showHint(){const status=put(root,'div',undefined,'status');status.setAttribute('role','status');const hints={representations:['Commence par compter toutes les parts égales de chaque support.','Combien de parts choisis-tu parmi toutes les parts ?'],repartition:['Choisis un jeton, puis place-le dans une boîte.','Compare les boîtes et examine si un reste est normal.'],causalite:['Cherche l’événement qui doit arriver avant les autres.','Un événement vient-il vraiment provoquer l’autre ?'],preuves:['Le texte décrit-il un fait visible ou propose-t-il une explication ?','Les mots « parce que » indiquent souvent une interprétation.'],expression:['Choisis deux moyens différents : voix, corps ou espace.','Demande à une personne si ton intention est perceptible.']};put(status,'p',hints[spec.type][Math.min(shown++,1)]);}
function showFeedback(result){
 const s=put(root,'section',undefined,'status');s.setAttribute('role','status');
 put(s,'h2',result.correct?'Construction vérifiée':'Regarde ce que tu peux ajuster');
 put(s,'p',result.diagnostic);
 if(result.criteria.length){const ul=put(s,'ul',undefined,'criteria');
  for(const c of result.criteria)put(ul,'li',(c.ok?'✓ ':'○ ')+c.id.replaceAll('_',' ')+' — '+c.detail);
 }
 put(s,'p','Résultat formatif, jamais une preuve de maîtrise.');s.scrollIntoView({block:'nearest',behavior:'auto'});
}
async function start(){try{const r=await fetch('data/catalogue.json',{cache:'no-store'});if(!r.ok)throw Error('Catalogue indisponible');const data=await r.json();catalog=data.items;const query=new URLSearchParams(location.search);const id=query.get('id');const course=query.get('cours');if(id){spec=catalog.find(x=>x.id===id);if(!spec)throw Error('Micro-monde inconnu');E.validateSpec(spec);state=E.initial(spec);render();}else{root.replaceChildren();put(root,'p','Des mondes pour essayer','eyebrow');put(root,'h1','Mes petits mondes');put(root,'p','Choisis une activité et construis une réponse avec les objets proposés. Les exercices ne donnent aucune note scolaire.');const list=put(root,'div',undefined,'catalogue');for(const item of catalog.filter(x=>!course||x.kristal_id===course)){const a=link(list,item.title,'?id='+encodeURIComponent(item.id));put(a,'p',item.instruction,'muted');}put(root,'p','Les activités sont des prototypes pédagogiques à faire réviser avec des enseignants.','muted');}}catch(e){root.replaceChildren();put(root,'h1','Activité indisponible');put(root,'p',e.message);}}start();
})();
