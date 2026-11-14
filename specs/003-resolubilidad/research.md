# Investigación y decisiones

Esta investigación se basa en la especificación enmendada, la constitución y el código
presente en el repositorio. No se consulta la red ni se implementan cambios. Las
decisiones post-plan están incorporadas en `spec.md` y se reflejan aquí y en los contratos.

## D1. Recorrido incremental con rondas (FR-002–FR-010, SC-002–SC-004)

### Alternativas consideradas

**A. Incremental**: una cola propia de salas; índice propio de llaves por ubicación;
registro de puertas cerradas pendientes indexado por id de llave. Las puertas se
desbloquean al incorporar la llave al final de su ronda. Ordenar las llaves nuevas por
(sala numérica, id de llave lexicográfico) antes de liberar puertas para la siguiente
ronda.

**B. Repetir recorrido completo**: recalcular desde la sala inicial al incorporar cada
llave, descartando o reconstruyendo el estado anterior.

**C. Usar `modelo/buscador_rutas.py`**: reutilizar el buscador ya existente.

### Decisión

Elegir A en producción. La topología es alcanzabilidad dirigida sin costo; el buscador
existente calcula rutas de costo mínimo y no corresponde al requisito. Conservar B solo
como oráculo de pruebas y variante de referencia en bench.

El recorrido abre primero el conjunto alcanzable con las llaves previas; recolecta la
ronda completa, la ordena y recién después libera las puertas de esas llaves. Cada sala
y salida se procesa una vez en la expansión incremental; las ubicaciones y salidas se
acceden mediante índices propios. El corte por puerta final se aplica después de
completar la ronda correspondiente.

### Complejidad y medición

- A: O(S+E+K log K) esperada, más el tamaño de la salida; el costo hash es esperado,
  no una garantía de peor caso. Las salas y llaves de una ronda usan ordenamiento propio.
- B: hasta O(K(S+E+K)) y sirve como comparación, no como camino de producción.
- SC-002: comparar resultado A/B en escenarios sintéticos deterministas por semilla.
- SC-004: familias de tres o más tamaños duplicados; registrar mediana, p95 y máximo.

### Límites

`CriptaModelo.sala_por_id()` es O(log S), por lo que no se debe llamar por cada arista.
La topología ya enlaza `Salida.sala_destino`; la clave es no asumir IDs densos y crear un
índice propio solo para asociaciones de IDs externas. La igualdad A/B debe comprobar
veredicto, orden por rondas y frontera antes de medir. Los costos no participan.

## D2. Diagnóstico de no resolubilidad (FR-011, FR-013, FR-022)

### Alternativas consideradas

**A. Capturar la frontera en la expansión** y reutilizar el resultado base; evaluar
indispensabilidad con recorridos adicionales acotados a las llaves candidatas y región
exterior al alcance sin llaves.

**B. Hacer un recorrido posterior completo por cada puerta y por cada relación de llave**.

**C. Inferir la frontera/ciclo directamente desde la topología sin calcular
alcanzabilidad con cada llave retirada**.

### Decisión

Elegir A. Cada puerta pendiente con origen alcanzable se registra como frontera durante
la expansión que descubre el origen, evitando un segundo barrido topológico. Para probar
si `kj` es indispensable, ejecutar una evaluación con todas las llaves excepto `kj`,
sembrada desde las salas alcanzables sin puertas cerradas y limitada al exterior que
podría cambiar de alcance. Inspeccionar todas las ubicaciones de las llaves candidatas
en cada evaluación y conservar todas las relaciones que exige FR-022. Una llave con
varias ubicaciones sigue inobtenible únicamente si todas ellas continúan inalcanzables.
Para las causas, las llaves que participan en un ciclo reportado reciben «en ciclo»;
las demás dependientes reciben «depende de». La frontera se imprime por sala de origen
numérica y luego dirección lexicográfica por código de carácter.

No reemplazar la prueba de indispensabilidad por análisis de ciclos solamente: una ruta
alternativa invalida una dependencia aunque el grafo de puertas parezca cíclico.

### Complejidad y medición

Sea U el número de llaves candidatas, Sx/Ex el número de salas/salidas del subgrafo
exterior examinado y D el número de pares indispensables que se reportan. El peor caso
es O(U(Sx+Ex+U)+D), con cota global O(U(S+E+U)+U²). D puede ser cuadrático y forma parte
del tamaño de salida. Medir tanto no resolubles acíclicos como ciclos y mallas con muchas
relaciones; contrastar contra SC-001.

### Límites

El subgrafo exterior puede coincidir con la cripta completa, por lo que el límite p95
no se garantiza solo por el algoritmo incremental. El trabajo no debe ejecutarse por
cada par de llaves si una evaluación retirada ya puede clasificar todas las llaves
candidatas. Las causas siguen la precedencia fijada por FR-011: «en ciclo» para
participantes de ciclos reportados y «depende de» para las demás llaves dependientes.

## D3. Selección de ciclos (FR-012)

### Alternativas consideradas

