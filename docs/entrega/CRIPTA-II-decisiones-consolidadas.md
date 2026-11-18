# CRIPTA II · Decisiones de diseño para revisión

Propuesta de cierre basada en `main` `87e166d` y las correcciones locales del 17 de noviembre. Este documento complementa el [Documento de Decisiones existente](https://github.com/sruizvargas11-dotcom/proyecto-2--estructuras-de-datos-/blob/87e166d/docs/DECISIONES.md). Cada responsable puede comprobar su sección antes de integrarla.

## §5.1 · Rutas de terreno y cazador (001)
[Spec](https://github.com/sruizvargas11-dotcom/proyecto-2--estructuras-de-datos-/blob/87e166d/specs/001-terreno-cazador/spec.md) · [Plan](https://github.com/sruizvargas11-dotcom/proyecto-2--estructuras-de-datos-/blob/87e166d/specs/001-terreno-cazador/plan.md)

Las aristas tienen costos positivos y variables. BFS minimiza pasos, mientras que Dijkstra minimiza el costo. Se eligió una búsqueda inversa desde el jugador para compartir distancias entre cazadores, con cola de prioridad propia y desempate determinista. Con V salas y E salidas, la fase de heap puede insertar O(E) candidatos. Una búsqueda compartida evita repetirla por cada cazador con el mismo objetivo. Sigue el plan. El ajuste de cierre reutiliza el índice propio para IDs densos y conserva búsqueda binaria con IDs dispersos. La evidencia original compara estrategias y perfiles de rango en el fixture de 256 salas. La prueba actual con carga nueva está en §5.6. El cazador offline está disponible en cripta-01. El ID ent_cazador no estaba disponible en el catálogo del servidor durante la verificación.

## §5.2 · Validez de rutas (001)
La caché evita recalcular cuando el jugador sigue en la misma sala y las puertas conservan su estado. Recalcular siempre evita mantener estado, pero desperdicia búsquedas con puertas estables. La decisión del plan se conserva. Comparar puertas cuesta O(E) incluso al acertar. Al cambiar la sala objetivo o las puertas se rehacen las aristas inversas y las distancias. La evidencia de terreno/cazador compara uso compartido e individual con cambios cada 1 y 100 ciclos, y comprueba decisiones contra la referencia. Los costos varían por topología, accesibilidad y frecuencia de invalidación.

## §5.3 · Mapa conocido (002)
Ver [sección de José](CRIPTA-II-decisiones-002-Jose-cierre.md). La ruta usa el subgrafo conocido y comparte la estructura de prioridad con la 001. La evidencia de cierre usa las 300 salas de la cripta oficial de referencia.

## §5.4 · Resolubilidad (003)
[Spec](https://github.com/sruizvargas11-dotcom/proyecto-2--estructuras-de-datos-/blob/87e166d/specs/003-resolubilidad/spec.md) · [Plan](https://github.com/sruizvargas11-dotcom/proyecto-2--estructuras-de-datos-/blob/87e166d/specs/003-resolubilidad/plan.md)

Se comparó repetir BFS desde el inicio por llave con ampliar la frontera a medida que aparecen llaves. Se tomó la segunda opción, conforme al plan. La expansión evita recorrer el grafo completo por cada llave, y usa sus índices y frontera para obtener bloqueos y dependencias. El costo combina el recorrido de salas/salidas con búsquedas en índices ordenados y el tratamiento de dependencias. La referencia publicada alcanzó p95 16,074 ms en 100 muestras según quickstart de 003. Las cadenas sintéticas comparan ambas alternativas en tres escalas. La verificación usa el contrato de llaves y topología. No reproduce combate, trampas ni supervivencia.

## §5.5 · Historia y checkpoints (004)
[Spec](https://github.com/sruizvargas11-dotcom/proyecto-2--estructuras-de-datos-/blob/87e166d/specs/004-linea-tiempo/spec.md) · [Plan](https://github.com/sruizvargas11-dotcom/proyecto-2--estructuras-de-datos-/blob/87e166d/specs/004-linea-tiempo/plan.md)

Guardar el estado en todas las acciones consume O(A × S) para A acciones y estado de tamaño S. El enfoque elegido guarda acciones y puntos periódicos, y reconstruye hacia adelante en una copia aislada. El índice temporal usa búsqueda binaria y la consulta previa a una acción calcula el bloque a partir de k. Con P puntos y costo de simulación C, la reconstrucción combina el costo de restaurar el estado, la localización del punto y hasta K acciones. La referencia sin checkpoints puede reproducir toda la historia.

La evidencia original de 5.000 acciones registra p95 de 5,7, 9,0, 12,4 y 20,4 ms para K de 10, 50, 100 y 200. La referencia sin puntos registró 390,4 ms. K=200 redujo memoria y mantuvo el p95 bajo 50 ms en las tres corridas publicadas, aunque una observó un máximo de 68,9 ms. El plan contemplaba inversión hacia atrás. La evidencia final compara reconstrucción hacia adelante con reconstrucción desde el inicio. La inversión hacia atrás quedó sin medir. En mapas grandes, la copia de cierre reserva las identidades de las salas y sus recuerdos antes de copiar enlaces para evitar agotar la pila. Las cifras anteriores corresponden al fixture documentado en la sección 4.14 original.

## §5.6 · Agenda y retroceso bajo carga nueva

Se conservan el heap de agenda y los deltas de retroceso. Un heap mantiene inserciones y extracciones O(log H) con H eventos, mientras que una lista ordenada trasladaría el costo a los desplazamientos de inserción. El retroceso aplica cambios del intervalo en orden inverso en lugar de copiar el mundo entero. Su costo depende de los deltas y de las operaciones que invierte. Los checkpoints de la línea de tiempo cumplen una función diferente: permiten consultar fuera de los cinco intervalos del pergamino.

El ensayo adjunto usa el mismo fixture de 256 salas y 20 actores. Compara guardianes y salidas de costo fijo con cazadores y costos variables, en el motor actual, con 1.000 ciclos y 200 retrocesos por perfil. Es una comparación controlada de carga, no una medición del ejecutable histórico de la Parte I ni de la cripta oficial. [Resultados](CRIPTA-II-medicion-estructuras.json) · [Script](medir-estructuras-CRIPTA-II.py). La carga nueva aumenta el costo del ciclo y debe contrastarse con el límite de 20 ms. El tiempo total de ciclo incluye IA, agenda y gestión de intervalos, por lo que no estima el tiempo exclusivo del heap.


| Carga | Ciclo mediana | Ciclo p95 | Ciclo máximo | Retroceso p95 |
|---|---:|---:|---:|---:|
| Costo fijo y guardianes | 0,397 ms | 0,653 ms | 1,383 ms | 0,142 ms |
| Costos variables y cazadores | 12,201 ms | 16,849 ms | 57,204 ms | 0,306 ms |

Con la carga II, el p95 está por debajo de 20 ms, pero el máximo lo supera. Los datos no cierran el límite para la carga de referencia. Esta corrida usó Windows 11 y Python 3.12.10. Los checkpoints y la agenda se ejecutan con el programa actual en ambos perfiles.

## Repetición contractual de terreno y cazador

La repetición contractual en el equipo de cierre completó 8 escenarios, 30 repeticiones por escenario y 240.000 ciclos. Las decisiones coincidieron con la referencia. Hubo 5 ciclos por encima de 20 ms y el máximo fue 43,1008 ms. Este equipo no reprodujo el cumplimiento del máximo obtenido en el informe original. [JSON de cierre](CRIPTA-II-terreno-benchmark-entrega.json).
