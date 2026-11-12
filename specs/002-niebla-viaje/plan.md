# Implementation Plan: Niebla de guerra, antorcha e ir a

**Branch**: `spec/jose` | **Date**: 2026-11-11 | **Spec**: [spec.md](spec.md)
**Input**: `specs/002-niebla-viaje/spec.md` (commit `c2c5528`), base `e5bd543`.

> [!NOTE]
> Spec Kit: la política de ejecución de PowerShell bloquea `.specify/scripts/powershell/*.ps1`.
> No se cambió esa protección. Este plan se redactó a mano siguiendo
> `.specify/templates/plan-template.md`; `research`, `data-model`, contratos y `quickstart` se
> incluyen como secciones de este archivo para mantener el alcance pequeño.

## Summary

Añadir al modelo un **conocimiento del jugador** separado del mapa real (salas exploradas,
avistadas y desconocidas, y recuerdos de puertas) cuyas mutaciones son deltas del historial
existente, más una orden `ir a <sala>` en el controlador que ejecuta movimientos ordinarios uno a
uno con una ruta calculada solo sobre ese conocimiento. La antorcha amplía la exploración al
entrar. El cazador de 001 no cambia.

## Technical Context

**Language/Version**: Python 3.12 (entorno local 3.12.10)
**Primary Dependencies**: ninguna nueva; estructuras propias (`Vector`, `ColaPrioridadRuta` de 001)
**Storage**: guardado binario existente (`persistencia/estado_partida.py`), `partida.log`
**Testing**: pytest (`tests/test_niebla_viaje.py`, `tests/test_bench_niebla_viaje.py`)
**Target Platform**: escritorio Windows/Linux, modo consola, `--replay`, `--bench`
**Project Type**: juego de consola MVC
**Performance Goals**: cálculo de un paso de `ir a` ≤ 5 ms con el mapa conocido completo de la cripta de referencia (FR-017)
**Constraints**: sin `dict`/`set` como índice ni bibliotecas de grafos (constitución I); determinismo (II); `--bench`/`--replay` sin vista (III); sin datos de cripta en código (IV); sin solicitudes extra (V)
**Scale/Scope**: cripta de referencia `cripta-01` (6 salas) y mapa de benchmark de 001 (16×16 = 256 salas) como escala adicional

## Constitution Check

| Principio | Cumplimiento |
|---|---|
| I. Estructuras propias | Registros en `Vector` ordenado por ID (búsqueda binaria), cola `ColaPrioridadRuta`; sin `dict`/`set`/`heapq`. |
| II. Determinismo | Ruta con desempate por menor ID; cada paso se registra como `mover <dir>`; `ir a` es comentario. |
| III. MVC sin vista | Conocimiento y ruta en `modelo/`; benchmark en `bench/` sin vista. |
| IV. Sin datos fijos | Todo se deriva del esqueleto cargado. |
| V. Presupuesto | La antorcha usa el esqueleto ya cargado; no pide contenido. |
| VI. Rendimiento medido | `bench/niebla_viaje.py` genera JSON en `docs/evidencia/`. |
| VII. Spec antes que código | Spec en `c2c5528`; plan y tareas en commit propio; código después. |

Resultado: PASA, sin violaciones.

## Project Structure

```text
specs/002-niebla-viaje/
├── spec.md, plan.md, tasks.md, checklists/requirements.md
modelo/conocimiento.py            # NUEVO: ConocimientoJugador, RegistroSala, RecuerdoPuerta, ruta conocida
modelo/deltas.py                  # + DeltaLongitud (trunca el registro de cambios al revertir)
modelo/partida.py                 # integra visitar/observar; propiedad conocimiento
controlador/controlador_juego.py  # comandos IR y MAPA; viaje paso a paso; pergamino corta viaje
bitacora_partida.py               # comentarios '# ...' ignorados al leer acciones
persistencia/estado_partida.py    # registra el módulo modelo.conocimiento para el codec
vista/vista_consola.py            # ayuda de IR y MAPA
bench/niebla_viaje.py             # NUEVO: benchmark FR-017
main.py                           # --bench-caso niebla-viaje
tests/test_niebla_viaje.py        # NUEVO: NV-01..NV-34
tests/test_bench_niebla_viaje.py  # NUEVO: contrato del reporte
docs/evidencia/                   # resultados reales y trazabilidad
```

