---
description: "Tareas de implementación para la verificación de resolubilidad"
---

# Tasks: Verificación de resolubilidad de la cripta

**Entrada**: Diseño de `specs/003-resolubilidad/` (`spec.md`, `plan.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`).

**Alcance**: Descomponer el diseño en cambios pequeños y verificables. Esta lista no implementa código.

**Pruebas**: Son obligatorias para esta capacidad: se solicitan pruebas por escenario, comparación con el oráculo, determinismo byte a byte, integración y benchmark.

**Formato**: Cada tarea usa `- [ ] TNNN [P?] [USn?]`, identifica sus archivos, requisitos/escenarios, criterio de terminado y dependencias explícitas.

## Fase 1: Base de datos de entrada

**Propósito**: Obtener las ubicaciones de llaves de forma uniforme, respetar el presupuesto, validar versiones y distinguir NO VERIFICABLE de errores de datos.

- [ ] T001 [P] Añadir pruebas de contrato de la fuente de llaves en `tests/test_fuente_llaves.py`.
  - **Atiende**: FR-001, FR-016, FR-018, FR-019; RS-E10, RS-E11, RS-E24.
  - **Criterio**: `python -m pytest --collect-only tests/test_fuente_llaves.py -q` termina con código 0 y recoge los casos de respuesta válida/vacía, reintentos y presupuesto, versión obsoleta, sala inexistente, enemigo no validado y fallos de consulta; las pruebas afirman errores de datos y NO VERIFICABLE como resultados distintos.
  - **Dependencias**: Ninguna.

- [ ] T002 Implementar la operación común y consulta HTTP de llaves en `adaptadores/fuente_datos.py` y `adaptadores/datos_http.py`.
  - **Atiende**: FR-001, FR-018, FR-019; RS-E10.
  - **Criterio**: `python -m pytest tests/test_fuente_llaves.py tests/test_datos_http.py -q` pasa; GET usa `_get()` y cada intento/reintento cuenta en `presupuesto_solicitudes`; transporte/timeout/indisponibilidad se distingue de una respuesta de datos inválidos.
  - **Dependencias**: T001.

- [ ] T003 [P] Implementar lectura offline y delegación simulada en `adaptadores/datos_offline.py` y `adaptadores/datos_simulado.py`.
  - **Atiende**: FR-001, FR-018; RS-E10, RS-E11.
  - **Criterio**: `python -m pytest tests/test_fuente_llaves.py tests/test_datos_offline.py -q` pasa; se lee `datos_offline/<cripta_id>/llaves.json`, una ausencia de archivo produce NO VERIFICABLE (nunca lista vacía) y el adaptador simulado conserva su demora determinista.
  - **Dependencias**: T001, T002.

- [ ] T004 Persistir llaves por cripta y versión y extender la descarga offline en `persistencia/llaves_cripta.py` y `herramientas/descargar_offline.py`.
  - **Atiende**: FR-001, FR-018, FR-019; RS-E10, RS-E11.
  - **Criterio**: `python -m pytest tests/test_fuente_llaves.py -q` pasa; una caché con versión e identificador coincidentes se reutiliza, una obsoleta/inválida se descarta y se consulta la fuente, y el guardado reutiliza `persistencia/cache_json.py` con escritura atómica.
  - **Dependencias**: T002, T003.

- [ ] T005 Sincronizar el modelo lógico en `specs/003-resolubilidad/data-model.md` con las reglas vigentes de `spec.md`.
  - **Atiende**: FR-016, FR-019, FR-020, FR-022; RS-E16, RS-E18, RS-E24, RS-E35.
  - **Criterio**: `git diff --check -- specs/003-resolubilidad/data-model.md` termina sin errores y el documento ya no contradice que el enemigo no se valida, que `llave_salida` nula/ausente es error no forzable, ni las reglas de ubicaciones múltiples e indispensabilidad.
  - **Dependencias**: Ninguna.

## Fase 2: Fundacional

**Propósito**: Preparar datos deterministas y un oráculo independiente antes del recorrido incremental.

