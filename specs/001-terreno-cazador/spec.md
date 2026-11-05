# Feature Specification: Terreno y cazador

**Feature Branch**: `feature/spec-kit-copilot`

**Created**: 2026-11-04

**Status**: Draft

**Input**: Capacidad «Terreno y cazador»: costos de salidas, tiempos de movimiento y comportamiento de un nuevo enemigo cazador.

## Clarifications

### Session 2026-11-04

**Bloque 1**

- Q: ¿El rango del cazador solo determina hasta qué costo de ruta intenta perseguir al jugador, mientras que solo lo ataca cuando ambos están en la misma sala? → A: El rango solo limita la persecución; el cazador solo ataca cuando comparte sala con el jugador.

### Session 2026-11-04

**Bloque 2**

- Q: ¿Los actores que ya están en una sala impiden que el cazador entre en ella o la atraviese? → A: Los actores no bloquean la entrada ni el paso; el cazador puede compartir sala con ellos.
- Q: ¿Qué debe ocurrir si un costo declarado o el rango del cazador falta, es inválido o pertenece a una versión incompatible? → A: Rechazar los datos incompatibles con un error claro y no iniciar esa cripta; la ausencia de costo en una salida sigue usando el valor predeterminado 100.
- Q: ¿En qué vistas deben mostrarse los costos efectivos y deben aparecer también junto a salidas cerradas? → A: Mostrar los costos efectivos en consola y Pygame, incluso para salidas cerradas, indicando claramente que están cerradas.
- Q: ¿Qué protocolo fijo debe usar la medición para comprobar de forma reproducible el límite de 20 ms con 20 cazadores? → A: Usar la misma cripta y semilla y ejecutar 30 repeticiones para cada uno de ocho escenarios que combinan dos grupos de rango (≤100 y ≥1000), dos frecuencias de cambio de puerta (una puerta en cada ciclo de eventos entre decisiones del jugador o cada 100 de esos ciclos) y cálculos individuales o compartidos; registrar los rangos concretos, validar cada decisión contra un recálculo desde cero y exigir que ningún ciclo supere 20 ms.
- Q: ¿Qué valores enteros deben admitirse para el rango del cazador? → A: El rango debe ser al menos 1; cero y los negativos se rechazan.

### Session 2026-11-04

**Bloque 3**

- Q: Si el cazador entra a la sala del jugador al completar un movimiento, ¿ataca inmediatamente o espera a su siguiente turno programado? → A: Espera a su siguiente turno programado para atacar.
- Q: ¿Qué protocolo permite comparar los ocho escenarios de rendimiento de forma justa y repetible? → A: Mantener iguales la cripta y versión, semilla, estado inicial, secuencia de acciones del jugador y equipo; fijar antes de medir los valores de rango 1 y 100 para el perfil pequeño y 1000 y 10000 para el grande, mantener la misma composición de rangos en cada escenario y sus 30 repeticiones, y registrar las condiciones del equipo y el entorno de ejecución.
- Q: ¿Cómo se deben repartir los 20 cazadores entre los dos valores de rango de cada perfil en cada escenario? → A: Diez cazadores con cada valor del perfil.
- Q: Si una salida no declara el campo costo, pero otra lo declara explícitamente como null, ¿debe tratarse el null como inválido? → A: La ausencia del campo usa costo 100; un campo costo presente con valor null se rechaza antes de iniciar la cripta.
- Q: Si los datos asignan costos distintos a los dos sentidos de una misma conexión, ¿qué debe ocurrir al validar la cripta? → A: Rechazar la cripta antes de iniciar e informar la conexión con costos distintos.

### Session 2026-11-04

**Bloque 4**

- Q: ¿Cómo se valida una conexión cuyos dos sentidos se representan por separado? → A: Si existen ambas salidas, se comparan los costos efectivos después de asignar 100 a todo sentido sin campo `costo`; se acepta la conexión solo si ambos costos efectivos coinciden. El error por conflicto identifica la conexión y los dos costos efectivos. Un `costo` presente con valor `null` sigue siendo inválido.