## Research (Fase 0)

- **Decisión R1 – Ubicación del conocimiento**: objeto propio en `Partida` con referencias de solo
  lectura a las salas reales para nombre/salidas. *Alternativa descartada*: marcar campos en
  `Sala` (mezcla mapa real y conocimiento, contradice FR-006).
- **Decisión R2 – Avistadas por contador**: cada registro guarda cuántas salas exploradas lo
  apuntan; avistada ⇔ no explorada y contador > 0. Explorar una sala cuesta O(salidas propias)
  (FR-016). *Alternativa*: recalcular desde todas las exploradas (O(conocido)).
- **Decisión R3 – Reversibilidad**: cada cambio usa `DeltaAtributos` del historial existente;
  el registro de cambios histórico se trunca con `DeltaLongitud`. Las observaciones del inicio de
  turno se hacen antes de `confirmar_accion`, dentro del intervalo abierto, para que el pergamino
  las revierta con la acción anterior.
- **Decisión R4 – Historia aislada**: registro append-only `(tiempo, tipo, sala, dirección,
  valor)`; `reconstruir_en(t)` crea un conocimiento nuevo sin historial y aplica los cambios con
  tiempo ≤ t. Dependencia 004: la consulta histórica de interfaz/red es de la capacidad 004; aquí
  solo se ofrece la reconstrucción del modelo.
- **Decisión R5 – Ruta**: Dijkstra inverso desde el destino sobre aristas conocidas (origen y
  destino explorados, recuerdo abierto) con `ColaPrioridadRuta` de Daniel; primer paso = vecina
  de menor ID con `costo + dist = d`, igual regla observable que FR-007 de 001. Marcas por
  llamada evitan reiniciar O(n). No se modifica `buscador_rutas.py` (cazador intacto).
- **Decisión R6 – Viaje**: estado transitorio del controlador (no se guarda); en cada turno del
  jugador evalúa causas con prioridad fin > daño > enemigos > llegada, recalcula y ejecuta un
  `mover` ordinario mediante `_ejecutar`. El pergamino anula el viaje.

## Data Model (Fase 1)

- **ConocimientoJugador**: `registros` (Vector ordenado por ID), `cambios` (Vector de tuplas),
  `historial` (compartido o `None`), `_marca` (entero para rutas).
- **RegistroSala**: `id`, `sala` (ref. real), `explorada`, `avistamientos`, `recuerdos`
  (Vector de RecuerdoPuerta propios), `entrantes` (Vector de RecuerdoPuerta de otras salas que
  llegan aquí), `dist`, `marca`.
- **RecuerdoPuerta**: `origen` (RegistroSala), `direccion`, `destino_id`, `costo`, `salida`
  (ref. real para observar), `cerrada` (`None` = no observada, `True`/`False`).
- Transiciones: desconocida → avistada (contador > 0) → explorada; explorada no retrocede salvo
  por delta revertido.

## Contracts

- Comando `IR [A] <id>` / `ir a <id>`; `M` / `MAPA` sin costo.
- Mensajes: rechazo único `"No conoces una sala explorada con ese identificador."`; llegada
  inmediata `"Ya estás en <nombre>."`; parada `"Viaje detenido: <causa>."` con causas
  `fin de partida | daño | enemigos | sin ruta conocida`; llegada `"Llegas a <nombre>: fin del viaje."`.
- `partida.log`: cada paso `t=<t> mover <D>`; la orden `# t=<t> ir a <id>`.
- Benchmark: `python main.py --bench --bench-caso niebla-viaje --salida <ruta.json>`.

## Quickstart

```powershell
python -m pytest tests/test_niebla_viaje.py tests/test_bench_niebla_viaje.py -q
python main.py --bench --bench-caso niebla-viaje --salida docs/evidencia/2026-11-11-niebla-viaje-benchmark.json
python -m pytest -q -m "not rendimiento"
```

## Complexity Tracking

Sin violaciones de la constitución que justificar.
