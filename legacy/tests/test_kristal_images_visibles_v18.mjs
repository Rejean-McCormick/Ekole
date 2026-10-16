// Verification comportementale du raccordement JSON -> image -> fiche Eleve.
import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import { fileURLToPath } from 'node:url';

const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const source=fs.readFileSync(path.join(ROOT,'site/eleve/app.js'),'utf8');
const first=source.indexOf('function kristalVisual(');
const last=source.indexOf('function courseTitle(',first);
assert(first!==-1 && last>first,'Fonction de rendu introuvable');

function node(tag,kind='',content=''){
 return {
  tag,kind,content,children:[],hidden:false,isConnected:true,
  dataset:{},src:'',append(child){this.children.push(child);child.isConnected=true;}
 };
}
const rootId='qc-pri-ma-012';
const item={slot:'concept',placement:'decouvrir',alt:'Fractions en parts égales',url:'assets/kristals/qc-pri-ma-012/concept.webp',revision:'beefabcdef123456'};
const parent=node('section');
const course={visuels:[item]};
const sandbox={
 STATE:{kristalVisuals:new Map([[rootId,course]])},
 child(parent,tag,kind='',text=''){const e=node(tag,kind,text);parent.append(e);return e;},
 el:node
};
vm.runInNewContext(source.slice(first,last)+'\nthis.draw=kristalVisual;',sandbox,{timeout:1000});
assert.equal(sandbox.draw(parent,rootId,'decouvrir'),true);
const fig=parent.children[0];
assert.equal(fig.children.length,1,'Avant la charge, seule la description doit etre visible');
assert.equal(fig.children[0].hidden,false);
const fn=sandbox.draw; // Capturer l'image en reproduisant le constructeur el
let lastPic;
sandbox.el=(tag,kind)=>{lastPic=node(tag,kind);return lastPic;};
const parent2=node('section');
assert.equal(fn(parent2,rootId,'decouvrir'),true);
assert.equal(lastPic.loading,'eager','Une image en attente ne peut pas etre lazy et hidden');
assert.match(lastPic.src,/concept\.webp\?v=beefabcdef123456$/);
const section=parent2.children[0];
assert.equal(section.children.length,1);
lastPic.onload();
assert.equal(section.children.length,2,'Image chargee doit etre ajoutee');
assert.equal(section.children[0].hidden,true,'Description doit disparaitre apres chargement');
assert.equal(section.children[1],lastPic);
// Erreur reseau: garder uniquement la description, sans afficher une image vide.
const parent3=node('section');
fn(parent3,rootId,'decouvrir');
lastPic.onerror();
assert.equal(parent3.children[0].children.length,1);
assert.equal(parent3.children[0].children[0].hidden,false);
// La retrocompatibilite des registres existants sans revision est conservee.
course.visuels=[{...item,revision:null}];
const parent4=node('section');
fn(parent4,rootId,'decouvrir');
assert.equal(lastPic.src,item.url);
// Description lorsque aucun fichier n'est declare.
course.visuels=[{...item,url:null,revision:null}];
const parent5=node('section');
fn(parent5,rootId,'decouvrir');
assert.equal(parent5.children[0].children.length,1);
console.log('OK v18 : image chargee, cache, erreur, registre ancien et absence de fichier');
