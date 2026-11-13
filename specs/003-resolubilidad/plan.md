# Plan de implementación: Verificación de resolubilidad

**Rama**: `003-resolubilidad` | **Fecha**: 2026-11-12 | **Especificación**: [spec.md](./spec.md)

**Alcance**: documentos de diseño en `specs/003-resolubilidad`. Esta fase no modifica código ni crea `tasks.md`.

## Resumen

Antes de una partida nueva, el modelo evalúa si se alcanza la llave de salida y se cruza
hacia la sala de salida por una puerta que la requiera. Devuelve un resultado de datos;
la presentación imprime el reporte completo para `--verificar` y solo el veredicto y
motivo al iniciar. La opción de forzar omite el bloqueo de un resultado no resoluble o
no verificable, pero nunca un error de datos. El recorrido principal será incremental,
con rondas deterministas y puertas pendientes liberadas al obtener su llave. La enmienda
post-plan fija ciclos simples más cortos con desempate determinista, direcciones
lexicográficas, precedencia de causas, modos CLI y el formato estable.

## Contexto técnico

**Lenguaje/versión**: Python 3.12; README declara como entorno de referencia Python 3.12.

**Dependencias principales**: dependencias existentes (`requests`, `pygame`, `pytest`).
No se propone dependencia nueva ni biblioteca de grafos/rutas.

**Persistencia**: JSON. El esqueleto se carga y se cachea por versión; las ubicaciones de
llaves se agregarán a la fuente HTTP/offline y a caché local versionada.

**Pruebas**: `pytest`, pruebas actuales de modelo, adaptadores, CLI, GUI y regresión.

**Plataforma**: Windows local como entorno de medición de referencia; sin afirmar
validación en otras plataformas.

**Tipo de proyecto**: juego de escritorio Python con MVC, CLI, vista de consola y Pygame.

**Objetivos de rendimiento**:
- SC-001: p95 < 200 ms, ≥5 repeticiones, con máximo informado; excluye red, carga de
  datos y renderizado.
- SC-004: al duplicar salas, salidas y llaves entre tamaños consecutivos, p95 aumenta
  como máximo 2.5×; al menos tres tamaños y cinco repeticiones por tamaño.
- SC-002: comparar recorrido incremental y referencia de recorrido completo repetido
  en criptas sintéticas deterministas por semilla.

**Restricciones**:
- Reutilizar `Cola`, `TablaHash`, `Vector` y los ordenamientos propios.
- No usar `dict`/`set` como índice o caché, ni `collections`, `heapq`, `bisect`,
  `networkx`, bibliotecas de grafos/rutas, `hash()` de cadenas ni iteración nativa para
  decidir el orden.
- No depender de `modelo/buscador_rutas.py`; la topología es dirigida y el costo de
  salida no participa en el veredicto.
- El verificador pertenece al modelo, no muta `CriptaModelo` y devuelve datos; la
  presentación da formato al texto.
- `--verificar`, `--bench` y `--replay` no crean una vista. `--replay` no verifica.
- Consultar llaves consume presupuesto; una falla de consulta produce NO VERIFICABLE.
- No incluir datos de una cripta concreta en la lógica.

**Escala**: el repositorio contiene datos offline de `cripta-01`, pero no fija el máximo
de criptas publicadas. Hasta que haya una cripta publicada mayor disponible localmente,
SC-001 se mide en la mayor disponible y en criptas sintéticas, registrando tamaño,
semilla y entorno.

## Verificación de constitución antes del diseño

