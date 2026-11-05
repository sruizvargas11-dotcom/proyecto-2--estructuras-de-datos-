# Investigación: Terreno y cazador

**Fecha**: 2026-11-04
**Base**: `spec.md`, la Constitución, README y código/documentación presentes en el
repositorio. El PDF del curso no está disponible y no se consultó.

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
- El conjunto offline examinado no incluye un costo de salida ni una ficha cazador. Las
  versiones de cripta y catálogo se administran por separado en persistencia; no se debe
  inferir que sus identificadores de versión tienen que ser iguales entre sí.
- La única cripta offline versionada disponible es `cripta-01`, versión `fd58f7743b9e`,
  con 6 salas; no cumple el requisito de benchmark de usar un mapa mayor. `bench/ciclo.py`
  genera un escenario sintético de 200 salas, pero no define un dataset de caminos fijo,
  versionado y con cambios de puertas para este feature.

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

**Alternativas consideradas**:
- Renderizar mientras se cronometra: descartado porque SC-002 excluye renderizado.
- Incluir HTTP/latencia de la fuente: descartado porque la métrica excluye red y el modelo
  usa el mapa cargado.
- Validar solamente la distancia final: descartado porque el criterio requiere validar
  cada decisión del cazador.

## Decisiones aclaradas y puntos del Plan

- **Salida inversa ausente**: resuelto en la especificación. Se acepta como salida
   unidireccional; solo se comparan costos efectivos si existen ambas direcciones.
- **Dataset de rendimiento**: no hay en el repositorio un mapa fijo/versionado que satisfaga
   la escala; la cripta offline tiene solo 6 salas. Se elige el fixture sintético
   `bench-terreno-cazador-grid-16x16`, versión `1.0.0`, con 256 salas en grilla ortogonal.
   Su topología, costos y estados iniciales/secuencia de puertas quedan definidos en el
   contrato. Es externo a los datos y la lógica de producción, determinista y no representa
   una cripta real.
- **Disponibilidad del catálogo**: el catálogo presente no incluye `rango` ni el nuevo
   comportamiento. La fuente de datos debe publicar una ficha y una versión compatibles;
   la implementación no debe ocultar la falta de datos ni fabricar una ficha en producción.

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
