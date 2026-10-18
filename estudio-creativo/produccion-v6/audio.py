"""Original instrumental cue; absolutely no audio taken from the source videos."""
from pathlib import Path
import json,wave,subprocess,math
import numpy as np
import fluidsynth
from scipy.signal import butter,sosfilt,resample_poly
from plan import ROOT,WORK,DURATION
SR=48000

def write(path,x):
 with wave.open(str(path),'wb') as f:
  f.setnchannels(2 if x.ndim==2 else 1);f.setsampwidth(2);f.setframerate(SR)
  f.writeframes((np.clip(x,-.999,.999)*32767).astype('<i2').tobytes())

def read(path):
 with wave.open(str(path)) as f:
  sr=f.getframerate();ch=f.getnchannels();x=np.frombuffer(f.readframes(f.getnframes()),'<i2').astype(np.float64).reshape(-1,ch)/32768
 if sr!=SR:
  g=math.gcd(sr,SR);x=resample_poly(x,SR//g,sr//g,axis=0)
 return x

def make_music():
 n=SR*DURATION;events=[]
 def note(at,duration,ch,key,vel):
  if at>=DURATION:return
  events.extend([(int(at*SR),1,ch,key,vel),(min(n,int((at+duration)*SR)),0,ch,key,0)])
 # D-minor orchestral pulse. 120 BPM; each key picture change lands on a beat.
 chords=[(0,[38,50,53,57]),(4,[34,46,50,53]),(8,[41,53,57,60]),(12,[36,48,52,55]),(16,[38,50,53,57]),(20,[34,46,50,53]),(24,[36,48,52,55]),(28,[38,50,53,57]),(32,[34,46,50,53]),(34,[38,50,53,57])]
 for j,(at,keys) in enumerate(chords):
  end=chords[j+1][0] if j+1<len(chords) else 38
  for key in keys[1:]:note(at,end-at-.08,0,key+12,42 if at<4 else 52)
  note(at,end-at-.1,2,keys[0],72)
  if at>=4:
   for key in keys[1:]:note(at,.95,3,key,54)
  step=.5 if at<4 or 28<=at<34 else .25
  for k,t in enumerate(np.arange(at,end-.05,step)):
   key=keys[1+(k%3)]+(12 if k%4==3 else 0)
   note(float(t),step*.74,1,key,64+(k%4==0)*16)
 # A restrained final brass lift supports the CTA.
 for key in [50,57,62,65]:note(34,3.4,3,key,64)
 synth=fluidsynth.Synth(samplerate=SR,gain=.35)
 sf=synth.sfload('/usr/share/sounds/sf2/TimGM6mb.sf2')
 assert sf>=0
 for ch,program in [(0,48),(1,45),(2,43),(3,60)]:synth.program_select(ch,sf,0,program)
 for ch,pan in [(0,42),(1,84),(2,64),(3,56)]:synth.cc(ch,10,pan)
 events.sort(key=lambda e:(e[0],e[1]));music=np.zeros((n,2));pos=0
 for at,kind,ch,key,vel in events+[(n,0,0,0,0)]:
  if at>pos:
   music[pos:at]=synth.get_samples(at-pos).reshape(-1,2).astype(np.float64)/32768;pos=at
  if kind:synth.noteon(ch,key,vel)
  else:synth.noteoff(ch,key)
 synth.delete()
 # Trailer drums and low-frequency pulses, synthesized without speech samples.
 rng=np.random.default_rng(20261018)
 def add(at,x,gain=.1,pan=0):
  start=int(at*SR);count=min(len(x),n-start)
  music[start:start+count,0]+=x[:count]*gain*np.sqrt((1-pan)/2)
  music[start:start+count,1]+=x[:count]*gain*np.sqrt((1+pan)/2)
 for beat in np.arange(0,38,.5):
  if 28.5<=beat<34:continue
  u=np.arange(int(.55*SR))/SR
  kick=np.sin(2*np.pi*(46*u+2.7*(1-np.exp(-u*18))))*np.exp(-u*9)
  kick+=rng.normal(size=len(u))*.12*np.exp(-u*90)
  add(float(beat),kick,.18 if beat%2==0 else .09)
  if beat%1==.5 and beat>=4:
   u=np.arange(int(.22*SR))/SR
   sn=sosfilt(butter(2,[650,7000],btype='bandpass',fs=SR,output='sos'),rng.normal(size=len(u)))*np.exp(-u*20)
   add(float(beat),sn,.045,.1)
 for at in [0,4,10,15,21,28,31.5,34]:
  u=np.arange(int(1.2*SR))/SR
  boom=np.sin(2*np.pi*(34*u+1.8*(1-np.exp(-u*15))))*np.exp(-u*4)
  add(at,boom,.22)
  if at>0:
   u=np.arange(int(.38*SR))/SR
   air=sosfilt(butter(2,[650,5500],btype='bandpass',fs=SR,output='sos'),rng.normal(size=len(u)))
   air*=np.sin(np.pi*np.arange(len(u))/len(u))**2
   add(at-.38,air,.075,-.2)
 music=sosfilt(butter(2,32,btype='highpass',fs=SR,output='sos'),music,axis=0)
 music*=.13/max(np.sqrt(np.mean(music**2)),1e-9)
 music*=np.minimum(np.arange(n)/SR/.08,1)[:,None]
 write(ROOT/'audio/instrumental-original.wav',music)
 return music

def main():
 music=make_music();n=len(music);voice=np.zeros(n);duck=np.ones(n)
 lines=json.loads((ROOT/'audio/locucion.json').read_text())
 for line in lines:
  x=read(ROOT/'audio'/line['path']).mean(axis=1)
  active=x[np.abs(x)>.012];x*=.19/max(np.sqrt(np.mean(active**2)),1e-9)
  x*=min(1,.83/max(np.abs(x).max(),1e-9))
  at=int(line['at']*SR);voice[at:at+len(x)]+=x
  start=max(0,at-int(.12*SR));end=min(n,at+len(x)+int(.25*SR))
  floor=.11 if line['speaker']=='M2' else .20
  env=np.full(end-start,floor)
  attack=at-start;release=end-at-len(x)
  if attack:env[:attack]=np.linspace(1,floor,attack)
  if release:env[-release:]=np.linspace(floor,1,release)
  duck[start:end]=np.minimum(duck[start:end],env)
 write(ROOT/'audio/narracion-aislada.wav',voice)
 # During the dragon's dialogue, the score leaves a deliberate pocket.
 duck[int(28*SR):int(31.5*SR)]=np.minimum(duck[int(28*SR):int(31.5*SR)],.18)
 mix=music*duck[:,None]+voice[:,None]
 t=np.arange(n)/SR;mix*=np.clip((DURATION-t)/.65,0,1)[:,None]
 mix*=.9/max(1,np.abs(mix).max())
 premaster=WORK/'premaster.wav';write(premaster,mix)
 analysis=subprocess.run(['ffmpeg','-hide_banner','-i',str(premaster),'-af','loudnorm=I=-14:TP=-1.3:LRA=8:print_format=json','-f','null','-'],capture_output=True,text=True,check=True)
 m=json.JSONDecoder().raw_decode(analysis.stderr[analysis.stderr.rfind('{'):])[0]
 af=f"loudnorm=I=-14:TP=-1.3:LRA=8:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true"
 subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(premaster),'-af',af,'-ar',str(SR),'-c:a','pcm_s16le',str(ROOT/'audio/master.wav')],check=True)
 (ROOT/'audio/loudness.json').write_text(json.dumps(m,indent=2)+'\n')
 print('Master nuevo: instrumental original, voz M3 y diálogo M2. CERO audio de los clips fuente.',flush=True)

if __name__=='__main__':main()
