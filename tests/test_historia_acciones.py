"""Pruebas de consultas por numero de accion vigente."""

from adaptadores.datos_offline import DatosOffline
from controlador.controlador_juego import ControladorJuego
from controlador.inicio_partida import nueva_partida
from modelo.historia import Historia
from tests.test_controlador_juego import VistaGuion


class VistaConResumen(VistaGuion):
    def __init__(self, comandos):
        super().__init__(comandos)
        self.resumenes_historicos = []
        self.vidas_decision = []
        self.tiempos_decision_registrados = []

    def mostrar_estado(self, partida):
        super().mostrar_estado(partida)
        self.vidas_decision.append(partida.jugador.vida)
        self.tiempos_decision_registrados.append(partida.tiempo)

    def mostrar_resumen_historico(self, resumen):
        self.resumenes_historicos.append(resumen)


def test_historia_k_en_multiplos_de_K_es_previa_a_la_accion(tmp_path):
    """Verifica que #K y #2K resumen el estado previo a esas acciones (FR-002, FR-003)."""
    k = 2
    sesion = nueva_partida(
        DatosOffline(),
        "cripta-01",
        str(tmp_path / "cache"),
        semilla=2026,
    )
    historia = getattr(sesion.partida, "historia", None)
    if historia is None:
        historia = Historia(k)
        sesion.partida.historia = historia
    else:
        historia.k = k
    comandos = ["W"] * (2 * k) + [f"historia #{k}", f"historia #{2 * k}", "Q"]
    vista = VistaConResumen(comandos)

    ControladorJuego(sesion, vista).jugar()

    assert len(vista.resumenes_historicos) == 2
    for indice, numero_accion in enumerate((k, 2 * k)):
        resumen = vista.resumenes_historicos[indice]
        decision = numero_accion - 1
        assert resumen.tiempo == vista.tiempos_decision_registrados[decision]
        assert resumen.vida == vista.vidas_decision[decision]
