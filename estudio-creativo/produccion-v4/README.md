# HBO Max / Tzubaru: Historias, 32 segundos

Anuncio construido con los MP4 aportados por el usuario. Formato vertical de 1080 × 1920, 30 fps, voz en español, música, efectos estéreo y cierre de Tzubaru. Sin precios, descuentos, promociones ni fechas de disponibilidad.

## Montaje

- 0–9,2 s: fantasía, dragones y personajes de las referencias.
- 9,2–14 s: personajes e historias del anuncio de Max aportado.
- 14–20 s: aventuras y animación para compartir en familia.
- 20–28,8 s: montaje de acción creciente.
- 28,8–32 s: cierre de HBO Max y Tzubaru, con invitación a escribir y adquirir acceso.

`edicion.json` registra los puntos de entrada y la duración de los veinte planos. `locucion.json` contiene el texto y el inicio de cada frase.

## Material utilizado

Se revisaron los seis archivos. El metraje procede de `Download (1).mp4`, `(3).mp4`, `(4).mp4` y un fragmento sin fechas de `(5).mp4`. `(2).mp4` se usó como referencia de estilo; sus ofertas no se incluyen. `(6).mp4` se conserva como referencia y no aparece en el montaje.

La música base procede del audio del archivo `(4)`, omitiendo su introducción hablada. La voz es síntesis en español de México con Piper/VITS `es_MX-ald-medium`, ejecutada localmente con Sherpa ONNX; no imita a un actor. Se añadieron golpes y barridos, reduciendo la música durante las frases. `MODELO-VOZ.txt` conserva la información del modelo.

Los archivos originales adjuntos no se suben por separado a GitHub. Se conservan localmente en `/workspace/attachments`. La entrega pública contiene el montaje editado y sus recursos de producción.

## Reproducción técnica

`render.py` utiliza FFmpeg y las dependencias de `requirements.txt`. Los archivos de voz generados están en `audio/`; el script de generación de locución es opcional y requiere el modelo local. El manifiesto de entrada de esta sesión está en `/workspace/hbo-final/inputs.json`; el trabajo temporal está en `/workspace/hbo-final/work`.

La unión final decodifica cada plano de forma independiente y entrega un flujo de 960 fotogramas a un codificador único, con color BT.709 y tiempo constante a 30 fps. Así se evita que los distintos metadatos de color de las referencias reinicien los filtros y desajusten los cortes.

El master usa normalización de sonoridad en dos pasadas. La última frase termina antes del fundido de música.
