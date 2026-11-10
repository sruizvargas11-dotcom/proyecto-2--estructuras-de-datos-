"""Pruebas de la tabla hash propia (B01): función hash estable, colisiones
forzadas, actualización, borrado en cualquier punto de la cadena y crecimiento.

El oráculo de las pruebas aleatorias es una lista de pares, no un dict, para
no depender de la estructura que se está reemplazando.
"""
import os
import random
import subprocess
import sys

import pytest

from estructuras.tabla_hash import (
    CUBETAS_MINIMAS, TablaHash, _EntradaHash, hash_clave,
)

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _colision_total(_clave):
    return 0


# -- función hash -----------------------------------------------------------

def test_fnv1a_coincide_con_valores_de_referencia():
    # Vectores publicados de FNV-1a de 32 bits.
    assert hash_clave('') == 0x811C9DC5
    assert hash_clave('a') == 0xE40C292C
    assert hash_clave('foobar') == 0xBF9CF968


def test_hash_de_enteros_es_estable_y_acepta_negativos():
    assert hash_clave(0) == hash_clave(0)
    assert hash_clave(-1) != hash_clave(1)
    assert 0 <= hash_clave(-(2 ** 70)) <= 0xFFFFFFFF


@pytest.mark.parametrize('clave', [True, 1.5, None, ('a',), b'a'])
def test_hash_rechaza_tipos_no_admitidos(clave):
    with pytest.raises(TypeError):
        hash_clave(clave)


def test_hash_no_depende_del_proceso():
    """hash() de Python cambia con PYTHONHASHSEED; el nuestro no."""
    codigo = ('from estructuras.tabla_hash import hash_clave;'
              'print(hash_clave("ent_rata_gigante"), hash_clave(12345))')
    salidas = []
    for semilla in ('1', '2'):
        entorno = dict(os.environ, PYTHONHASHSEED=semilla, PYTHONPATH=RAIZ)
        salidas.append(subprocess.run([sys.executable, '-c', codigo], cwd=RAIZ, env=entorno,
                                      capture_output=True, text=True, check=True).stdout)
    assert salidas[0] == salidas[1]
    assert salidas[0].split() == [str(hash_clave('ent_rata_gigante')), str(hash_clave(12345))]


# -- operaciones básicas ----------------------------------------------------

def test_insertar_obtener_actualizar_y_eliminar():
    t = TablaHash()
    assert t.esta_vacia() and t.obtener('x') is None and not t.contiene('x')
    assert t.insertar('x', 1) is True
    assert t.insertar('x', 2) is False          # actualización, no duplica
    assert len(t) == 1 and t.obtener('x') == 2
    assert t.contador_inserciones == 1 and t.contador_actualizaciones == 1
    assert t.eliminar('x') is True and t.eliminar('x') is False
    assert len(t) == 0 and t.obtener('x', 'nada') == 'nada'
    assert t.insertar('x', 3) and t.obtener('x') == 3
    t._verificar_invariantes()


def test_texto_y_entero_con_igual_representacion_no_se_mezclan():
    t = TablaHash()
    t.insertar(1, 'entero')
    t.insertar('1', 'texto')
    assert t.obtener(1) == 'entero' and t.obtener('1') == 'texto' and len(t) == 2


def test_valores_none_se_distinguen_de_ausencia_con_contiene():
    t = TablaHash()
    t.insertar('a', None)
    assert t.contiene('a') and t.obtener('a', 'ausente') is None


@pytest.mark.parametrize('kwargs', [
    {'capacidad_inicial': -1}, {'capacidad_inicial': 2.0},
    {'factor_carga_maximo': 0}, {'factor_carga_maximo': 1.5},
    {'funcion_hash': 'no invocable'},
])
def test_parametros_invalidos(kwargs):
    with pytest.raises(ValueError):
        TablaHash(**kwargs)


def test_funcion_hash_inyectada_debe_devolver_entero_no_negativo():
    t = TablaHash(funcion_hash=lambda c: -1)
    with pytest.raises(ValueError):
        t.insertar('a', 1)


# -- colisiones forzadas ----------------------------------------------------

def test_colision_total_conserva_todas_las_claves():
    t = TablaHash(funcion_hash=_colision_total)
    claves = [f'id_{i}' for i in range(40)]
    for i, clave in enumerate(claves):
        t.insertar(clave, i)
    assert t.cubetas_ocupadas() == 1 and t.cadena_maxima() == 40
    assert t.contador_colisiones == 39
    for i, clave in enumerate(claves):
        assert t.obtener(clave) == i
    t._verificar_invariantes()


@pytest.mark.parametrize('posicion', ['cabeza', 'medio', 'final'])
def test_borrar_en_cualquier_punto_de_una_cadena(posicion):
    t = TablaHash(funcion_hash=_colision_total)
    for clave in 'abcde':
        t.insertar(clave, clave.upper())
    # Se inserta por la cabeza: la cadena queda e -> d -> c -> b -> a.
    victima = {'cabeza': 'e', 'medio': 'c', 'final': 'a'}[posicion]
    assert t.eliminar(victima)
    assert t.obtener(victima) is None and len(t) == 4
    for clave in 'abcde':
        if clave != victima:
            assert t.obtener(clave) == clave.upper()
    t._verificar_invariantes()


