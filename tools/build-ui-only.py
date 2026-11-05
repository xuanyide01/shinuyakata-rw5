"""UI-only build entry; does not invoke story, portrait, translation or font generators."""
from pathlib import Path
import argparse,json,os,subprocess,sys
R=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--version');p.add_argument('--assets',action='store_true');a=p.parse_args()
env=os.environ.copy()
if not env.get('WATCH_COMPAT_TOOLKIT'):
 for candidate in [R/'tools/compat-toolkit/node_modules/aiot-toolkit',R.parent/'源码/tools/compat-toolkit/node_modules/aiot-toolkit']:
  if(candidate/'package.json').is_file():env['WATCH_COMPAT_TOOLKIT']=str(candidate);break
if a.version:
 m=json.loads((R/'src/manifest.json').read_text('utf8'));m['versionName']=a.version;m['versionCode']+=1
 (R/'src/manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n','utf8')
 q=json.loads((R/'package.json').read_text('utf8'));q['version']=a.version
 (R/'package.json').write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n','utf8')
steps=([['node','tools/build-ui-classic.cjs']]if a.assets else[])+[['node','--test',*map(str,sorted((R/'tests').glob('*.test.cjs')))],['node','tools/build.cjs'],[sys.executable,'tools/audit-ui-only.py']]
for command in steps:
 print('RUN',command,flush=True);subprocess.run(command,cwd=R,env=env,check=True)
