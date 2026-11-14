"""Pruebas de los registros y metadatos del modelo de historia."""

import pytest

from estructuras.vector_dinamico import Vector
from modelo.historia import Historia


@pytest.mark.parametrize("k", [0, -1, True, 1.5, "2"])
def test_historia_rechaza_intervalo_no_positivo_o_no_entero(k):
    """Verifica la validacion del intervalo de puntos de control (FR-014)."""
    with pytest.raises(ValueError):
        Historia(k)


def test_historia_numera_acciones_desde_uno_y_guarda_arrays_propios():
    """Verifica registros vigentes y arreglos propios de acciones/puntos (FR-002, FR-009)."""
    historia = Historia(3)

    primera = historia.registrar_accion(0, ("esperar",))
    segunda = historia.registrar_accion(10, ("mover", "norte"))

    assert isinstance(historia.acciones, Vector)
    assert isinstance(historia.puntos_control, Vector)
    assert primera.numero == 1
    assert segunda.numero == 2
    assert [punto.numero_accion for punto in historia.puntos_control] == [0]


def test_historia_valida_y_agrega_metadatos_ordenados():
    """Verifica metadatos de puntos de control ordenados por tiempo/accion (FR-009)."""
    historia = Historia(2)
    historia.registrar_accion(10, ("esperar",))
    historia.registrar_accion(20, ("mover",))
    punto = historia.registrar_punto_control(20, 2)

    assert punto.tiempo == 20
    assert punto.numero_accion == 2
    assert historia.puntos_control.obtenerValor(1) is punto
    with pytest.raises(ValueError):
        historia.registrar_punto_control(15, 1)
