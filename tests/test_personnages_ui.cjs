// Vérifie l'UI client : 76 compagnons-rôles, 8 poses, dégradation sûre sans PNG.
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
const storage=new Map();
const context={document:{createElement:t=>new Element(t),querySelector:()=>null},
 window:{sessionStorage:{getItem:k=>storage.get(k)||null,setItem:(k,v)=>storage.set(k,v),removeItem:k=>storage.delete(k)}},
 location:{pathname:'/eleve/',hostname:'localhost',search:''},URLSearchParams,URL,console};
vm.createContext(context);
vm.runInContext(fs.readFileSync(path.join(root,'site/personnages.js'),'utf8'),context);
const cat=JSON.parse(fs.readFileSync(path.join(root,'../ekole-quebec/personnages/catalogue.json'),'utf8'));
assert.equal(cat.compagnons.length,380);assert.equal(cat.assets.length,3040);
const api=context.window.EkolePersonnages;api.configure(cat);
let host=new Element('div'),comp=cat.compagnons.find(c=>c.id==='photographe');
let portrait=api.companion(host,comp,3,'ecouter');
assert.equal(portrait.children.length,1,'Sans image, repli par initiale');
const neutral=cat.assets.find(a=>a.id==='role-photographe');neutral.disponible=true;neutral.url='/api/personnages/image/'+neutral.id;
api.configure(cat);host=new Element('div');portrait=api.companion(host,comp,3,'celebrer');
assert.equal(portrait.children[1].src,neutral.url,'Repli sur portrait neutre quand pose absente');
portrait.children[1].listeners.load();assert.equal(portrait.children[0].hidden,true);
portrait.children[1].listeners.error();assert.equal(portrait.children.length,1);
const fille=cat.compagnons.find(c=>c.id==='photographe-fille');
const neutreFille=cat.assets.find(a=>a.id==='role-photographe-fille');
neutreFille.disponible=true;neutreFille.url='/api/personnages/image/'+neutreFille.id;
api.configure(cat);host=new Element('div');
const visageFille=api.companion(host,fille,3,'ecouter');
assert.equal(visageFille.children[1].src,neutreFille.url,'La fille utilise son propre maître et non le garçon');
const pose=cat.assets.find(a=>a.id==='compagnon-photographe-pose-reflechir');pose.disponible=true;pose.url='/api/personnages/image/'+pose.id;
api.configure(cat);portrait=api.companion(host,comp,3,'reflechir');assert.equal(portrait.children[1].src,pose.url);
pose.url='https://external.invalid/image.png';api.configure(cat);portrait=api.companion(host,comp,3,'reflechir');
assert.equal(portrait.children[1].src,neutral.url,'Une URL externe n’est pas acceptée');
const app=fs.readFileSync(path.join(root,'site/app.js'),'utf8').replace(/main\(\);\s*$/,'');
vm.runInContext(app+`\npack={id:'primaire-qc',personnages_compagnons_actifs:true};COMPAGNON_THEMES=window.EkolePersonnages.catalogue.compagnons;globalThis.check={lireCompagnon,enregistrerCompagnon,demoCompagnonActif};`,context);
const check=context.check;
for(const c of cat.compagnons){check.enregistrerCompagnon(c.id,4);assert.equal(check.lireCompagnon().id,c.id);}
for(const [alias,current] of Object.entries(cat.anciens_choix)){
 storage.set('ekole-demo-compagnon-choice-v2',JSON.stringify({theme:alias,annee:3}));assert.equal(check.lireCompagnon().id,current);
}
context.location.hostname='example.com';assert.equal(check.demoCompagnonActif(),true,'Activation explicite du pack hors localhost');
vm.runInContext('pack.personnages_compagnons_actifs=false',context);assert.equal(check.demoCompagnonActif(),false);
api.configure(null);assert.equal(api.catalogue.compagnons.length,0);
console.log('76 compagnons × 8 poses : repli neutre, URL sûre, choix facultatif en session et activation pack OK.');