- [ ] T006 Crear el generador sintético por semilla y el oráculo de recorrido repetido en `bench/casos/resolubilidad.py` y sus pruebas en `tests/test_resolubilidad_oraculo.py`.
  - **Atiende**: FR-017; SC-002, SC-003; RS-E12.
  - **Criterio**: `python -m pytest tests/test_resolubilidad_oraculo.py -q` pasa; la misma semilla reproduce exactamente la misma cripta y el generador cubre cadenas de llaves, ciclos y rutas alternativas; el oráculo devuelve un resultado de datos comparable y no es usado como algoritmo de producción.
  - **Dependencias**: T005.

## Fase 3: User Story 1 - Conocer si la cripta puede ganarse (P1, MVP)

**Meta**: Obtener un reporte determinista correcto, diagnosticar los bloqueos y mostrar un resumen seguro al iniciar una partida nueva.

**Prueba independiente**: Correr pruebas G14–G17 y RS-E01–RS-E22/RS-E28–RS-E29/RS-E35–RS-E36; comparar el resultado incremental con el oráculo en criptas sintéticas.

### Pruebas de aceptación de US1

- [ ] T007 [P] [US1] Crear `tests/test_resolubilidad_g14.py` para llave de salida encerrada por la única puerta que ella misma abre.
  - **Atiende**: FR-007, FR-011, FR-012, FR-013; G14.
  - **Criterio**: `python -m pytest --collect-only tests/test_resolubilidad_g14.py -q` recoge aserciones para NO RESOLUBLE (a), puerta de frontera y ciclo llave→llave.
  - **Dependencias**: T006.

- [ ] T008 [P] [US1] Crear `tests/test_resolubilidad_g15.py` para llaves asociadas a enemigos.
  - **Atiende**: FR-004, FR-016; G15.
  - **Criterio**: `python -m pytest --collect-only tests/test_resolubilidad_g15.py -q` recoge el caso de enemigo errante y no errante y comprueba la sala de inicio del enemigo.
  - **Dependencias**: T006.

- [ ] T009 [P] [US1] Crear `tests/test_resolubilidad_g16.py` para orden determinista.
  - **Atiende**: FR-010, FR-017; SC-003; G16.
  - **Criterio**: `python -m pytest --collect-only tests/test_resolubilidad_g16.py -q` recoge dos ejecuciones idénticas y una comparación byte a byte del orden por rondas.
  - **Dependencias**: T006.

- [ ] T010 [P] [US1] Crear `tests/test_resolubilidad_g17.py` para bloquear el inicio no forzado.
  - **Atiende**: FR-015; G17.
  - **Criterio**: `python -m pytest --collect-only tests/test_resolubilidad_g17.py -q` recoge un caso no resoluble que conserva el reporte y no crea partida sin `--forzar`.
  - **Dependencias**: T006.

- [ ] T011 [P] [US1] Crear `tests/test_resolubilidad_e01_e09.py` para forzado, dependencias, rondas y supuestos de alcanzabilidad.
  - **Atiende**: FR-002, FR-003, FR-005–FR-010, FR-012, FR-015, FR-018; RS-E01–RS-E09.
  - **Criterio**: `python -m pytest --collect-only tests/test_resolubilidad_e01_e09.py -q` recoge los nueve escenarios, incluida ruta alternativa sin ciclo, cadena de llaves, puerta final abierta, costo ignorado, direccionalidad y llaves no consumidas.
  - **Dependencias**: T006.

- [ ] T012 [P] [US1] Crear `tests/test_resolubilidad_e10_e18.py` para consulta, versiones, trampas, ubicaciones múltiples y selección de puerta final.
  - **Atiende**: FR-001, FR-005, FR-008, FR-009, FR-016, FR-018–FR-020; RS-E10–RS-E18.
  - **Criterio**: `python -m pytest --collect-only tests/test_resolubilidad_e10_e18.py -q` recoge los nueve escenarios; las pruebas incluyen versión obsoleta, llave inicial en ronda 0 y desempate de puerta/ubicación.
  - **Dependencias**: T006.

