# Feature Specification: Niebla de guerra, antorcha e ir a

**Feature Branch**: `spec/jose`

**Created**: 2026-11-11

**Status**: Draft

**Input**: Capacidad «Niebla de guerra y viaje automático»: conocimiento del jugador sobre salas y puertas, antorcha y orden `ir a <sala>`. Fuente: `docs/equipo/BORRADOR_NIEBLA_VIAJE_JOSE.md` (enunciado CRIPTA Parte II §3.3, §3.4, §5.3, §6.1, §6.3, §7.3 y Apéndice B), la constitución 1.0.0 y la capacidad `001-terreno-cazador` integrada en la base `e5bd543`.

## Clarifications

### Session 2026-11-11

> Estado: **propuestas de José pendientes de revisión de Daniel**. No constan como aprobadas por
> Daniel; si la revisión las cambia, se corrige primero esta spec en un commit separado
> (constitución VII).

- Q: ¿Qué ocurre si el destino de `ir a` es la sala actual? → A (propuesta): se informa la
  llegada sin consumir turno ni tiempo virtual.
- Q: ¿Qué ocurre si ya hay enemigos en la sala al emitir la orden? → A (propuesta): el viaje se
  detiene sin caminar, con causa «enemigos», y no consume tiempo.
- Q: ¿Qué causa se muestra si coinciden varias en el mismo paso? → A (propuesta): prioridad fin
  de partida > daño > enemigos > llegada (la pérdida de ruta solo se evalúa si ninguna aplica).
- Q: ¿Cómo se responde a un ID inexistente o no explorado? → A (propuesta): con el mismo mensaje
  de rechazo, sin revelar si la sala existe, y sin consumir tiempo.
- Q: ¿Qué muestra el mapa conocido? → A (propuesta): de cada sala explorada, nombre, salidas
  (dirección y costo) y estado recordado de cada puerta; de cada avistada, solo que existe una
  sala sin explorar detrás de la salida, sin ID ni nombre; nada de las desconocidas.
- Q: ¿La antorcha observa las puertas de las vecinas reveladas? → A (propuesta): no; revela las
  vecinas y sus salidas sin observar puertas remotas. El jugador observa una puerta solo cuando
  está físicamente en cualquiera de sus dos extremos.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Explorar con niebla de guerra (Priority: P1)

Como jugador, necesito que el mapa muestre solo lo que he descubierto, distinguiendo salas
exploradas, avistadas y desconocidas, y que recuerde la última vez que vi cada puerta, para
orientarme sin recibir información que mi personaje no obtuvo.

**Why this priority**: El conocimiento del jugador es la base de la antorcha, del viaje
automático y del guardado; sin él ninguna otra historia puede verificarse.

**Independent Test**: Iniciar una cripta de prueba, moverse por varias salas, cambiar puertas
lejos del jugador y comparar el mapa conocido con el estado esperado sala por sala y puerta por
puerta.

**Acceptance Scenarios**:

1. **Given** una partida recién iniciada, **When** el jugador consulta el mapa en el instante 0,
   **Then** solo la sala inicial está explorada; los destinos de sus salidas están avistados y el
   resto es desconocido (NV-01; FR-001, FR-002).
2. **Given** el jugador entra a una sala avistada, **When** consulta el mapa, **Then** la sala
   queda explorada y los destinos no explorados de sus salidas pasan a avistados (NV-02; FR-001,
   FR-002).
3. **Given** una sala avistada, **When** se consulta el mapa, **Then** solo se indica su
   existencia detrás de la salida conocida, sin nombre, contenido ni salidas propias; una sala
   desconocida no aparece (NV-03; FR-003).
4. **Given** el jugador observó una puerta abierta y se alejó, **When** esa puerta se cierra sin
   que él esté en ninguno de sus extremos, **Then** el mapa sigue mostrando la puerta como abierta
   hasta una nueva observación (NV-04; FR-004).
5. **Given** el jugador está en un extremo de una puerta, **When** consulta el mapa, **Then** se
   muestra su estado real y ese estado pasa a ser el recordado (NV-05; FR-004).
