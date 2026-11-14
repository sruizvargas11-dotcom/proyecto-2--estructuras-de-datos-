"""Escenarios RS-E35–RS-E36 para datos inválidos y frontera."""

from modelo.mundo.cripta_modelo import CriptaModelo
from modelo.mundo.sala import Sala
from modelo.mundo.salida import Salida


def _crear_cripta(cripta_id, inicio, salida, llave_salida, ids_salas, puertas):
    cripta = CriptaModelo(
        cripta_id,
        "v1",
        inicio,
        salida,
        llave_salida,
        presupuesto_solicitudes=0,
        inventario_max=0,
    )
    salas = []
    for sala_id in ids_salas:
        sala = Sala(sala_id, f"Sala sintética {sala_id}")
        salas.append(sala)
        cripta.agregar_sala(sala)
    for origen, direccion, destino, llave in puertas:
        for sala in salas:
            if sala.id == origen:
                sala.salidas.insertar_al_final(
                    Salida(direccion, destino, cerrada=True, llave=llave)
                )
                break
    cripta.finalizar_carga()
    return cripta


def test_rs_e35_llave_salida_ausente_o_nula_es_error_no_forzable():
    """RS-E35: falta o nulidad de llave_salida constituye error de datos (FR-019)."""
    import pytest

    from modelo.verificador_resolubilidad import verificar_resolubilidad

    nula = _crear_cripta(
        "sintetica-rs-e35-nula",
        10,
        99,
        None,
        (10, 99),
        (),
    )
    with pytest.raises(ValueError):
        verificar_resolubilidad(nula, ())

    ausente = _crear_cripta(
        "sintetica-rs-e35-ausente",
        10,
        99,
        "key-exit",
        (10, 99),
        (),
    )
    del ausente.llave_salida
    with pytest.raises(ValueError):
        verificar_resolubilidad(ausente, ())


def test_rs_e36_frontera_se_ordena_por_sala_numerica_y_direccion():
    """RS-E36: la frontera usa orden numérico de sala y lexicográfico de dirección (FR-013, FR-021)."""
    from modelo.verificador_resolubilidad import verificar_resolubilidad

    cripta = _crear_cripta(
        "sintetica-rs-e36",
        10,
        99,
        "key-exit",
        (2, 10, 20, 30, 40, 50, 99),
        (
            (10, "A", 2, "missing-open"),
            (2, "Z", 20, "missing-z"),
            (10, "Z", 30, "missing-z"),
            (2, "A", 40, "missing-a"),
            (10, "B", 50, "missing-b"),
        ),
    )
    # La salida abierta hace alcanzable la sala 2; las puertas de frontera siguen cerradas.
    cripta.sala_por_id(10).salida_hacia("A").cerrada = False

    resultado = verificar_resolubilidad(cripta, ())

    assert tuple(
        (puerta.origen, puerta.direccion, puerta.destino)
        for puerta in resultado.frontera_bloqueada
    ) == (
        (2, "A", 40),
        (2, "Z", 20),
        (10, "B", 50),
        (10, "Z", 30),
    )
