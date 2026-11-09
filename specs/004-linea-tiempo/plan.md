# Plan de implementación: Línea de tiempo de CRIPTA

**Branch**: `spec/sebastian` | **Date**: 2026-11-09 | **Spec**: [spec.md](spec.md)

**Input**: `specs/004-linea-tiempo/spec.md` y decisiones de diseño proporcionadas para esta planificación.

## Summary

Implementar consultas históricas sin alterar la partida activa, usando un registro permanente de acciones y puntos de control cada `K` acciones. La consulta por tiempo localizará el punto anterior mediante búsqueda binaria propia sobre un arreglo ordenado; la consulta por acción usará el índice `(k - 1) // K` para respetar la numeración desde uno y el estado inmediatamente anterior a la acción. La reconstrucción ocurrirá en una partida temporal aislada. Se compararán reconstrucción hacia adelante e inversión de cambios mediante `--bench`; el K predeterminado será el mayor valor probado que cumpla SC-001.

Los puntos de control serializados deberán poder restaurarse sin cargar el grafo completo de la partida en cada consulta. La selección del formato y su costo se validarán con mediciones; no se presupone que una codificación específica cumpla el objetivo de latencia.

## Technical Context

**Language/Version**: Python 3.12 (según el entorno de referencia del proyecto).

**Primary Dependencies**: Bibliotecas estándar del proyecto; `pytest` para pruebas. No se propone agregar dependencias.

**Storage**: Archivos binarios de partida existentes; la historia vigente, los registros de cambios y los puntos de control se conservarán al guardar y cargar.

**Testing**: `pytest`; benchmarks mediante el modo existente `--bench`, ampliado con los escenarios de esta especificación.

**Target Platform**: Aplicación de consola Python; `--replay` y `--bench` deben seguir sin instanciar la vista.

**Project Type**: Juego de consola con arquitectura MVC y persistencia local.

**Performance Goals**: En al menos 5.000 acciones, para al menos 30 puntos medidos 30 veces cada uno, p95 de todas las mediciones de consulta menor de 50 ms; documentar también el máximo observado. Comparar mediana, p95, máximo y memoria según SC-001/002 y las mediciones planificadas.

**Constraints**:
- `K` debe ser positivo. Comparar `K = 10, 50, 100` y otros valores, y elegir el mayor probado que cumpla SC-001.
- No aplicar ni deshacer más de `K` acciones por consulta.
- La consulta no debe mutar la partida real, consumir el pergamino, alterar la caché LRU ni realizar solicitudes de red.
- Usar arreglos/estructuras propias y búsqueda binaria propia; no usar `bisect`, `heapq`, `dict` o `set` como índice o caché.
- Mantener determinismo, incluyendo el estado del generador aleatorio y el orden de la agenda de eventos.
- Los archivos de la Parte I se rechazan con un mensaje claro de incompatibilidad.

**Scale/Scope**: Historia fija de al menos 5.000 acciones; al menos 30 consultas distribuidas por la historia, 30 repeticiones por consulta; almacenamiento de acciones, cambios y puntos de control desde el inicio de la línea de tiempo vigente.

**Integrations/Dependencies**: El conocimiento del mapa de Niebla (José) forma parte del punto de control; los movimientos y costos de Terreno (Daniel) deben reconstruirse igual que en la partida original.

## Constitution Check

| Principio | Estado | Aplicación al diseño |
|---|---|---|
| I. Estructuras de datos implementadas a mano | PASS | Arreglos propios para acciones e índices; búsqueda binaria propia; no se usa `bisect`, `heapq` ni estructuras prohibidas como índice o caché. |
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
