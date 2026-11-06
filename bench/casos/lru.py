"""Compara ListaLRU con índice hash vs búsqueda lineal, misma política.

Ambos modos están en estructuras/listalru.py:
  - indice='lineal': recorre la lista completa, O(n) por buscar
  - indice='hash':   acceso por TablaHash propia, O(1) esperado

Usa la misma capacidad, la misma política de desalojo y la misma
secuencia de accesos (semilla fija). Antes de medir tiempos verifica que
aciertos, fallos y desalojos sean idénticos en ambos modos; si no lo son,
lanza AssertionError con el detalle.

Dos operaciones medidas por separado:
  - buscar_aislado: caché pre-llenada, solo buscar (todos son hits)
  - cache_completo: secuencia completa con misses e inserciones
"""
import random
from bench.medicion import Fila, medir
from estructuras.listalru import CAPACIDAD_DEFECTO

CAPACIDADES = (CAPACIDAD_DEFECTO, 100, 500)
BUSQUEDAS = 1000
CLAVES_FACTOR = 1.6   # claves_distintas = int(cap * CLAVES_FACTOR) > cap
REPETICIONES_LRU = 20


def _secuencia_completa(cap, semilla=42):
    """Accesos aleatorios con más claves que cap → hay desalojos."""
    rnd = random.Random(semilla)
    n_claves = int(cap * CLAVES_FACTOR)
    return [rnd.randrange(n_claves) for _ in range(BUSQUEDAS)]


def _secuencia_busquedas(cap, semilla=99):
    """Solo claves 0..cap-1 → todos son hits en una caché pre-llenada."""
    rnd = random.Random(semilla)
    return [rnd.randrange(cap) for _ in range(BUSQUEDAS)]


def _verificar_coincidencia(cap, secuencia):
    """Levanta AssertionError si lineal y hash no producen los mismos contadores."""
    from estructuras.listalru import ListaLRU
    resultados = {}
    for modo in ("lineal", "hash"):
        cache = ListaLRU(cap, indice=modo)
        for clave in secuencia:
            if cache.buscar(clave) is None:
                cache.insertar(clave, clave)
        resultados[modo] = cache.contadores()
    if resultados["lineal"] != resultados["hash"]:
        raise AssertionError(
            f"Contadores distintos cap={cap}: "
            f"lineal={resultados['lineal']} hash={resultados['hash']}"
        )
    return resultados["lineal"]   # (aciertos, fallos, desalojos)


def _medir_buscar_aislado(cap, indice, sec_busquedas):
    """Caché pre-llenada con cap claves; mide solo buscar (siempre hits)."""
    from estructuras.listalru import ListaLRU
    estado = [None]

    def preparar():
        estado[0] = ListaLRU(cap, indice=indice)
        for i in range(cap):
            estado[0].insertar(i, i)

    preparar()

    def buscar():
        c = estado[0]
        for clave in sec_busquedas:
            c.buscar(clave)

    return medir(buscar, repeticiones=REPETICIONES_LRU, preparar=preparar)


def _medir_cache_completo(cap, indice, sec_completa):
    """Secuencia completa: buscar + insertar en fallo, caché vacía al inicio."""
    from estructuras.listalru import ListaLRU
    estado = [None]

    def preparar():
        estado[0] = ListaLRU(cap, indice=indice)

    preparar()

    def operar():
        c = estado[0]
        for clave in sec_completa:
            if c.buscar(clave) is None:
                c.insertar(clave, clave)

    return medir(operar, repeticiones=REPETICIONES_LRU, preparar=preparar)


def correr():
    filas = []
    for cap in CAPACIDADES:
        sec_completa = _secuencia_completa(cap)
        sec_busquedas = _secuencia_busquedas(cap)

        aciertos, fallos, desalojos = _verificar_coincidencia(cap, sec_completa)
        extra_completo = (
            f"busquedas={BUSQUEDAS}; aciertos={aciertos}; "
            f"fallos={fallos}; desalojos={desalojos}"
        )
        extra_buscar = f"busquedas={BUSQUEDAS}; cap={cap}; solo_hits"

        for indice in ("lineal", "hash"):
            m_buscar = _medir_buscar_aislado(cap, indice, sec_busquedas)
            m_completo = _medir_cache_completo(cap, indice, sec_completa)

            filas.append(Fila.desde_medicion(
                "cache_buscar", indice, cap, m_buscar,
                extra_buscar,
                (("aciertos_potenciales", BUSQUEDAS),),
            ))
            filas.append(Fila.desde_medicion(
                "cache", indice, cap, m_completo,
                extra_completo,
                (("aciertos", aciertos), ("fallos", fallos)),
            ))

    return filas