### Session 2026-11-04

**Bloque 5**

- Q: Si existe una salida de una sala a otra, pero no hay una salida inversa correspondiente, ¿se acepta como conexión unidireccional o se rechaza la cripta por falta de reciprocidad? → A: Se acepta como conexión unidireccional; solo se comparan los costos efectivos cuando existen ambas salidas.

### Session 2026-11-04

**Bloque 6**

- Q: ¿Qué escala de mapa debe cubrir el objetivo de rendimiento de 20 ms: la cripta offline disponible o un mapa de benchmark fijo y versionado de mayor tamaño? → A: Usar un mapa de benchmark fijo y versionado de mayor tamaño que la cripta offline disponible; registrar su identidad, versión y dimensiones, sin fijar aquí un tamaño concreto.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Atravesar salidas con costos distintos (Priority: P1)

Como jugador o actor de la partida, necesito que el tiempo de movimiento refleje el costo de
la salida recorrida para que atravesar terreno más costoso tarde más, sin cambiar las demás
acciones ni las reglas de movimiento existentes.

**Why this priority**: El costo del terreno y el tiempo de movimiento afectan a todos los actores.

**Independent Test**: Preparar salidas con costo declarado y omitido, y comprobar costo e
intervalo de movimiento para más de una velocidad.

**Acceptance Scenarios**:

1. **Given** una conexión cuyos dos sentidos omiten el costo, **When** se valida y un actor
   atraviesa cualquiera de ellos, **Then** se acepta con costo base 100 en ambos sentidos
   (AB-01; FR-001).
2. **Given** salidas de costo 1 y de costo mayor, **When** actores las atraviesan, **Then**
   cada movimiento usa el costo de la salida y el intervalo establecido (AB-02; FR-002).
3. **Given** un actor que atraviesa una salida costosa, **When** su velocidad cambia,
   **Then** el tiempo restante se ajusta según P1 §2.3 (AB-03; FR-003).

### User Story 2 - Resolver el movimiento de un cazador (Priority: P1)

Como jugador, necesito que el cazador intente alcanzarme por la ruta abierta de menor costo,
para que sus decisiones respeten el terreno, las puertas y su rango.

**Why this priority**: El comportamiento define cuándo el cazador ataca, espera o se acerca.

**Independent Test**: Colocar jugador y cazador en salas conocidas, variar salidas abiertas,
costos, rango y posiciones, y verificar la decisión de cada turno.

**Acceptance Scenarios**:

1. **Given** el cazador comparte sala con el jugador, **When** llega su turno, **Then**
   ataca (AB-04; FR-004).
2. **Given** no existe ruta abierta o la ruta de menor costo excede el rango, **When** llega
   su turno, **Then** espera con costo 100 (AB-05 y AB-06; FR-005).
3. **Given** hay rutas con distinto número de salas y la que usa menos salas cuesta más,
   **When** el cazador se mueve, **Then** elige la ruta de menor costo total (AB-07; FR-006).
4. **Given** dos vecinas inician rutas de costo mínimo equivalente, **When** el cazador se
   mueve, **Then** elige la vecina con menor id (AB-08; FR-007).
5. **Given** cambia una puerta, la posición del jugador o el estado de otros actores entre
   turnos, **When** el cazador decide de nuevo, **Then** su decisión corresponde al estado
   actual, como si se calculara desde cero (AB-09 y AB-10; FR-008).
6. **Given** hay 20 cazadores activos, **When** se mide un ciclo de eventos entre decisiones
   del jugador en el equipo local y sin red ni renderizado, **Then** dura como máximo 20 ms
   (AB-13; FR-011).
7. **Given** la niebla oculta una ruta abierta y hay una salida cerrada, **When** el cazador
   decide su movimiento, **Then** considera la ruta oculta y no atraviesa ni abre la salida
   cerrada (AB-15; FR-009).
