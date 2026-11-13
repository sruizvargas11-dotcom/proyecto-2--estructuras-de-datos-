"""Pruebas unitarias de límites de reconstrucción y compatibilidad."""

import pytest

from modelo.historia import Historia
from modelo.reconstructor_historia import ReconstructorHistoria
from persistencia.PartidaBinaria import ErrorFormatoBinario, MAGIC, PartidaBinaria


class PuntoControlPrueba:
    def __init__(self, numero_accion):
        self.numero_accion = numero_accion

    def restaurar(self):
        return []


def _crear_historia(cantidad, k):
    historia = Historia(k)
    for numero in range(1, cantidad + 1):
        historia.registrar_accion(numero * 10, ("esperar", numero))
        if numero % k == 0:
            historia.registrar_punto_control(numero * 10, numero)
    return historia


def test_reconstruccion_aplica_como_maximo_k_acciones():
    """Cuenta re-simulaciones en consultas por accion y antes del checkpoint (FR-010)."""
    k = 5
    historia = _crear_historia(3 * k + 2, k)

    for numero_accion in range(1, len(historia.acciones) + 1):
        punto = historia.buscar_punto_control_accion(numero_accion)
        aplicadas = []
        hasta_accion = numero_accion - 1

        ReconstructorHistoria.reconstruir(
            PuntoControlPrueba(punto.numero_accion),
            historia.acciones,
            hasta_accion=hasta_accion,
            aplicar_accion=lambda _, accion: aplicadas.append(accion.numero),
        )

        assert len(aplicadas) <= k
        assert aplicadas == list(
            range(punto.numero_accion + 1, hasta_accion + 1)
        )

    for numero_checkpoint in range(k, len(historia.acciones) + 1, k):
        punto = historia.buscar_punto_control_tiempo(
            numero_checkpoint * 10 - 1,
            tiempo_actual=len(historia.acciones) * 10,
        )
        aplicadas = []

        ReconstructorHistoria.reconstruir(
            PuntoControlPrueba(punto.numero_accion),
            historia.acciones,
            hasta_accion=numero_checkpoint - 1,
            aplicar_accion=lambda _, accion: aplicadas.append(accion.numero),
        )

        assert len(aplicadas) == k - 1
        assert len(aplicadas) <= k


def test_persistencia_rechaza_version_binaria_anterior_con_mensaje(tmp_path):
    """Verifica que persistencia no cargue silenciosamente un formato anterior (FR-013)."""
    ruta = tmp_path / "partida-version-anterior.sav"
    ruta.write_bytes(
        MAGIC.to_bytes(4, byteorder="big")
        + (0).to_bytes(2, byteorder="big")
        + (0).to_bytes(2, byteorder="big")
        + (16).to_bytes(4, byteorder="big")
    )

    with pytest.raises(ErrorFormatoBinario, match="no compatible"):
        PartidaBinaria(str(ruta)).cargar_global()
