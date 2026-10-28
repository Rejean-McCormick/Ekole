'use strict';
/* B4: interface Élève sans accès aux APIs enseignantes, ni stockage d'identité. */
const B4 = (() => {
  const main = document.querySelector('#app');
  let params = new URLSearchParams(window.__B4_TEST_QUERY ?? window.location.search);
  const apiMode = params.get('source') === 'api';
  let lesson = null;
  const route = (page, extra={}) => {
    const p = new URLSearchParams({page, ...extra});
    if (apiMode) p.set('source','api');
    return `?${p.toString()}`;
  };
  function node(parent, tag, text='', cls='') {
    const e=document.createElement(tag);
    if(cls)e.className=cls;
    if(text!==null)e.textContent=text;
    parent.append(e);return e;
  }
  const paragraph=(parent,text,cls='')=>node(parent,'p',text,cls);
  function link(parent,label,url,cls='btn') {const el=node(parent,'a',label,cls);el.href=url;return el;}
  function button(parent,label,fn,cls='btn') {const el=node(parent,'button',label,cls);el.type='button';el.addEventListener('click',fn);return el;}
  function heading(parent,title,lead='',kicker='') {if(kicker)paragraph(parent,kicker,'kicker');node(parent,'h1',title,'page-title');if(lead)paragraph(parent,lead,'lead');}
  function empty(){main.replaceChildren();}
  function note(parent,text,type=''){paragraph(parent,text,'feedback '+type).setAttribute('role','status');}
  function crumb(parent,parts){const n=node(parent,'nav',null,'trail');n.setAttribute('aria-label','Chemin dans le parcours');parts.forEach((part,i)=>{if(i)node(n,'span','›');if(part.href)link(n,part.name,part.href,'');else node(n,'span',part.name);});}
  function dotBoard(host,groups,each){
    host.replaceChildren();
    const board=node(host,'div',null,'group-board');board.setAttribute('aria-label',`${groups} groupes de ${each} jetons`);
    for(let i=0;i<groups;i++){
      const item=node(board,'div',null,'group-item');
      const box=node(item,'div',null,'group-box');box.setAttribute('aria-hidden','true');
      for(let j=0;j<each;j++)node(box,'span',null,'token');
      paragraph(item,'Boîte '+(i+1),'group-name');
    }
  }
  function footActions(parent,index){
    const r=node(parent,'nav',null,'btnrow space');r.setAttribute('aria-label','Navigation dans la leçon');
    if(index>0) link(r,'← Étape précédente',route('lecon',{etape:lesson.steps[index-1].id}),'btn secondary');
    else link(r,'← Mes activités',route('parcours'),'btn secondary');
    if(index+1<lesson.steps.length)link(r,'Étape suivante →',route('lecon',{etape:lesson.steps[index+1].id}),'btn primary');
    else link(r,'Terminer ma découverte →',route('fin'),'btn primary');
  }
  function renderHome(){
    empty();const hero=node(main,'section',null,'hero');
    heading(hero,'Bienvenue dans ton espace !','Aujourd’hui, on va apprendre en regardant, en essayant et en réfléchissant. Pas besoin de se dépêcher.','BONJOUR !');
    const visual=node(hero,'div',null,'hero-visual');visual.setAttribute('aria-hidden','true');
    for(let i=0;i<3;i++){const cell=node(visual,'div',null,'group-box');for(let j=0;j<4;j++)node(cell,'span',null,'hero-dot');}
    const actions=node(hero,'div',null,'btnrow');link(actions,'J’explore la 3e année →',route('parcours'),'btn primary large');
    paragraph(main,'Cette démonstration montre une seule notion de mathématique. Les autres matières et les 36 cours complets ne sont pas publiés ici.','soft-info');
  }
  function renderGrade(){
    empty();crumb(main,[{name:'Accueil',href:route('accueil')},{name:'3e année'}]);
    heading(main,'Mes découvertes de 3e année','Choisis une activité. Tu peux t’arrêter ou revenir en arrière quand tu veux.','MON PARCOURS');
    const cards=node(main,'div',null,'cards');const card=node(cards,'section',null,'course-card');
    node(card,'span','À découvrir','badge');node(card,'h2',lesson.title);
    paragraph(card,lesson.description);link(card,'Commencer →',route('lecon',{etape:lesson.steps[0].id}),'btn primary');
    const others=node(cards,'section',null,'course-card');node(others,'span','En préparation','badge soon');node(others,'h2','Les autres découvertes');
    paragraph(others,'Les autres cours seront ajoutés quand leurs activités auront été préparées et relues.');
    paragraph(main,'Tu ne reçois pas de note dans cette démonstration. Tu peux recommencer autant de fois que tu veux.','soft-info');
  }
  function renderObserve(host){dotBoard(host,3,4);paragraph(host,'Trois boîtes, quatre jetons dans chacune. Regarde bien les groupes.','soft-info');}
  function feedbackControl(host){const status=node(host,'p','', 'feedback');status.hidden=true;status.setAttribute('role','status');status.setAttribute('aria-live','polite');return (text,variant)=>{status.textContent=text;status.className='feedback '+variant;status.hidden=false;};}
  function renderPredict(host){
    dotBoard(host,3,4);
    paragraph(host,'À ton avis, combien y a-t-il de jetons en tout ?','question');
    const choices=node(host,'div',null,'choices');choices.setAttribute('role','group');choices.setAttribute('aria-label','Choisis une réponse');
    const say=feedbackControl(host);
    [7,12,14].forEach(n=>button(choices,n+' jetons',()=>{
      for(const b of choices.querySelectorAll('button')){b.classList.remove('good','try-again');b.setAttribute('aria-pressed','false');}
      const chosen=[...choices.querySelectorAll('button')].find(b=>b.textContent===n+' jetons');chosen.setAttribute('aria-pressed','true');
      chosen.classList.add(n===12?'good':'try-again');
      say(n===12?'Bien vu ! Tu as compté 12 jetons. Tu peux maintenant découvrir une autre manière de compter.':'Pas encore. Compte quatre jetons dans chaque boîte, une boîte après l’autre. Tu peux réessayer.',n===12?'success':'hint');
    },'tap-choice').setAttribute('aria-pressed','false'));
  }
  function renderExplain(host){
    dotBoard(host,3,4);
    paragraph(host,'Chaque boîte contient le même nombre de jetons. Ce sont des groupes égaux.','soft-info');
    const reveal=node(host,'div',null,'answer-reveal');reveal.hidden=true;
    button(host,'Voir une façon de compter',()=>{reveal.hidden=false;reveal.textContent='4 + 4 + 4 = 12. On peut aussi écrire 3 × 4 = 12.';},'btn secondary');
  }
  function renderManipulate(host){
    const inputs=node(host,'div',null,'form-grid');
    function makeRange(label,id,min,max,initial){const col=node(inputs,'div');const row=node(col,'label',null,'range-label');row.htmlFor=id;node(row,'span',label);const value=node(row,'output',String(initial));value.htmlFor=id;const input=node(col,'input');input.id=id;input.type='range';input.min=String(min);input.max=String(max);input.step='1';input.value=String(initial);input.setAttribute('aria-label',label);return {input,value};}
    const groups=makeRange('Nombre de boîtes','b4-groupes',1,6,3),each=makeRange('Jetons par boîte','b4-jetons',1,6,4);
    const picture=node(host,'div');const readout=node(host,'p','', 'answer-reveal');readout.hidden=true;
    const check=button(host,'Je vérifie mon calcul',()=>{readout.hidden=false;const g=Number(groups.input.value),j=Number(each.input.value);readout.textContent=`${g} groupes de ${j} jetons : ${g} × ${j} = ${g*j}.`;},'btn primary');
    function refresh(){groups.value.textContent=groups.input.value;each.value.textContent=each.input.value;dotBoard(picture,+groups.input.value,+each.input.value);readout.hidden=true;}
    groups.input.addEventListener('input',refresh);each.input.addEventListener('input',refresh);refresh();
    paragraph(host,'D’abord, compte les jetons. Ensuite, utilise « Je vérifie mon calcul ».','little-note');
  }
  function renderChallenge(host){
    paragraph(host,'4 sacs. 3 crayons dans chaque sac.','role-example');
    paragraph(host,'Quelle multiplication représente cette histoire ?','question');
    const opts=node(host,'div',null,'choices'),say=feedbackControl(host);
    ['4 × 3','4 + 3','3 + 4 + 3'].forEach((value,i)=>button(opts,value,()=>{
      for(const x of opts.querySelectorAll('button')){x.setAttribute('aria-pressed','false');x.classList.remove('good','try-again');}
      opts.children[i].setAttribute('aria-pressed','true');opts.children[i].classList.add(i===0?'good':'try-again');
      say(i===0?'Oui ! Quatre groupes de trois crayons, c’est 4 × 3.':'Regarde combien il y a de sacs et combien de crayons dans chaque sac. Réessaie.',i===0?'success':'hint');
    },'tap-choice').setAttribute('aria-pressed','false'));
  }
  function renderReflect(host){
    paragraph(host,'Ce que je peux maintenant faire :','question');
    const ul=node(host,'ul',null,'summary');['Dessiner des groupes égaux.','Compter tous les objets.','Écrire une addition ou une multiplication pour raconter une situation.'].forEach(t=>node(ul,'li',t));
    paragraph(host,'Comment te sens-tu après ce défi ?');const c=node(host,'div',null,'reflect-options'),message=feedbackControl(host);
    [['Je peux l’expliquer !','Super ! Tu peux essayer de l’expliquer à quelqu’un.'],['Je veux encore pratiquer','Bonne idée. Tu peux revenir aux boîtes de jetons autant de fois que tu veux.']].forEach(([label,msg])=>button(c,label,()=>{for(const b of c.querySelectorAll('button'))b.setAttribute('aria-pressed','false');const chosen=[...c.children].find(x=>x.textContent===label);chosen.setAttribute('aria-pressed','true');message(msg,'success');},'btn'));
  }
  function renderPlainStudentModule(host,step){
    const lines=String(step.texte||step.instruction||'').split(/\n+/).map(x=>x.trim()).filter(Boolean);
    for(const line of lines){let t=line.replace(/^#{1,5}\s*/,'').replace(/\*\*/g,'').replace(/`/g,'');if(!t)continue;
      if(line.startsWith('## ')||line.startsWith('### '))node(host,'h3',t,'section-heading');
      else if(line.startsWith('- '))paragraph(host,'• '+t.slice(2));
      else paragraph(host,t);
    }
  }
  function renderLesson(){
    empty();const req=params.get('etape');let index=lesson.steps.findIndex(s=>s.id===req);if(index<0)index=0;const step=lesson.steps[index];
    crumb(main,[{name:'Accueil',href:route('accueil')},{name:'3e année',href:route('parcours')},{name:'Multiplication'}]);
    paragraph(main,'MATHÉMATIQUE · 3e ANNÉE','kicker');node(main,'h1',lesson.title,'page-title');
    const shell=node(main,'section',null,'lesson-shell');
    const progress=node(shell,'div',null,'progress-head');node(progress,'b',`Étape ${index+1} sur ${lesson.steps.length}`);node(progress,'span','Tu avances à ton rythme','progress-text');
    const bar=node(shell,'div',null,'progress-track');bar.setAttribute('role','progressbar');bar.setAttribute('aria-label','Étape de la leçon');bar.setAttribute('aria-valuemin','1');bar.setAttribute('aria-valuemax',String(lesson.steps.length));bar.setAttribute('aria-valuenow',String(index+1));const fill=node(bar,'div',null,'progress-fill');fill.style.width=((index+1)/lesson.steps.length*100)+'%';
    const panel=node(shell,'article',null,'surface');node(panel,'h2',step.lead||step.name,'step-title');paragraph(panel,step.instruction||'','step-intro');const body=node(panel,'div',null,'lesson-main');
    ({observe:renderObserve,predict:renderPredict,explain:renderExplain,manipulate:renderManipulate,challenge:renderChallenge,reflect:renderReflect,reading:renderPlainStudentModule}[step.kind]||renderPlainStudentModule)(body,step);
    footActions(main,index);
  }
  function renderFinish(){
    empty();crumb(main,[{name:'Accueil',href:route('accueil')},{name:'3e année',href:route('parcours')},{name:'Fin de la découverte'}]);
    const panel=node(main,'section',null,'surface');heading(panel,'Bravo pour ta découverte !','Tu as regardé, cherché, essayé et expliqué. Tu peux refaire un défi quand tu en as envie.','C’EST TERMINÉ POUR AUJOURD’HUI');
    paragraph(panel,'Pas de note ici. L’important, c’est la manière dont tu apprends.','soft-info');
    const r=node(panel,'div',null,'btnrow');link(r,'Je refais la manipulation',route('lecon',{etape:'manipuler'}),'btn secondary');link(r,'Je retourne à ma 3e année',route('parcours'),'btn primary');
  }
  function error(text){empty();const panel=node(main,'div',null,'alert');heading(panel,'Cette activité n’est pas prête',text);link(panel,'Revenir à l’accueil',route('accueil'),'btn');}
  async function load(){
    if(!apiMode){lesson=window.EKOLE_B4_DEMO;return;}
    // IMPORTANT : l'API est exclusivement la publication élève publique de v3.
    // Ne jamais requêter /api/editor, /api/kristal ou un document expert.
    const res=await fetch('/api/cours/qc-pri-ma-008.json',{credentials:'omit',cache:'no-store'});
    if(!res.ok)throw Error('La publication Élève est indisponible.');
    const data=await res.json();
    if(data.format!=='ekole.student-publication/1'||data.id!=='qc-pri-ma-008'||!Array.isArray(data.modules)||!data.modules.length)
      throw Error('Aucune version Élève publiée et compatible.');
    // Défense supplémentaire si un serveur défaillant laisse passer des fragments experts.
    if(/réponse et critères|sans note certificative|préalable interne|acquis équivalent|qc-pri-[a-z]{2}-\d{3}/i.test(JSON.stringify(data.modules)))
      throw Error('Publication incorrecte : revue pédagogique nécessaire.');
    lesson={title:data.titre,description:'Je découvre la multiplication à mon rythme.',steps:data.modules.map((m,i)=>({id:m.id,name:m.titre,lead:m.titre,texte:m.texte,kind:'reading',instruction:''}))};
  }
  async function start(){try{await load();if(!lesson||!Array.isArray(lesson.steps)||!lesson.steps.length)throw Error('Activité indisponible.');
      const page=params.get('page')||'accueil';if(page==='parcours')renderGrade();else if(page==='lecon')renderLesson();else if(page==='fin')renderFinish();else renderHome();}
    catch(e){error(e.message);}}
  document.addEventListener('click', e=>{
    const anchor=e.target.closest('a[href^="?"]');
    if(!anchor || e.defaultPrevented || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey)return;
    // En mode fichier local Windows, laisser le navigateur suivre les liens
    // (pushState peut etre interdit pour les origines file://).
    if(window.location.protocol==='file:' && typeof window.__B4_TEST_QUERY!=='string')return;
    e.preventDefault();
    const dest=anchor.getAttribute('href');
    if(typeof window.__B4_TEST_QUERY==='string')window.__B4_TEST_QUERY=dest;
    else window.history.pushState(null,'',dest);
    params=new URLSearchParams(window.__B4_TEST_QUERY ?? window.location.search);
    start();window.scrollTo(0,0);main.focus({preventScroll:true});
  });
  window.addEventListener('popstate',()=>{params=new URLSearchParams(window.location.search);start();});
  start();return {route,refresh:()=>{params=new URLSearchParams(window.__B4_TEST_QUERY ?? window.location.search);return start();}};
})();