| Principio | Estado previo | Evidencia y condición |
|---|---|---|
| I. Estructuras propias | Cumple con diseño pendiente | El repositorio incluye `Cola`, `TablaHash`, `Vector` y ordenamientos propios. Aún se debe elegir su composición para rondas y puertas pendientes. |
| II. Determinismo | Cumple con diseño pendiente | En el diagnóstico inicial faltaba fijar orden de direcciones y puertas paralelas en ciclos; ambos puntos están resueltos en la enmienda post-plan. |
| III. Separación MVC | Riesgo identificado | `main.py` y `nueva_partida()` son puntos existentes; `--replay` también usa `nueva_partida()`, por lo que habrá que exceptuarlo explícitamente. |
| IV. Datos externos | Cumple con condición | El modelo recibe topología y llaves desde fuentes; el generador sintético pertenecerá únicamente a `bench`. |
| V. Presupuesto | Riesgo identificado | `DatosHTTP._get()` cuenta intentos y reintentos. La consulta nueva debe pasar por ese control; falta definir el detalle de la fuente offline y disponibilidad del servicio. |
| VI. Rendimiento verificable | Pendiente de evidencia | `--bench` ya registra mediciones y entorno, pero no existe caso de resolubilidad ni evidencia para SC-001/004. |
| VII. Especificación antes del código | Cumple para esta fase | `spec.md` y su enmienda post-plan preceden al código; el diseño no modifica código. |

Esta tabla conserva el diagnóstico que precedió al diseño; el estado actualizado de cada
hallazgo se registra al final de este plan.

## Estructura del proyecto

### Documentación de esta capacidad

```text
specs/003-resolubilidad/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
└── contracts/
    ├── cli.md
    └── fuente-llaves.md
```

No se genera `tasks.md` en esta fase.

### Código existente que deberá tocar la implementación

| Ruta | Motivo |
|---|---|
| [adaptadores/fuente_datos.py](../../adaptadores/fuente_datos.py) | Declarar la consulta de ubicaciones de llaves en la interfaz común. |
| [adaptadores/datos_http.py](../../adaptadores/datos_http.py) | Consultar `GET /criptas/<id>/llaves` a través de `_get()` para contar cada intento y respetar reintentos/presupuesto. |
| [adaptadores/datos_offline.py](../../adaptadores/datos_offline.py) | Leer el archivo de llaves de la cripta offline; ese archivo aún no está en `datos_offline/`. |
| [adaptadores/datos_simulado.py](../../adaptadores/datos_simulado.py) | Delegar la nueva operación conservando la demora determinista existente. |
| [herramientas/descargar_offline.py](../../herramientas/descargar_offline.py) | Descargar y guardar la consulta de llaves con la versión de la cripta. |
| [persistencia/cache_json.py](../../persistencia/cache_json.py) | Reutilizar el contenedor JSON versionado y la escritura atómica existentes. |
| [controlador/inicio_partida.py](../../controlador/inicio_partida.py) | Orquestar verificación y decisión de bloqueo en `nueva_partida`; exponer el resultado sin formatearlo. |
| [controlador/controlador_replay.py](../../controlador/controlador_replay.py) | Desactivar explícitamente la verificación en el camino que reutiliza `nueva_partida()`. |
| [controlador/controlador_pygame.py](../../controlador/controlador_pygame.py) y [vista_pygame/escenas/menu_criptas.py](../../vista_pygame/escenas/menu_criptas.py) | Mostrar resumen al iniciar y presentar de forma visible el bloqueo; recibir el resultado sin ubicaciones. |
| [main.py](../../main.py) | Añadir `--verificar` y `--forzar`, formato de consola, y códigos de salida 0/1/2 sin crear la vista. |
| [bench/runner.py](../../bench/runner.py) y [bench/casos/__init__.py](../../bench/casos/__init__.py) | Registrar el caso nuevo en el camino normal de `--bench`, sin vista. |

### Módulos nuevos propuestos

| Ruta propuesta | Responsabilidad |
|---|---|
| `modelo/verificador_resolubilidad.py` | Recorrido puro sobre `CriptaModelo` y ubicaciones; devuelve resultado tipado, sin formatear ni modificar el mundo. |
| `persistencia/llaves_cripta.py` | Adaptar `cache_json` a la ruta e identidad de la lista de llaves; valida versión y estructura. Justificación: hay persistencias separadas por tipo de dato y no se debe mezclar la lista con el esqueleto. |
| `vista/formato_resolubilidad.py` | Formato estable del reporte completo y del resumen seguro al iniciar. |
| `bench/casos/resolubilidad.py` | Generador sintético determinista, referencia B, comparación de salidas y mediciones A/B. |
| `tests/test_resolubilidad_g14.py` … `tests/test_resolubilidad_g17.py` | Un archivo por escenario obligatorio, cada prueba cita sus FR/SC. |
| `tests/test_resolubilidad_e01_e09.py`, `tests/test_resolubilidad_e10_e18.py`, `tests/test_resolubilidad_e19_e27.py`, `tests/test_resolubilidad_e28_e36.py` | Grupos de escenarios adicionales; separar adaptadores y CLI en archivos de integración si el tamaño lo requiere. |