6. **Given** la infraestructura precargó o almacenó datos de salas no exploradas, **When** se
   consulta el mapa conocido, **Then** esas salas conservan su estado de conocimiento previo
   (NV-06; FR-006).

---

### User Story 2 - Viajar automáticamente con `ir a` (Priority: P1)

Como jugador, necesito ordenar `ir a <sala>` hacia una sala explorada para que mi personaje
avance paso a paso por la ruta conocida de menor costo, deteniéndose ante peligros o cambios,
sin saltarse reglas del juego.

**Why this priority**: Es la acción nueva de mayor valor y la que concentra los casos
obligatorios del Apéndice B.

**Independent Test**: Preparar criptas con salas exploradas, rutas de distintos costos, puertas
cambiantes, enemigos y daño, ejecutar `ir a` y verificar cada paso, el tiempo consumido y la
causa de parada.

**Acceptance Scenarios**:

1. **Given** un destino no explorado, **When** el jugador emite `ir a` hacia él, **Then** la orden
   se rechaza con un mensaje y el tiempo virtual no avanza (NV-07, Apéndice B; FR-008).
2. **Given** dos rutas conocidas, una con menos salas y mayor costo y otra con más salas y menor
   costo, **When** el jugador viaja, **Then** se usa la de menor costo total (NV-08; FR-009).
3. **Given** dos vecinas inician rutas conocidas de costo mínimo igual, **When** se calcula el
   paso, **Then** se elige la vecina de menor ID (NV-09; FR-009).
4. **Given** una puerta recordada abierta que en realidad está cerrada, **When** el viaje llega a
   uno de sus extremos y la observa, **Then** el recuerdo se actualiza y se recalcula: se toma una
   alternativa conocida si existe o el viaje se detiene sin tiempo adicional por el intento
   fallido (NV-10, Apéndice B; FR-004, FR-010).
5. **Given** no existe ruta conocida abierta desde la sala actual, **When** se emite o continúa
   el viaje, **Then** se detiene con causa «sin ruta conocida» sin consumir tiempo por el intento
   (NV-11; FR-010, FR-012).
6. **Given** la ruta entra a una sala con enemigos dormidos, **When** se completa ese paso,
   **Then** los enemigos se activan según P1 y el viaje se detiene mostrando la causa (NV-12,
   Apéndice B; FR-012).
7. **Given** el jugador recibe daño entre dos pasos, **When** termina el evento que lo causa,
   **Then** el viaje se detiene con causa «daño» y no se ejecuta el siguiente paso (NV-13;
   FR-012).
8. **Given** un viaje de varios pasos, **When** transcurre, **Then** cada paso consume el tiempo
   de un movimiento ordinario según costo de salida y velocidad, y los eventos del reloj se
   ejecutan entre pasos (NV-14; FR-011).
9. **Given** la ruta conocida exige atravesar una puerta cerrada y el jugador tiene la llave,
   **When** viaja, **Then** el viaje no abre la puerta (NV-15; FR-013).
10. **Given** un viaje completado o interrumpido, **When** se revisa `partida.log`, **Then** cada
    paso aparece como movimiento individual y la orden `ir a` como comentario de depuración; al
    reproducir el log se obtiene la misma partida (NV-16; FR-014).

---

### User Story 3 - Revelar vecinas con la antorcha (Priority: P2)

Como jugador, necesito que con la antorcha encendida, al entrar a una sala, se exploren sus
vecinas sin visitarlas ni activar lo que contengan, para planificar mejor mis rutas.

**Why this priority**: Amplía el conocimiento y cambia el comportamiento de `ir a`, pero depende
del conocimiento base.

**Independent Test**: Entrar con y sin antorcha a una sala con vecinas tras puertas abiertas y
cerradas que contienen enemigos y trampas; comparar mapa y estado de esos elementos.

**Acceptance Scenarios**:

1. **Given** antorcha encendida, **When** el jugador entra a una sala, **Then** todas sus vecinas,
   incluidas las situadas tras puertas cerradas, quedan exploradas con nombre y salidas, sin
   contenido (NV-17, Apéndice B; FR-005).
