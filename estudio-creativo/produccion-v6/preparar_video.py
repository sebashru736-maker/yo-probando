from pathlib import Path
import subprocess,hashlib,json,cv2,numpy as np,time,math
from plan import ROOT,WORK,INPUTS,SHOTS
from restore import model,upscale

def prepare(indices=None):
 cache=WORK/'cache';cache.mkdir(exist_ok=True)
 models={}
 for i,(source,begin,duration,kind,native_duration) in enumerate(SHOTS):
  if indices is not None and i not in indices:continue
  out=WORK/f'clean-{i:02d}.mkv'
  if out.exists():print(f'Imagen {i+1}/{len(SHOTS)} ya preparada.',flush=True);continue
  animation=source=='1'
  if animation not in models:models[animation]=model(animation)
  w,h=(576,288) if source=='4' else ((576,324) if kind=='wide' else (576,700))
  crop=f'crop={w}:{h}:0:'+('368' if source=='4' else ('350' if kind=='wide' else '30'))
  fps=25 if source=='4' else (30 if source=='1' else 24)
  retime=abs(duration-native_duration)>.01
  if retime:
   fps=30
   vf=f'{crop},setpts=PTS*{duration/native_duration},minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc:me_mode=bidir'
  else:vf=f'{crop},fps={fps}'
  count=round(duration*fps)
  # tpad provides the few handle frames required by motion interpolation.
  vf+=f',tpad=stop_mode=clone:stop_duration=0.15,trim=end_frame={count}'
  decoder=subprocess.Popen(['ffmpeg','-hide_banner','-loglevel','error','-threads','1','-ss',str(begin),'-t',str(native_duration+.12),'-i',INPUTS[source]['path'],'-vf',vf,'-frames:v',str(count),'-an','-pix_fmt','bgr24','-threads','1','-f','rawvideo','pipe:1'],stdout=subprocess.PIPE)
  ow=1920 if kind in ['wide','dragon'] else 1080;oh=round(h/w*ow/2)*2
  encoder=subprocess.Popen(['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pixel_format','bgr24','-video_size',f'{ow}x{oh}','-framerate',str(fps),'-i','pipe:0','-an','-c:v','ffv1','-level','3','-pix_fmt','bgr0','-threads','1',str(out)],stdin=subprocess.PIPE)
  n=0;started=time.time()
  try:
   while raw:=decoder.stdout.read(w*h*3):
    assert len(raw)==w*h*3
    x=np.frombuffer(raw,np.uint8).reshape(h,w,3)
    digest=hashlib.sha256(raw+str(animation).encode()).hexdigest();cached=cache/(digest+'.png')
    if cached.exists():y=cv2.imread(str(cached))
    else:
     restored=upscale(models[animation],x)
     restored=cv2.resize(restored,(ow,oh),interpolation=cv2.INTER_AREA)
     native=cv2.resize(x,(ow,oh),interpolation=cv2.INTER_LANCZOS4)
     # Retain some genuine source texture and limit the GAN's invented detail.
     y=cv2.addWeighted(restored,.85,native,.15,0)
     cv2.imwrite(str(cached),y,[cv2.IMWRITE_PNG_COMPRESSION,1])
    encoder.stdin.write(y.tobytes());n+=1
   encoder.stdin.close();assert decoder.wait()==0;assert encoder.wait()==0
   assert n==count,(i,n,count)
  except BaseException:
   decoder.kill();encoder.kill();out.unlink(missing_ok=True);raise
  print(f'Imagen {i+1}/{len(SHOTS)} restaurada; {n} fotogramas, {time.time()-started:.1f}s.',flush=True)

if __name__=='__main__':prepare()
