# Plan de implementación: Terreno y cazador

**Rama Git**: `feature/spec-kit-copilot` | **Feature**: `001-terreno-cazador` | **Fecha**: 2026-11-04 | **Especificación**: [spec.md](./spec.md)

**Entrada**: Requisitos funcionales FR-001–FR-013 y escenarios AB-01–AB-29.

## Resumen

Extender el costo efectivo de cada salida hasta el cálculo del intervalo de movimiento
sin cambiar las acciones existentes, e incorporar el comportamiento de cazador al modelo
de enemigos. La decisión del cazador debe ser una ruta abierta de costo mínimo y repetible
desde el estado actual. La carga valida los datos antes de iniciar, y ambas vistas presentan
los costos efectivos y distinguen al cazador. La validación de rendimiento se integrará en
`--bench`, sin red ni instanciación de vistas, y comparará cada decisión con un cálculo de
referencia desde cero.

## Contexto técnico

**Lenguaje/versión**: Python 3.12 (entorno de referencia indicado en README).

**Dependencias principales**: Dependencias existentes del proyecto (`requests`, `pygame` y
`pytest`). No se añadirá una biblioteca de grafos, rutas, heap o búsqueda.

**Persistencia**: JSON servido por adaptadores HTTP/offline; cachés locales de esqueleto,
contenido y catálogo. No hay base de datos.

**Pruebas**: `pytest`; pruebas unitarias, de integración MVC, CLI y vistas ya existentes.

**Plataforma**: Windows local como entorno de rendimiento declarado; la lógica del juego
continúa siendo multiplataforma dentro de los entornos actualmente soportados.

**Tipo de proyecto**: Juego Python con modelo, controlador, vista de consola y vista Pygame.

**Objetivo de rendimiento**: En el fixture fijo `bench-terreno-cazador-grid-16x16`,
versión `1.0.0`, con 256 salas y exactamente 20 cazadores, ejecutar los ocho escenarios
del spec con 30 repeticiones por escenario. Los perfiles usan rangos 1/100 o 1000/10000,
con diez cazadores por valor. Cada ciclo de eventos entre decisiones del jugador debe ser
≤20 ms. Toda decisión se contrasta con un recálculo de referencia desde cero.

**Restricciones**:
- Solo estructuras propias para índices, colas de prioridad y cachés de rutas. No usar
  `dict`/`set` como índice o caché ni `heapq`, `bisect`, `collections`, `networkx` o
  bibliotecas equivalentes.
- Conservar determinismo, historial reversible, serialización, presupuesto de solicitudes
  y separación MVC en `--replay` y `--bench`.
- No incluir datos de una cripta concreta en lógica de producción. Las pruebas y mediciones
  reciben datos externos reproducibles.
- No afirmar el cumplimiento de los 20 ms hasta tener evidencia de `--bench`.

**Escala**: 20 cazadores sobre un fixture sintético fijo, versionado y externo a la lógica
de producción. Sus 256 salas superan las 6 salas de `cripta-01`. La identidad, versión,
topología y mutaciones de puertas quedan especificadas en
[datos-entrada-y-benchmark.md](./contracts/datos-entrada-y-benchmark.md).

## Verificación de constitución

| Principio | Estado | Aplicación en el diseño |
|---|---|---|
| I. Estructuras propias | Cumple | Reutilizar `Vector`, `ListaSimple` y búsqueda binaria propia; para la ruta de mínimo costo, usar una cola de prioridad propia basada en `Vector`. No convertir datos JSON en índices/cachés con diccionarios o conjuntos. |
| II. Determinismo | Cumple | Ordenar desempates de ruta por ID de sala; fijar semilla y secuencia; no usar orden de respuesta externa ni azar para decisiones del cazador. |
| III. Separación MVC | Cumple | `--bench` y `--replay` no crean instancias de vistas. Pygame sigue consumiendo snapshots publicados por el controlador. |
| IV. Datos de criptas externos | Cumple con condición | Costos y topología vienen del esqueleto; rango viene del catálogo. Las pruebas usan datos de entrada controlados, no valores de criptas incrustados en la lógica. |
| V. Presupuesto de solicitudes | Cumple | La decisión de rutas usa el esqueleto y el estado ya cargados; no añade consultas HTTP. Datos incompatibles fallan en la validación existente, antes de jugar. |
| VI. Rendimiento verificable | Cumple con condición | La comparación de modalidades y cualquier afirmación de latencia se apoyan en la salida reproducible de `--bench`. |
| VII. Especificación antes de implementación | Cumple en esta fase | `spec.md` precede al plan; esta fase solo produce documentos. No modificar código hasta que la especificación y el plan estén revisados y confirmados según el flujo del proyecto. |
| Trazabilidad | Cumple | La matriz de validación en `data-model.md` vincula FR y AB; las tareas futuras deberán referir los FR atendidos y las pruebas deberán citar sus AB. |

No se identifica una violación constitucional que requiera excepción.

## Fases de diseño

### Fase 0 — Investigación

Las decisiones y alternativas se consolidan en [research.md](./research.md). La investigación
se limitó a los documentos y el código presentes en el repositorio; no se consultó el PDF ni
servicios externos.

### Fase 1 — Diseño y contratos

- [Modelo de datos y estados](./data-model.md): reglas de validación, estado de ruta,
  decisión y trazabilidad FR/AB.
- [Contrato de entrada y benchmark](./contracts/datos-entrada-y-benchmark.md): campos de
  entrada, rechazos, determinismo y evidencia de medición.