2. **Given** vecinas reveladas por antorcha con enemigos o trampas, **When** se revelan, **Then**
   ningún enemigo se activa ni trampa se dispara (NV-18, Apéndice B; FR-005).
3. **Given** vecinas recién exploradas por antorcha, **When** se consulta el mapa, **Then** los
   destinos no explorados de sus salidas pasan a avistados (NV-19; FR-002, FR-005).
4. **Given** antorcha apagada, **When** el jugador entra a una sala, **Then** solo esa sala queda
   explorada (NV-20; FR-005).

---

### User Story 4 - Conservar el conocimiento en guardado, retroceso e historia (Priority: P2)

Como jugador, necesito que guardar, cargar, usar el pergamino y consultar el pasado conserven
exactamente lo que sabía en cada momento.

**Why this priority**: Garantiza coherencia y determinismo con las capacidades existentes de
persistencia e historia.

**Independent Test**: Guardar y cargar una partida con conocimiento parcial; usar el pergamino
tras una entrada con antorcha y durante un viaje; consultar instantes históricos y comparar.

**Acceptance Scenarios**:

1. **Given** una partida con salas exploradas, avistadas y puertas recordadas desactualizadas,
   **When** se guarda y se carga, **Then** el conocimiento cargado es idéntico al guardado
   (NV-21; FR-007).
2. **Given** una entrada con antorcha que exploró vecinas, **When** se usa el pergamino, **Then**
   cada sala y recuerdo afectado vuelve a su estado anterior y lo que ya se conocía antes se
   conserva (NV-22, Apéndice B; FR-007).
3. **Given** un viaje en curso, **When** se usa el pergamino, **Then** solo se revierte el último
   paso con sus cambios asociados y el viaje no se reanuda (NV-23, Apéndice B; FR-015).
4. **Given** una consulta histórica de un instante anterior, **When** se reconstruye el
   conocimiento de ese instante, **Then** coincide con el que existía entonces, no contiene
   información descubierta después y no modifica el conocimiento actual (NV-24; FR-007).

---

### User Story 5 - Ver el mapa conocido y la causa de parada (Priority: P3)

Como jugador, necesito ver el mapa conocido, el progreso de `ir a` y la causa de parada en la
interfaz mínima del proyecto.

**Why this priority**: Hace visible la capacidad, pero las reglas son verificables sin vista.

**Independent Test**: Mostrar una partida con conocimiento parcial y un viaje detenido, y
comprobar que la vista muestra solo información conocida y la causa.

**Acceptance Scenarios**:

1. **Given** una partida con las tres categorías de salas, **When** se muestra el mapa, **Then**
   se distinguen exploradas y avistadas y no aparece información desconocida ni del mapa real
   no observado (NV-25; FR-018).
2. **Given** un viaje detenido, **When** se muestra el resultado, **Then** aparece la causa de
   parada (NV-26; FR-012, FR-018).

---

### Edge Cases

- Una puerta cambia varias veces lejos del jugador: el recuerdo conserva la última observación
  (NV-04; FR-004).
- La antorcha revela una vecina ya explorada: su estado no cambia y el retroceso no la convierte
  en desconocida (NV-22; FR-005, FR-007).
- La ruta de menor costo atraviesa una sala avistada pero no explorada: no se usa (NV-27; FR-009).
- Varias causas coinciden en el mismo paso: se muestra una sola según la prioridad fin de
  partida > daño > enemigos > llegada (NV-32; FR-012).
- El destino es la sala actual: se informa la llegada sin consumir turno (NV-30; FR-008).
- El ID no existe o no está explorado: mismo mensaje de rechazo, sin revelar existencia ni
  consumir tiempo (NV-07, NV-33; FR-008).
- Ya hay enemigos en la sala al ordenar: el viaje se detiene sin caminar (NV-31; FR-012).
- Una vecina revelada por antorcha no tiene puertas propias observadas: sus salidas aparecen
  sin estado recordado y no se usan como tránsito hasta observarlas (NV-34; FR-004, FR-005,
  FR-009).
