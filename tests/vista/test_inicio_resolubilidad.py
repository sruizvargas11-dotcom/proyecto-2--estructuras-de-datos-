"""Resumen seguro de resolubilidad en los flujos de inicio Pygame (FR-015, FR-024)."""

from types import SimpleNamespace

import pygame
import pytest

from controlador.controlador_pygame import (
    ControladorPygame,
    InicioPygameBloqueado,
)
from controlador.inicio_partida import InicioBloqueado
from vista.formato_resolubilidad import formatear_resumen
from vista_pygame.escenas.menu_criptas import EscenaMenuCriptas
from vista_pygame.stubs_temporales import (
    CargadorAssetsTemporal,
    GestorAudioTemporal,
)


class _ControladorFalso:
    def __init__(self, resultado):
        self.resultado = resultado

    def iniciar_partida(self, *args, **kwargs):
        raise InicioPygameBloqueado(
            self.resultado,
            formatear_resumen(self.resultado).strip(),
        )


class _ContextoFalso:
    def __init__(self, resultado):
        self.controlador = _ControladorFalso(resultado)
        self.assets = CargadorAssetsTemporal()
        self.audio = GestorAudioTemporal()
        self.cambios_escena = []

    def cambiar_escena(self, id_escena, datos=None):
        self.cambios_escena.append((id_escena, datos))


def test_controlador_publica_solo_el_resumen_seguro(monkeypatch, tmp_path):
    controlador = ControladorPygame(
        None,
        carpeta_cache=str(tmp_path / "cache"),
        partidas_dir=str(tmp_path / "partidas"),
    )
    resultado = SimpleNamespace(
        veredicto="NO RESOLUBLE",
        motivo="a",
        llave_secreta="key-private",
    )

    def bloquear(*args, **kwargs):
        raise InicioBloqueado(resultado)

    monkeypatch.setattr("controlador.controlador_pygame.nueva_partida", bloquear)

    with pytest.raises(InicioPygameBloqueado) as contexto:
        controlador.iniciar_partida("cripta-sintetica", "Ada", semilla=1)

    resumen = "VEREDICTO: NO RESOLUBLE | MOTIVO: (a) llave_salida inobtenible"
    assert contexto.value.resultado is resultado
    assert str(contexto.value) == resumen
    assert controlador.resumen_resolubilidad() == resumen
    assert controlador.mensajes() == [f"[t=0] {resumen}"]
    assert "key-private" not in controlador.mensajes()[0]


def test_menu_muestra_el_bloqueo_sin_revelar_ubicaciones():
    resultado = SimpleNamespace(
        veredicto="NO RESOLUBLE",
        motivo="a",
        ubicaciones=("key-private", 700),
    )
    contexto = _ContextoFalso(resultado)
    escena = EscenaMenuCriptas(contexto)
    escena._cargando = False
    escena._criptas = [
        {"id": "cripta-sintetica", "nombre": "Cripta", "salas": 2, "dificultad": 1}
    ]
    escena._nombre = "Ada"
    escena._foco = 0

    escena._confirmar(1)

    esperado = "VEREDICTO: NO RESOLUBLE | MOTIVO: (a) llave_salida inobtenible"
    assert escena._aviso_inicio == esperado
    assert "key-private" not in escena._aviso_inicio
    assert "700" not in escena._aviso_inicio
    escena._dibujar_mensaje_inicio(pygame.Surface((1280, 720)), escena._aviso_inicio)
    assert contexto.cambios_escena == []


def test_resumen_no_verificable_tambien_es_seguro():
    resultado = SimpleNamespace(
        veredicto="NO VERIFICABLE",
        motivo="consulta de llaves no disponible",
        ubicaciones=("key-private", 700),
    )
    resumen = formatear_resumen(resultado)

    assert resumen == (
        "VEREDICTO: NO VERIFICABLE | "
        "MOTIVO: consulta de llaves no disponible\n"
    )
    assert "key-private" not in resumen
    assert "700" not in resumen
