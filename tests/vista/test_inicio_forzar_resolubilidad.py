"""Propagación de --forzar en GUI (FR-015, FR-018; RS-E32, RS-E35)."""

from types import SimpleNamespace

import pytest

import main


def test_cli_gui_pasa_forzar_a_la_aplicacion(monkeypatch, tmp_path):
    import vista_pygame.app as app

    llamadas = []
    monkeypatch.setattr(app, "ejecutar", lambda *args, **kwargs: llamadas.append(kwargs))
    opciones = SimpleNamespace(
        cache_dir=str(tmp_path / "cache"),
        cache_size=25,
        partidas_dir=str(tmp_path / "partidas"),
        reportes=str(tmp_path / "reportes"),
        forzar=True,
    )

    assert main.jugar_gui(None, opciones) == 0
    assert llamadas[0]["forzar"] is True


def test_contexto_pasa_forzar_al_inicio_en_hilo():
    from vista_pygame.app import Contexto

    class ControladorFalso:
        forzar_inicio = True

        def iniciar_partida(self, *args, **kwargs):
            self.llamada = (args, kwargs)

    controlador = ControladorFalso()
    contexto = Contexto(controlador, None, None, None)

    contexto.arrancar_partida(("cripta-sintetica", "Ada", None))
    contexto._hilo_inicio.join(timeout=2)

    assert not contexto._hilo_inicio.is_alive()
    assert controlador.llamada[1]["forzar"] is True


def test_menu_propaga_forzar_al_inicio_directo():
    from vista_pygame.escenas.menu_criptas import EscenaMenuCriptas
    from vista_pygame.stubs_temporales import (
        CargadorAssetsTemporal,
        GestorAudioTemporal,
    )

    class ControladorFalso:
        forzar_inicio = True

        def __init__(self):
            self.llamada = None

        def iniciar_partida(self, *args, **kwargs):
            self.llamada = (args, kwargs)

    class ContextoFalso:
        def __init__(self):
            self.controlador = ControladorFalso()
            self.assets = CargadorAssetsTemporal()
            self.audio = GestorAudioTemporal()

        def cambiar_escena(self, *args):
            pass

    contexto = ContextoFalso()
    escena = EscenaMenuCriptas(contexto)
    escena._cargando = False
    escena._criptas = [
        {"id": "cripta-sintetica", "nombre": "Cripta", "salas": 2, "dificultad": 1}
    ]
    escena._nombre = "Ada"
    escena._foco = 0

    escena._confirmar(1)

    assert contexto.controlador.llamada[1]["forzar"] is True


@pytest.mark.parametrize(
    ("veredicto", "motivo", "esperado"),
    [
        (
            "NO RESOLUBLE",
            "a",
            "VEREDICTO: NO RESOLUBLE | MOTIVO: (a) llave_salida inobtenible",
        ),
        (
            "NO VERIFICABLE",
            "consulta de llaves no disponible",
            "VEREDICTO: NO VERIFICABLE | MOTIVO: consulta de llaves no disponible",
        ),
    ],
)
def test_gui_bloquea_y_publica_resumen_seguro(
    monkeypatch, tmp_path, veredicto, motivo, esperado
):
    import controlador.controlador_pygame as controlador_pygame
    from controlador.inicio_partida import InicioBloqueado

    controlador = controlador_pygame.ControladorPygame(
        None, carpeta_cache=str(tmp_path / "cache")
    )
    resultado = SimpleNamespace(
        veredicto=veredicto,
        motivo=motivo,
        ubicaciones=("ubicacion-secreta",),
    )

    def bloqueada(*args, **kwargs):
        raise InicioBloqueado(resultado)

    monkeypatch.setattr(controlador_pygame, "nueva_partida", bloqueada)

    with pytest.raises(controlador_pygame.InicioPygameBloqueado) as contexto:
        controlador.iniciar_partida("cripta-sintetica", "Ada", semilla=1)

    assert str(contexto.value) == esperado
    assert "ubicacion-secreta" not in str(contexto.value)


def test_error_de_datos_no_se_fuerza_en_gui(monkeypatch, tmp_path):
    import controlador.controlador_pygame as controlador_pygame

    controlador = controlador_pygame.ControladorPygame(
        None, carpeta_cache=str(tmp_path / "cache"), forzar=True
    )
    llamadas = []

    def error_datos(*args, **kwargs):
        llamadas.append(kwargs)
        raise ValueError("Datos de cripta inválidos.")

    monkeypatch.setattr(controlador_pygame, "nueva_partida", error_datos)

    with pytest.raises(ValueError, match="Datos de cripta inválidos"):
        controlador.iniciar_partida("cripta-sintetica", "Ada", semilla=1)

    assert llamadas[0]["forzar"] is True
