# Investigación: Terreno y cazador

**Fecha**: 2026-11-04
**Base**: `spec.md`, la Constitución, README y código/documentación presentes en el
repositorio. El PDF del curso no está disponible y no se consultó.

> **Actualización (2026-11-17)**: desde la investigación inicial se revisaron el PDF oficial
> y la API del curso. Los datos actuales de la API y la nueva validación de referencia se
> registran al final de este documento; reemplazan las conclusiones de escala que indicaban
> que solo estaba disponible una cripta offline de seis salas.

## Hallazgos del repositorio

- El juego usa Python 3.12; `pytest` valida el modelo y la integración, y Pygame es opcional.
- Las capas actuales son `modelo`, `controlador`, `vista`, `vista_pygame`, `adaptadores`,
  `persistencia` y `bench`. El reloj virtual ordena eventos por `(tiempo, secuencia)`.
- `Salida` conserva destino y estado de puerta, pero no un costo. El adaptador de esqueleto
  (`controlador/controlador_red.py`) construye las salidas desde JSON y hoy no lee `costo`.
- `Enemigo.decidir_accion` admite guardián, errante y rastreador; el turno de enemigo
  programa siempre una acción con costo base 100. `ControladorJuego` obtiene el costo
  devuelto por la acción del jugador para programar su siguiente decisión.
- `CriptaModelo` mantiene salas ordenadas en un `Vector` y consulta sus IDs con búsqueda
  binaria propia. La agenda `HeapMinimo` usa el orden de eventos, no es una cola genérica de
  prioridades para distancias.
- Las vistas se mantienen separadas: consola lee el modelo y Pygame recibe snapshots planos.
  Los contratos de snapshot ya incluyen `comportamiento` y `SalidaVisual`; el renderer de
  enemigos resuelve sprites mediante el ID y el comportamiento.
- El `--bench` integrado ejecuta benchmarks sintéticos registrados en `bench/casos`; evita
  crear la fuente de datos de juego. Pruebas existentes verifican que no se cargue Pygame.
  Herramientas de ciclo existentes usan medición local y semilla explícita, pero no cubren
  este algoritmo ni los ocho escenarios de la especificación.
- **Hallazgo histórico de la revisión del 2026-11-04**: los datos offline examinados entonces
  no incluían un costo de salida ni una ficha cazador; `cripta-01` era versión
  `fd58f7743b9e` y tenía 6 salas. El 2026-11-17 se añadió un cazador al catálogo offline y
  la cripta conservó su tamaño de 6 salas. La API y la cripta offline administran sus
  versiones por separado; sus identificadores no tienen que ser iguales.
- `bench/ciclo.py` genera un escenario sintético de 200 salas, pero no define un dataset de
  caminos fijo, versionado y con cambios de puertas para este feature. El fixture comparativo
  de 256 salas y el snapshot de referencia de 300 salas quedan separados y descritos en el
  contrato.

## Decisiones de diseño

### Dijkstra sobre aristas abiertas y costo de entrada

**Decisión**: calcular distancias mínimas ponderadas con las salidas abiertas del estado
actual. Para modalidad compartida, ejecutar la búsqueda desde el jugador sobre una vista
inversa de las aristas (cada arista original `u → v` se visita como `v → u` con su costo),
de modo que se obtengan `dist(u, jugador)` para todos los cazadores en una sola búsqueda.
Después, cada cazador elige entre sus propias salidas abiertas aquella que satisface la
ecuación de FR-007; el desempate se resuelve por ID de sala ascendente. La modalidad
individual ejecuta la referencia por separado para cada cazador.

**Razón**: Dijkstra resuelve costo positivo acumulado, a diferencia de BFS por cantidad de
salas. La búsqueda inversa también funciona con aristas dirigidas y puertas por sentido,
si se conserva exactamente la arista original y se filtra su estado actual. La búsqueda
compartida corresponde al caso de 20 cazadores persiguiendo a un mismo jugador.

**Alternativas consideradas**:
- BFS: descartada porque optimiza cantidad de aristas y contradice AB-07.
- Recorrer rutas completas y enumerarlas: descartado por crecimiento combinatorio.
- Ruta de biblioteca o `heapq`: descartadas por la Constitución.
- Una tabla global de distancias guardada sin invalidación: descartada porque jugador y
  puertas cambian entre turnos y produciría decisiones obsoletas.

### Estructuras y determinismo

**Decisión**: utilizar registros de distancia en `Vector`/índice ordenado propio y una
cola de prioridad específica para distancias implementada sobre `Vector`. Ordenar entradas
del heap por costo y luego ID para que exploración y resultados sean deterministas. La
selección final del vecino aplica el desempate explícito de FR-007, sin depender del orden
de iteración de datos externos.

**Razón**: `CriptaModelo` ya mantiene salas ordenadas y el proyecto dispone de búsqueda
binaria, vectores y heaps propios. `HeapMinimo` está acoplado a eventos por tiempo y
secuencia, por lo que reutilizarlo sin adaptación mezclaría los dos órdenes de prioridad.

**Alternativas consideradas**:
- Usar `dict`/`set` para `dist`/visitados: descartado por la Constitución.
- Indexar con el heap de eventos: descartado porque los criterios y estado de entrada son
  distintos.
- Un arreglo por `sala_id`: no se elige sin una garantía de IDs densos, que el modelo no
  establece.

### Integración con turnos y costos

**Decisión**: normalizar costo en la salida durante la carga, manteniendo el origen del
valor en JSON; propagar el costo de la salida elegida hasta el planificador de todo actor
que se mueva. Las acciones sin movimiento continúan con sus costos actuales. No cambiar el
camino lógico de errante/rastreador, salvo el costo temporal de cruzar una salida.

