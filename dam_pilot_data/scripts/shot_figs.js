const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:900,height:1000},deviceScaleFactor:2.5});
await p.goto('file://'+process.argv[2]);await p.waitForTimeout(400);
const pre=process.argv[4];
for(const i of process.argv.slice(5)){await (await p.$('#'+i)).screenshot({path:process.argv[3]+'/'+pre+i+'.png'});}
await b.close();})();
