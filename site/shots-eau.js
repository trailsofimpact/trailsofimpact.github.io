const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch();
  for (const [name, vp] of [['d', {width:1440, height:900}], ['m', {width:390, height:844}]]) {
    const ctx = await browser.newContext({ viewport: vp, deviceScaleFactor: 1 });
    const page = await ctx.newPage();
    const errs = [];
    page.on('pageerror', e => errs.push(e.message));
    await page.goto('http://localhost:8765/eau.html', { waitUntil: 'networkidle' });
    await page.waitForTimeout(2500);
    await page.screenshot({ path: `shots/eau-${name}-0.png` });
    const tops = await page.evaluate(() => [...document.querySelectorAll('.step')].map(s => s.getBoundingClientRect().top + window.scrollY + s.offsetHeight/2));
    const frac = name === 'm' ? 0.8 : 0.55;
    const picks = [0, 2, 3, 4, 6];
    for (const i of picks) {
      // aim: step i at ~70% progress (center line inside its lower part)
      const y = tops[i] - vp.height * frac + (name==='m'? 0.15: 0.25) * (await page.evaluate(i => document.querySelectorAll('.step')[i].offsetHeight, i));
      await page.evaluate(y => window.scrollTo(0, y), y);
      await page.waitForTimeout(700);
      await page.screenshot({ path: `shots/eau-${name}-s${i+1}.png` });
    }
    // rest of the page
    const after = await page.evaluate(() => document.querySelector('#savoir').getBoundingClientRect().top + window.scrollY - 72);
    await page.evaluate(y => window.scrollTo(0, y), after);
    await page.waitForTimeout(500);
    await page.screenshot({ path: `shots/eau-${name}-after.png`, fullPage: false });
    console.log(name, errs.join('|') || 'ok');
    await ctx.close();
  }
  await browser.close();
})();
