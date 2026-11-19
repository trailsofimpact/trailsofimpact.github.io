const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch();
  const errs = [];
  const d = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  let p = await d.newPage();
  p.on('pageerror', e => errs.push('d: ' + e.message));
  p.on('console', m => { if (m.type() === 'error') errs.push('d console: ' + m.text()); });
  await p.goto('http://localhost:8765/index.html', { waitUntil: 'networkidle' });
  await p.waitForTimeout(2500);
  await p.screenshot({ path: 'shots/v2-home-d-top.png' });
  // faire défiler pour déclencher le tracé et les 106 points
  for (let y = 0; y < 9000; y += 600) { await p.evaluate(y => window.scrollTo(0, y), y); await p.waitForTimeout(120); }
  await p.evaluate(() => window.scrollTo(0, 0)); await p.waitForTimeout(300);
  await p.screenshot({ path: 'shots/v2-home-d-full.png', fullPage: true });
  await p.goto('http://localhost:8765/histoire.html', { waitUntil: 'networkidle' }); await p.waitForTimeout(800);
  await p.screenshot({ path: 'shots/v2-hist-d-full.png', fullPage: true });
  await p.click('[data-lb="1"]'); await p.waitForTimeout(600);
  await p.screenshot({ path: 'shots/v2-lightbox-d.png' });
  await p.keyboard.press('ArrowRight'); await p.waitForTimeout(300);
  const cap = await p.textContent('[data-lb-cap]'); errs.push('lightbox caption after → : ' + cap);
  await p.keyboard.press('Escape');
  await p.goto('http://localhost:8765/fribourg.html', { waitUntil: 'networkidle' }); await p.waitForTimeout(800);
  await p.screenshot({ path: 'shots/v2-fr-d-top.png' });
  await p.goto('http://localhost:8765/rejoindre.html', { waitUntil: 'networkidle' }); await p.waitForTimeout(800);
  await p.screenshot({ path: 'shots/v2-rej-d-full.png', fullPage: true });
  await p.goto('http://localhost:8765/eau.html', { waitUntil: 'networkidle' }); await p.waitForTimeout(800);
  const pos = await p.evaluate(() => document.querySelector('#pourquoi-title').getBoundingClientRect().top + scrollY - 120);
  await p.evaluate(y => window.scrollTo(0, y), pos); await p.waitForTimeout(600);
  await p.screenshot({ path: 'shots/v2-eau-d-pourquoi.png' });
  const m = await browser.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 1 });
  p = await m.newPage(); p.on('pageerror', e => errs.push('m: ' + e.message));
  for (const pg of ['index', 'histoire', 'fribourg', 'rejoindre', 'eau', 'carnet']) {
    await p.goto(`http://localhost:8765/${pg}.html`, { waitUntil: 'networkidle' }); await p.waitForTimeout(1500);
    if (pg === 'index') await p.screenshot({ path: 'shots/v2-home-m-top.png' });
    const ow = await p.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
    if (ow > 0) errs.push(`${pg}/m overflow ${ow}px`);
    if (pg === 'index' || pg === 'histoire') {
      for (let y = 0; y < 14000; y += 700) { await p.evaluate(y => window.scrollTo(0, y), y); await p.waitForTimeout(80); }
      await p.evaluate(() => window.scrollTo(0, 0)); await p.waitForTimeout(300);
      await p.screenshot({ path: `shots/v2-${pg}-m-full.png`, fullPage: true });
    }
  }
  console.log(errs.join('\n') || 'no errors');
  await browser.close();
})();
