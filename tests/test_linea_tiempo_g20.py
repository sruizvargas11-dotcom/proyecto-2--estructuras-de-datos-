"""Prueba de aceptación G20 para eventos simultáneos."""

from adaptadores.datos_offline import DatosOffline
from controlador.controlador_juego import ControladorJuego
from controlador.inicio_partida import nueva_partida
from modelo.efectos import aplicar_veneno
from modelo.entidades.enemigo import Enemigo
from modelo.ejecutor_evento import EjecutorEvento
from modelo.partida import Partida
from tests.test_controlador_juego import VistaGuion


class VistaConResumen(VistaGuion):
    def __init__(self, comandos):
        super().__init__(comandos)
        self.resumenes_historicos = []
        self.vidas_decision = []

    def mostrar_estado(self, partida):
        super().mostrar_estado(partida)
        self.vidas_decision.append(partida.jugador.vida)

    def mostrar_resumen_historico(self, resumen):
        self.resumenes_historicos.append(resumen)


def test_g20_incluye_eventos_del_instante_antes_de_decidir(tmp_path, monkeypatch):
    """G20 comprueba que ambos eventos de t se reflejan antes de la decisión (FR-001, FR-004)."""
    inicializar_partida = Partida.__init__

    def inicializar_con_eventos(partida, cripta, jugador, *args, **kwargs):
        inicializar_partida(partida, cripta, jugador, *args, **kwargs)
        jugador.vida = jugador.vida_max - 1
        aplicar_veneno(partida.reloj, jugador, 3, pulsos=1, intervalo=100)
        sala = jugador.sala_actual
        enemigo = Enemigo(
            "e-g20", "tipo-g20", "Regenerador", 10, 0, 0, 100,
            "guardián", sala, vida=7,
        )
        enemigo.regeneracion = 2
        sala.enemigos_activos.insertar_al_final(enemigo)
        partida.reloj.vincular_actor(enemigo)
        partida.reloj.programar_en(
            100,
            EjecutorEvento("regeneracion", enemigo),
            tipo="regeneracion",
            dueno=enemigo,
            campo="evento_regeneracion",
        )

    monkeypatch.setattr(Partida, "__init__", inicializar_con_eventos)
    sesion = nueva_partida(
        DatosOffline(),
        "cripta-01",
        str(tmp_path / "cache"),
        semilla=2026,
    )

    vista = VistaConResumen(["W", "W", "historia 100", "Q"])
    controlador = ControladorJuego(sesion, vista)
    controlador.jugar()

    assert len(vista.resumenes_historicos) == 1
    resumen = vista.resumenes_historicos[0]
    assert resumen.tiempo == 100
    assert resumen.vida == sesion.partida.jugador.vida_max - 4
    assert resumen.vida == vista.vidas_decision[1]
    eventos = [
        mensaje
        for tiempo, mensaje in vista.mensajes
        if tiempo == 100
        and ("El veneno te quema" in mensaje or "Regenerador se regenera" in mensaje)
    ]
    assert len(eventos) == 2
    assert eventos[0].startswith("El veneno te quema")
    assert eventos[1].startswith("Regenerador se regenera")
