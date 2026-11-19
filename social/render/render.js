// Usage: node render.js <html-file> <out.png> <width> <height> [scale]
const { chromium } = require('playwright');
(async () => {
  const [,, file, out, w, h, scale] = process.argv;
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: +w, height: +h }, deviceScaleFactor: +(scale || 1) });
  await page.goto('file://' + require('path').resolve(file));
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(150);
  await page.screenshot({ path: out, clip: { x: 0, y: 0, width: +w, height: +h } });
  await browser.close();
})();
