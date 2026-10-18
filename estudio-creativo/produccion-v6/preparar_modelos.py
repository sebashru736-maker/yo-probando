"""Cache official artifacts over verified HTTPS and enforce the recorded hashes."""
from pathlib import Path
import json,hashlib,urllib.request,tarfile
ROOT=Path(__file__).resolve().parent
BASE=Path('/workspace/creative-tools/models');BASE.mkdir(exist_ok=True,parents=True)
data=json.loads((ROOT/'MODELOS.json').read_text())
def verify(p,sha):
 assert hashlib.sha256(p.read_bytes()).hexdigest()==sha,f'Checksum distinto: {p}'
for row in data['artifacts']:
 p=BASE/row['file']
 if not p.exists():
  temp=p.with_suffix(p.suffix+'.part')
  try:
   urllib.request.urlretrieve(row['source'],temp);verify(temp,row['sha256']);temp.replace(p)
  finally:temp.unlink(missing_ok=True)
 verify(p,row['sha256'])
 if p.name.endswith('.tar.bz2'):
  dest=BASE/p.name.removesuffix('.tar.bz2')
  if not dest.exists():
   with tarfile.open(p) as t:t.extractall(BASE,filter='data')
  for f in data['supertonic_files']:verify(dest/f['file'],f['sha256'])
print('Supertonic 3 y Real-ESRGAN disponibles; huellas verificadas.')
