"""Formato estable de reporte completo y resumen de resolubilidad (FR-024)."""

from modelo.verificador_resolubilidad import (
    CicloResolubilidad,
    LlaveInobtenible,
    PuertaBloqueada,
    PuertaFinal,
    ResultadoResolubilidad,
    UbicacionLlaveResultado,
)


def test_formato_reporte_resoluble_coincide_byte_a_byte_con_el_contrato():
    from vista.formato_resolubilidad import (
        formatear_reporte,
        formatear_resumen,
    )

    resultado = ResultadoResolubilidad(
        "RESOLUBLE",
        (
            (UbicacionLlaveResultado("key-a", 5),),
            (UbicacionLlaveResultado("key-exit", 17, "enemy-2"),),
        ),
        PuertaFinal(17, "N", 99, "key-exit"),
        None,
        (17, 99),
    )

    reporte_esperado = (
        "VEREDICTO: RESOLUBLE\n"
        "ORDEN_POR_RONDAS:\n"
        "  RONDA 0:\n"
        "    - id=key-a | sala=5 | enemigo=ninguno\n"
        "  RONDA 1:\n"
        "    - id=key-exit | sala=17 | enemigo=enemy-2\n"
        "PUERTA_FINAL: origen=17 | direccion=N | destino=99\n"
    )
    resumen_esperado = "VEREDICTO: RESOLUBLE\n"

    assert formatear_reporte(resultado).encode("utf-8") == reporte_esperado.encode("utf-8")
    assert formatear_resumen(resultado).encode("utf-8") == resumen_esperado.encode("utf-8")


def test_formato_reporte_no_resoluble_incluye_diagnosticos_en_orden():
    from vista.formato_resolubilidad import formatear_reporte

    resultado = ResultadoResolubilidad(
        "NO RESOLUBLE",
        (
            (UbicacionLlaveResultado("key-a", 5, "enemy-a"),),
            (),
        ),
        None,
        "a",
        (1, 5),
        (
            LlaveInobtenible(
                "key-z",
                (
                    UbicacionLlaveResultado("key-z", 12),
                    UbicacionLlaveResultado("key-z", 12, "enemy-a"),
                ),
                "depende de key-a, key-b",
                ("key-a", "key-b"),
            ),
        ),
        (
            PuertaBloqueada(1, "N", 12, "missing-key", ()),
        ),
        (
            CicloResolubilidad(
                ("key-a", "key-b", "key-a"),
                (
                    PuertaBloqueada(1, "E", 2, "key-b", ()),
                    PuertaBloqueada(2, "S", 1, "key-a", ()),
                ),
            ),
        ),
    )

    esperado = (
        "VEREDICTO: NO RESOLUBLE\n"
        "MOTIVO: (a) llave_salida inobtenible\n"
        "REGION: salas=2 | llaves_obtenidas=1\n"
        "LLAVES_INOBTENIBLES:\n"
        "  - id=key-z | ubicaciones=[sala:12; sala:12, enemigo:enemy-a] "
        "| causa=depende de key-a, key-b\n"
        "FRONTERA_BLOQUEADA:\n"
        "  - origen=1 | direccion=N | destino=12 | llave=inexistente\n"
        "CICLOS:\n"
        "  - llaves=key-a -> key-b -> key-a | puertas=[origen=1, direccion=E; "
        "origen=2, direccion=S]\n"
    )
    assert formatear_reporte(resultado).encode("utf-8") == esperado.encode("utf-8")


def test_resumen_no_resoluble_omite_ubicaciones_frontera_y_ciclos():
    from vista.formato_resolubilidad import formatear_resumen

    resultado = ResultadoResolubilidad(
        "NO RESOLUBLE",
        ((UbicacionLlaveResultado("key-secret", 123, "enemy-secret"),),),
        None,
        "b",
        (1, 123),
        (
            LlaveInobtenible(
                "key-secret",
                (UbicacionLlaveResultado("key-secret", 123, "enemy-secret"),),
                "en ciclo",
            ),
        ),
        (PuertaBloqueada(1, "N", 123, "key-secret", ()),),
        (
            CicloResolubilidad(
                ("key-secret", "key-secret"),
                (PuertaBloqueada(1, "N", 123, "key-secret", ()),),
            ),
        ),
    )

    resumen = formatear_resumen(resultado)
    assert resumen.encode("utf-8") == (
        "VEREDICTO: NO RESOLUBLE | MOTIVO: (b) llave_salida obtenida, "
        "pero no se alcanza ninguna puerta hacia sala_salida que la requiera\n"
    ).encode("utf-8")
    assert "key-secret" not in resumen
    assert "123" not in resumen
    assert "CICLOS" not in resumen
    assert "FRONTERA_BLOQUEADA" not in resumen


def test_formato_no_verificable_usa_motivo_estable_y_sin_detalle():
    from types import SimpleNamespace

    from vista.formato_resolubilidad import formatear_no_verificable
    from vista.formato_resolubilidad import formatear_reporte

    esperado = (
        "VEREDICTO: NO VERIFICABLE\n"
        "MOTIVO: consulta de llaves no disponible\n"
    )
    assert formatear_no_verificable().encode("utf-8") == esperado.encode("utf-8")
    assert formatear_reporte(
        SimpleNamespace(veredicto="NO VERIFICABLE")
    ).encode("utf-8") == esperado.encode("utf-8")


def test_resumen_no_verificable_coincide_con_el_contrato():
    from types import SimpleNamespace

    from vista.formato_resolubilidad import formatear_resumen

    resultado = SimpleNamespace(veredicto="NO VERIFICABLE")
    assert formatear_resumen(resultado).encode("utf-8") == (
        "VEREDICTO: NO VERIFICABLE | "
        "MOTIVO: consulta de llaves no disponible\n"
    ).encode("utf-8")