8. **Given** datos de una cripta y una ficha de catálogo de versiones correspondientes,
   **When** se determina el costo de una salida y el rango de un cazador, **Then** se usan
   los valores procedentes de esas fuentes (AB-16; FR-012).
9. **Given** el cazador no comparte sala con el jugador y la ruta abierta está dentro de su
   rango, **When** llega su turno, **Then** avanza un paso y no lo ataca a distancia
   (AB-17; FR-004 y FR-008).
10. **Given** el cazador entra a la sala del jugador al completar un movimiento, **When**
    termina ese movimiento, **Then** no ataca inmediatamente y espera hasta su siguiente turno
    programado para atacar (AB-23; FR-004).

### User Story 3 - Reconocer el terreno y a los cazadores (Priority: P2)

Como jugador, necesito ver el costo de las salidas disponibles en mi sala y distinguir a los
cazadores de los demás enemigos para interpretar el terreno y anticipar sus acciones.

**Why this priority**: La información visible ayuda a comprender el costo de desplazarse y
reconocer la nueva amenaza.

**Independent Test**: Abrir una sala con salidas de distintos costos y con un cazador y otros
enemigos, y verificar la información que se muestra.

**Acceptance Scenarios**:

1. **Given** la sala actual tiene salidas abiertas y cerradas con costos distintos o sin
   costo declarado, **When** el jugador consulta la vista de consola o Pygame, **Then** se
   muestra el costo efectivo de cada salida y se indica cuáles están cerradas
   (AB-11 y AB-22; FR-010).
2. **Given** hay un cazador y otro enemigo, **When** se muestran en la vista, **Then** el
   cazador se distingue de los demás enemigos (AB-12; FR-010).

### Edge Cases

- Una salida de costo 1 y una velocidad alta producen un intervalo mínimo de 1, nunca 0
  (AB-02; FR-002).
- Si el costo mínimo de llegada es exactamente igual al rango, el cazador puede moverse;
  solo espera cuando el costo supera el rango (AB-06; FR-005).
- Una puerta cerrada no forma parte de una ruta válida, aunque conecte con el jugador
  (AB-05 y AB-09; FR-005 y FR-008).
- Los actores en una sala no impiden que el cazador entre ni la atraviese; pueden compartir
  sala (AB-18; FR-008).
- Si un sentido no declara `costo`, su costo efectivo es 100. Si solo existe una salida,
  se acepta como unidireccional; si existen ambas, sus costos efectivos deben coincidir
  (AB-01, AB-26 y AB-28; FR-001).
- Si ambos sentidos omiten `costo`, o uno lo omite y el otro declara 100, la conexión se acepta
  con costo efectivo 100 en ambos sentidos (AB-01 y AB-26; FR-001).
- Si un sentido omite `costo` y el otro declara un valor distinto de 100, o ambos sentidos
  declaran costos distintos, la cripta se rechaza antes de iniciar. El error identifica la
  conexión y los costos efectivos encontrados (AB-25 y AB-27; FR-001 y FR-013).
- Si el campo costo está presente con valor `null`, la cripta se rechaza antes de iniciar; solo
  la ausencia del campo activa el valor predeterminado 100 (AB-24; FR-013).
- Si un costo declarado no es un entero positivo, falta el rango obligatorio de un cazador,
  el rango es menor que 1 o no es un entero, o los datos no son de versiones correspondientes,
  la cripta se rechaza antes de iniciar y se informa el motivo (AB-19, AB-20 y AB-21; FR-012
  y FR-013).
- Si el cazador no comparte sala con el jugador, estar dentro del rango solo le permite
  acercarse; no puede atacar a distancia (AB-17; FR-004 y FR-008).
