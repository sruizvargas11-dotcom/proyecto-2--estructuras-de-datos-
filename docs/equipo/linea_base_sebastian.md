# Línea base — rama base/sebastian

## 1. Identificación

| Campo   | Valor                                      |
|---------|--------------------------------------------|
| Fecha   | 2026-11-05                                 |
| Rama    | base/sebastian                             |
| Commit  | 43332618244334b81f247ff12fb3d531fb821316   |

La rama ya incluye el commit `4333261` de Daniel Centeno
(`origin/Hash-Table`, "Se implementa Hash Table para manejo de la caché").
La revisión inicial del equipo —antes de ese cambio— reportó **1 088 pruebas**.

## 2. Entorno

| Campo               | Valor                        |
|---------------------|------------------------------|
| Python              | 3.12.10                      |
| Sistema operativo   | Microsoft Windows 11 Home    |
| Versión NT          | 10.0.26200.0                 |

### Dependencias instaladas (`requirements.txt` no fija versiones)

| Paquete             | Versión instalada |
|---------------------|-------------------|
| requests            | 2.34.2            |
| pytest              | 9.2.0             |
| pygame              | 2.6.1             |
| urllib3             | 2.8.0             |
| certifi             | 2026.10.23        |
| charset-normalizer  | 3.5.2             |
| idna                | 3.20              |
| colorama            | 0.4.6             |
| iniconfig           | 2.3.1             |
| packaging           | 26.3              |
| pluggy              | 1.7.0             |

## 3. Pruebas

```
1149 passed in 125.41s (0:02:05)
```

**1 149 pruebas**, todas pasan. Tiempo total: **125.41 s**.

La diferencia respecto a las 1 088 pruebas de la revisión inicial se explica
por el commit de la tabla hash de Centeno (`4333261`), que agregó pruebas al
incorporarse en esta rama.

## 4. Salida completa de `main.py --bench`

