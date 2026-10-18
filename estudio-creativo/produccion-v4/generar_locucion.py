from pathlib import Path
import sherpa_onnx,numpy as np,wave,json
base=Path('/workspace/creative-tools/models/vits-piper-es_MX-ald-medium')
config=sherpa_onnx.OfflineTtsConfig(model=sherpa_onnx.OfflineTtsModelConfig(vits=sherpa_onnx.OfflineTtsVitsModelConfig(model=str(base/'es_MX-ald-medium.onnx'),tokens=str(base/'tokens.txt'),data_dir=str(base/'espeak-ng-data'),noise_scale=.45,noise_scale_w=.55),num_threads=2,provider='cpu'),max_num_sentences=1)
tts=sherpa_onnx.OfflineTts(config)
lines=[
 (.30,'¿Qué historia vas a vivir hoy?'),
 (4.10,'Batallas que te dejan sin aliento.'),
 (9.55,'Personajes que se quedan contigo.'),
 (14.15,'Aventuras para disfrutar en familia.'),
 (20.15,'Convierte cualquier noche en una gran historia.'),
 (25.65,'Vívelo en HBO Max.'),
 (28.80,'Escríbenos y empieza hoy.'),
]
out=Path('/workspace/yo-probando/estudio-creativo/produccion-v4/audio')
manifest=[]
for i,(at,text) in enumerate(lines):
 result=tts.generate(text,sid=0,speed=1.0)
 samples=np.array(result.samples,dtype=np.float32)
 active=np.flatnonzero(np.abs(samples)>.008)
 if len(active):samples=samples[max(0,active[0]-int(result.sample_rate*.03)):min(len(samples),active[-1]+int(result.sample_rate*.08))]
 path=out/f'voz-{i+1}.wav'
 with wave.open(str(path),'wb') as f:
  f.setnchannels(1);f.setsampwidth(2);f.setframerate(result.sample_rate);f.writeframes((np.clip(samples,-1,1)*32767).astype('<i2').tobytes())
 row={'at':at,'text':text,'duration':len(samples)/result.sample_rate,'path':str(path)}
 manifest.append(row);print(row,flush=True)
(out/'locucion.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
