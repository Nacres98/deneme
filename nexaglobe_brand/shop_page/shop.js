// Etsy shop page assets: featured photos (1600x1200) + intro video frames (1920x1080). node shop.js
const {chromium}=require('playwright');const fs=require('fs');
const N='M52 148V62h22l50 62V80h-12l24-28 24 28h-12v68h-22L76 86v62z';
const defs=`<defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#22d3ee"/><stop offset=".55" stop-color="#4f6bf0"/><stop offset="1" stop-color="#7c3aed"/></linearGradient></defs>`;
const globe=(c,o)=>`<g fill="none" stroke="${c}" stroke-opacity="${o}" stroke-width="2.5"><circle cx="100" cy="100" r="72"/><ellipse cx="100" cy="100" rx="30" ry="72"/><path d="M28 100h144M38 64h124M38 136h124"/></g>`;
const mark=(sz)=>`<svg width="${sz}" height="${sz}" viewBox="0 0 200 200">${defs}<rect width="200" height="200" rx="46" fill="url(#bg)"/>${globe('#fff',.18)}<path d="${N}" fill="#fff"/><circle cx="160" cy="44" r="7" fill="#ff6b4a"/></svg>`;
const ic={
 dl:`<path d="M50 20v42M32 46l18 18 18-18M24 74h52" stroke-linecap="round" stroke-linejoin="round"/>`,
 tee:`<path d="M36 20l-18 10 7 16 9-4v38h32V42l9 4 7-16-18-10c-2 6-7 9-14 9s-12-3-14-9z" stroke-linejoin="round"/>`,
 globe:`<circle cx="50" cy="50" r="30"/><ellipse cx="50" cy="50" rx="12" ry="30"/><path d="M20 50h60"/>`,
 lock:`<rect x="26" y="44" width="48" height="36" rx="6"/><path d="M36 44V34a14 14 0 0 1 28 0v10"/>`,
 star:`<path d="M50 18l9 20 22 2-17 15 5 22-19-11-19 11 5-22-17-15 22-2z" stroke-linejoin="round"/>`,
 chat:`<path d="M20 26h60v38H44l-14 12V64H20z" stroke-linejoin="round"/>`,
};
const icon=(k,sz,c)=>`<svg width="${sz}" height="${sz}" viewBox="0 0 100 100" fill="none" stroke="${c}" stroke-width="5">${ic[k]}</svg>`;
const base=(w,h,body,extra='')=>`<!doctype html><html><head><style>
*{margin:0;box-sizing:border-box}body{width:${w}px;height:${h}px;overflow:hidden;font-family:Inter;background:#0b1b3a;color:#fff;position:relative}
.grid{position:absolute;inset:0;background-image:linear-gradient(rgba(255,255,255,.04) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.04) 1px,transparent 1px);background-size:60px 60px}
.glow{position:absolute;border-radius:50%;filter:blur(140px)}
.wm{font-family:'Inter Display';line-height:1;letter-spacing:.04em}.wm b{font-weight:800}.wm span{font-weight:300}
.grad{background:linear-gradient(90deg,#22d3ee,#a78bfa);-webkit-background-clip:text;color:transparent}
.card{background:rgba(255,255,255,.06);border:2px solid rgba(255,255,255,.14);border-radius:36px}
h1{font-family:'Inter Display';font-weight:800;letter-spacing:-.01em;line-height:1.05}
${extra}</style></head><body><div class="grid"></div>
<div class="glow" style="width:800px;height:800px;background:#22d3ee;opacity:.2;left:-250px;top:-300px"></div>
<div class="glow" style="width:900px;height:900px;background:#7c3aed;opacity:.28;right:-300px;bottom:-400px"></div>${body}</body></html>`;
const foot=`<div style="position:absolute;left:0;right:0;bottom:56px;display:flex;justify-content:center;align-items:center;gap:16px">${mark(52)}<div class="wm" style="font-size:34px"><b>NEXA</b><span>GLOBE</span></div></div>`;
const head=(k,t)=>`<div style="text-align:center;padding-top:110px"><div class="grad" style="font-size:26px;font-weight:600;letter-spacing:10px">${k}</div><h1 style="font-size:92px;margin-top:22px">${t}</h1></div>`;
const cards=(items)=>`<div style="display:flex;gap:40px;justify-content:center;margin-top:100px">${items.map(([k,c,t,d])=>`<div class="card" style="width:440px;height:560px;padding:60px 46px;display:flex;flex-direction:column;gap:26px">
 <div style="width:120px;height:120px;border-radius:30px;background:${c}22;display:flex;align-items:center;justify-content:center">${icon(k,84,c)}</div>
 <div style="font-size:44px;font-weight:700;line-height:1.1">${t}</div><div style="font-size:27px;line-height:1.45;color:#b9c6e4">${d}</div></div>`).join('')}</div>`;
