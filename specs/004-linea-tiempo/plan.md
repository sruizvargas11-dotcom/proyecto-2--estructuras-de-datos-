# Plan de implementación: Línea de tiempo de CRIPTA

**Branch**: `spec/sebastian` | **Date**: 2026-11-09 | **Spec**: [spec.md](spec.md)

**Input**: `specs/004-linea-tiempo/spec.md` y decisiones de diseño proporcionadas para esta planificación.

## Summary

Implementar consultas históricas sin alterar la partida activa, usando un registro permanente de acciones y puntos de control cada `K` acciones. El `K` predeterminado será el mayor valor probado que cumpla SC-001.

**Decisiones de implementación (no criterios de aceptación adicionales)**: se propone localizar el punto de control de `historia t` con búsqueda binaria propia sobre un arreglo ordenado, seleccionar el punto para `historia #k` mediante `(k - 1) // K` y reconstruir en una partida temporal aislada. También se evaluará restaurar puntos de control sin cargar el grafo completo por consulta y validar en la integración con Niebla la conservación del conocimiento, y con Terreno la paridad de movimientos y costos. La selección del formato de persistencia y el costo de restaurar un punto se medirán; estas decisiones no añaden criterios de aceptación a los de `spec.md`.

**Protocolo exploratorio de benchmark**: comparar la reconstrucción hacia adelante con la inversión de cambios y evaluar `K = 10, 50, 100` y otros valores. Estas variantes y valores son exploratorios; el criterio formal sigue siendo SC-002: comparar al menos tres valores positivos de `K` y elegir el mayor probado que cumpla SC-001.

## Technical Context

**Language/Version**: Python 3.12 (según el entorno de referencia del proyecto).

**Primary Dependencies**: Bibliotecas estándar del proyecto; `pytest` para pruebas. No se propone agregar dependencias.

**Storage**: Archivos binarios de partida existentes; la historia vigente, los registros de cambios y los puntos de control se conservarán al guardar y cargar.

**Testing**: `pytest`; benchmarks mediante el modo existente `--bench`, ampliado con los escenarios de esta especificación.

**Target Platform**: Aplicación de consola Python; `--replay` y `--bench` deben seguir sin instanciar la vista.

**Project Type**: Juego de consola con arquitectura MVC y persistencia local.

**Performance Goals**: Aplicar los criterios de `spec.md`: con al menos 5.000 acciones y 30 puntos medidos 30 veces cada uno, p95 de todas las mediciones menor de 50 ms y máximo documentado (SC-001); comparar percentiles 50 y 95 y bytes persistidos de registros y puntos de control para cada `K` evaluado (SC-002). La memoria de ejecución puede registrarse como métrica informativa, no como criterio de aceptación.

**Baseline Note**: La cifra de ~72 ms corresponde a la "medición de la línea base del 2026-11-05 en main (commit 1e21b9a), pendiente de volver a medir en T024/T025"; se cita como referencia pendiente, no como medición verificada en esta rama.

**Constraints**:
- `K` debe ser positivo; aplicar SC-002 para comparar al menos tres valores positivos y elegir el mayor probado que cumpla SC-001.
- No aplicar ni deshacer más de `K` acciones por consulta.
- La consulta no debe mutar la partida real ni realizar solicitudes de red (FR-006, FR-010), ni alterar el pergamino (FR-007). Preservar la caché LRU es un detalle interno de la reconstrucción aislada vinculado a FR-006, no un criterio de aceptación nuevo.
- La agenda de eventos usa el `HeapMinimo` propio del proyecto (`estructuras/heap_minimo.py`). Por constitución, `heapq`, `bisect` y `collections` (y sus equivalentes para las estructuras evaluadas) están prohibidos; `dict` y `set` no se usan como índice o caché.
- Mantener determinismo, incluyendo el estado del generador aleatorio y el orden de la agenda de eventos.
- Los archivos de la Parte I se rechazan con un mensaje claro de incompatibilidad.

**Scale/Scope**: Historia fija de al menos 5.000 acciones; al menos 30 consultas distribuidas por la historia, 30 repeticiones por consulta; almacenamiento de acciones, cambios y puntos de control desde el inicio de la línea de tiempo vigente.

**Integrations/Dependencies — decisiones de implementación**: Se propone incluir el conocimiento del mapa de Niebla (José) en los puntos de control y validar en pruebas que los movimientos y costos de Terreno (Daniel) se reconstruyan igual que en la partida original. Son detalles de integración para satisfacer los requisitos aplicables de `spec.md`, no criterios de aceptación nuevos.

## Constitution Check

| Principio | Estado | Aplicación al diseño |
|---|---|---|
| I. Estructuras de datos implementadas a mano | PASS | La agenda usa `HeapMinimo` propio. `heapq`, `bisect` y `collections` están prohibidos por constitución; `dict`/`set` no se usan como índice o caché. |
| II. Determinismo de las partidas | PASS | El punto de control incluye `random.Random.getstate()` y la agenda de eventos con su secuencia; se conservan orden y estado de niebla/conocimiento. |
| III. Separación MVC en modos sin interfaz | PASS | `--replay` reutiliza la reconstrucción sin instanciar la vista; `--bench` también permanece sin vista. |
| IV. Datos de criptas externos al código | PASS | El diseño persiste estado de partida y referencias a datos de cripta; no incorpora datos de una cripta concreta al código. |
| V. Respeto al presupuesto de solicitudes | PASS | La reconstrucción y el replay no hacen solicitudes de red. |
| VI. Afirmaciones de rendimiento verificables | PASS | No se afirma que el diseño alcance el umbral hasta medirlo con `--bench`; se documentarán mediana, p95, máximo y memoria. |
| VII. Especificación antes que implementación | PASS | La especificación precede a esta planificación; esta fase no programa. Las decisiones de implementación se deberán documentar según el flujo de cambios del proyecto antes de implementar. |

No se identifica una violación que requiera una excepción. La implementación posterior deberá registrar las decisiones de cambio en el artefacto de gobierno correspondiente; esta tarea se limita a `specs/004-linea-tiempo`.

## Project Structure

### Documentación de esta capacidad

```text
specs/004-linea-tiempo/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
└── contracts/
    ├── cli.md
    └── checkpoint-persistence.md
```

### Código existente relacionado

```text
controlador/       # Acciones, guardado/carga y replay
estructuras/       # Agenda de eventos y estructuras propias
modelo/            # Partida, reloj, mundo y conocimiento del mapa
persistencia/      # Formato binario y codificación de estado
bench/             # Medición de estructuras y persistencia
tests/             # Pruebas unitarias, integración y persistencia/replay
```

**Structure Decision**: Mantener la organización existente por responsabilidades; los artefactos de diseño de esta fase quedan dentro de `specs/004-linea-tiempo`. Los cambios de código no forman parte de esta planificación.

## Complexity Tracking

No se proponen excepciones a la constitución ni dependencias adicionales.