**Decisión de estructura**: integrar en las capas MVC existentes y crear solo el
verificador, el adaptador de persistencia versionada, el formateador y el caso de bench.
La topología se lee de `CriptaModelo`, `Sala` y `Salida`; `Salida.sala_destino` ya se
enlaza al terminar la carga. No se asumen IDs densos ni se consulta `sala_por_id()` por
cada arista: esa búsqueda binaria es O(log S).

## Decisiones de integración

1. **Fuente de llaves y persistencia**: añadir la operación `llaves_cripta(cripta_id)`
   con respuesta lógica `{llaves: [...]}`; HTTP usa `_get`, offline lee
   `datos_offline/<cripta_id>/llaves.json`, y `DatosSimulado` delega. Guardar la copia
   local bajo `partidas/cache/<cripta_id>/llaves.json` mediante `guardar_cache` /
   `cargar_cache`, comparando la versión con `CriptaModelo.version`. La especificación
   de la respuesta, fallos y presupuesto está en [fuente-llaves.md](./contracts/fuente-llaves.md).
2. **Recorrido incremental**: construir índices propios por sala y llave; expandir cada
   sala una vez, registrar una puerta cerrada pendiente por llave, y liberar sus puertas
   al completar la ronda que obtiene esa llave. Cada ronda se ordena antes de habilitar
   la siguiente. Complejidad esperada O(S + E + K log K), más costo esperado de las
   tablas hash y tamaño del reporte. La referencia de recorrido repetido queda solo en
   pruebas/bench.
3. **Diagnóstico**: capturar la frontera en el recorrido base, sin recorrido adicional.
   Para indispensables, evaluar candidatos sobre la región exterior a la alcanzabilidad
   sin llaves, usando esa región abierta como semillas. Una llave con varias ubicaciones
   permanece inobtenible solo si todas siguen fuera; la indispensabilidad se calcula
   sobre todas ellas. Las llaves participantes en ciclos reportados reciben causa «en
   ciclo» y las demás dependientes «depende de». El peor caso sigue siendo
   O(U(S+E+K)+D), donde U es el número de llaves candidatas y D el número de pares
   indispensables reportados. Debe medirse con criptas no resolubles y ciclos; puede
   dominar SC-001.
4. **Ciclos**: FR-012 ahora requiere por llave un ciclo simple más corto, desempate por
   secuencia lexicográfica, inicio canónico en el id menor y puertas ordenadas por sala
   de origen/dirección lexicográfica. Se conserva la búsqueda por capas determinista,
   con complejidad O(U(U+D)) sobre dependencias; ya no hay enmienda pendiente.
5. **Inicio y modos**: `nueva_partida()` verifica y entrega el resultado como dato. Si
   bloquea, propaga un error tipado que conserva el resultado para el resumen de
   consola/Pygame. `--forzar` permite NO RESOLUBLE y NO VERIFICABLE, nunca error de
   datos, y también se aplica con `--gui`. `--verificar` ignora `--forzar`, pero se
   rechaza con `--replay` o `--bench` antes de consultar. `reproducir()` indica
   explícitamente que no verifique al llamar `nueva_partida()`. El reporte y resumen
   siguen el contrato estable de [contracts/cli.md](./contracts/cli.md).
