"""Supertonic 3: new narrator M3 and separate M2 creature dialogue."""
from pathlib import Path
import sherpa_onnx,numpy as np,wave,json,subprocess
from plan import ROOT

B=Path('/workspace/creative-tools/models/sherpa-onnx-supertonic-3-tts-int8-2026-05-11')
cfg=sherpa_onnx.OfflineTtsConfig(model=sherpa_onnx.OfflineTtsModelConfig(supertonic=sherpa_onnx.OfflineTtsSupertonicModelConfig(duration_predictor=str(B/'duration_predictor.int8.onnx'),text_encoder=str(B/'text_encoder.int8.onnx'),vector_estimator=str(B/'vector_estimator.int8.onnx'),vocoder=str(B/'vocoder.int8.onnx'),tts_json=str(B/'tts.json'),unicode_indexer=str(B/'unicode_indexer.bin'),voice_style=str(B/'voice.bin')),num_threads=2,provider='cpu'))
t=sherpa_onnx.OfflineTts(cfg)
lines=[
 (.30,'¡Prepárate para vivir grandes historias!',7,1.04,3.8),
 (4.20,'Batallas épicas, dragones y acción que no te suelta.',7,1.04,9.6),
 (10.20,'Personajes inolvidables. Historias que te atrapan.',7,1.04,14.7),
 (15.20,'Y aventuras para compartir en familia.',7,1.04,20.6),
 (21.20,'Tu próxima gran historia empieza en HBO Max.',7,1.05,27.7),
 (28.15,'Disponible en Tzubaru.',6,.98,31.35),
 (34.35,'Escríbenos y empieza a vivirlo.',7,1.03,37.4),
]
manifest=[]
for i,(at,text,sid,speed,deadline) in enumerate(lines):
 g=sherpa_onnx.GenerationConfig();g.sid=sid;g.num_steps=32;g.speed=speed;g.extra={'lang':'es'}
 a=t.generate(text,g);x=np.array(a.samples,dtype=np.float32)
 active=np.flatnonzero(np.abs(x)>.005);assert len(active)
 x=x[max(0,active[0]-int(a.sample_rate*.035)):min(len(x),active[-1]+int(a.sample_rate*.08))]
 raw=ROOT/'audio'/f'voice-{i+1}-native.wav'
 with wave.open(str(raw),'wb') as f:
  f.setnchannels(1);f.setsampwidth(2);f.setframerate(a.sample_rate);f.writeframes((np.clip(x,-1,1)*32767).astype('<i2').tobytes())
 target=ROOT/'audio'/f'voice-{i+1}.wav'
 eq='highpass=f=65,lowpass=f=15500,equalizer=f=180:t=q:w=0.8:g=1,equalizer=f=2800:t=q:w=0.7:g=2,acompressor=threshold=0.18:ratio=2.5:attack=8:release=90:makeup=1.35'
 if sid==6:
  # The fantasy character has its own deep voice and a short cavern-like echo.
  eq='asetrate=39690,aresample=48000,highpass=f=48,lowpass=f=8000,equalizer=f=130:t=q:w=0.7:g=2,acompressor=threshold=0.18:ratio=2:attack=8:release=100:makeup=1.2,aecho=0.8:0.86:55|110:0.12|0.06'
 subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(raw),'-af',eq,'-ar','48000','-c:a','pcm_s16le',str(target)],check=True)
 with wave.open(str(target)) as f:duration=f.getnframes()/f.getframerate()
 assert at+duration<deadline,(i,duration)
 row={'at':at,'text':text,'path':target.name,'native_path':raw.name,'duration':duration,'model':'Supertonic 3','speaker':'M2' if sid==6 else 'M3','sid':sid,'steps':32,'speed':speed,'native_sample_rate':a.sample_rate}
 manifest.append(row);print(row,flush=True)
(ROOT/'audio/locucion.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
