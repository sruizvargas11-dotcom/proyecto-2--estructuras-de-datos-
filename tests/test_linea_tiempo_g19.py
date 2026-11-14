"""Prueba de aceptacion G19 para excluir acciones revertidas."""

from adaptadores.datos_offline import DatosOffline
from controlador.controlador_juego import ControladorJuego
from controlador.inicio_partida import nueva_partida
from tests.test_controlador_juego import VistaGuion, _dar_pergamino


class VistaConResumen(VistaGuion):
    def __init__(self, comandos):
        super().__init__(comandos)
        self.resumenes_historicos = []

    def mostrar_resumen_historico(self, resumen):
        self.resumenes_historicos.append(resumen)


def test_g19_reversion_corta_historia_vigente(tmp_path):
    """G19 verifica que la accion revertida ya no se consulte (FR-002, FR-008)."""
    sesion = nueva_partida(
        DatosOffline(),
        "cripta-01",
        str(tmp_path / "cache"),
        semilla=2026,
    )
    sala_inicial = sesion.partida.jugador.sala_actual.id
    rastros_antes = tuple(
        (sala.id, sala.tiempo_rastro)
        for sala in sesion.partida.cripta.recorrer_salas()
    )
    _dar_pergamino(sesion)
    vista = VistaConResumen(["W", "N", "P", "historia #2", "Q"])

    ControladorJuego(sesion, vista).jugar()

    assert sesion.partida.acciones_jugador == 1
    assert sesion.partida.tiempo == 100
    assert sesion.partida.jugador.sala_actual.id == sala_inicial
    assert tuple(
        (sala.id, sala.tiempo_rastro)
        for sala in sesion.partida.cripta.recorrer_salas()
    ) == rastros_antes
    assert vista.resumenes_historicos == []
    assert any(
        ("accion" in mensaje.lower() or "acción" in mensaje.lower()) and (
            "exist" in mensaje.lower() or "vigente" in mensaje.lower()
        )
        for _, mensaje in vista.mensajes
    )
