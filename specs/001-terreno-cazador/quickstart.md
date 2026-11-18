# Validación rápida: Terreno y cazador

Guía de verificación para después de implementar la capacidad. Ejecutar desde la raíz del
repositorio con el entorno ya instalado. No requiere acceso al PDF.

## Prerrequisitos

- Python 3.12 y dependencias de `requirements.txt`.
- `pytest`.
- Una fuente/dataset versionado con esqueleto y catálogo compatibles. La cripta offline
  `cripta-01` contiene un cazador para probar la carga local. El benchmark combina el fixture
  sintético `bench-terreno-cazador-grid-16x16` v1.0.0 con un snapshot de la cripta de
  referencia `cripta-06`; ambos están definidos en el contrato.

## Pruebas focalizadas

```powershell
python -m pytest -q tests/test_terreno_cazador.py
python -m pytest -q tests/test_bloque2_entidades.py tests/test_rol2_bloque4.py
```

La primera suite se deberá crear durante la implementación y cubrirá AB-01–AB-10,
AB-14–AB-21 y AB-23–AB-28, incluyendo identificación de FR en cada prueba. AB-28 verifica
que una salida sin contraparte inversa se acepta como unidireccional. Las suites existentes
comprueban que los comportamientos anteriores, puertas y reglas del reloj permanezcan intactos.

## Validación de vistas y separación MVC

```powershell
python -m pytest -q tests/test_vista_consola.py tests/vista/test_render_enemigos.py tests/vista/test_salida_y_rejas.py
python -m pytest -q tests/vista/test_sin_pygame_en_replay_bench.py
```

Comprobar AB-11, AB-12 y AB-22 en ambas vistas. La prueba de separación debe confirmar que
`--bench` y `--replay` no instancian vistas ni importan Pygame en su camino headless.

## Prueba de carga de datos

```powershell
python -m pytest -q tests/test_controlador_red.py tests/test_datos_http.py tests/test_datos_offline.py
```

Las pruebas nuevas deberán usar payloads aislados, no datos de una cripta en la lógica:
ambos sentidos omitidos → 100; omitido/100 → aceptar; omitido/no-100 y dos valores
distintos → rechazo con conexión y valores efectivos; `null` explícito → rechazo; rango
faltante/no entero/<1 y versiones incompatibles → rechazo antes de comenzar.

## Benchmark

```powershell
python main.py --bench --salida docs/evidencia/terreno-cazador-benchmark-completo.json
```

El benchmark incluye dos grupos. El primero cubre AB-13 y AB-29: antes de medir, validar identidad
`bench-terreno-cazador-grid-16x16`, versión `1.0.0`, dimensiones 16×16 (256 salas), 480
conexiones y secuencia de puertas; luego ejecutar los ocho escenarios con 30 repeticiones
de 1000 ciclos cada una. Registrar rangos, frecuencia de cambios, modalidad, equipo y
entorno. `--salida` guarda un JSON UTF-8 indentado con SHA-256 del fixture, metadatos, las
30 repeticiones por escenario, las 1000 duraciones de ciclo en nanosegundos de cada
repetición, el máximo y todas las discrepancias contra el recálculo sin caché, que se ejecuta
fuera del intervalo medido. El reporte se conserva en `docs/evidencia/` bajo control de
versiones, incluso si documenta un resultado fallido. El máximo de cada ciclo entre
decisiones del jugador debe ser ≤20 ms; un fallo de corrección invalida el resultado aunque
la latencia cumpla. No emitir una afirmación de rendimiento hasta revisar y conservar el
reporte reproducible y sus metadatos.

El segundo grupo cubre AB-30 y FR-014: medir 30 repeticiones de 1000 ciclos sobre el snapshot
de `cripta-06` versión `f9ed9afa683d`, con catálogo `4b9e75a42be5`, 300 salas y sus 25
cazadores activos. La semilla es 42 y el jugador ejecuta `W`; cada repetición parte del mismo
estado. El reporte agrega identidad, versiones, SHA-256 y ubicación de las 25 instancias. La
carga de datos se realiza antes de cronometrar; las duraciones incluyen el ciclo real de
eventos, sin red ni renderizado. El máximo también debe ser ≤20 ms y cada decisión debe
coincidir con el recálculo desde cero.

La prueba de carga anterior cubre AB-28 (FR-001); la validación del fixture y sus metadatos
en este paso cubre AB-29 (FR-011).
