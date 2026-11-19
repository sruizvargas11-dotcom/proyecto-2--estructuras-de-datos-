# §5.3 · Mapa conocido, antorcha y viaje automático (002)

**Responsable:** José Fabio Barrantes. **Versión validada:** `main`, commit `87e166d`, 17 de noviembre de 2026.

[Especificación 002](https://github.com/sruizvargas11-dotcom/proyecto-2--estructuras-de-datos-/blob/87e166d/specs/002-niebla-viaje/spec.md) · [Plan técnico](https://github.com/sruizvargas11-dotcom/proyecto-2--estructuras-de-datos-/blob/87e166d/specs/002-niebla-viaje/plan.md) · [Trazabilidad de aceptación](https://github.com/sruizvargas11-dotcom/proyecto-2--estructuras-de-datos-/blob/87e166d/docs/evidencia/2026-11-12-niebla-viaje-trazabilidad.md)

## Problema y alternativas

El jugador debe distinguir salas desconocidas, avistadas y exploradas, y recordar el último estado observado de una puerta. La ruta de `IR A` debe usar ese conocimiento. Un recorrido lineal por las salas en cada consulta sería sencillo, pero crecería con el tamaño del mapa. Un arreglo indexado directamente por ID exigiría IDs densos o reservar huecos. Buscar en el grafo real del cazador revelaría rutas que el jugador todavía desconoce. BFS tampoco garantiza el menor costo cuando el terreno tiene pesos distintos.

## Decisión y complejidad

- **Conocimiento separado.** `modelo/conocimiento.py` usa un vector de registros ordenado por ID y recuerdos de puertas por sala. La búsqueda de una sala cuesta O(log V) y la consulta de puerta O(log V + d), con V salas y d salidas de esa sala. Se guardan referencias a los extremos para actualizar vecinas sin recorrer el mapa. Visitar y revelar cuesta en proporción a las salidas examinadas de las salas afectadas.
- **Antorcha y retroceso.** La antorcha revela las vecinas al entrar usando la topología ya cargada. Las puertas remotas no se dan por observadas. Los cambios se registran como deltas para revertirlos y se conservan en el guardado. La 004 reutiliza el conocimiento al reconstruir la partida.
- **Viaje.** Dijkstra inverso sobre el subgrafo de salas exploradas y puertas recordadas abiertas. Comparte con el cazador la cola de prioridad propia, pero cada uno decide sobre información diferente. Con V salas y E salidas, el peor caso de un paso es O(V + E log(E + 1)) por las inserciones y extracciones del heap. El empate elige la primera vecina de menor ID. Cada paso usa el movimiento normal y la bitácora registra los movimientos efectivamente ejecutados.

La implementación conserva la representación y el algoritmo del plan. La evidencia inicial usó la cripta offline de seis salas. Esta auditoría amplió la medición a la cripta oficial publicada, sin cambiar la decisión de diseño.

## Resultados y límites

| Verificación | Resultado |
|---|---|
| Pruebas focalizadas de 002, historia y resolubilidad | 58 aprobadas en `87e166d`. |
| Partida offline en consola | MAPA, antorcha, movimiento, detención de IR A por enemigos, guardado, carga e HISTORIA #1. |
| Paso de IR A, cripta oficial de referencia | Cripta-06, versión `f9ed9afa683d`, 300 salas exploradas y puertas observadas. Ruta alcanzable de mayor costo desde la entrada 141: destino 284, costo 1.340. En 100 muestras: mediana 0,118 ms, p95 0,240 ms y máximo 0,530 ms. Límite: 5 ms. |

Se cargó el esqueleto oficial antes de medir. Durante la medición no se hizo ninguna petición ni se abrió una vista. Se conservaron las puertas cerradas. El resultado cubre la ruta elegida, no todos los pares ni todos los estados posibles de las puertas. [Muestras JSON](./cripta-06-benchmark-002.json) y [script de medición](./medir-cripta-06-002.py), que se puede ejecutar desde la raíz del repositorio con PYTHONPATH apuntando a esa raíz.

La versión de cierre filtra también la vista histórica: HISTORIA 0 muestra «sala avistada» y omite su nombre e ID. El mismo formato se usa en consola, Pygame y replay histórico.