- [ ] T013 [P] [US1] Crear `tests/test_resolubilidad_e19_e22.py` para comparadores, corte por ronda, indispensabilidad y crecimiento.
  - **Atiende**: FR-009, FR-016, FR-021, FR-022; SC-004; RS-E19–RS-E22.
  - **Criterio**: `python -m pytest --collect-only tests/test_resolubilidad_e19_e22.py -q` recoge los cuatro escenarios y afirma comparación numérica de salas, comparación lexicográfica de ids, ronda final completa y todas las ubicaciones de una llave.
  - **Dependencias**: T006.

- [ ] T014 [P] [US1] Crear `tests/test_resolubilidad_e28_e29.py` para ciclos mínimos y prioridad de causas.
  - **Atiende**: FR-011, FR-012, FR-021; RS-E28, RS-E29.
  - **Criterio**: `python -m pytest --collect-only tests/test_resolubilidad_e28_e29.py -q` recoge ciclos simples más cortos, empates lexicográficos, inicio canónico, orden de puertas y causas «en ciclo»/«depende de».
  - **Dependencias**: T006.

- [ ] T015 [P] [US1] Crear `tests/test_resolubilidad_e35_e36.py` para llave de salida inválida y orden de frontera.
  - **Atiende**: FR-013, FR-019, FR-021; RS-E35, RS-E36.
  - **Criterio**: `python -m pytest --collect-only tests/test_resolubilidad_e35_e36.py -q` recoge `llave_salida` nula/ausente como error no forzable y orden de frontera por sala numérica/dirección lexicográfica.
  - **Dependencias**: T006.

### Implementación de US1

- [ ] T016 [US1] Implementar el recorrido incremental dirigido y las rondas en `modelo/verificador_resolubilidad.py`.
  - **Atiende**: FR-002–FR-010, FR-016, FR-017, FR-020, FR-021; G15, G16; RS-E04, RS-E07–RS-E09, RS-E13–RS-E14, RS-E16–RS-E20.
  - **Criterio**: `python -m pytest tests/test_resolubilidad_g15.py tests/test_resolubilidad_g16.py tests/test_resolubilidad_e01_e09.py tests/test_resolubilidad_e10_e18.py tests/test_resolubilidad_e19_e22.py -q` pasa; la ronda se completa y ordena antes de liberar puertas, el algoritmo no usa costos ni modifica `CriptaModelo`, y las pruebas sintéticas igualan al oráculo en veredicto, orden y frontera.
  - **Dependencias**: T006–T015.

- [ ] T017 [US1] Implementar diagnóstico de llaves inobtenibles, causas, frontera y dependencias en `modelo/verificador_resolubilidad.py`.
  - **Atiende**: FR-011, FR-013, FR-016, FR-022; G14; RS-E03, RS-E05–RS-E06, RS-E18, RS-E21, RS-E29, RS-E36.
  - **Criterio**: `python -m pytest tests/test_resolubilidad_g14.py tests/test_resolubilidad_e01_e09.py tests/test_resolubilidad_e10_e18.py tests/test_resolubilidad_e19_e22.py tests/test_resolubilidad_e28_e29.py tests/test_resolubilidad_e35_e36.py -q` pasa; la frontera se recoge en el recorrido base, se listan todas las dependencias indispensables y una llave múltiple solo es inobtenible si todas sus ubicaciones quedan fuera.
  - **Dependencias**: T016.

- [ ] T018 [US1] Implementar selección y orden determinista de ciclos simples en `modelo/verificador_resolubilidad.py`.
  - **Atiende**: FR-011, FR-012, FR-021; G14; RS-E02, RS-E28–RS-E29.
  - **Criterio**: `python -m pytest tests/test_resolubilidad_g14.py tests/test_resolubilidad_e01_e09.py tests/test_resolubilidad_e28_e29.py -q` pasa; cada llave participante recibe un ciclo simple más corto, los empates siguen la secuencia de ids requerida y las puertas se ordenan por sala/dirección.
  - **Dependencias**: T017.

- [ ] T019 [US1] Crear el formateador de reporte completo y resumen seguro en `vista/formato_resolubilidad.py` y sus pruebas en `tests/test_formato_resolubilidad.py`.
  - **Atiende**: FR-011, FR-013–FR-015, FR-024; SC-003; RS-E25, RS-E34.
  - **Criterio**: `python -m pytest tests/test_formato_resolubilidad.py -q` pasa y compara UTF-8 byte a byte con las plantillas de `specs/003-resolubilidad/contracts/cli.md`; el resumen inicial no imprime ubicaciones, frontera ni ciclos.
  - **Dependencias**: T016–T018.

