"""Download official HTTPS model artifacts and verify the recorded SHA-256."""
from pathlib import Path
import urllib.request,tarfile,json,hashlib

ROOT=Path(__file__).resolve().parent
DEST=Path('/workspace/creative-tools/models');DEST.mkdir(parents=True,exist_ok=True)
data=json.loads((ROOT/'MODELOS.json').read_text())

def verify(path,expected):
 assert hashlib.sha256(path.read_bytes()).hexdigest()==expected,f'Checksum distinto: {path}'

def download(row):
 path=DEST/row['file']
 if path.exists():
  verify(path,row['sha256']);return path
 temporary=path.with_suffix(path.suffix+'.part')
 try:
  urllib.request.urlretrieve(row['source'],temporary)
  verify(temporary,row['sha256'])
  temporary.replace(path)
 finally:temporary.unlink(missing_ok=True)
 return path

kokoro=DEST/'kokoro-multi-lang-v1_0'
if not all((kokoro/x).exists() for x in ['model.onnx','voices.bin','tokens.txt','espeak-ng-data']):
 archive=download(data['download_archive'])
 with tarfile.open(archive) as t:t.extractall(DEST,filter='data')
for row in data['artifacts']:
 if row['file'].endswith('.pb'):download(row)
 else:verify(kokoro/row['file'],row['sha256'])
print('Modelos de voz y reescalado disponibles, SHA-256 verificado.')
