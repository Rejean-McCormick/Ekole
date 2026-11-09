'use strict';

const {spawn} = require('node:child_process');
const {once} = require('node:events');
const {existsSync} = require('node:fs');
const {resolve} = require('node:path');
const {createInterface} = require('node:readline');
const {chapters} = require('./chapitres.cjs');

function startServer(engine, content) {
  const python = process.env.EKOLE_PYTHON || (process.platform === 'win32' ? 'python' : 'python3');
  const child = spawn(python, ['-B', resolve(__dirname, 'serveur-demo.py'), engine, content],
    {stdio: ['pipe', 'pipe', 'pipe'], windowsHide: true,
      env: {...process.env, PYTHONIOENCODING: 'utf-8'}});
  let error = '';
  child.stderr.setEncoding('utf8').on('data', part => { error += part; });
  child.stdin.on('error', () => {});
  const lines = createInterface({input: child.stdout});
  const ready = new Promise((ok, fail) => {
    child.once('error', fail);
    child.once('close', code => fail(new Error(error.trim() || 'Serveur de démonstration arrêté (' + code + ').')));
    lines.on('line', line => {
      try {
        const message = JSON.parse(line);
        if (message.status) console.log('[Ekole] ' + message.status);
        else ok(message);
      } catch (_) { fail(new Error('Réponse inattendue du serveur Ekole.')); }
    });
  });
  async function stop() {
    if (child.exitCode !== null || child.signalCode !== null || !child.pid) return;
    const closed = once(child, 'close');
    child.stdin.end();
    await closed;
  }
  return {ready, stop};
}

async function caption(page, slide) {
  await page.evaluate(({number, total, title, subtitle}) => {
    document.querySelector('[data-ekole-visite]')?.remove();
    const host = document.createElement('aside');
    host.dataset.ekoleVisite = '';
    host.setAttribute('aria-label', 'Visite guidée Ekole');
    const shadow = host.attachShadow({mode: 'open'});
    const style = document.createElement('style');
    style.textContent = `
      :host { position: fixed; z-index: 2147483647; bottom: 14px; inset-inline: 12px;
        margin-inline: auto; max-width: 940px; color: #fff; }
      section { box-sizing: border-box; display: grid; grid-template-columns: 1fr auto; gap: 6px 22px;
        align-items: end; background: #13243a; border: 1px solid #5c7d99; border-left: 5px solid #93e8c4;
        padding: 14px 18px; border-radius: 12px; box-shadow: 0 9px 30px #0b182f44;
        font: 16px/1.45 system-ui, sans-serif; }
      header, p { margin: 0; } small { display: block; color: #aeeccd; margin-bottom: 2px;
        font-size: 12px; letter-spacing: .12em; text-transform: uppercase; }
      strong { display: block; font-size: 20px; } p { color: #f2f6fd; margin-top: 4px; }
      button { color: #102035; background: #c2f4dc; border: 0; border-radius: 8px; cursor: pointer;
        padding: 9px 12px; font: 650 14px system-ui, sans-serif; white-space: nowrap; }
      button:focus-visible { outline: 2px solid white; outline-offset: 3px; }
      button:disabled { opacity: .7; cursor: wait; }
      @media (max-width: 600px) { section { grid-template-columns: 1fr; } button { justify-self: end; } }
    `;
    const panel = document.createElement('section');
    const body = document.createElement('header');
    body.setAttribute('aria-live', 'polite');
    const counter = document.createElement('small');
    counter.textContent = 'Visite Ekole · ' + number + ' / ' + total;
    const name = document.createElement('strong');
    name.textContent = title;
    const line = document.createElement('p');
    line.textContent = subtitle;
    body.append(counter, name, line);
    const next = document.createElement('button');
    next.type = 'button';
    next.textContent = number === total ? 'Espace · Terminer' : 'Espace · Suivant';
    next.onclick = () => {
      if (next.disabled) return;
      next.disabled = true;
      window.ekoleVisiteSuivante(number);
    };
    panel.append(body, next);
    shadow.append(style, panel);
    document.body.append(host);
    next.focus({preventScroll: true});
  }, slide);
}

