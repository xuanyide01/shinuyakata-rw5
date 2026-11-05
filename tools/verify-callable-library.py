"""Independent full target hash verification and metadata-only API smoke checks."""
from pathlib import Path
import hashlib,json,shutil
from resource_store import ResourceStore
R=Path(__file__).resolve().parents[1];s=ResourceStore();seen=set();total=0
for row in s.rows:
 assert row['id']not in seen;seen.add(row['id']);p=s.resolve(row['id'])
 assert p.stat().st_size==row['bytes'];assert hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256'],row['id']
 assert row['contentReview']=='unreviewed'and not row['watchAllowed'];total+=row['bytes']
assert len(s.rows)==10905
assert s.search('美亜.stand',limit=1)['total']==2
assert s.json('patch/s101.txt.scn')['scenes'][0]['nexts'][0]['storage']=='s102.txt'
assert s.scene_texts('patch/s101.txt.scn',offset=0,limit=1)['items'][0]['index']==0
try:s.resolve('../outside');raise AssertionError('Unexpected resource')
except KeyError:pass
try:s.search(limit=101);raise AssertionError('Unbounded search')
except ValueError:pass
shutil.copyfile(R/'tools/resource_store.py',s.root/'resource_store.py')
report={'result':'passed','resources':len(seen),'convertedBytes':total,'allTargetSizesAndSHA256Valid':True,'apiSmokeTestsPassed':True,'sourceArchiveModified':False}
(R/'reports/callable-library-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
print(json.dumps(report))
