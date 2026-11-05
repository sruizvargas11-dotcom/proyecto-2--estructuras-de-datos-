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

- [ ] T001 Crear `tests/fixtures/terreno_cazador.py` con constructores deterministas de payloads para salidas bidireccionales y unidireccionales, costos ausentes/inválidos y fichas de cazador con rangos válidos e inválidos; conservar los casos acordados en el contrato (FR-001, FR-012, FR-013; AB-01, AB-16, AB-19–AB-21, AB-24–AB-28).

**Punto de control**: Los payloads de pruebas quedan disponibles antes de comenzar cualquiera de las historias.

## Fase 3: Historia de usuario 1 — Atravesar salidas con costos distintos (Prioridad: P1)

**Objetivo**: Normalizar y validar costos efectivos, y aplicarlos al intervalo de movimiento de todos los actores sin alterar otras acciones.

**Prueba independiente**: Con payloads aislados, comprobar el costo predeterminado, acuerdos y conflictos entre sentidos, validaciones de costo y el intervalo de movimiento; correr las pruebas de carga y regresión indicadas en `quickstart.md`.

### Pruebas

- [ ] T002 [P] [US1] Añadir pruebas de carga HTTP/offline para costo ausente (100), `null`, tipo/valor inválido y comparación de costos efectivos entre sentidos, incluyendo salidas unidireccionales, en `tests/test_datos_http.py`, `tests/test_datos_offline.py` y `tests/test_controlador_red.py`; cada caso debe citar su AB y FR (FR-001, FR-013; AB-01, AB-19, AB-24–AB-28).
- [ ] T003 [P] [US1] Añadir pruebas de intervalo `max(1, costo_salida * 100 // velocidad)`, ajuste al cambiar velocidad y regresión de errantes/rastreadores y acciones no relacionadas en `tests/test_terreno_cazador.py`; identificar cada prueba con AB y FR (FR-002, FR-003; AB-02, AB-03, AB-14).

### Implementación

- [ ] T004 [US1] Añadir a `modelo/mundo/salida.py` el costo efectivo de salida con valor por defecto 100, preservando la construcción y el comportamiento existentes de salidas (FR-001, FR-002; AB-01, AB-02, AB-11, AB-22, AB-28).
- [ ] T005 [US1] Después de T004, leer y validar `costo` en `controlador/controlador_red.py`, `adaptadores/datos_http.py` y `adaptadores/datos_offline.py`: aceptar ausencia como 100; rechazar `null`, booleanos, no enteros y enteros menores que 1; comparar costos efectivos únicamente cuando existen ambos sentidos y rechazar desacuerdos con extremos y valores en el error; aceptar una salida unidireccional (FR-001, FR-013; AB-01, AB-19, AB-24–AB-28).
- [ ] T006 [P] [US1] Después de T004, propagar el costo de la salida atravesada al cálculo del intervalo de todo movimiento en `modelo/partida.py` y `controlador/controlador_juego.py`; conservar sin cambios los costos de ataque, espera y demás acciones y mantener el ajuste de tiempo restante de P1 §2.3 cuando cambia la velocidad (FR-002, FR-003; AB-02, AB-03, AB-14).
- [ ] T007 [US1] Tras T005 y T006, ejecutar y corregir las pruebas de carga y movimiento de esta historia con `python -m pytest -q tests/test_terreno_cazador.py tests/test_controlador_red.py tests/test_datos_http.py tests/test_datos_offline.py`; verificar explícitamente los criterios AB-01–AB-03, AB-14 y AB-19, AB-24–AB-28 (FR-001–FR-003, FR-013; AB-01–AB-03, AB-14, AB-19, AB-24–AB-28).

**Punto de control**: Las salidas tienen costo validado; todos los actores usan el intervalo correcto y sus demás acciones y comportamientos permanecen intactos.

## Fase 4: Historia de usuario 2 — Resolver el movimiento de un cazador (Prioridad: P1)

**Objetivo**: Incorporar el cazador y su persecución por costo mínimo usando el mapa y las puertas actuales, con rango, desempate, movimiento de un paso y evaluación reproducible.

**Prueba independiente**: Verificar ataques, espera, ruta mínima, desempates, cambios de puertas/posición, datos de catálogo y movimiento de una sala; comprobar que cálculo individual y compartido dan la misma decisión.

