"""Render the user's real-video HBO Max ad. FFmpeg, no external requests at render time."""
from pathlib import Path
import json, subprocess, math, wave
import cv2
import numpy as np
from scipy.signal import resample_poly, butter, sosfilt

ROOT=Path(__file__).resolve().parent
WORK=Path('/workspace/hbo-v5/work')
WORK.mkdir(parents=True,exist_ok=True)
INPUTS={r['id']:r for r in json.loads(Path('/workspace/hbo-final/inputs.json').read_text())}
FONT='/usr/share/fonts/truetype/open-sans/OpenSans-ExtraBold.ttf'
REG='/usr/share/fonts/truetype/open-sans/OpenSans-Semibold.ttf'
PURPLE='0xc284ff'
SR=48000
DURATION=32

# Source in-points were reviewed from the supplied videos, not inferred from titles.
SHOTS=[
 ('4',13.0,1.8,'wide',55),('4',9.1,1.6,'wide',110),
 ('5',3.55,1.4,'tall',0),('4',11.75,1.4,'wide',0),
 ('4',27.4,1.8,'wide',0),('4',20.25,1.2,'wide',0),
 ('3',11.9,1.5,'wide',72),
 ('3',35.8,1.8,'wide',72),('3',47.9,1.5,'wide',72),
 ('1',19.15,1.1,'tall',0),('1',20.28,1.1,'tall',0),
 ('1',21.7,1.0,'tall',0),('1',23.8,1.7,'tall',0),
 ('1',15.3,1.1,'tall',0),('4',5.6,1.4,'wide',0),
 ('1',7.3,1.2,'tall',0),('4',11.65,.8,'wide',0),
 ('4',19.6,1.2,'wide',0),('4',22.3,.6,'wide',0),
 ('1',21.05,.9,'tall',0),('4',14.7,1.0,'wide',0),
 ('4',29.3,1.7,'wide',0),
]
assert round(sum(s[2] for s in SHOTS),6)==28.8

def run(args):
 subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y',*map(str,args)],check=True)