def test_colision_parcial_y_actualizacion_dentro_de_la_cadena():
    t = TablaHash(funcion_hash=lambda c: c % 3)
    for k in range(30):
        t.insertar(k, k)
    for k in range(0, 30, 2):
        assert t.insertar(k, -k) is False
    assert len(t) == 30
    for k in range(30):
        assert t.obtener(k) == (-k if k % 2 == 0 else k)
    t._verificar_invariantes()


def test_mismo_hash_distinta_clave_cuenta_comparacion():
    t = TablaHash(funcion_hash=_colision_total)
    t.insertar('a', 1)
    antes = t.contador_comparaciones
    assert t.obtener('b') is None
    assert t.contador_comparaciones == antes + 1


# -- crecimiento ------------------------------------------------------------

def test_crece_duplicando_y_conserva_entradas():
    t = TablaHash(0)
    assert t.cantidad_cubetas() == CUBETAS_MINIMAS
    entradas = []
    for k in range(100):
        t.insertar(f'k{k}', k)
        entradas.append(t._buscar_sin_contar(f'k{k}'))
        assert t.factor_carga() <= 0.75
    # 8 -> 16 -> 32 -> 64 -> 128 -> 256
    assert t.cantidad_cubetas() == 256 and t.contador_redimensionamientos == 5
    for k in range(100):
        assert t.obtener(f'k{k}') == k
        # Crecer reutiliza la misma entrada y su hash guardado.
        assert t._buscar_sin_contar(f'k{k}') is entradas[k]
    t._verificar_invariantes()


def test_crecer_con_colision_total():
    t = TablaHash(0, funcion_hash=_colision_total)
    for k in range(50):
        t.insertar(k, k)
    assert t.contador_redimensionamientos > 0 and t.cadena_maxima() == 50
    assert all(t.obtener(k) == k for k in range(50))
    t._verificar_invariantes()


def test_capacidad_inicial_evita_crecer():
    t = TablaHash(25)
    for k in range(25):
        t.insertar(k, k)
    assert t.contador_redimensionamientos == 0
    t.insertar(25, 25)                    # 64 cubetas * 0.75 = 48: aún cabe
    assert t.contador_redimensionamientos == 0


def test_borrar_todo_y_reutilizar():
    t = TablaHash(0)
    for k in range(20):
        t.insertar(k, k)
    for k in range(20):
        assert t.eliminar(k)
    assert t.esta_vacia() and t.cubetas_ocupadas() == 0
    t.insertar('nuevo', 1)
    assert t.obtener('nuevo') == 1
    t._verificar_invariantes()


# -- consistencia general ---------------------------------------------------

def _oraculo_buscar(pares, clave):
    for i, (k, _) in enumerate(pares):
        if k == clave:
            return i
    return -1


@pytest.mark.parametrize('funcion', [None, lambda c: c % 7])
def test_operaciones_aleatorias_contra_oraculo(funcion):
    rnd = random.Random(42)
    t = TablaHash(0, funcion_hash=funcion)
    pares = []
    for paso in range(3000):
        clave = rnd.randrange(200)
        operacion = rnd.random()
        i = _oraculo_buscar(pares, clave)
        if operacion < 0.5:
            assert t.insertar(clave, paso) is (i == -1)
            if i == -1:
                pares.append((clave, paso))
            else:
                pares[i] = (clave, paso)
        elif operacion < 0.8:
            assert t.eliminar(clave) is (i != -1)
            if i != -1:
                pares.pop(i)
        else:
            assert t.obtener(clave) == (None if i == -1 else pares[i][1])
        if paso % 250 == 0:
            t._verificar_invariantes()
    assert len(t) == len(pares)
    assert sorted(t.recorrer_claves()) == sorted(k for k, _ in pares)
    t._verificar_invariantes()


def test_diagnostico_no_altera_contadores():
    t = TablaHash(funcion_hash=lambda c: c % 2)
    for k in range(6):
        t.insertar(k, k)
    t.obtener(3)
    antes = t.contadores()
    t.cadena_maxima(), t.cubetas_ocupadas(), t.factor_carga()
    t._verificar_invariantes()
    list(t.recorrer_claves())
    assert t.contadores() == antes


def test_invariantes_detectan_entrada_en_cubeta_equivocada():
    t = TablaHash()
    t.insertar('a', 1)
    indice = t._indice(t._hash('a'))
    t._cubetas[indice] = None
    t._cubetas[(indice + 1) % t.cantidad_cubetas()] = _EntradaHash('a', t._hash('a'), 1)
    with pytest.raises(AssertionError):
        t._verificar_invariantes()
