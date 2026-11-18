# Tareas: Terreno y cazador

**Entrada**: Diseño de `specs/001-terreno-cazador/` (`spec.md`, `plan.md`,
`research.md`, `data-model.md`, `contracts/datos-entrada-y-benchmark.md` y
`quickstart.md`).

**Pruebas**: Requeridas por los escenarios de aceptación del spec y la trazabilidad de la
Constitución. Cada prueba nueva debe citar el ID AB y FR que verifica.

**Convenciones**:
- Cada tarea referencia los FR y AB que atiende.
- `[P]` marca trabajo que puede hacerse en paralelo sin editar los mismos archivos ni
  depender de una tarea incompleta.
- El mapa de benchmark es dato externo al juego; no agregar topología ni datos de cripta a
  la lógica de producción.

## Fase 2: Fundacional

**Propósito**: Preparar fixtures compartidos que son prerrequisito de las pruebas e
implementaciones de las historias. No se incluye Fase 1 de setup: el proyecto y su entorno
Python/pytest ya existen, así que no hay inicialización pendiente que justifique una fase.

- [X] T001 Crear `tests/fixtures/terreno_cazador.py` con constructores deterministas de payloads para salidas bidireccionales y unidireccionales, costos ausentes/inválidos y fichas de cazador con rangos válidos e inválidos; conservar los casos acordados en el contrato (FR-001, FR-012, FR-013; AB-01, AB-16, AB-19–AB-21, AB-24–AB-28).

**Punto de control**: Los payloads de pruebas quedan disponibles antes de comenzar cualquiera de las historias.

## Fase 3: Historia de usuario 1 — Atravesar salidas con costos distintos (Prioridad: P1)

**Objetivo**: Normalizar y validar costos efectivos, y aplicarlos al intervalo de movimiento de todos los actores sin alterar otras acciones.

**Prueba independiente**: Con payloads aislados, comprobar el costo predeterminado, acuerdos y conflictos entre sentidos, validaciones de costo y el intervalo de movimiento; correr las pruebas de carga y regresión indicadas en `quickstart.md`.

### Pruebas

- [X] T002 [P] [US1] Añadir pruebas de carga HTTP/offline para costo ausente (100), `null`, tipo/valor inválido y comparación de costos efectivos entre sentidos, incluyendo salidas unidireccionales, en `tests/test_datos_http.py`, `tests/test_datos_offline.py` y `tests/test_controlador_red.py`; cada caso debe citar su AB y FR (FR-001, FR-013; AB-01, AB-19, AB-24–AB-28).
- [X] T003 [P] [US1] Añadir pruebas de intervalo `max(1, costo_salida * 100 // velocidad)`, ajuste al cambiar velocidad y regresión de errantes/rastreadores y acciones no relacionadas en `tests/test_terreno_cazador.py`; identificar cada prueba con AB y FR (FR-002, FR-003; AB-02, AB-03, AB-14).

### Implementación

- [X] T004 [US1] Añadir a `modelo/mundo/salida.py` el costo efectivo de salida con valor por defecto 100, preservando la construcción y el comportamiento existentes de salidas (FR-001, FR-002; AB-01, AB-02, AB-11, AB-22, AB-28).
- [X] T005 [US1] Después de T004, leer y validar `costo` en `controlador/controlador_red.py`, `adaptadores/datos_http.py` y `adaptadores/datos_offline.py`: aceptar ausencia como 100; rechazar `null`, booleanos, no enteros y enteros menores que 1; comparar costos efectivos únicamente cuando existen ambos sentidos y rechazar desacuerdos con extremos y valores en el error; aceptar una salida unidireccional (FR-001, FR-013; AB-01, AB-19, AB-24–AB-28).
- [X] T006 [P] [US1] Después de T004, propagar el costo de la salida atravesada al cálculo del intervalo de todo movimiento en `modelo/partida.py` y `controlador/controlador_juego.py`; conservar sin cambios los costos de ataque, espera y demás acciones y mantener el ajuste de tiempo restante de P1 §2.3 cuando cambia la velocidad (FR-002, FR-003; AB-02, AB-03, AB-14).
- [X] T007 [US1] Tras T005 y T006, ejecutar y corregir las pruebas de carga y movimiento de esta historia con `python -m pytest -q tests/test_terreno_cazador.py tests/test_controlador_red.py tests/test_datos_http.py tests/test_datos_offline.py`; verificar explícitamente los criterios AB-01–AB-03, AB-14 y AB-19, AB-24–AB-28 (FR-001–FR-003, FR-013; AB-01–AB-03, AB-14, AB-19, AB-24–AB-28).

**Punto de control**: Las salidas tienen costo validado; todos los actores usan el intervalo correcto y sus demás acciones y comportamientos permanecen intactos.

## Fase 4: Historia de usuario 2 — Resolver el movimiento de un cazador (Prioridad: P1)

**Objetivo**: Incorporar el cazador y su persecución por costo mínimo usando el mapa y las puertas actuales, con rango, desempate, movimiento de un paso y evaluación reproducible.

