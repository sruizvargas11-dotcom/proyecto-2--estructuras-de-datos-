"""G16: múltiples órdenes válidos deben resolverse con el mismo orden por rondas."""

from bench.casos.resolubilidad import (
    generar_cripta_sintetica,
)


def _bytes_orden(resultado):
    lineas = []
    for numero, ronda in enumerate(resultado.orden_por_rondas):
        lineas.append(f"RONDA {numero}")
        for llave in ronda:
            enemigo = llave.enemigo if llave.enemigo is not None else "ninguno"
            lineas.append(
                f"id={llave.id}|sala={llave.sala}|enemigo={enemigo}"
            )
    return "\n".join(lineas).encode("utf-8")


def test_g16_dos_ejecuciones_producen_orden_por_rondas_byte_a_byte_igual():
    """G16 comprueba determinismo observable en dos verificaciones independientes (FR-010, FR-017; SC-003)."""
    from modelo.verificador_resolubilidad import verificar_resolubilidad

    primera = generar_cripta_sintetica(
        semilla=91, cantidad_llaves=6, estructura="alternativa"
    )
    segunda = generar_cripta_sintetica(
        semilla=91, cantidad_llaves=6, estructura="alternativa"
    )
    resultado_a = verificar_resolubilidad(
        primera.cripta, primera.ubicaciones
    )
    resultado_b = verificar_resolubilidad(
        segunda.cripta, segunda.ubicaciones
    )

    assert _bytes_orden(resultado_a) == _bytes_orden(resultado_b)
