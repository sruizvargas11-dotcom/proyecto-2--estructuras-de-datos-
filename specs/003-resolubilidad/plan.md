# Plan de implementación: Verificación de resolubilidad

**Rama**: `003-resolubilidad` | **Fecha**: 2026-11-12 | **Especificación**: [spec.md](./spec.md)

**Alcance**: documentos de diseño en `specs/003-resolubilidad`. Esta fase no modifica código ni crea `tasks.md`.

## Resumen

Antes de una partida nueva, el modelo evalúa si se alcanza la llave de salida y se cruza
hacia la sala de salida por una puerta que la requiera. Devuelve un resultado de datos;
la presentación imprime el reporte completo para `--verificar` y solo el veredicto y
motivo al iniciar. La opción de forzar omite el bloqueo de un resultado no resoluble o
no verificable, pero nunca un error de datos. El recorrido principal será incremental,
con rondas deterministas y puertas pendientes liberadas al obtener su llave. La
investigación de ciclos identifica una incompatibilidad potencial entre el desempate
lexicográfico actual de FR-012 y el límite de rendimiento: la alternativa polinómica
requiere una enmienda de la especificación antes de programar.

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
| II. Determinismo | Cumple con diseño pendiente | La spec fija orden de salas/llaves y semillas para sintéticas; falta definir una regla para el orden de direcciones y puertas paralelas en ciclos. |
| III. Separación MVC | Riesgo identificado | `main.py` y `nueva_partida()` son puntos existentes; `--replay` también usa `nueva_partida()`, por lo que habrá que exceptuarlo explícitamente. |
| IV. Datos externos | Cumple con condición | El modelo recibe topología y llaves desde fuentes; el generador sintético pertenecerá únicamente a `bench`. |
| V. Presupuesto | Riesgo identificado | `DatosHTTP._get()` cuenta intentos y reintentos. La consulta nueva debe pasar por ese control; falta definir el detalle de la fuente offline y disponibilidad del servicio. |
| VI. Rendimiento verificable | Pendiente de evidencia | `--bench` ya registra mediciones y entorno, pero no existe caso de resolubilidad ni evidencia para SC-001/004. |
| VII. Especificación antes del código | Cumple para esta fase | `spec.md` existe antes del plan; el diseño no modifica código. La enmienda potencial de FR-012 debe confirmarse y registrarse antes de implementar. |

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
| `tests/test_resolubilidad_e01_e09.py`, `tests/test_resolubilidad_e10_e18.py`, `tests/test_resolubilidad_e19_e27.py` | Grupos de escenarios adicionales; separar adaptadores y CLI en archivos de integración si el tamaño lo requiere. |

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
   sin llaves, usando esa región abierta como semillas; el peor caso sigue siendo
   O(U(S+E+K)+D), donde U es el número de llaves candidatas y D el número de pares
   indispensables reportados. Debe medirse con criptas no resolubles y ciclos; puede
   dominar SC-001.
4. **Ciclos**: la petición de FR-012 de elegir la secuencia lexicográfica mínima puede
   requerir enumerar un número exponencial de ciclos. Proponer ciclo más corto por llave
   y desempate lexicográfico determinista, calculable en O(U(U+D)) sobre dependencias.
   Es una **ENMIENDA REQUERIDA** de `spec.md`; no se aplica en este plan.
5. **Inicio y modos**: `nueva_partida()` debe invocar el verificador y entregar el
   resultado como dato. Si bloquea, propagar un error tipado que conserve el resultado
   para que consola/Pygame muestren solo veredicto y motivo. `--forzar` permite NO
   RESOLUBLE y NO VERIFICABLE, nunca error de datos. `reproducir()` debe indicar
   explícitamente que no verifique al llamar `nueva_partida()`. El detalle se imprime
   solo para `--verificar`; `--bench` sigue headless.
6. **Benchmark**: añadir un caso registrado en `bench/casos/__init__.py`. Validar
   equivalencia de veredicto, orden y frontera antes de cronometrar. Medir tres o más
   tamaños con duplicación de S/E/K, semilla fija y ≥20 repeticiones por tamaño para
   que la tabla actual muestre p95; conservar también máximo, mediana, muestras y
   metadatos. Ejecutar ambos algoritmos con los mismos datos, sin fuente, carga o vista.
   El protocolo completo está en [quickstart.md](./quickstart.md).

## Verificación de constitución después del diseño

