"""Verification on the exported media, not just the rendering script."""
from pathlib import Path
import subprocess,json,hashlib,os,re,concurrent.futures
import numpy as np
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parent
VIDEO=ROOT/'HBO-Max-Tzubaru-Voz-Masculina-V2.mp4'
REVIEW=Path('/workspace/hbo-v5/review');REVIEW.mkdir(parents=True,exist_ok=True)

def cmd(args):
 return subprocess.run(list(map(str,args)),check=True,capture_output=True,text=True)

meta=json.loads(cmd(['ffprobe','-v','error','-show_streams','-show_format','-of','json',VIDEO]).stdout)
v=next(x for x in meta['streams'] if x['codec_type']=='video')
a=next(x for x in meta['streams'] if x['codec_type']=='audio')
assert (v['width'],v['height'],v['avg_frame_rate'],int(v['nb_frames']))==(1080,1920,'30/1',960)
assert abs(float(meta['format']['duration'])-32)<.04
assert a['channels']==2 and int(a['sample_rate'])==48000
assert all(v[k]=='bt709' for k in ['color_space','color_primaries','color_transfer'])
raw=cmd(['ffprobe','-v','error','-select_streams','v:0','-show_frames','-show_entries','frame=best_effort_timestamp_time','-of','json',VIDEO])
frames=json.loads(raw.stdout)['frames']
ts=np.array([float(x['best_effort_timestamp_time']) for x in frames])
assert len(ts)==960 and np.max(np.abs(ts-np.arange(960)/30))<1e-5
decode=cmd(['ffmpeg','-v','error','-xerror','-i',VIDEO,'-f','null','-'])
assert not decode.stderr.strip(),decode.stderr
print('Duración, 960 timestamps, color y decodificación completos: OK',flush=True)

analysis=cmd(['ffmpeg','-hide_banner','-i',VIDEO,'-af','loudnorm=I=-14.5:TP=-1.2:LRA=9:print_format=json','-f','null','-'])
loud=json.JSONDecoder().raw_decode(analysis.stderr[analysis.stderr.rfind('{'):])[0]
assert abs(float(loud['input_i'])+14.5)<.5,loud
assert float(loud['input_tp'])<-.8,loud

fr=REVIEW/'frames';fr.mkdir(exist_ok=True)
cmd(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',VIDEO,'-vf','fps=2,scale=270:480','-frames:v','64',fr/'%03d.jpg'])
paths=sorted(fr.glob('*.jpg'))
assert len(paths)==64
sheet=Image.new('RGB',(8*270,8*506),'#06040d');draw=ImageDraw.Draw(sheet)
for i,p in enumerate(paths):
 im=Image.open(p);x=(i%8)*270;y=(i//8)*506
 sheet.paste(im,(x,y+26));draw.text((x+8,y+7),f'{i/2:04.1f} s',fill='white')
sheet.save(REVIEW/'timeline.jpg',quality=90)

# OCR at original output size, once per second. Use one OpenMP thread per worker.
ocr=REVIEW/'ocr-frames';ocr.mkdir(exist_ok=True)
cmd(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',VIDEO,'-vf','fps=1','-frames:v','32',ocr/'%03d.jpg'])
env=os.environ.copy();env['OMP_THREAD_LIMIT']='1'
def scan(p):
 s=subprocess.run(['tesseract',str(p),'stdout','--psm','11'],env=env,check=True,capture_output=True,text=True).stdout
 return {'frame':p.name,'text':s}
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
 scans=list(pool.map(scan,sorted(ocr.glob('*.jpg'))))
pattern=re.compile(r'\$\s*\d|S/\s*\d|\bBs\.?\s*\d|\b(?:USD|PEN|BOB|precio|descuento|oferta)\b',re.I)
flagged=[x for x in scans if pattern.search(x['text'])]
assert not flagged,flagged
(ROOT/'verificacion-precios.json').write_text(json.dumps({'sampled_frames':32,'flagged':flagged,'ocr':scans},ensure_ascii=False,indent=2)+'\n')

lines=json.loads((ROOT/'audio/locucion.json').read_text())
assert all(x['at']+x['duration']<31.35 for x in lines)
result={'file':VIDEO.name,'bytes':VIDEO.stat().st_size,'sha256':hashlib.sha256(VIDEO.read_bytes()).hexdigest(),
 'duration_s':float(meta['format']['duration']),'video':{'width':1080,'height':1920,'fps':30,'frames':960,'color':'BT.709','last_frame_s':float(ts[-1]),'max_timestamp_error_s':float(np.max(np.abs(ts-np.arange(960)/30)))},
 'audio':{'sample_rate':48000,'channels':2,'integrated_lufs':float(loud['input_i']),'true_peak_dbtp':float(loud['input_tp']),'last_voice_end_s':max(x['at']+x['duration'] for x in lines)},
 'checks':{'full_decode':True,'constant_timestamps':True,'ocr_no_prices_32_frames':True,'visual_contact_sheet':'/workspace/hbo-v5/review/timeline.jpg'},
 'limits':['Las referencias comprimidas de 576 píxeles no tienen detalle HD nativo.','OCR por muestreo; selección de planos revisada visualmente.','La locución se comprueba mediante transcripción automática, no una escucha humana.']}
(ROOT/'verificacion.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(result,ensure_ascii=False,indent=2),flush=True)
