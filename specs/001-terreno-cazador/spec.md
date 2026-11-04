# Feature Specification: Terreno y cazador

**Feature Branch**: `No creada`

**Created**: 2026-11-04

**Status**: Draft

**Input**: Capacidad «Terreno y cazador»: costos de salidas, tiempos de movimiento y comportamiento de un nuevo enemigo cazador.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Atravesar salidas con costos distintos (Priority: P1)

Como jugador o actor de la partida, necesito que el tiempo de movimiento refleje el costo de
la salida recorrida para que atravesar terreno más costoso tarde más, sin cambiar las demás
acciones ni las reglas de movimiento existentes.

**Why this priority**: El costo del terreno y el tiempo de movimiento afectan a todos los actores.

**Independent Test**: Preparar salidas con costo declarado y omitido, y comprobar costo e
intervalo de movimiento para más de una velocidad.

**Acceptance Scenarios**:

1. **Given** una salida sin costo declarado, **When** un actor la atraviesa en cualquier
   sentido, **Then** la acción tiene costo base 100 (AB-01; FR-001).
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

### User Story 3 - Reconocer el terreno y a los cazadores (Priority: P2)

Como jugador, necesito ver el costo de las salidas disponibles en mi sala y distinguir a los
cazadores de los demás enemigos para interpretar el terreno y anticipar sus acciones.

**Why this priority**: La información visible ayuda a comprender el costo de desplazarse y
reconocer la nueva amenaza.

**Independent Test**: Abrir una sala con salidas de distintos costos y con un cazador y otros
enemigos, y verificar la información que se muestra.

**Acceptance Scenarios**:

1. **Given** la sala actual tiene salidas con costos distintos o sin costo declarado,
   **When** el jugador consulta la vista, **Then** se muestra el costo efectivo de cada
   salida (AB-11; FR-010).
2. **Given** hay un cazador y otro enemigo, **When** se muestran en la vista, **Then** el
   cazador se distingue de los demás enemigos (AB-12; FR-010).

### Edge Cases

- Una salida de costo 1 y una velocidad alta producen un intervalo mínimo de 1, nunca 0
  (AB-02; FR-002).
- Si el costo mínimo de llegada es exactamente igual al rango, el cazador puede moverse;
  solo espera cuando el costo supera el rango (AB-06; FR-005).
- Una puerta cerrada no forma parte de una ruta válida, aunque conecte con el jugador
  (AB-05 y AB-09; FR-005 y FR-008).
- Si el costo de una salida no está declarado, su costo efectivo es 100 en ambos sentidos
  (AB-01; FR-001).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Cada salida puede tener un costo entero mayor o igual que 1. Si no se declara,
  su costo efectivo es 100. El costo es igual en ambos sentidos.
- **FR-002**: Todo movimiento por una salida tiene como costo base el costo de esa salida y
  un intervalo de `max(1, costo_salida * 100 // velocidad)`. Este mínimo aplica incluso si
  la división entera produce 0.
- **FR-003**: El cambio de costo de terreno no altera el comportamiento de errantes ni de
  rastreadores, salvo el tiempo de sus movimientos. Atacar, esperar y las demás acciones
  mantienen sus costos e intervalos previos. Al cambiar la velocidad durante un movimiento,
  el tiempo restante se ajusta según P1 §2.3.
- **FR-004**: El cazador es el cuarto comportamiento de enemigo. Su ficha de catálogo declara
  un rango entero expresado en unidades de costo. En su turno, si comparte sala con el
  jugador, lo ataca antes de evaluar rutas.
- **FR-005**: Si no comparte sala con el jugador, el cazador considera únicamente salidas
  abiertas en ese instante. Si no hay ruta abierta o el costo mínimo hasta el jugador supera
  su rango, espera con costo 100.
- **FR-006**: El costo de una ruta es la suma de los costos de sus salidas. El cazador elige
  una ruta de costo mínimo, aunque tenga más salas que otra ruta disponible de mayor costo.
