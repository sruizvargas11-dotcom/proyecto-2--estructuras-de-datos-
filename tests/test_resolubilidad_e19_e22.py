"""Escenarios RS-E19–RS-E22 de orden, dependencias, rondas y crecimiento."""

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
    for origen, direccion, destino, cerrada, llave in puertas:
        for sala in salas:
            if sala.id == origen:
                sala.salidas.insertar_al_final(
                    Salida(direccion, destino, cerrada=cerrada, llave=llave)
                )
                break
    cripta.finalizar_carga()
    return cripta


def _ids_por_rondas(resultado):
    return tuple(
        tuple(ubicacion.id for ubicacion in ronda)
        for ronda in resultado.orden_por_rondas
    )


def test_rs_e19_orden_compara_salas_numericamente_e_ids_lexicograficamente():
    """RS-E19: salas usan orden numérico e ids de llave orden lexicográfico (FR-021)."""
    from modelo.verificador_resolubilidad import verificar_resolubilidad

    cripta = _crear_cripta(
        "sintetica-rs-e19-orden",
        1,
        99,
        "key-z",
        (1, 2, 10, 99),
        (
            (1, "A", 2, False, None),
            (1, "B", 10, False, None),
            (2, "Z", 99, True, "key-z"),
        ),
    )
    ubicaciones = (
        UbicacionLlave("key-z", 2),
        UbicacionLlave("key-a", 10),
        UbicacionLlave("key-2", 2),
        UbicacionLlave("key-10", 2),
    )

    resultado = verificar_resolubilidad(cripta, ubicaciones)

    assert _ids_por_rondas(resultado) == (
        ("key-10", "key-2", "key-z", "key-a"),
    )


def test_rs_e19_ubicaciones_ordena_sala_y_enemigo_deterministicamente():
    """RS-E19: ubicaciones inobtenibles usan sala numérica y enemigo lexicográfico (FR-016, FR-021)."""
    from modelo.verificador_resolubilidad import verificar_resolubilidad

    cripta = _crear_cripta(
        "sintetica-rs-e19-ubicaciones",
        10,
        99,
        "key-a",
        (2, 10, 20, 30, 99),
        (
            (10, "A", 2, True, "missing-a"),
            (10, "B", 20, True, "missing-b"),
            (10, "C", 30, True, "missing-c"),
            (20, "Z", 99, True, "key-a"),
        ),
    )
    ubicaciones = (
        UbicacionLlave("key-a", 20, "enemy-z"),
        UbicacionLlave("key-a", 2, "enemy-z"),
        UbicacionLlave("key-a", 2, "enemy-b"),
        UbicacionLlave("key-a", 2),
    )

    resultado = verificar_resolubilidad(cripta, ubicaciones)
    llave = resultado.llaves_inobtenibles[0]

    assert tuple(
        (ubicacion.sala, ubicacion.enemigo)
        for ubicacion in llave.ubicaciones
    ) == (
        (2, None),
        (2, "enemy-b"),
        (2, "enemy-z"),
        (20, "enemy-z"),
    )


def test_rs_e20_ronda_final_se_incluye_completa_y_el_orden_se_corta():
    """RS-E20: la ronda donde abre la puerta final se incluye completa (FR-009)."""
    from modelo.verificador_resolubilidad import verificar_resolubilidad

    cripta = _crear_cripta(
        "sintetica-rs-e20",
        10,
        99,
        "key-exit",
        (10, 20, 30, 40, 99),
        (
            (10, "A", 20, True, "key-root"),
            (20, "A", 30, False, None),
            (20, "B", 99, True, "key-exit"),
            (30, "C", 40, True, "key-a"),
        ),
    )
    ubicaciones = (
        UbicacionLlave("key-root", 10),
        UbicacionLlave("key-exit", 20),
        UbicacionLlave("key-a", 30),
        UbicacionLlave("key-late", 40),
    )

    resultado = verificar_resolubilidad(cripta, ubicaciones)

    assert _ids_por_rondas(resultado) == (
        ("key-root",),
        ("key-exit", "key-a"),
    )


def test_rs_e21_dependencias_evalua_todas_las_ubicaciones():
    """RS-E21: las ubicaciones alternativas se incluyen en la indispensabilidad (FR-022)."""
    from modelo.verificador_resolubilidad import verificar_resolubilidad

    cripta = _crear_cripta(
        "sintetica-rs-e21-dependencias",
        10,
        99,
        "key-a",
        (10, 20, 30, 40, 99),
        (
            (10, "A", 20, True, "key-b"),
            (10, "B", 30, True, "key-b"),
            (10, "C", 40, True, "missing"),
            (20, "Z", 99, True, "key-a"),
        ),
    )
    ubicaciones = (
        UbicacionLlave("key-a", 20),
        UbicacionLlave("key-a", 30),
        UbicacionLlave("key-b", 40),
    )

    resultado = verificar_resolubilidad(cripta, ubicaciones)

    assert tuple(
        (llave.id, llave.causa)
        for llave in resultado.llaves_inobtenibles
    ) == (
        ("key-a", "depende de key-b"),
        ("key-b", "sala inalcanzable aun con todas las llaves"),
    )


def test_rs_e21_ciclo_considera_todas_las_ubicaciones_de_la_llave():
    """RS-E21: todas las ubicaciones contribuyen a la relación cíclica (FR-011, FR-022)."""
    from modelo.verificador_resolubilidad import verificar_resolubilidad

    cripta = _crear_cripta(
        "sintetica-rs-e21-ciclo",
        10,
        99,
        "key-a",
        (10, 20, 30, 40, 99),
        (
            (10, "A", 20, True, "key-b"),
            (10, "B", 30, True, "key-b"),
            (10, "C", 40, True, "key-a"),
            (40, "Z", 99, True, "key-a"),
        ),
    )
    ubicaciones = (
        UbicacionLlave("key-a", 20),
        UbicacionLlave("key-a", 30),
        UbicacionLlave("key-b", 40),
    )

    resultado = verificar_resolubilidad(cripta, ubicaciones)

    assert tuple(
        (llave.id, llave.causa)
        for llave in resultado.llaves_inobtenibles
    ) == (
        ("key-a", "en ciclo"),
        ("key-b", "en ciclo"),
    )
    assert tuple(
        ciclo.llaves for ciclo in resultado.ciclos
    ) == (
        ("key-a", "key-b", "key-a"),
        ("key-a", "key-b", "key-a"),
    )


def test_rs_e22_generador_entrega_tamanos_deterministas_para_bench():
    """RS-E22: tamaños deterministas permiten medir tres duplicaciones (SC-004)."""
    cantidades = (4, 8, 16)
    tamanos = []
    for cantidad in cantidades:
        sintetica = generar_cripta_sintetica(
            semilla=22022,
            cantidad_llaves=cantidad,
            estructura="cadena",
        )
        cantidad_salidas = 0
        for sala in sintetica.cripta.recorrer_salas():
            for _ in sala.salidas:
                cantidad_salidas += 1
        tamanos.append(
            (len(sintetica.cripta), cantidad_salidas, len(sintetica.ubicaciones))
        )

    assert len(tamanos) == 3
    assert tamanos[0][2] * 2 == tamanos[1][2]
    assert tamanos[1][2] * 2 == tamanos[2][2]
