# Evidencias y materiales complementarios de CRIPTA II

Este directorio reúne guías de uso, partidas reproducibles, mediciones y registros de snapshots históricos. El README de la raíz y `docs/DECISIONES.md` describen el proyecto y las decisiones vigentes.

## Guía y resultados

- [Guía de demostración y pruebas](GUIA-DEMO.md)
- [Revisión histórica de integración](REVISION-MAIN-ACTUAL.md)
- [Validación histórica del snapshot de cierre](CRIPTA-II-validacion-cierre.md)
- [Resultados de pruebas de cierre](CRIPTA-II-pruebas-cierre.xml)
- [Regresión de los seis mapas offline](REGRESION-MAIN-INTEGRADO.json) y [resumen por cripta](CRIPTAS-OFFLINE.json)
- [Partida ganada con vida normal](CRIPTA-II-partida-sin-ajustes.txt), [replay reproducible](CRIPTA-II-victoria-semilla-354.replay) y [resultado del replay](CRIPTA-II-replay-victoria.txt)
- [Prueba online registrada en la rama de cierre](CRIPTA-II-prueba-online.txt) y [validación completa posterior de `cripta-02`](../evidencia/2026-11-18-cripta-02-integracion-api.md)

## Decisiones y mediciones

- [Registro histórico de decisiones consolidadas](CRIPTA-II-decisiones-consolidadas.md) (snapshot de `87e166d`) y [decisiones de la capacidad 002 en ese snapshot](CRIPTA-II-decisiones-002-cierre.md). Para las decisiones vigentes, consulta [`docs/DECISIONES.md`](../DECISIONES.md).
- [Medición de `IR A` en `cripta-06`](cripta-06-benchmark-002.json) y [medición de estructuras bajo carga](CRIPTA-II-medicion-estructuras.json).
- La evidencia vigente del benchmark de terreno en esta rama está en [iteración 6](../evidencia/terreno-cazador-benchmark-iteracion-6.json). [`CRIPTA-II-terreno-benchmark-entrega.json`](CRIPTA-II-terreno-benchmark-entrega.json) conserva una corrida anterior de la rama de cierre que superó el límite; se mantiene como antecedente, no como resultado aprobado.
- [Registro de revisión documental del snapshot de cierre](CRIPTA-II-revision-documental-cierre.md).

Las validaciones descritas en `CRIPTA-II-validacion-cierre.md` corresponden al snapshot de la rama de cierre documentado allí. Los resultados no se deben atribuir a otra revisión del código sin repetir la medición indicada.
