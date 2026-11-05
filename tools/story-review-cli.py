"""Read small original text windows; record reviewed ordinary ranges for rebuilding."""
from pathlib import Path
import argparse,json,re
from resource_store import ResourceStore
R=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(description=__doc__);p.add_argument('command',choices=['show','include-reviewed','status']);p.add_argument('storage',nargs='?');p.add_argument('--scene',type=int,default=0);p.add_argument('--start',type=int,default=0);p.add_argument('--count',type=int,default=20);p.add_argument('--indices',help='Example: 10-20,25,28');p.add_argument('--note',help='Required review note when including ordinary narrative')
a=p.parse_args();reviewfile=R/'converted/story-review.json';review=json.loads(reviewfile.read_text('utf8'))
if a.command=='status':
 result={'included':sum(len(x['include'])for x in review['scenes']),'scenes':len(review['scenes']),'instructions':'Read bounded original windows, review context, include only ordinary narrative, then run tools/update.py.'}
else:
 store=ResourceStore();options=[x for x in store.rows if x['kind']=='json'and x['originalPath'].lower().endswith('/'+a.storage.lower()+'.scn')]
 if not options:raise ValueError('Unknown story storage')
 row=next((x for x in options if x['originalPath'].startswith('patch/')),options[0]);data=store.json(row['id']);texts=data['scenes'][a.scene].get('texts',[])
 if a.command=='show':result=store.scene_texts(row['id'],a.scene,a.start,a.count)
 else:
  if not a.indices or not a.note:raise ValueError('Provide explicit inspected indices and a review note; no bulk all-content flag is available')
  indices=set()
  for part in a.indices.split(','):
   if not re.fullmatch(r'\d+(?:-\d+)?',part):raise ValueError('Invalid index range')
   lo,_,hi=part.partition('-');lo=int(lo);hi=int(hi)if hi else lo
   if hi<lo or hi>=len(texts):raise ValueError('Index outside scene')
   indices.update(range(lo,hi+1))
  if len(indices)>200:raise ValueError('Review at most 200 records per batch')
  entry=next(x for x in review['scenes']if x['storage']==a.storage.lower()and x['scene']==a.scene)
  entry['include']=sorted(set(entry['include'])|indices);entry.setdefault('reviewNotes',[]).append({'indices':sorted(indices),'note':a.note})
  reviewfile.write_text(json.dumps(review,ensure_ascii=False,indent=2),'utf8');result={'includedIndices':len(indices),'rebuild':'python tools/update.py','contentBoundary':'Only reviewed non-explicit narrative is supported; this is not an R18 import switch.'}
print(json.dumps(result,ensure_ascii=False,indent=2))
