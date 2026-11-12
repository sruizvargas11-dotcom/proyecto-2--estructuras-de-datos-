# Validación de la capacidad 002

Fecha: 2026-11-12. Rama: `spec/jose`. Base: `e5bd543`. Especificación: `c2c5528`.
Plan y tareas: `8524838`. Las mediciones incluyen la implementación local.

| Verificación | Resultado |
|---|---|
| Niebla, antorcha, viaje, guardado, retroceso y replay | 38 aprobadas |
| Niebla más contrato del benchmark | 42 aprobadas |
| Niebla, benchmark y regresiones focalizadas de vistas | 69 aprobadas |
| Suite de consola y Pygame en Antigravity | 288 aprobadas |
| Regresión del proyecto sin la marca rendimiento | 1218 aprobadas, 3 deseleccionadas, 275,04 s |

La regresión se ejecutó en una copia local escribible. En el entorno de ejecución,
la carpeta original rechazaba el regreso mediante os.chdir después de una prueba.
Esa prueba pasó de forma aislada y dentro de la regresión en la copia. Se verificaron
los hashes de los archivos de implementación y prueba de la 002 contra esa copia.

```powershell
python -m pytest -q tests/test_niebla_viaje.py tests/test_bench_niebla_viaje.py
python -m pytest -q tests/test_vista_consola.py tests/vista
python -m pytest -q -m "not rendimiento"
python main.py --bench --bench-caso niebla-viaje --salida docs/evidencia/2026-11-12-niebla-viaje-benchmark.json
```

El benchmark registró 100 muestras por operación sobre las seis salas exploradas
de cripta-01. El paso de viaje tuvo p95 de 0,0239 ms y máximo de 0,0444 ms,
frente al límite de 5 ms. El resultado aplica a ese mapa de referencia.

- [Datos completos del benchmark](2026-11-12-niebla-viaje-benchmark.json)
- [Trazabilidad de los 34 escenarios](2026-11-12-niebla-viaje-trazabilidad.md)

La prueba de historia verifica la reconstrucción aislada del modelo. La consulta
desde la interfaz histórica corresponde a la integración con la 004.
