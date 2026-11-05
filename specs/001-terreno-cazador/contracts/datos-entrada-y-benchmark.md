# Contrato de datos y benchmark

Este contrato documenta los límites externos que requiere la capacidad. Los campos nuevos
son parte de los datos de entrada; no se embeben en el código valores para una cripta.

## Esqueleto de cripta

Se conserva el formato actual por sala y salida. Cada salida mantiene su dirección, sala
destino y atributos de puerta; `costo` es opcional:

| Entrada de `costo` | Costo efectivo / resultado |
|---|---|
| Campo ausente | 100 |
| Entero JSON ≥1 | El valor declarado |
| `null`, booleano, otro tipo o entero <1 | Rechazar la cripta antes de iniciar |

Las dos representaciones de una conexión se comparan después del default. Si sus costos
efectivos difieren, se rechaza la cripta y el error identifica ambos extremos y valores.
Si solo existe una salida, se acepta como unidireccional y no se exige reciprocidad.

## Catálogo

Una ficha de clase enemigo puede usar `comportamiento: "cazador"`. En ese caso debe
proporcionar `rango` como entero JSON ≥1. `null`, ausencia, booleano, otros tipos, cero o
negativos son inválidos. La versión de catálogo se valida con el mecanismo vigente del
repositorio, sin asumir que su cadena debe ser idéntica a la versión de cripta.

Las fuentes HTTP y offline deben entregar los campos en la versión correspondiente. Si
están ausentes o la versión no es compatible, la cripta no inicia y el error se reporta
explícitamente. No se debe añadir un cazador artificial a los datos de producción.

## Comportamiento observable

- El costo efectivo aparece en las salidas de consola y Pygame, también en las cerradas;
  el estado cerrado permanece inequívoco.
- Ambas presentaciones distinguen cazador de otros enemigos sin trasladar la decisión de
  ruta a la vista.
- `--bench` se ejecuta localmente, sin red ni instancias de vista/Pygame. `--replay`
  mantiene su separación existente.
- Cada movimiento transporta el costo de la salida cruzada; las demás acciones conservan
  sus costos actuales.

## Contrato de `--bench`

### Dataset fijo

No hay un dataset de cripta versionado en el repositorio que satisfaga el tamaño requerido:
`datos_offline/cripta-01` es versión `fd58f7743b9e` y contiene 6 salas. Se elige, por tanto,
un fixture sintético de benchmark:

- **Identidad**: `bench-terreno-cazador-grid-16x16`
- **Versión del fixture**: `1.0.0`
- **Dimensiones**: 16 × 16, 256 salas identificadas por fila, de 1 a 256.
- **Topología**: cada sala conecta con sus vecinas ortogonales dentro de la grilla. Hay 240
  pares horizontales y 240 verticales: 480 conexiones bidireccionales, 960 salidas dirigidas.
- **Costo**: para cada par de extremos `u < v`, ambos sentidos reciben
  `1 + ((7*u + 11*v) mod 100)`. No hay datos de cripta real ni selección aleatoria de
  topología o costos.
- **Puertas variables**: ocho conexiones del fixture se identifican como puertas:
  D1 `(4,4)-(4,5)`, D2 `(4,12)-(5,12)`, D3 `(8,8)-(8,9)`, D4 `(12,4)-(13,4)`,
  D5 `(12,12)-(12,13)`, D6 `(2,8)-(3,8)`, D7 `(8,2)-(8,3)`, D8 `(15,8)-(16,8)`.
  Las coordenadas son `(fila,columna)`, iniciadas en 1. Las ocho están abiertas en el
  estado inicial; las demás conexiones permanecen siempre abiertas.
- **Secuencia de cambios**: numerar ciclos de eventos entre decisiones del jugador desde 1.
  En el escenario frecuente, alternar una puerta al inicio de cada ciclo; en el infrecuente,
  alternar una al inicio de cada ciclo múltiplo de 100. Elegir D1…D8 en orden circular,
  reiniciando en D1 tras D8. Solo cambia el estado abierto/cerrado; topología y costos no
  cambian.
- **Estado de actores**: sala del jugador 136; los cazadores `cazador-01`…`cazador-20`
  ocupan, en ese orden, las salas 118–125, 134–135 y 137–146 (no se bloquean entre sí).
  Los diez primeros usan el primer rango del perfil y los diez restantes el segundo. Todos
  los valores siguientes son fijos en todos los escenarios:

  | Actor/campo | Valor |
  |---|---:|
  | Jugador `vida_max` y `vida` inicial | 1 000 000 000 |
  | Jugador `ataque` | 10 |
  | Jugador `defensa` | 5 |
  | Jugador `velocidad` | 100 |
  | Jugador `inventario_max` | 10; inventario vacío |
  | Cazador `vida_max` y `vida` inicial | 100 |
  | Cazador `ataque` | 1 |
  | Cazador `defensa` | 0 |
  | Cazador `velocidad` | 100 |
  | Cazador `comportamiento` | `cazador` |
  | Cazador `rango` | El valor del perfil asignado según el orden de instancia |
  | Cazador `regeneracion` | 0 |
  | Cazador `suelta` | Lista vacía |

  Todos comienzan vivos, sin objetos ni efectos activos o pendientes que alteren sus
  atributos. El jugador no cambia inventario ni recibe efectos durante la secuencia de
  benchmark. Los IDs de
  instancias son exactamente los indicados arriba y `tipo_id`/nombre son `bench-cazador` /
  `Cazador de benchmark`. La secuencia de acciones del jugador es `W` (esperar) en cada
  decisión; la semilla es 42.

