---
description: "Tareas para implementar la línea de tiempo de CRIPTA"
---

# Tasks: Línea de tiempo de CRIPTA

**Input**: Documentos de diseño en `specs/004-linea-tiempo/`.

**Prerequisitos**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`.

**Pruebas**: Se solicitan pruebas de aceptación G18–G23, del límite `#k` en múltiplos de `K`, de persistencia y de integración. Escríbelas antes de la implementación de cada historia.

**Formato**: Cada tarea indica responsable, dependencias, requisitos y prueba/comando de cierre. No ejecutar estas tareas como parte de la generación de este archivo.

## Precondiciones (gates)

De acuerdo con el principio VII de la constitución, `spec.md`, `plan.md` y `tasks.md` deben tener un commit antes de cualquier cambio de código.

## Phase 1: Setup

**Purpose**: Preparar fixtures deterministas que puedan reutilizar las pruebas de todas las historias.

- [X] T001 Crear el constructor de partidas e historias deterministas en `tests/fixtures/linea_tiempo.py` y comprobar sus invariantes en `tests/test_linea_tiempo_fixtures.py`. [Responsable: Sebastián; Depende de: ninguna; Atiende: FR-001, SC-001; Cierre: `.\.venv\Scripts\python.exe -m pytest -q tests\test_linea_tiempo_fixtures.py`]

## Phase 2: Foundational Components

**Purpose**: Construir los registros y la reconstrucción aislada que requieren todas las historias.

- [X] T002 Crear el archivo nuevo `modelo/historia.py` con los arreglos propios de acciones vigentes y metadatos de puntos de control, numeración desde 1 y validación de `K > 0`. [Responsable: Sebastián; Depende de: T001; Atiende: FR-002, FR-009, FR-014; Cierre: `.\.venv\Scripts\python.exe -m pytest -q tests\test_historia_modelo.py`]
- [X] T003 Crear el archivo nuevo `modelo/punto_control.py` para capturar/restaurar el estado completo, incluido reloj, estado de `random.Random`, agenda ordenada de eventos y conocimiento del mapa; excluir caché LRU e historial del pergamino. [Responsable: Sebastián; Depende de: T002; Atiende: FR-009, FR-012; Cierre: `.\.venv\Scripts\python.exe -m pytest -q tests\test_punto_control.py`]
- [X] T004 Añadir en el archivo nuevo `modelo/historia.py` el registro permanente e invertible de cambios, separado de los deltas consumibles del pergamino. [Responsable: Sebastián; Depende de: T002; Atiende: FR-008, FR-009, FR-010; Cierre: `.\.venv\Scripts\python.exe -m pytest -q tests\test_registro_cambios_linea_tiempo.py`]
- [X] T005 Crear el archivo nuevo `modelo/reconstructor_historia.py` para reconstruir sobre estado temporal aislado desde un punto de control, sin mutar la partida real. [Responsable: Sebastián; Depende de: T003, T004; Atiende: FR-006, FR-010; Cierre: `.\.venv\Scripts\python.exe -m pytest -q tests\test_reconstructor_historia.py`]

## Phase 3: User Story 1 - Consultar un instante pasado (Priority: P1)

**Goal**: Consultar por tiempo o número de acción y obtener el resumen del estado histórico correcto.

**Independent Test**: Con una historia determinista, comparar consultas por tiempo y por acción con sus estados de referencia; verificar rechazo de tiempos futuros y el orden de eventos simultáneos.

### Tests for User Story 1

