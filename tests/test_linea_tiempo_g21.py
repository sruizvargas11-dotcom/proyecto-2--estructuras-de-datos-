"""Prueba de aceptacion G21 para consultas historicas sin mutaciones."""

from adaptadores.datos_offline import DatosOffline
from controlador.controlador_juego import ControladorJuego
from controlador.inicio_partida import nueva_partida
from tests.test_controlador_juego import VistaGuion, _dar_pergamino


def _firma_partida(partida, sesion, pergamino):
    agenda = partida.reloj.agenda
    return (
        partida.tiempo,
        partida.estado,
        partida.jugador.vida,
        partida.jugador.sala_actual.id,
        partida.acciones_jugador,
        partida.reloj.azar.getstate(),
        tuple(
            (entrada.tiempo, entrada.secuencia, entrada.dato.tipo, entrada.valido)
            for entrada in agenda._datos
        ),
        len(partida.historial),
        partida.historial.contadores(),
        partida.jugador.buscar_nodo(pergamino.instancia_id) is not None,
        len(sesion.acciones),
    )


class VistaConFirma(VistaGuion):
    def __init__(self, comandos, sesion, pergamino):
        super().__init__(comandos)
        self.sesion = sesion
        self.pergamino = pergamino
        self.antes_consulta = None
        self.resumenes_historicos = []

    def leer_comando(self):
        comando = super().leer_comando()
        if comando.lower().startswith("historia "):
            self.antes_consulta = _firma_partida(
                self.sesion.partida,
                self.sesion,
                self.pergamino,
            )
        return comando

    def mostrar_resumen_historico(self, resumen):
        self.resumenes_historicos.append(resumen)


def test_g21_consulta_no_altera_partida_ni_pergamino(tmp_path):
    """G21 compara estado, reloj, acciones y pergamino antes y despues (FR-006, FR-007)."""
    sesion = nueva_partida(
        DatosOffline(),
        "cripta-01",
        str(tmp_path / "cache"),
        semilla=2026,
    )
    pergamino = _dar_pergamino(sesion)
    vista = VistaConFirma(["W", "historia 0", "Q"], sesion, pergamino)

    ControladorJuego(sesion, vista).jugar()

    despues = _firma_partida(sesion.partida, sesion, pergamino)
    assert vista.antes_consulta == despues
    assert len(vista.resumenes_historicos) == 1
