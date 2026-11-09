# Investigación: Línea de tiempo de CRIPTA

## Contexto del código existente

- `modelo/partida.py` reúne el estado de partida y sus referencias al mundo y al jugador.
- `modelo/reloj.py` comparte un `random.Random`; el formato persistente existente ya conserva su estado aleatorio.
- La agenda de eventos es una estructura heap propia y ordena por tiempo y secuencia. Las entradas de evento contienen datos tipados, no callbacks serializables.
- El conocimiento del mapa se representa con marcas de tiempo de rastro por sala; el rastro afecta qué salas se consideran conocidas/recientes.
- `controlador/guardado.py` carga el estado global y recorre los bloques de sala para reconstruir y validar la partida completa.
- `persistencia/PartidaBinaria.py` utiliza un encabezado binario, índice de salas y bloques; puede leer bloques por desplazamiento.
- `persistencia/estado_partida.py` contiene la codificación/decodificación del estado actual, incluido `getstate()`/`setstate()` del generador aleatorio.
- `controlador/controlador_replay.py` reproduce comandos en una partida nueva; la ruta actual no es una reconstrucción desde puntos de control.
- `bench/bench_bloque3.py` ya mide escenarios de persistencia, pero sus casos actuales no equivalen a medir una reconstrucción histórica completa.
- No se encontró en este checkout `docs/equipo/revision_persistencia.md`, citado en la solicitud. El valor de aproximadamente 72 ms para cargar 5.000 salas se trata aquí como dato comunicado por el solicitante, no como una medición reproducida durante esta planificación.

## Decisiones de diseño

### Registro permanente y pergamino

**Decision**: Mantener un arreglo permanente de registros de acciones con número e instante del reloj, separado del historial de deltas del pergamino. Para la reconstrucción hacia atrás, conservar además información de cambios suficiente para invertirlos; no depender de los deltas consumibles del pergamino.

**Rationale**: Las consultas requieren el historial completo vigente, pero el pergamino conserva como máximo cinco intervalos y los consume al retroceder.

**Alternatives considered**: Reutilizar el historial del pergamino se descarta porque es limitado, consumible y no representa toda la historia.

### Selección de puntos de control

**Decision**: Mantener puntos de control completos en un arreglo ordenado por tiempo, con el estado inicial y un punto cada `K` acciones. Para `historia t`, usar búsqueda binaria propia del último punto con tiempo menor o igual que `t`. Para `historia #k`, con numeración desde uno y consulta inmediatamente anterior a la acción, usar el índice `(k - 1) // K`.

**Rationale**: La fórmula `(k - 1) // K` corresponde a la posición de acción basada en cero y evita seleccionar el estado posterior a la acción consultada cuando `k` es múltiplo de `K`. La búsqueda binaria cumple la selección por tiempo sin usar `bisect`.

**Alternatives considered**:

| Alternativa | Evaluación |
|---|---|
| Árbol BST simple | Puede degenerar con inserciones de tiempos crecientes y agrega estructura innecesaria cuando solo se agrega/corta al final. |
| AVL | Mantiene equilibrio, pero sus rotaciones no aportan valor proporcional al patrón de inserción y truncado final. |
| Tabla hash | No resuelve la consulta de predecesor “último tiempo menor o igual que `t`”. |
| Búsqueda lineal | Se conserva como referencia de medición; no es la estrategia seleccionada para consultas por tiempo. |
| Sin puntos de control | No cumple el límite de reconstrucción de `K` acciones. |

### Estado que se conserva en cada punto

**Decision**: El punto contiene una copia completa y directamente restaurable del estado necesario para reconstruir la partida en ese límite: estado del mundo y jugador, reloj, agenda de eventos, `random.Random.getstate()` y conocimiento del mapa/niebla. No incluye caché LRU ni historial del pergamino.

**Rationale**: Omitir cualquiera de los componentes que afecta a las decisiones futuras podría alterar el orden o los resultados al reproducir; la caché y el pergamino no son parte del estado histórico que debe restaurarse.