- [ ] T020 [US1] Integrar la verificación y el bloqueo de partidas nuevas en `controlador/inicio_partida.py`.
  - **Atiende**: FR-015, FR-018, FR-019; G17; RS-E01, RS-E10, RS-E15, RS-E25.
  - **Criterio**: `python -m pytest tests/test_resolubilidad_g17.py tests/test_resolubilidad_e01_e09.py tests/test_resolubilidad_e10_e18.py tests/test_resolubilidad_e35_e36.py -q` pasa; `nueva_partida()` verifica una vez, conserva el resultado para presentación y bloquea NO RESOLUBLE/NO VERIFICABLE sin forzado y todo error de datos.
  - **Dependencias**: T004, T016–T019.

- [ ] T021 [US1] Mostrar el resumen seguro en el flujo GUI en `controlador/controlador_pygame.py` y `vista_pygame/escenas/menu_criptas.py`.
  - **Atiende**: FR-015, FR-024; RS-E25.
  - **Criterio**: `python -m pytest tests/vista/test_inicio_resolubilidad.py -q` pasa; el inicio GUI muestra solo veredicto/motivo y no revela ubicaciones de llaves.
  - **Dependencias**: T019, T020.

**Punto de control US1**: pasan G14–G17, los escenarios de modelo asignados y la comparación incremental/oráculo; inicio normal bloquea conforme al resultado.

## Fase 4: User Story 2 - Verificar sin iniciar una partida (P2)

**Meta**: Proveer `--verificar` headless con reporte contractual, códigos 0/1/2 y rechazo temprano de combinaciones incompatibles.

**Prueba independiente**: Ejecutar pruebas CLI para resultados resoluble, no resoluble, datos inválidos y combinaciones prohibidas, comprobando códigos y que no se crea vista.

- [ ] T022 [P] [US2] Añadir pruebas de contrato CLI en `tests/test_cli_resolubilidad.py`.
  - **Atiende**: FR-014, FR-024; RS-E23–RS-E25, RS-E30–RS-E31, RS-E34.
  - **Criterio**: `python -m pytest --collect-only tests/test_cli_resolubilidad.py -q` recoge reporte/código para resoluble, no resoluble y error; ausencia de vista; rechazo antes de consultar con `--replay`/`--bench`; y que `--forzar` no altere `--verificar`.
  - **Dependencias**: T019–T021.

- [ ] T023 [US2] Implementar `--verificar <cripta>` y sus códigos/formato en `main.py`.
  - **Atiende**: FR-014, FR-024; SC-005; RS-E23–RS-E25, RS-E30–RS-E31, RS-E34.
  - **Criterio**: `python -m pytest tests/test_cli_resolubilidad.py -q` pasa; invocaciones resoluble/no resoluble/devuelven 0/1, error de datos o consulta devuelve 2, no se instancia vista, los conflictos se rechazan antes de consultar y la salida coincide con `contracts/cli.md`.
  - **Dependencias**: T004, T016–T022.

- [ ] T024 [P] [US2] Excluir la verificación del replay en `controlador/controlador_replay.py` y ampliar `tests/test_controlador_replay.py`.
  - **Atiende**: FR-023; RS-E26.
  - **Criterio**: `python -m pytest tests/test_controlador_replay.py tests/vista/test_sin_pygame_en_replay_bench.py -q` pasa; reproducir no consulta llaves ni instancia vista.
  - **Dependencias**: T020.

**Punto de control US2**: `--verificar` funciona sin vista, respeta el contrato y el replay conserva su comportamiento sin verificación.

## Fase 5: User Story 3 - Forzar el inicio (P3)

**Meta**: Permitir continuar explícitamente con NO RESOLUBLE o NO VERIFICABLE, sin permitir forzar errores de datos y aplicando la opción también a GUI.

**Prueba independiente**: Contrastar inicio normal/GUI con y sin `--forzar` para NO RESOLUBLE, NO VERIFICABLE y error de datos.

