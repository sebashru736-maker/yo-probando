# HBO Max / Tzubaru — revisión de voz, imagen y acción

[Descargar el video revisado, 32 segundos](../../creaciones/HBO-Max-Tzubaru-Voz-Masculina-V2.mp4).

Se conserva la estructura que gustó al usuario: gancho, fantasía y acción, personajes, aventuras familiares, montaje final y cierre de Tzubaru. Sin precios ni fechas de estreno. Esta revisión todavía no implica aprobación del usuario.

Cambios frente a V4:

- Locución nueva con Kokoro multilingüe v1.0, voz masculina española `em_santa`, a 24 kHz, en lugar de Piper `ald-medium`. No se utiliza una grabación ni se clona la voz de un locutor de HBO. Registro naturalmente más grave, puntuación y ritmos por frase; sin bajar artificialmente el tono de la voz anterior.
- Presencia de voz con ecualización ligera, compresión suave y música reducida durante cada frase. Golpes, barridos y pulsos de aire sincronizados con los cortes. Master de 48 kHz estéreo, normalización en dos pasadas.
- Veintidós planos: más tiempo de fantasía/guerreros y mayor presencia de dragones en el montaje final, manteniendo el infectado y el bloque familiar. Se usan exclusivamente los clips aportados.
- Limpieza ligera antes de ampliar, reescalado FSRCNN 2× y enfoque moderado. Los planos horizontales conservan toda su anchura, eliminando el recorte adicional de 576 a 432 píxeles que hacía V4. Los intermedios son FFV1 sin pérdidas; la compresión de entrega H.264 se aplica una sola vez, CRF 16.

La salida es de 1080 × 1920, 30 fps, 960 fotogramas. Los originales proceden de descargas comprimidas de 576 píxeles de ancho; el procesamiento reduce algunos defectos, pero no convierte el detalle original en HD nativo. No se consiguió ni se afirma haber conseguido una nueva fuente de alta definición.

## Producción reproducible

FFmpeg y Python 3.12 con `requirements.txt`. En esta sesión:

```bash
/workspace/yo-probando/estudio-creativo/.venv/bin/python estudio-creativo/produccion-v5/generar_locucion.py
/workspace/yo-probando/estudio-creativo/.venv/bin/python estudio-creativo/produccion-v5/render.py
```

Los archivos fuente permanecen en `/workspace/attachments`, el manifiesto en `/workspace/hbo-final/inputs.json` y los temporales en `/workspace/hbo-v5/work`. Los modelos se guardan fuera del repositorio, en `/workspace/creative-tools/models`. `MODELOS.json` documenta fuentes, licencias y huellas. No se suben los originales ni los modelos a GitHub.

`audio/locucion.json` incluye textos, tiempos y voz; `edicion.json`, puntos de entrada de los planos. `verificar.py` comprueba duración, fotogramas, timestamps, decodificación, sonoridad, continuidad de imagen y una revisión OCR de precios. La revisión de locución usa transcripción automática, no una escucha humana.

La música base procede del MP4 `(4)`, omitiendo su introducción hablada, como en V4. Las futuras fechas y gráficos de ofertas de otras referencias no se incorporan.
