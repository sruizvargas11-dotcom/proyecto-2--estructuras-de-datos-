# Feature Specification: Línea de tiempo de CRIPTA

**Feature Branch**: `spec/sebastian`

**Created**: 2026-11-09

**Status**: Draft

**Input**: Capacidad «Línea de tiempo del juego CRIPTA» (Parte II, §3.6): consultar estados pasados y reproducirlos sin alterar la partida.

## Clarifications

### Session 2026-11-09

- Q: ¿El valor predeterminado de K es el mayor valor probado que cumple el umbral de rendimiento? → A: Sí; se elige el mayor K probado que cumpla SC-001.
- Q: ¿Los 50 ms de SC-001 se exigen sobre el máximo de todas las mediciones o sobre el p95, con el máximo documentado? → A: El p95 de todas las mediciones debe ser menor de 50 ms y también se documenta el máximo.
- Q: ¿La numeración de acciones empieza en 1? → A: Sí; empieza en 1 y solo cuenta las acciones vigentes.
- Q: ¿Cómo se deben tratar los archivos de partida de la Parte I? → A: Se rechazan con un mensaje claro de incompatibilidad; no se migran.

## User Scenarios & Testing *(mandatory)*

### Historia de usuario 1 - Consultar un instante pasado (Priority: P1)

Como jugador, quiero consultar la partida en un instante del reloj virtual o antes de una acción mía para entender cómo había evolucionado sin cambiar la partida actual.

**Why this priority**: Es el propósito central de la capacidad y permite inspeccionar una partida desde su inicio.

**Independent Test**: Avanzar una partida con eventos y acciones conocidos, consultar instantes y números de acción, y comparar cada resumen con el estado registrado en ese punto.

**Acceptance Scenarios**:

1. **Given** una partida activa con eventos programados y una decisión del jugador en el instante `t`, **When** el jugador consulta `historia t`, **Then** se muestra el estado resultante de todos los eventos con tiempo menor o igual que `t`, justo antes de esa decisión (G20; FR-001, FR-003, FR-004).
2. **Given** que se han ejecutado al menos `k` acciones del jugador en la línea de tiempo vigente, **When** el jugador consulta `historia #k`, **Then** se muestra el estado justo antes de la acción número `k` (FR-002, FR-003, FR-004).
3. **Given** una partida cuyo reloj actual es `t_actual`, **When** el jugador consulta un instante mayor que `t_actual`, **Then** la consulta se rechaza e informa que el instante está fuera del tiempo transcurrido (G18; FR-005).

### Historia de usuario 2 - Mantener intacta la partida al consultar (Priority: P1)

Como jugador, quiero que inspeccionar el pasado no consuma tiempo ni interfiera con mis acciones o con el pergamino.

**Why this priority**: Una consulta histórica solo es útil si no cambia aquello que pretende inspeccionar ni la partida en curso.

**Independent Test**: Comparar la partida y el pergamino antes y después de varias consultas; luego usar el pergamino y verificar qué acciones permanecen en la línea de tiempo.

**Acceptance Scenarios**:

1. **Given** una partida y un pergamino con su historial actual, **When** el jugador consulta cualquier estado válido, **Then** el reloj, el estado actual, las acciones contabilizadas y el contenido del pergamino permanecen iguales (G21; FR-006, FR-007).
2. **Given** que el jugador revierte acciones con el pergamino, **When** consulta el pasado de la línea de tiempo resultante, **Then** las acciones revertidas y sus efectos ya no aparecen como historia vigente (G19; FR-008).
3. **Given** un historial del pergamino con hasta cinco acciones, **When** se realizan consultas históricas y después se usa el pergamino, **Then** se conserva el límite de cinco acciones y la consulta no añade ni elimina entradas del pergamino (FR-007).

### Historia de usuario 3 - Reproducir y conservar la historia (Priority: P2)

Como jugador, quiero reproducir una partida hasta un instante sin abrir la interfaz y conservar su historia y mapa conocido al guardar y cargar.

**Why this priority**: Permite revisar partidas terminadas o guardadas con el mismo resumen que en una partida activa.

**Independent Test**: Reproducir una partida hasta un instante, comparar el resumen con una consulta interactiva equivalente y guardar/cargar una partida para volver a consultar su historia y mapa.

**Acceptance Scenarios**:

