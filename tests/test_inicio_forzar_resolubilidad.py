"""Inicio de consola con --forzar (FR-015, FR-018; SC-005, RS-E01, RS-E10)."""

from types import SimpleNamespace

import pytest

import main
from vista.formato_resolubilidad import formatear_resumen


@pytest.mark.parametrize(
    ("veredicto", "motivo"),
    [
        ("NO RESOLUBLE", "a"),
        ("NO VERIFICABLE", "consulta de llaves no disponible"),
    ],
)
def test_consola_pasa_forzar_y_muestra_resumen(
    monkeypatch, tmp_path, veredicto, motivo
):
    import controlador.controlador_juego as controlador_juego
    import controlador.inicio_partida as inicio_partida
    import persistencia.puntajes as puntajes
    import vista.vista_consola as vista_consola

    resultado = SimpleNamespace(veredicto=veredicto, motivo=motivo)
    sesion = SimpleNamespace(
        resultado_resolubilidad=resultado,
        partida=SimpleNamespace(
            estado="en_curso",
            cripta_id="cripta-sintetica",
            version_cripta="v1",
        ),
    )
    llamadas = []

    def crear_partida(*args, **kwargs):
        llamadas.append(kwargs)
        return sesion

    class VistaFalsa:
        def pedir_nombre_jugador(self):
            return "Ada"

        def mostrar_inicio(self, *args):
            pass

        def mostrar_error_puntaje(self, *args):
            pass

        def mostrar_tabla_puntajes(self, *args):
            pass

    class ControladorFalso:
        def __init__(self, sesion, *args):
            self.sesion = sesion
            self.partida = sesion.partida
            self.error_puntaje = None
            self.tabla_puntajes = ()
            self.bitacora = None

        def jugar(self):
            pass

    salidas = []
    monkeypatch.setattr(inicio_partida, "nueva_partida", crear_partida)
    monkeypatch.setattr(vista_consola, "VistaConsola", VistaFalsa)
    monkeypatch.setattr(controlador_juego, "ControladorJuego", ControladorFalso)
    monkeypatch.setattr(puntajes, "TablaPuntajes", lambda ruta: ())
    monkeypatch.setattr(main, "informar", salidas.append)
    monkeypatch.setattr(main, "_mostrar_reporte", lambda *args, **kwargs: None)
    opciones = SimpleNamespace(
        cache_dir=str(tmp_path / "cache"),
        partidas_dir=str(tmp_path / "partidas"),
        cache_size=25,
        hilos=False,
        forzar=True,
        reportes=str(tmp_path / "reportes"),
    )

    main.jugar(None, "cripta-sintetica", opciones)

    assert llamadas[0]["forzar"] is True
    assert formatear_resumen(resultado).rstrip("\n") in salidas