### Pruebas

- [ ] T008 [P] [US2] Añadir a `tests/test_terreno_cazador.py` pruebas de aceptación que citen cada caso para ataque solo en sala compartida, espera sin ruta o sobre rango, ruta de menor costo, desempate por menor ID, recálculo ante cambios, conocimiento pese a niebla, no ataque a distancia, sala ocupada y ataque solo en el siguiente turno programado (FR-004–FR-009; AB-04–AB-10, AB-15, AB-17, AB-18, AB-23).
- [ ] T009 [P] [US2] Crear `tests/test_catalogo_cazador.py` con pruebas de procedencia de costo/rango, rango obligatorio entero ≥1, rechazo previo al inicio por datos inválidos y rechazo por versiones incompatibles; cada prueba cita los AB/FR correspondientes (FR-012, FR-013; AB-16, AB-20, AB-21).

### Implementación del comportamiento

- [ ] T010 [P] [US2] Integrar `comportamiento: "cazador"` y `rango` en `persistencia/catalogo.py`, `controlador/controlador_red.py` y `modelo/entidades/enemigo.py`; exigir rango entero ≥1 para cazadores, conservar los tres comportamientos existentes y rechazar catálogo/cripta inválidos o incompatibles antes de iniciar (FR-004, FR-012, FR-013; AB-16, AB-20, AB-21).
- [ ] T011 [P] [US2] Implementar en `estructuras/heap_prioridad_ruta.py` una cola de prioridad propia para búsqueda ponderada, con orden determinista por costo y sala; no usar `heapq`, `bisect`, bibliotecas de grafos/rutas, ni `dict`/`set` como índice o caché (FR-006–FR-008; AB-07, AB-08, AB-13).
- [ ] T012 [US2] Implementar en `modelo/buscador_rutas.py` búsqueda de costo mínimo que use solo salidas abiertas, respete salidas dirigidas y calcule las distancias al jugador sobre aristas entrantes para el modo compartido; en cada modo, elegir entre vecinas la de menor ID que satisfaga la igualdad de costo mínimo, sin índices/cachés prohibidos (FR-005–FR-009, FR-011; AB-05–AB-10, AB-13, AB-15).
- [ ] T013 [US2] Implementar en `modelo/entidades/enemigo.py` la decisión del cazador en el orden contractual: atacar si comparte sala; esperar con costo 100 si no hay ruta o el costo mínimo supera el rango; de otro modo mover una sola salida con su costo; no atacar durante el movimiento que entra a la sala del jugador (FR-004–FR-008; AB-04–AB-08, AB-17, AB-18, AB-23).
- [ ] T014 [US2] Integrar la decisión del cazador con el reloj en `modelo/partida.py` y `controlador/controlador_juego.py`: tomar posición actual del jugador, puertas actuales y estado de actores en cada turno; permitir compartir sala sin bloqueo; programar el movimiento con el costo de la salida y atacar solo en el siguiente turno programado tras llegar al jugador (FR-002, FR-004–FR-009; AB-02, AB-04–AB-10, AB-17, AB-18, AB-23).
- [ ] T015 [US2] Ejecutar y corregir las pruebas de cazador y catálogo con `python -m pytest -q tests/test_terreno_cazador.py tests/test_catalogo_cazador.py`; comprobar que cada caso AB-04–AB-10, AB-15–AB-18 y AB-20–AB-23 tenga una prueba identificada (FR-004–FR-009, FR-013; AB-04–AB-10, AB-15–AB-18, AB-20–AB-23).

### Dataset y benchmark headless

