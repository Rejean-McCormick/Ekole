'use strict';

const COURSE = 'qc-pri-ma-009';
const LESSON = 'Sens et stratégies de la division';
const ACTIVITY = 'Les invitations de Mila';

function chapters(page, urls) {
  const heading = name => page.getByRole('heading', {name, exact: true}).first();
  const button = name => page.getByRole('button', {name, exact: true});
  const link = name => page.getByRole('link', {name, exact: true});
  const show = async locator => {
    await locator.waitFor();
    await locator.evaluate(element => element.scrollIntoView({block: 'center'}));
  };
  const text = name => page.getByText(name, {exact: true});
  const go = async (base, path) => {
    const response = await page.goto(new URL(path, base).href);
    if (!response?.ok()) throw new Error('Page locale indisponible.');
  };
  const pupil = path => go(urls.public, '/eleve/' + path);
  const course = () => pupil('?cours=' + COURSE + '&retour=annee-3');
  const teacherTab = async name => {
    await go(urls.teacher, '/');
    await button(name).click();
  };

  return [
    ['Bienvenue dans Ekole',
      'Voici une école primaire à explorer par année ou par matière. Suivons ensemble une notion de 3e année, de la leçon jusqu’à la rétroaction.',
      async () => {
        await pupil('');
        await show(page.getByRole('heading', {name: /Bienvenue dans/i}));
      }],
    ['Choisir une notion',
      'Les 202 cours du pack Québec sont répartis sur six années. L’élève retrouve une notion dans son parcours, avec son objectif et les ressources associées.',
      async () => {
        await link('Explorer la 3e année →').click();
        await show(heading('Toutes les matières'));
      }],
    ['Un scénario donne du sens',
      'La banque Kontexte propose des situations réutilisables. Dans la trame de la fête commune, Mila doit préparer des invitations. Ce problème donne un usage concret à la division.',
      async () => {
        await go(urls.teacher, urls.open);
        await button('Scénarios Kontexte').click();
        await page.getByLabel('Chercher par titre, famille ou production').fill('fête commune');
        await show(text('La fête commune'));
      }],
    ['Préparer la leçon',
      'Dans l’atelier, les leçons candidates sont déjà rédigées en six étapes. Le Kristal fournit l’objectif et les repères. Le texte destiné à l’élève se travaille dans le brouillon.',
      async () => {
        await button('Leçons structurées').click();
        const selectors = page.locator('#editor > .b3-toolbar').first().locator('select');
        await selectors.nth(0).selectOption('annee-3');
        await selectors.nth(1).selectOption(COURSE);
        await button('Préparer les brouillons du parcours').click();
        await page.getByText(/brouillons créés/).waitFor();
        await text('Repères privés de rédaction').click();
        await show(heading(LESSON));
      }],
    ['Relire dans la vue élève',
      'La revue commence ici. On vérifie si les consignes sont claires, si les exemples sont justes et si l’activité permet à l’élève de montrer ce qu’il a compris.',
      async () => {
        await text('Aperçu élève privé du brouillon enregistré').click();
        await show(page.locator('#editor details[open] h4').first());
      }],
    ['De la revue à la diffusion',
      'Dans cette démo, j’enregistre une revue fictive et je sélectionne une seule leçon à diffuser. Sur une installation réelle, la personne qui relit confirme elle-même la révision.',
      async () => {
        await page.getByLabel('Nom du relecteur', {exact: true}).fill('Visite Ekole — démonstration');
        await page.getByRole('checkbox', {name: /J’ai relu la totalité/}).check();
        await button('Enregistrer la revue').click();
        await text('Diffuser un lot de leçons relues').click();
        await page.getByRole('checkbox', {name: LESSON, exact: true}).check();
        await button('Diffuser les leçons cochées dans l’espace Élève local').click();
        await show(page.getByText(/disponible\(s\) dans l’espace Élève local/));
      }],
    ['L’élève voit la leçon',
      'La leçon apparaît maintenant dans l’espace Élève de la démo. L’élève avance à son rythme. Les repères de rédaction et les corrigés restent dans l’espace enseignant.',
      async () => {
        await course();
        await page.getByRole('link', {name: /Étape suivante/}).click();
        await show(text('Étape 2 sur 6'));
      }],
    ['Pratiquer avec Mila',
      'Une feuille donne deux invitations. En ajoutant des feuilles à l’écran, l’élève voit que six invitations occupent trois feuilles, puis compare ce total au stock.',
      async () => {
        await link('Activité pilote').click();
        await page.getByRole('navigation', {name: 'Activités', exact: true}).getByRole('link', {name: ACTIVITY, exact: true}).click();
        const add = button('Ajouter une feuille');
        for (let index = 0; index < 3; index++) await add.click();
        await show(text('6 sur 6 invitations placées'));
      }],
    ['Essayer un autre exemple',
      'Inkuisite réutilise le même moteur de questions pour la pratique et le bilan. Ici, l’élève change de nombres et explique pourquoi une feuille de plus est nécessaire.',
      async () => {
        const label = 'Je vérifie avec un autre exemple';
        await link(label).click();
        await button(label).click();
        const form = page.locator('.activity-form');
        await form.getByLabel('Combien de feuilles Mila doit-elle utiliser ?', {exact: true}).fill('5');
        await form.getByLabel('Combien de feuilles lui manquent ?', {exact: true}).fill('2');
        await form.getByLabel('Explique pourquoi il faut une feuille pour un groupe incomplet.', {exact: true}).fill('Quatre feuilles donnent huit invitations. La neuvième a besoin de sa propre feuille.');
        await show(form.getByRole('button', {name: 'Remettre'}));
      }],
    ['Une justification attend une personne',
      'Les réponses numériques peuvent être vérifiées par le moteur. La justification écrite attend une lecture humaine, et la rétroaction du bilan reste privée entre-temps.',
      async () => {
        await button('Remettre').click();
        await show(text('La rétroaction sera disponible après la revue.'));
      }],
    ['L’enseignant lit la réponse',
      'Dans l’atelier Inkuisite, la personne qui corrige voit la réponse, le critère et le résultat privé. Elle peut expliquer sa décision et indiquer la prochaine étape.',
      async () => {
        await teacherTab('Revue Inkuisite');
        await page.locator('#editor .b3-toolbar button').first().click();
        await show(text('Résultat privé'));
      }],
    ['Retourner une rétroaction à l’élève',
      'La rétroaction revient dans l’activité après la correction et la diffusion du résultat. L’élève retrouve une explication et un conseil pour son prochain essai.',
      async () => {
        const reviewer = page.getByLabel('Nom du relecteur', {exact: true});
        await reviewer.fill('Visite Ekole — démonstration');
        await page.getByRole('spinbutton').fill('1');
        await page.getByLabel('Motif de la décision', {exact: true}).fill('La réponse explique le groupe incomplet.');
        await page.getByLabel('Observation', {exact: true}).fill('La neuvième invitation nécessite une feuille de plus.');
        await page.getByLabel('Rétroaction à l’élève', {exact: true}).fill('Ton explication relie la neuvième invitation à la cinquième feuille.');
        await page.getByLabel('Prochaine étape', {exact: true}).fill('Essaie maintenant avec onze invitations.');
        await button('Enregistrer la revue').click();
        await button('Diffuser le résultat').waitFor();
        await reviewer.fill('Visite Ekole — démonstration');
        await button('Diffuser le résultat').click();
        await text('Résultat diffusé').waitFor();
        await pupil('?cours=' + COURSE + '&vue=activite&activite=invitations-mila&mode=bilan');
        await show(text('Ton explication relie la neuvième invitation à la cinquième feuille.'));
      }],
    ['Partager une fiche dans une autre langue',
      'Le scénario et l’objectif restent les mêmes. Cette activité possède déjà une version anglaise. Spek en produit une fiche à partir du même contenu structuré.',
      async () => {
        await pupil('?cours=' + COURSE + '&vue=activite&activite=invitations-mila');
        await link('English').click();
        await link('Spek page').click();
        await show(page.getByRole('heading', {name: /Mila.s invitations/i}).first());
      }],
    ['Explorer les liens entre notions',
      'La carte Konstellation-Light permet de repartir d’une notion et d’explorer ses liens avec les autres. Pour un collaborateur, c’est aussi une façon de repérer les notions à relier ou à enrichir.',
      async () => {
        await course();
        await link('Carte des liens').click();
        await link('Explorer la carte dans Konstellation').click();
        await page.locator('#visual svg').first().waitFor();
        await show(page.locator('#panel-title'));
      }],
    ['Manipuler dans un micro-monde',
      'Les micro-mondes proposent une autre forme d’entraînement. L’élève construit une réponse avec des objets et peut vérifier son essai sur-le-champ.',
      async () => {
        await pupil('mondes-v12/');
        await heading('Mes petits mondes').waitFor();
        await page.locator('#contenu .catalogue a').first().click();
        await show(heading('À toi de manipuler'));
      }],
    ['Les images dans le flux de travail',
      'L’atelier donne accès aux emplacements d’illustrations, aux prompts des Kristals et à l’album. Les images préparées dans les outils de création sont importées puis vérifiées dans Ekole.',
      async () => {
        await go(urls.teacher, '/');
        await page.locator('#cours').selectOption(COURSE);
        await heading(LESSON).waitFor();
        await button('Illustrations et prompts').click();
        await show(heading('Illustrations et prompts'));
      }],
    ['Choisir un premier chantier ensemble',
      'Le tableau de couverture permet de repérer les leçons et activités disponibles. Une collaboration peut commencer avec une matière, quelques leçons à relire et un scénario à adapter.',
      async () => {
        await teacherTab('Couverture Québec');
        await page.locator('#editor').getByText(/202 cours · /).waitFor();
        await show(heading('Couverture du corpus Québec'));
      }],
  ];
}

module.exports = {chapters};
