const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch();
  const d = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const p = await d.newPage();
  await p.goto('http://localhost:8765/index.html', { waitUntil: 'networkidle' }); await p.waitForTimeout(1500);
  await p.screenshot({ path: 'shots/v2b-hero.png' });
  const t = await p.evaluate(() => document.querySelector('.trace').getBoundingClientRect().top + scrollY - 72);
  await p.evaluate(y => window.scrollTo(0, y), t); await p.waitForTimeout(4200);
  await p.screenshot({ path: 'shots/v2b-trace.png' });
  const b = await p.evaluate(() => document.querySelector('.band--photo').getBoundingClientRect().top + scrollY + 260);
  await p.evaluate(y => window.scrollTo(0, y), b); await p.waitForTimeout(2200);
  await p.screenshot({ path: 'shots/v2b-106.png' });
  await p.goto('http://localhost:8765/histoire.html', { waitUntil: 'networkidle' }); await p.waitForTimeout(600);
  await p.screenshot({ path: 'shots/v2b-hist-top.png' });
  const g = await p.evaluate(() => document.querySelector('#galerie').getBoundingClientRect().top + scrollY - 40);
  for (let y = g; y < g + 1600; y += 300) { await p.evaluate(y => window.scrollTo(0, y), y); await p.waitForTimeout(250); }
  await p.evaluate(y => window.scrollTo(0, y), g + 200); await p.waitForTimeout(1200);
  await p.screenshot({ path: 'shots/v2b-gallery.png' });
  await p.goto('http://localhost:8765/fribourg.html', { waitUntil: 'networkidle' }); await p.waitForTimeout(600);
  await p.screenshot({ path: 'shots/v2b-fr.png' });
  await browser.close();
})();
