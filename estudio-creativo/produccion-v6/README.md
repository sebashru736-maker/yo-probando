# HBO Max / Tzubaru: dragón, narración nueva y audio limpio

Revisión de 38 segundos en dos formatos:

- [Panorámico 1920×1080](../../creaciones/HBO-Max-Tzubaru-Dragon-Cine-38s.mp4), para ver las escenas horizontales con más presencia.
- [Vertical 1080×1920](../../creaciones/HBO-Max-Tzubaru-Dragon-Vertical-38s.mp4), para móvil y estados.

Se mantiene la estructura de acción, personajes, familia y cierre. No contiene precios, descuentos ni fechas de estreno. La versión todavía no ha recibido la valoración del usuario.

## Cambios tras revisar V5

La revisión previa está en [ANALISIS.md](ANALISIS.md). Se descarta completamente el audio de los MP4 originales: la música reutilizada contenía voces. La pista nueva es una composición instrumental separada, con cuerdas, metales, graves y percusión; no usa grabaciones de diálogo. Las frases de narración, el personaje del dragón y la música quedan en stems independientes dentro de `audio/`.

La narración cambia de Kokoro a **Supertonic 3**, perfil masculino M3, descrito por su fabricante como una voz de presentación firme y con autoridad. Se genera a 44,1 kHz, con 32 pasos, y se mezcla a 48 kHz. Se probaron cinco perfiles masculinos. M2, más profundo, da voz al dragón y recibe un tratamiento de personaje con eco corto. No se afirma usar la voz oficial ni clonar a un locutor de HBO Max.

El dragón ocupa **28–34 segundos**. Dice «Disponible en Tzubaru» a partir de 28,15 s, sobre un plano con movimiento de boca existente y retimado. Es un montaje de voz de personaje; no una animación labial generada por fonemas. La apertura también cambia a un primer plano de dragón.

La imagen se restaura con **Real-ESRGAN general x4v3** y la variante **animevideov3**, usando el metraje original seleccionado, no un archivo exportado anterior. La mezcla conserva un 15 % de la textura de origen. Se usan intermedios FFV1 sin pérdidas, color BT.709 y una única compresión H.264 de entrega, CRF 15, con audio AAC estéreo de 320 kbit/s.

**Límite de las fuentes:** siguen siendo MP4 comprimidos de 576 píxeles de ancho, y algunos planos solo contienen unos 288 píxeles de altura útil. La restauración reconstruye detalle aproximado; no sustituye una nueva fuente HD. YouTube, Microsoft Speech y HBO/WBD siguieron bloqueados por el proxy al consultar sus dominios en esta sesión.

## Producir y comprobar

Desde `/workspace/yo-probando/estudio-creativo` con `.venv` activado:

```bash
python produccion-v6/preparar_modelos.py
python produccion-v6/generar_voz.py
python produccion-v6/audio.py
python produccion-v6/preparar_video.py
python produccion-v6/render.py
python produccion-v6/revisar_locucion.py
python produccion-v6/verificar.py
```

Se requieren los archivos aportados, en `/workspace/attachments`, y el manifiesto `/workspace/hbo-final/inputs.json`. No se suben los originales ni los modelos por separado al repositorio. Los modelos, fuentes, licencias y SHA-256 están en `MODELOS.json`. PyTorch usa el wheel CPU de `https://download.pytorch.org/whl/cpu`; el resto de paquetes se fija en `requirements.txt`.

FluidSynth utiliza la biblioteca del sistema `libfluidsynth.so.3` y `TimGM6mb.sf2`. La composición de notas y el diseño de percusión están en `audio.py`; la procedencia del banco de instrumentos se conserva en `FUENTE-SOUNDFONT.txt`. La publicación de pesos de Supertonic incluye una licencia MIT para código; su README identifica OpenRAIL-M como licencia del modelo. Se conservan ambas referencias de forma diferenciada.

`edicion.json` contiene los cortes; `audio/locucion.json`, tiempos y textos. `verificar.py` valida los 1140 fotogramas por versión, sus timestamps, color, duración, decodificación completa, sonoridad y OCR de precios. `revisar_locucion.py` usa transcripción automática y comprueba picos; **no sustituye una escucha humana**. Los informes incluyen esa limitación.

Las exportaciones locales quedan en esta carpeta y las copias de entrega en `creaciones/`. Los archivos MP4 de esta carpeta se ignoran en Git para evitar duplicarlos.