**Prueba independiente**: Verificar ataques, espera, ruta mínima, desempates, cambios de puertas/posición, datos de catálogo y movimiento de una sala; comprobar que cálculo individual y compartido dan la misma decisión.

### Pruebas

- [X] T008 [P] [US2] Añadir a `tests/test_terreno_cazador.py` pruebas de aceptación que citen cada caso para ataque solo en sala compartida, espera sin ruta o sobre rango, ruta de menor costo, desempate por menor ID, recálculo ante cambios, conocimiento pese a niebla, no ataque a distancia, sala ocupada y ataque solo en el siguiente turno programado (FR-004–FR-009; AB-04–AB-10, AB-15, AB-17, AB-18, AB-23).
- [X] T009 [P] [US2] Crear `tests/test_catalogo_cazador.py` con pruebas de procedencia de costo/rango, rango obligatorio entero ≥1, rechazo previo al inicio por datos inválidos y rechazo por versiones incompatibles; cada prueba cita los AB/FR correspondientes (FR-012, FR-013; AB-16, AB-20, AB-21).

### Implementación del comportamiento

- [X] T010 [P] [US2] Integrar `comportamiento: "cazador"` y `rango` en `persistencia/catalogo.py`, `controlador/controlador_red.py` y `modelo/entidades/enemigo.py`; exigir rango entero ≥1 para cazadores, conservar los tres comportamientos existentes y rechazar catálogo/cripta inválidos o incompatibles antes de iniciar (FR-004, FR-012, FR-013; AB-16, AB-20, AB-21).
- [X] T011 [P] [US2] Implementar en `estructuras/heap_prioridad_ruta.py` una cola de prioridad propia para búsqueda ponderada, con orden determinista por costo y sala; no usar `heapq`, `bisect`, bibliotecas de grafos/rutas, ni `dict`/`set` como índice o caché (FR-006–FR-008; AB-07, AB-08, AB-13).
- [X] T012 [US2] Implementar en `modelo/buscador_rutas.py` búsqueda de costo mínimo que use solo salidas abiertas, respete salidas dirigidas y calcule las distancias al jugador sobre aristas entrantes para el modo compartido; en cada modo, elegir entre vecinas la de menor ID que satisfaga la igualdad de costo mínimo, sin índices/cachés prohibidos (FR-005–FR-009, FR-011; AB-05–AB-10, AB-13, AB-15).
- [X] T013 [US2] Implementar en `modelo/entidades/enemigo.py` la decisión del cazador en el orden contractual: atacar si comparte sala; esperar con costo 100 si no hay ruta o el costo mínimo supera el rango; de otro modo mover una sola salida con su costo; no atacar durante el movimiento que entra a la sala del jugador (FR-004–FR-008; AB-04–AB-08, AB-17, AB-18, AB-23).
- [X] T014 [US2] Integrar la decisión del cazador con el reloj en `modelo/partida.py` y `controlador/controlador_juego.py`: tomar posición actual del jugador, puertas actuales y estado de actores en cada turno; permitir compartir sala sin bloqueo; programar el movimiento con el costo de la salida y atacar solo en el siguiente turno programado tras llegar al jugador (FR-002, FR-004–FR-009; AB-02, AB-04–AB-10, AB-17, AB-18, AB-23).
- [X] T015 [US2] Ejecutar y corregir las pruebas de cazador y catálogo con `python -m pytest -q tests/test_terreno_cazador.py tests/test_catalogo_cazador.py`; comprobar que cada caso AB-04–AB-10, AB-15–AB-18 y AB-20–AB-23 tenga una prueba identificada (FR-004–FR-009, FR-013; AB-04–AB-10, AB-15–AB-18, AB-20–AB-23).

### Dataset y benchmark headless