- Si un movimiento lleva al cazador a la sala del jugador, termina el movimiento sin atacar;
  ataca al llegar su siguiente turno programado (AB-23; FR-004).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Cada salida puede declarar un costo entero mayor o igual que 1. Si no declara
  el campo `costo`, su costo efectivo es 100. Una salida sin salida inversa correspondiente
  se acepta como unidireccional. Cuando están representados ambos sentidos de una conexión,
  sus costos efectivos deben coincidir: se acepta que ambos omitan el campo o que uno lo
  omita y el otro declare 100; se rechaza si difieren, según FR-013.
- **FR-002**: Todo movimiento por una salida tiene como costo base el costo de esa salida y
  un intervalo de `max(1, costo_salida * 100 // velocidad)`. Este mínimo aplica incluso si
  la división entera produce 0.
- **FR-003**: El cambio de costo de terreno no altera el comportamiento de errantes ni de
  rastreadores, salvo el tiempo de sus movimientos. Atacar, esperar y las demás acciones
  mantienen sus costos e intervalos previos. Al cambiar la velocidad durante un movimiento,
  el tiempo restante se ajusta según P1 §2.3.
- **FR-004**: El cazador es el cuarto comportamiento de enemigo. Su ficha de catálogo declara
  un rango entero mayor o igual que 1, expresado en unidades de costo. Solo ataca cuando
  comparte sala con el jugador; estar dentro de su rango de persecución no habilita ataques
  a distancia. Si entra a la sala del jugador al completar un movimiento, termina su acción
  de movimiento y ataca al llegar su siguiente turno programado.
- **FR-005**: Si no comparte sala con el jugador, el cazador considera únicamente salidas
  abiertas en ese instante. Si no hay ruta abierta o el costo mínimo hasta el jugador supera
  su rango, espera con costo 100.
- **FR-006**: El costo de una ruta es la suma de los costos de sus salidas. El cazador elige
  una ruta de costo mínimo, aunque tenga más salas que otra ruta disponible de mayor costo.
- **FR-007**: Si varias salas vecinas inician rutas de costo mínimo, el cazador elige la
  vecina de menor id que satisfaga `costo(u, v) + dist(v, jugador) = d`, donde `d` es el
  costo mínimo desde su sala actual.
- **FR-008**: Si el cazador no comparte sala con el jugador y existe una ruta de costo mínimo
  dentro del rango, avanza un paso por ella; el costo base de su movimiento es el de la salida
  atravesada. En cada turno determina su decisión como si se calculara desde cero con el
  estado actual de la cripta, incluida la posición del jugador, las puertas y los actores, sin
  depender de una decisión anterior. Otros actores no bloquean la entrada ni el paso del
  cazador, que puede compartir sala con ellos. El cazador se mueve como máximo a una sala
  adyacente por turno; si esa sala está ocupada, entra en ella y termina allí su movimiento.
- **FR-009**: El cazador conoce el esqueleto completo de la cripta y el estado actual de las
  puertas, no está limitado por la niebla de guerra y nunca abre puertas cerradas.
- **FR-010**: Las vistas de consola y Pygame muestran los costos efectivos de todas las
  salidas de la sala actual, incluidas las cerradas, cuyo estado se distingue claramente.
  Ambas vistas también distinguen visualmente a los cazadores de los demás enemigos.
- **FR-011**: Con exactamente 20 cazadores activos en un mapa de benchmark fijo y versionado
  de mayor tamaño que la cripta offline disponible, cada ciclo de eventos entre dos decisiones
  del jugador no supera 20 ms en el equipo local, sin red ni renderizado. Se registran la
  identidad, versión y dimensiones del mapa. Los ocho escenarios
  combinan dos perfiles de rango (1 y 100; 1000 y 10000), dos frecuencias de cambio de puerta
  (una puerta en cada ciclo de eventos entre decisiones del jugador y una puerta cada 100 de
  esos ciclos) y dos modalidades de cálculo (individual y compartida entre cazadores que
  persiguen al mismo jugador). Cada escenario tiene 30 repeticiones. Se mantienen iguales la
  identidad y versión del mapa, semilla, estado inicial, secuencia de acciones del
  jugador, composición de rangos (diez cazadores por cada valor del perfil) y condiciones del
  equipo; solo varían los factores propios de cada escenario. Se registran los valores concretos
  de rango, la identidad, versión y dimensiones del mapa, semilla, modelo y núcleos del procesador,
  memoria instalada, sistema operativo y versión, entorno de ejecución y su versión, y el
  perfil de energía del equipo. Cada decisión se compara con un recálculo desde cero para
  verificar que sigue siendo correcta.