- El cazador sigue usando el esqueleto completo y el estado real de las puertas; la niebla no
  lo limita (NV-28; FR-006, FR-009 de 001).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Cada sala tiene para el jugador un estado de conocimiento: explorada, avistada o
  desconocida. La sala inicial está explorada desde el instante 0 y toda sala visitada queda
  explorada.
- **FR-002**: Una sala no explorada que sea destino de una salida de una sala explorada está
  avistada; las demás no exploradas son desconocidas. Este estado se actualiza cada vez que se
  exploran salas nuevas.
- **FR-003**: De una sala explorada se conocen nombre, salidas, costo efectivo de cada salida y
  el último estado observado de sus puertas. De una avistada solo se conoce su existencia detrás
  de la salida; no se revelan ID, nombre, contenido ni salidas propias. De una desconocida no se
  revela nada. Las salidas de una sala explorada cuya puerta nunca fue observada se muestran
  sin estado recordado.
- **FR-004**: El estado real de una puerta se observa cuando el jugador está físicamente en
  cualquiera de sus dos extremos y pasa a ser el recordado. El recuerdo no se actualiza con
  cambios no observados ni por revelación de antorcha.
- **FR-005**: Con la antorcha encendida, al entrar a una sala se exploran todas sus vecinas,
  tras salidas abiertas o cerradas, revelando nombre y salidas pero no contenido ni estado de
  sus puertas remotas, sin activar enemigos ni trampas, y se recalculan las salas avistadas.
- **FR-006**: El conocimiento del jugador está separado del mapa real y de los datos precargados
  o almacenados. Descargar datos no equivale a explorarlos. El mapa conocido y `ir a` usan solo
  el conocimiento del jugador; el cazador conserva el conocimiento completo de 001 (FR-009).
- **FR-007**: El conocimiento se guarda y se carga sin pérdidas; el retroceso lo restaura
  exactamente al estado previo; y el conocimiento de cualquier instante histórico puede
  reconstruirse de forma aislada, sin leer ni alterar el conocimiento actual.
- **FR-008**: `ir a <sala>` se acepta solo si el destino está explorado; un ID inexistente o no
  explorado recibe el mismo mensaje de rechazo, sin revelar si la sala existe y sin consumir
  tiempo virtual. Si el destino es la sala actual, se informa la llegada sin consumir turno.
- **FR-009**: El viaje usa solo salas exploradas y salidas recordadas abiertas, minimiza el costo
  total de tránsito y, si varios primeros pasos alcanzan el costo mínimo, elige la vecina de menor
  ID, con la misma regla observable que el cazador (FR-007 de 001).
- **FR-010**: Antes de cada paso la ruta se recalcula con el conocimiento vigente. Si una
  observación revela una puerta cerrada, se actualiza el recuerdo y se busca alternativa conocida;
  si no existe, el viaje se detiene sin consumir tiempo adicional por el intento fallido.
- **FR-011**: Cada paso es un movimiento ordinario completo: consume el tiempo de las reglas de
  terreno y velocidad (FR-002 de 001) y entre pasos se ejecutan normalmente los eventos del reloj.
  No hay teletransporte ni efectos omitidos.
- **FR-012**: El viaje se detiene al llegar al destino, entrar a una sala con enemigos activos o
  dormidos, recibir daño o quedarse sin ruta conocida, y muestra la causa. Los enemigos dormidos
  de la sala de entrada se activan según P1. Si ya hay enemigos en la sala al emitir la orden,
  el viaje se detiene sin caminar ni consumir tiempo. Si coinciden causas se muestra una sola
  con prioridad fin de partida > daño > enemigos > llegada; «sin ruta conocida» solo se informa
  si ninguna de ellas aplica.
- **FR-013**: El viaje nunca abre puertas, aunque el jugador tenga la llave.
- **FR-014**: Cada paso se registra individualmente en `partida.log` y la orden `ir a` como
  comentario de depuración; la reproducción del log es determinista.
