// Pull and fingerprint only UI, manifest, font and icon bytes from the dedicated VM.
const fs=require('fs'),path=require('path'),crypto=require('crypto'),{execFileSync}=require('child_process');
const R=path.resolve(__dirname,'..'),toolkit=process.env.WATCH_COMPAT_TOOLKIT||path.join(__dirname,'compat-toolkit/node_modules/aiot-toolkit');
const JSZip=require(require.resolve('jszip',{paths:[toolkit]}));
const adb=path.resolve(path.dirname(require.resolve('@miwt/adb')),'../bin/win/adb.exe');
const sha=x=>crypto.createHash('sha256').update(x).digest('hex');
(async()=>{
 const m=JSON.parse(fs.readFileSync(path.join(R,'src/manifest.json'))),p=path.join(R,'dist',m.package+'.debug.'+m.versionName+'.rpk'),z=await JSZip.loadAsync(fs.readFileSync(p),{checkCRC32:true});
 const out=path.join(R,'reports/ui-installed'),files=[];fs.mkdirSync(out,{recursive:true});
 for(const name of ['pages/index/index.js','manifest-watch.json','common/watch.otf','common/logo.png','common/ui2/title-start.png','common/ui2/title-start-over.png','common/ui2/panel_full.png']){
  const dest=path.join(out,name);fs.mkdirSync(path.dirname(dest),{recursive:true});execFileSync(adb,['-s','emulator-5562','pull','/data/app/'+m.package+'/'+name,dest],{windowsHide:true,timeout:30000,stdio:'pipe'});
  const expected=sha(await z.file(name).async('nodebuffer'));if(sha(fs.readFileSync(dest))!==expected)throw Error('Installed UI mismatch: '+name);files.push({name,sha256:expected});
 }
 const result={result:'passed',packageSha256:sha(fs.readFileSync(p)),version:m.versionName,versionCode:m.versionCode,files};fs.writeFileSync(path.join(R,'reports/ui-installed-verification.json'),JSON.stringify(result,null,2));console.log(JSON.stringify({result:'passed',files:files.length,sha256:result.packageSha256}));
})().catch(e=>{console.error(e.message);process.exitCode=1;});
