# Revisión de persistencia — rama base/sebastian

Fecha: 2026-11-05 · Commit: 4333261 +sin commit

---

## Nota previa: `guardado.py` no existe

El usuario mencionó `persistencia/guardado.py`; ese archivo no existe en la rama.
El guardado de la partida está distribuido entre:

| Archivo | Responsabilidad |
|---|---|
| `persistencia/PartidaBinaria.py` | Formato binario con índice por sala |
| `persistencia/estado_partida.py` | Codec del grafo de objetos (codificar/decodificar) |
| `persistencia/esqueleto.py` | Estructura estática de la cripta (formato JSON, `formato:1`) |
| `persistencia/cache_json.py` | Formato común de caché para catálogo y contenido |
| `persistencia/version.py` | Versión local vs. versión del servicio HTTP |
| `persistencia/catalogo.py` | Fichas del catálogo tipo por tipo |
| `persistencia/contenido.py` | Contenido por sala (enemigos, objetos, trampas) |

El término "esquema 2" no aparece en el código; probablemente refiere al
formato `PartidaBinaria` (segunda generación tras el caché JSON).

---

## 1. Qué guarda el formato binario y cómo detecta la versión

### Detección de versión

`PartidaBinaria` usa dos verificaciones al abrir un archivo:

1. **Magic bytes** — 4 bytes `0x43525054` ("CRPT"). Si no coinciden → error.
2. **`VERSION_FORMATO`** — 2 bytes. Valor actual: `1`. Si difiere → error.

Los archivos de caché JSON usan un esquema diferente:
`{"formato_cache": 1, "version": "<hash del servidor>", "identificador": "..."}`.
Si cualquiera de los tres campos no coincide, la caché se descarta y se
solicita al servidor.

### Estructura del archivo binario

```
[encabezado] 12 bytes  magic(4) + VERSION_FORMATO(2) + num_salas(2) + inicio_datos(4)
[índice]     n × 8     sala_id(4) + offset(4) por sala, ordenado por sala_id
[global]     4 + n     longitud(4) + JSON del estado global
[salas]      por sala: sala_id(4) + longitud(4) + JSON de la sala
```

### Qué contiene el estado global

`codificar(partida)` en `estado_partida.py` recorre el grafo completo de objetos
desde `Partida` y los serializa por referencia (evita duplicar objetos compartidos):

| Componente | Qué incluye |
|---|---|
| `Partida` | Todos sus atributos, excepto los callbacks de `OMITIDOS_PARTIDA` |
| `Reloj` | `tiempo_actual`, `agenda` (HeapMinimo completo), estado del PRNG (`random.Random.getstate()`) |
| `Historial` | Pila de hasta 5 `GrupoDeltas` con todos sus objetos delta |
| `Jugador` | Stats (vida, ataque, defensa), inventario (ListaDoble de ítems), sala actual, cursor |
| `Enemigo`, `Trampa` | Todos sus atributos |
| Ítems | `Arma`, `Armadura`, `Pocion`, `Antorcha`, `Antidoto`, `Llave`, `PergaminoRetroceso` |
| `ListaLRU` | Estado completo, incluyendo `TablaHash` desde el commit 4333261 |
| Todas las TDAs | `Vector`, `ListaDoble`, `ListaSimple`, `HeapMinimo`, `Pila`, `Cola`, `ArrayOrdenado`, `TablaHash` |
| `random.Random` | Estado completo del PRNG vía `getstate()` |

**Excluidos** (`OMITIDOS_PARTIDA`): ocho atributos de `Partida` que son
callbacks/funciones (`al_mensaje`, `al_morir_enemigo`, `al_entrar_sala`,
`al_mover_enemigo`, `al_atacar`, `al_activar_trampa`, `_resolver_ficha`,
`aplicar_efecto`). Se reconstruyen en `decodificar()` como `Vector()` vacíos
o `None` según el prefijo.

---