- [ ] T025 [US3] Implementar `--forzar` y su propagación en `main.py`, `controlador/inicio_partida.py`, `controlador/controlador_pygame.py` y `vista_pygame/escenas/menu_criptas.py`; añadir `tests/test_inicio_forzar_resolubilidad.py`.
  - **Atiende**: FR-015, FR-018, FR-019; SC-005; G17; RS-E01, RS-E10, RS-E15, RS-E32, RS-E35.
  - **Criterio**: `python -m pytest tests/test_inicio_forzar_resolubilidad.py tests/test_resolubilidad_g17.py tests/test_resolubilidad_e01_e09.py tests/test_resolubilidad_e10_e18.py tests/test_resolubilidad_e35_e36.py -q` pasa; forzar permite NO RESOLUBLE/NO VERIFICABLE con resumen, también en GUI, pero nunca permite iniciar con error de datos. En modo verificar, `--forzar` sigue ignorado.
  - **Dependencias**: T020–T023.

**Punto de control US3**: forzar solo omite el bloqueo de estados permitidos y nunca cambia un error de datos en éxito.

## Fase 6: Rendimiento y benchmark

**Propósito**: Comparar incremental y oráculo con equivalencia previa, y medir SC-001/SC-004 con evidencia reproducible.

- [ ] T026 Integrar el caso de resolubilidad en `bench/casos/resolubilidad.py`, `bench/casos/__init__.py`, `bench/runner.py` y `main.py`; añadir `tests/test_bench_resolubilidad.py`.
  - **Atiende**: FR-023; SC-002; RS-E12, RS-E33.
  - **Criterio**: `python -m pytest tests/test_bench_resolubilidad.py tests/test_bench_runner.py -q` pasa; `python main.py --bench` y `python main.py --bench --salida <ruta>` ambos ejecutan el caso de resolubilidad, sin vista ni red, y el benchmark rechaza discrepancias de veredicto/orden/frontera antes de cronometrar.
  - **Dependencias**: T006, T016–T018, T023.

- [ ] T027 Ejecutar el protocolo de medición en `bench/resultados/<timestamp>_<commit>_bench.json` y registrar resultados en `specs/003-resolubilidad/quickstart.md`.
  - **Atiende**: SC-001, SC-002, SC-004; RS-E22, RS-E27, RS-E33.
  - **Criterio**: ejecutar ambos comandos de T026 en un commit limpio, con ≥5 repeticiones por tamaño (preferiblemente 20), al menos tres tamaños con S/E/K duplicados y semillas registradas; guardar commit, entorno, semilla, mediana, p95 y máximo. Confirmar equivalencia antes del tiempo. SC-001 pasa solo si p95 <200 ms en la mayor cripta disponible y sintéticas; SC-004 pasa solo si cada duplicación aumenta p95 ≤2.5×. Si falla un umbral, optimizar `modelo/verificador_resolubilidad.py` y repetir hasta cumplir o dejar evidencia explícita del incumplimiento.
  - **Dependencias**: T026.

## Fase 7: Cierre y verificación transversal

- [ ] T028 Crear una revisión automatizada de restricciones en `tests/test_resolubilidad_restricciones.py` para `modelo/verificador_resolubilidad.py`, `vista/formato_resolubilidad.py` y `bench/casos/resolubilidad.py`.
  - **Atiende**: FR-009, FR-010, FR-012, FR-013, FR-017, FR-021; SC-003; G16; RS-E19, RS-E28, RS-E36.
  - **Criterio**: `python -m pytest tests/test_resolubilidad_restricciones.py -q` pasa y la revisión confirma que no se usan `dict`/`set` como índice/caché, `collections`, `heapq`, `bisect`, bibliotecas de grafos/rutas, `hash()` de cadenas ni `sorted()`/iteración nativa para ordenar el reporte; se reutilizan las estructuras y ordenamientos propios.
  - **Dependencias**: T016–T019, T026.

