/** Contrats synthétiques existants. Aucun --apply, aucune connexion, aucun World live. */
import fs from 'node:fs';
import {pathToFileURL} from 'node:url';
import {resolve} from 'node:path';
const [orgoRoot, worldsRoot, payloadPath]=process.argv.slice(2);
if(!orgoRoot || !worldsRoot || !payloadPath)throw Error('Usage: node verifier_ecosysteme_tandem.mjs ORGO WORLDS PLANS');
const {validateScenario}=await import(pathToFileURL(resolve(orgoRoot,'tools/scenario-injector/lib.mjs')).href);
const {reviewSyntheticWorld}=await import(pathToFileURL(resolve(worldsRoot,'scripts/tandem-education/scope-review.mjs')).href);
const plans=JSON.parse(fs.readFileSync(payloadPath,'utf8'));
if(!Array.isArray(plans) || plans.length<1)throw Error('Plans vides');
let count=0;
for(const row of plans){
  const result=validateScenario(row.scenario_fixture);
  if(!result.ok)throw Error('Scenario review Orgo invalide '+row.mission_id+': '+result.errors.join('; '));
  if(row.scenario_fixture.operations.length!==2 ||
     row.scenario_fixture.operations[1].input.metadata.pending_workflow_authoring!==true)
    throw Error('Preview Orgo doit rester une tache de preparation uniquement');
  if (!row.intent) continue;
  const intent=row.intent;
  const context={format:'orgo-worlds.synthetic-context/1.0',synthetic:true,
    tenant_id:intent.tenant_id,world_id:intent.world_id,world_release_id:intent.world_release_id,
    world_status:'active',release_status:'current',classroom_ref:'classe-fictive'};
  const witness=reviewSyntheticWorld(intent,context,Buffer.from(JSON.stringify(intent),'utf8'));
  if(!witness.scope_consistent || witness.dispatch_allowed!==false || witness.may_publish_to_child!==false)
    throw Error('Preuve de scope hors contrat');
  count++;
}
// Exigence supplémentaire : la fête passe l'injecteur officiel pour revue seulement.
const packFile=resolve(worldsRoot,'world-packs/ekole-fete-sorciere/scenarios/REVUE.scenario.json');
const review=JSON.parse(fs.readFileSync(packFile,'utf8'));
const validReview=validateScenario(review);
if(!validReview.ok)throw Error('World pack de revue invalide : '+validReview.errors.join('; '));
const workflow=review.operations.find(o=>o.op==='publish_workflow');
const rule=workflow?.content?.rules?.[0];
const steps=rule?.actions?.filter(a=>a.type==='CREATE_TASK') ?? [];
if(steps.length!==11 || steps.some(a=>a.input.metadata.pending_workflow_review!==true ||
  a.input.metadata.private_fragments_embedded!==false || a.input.metadata.synthetic!==true))
  throw Error('World pack ne doit contenir que onze tâches de revue synthétiques');
if(review.operations.some(o=>o.op==='create_task' || o.op==='comment_task'))
  throw Error('World pack ne peut attribuer des tâches à des élèves');
process.stdout.write(JSON.stringify({world_contracts_checked:count,orgo_review_fixtures_checked:plans.length,
  world_pack_review_steps:steps.length}));