## 2. Qué guarda el esqueleto

`PersistenciaEsqueleto.guardar_esqueleto()` produce un JSON con `formato: 1`:

| Campo | Incluido |
|---|---|
| `id`, `version` de la cripta | ✓ |
| `sala_inicial_id`, `sala_salida_id`, `llave_salida` | ✓ |
| `presupuesto_solicitudes`, `inventario_max` | ✓ |
| Por sala: `id`, `nombre` | ✓ |
| Por salida: `direccion`, `sala_destino_id`, `cerrada`, `llave`, `cierre_automatico` | ✓ |
| **`costo` de la salida** | **✗ — no existe en el modelo** |
| Contenido (enemigos, objetos, trampas) | ✗ — va en `contenido.py` |
| Niebla de guerra / salas conocidas | ✗ — no modelado |
| Historial de movimientos | ✗ — no modelado |

El esqueleto es una copia local de la topología del servidor, válida
mientras la `version` de la cripta no cambie.

---

## 3. Qué cambió en `estado_partida.py` con el commit 4333261

Una sola línea modificada:

```diff
-    'estructuras.cola', 'estructuras.listalru', 'estructuras.array_ordenado',
+    'estructuras.cola', 'estructuras.listalru', 'estructuras.tabla_hash',
+    'estructuras.array_ordenado',
```

**Qué implicaba antes del commit**: `codificar()` enumera los módulos de
`MODULOS` para construir la tabla de clases permitidas. `TablaHash` y
`_EntradaHash` no estaban en esa tabla; al intentar guardar una partida
con `ListaLRU(indice="hash")` el codec lanzaba:
`ValueError: No se puede guardar el tipo estructuras.tabla_hash.TablaHash`.

**Qué implica después**: `TablaHash` y sus nodos `_EntradaHash` pueden
ser serializados y restaurados. El índice hash de la caché LRU se guarda
y reconstruye íntegramente; no hace falta `_reconstruir_indice()` al
cargar porque el índice viene en el archivo.

---

## 4. `GrupoDeltas` y la pila del pergamino

### Flujo de una acción

```
iniciar_accion(reloj)
  → crea GrupoDeltas
  → registra DeltaReloj (captura tiempo, secuencia, estado PRNG)

registrar(delta)        ← se llama por cada cambio atómico
  → GrupoDeltas._deltas.agregarValor(delta)

confirmar_accion()
  → Pila.apilar_elemento(grupo)
  → si len > 5: descarta el fondo (el MÁS ANTIGUO), no el nuevo
```

### Reversión

`revertir()` / `usar_pergamino()`:

```
Historial.revertir()
  → grupo = Pila.ver_tope()
  → grupo.revertir_todo()
        while len(deltas) > 0:
            deltas[-1].revertir()       ← orden INVERSO al de registro
            deltas.eliminarUltimo()     ← el delta SE CONSUME
  → Pila.desapilar_elemento()          ← el grupo SE ELIMINA
```

**Sí: los deltas se consumen al revertir.** Tras `revertir_todo()` el
`Vector` queda vacío y el `GrupoDeltas` es desapilado. No es posible
"revertir una reversión".

### Por qué se limita a 5

| Razón | Detalle |
|---|---|
| Mecánica del juego | El pergamino de retroceso retrocede exactamente una acción por uso |
| Memoria acotada | Cada grupo guarda referencias a objetos del juego, no copias; aun así el volumen crece con la complejidad de cada turno |
| Implementación | `Pila(capacidad_maxima=5)` descarta el fondo automáticamente en O(1); no hay lógica extra |

### Los pergaminos son irreversibles

`DeltaListaSimple` y `DeltaObjeto` tienen `excluido = True` cuando el
objeto es `pergamino_retroceso`. Consumir un pergamino no se registra
como delta; no puede deshacerse.

---

## 5. Por qué `carga_total binario` tarda ~72 ms vs ~11 ms de JSON

