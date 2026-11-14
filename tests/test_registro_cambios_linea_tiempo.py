"""Pruebas del registro permanente e invertible de cambios."""

from types import SimpleNamespace

from modelo.deltas import DeltaAtributos
from modelo.historia import Historia


def test_cambios_permanentes_se_invierten_y_se_truncan_por_accion():
    """Verifica que los cambios son independientes del pergamino y reversibles (FR-008, FR-009, FR-010)."""
    historia = Historia(2)
    estado = SimpleNamespace(valor=0)

    historia.registrar_accion(10, ("accion", 1))
    cambio_primero = DeltaAtributos(estado, "valor")
    estado.valor = 1
    historia.registrar_cambio(1, cambio_primero)
    historia.registrar_punto_control(10, 1)

    historia.registrar_accion(20, ("accion", 2))
    cambio_segundo = DeltaAtributos(estado, "valor")
    estado.valor = 2
    historia.registrar_cambio(2, cambio_segundo)

    historia.truncar(1)

    assert estado.valor == 1
    assert [registro.numero for registro in historia.acciones] == [1]
    assert [registro.numero_accion for registro in historia.cambios] == [1]
    assert [punto.numero_accion for punto in historia.puntos_control] == [0, 1]
