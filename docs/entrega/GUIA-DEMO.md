# Guía de demostración de CRIPTA II

Ejecutá los comandos desde la raíz del repositorio.

## Cómo demostrar la Parte II

```powershell
python -m pip install -r requirements.txt
python main.py --offline --cripta cripta-01
python main.py --offline --gui --cripta cripta-01
python main.py --offline --verificar cripta-01
python main.py --cripta cripta-06 --checkpoint-cada 200
python main.py --offline --replay partidas/bitacoras/ARCHIVO.log --hasta 100
python main.py --bench --bench-caso niebla-viaje --salida niebla.json
python main.py --bench --salida terreno-y-resolubilidad.json
```

| Comando de juego | Uso |
|---|---|
| `MAPA` o `M` | Muestra lo explorado y señala las salas avistadas sin revelar sus nombres. |
| `IR A <id>` | Viaja hacia un destino explorado. Cada paso consume lo que cuesta el movimiento normal. El juego explica el motivo de parada. |
| `HISTORIA <t>` / `HISTORIA #<k>` | Consulta el reloj virtual o el estado previo a una acción, sin avanzar la partida. |

En Pygame, presioná **F2**, escribí el comando y presioná Enter. Esc cancela. F5 muestra u oculta el minimapa. El reporte de resolubilidad aparece al iniciar. `--forzar` permite continuar ante un veredicto no resoluble o no verificable. No permite ignorar datos inválidos. La cripta offline incluye el cazador. Usá la caché por defecto para la demo. Una caché de una sola ficha puede impedir incorporar una sala con enemigos cuando la única ficha está protegida.

## Pruebas desde la raíz

```powershell
python -m pytest -q tests/test_terreno_cazador.py tests/test_bench_terreno_cazador.py
python -m pytest -q tests/test_niebla_viaje.py tests/test_bench_niebla_viaje.py
python -m pytest -q -k resolubilidad
python -m pytest -q tests/test_linea_tiempo_integraciones.py tests/test_linea_tiempo_limites_modelo.py tests/test_linea_tiempo_g22.py tests/test_linea_tiempo_guardado.py
python -m pytest -q
```

El equipo usó la configuración Spec Kit 1.2.6.dev0 con Copilot y Antigravity. Las correcciones de cierre siguen los requisitos existentes de las specs 001–004. La versión consta en los manifiestos incluidos en el repositorio. Para jugar y ejecutar las pruebas basta con las dependencias de Python.


## Demostración reproducible

La partida offline de la semilla 354 se completó con 30 puntos de vida iniciales, en ocho acciones y con un punto de vida al llegar a la salida. La bitácora adjunta se puede reproducir desde la raíz del proyecto:

```powershell
python main.py --offline --replay docs/entrega/CRIPTA-II-victoria-semilla-354.replay
```