- [ ] T016 [P] [US2] Materializar como dato externo en `bench/datos/bench-terreno-cazador-grid-16x16-v1.0.0.json` el fixture del contrato: grilla 16×16 con IDs por filas, 256 salas, 480 conexiones bidireccionales, costos simétricos `1 + ((7*u + 11*v) mod 100)`, ocho puertas enumeradas y abiertas inicialmente, semilla 42; jugador en sala 136, vivo, vida_max/vida 1 000 000 000, ataque 10, defensa 5, velocidad 100, inventario_max 10 e inventario vacío; cazadores `cazador-01`–`cazador-20`, en ese orden, en salas 118–125, 134–135 y 137–146, diez con rango 1 y diez con rango 100 para los escenarios pequeños o rangos 1000 y 10000 para los grandes; todos vivos, vida_max/vida 100, ataque 1, defensa 0, velocidad 100, comportamiento `cazador`, regeneracion 0, suelta vacía, sin objetos ni efectos activos o pendientes, y tipo_id/nombre `bench-cazador`/`Cazador de benchmark` (FR-011; AB-13, AB-29).
- [ ] T017 [US2] Calcular el SHA-256 del fixture de T016 y registrar identidad, versión, dimensiones, topología y checksum en `bench/datos/manifest.json`; mantener ambos archivos fuera de los módulos de producción y regenerar el checksum ante cualquier cambio del fixture (FR-011; AB-13, AB-29).
- [ ] T018 [US2] Después de T014 y T017, implementar el caso de `--bench` en `bench/runner.py`, `bench/terreno_cazador.py` y `main.py`: ejecutar ocho escenarios con exactamente 20 cazadores y 30 repeticiones de 1000 ciclos por escenario; usar perfiles concretos de rangos 1/100 o 1000/10000, diez cazadores por rango, puertas alternadas cada 1 o 100 ciclos, modalidad individual o compartida, semilla 42 y estado inicial idéntico al fixture T016/contrato (jugador: vida actual/máxima 1 000 000 000, ataque 10, defensa 5, velocidad 100, inventario_max 10 e inventario vacío; cazadores: vida actual/máxima 100, ataque 1, defensa 0, velocidad 100, regeneracion 0, sin botín, objetos ni efectos, comportamiento `cazador`). Contrastar cada decisión con referencia desde cero fuera del tiempo cronometrado. Añadir `--salida RUTA` y generar el reporte de referencia en `docs/evidencia/2026-11-04-terreno-cazador-benchmark.json` como JSON UTF-8 indentado, con el esquema del contrato: claves de nivel superior `benchmark`, `fecha`, `fixture`, `equipo`, `semilla`, `estado_inicial`, `escenarios`, `cumple_umbral` y `decisiones_correctas`; dimensiones y SHA-256 del fixture; metadatos de equipo/entorno; ocho escenarios con `perfil_rango`, `rangos`, `cambio_puerta_cada_ciclos`, `modalidad` y `repeticiones`; y 30 repeticiones por escenario con `numero`, 1000 `duraciones_ciclo_ns`, `maximo_ciclo_ns` y `discrepancias` (FR-011; AB-13, AB-29).
- [ ] T019 [P] [US2] Añadir o extender `tests/vista/test_sin_pygame_en_replay_bench.py` para comprobar que `--bench` ejecuta la medición sin instanciar vistas ni importar/iniciar Pygame, y que el JSON de `--salida` contiene identidad, versión, dimensiones y SHA-256 del fixture, ocho escenarios, 30 repeticiones por escenario, 1000 duraciones por repetición y discrepancias (FR-011; AB-13, AB-29).
- [ ] T020 [US2] Tras T015–T019, ejecutar `python main.py --bench --salida docs/evidencia/2026-11-04-terreno-cazador-benchmark.json`; verificar ocho escenarios × 30 repeticiones × 1000 ciclos, decisiones idénticas a la referencia y máximo ≤20 ms en cada ciclo; guardar y revisar el JSON de evidencia con todas las duraciones, máximos, discrepancias y metadatos. Incorporar el reporte resultante a `docs/evidencia/` bajo control de versiones; no afirmar el cumplimiento si cualquier ciclo supera el umbral (FR-011; AB-13, AB-29).

**Punto de control**: El cazador satisface sus escenarios de aceptación y el benchmark documenta su dataset, checksum, corrección y latencias sin red ni vistas.

## Fase 5: Historia de usuario 3 — Reconocer el terreno y a los cazadores (Prioridad: P2)

**Objetivo**: Presentar en consola y Pygame los costos efectivos de todas las salidas de la sala y distinguir al cazador de los demás enemigos.

**Prueba independiente**: En ambas vistas, verificar costos declarados y predeterminados, salidas abiertas/cerradas y diferenciación visual del cazador.

