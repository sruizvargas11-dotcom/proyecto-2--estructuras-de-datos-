# Contrato de CLI: Línea de tiempo

Contrato derivado de `spec.md` (FR-001–FR-014, SC-001–SC-005).

## Consulta interactiva

| Forma | Resultado |
|---|---|
| `historia t` | Resume el estado tras todos los eventos con tiempo `<= t`; si hay decisión del jugador en `t`, el resumen es previo a esa decisión. |
| `historia #k` | Resume el estado inmediatamente anterior a la acción vigente número `k`; la numeración empieza en 1. |

El resumen incluye reloj, sala, vida y estadísticas del jugador, inventario, efectos activos, enemigos de la sala con su vida y mapa conocido del instante. La consulta no consume tiempo, no se registra como acción, no cambia la partida ni el pergamino, y no realiza solicitudes de red.

Se rechazan con mensaje claro los instantes anteriores al inicio o posteriores al reloj interactivo actual y los números de acción inexistentes. Las acciones revertidas no forman parte de la numeración vigente.

## Configuración de puntos de control

`--checkpoint-cada K` establece un `K` positivo. Un valor inválido se rechaza con el motivo y sin alterar la partida. El valor predeterminado será el mayor `K` probado que cumpla el p95 de SC-001; su valor debe justificarse con mediciones reproducibles antes de fijarlo.

## Replay

`--replay partida.log --hasta t` emite el mismo resumen que `historia t` cuando la partida alcanza `t`, sin abrir la vista ni realizar solicitudes de red. Si la partida termina antes, emite el resumen del estado final y un aviso de que terminó antes de `t`.

## Guardado y compatibilidad

Guardar y cargar conserva la historia vigente desde el inicio y el mapa conocido correspondiente. Un archivo de partida de Parte I se rechaza con un mensaje claro de incompatibilidad; no se migra ni se carga silenciosamente.
