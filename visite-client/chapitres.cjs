'use strict';

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
  const course = id => pupil('?cours=' + id);
  const themes = () => page.locator('#editor fieldset');
  const picker = () => page.locator('.ekole-univers-card select');
  const choose = async (key, name) => {
    await picker().selectOption(key);
    await heading(name).waitFor();
  };

  return [
    ['Une école, plusieurs univers',
      'Les cours du primaire restent organisés par année et par matière. Nous allons voir comment une classe peut les traverser avec le jardinage ou le jazz.',
      async () => {
        await pupil('');
        await show(page.getByRole('heading', {name: /Bienvenue dans/i}));
      }],
    ['L’enseignant choisit à l’échelle de la classe',
      'Voici la palette de thèmes déjà préparée. L’enseignant ouvre les univers qui parlent à ses élèves et choisit celui qui les accueille.',
      async () => {
        await go(urls.teacher, urls.open);
        await heading('Univers de la classe').waitFor();
        await themes().getByRole('checkbox', {name: /^Les jardins du village/}).check();
        await themes().getByRole('checkbox', {name: /^Le festival de jazz/}).check();
        await show(heading('Univers de la classe'));
      }],
    ['Jardinage au printemps, palette pastel',
      'Je choisis le jardinage comme point de départ et le pastel comme style de classe. Le professeur applique ces choix en une fois.',
      async () => {
        await page.locator('#editor select').nth(0).selectOption('jardinage');
        await page.locator('#editor select').nth(1).selectOption('pastel');
        await button('Appliquer à la classe').click();
        await show(text('Choix de classe appliqués.'));
      }],
    ['La contribution locale passe par l’univers',
      'L’enseignant voit des situations pour plusieurs matières et un prompt adapté au pastel. Il peut approuver une illustration pour cet univers et cette palette.',
      async () => {
        await page.locator('#editor textarea').waitFor();
        await page.waitForFunction(() => document.querySelector('#editor textarea')?.value.includes('Aplats pastel'));
        await show(heading('Illustration et aperçu d’un univers'));
      }],
    ['Chaque élève peut choisir son compagnon',
      'L’élève retrouve les thèmes proposés pour sa classe. Il peut aussi choisir un compagnon qui l’accompagnera pendant cette session.',
      async () => {
        await pupil('?page=parcours');
        await show(heading('Choisis ton univers'));
        await page.getByRole('button', {name: /Mila/}).click();
        await show(heading('Choisis un compagnon (facultatif)'));
      }],
    ['Le jardin devient un contexte de travail',
      'La notion de division vient du programme. Dans cet univers, l’élève prépare des sachets de semences pour les équipes du jardin.',
      async () => {
        await course('qc-pri-ma-009');
        await show(heading('Les jardins du village'));
      }],
    ['Manipuler les groupes',
      'L’élève remplit des contenants à l’écran. Les quantités et les questions ont été calculées pour cet univers et le bilan passe par Inkuisite.',
      async () => {
        await link('Jouer dans cet univers').click();
        await button('Ajouter un contenant').click();
        await button('Ajouter un contenant').click();
        await show(text('4 objets sur 6 rangés'));
      }],
    ['Le même jardin en sciences',
      'Cette fois, les semences et les bacs servent à distinguer une observation d’une explication. L’élève essaie plusieurs choix avant de justifier sa démarche.',
      async () => {
        await course('qc-pri-st-001');
        await link('Jouer dans cet univers').click();
        await button('Je pratique').click();
        await page.getByRole('checkbox', {name: 'Le plant près de la clôture mesure 5 cm.'}).check();
        await page.getByRole('checkbox', {name: 'Le plant près de l’allée mesure 8 cm.'}).check();
        await button('Remettre').click();
        await show(text('Tes choix correspondent à la question.'));
      }],
    ['L’élève passe au jazz',
      'Parmi les univers que son professeur a ouverts, l’élève choisit le jazz. Le style de classe reste pastel et le contenu suit le nouvel univers.',
      async () => {
        await course('qc-pri-fr-008');
        await choose('jazz', 'Le festival de jazz');
        await page.waitForFunction(() => document.documentElement.dataset.ekoleStyle === 'pastel');
        await show(heading('Le festival de jazz'));
      }],
    ['Un autre univers, une autre activité',
      'En lecture, l’élève doit remettre dans l’ordre les étapes de préparation du programme du festival. Le contenu du récit change avec l’univers.',
      async () => {
        await link('Jouer dans cet univers').click();
        await button('Je pratique').click();
        await show(text('Quel ordre correspond au récit ?'));
      }],
    ['Spek projette le cours dans son univers',
      'La fiche Spek réunit l’objectif du cours et le contexte choisi. La même palette s’applique aux fiches, avec l’illustration approuvée quand elle est disponible.',
      async () => {
        await course('qc-pri-fr-008');
        await link('Fiche Spek de ce cours dans cet univers').click();
        await show(heading('Le festival de jazz'));
      }],
    ['L’atelier d’exercices reste disponible',
      'Pour aller plus loin, un enseignant peut toujours retoucher une leçon ou préparer une question. Il peut déjà proposer un univers à toute sa classe depuis un seul écran.',
      async () => {
        await go(urls.teacher, '/');
        await button('Banques de questions').click();
        await show(heading('Banques de questions du corpus'));
      }],
  ];
}

module.exports = {chapters};