- [ ] T029 Documentar la decisión y uso en `docs/DECISIONES.md`, `README.md`, `docs/PROMPTS_LLM.md` y `specs/003-resolubilidad/quickstart.md`.
  - **Atiende**: FR-001, FR-014, FR-015, FR-023, FR-024; SC-001–SC-004; RS-E10, RS-E23, RS-E33–RS-E34.
  - **Criterio**: `git diff --check` pasa; `docs/DECISIONES.md` contiene problema, alternativas, decisión, complejidad, evidencia y límites; README y quickstart documentan `--verificar`, `--forzar`, pruebas y ambos modos de bench; `docs/PROMPTS_LLM.md` registra el cambio.
  - **Dependencias**: T023, T025–T027.

- [ ] T030 Ejecutar la suite y regresión final con `python -m pytest -q`.
  - **Atiende**: FR-001–FR-024; SC-001–SC-005; G14–G17; RS-E01–RS-E36.
  - **Criterio**: `python -m pytest -q` termina con código 0; además pasan las pruebas focalizadas descritas en `specs/003-resolubilidad/quickstart.md`. Adjuntar el resultado de la suite y la evidencia de benchmark a la revisión final.
  - **Dependencias**: T001–T029.

## Dependencias y orden de ejecución

### Dependencias entre fases

- **Fase 1**: T001 → T002 → T003 → T004; T005 es independiente y debe completarse antes de la fundación.
- **Fase 2**: T006 depende de T005 y deja disponible el generador/oráculo para el modelo y el benchmark.
- **US1**: pruebas T007–T015 pueden escribirse en paralelo después de T006; T016 precede a diagnósticos T017, ciclos T018, presentación T019 e inicio T020–T021.
- **US2**: pruebas T022 esperan el contrato de presentación; T023 implementa CLI y T024 excluye replay. Tras la fundación, US2 puede avanzar en paralelo con partes independientes de US1, pero su integración requiere T016–T021.
- **US3**: T025 depende del inicio integrado, CLI y resultado de datos.
- **Rendimiento**: T026 requiere incremental y oráculo; T027 mide solo después de comprobar equivalencia.
- **Cierre**: T028–T030 requieren las implementaciones y mediciones correspondientes.

### Oportunidades de paralelismo

- Fase 1: T001 y T005; luego T003 solo después de T002.
- Fase 3: T007–T015 son archivos distintos y pueden desarrollarse en paralelo después de T006.
- US2: T024 puede desarrollarse en paralelo con T023 una vez disponible T020 y las pruebas.
- Cierre: T028 y T029 pueden avanzar en paralelo una vez terminadas sus dependencias.

## Ejemplos de ejecución en paralelo

```text
Después de T006:
Task: T007, tests/test_resolubilidad_g14.py
Task: T008, tests/test_resolubilidad_g15.py
Task: T009, tests/test_resolubilidad_g16.py
Task: T010, tests/test_resolubilidad_g17.py
Task: T011–T015, archivos de escenarios adicionales indicados en cada tarea
```

```text
Después de T020 y T022:
Task: T023, CLI --verificar en main.py
Task: T024, bypass de verificación en controlador/controlador_replay.py
```

## Estrategia de implementación

### MVP

Completar Fases 1–3: consulta versionada de llaves, oráculo, verificador incremental y diagnóstico, formato y bloqueo de inicio normal. Validar G14–G17, casos de modelo y equivalencia con el oráculo antes de ampliar a CLI/forzado.

### Entrega incremental

1. Fuente de datos y oráculo.
2. US1: veredicto, rondas, diagnósticos y resumen de inicio.
3. US2: `--verificar`, reporte estable y replay sin verificación.
4. US3: `--forzar` para los estados permitidos.
5. Bench reproducible y cumplimiento de SC-001/SC-004.
6. Documentación, auditoría de restricciones y suite completa.

## Trazabilidad FR/SC/escenarios → tareas

