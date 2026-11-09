# Guía de validación: Línea de tiempo de CRIPTA

Ejecutar desde la raíz del repositorio con Python 3.12 y las dependencias de `requirements.txt` instaladas.

## Pruebas de regresión

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests\test_persistencia.py tests\test_consola_persistencia_replay.py tests\test_controlador_replay.py tests\test_historial_bloque3.py
```

**Resultado esperado**: pasan las pruebas existentes de persistencia, replay y reversión. La implementación añadirá pruebas de timeline para consultas por tiempo/acción, reconstrucción aislada, mapa conocido, estado aleatorio y truncamiento tras una reversión.

## Escenarios de la capacidad

1. Crear una historia fija de al menos 5.000 acciones con semilla y secuencia deterministas.
2. Distribuir al menos 30 instantes/puntos de consulta por la historia; medir cada uno 30 veces con el `K` predeterminado.
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

Los casos de esta capacidad deberán incorporarse al runner de benchmarks para aceptar `K = 10, 50, 100` y otros valores, ejecutar las mismas consultas en todas las variantes y reportar mediana, p95, máximo y memoria. No se fija aquí una sintaxis adicional para seleccionar casos que el CLI actual no documenta.

## Prueba manual de la interfaz de consola

Una vez implementada la opción, iniciar una partida local:

```powershell
.\.venv\Scripts\python.exe main.py --offline --cripta cripta-01
```

En una partida con acciones conocidas, ejecutar consultas `historia t` y `historia #k`, comparar el resumen y verificar que reloj, partida y pergamino no cambien. Esta prueba es manual; las pruebas automatizadas y el benchmark son los criterios reproducibles de aceptación.