| Principio | Estado del diseño | Evidencia |
|---|---|---|
| I. Estructuras propias | Cumple condicionado a implementación | La selección está acotada a `Cola`, `TablaHash`, `Vector` y ordenamientos propios. No hay `dict`/`set` como índice/cache ni bibliotecas prohibidas. |
| II. Determinismo | Cumple con observaciones | Las rondas, llaves, salas y enemigos tienen orden fijado. Falta precisar orden de direcciones y desempate de puertas de dependencia; se proponen en hallazgos, no se incorporan como reglas. |
| III. Separación MVC | Cumple condicionado a integración | Verificador en modelo; salida en presentación. El replay se excluye expresamente; CLI verificar/bench no instancian vista. |
| IV. Datos externos | Cumple | El modelo no contiene topología de cripta; el generador sintético vive en `bench`. |
| V. Presupuesto | Cumple condicionado a contrato | HTTP usa `_get()` para contar GET/reintentos. La cache/offline debe validar versión y las fallas de consulta no pueden aparentar éxito. |
| VI. Rendimiento verificable | Cumple condicionado a evidencia | El caso registra p95, máximo y metadatos; no se declara SC-001/004 satisfecho sin ejecutar y conservar evidencia. |
| VII. Especificación antes del código | Pendiente por FR-012 | Toda enmienda deberá actualizarse y confirmarse antes del código. No programar mientras el criterio exacto de ciclo contradiga el presupuesto medible. |
| Trazabilidad | Cumple en artefactos | [spec.md](./spec.md) relaciona escenarios y FR; la matriz de este plan conecta FR/SC con decisiones y pruebas previstas. Las tareas futuras citarán FR. |

## Seguimiento de complejidad

| Trabajo | Complejidad esperada | Evidencia y límite |
|---|---|---|
| Construcción de índices y recorrido/rondas A | O(S + E + K log K), esperado en índices hash propios | A frente a B con cadenas largas; hash adversario puede degradar la expectativa. |
| Referencia B | O(K(S + E + K)) en el peor caso | Solo oráculo/bench; nunca modo de producción. |
| Frontera | O(E), recogida durante el recorrido principal | Sin pasada posterior; orden final requiere ordenar entradas de salida. |
| Indispensables/dependencias | O(U(S_x + E_x + U) + D), máximo O(U(S+E+U)+U²) | U candidatos, región exterior x, D pares reportados; medir especialmente grafos no resolubles. |
| Ciclos alternativos | O(U(U + D)) tras ordenar vecinos, salida ≤U ciclos | Solo después de enmendar FR-012; el ciclo lexicográfico actual no tiene cota polinómica aceptable. |
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
| FR-011 | D2: resultado no resoluble y causas | G14, RS-E03, RS-E05 |
| FR-012 | D3: enmienda propuesta para ciclo polinómico | G14, RS-E02; bloqueada hasta confirmar enmienda |
| FR-013 | D2: frontera capturada durante recorrido | G14, RS-E06 |
| FR-014 | D5: CLI headless y códigos 0/1/2 | RS-E23/24, pruebas CLI |
| FR-015 | D5: resumen seguro y bloqueo/forzar | G17, RS-E01/25 |
| FR-016 | D4: sala inicial de enemigo y ubicaciones múltiples | G15, RS-E14/18 |
| FR-017 | D1/D6: entradas externas y orden canónico | G16, RS-E12, igualdad byte a byte |
| FR-018 | D4/D5: NO VERIFICABLE y forzado | RS-E10 |
| FR-019 | D4: error de datos no forzable | RS-E15/24 |
| FR-020 | D1: llave inicial en ronda 0 y puerta exigida | RS-E16 |
| FR-021 | D1: comparadores numérico/lexicográfico | RS-E19 |
| FR-022 | D2: todas las dependencias indispensables | RS-E03/21 |
| FR-023 | D5/D6: replay excluido; bench headless | RS-E12/26 |
| SC-001 | D6: p95 <200 ms, máximo guardado | RS-E27; evidencia bench reproducible |
| SC-002 | D6: A/B con semillas y equivalencia previa | RS-E12; oráculo sintético |
| SC-003 | D1/D6: reporte byte a byte | G16, RS-E12 |
| SC-004 | D6: tamaños duplicados y p95 ≤2.5× | RS-E22 |
| SC-005 | D4/D5: distinguir cuatro estados/resultados | RS-E10, E15, E23, E24, escenarios de inicio |

## Riesgos visibles

- **Ciclos**: FR-012 puede no cumplir el límite de rendimiento con su criterio lexicográfico.
  Requiere enmienda aprobada, no reinterpretación durante la implementación.
- **Validación de enemigos**: el esqueleto no contiene su roster; el contenido se carga
  bajo demanda. La consulta de llaves debe certificar el enemigo/sala inicial o aportar
  metadatos suficientes para detectar un enemigo inexistente sin cargar todos los cuartos.
- **Contrato externo**: el endpoint HTTP `/llaves` y el archivo offline correspondiente
  aún no están presentes; su disponibilidad, formato real y validación de referencias
  deben confirmarse contra la fuente.
- **Clasificación HTTP**: `DatosHTTP._get()` convierte hoy cualquier estado no exitoso en
  `RuntimeError`. La integración debe distinguir fallas de disponibilidad de respuestas
  que indiquen datos inválidos; un mapeo general de todos los estados HTTP a NO
  VERIFICABLE no satisface la distinción de FR-019.
