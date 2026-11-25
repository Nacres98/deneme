// Renders guide/quick_start_guide.html to output/NexaGlobe_Wedding_Planner_User_Guide.pdf (Letter, 3 pages)
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('file://' + path.resolve(__dirname, 'quick_start_guide.html'), { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts.ready);
  await page.pdf({ path: path.resolve(__dirname, '../output/NexaGlobe_Wedding_Planner_User_Guide.pdf'), format: 'Letter',
                   printBackground: true, margin: { top: 0, right: 0, bottom: 0, left: 0 } });
  await browser.close();
})();
