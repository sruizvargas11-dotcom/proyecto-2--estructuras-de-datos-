"""Escenarios RS-E01–RS-E09 para verificación e inicio de la cripta."""

from types import SimpleNamespace

from bench.casos.resolubilidad import UbicacionLlave, generar_cripta_sintetica
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


def test_rs_e01_forzar_permite_iniciar_cripta_no_resoluble():
    """RS-E01: el forzado permite iniciar y conserva el reporte (FR-015, FR-018)."""
    from controlador.inicio_partida import asegurar_inicio_permitido

    resultado = SimpleNamespace(
        veredicto="NO RESOLUBLE",
        motivo="a",
        reporte="VEREDICTO: NO RESOLUBLE\nMOTIVO: (a) llave_salida inobtenible",
    )

    asegurar_inicio_permitido(resultado, forzar=True)


def test_rs_e02_ruta_alternativa_no_reporta_ciclo():
    """RS-E02: una ruta alternativa elimina la dependencia aparente (FR-012)."""
    from modelo.verificador_resolubilidad import verificar_resolubilidad

    sintetica = generar_cripta_sintetica(
        semilla=202602, cantidad_llaves=2, estructura="alternativa"
    )
    resultado = verificar_resolubilidad(
        sintetica.cripta, sintetica.ubicaciones
    )

    assert resultado.veredicto == "RESOLUBLE"
    assert resultado.ciclos == ()


def test_rs_e03_dependencias_enumera_todas_las_llaves_indispensables():
    """RS-E03: cada causa enumera sus dependencias directas (FR-011, FR-022)."""
    from modelo.verificador_resolubilidad import verificar_resolubilidad

    cripta = _crear_cripta(
        "sintetica-rs-e03-dependencias",
        10,
        99,
        "key-c",
        (10, 20, 30, 40, 99),
        (
            (10, "A", 20, True, "key-b", 1),
            (10, "B", 30, True, "key-c", 1),
            (30, "A", 40, True, "missing", 1),
            (40, "Z", 99, True, "key-c", 1),
        ),
    )
    ubicaciones = (
        UbicacionLlave("key-a", 20),
        UbicacionLlave("key-b", 30),
        UbicacionLlave("key-c", 40),
    )

    resultado = verificar_resolubilidad(cripta, ubicaciones)

    assert resultado.veredicto == "NO RESOLUBLE"
    assert tuple(
        (llave.id, llave.causa)
        for llave in resultado.llaves_inobtenibles
    ) == (
        ("key-a", "depende de key-b"),
        ("key-b", "depende de key-c"),
        ("key-c", "sala inalcanzable aun con todas las llaves"),
    )


def test_rs_e03_ciclo_asigna_causa_en_ciclo_solo_a_participantes():
    """RS-E03: las dependientes no cíclicas conservan «depende de» (FR-011)."""
    from modelo.verificador_resolubilidad import verificar_resolubilidad

    cripta = _crear_cripta(
        "sintetica-rs-e03-ciclo",
        10,
        99,
        "key-a",
        (10, 20, 30, 40, 99),
        (
            (10, "A", 20, True, "key-b", 1),
            (10, "B", 30, True, "key-c", 1),
            (10, "C", 40, True, "key-b", 1),
            (20, "Z", 99, True, "key-a", 1),
        ),
    )
    ubicaciones = (
        UbicacionLlave("key-a", 20),
        UbicacionLlave("key-b", 30),
        UbicacionLlave("key-c", 40),
    )

    resultado = verificar_resolubilidad(cripta, ubicaciones)

    assert tuple(
        (llave.id, llave.causa)
        for llave in resultado.llaves_inobtenibles
    ) == (
        ("key-a", "depende de key-b"),
        ("key-b", "en ciclo"),
        ("key-c", "en ciclo"),
    )
    assert tuple(
        ciclo.llaves for ciclo in resultado.ciclos
    ) == (
        ("key-b", "key-c", "key-b"),
        ("key-b", "key-c", "key-b"),
    )


def test_rs_e04_las_llaves_de_la_region_abierta_quedan_en_la_ronda_siguiente():
    """RS-E04: una llave abre la región y descubre varias llaves en la ronda siguiente (FR-009, FR-010)."""
    from modelo.verificador_resolubilidad import verificar_resolubilidad

    cripta = _crear_cripta(
        "sintetica-rs-e04",
        10,
        99,
        "key-exit",
        (10, 20, 30, 40, 50, 99),
        (
            (10, "A", 20, True, "key-root", 1),
            (20, "A", 30, False, None, 1),
            (20, "B", 40, False, None, 1),
            (40, "Z", 99, True, "key-exit", 1),
        ),
    )
    ubicaciones = (
        UbicacionLlave("key-root", 10),
        UbicacionLlave("key-a", 30),
        UbicacionLlave("key-exit", 40),
    )

    resultado = verificar_resolubilidad(cripta, ubicaciones)

    assert _ids_por_rondas(resultado) == (
        ("key-root",),
        ("key-a", "key-exit"),
    )


