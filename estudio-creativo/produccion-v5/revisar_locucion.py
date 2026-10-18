"""ASR and acoustic checks; does not pretend to replace human listening."""
from pathlib import Path
import wave,json,math
import numpy as np
from scipy.signal import resample_poly, butter,sosfilt,find_peaks
import sherpa_onnx
ROOT=Path(__file__).resolve().parent
B=Path('/workspace/creative-tools/models/sherpa-onnx-whisper-tiny')
r=sherpa_onnx.OfflineRecognizer.from_whisper(encoder=str(B/'tiny-encoder.int8.onnx'),decoder=str(B/'tiny-decoder.int8.onnx'),tokens=str(B/'tiny-tokens.txt'),language='es',num_threads=2)
def read(p):
 with wave.open(str(p)) as f:
  sr=f.getframerate();ch=f.getnchannels();x=np.frombuffer(f.readframes(f.getnframes()),dtype='<i2').astype(np.float32).reshape(-1,ch).mean(axis=1)/32768
 g=math.gcd(sr,16000);return resample_poly(x,16000//g,sr//g)
master=read(ROOT/'audio/master.wav')
rows=[]
for line in json.loads((ROOT/'audio/locucion.json').read_text()):
 x=read(ROOT/'audio'/line['path'])
 y=sosfilt(butter(3,[65,500],btype='bandpass',fs=16000,output='sos'),x)
 f0=[]
 for start in range(0,len(y)-640,320):
  a=y[start:start+640];a=a-a.mean()
  if np.sqrt(np.mean(a*a))<.007:continue
  ac=np.correlate(a*np.hanning(640),a*np.hanning(640),mode='full')[639:]
  peaks,_=find_peaks(ac[40:229]);peaks+=40
  if len(peaks):
   k=peaks[np.argmax(ac[peaks])]
   if ac[k]/max(ac[0],1e-9)>.38:f0.append(16000/k)
 at=int(max(0,line['at']-.15)*16000)
 count=int((line['duration']+.35)*16000)
 s=r.create_stream();s.accept_waveform(16000,master[at:at+count]);r.decode_stream(s)
 row={'expected':line['text'],'mixed_audio_asr':s.result.text,'median_pitch_hz':float(np.median(f0)),'clipped_samples_voice':int(np.sum(np.abs(x)>.999))}
 assert row['clipped_samples_voice']==0
 print(row,flush=True);rows.append(row)
(ROOT/'verificacion-locucion.json').write_text(json.dumps({'method':'Whisper tiny ASR + pitch autocorrelation; no human listening','speaker':'Kokoro em_santa','lines':rows},ensure_ascii=False,indent=2)+'\n')