- **FR-015**: El pergamino durante o tras un viaje revierte solo el último paso con sus cambios
  asociados (incluido el conocimiento) y no reinicia ni continúa el viaje.
- **FR-016**: Consultar el estado de salas y puertas conocidas es independiente de cualquier
  vista. Explorar nuevas salas cuesta proporcionalmente a las salas reveladas, no al total
  conocido, y registrar o invertir cambios de conocimiento es compatible con la historia.
- **FR-017**: `--bench` mide las consultas de estado de salas, los recuerdos de puertas y el
  cálculo de un paso de `ir a`. El cálculo de un paso no supera 5 ms con el mapa conocido completo
  de la cripta de referencia, sin red ni renderizado, salvo enmienda oficial. Se registran entorno,
  semilla y resultados reproducibles; no se afirma cumplimiento sin medir.
- **FR-018**: La interfaz mínima del proyecto muestra el mapa conocido, la ejecución de `ir a` y
  la causa de parada, sin filtrar información del mapa real no conocida por el jugador.

### Key Entities

- **Conocimiento del jugador**: estado por sala (explorada, avistada, desconocida) y último
  estado observado de cada puerta conocida; separado del mapa real.
- **Recuerdo de puerta**: último estado observado de una puerta y momento de esa observación.
- **Antorcha**: objeto con estado encendido/apagado que amplía la exploración al entrar.
- **Viaje (`ir a`)**: orden con destino explorado, paso actual y causa de parada.
- **Cambio de conocimiento**: diferencia reversible antes/después asociada a una acción, usada
  por retroceso, guardado e historia.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Los 34 escenarios NV-01 a NV-34, incluidos los seis casos del Apéndice B, tienen al
  menos una prueba aprobada que cita los FR que verifica.
- **SC-002**: En el 100 % de los casos probados, ninguna vista ni el viaje revelan nombre,
  contenido o salidas de salas avistadas o desconocidas, ni estados de puertas no observados.
- **SC-003**: Toda orden rechazada o intento fallido de paso consume 0 unidades de tiempo virtual.
- **SC-004**: Tras guardar/cargar, retroceder o reconstruir un instante histórico, el
  conocimiento coincide en el 100 % de salas y recuerdos con el esperado.
- **SC-005**: El informe de `--bench` muestra que el cálculo de un paso de `ir a` no supera 5 ms
  con el mapa conocido completo de la cripta de referencia, e incluye entorno, semilla, número de
  repeticiones y resultados reproducibles, además de las mediciones de consultas de estado y
  recuerdos de puertas.
- **SC-006**: Reproducir dos veces el mismo `partida.log` produce la misma partida y el mismo
  conocimiento final.
- **SC-007**: La matriz de pruebas de la capacidad incluye evidencia de ejecución (comando,
  resultado y fecha) para todos los escenarios NV antes de declarar la capacidad completa.

## Assumptions

- Se reutilizan sin redefinir las reglas de 001: costo efectivo de salidas, intervalo de
  movimiento y desempate por menor ID del cazador.
- La activación de enemigos dormidos al entrar y el resto de reglas de P1 no cambian.
- La cripta de referencia para FR-017 es la indicada por el enunciado; si existe enmienda
  oficial, prevalece.
- Las decisiones de la sesión de clarificación del 2026-11-11 son propuestas de José pendientes
  de revisión de Daniel; no se atribuye aprobación.
- Los identificadores NV son locales a esta capacidad; no se asignan números globales G sin
  coordinarlos con la matriz del equipo.
- Las estructuras, algoritmos, clases y módulos se definen en `plan.md` (fase D) respetando la
  constitución: estructuras propias sin `dict`/`set` como índice, determinismo, `--replay` y
  `--bench` sin vista, y presupuesto de solicitudes.
- Coordinación prevista: contrato de ruta con Daniel; cambios reversibles, persistencia e
  historia con Sebastián; caché/precarga sin revelar conocimiento con Centeno.

## Apéndice B — Escenarios de aceptación