- [Guía de validación](./quickstart.md): comandos previstos para pruebas focalizadas,
  regresión, CLI headless y benchmark.
- No se crea `tasks.md` en esta fase.

## Decisiones de integración

1. **Costo de movimiento**: almacenar en cada salida su costo efectivo validado; el
   adaptador asigna 100 solo cuando el campo está ausente. El costo de acción seleccionado
   debe llegar al punto que calcula `max(1, costo * 100 // velocidad)`. Todo actor que se
   mueva comunica el costo de la salida atravesada. Errante y rastreador conservan su
   selección de movimiento; ataques, espera y acciones restantes conservan su costo actual
   de 100.
2. **Validación**: se integra en la carga del esqueleto y del catálogo antes de crear la
   partida. Para cada par de sentidos representados, comparar los costos efectivos después
   del valor predeterminado; informar origen/destino y ambos costos al rechazar.
3. **Ruta**: búsqueda ponderada sobre el mapa completo y puertas abiertas en ese instante.
   Una búsqueda desde el jugador sobre aristas entrantes puede producir distancias al
   jugador para todos los cazadores; la selección final se hace entre salidas abiertas del
   cazador y elige el destino de menor ID que cumpla `costo + dist(destino) = dist(origen)`.
   Mantener cálculo individual y compartido para poder medir ambos. Todo estado compartido
   debe quedar invalidado al cambiar la posición del jugador o una puerta. Las salidas sin
   representación inversa son válidas y se tratan como dirigidas; comparar costos solo
   cuando existan ambos sentidos.
4. **Turnos**: conservar el orden de eventos del reloj. La decisión del cazador mantiene
   primero el ataque al compartir sala; entrar a la sala del jugador termina el movimiento
   sin ataque hasta el siguiente turno programado.
5. **Vistas**: consola lee costo efectivo del modelo; Pygame lo recibe en su snapshot plano.
   No pasar reglas de ruta a las vistas. Diferenciar el cazador por comportamiento y
   conservar el mecanismo existente de sprites/estilo como fallback si no existe un asset
   específico.
6. **Benchmark**: añadir la evaluación del cazador al camino headless de `--bench`, sin
   fuente de red ni vistas. Usar el fixture `bench-terreno-cazador-grid-16x16` v1.0.0
   (256 salas, 480 conexiones bidireccionales; definición exacta en el contrato). Mantener
   mapa/versión, semilla, estado inicial, acciones y equipo invariantes entre comparaciones.
   Ejecutar los ocho escenarios: rango pequeño/grande, diez cazadores por cada uno de los
   dos rangos, puertas alternadas cada ciclo/cada 100 ciclos, y cálculo individual/compartido;
   realizar 30 repeticiones por escenario. Instrumentar el ciclo entre decisiones del
   jugador, excluyendo espera humana, red y renderizado. Comparar cada decisión con
   Dijkstra de referencia sin caché fuera del intervalo cronometrado y registrar máximo
   por ciclo, metadatos y corrección. Reiniciar cada repetición desde el mismo estado y
   procesar 1000 ciclos por repetición. La CLI acepta `--salida RUTA` y exporta un reporte
   JSON UTF-8 indentado con dos espacios. La ejecución de referencia guarda el reporte en
   `docs/evidencia/2026-11-04-terreno-cazador-benchmark.json`, bajo control de versiones;
   el contrato define el esquema y los campos detallados.

## Estructura del proyecto

### Documentación de esta capacidad

```text
specs/001-terreno-cazador/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
└── contracts/
    └── datos-entrada-y-benchmark.md
```

### Código existente que deberá tocar la implementación

```text
adaptadores/                 # leer costo y rango y validar datos
bench/                        # escenarios, comparador de referencia y salida
controlador/                  # flujo del reloj, proyección a Pygame
estructuras/                  # prioridad propia para búsqueda ponderada
modelo/entidades/enemigo.py   # comportamiento cazador y decisión
modelo/mundo/salida.py        # costo efectivo
modelo/mundo/cripta_modelo.py # acceso a mapa ya ordenado
modelo/partida.py             # movimiento y costo programado
persistencia/                 # compatibilidad de datos/cachés/versiones
vista/                         # consola
vista_pygame/                  # snapshot y HUD/render
tests/                         # pruebas unitarias, integración y vista
```

**Decisión de estructura**: integrar en las capas MVC y de persistencia existentes,
reutilizando los patrones de carga, snapshots y pruebas actuales. El buscador de rutas
pertenece al modelo/estructura propia, no a la vista ni a un servicio externo.

## Riesgos y decisiones que deben mantenerse visibles

- El modelo actual representa salidas por dirección desde cada sala; no valida que toda
  salida tenga otra representación de regreso. El spec ahora define que una salida sin
  inversa es válida como unidireccional y que los costos se comparan solo si ambos sentidos
  están presentes.
- El repositorio no incluye una ficha de catálogo de cazador ni el campo `costo` en el
  esqueleto offline actual. La disponibilidad de esos campos en la fuente de datos y su
  política de publicación de versión debe confirmarse antes de desplegar; no suplirlos con
  datos incrustados.
- El fixture de benchmark es sintético y no representa una cripta real. Los resultados
  acreditan el umbral solo para la dimensión y topología registradas, no para mapas de
  cualquier escala.

## Seguimiento de complejidad

No aplica: el diseño respeta la constitución y reutiliza la arquitectura existente. La
cola de prioridad específica de caminos se considera una estructura propia del problema,
no una dependencia externa.
