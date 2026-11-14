"""Pruebas de los constructores compartidos de linea de tiempo."""

from tests.fixtures.linea_tiempo import (
    crear_historia_determinista,
    crear_partida_determinista,
)


def test_partida_determinista_inicia_con_la_semilla_solicitada(tmp_path):
    """Verifica el estado inicial estable de la fixture (FR-001, SC-001)."""
    partida = crear_partida_determinista(2026, tmp_path / "cache")

    assert partida.semilla == 2026
    assert partida.tiempo == 0
    assert partida.estado == "en_curso"
    assert partida.reloj.proximo() is partida.jugador.evento_actual


def test_constructor_de_historia_repite_acciones_y_puntos_de_control():
    """Verifica registros y puntos de control reproducibles (FR-001, SC-001)."""
    primera = crear_historia_determinista(9, 3)
    segunda = crear_historia_determinista(9, 3)

    acciones_primera = tuple(
        (registro.numero, registro.tiempo, registro.datos)
        for registro in primera.acciones
    )
    acciones_segunda = tuple(
        (registro.numero, registro.tiempo, registro.datos)
        for registro in segunda.acciones
    )
    puntos_primera = tuple(
        (punto.tiempo, punto.numero_accion)
        for punto in primera.puntos_control
    )
    puntos_segunda = tuple(
        (punto.tiempo, punto.numero_accion)
        for punto in segunda.puntos_control
    )

    assert acciones_primera == acciones_segunda
    assert puntos_primera == puntos_segunda
    assert [registro.numero for registro in primera.acciones] == list(range(1, 10))
    assert [punto.numero_accion for punto in primera.puntos_control] == [0, 3, 6, 9]
