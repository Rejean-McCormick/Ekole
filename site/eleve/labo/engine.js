/* Ekole MiniLab Engine v0.1 — pure deterministic practice, no network, no tracking. */
(function(root,factory){const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;if(root)root.EkoleMiniLabEngine=api;})(typeof globalThis!=='undefined'?globalThis:null,function(){
 'use strict';
 const TYPES=['jetons','fraction','droite','ordonner','associer','classer','grille','estimer','suite','position','probleme','diagramme','equivalence','duree'];
 function fail(msg){throw new Error('Invalid mini-lab configuration: '+msg);}
 function integer(n){return Number.isInteger(n);}
 function unique(a){return new Set(a).size===a.length;}
 function validateSpec(spec){
  if(!spec||typeof spec!=='object'||typeof spec.id!=='string'||!/^[-a-z0-9]{3,48}$/.test(spec.id)||!TYPES.includes(spec.type))fail('id/type');
  if(typeof spec.title!=='string'||!spec.title.trim()||typeof spec.instruction!=='string'||!spec.instruction.trim())fail('text');
  const p=spec.parameters;if(!p||typeof p!=='object')fail('parameters');
  switch(spec.type){
   case 'jetons':if(!integer(p.total)||p.total<1||p.total>40||!integer(p.groups)||p.groups<2||p.groups>8||p.groups>p.total)fail('total/groups');break;
   case 'fraction':if(!integer(p.total)||p.total<2||p.total>16||!integer(p.wanted)||p.wanted<1||p.wanted>p.total)fail('fraction');break;
   case 'droite':if(![p.min,p.max,p.start,p.target,p.step].every(integer)||p.max-p.min<2||p.max-p.min>40||p.step<1||p.step>5||p.start<p.min||p.start>p.max||p.target<p.min||p.target>p.max||(p.target-p.min)%p.step!==0||(p.start-p.min)%p.step!==0)fail('number line');break;
   case 'ordonner':{const a=p.cards;if(!Array.isArray(a)||a.length<3||a.length>8||!a.every(x=>typeof x.id==='string'&&typeof x.text==='string'&&x.text.trim())||!unique(a.map(x=>x.id))||!Array.isArray(p.correct)||!Array.isArray(p.initial)||p.correct.length!==a.length||p.initial.length!==a.length||!unique(p.correct)||!unique(p.initial)||!p.correct.every(x=>a.some(y=>y.id===x))||!p.initial.every(x=>a.some(y=>y.id===x)))fail('order');break;}
   case 'associer':{const a=p.pairs;if(!Array.isArray(a)||a.length<2||a.length>8||!a.every(x=>['left','label','right','correct_label'].every(k=>typeof x[k]==='string'&&x[k].trim()))||!unique(a.map(x=>x.left))||!unique(a.map(x=>x.right)))fail('matching');break;}
   case 'classer':{const a=p.objects;if(!Array.isArray(p.bins)||p.bins.length<2||p.bins.length>5||!unique(p.bins)||!p.bins.every(x=>typeof x==='string'&&x.trim())||!Array.isArray(a)||a.length<2||a.length>12||!a.every(x=>typeof x.id==='string'&&typeof x.text==='string'&&p.bins.includes(x.bin))||!unique(a.map(x=>x.id)))fail('bins');break;}
   case 'grille':if(!integer(p.width)||!integer(p.height)||p.width<2||p.width>10||p.height<2||p.height>10||!Array.isArray(p.target)||p.target.length!==2||typeof p.target[0]!=='string'||!integer(p.target[1])||p.target[0].length!==1||p.target[0].charCodeAt(0)<65||p.target[0].charCodeAt(0)>=65+p.width||p.target[1]<1||p.target[1]>p.height)fail('coordinates');break;
   case 'estimer':if(![p.exact,p.min,p.max,p.tolerance].every(integer)||p.min<0||p.max>10000||p.max<=p.min||p.tolerance<0||p.exact<p.min||p.exact>p.max||!Array.isArray(p.display_groups)||p.display_groups.length<1||p.display_groups.length>15||!p.display_groups.every(x=>integer(x)&&x>=1&&x<=10)||p.display_groups.reduce((a,b)=>a+b,0)!==p.exact)fail('estimate');break;

   case 'position':if(!integer(p.target)||p.target<100||p.target>999||!Array.isArray(p.start)||p.start.length!==3||!p.start.every(n=>integer(n)&&n>=0&&n<=9)||p.start[0]*100+p.start[1]*10+p.start[2]===p.target)fail('place value');break;
   case 'probleme':if(!Array.isArray(p.steps)||p.steps.length!==2||!p.steps.every(x=>x&&typeof x.prompt==='string'&&x.prompt.trim()&&Array.isArray(x.options)&&x.options.length>=3&&x.options.length<=5&&unique(x.options)&&x.options.every(y=>typeof y==='string'&&y.trim())&&x.options.includes(x.answer)))fail('multi-step');break;
   case 'diagramme':if(!Array.isArray(p.bars)||p.bars.length<3||p.bars.length>6||!p.bars.every(x=>x&&typeof x.label==='string'&&x.label&&integer(x.value)&&x.value>=1&&x.value<=20)||!unique(p.bars.map(x=>x.label))||!Array.isArray(p.questions)||p.questions.length!==2||!p.questions.every(x=>x&&typeof x.prompt==='string'&&Array.isArray(x.options)&&x.options.length>=3&&unique(x.options)&&x.options.every(integer)&&x.options.includes(x.answer)))fail('diagramme');break;
   case 'equivalence':if(!integer(p.numerator)||!integer(p.denominator)||p.numerator<1||p.denominator<=p.numerator||p.denominator>12||!Array.isArray(p.choices)||p.choices.length<4||p.choices.length>7||!p.choices.every(x=>x&&typeof x.id==='string'&&integer(x.n)&&integer(x.d)&&x.n>0&&x.d>x.n&&x.d<=36)||!unique(p.choices.map(x=>x.id))||!p.choices.some(x=>x.n*p.denominator===x.d*p.numerator)||!p.choices.some(x=>x.n*p.denominator!==x.d*p.numerator))fail('equivalence');break;
   case 'duree':if(![p.start_hour,p.start_minute,p.duration,p.max_duration].every(integer)||p.start_hour<0||p.start_hour>23||p.start_minute<0||p.start_minute>=60||p.duration<=0||p.duration>p.max_duration||p.max_duration>180||p.start_hour*60+p.start_minute+p.duration>=1440)fail('elapsed time');break;
   case 'suite':if(!Array.isArray(p.shown)||p.shown.length<3||p.shown.length>8||!p.shown.every(integer)||!Array.isArray(p.choices)||p.choices.length<2||p.choices.length>6||!p.choices.every(integer)||!unique(p.choices)||!p.choices.includes(p.answer)||!integer(p.answer)||p.shown.some((n,i)=>i>1&&n-p.shown[i-1]!==p.shown[1]-p.shown[0])||p.answer!==p.shown[p.shown.length-1]+(p.shown[1]-p.shown[0]))fail('sequence');break;
  }
  return true;
 }
 function initial(spec){validateSpec(spec);const p=spec.parameters;
  switch(spec.type){
   case 'jetons':return {bins:Array(p.total).fill(-1),active:null};
   case 'fraction':return {marked:[]};
   case 'droite':return {value:p.start};
   case 'ordonner':return {order:p.initial.slice()};
   case 'associer':return {matches:{}};
   case 'classer':return {bins:{}};
   case 'grille':return {column:null,row:null};
   case 'estimer':return {value:null};
   case 'suite':return {choice:null};
   case 'position':return {digits:p.start.slice()};
   case 'probleme':return {answers:[null,null]};
   case 'diagramme':return {answers:[null,null]};
   case 'equivalence':return {selected:[]};
   case 'duree':return {minutes:0};
  }
 }
 function apply(spec,state,action){validateSpec(spec);const p=spec.parameters;const s=JSON.parse(JSON.stringify(state));if(!action||typeof action!=='object')return s;
  switch(spec.type){
   case 'jetons':if(action.kind==='select'&&integer(action.index)&&action.index>=0&&action.index<p.total)s.active=action.index;
    if(action.kind==='place'&&integer(action.group)&&action.group>=-1&&action.group<p.groups&&integer(s.active)&&s.active>=0&&s.active<p.total){s.bins[s.active]=action.group;s.active=null;}
    if(action.kind==='back'&&integer(action.index)&&action.index>=0&&action.index<p.total)s.bins[action.index]=-1;break;
   case 'fraction':if(action.kind==='toggle'&&integer(action.index)&&action.index>=0&&action.index<p.total){const set=new Set(s.marked);set.has(action.index)?set.delete(action.index):set.add(action.index);s.marked=Array.from(set).sort((a,b)=>a-b);}break;
   case 'droite':if(action.kind==='shift'&&[-1,1].includes(action.direction))s.value=Math.min(p.max,Math.max(p.min,s.value+action.direction*p.step));
    if(action.kind==='set'&&integer(action.value)&&action.value>=p.min&&action.value<=p.max&&(action.value-p.min)%p.step===0)s.value=action.value;break;
   case 'ordonner':if(action.kind==='move'&&integer(action.index)&&[-1,1].includes(action.direction)){const i=action.index,j=i+action.direction;if(i>=0&&i<s.order.length&&j>=0&&j<s.order.length)[s.order[i],s.order[j]]=[s.order[j],s.order[i]];}break;
   case 'associer':if(action.kind==='set'&&p.pairs.some(x=>x.left===action.id)&&(action.value===''||p.pairs.some(x=>x.right===action.value))){s.matches[action.id]=action.value;}break;
   case 'classer':if(action.kind==='set'&&p.objects.some(x=>x.id===action.id)&&(action.value===''||p.bins.includes(action.value))){s.bins[action.id]=action.value;}break;
   case 'grille':if(action.kind==='set'&&typeof action.column==='string'&&integer(action.row)&&action.column>='A'&&action.column<=String.fromCharCode(64+p.width)&&action.row>=1&&action.row<=p.height){s.column=action.column;s.row=action.row;}break;
   case 'estimer':if(action.kind==='set'){const v=Number(action.value);s.value=Number.isFinite(v)&&integer(v)&&v>=p.min&&v<=p.max?v:null;}break;
   case 'position':if(action.kind==='shift'&&integer(action.column)&&action.column>=0&&action.column<3&&[-1,1].includes(action.direction))s.digits[action.column]=(s.digits[action.column]+action.direction+10)%10;break;
   case 'probleme':case 'diagramme':{const questions=spec.type==='probleme'?p.steps:p.questions;if(action.kind==='choose'&&integer(action.index)&&action.index>=0&&action.index<2&&questions[action.index].options.includes(action.value))s.answers[action.index]=action.value;break;}
   case 'equivalence':if(action.kind==='toggle'&&p.choices.some(x=>x.id===action.id)){const a=new Set(s.selected);a.has(action.id)?a.delete(action.id):a.add(action.id);s.selected=[...a].sort();}break;
   case 'duree':if(action.kind==='shift'&&integer(action.minutes)&&[-60,-30,-15,-10,-5,5,10,15,30,60].includes(action.minutes))s.minutes=Math.max(0,Math.min(p.max_duration,s.minutes+action.minutes));break;
   case 'suite':if(action.kind==='set'&&p.choices.includes(action.value))s.choice=action.value;break;
  }return s;
 }
 function evaluate(spec,s){validateSpec(spec);const p=spec.parameters;let ok=false,complete=true,code='try_again',detail={};
  switch(spec.type){
   case 'jetons':{const counts=Array(p.groups).fill(0);for(const b of s.bins)if(integer(b)&&b>=0&&b<p.groups)counts[b]++;const rest=s.bins.filter(x=>x===-1).length;const quotient=Math.floor(p.total/p.groups),remainder=p.total%p.groups;ok=counts.every(n=>n===quotient)&&rest===remainder;complete=counts.some(n=>n>0);code=ok?'correct':counts.some(n=>n>quotient)?'too_many_in_group':rest>remainder?'tokens_remaining':'unequal_groups';detail={counts,rest,quotient,remainder};break;}
   case 'fraction':ok=s.marked.length===p.wanted;complete=s.marked.length>0;code=ok?'correct':s.marked.length<p.wanted?'not_enough':'too_many';detail={colored:s.marked.length,total:p.total};break;
   case 'droite':ok=s.value===p.target;code=ok?'correct':s.value<p.target?'move_right':'move_left';detail={value:s.value};break;
   case 'ordonner':ok=s.order.every((x,i)=>p.correct[i]===x);code=ok?'correct':'order_mismatch';detail={positions:s.order.length};break;
   case 'associer':{const filled=p.pairs.filter(x=>s.matches[x.left]).length;complete=filled===p.pairs.length;ok=complete&&p.pairs.every(x=>s.matches[x.left]===x.right);code=ok?'correct':!complete?'incomplete_pairs':'pair_mismatch';detail={filled,total:p.pairs.length};break;}
   case 'classer':{const filled=p.objects.filter(x=>s.bins[x.id]).length;complete=filled===p.objects.length;ok=complete&&p.objects.every(x=>s.bins[x.id]===x.bin);code=ok?'correct':!complete?'incomplete_bins':'bin_mismatch';detail={filled,total:p.objects.length};break;}
   case 'grille':complete=!!s.column&&!!s.row;ok=s.column===p.target[0]&&s.row===p.target[1];code=ok?'correct':!complete?'pick_cell':'wrong_cell';detail={coordinate:s.column?`${s.column}${s.row}`:null};break;
   case 'estimer':complete=integer(s.value);ok=complete&&Math.abs(s.value-p.exact)<=p.tolerance;code=ok?'reasonable_estimate':!complete?'enter_number':'estimate_gap';detail={value:s.value,exact:p.exact,gap:complete?Math.abs(s.value-p.exact):null};break;
   case 'position':{const n=s.digits[0]*100+s.digits[1]*10+s.digits[2];complete=true;ok=n===p.target;code=ok?'correct':s.digits[0]!==Math.floor(p.target/100)?'hundreds_mismatch':s.digits[1]!==Math.floor(p.target/10)%10?'tens_mismatch':'units_mismatch';detail={value:n};break;}
   case 'probleme':case 'diagramme':{const questions=spec.type==='probleme'?p.steps:p.questions;complete=s.answers.every(x=>x!==null);const checks=questions.map((x,i)=>s.answers[i]===x.answer);ok=complete&&checks.every(Boolean);code=ok?'correct':!complete?'complete_steps':!checks[0]?'first_step':'second_step';detail={checks};break;}
   case 'equivalence':{complete=s.selected.length>0;const valid=p.choices.filter(x=>x.n*p.denominator===x.d*p.numerator).map(x=>x.id).sort();const wrong=s.selected.filter(x=>!valid.includes(x));const missing=valid.filter(x=>!s.selected.includes(x));ok=wrong.length===0&&missing.length===0;code=ok?'correct':wrong.length?'wrong_equivalence':'missing_equivalence';detail={missing:missing.length,incorrect:wrong.length};break;}
   case 'duree':complete=true;ok=s.minutes===p.duration;code=ok?'correct':s.minutes<p.duration?'duration_short':'duration_long';detail={minutes:s.minutes};break;
   case 'suite':complete=s.choice!==null;ok=s.choice===p.answer;code=ok?'correct':!complete?'choose_option':'pattern_mismatch';break;
  }
  const feedback={correct:'Bien joué ! Ta construction respecte la consigne.',reasonable_estimate:'Ton estimation est dans la zone attendue. Ce n’est pas une mesure exacte.',too_many_in_group:'Un groupe contient trop d’objets. Compare les boîtes.',tokens_remaining:'Il reste des objets à distribuer. Vérifie si le reste est nécessaire.',unequal_groups:'Compare chaque boîte : le partage doit être équitable.',not_enough:'Il manque des parts coloriées.',too_many:'Tu as colorié trop de parts.',move_right:'Le repère est trop à gauche.',move_left:'Le repère est trop à droite.',order_mismatch:'Regarde ce qui doit se passer avant et après.',incomplete_pairs:'Certaines associations sont encore vides.',pair_mismatch:'Au moins une association est à revoir.',incomplete_bins:'Chaque objet doit être classé.',bin_mismatch:'Un classement ne correspond pas à la propriété.',pick_cell:'Choisis une case de la grille.',wrong_cell:'Regarde la lettre de colonne et le numéro de ligne.',enter_number:'Entre un nombre entier dans l’intervalle.',estimate_gap:'Cette estimation est trop éloignée. Cherche un ordre de grandeur.',choose_option:'Choisis une réponse.',pattern_mismatch:'Regarde de combien la suite augmente à chaque fois.',hundreds_mismatch:'Vérifie le chiffre des centaines : chaque centaine vaut dix dizaines.',tens_mismatch:'Vérifie le chiffre des dizaines, pas celui des unités.',units_mismatch:'Les centaines et dizaines sont bonnes : vérifie les unités.',complete_steps:'Choisis une proposition pour chaque étape du raisonnement.',first_step:'La première décision ne correspond pas aux données du problème.',second_step:'Reprends le calcul ou la décision de la deuxième étape.',wrong_equivalence:'Une des fractions choisies ne représente pas la même part du tout.',missing_equivalence:'Il reste au moins une fraction équivalente à reconnaître.',duration_short:'Ton trajet dans le temps est trop court.',duration_long:'Tu as dépassé la durée entre les deux heures.'};
  return {correct:!!ok,complete:!!complete,code,feedback:feedback[code]||'Essaie de nouveau.',detail,proof_of_mastery:false};
 }
 return Object.freeze({TYPES,validateSpec,initial,apply,evaluate});
});
