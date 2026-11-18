# Plan de implementación: Terreno y cazador

**Rama Git**: `feature/spec-kit-copilot` | **Feature**: `001-terreno-cazador` | **Fecha**: 2026-11-04 | **Especificación**: [spec.md](./spec.md)

**Entrada**: Requisitos funcionales FR-001–FR-014 y escenarios AB-01–AB-30.

## Resumen

Extender el costo efectivo de cada salida hasta el cálculo del intervalo de movimiento
sin cambiar las acciones existentes, e incorporar el comportamiento de cazador al modelo
de enemigos. La decisión del cazador debe ser una ruta abierta de costo mínimo y repetible
desde el estado actual. La carga valida los datos antes de iniciar, y ambas vistas presentan
los costos efectivos y distinguen al cazador. La validación de rendimiento se integrará en
`--bench`, sin red ni instanciación de vistas, y comparará cada decisión con un cálculo de
referencia desde cero.

## Contexto técnico

**Lenguaje/versión**: Python 3.12 (entorno de referencia indicado en README).

**Dependencias principales**: Dependencias existentes del proyecto (`requests`, `pygame` y
`pytest`). No se añadirá una biblioteca de grafos, rutas, heap o búsqueda.

**Persistencia**: JSON servido por adaptadores HTTP/offline; cachés locales de esqueleto,
contenido y catálogo. No hay base de datos.

**Pruebas**: `pytest`; pruebas unitarias, de integración MVC, CLI y vistas ya existentes.

**Plataforma**: Windows local como entorno de rendimiento declarado; la lógica del juego
continúa siendo multiplataforma dentro de los entornos actualmente soportados.

**Tipo de proyecto**: Juego Python con modelo, controlador, vista de consola y vista Pygame.

**Objetivo de rendimiento**: Mantener dos mediciones complementarias. La comparativa
controlada ejecuta los ocho escenarios existentes en el fixture sintético
`bench-terreno-cazador-grid-16x16` v1.0.0, con 256 salas, 20 cazadores y 30 repeticiones
de 1000 ciclos por escenario. La validación del límite oficial ejecuta además 30
repeticiones de 1000 ciclos con las 25 instancias de cazador de `cripta-06` en un snapshot
fijo de 300 salas. En ambas mediciones cada ciclo debe ser ≤20 ms y las decisiones deben
coincidir con un recálculo desde cero.

**Restricciones**:
- Solo estructuras propias para índices, colas de prioridad y cachés de rutas. No usar
  `dict`/`set` como índice o caché ni `heapq`, `bisect`, `collections`, `networkx` o
  bibliotecas equivalentes.
- Conservar determinismo, historial reversible, serialización, presupuesto de solicitudes
  y separación MVC en `--replay` y `--bench`.
- No incluir datos de una cripta concreta en lógica de producción. Las pruebas y mediciones
  reciben datos externos reproducibles.
- No afirmar el cumplimiento de los 20 ms hasta tener evidencia de `--bench`.

**Escala**: La prueba comparativa conserva los 20 cazadores del fixture sintético fijo,
versionado y externo a la lógica de producción. La prueba de referencia añade el mapa
publicado `cripta-06` versión `f9ed9afa683d` y el catálogo versión `4b9e75a42be5`, con 300
salas y 25 `ent_sabueso_oseo` de rango 600. Se materializa un snapshot con checksum para no
consultar la API durante las mediciones. Las dos identidades, sus estados y sus protocolos
quedan definidos en [el contrato](./contracts/datos-entrada-y-benchmark.md).

## Verificación de constitución

