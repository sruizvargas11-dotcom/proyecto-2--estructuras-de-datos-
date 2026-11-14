"""G17: una cripta no resoluble no inicia sin --forzar."""

from types import SimpleNamespace

import pytest


def _cripta_resoluble():
    from modelo.mundo.cripta_modelo import CriptaModelo
    from modelo.mundo.sala import Sala
    from modelo.mundo.salida import Salida

    cripta = CriptaModelo("sintetica-inicio", "v1", 10, 99, "key-exit", 0, 0)
    inicial = Sala(10, "Inicial")
    salida = Sala(99, "Salida")
    inicial.salidas.insertar_al_final(
        Salida("N", 99, cerrada=True, llave="key-exit")
    )
    cripta.agregar_sala(inicial)
    cripta.agregar_sala(salida)
    cripta.finalizar_carga()
    return cripta


def test_g17_bloquea_inicio_y_conserva_el_reporte():
    """G17 exige conservar el resultado que se debe mostrar al jugador (FR-015)."""
    from controlador.inicio_partida import (
        InicioBloqueado,
        asegurar_inicio_permitido,
    )

    resultado = SimpleNamespace(
        veredicto="NO RESOLUBLE",
        motivo="a",
        reporte="VEREDICTO: NO RESOLUBLE\nMOTIVO: (a) llave_salida inobtenible",
    )

    with pytest.raises(InicioBloqueado) as contexto:
        asegurar_inicio_permitido(resultado)

    assert contexto.value.resultado is resultado


def test_nueva_partida_verifica_una_vez_y_conserva_el_resultado(monkeypatch, tmp_path):
    from estructuras.vector_dinamico import Vector

    import controlador.inicio_partida as inicio
    from modelo.verificador_resolubilidad import verificar_resolubilidad

    cripta = _cripta_resoluble()
    generales = {
        "jugador": {
            "vida_max": 100,
            "ataque": 10,
            "defensa": 5,
            "velocidad": 1,
        }
    }
    fuente = SimpleNamespace(llaves_cripta=lambda cripta_id: None)
    monkeypatch.setattr(inicio, "_generales", lambda fuente, cripta_id: generales)
    monkeypatch.setattr(
        inicio, "cargar_cripta", lambda fuente, cripta_id, cache: (cripta, False)
    )
    monkeypatch.setattr(
        inicio,
        "obtener_llaves",
        lambda fuente, cache, cripta_id, version: {
            "llaves": [{"id": "key-exit", "sala": 10}]
        },
    )

    llamadas = []

    def verificar_una_vez(modelo, llaves):
        llamadas.append((modelo, llaves))
        return verificar_resolubilidad(modelo, llaves)

    monkeypatch.setattr(inicio, "verificar_resolubilidad", verificar_una_vez)

    red = SimpleNamespace(
        planificar_precarga=lambda sala: None,
        garantizar_contenido=lambda sala_id: None,
        version_catalogo=lambda: "catalog-v1",
        notificar_muerte_enemigo=lambda enemigo: None,
    )
    monkeypatch.setattr(inicio, "ControladorRed", lambda *args, **kwargs: red)
    monkeypatch.setattr(
        inicio,
        "Jugador",
        SimpleNamespace(
            desde_generales=lambda generales, sala: SimpleNamespace()
        ),
    )
    monkeypatch.setattr(
        inicio,
        "Partida",
        lambda *args, **kwargs: SimpleNamespace(
            al_morir_enemigo=Vector(),
            inicializar=lambda: None,
        ),
    )

    sesion = inicio.nueva_partida(
        fuente,
        "sintetica-inicio",
        str(tmp_path),
        semilla=1,
    )

    assert len(llamadas) == 1
    assert sesion.resultado_resolubilidad.veredicto == "RESOLUBLE"


def test_forzar_no_permite_iniciar_con_ubicacion_de_llave_invalida(
    monkeypatch, tmp_path
):
    import controlador.inicio_partida as inicio

    cripta = _cripta_resoluble()
    generales = {
        "jugador": {
            "vida_max": 100,
            "ataque": 10,
            "defensa": 5,
            "velocidad": 1,
        }
    }
    fuente = SimpleNamespace(llaves_cripta=lambda cripta_id: None)
    monkeypatch.setattr(inicio, "_generales", lambda fuente, cripta_id: generales)
    monkeypatch.setattr(
        inicio, "cargar_cripta", lambda fuente, cripta_id, cache: (cripta, False)
    )
    monkeypatch.setattr(
        inicio,
        "obtener_llaves",
        lambda fuente, cache, cripta_id, version: {
            "llaves": [{"id": "key-exit", "sala": 700}]
        },
    )

    with pytest.raises(ValueError, match="no existe"):
        inicio.nueva_partida(
            fuente,
            "sintetica-inicio",
            str(tmp_path),
            semilla=1,
            forzar=True,
        )


def test_llaves_offline_ausentes_producen_no_verificable_y_bloquean(
    monkeypatch, tmp_path
):
    import controlador.inicio_partida as inicio

    cripta = _cripta_resoluble()
    generales = {
        "jugador": {
            "vida_max": 100,
            "ataque": 10,
            "defensa": 5,
            "velocidad": 1,
        }
    }
    fuente = SimpleNamespace(llaves_cripta=lambda cripta_id: None)
    monkeypatch.setattr(inicio, "_generales", lambda fuente, cripta_id: generales)
    monkeypatch.setattr(
        inicio, "cargar_cripta", lambda fuente, cripta_id, cache: (cripta, False)
    )

    def archivo_de_llaves_ausente(*args):
        raise FileNotFoundError("llaves.json no encontrado")

    monkeypatch.setattr(inicio, "obtener_llaves", archivo_de_llaves_ausente)

    with pytest.raises(inicio.InicioBloqueado) as contexto:
        inicio.nueva_partida(
            fuente,
            "sintetica-inicio",
            str(tmp_path),
            semilla=1,
        )

    assert contexto.value.resultado.veredicto == "NO VERIFICABLE"
    assert contexto.value.resultado.motivo == "consulta de llaves no disponible"