| ID de prueba | Escenario de aceptación | Requisitos |
|---|---|---|
| NV-01 | En el instante 0 solo la sala inicial está explorada; destinos de sus salidas avistados; resto desconocido. | FR-001, FR-002 |
| NV-02 | Al visitar una sala avistada queda explorada y sus destinos no explorados pasan a avistados. | FR-001, FR-002 |
| NV-03 | Una avistada no revela nombre, contenido ni salidas; una desconocida no revela nada. | FR-003 |
| NV-04 | Una puerta que cambia sin observación conserva en el mapa el último estado observado. | FR-004 |
| NV-05 | Desde un extremo de una puerta se observa y recuerda su estado real. | FR-004 |
| NV-06 | Datos precargados o almacenados no cambian el conocimiento. | FR-006 |
| NV-07 | (Apéndice B) `ir a` a destino no explorado: rechazo y cero tiempo consumido. | FR-008 |
| NV-08 | Se prefiere la ruta conocida de menor costo frente a la de menos salas. | FR-009 |
| NV-09 | Empate de primer paso: vecina de menor ID. | FR-009 |
| NV-10 | (Apéndice B) Puerta recordada abierta pero cerrada: actualizar al observar y recalcular; alternativa o parada sin tiempo adicional. | FR-004, FR-010 |
| NV-11 | Sin ruta conocida: parada con causa y sin tiempo por el intento. | FR-010, FR-012 |
| NV-12 | (Apéndice B) Entrada en sala con enemigos dormidos: activación ordinaria y parada. | FR-012 |
| NV-13 | Daño entre pasos: parada con causa «daño». | FR-012 |
| NV-14 | Cada paso consume tiempo de movimiento ordinario y los eventos del reloj ocurren entre pasos. | FR-011 |
| NV-15 | El viaje no abre puertas aunque el jugador tenga la llave. | FR-013 |
| NV-16 | Cada paso en `partida.log`; `ir a` como comentario; reproducción determinista. | FR-014 |
| NV-17 | (Apéndice B) Con antorcha, vecinas exploradas incluso tras puertas cerradas. | FR-005 |
| NV-18 | (Apéndice B) La revelación por antorcha no activa enemigos ni trampas. | FR-005 |
| NV-19 | Vecinas reveladas por antorcha generan nuevas avistadas. | FR-002, FR-005 |
| NV-20 | Sin antorcha solo se explora la sala visitada. | FR-005 |
| NV-21 | Guardar y cargar conserva exactamente el conocimiento. | FR-007 |
| NV-22 | (Apéndice B) Retroceso de entrada con antorcha restaura cada sala y recuerdo, conservando lo previo. | FR-007 |
| NV-23 | (Apéndice B) Retroceso durante viaje: solo último paso revertido; sin reanudación. | FR-015 |
| NV-24 | Conocimiento histórico reconstruido sin filtración del actual ni modificación de este. | FR-007 |
| NV-25 | La vista muestra solo conocimiento del jugador. | FR-018 |
| NV-26 | La vista muestra la causa de parada. | FR-012, FR-018 |
| NV-27 | Una sala avistada no se usa como tránsito. | FR-009 |
| NV-28 | El cazador no queda limitado por la niebla del jugador. | FR-006 |
| NV-29 | `--bench` mide consultas, recuerdos y paso de `ir a`; paso ≤ 5 ms con entorno y semilla registrados. | FR-016, FR-017 |
| NV-30 | (Propuesta) Destino igual a la sala actual: se informa la llegada sin consumir turno. | FR-008 |
| NV-31 | (Propuesta) Enemigos presentes al ordenar: parada sin caminar y sin tiempo. | FR-012 |
| NV-32 | (Propuesta) Causas coincidentes: se muestra fin de partida > daño > enemigos > llegada. | FR-012 |
| NV-33 | (Propuesta) ID inexistente y no explorado reciben el mismo mensaje, sin tiempo. | FR-008 |
| NV-34 | (Propuesta) La antorcha no observa puertas remotas; sus salidas no se usan como tránsito hasta observarlas. | FR-004, FR-005, FR-009 |
