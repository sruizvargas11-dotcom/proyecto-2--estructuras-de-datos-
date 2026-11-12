# Tasks: Niebla de guerra, antorcha e ir a

**Input**: `specs/002-niebla-viaje/spec.md`, `plan.md`
**Tests**: obligatorios (constitución: cada escenario NV con prueba que cita sus FR).

> Generado a mano con la estructura de `.specify/templates/tasks-template.md` (los scripts de
> Spec Kit están bloqueados por la política de PowerShell).

## Phase 1: Setup

- [ ] T001 Registrar `modelo.conocimiento` en `MODULOS` de `persistencia/estado_partida.py` (FR-007)
- [ ] T002 [P] Añadir `DeltaLongitud` en `modelo/deltas.py` (FR-007, FR-016)

## Phase 2: Foundational

- [ ] T003 Crear `ConocimientoJugador`, `RegistroSala`, `RecuerdoPuerta` en `modelo/conocimiento.py` con explorar, observar, visitar, consultas y registro de cambios (FR-001..FR-007, FR-016)
- [ ] T004 Integrar en `modelo/partida.py`: propiedad `conocimiento`, visita inicial, visita al entrar, `observar_entorno`, detección de antorcha encendida (FR-001, FR-004, FR-005)

## Phase 3: User Story 1 – Niebla de guerra (P1)

- [ ] T005 [US1] Pruebas NV-01..NV-06, NV-28 en `tests/test_niebla_viaje.py` (FR-001..FR-004, FR-006)
- [ ] T006 [US1] Observación de puertas al inicio de cada turno del jugador en `controlador/controlador_juego.py` antes de confirmar el intervalo (FR-004)

## Phase 4: User Story 2 – `ir a` (P1)

- [ ] T007 [US2] Ruta conocida (`siguiente_paso`) en `modelo/conocimiento.py` (FR-009, FR-010)
- [ ] T008 [US2] Comando `IR`, inicio de viaje, pasos automáticos, causas de parada y prioridad en `controlador/controlador_juego.py` (FR-008, FR-010..FR-013)
- [ ] T009 [US2] Comentarios `#` en `bitacora_partida.py` y registro de `ir a` como comentario (FR-014)
- [ ] T010 [US2] Pruebas NV-07..NV-16, NV-27, NV-30..NV-33 en `tests/test_niebla_viaje.py`

## Phase 5: User Story 3 – Antorcha (P2)

- [ ] T011 [US3] Pruebas NV-17..NV-20, NV-34 en `tests/test_niebla_viaje.py` (FR-005)

## Phase 6: User Story 4 – Guardado, retroceso, historia (P2)

- [ ] T012 [US4] Pergamino anula el viaje en `controlador/controlador_juego.py` (FR-015)
- [ ] T013 [US4] `reconstruir_en(t)` aislado en `modelo/conocimiento.py` (FR-007)
- [ ] T014 [US4] Pruebas NV-21..NV-24 (guardar/cargar, retroceso con antorcha, retroceso en viaje, historia) y replay determinista en `tests/test_niebla_viaje.py`

## Phase 7: User Story 5 – Interfaz mínima (P3)

- [ ] T015 [US5] Comando `M`/`MAPA` y ayuda en `controlador/controlador_juego.py` y `vista/vista_consola.py` (FR-018)
- [ ] T016 [US5] Pruebas NV-25, NV-26 en `tests/test_niebla_viaje.py`

## Phase 8: Rendimiento y evidencia

- [ ] T017 Benchmark `bench/niebla_viaje.py` y opción `--bench-caso` en `main.py` (FR-016, FR-017)
- [ ] T018 [P] Prueba de contrato del reporte en `tests/test_bench_niebla_viaje.py` (NV-29; FR-017)
- [ ] T019 Ejecutar pruebas focalizadas, benchmark y suite completa; guardar resultados en `docs/evidencia/` (SC-001..SC-007)
- [ ] T020 Matriz de trazabilidad NV→FR→prueba en `docs/evidencia/2026-11-11-niebla-viaje-trazabilidad.md` (SC-001, SC-007)
- [ ] T021 Registrar decisiones en `docs/DECISIONES.md` (constitución: flujo de cambios)

## Dependencies

T001–T004 → US1 → US2 → (US3, US4 en paralelo) → US5 → Fase 8.
