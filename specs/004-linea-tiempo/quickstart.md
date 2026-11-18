# Guía de validación: Línea de tiempo de CRIPTA

Ejecutar desde la raíz del repositorio con Python 3.12 y las dependencias de `requirements.txt` instaladas.

## Pruebas de regresión

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests\test_persistencia.py tests\test_consola_persistencia_replay.py tests\test_controlador_replay.py tests\test_historial_bloque3.py
```

**Resultado esperado**: pasan las pruebas existentes de persistencia, replay y reversión. La implementación añadirá pruebas de timeline para consultas por tiempo/acción, reconstrucción aislada, mapa conocido, estado aleatorio y truncamiento tras una reversión.

## Escenarios de la capacidad

1. Crear una historia fija de al menos 5.000 acciones con semilla y secuencia deterministas.
2. Distribuir al menos 30 instantes/puntos de consulta por la historia; medir cada uno 30 veces con el `K` predeterminado (200).
3. Comprobar p95 menor de 50 ms y registrar mediana, p95 y máximo de las mediciones.
4. Consultar `historia t` en tiempos antes, en y entre puntos de control; comparar cada resumen con una reproducción de referencia.
5. Consultar `historia #1`, `historia #K`, `historia #(K+1)` y el último número vigente; verificar que el resultado es anterior a la acción indicada.
6. Comparar puntos de control y reconstrucción con la misma historia mediante búsqueda binaria propia y lineal, re-simulación e inversión; verificar que el conocimiento del mapa, los movimientos y sus costos coinciden con la partida original.
7. Medir por separado lectura del índice, carga/restauración de un punto, memoria y consulta completa.
8. Revertir acciones con el pergamino; comprobar que no aparecen registros de acciones, cambios ni puntos posteriores al corte.
9. Guardar y cargar; comprobar que continúan disponibles la historia vigente y el mapa conocido. Intentar cargar un archivo Parte I y verificar rechazo explícito.
10. Ejecutar `--replay partida.log --hasta t` con un punto alcanzado y otro posterior al fin; comparar el primero con `historia t` y confirmar estado final/aviso en el segundo.

## Ejecución de benchmarks

El proyecto dispone de `--bench` para mediciones de estructuras y persistencia:

```powershell
.\.venv\Scripts\python.exe main.py --bench
```

Los casos de esta capacidad están incorporados al runner de benchmarks (`bench/casos/linea_tiempo.py`, T024/T025) para aceptar `K = 10, 50, 100` y otros valores, ejecutar las mismas consultas en todas las variantes y reportar mediana, p95, máximo y memoria. No se fija aquí una sintaxis adicional para seleccionar casos que el CLI actual no documenta.

### Resultado medido

La evidencia reproducible de T025 está en `docs/evidencia/2026-11-16T160604_9c6f61b_bench.json`. Sobre 5.000 acciones, el valor predeterminado `K = 200` obtuvo p95 de 20,4 ms, 20,6 ms y 22,9 ms en tres corridas; todas cumplen el límite p95 < 50 ms. Los máximos fueron 43,6 ms, 42,1 ms y 68,9 ms, y la memoria pico medida fue 2,80 MiB. El máximo se informa por separado; el criterio de aceptación se evalúa sobre p95.

La reconstrucción desde el inicio obtuvo p95 de 390,4 ms. Con `K = 200`, la búsqueda binaria propia localizó puntos de control con p95 de 0,004 ms, frente a 0,013 ms para la búsqueda lineal. La implementación reanuda desde el punto de control más cercano y vuelve a aplicar como máximo `K - 1` acciones. Los detalles de variantes, límites y exclusiones están en `specs/004-linea-tiempo/research.md`.

## Prueba manual de la interfaz de consola

Una vez implementada la opción, iniciar una partida local:

```powershell
.\.venv\Scripts\python.exe main.py --offline --cripta cripta-01
```

En una partida con acciones conocidas, ejecutar consultas `historia t` y `historia #k`, comparar el resumen y verificar que reloj, partida y pergamino no cambien. Esta prueba es manual; las pruebas automatizadas y el benchmark son los criterios reproducibles de aceptación.
