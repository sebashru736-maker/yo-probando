"""38-second edit in landscape and vertical formats; source video audio is never mapped."""
from pathlib import Path
import subprocess,json
from plan import ROOT,WORK,SHOTS,DURATION,chapter

FONT='/usr/share/fonts/truetype/open-sans/OpenSans-ExtraBold.ttf'
REG='/usr/share/fonts/truetype/open-sans/OpenSans-Semibold.ttf'
PURPLE='0xc58bff'

def run(args):subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y',*map(str,args)],check=True)

def text(label,size,x,y,color='white',regular=False):
 name=WORK/f'text-{len(list(WORK.glob("text-*.txt"))):04d}.txt';name.write_text(label)
 return f"drawtext=fontfile={REG if regular else FONT}:textfile={name}:fontsize={size}:fontcolor={color}:x={x}:y={y}:shadowcolor=black@0.65:shadowy=2"

def shot(i,at,vertical):
 source,_,duration,kind,_=SHOTS[i]
 w,h=(1080,1920) if vertical else (1920,1080)
 inp=WORK/f'clean-{i:02d}.mkv';out=WORK/f'{"vertical" if vertical else "panoramico"}-{i:02d}.mkv'
 if out.exists():return out
 pre='eq=gamma=1.09:contrast=1.035:saturation=1.06' if source=='4' else 'eq=contrast=1.025:saturation=1.02'
 start=f'[0:v]fps=30,tpad=stop_mode=clone:stop_duration=0.10,trim=duration={duration},setpts=PTS-STARTPTS,{pre},split=2[b0][f0]'
 bg=f'[b0]scale={w//4}:{h//4}:force_original_aspect_ratio=increase,crop={w//4}:{h//4},boxblur=13:2,scale={w}:{h},eq=brightness=-0.16:saturation=0.65[bg]'
 if vertical:
  if kind in ['wide','dragon']:
   fg='scale=1080:-2:flags=lanczos';fy='(H-h)/2-110'
  else:fg='scale=1080:-2:flags=lanczos';fy='(H-h)/2-40'
 else:
  if source=='4':fg='crop=1920:800:0:0';fy='160'
  elif kind=='wide':fg='scale=1920:1080:flags=lanczos';fy='0'
  else:fg='scale=-2:1080:flags=lanczos';fy='0'
 graph=f'{start};{bg};[f0]{fg}[fg];[bg][fg]overlay=(W-w)/2:{fy},setsar=1'
 first,second,benefit=chapter(at)
 if vertical:
  filters=['drawbox=x=0:y=0:w=iw:h=450:color=0x080410@0.94:t=fill',
   'drawbox=x=0:y=1460:w=iw:h=460:color=0x080410@0.95:t=fill',
   text('HBO max',38,'(w-text_w)/2',160,regular=True),
   text(first,62 if at<28 else 55,'(w-text_w)/2',257),
   text(second,67 if at<28 else 48,'(w-text_w)/2',347,PURPLE),
   'drawbox=x=0:y=1275:w=iw:h=185:color=0x080410@0.94:t=fill',
   text(benefit,30 if at<28 else 42,'(w-text_w)/2',1336,PURPLE if at>=28 else 'white',regular=at<28),
   text('tzubaru',26,'(w-text_w)/2',1500,regular=True)]
  if at>=28:filters.append(text('« Disponible en Tzubaru »',35,'(w-text_w)/2',1190))
  filters.extend(['drawbox=x=180:y=1422:w=720:h=3:color=0x4d365e:t=fill',f'drawbox=x=180:y=1422:w={round(720*(at+duration)/DURATION)}:h=3:color={PURPLE}:t=fill'])
 else:
  filters=['drawbox=x=0:y=0:w=iw:h=160:color=0x080410@0.90:t=fill',
   'drawbox=x=0:y=960:w=iw:h=120:color=0x080410@0.96:t=fill',
   text(first,36,72,30),text(second,54,72,78,PURPLE),text('HBO max',39,'w-text_w-72',63,regular=True),
   text(benefit,31 if at<28 else 46,'(w-text_w)/2',990,PURPLE if at>=28 else 'white',regular=at<28),
   'drawbox=x=0:y=1075:w=iw:h=5:color=0x4d365e:t=fill',
   f'drawbox=x=0:y=1075:w={round(w*(at+duration)/DURATION)}:h=5:color={PURPLE}:t=fill']
  if at>=28:filters.append(text('« Disponible en Tzubaru »',40,'(w-text_w)/2',886))
 filters.append('format=yuv420p')
 graph+=','+','.join(filters)+'[v]'
 run(['-i',inp,'-filter_complex_threads','1','-filter_complex',graph,'-map','[v]','-an','-frames:v',round(duration*30),'-c:v','ffv1','-level','3','-threads','2',out])
 return out