- [X] T016 [P] [US2] Materializar como dato externo en `bench/datos/bench-terreno-cazador-grid-16x16-v1.0.0.json` el fixture del contrato: grilla 16×16 con IDs por filas, 256 salas, 480 conexiones bidireccionales, costos simétricos `1 + ((7*u + 11*v) mod 100)`, ocho puertas enumeradas y abiertas inicialmente, semilla 42; jugador en sala 136, vivo, vida_max/vida 1 000 000 000, ataque 10, defensa 5, velocidad 100, inventario_max 10 e inventario vacío; cazadores `cazador-01`–`cazador-20`, en ese orden, en salas 118–125, 134–135 y 137–146, diez con rango 1 y diez con rango 100 para los escenarios pequeños o rangos 1000 y 10000 para los grandes; todos vivos, vida_max/vida 100, ataque 1, defensa 0, velocidad 100, comportamiento `cazador`, regeneracion 0, suelta vacía, sin objetos ni efectos activos o pendientes, y tipo_id/nombre `bench-cazador`/`Cazador de benchmark` (FR-011; AB-13, AB-29).
- [X] T017 [US2] Calcular el SHA-256 del fixture de T016 y registrar identidad, versión, dimensiones, topología y checksum en `bench/datos/manifest.json`; mantener ambos archivos fuera de los módulos de producción y regenerar el checksum ante cualquier cambio del fixture (FR-011; AB-13, AB-29).
- [X] T018 [US2] Después de T014 y T017, implementar el caso de `--bench` en `bench/runner.py`, `bench/terreno_cazador.py` y `main.py`: ejecutar ocho escenarios con exactamente 20 cazadores y 30 repeticiones de 1000 ciclos por escenario; usar perfiles concretos de rangos 1/100 o 1000/10000, diez cazadores por rango, puertas alternadas cada 1 o 100 ciclos, modalidad individual o compartida, semilla 42 y estado inicial idéntico al fixture T016/contrato (jugador: vida actual/máxima 1 000 000 000, ataque 10, defensa 5, velocidad 100, inventario_max 10 e inventario vacío; cazadores: vida actual/máxima 100, ataque 1, defensa 0, velocidad 100, regeneracion 0, sin botín, objetos ni efectos, comportamiento `cazador`). Contrastar cada decisión con referencia desde cero fuera del tiempo cronometrado. Añadir `--salida RUTA` y generar el reporte de referencia en `docs/evidencia/2026-11-04-terreno-cazador-benchmark.json` como JSON UTF-8 indentado, con el esquema del contrato: claves de nivel superior `benchmark`, `fecha`, `fixture`, `equipo`, `semilla`, `estado_inicial`, `escenarios`, `cumple_umbral` y `decisiones_correctas`; dimensiones y SHA-256 del fixture; metadatos de equipo/entorno; ocho escenarios con `perfil_rango`, `rangos`, `cambio_puerta_cada_ciclos`, `modalidad` y `repeticiones`; y 30 repeticiones por escenario con `numero`, 1000 `duraciones_ciclo_ns`, `maximo_ciclo_ns` y `discrepancias` (FR-011; AB-13, AB-29).
- [X] T019 [P] [US2] Añadir o extender `tests/vista/test_sin_pygame_en_replay_bench.py` para comprobar que `--bench` ejecuta la medición sin instanciar vistas ni importar/iniciar Pygame, y que el JSON de `--salida` contiene identidad, versión, dimensiones y SHA-256 del fixture, ocho escenarios, 30 repeticiones por escenario, 1000 duraciones por repetición y discrepancias (FR-011; AB-13, AB-29).
- [X] T020 [US2] Tras T015–T019, ejecutar `python main.py --bench --salida docs/evidencia/2026-11-04-terreno-cazador-benchmark.json`; verificar ocho escenarios × 30 repeticiones × 1000 ciclos, decisiones idénticas a la referencia y máximo ≤20 ms en cada ciclo; guardar y revisar el JSON de evidencia con todas las duraciones, máximos, discrepancias y metadatos. Incorporar el reporte resultante a `docs/evidencia/` bajo control de versiones; no afirmar el cumplimiento si cualquier ciclo supera el umbral (FR-011; AB-13, AB-29).

**Punto de control**: El cazador satisface sus escenarios de aceptación y el benchmark documenta su dataset, checksum, corrección y latencias sin red ni vistas.

## Fase 5: Historia de usuario 3 — Reconocer el terreno y a los cazadores (Prioridad: P2)

**Objetivo**: Presentar en consola y Pygame los costos efectivos de todas las salidas de la sala y distinguir al cazador de los demás enemigos.

**Prueba independiente**: En ambas vistas, verificar costos declarados y predeterminados, salidas abiertas/cerradas y diferenciación visual del cazador.

### Pruebas

- [X] T021 [US3] Añadir pruebas de consola y Pygame para costo efectivo en salidas abiertas y cerradas, estado de puerta inequívoco y diferenciación del cazador, citando AB y FR en cada prueba, en `tests/test_vista_consola.py`, `tests/vista/test_salida_y_rejas.py` y `tests/vista/test_render_enemigos.py` (FR-001, FR-010; AB-11, AB-12, AB-22).

### Implementación

- [X] T022 [P] [US3] Actualizar `vista/vista_consola.py` para mostrar el costo efectivo de cada salida de la sala actual, incluidas las cerradas con su estado claramente indicado, sin trasladar lógica de rutas a la vista (FR-001, FR-010; AB-11, AB-22).
- [X] T023 [P] [US3] Propagar costo efectivo y comportamiento del enemigo en los contratos/snapshots de `vista_pygame/contratos.py` y `controlador/controlador_pygame.py`, conservando una proyección plana de modelo a vista (FR-001, FR-010; AB-11, AB-12, AB-22).
- [X] T024 [US3] Renderizar en `vista_pygame/render/render_sala.py` y `vista_pygame/render/render_actores.py` los costos efectivos de todas las salidas, el estado de las cerradas y una presentación distinguible del cazador; usar el fallback visual existente si no hay recurso específico (FR-001, FR-010; AB-11, AB-12, AB-22).
- [X] T025 [US3] Ejecutar y corregir las pruebas de ambas vistas con `python -m pytest -q tests/test_vista_consola.py tests/vista/test_salida_y_rejas.py tests/vista/test_render_enemigos.py`; verificar por separado AB-11, AB-12 y AB-22 en consola y Pygame (FR-001, FR-010; AB-11, AB-12, AB-22).

