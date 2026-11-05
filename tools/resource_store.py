"""Bounded, read-only file API for a local coding agent. Never executes original scripts."""
from pathlib import Path
import argparse, json, sys

class ResourceStore:
 def __init__(self,root=None):
  here=Path(__file__).resolve().parent
  self.root=Path(root or (here if(here/'resource_catalog.json').is_file()else here.parents[1]/'可调用资源')).resolve()
  self.catalog=json.loads((self.root/'resource_catalog.json').read_text('utf8'))
  self.rows=self.catalog['resources']
  self.by_id={r['id']:r for r in self.rows}
  self.by_original={r['originalPath']:r for r in self.rows}
 def get(self,key):
  row=self.by_id.get(key)or self.by_original.get(key)
  if row is None:raise KeyError('Unknown resource id or originalPath')
  return row
 def resolve(self,key):
  p=(self.root/self.get(key)['path']).resolve()
  if not p.is_relative_to(self.root):raise ValueError('Resource path escapes root')
  if not p.is_file():raise FileNotFoundError(p)
  return p
 def search(self,query='',kind=None,offset=0,limit=20):
  if offset<0 or not 1<=limit<=100:raise ValueError('Invalid pagination')
  rows=[r for r in self.rows if query.casefold()in r['originalPath'].casefold()and(kind is None or kind==r['kind'])]
  return {'total':len(rows),'offset':offset,'items':rows[offset:offset+limit]}
 def text(self,key,offset=0,limit=2000):
  if self.get(key)['kind']!='utf8':raise ValueError('Not UTF-8 text')
  if offset<0 or not 1<=limit<=20000:raise ValueError('Invalid text window')
  data=self.resolve(key).read_text('utf8')
  return {'totalCharacters':len(data),'offset':offset,'text':data[offset:offset+limit]}
 def json(self,key):
  if self.get(key)['kind']!='json':raise ValueError('Not JSON')
  return json.loads(self.resolve(key).read_text('utf-8-sig'))
 def scene_texts(self,key,scene=0,offset=0,limit=20,include_state=False):
  if offset<0 or not 1<=limit<=100:raise ValueError('Invalid pagination')
  data=self.json(key);s=data['scenes'][scene];texts=s.get('texts',[])
  return {'scene':scene,'title':s.get('title'),'nexts':s.get('nexts'),'total':len(texts),'offset':offset,
   'items':[dict({'index':i,'speaker':t[0],'voice':t[1],'text':t[2]},**({'originalTuple':t}if include_state else{}))for i,t in enumerate(texts[offset:offset+limit],offset)]}

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path)
 p.add_argument('command',choices=['search','resolve','text','scene-texts','inspect']);p.add_argument('key',nargs='?',default='')
 p.add_argument('--kind');p.add_argument('--offset',type=int,default=0);p.add_argument('--limit',type=int,default=20);p.add_argument('--scene',type=int,default=0);p.add_argument('--state',action='store_true')
 args=p.parse_args();store=ResourceStore(args.root)
 if args.command=='search':result=store.search(args.key,args.kind,args.offset,args.limit)
 elif args.command=='resolve':result={'resource':store.get(args.key),'absolutePath':str(store.resolve(args.key))}
 elif args.command=='text':result=store.text(args.key,args.offset,args.limit)
 elif args.command=='scene-texts':result=store.scene_texts(args.key,args.scene,args.offset,args.limit,args.state)
 else:
  data=store.json(args.key);result={'keys':list(data),'scenes':[{'index':i,'title':s.get('title'),'label':s.get('label'),'texts':len(s.get('texts',[])),'nexts':s.get('nexts')}for i,s in enumerate(data.get('scenes',[]))]}
 print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
