# Quickstart de validación

Esta guía documenta los comandos de uso y la evidencia de validación ejecutada.

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

Las mediciones siguientes se hicieron en un árbol limpio en el commit `1781d41`,
Python 3.12.10, Windows 10 (10.0.19045), Intel Core i7-8750H @ 2.20 GHz,
semilla 42. No había una cripta publicada con datos de llaves disponible; por eso,
SC-001 se midió con la mayor cripta sintética disponible (S/E/K = 64/64/32). Se
excluyeron red, carga de datos y renderizado. La equivalencia de veredicto, orden y
frontera se comprobó antes de medir.

Ejecución completa de `python main.py --bench`, 20 repeticiones por tamaño; evidencia:
`bench/resultados/2026-11-13T015255_1781d41_bench.json`.

| S/E/K | variante | mediana ms | p95 ms | máximo ms | razón p95 |
|---|---|---:|---:|---:|---:|
| 16/16/8 | incremental | 0.694 | 1.286 | 1.443 | — |
| 32/32/16 | incremental | 1.462 | 2.256 | 2.639 | 1.754× |
| 64/64/32 | incremental | 3.168 | 3.409 | 3.599 | 1.511× |

Para `python main.py --bench --salida C:\Temp\resolubilidad-terreno.json`, el caso
de resolubilidad se ejecutó y midió antes del benchmark especializado de terreno.
Ese benchmark legado seguía en la repetición 17/30, por lo que se detuvo el comando
sin completar el reporte de terreno. Resultados de resolubilidad (20 repeticiones):

| S/E/K | variante | mediana ms | p95 ms | máximo ms |
|---|---|---:|---:|---:|
| 16/16/8 | incremental | 0.938 | 0.996 | 1.282 |
| 32/32/16 | incremental | 1.552 | 1.820 | 1.876 |
| 64/64/32 | incremental | 3.793 | 5.006 | 5.105 |

En esa ejecución, las razones p95 fueron 1.827× y 2.750×; el segundo crecimiento
excedió SC-004. Como comprobación adicional de variabilidad, se repitió directamente
el caso de benchmark con 100 muestras por tamaño, tras verificar equivalencia:

| S/E/K | variante | mediana ms | p95 ms | máximo ms |
|---|---|---:|---:|---:|
| 16/16/8 | incremental | 1.977 | 2.973 | 3.133 |
| 32/32/16 | incremental | 1.810 | 4.412 | 5.409 |
| 64/64/32 | incremental | 3.368 | 4.622 | 8.140 |

Las razones p95 de esta comprobación fueron 1.484× y 1.048×. SC-001 se cumple en
las mediciones sintéticas (todos los p95 <200 ms); SC-004 pasa en el `--bench` completo
y en la comprobación de 100 muestras, pero no en la ejecución de `--bench --salida`.
Por tanto, el resultado de SC-004 es variable y T028 queda pendiente hasta resolver
esa variación y completar el comando con `--salida`. No se afirma cumplimiento sobre
una cripta publicada.

## Preparación

Usar el Python 3.12 del entorno de referencia, instalar dependencias según
`requirements.txt` si faltan, y evitar fuentes de red durante pruebas/mediciones del
modelo. El formato de invocaciones y resultados se detalla en
[contracts/cli.md](./contracts/cli.md); la fuente y el presupuesto en
[contracts/fuente-llaves.md](./contracts/fuente-llaves.md).