**Punto de control**: Las dos vistas muestran la misma información de terreno y diferencian al cazador sin calcular rutas.

## Fase 6: Pulido y verificación transversal

**Propósito**: Registrar las decisiones, comprobar regresiones y confirmar que las restricciones del proyecto se mantienen.

- [X] T026 Actualizar `docs/DECISIONES.md` con las decisiones de implementación que difieran o concreten el Plan y con la evidencia de `--bench`; no registrar afirmaciones de rendimiento sin resultados reproducibles (FR-001–FR-013; AB-01–AB-29).
- [X] T027 Ejecutar los comandos de regresión de `specs/001-terreno-cazador/quickstart.md` y revisar `tests/` para confirmar trazabilidad de todos los AB-01–AB-29 a pruebas con sus FR; verificar que `--replay` y `--bench` no instancien vistas, que no se añadieron bibliotecas/índices/cachés prohibidos y que no se afectó el presupuesto de solicitudes (FR-001–FR-013; AB-01–AB-29).

## Validación adicional en la cripta de referencia

La siguiente extensión conserva el benchmark sintético completado en T016–T020 y cubre el
requisito oficial de rendimiento sobre `cripta-06`. El snapshot es un fixture de benchmark,
no un dato de producción; ningún ciclo medido realiza solicitudes HTTP.

- [X] T028 [P] Añadir `tests/test_bench_terreno_cazador_referencia.py` para comprobar el contrato del snapshot y del reporte de referencia: versiones fijadas, 300 salas, 25 instancias activas en las salas declaradas, 30 repeticiones de 1000 ciclos, metadata y SHA-256, discrepancias vacías cuando las decisiones son correctas, y ausencia de red/vistas en el intervalo medido (FR-014; AB-30; SC-004).
- [X] T029 Materializar en `bench/datos/cripta-06-terreno-cazador-vf9ed9afa683d.json` el snapshot del esqueleto, los costos/puertas, los datos de catálogo necesarios y las 25 instancias `ent_sabueso_oseo` de la API. Registrar versión de cripta `f9ed9afa683d`, versión de catálogo `4b9e75a42be5`, ubicaciones, dimensiones y SHA-256 en `bench/datos/manifest.json`. La descarga inicial debe mantenerse dentro del presupuesto publicado de 63 solicitudes. No incluir solicitudes HTTP en el benchmark ni trasladar esos datos a la lógica de producción (FR-014; AB-30).
- [X] T030 Extender `bench/terreno_cazador.py`, `bench/runner.py` y `main.py` para que `--bench` conserve los ocho escenarios sintéticos y agregue la validación sobre el snapshot de referencia: 25 cazadores activos, estado reproducible, semilla 42, acción `W`, 30 repeticiones de 1000 ciclos y comparación con el recálculo desde cero fuera del cronómetro. Agregar `validacion_referencia` al reporte sin eliminar ni reinterpretar el campo `escenarios` ya existente; no hacer solicitudes HTTP ni crear vistas/Pygame (FR-014; AB-30; SC-004).
- [ ] T031 Ejecutar una medición posterior completa con `python main.py --bench --salida docs/evidencia/terreno-cazador-benchmark-iteracion-3.json`; comprobar ambos grupos, sus metadatos y checksums, todas las decisiones y todos los máximos. T031 solo se completa si el reporte iteración-3 contiene los ocho escenarios sintéticos y la validación de `cripta-06`, exactamente 30 repeticiones × 1000 ciclos por grupo, cero discrepancias y ningún máximo >20 ms. Si falla el umbral o hay discrepancias, fijar `cumple_umbral=false`, mantener T031 pendiente y conservar el reporte iteración-3. El reporte `docs/evidencia/terreno-cazador-benchmark-final.json` permanece intacto como evidencia fallida anterior y no se reemplaza ni usa como aprobación de T031 (FR-014; AB-30; SC-004).
- [X] T032 Actualizar `docs/DECISIONES.md` con la razón para mantener los ocho escenarios controlados y añadir la validación de referencia, las versiones observadas y los resultados reales de T031; declarar límites sin generalizar más allá de los datasets medidos (FR-014; AB-30; SC-004).
- [X] T033 Ejecutar las pruebas focalizadas del cazador y benchmark, las regresiones indicadas en `quickstart.md` y la suite completa. Registrar resultados reales; no marcar el cierre si quedan fallos atribuibles a esta extensión (FR-001–FR-014; AB-01–AB-30; SC-001–SC-004).

## Dependencias y orden de ejecución

### Dependencias entre fases