El fixture pertenece a los datos de benchmark y debe residir fuera de los módulos de lógica
del juego. Su identidad/versionado se cambia solo cuando se cambia esta definición; debe
registrarse junto con dimensiones y checksum del archivo materializado si el fixture se
guarda como archivo.

### Archivo de evidencia

El benchmark acepta `--salida RUTA`, siguiendo la convención existente de exportar evidencia
JSON UTF-8 con indentación de dos espacios. Para la ejecución de referencia del proyecto se
conserva y versiona `docs/evidencia/2026-11-04-terreno-cazador-benchmark.json`; no es solo
un archivo temporal local. La explicación y las conclusiones de la medición se registran en
`docs/DECISIONES.md`.

El JSON contiene metadatos de ejecución (fecha, sistema operativo y versión, procesador,
número de núcleos, memoria instalada, entorno de ejecución y versión y perfil de energía),
identidad, versión, dimensiones y SHA-256 del fixture, semilla y estado inicial. Incluye una
lista de exactamente ocho escenarios y, en cada escenario, 30 repeticiones; cada repetición
registra exactamente 1000 duraciones de ciclo en nanosegundos, el máximo de esos ciclos y
una lista de discrepancias contra la referencia calculada desde cero. La lista de
discrepancias debe estar vacía para que el resultado sea válido; el reporte también se
conserva si hay discrepancias o ciclos que superan 20 ms, para que el fallo sea auditable.
Los tiempos de la referencia no forman parte de las duraciones cronometradas.

La estructura JSON usa estas claves de nivel superior: `benchmark`, `fecha`, `fixture`,
`equipo`, `semilla`, `estado_inicial`, `escenarios`, `cumple_umbral` y
`decisiones_correctas`. `fixture` contiene `identidad`, `version`, `sha256`, `filas`,
`columnas`, `salas` y `conexiones`; `equipo` contiene `sistema_operativo`, `procesador`,
`nucleos`, `memoria_bytes`, `entorno_ejecucion`, `version_entorno` y `perfil_energia`.
Cada elemento de `escenarios` contiene `perfil_rango`, `rangos`, `cambio_puerta_cada_ciclos`,
`modalidad` y `repeticiones`. Cada repetición contiene `numero`, `duraciones_ciclo_ns`
(exactamente 1000 enteros), `maximo_ciclo_ns` y `discrepancias`; cada discrepancia registra
el ciclo, el cazador y las decisiones esperada y observada. `cumple_umbral` solo es verdadero
si todos los máximos equivalen a ≤20 ms; `decisiones_correctas` solo es verdadero si todas
las listas de discrepancias están vacías.

### Escenarios y comparabilidad

Ejecutar ocho escenarios sobre exactamente el mismo fixture: rango pequeño (1 y 100) o
grande (1000 y 10000), diez cazadores por valor; cambios de puerta cada ciclo o cada 100
ciclos; cálculo individual o compartido. Ejecutar 30 repeticiones por escenario.
Mantener mapa/versión, estado de actores, semilla 42, secuencia `W` y condiciones del equipo
idénticos entre modalidades y repeticiones de un escenario; entre escenarios solo varían el
perfil de rangos y los dos factores de puerta/modalidad descritos. Registrar identidad,
versión, 16×16,
256 salas, 480 conexiones, estado inicial y secuencia de puertas, rangos, semilla, sistema,
CPU/núcleos, memoria, entorno de ejecución y perfil de energía.

Cada repetición se reinicia desde el mismo estado y procesa 1000 ciclos de eventos entre
decisiones consecutivas del jugador. Registrar la duración de cada ciclo y su máximo. Medir
solo la modalidad seleccionada en el escenario; contrastar cada decisión con la referencia
desde cero fuera del intervalo cronometrado, para que la validación no infle la latencia
reportada.

El tiempo medido corresponde al procesamiento del modelo/reloj entre decisiones del
jugador; excluir espera humana, red y renderizado. Registrar duración máxima del ciclo,
escenario, repetición y discrepancias. La modalidad individual recalculada sin caché sirve
como referencia para comparar cada decisión de la modalidad compartida. El resultado solo
respalda afirmaciones sobre la escala y topología del mapa registrado.
