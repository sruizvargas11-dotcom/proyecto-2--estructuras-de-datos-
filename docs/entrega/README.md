# Material de entrega de CRIPTA II

Este directorio reúne guías y evidencias complementarias para la demostración y la revisión. El README de la raíz y `docs/DECISIONES.md` son los documentos principales del proyecto.

## Guía y resultados

- [Guía de demostración y pruebas](GUIA-DEMO.md)
- [Revisión de integración con `main`](REVISION-MAIN-ACTUAL.md)
- [Validación de cierre de la rama de entrega](CRIPTA-II-validacion-cierre.md)
- [Resultados de pruebas de cierre](CRIPTA-II-pruebas-cierre.xml)
- [Regresión de los seis mapas offline](REGRESION-MAIN-INTEGRADO.json) y [resumen por cripta](CRIPTAS-OFFLINE.json)
- [Partida ganada con vida normal](CRIPTA-II-partida-sin-ajustes.txt), [replay reproducible](CRIPTA-II-victoria-semilla-354.replay) y [resultado del replay](CRIPTA-II-replay-victoria.txt)
- [Prueba online registrada en la rama de cierre](CRIPTA-II-prueba-online.txt) y [validación completa posterior de `cripta-02`](../evidencia/2026-11-18-cripta-02-integracion-api.md)

## Decisiones y mediciones

- [Borrador de decisiones consolidadas de la rama de cierre](CRIPTA-II-decisiones-consolidadas.md) (basado en `main` `87e166d`) y [sección 002 de José](CRIPTA-II-decisiones-002-Jose-cierre.md). Para las decisiones vigentes, consulta también [`docs/DECISIONES.md`](../DECISIONES.md).
- [Medición de `IR A` en `cripta-06`](cripta-06-benchmark-002.json) y [medición de estructuras bajo carga](CRIPTA-II-medicion-estructuras.json).
- La evidencia vigente del benchmark de terreno en esta rama está en [iteración 6](../evidencia/terreno-cazador-benchmark-iteracion-6.json). [`CRIPTA-II-terreno-benchmark-entrega.json`](CRIPTA-II-terreno-benchmark-entrega.json) conserva una corrida anterior de la rama de cierre que superó el límite; se mantiene como antecedente, no como resultado aprobado.
- [Registro de revisión con Antigravity](CRIPTA-II-registro-antigravity-cierre.md).

Las validaciones descritas en `CRIPTA-II-validacion-cierre.md` corresponden al snapshot de la rama de cierre documentado allí. Los resultados no se deben atribuir a otra revisión del código sin repetir la medición indicada.
