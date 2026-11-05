"""One-command reviewed story rebuild; never installs or publishes automatically."""
from pathlib import Path
import argparse,subprocess,sys
R=Path(__file__).resolve().parents[1];p=argparse.ArgumentParser();p.add_argument('--version');a=p.parse_args()
steps=[[sys.executable,'tools/build-story.py']+(['--version',a.version]if a.version else[]),[sys.executable,'tools/build-font.py'],['node','--test',*map(str,sorted((R/'tests').glob('*.test.cjs')))],['node','tools/build.cjs'],[sys.executable,'tools/audit-delivery.py']]
for command in steps:
 print('RUN',command,flush=True);subprocess.run(command,cwd=R,check=True)
