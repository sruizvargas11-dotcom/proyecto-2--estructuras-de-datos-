"""G14: llave de salida encerrada por la única puerta que ella misma abre."""

from bench.casos.resolubilidad import UbicacionLlave
from modelo.mundo.cripta_modelo import CriptaModelo
from modelo.mundo.sala import Sala
from modelo.mundo.salida import Salida


def _cripta_g14():
    cripta = CriptaModelo(
        "sintetica-g14", "v1", 17, 99, "llave-salida", 0, 0
    )
    inicial = Sala(17, "Inicial sintética")
    salida = Sala(99, "Salida sintética")
    inicial.salidas.insertar_al_final(
        Salida("N", 99, cerrada=True, llave="llave-salida")
    )
    cripta.agregar_sala(inicial)
    cripta.agregar_sala(salida)
    cripta.finalizar_carga()
    return cripta, (UbicacionLlave("llave-salida", 99),)


def test_g14_llave_salida_encerrada_por_su_propia_puerta():
    """G14 exige NO RESOLUBLE, frontera visible y ciclo llave→llave (FR-007, FR-011–FR-013)."""
    from modelo.verificador_resolubilidad import verificar_resolubilidad

    cripta, ubicaciones = _cripta_g14()
    resultado = verificar_resolubilidad(cripta, ubicaciones)

    assert resultado.veredicto == "NO RESOLUBLE"
    assert resultado.motivo == "a"
    assert [
        (puerta.origen, puerta.direccion, puerta.destino, puerta.llave)
        for puerta in resultado.frontera_bloqueada
    ] == [(17, "N", 99, "llave-salida")]
    assert len(resultado.ciclos) == 1
    assert resultado.ciclos[0].llaves == ("llave-salida", "llave-salida")