6. **Benchmark**: añadir un caso registrado en `bench/casos/__init__.py` que se ejecute
   en `--bench` con y sin `--salida`. Validar equivalencia de veredicto, orden y frontera
   antes de cronometrar. Medir tres o más tamaños con duplicación de S/E/K, semilla fija
   y ≥20 repeticiones por tamaño para que la tabla actual muestre p95; conservar también
   máximo, mediana, muestras y metadatos. Ejecutar ambos algoritmos con los mismos datos,
   sin fuente, carga o vista. El protocolo completo está en [quickstart.md](./quickstart.md).

## Verificación de constitución después del diseño

| Principio | Estado del diseño | Evidencia |
|---|---|---|
| I. Estructuras propias | Cumple condicionado a implementación | La selección está acotada a `Cola`, `TablaHash`, `Vector` y ordenamientos propios. No hay `dict`/`set` como índice/cache ni bibliotecas prohibidas. |
| II. Determinismo | Cumple | Direcciones y puertas de ciclos se ordenan lexicográficamente después del origen; ubicaciones duplicadas en una sala prefieren ausencia de enemigo y luego su id. |
| III. Separación MVC | Cumple condicionado a integración | Verificador en modelo; salida en presentación. `--verificar` con `--replay` o `--bench` se rechaza; replay se excluye y bench/verify no instancian vista. |
| IV. Datos externos | Cumple | El modelo no contiene topología de cripta; el generador sintético vive en `bench`. |
| V. Presupuesto | Cumple condicionado a contrato | HTTP usa `_get()` para contar GET/reintentos. La cache/offline debe validar versión y las fallas de consulta no pueden aparentar éxito. |
| VI. Rendimiento verificable | Cumple condicionado a evidencia | El caso registra p95, máximo y metadatos; no se declara SC-001/004 satisfecho sin ejecutar y conservar evidencia. |
| VII. Especificación antes del código | Cumple para esta fase | La enmienda FR-012 y los demás hallazgos resueltos ya constan en `spec.md`; no se modifica código. |
| Trazabilidad | Cumple en artefactos | [spec.md](./spec.md) relaciona escenarios y FR; la matriz de este plan conecta FR/SC con decisiones y pruebas previstas. Las tareas futuras citarán FR. |

## Seguimiento de complejidad

| Trabajo | Complejidad esperada | Evidencia y límite |
|---|---|---|
| Construcción de índices y recorrido/rondas A | O(S + E + K log K), esperado en índices hash propios | A frente a B con cadenas largas; hash adversario puede degradar la expectativa. |
| Referencia B | O(K(S + E + K)) en el peor caso | Solo oráculo/bench; nunca modo de producción. |
| Frontera | O(E), recogida durante el recorrido principal | Sin pasada posterior; orden final requiere ordenar entradas de salida. |
| Indispensables/dependencias | O(U(S_x + E_x + U) + D), máximo O(U(S+E+U)+U²) | U candidatos, región exterior x, D pares reportados; medir especialmente grafos no resolubles. |
| Ciclos | O(U(U + D)) tras ordenar vecinos, salida ≤U ciclos | Ciclo simple más corto por llave; secuencia lexicográfica y puertas con orden estable conforme a FR-012. |
| Formato determinista | O(R log R) sobre campos del reporte | Ordenamientos propios; no se usa el orden de iteración hash. |

## Trazabilidad FR/SC → decisión → prueba prevista

