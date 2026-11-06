"""ListaLRU con índice hash (B01): índice y lista sincronizados, protección de
fichas en uso, mismos resultados que la búsqueda lineal, colisiones forzadas,
guardado entre procesos y guardados anteriores al índice.
"""
import json
import os
import random
import subprocess
import sys

import pytest

from estructuras.listalru import ListaLRU
from estructuras.tabla_hash import TablaHash
from persistencia.estado_partida import codificar, decodificar

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _ids_en_orden(lru):
    ids, nodo = [], lru._lista.head()
    while nodo is not None:
        ids.append(nodo.valor.id_ficha)
        nodo = nodo.siguiente
    return ids


def _ficha(id_ficha):
    return {'id': id_ficha}


# -- sincronización índice <-> lista ---------------------------------------

def test_el_indice_apunta_al_nodo_de_la_lista():
    lru = ListaLRU(3)
    for k in ('a', 'b', 'c'):
        lru.insertar(k, _ficha(k))
    nodo = lru._indice.obtener('b')
    assert lru._nodo('b') is nodo and nodo.valor.id_ficha == 'b'
    assert lru._lista.pertenece(nodo)
    lru._verificar_invariantes()


def test_desalojo_quita_la_ficha_del_indice():
    lru = ListaLRU(2)
    lru.insertar('a', _ficha('a'))
    lru.insertar('b', _ficha('b'))
    lru.insertar('c', _ficha('c'))           # desaloja 'a', la menos reciente
    assert lru._indice.obtener('a') is None and lru.buscar('a') is None
    assert len(lru._indice) == 2 and lru.contador_desalojos == 1
    lru._verificar_invariantes()


def test_actualizar_no_duplica_en_el_indice():
    lru = ListaLRU(2)
    primera, segunda = _ficha('a'), _ficha('a')
    lru.insertar('a', primera)
    nodo = lru._nodo('a')
    lru.insertar('a', segunda)
    assert lru._nodo('a') is nodo and lru.buscar('a') is segunda
    assert len(lru._indice) == 1 and lru.contador_actualizaciones == 1
    lru._verificar_invariantes()


def test_buscar_cuesta_una_comparacion_en_vez_de_recorrer():
    con_hash, lineal = ListaLRU(25), ListaLRU(25, indice='lineal')
    for lru in (con_hash, lineal):
        for k in range(25):
            lru.insertar(f'ent_{k}', _ficha(k))
    for lru in (con_hash, lineal):
        antes = lru.contador_comparaciones
        lru.buscar('ent_0')                  # la menos reciente: fondo de la lista
        lru.diferencia = lru.contador_comparaciones - antes
    assert con_hash.diferencia == 1 and lineal.diferencia == 25


def test_indice_dimensionado_no_crece_en_uso_normal():
    lru = ListaLRU(25)
    for k in range(500):
        lru.insertar(k % 60, _ficha(k))
    assert lru._indice.contador_redimensionamientos == 0
    lru._verificar_invariantes()


def test_indice_invalido_y_claves_no_admitidas():
    with pytest.raises(ValueError):
        ListaLRU(5, indice='dict')
    with pytest.raises(TypeError):
        ListaLRU(5).insertar(True, _ficha('x'))


# -- protección de fichas en uso -------------------------------------------

def test_desalojo_salta_protegidas_y_lo_cuenta():
    lru = ListaLRU(3)
    for k in ('a', 'b', 'c'):
        lru.insertar(k, _ficha(k))
    lru.marcar_en_uso('a')                   # la menos reciente, protegida
    lru.marcar_en_uso('b')
    assert lru.insertar('d', _ficha('d'))
    assert lru.buscar('c') is None           # única libre: se desalojó
    assert lru.contiene('a') and lru.contiene('b')
    assert lru.contador_protegidas_saltadas == 2
    assert ('protegidas_saltadas', 2) in lru.contadores_operaciones()
    lru._verificar_invariantes()