### Perfil cProfile (10 × cargar_todo, 5 000 salas)

```
ncalls   tottime  cumtime  función
     10    0.080    1.588  PartidaBinaria.cargar_todo
  50010    0.106    1.314  PartidaBinaria._leer_json
  50020    0.559    0.559  nt.fstat          ← 35% del tiempo total
  50010    0.091    0.562  json.loads
  50010    0.090    0.316  json.decoder.decode
 100050    0.093    0.154  PartidaBinaria._leer
  50010    0.067    0.102  json.detect_encoding
```

### Causas identificadas

| Causa | Detalle | Coste medido |
|---|---|---|
| `os.fstat()` por bloque | `_leer_json` llama `os.fstat(f.fileno()).st_size` como cota de seguridad **antes de cada lectura**. Con 5 001 bloques por carga = 5 001 syscalls | 35 % del tiempo total |
| 5 001 llamadas a `json.loads` | Cada sala es un parse independiente. JSON lo hace en un único paso sobre todo el archivo | ≈ 35 % |
| `detect_encoding` por bloque | `f.read(longitud)` devuelve `bytes`; `json.loads(bytes)` detecta BOM/codificación en cada llamada | ≈ 6 % |
| Lectura fragmentada | `_leer()` lee 4 bytes por llamada con `int.from_bytes`; 100 050 lecturas diminutas mantienen el puntero del buffer activo | ≈ 10 % |

### Por qué ocupa casi lo mismo que el JSON

El formato binario almacena cada sala como **texto JSON**, no como datos
binarios compactos. El "binario" solo es el encabezado y el índice:

```
Overhead del índice y cabeceras: 80 012 bytes  (6,7 % del archivo)
Contenido JSON real:          1 106 387 bytes (93,3 %)
Total binario:                1 186 399 bytes

JSON equivalente:             1 195 115 bytes
```

Los ≈ 8 700 bytes de diferencia (binario más pequeño) se explican porque en
el archivo JSON los IDs de sala son claves de texto `"1234"`; en el binario
son enteros de 4 bytes en la cabecera del bloque, fuera del JSON.

---

## 6. Tabla de estado: hoy vs. Parte II

| Elemento | Guarda hoy | Faltará para la Parte II | No reutilizable para historia permanente |
|---|---|---|---|
| Topología de la cripta | Sí (esqueleto: salas, salidas, cerrojos, cierre automático) | **Costos de salida** (campo `costo` no existe en el modelo ni en el esqueleto) | — |
| Estado del jugador | Sí (vida, stats, inventario, sala actual) | — | Los stats se reinician en cada partida; no acumulan entre partidas |
| Niebla de guerra / salas visitadas | No | Mapa de salas conocidas por el jugador (booleano o timestamp por sala) | No hay estructura ni campo para esto |
| Estado de enemigos/trampas | Sí (vivos/muertos, armadas/desarmadas) | — | Se reinicializa al empezar partida nueva |
| Historial de retroceso | Sí (5 GrupoDeltas, efímero) | — | Efímero por diseño; no sirve para registrar la historia de partidas pasadas |
| Historia completa de movimientos | No | Log de acciones del jugador (sala×turno×acción) para estadísticas y replay | Requeriría una estructura de log separada, no el sistema de deltas |
| Caché LRU (fichas en memoria) | Sí (ListaLRU + TablaHash desde 4333261) | — | Específica de la sesión; no tiene sentido persistir entre partidas distintas |
| Puntajes | Sí (en `puntajes.json`, separado) | Clasificación por cripta, versión y jugador (ya implementado en `puntajes.py`) | — |
| PRNG (semilla y estado) | Sí (random.Random.getstate()) | — | No reutilizable: cada partida nueva necesita semilla nueva |

### Resumen de brechas para la Parte II

1. **Costos de salida**: ni el modelo (`Salida`), ni el esqueleto, ni el
   codec los incluyen. Habría que agregar el campo al modelo, al esqueleto
   y al codec `codificar/decodificar`.

