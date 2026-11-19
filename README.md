# CRIPTA

CRIPTA es un juego de exploración de mazmorras para consola y Pygame. El jugador recorre salas, administra objetos, combate enemigos y busca la salida mientras el reloj del juego procesa acciones y efectos en orden determinista.

El proyecto está construido en Python y utiliza estructuras de datos implementadas dentro del repositorio. Puede cargar datos desde una API HTTP o desde las criptas incluidas para jugar sin conexión.

## Funcionalidades

- Partidas por consola o con interfaz gráfica Pygame.
- Seis criptas disponibles en el paquete offline.
- Movimiento con costos variables, puertas, objetos, llaves, trampas y enemigos.
- Cazadores que eligen rutas de costo mínimo y atacan al compartir sala con el jugador.
- Mapa conocido, antorcha y viaje automático por rutas exploradas.
- Guardado, carga, replay determinista y consultas históricas.
- Verificación de resolubilidad antes de iniciar una partida.
- Pruebas automatizadas y benchmarks reproducibles.

## Requisitos

- Python 3.12.
- Dependencias de [requirements.txt](requirements.txt).
- Pygame se necesita solo para `--gui`; `requests` se usa para el acceso HTTP.

## Instalación

Clona el repositorio y crea un entorno virtual desde su raíz.

### Windows PowerShell

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\Activate.ps1
```

### Linux o macOS

```sh
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Iniciar una partida

Para abrir el juego con datos offline:

```console
python main.py --offline
```

Para elegir una cripta directamente:

```console
python main.py --offline --cripta cripta-01
```

Por defecto, el juego intenta usar la API HTTP. La conexión depende de que el servicio externo esté disponible. La opción `--offline` usa los datos versionados en el repositorio.

La interfaz gráfica se inicia con:

```console
python main.py --offline --gui
```

La consola acepta `N`, `S`, `E`, `O` para moverse, `A [n]` para atacar, `W` para esperar, `R [n]` para recoger, `T [n]` para soltar, `U [n]` para usar objetos, `EQ [n]` para equipar, `AB <dirección>` para abrir una puerta y `Q` para salir. `H` muestra la ayuda completa durante la partida.

### Controles de Pygame

| Teclas | Acción |
| --- | --- |
| Flechas o `W`, `A`, `S`, `D` | Moverse. |
| `Shift` + dirección | Intentar abrir la puerta en esa dirección. |
| `Espacio` | Atacar al objetivo seleccionado. |
| `X` | Esperar. |
| `R`, `F`, `U`, `C` | Recoger, soltar, usar o equipar un objeto. |
| `P` | Usar el pergamino de retroceso. |
| `G`, `L` | Guardar o cargar con la ruta predeterminada. |
| `I` | Abrir el inventario. |
| `F1` | Mostrar la ayuda. |
| `F2` | Escribir un comando; pulsa `Enter` para enviarlo o `Esc` para cancelar. |
| `F5` | Mostrar u ocultar el minimapa. |
| `Esc` | Abrir la pausa. |
| `F11` | Alternar pantalla completa. |

En los menús, usa las flechas para cambiar la selección y `Enter` para confirmar.

## Opciones principales

Consulta todas las opciones con `python main.py --help`.