- [ ] T006 [P] [US1] Añadir la prueba G18 de rechazo de `historia t` futuro y ausencia de mutaciones en `tests/test_linea_tiempo_g18.py::test_g18_rechaza_futuro_sin_mutar`. [Responsable: Sebastián; Depende de: T001, T005; Atiende: FR-005, FR-006; Cierre: `.\.venv\Scripts\python.exe -m pytest -q tests\test_linea_tiempo_g18.py::test_g18_rechaza_futuro_sin_mutar`]
- [ ] T007 [P] [US1] Añadir la prueba G20 de eventos simultáneos antes de la decisión del jugador en `tests/test_linea_tiempo_g20.py::test_g20_incluye_eventos_del_instante_antes_de_decidir`. [Responsable: Sebastián; Depende de: T001, T005; Atiende: FR-001, FR-004; Cierre: `.\.venv\Scripts\python.exe -m pytest -q tests\test_linea_tiempo_g20.py::test_g20_incluye_eventos_del_instante_antes_de_decidir`]
- [ ] T008 [P] [US1] Añadir en `tests/test_historia_acciones.py::test_historia_k_en_multiplos_de_K_es_previa_a_la_accion` una prueba para `historia #k` en `k = K` y `k = 2K`, verificando el estado justo antes de cada acción. [Responsable: Sebastián; Depende de: T001, T005; Atiende: FR-002, FR-003; Cierre: `.\.venv\Scripts\python.exe -m pytest -q tests\test_historia_acciones.py::test_historia_k_en_multiplos_de_K_es_previa_a_la_accion`]

### Components for User Story 1

- [ ] T009 [US1] Integración (turno de integración): implementar la búsqueda binaria propia y la consulta/reconstrucción `historia t` en el archivo nuevo `modelo/historia.py`; conectar en `controlador/controlador_juego.py` el comando recibido con el modelo, y mostrar el resultado desde `vista/vista_consola.py`. El controlador no implementa búsqueda ni reconstrucción y la vista no calcula el estado. [Responsable: Sebastián; Depende de: T006, T007; Atiende: FR-001, FR-003, FR-005; Cierre: `.\.venv\Scripts\python.exe -m pytest -q tests\test_linea_tiempo_g18.py tests\test_linea_tiempo_g20.py`]
- [ ] T010 [US1] Integración (turno de integración): implementar en el archivo nuevo `modelo/historia.py` la selección de `historia #k` mediante `(k - 1) // K` y la reconstrucción previa a la acción; conectar el comando recibido en `controlador/controlador_juego.py` con el modelo, sin lógica de selección ni reconstrucción en el controlador. [Responsable: Sebastián; Depende de: T008, T009; Atiende: FR-002, FR-003, FR-010; Cierre: `.\.venv\Scripts\python.exe -m pytest -q tests\test_historia_acciones.py`]
- [ ] T011 [US1] Crear el archivo nuevo `modelo/resumen_historico.py` para construir como datos el resumen exigido por FR-004 y adaptar `vista/vista_consola.py` para mostrarlo sin derivar estado ni calcular campos. [Responsable: Sebastián; Depende de: T009, T010; Atiende: FR-004; Cierre: `.\.venv\Scripts\python.exe -m pytest -q tests\test_linea_tiempo_resumen.py`]
- [ ] T029 [US1] Añadir en `tests/test_linea_tiempo_limite_K.py::test_reconstruccion_aplica_como_maximo_K_acciones` una prueba que cuente las acciones de jugador aplicadas/deshechas por cada consulta y falle si alguna reconstrucción excede `K`. [Responsable: Sebastián; Depende de: T005, T010; Atiende: FR-010; Cierre: `.\.venv\Scripts\python.exe -m pytest -q tests\test_linea_tiempo_limite_K.py::test_reconstruccion_aplica_como_maximo_K_acciones`]
- [ ] T032 [US1] Integración (turno de integración): añadir en el archivo existente `main.py` la bandera `--checkpoint-cada K`, validar que `K` sea positivo antes de iniciar consulta o replay y pasar el valor al modelo; probar valores positivo y no positivo en `tests/test_linea_tiempo_checkpoint_cli.py`. [Responsable: Sebastián; Depende de: T002, T009; Atiende: FR-009, FR-014; Cierre: `.\.venv\Scripts\python.exe -m pytest -q tests\test_linea_tiempo_checkpoint_cli.py`]