1. **Given** un registro de partida que termina antes del instante solicitado, **When** se ejecuta `--replay partida.log --hasta t`, **Then** se imprime el resumen del estado final y se informa que la partida terminó antes de `t` (G22; FR-011).
2. **Given** un registro de partida que alcanza el instante solicitado, **When** se ejecuta `--replay partida.log --hasta t`, **Then** se imprime el mismo resumen que `historia t`, sin abrir la interfaz ni realizar solicitudes de red (FR-010, FR-011).
3. **Given** una partida guardada con historia y mapa conocido, **When** se carga y se consulta un punto anterior, **Then** se conserva y muestra la misma historia y el mismo mapa conocido que antes de guardar (FR-012).
4. **Given** un archivo de partida de la Parte I, **When** se intenta cargar, **Then** se rechaza con un mensaje claro de incompatibilidad; nunca se carga en silencio (G23; FR-013).

### Edge Cases

- Si el instante consultado es anterior al inicio del registro, la consulta se rechaza con un mensaje claro.
- Si `k` no corresponde a una acción existente en la línea de tiempo vigente, la consulta se rechaza sin modificar la partida.
- La numeración de acciones es de base uno y se refiere solo a las acciones que siguen vigentes después de cualquier reversión.
- Si ocurren varios eventos en el mismo instante, el resumen incluye todos los eventos ejecutados en ese instante antes de la decisión del jugador; el orden entre eventos coincide con el orden determinista de la partida.
- Una solicitud `--hasta t` posterior al final de la partida presenta el estado final y el aviso de finalización anticipada; no se trata como una consulta interactiva a un reloj futuro.
- Un valor inválido para `--checkpoint-cada K` se rechaza con un mensaje claro antes de iniciar la consulta o reproducción.
- La historia y el mapa conocido empiezan con el estado inicial de la partida; la información descubierta posteriormente no aparece en consultas anteriores.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Para un instante `t`, la historia refleja todos los eventos de la partida cuyo tiempo sea menor o igual que `t`. Si en `t` corresponde una decisión del jugador, el estado mostrado es justo antes de tomarla.
- **FR-002**: El jugador MUST poder consultar un instante del reloj virtual mediante `historia t` y el estado previo a una acción mediante `historia #k`; la primera acción vigente se consulta como `historia #1` y solo se numeran acciones vigentes.
- **FR-003**: El historial consultable empieza en el estado inicial. `historia #k` muestra el estado tras los eventos que correspondan y justo antes de la acción vigente número `k`. Una acción inexistente o un instante previo al inicio se rechaza con un mensaje claro.
- **FR-004**: Cada resumen MUST incluir como mínimo el reloj, la sala del jugador, su vida y estadísticas, inventario, efectos activos, enemigos de esa sala con su vida y el mapa conocido en el instante consultado.
- **FR-005**: Una consulta interactiva a un instante posterior al reloj actual se rechaza; no presenta un estado futuro como si fuera historia disponible.
- **FR-006**: Consultar historia no consume tiempo, no se registra como acción, no cambia el estado actual y no modifica ningún dato de la partida.
- **FR-007**: El pergamino conserva su límite de cinco acciones y es independiente de las consultas históricas: consultar no altera su historial ni cuenta como acción.
- **FR-008**: Al revertir acciones con el pergamino, las acciones revertidas y sus efectos dejan de formar parte de la línea de tiempo consultable vigente.
- **FR-009**: El sistema MUST permitir configurar `K` mediante `--checkpoint-cada K`, con un valor predeterminado seleccionado y justificado mediante mediciones reproducibles. No se conserva más de una copia completa del estado por cada `K` acciones del jugador; el estado inicial puede consultarse. Fuera de esas copias se conserva únicamente información necesaria para reconstruir los cambios.
- **FR-010**: Para responder una consulta histórica, el trabajo de reconstrucción no aplica ni deshace cambios de más de `K` acciones del jugador. La consulta no realiza solicitudes de red.
- **FR-011**: `--replay partida.log --hasta t` imprime el mismo resumen definido en FR-004 sin abrir la interfaz. Si la partida termina antes de `t`, imprime el estado final e informa explícitamente que terminó antes.
- **FR-012**: Guardar y cargar una partida conserva la historia completa que siga vigente, desde el inicio, y el mapa conocido correspondiente a cada instante consultable.
- **FR-013**: Un archivo de partida de la Parte I se rechaza con un mensaje claro de incompatibilidad; no se migra ni se carga silenciosamente.
- **FR-014**: Si `K` no es un valor positivo válido, el sistema rechaza la opción e informa el motivo sin alterar la partida.

### Key Entities *(include if feature involves data)*