| Principio | Estado | Aplicación en el diseño |
|---|---|---|
| I. Estructuras propias | Cumple | Reutilizar `Vector`, `ListaSimple` y búsqueda binaria propia; para la ruta de mínimo costo, usar una cola de prioridad propia basada en `Vector`. No convertir datos JSON en índices/cachés con diccionarios o conjuntos. |
| II. Determinismo | Cumple | Ordenar desempates de ruta por ID de sala; fijar semilla y secuencia; no usar orden de respuesta externa ni azar para decisiones del cazador. |
| III. Separación MVC | Cumple | `--bench` y `--replay` no crean instancias de vistas. Pygame sigue consumiendo snapshots publicados por el controlador. |
| IV. Datos de criptas externos | Cumple con condición | Costos y topología vienen del esqueleto; rango viene del catálogo. Las pruebas usan datos de entrada controlados, no valores de criptas incrustados en la lógica. |
| V. Presupuesto de solicitudes | Cumple | La decisión de rutas usa el esqueleto y el estado ya cargados; no añade consultas HTTP. Datos incompatibles fallan en la validación existente, antes de jugar. |
| VI. Rendimiento verificable | Cumple con condición | La comparación de modalidades y cualquier afirmación de latencia se apoyan en la salida reproducible de `--bench`. |
| VII. Especificación antes de implementación | Cumple en esta fase | `spec.md` precede al plan; esta fase solo produce documentos. No modificar código hasta que la especificación y el plan estén revisados y confirmados según el flujo del proyecto. |
| Trazabilidad | Cumple | La matriz de validación en `data-model.md` vincula FR y AB; las tareas futuras deberán referir los FR atendidos y las pruebas deberán citar sus AB. |

No se identifica una violación constitucional que requiera excepción.

## Fases de diseño

### Fase 0 — Investigación

Las decisiones y alternativas se consolidan en [research.md](./research.md). La investigación
inicial del 2026-11-04 se limitó a los documentos y el código presentes en el repositorio.
La actualización del 2026-11-17 contrastó el PDF oficial y consultó la API para verificar la
cripta de referencia y las versiones de sus datos; no midió rendimiento del juego en esa
consulta.

### Fase 1 — Diseño y contratos

- [Modelo de datos y estados](./data-model.md): reglas de validación, estado de ruta,
  decisión y trazabilidad FR/AB.
- [Contrato de entrada y benchmark](./contracts/datos-entrada-y-benchmark.md): campos de
  entrada, rechazos, determinismo y evidencia de medición.
- [Guía de validación](./quickstart.md): comandos previstos para pruebas focalizadas,
  regresión, CLI headless y benchmark.
- No se crea `tasks.md` en esta fase.

## Decisiones de integración

1. **Costo de movimiento**: almacenar en cada salida su costo efectivo validado; el
   adaptador asigna 100 solo cuando el campo está ausente. El costo de acción seleccionado
   debe llegar al punto que calcula `max(1, costo * 100 // velocidad)`. Todo actor que se
   mueva comunica el costo de la salida atravesada. Errante y rastreador conservan su
   selección de movimiento; ataques, espera y acciones restantes conservan su costo actual
   de 100.
2. **Validación**: se integra en la carga del esqueleto y del catálogo antes de crear la
   partida. Para cada par de sentidos representados, comparar los costos efectivos después
   del valor predeterminado; informar origen/destino y ambos costos al rechazar.
3. **Ruta**: búsqueda ponderada sobre el mapa completo y puertas abiertas en ese instante.
   Una búsqueda desde el jugador sobre aristas entrantes puede producir distancias al
   jugador para todos los cazadores; la selección final se hace entre salidas abiertas del
   cazador y elige el destino de menor ID que cumpla `costo + dist(destino) = dist(origen)`.
   Mantener cálculo individual y compartido para poder medir ambos. Todo estado compartido
   debe quedar invalidado al cambiar la posición del jugador o una puerta. Las salidas sin
   representación inversa son válidas y se tratan como dirigidas; comparar costos solo
   cuando existan ambos sentidos.
4. **Turnos**: conservar el orden de eventos del reloj. La decisión del cazador mantiene
   primero el ataque al compartir sala; entrar a la sala del jugador termina el movimiento
   sin ataque hasta el siguiente turno programado.
5. **Vistas**: consola lee costo efectivo del modelo; Pygame lo recibe en su snapshot plano.
   No pasar reglas de ruta a las vistas. Diferenciar el cazador por comportamiento y
   conservar el mecanismo existente de sprites/estilo como fallback si no existe un asset
   específico.
