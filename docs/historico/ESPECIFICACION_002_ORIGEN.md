# Contexto inicial de la capacidad 002

Archivo histórico de preparación de requisitos para niebla de guerra, antorcha y viaje automático. La especificación normativa y completa está en [`specs/002-niebla-viaje/spec.md`](../../specs/002-niebla-viaje/spec.md); este resumen no agrega requisitos.

## Alcance incorporado en la especificación

- Mantener separado el conocimiento del jugador del mapa completo.
- Distinguir salas exploradas, avistadas y desconocidas, y recordar la última observación de cada puerta.
- Hacer que la antorcha revele salas cercanas sin revelar contenido ni observar puertas remotas.
- Calcular `IR A` sobre rutas conocidas de menor costo y ejecutar cada paso con las reglas normales del juego.
- Detener el viaje ante cambios de puerta, enemigos, daño, llegada o ausencia de ruta, e indicar la causa.
- Conservar el conocimiento en guardado, carga, retroceso, historia y replay.
- Medir consultas de conocimiento y el cálculo de un paso con benchmarks reproducibles.

## Decisiones y trazabilidad

Las decisiones de borde se resolvieron en la sesión de clarificación del 11 de noviembre de 2026 y se revisaron el 18 de noviembre de 2026. Se reflejan en NV-03 y NV-30 a NV-34 de la especificación. Los casos del Apéndice B y los requisitos funcionales tienen trazabilidad en la misma capacidad.

Para implementación y validación, consultar [`plan.md`](../../specs/002-niebla-viaje/plan.md), [`tasks.md`](../../specs/002-niebla-viaje/tasks.md) y los documentos de evidencia enlazados desde la spec.