**Razón**: el modelo actual separa decisión y ejecución de acción; los costos deben
converger en un punto consistente antes de calcular el siguiente evento. La política
existente del reloj y el orden de eventos se conserva.

**Alternativas consideradas**:
- Calcular el costo en cada vista/controlador: descartado porque duplicaría reglas.
- Modificar el peso de todos los turnos enemigos: descartado porque cambiaría ataques y
  esperas.
- Dejar el costo de movimiento solo en la vista: descartado porque no cambiaría tiempo
  virtual.

### Validación de entrada y versiones

**Decisión**: extender la validación existente de las salidas y las fichas antes de
publicar una cripta jugable. Resolver ausencia de `costo` a 100 y comparar los dos costos
efectivos de cada conexión representada; rechazar `null`, tipos no enteros, valores <1,
desacuerdo de sentidos, rango faltante/inválido y datos incompatibles, con errores que
identifiquen los datos implicados.

**Razón**: el adaptador ya valida respuestas antes de publicar estructuras, y las
versiones de cripta/catálogo se guardan por separado. El error debe aparecer antes de
iniciar la cripta y no transformarse en un valor por defecto silencioso.

**Alternativas consideradas**:
- Aceptar `null` como ausencia: descartado por FR-013.
- Comparar costos declarados sin aplicar el default: descartado porque mezcla valores
  explícitos y efectivos y contradice AB-26.
- Igualar versiones de cripta y catálogo por texto: descartado; la persistencia trata
  ambas versiones de forma independiente y el spec no impone igualdad literal.

### Vistas y benchmark

**Decisión**: mantener las vistas como proyecciones: consola presenta el costo efectivo y
el estado; el snapshot de Pygame transporta el mismo costo y estado. Añadir a `bench` un
caso determinista sin fuente de red ni construcción de vista. Repetir las ocho
combinaciones treinta veces, registrar metadatos especificados, tomar el máximo por ciclo
y comparar cada elección con una búsqueda individual de referencia sin reutilización.

**Razón**: se conserva MVC y se mide tanto corrección como desempeño, no solo el tiempo de
una función aislada. El proyecto ya cuenta con un runner de benchmarks y utilidades de
medición que pueden extenderse.

### Actualización de dataset de rendimiento y cripta de referencia (2026-11-17)

La API del curso publica cinco criptas; `cripta-06`, llamada «Cripta de referencia», tiene
300 salas y versión `f9ed9afa683d`. El catálogo tiene versión `4b9e75a42be5`; el contenido
de `cripta-06` incluye 25 instancias de `ent_sabueso_oseo`, cuya ficha declara
`comportamiento: cazador` y `rango: 600`. Se verificó también la consulta de llaves: devuelve
cuatro ubicaciones para esa versión de cripta. La API anuncia un presupuesto de 63 solicitudes.

La revisión del enunciado confirma que el límite de 20 ms se refiere a la cripta de referencia
con decenas de cazadores activos. Por eso, el fixture sintético de 16×16 se conserva para los
ocho escenarios comparativos ya acordados (20 cazadores, reparto 10/10 y variaciones
controladas de rango, puertas y modalidad); se añade una validación contractual aparte con
un snapshot de `cripta-06` que active las 25 instancias publicadas. El snapshot y el checksum
se guardan en `bench/datos/`; los ciclos medidos no hacen solicitudes HTTP. El detalle del
protocolo y su reporte están definidos en el contrato del benchmark.

Esta actualización se basa en respuestas observadas de la API el 2026-11-17. Si cambian las
versiones publicadas, no se reemplaza silenciosamente el snapshot: se crea una nueva versión
de fixture y evidencia.

**Alternativas consideradas**:
- Renderizar mientras se cronometra: descartado porque SC-002 excluye renderizado.
- Incluir HTTP/latencia de la fuente: descartado porque la métrica excluye red y el modelo
  usa el mapa cargado.
- Validar solamente la distancia final: descartado porque el criterio requiere validar
  cada decisión del cazador.

## Decisiones aclaradas y puntos del Plan

- **Salida inversa ausente**: resuelto en la especificación. Se acepta como salida
   unidireccional; solo se comparan costos efectivos si existen ambas direcciones.
- **Dataset de comparación**: se conserva el fixture sintético
   `bench-terreno-cazador-grid-16x16`, versión `1.0.0`, con 256 salas en grilla ortogonal.
   Su topología, costos y estados iniciales/secuencia de puertas quedan definidos en el
   contrato. Es externo a los datos y la lógica de producción, determinista y no representa
   una cripta real.
- **Cripta de referencia**: la actualización del 2026-11-17 confirma que la API publica
   `cripta-06` con 300 salas y 25 instancias de cazador; se añade un snapshot de esos datos
   como validación separada del fixture comparativo.
- **Disponibilidad del catálogo**: al revisar la API, esta sí publica la ficha
   `ent_sabueso_oseo` con `comportamiento: cazador` y rango 600. La ficha offline
   `ent_cazador` no sustituye ni se confunde con la ficha online; cada fuente conserva sus
   propios datos y versión. La lógica de producción no debe inventar fichas.

## Referencias internas

- `.specify/memory/constitution.md`
- `README.md`
- `docs/ANALISIS_ARQUITECTURA.md`
- `controlador/controlador_red.py`
- `controlador/controlador_juego.py`
- `modelo/entidades/enemigo.py`
- `modelo/mundo/salida.py`
- `modelo/mundo/cripta_modelo.py`
- `modelo/partida.py`
- `estructuras/heap_minimo.py`
- `estructuras/array_ordenado.py`
- `bench/runner.py`
- `tests/test_bench_runner.py`
- `tests/vista/test_sin_pygame_en_replay_bench.py`
