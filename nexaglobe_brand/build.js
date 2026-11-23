// NexaGlobe brand kit generator: node build.js
const {chromium}=require('playwright');const fs=require('fs');
const N='M52 148V62h22l50 62V80h-12l24-28 24 28h-12v68h-22L76 86v62z';
const defs=`<defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#22d3ee"/><stop offset=".55" stop-color="#4f6bf0"/><stop offset="1" stop-color="#7c3aed"/></linearGradient>
<linearGradient id="tx" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#22d3ee"/><stop offset="1" stop-color="#a78bfa"/></linearGradient></defs>`;
const globe=(c,o)=>`<g fill="none" stroke="${c}" stroke-opacity="${o}" stroke-width="2.5"><circle cx="100" cy="100" r="72"/><ellipse cx="100" cy="100" rx="30" ry="72"/><path d="M28 100h144M38 64h124M38 136h124"/></g>`;
const mark=`<rect width="200" height="200" rx="46" fill="url(#bg)"/>${globe('#fff',.18)}<path d="${N}" fill="#fff"/><circle cx="160" cy="44" r="7" fill="#ff6b4a"/>`;
const svg=(w,h,body,vb)=>`<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}" viewBox="${vb||`0 0 ${w} ${h}`}">${defs}${body}</svg>`;
const word=(x,y,s,c)=>`<text x="${x}" y="${y}" font-family="Inter Display" font-size="${s}" letter-spacing="${s*.04}" fill="${c}"><tspan font-weight="800">NEXA</tspan><tspan font-weight="300">GLOBE</tspan></text>`;
const files={
 'icon_mark.svg':svg(200,200,mark),
 'mark_white.svg':svg(200,200,`<path d="${N}" fill="#fff"/>`),
 'mark_black.svg':svg(200,200,`<path d="${N}" fill="#0b1b3a"/>`),
 'etsy_shop_icon.svg':svg(500,500,`<rect width="500" height="500" fill="#0b1b3a"/><g transform="translate(140 92) scale(1.1)">${mark}</g>${word(250,412,40,'#fff').replace('<text','<text text-anchor="middle"')}<text x="250" y="450" text-anchor="middle" font-family="Inter" font-weight="500" font-size="15" letter-spacing="5" fill="#8fa3c7">DIGITAL · APPAREL · WORLDWIDE</text>`),
 'logo_horizontal_dark.svg':svg(1200,320,`<rect width="1200" height="320" fill="#0b1b3a"/><g transform="translate(70 60)">${mark}</g>${word(320,175,96,'#fff')}<text x="324" y="232" font-family="Inter" font-weight="500" font-size="26" letter-spacing="9" fill="url(#tx)">DIGITAL · APPAREL · WORLDWIDE</text>`),
 'logo_horizontal_light.svg':svg(1200,320,`<rect width="1200" height="320" fill="#ffffff"/><g transform="translate(70 60)">${mark}</g>${word(320,175,96,'#0b1b3a')}<text x="324" y="232" font-family="Inter" font-weight="500" font-size="26" letter-spacing="9" fill="#4f6bf0">DIGITAL · APPAREL · WORLDWIDE</text>`),
};
for(const[k,v] of Object.entries(files))fs.writeFileSync(k,v);
const banner=(w,h)=>{const s=h/840;return `<!doctype html><html><head><style>
*{margin:0;box-sizing:border-box}body{width:${w}px;height:${h}px;overflow:hidden;font-family:Inter;background:#0b1b3a;position:relative;color:#fff}
.glow{position:absolute;border-radius:50%;filter:blur(${160*s}px)}
.grid{position:absolute;inset:0;background-image:linear-gradient(rgba(255,255,255,.04) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.04) 1px,transparent 1px);background-size:${70*s}px ${70*s}px}
.wrap{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:${34*s}px}
.lock{display:flex;align-items:center;gap:${44*s}px}
.wm{font-family:'Inter Display';font-size:${150*s}px;letter-spacing:${6*s}px;line-height:1}.wm b{font-weight:800}.wm span{font-weight:300}
.tag{font-size:${30*s}px;letter-spacing:${12*s}px;font-weight:500;background:linear-gradient(90deg,#22d3ee,#a78bfa);-webkit-background-clip:text;color:transparent}
.pills{display:flex;gap:${22*s}px}.pill{border:${2*s}px solid rgba(255,255,255,.18);background:rgba(255,255,255,.06);border-radius:999px;padding:${16*s}px ${34*s}px;font-size:${30*s}px;font-weight:600;display:flex;align-items:center;gap:${14*s}px}
.dot{width:${14*s}px;height:${14*s}px;border-radius:50%}
.orb{position:absolute;opacity:.5}
</style></head><body><div class="grid"></div>
<div class="glow" style="width:${900*s}px;height:${900*s}px;background:#22d3ee;opacity:.22;left:${-200*s}px;top:${-300*s}px"></div>
<div class="glow" style="width:${1000*s}px;height:${1000*s}px;background:#7c3aed;opacity:.3;right:${-250*s}px;bottom:${-450*s}px"></div>
<svg class="orb" style="right:${-220*s}px;top:${-160*s}px" width="${1000*s}" height="${1000*s}" viewBox="0 0 200 200">${globe('#8fb4ff',.35)}</svg>
<svg class="orb" style="left:${-160*s}px;bottom:${-300*s}px" width="${700*s}" height="${700*s}" viewBox="0 0 200 200">${globe('#8fb4ff',.25)}</svg>
<div class="wrap"><div class="lock">${svg(230*s,230*s,mark,'0 0 200 200')}<div class="wm"><b>NEXA</b><span>GLOBE</span></div></div>
<div class="tag">DIGITAL PRODUCTS · PRINTED APPAREL · WORLDWIDE</div>
<div class="pills"><div class="pill"><i class="dot" style="background:#22d3ee"></i>Digital Downloads</div><div class="pill"><i class="dot" style="background:#a78bfa"></i>Custom Print Tees</div><div class="pill"><i class="dot" style="background:#ff6b4a"></i>Fast Global Shipping</div></div></div>
</body></html>`};
const mini=()=>`<!doctype html><html><head><style>
*{margin:0;box-sizing:border-box}body{width:1200px;height:160px;overflow:hidden;font-family:Inter;background:#0b1b3a;position:relative;color:#fff}
.glow{position:absolute;border-radius:50%;filter:blur(60px)}
.grid{position:absolute;inset:0;background-image:linear-gradient(rgba(255,255,255,.04) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.04) 1px,transparent 1px);background-size:24px 24px}
.row{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;gap:34px}
.lock{display:flex;align-items:center;gap:16px}
.wm{font-family:'Inter Display';font-size:46px;letter-spacing:2px;line-height:1}.wm b{font-weight:800}.wm span{font-weight:300}
.sep{width:1px;height:64px;background:rgba(255,255,255,.2)}
.right{display:flex;flex-direction:column;gap:12px}
.tag{font-size:12px;letter-spacing:4.5px;font-weight:600;background:linear-gradient(90deg,#22d3ee,#a78bfa);-webkit-background-clip:text;color:transparent}
.pills{display:flex;gap:8px}.pill{border:1px solid rgba(255,255,255,.18);background:rgba(255,255,255,.06);border-radius:999px;padding:6px 13px;font-size:13px;font-weight:600;display:flex;align-items:center;gap:7px}
.dot{width:7px;height:7px;border-radius:50%}.orb{position:absolute;opacity:.5}
</style></head><body><div class="grid"></div>
<div class="glow" style="width:420px;height:300px;background:#22d3ee;opacity:.22;left:-120px;top:-120px"></div>
<div class="glow" style="width:460px;height:320px;background:#7c3aed;opacity:.32;right:-120px;bottom:-160px"></div>
<svg class="orb" style="right:-70px;top:-90px" width="300" height="300" viewBox="0 0 200 200">${globe('#8fb4ff',.35)}</svg>
<svg class="orb" style="left:-80px;bottom:-130px" width="240" height="240" viewBox="0 0 200 200">${globe('#8fb4ff',.25)}</svg>
<div class="row"><div class="lock">${svg(80,80,mark,'0 0 200 200')}<div class="wm"><b>NEXA</b><span>GLOBE</span></div></div><div class="sep"></div>
<div class="right"><div class="tag">DIGITAL PRODUCTS · PRINTED APPAREL · WORLDWIDE</div>
<div class="pills"><div class="pill"><i class="dot" style="background:#22d3ee"></i>Digital Downloads</div><div class="pill"><i class="dot" style="background:#a78bfa"></i>Custom Print Tees</div><div class="pill"><i class="dot" style="background:#ff6b4a"></i>Fast Global Shipping</div></div></div></div>
</body></html>`;
(async()=>{const b=await chromium.launch();const p=await b.newPage();
 const shot=async(html,w,h,out,scale=1,transparent=false)=>{await p.setViewportSize({width:w,height:h});await p.setContent(html);await p.evaluate(()=>document.fonts.ready);await p.screenshot({path:out,omitBackground:transparent,scale:'device'});};
 const page=(f,w,h,bg='transparent')=>`<style>body{margin:0;background:${bg}}svg{display:block;width:${w}px;height:${h}px}</style>${fs.readFileSync(f,'utf8')}`;
 const p2=await b.newPage({deviceScaleFactor:2});
 for(const[f,w,h,out,tr] of [['etsy_shop_icon.svg',500,500,'etsy_shop_icon_1000.png'],['icon_mark.svg',500,500,'icon_mark_1000.png',1],['mark_white.svg',1000,1000,'mark_white_print_2000.png',1],['mark_black.svg',1000,1000,'mark_black_print_2000.png',1],['logo_horizontal_dark.svg',1200,320,'logo_horizontal_dark.png'],['logo_horizontal_light.svg',1200,320,'logo_horizontal_light.png']]){
  await p2.setViewportSize({width:w,height:h});await p2.setContent(page(f,w,h));await p2.evaluate(()=>document.fonts.ready);await p2.screenshot({path:out,omitBackground:!!tr});}
 await shot(banner(3360,840),3360,840,'etsy_banner_3360x840.png');
 await shot(banner(1500,500),1500,500,'social_banner_1500x500.png');
 await shot(banner(1200,300),1200,300,'banner_1200x300.png');
 await shot(mini(),1200,160,'etsy_mini_banner_1200x160.png');
 await p2.setViewportSize({width:1200,height:160});await p2.setContent(mini());await p2.evaluate(()=>document.fonts.ready);await p2.screenshot({path:'etsy_mini_banner_2400x320.png'});
 await b.close();})();
