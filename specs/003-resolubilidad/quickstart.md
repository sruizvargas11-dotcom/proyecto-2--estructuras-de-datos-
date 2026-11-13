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

### Evidencia T028 (2026-11-13)

Las mediciones se ejecutaron en el commit limpio `c40f0a4`, Python 3.12.10,
Windows 10 (10.0.19045), Intel Core i7-8750H @ 2.20 GHz. La semilla sintética fue
42. El benchmark usa 50 repeticiones por tamaño y una llamada de calentamiento,
excluida de las muestras; antes de cada medición se comprobó equivalencia de
veredicto, orden y frontera entre la versión incremental y la referencia.
Red, carga de datos y renderizado no forman parte del tiempo medido.

#### SC-001: cripta publicada más grande

Se cargaron el esqueleto y las llaves versionados de
`partidas/cache/cripta-06/` antes de cronometrar; no hubo red ni carga de datos dentro
de la medición. La «Cripta de referencia» tiene 300 salas y 4 llaves. Una llamada de
calentamiento precedió a 100 repeticiones:

| Cripta | versión | mediana ms | p95 ms | máximo ms | veredicto |
|---|---|---:|---:|---:|---|
| cripta-06 | `f9ed9afa683d` | 14.860 | 20.713 | 34.866 | RESOLUBLE |

SC-001 pasa: p95 <200 ms.

#### SC-004: duplicación sintética

La familia de cadenas encadenadas duplica exactamente S, E y K en cada tamaño.
El menor tamaño tuvo mediana ≥10 ms en ambos modos.

Ejecución completa de `python main.py --bench`; evidencia JSON:
`bench/resultados/2026-11-13T120704_c40f0a4_bench.json`.

| S/E/K | variante | mediana ms | p95 ms | máximo ms | razón p95 incremental |
|---|---|---:|---:|---:|---:|
| 192/192/96 | incremental | 12.043 | 24.529 | 25.448 | — |
| 192/192/96 | referencia | 485.742 | 580.134 | 615.862 | — |
| 384/384/192 | incremental | 23.535 | 35.218 | 49.361 | 1.436× |
| 384/384/192 | referencia | 2248.420 | 5527.517 | 6461.719 | — |
| 768/768/384 | incremental | 52.068 | 94.380 | 103.208 | 2.680× |
| 768/768/384 | referencia | 8919.534 | 13689.497 | 14805.982 | — |

Ejecución completa de `python main.py --bench --salida
C:\Temp\resolubilidad-terreno-completo.json` (incluyó el reporte especializado de
terreno; terminó con código 0):

| S/E/K | variante | mediana ms | p95 ms | máximo ms | razón p95 incremental |
|---|---|---:|---:|---:|---:|
| 192/192/96 | incremental | 15.790 | 31.976 | 34.031 | — |
| 192/192/96 | referencia | 525.323 | 870.029 | 961.835 | — |
| 384/384/192 | incremental | 25.449 | 59.129 | 66.778 | 1.849× |
| 384/384/192 | referencia | 2083.714 | 2443.012 | 2772.630 | — |
| 768/768/384 | incremental | 47.724 | 61.447 | 103.726 | 1.039× |
| 768/768/384 | referencia | 9055.908 | 12779.000 | 13024.505 | — |

SC-004 pasa en `--bench --salida`, pero falla en `--bench`: la última duplicación
creció 2.680×, mayor que el máximo permitido de 2.5×. T028 permanece pendiente;
no se cambió SC-001, SC-004 ni sus umbrales.

#### Perfil y propuesta

Ante el incumplimiento de SC-004, se perfiló una verificación de una cripta sintética
de S/E/K = 768/768/384 con `cProfile` (162 195 llamadas, 0.294 s bajo perfil). El
tiempo acumulado principal fue: `TablaHash._hash` 0.105 s, FNV-1a 0.057 s,
`expandir_region` 0.081 s y `TablaHash.insertar` 0.075 s. La propuesta —no aplicada—
es reducir búsquedas repetidas en la expansión y en el registro de candidatas,
evaluando una operación de tabla que combine comprobación/obtención e inserción
cuando proceda, sin cambiar FNV-1a ni introducir índices nativos. Luego se debe
repetir el protocolo completo de ambos modos y comprobar equivalencia primero.

## Preparación

Usar el Python 3.12 del entorno de referencia, instalar dependencias según
`requirements.txt` si faltan, y evitar fuentes de red durante pruebas/mediciones del
modelo. El formato de invocaciones y resultados se detalla en
[contracts/cli.md](./contracts/cli.md); la fuente y el presupuesto en
[contracts/fuente-llaves.md](./contracts/fuente-llaves.md).
