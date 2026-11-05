// Compare actual files pulled from this project's dedicated virtual watch.
const fs=require('fs'),path=require('path'),crypto=require('crypto'),{execFileSync}=require('child_process');
const root=path.resolve(__dirname,'..'),toolkit=path.join(__dirname,'compat-toolkit/node_modules/aiot-toolkit');
const req=require('module').createRequire(path.join(toolkit,'package.json')),JSZip=req('jszip');
const adb=path.resolve(path.dirname(require.resolve('@miwt/adb')),'../bin/win/adb.exe');
const m=JSON.parse(fs.readFileSync(path.join(root,'src/manifest.json'))),out=path.join(root,'reports/native-installed');fs.mkdirSync(out,{recursive:true});
const sha=x=>crypto.createHash('sha256').update(x).digest('hex');
(async()=>{const file=path.join(root,'dist',m.package+'.debug.'+m.versionName+'.rpk'),z=await JSZip.loadAsync(fs.readFileSync(file),{checkCRC32:true}),files=[];
for(const name of ['pages/index/index.js','common/story/demo.txt','common/watch.otf','common/font-license.txt','common/logo.png','manifest-watch.json']){
 const dest=path.join(out,name);fs.mkdirSync(path.dirname(dest),{recursive:true});
 execFileSync(adb,['-s','emulator-5562','pull','/data/app/'+m.package+'/'+name,dest],{windowsHide:true,timeout:30000,stdio:'pipe'});
 const expected=sha(await z.file(name).async('nodebuffer')),actual=sha(fs.readFileSync(dest));if(expected!==actual)throw Error('Installed file mismatch: '+name);files.push({name,sha256:actual});
}
const result={result:'passed',package:m.package,packageSha256:sha(fs.readFileSync(file)),files};fs.writeFileSync(path.join(root,'reports/native-installed-verification.json'),JSON.stringify(result,null,2));console.log(JSON.stringify(result));
})().catch(e=>{console.error(e.message);process.exitCode=1;});