- **Estado histórico**: La situación de la partida en un instante, incluidos los datos mínimos requeridos para el resumen y el conocimiento del mapa de ese momento.
- **Acción vigente**: Una decisión del jugador que permanece en la línea de tiempo después de las reversiones.
- **Historia de partida**: Los estados y cambios desde el inicio que permiten consultar o reproducir la línea de tiempo vigente.
- **Partida guardada**: Una partida persistida cuya historia y mapa conocido pueden recuperarse al cargarla.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Sobre una historia fija de al menos 5.000 acciones y con el valor predeterminado de `K`, se eligen al menos 30 puntos de consulta distribuidos por la historia y se mide cada uno 30 veces; el p95 de todas las mediciones es menor de 50 ms y también se documenta el máximo observado.
- **SC-002**: Antes de fijar el valor predeterminado, se comparan al menos tres valores positivos de `K` sobre la misma historia y los mismos puntos de consulta; se documentan sus percentiles 50 y 95 y el volumen conservado, y se elige el `K` mayor probado que cumpla SC-001.
- **SC-003**: En el 100 % de las pruebas de no alteración, los valores observables de la partida, el reloj, el conteo de acciones y el pergamino son idénticos antes y después de una consulta.
- **SC-004**: En todas las pruebas de paridad, `--replay ... --hasta t` y `historia t` presentan el mismo resumen cuando la partida alcanza `t`; en el 100 % de pruebas de finalización anticipada, el replay muestra el estado final y el aviso correspondiente.
- **SC-005**: En el 100 % de las pruebas de guardado y carga, se puede consultar desde el inicio la misma historia vigente y el mismo mapa conocido que antes de guardar.

## Assumptions

- Los instantes usan la misma unidad y precisión que el reloj virtual de la partida.
- Los números de acción son enteros positivos, comienzan en uno y se refieren a las acciones que siguen vigentes después de reversiones.
- Los archivos de partida de la Parte I se rechazan con un mensaje claro de incompatibilidad; no se migran.
- El valor predeterminado de `K` no se fija sin mediciones; su selección y justificación deben completarse antes de dar por lista la capacidad.
- La historia refleja el orden determinista de eventos ya ejecutados por la partida y no inventa información del mapa que el jugador todavía no conocía.

## Apéndice B — Escenarios de aceptación

### G18 — Rechazar un instante futuro interactivo

**Given** una partida activa cuyo reloj actual es `t_actual`, **When** el jugador solicita `historia t` con `t > t_actual`, **Then** se rechaza la consulta, se informa que ese instante aún no existe y la partida no cambia. (**FR-005, FR-006**)

### G19 — Excluir acciones revertidas

**Given** una línea de tiempo con acciones posteriores a un punto que el jugador revierte con el pergamino, **When** consulta tiempos o números de acción de la línea de tiempo resultante, **Then** las acciones revertidas y sus efectos no aparecen y la numeración vigente no las incluye. (**FR-002, FR-008**)

### G20 — Incluir todos los eventos simultáneos

**Given** dos o más eventos con tiempo `t` y una decisión del jugador que corresponde a `t`, **When** se consulta `historia t`, **Then** se incluyen todos los eventos de tiempo `t` en su orden determinista y se presenta el estado justo antes de la decisión. (**FR-001, FR-004**)

### G21 — No alterar la partida al consultar

**Given** una partida y un pergamino con valores conocidos, **When** se realiza una consulta histórica válida, **Then** no cambian el estado actual, el reloj, las acciones contabilizadas ni el historial del pergamino, y la consulta no se añade como acción. (**FR-006, FR-007**)

### G22 — Replay solicitado después del final

**Given** una partida que termina antes del instante `t` solicitado, **When** se ejecuta `--replay partida.log --hasta t`, **Then** se imprime el resumen del estado final y un aviso de que la partida terminó antes de `t`, sin abrir la interfaz. (**FR-004, FR-011**)

### G23 — Rechazo explícito de archivos de Parte I

**Given** un archivo de partida creado para la Parte I, **When** se intenta cargarlo, **Then** el sistema rechaza el archivo con un mensaje claro de incompatibilidad, sin migrarlo ni cargarlo silenciosamente. (**FR-013**)

### Trazabilidad de casos obligatorios

| Caso | Escenario de aceptación | Requisitos funcionales |
| --- | --- | --- |
| G18 | Rechazar un instante futuro interactivo | FR-005, FR-006 |
| G19 | Excluir acciones revertidas | FR-002, FR-008 |
| G20 | Incluir todos los eventos simultáneos | FR-001, FR-004 |
| G21 | No alterar la partida al consultar | FR-006, FR-007 |
| G22 | Replay solicitado después del final | FR-004, FR-011 |
| G23 | Rechazo explícito de archivos de Parte I | FR-013 |