**A. Criterio actual**: enumerar ciclos simples que contienen cada llave y elegir la
secuencia de IDs lexicográficamente menor. El número de ciclos simples puede ser
exponencial.

**B. Ciclo más corto por cada llave participante**, con vecinos ordenados y desempate
lexicográfico entre secuencias de igual longitud. La búsqueda por capas encuentra
caminos mínimos en el grafo lógico de dependencias.

**C. Reportar un ciclo DFS arbitrario**: barato, pero no cumple el determinismo semántico
del criterio solicitado sin agregar reglas de visita.

### Decisión

Aplicar B, ahora fijada por la enmienda de FR-012. Para cada llave participante se
selecciona el ciclo simple de menor longitud; a igual longitud, la menor secuencia de IDs
lexicográfica con inicio canónico en el ID menor. Las puertas de cada ciclo se ordenan
por sala de origen numérica y dirección lexicográfica por código de carácter. Los ciclos
se ordenan por el id inicial. La opción A queda descartada para el comportamiento
normativo porque enumera potencialmente todos los ciclos simples.

### Complejidad y medición

Con U llaves candidatas y D enlaces de dependencia, ordenar vecinos y ejecutar una
búsqueda por capas por llave cuesta O(U(U+D)) más el ordenamiento determinista; como
máximo se informa un ciclo por cada llave participante, hasta U ciclos. Probar ciclos
propios, auto-ciclos y rutas alternativas; medir el caso denso junto a SC-001.

### Límites

La regla ya es observable y normativa. La complejidad O(U(U+D)) debe medirse con grafos
densos. Si existen puertas paralelas para un mismo enlace de dependencia, se imprimen
en el orden de sala de origen y dirección fijado en la spec.

## D4. Fuente y persistencia de llaves (FR-001, FR-016, FR-018, FR-019)

### Alternativas consideradas

**A. Agregar `llaves_cripta()` a `FuenteDeDatos` y a HTTP, offline y simulado; almacenar
la respuesta en un cache independiente validado por versión.**

**B. Incluir la lista de llaves en el esqueleto persistido**, cambiando su formato y su
ciclo de actualización.

**C. Consultar el endpoint directamente desde el modelo/controlador de inicio**, sin
adaptador común ni persistencia versionada.

### Decisión

Elegir A: mantiene la fuente intercambiable y separa una colección que se consulta por
endpoint distinto del esqueleto. Reutilizar `guardar_cache`/`cargar_cache` de
`persistencia/cache_json.py`, que ya guarda versión, identificador y JSON atómicamente.
La forma de la respuesta local se conserva como objeto `{llaves: [...]}`. El archivo
offline propuesto es `datos_offline/<cripta_id>/llaves.json`, con versión asociada; el
descargador offline lo obtiene con la misma operación lógica que HTTP. `DatosSimulado`
delega el método para que los tests sigan cubriendo la interfaz completa.

Fallas de transporte, timeout, indisponibilidad del servicio, reintentos agotados o
presupuesto producen NO VERIFICABLE. Respuesta inválida o ubicación que refiere a una
sala inexistente es error de datos y no se fuerza. La verificación no valida si existe el
enemigo indicado; el id es metadato de ubicación. El adaptador HTTP debe usar
`_get()`; `_get()` suma cada intento, incluidos reintentos. La lista cacheada se usa solo
si la versión coincide con la del esqueleto actual; si no coincide, se descarta y se
consulta la fuente. La clasificación de estados HTTP debe basarse en el contrato de
error del servicio; el `RuntimeError` genérico actual no basta para distinguir datos de
indisponibilidad.

### Complejidad y medición

La carga de la lista y la indexación en el verificador son O(K) esperadas. La red y la
carga no forman parte del benchmark de algoritmo. Las pruebas de adaptador comprueban
presupuesto/reintentos, versión coincidente/obsoleta, modo offline y fallo de esquema.

### Límites

El repositorio no contiene endpoint ni archivo offline de llaves. El esqueleto y el
contenido de salas no ofrecen un roster completo ya cargado; FR-016 resuelve el alcance:
se valida la sala de ubicación, no la existencia del enemigo. El contrato definitivo de
la respuesta del servicio requiere confirmación. La falta de un archivo offline se trata
como consulta no disponible y no como lista vacía.

## D5. CLI e inicio de partida (FR-014, FR-015, FR-018, FR-019, FR-023)

### Alternativas consideradas

**A. Verificar en cada vista por separado**, duplicando la regla de bloqueo en consola y
Pygame.

**B. Verificar en `controlador/inicio_partida.py` y entregar el resultado a las vistas**,
dejando el modelo como dueño del cálculo y cada presentación a cargo del texto.

**C. Verificar dentro de `CriptaModelo` durante su construcción**, haciendo que cargar un
esqueleto consulte la fuente de llaves.

### Decisión