- **FR-012**: El costo procede del esqueleto de la cripta y el rango de la ficha de catálogo.
  Una salida puede omitir el costo; en ese caso se aplica el valor predeterminado de FR-001.
- **FR-013**: Antes de iniciar la cripta, se rechazan con un error que identifica el problema:
  todo costo declarado que no sea un entero positivo, incluido `null`; toda ficha de cazador
  sin rango o con rango que no sea un entero mayor o igual que 1; y los datos de la cripta y
  el catálogo cuyas versiones no correspondan. También se rechaza toda conexión cuyos costos
  efectivos difieran entre sentidos cuando existen ambas salidas, después de aplicar 100 a
  cada sentido sin campo `costo`. El error identifica la conexión y ambos costos efectivos.
  La ausencia de una salida inversa se acepta como conexión unidireccional. La ausencia del
  campo costo no es un error y usa el valor predeterminado 100; un campo presente con valor
  `null` sí se rechaza.

### Key Entities

- **Salida**: Conecta salas en un sentido; puede no tener una salida inversa. Cuando existen
  ambos sentidos, pueden declarar costo entero siempre que sus costos efectivos coincidan.
- **Cazador**: Enemigo con rango entero mayor o igual que 1 que decide entre atacar, esperar
  o avanzar según las salidas abiertas y el costo mínimo de llegada al jugador.
- **Estado de puertas**: Indica cuáles salidas están abiertas en el instante de decisión.
- **Velocidad**: Determina el intervalo de movimiento a partir del costo de la salida.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Todos los escenarios AB-01 a AB-29 de este documento se satisfacen en sus
  respectivas pruebas de aceptación.
- **SC-002**: Se evalúan ocho escenarios, cada uno con 30 repeticiones, exactamente 20
  cazadores, el mismo mapa de benchmark fijo y versionado de mayor tamaño que la cripta
  offline disponible, semilla, estado inicial, secuencia de acciones del
  jugador, composición de rangos (diez cazadores por cada valor del perfil) y condiciones del
  equipo. Se combinan rangos 1 y 100, rangos 1000 y 10000, cambios de una puerta en cada ciclo
  de eventos entre decisiones del jugador y cada 100 de esos ciclos, y cálculo individual o
  compartido entre cazadores que persiguen al mismo jugador. En cada escenario, cada ciclo dura
  como máximo 20 ms en el equipo local, sin red ni renderizado. Se registra la identidad,
  versión y dimensiones del mapa, los rangos concretos, modelo y núcleos del procesador,
  memoria instalada, sistema operativo y versión, entorno de
  ejecución y versión, y perfil de energía; cada decisión coincide con la referencia recalculada
  desde cero.
- **SC-003**: En todos los casos probados, los movimientos usan el costo y el intervalo
  definidos en FR-001 y FR-002, mientras que las acciones no relacionadas conservan su
  comportamiento previo.

## Assumptions

- La referencia P1 §2.3 define el ajuste del tiempo restante cuando cambia la velocidad; esta
  capacidad no redefine esa regla.
- La medición de rendimiento usa exactamente 20 cazadores activos en cada escenario y un
  mapa fijo/versionado de mayor tamaño que la cripta offline disponible; el tamaño concreto
  no se fija en esta especificación.
- En las mediciones de rendimiento, se usan los rangos fijos 1 y 100 para el perfil pequeño
  y 1000 y 10000 para el grande; se asignan diez cazadores a cada valor y se conserva la misma
  composición en todas las repeticiones de un escenario.
