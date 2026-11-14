"""Pruebas de reconstruccion en estado temporal aislado."""

from modelo.historia import Historia
from modelo.punto_control import PuntoControl
from modelo.reconstructor_historia import ReconstructorHistoria
from tests.fixtures.linea_tiempo import crear_partida_determinista


def test_reconstructor_aplica_acciones_solo_a_la_copia_temporal(tmp_path):
    """Verifica reconstruccion aislada sin modificar la partida real (FR-006, FR-010)."""
    partida = crear_partida_determinista(carpeta_cache=tmp_path / "cache")
    vida_real = partida.jugador.vida
    punto = PuntoControl.capturar(partida)
    historia = Historia(3)
    historia.registrar_accion(10, ("danar", 2))
    historia.registrar_accion(20, ("danar", 3))

    def aplicar(temporal, accion):
        temporal.jugador.vida -= accion.datos[1]

    temporal = ReconstructorHistoria.reconstruir(
        punto,
        historia.acciones,
        hasta_accion=2,
        aplicar_accion=aplicar,
    )

    assert temporal.jugador.vida == vida_real - 5
    assert partida.jugador.vida == vida_real


def test_reconstructor_sin_acciones_devuelve_instancia_aislada(tmp_path):
    """Verifica que la reconstruccion vacia tampoco comparte el estado real (FR-006)."""
    partida = crear_partida_determinista(carpeta_cache=tmp_path / "cache")
    punto = PuntoControl.capturar(partida)

    temporal = ReconstructorHistoria.reconstruir(punto)

    assert temporal is not partida
    assert temporal.jugador is not partida.jugador
