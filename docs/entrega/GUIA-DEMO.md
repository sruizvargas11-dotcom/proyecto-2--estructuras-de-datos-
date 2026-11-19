# Guía de uso y demostración

Ejecuta los comandos desde la raíz del repositorio y con Python 3.12.

## Instalar y ejecutar

```console
python -m pip install -r requirements.txt
python main.py --offline --cripta cripta-01
python main.py --offline --gui --cripta cripta-01
python main.py --offline --verificar cripta-01
```

Para iniciar desde la API, omite `--offline`; se requiere conectividad y disponibilidad del servicio.

## Recorrido recomendado

Durante una partida, prueba los comandos `MAPA`, `IR A <id>`, `HISTORIA <t>` y `HISTORIA #<k>`. En consola, `H` muestra la ayuda. En Pygame, F2 permite escribir un comando, F5 muestra u oculta el minimapa y Esc abre la pausa.

Para guardar y continuar una partida, usa `G [ruta]` y `L [ruta]`. Para reproducir una bitácora existente:

```console
python main.py --offline --replay partidas/bitacoras/ARCHIVO.log --hasta 100
```

Para probar la verificación y las mediciones:

```console
python -m pytest -q
python main.py --bench --bench-caso niebla-viaje --salida niebla.json
python main.py --bench --salida terreno-y-resolubilidad.json
```

La suite completa de benchmarks incluye varios casos extensos y puede tardar varios minutos.

## Evidencia reproducible

La victoria offline con semilla 354 se conserva en [`CRIPTA-II-victoria-semilla-354.replay`](CRIPTA-II-victoria-semilla-354.replay). Se reproduce desde la raíz con:

```console
python main.py --offline --replay docs/entrega/CRIPTA-II-victoria-semilla-354.replay
```

El reporte de pruebas online y sus límites están descritos en [la evidencia de integración de cripta-02](../evidencia/2026-11-18-cripta-02-integracion-api.md). Los comandos, parámetros y resultados actuales se mantienen en el [README principal](../../README.md) y el [Documento de Decisiones](../DECISIONES.md).