- **FR-007**: Si varias salas vecinas inician rutas de costo mínimo, el cazador elige la
  vecina de menor id que satisfaga `costo(u, v) + dist(v, jugador) = d`, donde `d` es el
  costo mínimo desde su sala actual.
- **FR-008**: Si existe una ruta de costo mínimo dentro del rango, el cazador avanza un paso
  por ella y el costo base de su movimiento es el de la salida atravesada. En cada turno
  determina su decisión como si se calculara desde cero con el estado actual de la cripta,
  incluida la posición del jugador, las puertas y los actores, sin depender de una decisión
  anterior.
- **FR-009**: El cazador conoce el esqueleto completo de la cripta y el estado actual de las
  puertas, no está limitado por la niebla de guerra y nunca abre puertas cerradas.
- **FR-010**: La vista muestra los costos efectivos de las salidas de la sala actual y
  distingue visualmente a los cazadores de los demás enemigos.
- **FR-011**: Con decenas de cazadores activos, el ciclo de eventos entre dos decisiones del
  jugador no supera 20 ms en el equipo local, sin red ni renderizado.
- **FR-012**: El costo procede del esqueleto de la cripta y el rango de la ficha de catálogo.
  Ambos datos se consideran válidos mientras correspondan a la versión de datos aplicable.

### Key Entities

- **Salida**: Conecta salas; puede declarar un costo entero, que es igual en ambos sentidos.
- **Cazador**: Enemigo con rango entero que decide entre atacar, esperar o avanzar según las
  salidas abiertas y el costo mínimo de llegada al jugador.
- **Estado de puertas**: Indica cuáles salidas están abiertas en el instante de decisión.
- **Velocidad**: Determina el intervalo de movimiento a partir del costo de la salida.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Todos los escenarios AB-01 a AB-16 de este documento se satisfacen en sus
  respectivas pruebas de aceptación.
- **SC-002**: Con 20 cazadores activos, cada ciclo de eventos entre decisiones del jugador
  dura como máximo 20 ms en el equipo local, sin red ni renderizado.
- **SC-003**: En todos los casos probados, los movimientos usan el costo y el intervalo
  definidos en FR-001 y FR-002, mientras que las acciones no relacionadas conservan su
  comportamiento previo.

## Assumptions

- La referencia P1 §2.3 define el ajuste del tiempo restante cuando cambia la velocidad; esta
  capacidad no redefine esa regla.
- Para hacer verificable «decenas de cazadores», la medición de rendimiento usa al menos 20
  cazadores activos.
- Los costos y rangos provienen de datos válidos de versiones correspondientes, como indica
  el alcance; no se especifica aquí el tratamiento de datos inválidos o incompatibles.
- La ruta se determina con las salidas abiertas y sus costos; otros actores no modifican el
  costo de una ruta.

## Apéndice B — Escenarios de aceptación

Cada caso es un escenario verificable. El identificador AB permite que la prueba
correspondiente cite explícitamente los requisitos funcionales cubiertos.

| ID de prueba | Escenario de aceptación | Requisitos |
|---|---|---|
| AB-01 | Dada una salida cuyo costo no está declarado, al cruzarla en cualquiera de los dos sentidos, el costo de la acción es 100 en ambos casos. | FR-001 |
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
| AB-13 | Con 20 cazadores activos en el equipo local y sin red ni renderizado, cada ciclo de eventos entre decisiones del jugador no supera 20 ms, medido con `--bench`. | FR-011 |
| AB-14 | Al añadir costos de salida, errantes y rastreadores conservan sus decisiones previas; atacar, esperar y las demás acciones conservan sus costos e intervalos previos. | FR-003 |
| AB-15 | Dada una cripta donde la niebla oculta una ruta abierta y existe una salida cerrada, el cazador considera la ruta oculta y no atraviesa ni abre la salida cerrada. | FR-009 |
| AB-16 | Dadas versiones correspondientes de una cripta y una ficha de catálogo, el costo de la salida se toma del esqueleto y el rango del cazador de la ficha. | FR-012 |