## Phase 4: User Story 2 - Mantener intacta la partida al consultar (Priority: P1)

**Goal**: Mantener la partida y el pergamino intactos; excluir de la historia vigente las acciones revertidas.

**Independent Test**: Capturar los valores observables de partida, reloj, acciones y pergamino antes y después de consultar; revertir acciones y verificar que no reaparezcan.

### Tests for User Story 2

- [ ] T012 [P] [US2] Añadir la prueba G19 de exclusión de acciones y efectos revertidos en `tests/test_linea_tiempo_g19.py::test_g19_reversion_corta_historia_vigente`. [Responsable: Sebastián; Depende de: T001, T005, T011; Atiende: FR-002, FR-008; Cierre: `.\.venv\Scripts\python.exe -m pytest -q tests\test_linea_tiempo_g19.py::test_g19_reversion_corta_historia_vigente`]
- [ ] T013 [P] [US2] Añadir la prueba G21 de igualdad de estado, reloj, conteo de acciones y pergamino antes/después de consultar en `tests/test_linea_tiempo_g21.py::test_g21_consulta_no_altera_partida_ni_pergamino`. [Responsable: Sebastián; Depende de: T001, T005, T011; Atiende: FR-006, FR-007; Cierre: `.\.venv\Scripts\python.exe -m pytest -q tests\test_linea_tiempo_g21.py::test_g21_consulta_no_altera_partida_ni_pergamino`]

### Integration with the Scroll and Existing Cache

- [ ] T014 [US2] Integración (turno de integración): conectar en `controlador/controlador_juego.py` la reversión del pergamino con `modelo/historia.py` para truncar acciones, cambios y puntos posteriores al límite revertido, conservando el límite de cinco acciones del pergamino. [Responsable: Sebastián; Depende de: T012; Atiende: FR-007, FR-008; Cierre: `.\.venv\Scripts\python.exe -m pytest -q tests\test_linea_tiempo_g19.py tests\test_historial_bloque3.py`]
- [ ] T015 [US2] Asegurar en `modelo/reconstructor_historia.py` y `tests/test_linea_tiempo_g21.py` que la consulta use solo su estado temporal y no cambie la partida ni el pergamino; preservar la caché LRU como detalle interno de la reconstrucción aislada vinculado a FR-006, no como criterio de aceptación nuevo. [Responsable: Sebastián; Depende de: T013, T014; Atiende: FR-006, FR-007; Cierre: `.\.venv\Scripts\python.exe -m pytest -q tests\test_linea_tiempo_g21.py`]

## Phase 5: User Story 3 - Reproducir y conservar la historia (Priority: P2)

**Goal**: Conservar la historia y el mapa conocido al guardar/cargar, compartir la reconstrucción con replay y rechazar archivos de Parte I.

**Independent Test**: Comparar `historia t` con `--replay ... --hasta t`, guardar/cargar y consultar un punto anterior, y probar el rechazo explícito de un archivo Parte I.

### Tests for User Story 3

- [ ] T016 [P] [US3] Añadir la prueba G22 de paridad de resumen y finalización anticipada en `tests/test_linea_tiempo_g22.py::test_g22_replay_reutiliza_historia_y_avisa_fin_anticipado`. [Responsable: Sebastián; Depende de: T001, T011; Atiende: FR-004, FR-011; Cierre: `.\.venv\Scripts\python.exe -m pytest -q tests\test_linea_tiempo_g22.py::test_g22_replay_reutiliza_historia_y_avisa_fin_anticipado`]
- [ ] T017 [P] [US3] Añadir la prueba G23 de rechazo de archivo Parte I, sin migración ni carga silenciosa, en `tests/test_linea_tiempo_g23.py::test_g23_rechaza_archivo_parte_i`. [Responsable: Sebastián; Depende de: T001; Atiende: FR-013; Cierre: `.\.venv\Scripts\python.exe -m pytest -q tests\test_linea_tiempo_g23.py::test_g23_rechaza_archivo_parte_i`]
- [ ] T018 [P] [US3] Añadir la prueba SC-005 de guardado/carga y consulta de la historia y mapa conocido desde el inicio en `tests/test_linea_tiempo_guardado.py::test_guardado_carga_conserva_historia_y_mapa`. [Responsable: Sebastián; Depende de: T001, T011; Atiende: FR-012, SC-005; Cierre: `.\.venv\Scripts\python.exe -m pytest -q tests\test_linea_tiempo_guardado.py::test_guardado_carga_conserva_historia_y_mapa`]

