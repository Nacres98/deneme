// Screenshots each .slide in listing/slides.html at 2x -> listing/images/NN.png (3000x2250)
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');
(async () => {
  const out = path.resolve(__dirname, 'images');
  fs.mkdirSync(out, { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1540, height: 1165 }, deviceScaleFactor: 2 });
  await page.goto('file://' + path.resolve(__dirname, 'slides.html'), { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts.ready);
  const slides = await page.$$('.slide');
  for (let i = 0; i < slides.length; i++) {
    await slides[i].screenshot({ path: path.join(out, String(i + 1).padStart(2, '0') + '.png') });
  }
  await browser.close();
  console.log('rendered', slides.length);
})();
