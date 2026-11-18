# Revisión de main 7655ecb

Se incorporó main 7655ecb a la rama cierre-entrega el 18 de noviembre de 2026. Se resolvieron cuatro conflictos conservando el buscador optimizado actual, el cierre de T033 y ambos casos de capacidad de caché. Se eliminaron marcas de conflicto del documento de decisiones.

| Capacidad | Validación |
|---|---|
| 001 Terreno y cazador | Se conserva el código de main. Su reporte de iteración 5 contiene 270.000 ciclos, cero discrepancias, máximo global 12,8721 ms y máximo en cripta-06 de 2,0696 ms. Se verificaron las muestras y el checksum del snapshot. |
| 002 Niebla, antorcha y viaje | Suite de aceptación incluida, historial y minimapa filtrados, replay de victoria y preservación del conocimiento tras guardar y cargar. Se conserva la medición de IR A en 300 salas, con máximo de 0,530 ms en la ruta registrada. |
| 003 Resolubilidad | Suite de aceptación incluida, cierre T031, pruebas de caché en capacidades uno y dos, veredicto NO RESOLUBLE conservado para cripta-05 y continuación explícita con forzar. |
| 004 Línea de tiempo | Se adopta el cierre de T033 de main. Se probaron MAPA, HISTORIA 0, movimiento, guardado y carga en los seis mapas, incluido el de 300 salas. |
| Datos offline | Se conservan seis criptas con contenido, llaves y catálogos completos por mapa. La regresión comprueba que el catálogo oficial conserva sus estadísticas y Osario menor conserva las suyas. |

La suite completa del código integrado pasó 1.401 pruebas en 438,72 s, con cero fallos y cero errores. El reporte XML está en esta carpeta. Después se ajustó una prueba de contrato para simular también la nueva referencia y evitar ejecutar su medición completa durante esa prueba; las tres pruebas del archivo pasaron en 2,81 s. La prueba dedicada de motor con la referencia continúa ejecutándose en la suite.

La partida con vida normal y semilla 354 vuelve a terminar en victoria al reproducirla con el código integrado. La regresión de los seis mapas se conserva en REGRESION-MAIN-INTEGRADO.json.

Las mediciones son las registradas en sus respectivos equipos, versiones y escenarios. El resultado de 43,1008 ms conservado en el reporte anterior corresponde al buscador previo a esta actualización.