- **Presupuesto**: el inicio puede depender de contenido/catálogo además de la consulta
  nueva. El forzado de NO VERIFICABLE no debe convertirse en una falla silenciosa de
  carga ni exceder presupuesto.
- **Orden determinista**: FR-013/012 no fijan una convención de dirección ni el desempate
  de varias puertas que representan la misma dependencia.
- **CLI/GUI**: combinaciones de `--verificar`, `--forzar`, `--gui`, `--bench`,
  `--replay` y `--salida` no están completamente especificadas.
- **Medición**: hoy `--bench --salida` deriva al reporte especializado de terreno y no
  ejecuta los casos registrados. Debe preservarse o aclararse el alcance de esa combinación.

## Borrador para `docs/DECISIONES.md`

**Problema**: verificar alcanzabilidad de llaves y puerta final antes de iniciar, explicar
las causas de NO RESOLUBLE, conservar determinismo y respetar el presupuesto del curso.

**Alternativas**:
- A: expansión incremental por salas, registro de puertas pendientes indexado por llave,
  liberación al adquirirla y orden por rondas.
- B: repetir recorrido completo por cada llave; más simple como referencia pero
  O(K(S+E+K)).
- Para ciclos: secuencia lexicográfica mínima (FR-012 actual, potencialmente exponencial)
  o ciclo más corto con desempate lexicográfico (polinómico).

**Decisión propuesta**: usar A en producción; conservar B como oráculo/benchmark. Solicitar
enmienda formal de FR-012 antes de elegir ciclo más corto. Consulta de llaves mediante
adaptadores existentes y caché JSON atómica validada por versión.

**Complejidad**: A O(S+E+K log K) esperada; diagnósticos O(U(S_x+E_x+U)+D);
ciclos alternativos O(U(U+D)). Ver tabla de complejidad y límites arriba.

**Evidencia planificada**: `--bench` con criptas sintéticas por semilla, al menos tres
tamaños doblados, 20 repeticiones, A/B equivalente antes del tiempo, y reporte de mediana,
p95, máximo, commit y entorno; además la cripta mayor disponible, sin red/carga/render.

**Límites conocidos**: máximo publicado local no determinado; el endpoint y archivo offline
faltan; la verificación de enemigo depende de contrato de fuente; la enmienda de ciclo y
varios desempates requieren aprobación antes del código.

## Hallazgos y enmiendas propuestas

1. **ENMIENDA REQUERIDA — FR-012**: sustituir la secuencia lexicográficamente mínima por
   “un ciclo simple más corto por llave participante, con secuencia de IDs
   lexicográficamente menor entre ciclos de igual longitud; canonizar el inicio en el ID
   menor; desempatar puertas por sala de origen y dirección”. Es polinómico, pero cambia
   el comportamiento observable solicitado. No se modifica `spec.md` en esta fase.
2. El orden de dirección en FR-008/013 y el desempate de puertas de dependencia no están
   definidos; propuesta: orden lexicográfico por código de carácter, pendiente de
   especificar.
3. La spec no define cómo comprobar desde las entradas del cliente que un `enemigo`
   existe y que `sala` coincide con su sala inicial; el esqueleto no trae enemigos.
   Propuesta: exigir que el servicio de llaves entregue referencias validadas o la
   información necesaria.
4. Si el mismo id aparece en varias ubicaciones de igual sala, falta desempate de enemigo;
   propuesta: id de enemigo lexicográfico, y ubicación sin enemigo antes que con enemigo.
5. Falta precisar si un id de llave es indispensable para otro cuando existen varias
   ubicaciones; propuesta: la llave permanece inobtenible solo si todas sus ubicaciones
   siguen fuera de la región.
6. Falta definir prioridad de causas si una llave puede etiquetarse como “en ciclo” y
   “depende de”; propuesta: “en ciclo” para participantes y “depende de” para el resto.
7. El comportamiento de combinaciones de flags CLI, y `--forzar` en el flujo GUI, no se
   especifica. Propuesta: rechazar combinaciones de modos de diagnóstico incompatibles y
   propagar el forzado al inicio GUI, previa confirmación en spec.
8. La fuente real de `--bench --salida` omite los casos generales. Precisar si el nuevo
   caso debe ejecutarse también con ese parámetro o si la exigencia de comparación aplica
   únicamente a `--bench` sin `--salida`.
9. Falta precisar qué hacer con una salida marcada cerrada cuyo campo de llave sea nulo o
   falte; la spec solo define la llave no listada. Propuesta: tratarla como puerta que no
   puede abrirse y representar la llave requerida como inexistente, previa confirmación.
10. El formato textual del reporte y del resumen no está definido línea por línea. Se
    propone una plantilla estable en [contracts/cli.md](./contracts/cli.md), pendiente
    de aprobación como contrato de presentación.
11. `CriptaModelo` admite `llave_salida=None`, pero la spec no define ese caso. Propuesta:
    clasificarlo como error de datos no forzable, previa confirmación.
