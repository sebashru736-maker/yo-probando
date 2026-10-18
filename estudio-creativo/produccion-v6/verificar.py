"""Decode and inspect both finished exports, including exact timing and audio."""
from pathlib import Path
import json,subprocess,hashlib,os,re,concurrent.futures
import numpy as np
from PIL import Image,ImageDraw
from plan import ROOT,DURATION
REVIEW=Path('/workspace/hbo-v6/review')

def cmd(args):return subprocess.run(list(map(str,args)),check=True,capture_output=True,text=True)

def verify(video,w,h):
 info=json.loads(cmd(['ffprobe','-v','error','-show_streams','-show_format','-of','json',video]).stdout)
 v=next(x for x in info['streams'] if x['codec_type']=='video');a=next(x for x in info['streams'] if x['codec_type']=='audio')
 assert (v['width'],v['height'],v['avg_frame_rate'],int(v['nb_frames']))==(w,h,'30/1',DURATION*30)
 assert abs(float(info['format']['duration'])-DURATION)<.04
 assert all(v[k]=='bt709' for k in ['color_space','color_transfer','color_primaries'])
 assert (a['channels'],a['sample_rate'])==(2,'48000')
 frames=json.loads(cmd(['ffprobe','-v','error','-select_streams','v:0','-show_frames','-show_entries','frame=best_effort_timestamp_time','-of','json',video]).stdout)['frames']
 ts=np.array([float(x['best_effort_timestamp_time']) for x in frames]);error=float(np.abs(ts-np.arange(DURATION*30)/30).max())
 assert error<1e-5
 decoded=cmd(['ffmpeg','-v','error','-xerror','-i',video,'-f','null','-']);assert not decoded.stderr.strip(),decoded.stderr
 analysis=cmd(['ffmpeg','-hide_banner','-i',video,'-af','loudnorm=I=-14:TP=-1.3:LRA=8:print_format=json','-f','null','-'])
 loud=json.JSONDecoder().raw_decode(analysis.stderr[analysis.stderr.rfind('{'):])[0]
 assert abs(float(loud['input_i'])+14)<.6,loud
 assert float(loud['input_tp'])<-.9,loud
 folder=REVIEW/video.stem;folder.mkdir(exist_ok=True)
 cmd(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',video,'-vf','fps=1','-frames:v',str(DURATION),folder/'%03d.jpg'])
 thumbw,thumbh=(480,270) if w>h else (270,480)
 # Contact sheets in chunks so individual scenes remain readable.
 allpaths=sorted(folder.glob('*.jpg'))
 assert len(allpaths)==DURATION
 for start in range(0,DURATION,16):
  paths=allpaths[start:start+16];sheet=Image.new('RGB',(4*thumbw,4*(thumbh+26)),'#080410');draw=ImageDraw.Draw(sheet)
  for k,p in enumerate(paths):
   x=k%4*thumbw;y=k//4*(thumbh+26)
   im=Image.open(p).resize((thumbw,thumbh));sheet.paste(im,(x,y+26));draw.text((x+8,y+6),f'{start+k:02d} s',fill='white')
  sheet.save(REVIEW/f'{video.stem}-timeline-{start//16+1}.jpg',quality=90)
 env=os.environ.copy();env['OMP_THREAD_LIMIT']='1'
 def ocr(p):
  r=subprocess.run(['tesseract',str(p),'stdout','--psm','11'],env=env,check=True,capture_output=True,text=True)
  return {'frame':p.name,'text':r.stdout}
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:scans=list(pool.map(ocr,allpaths))
 pattern=re.compile(r'\$\s*\d|S/\s*\d|\bBs\.?\s*\d|\b(?:USD|PEN|BOB|precio|descuento|oferta)\b',re.I)
 flagged=[x for x in scans if pattern.search(x['text'])];assert not flagged,flagged
 print(video.name,'OK: fotogramas, timestamps, decodificación, audio, OCR.',flush=True)
 return {'file':video.name,'bytes':video.stat().st_size,'sha256':hashlib.sha256(video.read_bytes()).hexdigest(),'duration_s':DURATION,'width':w,'height':h,'fps':30,'frames':DURATION*30,'max_timestamp_error_s':error,'color':'BT.709','full_decode':True,'audio_channels':2,'audio_sample_rate':48000,'integrated_lufs':float(loud['input_i']),'true_peak_dbtp':float(loud['input_tp']),'ocr_sampled_frames':len(scans),'price_flags':flagged}

if __name__=='__main__':
 outputs=[]
 for suffix,w,h in [('Cine',1920,1080),('Vertical',1080,1920)]:outputs.append(verify(ROOT/f'HBO-Max-Tzubaru-Dragon-{suffix}-38s.mp4',w,h))
 lines=json.loads((ROOT/'audio/locucion.json').read_text())
 result={'outputs':outputs,'voice_model':'Supertonic 3','narrator':'M3','dragon_voice':'M2 + character processing','dragon_segment_s':[28,34],'dragon_dialogue':next(x for x in lines if x['speaker']=='M2'),'source_audio_used':False,'music':'Original instrumental rendered separately with FluidSynth; no dialogue samples','restoration':'Real-ESRGAN general x4v3 + animevideov3; original compressed 576px sources','review_limits':['ASR and visual frame review; no human listening in this environment.','No newly obtained HD source footage. Reconstruction does not guarantee original fine detail.','Dragon dialogue accompanies retimed existing mouth motion, not generated phoneme-level lip sync.']}
 (ROOT/'verificacion.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(result,ensure_ascii=False,indent=2),flush=True)