const photos={
 'featured_1_what_we_offer':base(1600,1200,head('WHAT WE OFFER','Three ways to shop')+cards([
  ['dl','#22d3ee','Digital Downloads','Instant files you can download, print and use right away.'],
  ['tee','#a78bfa','Custom Print Tees','Original designs printed on demand, just for you.'],
  ['globe','#ff6b4a','Worldwide Shipping','Physical orders ship to customers around the world.']])+foot),
 'featured_2_how_downloads_work':base(1600,1200,head('DIGITAL DOWNLOADS','How it works')+`<div style="display:flex;gap:40px;justify-content:center;margin-top:100px">${[['1','Buy','Check out securely through Etsy.'],['2','Download','Your files appear instantly in your Etsy account and email.'],['3','Print & enjoy','Print at home, at a print shop, or use them digitally.']].map(([n,t,d])=>`<div class="card" style="width:440px;height:560px;padding:60px 46px;display:flex;flex-direction:column;gap:26px">
 <div style="width:120px;height:120px;border-radius:999px;background:linear-gradient(135deg,#22d3ee,#7c3aed);display:flex;align-items:center;justify-content:center;font-family:'Inter Display';font-weight:800;font-size:60px">${n}</div>
 <div style="font-size:44px;font-weight:700">${t}</div><div style="font-size:27px;line-height:1.45;color:#b9c6e4">${d}</div></div>`).join('')}</div>`+foot),
 'featured_3_printed_apparel':base(1600,1200,`<div style="position:absolute;left:110px;top:0;bottom:0;width:780px;display:flex;flex-direction:column;justify-content:center;gap:34px">
 <div class="grad" style="font-size:26px;font-weight:600;letter-spacing:10px">PRINTED APPAREL</div><h1 style="font-size:84px">Designed by us.<br>Printed for you.</h1>
 <div style="font-size:32px;line-height:1.5;color:#b9c6e4">Every tee is printed on demand when you order, so nothing sits in a warehouse and every piece is made fresh.</div></div>
 <div style="position:absolute;right:60px;top:190px;width:700px;height:760px;display:flex;align-items:center;justify-content:center">
 <svg width="700" height="700" viewBox="0 0 100 100"><defs><linearGradient id="t" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1c2f57"/><stop offset="1" stop-color="#14244a"/></linearGradient></defs>
 <path d="M36 14l-22 12 8 18 10-5v47h36V39l10 5 8-18-22-12c-2 6-7 9-14 9s-12-3-14-9z" fill="url(#t)" stroke="rgba(255,255,255,.25)" stroke-width=".6" stroke-linejoin="round"/></svg>
 <div style="position:absolute;top:340px">${mark(170)}</div></div>`+foot),
 'featured_4_our_promise':base(1600,1200,head('OUR PROMISE','Shop with confidence')+cards([
  ['star','#22d3ee','Original designs','Every design in our shop is created by the NexaGlobe team.'],
  ['lock','#a78bfa','Secure checkout','All payments are handled safely by Etsy.'],
  ['chat','#ff6b4a','Friendly support','Questions about an order? Send us a message on Etsy.']])+foot),
};
// --- video: 10 s, 30 fps; scene driven by window.T (seconds)
const ease=t=>t<0?0:t>1?1:1-Math.pow(1-t,3);
const vid=`<div id="s1" style="position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:40px">
<div id="m">${mark(260)}</div><div id="w" class="wm" style="font-size:120px"><b>NEXA</b><span>GLOBE</span></div>
<div id="tg" class="grad" style="font-size:30px;font-weight:600;letter-spacing:12px">DIGITAL · APPAREL · WORLDWIDE</div></div>
<div id="s2" style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;gap:50px">
${[['dl','#22d3ee','Digital Downloads'],['tee','#a78bfa','Custom Print Tees'],['globe','#ff6b4a','Worldwide Shipping']].map(([k,c,t],i)=>`<div class="card c" id="c${i}" style="width:480px;height:440px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:40px">
<div style="width:170px;height:170px;border-radius:44px;background:${c}22;display:flex;align-items:center;justify-content:center">${icon(k,120,c)}</div><div style="font-size:46px;font-weight:700">${t}</div></div>`).join('')}</div>
<div id="s3" style="position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:44px">
<div style="display:flex;align-items:center;gap:34px">${mark(150)}<div class="wm" style="font-size:96px"><b>NEXA</b><span>GLOBE</span></div></div>
<div style="font-size:44px;font-weight:600">Thanks for visiting our shop</div><div class="grad" style="font-size:30px;font-weight:600;letter-spacing:10px">FOLLOW US FOR NEW DROPS</div></div>
<script>
const E=t=>t<0?0:t>1?1:1-Math.pow(1-t,3);const $=id=>document.getElementById(id);
function frame(T){
 const a=E(T/0.9), out1=E((T-3)/0.5); $('s1').style.opacity=Math.min(1,T/0.4)*(1-out1);
 $('m').style.transform='scale('+(0.6+0.4*a)+') rotate('+(-12*(1-a))+'deg)';
 const w=E((T-0.6)/0.8); $('w').style.opacity=w; $('w').style.transform='translateY('+(40*(1-w))+'px)';
 const g=E((T-1.3)/0.8); $('tg').style.opacity=g; $('tg').style.letterSpacing=(12+14*(1-g))+'px';
 const out2=E((T-7.2)/0.5); $('s2').style.opacity=(T>3.2?1:0)*(1-out2);
 for(let i=0;i<3;i++){const c=E((T-3.4-i*0.6)/0.7);const el=$('c'+i);el.style.opacity=c;el.style.transform='translateY('+(80*(1-c))+'px)';}
 const s3=E((T-7.6)/0.8); $('s3').style.opacity=s3; $('s3').style.transform='scale('+(0.94+0.06*s3)+')';
}
</script>`;
(async()=>{const b=await chromium.launch();
 const p=await b.newPage({viewport:{width:1600,height:1200}});
 for(const[k,h] of Object.entries(photos)){await p.setContent(h);await p.evaluate(()=>document.fonts.ready);await p.screenshot({path:k+'.jpg',type:'jpeg',quality:92});}
 const v=await b.newPage({viewport:{width:1920,height:1080}});await v.setContent(base(1920,1080,vid));await v.evaluate(()=>document.fonts.ready);
 for(let f=0;f<300;f++){await v.evaluate(t=>frame(t),f/30);await v.screenshot({path:`frames/${String(f).padStart(4,'0')}.png`});}
 await b.close();})();