def test_todas_protegidas_rechaza_sin_romper_el_indice():
    lru = ListaLRU(2)
    for k in ('a', 'b'):
        lru.insertar(k, _ficha(k))
        lru.marcar_en_uso(k)
    assert lru.insertar('c', _ficha('c')) is False
    assert lru.contador_rechazos_capacidad == 1 and len(lru._indice) == 2
    assert lru._indice.obtener('c') is None
    lru.desmarcar_en_uso('a')
    assert lru.insertar('c', _ficha('c')) and lru.buscar('a') is None
    lru._verificar_invariantes()


def test_contiene_no_cambia_orden_ni_aciertos():
    lru = ListaLRU(3)
    for k in ('a', 'b'):
        lru.insertar(k, _ficha(k))
    orden, metricas = _ids_en_orden(lru), lru.contadores()
    assert lru.contiene('a') and not lru.contiene('z')
    assert _ids_en_orden(lru) == orden and lru.contadores() == metricas


# -- misma política que la búsqueda lineal (comparación justa, B02) ---------

def _secuencia(lru, semilla, pasos=2000, claves=40):
    rnd = random.Random(semilla)
    resultados = []
    for _ in range(pasos):
        clave = f'tipo_{rnd.randrange(claves)}'
        op = rnd.random()
        if op < 0.55:
            resultados.append(lru.buscar(clave) is not None)
        elif op < 0.85:
            try:
                resultados.append(lru.insertar(clave, _ficha(clave)))
            except ValueError:               # no se sustituye una ficha en uso
                resultados.append('i-')
        elif op < 0.93:
            try:
                lru.marcar_en_uso(clave)
                resultados.append('m')
            except KeyError:
                resultados.append('m-')
        else:
            try:
                lru.desmarcar_en_uso(clave)
                resultados.append('d')
            except (KeyError, ValueError):
                resultados.append('d-')
    return resultados


@pytest.mark.parametrize('semilla', [1, 7, 42])
def test_hash_y_lineal_dan_exactamente_lo_mismo(semilla):
    con_hash, lineal = ListaLRU(25), ListaLRU(25, indice='lineal')
    assert _secuencia(con_hash, semilla) == _secuencia(lineal, semilla)
    assert _ids_en_orden(con_hash) == _ids_en_orden(lineal)
    assert con_hash.contadores() == lineal.contadores()
    a, b = con_hash.contadores_operaciones(), lineal.contadores_operaciones()
    sin_comparaciones = lambda pares: [p for p in pares if p[0] != 'comparaciones']
    assert sin_comparaciones(a) == sin_comparaciones(b)
    con_hash._verificar_invariantes()
    lineal._verificar_invariantes()


def test_colisiones_forzadas_dentro_de_la_lru():
    lru = ListaLRU(10)
    lru._indice = TablaHash(10, funcion_hash=lambda c: 0)
    referencia = ListaLRU(10, indice='lineal')
    assert _secuencia(lru, 3, pasos=800, claves=20) == _secuencia(referencia, 3, pasos=800, claves=20)
    assert _ids_en_orden(lru) == _ids_en_orden(referencia)
    assert lru._indice.cadena_maxima() == len(lru)
    lru._verificar_invariantes()


def test_invariantes_tras_muchas_operaciones():
    lru = ListaLRU(25)
    rnd = random.Random(2026)
    for bloque in range(20):
        _secuencia(lru, rnd.randrange(10 ** 6), pasos=50, claves=60)
        lru._verificar_invariantes()


def test_invariantes_detectan_indice_desincronizado():
    lru = ListaLRU(3)
    lru.insertar('a', _ficha('a'))
    lru._indice.eliminar('a')
    with pytest.raises(AssertionError):
        lru._verificar_invariantes()


# -- métricas del índice ----------------------------------------------------

