"""Contrato y seleccion de K para las mediciones de linea de tiempo."""

from bench.casos import linea_tiempo
from bench.medicion import Fila


def test_parametros_de_medicion_cubren_sc001_y_sc002():
    assert linea_tiempo.ACCIONES_BENCH >= 5000
    assert linea_tiempo.CONSULTAS_POR_TIPO * 2 >= 30
    assert linea_tiempo.REPETICIONES_BENCH >= 30
    assert len(linea_tiempo.K_EVALUADOS) >= 3
    assert 10 in linea_tiempo.K_EVALUADOS
    assert 50 in linea_tiempo.K_EVALUADOS
    assert 100 in linea_tiempo.K_EVALUADOS
    assert any(k > 100 for k in linea_tiempo.K_EVALUADOS)
    assert linea_tiempo.UMBRAL_P95_MS == 50.0


def test_propuesta_es_el_mayor_k_con_p95_estrictamente_menor_a_50_ms():
    filas = (
        Fila("linea-tiempo", "consulta_K=10", 5000, 0, ms_p95=25.0),
        Fila("linea-tiempo", "consulta_K=50", 5000, 0, ms_p95=49.9),
        Fila("linea-tiempo", "consulta_K=100", 5000, 0, ms_p95=50.0),
        Fila("linea-tiempo", "consulta_K=200", 5000, 0, ms_p95=71.0),
        Fila("otra-caso", "consulta_K=500", 5000, 0, ms_p95=1.0),
    )
    assert linea_tiempo.proponer_k(filas) == 50

    filas_sin_cumplimiento = (
        Fila("linea-tiempo", "consulta_K=10", 5000, 0, ms_p95=50.0),
    )
    assert linea_tiempo.proponer_k(filas_sin_cumplimiento) is None
