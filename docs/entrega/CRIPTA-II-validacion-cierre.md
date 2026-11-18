# CRIPTA II · Validación de cierre

Base revisada: `main` en `87e166d`. Validación de los cambios de la rama de entrega sobre esa base.

## Confirmación para Centeno

Los números de su corrección coinciden con cripta-01 después de introducir el cazador en sala 5:

- 12 tipos distintos, lotes de catálogo de 10 y 2, y 12 fichas recuperadas desde disco en la prueba sin acceso a red.
- 4 enemigos derrotados en el guion de victoria, incluido el nuevo cazador.
- La sala 5 pasó a contener un enemigo y salió del caso de prueba de salas con objetos bajo caché saturada. La corrección local también comprueba que con una única ficha protegida se informa el error de capacidad, no se marca la sala como incorporada y se mantienen las invariantes de la caché.

T031 incorpora el cierre validado en la rama de Centeno (`f976097`). Se conservaron la evidencia de regresión y los valores del catálogo actualizado.

## Correcciones adicionales

- El resumen histórico oculta nombre, ID y rastro de las salas avistadas desde el modelo. Consola, replay y el panel de mensajes de Pygame usan el mismo formato. La vista gráfica asigna identificadores de dibujo a los nodos avistados.
- F2 abre la entrada de comandos en Pygame. Se probó el recorrido F2 → HISTORIA 0 → Enter con el controlador real y el driver de prueba.
- Los puntos de control ya pueden copiar el mapa grande sin recorrer recursivamente cadenas de salas y puertas. Se probó la restauración en 256 salas y la consulta online en cripta-06, de 300 salas. La prueba online con caché previa registró 3 de 63 solicitudes.
- El JSON de terreno conserva sus campos e incluye las filas de resolubilidad cuando se solicita `--bench --salida`. El contrato combinado se verificó por prueba automatizada.
- Se redujo el costo observado del cálculo compartido de rutas de cazador conservando la comparación del estado de puertas y el desempate existente.

## Alcance de las mediciones y de los datos oficiales

- La evidencia contractual versionada de Terreno/Cazador registra 240.000 ciclos del fixture de 256 salas, cero discrepancias y máximo de 17,7855 ms en el equipo de esa medición. La auditoría complementaria de carga local dio p95 de 16,849 ms y máximo de 57,204 ms bajo su propio protocolo. Se conservan ambas mediciones con sus condiciones.
- La API oficial publica cripta-02 a cripta-06. En cripta-06 se validaron las llaves y la entidad que custodia la de hierro: un carcelero de comportamiento errante. La ficha de la demostración con cazador pertenece al catálogo offline; el servidor devolvió 404 para ese ID y para cripta-01.
- Una segunda partida de consola, con semilla 354 y vida normal de 30, terminó en victoria en 8 acciones, a tiempo 450 y con 1 punto de vida. La bitácora reproducida desde main.py confirmó el mismo resultado. El recorrido opcional que derrota al cazador se conserva como prueba separada con vida ajustada.

Artefactos adjuntos: propuesta de README, secciones de decisiones §5.1–§5.6, Markdown de José, muestras de benchmark, reporte XML y parche de código separado.

## Revisión con Spec Kit y Antigravity

Se ejecutó `/speckit-implement` en modo de revisión sobre la rama local, con FR-003 de 002, T031 de 003 y T033 de 004. Antigravity ejecutó la suite y devolvió 1.381 pruebas aprobadas sobre la versión previa. A partir de sus hallazgos se ajustaron el resumen histórico, el minimapa, F2 y la copia de las referencias a puertas en mapas grandes. La copia usa el memo de `copy.deepcopy` para conservar la identidad compartida entre salas, salidas y recuerdos. Se comprobaron esas referencias en 256 salas.

En `87e166d`, 004 marca T027, T028 y T034 completas. La [spec 004](../../specs/004-linea-tiempo/tasks.md) marca T033 tras ejecutar sus cinco pruebas focalizadas. Se corrigió la ruta de prueba y se usó la decisión que ya figura en `research.md`: K=200 y reconstrucción hacia adelante. La inversión queda consignada como variante exploratoria no medida. El cierre de T031 se incorporó en la [spec 003](../../specs/003-resolubilidad/tasks.md).

El parche se comprobó con `git diff --check` y `git apply --cached --check` sobre la base indicada. Registro de Antigravity en el archivo adjunto correspondiente.

## Resultado final de la copia corregida

La suite completa aprobó **1.381 pruebas**, con cero fallos y cero errores, en 132,12 s. Las aserciones focalizadas adicionales de F2 y de identidad de las puertas en un mapa de 256 salas también pasaron. La medición registrada de IR A sobre el mapa oficial de 300 salas dio 0,530 ms como máximo en 100 muestras, por debajo de 5 ms para la ruta indicada en el JSON.

## Repetición contractual de terreno y cazador

La repetición contractual en el equipo de cierre completó 8 escenarios, 30 repeticiones por escenario y 240.000 ciclos. Las decisiones coincidieron con la referencia. Hubo 5 ciclos por encima de 20 ms y el máximo fue 43,1008 ms. Este equipo no reprodujo el cumplimiento del máximo obtenido en el informe original. [JSON de cierre](CRIPTA-II-terreno-benchmark-entrega.json).