Elegir B. El verificador del modelo recibe cripta y ubicaciones y devuelve datos; el
controlador orquesta consulta, error y bloqueo. `nueva_partida()` conserva el resultado
en la sesión o en un error tipado de inicio para que consola/Pygame muestren solo
veredicto y motivo. `--verificar` llama al modelo y al formateador directamente, sin
crear una instancia de vista. Los errores de datos no son forzables; NO RESOLUBLE y NO
VERIFICABLE sí pueden continuarse con `--forzar`.

`controlador/controlador_replay.py` ya llama a `nueva_partida()`: debe pasar una opción
explícita de no verificar (FR-023). La vía de `--bench` continúa separada de `nueva_partida`
y sin vista. `--verificar` se rechaza con `--replay` o `--bench` antes de consultar;
`--forzar` se ignora en modo verificar y también funciona con inicio GUI. El reporte y
resumen inicial usan el formato estable de `contracts/cli.md`. El código de salida queda
0/1/2 según el contrato CLI.

### Complejidad y medición

La orquestación añade una consulta lógica y el tiempo del verificador, sin solicitud
adicional de versión; HTTP cuenta los intentos reales de la nueva consulta. Pruebas
separadas cubren CLI, `nueva_partida()`, bypass replay, resumen seguro y todas las
combinaciones permitidas después de que spec las defina.

### Límites

La implementación debe propagar `--forzar` a la ruta GUI sin revelar ubicaciones. Las
combinaciones `--verificar`/`--replay` y `--verificar`/`--bench` se rechazan antes de
consultar; otras combinaciones de flags no establecidas por la enmienda no se presuponen.
La operación de inicio normal aún puede fallar en cargas requeridas por presupuesto
aunque el reporte de verificación permita continuar; no ocultar esa falla.

## D6. Benchmark (SC-001, SC-002, SC-004)

### Alternativas consideradas

**A. Añadir caso en `bench/casos/` y registrarlo en `bench/casos/__init__.py`**, usando
el `bench.runner` y `bench.medicion` existentes.

**B. Crear un ejecutable de benchmark aislado** que duplique medición, metadatos y guardado.

**C. Medir solo el verificador incremental**, sin variante de referencia ni equivalencia.

### Decisión

Elegir A. Un caso del menú estándar mantiene la semilla 42 del runner, commit, versión de
Python, sistema, CPU, medianas/p95/máximo, repeticiones y JSON de evidencia. El generador
de criptas se fija por semilla y se mantiene bajo `bench`; no introduce topología de
cripta real en producción. Antes de medir, comparar A y B con el mismo input y verificar
veredicto, orden y frontera. Medir A/B para la comparación algorítmica y A end-to-end
para SC-001, incluyendo los diagnósticos necesarios pero sin red, carga ni renderizado.

Usar al menos tres tamaños con duplicación de salas, salidas y llaves encadenadas. El
caso de resolubilidad se ejecuta en `--bench` con y sin `--salida`. Se proponen 20
repeticiones (la tabla imprime p95 desde 20; el requisito mínimo es cinco).
Incluir la mayor cripta publicada disponible cuando exista y documentar el máximo. Las
mediciones se ejecutan en un commit limpio y guardan el hash y entorno.

### Complejidad y medición

Por cada tamaño: equivalencia antes del tiempo; mediana, p95, máximo, muestras y n.
Registrar razón de p95 entre tamaños consecutivos y el resultado frente a los umbrales
SC-001/004. La repetición de B es intencionalmente costosa y solo para comparación.

### Límites

`bench.medicion` oculta p95 en pantalla con menos de 20 repeticiones, aunque lo guarda en
JSON; por eso se prefieren 20. `main.py --bench --salida` desvía actualmente al reporte
especializado de terreno y no ejecuta `CASOS`; la implementación debe ejecutar también
el caso de resolubilidad y conservar el reporte indicado por `--salida`. No se ha medido
ningún umbral durante esta fase documental.

## Hallazgos de investigación

- La entrada de `CriptaModelo` mantiene salas ordenadas y `sala_por_id()` es O(log S);
  no usarlo como índice de cada salida. La carga ya deja `Salida.sala_destino` enlazada.
- El constructor del esqueleto valida sala inicial y de salida; mantener esos errores
  como datos no forzables.
- El inicio de consola y GUI usan `nueva_partida()`, y replay también la reutiliza; el
  bypass de replay es obligatorio.
- `DatosHTTP._get()` cuenta cada intento con presupuesto y aplica timeout; estados no
  exitosos y problemas de red se convierten en `RuntimeError`, JSON inválido en
  `ValueError`.
- La interfaz de fuente no tiene método de llaves; `DatosOffline` no tiene el archivo;
  el descargador obtiene generales, salas, contenido y catálogo, pero no llaves.
- `bench.runner` registra casos desde `bench.casos.CASOS`, guarda metadatos y JSON;
  `bench.medicion` tiene p95/máximo y calentamiento fuera de tiempo. `mensajes.py`
  compara resultados antes de medir.
- Los hallazgos del plan están resueltos en la sesión de enmienda post-plan de
  [spec.md](./spec.md); su estado y trazabilidad se resumen en [plan.md](./plan.md).