2. **Conocimiento de niebla**: no hay campo `visitada` ni estructura de
   "salas conocidas". Requeriría al menos un `Vector` o `TablaHash` de IDs
   de sala visitados, persistido en el estado global.

3. **Historia permanente**: el `Historial` es de retroceso en memoria, no
   un log. Para una historia de partidas (estadísticas acumuladas, replay
   completo) habría que registrar las acciones en un append-only log
   separado (p. ej. `bitácora.log`) y no en el sistema de deltas.

---

## 7. Mejoras posibles al formato binario (sin implementar)

| Mejora | Ahorro esperado | Complejidad |
|---|---|---|
| Leer tamaño del archivo una sola vez al abrir y pasarlo como argumento a `_leer_json` | Elimina 5 001 syscalls `fstat` por carga (≈ 35 % del tiempo) | Baja |
| Leer todo el archivo en memoria (`BytesIO`) y parsear desde allí | Elimina la fragmentación de lecturas y los `fstat` a la vez | Baja |
| Decodificar el `bytes` leído a `str` antes de pasarlo a `json.loads` | Evita 5 001 llamadas a `detect_encoding` | Muy baja |
| Usar formato binario real para campos simples (enteros, strings cortos) en lugar de JSON por sala | Reduce tamaño en 30-50 % y acelera el parse | Alta |
| Comprimir el archivo con `zlib` | El texto JSON comprime ≈ 60-70 %; el archivo pasaría de ~1,2 MB a ~400 KB | Media |
| Cargar el estado global por separado de las salas (ya disponible con `cargar_global()`) | Para el caso de uso habitual solo se necesita el estado global al iniciar | — (ya implementado) |

---

## 8. El PRNG del juego se guarda completamente

**Pregunta:** ¿`codificar()` guarda el estado interno del `random.Random`?

**Sí, de dos maneras independientes.**

### En la serialización completa (`codificar`)

`estado_partida.py` trata `random.Random` como un tipo especial:

```python
# codificar — estado_partida.py:75-76
elif type(objeto) is random.Random:
    tipo, datos = 'azar', valor(objeto.getstate(), grupo)

# decodificar — estado_partida.py:128-129
elif tipo == 'azar':
    objeto.setstate(valor(datos))
```

`getstate()` captura el estado interno completo del Mersenne Twister
(versión, vector de 624 enteros y posición del índice). Al cargar,
`setstate()` lo restaura bit a bit. Re-simular desde ese checkpoint produce
exactamente la misma secuencia de números.

### En cada `DeltaReloj` (historial de retroceso)

`modelo/deltas.py:DeltaReloj.__init__` también captura:

```python
self.estado_azar = reloj.azar.getstate()
```

y lo restaura en `revertir()`. Así, retroceder una acción devuelve el PRNG
al estado exacto de antes de esa decisión — sin eso, los dados del retroceso
darían resultados diferentes.

---

## 9. Los deltas guardan solo el valor anterior, no el nuevo

**Pregunta:** ¿Cada delta guarda solo el valor anterior, o también el nuevo?

**Solo el anterior.** Revisando cada clase en `modelo/deltas.py`:

| Clase delta | Qué captura | ¿Guarda el nuevo valor? |
|---|---|---|
| `DeltaAtributos` | `getattr(objeto, campo)` antes del cambio | No |
| `DeltaVida`, `DeltaPuerta`, `DeltaTrampa`, `DeltaRastro`, `DeltaVelocidad` | Subclases de `DeltaAtributos` | No |
| `DeltaReloj` | `tiempo`, `secuencia`, `estado_azar` previos | No |
| `DeltaEvento` | `self.anterior = getattr(dueno, campo)` antes del cambio | No |
| `DeltaActivacion` | `tuple(sala.enemigos_dormidos)` y `len(activos)` previos | No |
| `DeltaListaSimple` | `self.indice` previo en la lista | No |
| `DeltaRetiro` | `self.indice` donde estaba | No |
| `DeltaAgregadoAlFinal` | `self.nodo`, `self.anterior` (punteros previos) | No |
| `DeltaObjeto` | Nodo, cursor, `DeltaAtributos` de equipo previos | No |

