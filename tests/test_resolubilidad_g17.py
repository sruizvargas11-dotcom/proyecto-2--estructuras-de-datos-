"""G17: una cripta no resoluble no inicia sin --forzar."""

from types import SimpleNamespace

import pytest


def test_g17_bloquea_inicio_y_conserva_el_reporte():
    """G17 exige conservar el resultado que se debe mostrar al jugador (FR-015)."""
    from controlador.inicio_partida import (
        InicioBloqueado,
        asegurar_inicio_permitido,
    )

    resultado = SimpleNamespace(
        veredicto="NO RESOLUBLE",
        motivo="a",
        reporte="VEREDICTO: NO RESOLUBLE\nMOTIVO: (a) llave_salida inobtenible",
    )

    with pytest.raises(InicioBloqueado) as contexto:
        asegurar_inicio_permitido(resultado)

    assert contexto.value.resultado is resultado
