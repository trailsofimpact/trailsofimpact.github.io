const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch();
  const errs = [];
  const d = await browser.newContext({ viewport: {width:1440, height:900} });
  let p = await d.newPage(); p.on('pageerror', e => errs.push(e.message));
  await p.goto('http://localhost:8765/rejoindre.html', { waitUntil: 'networkidle' }); await p.waitForTimeout(800);
  await p.screenshot({ path: 'shots/fix-rej-d.png', clip: {x:0,y:0,width:1440,height:760} });
  // formulaire
  await p.goto('http://localhost:8765/rejoindre.html#prevenir', { waitUntil: 'networkidle' });
  await p.click('a[data-pick="dons"]');
  await p.fill('#f-nom', 'Marie Exemple'); await p.fill('#f-email', 'marie@exemple.ch');
  await p.fill('#f-message', 'Bonjour, je souhaite être prévenue à l’ouverture des dons.');
  await p.click('#contact-form button[type=submit]'); await p.waitForTimeout(400);
  const res = await p.evaluate(() => ({ hidden: document.getElementById('form-result').hidden, pre: document.getElementById('msg-preview').textContent, href: document.querySelector('[data-mailto]').getAttribute('href').slice(0,80) }));
  console.log(JSON.stringify(res));
  await p.goto('http://localhost:8765/index.html', { waitUntil: 'networkidle' }); await p.waitForTimeout(3500);
  const mc = await p.$('.mini-coupe'); await mc.screenshot({ path: 'shots/fix-minicoupe.png' });
  const hm = await p.$('.hero__map'); await hm.screenshot({ path: 'shots/fix-heromap.png' });
  // liens internes : tous résolus ?
  const links = await p.evaluate(() => [...new Set([...document.querySelectorAll('a[href]')].map(a => a.getAttribute('href')))]);
  console.log(links.join(' '));
  const m = await browser.newContext({ viewport: {width:390, height:844}, deviceScaleFactor: 1 });
  p = await m.newPage(); p.on('pageerror', e => errs.push(e.message));
  await p.goto('http://localhost:8765/rejoindre.html', { waitUntil: 'networkidle' }); await p.waitForTimeout(800);
  await p.screenshot({ path: 'shots/fix-rej-m.png', fullPage: false });
  await p.click('[data-menu-open]'); await p.waitForTimeout(300);
  await p.screenshot({ path: 'shots/fix-menu-m.png' });
  console.log(errs.length ? errs.join('\n') : 'no page errors');
  await browser.close();
})();