Ningún delta almacena el valor posterior. Esto tiene dos consecuencias:

- **Revertir (←) funciona directamente**: `revertir()` restaura el `anterior`
  guardado.
- **Reproducir hacia adelante (→) es imposible con los datos actuales**: para
  "re-aplicar" una acción habría que ejecutarla de nuevo, no hay valor nuevo
  almacenado que aplicar. Los deltas no sirven como log reproducible.

---

## 10. Implicaciones para la línea de tiempo

### La caché LRU y el historial del pergamino no deben entrar en un checkpoint

Un checkpoint representa el estado lógico del juego en un instante. La
`ListaLRU` es una optimización de acceso (qué fichas están cargadas en
memoria); su contenido depende del orden de operaciones desde el arranque,
no de la partida en sí. Incluirla en el checkpoint:

- Infla el archivo con datos recuperables desde disco/servidor.
- Reproduce un estado de caché que no tiene por qué coincidir con el momento
  de retomar la partida (fichas desalojadas mientras la partida estaba
  cerrada ya no estarán "calientes").

El historial del pergamino (`Historial` con sus 5 `GrupoDeltas`) es estado
efímero de retroceso: depende de acciones ocurridas *desde* el checkpoint,
no *en* él. Un checkpoint limpio debería guardarse con el historial vacío
(o excluirlo del codec), de modo que al retomar la partida no haya
"retrocesos heredados" de antes del guardado.

### El historial actual no sirve como registro permanente (B08)

El `Historial` tiene tres limitaciones estructurales que lo hacen inadecuado
como registro de historia permanente:

1. **Solo 5 pasos**: la `Pila(capacidad_maxima=5)` descarta el más antiguo
   en cuanto llega el sexto. No puede crecer ilimitadamente.

2. **Solo hacia atrás**: los deltas guardan únicamente el valor anterior
   (sección 9). No es posible reproducir la partida hacia adelante desde
   el delta; habría que re-ejecutar cada acción.

3. **Sin semántica de "qué pasó"**: cada `GrupoDeltas` es un conjunto de
   cambios de bajo nivel (atributos, posiciones en listas). No hay campo
   "acción: moverse_norte" ni "resultado: enemigo_muerto". Reconstruir la
   narrativa de la partida desde los deltas sería extremadamente complejo.

Para B08 (registro permanente) se necesitaría un **log de comandos** separado:
una estructura append-only con entrada `{turno, sala_origen, acción, resultado}`
persistida independientemente del estado del juego.

### La carga binaria (~72 ms con 5 000 salas) pone en riesgo el límite de 50 ms

Si la historia requiere cargar checkpoints frecuentemente (p. ej. al navegar
la línea de tiempo), el tiempo de carga actual es un problema:

| Escenario | Tiempo medido | Margen |
|---|---|---|
| `carga_total binario` 5 000 salas | ~72–107 ms (mediana/máx del bench) | **Por encima del límite de 50 ms** |
| `carga_total json` 5 000 salas | ~12–23 ms | Dentro del límite |
| `carga_1_sala binario` (acceso directo por índice) | ~0,1–0,2 ms | Sin problema |

La causa principal ya está identificada: 5 001 syscalls `fstat` por carga
(sección 5). La mejora de baja complejidad —leer todo el archivo en un
`BytesIO` y parsear desde memoria— eliminaría esa causa y reduciría
el tiempo estimado a 15–25 ms, dentro del límite. Sin esa mejora, el
checkpoint de 5 000 salas no puede cumplir el límite de 50 ms con el
formato binario actual.
