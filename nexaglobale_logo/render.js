const {chromium}=require('playwright');const fs=require('fs');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:500,height:500},deviceScaleFactor:2});
for(const n of ['a','b','c']){await p.setContent(`<style>body{margin:0}</style>${fs.readFileSync(n+'.svg','utf8')}`);await p.screenshot({path:`nexaglobale_${n}_1000px.png`});}
await p.setViewportSize({width:1500,height:500});await p.setContent(`<style>body{margin:0;display:flex;gap:0}</style>${['a','b','c'].map(n=>fs.readFileSync(n+'.svg','utf8')).join('')}`);
await p.screenshot({path:'preview.png',deviceScaleFactor:1});await b.close();})();