| Requisito | Decisión | Prueba prevista |
|---|---|---|
| FR-001 | D4: consulta y caché versionada | `test_fuente_llaves.py`; RS-E10/11 |
| FR-002 | D1: solo aristas salientes dirigidas | RS-E08 |
| FR-003 | D1: liberar puerta si abierta o llave adquirida; no consumir | RS-E09 |
| FR-004 | D1/D4: enemigo no impide la ubicación | G15, RS-E14 |
| FR-005 | D1: trampas/cierres fuera de la decisión | RS-E13 |
| FR-006 | D1: costo ignorado por recorrido | RS-E07 |
| FR-007 | D1: veredicto exige llave y puerta final | G14, RS-E05, RS-E16 |
| FR-008 | D1: escoger primera puerta cruzable en orden | RS-E17 |
| FR-009 | D1: rondas completas, sort antes de liberar | G16, RS-E04, RS-E16, RS-E18–20 |
| FR-010 | D1: propiedades del orden y repetibilidad | G16, prueba byte a byte |
| FR-011 | D2: causas con precedencia para ciclos reportados | G14, RS-E03, RS-E05, RS-E29 |
| FR-012 | D3: ciclo simple más corto, desempate lexicográfico | G14, RS-E02, RS-E28 |
| FR-013 | D2: frontera incremental; dirección lexicográfica; llave nula «inexistente» | G14, RS-E06/36 |
| FR-014 | D5: CLI headless, modos mutuamente excluyentes, force ignorado | RS-E23/24, RS-E30/31 |
| FR-015 | D5: resumen seguro, bloqueo y force también con GUI | G17, RS-E01/25/32 |
| FR-016 | D4: validar sala, no existencia del enemigo; desempate de ubicaciones | G15, RS-E14/18/24 |
| FR-017 | D1/D6: entradas externas y orden canónico | G16, RS-E12, igualdad byte a byte |
| FR-018 | D4/D5: NO VERIFICABLE y forzado | RS-E10 |
| FR-019 | D4: sala/llave_salida inválida no forzable; enemigo no validado | RS-E15/24/35 |
| FR-020 | D1: llave inicial en ronda 0 y puerta exigida | RS-E16 |
| FR-021 | D1: comparadores numérico/lexicográfico, también dirección | RS-E17/19/28/36 |
| FR-022 | D2: todas las dependencias, sobre cada ubicación | RS-E03/18/21 |
| FR-023 | D5/D6: replay excluido; bench headless con/sin `--salida` | RS-E12/26/30/33 |
| FR-024 | D5: formato estable del reporte y resumen | RS-E34 |
| SC-001 | D6: p95 <200 ms, máximo guardado | RS-E27; evidencia bench reproducible |
| SC-002 | D6: A/B con semillas y equivalencia previa | RS-E12; oráculo sintético |
| SC-003 | D1/D6: reporte byte a byte | G16, RS-E12 |
| SC-004 | D6: tamaños duplicados y p95 ≤2.5× | RS-E22 |
| SC-005 | D4/D5: distinguir cuatro estados/resultados | RS-E10, E15, E23, E24, escenarios de inicio |

## Riesgos visibles

- **Ciclos**: FR-012 ya fija el ciclo simple más corto con desempate determinista. Aun así,
  medir el peor caso denso junto a SC-001.
- **Validación de enemigos**: por la enmienda, el cliente valida solo que exista la sala;
  no valida el id de enemigo porque el esqueleto no contiene su roster.
- **Contrato externo**: el endpoint HTTP `/llaves` y el archivo offline correspondiente
  aún no están presentes; su disponibilidad y esquema real deben confirmarse contra la
  fuente. La validez de la sala se comprueba en el cliente; el id de enemigo no se valida.
- **Clasificación HTTP**: `DatosHTTP._get()` convierte hoy cualquier estado no exitoso en
  `RuntimeError`. La integración debe distinguir fallas de disponibilidad de respuestas
  que indiquen datos inválidos; un mapeo general de todos los estados HTTP a NO
  VERIFICABLE no satisface la distinción de FR-019.
- **Presupuesto**: el inicio puede depender de contenido/catálogo además de la consulta
  nueva. El forzado de NO VERIFICABLE no debe convertirse en una falla silenciosa de
  carga ni exceder presupuesto.
- **CLI/GUI**: FR-014/015 ya fijan rechazo de `--verificar` con replay/bench, ignorar
  `--forzar` en verificación y aplicar `--forzar` también en GUI.
- **Medición**: FR-023 requiere que el caso de resolubilidad se ejecute tanto con como
  sin `--salida`; la implementación debe integrar el caso aun cuando `main_bench(salida)`
  produzca además el reporte especializado de terreno.

## Borrador para `docs/DECISIONES.md`

**Problema**: verificar alcanzabilidad de llaves y puerta final antes de iniciar, explicar
las causas de NO RESOLUBLE, conservar determinismo y respetar el presupuesto del curso.