6. **Benchmark**: añadir la evaluación del cazador al camino headless de `--bench`, sin
   fuente de red ni vistas. Usar el fixture `bench-terreno-cazador-grid-16x16` v1.0.0
   (256 salas, 480 conexiones bidireccionales; definición exacta en el contrato). Mantener
   mapa/versión, semilla, estado inicial, acciones y equipo invariantes entre comparaciones.
   Ejecutar los ocho escenarios: rango pequeño/grande, diez cazadores por cada uno de los
   dos rangos, puertas alternadas cada ciclo/cada 100 ciclos, y cálculo individual/compartido;
   realizar 30 repeticiones por escenario. Instrumentar el ciclo entre decisiones del
   jugador, excluyendo espera humana, red y renderizado. Comparar cada decisión con
   Dijkstra de referencia sin caché fuera del intervalo cronometrado y registrar máximo
   por ciclo, metadatos y corrección. Reiniciar cada repetición desde el mismo estado y
   procesar 1000 ciclos por repetición. La CLI acepta `--salida RUTA` y exporta un reporte
   JSON UTF-8 indentado con dos espacios. La ejecución de referencia guarda el reporte en
   `docs/evidencia/2026-11-04-terreno-cazador-benchmark.json`, bajo control de versiones;
   el contrato define el esquema y los campos detallados.
   Además, materializar y medir el snapshot de `cripta-06` versión `f9ed9afa683d` con
   catálogo `4b9e75a42be5`, 300 salas y 25 cazadores activos. Integrar esta medición como
   `validacion_referencia` sin alterar los ocho escenarios ni sobrescribir su evidencia
   histórica. El reporte nuevo registra ambos grupos, sus versiones/checksums y metadatos;
   los ciclos usan el mismo flujo real del modelo/reloj, sin red ni vistas.

### Optimización posterior al diagnóstico de rendimiento

El diagnóstico separado de la medición contractual identificó que `_buscar` se ejecuta
2.498 millones de veces durante la construcción y recorrido de distancias compartidas en
una ejecución representativa, acumulando 4.345 s bajo perfilador. Las cifras perfiladas
permiten priorizar cambios, pero no sustituyen ni amplían la evidencia contractual de
20 ms. No se modificarán el umbral, los ocho escenarios, el reparto 10/10, `cripta-06`, el
protocolo de 30 repeticiones × 1000 ciclos ni el esquema del reporte.

La optimización se aborda en este orden:

1. **Eliminar búsquedas lineales o binarias repetidas en las tablas de distancias**.
   `_construir_entrantes` y `_distancias_hacia_jugador` deben conservar Dijkstra ponderado,
   aristas dirigidas, puertas abiertas y el desempate por menor ID. Se pueden usar
   estructuras manuales propias, vectores de acceso directo por ID y colas propias existentes.
   No se introducirá `dict`, `set`, `heapq`, `bisect`, `collections`, grafos externos ni
   ningún índice/caché equivalente prohibido por la Constitución.
   La optimización debe probar y admitir IDs de sala dispersos o no contiguos. El acceso
   directo solo se aceptará si existe una construcción propia que mapee cada ID al índice
   válido sin asumir que los IDs llenan un rango compacto. Si el mapa no permite ese mapeo
   seguro, se conservará una alternativa propia correcta, como búsqueda binaria sobre
   registros ordenados o índice compacto auxiliar, sin `dict`, `set` ni bibliotecas prohibidas.
2. **Sustituir el escaneo completo de puertas en la caché cuando sea seguro**. La caché debe
   observar cambios reales de sala del jugador y puertas de todas las formas posibles:
   cambios directos del modelo, historial/reversión, replay, carga de partida y restauración
   de estado. Debe incluir cualquier cambio de puerta que ocurra fuera del benchmark. Si una
   puerta cambia cada ciclo, la revisión debe invalidar y recalcular las distancias; no debe
   construir una caché artificialmente persistente que oculte ese cambio.
   Esta revisión se implementará obligatoriamente y se verificará con cambios directos,
   historial, replay y carga. No se dejará como opción condicionada a la existencia de otro
   mecanismo previo.
