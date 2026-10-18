"""New native Spanish male voice; no pitch-shift or imitation of an announcer."""
from pathlib import Path
import sherpa_onnx,numpy as np,wave,json,subprocess

ROOT=Path(__file__).resolve().parent
base=Path('/workspace/creative-tools/models/kokoro-multi-lang-v1_0')
config=sherpa_onnx.OfflineTtsConfig(model=sherpa_onnx.OfflineTtsModelConfig(
 kokoro=sherpa_onnx.OfflineTtsKokoroModelConfig(model=str(base/'model.onnx'),voices=str(base/'voices.bin'),tokens=str(base/'tokens.txt'),data_dir=str(base/'espeak-ng-data'),lang='es'),num_threads=3,provider='cpu'),max_num_sentences=1)
tts=sherpa_onnx.OfflineTts(config)
# One thought per breath; give the action scenes space between the phrases.
lines=[
 (.35,'¿Qué historia vas a vivir hoy?',1.00),
 (3.95,'¡Batallas que te dejan sin aliento!',1.01),
 (9.55,'Personajes que se quedan contigo.',.98),
 (14.20,'Aventuras para disfrutar en familia.',1.01),
 (20.15,'Convierte cualquier noche en una gran historia.',1.02),
 (25.55,'¡Vívelo en HBO Max!',.99),
 (28.85,'Escríbenos y empieza hoy.',1.02),
]
manifest=[]
for i,(at,text,speed) in enumerate(lines):
 a=tts.generate(text,sid=53,speed=speed)
 x=np.array(a.samples,dtype=np.float32)
 active=np.flatnonzero(np.abs(x)>.005)
 assert len(active)
 x=x[max(0,active[0]-int(a.sample_rate*.04)):min(len(x),active[-1]+int(a.sample_rate*.10))]
 p=ROOT/'audio'/f'voz-{i+1}-raw.wav'
 with wave.open(str(p),'wb') as f:
  f.setnchannels(1);f.setsampwidth(2);f.setframerate(a.sample_rate);f.writeframes((np.clip(x,-1,1)*32767).astype('<i2').tobytes())
 target=ROOT/'audio'/f'voz-{i+1}.wav'
 # Subtle warmth/presence and gentle dynamics. No artificial lowering of pitch.
 eq='highpass=f=70,lowpass=f=10500,equalizer=f=150:t=q:w=0.8:g=1.2,equalizer=f=2700:t=q:w=0.8:g=1.6,acompressor=threshold=0.16:ratio=2:attack=12:release=110:makeup=1.15,alimiter=limit=0.95:level=false'
 subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(p),'-af',eq,'-ar','48000','-c:a','pcm_s16le',str(target)],check=True)
 p.unlink()
 duration=len(x)/a.sample_rate
 assert at+duration<([3.4,9.2,14,20,25.5,28.8,31.35][i]),(i,duration)
 row={'at':at,'text':text,'duration':duration,'path':target.name,'model':'Kokoro v1.0','speaker':'em_santa','speaker_id':53,'speed':speed}
 manifest.append(row);print(row,flush=True)
(ROOT/'audio/locucion.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
