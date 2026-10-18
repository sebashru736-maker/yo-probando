"""Original score and stereo effects, tied to the Remotion edit's frame cues."""
from pathlib import Path
import json
import subprocess
import wave
import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'public/audio'
OUT.mkdir(exist_ok=True)
SR = 48000

def synth(duration, logo, cuts, name):
    rng = np.random.default_rng(736)
    n = int(SR * duration)
    audio = np.zeros((n, 2), dtype=np.float64)

    def mix(signal, start, level=1., pan=0.):
        begin = max(0, int(start * SR))
        count = min(len(signal), n - begin)
        if count <= 0:
            return
        signal = signal[:count] * level
        audio[begin:begin+count, 0] += signal * np.sqrt((1-pan)/2)
        audio[begin:begin+count, 1] += signal * np.sqrt((1+pan)/2)

    # Slow bowed-string chords, with detuning and gently moving vibrato.
    for start in np.arange(0, duration, 4.):
        chord = [[55, 82.4069, 110, 130.8128], [43.6535, 65.4064, 87.3071, 110], [65.4064, 98, 130.8128, 164.8138], [48.9994, 73.4162, 98, 123.4708]][int(start//4)%4]
        length=min(5.5,duration-start)
        t=np.arange(int(length*SR))/SR
        env=np.minimum(t/1.0,1)*np.minimum((length-t)/1.7,1)
        for j,freq in enumerate(chord):
            tone=np.zeros_like(t)
            for partial in range(1,9):
                phase=2*np.pi*(freq*partial*t+.0008*freq*partial*np.sin(2*np.pi*.7*t))
                tone+=np.sin(phase)/(partial**1.65)
                tone+=.2*np.sin(2*np.pi*freq*partial*1.002*t)/(partial**1.8)
            mix(tone*env,start,.055,(-.7,-.25,.25,.7)[j])

    # Measured eighth-note low strings. Final section resolves into the logo.
    for beat in np.arange(0, logo, .5):
        t=np.arange(int(.45*SR))/SR
        freq=55 if int(beat//4)%2==0 else 43.6535
        env=(1-np.exp(-t*85))*np.exp(-t*8)
        tone=sum(np.sin(2*np.pi*freq*k*t)/(k**1.7) for k in range(1,7))
        mix(tone*env,beat,.09)
        if beat>=2:
            melody=[220,261.6256,329.6276,391.9954,440,391.9954,329.6276,261.6256]
            f=melody[int(beat*2)%len(melody)]
            piano=sum(np.sin(2*np.pi*f*k*t)/(k*k) for k in range(1,5))*np.exp(-t*9)
            mix(piano,beat,.035,np.sin(beat)*.6)

    # Low drum and wide orchestral-style tom strokes, no sampled film audio.
    for beat in np.arange(0,logo,.5):
        t=np.arange(int(.7*SR))/SR
        phase=2*np.pi*(42*t+2.4*(1-np.exp(-t*23)))
        kick=np.sin(phase)*np.exp(-t*8)
        mix(kick,beat,.25 if beat%2==0 else .10)
        if beat%2==1:
            noise=sosfilt(butter(2,[180,1800],btype='bandpass',fs=SR,output='sos'),rng.normal(size=len(t)))
            tom=(np.sin(2*np.pi*(105*t+.8*(1-np.exp(-t*12))))+.25*noise)*np.exp(-t*9)
            mix(tom,beat,.15,(-.35 if int(beat)%4==1 else .35))

    # Cinematic hits and moving air sweeps at the exact cut/reveal frame.
    for cut in cuts:
        length=min(2.8,duration-cut)
        t=np.arange(int(length*SR))/SR
        low=np.sin(2*np.pi*(34*t+1.3*(1-np.exp(-t*15))))*np.exp(-t*2.2)
        texture=sosfilt(butter(2,2600,fs=SR,output='sos'),rng.normal(size=len(t)))*np.exp(-t*3.4)
        metal=(np.sin(2*np.pi*523.251*t)+.3*np.sin(2*np.pi*791*t))*np.exp(-t*4.5)
        mix(low,cut,.43)
        mix(texture,cut,.15)
        mix(metal,cut,.055)
        if cut>=.8:
            t=np.arange(int(.8*SR))/SR
            wind=sosfilt(butter(2,[500,7500],btype='bandpass',fs=SR,output='sos'),rng.normal(size=len(t)))
            env=(t/.8)**2
            sweep=wind*env
            begin=int((cut-.8)*SR)
            count=min(len(sweep),n-begin)
            pan=np.linspace(-.9,.9,count)
            audio[begin:begin+count,0]+=.12*sweep[:count]*np.sqrt((1-pan)/2)
            audio[begin:begin+count,1]+=.12*sweep[:count]*np.sqrt((1+pan)/2)

    # Warm, sustained three-note sonic identity on the brand reveal.
    for offset,freq in [(0,220),(.10,329.6276),(.21,440)]:
        length=min(3.8,duration-logo-offset)
        if length<=0: continue
        t=np.arange(int(length*SR))/SR
        bell=(np.sin(2*np.pi*freq*t)+.18*np.sin(2*np.pi*freq*2*t)+.08*np.sin(2*np.pi*freq*3*t))
        bell*=(1-np.exp(-t*70))*np.exp(-t*1.3)
        mix(bell,logo+offset,.15,(offset-.1)*3)

    # A stereo room tail creates width while retaining a mono-compatible core.
    dry=audio.copy()
    for ch in [0,1]:
        length=int(.85*SR)
        t=np.arange(length)/SR
        impulse=rng.normal(0,1,length)*np.exp(-t*8)
        impulse[:int(.035*SR)]=0
        impulse=sosfilt(butter(1,4000,fs=SR,output='sos'),impulse)
        impulse*=.2/max(np.sqrt(np.sum(impulse*impulse)),1e-9)
        audio[:,ch]+=fftconvolve(dry[:,ch],impulse)[:n]
    t=np.arange(n)/SR
    audio*=np.minimum(t/.18,1)[:,None]*np.clip((duration-t)/1.0,0,1)[:,None]
    audio=np.tanh(audio*1.15)
    audio*=.86/max(np.max(np.abs(audio)),1e-9)
    temp=OUT/f'{name}-premaster.wav'
    with wave.open(str(temp),'wb') as out:
        out.setnchannels(2);out.setsampwidth(2);out.setframerate(SR)
        out.writeframes((audio*32767).astype('<i2').tobytes())
    subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(temp),'-af','loudnorm=I=-16:TP=-1.5:LRA=9','-ar',str(SR),'-c:a','pcm_s16le',str(OUT/f'{name}-master.wav')],check=True)
    temp.unlink()
    return {'duration':duration,'logo_frame':int(logo*30),'impact_frames':[int(c*30) for c in cuts],'fps':30,'sample_rate':SR,'target_lufs':-16,'true_peak_limit_db':-1.5}

cues={
 'avance':synth(12,8,[0,4,8],'avance'),
 'final':synth(32,25,[0,3,7,11,15,18,21,25],'final'),
}
(OUT/'cue-sheet.json').write_text(json.dumps(cues,indent=2)+'\n')
print('Masters estéreo y hoja de sincronización generados.')
