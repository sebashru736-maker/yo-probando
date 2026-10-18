# Revisión previa a la edición

Se revisó el montaje V5 completo mediante 64 fotogramas, los originales, los cortes, las pistas de voz y sus transcripciones. No se dispone de escucha humana en este entorno; no se presenta el análisis automático como una escucha.

Problemas encontrados y correcciones previstas:

1. **Voces de fondo:** V5 reutiliza la mezcla del MP4 `(4)` como música. Esa mezcla contiene voz, gritos y efectos, que no desaparecen por recortar su introducción. Se descarta completamente todo el audio de los originales. La nueva pista será instrumental, creada por separado, con narración y efectos en pistas independientes.
2. **Narración:** el usuario vuelve a rechazar Kokoro `em_santa`. No basta con bajar el tono ni aumentar el volumen. Se sustituye por Supertonic 3, con perfil masculino M3 de presentación firme y generación de frases completas a 44,1 kHz. Se prueban cinco perfiles masculinos; el M2, más profundo, se reserva al dragón. La información de los perfiles procede de la documentación del fabricante, no de una escucha simulada.
3. **Imagen:** los clips descargados son de 576 píxeles de ancho; la imagen de algunos dragones ocupa solo unos 288 píxeles de alto. Una etiqueta 1080p no recupera detalle. La restauración anterior FSRCNN no satisfizo al usuario. Se prueba Real-ESRGAN general x4 y su variante de animación, con inferencia en los fotogramas seleccionados, limpieza prudente y menor compresión de salida. Es reconstrucción aproximada, no una nueva fuente HD.
4. **Encuadre:** los planos horizontales pierden presencia dentro del lienzo vertical. Se añadirá una entrega panorámica 1920×1080 para aprovecharlos y se conservará una alternativa vertical.
5. **Ritmo:** veintidós planos de duraciones a veces inferiores a un segundo daban poco tiempo para apreciar la acción. La revisión usa planos más largos y un momento dedicado al dragón, conservando gancho, acción, personajes, familia y cierre.
6. **Dragón:** se extiende la pieza a 38 segundos, con seis segundos reservados al primer plano y reacción del dragón antes del cierre. Una voz de personaje dirá «Disponible en Tzubaru». Se retima el movimiento existente de la boca; no se afirma disponer de sincronización labial fonética generada.
7. **Marca y precios:** se mantiene Tzubaru, nombre del logo aportado, y la instrucción de no incluir precios, descuentos ni fechas de estreno.

Se intentó consultar la voz pública de Microsoft, YouTube y las páginas de HBO/WBD. El proxy sigue devolviendo HTTP 403. No se reutilizan credenciales ambientales de Azure para servicios que el usuario no ha conectado. Las mejoras se ejecutan con modelos locales descargados de sus publicaciones oficiales y sin servicios de pago.