def end(vertical):
 w,h=(1080,1920) if vertical else (1920,1080)
 out=WORK/f'{"vertical" if vertical else "panoramico"}-end.mkv'
 logo=ROOT.parent/'public/tzubaru.png'
 if vertical:
  graph='[0:v]format=yuv420p[b];[1:v]scale=470:-1:flags=lanczos[l];[b][l]overlay=(W-w)/2:800'
  filters=[text('TU PRÓXIMA',69,'(w-text_w)/2',260),text('GRAN HISTORIA.',69,'(w-text_w)/2',355,PURPLE),text('HBO',106,'(w-text_w)/2',540),text('max',106,'(w-text_w)/2',655),
   'drawbox=x=180:y=1330:w=720:h=100:color=0x793bd5:t=fill',text('ESCRÍBENOS',51,'(w-text_w)/2',1344),text('DISPONIBLE EN TZUBARU',32,'(w-text_w)/2',1480)]
 else:
  graph='[0:v]format=yuv420p[b];[1:v]scale=620:-1:flags=lanczos[l];[b][l]overlay=150:310'
  filters=[text('TU PRÓXIMA GRAN HISTORIA',76,'(w-text_w)/2',110),text('HBO',123,1110,300),text('max',123,1110,440),
   'drawbox=x=990:y=670:w=650:h=112:color=0x793bd5:t=fill',text('ESCRÍBENOS',56,1120,691),text('DISPONIBLE EN TZUBARU',34,1070,840)]
 filters+=['fade=t=in:st=0:d=0.18','fade=t=out:st=3.70:d=0.30','format=yuv420p']
 graph+=','+','.join(filters)+'[v]'
 run(['-f','lavfi','-i',f'color=c=0x090414:s={w}x{h}:r=30:d=4','-loop','1','-i',logo,'-filter_complex_threads','1','-filter_complex',graph,'-map','[v]','-an','-frames:v','120','-c:v','ffv1','-level','3','-threads','2',out])
 return out

def mux(paths,vertical):
 w,h=(1080,1920) if vertical else (1920,1080)
 name=f'HBO-Max-Tzubaru-Dragon-{"Vertical" if vertical else "Cine"}-38s.mp4'
 final=ROOT/name;temp=ROOT/('export-'+name)
 encoder=subprocess.Popen(['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pixel_format','yuv420p','-video_size',f'{w}x{h}','-framerate','30','-i','pipe:0','-i',str(ROOT/'audio/master.wav'),'-map','0:v:0','-map','1:a:0','-c:v','libx264','-preset','slow','-crf','15','-maxrate','16M','-bufsize','32M','-threads','3','-color_range','tv','-colorspace','bt709','-color_trc','bt709','-color_primaries','bt709','-bsf:v','h264_metadata=colour_primaries=1:transfer_characteristics=1:matrix_coefficients=1:video_full_range_flag=0','-c:a','aac','-b:a','320k','-t',str(DURATION),'-movflags','+faststart',str(temp)],stdin=subprocess.PIPE)
 total=0;frame_bytes=w*h*3//2
 try:
  for i,path in enumerate(paths):
   decoder=subprocess.Popen(['ffmpeg','-hide_banner','-loglevel','error','-threads','1','-i',str(path),'-map','0:v:0','-an','-vf','scale=out_color_matrix=bt709:out_range=tv','-fps_mode','passthrough','-pix_fmt','yuv420p','-threads','1','-f','rawvideo','pipe:1'],stdout=subprocess.PIPE)
   count=0
   while raw:=decoder.stdout.read(1024*1024):encoder.stdin.write(raw);count+=len(raw)
   assert decoder.wait()==0;assert count%frame_bytes==0;total+=count//frame_bytes
   print(name,f'unión {i+1}/{len(paths)}: {total} fotogramas.',flush=True)
  encoder.stdin.close();assert total==DURATION*30;assert encoder.wait()==0
 except BaseException:encoder.kill();raise
 temp.replace(final);return final

if __name__=='__main__':
 edl=[];at=0
 for i,s in enumerate(SHOTS):
  edl.append({'timeline_in':at,'source':s[0],'source_in':s[1],'duration':s[2],'source_duration':s[4],'layout':s[3]});at=round(at+s[2],3)
 (ROOT/'edicion.json').write_text(json.dumps(edl,indent=2)+'\n')
 for vertical in [False,True]:
  paths=[];at=0
  for i,s in enumerate(SHOTS):
   paths.append(shot(i,at,vertical));at=round(at+s[2],3)
   print('Plano',i+1,'vertical' if vertical else 'panorámico','terminado.',flush=True)
  paths.append(end(vertical));print('TERMINADO',mux(paths,vertical),flush=True)
