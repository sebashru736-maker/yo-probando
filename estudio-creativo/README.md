# Estudio creativo de Tzubaru

Proyecto de Remotion con React, Three.js y React Three Fiber, tipografía local, escenas tridimensionales y diseño sonoro original. Es independiente del primer video de imágenes animadas, que se conserva en `../creaciones`.

## Estado del trabajo

- `Avance3D`: apertura y cierre originales, 12 segundos, 1080 × 1920, 30 fps. No incluye clips de películas.
- `Apertura3D` y `CierreTzubaru`: piezas editables por separado.
- `HBOFinal`: montaje previsto de 32 segundos. **Pendiente de obtener los tres clips oficiales** descritos en `public/clips/README.md`. No se ha validado la disponibilidad actual de los títulos en el catálogo local.
- La consulta a los sitios de HBO Max, WBD y YouTube recibió un bloqueo HTTP 403 del proxy. Los dominios necesarios se guardaron en el borrador de configuración del entorno; ese guardado no activa el acceso.

## Preparación

Requisitos: Node 24, Python 3.12, FFmpeg y Chromium. En el entorno de Codex están disponibles; las exportaciones usan `/usr/bin/chromium` con el renderizador de software `swangle`.

```bash
cd /workspace/yo-probando/estudio-creativo
npm ci
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-audio.txt
. .venv/bin/activate
npm run audio
npm run check
npm run dev -- --no-open
```

La vista previa es local al entorno. Para exportar el avance:

```bash
npm run render:avance
```

La exportación queda en `out/Tzubaru-HBO-Max-avance-3D.mp4`. En otro sistema, sustituye el parámetro `--browser-executable` por la ubicación de Chromium/Chrome.

Para el montaje de películas, incorpora primero los segmentos oficiales, registra sus fuentes y revisa el encuadre. Después usa `npm run render:final`; el comando falla si falta algún clip.

## Animación y sonido

Toda animación depende del número de fotograma. El archivo `public/audio/cue-sheet.json` registra los golpes de sonido y el momento del logo. La banda sonora y los efectos estéreo son síntesis original: cuerdas armónicas, percusión, subgraves, barridos y una firma sonora de tres notas, con objetivo de −16 LUFS y límite de pico verdadero de −1,5 dBTP.

El logo limpio de Tzubaru se generó a partir de la referencia facilitada por el usuario. El símbolo HBO se extruye en 3D desde el trazado incluido en Simple Icons 11.3.0: https://github.com/simple-icons/simple-icons/blob/11.3.0/icons/hbo.svg. La geometría tipográfica usa Helvetiker de Three.js. Las fuentes DejaVu incluyen su licencia en `public/DejaVu-LICENSE.txt`.

## Habilidades instaladas

Las habilidades están en `../.agents/skills`, disponibles para este repositorio, junto a un registro de fuentes y commits en `PROVENANCE.json`:

- Remotion: edición, animación, audio, sincronización, transiciones y exportación.
- Diseño visual de interfaces de Anthropic.
- Buenas prácticas de React y revisión de interfaces de Vercel.
- Diez habilidades de Three.js: fundamentos, geometría, materiales, luces, texturas, animación, carga de modelos, shaders, posproducción e interacción.

Para futuras páginas web, ya están instaladas las bibliotecas Three.js, React Three Fiber, Drei y GSAP. El proyecto actual es un estudio de video; todavía no se ha definido ni construido una página comercial.