### Components for User Story 3

- [ ] T019 [US3] Persistir en los archivos existentes `persistencia/PartidaBinaria.py` y `persistencia/estado_partida.py` la historia vigente y bloques versionados de puntos de control con índice ordenado por tiempo/acción y acceso por desplazamiento. [Responsable: Sebastián; Depende de: T017, T018; Atiende: FR-009, FR-012, FR-013; Cierre: `.\.venv\Scripts\python.exe -m pytest -q tests\test_linea_tiempo_g23.py tests\test_linea_tiempo_guardado.py`]
- [ ] T020 [US3] Integración (turno de integración): integrar en el archivo existente `controlador/guardado.py` el guardado/cargado de registros, puntos de control y mapa conocido; restaurar un punto sin decodificar todas las salas por consulta. [Responsable: Sebastián; Depende de: T019; Atiende: FR-009, FR-012; Cierre: `.\.venv\Scripts\python.exe -m pytest -q tests\test_linea_tiempo_guardado.py tests\test_persistencia.py`]
- [ ] T021 [US3] Integración (turno de integración): modificar los archivos existentes `controlador/controlador_replay.py` y `main.py` para que `--replay partida.log --hasta t` reutilice la reconstrucción del modelo y el mismo constructor de resumen de `modelo/resumen_historico.py` que `historia t`, sin instanciar la vista ni realizar solicitudes de red. [Responsable: Sebastián; Depende de: T016, T020; Atiende: FR-010, FR-011; Cierre: `.\.venv\Scripts\python.exe -m pytest -q tests\test_linea_tiempo_g22.py tests\test_controlador_replay.py tests\test_separacion_mvc.py`]

## Phase 6: Integration with Other Capabilities

**Purpose**: Verificar que la instantánea y reconstrucción concuerden con Niebla y Terreno.

- [ ] T022 [P] Crear en `tests/test_linea_tiempo_integraciones.py` pruebas de que el conocimiento de Niebla se conserva en cada punto y que los movimientos/costos de Terreno se reproducen igual que en la partida original. [Responsable: Sebastián; Depende de: T001, T011; Atiende: FR-004, FR-012; Cierre: `.\.venv\Scripts\python.exe -m pytest -q tests\test_linea_tiempo_integraciones.py`]
- [ ] T023 Integrar en `modelo/punto_control.py` y `modelo/reconstructor_historia.py` la captura/restauración del conocimiento de Niebla y la paridad de movimiento/costos de Terreno comprobada por T022. [Responsable: Sebastián; Depende de: T022; Atiende: FR-004, FR-010, FR-012; Cierre: `.\.venv\Scripts\python.exe -m pytest -q tests\test_linea_tiempo_integraciones.py tests\test_orden_determinista.py`]

## Phase 7: Measurements

**Purpose**: Medir las variantes con una historia y conjunto de consultas comunes; fijar `K` solo a partir de resultados.