```
caso            variante                 n    ms (med)  extra
--------------------------------------------------------------------
mensajes        circular                20       0.007  agregados=20; desplazamientos=0
mensajes        desplazamiento          20       0.002  agregados=20; desplazamientos=0
mensajes        circular             20000       5.094  agregados=20000; desplazamientos=0
mensajes        desplazamiento       20000      15.712  agregados=20000; desplazamientos=379620
agenda_eventos  HeapMinimo             100     104.541  extracciones=20001; inserciones=20101
agenda_eventos  lista_lineal           100      70.998  extracciones=20001; inserciones=20101
agenda_eventos  HeapMinimo             500     150.197  extracciones=20001; inserciones=20501
agenda_eventos  lista_lineal           500     354.616  extracciones=20001; inserciones=20501
agenda_eventos  HeapMinimo            1000     140.221  extracciones=20001; inserciones=21001
agenda_eventos  lista_lineal          1000     752.112  extracciones=20001; inserciones=21001
agenda_eventos  HeapMinimo            5000     182.784  extracciones=20001; inserciones=25001
agenda_eventos  lista_lineal          5000    3856.122  extracciones=20001; inserciones=25001
proximos_turnos vista_ordenada(5)      100       4.809  200 llamadas/repetición
proximos_turnos copiar_y_ordenar       100     219.908  200 llamadas/repetición
proximos_turnos vista_ordenada(5)      500       6.162  200 llamadas/repetición
proximos_turnos copiar_y_ordenar       500    1283.672  200 llamadas/repetición
proximos_turnos vista_ordenada(5)     1000       4.289  200 llamadas/repetición
proximos_turnos copiar_y_ordenar      1000    2600.917  200 llamadas/repetición
proximos_turnos vista_ordenada(5)     5000       5.944  200 llamadas/repetición
proximos_turnos copiar_y_ordenar      5000   17618.060  200 llamadas/repetición
cache           ListaLRU              1000       4.299  aciertos=617; fallos=383
cache           lista_plana           1000       0.690  aciertos=960; fallos=40
recuperacion    en_memoria              25       0.229
recuperacion    desde_disco             25       3.016
inventario      ListaDoble              10       0.006
inventario      list                    10       0.001
inventario      ListaDoble              50       0.025
inventario      list                    50       0.003
inventario      ListaDoble             500       0.262
inventario      list                   500       0.041
historial       deltas                 100       0.183  valores_guardados=5; cambios=5; reversiones=5; PRNG incluido
historial       copias                 100       0.082  valores_guardados=500; cambios=5; reversiones=5; PRNG incluido
historial       deltas                1000       0.074  valores_guardados=5; cambios=5; reversiones=5; PRNG incluido
historial       copias                1000       0.264  valores_guardados=5000; cambios=5; reversiones=5; PRNG incluido
historial       deltas               10000       0.079  valores_guardados=5; cambios=5; reversiones=5; PRNG incluido
historial       copias               10000       2.282  valores_guardados=50000; cambios=5; reversiones=5; PRNG incluido
ordenamiento    insertion_sort           5       0.007  aleatorio; rep=7; muestras=20
ordenamiento    merge_sort               5       0.024  aleatorio; rep=7; muestras=20
ordenamiento    insertion_sort          10       0.020  aleatorio; rep=7; muestras=20
ordenamiento    merge_sort              10       0.059  aleatorio; rep=7; muestras=20
ordenamiento    insertion_sort          15       0.036  aleatorio; rep=7; muestras=20
ordenamiento    merge_sort              15       0.069  aleatorio; rep=7; muestras=20
ordenamiento    insertion_sort          20       0.066  aleatorio; rep=7; muestras=20
ordenamiento    merge_sort              20       0.130  aleatorio; rep=7; muestras=20
ordenamiento    insertion_sort          25       0.103  aleatorio; rep=7; muestras=20
ordenamiento    merge_sort              25       0.175  aleatorio; rep=7; muestras=20
ordenamiento    insertion_sort          30       0.151  aleatorio; rep=7; muestras=20
ordenamiento    merge_sort              30       0.264  aleatorio; rep=7; muestras=20
ordenamiento    insertion_sort          50       0.308  aleatorio; rep=7; muestras=20
ordenamiento    merge_sort              50       0.466  aleatorio; rep=7; muestras=20
ordenamiento    insertion_sort          60       0.513  aleatorio; rep=7; muestras=20
ordenamiento    merge_sort              60       0.512  aleatorio; rep=7; muestras=20
ordenamiento    insertion_sort          75       0.657  aleatorio; rep=7; muestras=20
ordenamiento    merge_sort              75       0.509  aleatorio; rep=7; muestras=20
ordenamiento    insertion_sort         100       1.287  aleatorio; rep=7; muestras=20
ordenamiento    merge_sort             100       0.725  aleatorio; rep=7; muestras=20
ordenamiento    insertion_sort         200       5.135  aleatorio; rep=7; muestras=20
ordenamiento    merge_sort             200       1.662  aleatorio; rep=7; muestras=20
ordenamiento    insertion_sort         500      34.469  aleatorio; rep=7; muestras=20
ordenamiento    merge_sort             500       6.232  aleatorio; rep=7; muestras=20
ordenamiento    insertion_sort           5       0.003  casi_ordenado; rep=7; muestras=20
ordenamiento    merge_sort               5       0.015  casi_ordenado; rep=7; muestras=20
ordenamiento    insertion_sort          10       0.007  casi_ordenado; rep=7; muestras=20
ordenamiento    merge_sort              10       0.040  casi_ordenado; rep=7; muestras=20
ordenamiento    insertion_sort          15       0.011  casi_ordenado; rep=7; muestras=20
ordenamiento    merge_sort              15       0.076  casi_ordenado; rep=7; muestras=20
ordenamiento    insertion_sort          20       0.015  casi_ordenado; rep=7; muestras=20
ordenamiento    merge_sort              20       0.097  casi_ordenado; rep=7; muestras=20
ordenamiento    insertion_sort          25       0.020  casi_ordenado; rep=7; muestras=20
ordenamiento    merge_sort              25       0.128  casi_ordenado; rep=7; muestras=20
ordenamiento    insertion_sort          30       0.021  casi_ordenado; rep=7; muestras=20
ordenamiento    merge_sort              30       0.155  casi_ordenado; rep=7; muestras=20
ordenamiento    insertion_sort          50       0.077  casi_ordenado; rep=7; muestras=20
ordenamiento    merge_sort              50       0.430  casi_ordenado; rep=7; muestras=20
ordenamiento    insertion_sort          60       0.101  casi_ordenado; rep=7; muestras=20
ordenamiento    merge_sort              60       0.484  casi_ordenado; rep=7; muestras=20
ordenamiento    insertion_sort          75       0.109  casi_ordenado; rep=7; muestras=20
ordenamiento    merge_sort              75       0.582  casi_ordenado; rep=7; muestras=20
ordenamiento    insertion_sort         100       0.160  casi_ordenado; rep=7; muestras=20
ordenamiento    merge_sort             100       0.693  casi_ordenado; rep=7; muestras=20
ordenamiento    insertion_sort         200       0.624  casi_ordenado; rep=7; muestras=20
ordenamiento    merge_sort             200       1.647  casi_ordenado; rep=7; muestras=20
ordenamiento    insertion_sort         500       3.680  casi_ordenado; rep=7; muestras=20
ordenamiento    merge_sort             500       4.568  casi_ordenado; rep=7; muestras=20
guardado        binario                 50       0.778  bytes=11978
guardado        json                    50       0.809  bytes=11964
carga_total     binario                 50       1.503
carga_total     json                    50       0.174
carga_1_sala    binario                 50       0.086  usa índice
carga_1_sala    json                    50       0.174  lee todo
guardado        binario                500       5.444  bytes=118609
guardado        json                   500       5.304  bytes=118996
carga_total     binario                500       7.246
carga_total     json                   500       0.930
carga_1_sala    binario                500       0.099  usa índice
carga_1_sala    json                   500       0.930  lee todo
guardado        binario               5000      39.963  bytes=1186399
guardado        json                  5000      39.668  bytes=1195115
carga_total     binario               5000      97.544
carga_total     json                  5000      13.403
carga_1_sala    binario               5000       0.172  usa índice
carga_1_sala    json                  5000      13.403  lee todo
```