- La cripta, versión, semilla, estado inicial, secuencia de acciones y equipo se conservan
  entre repeticiones; solo cambian los tres factores descritos en el diseño de ocho escenarios.
- En cada medición se registran el modelo y núcleos del procesador, memoria instalada, sistema
  operativo y versión, entorno de ejecución y versión, y perfil de energía.
- La validación de datos ocurre antes de iniciar la cripta; una salida sin campo costo es
  válida y recibe el valor predeterminado 100 antes de comparar los sentidos de una conexión.
  La conexión se acepta si los costos efectivos coinciden y se rechaza si difieren; valores
  inválidos o versiones incompatibles también se rechazan.
- Una salida sin representación inversa es válida y se interpreta como unidireccional; la
  comparación de costos efectivos aplica solo cuando están representados ambos sentidos.
- La ruta se determina con las salidas abiertas y sus costos; otros actores no modifican el
  costo de una ruta.

## Apéndice B — Escenarios de aceptación

Cada caso es un escenario verificable. El identificador AB permite que la prueba
correspondiente cite explícitamente los requisitos funcionales cubiertos.

| ID de prueba | Escenario de aceptación | Requisitos |
|---|---|---|
| AB-01 | Dada una conexión cuyos dos sentidos omiten el campo costo, al validar los datos, se acepta con costo efectivo 100 en ambos sentidos. | FR-001 |
| AB-02 | Dada una salida de costo 1 y un actor cuya velocidad es mayor que 100, al atravesarla, el intervalo es al menos 1; con otros costos y velocidades, se aplica `max(1, costo_salida * 100 // velocidad)`. | FR-002 |
| AB-03 | Dado un actor que atraviesa una salida costosa, al cambiar su velocidad, el tiempo restante se escala según P1 §2.3. | FR-003 |
| AB-04 | Dado un cazador en la misma sala que el jugador, al llegar su turno, ataca sin evaluar una ruta. | FR-004 |
| AB-05 | Dado que no hay ruta compuesta solo por salidas abiertas hasta el jugador, al llegar el turno del cazador, espera con costo 100. | FR-005 |
| AB-06 | Dada una ruta abierta cuyo costo mínimo es mayor que el rango, al llegar el turno del cazador, espera con costo 100; si el costo mínimo es igual al rango, avanza. | FR-005 |
| AB-07 | Dadas dos rutas, una con menos salas y mayor costo, y otra con más salas y menor costo, el cazador avanza por una ruta de menor costo. | FR-006, FR-008 |
| AB-08 | Dadas dos vecinas que inician rutas de costo mínimo, el cazador avanza por la vecina de menor id. | FR-007 |
| AB-09 | Dado que una puerta de la ruta elegida se cierra entre turnos y hay otra alternativa, en el siguiente turno el cazador decide usando las puertas abiertas actuales. | FR-005, FR-008 |
| AB-10 | Dado que cambian la posición del jugador o el estado de otros actores entre turnos, el cazador determina su siguiente decisión como si la calculara desde cero en el estado actual. | FR-008 |
| AB-11 | Dada una sala actual con salidas de costos declarados y no declarados, la vista muestra el costo efectivo de cada salida. | FR-001, FR-010 |
| AB-12 | Dada una vista con cazadores y otros enemigos, el cazador se distingue visualmente de los demás. | FR-010 |
| AB-13 | Con exactamente 20 cazadores activos en un mapa de benchmark fijo y versionado de mayor tamaño que la cripta offline disponible, en el equipo local y sin red ni renderizado, evaluar ocho escenarios: rangos 1 y 100 o rangos 1000 y 10000, con diez cazadores en cada valor; cambio de una puerta cada ciclo de eventos entre decisiones del jugador o cada 100 de esos ciclos; y cálculo individual o compartido entre cazadores que persiguen al mismo jugador. Ejecutar 30 repeticiones por escenario con el mismo mapa y versión, semilla, estado inicial, secuencia de acciones del jugador, composición de rangos y equipo. Registrar identidad, versión y dimensiones del mapa, semilla, rangos concretos, modelo y núcleos del procesador, memoria instalada, sistema operativo y versión, entorno de ejecución y versión, y perfil de energía. Comparar cada decisión con un recálculo desde cero. Ningún ciclo supera 20 ms y todas las decisiones coinciden con la referencia. | FR-011 |
| AB-14 | Al añadir costos de salida, errantes y rastreadores conservan sus decisiones previas; atacar, esperar y las demás acciones conservan sus costos e intervalos previos. | FR-003 |
| AB-15 | Dada una cripta donde la niebla oculta una ruta abierta y existe una salida cerrada, el cazador considera la ruta oculta y no atraviesa ni abre la salida cerrada. | FR-009 |
| AB-16 | Dadas versiones correspondientes de una cripta y una ficha de catálogo, el costo de la salida se toma del esqueleto y el rango del cazador de la ficha. | FR-012 |
| AB-17 | Dado que el cazador no comparte sala con el jugador y la ruta abierta está dentro del rango, al llegar su turno, avanza un paso y no realiza un ataque a distancia. | FR-004, FR-008 |
| AB-18 | Dado que otro actor ocupa la sala adyacente elegida en la ruta, al llegar el turno del cazador, este entra a esa sala y termina allí su movimiento, sin avanzar más de una salida. | FR-008 |
| AB-19 | Dada una salida con un costo declarado que no es un entero positivo, al validar los datos, se rechaza la cripta antes de iniciar y se informa el costo inválido. | FR-013 |
| AB-20 | Dada una ficha de cazador sin rango, con rango no entero, con rango cero o negativo, al validar los datos, se rechaza la cripta antes de iniciar y se informa el problema del rango. | FR-013 |
| AB-21 | Dados un esqueleto de cripta y un catálogo con versiones incompatibles, al validar los datos, se rechaza la cripta antes de iniciar y se informa la incompatibilidad. | FR-013 |
| AB-22 | Dada una sala con salidas abiertas y cerradas, con costos declarados y no declarados, las vistas de consola y Pygame muestran el costo efectivo de cada salida e indican cuáles están cerradas. | FR-001, FR-010 |
| AB-23 | Dado que el cazador está fuera de la sala del jugador, al completar un movimiento que lo lleva a esa sala, termina su movimiento sin atacar; ataca cuando llega su siguiente turno programado. | FR-004 |
| AB-24 | Dada una salida cuyo campo costo está ausente, su costo efectivo es 100; dada otra salida cuyo campo costo está presente con valor `null`, se rechaza la cripta antes de iniciar y se informa el dato inválido. | FR-001, FR-013 |
| AB-25 | Dada una conexión cuyos dos sentidos declaran costos distintos, al validar los datos, se rechaza la cripta antes de iniciar y el error identifica la conexión y ambos costos efectivos. | FR-001, FR-013 |
| AB-26 | Dada una conexión donde un sentido omite el campo costo y el otro declara costo 100, al validar los datos, se acepta la conexión con costo efectivo 100 en ambos sentidos. | FR-001 |
| AB-27 | Dada una conexión donde un sentido omite el campo costo y el otro declara un valor distinto de 100, al validar los datos, se rechaza la cripta antes de iniciar y el error identifica la conexión y ambos costos efectivos. | FR-001, FR-013 |
| AB-28 | Dada una salida de una sala a otra sin una salida inversa correspondiente, al validar los datos, se acepta como conexión unidireccional. | FR-001 |
| AB-29 | Dado el protocolo de medición del objetivo de 20 ms, se usa en los ocho escenarios el mismo mapa de benchmark fijo y versionado de mayor tamaño que la cripta offline disponible, y se registran su identidad, versión y dimensiones. | FR-011 |
