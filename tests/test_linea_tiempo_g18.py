"""Prueba de aceptación G18 para rechazar consultas futuras."""

from tests.test_controlador_juego import _juego


def _firma(partida, sesion):
    agenda = partida.reloj.agenda
    return (
        partida.tiempo,
        partida.estado,
        partida.jugador.vida,
        partida.jugador.sala_actual.id,
        partida.acciones_jugador,
        partida.reloj.azar.getstate(),
        agenda.siguiente_secuencia,
        tuple(
            (entrada.tiempo, entrada.secuencia, entrada.dato.tipo, entrada.valido)
            for entrada in agenda._datos
        ),
        len(partida.historial),
        len(sesion.acciones),
    )


def test_g18_rechaza_futuro_sin_mutar(tmp_path):
    """G18 comprueba que un tiempo futuro se rechaza sin modificar el juego (FR-005, FR-006)."""
    controlador, vista, sesion, _ = _juego(
        tmp_path, ["historia 1", "Q"], bitacora=False
    )
    antes = _firma(sesion.partida, sesion)

    controlador.jugar()

    assert any("tiempo transcurrido" in mensaje.lower()
               for _, mensaje in vista.mensajes)
    assert _firma(sesion.partida, sesion) == antes
