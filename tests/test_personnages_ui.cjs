// Tests DOM minimaux sans dépendance ni navigateur installé.
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..');
class Element{
 constructor(tag){this.tagName=tag;this.children=[];this.dataset={};this.listeners={};this.hidden=false;}
 append(node){if(node.parentElement)node.remove();this.children.push(node);node.parentElement=this;}
 prepend(node){if(node.parentElement)node.remove();this.children.unshift(node);node.parentElement=this;}
 remove(){const p=this.parentElement;if(p)p.children.splice(p.children.indexOf(this),1);this.parentElement=null;}
 setAttribute(k,v){this[k]=v;}
 addEventListener(k,fn){this.listeners[k]=fn;}
}
const storage=new Map();storage.set('ekole-demo-compagnon-active-v2','1');
const context={document:{createElement:t=>new Element(t),querySelector:()=>null},window:{sessionStorage:{getItem:k=>storage.get(k)||null,setItem:(k,v)=>storage.set(k,v),removeItem:k=>storage.delete(k)}},location:{pathname:'/eleve/',hostname:'localhost',search:''},URLSearchParams,URL,console};
vm.createContext(context);
vm.runInContext(fs.readFileSync(path.join(root,'site/personnages.js'),'utf8'),context);
const catalogue=JSON.parse(fs.readFileSync(path.join(root,'../ekole-quebec/personnages/catalogue.json'),'utf8'));
const api=context.window.EkolePersonnages;
api.configure(catalogue);
let host=new Element('div'),c=catalogue.compagnons[0];
let portrait=api.companion(host,c,3);
assert.equal(portrait.children.length,1,'Aucune requête image quand le visuel est absent');
const year=catalogue.assets.find(a=>a.id==='compagnon-mila-annee-03');year.disponible=true;year.url='/api/personnages/image/'+year.id;
api.configure(catalogue);host=new Element('div');portrait=api.companion(host,c,3,'celebrer');
assert.equal(portrait.children[1].src,year.url,'Repli sur le bon niveau si pose absente');
portrait.children[1].listeners.load();assert.equal(portrait.children[0].hidden,true);
portrait.children[1].listeners.error();assert.equal(portrait.children.length,1);assert.equal(portrait.children[0].hidden,false);
const pose=catalogue.assets.find(a=>a.id==='compagnon-mila-pose-celebrer');pose.disponible=true;pose.url='/api/personnages/image/'+pose.id;
api.configure(catalogue);portrait=api.companion(host,c,3,'celebrer');assert.equal(portrait.children[1].src,pose.url);
year.url='https://external.invalid/image.png';api.configure(catalogue);portrait=api.companion(host,c,3);assert.equal(portrait.children.length,1);
const app=fs.readFileSync(path.join(root,'site/app.js'),'utf8').replace(/main\(\);\s*$/,'');
vm.runInContext(app+`\npack={id:'primaire-qc'};COMPAGNON_THEMES=window.EkolePersonnages.catalogue.compagnons;globalThis.check={lireCompagnon,enregistrerCompagnon,demoCompagnonActif};`,context);
const checks=context.check;
for(const [old,current] of Object.entries(catalogue.anciens_choix)){
 storage.set('ekole-demo-compagnon-choice-v2',JSON.stringify({theme:old,annee:3}));assert.equal(checks.lireCompagnon().id,current);
}
for(const comp of catalogue.compagnons){checks.enregistrerCompagnon(comp.id,4);assert.equal(checks.lireCompagnon().id,comp.id);}
checks.enregistrerCompagnon('intrus',3);assert.equal(checks.lireCompagnon().id,'extraterrestre');
context.location.hostname='example.com';assert.equal(checks.demoCompagnonActif(),false);
api.configure(null);assert.equal(api.catalogue.compagnons.length,0);
console.log('UI personnages : repli, erreur image, poses, niveaux, 5 choix et migration des 3 anciens choix OK.');
