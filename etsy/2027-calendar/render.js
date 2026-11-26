// Render HTML files to PDF / PNG with the pre-installed Chromium.
// Usage: node render.js jobs.json
// jobs.json: [{"html": "/abs/file.html", "pdf": "/abs/out.pdf"} | {"html": ..., "png": ..., "w": 2700, "h": 2025}]
const { chromium } = require('playwright');
const fs = require('fs');

(async () => {
  const jobs = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
  const browser = await chromium.launch();
  const ctx = await browser.newContext({ deviceScaleFactor: 1 });
  const page = await ctx.newPage();
  for (const j of jobs) {
    if (j.png) await page.setViewportSize({ width: j.w, height: j.h });
    await page.goto('file://' + j.html, { waitUntil: 'load' });
    await page.evaluate(() => document.fonts.ready);
    if (j.pdf) {
      await page.pdf({ path: j.pdf, preferCSSPageSize: true, printBackground: true });
    } else {
      await page.screenshot({ path: j.png, type: 'png' });
    }
  }
  await browser.close();
  console.log(`rendered ${jobs.length} jobs`);
})();