def test_estadisticas_del_indice():
    lru = ListaLRU(25)
    for k in range(10):
        lru.insertar(k, _ficha(k))
    lru.buscar(3)
    pares = lru.estadisticas_indice()
    nombres = [n for n, _ in pares]
    assert nombres == ['indice_modo', 'indice_cubetas', 'indice_factor_carga',
                       'indice_colisiones', 'indice_cadena_maxima',
                       'indice_redimensionamientos', 'indice_comparaciones_por_busqueda',
                       'indice_protegidas_saltadas']
    datos = list(pares)
    assert datos[0] == ('indice_modo', 'hash') and datos[1] == ('indice_cubetas', 64)
    assert ListaLRU(2, indice='lineal').estadisticas_indice()[0] == ('indice_modo', 'lineal')


# -- guardado ---------------------------------------------------------------

def _guardar(lru):
    referencia, registros = codificar(lru)
    return json.dumps({'ref': referencia, 'registros': registros})


def _cargar(texto):
    datos = json.loads(texto)
    return decodificar(datos['ref'], datos['registros'])


def test_guardar_y_cargar_conserva_indice_orden_y_protecciones():
    lru = ListaLRU(5)
    for k in ('ent_a', 'ent_b', 'ent_c'):
        lru.insertar(k, _ficha(k))
    lru.marcar_en_uso('ent_a')
    cargada = _cargar(_guardar(lru))
    assert type(cargada._indice) is TablaHash
    assert _ids_en_orden(cargada) == _ids_en_orden(lru)
    cargada._verificar_invariantes()
    assert cargada._nodo('ent_a').valor.en_uso == 1
    assert cargada.buscar('ent_b') == {'id': 'ent_b'}


def test_guardado_se_carga_en_otro_proceso_con_otra_semilla(tmp_path):
    """Las posiciones de la tabla se guardan; deben valer en otro proceso."""
    lru = ListaLRU(25)
    ids = [f'ent_{i}' for i in range(20)]
    for k in ids:
        lru.insertar(k, _ficha(k))
    ruta = tmp_path / 'lru.json'
    ruta.write_text(_guardar(lru), encoding='utf-8')
    codigo = (
        'import json,sys\n'
        'from persistencia.estado_partida import decodificar\n'
        'd=json.load(open(sys.argv[1],encoding="utf-8"))\n'
        'lru=decodificar(d["ref"],d["registros"])\n'
        'lru._verificar_invariantes()\n'
        'ids=sys.argv[2].split(",")\n'
        'print(all(lru._indice._buscar_sin_contar(k) is not None for k in ids))\n'
    )
    for semilla in ('11', '99'):
        entorno = dict(os.environ, PYTHONHASHSEED=semilla, PYTHONPATH=RAIZ)
        salida = subprocess.run([sys.executable, '-c', codigo, str(ruta), ','.join(ids)],
                                cwd=RAIZ, env=entorno, capture_output=True, text=True)
        assert salida.returncode == 0, salida.stderr
        assert salida.stdout.strip() == 'True'


def test_guardado_anterior_al_indice_se_reconstruye():
    """Un guardado de esquema 2 hecho antes de B01 no trae el índice."""
    lru = ListaLRU(4)
    for k in ('a', 'b', 'c'):
        lru.insertar(k, _ficha(k))
    lru.marcar_en_uso('b')
    for campo in ('_indice', '_modo_indice', 'contador_protegidas_saltadas'):
        delattr(lru, campo)
    texto = _guardar(lru)
    assert 'estructuras.tabla_hash' not in texto
    vieja = _cargar(texto)
    orden = _ids_en_orden(vieja)
    assert vieja.buscar('a') == {'id': 'a'}   # primera operación: reconstruye
    assert type(vieja._indice) is TablaHash and len(vieja._indice) == 3
    assert vieja._nodo('b').valor.en_uso == 1
    assert ('protegidas_saltadas', 0) in vieja.contadores_operaciones()
    assert sorted(_ids_en_orden(vieja)) == sorted(orden)
    vieja._verificar_invariantes()