| Opción | Descripción |
| --- | --- |
| `--offline` | Usar datos locales en lugar de la API. |
| `--offline-dir RUTA` | Seleccionar otra carpeta de datos offline; requiere `--offline`. |
| `--cripta ID` | Elegir una cripta directamente. |
| `--gui` | Usar la interfaz Pygame. |
| `--verificar ID` | Informar si una cripta es resoluble sin iniciar partida. |
| `--forzar` | Permitir una partida cuyo estado sea no resoluble o no verificable; no ignora datos inválidos. |
| `--solo-mapa` | Cargar y verificar el mapa sin iniciar partida. |
| `--cache-size N` | Fijar la capacidad de la caché LRU del catálogo (predeterminado: 25). |
| `--cache-dir RUTA` | Cambiar la ubicación de la caché persistente. |
| `--hilos` | Precargar contenido en segundo plano durante una partida nueva. |
| `--partidas-dir RUTA` | Cambiar la ubicación de guardados, bitácoras y puntajes. |
| `--replay ARCHIVO` | Reproducir una bitácora sin entrada interactiva. |
| `--hasta T` | Detener un replay en el tiempo virtual indicado. |
| `--silencioso` | Mostrar el resumen del replay sin listar cada acción. |
| `--checkpoint-cada K` | Fijar el intervalo de puntos de control de la línea de tiempo (predeterminado: 200). |
| `--bench` | Ejecutar la suite completa de benchmarks locales. |
| `--bench-caso niebla-viaje` | Ejecutar solo las mediciones de niebla y viaje; requiere `--bench`. |
| `--salida RUTA` | Guardar el reporte detallado del benchmark en la ruta indicada. |

`--gui`, `--replay` y `--bench` tienen restricciones de combinación; el programa las informa si los argumentos no son válidos. Los modos de verificación, replay y benchmark no abren una vista gráfica.

## Ejemplos habituales

Verificar una cripta local sin iniciar una partida:

```console
python main.py --offline --verificar cripta-01
```

La verificación también muestra por qué `cripta-05` no es resoluble. Para permitir iniciar esa cripta en consola, se puede indicar `--forzar`:

```console
python main.py --offline --cripta cripta-05 --forzar
```

Para jugar con los datos del servicio HTTP, omite `--offline`:

```console
python main.py --cripta cripta-02
```

Reproducir una bitácora hasta el tiempo virtual 100, mostrando solo el resumen:

```console
python main.py --offline --replay partidas/bitacoras/ARCHIVO.log --hasta 100 --silencioso
```

Medir solo niebla y viaje, o ejecutar la suite completa y guardar los reportes locales:

```console
python main.py --bench --bench-caso niebla-viaje --salida bench/resultados/niebla-viaje-local.json
python main.py --bench --salida bench/resultados/terreno-cazador-local.json
```

## Partida, guardado y línea de tiempo

El tiempo es virtual. Una acción válida programa el siguiente evento según el costo de la acción y la velocidad del actor. Los enemigos y efectos que vencen durante ese intervalo se procesan antes de la siguiente decisión del jugador. Las acciones rechazadas no consumen tiempo.

Durante la partida, `G [ruta]` guarda y `L [ruta]` carga. Los archivos incluyen las versiones de cripta y catálogo; se rechaza una carga incompatible antes de sustituir la sesión activa.

Cada partida nueva genera una bitácora bajo `partidas/bitacoras/`. Puedes reproducirla con:

```console
python main.py --offline --replay partidas/bitacoras/ARCHIVO.log
```

`HISTORIA <t>` consulta el estado en un tiempo virtual y `HISTORIA #<k>` consulta el estado justo antes de la acción número `k`. Las consultas no cambian la partida. Un retroceso elimina de la historia consultable los cambios posteriores al punto restaurado.

## Datos offline y API

Los mapas offline están bajo `datos_offline/`. Cada cripta mantiene su propio esqueleto, contenido y versión de catálogo. Entre los datos disponibles están `cripta-01` a `cripta-06`; `cripta-05` conserva su clasificación de no resoluble y requiere `--forzar` para jugar.

El modo online consulta el servicio HTTP configurado por los adaptadores. La aplicación aplica un presupuesto de solicitudes, caché persistente y validación de versiones. Los benchmarks locales no hacen solicitudes HTTP.

### Si la API no está disponible

El modo online no cambia silenciosamente a offline. Si el servicio o la conexión no responden, revisa la conectividad y vuelve a intentarlo. Para continuar sin depender del servicio, inicia explícitamente una cripta local con `--offline`, por ejemplo `python main.py --offline --cripta cripta-01`. Los datos offline tienen sus propias versiones y se guardan en `datos_offline/`.

