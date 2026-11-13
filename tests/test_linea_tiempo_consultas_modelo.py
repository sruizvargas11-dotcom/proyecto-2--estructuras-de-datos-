"""Pruebas unitarias de seleccion de puntos de control."""

import pytest

from modelo.historia import Historia


def _historia_con_puntos():
    historia = Historia(3)
    for numero in range(1, 7):
        historia.registrar_accion(numero * 10, ("esperar", numero))
    historia.registrar_punto_control(30, 3)
    historia.registrar_punto_control(60, 6)
    return historia


def test_busqueda_temporal_incluye_punto_con_tiempo_igual():
    """Verifica que se elija el ultimo punto con tiempo <= t (FR-001)."""
    historia = _historia_con_puntos()

    punto = historia.buscar_punto_control_tiempo(30, tiempo_actual=60)

    assert punto.tiempo == 30
    assert punto.numero_accion == 3


def test_busqueda_temporal_entre_puntos_elige_el_anterior():
    """Verifica la busqueda de predecesor cuando t cae entre controles (FR-001)."""
    historia = _historia_con_puntos()

    punto = historia.buscar_punto_control_tiempo(45, tiempo_actual=60)

    assert punto.tiempo == 30
    assert punto.numero_accion == 3


def test_busqueda_temporal_rechaza_tiempo_anterior_al_inicio():
    """Verifica que no se acepte consultar antes del punto inicial (FR-003)."""
    historia = _historia_con_puntos()

    with pytest.raises(ValueError):
        historia.buscar_punto_control_tiempo(-1, tiempo_actual=60)


def test_busqueda_temporal_rechaza_tiempo_futuro():
    """Verifica el rechazo de consultas posteriores al reloj actual (FR-005)."""
    historia = _historia_con_puntos()

    with pytest.raises(ValueError):
        historia.buscar_punto_control_tiempo(61, tiempo_actual=60)


def test_accion_en_multiplo_de_k_usa_checkpoint_previo():
    """Verifica (k - 1) // K para k=K y k=2K (FR-002, FR-003)."""
    historia = _historia_con_puntos()

    punto_k = historia.buscar_punto_control_accion(3)
    punto_2k = historia.buscar_punto_control_accion(6)

    assert punto_k.numero_accion == ((3 - 1) // historia.k) * historia.k == 0
    assert punto_2k.numero_accion == ((6 - 1) // historia.k) * historia.k == 3