- Fase 2 fundacional: T001 no depende de tareas previas y bloquea todas las historias.
- US1: T002 y T003 dependen de T001; T004 depende de T002/T003; T005 y T006 dependen de T004; T007 depende de T005/T006.
- US2: comienza después de US1 para reutilizar el costo validado. T008 y T009 preparan las pruebas; T010, T011 y T016 son componentes independientes; T012 depende de T011; T013 depende de T010 y T012; T014 depende de T013; T017 depende de T016; T018 depende de T014 y T017; T019 depende de T017 y puede prepararse en paralelo con T018 una vez satisfechas las dependencias de T018 (T014 y T017); T015 depende de T010–T014; T020 depende de T015, T018 y T019.
- US3: depende de US1 (costo en el modelo) y US2 (comportamiento cazador). T021 prepara pruebas; T022 y T023 pueden avanzar en paralelo; T024 depende de T023; T025 depende de T022–T024.
- Pulido: T026 y T027 dependen de las historias que validan; ejecutar T027 después de integrar todas las tareas anteriores.
- Validación de referencia: T028 y T029 pueden prepararse en paralelo al tener fijado este contrato; T030 depende de ambas; T031 depende de T030; T032 registra el resultado de T031; T033 cierra tras T032.

### Dependencias entre historias

- **US1 (P1)**: primera historia implementable tras T001; establece el costo de salida y su intervalo.
- **US2 (P1)**: depende de US1 porque el movimiento del cazador usa el costo y la programación común de acciones.
- **US3 (P2)**: depende de US1 y US2 para presentar los costos del modelo y distinguir el nuevo comportamiento.

### Oportunidades de paralelismo

- T002 y T003: pruebas de carga y pruebas de movimiento en archivos distintos, tras T001.
- T005 y T006: validación de entradas y propagación del costo al reloj en archivos distintos, tras T004.
- T008 y T009: pruebas de decisión y de catálogo en archivos distintos.
- T010, T011 y T016: catálogo, cola de prioridad y materialización del fixture en archivos distintos.
- T016 puede implementarse en paralelo con T010/T011; T019 puede escribirse en paralelo con T018 una vez completadas las dependencias de T018 (T014 y T017), pues el esquema JSON está fijado por el contrato.
- T022 y T023: consola y contrato/snapshot Pygame en archivos distintos.
- T028 y T029: prueba del contrato y materialización del fixture de `cripta-06` en archivos distintos; ambos deben respetar las versiones fijadas.

No ejecutar tareas paralelas que modifiquen el mismo archivo; coordinar los cambios de tests compartidos antes de integrarlos.

## Estrategia de implementación

### MVP

1. Completar T001 en la Fase 2 fundacional.
2. Completar US1 (T002–T007) y validar movimiento con costos sin incorporar el cazador.
3. **MVP funcional**: costo predeterminado y validado, intervalo correcto para todos los actores y regresiones existentes intactas.

### Incrementos

1. Implementar US2 con pruebas de aceptación; validar el cazador frente a rutas dirigidas, puertas cambiantes y recálculo de referencia.
2. Materializar el fixture y ejecutar el benchmark headless antes de respaldar el umbral de 20 ms.
3. Implementar US3 después de estabilizar el modelo y verificar ambas vistas.
4. Completar T026–T027, documentando resultados y confirmando todos los AB trazables.

## Revisión de coherencia

- La secuencia de ocho escenarios, 20 cazadores, reparto de rangos, 30 repeticiones, semilla, fixture, puertas y ciclo cronometrado sigue el Plan y el contrato.
- La validación adicional usa las 25 instancias publicadas de `cripta-06` para cubrir el límite oficial en la cripta de referencia; no altera los ocho escenarios ni sus 20 cazadores.
- El fixture versionado y su checksum se mantienen fuera de la lógica de producción; el
  reporte JSON reproducible se conserva como evidencia versionada en `docs/evidencia/`.
- Los atributos de todos los actores del fixture están fijados en el contrato; T016 debe copiarlos literalmente al archivo de datos y no convertirlos en valores de producción.

## Optimización posterior al diagnóstico

La siguiente fase empieza después de T033 y no debe modificar ni sobrescribir el reporte
contractual anterior. El perfil reciente es diagnóstico, no evidencia de cumplimiento:
T031 seguirá pendiente hasta que el reporte final completo medido sin perfilador tenga cero
discrepancias y ningún máximo superior a 20 ms.

