# Contexto creativo de Tzubaru / HBO Max

## Pedido vigente

El usuario quiere un anuncio emocionante y llamativo, con escenas reales de películas y series de HBO Max: acción, batallas, personajes y variedad. Solicitó dirección audiovisual, edición, marketing, animación y 3D. Facilitó una imagen de la marca Tzubaru.

## Aprendizajes de las revisiones

- Rechazó el primer montaje de ilustraciones animadas y textos.
- Rechazó también el avance de 12 segundos centrado en anillos 3D y logotipos. Lo calificó como horrible.
- Ambas son propuestas anteriores no aprobadas. No presentarlas como ejemplos de calidad ni como el anuncio final.
- La corrección central es que el material de películas y series debe protagonizar el anuncio. La animación de marca es un recurso secundario.
- Instalar habilidades no garantiza la calidad del montaje ni sustituye los videos fuente.

## Alcance y evidencia

- Hay una valoración cualitativa directa del usuario; no existen métricas de campañas, CTR, ventas o retención.
- Público de trabajo propuesto: personas interesadas en acción, fantasía y ciencia ficción. Es una hipótesis creativa, no investigación de audiencia.
- No se han facilitado precios, promociones, condiciones comerciales ni un enlace de contratación. No inventarlos.
- La disponibilidad actual de títulos por país no se ha verificado. No anunciar una selección como catálogo confirmado.
- Las consultas a HBO Max, WBD y YouTube siguen bloqueadas con HTTP 403. La sesión no dispone todavía de clips reales descargados de esas fuentes.

## Siguiente trabajo

Seguir `estudio-creativo/BRIEF-V3.md`. Obtener material oficial accesible o archivos MP4 adjuntos por el usuario, seleccionar los planos después de ver y escuchar los clips, y editar el anuncio completo. No exportar otro sustituto de imágenes fijas o de logotipos como respuesta a este pedido.

## Actualización: material recibido y producción V4

El usuario adjuntó seis MP4 e indicó expresamente **sin precios**. Pidió buenos sonidos, emoción, motivos para adquirir HBO Max y libertad de dirección creativa. Ya no se necesita acceso a las redes sociales para editar esta versión.

La entrega actual se produce en `estudio-creativo/produccion-v4`: veinte planos y cierre de marca, 32 segundos, con voz sintetizada en español, música de una referencia y efectos. Se omiten los gráficos de ofertas y las fechas de estreno. Esta actualización no implica aprobación del usuario ni resultados de marketing medidos.

## Revisión solicitada: V5

El usuario valoró positivamente la estructura de V4, pero rechazó la calidad de su narración. Pidió voz más masculina, emocionante y con presencia; más batallas; menos pixelación. Conservar la estructura y la restricción de no incluir precios.

V5 sustituye el modelo de voz por Kokoro `em_santa`, con registro naturalmente más grave, y da más espacio a guerreros, dragones y acción presentes en los archivos aportados. No clona a un locutor oficial. La mezcla reduce más la música bajo la voz. Se aplica FSRCNN 2× y limpieza moderada, conservando el ancho original en los planos horizontales y usando intermedios sin pérdidas. No afirmar que se consiguió metraje nativo HD ni nuevas batallas descargadas; las referencias siguen siendo comprimidas de 576 píxeles. Proyecto `estudio-creativo/produccion-v5`, entrega `creaciones/HBO-Max-Tzubaru-Voz-Masculina-V2.mp4`. La revisión aún no ha recibido valoración del usuario.

## V6: rechazo de V5 y corrección de audio y calidad

El usuario rechazó también la voz y la imagen de V5: percibe una voz frágil, poco fluida y voces de fondo que la interrumpen. Pidió analizar el video completo antes de cambiarlo y extender al dragón para decir «Disponible en Subaru». Se mantiene Tzubaru conforme al logo aportado; se informó esa interpretación en la conversación.

El análisis está en `estudio-creativo/produccion-v6/ANALISIS.md`. V6 descarta TODO el audio de los originales, porque la pista usada como música conservaba voces. Crea instrumental y efectos por separado. Cambia Kokoro por Supertonic 3 M3, perfil de presentación firme, y M2 más profundo para el dragón. No afirmar que sea la voz oficial ni un clon de un locutor de HBO.

La pieza pasa a 38 segundos, con seis segundos dedicados al dragón entre 28 y 34. Su diálogo acompaña movimiento de boca existente retimado; no se generó sincronización labial por fonemas. Se restaura con Real-ESRGAN general y de animación, y se entrega panorámica y vertical. La fuente sigue siendo comprimida de 576 píxeles y la restauración no implica nuevo metraje HD. El acceso a servicios de voz Microsoft, YouTube y HBO/WBD volvió a recibir HTTP 403; no repetir permisos ni afirmar nuevas fuentes descargadas.

Se añadió la habilidad `video-router`; las instrucciones no sustituyen a los modelos ni garantizan una valoración positiva. La revisión V6 aún no ha sido aprobada ni valorada por el usuario. No describir V5 como la entrega vigente o una voz aceptada.