async function main() {
  const args = process.argv.slice(2);
  if (args.includes('--aide') || args.includes('--help')) {
    console.log('node visite.cjs [--verifier]\nEKOLE_MOTEUR, EKOLE_CONTENU et EKOLE_PYTHON sont facultatifs.');
    return;
  }
  if (args.some(arg => arg !== '--verifier')) throw new Error('Option inconnue. Utilise --aide.');
  const verify = args.includes('--verifier');
  const parent = resolve(__dirname, '..');
  const nested = resolve(parent, 'ekole');
  const engine = resolve(process.env.EKOLE_MOTEUR ||
    (!existsSync(resolve(parent, 'activite_locale.py')) && existsSync(resolve(nested, 'activite_locale.py'))
      ? nested : parent));
  const content = resolve(process.env.EKOLE_CONTENU || resolve(engine, '../ekole-quebec'));
  const launch = {headless: verify};
  if (process.env.EKOLE_CHROMIUM) launch.executablePath = process.env.EKOLE_CHROMIUM;

  let playwright;
  try {
    playwright = require('playwright');
  } catch (error) {
    if (error.code !== 'MODULE_NOT_FOUND') throw error;
    throw new Error('Playwright est manquant. Ouvre LANCER_VISITE.cmd sous Windows, ou exécute npm install dans visite-client.');
  }
  const server = startServer(engine, content);
  let browser;
  const closeOnInterrupt = () => { void browser?.close(); };
  process.on('SIGINT', closeOnInterrupt);
  process.on('SIGTERM', closeOnInterrupt);
  try {
    const urls = await server.ready;
    browser = await playwright.chromium.launch(launch);
    const viewport = verify ? {width: 1440, height: 940} : null;
    const context = await browser.newContext({viewport, locale: 'fr-CA'});
    let advance;
    await context.exposeBinding('ekoleVisiteSuivante', ({page: source}, number) => {
      if (source === page && advance?.number === number) advance.resolve();
    });
    await context.addInitScript(() => {
      window.addEventListener('keydown', event => {
        if (event.code !== 'Space' || event.repeat || event.altKey || event.ctrlKey || event.metaKey) return;
        if (event.composedPath().some(node => node instanceof HTMLElement &&
          (node.isContentEditable || node.matches('input:not([type=checkbox]):not([type=radio]), textarea, select')))) return;
        const next = document.querySelector('[data-ekole-visite]')?.shadowRoot?.querySelector('button');
        if (next) { event.preventDefault(); next.click(); }
      }, true);
    });
    const page = await context.newPage();
    page.setDefaultTimeout(10000);
    const closed = once(page, 'close');
    page.on('dialog', async dialog => {
      if (dialog.type() === 'confirm' && /^Diffuser localement 1 leçon/.test(dialog.message())) await dialog.accept();
      else await dialog.dismiss();
    });
    const tour = chapters(page, urls);
    for (const [index, [title, subtitle, navigate]] of tour.entries()) {
      const number = index + 1;
      try {
        await page.evaluate(() => document.querySelector('[data-ekole-visite]')?.remove());
        await navigate();
        const next = new Promise(resolve => { advance = {number, resolve}; });
        await caption(page, {number, total: tour.length, title, subtitle});
        console.log(number + '/' + tour.length + ' · ' + title);
        if (verify) {
          await page.keyboard.press('Space');
          await page.waitForFunction(() => document.querySelector('[data-ekole-visite]')
            ?.shadowRoot.querySelector('button').disabled);
        }
        if (await Promise.race([next.then(() => true), closed.then(() => false)]) === false) return;
        advance = undefined;
      } catch (error) {
        if (page.isClosed() && !verify) return;
        throw new Error('Étape ' + number + ' (« ' + title + ' ») : ' + error.message);
      }
    }
    console.log('Visite terminée.');
  } finally {
    process.off('SIGINT', closeOnInterrupt);
    process.off('SIGTERM', closeOnInterrupt);
    try {
      await browser?.close();
    } finally {
      await server.stop();
    }
  }
}

main().catch(error => {
  console.error(error.message.replace(/([?&]key=)[A-Za-z0-9_-]+/g, '$1[masquée]'));
  process.exitCode = 1;
});