| Requisito/escenario | Tareas |
|---|---|
| FR-001 | T001–T004 |
| FR-002 | T016 |
| FR-003 | T016 |
| FR-004 | T008, T016 |
| FR-005 | T011–T012, T016 |
| FR-006 | T011, T016 |
| FR-007 | T007, T016 |
| FR-008 | T012, T016 |
| FR-009 | T012–T013, T016 |
| FR-010 | T009, T016 |
| FR-011 | T007, T014, T017–T018 |
| FR-012 | T007, T011, T014, T018, T028 |
| FR-013 | T007, T015, T017 |
| FR-014 | T022–T023 |
| FR-015 | T010–T011, T019–T021, T025 |
| FR-016 | T001, T005, T008, T012–T013, T016–T017 |
| FR-017 | T006, T009, T016, T028 |
| FR-018 | T001–T004, T020, T025 |
| FR-019 | T001–T005, T012, T015, T020, T025 |
| FR-020 | T005, T012, T016 |
| FR-021 | T013–T015, T016, T018, T028 |
| FR-022 | T013, T017 |
| FR-023 | T024, T026 |
| FR-024 | T019, T021–T023, T029 |
| SC-001 | T027, T030 |
| SC-002 | T006, T026–T027 |
| SC-003 | T009, T016, T019, T028 |
| SC-004 | T013, T027, T030 |
| SC-005 | T001–T004, T020, T023, T025, T030 |
| G14 | T007, T017–T018, T030 |
| G15 | T008, T016, T030 |
| G16 | T009, T016, T019, T028, T030 |
| G17 | T010, T020, T025, T030 |
| RS-E01 | T011, T025, T030 |
| RS-E02 | T011, T018, T030 |
| RS-E03 | T011, T017, T030 |
| RS-E04 | T011, T016, T030 |
| RS-E05 | T011, T016–T017, T030 |
| RS-E06 | T011, T017, T030 |
| RS-E07 | T011, T016, T030 |
| RS-E08 | T011, T016, T030 |
| RS-E09 | T011, T016, T030 |
| RS-E10 | T001–T004, T012, T020, T025, T030 |
| RS-E11 | T001, T003–T004, T012, T030 |
| RS-E12 | T006, T026–T027, T030 |
| RS-E13 | T012, T016, T030 |
| RS-E14 | T008, T012, T016, T030 |
| RS-E15 | T012, T020, T025, T030 |
| RS-E16 | T012, T016, T030 |
| RS-E17 | T012, T016, T030 |
| RS-E18 | T012–T013, T016–T017, T030 |
| RS-E19 | T013, T016, T028, T030 |
| RS-E20 | T013, T016, T030 |
| RS-E21 | T013, T017, T030 |
| RS-E22 | T013, T027, T030 |
| RS-E23 | T022–T023, T030 |
| RS-E24 | T001, T022–T023, T030 |
| RS-E25 | T019–T021, T030 |
| RS-E26 | T024, T030 |
| RS-E27 | T027, T030 |
| RS-E28 | T014, T018, T028, T030 |
| RS-E29 | T014, T017–T018, T030 |
| RS-E30 | T022–T023, T030 |
| RS-E31 | T022–T023, T030 |
| RS-E32 | T021, T025, T030 |
| RS-E33 | T026–T027, T030 |
| RS-E34 | T019, T022–T023, T029–T030 |
| RS-E35 | T015, T020, T025, T030 |
| RS-E36 | T015, T017, T028, T030 |

**Requisitos sin cobertura**: ninguno; FR-001–FR-024, SC-001–SC-005, G14–G17 y RS-E01–RS-E36 tienen al menos una tarea asignada.

## Resumen de ejecución

- **Total**: 30 tareas.
- **US1 (P1)**: 15 tareas (T007–T021).
- **US2 (P2)**: 3 tareas (T022–T024).
- **US3 (P3)**: 1 tarea (T025).
- **Compartidas/fundacionales/bench/cierre**: 11 tareas (T001–T006, T026–T030).
- **Criterio independiente US1**: pruebas G14–G17 y RS-E01–RS-E22/RS-E28–RS-E29/RS-E35–RS-E36; equivalencia incremental/oráculo.
- **Criterio independiente US2**: reporte, código de salida 0/1/2, rechazo temprano, sin vista y replay sin verificación.
- **Criterio independiente US3**: forzado de NO RESOLUBLE/NO VERIFICABLE en consola y GUI; error de datos siempre bloquea.
- **MVP sugerido**: Fases 1–3 (US1).
- **Formato**: las 30 tareas usan checkbox, id secuencial, etiqueta [P] solo en tareas paralelizables, etiquetas de historia en fases US, ruta, trazabilidad, criterio y dependencias.
