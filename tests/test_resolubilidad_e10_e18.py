"""Escenarios RS-E10–RS-E18 y RS-E24 de verificación de la cripta."""

import json
from types import SimpleNamespace

import pytest

from bench.casos.resolubilidad import UbicacionLlave
from modelo.mundo.cripta_modelo import CriptaModelo
from modelo.mundo.sala import Sala
from modelo.mundo.salida import Salida


def _crear_cripta(cripta_id, inicio, salida, llave_salida, ids_salas, puertas):
    cripta = CriptaModelo(
        cripta_id,
        "v1",
        inicio,
        salida,
        llave_salida,
        presupuesto_solicitudes=0,
        inventario_max=0,
    )
    salas = []
    for sala_id in ids_salas:
        sala = Sala(sala_id, f"Sala sintética {sala_id}")
        salas.append(sala)
        cripta.agregar_sala(sala)
    for origen, direccion, destino, cerrada, llave, costo in puertas:
        for sala in salas:
            if sala.id == origen:
                sala.salidas.insertar_al_final(
                    Salida(
                        direccion,
                        destino,
                        cerrada=cerrada,
                        llave=llave,
                        costo=costo,
                    )
                )
                break
    cripta.finalizar_carga()
    return cripta


def _ids_por_rondas(resultado):
    return tuple(
        tuple(ubicacion.id for ubicacion in ronda)
        for ronda in resultado.orden_por_rondas
    )


def _resultado_no_verificable():
    return SimpleNamespace(
        veredicto="NO VERIFICABLE",
        motivo="consulta de llaves no disponible",
        reporte="VEREDICTO: NO VERIFICABLE\nMOTIVO: consulta de llaves no disponible",
    )


def test_rs_e10_no_forzar_bloquea_inicio_no_verificable():
    """RS-E10: el fallo de consulta bloquea el inicio normal (FR-018)."""
    from controlador.inicio_partida import (
        InicioBloqueado,
        asegurar_inicio_permitido,
    )

    with pytest.raises(InicioBloqueado) as contexto:
        asegurar_inicio_permitido(_resultado_no_verificable())

    assert contexto.value.resultado.veredicto == "NO VERIFICABLE"


def test_rs_e10_forzar_permite_continuar_no_verificable():
    """RS-E10: --forzar permite continuar tras NO VERIFICABLE (FR-018)."""
    from controlador.inicio_partida import asegurar_inicio_permitido

    asegurar_inicio_permitido(_resultado_no_verificable(), forzar=True)


def test_rs_e11_lista_de_otra_version_se_rechaza(tmp_path):
    """RS-E11: la fuente no acepta ubicaciones persistidas de otra versión (FR-001)."""
    from adaptadores.datos_offline import DatosOffline

    carpeta_cripta = tmp_path / "cripta-sintetica"
    carpeta_cripta.mkdir()
    (carpeta_cripta / "version.json").write_text(
        json.dumps({"version": "v1"}), encoding="utf-8"
    )
    (carpeta_cripta / "llaves.json").write_text(
        json.dumps({"version": "v0", "llaves": []}), encoding="utf-8"
    )

    with pytest.raises(ValueError):
        DatosOffline(str(tmp_path)).llaves_cripta("cripta-sintetica")


def test_rs_e13_trampa_y_cierre_automatico_no_bloquean_cruce():
    """RS-E13: los efectos de trampa y cierre automático no cambian la alcanzabilidad (FR-005)."""
    from modelo.verificador_resolubilidad import verificar_resolubilidad

    cripta = _crear_cripta(
        "sintetica-rs-e13",
        10,
        99,
        "key-exit",
        (10, 20, 99),
        (
            (10, "A", 20, False, None, 1),
            (20, "Z", 99, True, "key-exit", 1),
        ),
    )
    cripta.sala_por_id(20).trampas.insertar_al_final(object())
    cripta.sala_por_id(10).salida_hacia("A").cierre_automatico = 1

    resultado = verificar_resolubilidad(
        cripta, (UbicacionLlave("key-exit", 20),)
    )

    assert resultado.veredicto == "RESOLUBLE"


def test_rs_e14_enemigo_no_errante_no_bloquea_obtener_la_llave():
    """RS-E14: todo enemigo puede ser derrotado en la verificación (FR-004, FR-016)."""
    from modelo.verificador_resolubilidad import verificar_resolubilidad

    cripta = _crear_cripta(
        "sintetica-rs-e14",
        10,
        99,
        "key-exit",
        (10, 20, 99),
        (
            (10, "A", 20, False, None, 1),
            (20, "Z", 99, True, "key-exit", 1),
        ),
    )

    resultado = verificar_resolubilidad(
        cripta,
        (UbicacionLlave("key-exit", 20, "enemy-no-errante"),),
    )

    assert resultado.veredicto == "RESOLUBLE"
    assert resultado.puerta_final.origen == 20


def test_rs_e15_sala_inicial_inexistente_es_error_de_datos():
    """RS-E15: una sala inicial ausente del esqueleto es error de datos (FR-019)."""
    from modelo.verificador_resolubilidad import verificar_resolubilidad

    cripta = _crear_cripta(
        "sintetica-rs-e15-inicio",
        10,
        99,
        "key-exit",
        (99,),
        (),
    )

    with pytest.raises(ValueError):
        verificar_resolubilidad(cripta, ())


def test_rs_e15_sala_salida_inexistente_es_error_de_datos():
    """RS-E15: una sala de salida ausente del esqueleto es error de datos (FR-019)."""
    from modelo.verificador_resolubilidad import verificar_resolubilidad

    cripta = _crear_cripta(
        "sintetica-rs-e15-salida",
        10,
        99,
        "key-exit",
        (10,),
        (),
    )

    with pytest.raises(ValueError):
        verificar_resolubilidad(cripta, ())


