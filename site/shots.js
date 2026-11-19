const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch();
  const pages = ['index','histoire','eau','fribourg','carnet','rejoindre'];
  const errors = [];
  for (const [name, vp] of [['d', {width:1440, height:900}], ['m', {width:390, height:844}]]) {
    const ctx = await browser.newContext({ viewport: vp, deviceScaleFactor: 1 });
    for (const p of pages) {
      const page = await ctx.newPage();
      page.on('console', m => { if (m.type() === 'error') errors.push(`${p}/${name}: ${m.text()}`); });
      page.on('pageerror', e => errors.push(`${p}/${name}: ${e.message}`));
      await page.goto(`http://localhost:8765/${p}.html`, { waitUntil: 'networkidle' });
      await page.waitForTimeout(3600);
      await page.screenshot({ path: `shots/${p}-${name}-top.png` });
      if (p !== 'eau') await page.screenshot({ path: `shots/${p}-${name}-full.png`, fullPage: true });
      const ow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
      if (ow > 0) errors.push(`${p}/${name}: horizontal overflow ${ow}px`);
      await page.close();
    }
    await ctx.close();
  }
  console.log(errors.length ? errors.join('\n') : 'no errors');
  await browser.close();
})();