## 5. Problemas de entorno encontrados

**a) Python 3.14 incompatible con pygame 2.6.1**
El entorno virtual estaba originalmente creado con Python 3.14.3. `pygame 2.6.1`
no tiene paquete precompilado (`wheel`) para CPython 3.14 e intenta compilarse
desde fuente, fallando durante `pip install`. Se resolvió recreando el entorno
con Python 3.12:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
```

**b) pytest no estaba instalado en el entorno anterior**
El entorno con Python 3.14 no tenía `pytest` instalado, por lo que cualquier
intento de correr las pruebas fallaba con `No module named pytest`.

**c) `requirements.txt` no fija versiones**
El archivo declara solo los nombres de los paquetes sin restricciones de versión
(`requests`, `pytest`, `pygame`), lo que hace que `pip install` resuelva las
versiones más recientes disponibles en el momento de la instalación. Las versiones
que quedaron registradas en la sección 2 de este documento son las que resolvió
pip con Python 3.12.10 el 2026-11-05.

## 6. Cambio de metodología (B05)

Los tiempos de la sección 4 —en particular los de `binario_json`— se
obtuvieron con el medidor original (`bench_bloque3.medir`), que usaba
`time.time()` sobre un **lote** de 5 llamadas consecutivas y dividía el
total:

```python
# metodología pre-B05
t0 = time()
for _ in range(repeticiones):
    func()
return (time() - t0) / repeticiones * 1000  # media de lote en ms
```

Desde **B05** (`bench.medicion.medir`) cada llamada se cronometra por
separado con `perf_counter()` y el resultado es la **mediana** de las
muestras individuales:

```python
# metodología B05
for _ in range(repeticiones):
    inicio = perf_counter()
    accion(*argumentos)
    muestras.append((perf_counter() - inicio) * 1000)
return estadisticas(muestras)  # devuelve Medicion con min/med/p95/max
```

Consecuencias observadas:
- `perf_counter()` es de alta resolución; el jitter del OS scheduler
  aparece íntegro en cada muestra, en lugar de diluirse en un lote.
- La mediana individual puede ser mayor que la media de lote para
  operaciones sub-2 ms donde el jitter domina.
- Los valores de `binario_json` de la sección 4 **no son comparables**
  con los producidos por B05; los nuevos los reemplazan como referencia.

## Nota

Estos tiempos son la **referencia antes de**:
- **B05** — unificación de mediciones (implementado en esta rama).
- **B02** — comparación justa de caché (pendiente).

Los valores de `ordenamiento` e `historial` son comparables entre la
línea base y B05 porque ambas versiones ya medían por llamada individual.
Los de `binario_json` **no** son comparables por el cambio de metodología
descrito arriba.