def test_rs_e05_salida_alcanzable_sin_puerta_con_llave_de_salida():
    """RS-E05: alcanzar la salida por puerta abierta no satisface la condición final (FR-007, FR-011)."""
    from modelo.verificador_resolubilidad import verificar_resolubilidad

    cripta = _crear_cripta(
        "sintetica-rs-e05",
        10,
        99,
        "key-exit",
        (10, 20, 99),
        (
            (10, "A", 20, False, None, 1),
            (20, "A", 99, False, None, 1),
        ),
    )

    resultado = verificar_resolubilidad(
        cripta, (UbicacionLlave("key-exit", 10),)
    )

    assert resultado.veredicto == "NO RESOLUBLE"
    assert resultado.motivo == "b"


def test_rs_e06_frontera_muestra_llave_inexistente_para_ids_ausentes_y_nulos():
    """RS-E06: una puerta cerrada sin llave disponible nunca abre (FR-013)."""
    from modelo.verificador_resolubilidad import verificar_resolubilidad

    cripta = _crear_cripta(
        "sintetica-rs-e06",
        10,
        99,
        "key-exit",
        (10, 20, 30, 99),
        (
            (10, "A", 20, True, "missing", 1),
            (10, "B", 30, True, None, 1),
        ),
    )

    resultado = verificar_resolubilidad(
        cripta, (UbicacionLlave("key-exit", 99),)
    )

    assert tuple(
        (puerta.direccion, puerta.llave)
        for puerta in resultado.frontera_bloqueada
    ) == (
        ("A", "inexistente"),
        ("B", "inexistente"),
    )


def test_rs_e07_cambiar_costos_no_cambia_veredicto_ni_orden():
    """RS-E07: el costo no afecta la alcanzabilidad ni el orden (FR-006)."""
    from modelo.verificador_resolubilidad import verificar_resolubilidad

    primero = generar_cripta_sintetica(
        semilla=202607, cantidad_llaves=4, estructura="cadena"
    )
    segundo = generar_cripta_sintetica(
        semilla=202607, cantidad_llaves=4, estructura="cadena"
    )
    for sala in segundo.cripta.recorrer_salas():
        for salida in sala.salidas:
            salida.costo += 100000

    resultado_a = verificar_resolubilidad(
        primero.cripta, primero.ubicaciones
    )
    resultado_b = verificar_resolubilidad(
        segundo.cripta, segundo.ubicaciones
    )

    assert resultado_a.veredicto == resultado_b.veredicto
    assert _ids_por_rondas(resultado_a) == _ids_por_rondas(resultado_b)


def test_rs_e08_salida_dirigida_no_alcanza_su_origen():
    """RS-E08: no se infiere el arco inverso (FR-002)."""
    from modelo.verificador_resolubilidad import verificar_resolubilidad

    cripta = _crear_cripta(
        "sintetica-rs-e08",
        20,
        99,
        "key-exit",
        (10, 20, 99),
        (
            (10, "A", 20, False, None, 1),
            (10, "Z", 99, True, "key-exit", 1),
        ),
    )

    resultado = verificar_resolubilidad(
        cripta, (UbicacionLlave("key-exit", 10),)
    )

    assert resultado.veredicto == "NO RESOLUBLE"
    assert resultado.motivo == "a"
    assert _ids_por_rondas(resultado) == ((),)


def test_rs_e09_la_misma_llave_abre_varias_puertas_sin_consumirse():
    """RS-E09: una llave puede abrir más de una salida cerrada (FR-003)."""
    from modelo.verificador_resolubilidad import verificar_resolubilidad

    cripta = _crear_cripta(
        "sintetica-rs-e09",
        10,
        99,
        "key-exit",
        (10, 20, 99),
        (
            (10, "A", 20, True, "key-exit", 1),
            (20, "B", 99, True, "key-exit", 1),
        ),
    )

    resultado = verificar_resolubilidad(
        cripta, (UbicacionLlave("key-exit", 10),)
    )

    assert resultado.veredicto == "RESOLUBLE"
    assert resultado.puerta_final.origen == 20
    assert resultado.puerta_final.direccion == "B"
