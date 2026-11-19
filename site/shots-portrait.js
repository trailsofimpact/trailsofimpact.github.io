const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch();
  for (const [n, vp] of [['d', { width: 1440, height: 900 }], ['m', { width: 390, height: 844 }]]) {
    const ctx = await browser.newContext({ viewport: vp }); const p = await ctx.newPage();
    await p.goto('http://localhost:8765/histoire.html', { waitUntil: 'networkidle' });
    const y = await p.evaluate(() => document.querySelector('#fondatrice-title').getBoundingClientRect().top + scrollY - (innerWidth < 800 ? 420 : 240));
    await p.evaluate(y => window.scrollTo(0, y), y); await p.waitForTimeout(900);
    await p.screenshot({ path: `shots/portrait-${n}.png` });
    await p.goto('http://localhost:8765/rejoindre.html#comite', { waitUntil: 'networkidle' }); await p.waitForTimeout(900);
    const z = await p.evaluate(() => document.querySelector('.with').getBoundingClientRect().top + scrollY - (innerWidth < 800 ? 300 : 420));
    await p.evaluate(y => window.scrollTo(0, y), z); await p.waitForTimeout(700);
    await p.screenshot({ path: `shots/with-${n}.png` });
    await ctx.close();
  }
  await browser.close();
})();