def read_audio(path):
 with wave.open(str(path)) as f:
  sr=f.getframerate();ch=f.getnchannels()
  x=np.frombuffer(f.readframes(f.getnframes()),dtype='<i2').astype(np.float64).reshape(-1,ch)/32768
 if sr!=SR:
  g=math.gcd(sr,SR);x=resample_poly(x,SR//g,sr//g,axis=0)
 return x

def make_audio():
 n=SR*DURATION
 raw=read_audio(WORK/'music-source.wav')
 # Omit the source's spoken introduction. Crossfade the closing music tail.
 music=np.zeros((n,2))
 first=raw[int(3.6*SR):int(32.4*SR)]
 music[:len(first)]=first
 tail=raw[int(28.8*SR):int(32.8*SR)]
 at=int(28*SR);fade=int(.8*SR)
 music[at:at+fade]*=np.linspace(1,0,fade)[:,None]
 tail[:fade]*=np.linspace(0,1,fade)[:,None]
 music[at:at+len(tail)]+=tail
 music=sosfilt(butter(2,45,btype='highpass',fs=SR,output='sos'),music,axis=0)
 music*=.24/max(np.sqrt(np.mean(music**2)),1e-8)
 voice=np.zeros(n)
 duck=np.ones(n)
 lines=json.loads((ROOT/'audio/locucion.json').read_text())
 for line in lines:
  x=read_audio(ROOT/'audio'/line['path']).mean(axis=1)
  # The new voice is already EQ'd and gently compressed. Match phrase energy.
  target_rms=.145 if line['at']<28 else .16
  active=x[np.abs(x)>.012]
  x*=target_rms/max(np.sqrt(np.mean(active**2)),1e-8)
  x*=min(1,.82/max(np.max(np.abs(x)),1e-8))
  at=int(line['at']*SR);count=min(len(x),n-at)
  voice[at:at+count]+=x[:count]
  a=max(0,at-int(.15*SR));b=min(n,at+count+int(.22*SR))
  env=np.ones(b-a)*.13
  attack=at-a;release=b-(at+count)
  if attack:env[:attack]=np.linspace(1,.13,attack)
  if release:env[-release:]=np.linspace(.13,1,release)
  duck[a:b]=np.minimum(duck[a:b],env)
 # Let the moment before the rapid final montage breathe.
 t=np.arange(n)/SR
 duck*=np.where((t>=19.5)&(t<20),.25,1)
 mix=music*duck[:,None]
 mix+=voice[:,None]*np.ones((1,2))
 rng=np.random.default_rng(42)
 for cut in [0,1.8,3.4,6.2,8.0,9.2,14,20,21.4,23.4,25.2,27.1,28.8]:
  at=int(cut*SR);length=min(int(1.15*SR),n-at)
  u=np.arange(length)/SR
  hit=np.sin(2*np.pi*(39*u+1.1*(1-np.exp(-u*24))))*np.exp(-u*6)
  mix[at:at+length]+=hit[:,None]*(.17 if cut in [0,3.4,9.2,14,20,28.8] else .085)
  if cut>.6:
   length=int(.42*SR);u=np.arange(length)/SR
   noise=sosfilt(butter(2,[800,6500],btype='bandpass',fs=SR,output='sos'),rng.normal(size=length))
   env=np.sin(np.pi*np.arange(length)/length)**2
   pan=np.linspace(-.75,.75,length)
   start=at-length
   mix[start:at,0]+=.052*noise*env*np.sqrt((1-pan)/2)
   mix[start:at,1]+=.052*noise*env*np.sqrt((1+pan)/2)
 # Short low wing pulses for the dragon flights. Keep the voice in the centre.
 for at_sec in [6.35,7.15,27.30,27.85]:
  at=int(at_sec*SR);length=int(.28*SR);u=np.arange(length)/SR
  air=sosfilt(butter(2,[90,1100],btype='bandpass',fs=SR,output='sos'),rng.normal(size=length))
  env=np.sin(np.pi*np.arange(length)/length)**2
  mix[at:at+length]+=air[:,None]*env[:,None]*.055
 fadeout=np.clip((32-t)/.75,0,1)
 mix*=fadeout[:,None]
 # Keep the premaster clean, then use a measured two-pass loudness normalization.
 mix*=.91/max(1,np.max(np.abs(mix)))
 premaster=WORK/'premaster.wav'
 with wave.open(str(premaster),'wb') as f:
  f.setnchannels(2);f.setsampwidth(2);f.setframerate(SR);f.writeframes((mix*32767).astype('<i2').tobytes())
 analysis=subprocess.run(['ffmpeg','-hide_banner','-i',str(premaster),'-af','loudnorm=I=-14.5:TP=-1.2:LRA=9:print_format=json','-f','null','-'],capture_output=True,text=True,check=True)
 measured=json.JSONDecoder().raw_decode(analysis.stderr[analysis.stderr.rfind('{'):])[0]
 loud=f"loudnorm=I=-14.5:TP=-1.2:LRA=9:measured_I={measured['input_i']}:measured_TP={measured['input_tp']}:measured_LRA={measured['input_lra']}:measured_thresh={measured['input_thresh']}:offset={measured['target_offset']}:linear=true"
 run(['-i',premaster,'-af',loud,'-ar','48000','-c:a','pcm_s16le',ROOT/'audio/master.wav'])
 (ROOT/'audio/loudness.json').write_text(json.dumps(measured,indent=2)+'\n')

def text_filter(text,size,y,color='white',align='center',start=0,end=100,alpha=None):
 path=WORK/f'text-{len(list(WORK.glob("text-*.txt"))):03d}.txt'
 path.write_text(text)
 x='(w-text_w)/2' if align=='center' else '180'
 f=f"drawtext=fontfile={FONT if size>40 else REG}:textfile={path}:fontcolor={color}:fontsize={size}:x={x}:y={y}:shadowcolor=black@0.7:shadowx=0:shadowy=3:enable='between(t,{start},{end})'"
 if alpha:f+=f":alpha='{alpha}'"
 return f

def chapter(at):
 if at<3.4:return ('¿QUÉ HISTORIA','VAS A VIVIR HOY?',72,'Elige cómo quieres sentirte.')
 if at<9.2:return ('SIENTE CADA','BATALLA.',87,'Fantasía que te deja sin aliento.')
 if at<14:return ('HISTORIAS','QUE TE ATRAPAN.',78,'Personajes que se quedan contigo.')
 if at<20:return ('AVENTURAS','PARA COMPARTIR.',76,'Una gran historia también se vive en familia.')
 return ('TU PRÓXIMA','GRAN HISTORIA.',80,'Haz de cualquier noche un plan inolvidable.')

def prepare_shot(i,shot):
 """Clean at native resolution, then FSRCNN 2x without cropping away the sides."""
 source,begin,duration,kind,_=shot
 crop='crop=576:288:0:368' if source=='4' else ('crop=576:324:0:350' if kind=='wide' else 'crop=576:780:0:0')
 w,h=576,(288 if source=='4' else (324 if kind=='wide' else 780))
 dest=WORK/f'clean-{i:02d}.mkv'
 if dest.exists():return dest
 sr=cv2.dnn_superres.DnnSuperResImpl_create()
 sr.readModel('/workspace/creative-tools/models/FSRCNN_x2.pb');sr.setModel('fsrcnn',2)
 cv2.setNumThreads(2)
 decoder=subprocess.Popen(['ffmpeg','-hide_banner','-loglevel','error','-threads','1','-ss',str(begin),'-i',INPUTS[source]['path'],
  '-vf',f'fps=30,{crop},hqdn3d=0.7:0.7:2:2','-frames:v',str(round(duration*30)),
  '-an','-threads','1','-pix_fmt','bgr24','-f','rawvideo','pipe:1'],stdout=subprocess.PIPE)
 encoder=subprocess.Popen(['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pixel_format','bgr24',
  '-video_size',f'{w*2}x{h*2}','-framerate','30','-i','pipe:0','-an','-c:v','ffv1','-level','3','-pix_fmt','bgr0','-threads','1',str(dest)],stdin=subprocess.PIPE)
 count=0
 try:
  while data:=decoder.stdout.read(w*h*3):
   assert len(data)==w*h*3
   frame=np.frombuffer(data,dtype=np.uint8).reshape(h,w,3)
   enlarged=sr.upsample(frame)
   encoder.stdin.write(enlarged.tobytes());count+=1
  encoder.stdin.close()
  assert decoder.wait()==0
  assert encoder.wait()==0
  assert count==round(duration*30),(i,count)
 except BaseException:
  decoder.kill();encoder.kill();dest.unlink(missing_ok=True);raise
 return dest

def render_shot(i,shot,at):
 source,begin,duration,kind,x=shot
 path=prepare_shot(i,shot)
 if kind=='wide':
  pre='eq=gamma=1.10:saturation=1.05'
  fore='scale=1080:-2:flags=lanczos,unsharp=3:3:0.20:3:3:0'
  fy=520 if source!='4' else 554
 else:
  pre='eq=saturation=0.99:contrast=1.01'
  fore='scale=1080:1462:flags=lanczos,unsharp=3:3:0.15:3:3:0'
  fy=190
 graph=f"[0:v]fps=30,trim=duration={duration},setpts=PTS-STARTPTS,{pre},split=2[bg0][fg0];[bg0]scale=270:480:force_original_aspect_ratio=increase,crop=270:480,boxblur=14:2,scale=1080:1920,eq=brightness=-0.23:saturation=0.65[bg];[fg0]{fore}[fg];[bg][fg]overlay=0:{fy},setsar=1"
 overlays=[
  'drawbox=x=0:y=0:w=iw:h=420:color=0x070511@0.90:t=fill',
  'drawbox=x=0:y=1420:w=iw:h=500:color=0x070511@0.98:t=fill',
  text_filter('HBO max',40,185),
 ]
 line1,line2,size,benefit=chapter(at)
 overlays += [text_filter(line1,size,265),text_filter(line2,size,360,PURPLE)]
 # A quiet lower strip holds the value statement, away from the faces.
 if kind=='wide':
  tag='LA CASA DEL DRAGÓN' if source=='4' else 'HISTORIAS EN HBO MAX'
  overlays += [text_filter(tag,25,1160,PURPLE)]
 overlays += ['drawbox=x=0:y=1260:w=iw:h=160:color=0x070511@0.92:t=fill',text_filter(benefit,30,1306), 'drawbox=x=180:y=1385:w=720:h=2:color=0x67517c@0.65:t=fill']
 progress=int(720*(at+duration)/DURATION)
 overlays += [f'drawbox=x=180:y=1385:w={progress}:h=2:color={PURPLE}:t=fill',text_filter('tzubaru',24,1452), 'format=yuv420p']
 graph+=','+','.join(overlays)+'[v]'
 out=WORK/f'shot-{i:02d}.mkv'
 run(['-i',path,'-filter_complex_threads','1','-filter_complex',graph,'-map','[v]','-an','-frames:v',round(duration*30),'-c:v','ffv1','-level','3','-threads','2',out])
 return out

def render_end():
 logo=Path('/workspace/yo-probando/estudio-creativo/public/tzubaru.png')
 graph="[0:v]scale=1080:1920,format=yuv420p[base];[1:v]scale=380:-1:flags=lanczos[logo];[base][logo]overlay=(W-w)/2:925"
 filters=[
  'drawbox=x=180:y=280:w=720:h=3:color=0xa45dff:t=fill',
  text_filter('TU PRÓXIMA',75,345),text_filter('GRAN HISTORIA.',75,440,PURPLE),
  text_filter('HBO',110,630),text_filter('max',108,748),
  'drawbox=x=220:y=1300:w=640:h=92:color=0x793bd5:t=fill',
  text_filter('ESCRÍBENOS',47,1313),
  text_filter('Y ADQUIERE HBO MAX',32,1435),
  'fade=t=in:st=0:d=0.16','fade=t=out:st=3.0:d=0.2','format=yuv420p',
 ]
 graph+=','+','.join(filters)+'[v]'
 out=WORK/'end.mkv'
 run(['-f','lavfi','-i','color=c=0x0b051b:s=1080x1920:r=30:d=3.2','-loop','1','-i',logo,'-filter_complex_threads','1','-filter_complex',graph,'-map','[v]','-an','-frames:v','96','-c:v','ffv1','-level','3','-threads','2',out])
 return out

def mux_final(output):
 # Source files have different color metadata. Decode each independently before
 # combining frames so FFmpeg cannot reset filter state at a color-space change.
 final=ROOT/'HBO-Max-Tzubaru-Voz-Masculina-V2.mp4'
 temporary=ROOT/'export-temporal.mp4'
 encoder=subprocess.Popen(['ffmpeg','-hide_banner','-loglevel','error','-y',
  '-f','rawvideo','-pixel_format','yuv420p','-video_size','1080x1920','-framerate','30','-i','pipe:0',
  '-i',str(ROOT/'audio/master.wav'),'-map','0:v:0','-map','1:a:0',
  '-c:v','libx264','-preset','slow','-crf','16','-threads','3',
  '-color_range','tv','-colorspace','bt709','-color_trc','bt709','-color_primaries','bt709',
  '-bsf:v','h264_metadata=colour_primaries=1:transfer_characteristics=1:matrix_coefficients=1:video_full_range_flag=0',
  '-c:a','aac','-b:a','256k','-t','32','-movflags','+faststart',str(temporary)],stdin=subprocess.PIPE)
 frame_bytes=1080*1920*3//2
 total_frames=0
 try:
  for i,path in enumerate(output):
   decoder=subprocess.Popen(['ffmpeg','-hide_banner','-loglevel','error','-threads','1','-i',str(path),
    '-map','0:v:0','-an','-sn','-vf','scale=out_color_matrix=bt709:out_range=tv',
    '-fps_mode','passthrough','-pix_fmt','yuv420p','-threads','1','-f','rawvideo','pipe:1'],stdout=subprocess.PIPE)
   count=0
   while data:=decoder.stdout.read(1024*1024):
    count+=len(data);encoder.stdin.write(data)
   if decoder.wait()!=0:raise RuntimeError(f'Error decodificando {path}')
   assert count%frame_bytes==0
   total_frames+=count//frame_bytes
   print(f'Unión de imagen {i+1}/{len(output)}; {total_frames} fotogramas.',flush=True)
  encoder.stdin.close()
  assert total_frames==960,total_frames
  if encoder.wait()!=0:raise RuntimeError('Falló la codificación final')
 except BaseException:
  encoder.kill();encoder.wait();raise
 temporary.replace(final)
 return final

if __name__=='__main__':
 make_audio()
 print('Master de música, voz y efectos terminado.',flush=True)
 output=[];time=0;edl=[]
 for i,shot in enumerate(SHOTS):
  output.append(render_shot(i,shot,time))
  edl.append({'timeline_in':round(time,3),'source':shot[0],'source_in':shot[1],'duration':shot[2],'layout':shot[3]})
  time+=shot[2]
  print(f'Plano {i+1}/{len(SHOTS)} terminado.',flush=True)
 output.append(render_end())
 (WORK/'concat.txt').write_text(''.join(f"file '{p}'\n" for p in output))
 final=mux_final(output)
 (ROOT/'edicion.json').write_text(json.dumps(edl,indent=2)+'\n')
 print('VIDEO TERMINADO:',final,flush=True)