3. **Separar el arnés de medición del trabajo real del juego**. El benchmark debe precalcular
   fuera del cronómetro la asociación entre instancia, cazador e índice. Dentro del intervalo
   medido no deben quedar `enemigos.index(...)`, búsquedas posteriores por identificador para
   observaciones ni validaciones auxiliares que no sean procesamiento del modelo/reloj.
   Permanecen dentro el evento del jugador, los eventos de enemigos, sus decisiones,
   movimientos, ataques, espera y reprogramaciones reales.
4. **Conservar los modos individual y compartido**. La búsqueda individual recalculará rutas
   desde cero para cada cazador y seguirá sirviendo como referencia independiente. La caché
   compartida solo podrá reutilizar distancias válidas para el estado actual; no convertirá
   el modo individual en una llamada compartida ni alterará el reparto de rangos ni los
   resultados comparables.

Cada optimización necesita criterios verificables:

- Las decisiones coinciden con el recálculo independiente en mapas ponderados, puertas
  abiertas/cerradas, conexiones unidireccionales, distancias iguales al rango, distancias
  superiores al rango y salas sin ruta.
- El resultado conserva el menor costo total y el menor ID entre vecinas empatadas.
- La caché comparte solo distancias válidas para el mismo jugador y el mismo estado físico
  de todas las puertas. Cambios por historial, replay o carga producen la misma revisión que
  un cambio directo.
- Si una puerta cambia cada ciclo, `obtener` invalidará y reconstruirá las distancias; si
  el estado no cambia, no habrá una reconstrucción falsa.
- En el benchmark, la asociación actor/índice queda fuera del cronómetro y la referencia
  externa sigue fuera del tiempo medido.
- El modo individual mantiene su cálculo independiente y el compartido mantiene la reutilización
  solo mientras su snapshot siga válido.

La revisión incremental no deberá concluir que todas las puertas están abiertas si puertas
cerradas se restauraron desde el estado cargado o desde el historial. Toda modificación de
puerta debe pasar por un mecanismo observable o revisar una revisión monotónica mantenida
por el modelo; no se aceptará una implementación basada en suposiciones sobre el estado
inicial o sobre el escenario concreto.

### Segunda iteración de optimización para los escenarios sintéticos

El reporte `terreno-cazador-benchmark-final.json` conserva una ejecución fallida: mantiene
cero discrepancias, pero el máximo sintético es 35.9268 ms. Fallan los cuatro escenarios de
rango grande y el escenario pequeño con cambio de puerta cada ciclo y modalidad compartida.
Este diagnóstico no modifica ni reutiliza cifras perfiladas como evidencia contractual.

Antes de optimizar, se ejecutará una medición separada y fuera de `--bench` con tres perfiles:

1. rutas individuales de rango grande sobre el fixture sintético;
2. reconstrucción de distancias compartidas cuando cambia una puerta;
3. procesamiento real de turnos, incluyendo reloj, decisión, movimiento y reprogramación,
   sin renderizado ni red.

Cada perfil comparará el primer ciclo con los ciclos siguientes. Las mediciones perfiladas
solo localizarán costos y no sustituirán el protocolo contractual de ocho escenarios,
30 repeticiones por escenario y 1000 ciclos por repetición.

La implementación de esta iteración conservará `_asignar_indices_benchmark` y el atributo
`_indice_benchmark` ya asociado antes de iniciar los ciclos. No se volverán a buscar actores
por instancia dentro del cronómetro. Las optimizaciones deben mantener Dijkstra ponderado,
conexiones dirigidas, costos efectivos, rango, puertas abiertas/cerradas, desempates y
equivalencia con el cálculo desde cero.

Los modos individual y compartido conservarán su significado actual: individual ejecutará
una búsqueda independiente por cazador; compartido reutilizará distancias solo para el
mismo jugador y revisión de puertas válida. Ninguna optimización permitirá usar `dict`,
`set`, `heapq`, `bisect`, `collections`, bibliotecas de grafos o cachés equivalentes
prohibidas por la Constitución.

