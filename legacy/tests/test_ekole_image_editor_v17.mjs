import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const app=fs.readFileSync(path.join(root,'enseignant-app/app.js'),'utf8');
const fragment=app.slice(app.indexOf('const copyTimers='),app.indexOf('function label('));
class ClassList {constructor(){this.set=new Set();}add(...ss){ss.forEach(s=>this.set.add(s));}remove(...ss){ss.forEach(s=>this.set.delete(s));}contains(s){return this.set.has(s);}}
class Element {constructor(tag){this.tagName=tag;this.children=[];this.handlers={};this.classList=new ClassList();this.textContent='';this.hidden=false;this.style={};this.value='';}
 append(...els){els.forEach(el=>{el.parent=this;this.children.push(el);});}
 remove(){if(this.parent)this.parent.children=this.parent.children.filter(x=>x!==this);}
 replaceChildren(...els){this.children=[];this.append(...els);}
 addEventListener(t,fn){this.handlers[t]=fn;}
 setAttribute(k,v){this[k]=v;}
 removeAttribute(k){delete this[k];}
 querySelector(k){return this.children.find(x=>x.tagName===k);}
 select(){}
}
const all=e=>[e,...e.children.flatMap(all)];const find=(e,f)=>all(e).find(f);
const makeDoc=()=>({body:new Element('body'),createElement:t=>new Element(t),execCommand:()=>true});
const doc=makeDoc(),data={};const add=(parent,tag,cls='',v)=>{const x=new Element(tag);x.className=cls;if(v!==undefined)x.textContent=String(v);parent.append(x);return x;};
const ctx=vm.createContext({document:doc,add,navigator:{clipboard:{writeText:async v=>data.copied=v}},setTimeout:()=>1,clearTimeout:()=>{},console});
vm.runInContext(fragment+'\nthis.imageProductionCode=imageProductionCode;this.promptWithProductionCode=promptWithProductionCode;this.copyImagePrompt=copyImagePrompt;',ctx);
const code=ctx.imageProductionCode('qc-pri-ma-028','concept');
assert.equal(code,'EKOLE-IMG-QC-PRI-MA-028-CONCEPT');
assert.notEqual(code,ctx.imageProductionCode('qc-pri-ma-029','concept'));
const composed=ctx.promptWithProductionCode('Une illustration de fractions','EKOLE-IMG-QC-PRI-MA-028-CONCEPT');
assert.match(composed,/Une illustration de fractions/);
assert.match(composed,/EKOLE-IMG-QC-PRI-MA-028-CONCEPT/);
assert.match(composed,/Ne jamais représenter ce code/);
await ctx.copyImagePrompt(new Element('button'),composed);
assert.equal(data.copied,composed);
// Authoring-only code: not inserted into the student web script.
const student=fs.readFileSync(path.join(root,'site/eleve/app.js'),'utf8');
assert.ok(!student.includes('imageProductionCode'));

let confirmed=false, deleteCalls=0, deleted=false, callback=false;
const doc2=makeDoc();const context=vm.createContext({
 document:doc2,
 window:{confirm:()=>confirmed},
 URL:{createObjectURL:()=> 'blob:preview',revokeObjectURL:()=>{}},
 fetch:async(url,opt={})=>{
  if(url.includes('config'))return{ok:true,json:async()=>({csrf:'token'})};
  if(opt.method==='DELETE'){deleteCalls++;assert.equal(opt.headers['X-Ekole-Delete-Confirm'],'yes');return{ok:true,json:async()=>({status:'deleted',public_url:null})};}
  throw Error('unexpected URL: '+url);
 },
 console,encodeURIComponent
});
vm.runInContext(fs.readFileSync(path.join(root,'enseignant-app/images-editor-v15.js'),'utf8'),context);
const parent=new Element('main');const wrapper=context.window.EkoleImagesV15.attach(parent,'qc-pri-ma-028','concept',true,null,(result,status)=>{deleted=true;callback=true;status.textContent='Effacée et remplacée par la description.';});
const erase=find(wrapper,x=>x.className==='button secondary image-delete-button');
assert.ok(erase);assert.equal(erase.disabled,false);
await erase.handlers.click();assert.equal(deleteCalls,0,'Cancellation must not send DELETE');
assert.equal(erase.disabled,false);
confirmed=true;await erase.handlers.click();assert.equal(deleteCalls,1);
assert.equal(deleted,true);assert.equal(callback,true);assert.equal(erase.disabled,true);
assert.match(find(wrapper,x=>x.className==='image-upload-feedback').textContent,/Effacée/);
const blankParent=new Element('main');const blank=context.window.EkoleImagesV15.attach(blankParent,'qc-pri-ma-028','concept',false);
assert.equal(find(blank,x=>x.className==='button secondary image-delete-button').disabled,true);
console.log('PASS v17: stable hidden-code prompt, copy, delete cancellation/confirmation and live feedback');