def test_rs_e16_llave_de_salida_en_inicio_aparece_en_ronda_cero():
    """RS-E16: una llave de salida en la sala inicial pertenece a la ronda 0 (FR-020)."""
    from modelo.verificador_resolubilidad import verificar_resolubilidad

    cripta = _crear_cripta(
        "sintetica-rs-e16-inicio",
        10,
        99,
        "key-exit",
        (10, 99),
        ((10, "Z", 99, True, "key-exit", 1),),
    )
    resultado = verificar_resolubilidad(
        cripta, (UbicacionLlave("key-exit", 10),)
    )

    assert _ids_por_rondas(resultado) == (("key-exit",),)


def test_rs_e16_inicio_igual_salida_aun_exige_puerta_con_llave():
    """RS-E16: la sala inicial igual a la salida no elimina la puerta final (FR-007, FR-020)."""
    from modelo.verificador_resolubilidad import verificar_resolubilidad

    cripta = _crear_cripta(
        "sintetica-rs-e16-misma-sala",
        10,
        10,
        "key-exit",
        (10,),
        ((10, "A", 10, True, "key-exit", 1),),
    )
    resultado = verificar_resolubilidad(
        cripta, (UbicacionLlave("key-exit", 10),)
    )

    assert resultado.veredicto == "RESOLUBLE"
    assert resultado.puerta_final.origen == 10
    assert resultado.puerta_final.direccion == "A"


def test_rs_e17_puerta_final_se_desempata_por_sala_y_direccion():
    """RS-E17: se elige sala de origen menor y luego dirección lexicográfica (FR-008, FR-021)."""
    from modelo.verificador_resolubilidad import verificar_resolubilidad

    cripta = _crear_cripta(
        "sintetica-rs-e17",
        10,
        99,
        "key-exit",
        (2, 10, 99),
        (
            (10, "A", 2, False, None, 1),
            (2, "Z", 99, True, "key-exit", 1),
            (2, "A", 99, True, "key-exit", 1),
            (10, "A", 99, True, "key-exit", 1),
        ),
    )
    resultado = verificar_resolubilidad(
        cripta, (UbicacionLlave("key-exit", 10),)
    )

    assert resultado.puerta_final.origen == 2
    assert resultado.puerta_final.direccion == "A"


def test_rs_e18_alcanzable_se_elige_ubicacion_minima_y_sin_enemigo():
    """RS-E18: cualquier ubicación alcanzable obtiene la llave con desempate estable (FR-016)."""
    from modelo.verificador_resolubilidad import verificar_resolubilidad

    cripta = _crear_cripta(
        "sintetica-rs-e18-alcanzable",
        10,
        99,
        "key-exit",
        (10, 20, 50, 99),
        (
            (10, "A", 20, False, None, 1),
            (10, "B", 50, False, None, 1),
            (20, "Z", 99, True, "key-exit", 1),
        ),
    )
    ubicaciones = (
        UbicacionLlave("key-exit", 50, "enemy-z"),
        UbicacionLlave("key-exit", 20, "enemy-z"),
        UbicacionLlave("key-exit", 20, "enemy-a"),
        UbicacionLlave("key-exit", 20),
    )

    resultado = verificar_resolubilidad(cripta, ubicaciones)
    llave = resultado.orden_por_rondas[0][0]

    assert (llave.id, llave.sala, llave.enemigo) == ("key-exit", 20, None)


def test_rs_e18_inobtenible_conserva_todas_las_ubicaciones():
    """RS-E18: la llave solo es inobtenible si todas sus ubicaciones quedan fuera (FR-016, FR-022)."""
    from modelo.verificador_resolubilidad import verificar_resolubilidad

    cripta = _crear_cripta(
        "sintetica-rs-e18-inobtenible",
        10,
        99,
        "key-a",
        (10, 20, 30, 99),
        (
            (10, "A", 20, True, "missing-a", 1),
            (10, "B", 30, True, "missing-b", 1),
            (30, "Z", 99, True, "key-a", 1),
        ),
    )
    ubicaciones = (
        UbicacionLlave("key-a", 20, "enemy-z"),
        UbicacionLlave("key-a", 20),
        UbicacionLlave("key-a", 30),
    )

    resultado = verificar_resolubilidad(cripta, ubicaciones)
    llave = resultado.llaves_inobtenibles[0]

    assert llave.id == "key-a"
    assert tuple(
        (ubicacion.sala, ubicacion.enemigo)
        for ubicacion in llave.ubicaciones
    ) == (
        (20, None),
        (20, "enemy-z"),
        (30, None),
    )


def test_rs_e24_sala_inexistente_es_error_datos_y_enemigo_no_se_valida():
    """RS-E24: se valida la sala de ubicación, pero no la existencia del enemigo (FR-016, FR-019)."""
    from modelo.verificador_resolubilidad import verificar_resolubilidad

    cripta = _crear_cripta(
        "sintetica-rs-e24",
        10,
        99,
        "key-exit",
        (10, 99),
        ((10, "Z", 99, True, "key-exit", 1),),
    )
    ubicacion_enemigo_desconocido = UbicacionLlave(
        "key-exit", 10, "enemy-no-registrado"
    )

    resultado = verificar_resolubilidad(
        cripta, (ubicacion_enemigo_desconocido,)
    )
    assert resultado.veredicto == "RESOLUBLE"

    with pytest.raises(ValueError):
        verificar_resolubilidad(
            cripta, (UbicacionLlave("key-exit", 700, "enemy-no-registrado"),)
        )