- [ ] T024 Integración (turno de integración): añadir a `bench/bench_linea_tiempo.py` y registrar mediante el archivo existente `main.py` el caso `--bench` de al menos 5.000 acciones y 30 puntos medidos 30 veces cada uno; para cada `K` evaluado, informar mediana, p95, máximo y bytes persistidos de registros y puntos de control. Registrar la memoria de ejecución solo como métrica informativa. Añadir en `tests/test_separacion_mvc.py` una prueba que verifique que `--bench` no instancia la vista (Principio III). [Responsable: Sebastián; Depende de: T019, T020, T023; Atiende: SC-001, SC-002, Principio III; Cierre: `.\.venv\Scripts\python.exe -m pytest -q tests\test_separacion_mvc.py; .\.venv\Scripts\python.exe main.py --bench`]
- [ ] T025 Extender `bench/bench_linea_tiempo.py` para comparar búsqueda binaria propia con lineal, re-simulación hacia adelante con inversión, y lectura/decodificación/restauración de un punto de control. [Responsable: Sebastián; Depende de: T024; Atiende: FR-010, SC-002; Cierre: `.\.venv\Scripts\python.exe main.py --bench`]
- [ ] T030 Crear el archivo nuevo `tests/test_linea_tiempo_rendimiento.py` con las aserciones de medición SC-001/SC-002 y la selección del mayor `K` probado que cumple el umbral; dejarlo listo antes de configurar el valor predeterminado. [Responsable: Sebastián; Depende de: T024, T025; Atiende: SC-001, SC-002; Cierre: `.\.venv\Scripts\python.exe -m pytest -q tests\test_linea_tiempo_rendimiento.py`]
- [ ] T026 Elegir y configurar el valor predeterminado de `K` en el archivo nuevo `modelo/historia.py` como el mayor valor probado que cumpla SC-001; rechazar valores no positivos. [Responsable: Sebastián; Depende de: T025, T030; Atiende: FR-009, FR-014, SC-001, SC-002; Cierre: `.\.venv\Scripts\python.exe -m pytest -q tests\test_historia_modelo.py tests\test_linea_tiempo_rendimiento.py`]
- [ ] T033 Implementar en `modelo/reconstructor_historia.py` la estrategia de reconstrucción elegida a partir de las mediciones de T025, conectarla a las consultas y comprobar que no exceda `K` acciones ni altere la partida real. [Responsable: Sebastián; Depende de: T025, T026, T030; Atiende: FR-006, FR-010, SC-002; Cierre: `.\.venv\Scripts\python.exe -m pytest -q tests\test_reconstructor_historia.py tests\test_linea_tiempo_limite_K.py tests\test_linea_tiempo_g22.py`]

## Phase 8: Documentation and Final Validation

**Purpose**: Registrar diseño y resultados medidos en los artefactos de esta capacidad y comprobar los escenarios de extremo a extremo.

- [ ] T027 Actualizar `specs/004-linea-tiempo/research.md`, `data-model.md`, `contracts/cli.md`, `contracts/checkpoint-persistence.md` y `quickstart.md` con la estrategia elegida y resultados reales de medición, sin añadir comportamiento distinto de `spec.md`. [Responsable: Sebastián; Depende de: T021, T023, T026, T032, T033; Atiende: FR-001–FR-014, SC-001–SC-005; Cierre: revisar cada documento contra `specs/004-linea-tiempo/spec.md` y ejecutar `git diff --check -- specs/004-linea-tiempo`]
- [ ] T028 Ejecutar las regresiones de persistencia, replay, pergamino, no alteración, Niebla/Terreno y el recorrido de `quickstart.md`; registrar cualquier falla sin cambiar requisitos fuera del alcance. [Responsable: Sebastián; Depende de: T027, T032, T033; Atiende: FR-001–FR-014, SC-001–SC-005; Cierre: `.\.venv\Scripts\python.exe -m pytest -q tests\test_linea_tiempo_g18.py tests\test_linea_tiempo_g19.py tests\test_linea_tiempo_g20.py tests\test_linea_tiempo_g21.py tests\test_linea_tiempo_g22.py tests\test_linea_tiempo_g23.py tests\test_historia_acciones.py tests\test_linea_tiempo_guardado.py tests\test_linea_tiempo_integraciones.py tests\test_linea_tiempo_checkpoint_cli.py`]
- [ ] T034 Documentar en `docs/DECISIONES.md` las decisiones de la línea de tiempo, alternativas evaluadas y mediciones reproducibles de T024/T025, incluyendo el `K` y la estrategia seleccionados. [Responsable: Sebastián; Depende de: T027, T028, T032, T033; Atiende: Principio de Flujo de cambios, SC-001, SC-002; Cierre: revisar la entrada de decisión y ejecutar `git diff --check -- docs/DECISIONES.md`]