**Alternativas**:
- A: expansión incremental por salas, registro de puertas pendientes indexado por llave,
  liberación al adquirirla y orden por rondas.
- B: repetir recorrido completo por cada llave; más simple como referencia pero
  O(K(S+E+K)).
- Para ciclos: enumerar todos para escoger la secuencia lexicográfica mínima o seleccionar
  un ciclo simple más corto con desempate lexicográfico.

**Decisión**: usar A en producción; conservar B como oráculo/benchmark. Aplicar el ciclo
simple más corto por llave, con desempates estables de secuencia y puerta según FR-012
enmendado. Consultar llaves mediante adaptadores existentes y caché JSON atómica validada
por versión.

**Complejidad**: A O(S+E+K log K) esperada; diagnósticos O(U(S_x+E_x+U)+D);
ciclos O(U(U+D)). La indispensabilidad considera todas las ubicaciones de cada llave.
Ver tabla de complejidad y límites arriba.

**Evidencia planificada**: `--bench` con criptas sintéticas por semilla, al menos tres
tamaños doblados, 20 repeticiones, A/B equivalente antes del tiempo, y reporte de mediana,
p95, máximo, commit y entorno; el caso se ejecuta con y sin `--salida`. Medir también la
cripta mayor disponible, sin red/carga/render.

**Límites conocidos**: máximo publicado local no determinado; el endpoint y archivo offline
faltan; solo se valida la sala de ubicación, no la existencia del enemigo. El contrato de
errores HTTP y de esquema externo debe conservar la distinción entre disponibilidad y
datos inválidos.

## Hallazgos resueltos en la spec

1. **Resuelto en spec (enmienda post-plan)**: FR-012 elige un ciclo simple más corto por
   llave, luego secuencia lexicográfica, inicio canónico menor y puertas por sala/dirección.
2. **Resuelto en spec (enmienda post-plan)**: FR-008, FR-013 y FR-021 fijan dirección
   lexicográfica por código de carácter para puerta final, frontera y dependencias.
3. **Resuelto en spec (enmienda post-plan)**: FR-016/019 y RS-E24 validan la sala, no la
   existencia del enemigo asociado.
4. **Resuelto en spec (enmienda post-plan)**: FR-016 y RS-E18 desempatan ubicaciones de
   igual sala por ausencia de enemigo y luego id de enemigo lexicográfico.
5. **Resuelto en spec (enmienda post-plan)**: FR-022 y RS-E18/21 consideran inobtenible
   una llave solo si todas sus ubicaciones siguen inalcanzables.
6. **Resuelto en spec (enmienda post-plan)**: FR-011/RS-E29 dan prioridad «en ciclo» a
   participantes de ciclos reportados y «depende de» a las otras dependientes.
7. **Resuelto en spec (enmienda post-plan)**: FR-014/015 y RS-E30–32 rechazan combinaciones
   verificar/replay o verificar/bench antes de consultar, ignoran force con verificar y
   aplican force también a GUI.
8. **Resuelto en spec (enmienda post-plan)**: FR-023/SC-002 y RS-E33 requieren el caso de
   resolubilidad con y sin `--salida`.
9. **Resuelto en spec (enmienda post-plan)**: FR-013 y RS-E06 establecen que una puerta
   cerrada sin llave nunca abre y se muestra con llave «inexistente».
10. **Resuelto en spec (enmienda post-plan)**: FR-024/RS-E34 hacen normativo el formato
    estable del contrato `contracts/cli.md`.
11. **Resuelto en spec (enmienda post-plan)**: FR-019/RS-E35 clasifican `llave_salida`
    ausente o nula como error de datos no forzable.

## FR y escenarios nuevos o modificados

- **Nuevo FR**: FR-024 (formato estable del reporte completo y resumen inicial).
- **FR modificados**: FR-008, FR-011–FR-016, FR-019, FR-021–FR-023.
- **Escenarios modificados**: RS-E06, RS-E17, RS-E18, RS-E21 y RS-E24.
- **Escenarios nuevos**: RS-E28–RS-E36. G14–G17 conservan sus identificadores.
