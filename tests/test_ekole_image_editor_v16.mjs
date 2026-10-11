import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
class FakeClassList {
 constructor(){this.values=new Set();}
 add(...items){for(const s of items)this.values.add(s);}
 remove(...items){for(const s of items)this.values.delete(s);}
 contains(s){return this.values.has(s);}
}
class Element {
 constructor(tag){this.tagName=tag;this.children=[];this.classList=new FakeClassList();this.handlers={};this.style={};this.hidden=false;this.textContent='';this.value='';}
 append(...items){for(const item of items){item.parent=this;this.children.push(item);} }
 appendChild(item){this.append(item);return item;}
 replaceChildren(...items){this.children=[];this.append(...items);}
 remove(){if(this.parent)this.parent.children=this.parent.children.filter(c=>c!==this);}
 addEventListener(type,fn){this.handlers[type]=fn;}
 setAttribute(k,v){this[k]=v;}
 querySelector(selector){if(selector==='span')return this.children.find(e=>e.tagName==='span');return null;}
 select(){}
}
const all=(el)=>[el,...el.children.flatMap(all)];
const find=(el, predicate)=>all(el).find(predicate);
const makeDocument=()=>({body:new Element('body'),createElement:t=>new Element(t),execCommand:()=>true});
// Copy prompt changes state only on successful clipboard operations.
const app=fs.readFileSync(path.join(root,'enseignant-app/app.js'),'utf8');
const appHelper=app.slice(app.indexOf('const copyTimers='),app.indexOf('function label('));
const document=makeDocument();
const mockTimers=[];
const add=(parent,tag,klass='',value)=>{const x=new Element(tag);x.className=klass;if(value!==undefined)x.textContent=String(value);parent.append(x);return x;};
const context=vm.createContext({document,add,navigator:{clipboard:{writeText:async text=>{context.lastCopied=text;}}},setTimeout:fn=>{mockTimers.push(fn);return mockTimers.length;},clearTimeout:()=>{},console});
vm.runInContext(appHelper+'\nthis.copyImagePrompt=copyImagePrompt;this.paintKristalImage=paintKristalImage;',context);
const copyBtn=new Element('button');copyBtn.textContent='Copier le prompt';
await context.copyImagePrompt(copyBtn,'Image conceptuelle sans style');
assert.equal(context.lastCopied,'Image conceptuelle sans style');
assert.equal(copyBtn.textContent,'✓ Prompt copié !');
assert.ok(copyBtn.classList.contains('is-copied'));
mockTimers.pop()();assert.equal(copyBtn.textContent,'Copier le prompt');
context.navigator.clipboard.writeText=async()=>{throw Error('blocked');};
await context.copyImagePrompt(copyBtn,'x');
assert.ok(copyBtn.classList.contains('copy-failed'));
assert.match(copyBtn.textContent,/Copie impossible/);

// Saving an image paints the right slot immediately with cache-busting.
const picture=new Element('div');const feedback=new Element('p');
context.paintKristalImage(picture,{url:'assets/kristals/qc-pri-ma-012/concept.webp',alt:'Un arbre'},'abcd1234',feedback);
const current=find(picture,e=>e.tagName==='img');
assert.equal(current.src,'/api/kristal-image/qc-pri-ma-012/concept.webp?v=abcd1234');
assert.equal(current.alt,'Un arbre');current.onload();
assert.match(feedback.textContent,/affichée immédiatement/);
context.paintKristalImage(picture,{url:null});
assert.match(find(picture,e=>e.className==='image-not-installed').textContent,/Aucune image/);

// Simulate the drag/select -> local preview -> upload -> in-place callback cycle.
const doc2=makeDocument();
const fetchCalls=[];const saved=[];const created=[];
const ctx2=vm.createContext({
 document:doc2,window:{},URL:{createObjectURL:(file)=>{created.push(file.name);return 'blob:ekole-example';},revokeObjectURL:()=>{}},
 fetch:async(url,options={})=>{fetchCalls.push([url,options]);if(url.includes('config'))return{ok:true,json:async()=>({csrf:'local-token'})};return{ok:true,json:async()=>({status:'installed',file_name:'concept.webp',public_url:'assets/kristals/qc-pri-ma-012/concept.webp',width:800,height:500,sha256:'abc123abc123abc123'})};},
 console,encodeURIComponent
});
vm.runInContext(fs.readFileSync(path.join(root,'enseignant-app/images-editor-v15.js'),'utf8'),ctx2);
const parent=new Element('main');const wrapper=ctx2.window.EkoleImagesV15.attach(parent,'qc-pri-ma-012','concept',false,(result,status)=>{saved.push(result);status.textContent='✓ Image affichée automatiquement';});
const input=find(wrapper,e=>e.tagName==='input' && e.type==='file');
const file={name:'illustration.png',size:1000,type:'image/png',arrayBuffer:async()=>new Uint8Array(1000).buffer};
input.files=[file];input.handlers.change();
const preview=find(wrapper,e=>e.className==='image-upload-preview');
assert.equal(preview.src,'blob:ekole-example');
preview.onload();assert.equal(preview.hidden,false);
const submit=find(wrapper,e=>e.tagName==='button');
assert.equal(submit.disabled,false);
await submit.handlers.click();
assert.equal(saved.length,1);
assert.equal(saved[0].file_name,'concept.webp');
assert.ok(parent.children.includes(wrapper),'Saving must not remove the editor');
assert.match(find(wrapper,e=>e.className==='image-upload-feedback').textContent,/affichée automatiquement/);
assert.equal(submit.disabled,true);
assert.equal(fetchCalls.filter(([u])=>u.includes('visual-upload')).length,1);
console.log('PASS v16 UI: copy feedback, errors, preview, cache-busted image, in-place upload');
