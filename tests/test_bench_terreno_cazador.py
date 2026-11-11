import json

from bench.terreno_cazador import (
    _correr_escenario,
    _fixture,
    _grafo,
    _puertas,
    _estado,
    _alternar_puerta,
    _debe_alternar_puerta,
    _registrar_observacion,
)
from modelo.entidades.enemigo import Enemigo
from modelo.mundo.sala import Sala


def test_fixture_distribuye_diez_cazadores_por_rango():
    datos, _ = _fixture()
    _, rangos = _estado(datos, [1, 100])
    assert rangos[:10] == [1] * 10
    assert rangos[10:] == [100] * 10


def test_puertas_alternan_sus_dos_sentidos():
    datos, _ = _fixture()
    vecinos = _grafo(datos)
    puertas = _puertas(datos, vecinos)
    assert len(puertas) == 8
    assert all(len(extremos) == 2 for extremos in puertas)
    cerradas = []
    _alternar_puerta(cerradas, puertas[0])
    assert len(cerradas) == 2
    assert all(extremo in cerradas for extremo in puertas[0])
    _alternar_puerta(cerradas, puertas[0])
    assert not cerradas


def test_referencia_se_compara_fuera_del_calculo_compartido():
    datos, _ = _fixture()
    vecinos = _grafo(datos)
    puertas = _puertas(datos, vecinos)
    duraciones, discrepancias = _correr_escenario(
        datos, vecinos, puertas, [1, 100], 100, "compartida"
    )
    assert len(duraciones) == 1000
    assert not discrepancias


def test_cambios_cada_cien_no_alternan_en_el_ciclo_inicial():
    assert not _debe_alternar_puerta(1, 100)
    assert _debe_alternar_puerta(100, 100)
    assert _debe_alternar_puerta(200, 100)


def test_espera_registra_sala_actual_tras_dos_movimientos():
    salas = [Sala(1, "uno"), Sala(2, "dos"), Sala(3, "tres")]
    cazador = Enemigo(
        "cazador-regresion", "bench-cazador", "Cazador", 100, 1, 0, 100,
        "cazador", salas[0], rango=1
    )
    posiciones = [salas[0].id]
    cazador.sala_actual = salas[1]
    cazador.sala_actual = salas[2]

    observacion = _registrar_observacion(
        cazador, "esperar", posiciones, 0
    )

    assert observacion == ("cazador-regresion", ("esperar", 3))
    assert posiciones == [3]