- [X] T034 Añadir pruebas de regresión para tablas directas de distancias y extracción de vecinos en `tests/test_terreno_cazador.py` y `tests/test_bench_terreno_cazador.py`: comparación con recálculo desde cero en mapas ponderados, puertas abiertas/cerradas, conexiones unidireccionales, límite de rango exacto, rango excedido y sala sin ruta; preservar menor costo y menor ID en empates. Incluir mapas con IDs de sala dispersos o no contiguos y verificar que el resultado no depende de que los IDs formen una secuencia compacta (FR-006–FR-008, FR-011, FR-014; AB-07–AB-10, AB-30).
- [X] T035 Después de T034, optimizar `_construir_entrantes`, `_distancias_hacia_jugador`, `_decidir_cazador_individual` y `decidir_cazador` en `modelo/buscador_rutas.py` usando `Vector`, listas propias/arrays autorizados y acceso directo por ID de sala cuando exista un mapeo propio seguro y completo; en ese caso, eliminar `_buscar` de los recorridos masivos. Para mapas con IDs dispersos, usar una alternativa propia correcta definida por el Plan: búsqueda binaria sobre registros ordenados o índice compacto auxiliar, sin `dict`, `set` ni bibliotecas prohibidas. En ambos casos, conservar Dijkstra ponderado, aristas dirigidas, rango y desempate por menor ID (FR-006–FR-008, FR-011; AB-07–AB-10, AB-13).
- [X] T036 Después de T034, añadir pruebas obligatorias de invalidación de caché en `tests/test_terreno_cazador.py` para cambios de sala del jugador, apertura/cierre directo y restauración por historial. Añadir también pruebas obligatorias de las rutas existentes de replay y carga en `tests/`; verificar que toda restauración reproduce el estado físico de las puertas, que abrir/cerrar/restaurar invalida solo cuando cambia el estado y que, si una puerta cambia cada ciclo, la caché reconstruye distancias (FR-008, FR-011, FR-014; AB-09, AB-10, AB-13, AB-30).
- [X] T037 Después de T036, integrar en `modelo/buscador_rutas.py`, `modelo/partida.py`, `modelo/reloj.py` y las rutas de deshacer/carga existentes un mecanismo obligatorio y verificable de revisión incremental de jugador y puertas; almacenar revisiones observadas sin escanear todas las salidas por cada consulta y cubrir cambios directos, operaciones de historial, replay y carga; conservar la reconstrucción necesaria cuando una puerta cambie cada ciclo (FR-008, FR-011, FR-014; AB-09, AB-10, AB-13, AB-30).
- [X] T038 Precalcular fuera del cronómetro en `bench/terreno_cazador.py` la asociación instancia/actor/índice y los índices de referencia de _correr_escenario y _correr_referencia; eliminar `enemigos.index(...)` y búsquedas posteriores por identificador del intervalo medido; conservar dentro del ciclo turno del jugador, eventos de enemigos, decisiones, movimiento/ataque/espera y reprogramación real; mantener la referencia independiente fuera del cronómetro (FR-011, FR-014; AB-13, AB-29, AB-30).
- [ ] T039 Tras T035, T037 y T038, ejecutar las pruebas focalizadas y regresiones, la suite completa con Python 3.12 y el benchmark contractual final: conservar ocho escenarios y `cripta-06`, 30 repeticiones × 1000 ciclos, cero discrepancias y máximo ≤20 ms. Generar `docs/evidencia/terreno-cazador-benchmark-final.json` con el mismo esquema del reporte completo, sin usar cifras perfiladas ni modificar los reportes anteriores. Reutilizar exactamente la ruta y las condiciones de T031. Si el reporte cumple el umbral y todas las decisiones coinciden con la referencia, marcar T031 como completada; T039 solo se completa cuando, además, pasan las pruebas obligatorias y se actualiza `docs/DECISIONES.md` con el cambio y los resultados reales. Si falla el umbral o hay discrepancias, conservar el reporte final, dejar T031 y T039 pendientes, mantener `cumple_umbral=false` y documentar el fallo sin cambiar los criterios. Si el benchmark pasa pero alguna prueba falla, T031 puede completarse y T039 permanece pendiente, documentando los fallos (FR-006–FR-008, FR-011, FR-014; AB-07–AB-10, AB-13, AB-29, AB-30).

### Dependencias de optimización

- T034 no depende de cambios de implementación y puede comenzar primero.
- T035 depende de T034.
- T036 depende de T034 y puede avanzar en paralelo con T035 si no comparten archivos: T036 trabaja pruebas de caché en `tests/test_terreno_cazador.py`, mientras T035 trabaja la implementación en `modelo/buscador_rutas.py`.
- T037 depende de T036 y debe invalidar mediante mecanismos compatibles con historial, replay y carga.
- T038 puede ejecutarse en paralelo con T035 y T037 si no comparte archivos editados por esas tareas, pero debe mantener el flujo real de `Reloj` y `Partida`.
- T039 depende de T035, T037 y T038 y no debe marcarse aprobada sin el reporte contractual final.

## Segunda iteración de diagnóstico y optimización

Esta iteración conserva el alcance y la evidencia anterior de T034–T039; no altera su
definición ni sobrescribe sus reportes. T046 puede actualizar el estado de T039 según el
nuevo resultado contractual. Los cinco escenarios sintéticos fallidos tienen prioridad; no
cambian sus rangos, mapas, puertas, repeticiones, modalidades ni umbral.

