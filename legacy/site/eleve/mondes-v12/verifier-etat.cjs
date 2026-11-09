'use strict';

const {readFileSync} = require('node:fs');
const engine = require('./engine.js');
const {spec, state} = JSON.parse(readFileSync(0, 'utf8'));
engine.validateSpec(spec);
const p = spec.parameters;
const bounded = (value, min, max) => Number.isInteger(value) && value >= min && value <= max;
const distinct = (value, check, max) =>
 Array.isArray(value) && value.length <= max && new Set(value).size === value.length && value.every(check);
const object = value => value && typeof value === 'object' && !Array.isArray(value);
const entries = (value, check) => object(value) && Object.entries(value).every(check);
let valid = false;
if (object(state)) {
 switch (spec.type) {
  case 'representations':
   valid = ['surface', 'bande', 'collection'].every(key =>
    distinct(state[key], item => bounded(item, 0, p.parts - 1), p.parts));
   break;
  case 'repartition':
   valid = Array.isArray(state.bins) && state.bins.length === p.total &&
    state.bins.every(bin => bounded(bin, -1, p.bins - 1));
   break;
  case 'causalite': {
   const ids = p.events.map(event => event.id);
   valid = distinct(state.order, id => ids.includes(id), ids.length) && state.order.length === ids.length &&
    entries(state.links, ([key, value]) =>
     /^(0|[1-9][0-9]*)$/.test(key) && Number(key) < p.links.length && typeof value === 'boolean');
   break;
  }
  case 'preuves': {
   const ids = p.statements.map(row => row.id);
   valid = entries(state.classifications, ([id, kind]) => ids.includes(id) &&
    ['observation', 'interpretation'].includes(kind));
   break;
  }
  case 'expression':
   valid = distinct(state.selected, value => p.gestures.includes(value), p.gestures.length);
   break;
 }
}
if (!valid) throw new Error('État de manipulation invalide');
process.stdout.write(JSON.stringify(engine.evaluate(spec, state)));
