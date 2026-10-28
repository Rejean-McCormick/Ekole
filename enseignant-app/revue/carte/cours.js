'use strict';
// Module autonome B7, lit le pack Light au SHA-256 et la liste d'attributions candidate.
// Aucune requête à l'API expert Ekole, aucune collecte de données élève.
const $ = id => document.getElementById(id);
const METADATA_SHA256='c3f232d381fbbe44d108aa3d3896a5a8576c766cdb9e1aee844f488b40cf5c17'; // épinglé lors de la construction, pas depuis le site
const label = (text)=>document.createTextNode(String(text));
const state={bundle:null,meta:null,byId:new Map(),last:[],focus:null};
function error(text){$('focus-title').textContent='Carte indisponible';$('focus-detail').textContent=text;$('map').hidden=true;}
async function load(){
 const catalog=await (await fetch('./data/catalog.json',{cache:'no-store'})).json();
 if(catalog.format!=='konstellation.light-catalog/1.0'||catalog.entries.length!==1)throw Error('Catalogue Light inattendu');
 const entry=catalog.entries[0];
 if(entry.mode!=='semantic_preview'||!/^data\/pack-[0-9a-f]{64}\.json$/.test(entry.path)||!/^sha256:[0-9a-f]{64}$/.test(entry.sha256))throw Error('Entrée non conforme');
 const response=await fetch('./'+entry.path,{cache:'no-store'});if(!response.ok)throw Error('Graphe indisponible');
 const buffer=await response.arrayBuffer();if(buffer.byteLength!==entry.bytes||buffer.byteLength>8*1024*1024)throw Error('Taille du bundle invalide');
 if(!crypto.subtle)throw Error('Un navigateur sur localhost ou HTTPS est nécessaire');
 const digest=[...new Uint8Array(await crypto.subtle.digest('SHA-256',buffer))].map(n=>n.toString(16).padStart(2,'0')).join('');
 if('sha256:'+digest!==entry.sha256)throw Error('Intégrité de la carte non vérifiée');
 const bundle=JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(buffer));
 if(bundle.format!=='konstellation.light-navigation/1.0'||bundle.semantic_authority!==false||bundle.view_kind!=='derived-semantic-preview'||!Array.isArray(bundle.nodes)||!Array.isArray(bundle.edges))throw Error('Bundle non approuvé comme prévisualisation');
 const metares=await fetch('./data/ekole-grade.json',{cache:'no-store'});if(!metares.ok)throw Error('Attributions indisponibles');
 const metabuf=await metares.arrayBuffer();if(metabuf.byteLength>350000)throw Error('Attributions trop volumineuses');
 const metadigest=[...new Uint8Array(await crypto.subtle.digest('SHA-256',metabuf))].map(x=>x.toString(16).padStart(2,'0')).join('');
 if(metadigest!==METADATA_SHA256)throw Error('Attributions modifiées après construction');
 const meta=JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(metabuf));
 if(meta.format!=='ekole.b7-graph/1'||!Array.isArray(meta['nœuds'])||!Array.isArray(meta.relations))throw Error('Métadonnées pédagogiques invalides');
 const byId=new Map(bundle.nodes.map(x=>[x.id,x]));
 if(byId.size!==bundle.nodes.length)throw Error('Nœuds répétés');
 const permitted=new Set(['requires','recommends_before','reinforces']);
 const metaKeys=new Set(meta.relations.map(e=>e.from+'|'+e.to+'|'+e.type));
 if(bundle.edges.length!==meta.relations.length||metaKeys.size!==bundle.edges.length)throw Error('Relations sources non concordantes');
 for(const edge of bundle.edges){if(!byId.has(edge.from)||!byId.has(edge.to)||!permitted.has(edge.relation)||!metaKeys.has(edge.from+'|'+edge.to+'|'+edge.relation))throw Error('Relation inconnue ou non déclarée');}
 // Les sources de curation ne contiennent que titres publics et relations internes; pas de savoir métier projeté par inférence.
 return {bundle,meta,byId};
}
const relationKey = e=>e.from+'|'+e.to+'|'+e.relation;
function addCards(target,items){
 target.replaceChildren();
 if(!items.length){const p=document.createElement('p');p.className='empty';p.textContent='Aucun lien de ce type n’est documenté ici.';target.append(p);return;}
 for(const item of items){
  const button=document.createElement('button');button.type='button';button.className='notion';
  const title=document.createElement('strong');title.textContent=state.byId.get(item.id).label;
  const context=document.createElement('small');context.textContent=item.caption;
  button.append(title,context);button.addEventListener('click',()=>selectCourse(item.id));target.append(button);
 }
}
function createEvidence(edges){const parent=$('evidence');parent.replaceChildren();
 const p=document.createElement('p');p.textContent='Chaque relation provient du graphe pédagogique interne « qc.learning-graph/1.2 » ; les décisions ne constituent pas une validation ministérielle. La direction est préservée : A requires B signifie que B est une base déclarée pour A.';parent.append(p);
 const list=document.createElement('ul');for(const e of edges){const line=document.createElement('li');
  const src=state.byId.get(e.from).label,dst=state.byId.get(e.to).label;
  const match=state.meta.relations.find(x=>x.from===e.from&&x.to===e.to&&x.type===e.relation);
  line.textContent=`${src} — ${e.relation} → ${dst} · ${match?.provenance||'provenance absente'}`;list.append(line);
 }parent.append(list);
}
function selectCourse(id,{first=false}={}){
 if(!state.byId.has(id))return;
 if(!first && state.focus && state.focus!==id){state.last.push(state.focus);if(state.last.length>30)state.last.shift();}
 state.focus=id;const n=state.byId.get(id);$('focus-title').textContent=n.label;$('center-title').textContent=n.label;
 const candidates=state.meta.cours_3e_candidats.includes(id);
 $('focus-detail').textContent=candidates?'Cette notion figure dans la proposition de parcours de 3e année.':'Cette notion est reliée à la 3e année, mais son classement n’est pas confirmé ici.';
 const edges=state.bundle.edges.filter(e=>e.from===id||e.to===id);
 const before=[],after=[],transfer=[];
 for(const e of edges){const other=e.from===id?e.to:e.from;
  if(e.relation==='reinforces'){transfer.push({id:other,caption:'Un lien de transfert est déclaré.'});continue;}
  if(e.from===id){before.push({id:other,caption:e.relation==='requires'?'Une base déclarée pour cette leçon.':'Un ordre conseillé, pas une obligation.'});}
  else{after.push({id:other,caption:e.relation==='requires'?'Cette notion s’appuie sur celle que je regarde.':'Une notion conseillée plus tard.'});}
 }
 // Même nœud peut figurer dans plusieurs catégories si les relations sont distinctes : ne pas en déduire de maîtrise.
 const sort=(a,b)=>state.byId.get(a.id).label.localeCompare(state.byId.get(b.id).label,'fr');
 addCards($('before-list'),before.sort(sort));addCards($('after-list'),after.sort(sort));addCards($('transfer-list'),transfer.sort(sort));
 $('back').disabled=state.last.length===0;createEvidence(edges);
 $('pick').value=id;
 const params=new URLSearchParams(location.search);params.set('cours',id);
 history.replaceState(null,'',location.pathname+'?'+params.toString());
 $('expert').href='./?lens=constellation&focus='+encodeURIComponent(id)+'&n=8';
}
function returnLink(){const input=new URLSearchParams(location.search).get('retour');if(!input)return;
 try{const u=new URL(input);
 // Retours exclusivement vers un Ekole local : aucune redirection ouverte vers un site tiers.
 if(!['127.0.0.1','localhost'].includes(u.hostname)|| !['http:','https:'].includes(u.protocol)||!u.pathname.startsWith('/eleve/'))return;
 const link=$('return');link.href=u.href;link.hidden=false;
 }catch(_){}
}
async function main(){try{
 const loaded=await load();Object.assign(state,loaded);
 $('disclaimer').textContent=state.meta.grade_source+' · '+state.meta.cours_3e_candidats.length+' cours classés à titre de proposition. Pas de résultat élève.';
 const select=$('pick');select.replaceChildren();
 for(const n of [...state.bundle.nodes].sort((a,b)=>a.label.localeCompare(b.label,'fr'))){const opt=document.createElement('option');opt.value=n.id;opt.textContent=n.label;select.append(opt);}
 select.addEventListener('change',()=>selectCourse(select.value));
 $('back').addEventListener('click',()=>{const prev=state.last.pop();if(prev)selectCourse(prev,{first:true});});
 returnLink();const requested=new URLSearchParams(location.search).get('cours');
 selectCourse(state.byId.has(requested)?requested:(state.byId.has('qc-pri-ma-008')?'qc-pri-ma-008':state.bundle.nodes[0].id),{first:true});
 }catch(e){error('Lecture arrêtée : '+e.message);}}
main();