- [X] T040 Ejecutar fuera de `--bench` un perfil diagnóstico de las rutas individuales del perfil de rango grande mediante un comando o archivo temporal local separado. Separar el primer ciclo de los siguientes y registrar llamadas, tiempo propio/acumulado y costo de `_decidir_cazador_individual`, sin usar los máximos perfilados como evidencia contractual (FR-011; AB-13).
- [X] T041 Ejecutar fuera de `--bench` un perfil diagnóstico de `CacheDistanciasCazador.obtener`, `_construir_entrantes` y `_distancias_hacia_jugador` al cambiar una puerta mediante un comando o archivo temporal local separado. Separar inicialización y ciclos posteriores, registrar reconstrucción/reutilización y no registrarlo como validación contractual (FR-008, FR-011; AB-09, AB-13).
- [X] T042 Ejecutar fuera de `--bench` un perfil diagnóstico del procesamiento real de turnos mediante `Reloj`, `Partida` y `_correr_escenario` mediante un comando o archivo temporal local separado. Medir por separado reloj, extracción/ejecución de eventos, decisiones, movimiento, reprogramación y observaciones auxiliares; distinguir el primer ciclo de los siguientes y conservar `_indice_benchmark` sin buscar actores por ID dentro del cronómetro (FR-011; AB-13).
- [X] T043 Después de T040–T042, añadir pruebas de regresión en `tests/test_terreno_cazador.py` y `tests/test_bench_terreno_cazador.py` para rutas individuales ponderadas, reconstrucción por cambio de puerta, recorridos dirigidos, rangos exactos y excedidos, puertas abiertas/cerradas, rutas inexistentes, empates por menor ID y equivalencia individual/compartida con una referencia independiente (FR-006–FR-008, FR-011, FR-014; AB-07–AB-10, AB-13, AB-30).
- [X] T044 Implementar en `modelo/buscador_rutas.py`, `modelo/partida.py`, `modelo/reloj.py` y `bench/terreno_cazador.py` únicamente las optimizaciones respaldadas por T040–T043: conservar Dijkstra ponderado y modos individuales/compartidos, conservar `_indice_benchmark`, evitar búsquedas auxiliares dentro del cronómetro y no introducir estructuras o bibliotecas prohibidas (FR-006–FR-008, FR-011, FR-014; AB-07–AB-10, AB-13, AB-29, AB-30).
- [ ] T045 Ejecutar las pruebas focalizadas, replay/carga y la suite completa con Python 3.12 después de T044. Si pasan, ejecutar el benchmark contractual una sola vez hacia `docs/evidencia/terreno-cazador-benchmark-iteracion-2.json`; conservar los ocho escenarios, `cripta-06`, 30 repeticiones × 1000 ciclos, cero discrepancias y máximo ≤20 ms. Conservar el reporte aunque falle y fijar `cumple_umbral=false` si existe cualquier discrepancia o si algún ciclo supera 20 ms. Dejar T039/T045 pendientes si hay discrepancias o cualquier máximo >20 ms y no modificar los reportes anteriores (FR-006–FR-008, FR-011, FR-014; AB-07–AB-10, AB-13, AB-29, AB-30).
- [X] T046 Actualizar `docs/DECISIONES.md` con el resultado previo de `terreno-cazador-benchmark-final.json`, los hallazgos de T040–T042, los cambios validados de T044 y el resultado real de T045. Si el reporte iteración-2 cumple el cierre con cero discrepancias y máximos ≤20 ms, marcar T039, T045 y T046 como completadas y documentar la aprobación. Si el reporte vuelve a fallar por discrepancias o máximos >20 ms, T039 y T045 quedan pendientes, pero T046 puede completarse al conservar y documentar el fallo real, mantener `cumple_umbral=false` y no cambiar los criterios (FR-011, FR-014; AB-13, AB-29, AB-30).

### Dependencias de la segunda iteración

- T040–T042 pueden ejecutarse en paralelo porque son perfiles separados y no modifican el código. Cada tarea usa su propio comando temporal o archivo temporal separado, por ejemplo con nombres propios bajo la sesión temporal o `bench/salidas/`, sin escribir el mismo archivo ni compartir resultados incompletos; no crean ni sobrescriben reportes contractuales.
- T043 depende de T040–T042 y prepara las pruebas de regresión.
- T044 depende de T043 y no debe aplicar optimizaciones no respaldadas por mediciones o pruebas.
- T045 depende de T044 y genera exclusivamente `docs/evidencia/terreno-cazador-benchmark-iteracion-2.json`.
- T046 depende de T045 y registra el resultado previo y el nuevo; no cambia T039 ni el umbral.

## Tercera iteración: índice inmutable por cripta para rutas individuales

