from pathlib import Path
import json
ROOT=Path(__file__).resolve().parent
WORK=Path('/workspace/hbo-v6/work');WORK.mkdir(parents=True,exist_ok=True)
INPUTS={x['id']:x for x in json.loads(Path('/workspace/hbo-final/inputs.json').read_text())}
DURATION=38
# source, source-in, output duration, layout, source duration
SHOTS=[
 ('4',9.4,2.0,'wide',2.0),('4',5.4,2.0,'wide',2.0),
 ('5',3.55,1.5,'tall',1.5),('4',27.4,2.0,'wide',2.0),('4',19.4,2.5,'wide',2.5),
 ('3',11.8,2.0,'wide',2.0),('3',35.8,1.5,'wide',1.5),('3',48.0,1.5,'wide',1.5),
 ('1',19.15,1.5,'tall',1.5),('1',20.65,1.5,'tall',1.5),('1',23.1,1.5,'tall',1.5),('1',15.3,1.5,'tall',1.5),
 ('1',7.0,2.0,'tall',2.0),('4',11.7,1.5,'wide',1.5),('4',27.4,2.0,'wide',2.0),('4',20.2,1.5,'wide',1.5),
 ('4',9.0,3.5,'dragon',2.5),('4',17.4,2.5,'dragon',2.5),
]
assert sum(x[2] for x in SHOTS)==34

def chapter(at):
 if at<4:return ('TU PRÓXIMA','GRAN HISTORIA','Elige cómo quieres sentirte.')
 if at<10:return ('SIENTE CADA','BATALLA','Dragones, fantasía y acción.')
 if at<15:return ('HISTORIAS','QUE TE ATRAPAN','Personajes que se quedan contigo.')
 if at<21:return ('AVENTURAS','PARA COMPARTIR','Grandes momentos en familia.')
 if at<28:return ('VÍVELO EN','HBO MAX','Haz de cualquier noche un gran plan.')
 return ('EL DRAGÓN','TIENE ALGO QUE DECIR','DISPONIBLE EN TZUBARU')
