// Extract the original UI sprites and render code-authored SVG panels. No story/CG access.
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const R=path.resolve(__dirname,'..'),P=path.dirname(R);
const toolkit=process.env.WATCH_COMPAT_TOOLKIT||path.join(P,'源码/tools/compat-toolkit/node_modules/aiot-toolkit');
const sharp=require(require.resolve('sharp',{paths:[toolkit]}));
const input=path.join(P,'可调用资源/images/data/uipsd'),out=path.join(R,'src/common/ui2');
const vectors=path.join(__dirname,'ui-source');fs.mkdirSync(out,{recursive:true});fs.mkdirSync(vectors,{recursive:true});
const provenance=[];
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
function original(name){const b=fs.readFileSync(path.join(input,name));provenance.push({source:'可调用资源/images/data/uipsd/'+name,sha256:hash(b)});return b;}
const svg=(w,h,body)=>`<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}" viewBox="0 0 ${w} ${h}">${body}</svg>`;
const grad=(a='#201c2e',b='#0c0b14')=>`<defs><linearGradient id="g" x2="0" y2="1"><stop stop-color="${a}"/><stop offset="1" stop-color="${b}"/></linearGradient></defs>`;
async function render(name,w,h,body){const s=svg(w,h,body);fs.writeFileSync(path.join(vectors,name+'.svg'),s);await sharp(Buffer.from(s)).png({compressionLevel:9}).toFile(path.join(out,name+'.png'));}
function corners(w,h,c='#67556f'){return `<path d="M12 26V12H26 M${w-26} 12H${w-12}V26 M12 ${h-26}V${h-12}H26 M${w-26} ${h-12}H${w-12}V${h-26}" fill="none" stroke="${c}" stroke-width="1"/>`;}
async function button(name,w,h,pressed=false){await render(name,w,h,grad(pressed?'#292031':'#272232',pressed?'#100c16':'#14121e')+`<rect x=".5" y=".5" width="${w-1}" height="${h-1}" rx="2" fill="url(#g)" stroke="${pressed?'#ae5269':'#73637e'}"/><path d="M8 3H${w-8}" stroke="#ae9ab6" stroke-opacity=".25"/><path d="M10 ${h/2}l3 -3 3 3 -3 3z" fill="${pressed?'#d36277':'#92677f'}"/><path d="M${w-16} ${h/2}l3 -3 3 3 -3 3z" fill="${pressed?'#d36277':'#92677f'}"/>`);}
(async()=>{
 const offRaw=original('title@allbtns%cref;off.png'),over=original('title@allbtns%cref;over.png');
 // title.csv places the trimmed normal-state sheet at (23,16) inside the 217x293 cref.
 const off=await sharp({create:{width:217,height:293,channels:4,background:{r:0,g:0,b:0,alpha:0}}}).composite([{input:offRaw,left:23,top:16}]).png().toBuffer();
 for(const [i,key]of ['start','load','gallery','settings','end'].entries()){
  for(const [suffix,data]of [['',off],['-over',over]])await sharp(data).extract({left:0,top:i*50,width:217,height:46}).png({compressionLevel:9}).toFile(path.join(out,'title-'+key+suffix+'.png'));
 }
 // Only the non-narrative original message-box art is used as an unobtrusive edge motif.
 const base=original('message@base%base.png');
 const motif=await sharp(base).extract({left:0,top:24,width:1280,height:188}).resize(432,66).png().toBuffer();
 const embedded='data:image/png;base64,'+motif.toString('base64');
 await render('title-shade',432,514,`<defs><linearGradient id="fade" x2="0" y2="1"><stop offset=".31" stop-color="#0b0812" stop-opacity="0"/><stop offset=".49" stop-color="#0b0812"/><stop offset="1" stop-color="#0b0812"/></linearGradient></defs><rect width="432" height="514" fill="url(#fade)"/><image href="${embedded}" x="0" y="425" width="432" height="66" opacity=".18"/><path d="M42 501H176 M188 501H200" stroke="#8e3d52" stroke-opacity=".7"/>`);
 await render('box',432,228,grad('#191424','#0d0b15')+`<rect width="432" height="228" fill="url(#g)"/><image href="${embedded}" y="160" width="432" height="66" opacity=".13"/><path d="M0 .5H432 M22 42.5H410" stroke="#765775" stroke-opacity=".8"/><path d="M24 2H98" stroke="#b75c71"/><path d="M24 217H408" stroke="#5e4664" stroke-opacity=".5"/>`);
 await render('panel_full',432,514,grad('#171320','#0b0a12')+`<rect width="432" height="514" fill="url(#g)"/><image href="${embedded}" x="0" y="432" width="432" height="66" opacity=".16"/><rect x="15.5" y="17.5" width="401" height="479" fill="none" stroke="#4a3b52"/>${corners(432,514)}<path d="M30 76.5H402" stroke="#53425d"/><path d="M30 76.5H91" stroke="#b65b73"/><path d="M30 442H402" stroke="#45394e"/>`);
 await render('panel',396,470,grad()+`<rect x=".5" y=".5" width="395" height="469" fill="url(#g)" stroke="#62506d"/>${corners(396,470)}`);
 for(const [name,w,h,pressed]of [['btn',380,52,false],['btn_press',380,52,true],['btn_small',118,46,false],['btn_small_press',118,46,true]])await button(name,w,h,pressed);
 for(const [name,w,h]of [['slot_plate',376,76],['chapter_plate',376,92],['card_plate',178,150]]){
  await render(name,w,h,grad('#211a2c','#12101b')+`<rect x=".5" y=".5" width="${w-1}" height="${h-1}" fill="url(#g)" stroke="#53425e"/><path d="M.5 12V${h-12}" stroke="#a5566b" stroke-width="2"/><path d="M12 3H${w-12}" stroke="#8d7398" stroke-opacity=".18"/>${corners(w,h,'#6d5374')}`);
 }
 await render('namebar',432,42,`<path d="M24 41.5H408" stroke="#735575"/><path d="M24 41.5H98" stroke="#b25972"/>`);
 await render('divider',260,16,`<path d="M0 8H119 M141 8H260" stroke="#6e536f"/><path d="M124 8l6 -4 6 4 -6 4z" fill="#b35d73"/>`);
 await render('cursor',14,14,`<path d="M1 7l6 -5 6 5 -6 5z" fill="#c36e87"/>`);
 fs.writeFileSync(path.join(R,'reports/ui-original-assets.json'),JSON.stringify({scope:'Original non-narrative UI sprites only',sources:provenance,titleSpriteCrop:{width:217,height:46,pitchY:50,rows:5,normalSheetOffset:[23,16]},outputs:fs.readdirSync(out).filter(n=>n.endsWith('.png')).map(n=>({name:n,bytes:fs.statSync(path.join(out,n)).size,sha256:hash(fs.readFileSync(path.join(out,n)))}))},null,2));
 console.log('UI sprites / panels generated; no narrative assets read.');
})().catch(e=>{console.error(e);process.exitCode=1;});
