"""Prueba de aceptacion SC-005: persistencia de historia y mapa conocido (FR-012)."""

from adaptadores.datos_offline import DatosOffline
from controlador.controlador_juego import ControladorJuego
from controlador.guardado import cargar
from controlador.inicio_partida import nueva_partida
from tests.test_controlador_juego import VistaGuion


class VistaConResumen(VistaGuion):
    def __init__(self, comandos):
        super().__init__(comandos)
        self.resumenes_historicos = []

    def mostrar_resumen_historico(self, resumen):
        self.resumenes_historicos.append(resumen)


def _firma_resumen(resumen):
    return (
        resumen.tiempo,
        resumen.sala_id,
        resumen.sala_nombre,
        resumen.vida,
        resumen.vida_max,
        resumen.ataque,
        resumen.defensa,
        resumen.velocidad,
        tuple(
            (objeto.instancia_id, objeto.nombre, objeto.clase)
            for objeto in resumen.inventario
        ),
        tuple(
            (
                efecto.tipo,
                efecto.dano_por_pulso,
                efecto.pulsos_restantes,
                efecto.parametro,
                efecto.tiempo_fin,
                efecto.instancia_id,
            )
            for efecto in resumen.efectos_activos
        ),
        tuple(
            (enemigo.instancia_id, enemigo.nombre, enemigo.vida, enemigo.vida_max)
            for enemigo in resumen.enemigos
        ),
        tuple(
            (sala.sala_id, sala.nombre, sala.tiempo_rastro)
            for sala in resumen.mapa_conocido
        ),
    )


def test_guardado_carga_conserva_historia_y_mapa(tmp_path):
    """Compara consultas temporales y por accion antes/despues de cargar (FR-012, SC-005)."""
    fuente = DatosOffline()
    sesion = nueva_partida(
        fuente,
        "cripta-01",
        str(tmp_path / "cache-original"),
        semilla=2026,
    )
    ruta = tmp_path / "linea-tiempo.sav"
    consultas = ["historia 0", "historia 100", "historia #1", "historia #2"]
    vista_antes = VistaConResumen(["W", "W"] + consultas + [f"G {ruta}", "Q"])
    ControladorJuego(sesion, vista_antes).jugar()

    sesion_receptora = nueva_partida(
        fuente,
        "cripta-01",
        str(tmp_path / "cache-receptora"),
        semilla=2026,
    )
    restaurada = cargar(str(ruta), sesion_receptora)
    vista_despues = VistaConResumen(consultas + ["Q"])
    ControladorJuego(restaurada, vista_despues).jugar()

    assert tuple(sesion.acciones) == tuple(restaurada.acciones)
    assert sesion.partida.acciones_jugador == restaurada.partida.acciones_jugador == 2
    assert len(vista_antes.resumenes_historicos) == len(consultas)
    assert len(vista_despues.resumenes_historicos) == len(consultas)
    for antes, despues in zip(
        vista_antes.resumenes_historicos, vista_despues.resumenes_historicos
    ):
        assert _firma_resumen(antes) == _firma_resumen(despues)

