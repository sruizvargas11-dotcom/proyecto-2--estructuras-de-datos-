"""Pruebas del generador sintético y del oráculo de recorrido repetido."""

from bench.casos.resolubilidad import (
    generar_cripta_sintetica,
    recorrido_completo_repetido,
)


def _firma(cripta_sintetica):
    salas = []
    for sala in cripta_sintetica.cripta.recorrer_salas():
        salidas = []
        for salida in sala.salidas:
            salidas.append((
                salida.direccion,
                salida.sala_destino_id,
                salida.cerrada,
                salida.llave,
                salida.costo,
            ))
        salas.append((sala.id, tuple(salidas)))
    llaves = tuple(
        (llave.id, llave.sala, llave.enemigo)
        for llave in cripta_sintetica.ubicaciones
    )
    return tuple(salas), llaves


def test_generador_repite_topologia_y_costos_para_la_misma_semilla():
    """La entrada de prueba no incorpora criptas publicadas (FR-017, SC-002)."""
    primera = generar_cripta_sintetica(semilla=37, cantidad_llaves=5)
    segunda = generar_cripta_sintetica(semilla=37, cantidad_llaves=5)

    assert _firma(primera) == _firma(segunda)
    ids_salas = [sala[0] for sala in _firma(primera)[0]]
    assert all(
        ids_salas[indice + 1] - ids_salas[indice] > 1
        for indice in range(len(ids_salas) - 1)
    )


def test_oraculo_resuelve_cadena_y_conserva_las_rondas():
    """El oráculo usa recorridos completos y mantiene el orden de ronda (FR-009, FR-017)."""
    sintetica = generar_cripta_sintetica(
        semilla=11, cantidad_llaves=4, estructura="cadena"
    )

    resultado = recorrido_completo_repetido(
        sintetica.cripta, sintetica.ubicaciones
    )

    assert resultado.veredicto == "RESOLUBLE"
    assert [
        [llave.id for llave in ronda]
        for ronda in resultado.orden_por_rondas
    ] == [[f"llave-{indice:04d}"] for indice in range(4)]
    assert resultado.puerta_final.llave == sintetica.cripta.llave_salida
    assert len(resultado.salas_alcanzables) == 6
    assert resultado.recorridos_completos > 4


def test_oraculo_detecta_ciclo_sin_ruta_inicial():
    """Una cadena de puertas mutuamente cerradas no libera ninguna llave (FR-011, FR-012)."""
    sintetica = generar_cripta_sintetica(
        semilla=19, cantidad_llaves=2, estructura="ciclo"
    )

    resultado = recorrido_completo_repetido(
        sintetica.cripta, sintetica.ubicaciones
    )

    assert resultado.veredicto == "NO RESOLUBLE"
    assert resultado.orden_por_rondas == ((),)
    assert [
        (puerta.origen, puerta.direccion, puerta.llave)
        for puerta in resultado.frontera
    ] == [
        (sintetica.cripta.sala_inicial_id, "A", "llave-0001"),
        (sintetica.cripta.sala_inicial_id, "B", "llave-0000"),
    ]


def test_oraculo_resuelve_ciclo_aparente_por_ruta_alternativa():
    """La ruta abierta a A evita que la dependencia aparente bloquee la cadena (FR-012)."""
    sintetica = generar_cripta_sintetica(
        semilla=23, cantidad_llaves=2, estructura="alternativa"
    )

    resultado = recorrido_completo_repetido(
        sintetica.cripta, sintetica.ubicaciones
    )

    assert resultado.veredicto == "RESOLUBLE"
    assert [
        [llave.id for llave in ronda]
        for ronda in resultado.orden_por_rondas
    ] == [["llave-0000"], ["llave-0001"]]
    assert resultado.puerta_final.llave == "llave-0001"