## Dependencies & Execution Order

### Phase dependencies

- **Precondiciones**: Los commits de `spec.md`, `plan.md` y `tasks.md` deben preceder cualquier cambio de código, conforme al principio VII.
- **Setup (Phase 1)**: T001 no tiene dependencias.
- **Foundational (Phase 2)**: T002 depende de T001; T003/T004 dependen de T002; T005 depende de T003 y T004. Deben completarse antes de las historias.
- **User Story 1 (Phase 3)**: Las pruebas T006–T008 pueden avanzar en paralelo tras T001/T005; T009–T011 dependen de esas pruebas y componentes. T029 cierra la historia verificando el límite de `K`; T032 integra la bandera de configuración.
- **User Story 2 (Phase 4)**: Depende de la base y de US1 para consultar; T012/T013 pueden avanzar en paralelo y preceden a T014/T015.
- **User Story 3 (Phase 5)**: Depende de la reconstrucción/consulta de US1; T016–T018 pueden avanzar en paralelo, luego T019–T021 integran persistencia y replay.
- **Integración (Phase 6)**: T022 verifica las dependencias externas tras US1; T023 implementa la integración según dichas pruebas.
- **Mediciones (Phase 7)**: T024 requiere persistencia e integración; T025 compara variantes; T030 crea la prueba de medición, T026 fija el valor predeterminado y T033 implementa la estrategia medida.
- **Documentación (Phase 8)**: T027 actualiza los artefactos de diseño; T028 cierra con pruebas de regresión; T034 documenta decisiones y mediciones en `docs/DECISIONES.md`.

### User story dependencies

- **US1 (P1)**: No depende de otra historia; requiere Setup y Foundational.
- **US2 (P1)**: Depende de US1, porque consulta el historial y extiende su truncamiento al pergamino.
- **US3 (P2)**: Depende de US1 para compartir la reconstrucción; no depende de US2.

### Parallel opportunities

- T006, T007 y T008 usan archivos de prueba distintos y pueden escribirse en paralelo después de T001/T005.
- T012 y T013 prueban G19 y G21 en archivos distintos.
- T016, T017 y T018 cubren replay, compatibilidad y persistencia en archivos distintos.
- T022 puede prepararse en paralelo con pruebas de US3 después de US1; no debe integrarse en código hasta pasar por su prueba.
- No paralelizar tareas que editan el mismo módulo (`controlador/controlador_juego.py`, `modelo/historia.py` o `bench/bench_linea_tiempo.py`).

## Parallel Example: User Story 1

```text
Después de T001 y T005:
T006: prueba G18 en tests/test_linea_tiempo_g18.py
T007: prueba G20 en tests/test_linea_tiempo_g20.py
T008: prueba de múltiplos de K en tests/test_historia_acciones.py
```

## Implementation Strategy

### MVP

El MVP es US1: T001–T011, T029 y T032, incluyendo consulta por tiempo y acción, resumen mínimo, G18/G20, límites `#k` en múltiplos de `K`, la cota de reconstrucción de FR-010 y la bandera `--checkpoint-cada K`.

### Incremental delivery

1. Completar Setup y Foundational.
2. Entregar US1 y validar consultas históricas.
3. Integrar US2 para no alteración y reversión con pergamino.
4. Integrar US3 para guardado/carga y replay sin vista.
5. Validar Niebla/Terreno, ejecutar mediciones comparativas y fijar `K`.
6. Implementar la estrategia medida de reconstrucción, actualizar documentación y registrar las decisiones en `docs/DECISIONES.md`.
7. Ejecutar la validación final.