El siguiente resultado contractual se guardará en
`docs/evidencia/terreno-cazador-benchmark-iteracion-2.json`. Se conservarán sin modificar
`docs/evidencia/terreno-cazador-benchmark-final.json` y
`docs/evidencia/terreno-cazador-benchmark-completo.json`. Si la iteración vuelve a fallar,
el reporte seguirá conservándose y las tareas de aceptación permanecerán pendientes. El
cierre exige cero discrepancias y máximo ≤20 ms en los ocho escenarios sintéticos y en
`cripta-06`.

### Tercera iteración: índice inmutable por cripta para búsquedas individuales

La iteración 2 confirmó cero discrepancias, pero dejó una única combinación sintética
fallida: rango grande (1000/10000), cambio de puerta cada 100 ciclos y cálculo individual.
El ciclo 2 realiza 39 decisiones individuales. El diagnóstico estableció que las 39
decisiones recrean juntas sus tablas/índices y que esas inicializaciones suman alrededor de
5.3 ms perfilados dentro del ciclo completo. Esa cifra es el costo agregado de las 39
inicializaciones, no el costo de una llamada individual ni una constante por decisión. Se
conserva solo como diagnóstico; no cuenta como evidencia contractual.

La optimización acotada será:

1. Construir una sola vez por cripta un índice propio e inmutable que relacione el ID de
   cada sala con su posición en el vector ordenado de salas. El índice pertenece a la cripta
   y se reutiliza por todas las búsquedas individuales.
2. Mantener separadas para cada búsqueda sus distancias, predecesores y cola de prioridad.
   Cada llamada a `_decidir_cazador_individual` conserva su frontera, estados y desempates
   locales; no reutilizará decisiones ni resultados de ruta de otra búsqueda.
3. Conservar Dijkstra ponderado, aristas dirigidas, costos efectivos, rango, puertas abiertas
   y cerradas, menor costo total y desempate por menor ID. No convertir el modo individual
   en compartido ni usar BFS.
4. Probar IDs densos, dispersos y muy grandes sin memoria proporcional al ID máximo. Para
   mapas que admitan un vector compacto seguro, usar acceso directo propio. Para IDs dispersos
   o grandes, usar registros propios ordenados con búsqueda binaria o un índice compacto
   auxiliar basado en posiciones reales de las salas; no usar `dict`, `set`, `heapq`, `bisect`,
   `collections`, grafos externos ni bibliotecas equivalentes prohibidas.

Criterios verificables:

- Mismo resultado que el cálculo individual desde cero en mapas densos, dispersos y de IDs
  grandes, criptas distintas, costos ponderados, conexiones dirigidas, puertas abiertas/
  cerradas, rango exacto y excedido y salas sin ruta.
- Dos búsquedas individuales simultáneas o consecutivas no comparten distancias, predecesores
  ni cola mutable.
- El índice estático no apunta a registros mutables de Dijkstra ni contiene resultados de ruta.
- La optimización elimina la reconstrucción por decisión, sin reducir la cobertura contractual
  ni cambiar los ocho escenarios, rangos, 30 repeticiones × 1000 ciclos o el límite de 20 ms.
- El siguiente reporte se conserva en
  `docs/evidencia/terreno-cazador-benchmark-iteracion-3.json`, sin modificar ninguna evidencia
  anterior. Si falla el umbral o hay discrepancias, `cumple_umbral=false` y las tareas de
  aceptación quedan pendientes.

Las tareas T034–T039 conservan su alcance y evidencia anterior. Esta iteración puede
actualizar el estado de T031 y T039 según el nuevo reporte contractual de iteración 3,
guardado en `docs/evidencia/terreno-cazador-benchmark-iteracion-3.json`, sin sobrescribir
los reportes previos. Si ese reporte cumple el cierre y pasan las pruebas requeridas, T052
puede marcar T031 y T039 como completadas; si falla, ambas permanecen pendientes.

## Estructura del proyecto

### Documentación de esta capacidad