- [X] T047 Añadir pruebas en `tests/test_terreno_cazador.py` y `tests/test_buscador_rutas.py` para índices de sala densos, dispersos y de IDs muy grandes; comprobar criptas distintas y ausencia de asignación proporcional al ID máximo. Para mapas densos debe probar acceso directo propio; para IDs dispersos/grandes debe probar búsqueda binaria propia o índice compacto auxiliar sin `dict`, `set` ni bibliotecas prohibidas (FR-006–FR-008; AB-07–AB-08).
- [X] T048 Añadir pruebas de equivalencia individual en `tests/test_terreno_cazador.py` y `tests/test_bench_terreno_cazador.py`: mapas ponderados, conexiones dirigidas, puertas abiertas/cerradas, rango exacto/excedido, empate por menor ID y sala sin ruta. Verificar que dos búsquedas individuales no compartan distancias, predecesores ni cola y que coincidan con el recálculo independiente (FR-005–FR-009, FR-011; AB-05–AB-10, AB-13).
- [X] T049 Implementar en `modelo/mundo/cripta_modelo.py` un índice propio e inmutable por cripta que relacione ID de sala con posición en el vector ordenado. Construirlo una vez al finalizar la carga; usar acceso directo compacto solo si es seguro y una alternativa propia binaria/compacta para IDs dispersos o grandes, sin asignar memoria proporcional al máximo (FR-006–FR-008; AB-07–AB-08).
- [X] T050 Reutilizar en `modelo/buscador_rutas.py` el índice inmutable de la cripta dentro de `_crear_indice_registros` y las búsquedas individuales. Mantener distancias, predecesores y cola locales por búsqueda; no apuntar el índice a registros mutables de Dijkstra, no reutilizar rutas y no alterar el modo compartido (FR-005–FR-009, FR-011; AB-05–AB-10, AB-13).
- [ ] T051 Ejecutar las pruebas focalizadas nuevas y existentes, replay/carga y la suite completa con Python 3.12. Solo si pasan, ejecutar una sola medición contractual y guardar `docs/evidencia/terreno-cazador-benchmark-iteracion-3.json`: ambos grupos, ocho escenarios sintéticos y `cripta-06`, 30 repeticiones × 1000 ciclos en cada grupo, cero discrepancias y máximo ≤20 ms. Si hay discrepancias o ciclos >20 ms, conservar el reporte, fijar `cumple_umbral=false` y dejar T031, T039 y T051 pendientes (FR-005–FR-009, FR-011, FR-014; AB-05–AB-10, AB-13, AB-29, AB-30).
- [X] T052 Actualizar `docs/DECISIONES.md` con las pruebas, el índice implementado y los resultados reales de T051. Si `docs/evidencia/terreno-cazador-benchmark-iteracion-3.json` cumple el protocolo completo, cero discrepancias y máximos ≤20 ms y además pasan todas las pruebas requeridas, marcar T031, T039, T051 y T052 como completadas. Si falla el umbral o hay discrepancias, T031, T039 y T051 permanecen pendientes, fijar `cumple_umbral=false` y documentar el resultado real; T052 puede completarse al documentar el fallo sin cambiar el umbral (FR-011, FR-014; AB-13, AB-29, AB-30).

### Dependencias de la tercera iteración

- T047 prepara las pruebas del índice y puede comenzar primero.
- T048 depende de T047 y define equivalencia de decisiones y aislamiento mutable.
- T049 depende de T047 y construye el índice inmutable por cripta.
- T050 depende de T048 y T049 y debe mantener independiente toda búsqueda individual.
- T051 depende de T050 y ejecuta primero todas las pruebas antes del único benchmark contractual.
- T052 depende de T051 y documenta aprobación o fallo según el reporte real.

## Revisión final de rendimiento

- [X] T053 Revisar los máximos del reporte de iteración 3 y ejecutar un diagnóstico no contractual de cinco repeticiones por escenario compartido de rango grande y `cripta-06`; observar eventos GC sin modificar el cronómetro contractual. Registrar que el máximo diagnóstico fue 7.385 ms, que no se reprodujeron ciclos >20 ms, que el resultado no prueba la causa de los picos anteriores y que la suite completa pasó 1192 pruebas. No modificar el modo compartido ni atribuir cumplimiento a este diagnóstico (FR-011, FR-014; AB-13, AB-29, AB-30).
- [X] T054 Después de confirmar las pruebas focalizadas, replay/carga y suite completa con Python 3.12, ejecutar una sola medición contractual completa con el código actual y guardar `docs/evidencia/terreno-cazador-benchmark-iteracion-4.json`. Conservar los ocho escenarios sintéticos y `cripta-06`, 30 repeticiones × 1000 ciclos en cada grupo, cero discrepancias y máximo ≤20 ms. No usar perfilador, filtrar ciclos, cambiar el cronómetro ni modificar reportes anteriores. Si cumple, puede cerrar T031, T039, T051 y T054; si falla, mantener `cumple_umbral=false`, dejar T031/T039/T051 pendientes y conservar el reporte completo de fallo. T054 puede marcarse completada al ejecutar y clasificar íntegramente el resultado, aunque no cumpla el umbral (FR-011, FR-014; AB-13, AB-29, AB-30).
- [X] T055 Actualizar `docs/DECISIONES.md` con el resultado real de T054, las versiones y checksum, las pruebas previas y el estado de T031/T039/T051. No declarar cumplimiento si cualquier ciclo supera 20 ms ni cambiar el criterio (FR-011, FR-014; AB-13, AB-29, AB-30).

### Dependencias de la revisión final

- T053 registra el diagnóstico ya realizado y puede cerrarse junto con la actualización documental.
- T054 depende de las pruebas focalizadas, replay/carga y suite completa; solo se ejecuta una vez y conserva el reporte aunque falle.
- T055 depende de T054 y registra aprobación o fallo sin alterar los criterios de aceptación.
