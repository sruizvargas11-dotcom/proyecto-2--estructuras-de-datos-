# Contrato de persistencia de puntos de control

Contrato interno derivado de FR-009, FR-010 y FR-012 y de las decisiones de diseño proporcionadas.

## Representación lógica

- La historia contiene el registro permanente de acciones y los registros necesarios para reconstruirlas; no reutiliza como historial permanente los deltas consumibles del pergamino.
- Los puntos de control completos se ordenan por tiempo, incluyen el estado inicial y se crean con el intervalo `K`.
- Cada punto contiene reloj, estado del juego, estado de `random.Random`, agenda de eventos y conocimiento del mapa.
- Los puntos no contienen la caché LRU ni el historial del pergamino.
- La agenda conserva el orden por tiempo y secuencia; los eventos se reconstruyen desde datos tipados.

## Acceso y restauración

- La tabla de metadatos permite localizar puntos de control en un arreglo y se busca con algoritmos propios.
- Un bloque de punto debe poder localizarse y restaurarse sin decodificar el grafo completo de todas las salas por cada consulta.
- La reconstrucción ocurre en estado temporal aislado. La variante hacia adelante o hacia atrás se elige con mediciones comparativas; no se prescribe una ganadora antes de medir.
- La lectura/decodificación/restauración de un punto se mide separada de la búsqueda y del costo total de consulta.

## Persistencia y reversión

- Guardar/cargar conserva la historia vigente y el conocimiento del mapa desde el inicio.
- Al revertir, se truncan las acciones, cambios y puntos de control posteriores al límite vigente.
- Los archivos de Parte I se rechazan explícitamente, sin migración silenciosa.
- El tamaño/versión/codificación física de los bloques se decidirá y validará mediante benchmarks; el contrato no atribuye al formato propuesto un rendimiento todavía no medido.
