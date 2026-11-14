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

Mediciones en el commit limpio `b0ee832`, Python 3.12.10, Windows 10
(10.0.19045), Intel Core i7-8750H @ 2.20 GHz (la evidencia del runner identifica
la CPU como Intel64 Family 6 Model 158 Stepping 10). Semilla sintética: 42.
Antes de cronometrar se comparan veredicto, orden y frontera con la referencia.
Cada variante se calienta una vez; el GC se deshabilita solo durante las muestras
y se restaura al terminar. Hubo 100 repeticiones incrementales y 20 de referencia;
carga de datos, red y renderizado quedan fuera del tiempo.

#### Dispersión inicial

Cinco ejecuciones preliminares con semilla 42 y K=96/192/384 dieron estas razones
entre p95 incremental consecutivos:

| Ejecución | 96→192 | 192→384 |
|---|---:|---:|
| 1 | 2.105× | 2.234× |
| 2 | 2.648× | 3.172× |
| 3 | 3.335× | 3.094× |
| 4 | 1.063× | 1.989× |
| 5 | 3.004× | 0.777× |
| Rango | 1.063–3.335× | 0.777–3.172× |
| Mediana | 2.648× | 2.234× |

La dispersión indicaba ruido. Se aisló la recolección de basura de las muestras,
se mantuvo el calentamiento fuera del cronometraje, se aumentaron las repeticiones
y se calibró el tamaño mínimo por encima de 10 ms.

#### SC-001: cripta publicada más grande

El esqueleto y las ubicaciones versionadas de `partidas/cache/cripta-06/` se
cargaron directamente desde caché antes de medir; no hubo red ni lectura de datos
dentro del cronometraje. La cripta tiene 300 salas y 4 llaves; se hizo un
calentamiento y 100 repeticiones con GC deshabilitado:

| Cripta | versión | n | mediana ms | p95 ms | máximo ms | veredicto |
|---|---|---:|---:|---:|---:|---|
| cripta-06 | `f9ed9afa683d` | 100 | 11.177 | 16.074 | 30.315 | RESOLUBLE |

SC-001 pasa: p95 = 16.074 ms < 200 ms.

#### SC-004: duplicación sintética

La familia de cadenas encadenadas duplica exactamente S, E y K. En el menor
tamaño, la mediana incremental fue 12.700 ms y la de referencia 689.320 ms.
Ejecución completa de `python main.py --bench`; evidencia:
`bench/resultados/2026-11-13T171401_b0ee832_bench.json`.

| S/E/K | variante | n | mediana ms | p95 ms | máximo ms | razón p95 incremental |
|---|---|---:|---:|---:|---:|---:|
| 256/256/128 | incremental | 100 | 12.700 | 16.804 | 35.596 | — |
| 256/256/128 | referencia | 20 | 689.320 | 741.176 | 844.634 | — |
| 512/512/256 | incremental | 100 | 25.938 | 35.474 | 48.700 | 2.111× |
| 512/512/256 | referencia | 20 | 2822.413 | 2953.073 | 2953.964 | — |
| 1024/1024/512 | incremental | 100 | 51.666 | 58.179 | 72.821 | 1.640× |
| 1024/1024/512 | referencia | 20 | 12840.450 | 14308.241 | 24110.091 | — |

También se ejecutó `python main.py --bench --salida <ruta>` en el mismo commit
limpio y se detuvo después de imprimirse la tabla de resolubilidad, antes del
reporte de terreno:

| S/E/K | variante | n | mediana ms | p95 ms | máximo ms | razón p95 incremental |
|---|---|---:|---:|---:|---:|---:|
| 256/256/128 | incremental | 100 | 16.462 | 25.169 | 32.780 | — |
| 256/256/128 | referencia | 20 | 790.764 | 939.935 | 968.572 | — |
| 512/512/256 | incremental | 100 | 26.110 | 31.468 | 54.825 | 1.250× |
| 512/512/256 | referencia | 20 | 3109.695 | 3825.157 | 4490.597 | — |
| 1024/1024/512 | incremental | 100 | 53.804 | 62.256 | 72.688 | 1.979× |
| 1024/1024/512 | referencia | 20 | 11876.145 | 12585.742 | 12914.881 | — |

SC-004 pasa en ambos modos: todas las duplicaciones incrementan p95 ≤2.5×.

#### Perfil y decisión

`cProfile` antes/después, con la misma cripta sintética S/E/K=1024/1024/512:

| Medición | Antes | Después |
|---|---:|---:|
| Llamadas totales | 216 211 | 208 027 |
| Tiempo bajo perfil | 0.170 s | 0.174 s |
| `TablaHash._hash` llamadas | 15 364 | 14 341 |
| `contiene` llamadas | 5 123 | 4 099 |

Se redujeron 1 023 llamadas a `_hash` y 1 024 búsquedas `contiene`; el tiempo
profilado no demuestra una mejora por sí solo y se considera ruidoso. La decisión
fue combinar la comprobación e inserción en la expansión de región usando el
resultado booleano de `TablaHash.insertar`, sin cambiar FNV-1a ni introducir
índices nativos. La mejora se acepta por la reducción de trabajo repetido y por
cumplir SC-004 en las mediciones finales; no se atribuye al profiler una reducción
de tiempo.

## Preparación

Usar el Python 3.12 del entorno de referencia, instalar dependencias según
`requirements.txt` si faltan, y evitar fuentes de red durante pruebas/mediciones del
modelo. El formato de invocaciones y resultados se detalla en
[contracts/cli.md](./contracts/cli.md); la fuente y el presupuesto en
[contracts/fuente-llaves.md](./contracts/fuente-llaves.md).