**Alternatives considered**: Copiar el grafo completo a ciegas o incluir la caché/el pergamino aumenta el costo y mezcla estado histórico con estado auxiliar o consumible.

### Reconstrucción

**Decision**: Crear la partida temporal aislada y restaurar el punto elegido; nunca aplicar deltas sobre la partida real. Implementar y medir dos variantes antes de escoger la usada: (a) simular hacia adelante desde el punto anterior; (b) invertir cambios desde el estado actual si la distancia es menor de `K` acciones. El replay hasta un instante reutiliza esta reconstrucción y no crea vista.

**Rationale**: La primera variante parte de un estado explícito; la segunda puede reducir trabajo cuando el estado actual está cerca, pero exige un registro permanente e invertible. El conocimiento del mapa que mantiene Niebla (José) debe estar en el punto. La reproducción debe respetar los movimientos y costos de Terreno (Daniel), manteniendo la paridad con la partida original.

**Alternatives considered**: Elegir una variante sin comparar mediciones se descarta; las mediciones planificadas decidirán cuál ofrece mejor resultado manteniendo la paridad de estado.

### Persistencia rápida de puntos de control

**Decision**: Probar bloques de punto de control versionados, de longitud explícita y restaurables directamente, con una tabla compacta ordenada de metadatos `(tiempo, número de acción, desplazamiento, longitud)`. Cargar/consultar el índice una vez y leer el bloque seleccionado por desplazamiento, evitando invocar la carga completa de todas las salas para cada consulta. El formato debe conservar orden estable de registros y la secuencia de la agenda; los eventos se reconstruyen desde sus datos tipados.

**Rationale**: La ruta actual de carga reconstruye el grafo completo de salas. Los bloques direccionables permiten medir el costo real de restaurar un punto sin volver a decodificar toda la partida.

**Alternatives considered**:
- Reutilizar la carga completa existente por consulta: referencia de corrección, pero el dato comunicado de ~72 ms para 5.000 salas ya supera el umbral y requiere verificación.
- Serializar todo el historial dentro de un único bloque global: obliga a decodificar datos no requeridos para localizar el punto y no facilita medir la restauración de un solo punto.

**Validation required**: Medir por separado la lectura del índice, lectura/decodificación/restauración de un punto y la consulta completa. No se presupone que los bloques propuestos alcancen SC-001 hasta obtener resultados de `--bench`.

### Truncamiento después del pergamino

**Decision**: Al revertir a un punto, truncar el final del registro permanente de acciones, el registro permanente de cambios asociado y todos los puntos de control posteriores al punto revertido. No alterar el límite ni el historial consumible del pergamino desde una consulta histórica.

**Rationale**: La línea de tiempo consultable solo incluye acciones vigentes después de una reversión.

**Alternatives considered**: Mantener acciones revertidas como si siguieran vigentes contradice FR-008; modificar el pergamino por consultar contradice FR-006/007.

## Plan de mediciones

Todas las variantes se medirán sobre la misma historia fija de al menos 5.000 acciones y los mismos puntos. Para SC-001 se usarán al menos 30 puntos distribuidos por la historia y 30 mediciones por punto. Se registrarán la mediana, p95 y máximo; el máximo se informa aunque el umbral se evalúa sobre p95. También se medirá memoria.

| Comparación | Datos a registrar |
|---|---|
| `K = 10, 50, 100` y otros valores positivos | Mediana, p95, máximo, volumen/memoria conservada y cumplimiento SC-001 |
| Búsqueda binaria propia frente a búsqueda lineal | Tiempo de localización del punto para los mismos tiempos consultados |
| Re-simulación frente a inversión | Tiempo total de consulta, p95, máximo, memoria y equivalencia del resumen |
| Carga de punto de control | Lectura, decodificación y restauración por separado |
| Guardado/carga con historia | Preservación de historia, mapa conocido y rechazo explícito de archivos Parte I |

No se registran resultados numéricos de estas mediciones en esta fase. El valor predeterminado de `K` se fijará después de ejecutar el benchmark y será el mayor valor probado que cumpla SC-001.
