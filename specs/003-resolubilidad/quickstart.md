# Quickstart de validación

Esta guía define los comandos previstos una vez implementada la capacidad. No se han
ejecutado en esta fase de planificación.

## Verificación por consola

Con datos HTTP:

```powershell
python main.py --verificar cripta-01
```

Con datos offline:

```powershell
python main.py --offline --verificar cripta-01
```

Comprobar el reporte completo y los códigos: 0 resoluble, 1 no resoluble y 2 ante
NO VERIFICABLE o error de datos/red. Ninguna de las dos llamadas debe crear la vista.

## Inicio de partida

```powershell
python main.py --offline --cripta cripta-01
python main.py --offline --cripta cripta-01 --forzar
```

El primer comando bloquea una cripta no resoluble/no verificable; el segundo permite
continuar esos dos estados y muestra solo resumen sin ubicaciones. Un error de datos
bloquea ambos. Probar una partida resoluble y una no resoluble con y sin `--forzar`.

## Pruebas focalizadas

```powershell
python -m pytest tests/test_resolubilidad_g14.py -q
python -m pytest tests/test_resolubilidad_g15.py -q
python -m pytest tests/test_resolubilidad_g16.py -q
python -m pytest tests/test_resolubilidad_g17.py -q
python -m pytest tests/test_resolubilidad_e01_e09.py tests/test_resolubilidad_e10_e18.py tests/test_resolubilidad_e19_e27.py -q
python -m pytest tests/test_fuente_llaves.py tests/test_cli_resolubilidad.py -q
```

Los grupos deben incluir los escenarios RS-E01–RS-E27, citar FR/SC por prueba, comparar
el verificador incremental contra la referencia en datos sintéticos deterministas y
comprobar que dos reportes son idénticos byte a byte. El comando de regresión del
repositorio es `python -m pytest -q`.

## Bench

Ejecutar el caso registrado en `CASOS` sin `--salida`:

```powershell
python main.py --bench
```

El caso genera por semilla criptas con muchas llaves encadenadas, verifica equivalencia
de veredicto/orden/frontera antes de cronometrar y compara A incremental con B de recorrido
completo repetido. Usar al menos tres tamaños duplicados y 20 repeticiones por tamaño
(mínimo requerido: cinco). Revisar evidencia JSON en `bench/resultados/`: commit limpio,
Python, sistema, CPU, semilla, mediana, p95, máximo y muestras.

Para SC-001 incluir la cripta publicada mayor disponible además de sintéticas; excluir
red, carga de datos y renderizado. Registrar explícitamente el máximo. No reportar
cumplimiento si p95 ≥200 ms o el crecimiento supera 2.5×. La combinación
`--bench --salida` está pendiente de aclaración porque actualmente selecciona un reporte
especializado distinto y omite los casos de `CASOS`.

## Preparación

Usar el Python 3.12 del entorno de referencia, instalar dependencias según
`requirements.txt` si faltan, y evitar fuentes de red durante pruebas/mediciones del
modelo. El formato de invocaciones y resultados se detalla en
[contracts/cli.md](./contracts/cli.md); la fuente y el presupuesto en
[contracts/fuente-llaves.md](./contracts/fuente-llaves.md).
