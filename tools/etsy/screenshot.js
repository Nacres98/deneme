// usage: node tools/etsy/screenshot.js in1.html out1.png [in2.html out2.png ...]  (2700x2025)
const { chromium } = require('playwright');
(async () => {
  const a = process.argv.slice(2);
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 2700, height: 2025 }, deviceScaleFactor: 1 });
  for (let i = 0; i < a.length; i += 2) {
    await p.goto('file://' + a[i]);
    await p.waitForTimeout(300);
    await p.screenshot({ path: a[i + 1] });
  }
  await b.close();
})();
