"""Lossless text/container/image format conversion; no gameplay or rendering."""
from pathlib import Path
import base64, collections, hashlib, json, shutil, subprocess, sys, zlib
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
PROJECT=ROOT.parent
RAW=PROJECT/'原始资源解码'
OUT=PROJECT/'可调用资源'
OUT.mkdir(exist_ok=True)
FM=PROJECT/'研究/FreeMote/PsbDecompile.exe'
manifest=json.loads((ROOT/'reports/restored-disk-verification.json').read_text('utf8'))['resources']
TEXT_EXT={'.tjs','.ks','.txt','.csv','.ini','.func','.stand','.stage','.sli','.asd'}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def text_decode(data):
 if data.startswith(b'\xff\xfe'):return data[2:].decode('utf-16-le'),'utf-16-le'
 if data.startswith(b'\xef\xbb\xbf'):return data[3:].decode('utf8'),'utf-8-sig'
 if data.startswith(b'\xfe\xfe\x02\xff\xfe'):
  import struct
  packed,raw=struct.unpack_from('<QQ',data,5);text=zlib.decompress(data[21:21+packed]);assert len(text)==raw
  return text.decode('utf-16-le'),'kirikiri-mode-2'
 if data.startswith(b'\xfe\xfe\x01\xff\xfe'):
  d=data[5:];assert len(d)%2==0
  t=b''.join((((v&0xaaaa)>>1)|((v&0x5555)<<1)).to_bytes(2,'little')for v in (int.from_bytes(d[i:i+2],'little')for i in range(0,len(d),2)))
  return t.decode('utf-16-le'),'kirikiri-mode-1'
 for enc in ['utf8','cp932','gb18030']:
  try:return data.decode(enc),enc
  except UnicodeDecodeError:pass
 raise ValueError('Unsupported text encoding')

rows=[];psb_groups=collections.defaultdict(list);tlg=[]
for record in manifest:
 rel=Path(record['path']);source=RAW/rel
 with source.open('rb')as f:head=f.read(8)
 item={'id':hashlib.sha256(rel.as_posix().encode()).hexdigest()[:20],
       'originalPath':rel.as_posix(),'originalSha256':record['sha256'],
       'originalBytes':record['bytes'],'contentReview':'unreviewed','watchAllowed':False}
 if head.startswith(b'PSB'):
  target=OUT/'json'/rel.parent/(rel.name+'.json');kind='json';psb_groups[rel.parent].append((source,target))
 elif head.startswith(b'TLG'):
  target=OUT/'images'/rel.parent/(rel.name+'.png');kind='png'
  tlg.append({'input':str(source),'output':str(target)})
 elif rel.suffix.lower()in TEXT_EXT:
  target=OUT/'text'/rel.parent/(rel.name+'.utf8.txt');kind='utf8'
  target.parent.mkdir(parents=True,exist_ok=True)
  try:
   text,encoding=text_decode(source.read_bytes());target.write_text(text,'utf8');item['sourceEncoding']=encoding
  except (UnicodeError,ValueError)as e:
   target=OUT/'json'/rel.parent/(rel.name+'.binary.json');kind='binary-json';target.parent.mkdir(parents=True,exist_ok=True)
   data=source.read_bytes()
   target.write_text(json.dumps({'format':'binary-wrapper','originalPath':rel.as_posix(),'encoding':'base64','bytes':len(data),'data':base64.b64encode(data).decode(),'note':'Unknown or compiled text format; original bytes are losslessly available, not source-decompiled.'}), 'utf8')
   item['sourceEncoding']='binary/unrecognized';print(json.dumps({'binaryTextFallback':rel.as_posix(),'header':data[:8].hex()}),flush=True)
 elif rel.suffix.lower()=='.png':
  target=OUT/'images'/rel;kind='png'
  target.parent.mkdir(parents=True,exist_ok=True)
  if not target.exists():shutil.copyfile(source,target)
 elif rel.suffix.lower()in {'.ogg','.wmv'}:
  target=OUT/'media'/rel;kind='ogg'if rel.suffix.lower()=='.ogg'else'wmv'
  target.parent.mkdir(parents=True,exist_ok=True)
  if not target.exists():shutil.copyfile(source,target)
 else:
  target=OUT/'files'/rel;kind=rel.suffix.lower().lstrip('.')or'binary'
  target.parent.mkdir(parents=True,exist_ok=True)
  if not target.exists():shutil.copyfile(source,target)
 item.update(kind=kind,path=target.relative_to(OUT).as_posix());rows.append(item)

for group,jobs in psb_groups.items():
 dest=OUT/'json'/group;dest.mkdir(parents=True,exist_ok=True)
 missing=[(s,t)for s,t in jobs if not t.exists()]
 if missing:
  # FreeMote changes a.scn to a.json. Move its complete dictionary to the
  # stable source-filename.json name; no script content is synthesized.
  args=[str(FM),'-o',str(dest),*[str(s)for s,t in missing]]
  result=subprocess.run(args,capture_output=True,text=True,errors='replace',creationflags=subprocess.CREATE_NO_WINDOW)
  if result.returncode:raise RuntimeError('PSB decoder failed: '+str(group))
  for source,target in missing:
   produced=dest/(source.stem+'.json')
   if produced!=target:produced.replace(target)
  print(json.dumps({'psbGroup':group.as_posix(),'converted':len(missing)}),flush=True)

plan=ROOT/'reports/tlg-conversion-plan.json';plan.write_text(json.dumps(tlg,ensure_ascii=False),'utf8')
script=ROOT/'tools/convert-tlg.ps1'
script.write_text(script.read_text('utf-8-sig'),'utf-8-sig')
subprocess.run([r'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe','-NoProfile','-ExecutionPolicy','Bypass','-File',str(script),'-Plan',str(plan)],check=True)

for i,item in enumerate(rows):
 f=OUT/item['path'];assert f.is_file(),item['originalPath']
 if item['kind']=='png':
  with Image.open(f)as im:
   item.update(width=im.width,height=im.height,mode=im.mode);im.verify()
 elif item['kind']=='json':
  j=json.loads(f.read_text('utf-8-sig'));item['jsonTopLevelType']=type(j).__name__
  if isinstance(j,dict):item['jsonKeys']=list(j)
 item.update(bytes=f.stat().st_size,sha256=sha(f))
 if i%1000==0:print(json.dumps({'convertedFilesVerified':i,'total':len(rows)}),flush=True)
report={'result':'passed','originalFiles':len(manifest),'catalogEntries':len(rows),
        'types':dict(collections.Counter(x['kind']for x in rows)),
        'allImageAndJSONFilesVerified':True,'convertedContentUnfiltered':True,
        'watchPackageMustUseSeparateWhitelist':True,'resources':rows}
(OUT/'resource_catalog.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf8')
(ROOT/'reports/callable-resource-conversion.json').write_text(json.dumps({k:v for k,v in report.items()if k!='resources'},ensure_ascii=False,indent=2)+'\n','utf8')
print(json.dumps({k:v for k,v in report.items()if k!='resources'},ensure_ascii=False),flush=True)
