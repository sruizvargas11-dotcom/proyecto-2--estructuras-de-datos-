# Modelo de datos: Terreno y cazador

Este documento describe los datos y transiciones que la implementación deberá integrar
en el modelo MVC existente. No introduce valores concretos de una cripta.

## Entidades

### Salida

| Campo | Tipo | Origen | Regla |
|---|---|---|---|
| `direccion` | dirección existente | esqueleto de cripta | Una salida por dirección según el contrato actual. |
| `sala_destino_id` | entero | esqueleto de cripta | Debe apuntar a una sala existente. |
| `costo` | entero positivo efectivo | `costo` opcional del esqueleto | Ausente → 100. Presente con `null`, booleano, valor no entero o <1 → rechazo. |
| `cerrada` | booleano mutable | esqueleto/eventos de puerta | Se evalúa en el estado actual; las salidas cerradas no forman parte de rutas. |

El costo se valida antes de comenzar la partida. No muta al abrir o cerrar una puerta.
La acción de movimiento que atraviesa una salida usa dicho costo como costo base y
programa el evento con `max(1, costo * 100 // velocidad)`.

### Conexión representada en dos sentidos

Los registros de salida son los datos de entrada; una conexión física tiene dos
representaciones dirigidas cuando ambas existen. Se normaliza cada costo efectivo y se
acepta solamente si ambos coinciden. El error de desacuerdo identifica los IDs de las salas
y ambos costos efectivos.

| Representación A | Representación B | Resultado |
|---|---|---|
| arista presente, `costo` omitido | arista presente, `costo` omitido | Ambos efectivos 100; aceptar |
| arista presente, `costo` omitido | arista presente, `costo` 100 | Ambos efectivos 100; aceptar |
| arista presente, `costo` omitido | arista presente, costo positivo distinto de 100 | Rechazar |
| dos aristas presentes con costos positivos diferentes | — | Rechazar |
| cualquier arista con costo presente `null` o inválido | — | Rechazar |

Si solo existe una de las salidas, se acepta como unidireccional (AB-28; FR-001); la
validación no exige reciprocidad.

### Ficha de enemigo

| Campo | Tipo | Origen | Regla |
|---|---|---|---|
| `comportamiento` | texto | catálogo | Admite `cazador` como cuarto comportamiento; se conservan los tres existentes. |
| `rango` | entero ≥1 | catálogo | Obligatorio para cazador; está expresado en unidades de costo y no limita ataques en la misma sala. |

La identidad, atributos, instancias, vida y demás propiedades conservan los contratos del
catálogo y contenido actuales. Los datos incompatibles entre versiones se rechazan antes
de iniciar la partida.

### Estado de búsqueda y decisión

| Dato | Contenido | Ciclo de vida |
|---|---|---|
| Distancia a jugador | costo mínimo acumulado o “sin ruta” por sala | Se calcula sobre salidas abiertas del snapshot actual. |
| Cola de búsqueda | frontera de salas priorizada por distancia | Local a cada cálculo; prioridad determinista por costo y sala. |
| Versión de puertas | revisión monotónica de estado abierto/cerrado | Cambia con toda transición de puerta que afecte rutas. |
| Snapshot compartido | sala del jugador + revisión de puertas + distancias | Reutilizable solo mientras ambos componentes sigan iguales. |
| Decisión | atacar, esperar o mover; sala destino; costo de acción | Vuelve a evaluarse en cada turno de cazador. |

La modalidad compartida calcula una sola tabla de distancias al jugador sobre aristas
entrantes; la individual usa una búsqueda nueva por cazador. Ambas son comparables y deben
producir la misma acción observable. Un actor no bloquea la sala destino. El movimiento
avanza una salida y termina; si llega a la sala del jugador no ataca en ese mismo evento.

## Validación de secuencia

1. Leer y validar el esqueleto, incluyendo existencia de salas destino.
2. Normalizar el costo ausente a 100; rechazar inválidos y comparar costos efectivos de
   los sentidos representados.
3. Resolver fichas de catálogo y validar comportamiento/rango junto con las versiones
   correspondientes.
4. Publicar modelo y contenido solo si la validación anterior termina correctamente.
5. Iniciar el reloj. Los fallos no deben crear una partida parcialmente válida ni exceder
   `presupuesto_solicitudes`.

Una salida inversa ausente es válida como conexión unidireccional. El benchmark usa un mapa
fijo/versionado mayor que el mapa offline disponible, y debe registrar identidad, versión y
dimensiones (AB-29; FR-011).

### Fixture del benchmark

| Atributo | Valor |
|---|---|
| Identidad | `bench-terreno-cazador-grid-16x16` |
| Versión | `1.0.0` |
| Dimensiones | 16 filas × 16 columnas; 256 salas, IDs 1–256 en orden por filas |
| Topología | Grilla ortogonal; 240 aristas horizontales y 240 verticales, cada una representada en ambos sentidos (480 conexiones, 960 salidas) |
| Costos | Deterministas y simétricos; para extremos `u < v`, `1 + ((7*u + 11*v) mod 100)` |
| Puertas | Ocho aristas designadas en el contrato; todas abiertas inicialmente, se alterna una por cambio en orden fijo |
| Escala base | La cripta offline disponible, `cripta-01`, tiene 6 salas; el fixture tiene 256 |

Este fixture es dato exclusivo de medición, no una cripta oficial ni una constante de la
lógica de producción. La definición completa y la secuencia de estados está en
[el contrato de benchmark](./contracts/datos-entrada-y-benchmark.md).

## Matriz de trazabilidad FR–AB

Esta matriz enlaza los requisitos con los escenarios del Apéndice B. Las pruebas creadas
en la fase de implementación deberán citar explícitamente cada ID AB y FR.

| Requisito | Escenarios de aceptación |
|---|---|
| FR-001 | AB-01, AB-11, AB-22, AB-24, AB-25, AB-26, AB-27, AB-28 |
| FR-002 | AB-02 |
| FR-003 | AB-03, AB-14 |
| FR-004 | AB-04, AB-17, AB-23 |
| FR-005 | AB-05, AB-06, AB-09 |
| FR-006 | AB-07 |
| FR-007 | AB-08 |
| FR-008 | AB-07, AB-09, AB-10, AB-17, AB-18 |
| FR-009 | AB-15 |
| FR-010 | AB-11, AB-12, AB-22 |
| FR-011 | AB-13, AB-29 |
| FR-012 | AB-16 |
| FR-013 | AB-19, AB-20, AB-21, AB-24, AB-25, AB-27 |

**Revisión requerida**: todos los FR-001–FR-013 aparecen en al menos un escenario y cada
AB-01–AB-29 aparece en la tabla de especificación con uno o más FR.
