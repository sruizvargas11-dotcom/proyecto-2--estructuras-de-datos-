# Decisiones de niebla, antorcha y viaje automático

Registro técnico correspondiente al snapshot `main` en `87e166d`, del 17 de noviembre de 2026. La especificación vigente está en [`specs/002-niebla-viaje/spec.md`](../../specs/002-niebla-viaje/spec.md); este archivo conserva resultados históricos de esa versión.

## Decisiones

- El conocimiento del jugador se conserva separado del mapa real. La vista solo presenta salas exploradas y la existencia, sin identidad, de las avistadas.
- `IR A` calcula rutas sobre salas exploradas y puertas recordadas como abiertas. Usa Dijkstra porque los costos de tránsito pueden variar; BFS solo minimiza cantidad de pasos.
- Cada paso del viaje aplica el movimiento normal, sus costos y los eventos del reloj. El viaje se recalcula al observar puertas y se detiene ante sus condiciones de parada.
- Antorcha, guardado, retroceso, historia y replay conservan los cambios de conocimiento sin revelar el estado actual en consultas históricas.

## Evidencia del snapshot

| Medición | Resultado registrado |
| --- | --- |
| Pruebas focalizadas de las capacidades 002 y relacionadas | 58 aprobadas en `87e166d`. |
| `IR A` en cripta-06 | 300 salas exploradas; ruta de mayor costo alcanzable desde la entrada: 141 hacia 284, costo 1340. |
| Tiempo de un paso | 100 muestras: mediana 0.118 ms, p95 0.240 ms, máximo 0.530 ms; umbral de referencia: 5 ms. |

La medición cargó el esqueleto antes del cronómetro y no hizo solicitudes HTTP durante el intervalo medido. Cubre esa ruta y estado, no todos los pares de salas ni todas las combinaciones de puertas. Las muestras y el script están disponibles en [`cripta-06-benchmark-002.json`](cripta-06-benchmark-002.json) y el repositorio conserva evidencia adicional bajo `docs/entrega/`.
