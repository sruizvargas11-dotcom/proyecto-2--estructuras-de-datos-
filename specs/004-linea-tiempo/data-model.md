# Modelo de datos: Línea de tiempo de CRIPTA

Este modelo describe los datos necesarios para cumplir `spec.md`; no prescribe nombres de clases o módulos.

## Entidades

### Línea de tiempo

Representa la historia vigente desde el inicio de la partida.

| Campo | Descripción | Validación / regla |
|---|---|---|
| Registros de acciones | Arreglo permanente ordenado con una entrada por decisión del jugador vigente. | Numeración entera positiva desde 1; contiene solo acciones vigentes. |
| Registros de cambios | Información suficiente para reproducir los cambios o invertirlos. | Persiste aparte de los deltas consumibles del pergamino. |
| Puntos de control | Arreglo de estados completos restaurables, ordenado por tiempo y asociado al conteo de acciones. | Incluye el estado inicial y un punto cada `K` acciones; `K` positivo. |
| Valor `K` | Intervalo configurable de puntos de control. | El predeterminado se decide por medición: mayor valor probado que cumpla SC-001. |

La reversión con el pergamino corta las acciones y registros de cambios posteriores al punto revertido, además de los puntos de control posteriores. Una consulta no modifica ninguno de estos arreglos.

### Registro de acción

Representa una acción de jugador que permanece vigente.

| Campo | Descripción | Validación / regla |
|---|---|---|
| Número de acción | Identificador ordinal de la acción vigente. | Empieza en 1 y no incluye acciones revertidas. |
| Instante del reloj | Tiempo virtual asociado a la acción. | Usa la unidad y precisión del reloj de la partida. |
| Datos de acción necesarios para replay | Datos ya requeridos por el flujo de reproducción. | El replay debe conservar el determinismo de la partida. |

El historial del pergamino es independiente y conserva su propio límite de cinco acciones/deltas conforme a `spec.md`.

### Punto de control

Representa una instantánea completa del estado necesario para reconstruir la línea de tiempo.

| Campo | Descripción |
|---|---|
| Instante del reloj | Tiempo virtual de la instantánea, para selección por `historia t`. |
| Conteo de acciones | Número de acciones vigentes que preceden a la instantánea. |
| Estado del juego | Estado de jugador, mundo, entidades, reloj y datos que afectan el resumen o la simulación. |
| Estado aleatorio | Estado recuperable de `random.Random`, equivalente al guardado con `getstate()`. |
| Agenda de eventos | Eventos pendientes, orden determinista (tiempo y secuencia) y siguiente secuencia necesaria para continuar. |
| Conocimiento del mapa | Estado conocido/rastro de cada sala en ese punto. |

No contiene caché LRU ni historial del pergamino. Su representación persistente debe poder restaurarse como bloque independiente.

### Reconstrucción temporal

Estado de trabajo aislado creado para una consulta.

| Campo | Descripción |
|---|---|
| Punto de origen | Punto de control elegido según instante o acción. |
| Estado temporal | Copia restaurada sobre la que se avanza o se invierten cambios. |
| Resultado | Resumen definido por FR-004 o estado final de replay. |

No comparte mutaciones con la partida real, no consume el pergamino ni efectúa solicitudes de red.

## Relaciones

- Una línea de tiempo contiene registros de acciones, registros de cambios y puntos de control.
- Un punto de control corresponde a un límite del registro de acciones y captura el estado completo en ese límite.
- La reconstrucción temporal usa un punto de control y los registros necesarios para llegar al instante solicitado.
- El pergamino es independiente de la línea de tiempo consultable; su reversión trunca la línea de tiempo vigente.
- Una partida guardada conserva la línea de tiempo vigente y el conocimiento del mapa de cada punto consultable.

## Reglas de selección y validación

- `historia t` selecciona mediante búsqueda binaria propia el último punto cuyo instante sea menor o igual que `t`.
- `historia #k` consulta el estado inmediatamente anterior a la acción vigente `k`; usa la posición de acción cero-based `(k - 1)` para localizar el punto correspondiente con `(k - 1) // K`.
- No se acepta un instante anterior al inicio, posterior al reloj actual interactivo, ni un número de acción inexistente.
- El trabajo de reconstrucción no excede `K` acciones del jugador.
- Si un evento y una decisión coinciden en el tiempo, se conserva el orden determinista y se consulta después de los eventos del instante y antes de la decisión.
- Los archivos de partida de la Parte I se rechazan con un mensaje claro de incompatibilidad; no se migran.
