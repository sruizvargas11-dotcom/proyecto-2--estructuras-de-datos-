"""Herramientas comunes de medición: estadísticas, cronometrar, imprimir tabla."""
import math
from dataclasses import dataclass
from time import perf_counter

REPETICIONES = 5


@dataclass
class Medicion:
    """Resultado estadístico de un conjunto de muestras cronometradas."""
    ms_min:   float
    ms_med:   float
    ms_p95:   float
    ms_max:   float
    n_rep:    int
    muestras: tuple  # tiempos en orden de ejecución (ms)


def _cmp_num(a, b):
    return (a > b) - (a < b)


def estadisticas(v):
    """Min, mediana, p95 y máximo; ordenamiento con la implementación del proyecto.

    `v` puede ser cualquier iterable de floats (lista, Vector, generador).
    Deja `v` sin modificar; construye internamente un Vector de trabajo.
    """
    from estructuras.vector_dinamico import Vector
    from estructuras.ordenamientos import ordenar

    muestras_orig = []
    orden = Vector()
    for ms in v:
        orden.agregarValor(ms)
        muestras_orig.append(ms)
    if not len(orden):
        raise ValueError('No hay muestras.')
    ordenar(orden, _cmp_num)
    n = len(orden)
    medio = n // 2
    med = orden.obtenerValor(medio)
    if n % 2 == 0:
        med = (med + orden.obtenerValor(medio - 1)) / 2
    return Medicion(
        ms_min=orden.obtenerValor(0),
        ms_med=med,
        ms_p95=orden.obtenerValor(math.ceil(n * 0.95) - 1),
        ms_max=orden.obtenerValor(n - 1),
        n_rep=n,
        muestras=tuple(muestras_orig),
    )


def mediana(valores):
    """Calcula la mediana — delegado de estadisticas() para compatibilidad."""
    return estadisticas(valores).ms_med


def medir(accion, *argumentos, repeticiones=REPETICIONES, preparar=None):
    """Corre `accion(*argumentos)` varias veces y devuelve Medicion.

    El calentamiento previo no se incluye en las muestras.
    `preparar`, si se pasa, se llama antes de cada repetición cronometrada
    para reiniciar estado mutable fuera del tiempo medido.
    """
    if type(repeticiones) is not int or repeticiones < 1:
        raise ValueError('Las repeticiones deben ser positivas.')
    accion(*argumentos)  # calentamiento excluido de las muestras
    muestras = []
    for _ in range(repeticiones):
        if preparar is not None:
            preparar()
        inicio = perf_counter()
        accion(*argumentos)
        muestras.append((perf_counter() - inicio) * 1000)
    return estadisticas(muestras)


@dataclass
class Fila:
    caso:       str
    variante:   str
    n:          int
    ms:         float    # mediana en ms — mantiene compatibilidad
    extra:      str   = ''
    contadores: tuple = ()
    ms_min:     float = 0.0
    ms_p95:     float = 0.0
    ms_max:     float = 0.0
    n_rep:      int   = 0
    muestras:   tuple = ()

    @classmethod
    def desde_medicion(cls, caso, variante, n, medicion, extra='', contadores=()):
        return cls(
            caso=caso, variante=variante, n=n,
            ms=medicion.ms_med,
            extra=extra, contadores=contadores,
            ms_min=medicion.ms_min, ms_p95=medicion.ms_p95,
            ms_max=medicion.ms_max, n_rep=medicion.n_rep,
            muestras=medicion.muestras,
        )


_SEP = 79


def imprimir_tabla(filas):
    """Imprime las filas como tabla de texto alineada."""
    con_stats = any(f.n_rep > 0 for f in filas)
    if con_stats:
        print(f"{'caso':<16}{'variante':<18}{'n':>8}{'med':>10}{'p95':>10}{'max':>10}{'rep':>5}  extra")
        print('-' * _SEP)
        for f in filas:
            if f.n_rep > 0:
                p95_str = f"{f.ms_p95:.3f}" if f.n_rep >= 20 else "---"
                print(f"{f.caso:<16}{f.variante:<18}{f.n:>8}{f.ms:>10.3f}"
                      f"{p95_str:>10}{f.ms_max:>10.3f}{f.n_rep:>5}  {f.extra}")
            else:
                print(f"{f.caso:<16}{f.variante:<18}{f.n:>8}{f.ms:>10.3f}"
                      f"{'---':>10}{'---':>10}{'---':>5}  {f.extra}")
    else:
        print(f"{'caso':<16}{'variante':<18}{'n':>8}{'ms (med)':>12}  extra")
        print('-' * 68)
        for f in filas:
            print(f"{f.caso:<16}{f.variante:<18}{f.n:>8}{f.ms:>12.3f}  {f.extra}")