```text
specs/001-terreno-cazador/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
└── contracts/
    └── datos-entrada-y-benchmark.md
```

### Código existente que deberá tocar la implementación

```text
adaptadores/                 # leer costo y rango y validar datos
bench/                        # escenarios, comparador de referencia y salida
controlador/                  # flujo del reloj, proyección a Pygame
estructuras/                  # prioridad propia para búsqueda ponderada
modelo/entidades/enemigo.py   # comportamiento cazador y decisión
modelo/mundo/salida.py        # costo efectivo
modelo/mundo/cripta_modelo.py # acceso a mapa ya ordenado
modelo/partida.py             # movimiento y costo programado
persistencia/                 # compatibilidad de datos/cachés/versiones
vista/                         # consola
vista_pygame/                  # snapshot y HUD/render
tests/                         # pruebas unitarias, integración y vista
```

**Decisión de estructura**: integrar en las capas MVC y de persistencia existentes,
reutilizando los patrones de carga, snapshots y pruebas actuales. El buscador de rutas
pertenece al modelo/estructura propia, no a la vista ni a un servicio externo.

## Riesgos y decisiones que deben mantenerse visibles

- El modelo actual representa salidas por dirección desde cada sala; no valida que toda
  salida tenga otra representación de regreso. El spec ahora define que una salida sin
  inversa es válida como unidireccional y que los costos se comparan solo si ambos sentidos
  están presentes.
- Las versiones de la API pueden cambiar. El benchmark de referencia usa un snapshot
  versionado y su checksum, no la respuesta viva del servidor; una nueva versión requiere
  renovar el snapshot y su evidencia, sin modificar datos de producción.
- La comparación sintética y la validación sobre `cripta-06` respaldan únicamente las
  topologías, versiones, estados y cantidades de actores registradas; no se extrapolan a
  mapas de cualquier escala.

## Seguimiento de complejidad

No aplica: el diseño respeta la constitución y reutiliza la arquitectura existente. La
cola de prioridad específica de caminos se considera una estructura propia del problema,
no una dependencia externa.

## Revisión final del rendimiento (2026-11-18)

La cola compacta redujo el cálculo individual de rango grande por debajo de 20 ms en los
dos escenarios objetivo del reporte iteración 3: 16.6045 ms con cambio de puerta cada ciclo
y 13.3090 ms cada 100 ciclos. El reporte conserva cero discrepancias, pero sigue fallando el
umbral por máximos registrados en el modo compartido y en `cripta-06`.

Un diagnóstico local separado ejecutó cinco repeticiones de cada escenario compartido de
rango grande y de `cripta-06`, con observación auxiliar de recolecciones GC. Ningún ciclo
superó 20 ms; el máximo observado fue 7.385 ms. Este ensayo es exploratorio, no contractual,
no demuestra la causa de los picos del reporte y no sustituye ni modifica la evidencia de
iteración 3. La suite completa también se verificó con 1192 pruebas pasadas.

No se identificó un costo alto y repetible en el modo compartido que respalde otro cambio
de código. La siguiente acción es una única medición contractual completa con el código y
el arnés actuales, en el equipo local y sin perfilador, guardada en
`docs/evidencia/terreno-cazador-benchmark-iteracion-4.json`. Debe conservar exactamente los
ocho escenarios, `cripta-06`, 30 repeticiones por grupo, 1000 ciclos por repetición, todas
las decisiones y el umbral de 20 ms. No se filtran ciclos ni se cambia la medición para
ocultar pausas del sistema. Se conservan íntegros los reportes anteriores. Si la nueva
medición vuelve a superar el umbral, se documenta el fallo y no se afirma cumplimiento; no
se repite hasta una nueva iteración planificada.

La medición de iteración 4 se ejecutó el 2026-11-18 con Python 3.12.10. Las decisiones
coincidieron con la referencia, pero el máximo global fue 24.8583 ms y
`cumple_umbral=false`; T031, T039 y T051 siguen pendientes. `cripta-06` tuvo máximo de
16.1787 ms. El reporte completo se conserva en la ruta de iteración 4.