### Pruebas

- [ ] T021 [US3] Añadir pruebas de consola y Pygame para costo efectivo en salidas abiertas y cerradas, estado de puerta inequívoco y diferenciación del cazador, citando AB y FR en cada prueba, en `tests/test_vista_consola.py`, `tests/vista/test_salida_y_rejas.py` y `tests/vista/test_render_enemigos.py` (FR-001, FR-010; AB-11, AB-12, AB-22).

### Implementación

- [ ] T022 [P] [US3] Actualizar `vista/vista_consola.py` para mostrar el costo efectivo de cada salida de la sala actual, incluidas las cerradas con su estado claramente indicado, sin trasladar lógica de rutas a la vista (FR-001, FR-010; AB-11, AB-22).
- [ ] T023 [P] [US3] Propagar costo efectivo y comportamiento del enemigo en los contratos/snapshots de `vista_pygame/contratos.py` y `controlador/controlador_pygame.py`, conservando una proyección plana de modelo a vista (FR-001, FR-010; AB-11, AB-12, AB-22).
- [ ] T024 [US3] Renderizar en `vista_pygame/render/render_sala.py` y `vista_pygame/render/render_actores.py` los costos efectivos de todas las salidas, el estado de las cerradas y una presentación distinguible del cazador; usar el fallback visual existente si no hay recurso específico (FR-001, FR-010; AB-11, AB-12, AB-22).
- [ ] T025 [US3] Ejecutar y corregir las pruebas de ambas vistas con `python -m pytest -q tests/test_vista_consola.py tests/vista/test_salida_y_rejas.py tests/vista/test_render_enemigos.py`; verificar por separado AB-11, AB-12 y AB-22 en consola y Pygame (FR-001, FR-010; AB-11, AB-12, AB-22).

**Punto de control**: Las dos vistas muestran la misma información de terreno y diferencian al cazador sin calcular rutas.

## Fase 6: Pulido y verificación transversal

**Propósito**: Registrar las decisiones, comprobar regresiones y confirmar que las restricciones del proyecto se mantienen.

- [ ] T026 Actualizar `docs/DECISIONES.md` con las decisiones de implementación que difieran o concreten el Plan y con la evidencia de `--bench`; no registrar afirmaciones de rendimiento sin resultados reproducibles (FR-001–FR-013; AB-01–AB-29).
- [ ] T027 Ejecutar los comandos de regresión de `specs/001-terreno-cazador/quickstart.md` y revisar `tests/` para confirmar trazabilidad de todos los AB-01–AB-29 a pruebas con sus FR; verificar que `--replay` y `--bench` no instancien vistas, que no se añadieron bibliotecas/índices/cachés prohibidos y que no se afectó el presupuesto de solicitudes (FR-001–FR-013; AB-01–AB-29).

## Dependencias y orden de ejecución

### Dependencias entre fases

- Fase 2 fundacional: T001 no depende de tareas previas y bloquea todas las historias.
- US1: T002 y T003 dependen de T001; T004 depende de T002/T003; T005 y T006 dependen de T004; T007 depende de T005/T006.
- US2: comienza después de US1 para reutilizar el costo validado. T008 y T009 preparan las pruebas; T010, T011 y T016 son componentes independientes; T012 depende de T011; T013 depende de T010 y T012; T014 depende de T013; T017 depende de T016; T018 depende de T014 y T017; T019 depende de T017 y puede prepararse en paralelo con T018 una vez satisfechas las dependencias de T018 (T014 y T017); T015 depende de T010–T014; T020 depende de T015, T018 y T019.
- US3: depende de US1 (costo en el modelo) y US2 (comportamiento cazador). T021 prepara pruebas; T022 y T023 pueden avanzar en paralelo; T024 depende de T023; T025 depende de T022–T024.
- Pulido: T026 y T027 dependen de las historias que validan; ejecutar T027 después de integrar todas las tareas anteriores.

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
- El fixture versionado y su checksum se mantienen fuera de la lógica de producción; el
  reporte JSON reproducible se conserva como evidencia versionada en `docs/evidencia/`.
- Los atributos de todos los actores del fixture están fijados en el contrato; T016 debe copiarlos literalmente al archivo de datos y no convertirlos en valores de producción.
