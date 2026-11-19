# Validación histórica de integración

Este registro describe el snapshot de cierre basado en `main` `87e166d` e integrado en `cierre-entrega` el 18 de noviembre de 2026. No corresponde a la validación vigente de `rama-version-prefinal`; los resultados actuales están en el [README principal](../../README.md) y en [`docs/DECISIONES.md`](../DECISIONES.md).

## Cambios revisados en ese snapshot

- Integración de optimizaciones de terreno y cazador con persistencia, Pygame y catálogos offline.
- Incorporación de snapshots para cripta-02 a cripta-06 y regresiones de carga, mapa, historia, guardado y carga.
- Ocultamiento de IDs, nombres y rastros de salas avistadas en los resúmenes históricos.
- Entrada de comandos en Pygame mediante F2 y reconstrucción de mapas grandes sin recorridos recursivos.
- Reportes de benchmark combinados para terreno/cazador y resolubilidad.

## Resultados conservados

| Prueba o medición | Resultado del snapshot |
| --- | --- |
| Suite antes de incorporar los mapas oficiales | 1 401 pruebas aprobadas. |
| Suite con los seis mapas offline | 1 382 pruebas aprobadas en la corrida registrada. |
| `IR A` sobre cripta-06 | Máximo de 0.530 ms en 100 muestras para la ruta ensayada; umbral de referencia: 5 ms. |
| Benchmark de terreno y cazador de cierre | Ocho escenarios, 30 repeticiones cada uno, cero discrepancias; cinco ciclos excedieron 20 ms y el máximo fue 43.1008 ms. |

La corrida de terreno/cazador que superó el límite se conserva en [`CRIPTA-II-terreno-benchmark-entrega.json`](CRIPTA-II-terreno-benchmark-entrega.json). No se presenta como evidencia aprobatoria.

## Datos oficiales y límites

En esa integración se incorporaron cinco criptas oficiales adicionales al catálogo offline y se mantuvo `cripta-05` bloqueada por su resultado NO RESOLUBLE, salvo uso explícito de `--forzar`. La API devolvió 404 para el cazador de catálogo específico del modo offline, por lo que la prueba de ese enemigo se limitó al snapshot local.

El reporte de la partida en vivo ejercitó una partida completa de cripta-02. No cubrió fallos de red, respuestas malformadas, incompatibilidad de versiones ni agotamiento del presupuesto de solicitudes; la evidencia actual de API se enlaza desde el [índice de entrega](README.md).