## Arquitectura

El código separa el modelo del juego, la coordinación de acciones, las vistas y las fuentes de datos.

| Carpeta | Responsabilidad |
| --- | --- |
| `modelo/` | Estado de la partida, actores, reloj, rutas, conocimiento y reglas. |
| `controlador/` | Procesamiento de comandos, sesiones, guardado, replay e integración de vistas. |
| `vista/` | Interfaz de consola. |
| `vista_pygame/` | Interfaz gráfica, escenas, renderizado y audio. |
| `adaptadores/` | Integración con fuentes HTTP y offline. |
| `estructuras/` | Vectores, listas, heaps, colas y estructuras auxiliares propias. |
| `persistencia/` | Serialización, caché y almacenamiento de partidas. |
| `bench/` | Casos y herramientas de medición. |
| `tests/` | Pruebas unitarias, de integración y aceptación. |
| `specs/` | Requisitos, decisiones de diseño, contratos y tareas por capacidad. |

## Flujo de trabajo con Spec Kit y asistentes de IA

Durante el trabajo de especificación e implementación se utilizaron GitHub Copilot y Claude en distintas partes del proyecto. La selección dependió de la disponibilidad de planes gratuitos y de los límites de uso, créditos o tokens de cada servicio para los integrantes. Esto permitió avanzar con las herramientas disponibles sin exigir una suscripción paga a todo el equipo.

El agente podía variar, pero el flujo común se mantuvo en los artefactos versionados: Constitución, especificación, aclaraciones, plan, tareas, análisis y, después de revisar esos documentos, implementación. Las decisiones funcionales y técnicas se contrastaron con los requisitos, las pruebas y las mediciones; el asistente no sustituye esa revisión. La bitácora [PROMPTS_LLM.md](docs/PROMPTS_LLM.md) registra los prompts y las herramientas utilizadas por cada integrante.

## Pruebas y benchmarks

Ejecuta la suite completa desde la raíz:

```console
python -m pytest -q
```

Para medir el rendimiento:

```console
python main.py --bench
python main.py --bench --salida docs/evidencia/terreno-cazador-benchmark.json
```

La suite completa incluye mediciones de estructuras, persistencia, resolubilidad, niebla y viaje, y terreno y cazador. El benchmark contractual de terreno mantiene ocho escenarios, 30 repeticiones por escenario y la referencia `cripta-06`. Puede tardar varios minutos.

La última revalidación completa registrada se ejecutó con Python 3.12.10: pasaron 1403 pruebas. El benchmark tuvo cero discrepancias y cumplió el umbral de 20 ms; su máximo sintético fue 18.8242 ms. El resultado está en [el reporte de revalidación](docs/evidencia/2026-11-18-revalidacion-entrega-terreno-cazador-intento-2.json). Se conserva una corrida anterior que excedió el umbral en [su reporte histórico](docs/evidencia/2026-11-18-revalidacion-entrega-terreno-cazador.json).

## Documentación y evidencias

- [Documento de decisiones técnicas](docs/DECISIONES.md): alternativas, decisiones y mediciones.
- [Análisis de arquitectura](docs/ANALISIS_ARQUITECTURA.md): componentes y relaciones entre módulos.
- [Guía de demostración](docs/entrega/GUIA-DEMO.md): recorrido y comandos de prueba.
- [Índice de materiales complementarios](docs/entrega/README.md).
- [Trazabilidad y validación de niebla y viaje](docs/evidencia/2026-11-12-niebla-viaje-trazabilidad.md).
- [Integración de la API con `cripta-02`](docs/evidencia/2026-11-18-cripta-02-integracion-api.md).
- [Bitácora de uso de modelos de lenguaje](docs/PROMPTS_LLM.md): conserva los nombres y el registro de autoría requerido.

Las mediciones siempre deben interpretarse junto con su fixture, entorno y fecha; los reportes históricos se conservan como fueron generados.
