/* Ekole Atelier v8: educational explorations. No assessment, telemetry or stored results. */
(function (global) {
  'use strict';
  const examples = Object.freeze({
    denombrer:[{count:6,choices:[5,6,7]},{count:8,choices:[7,8,9]},{count:10,choices:[9,10,11]}],
    fraction:[{total:2,wanted:1},{total:5,wanted:2},{total:4,wanted:3}],
    groupes:[{total:12,groups:3},{total:12,groups:4},{total:15,groups:5}],
    estimation:[{count:8},{count:11},{count:14}]
  });
  const labTypes=Object.keys(examples).concat('lecture','theatre','reflexion');
  function valid(type,exercise,response){
    if(type==='denombrer')return response===exercise.count;
    if(type==='fraction')return response===exercise.wanted;
    if(type==='groupes')return response===exercise.total/exercise.groups;
    if(type==='estimation')return response===exercise.count;
    return null;
  }
  function make(tag,cl='',text){const e=document.createElement(tag);if(cl)e.className=cl;if(text!==undefined)e.textContent=String(text);return e;}
  function add(parent,tag,cl,text){const e=make(tag,cl,text);parent.append(e);return e;}
  function button(parent,text,action,cl='action'){const b=add(parent,'button',cl,text);b.type='button';b.addEventListener('click',action);return b;}
  function speak(text){if(!('speechSynthesis'in global))return false;try{global.speechSynthesis.cancel();const u=new SpeechSynthesisUtterance(text);u.lang='fr-CA';u.rate=.85;global.speechSynthesis.speak(u);return true;}catch(_){return false;}}
  function voiceButton(parent,text){button(parent,'🔊 Écouter la consigne',()=>{if(!speak(text))add(parent,'p','tiny','Lecture audio non disponible sur cet appareil.');},'secondary');}
  function result(host,initial){const p=add(host,'p','feedback-v8',initial);p.setAttribute('role','status');p.setAttribute('aria-live','polite');return p;}
  function renderCounting(host){let index=0;
    const title=add(host,'h3','','Je compte les jetons');const instruction='Touche chaque jeton avec tes yeux. Combien en vois-tu ?';add(host,'p','lead',instruction);voiceButton(host,instruction);
    const points=add(host,'div','counting-grid');points.setAttribute('role','group');points.setAttribute('aria-label','Jetons à compter');const choices=add(host,'div','choice-row');const feedback=result(host,'Choisis un nombre. Tu peux recommencer.');
    function draw(){const e=examples.denombrer[index];points.replaceChildren();choices.replaceChildren();
      for(let i=0;i<e.count;i++){const dot=add(points,'span','counter','●');dot.setAttribute('aria-label',`Jeton ${i+1}`);dot.setAttribute('role','img');}
      for(const n of e.choices)button(choices,String(n),()=>{feedback.textContent=valid('denombrer',e,n)?'Oui, tu as compté chaque jeton une fois !':'Essaie encore : compte un jeton après l’autre.';},'number-button');}
    draw();button(host,'Une autre collection ↻',()=>{index=(index+1)%examples.denombrer.length;draw();feedback.textContent='Nouveau défi. À toi de compter !';},'secondary');
  }
  function renderFraction(host){let index=0,chosen=new Set();add(host,'h3','','Je colorie les fractions');const explain=add(host,'p','lead','Colorie les parts égales demandées.');voiceButton(host,explain.textContent);const status=result(host,'Clique sur les parts à colorier.');const boxes=add(host,'div','fraction-v8');const controls=add(host,'div','choice-row');
    function draw(){const e=examples.fraction[index];chosen=new Set();boxes.replaceChildren();controls.replaceChildren();add(host,'span','sr-only',`Fraction ${e.wanted} sur ${e.total}`);
      status.textContent=`Colorie ${e.wanted} part${e.wanted>1?'s':''} sur ${e.total} parts égales.`;
      for(let i=0;i<e.total;i++){const j=i,b=button(boxes,'',()=>{if(chosen.has(j))chosen.delete(j);else chosen.add(j);b.setAttribute('aria-pressed',String(chosen.has(j)));b.textContent=chosen.has(j)?'■':'□';},'fraction-part');b.textContent='□';b.setAttribute('aria-pressed','false');b.setAttribute('aria-label',`Colorier la part ${i+1} sur ${e.total}`);}
      button(controls,'Vérifier',()=>{status.textContent=valid('fraction',e,chosen.size)?`Exactement ${e.wanted} parts sur ${e.total}. Pourquoi les parts doivent-elles être égales ?`:`Tu as choisi ${chosen.size} part(s). On en cherche ${e.wanted}.`;},'action');
      button(controls,'Recommencer',()=>draw(),'secondary');}
    draw();button(host,'Une autre fraction ↻',()=>{index=(index+1)%examples.fraction.length;draw();},'secondary');
  }
  function renderGrouping(host){let index=0;add(host,'h3','','Je forme des groupes égaux');const instruction='Trouve combien de jetons il y aura dans chaque groupe.';add(host,'p','lead',instruction);voiceButton(host,instruction);
    const display=add(host,'div','grouping-grid');const controls=add(host,'div','choice-row');const status=result(host,'Observe le nombre total de jetons et de groupes.');
    function draw(){const e=examples.groupes[index];display.replaceChildren();controls.replaceChildren();add(display,'p','',`${e.total} jetons · ${e.groups} groupes`);const nodes=add(display,'div','group-frames');for(let k=0;k<e.groups;k++){const slot=add(nodes,'div','group-frame','?');slot.setAttribute('aria-label',`Groupe ${k+1} vide`);}
       for(const n of [e.total/e.groups-1,e.total/e.groups,e.total/e.groups+1])button(controls,String(n)+' par groupe',()=>{status.textContent=valid('groupes',e,n)?`Bravo ! ${e.groups} groupes de ${n} jetons font ${e.total} jetons.`:'Repartage les jetons : chaque groupe doit en recevoir autant.';},'number-button');}
    draw();button(host,'Un nouveau partage ↻',()=>{index=(index+1)%examples.groupes.length;draw();status.textContent='Fais un nouveau partage.';},'secondary');
  }
  function renderEstimation(host){let index=0;let reveal=false;add(host,'h3','','Je devine, puis je vérifie');const prompt='Estime le nombre de jetons. Ensuite, révèle le nombre et compare ton estimation.';add(host,'p','lead',prompt);voiceButton(host,prompt);const dots=add(host,'div','counting-grid');const entry=add(host,'div','choice-row');const status=result(host,'Commence par une estimation.');
    function draw(){reveal=false;entry.replaceChildren();dots.replaceChildren();const e=examples.estimation[index];for(let i=0;i<e.count;i++)add(dots,'span','counter','●');for(const x of [e.count-2,e.count,e.count+2])button(entry,String(x),()=>{const diff=Math.abs(e.count-x);status.textContent=`Il y a ${e.count} jetons. Tu avais choisi ${x}. L’écart est de ${diff}.`;},'number-button');}
    draw();button(host,'Nouvelle estimation ↻',()=>{index=(index+1)%examples.estimation.length;draw();status.textContent='Essaie un nouveau nombre.';},'secondary');
  }
  function renderReading(host){add(host,'h3','','Je lis avec expression');const quote='Le vent souffle doucement. Puis, soudain, la pluie arrive !';const block=add(host,'blockquote','reading-card',quote);add(host,'p','','Lis d’abord lentement. Lis une deuxième fois en faisant une pause au point et en changeant ton intonation au point d’exclamation.');voiceButton(host,quote);add(host,'p','hint','On ne mesure pas ta vitesse et aucune lecture n’est enregistrée.');button(host,'J’ai lu deux fois ✓',()=>{add(host,'p','feedback-v8','Qu’est-ce qui était plus facile la deuxième fois ?');},'secondary');}
  function renderDrama(host){add(host,'h3','','Je joue avec les gestes et la voix');add(host,'p','lead','Choisis une intention : accueillir quelqu’un, remercier ou demander de l’aide.');const select=add(host,'select','theatre-select');['Accueillir','Remercier','Demander de l’aide'].forEach(x=>{const o=add(select,'option','',x);o.value=x;});const feed=result(host,'Tu peux jouer debout, assis ou avec une marionnette.');const choice=add(host,'div','choice-row');['Avec mon corps','Avec ma voix'].forEach(x=>button(choice,x,()=>{feed.textContent=`Montre « ${select.value} » ${x==='Avec mon corps'?'avec une posture ou un geste':'avec une intonation'}; une autre personne peut deviner ton intention.`;},'chip'));
    add(host,'p','hint','Ton confort compte. Tu peux observer au lieu de jouer. Il n’y a pas de jugement de personnalité.');}
  function renderReflection(host,activity){add(host,'h3','','Je cherche une façon de montrer mon idée');const p=add(host,'p','lead',activity.consigne_courte);voiceButton(host,p.textContent);const row=add(host,'div','choice-row');const detail=result(host,'Choisis une façon d’essayer.');
    [['✏️ Dessiner','Fais un dessin qui montre ton idée.'],['🗣️ Raconter','Explique ton idée à quelqu’un.'],['👐 Manipuler','Utilise des objets ou des gestes pour montrer ton idée.']].forEach(([n,txt])=>button(row,n,()=>{detail.textContent=txt;},'chip'));
    add(host,'p','tiny','Activité d’exploration accompagnée : aucune réponse libre à saisir ni note automatique.');}
  function render(host,activity){host.replaceChildren();const lab=add(host,'div','lab-card');const type=activity?.activite_type||'reflexion';
    ({denombrer:renderCounting,fraction:renderFraction,groupes:renderGrouping,estimation:renderEstimation,lecture:renderReading,theatre:renderDrama,reflexion:renderReflection}[type]||renderReflection)(lab,activity||{});
    add(host,'p','tiny','Atelier de découverte. Ne remplace pas une preuve autonome de maîtrise du Kristal.');}
  global.EkoleAteliers={render,valid,examples,types:labTypes};
  if(typeof module!=='undefined'&&module.exports)module.exports={valid,examples,types:labTypes};
})(typeof window!=='undefined'?window:globalThis);
