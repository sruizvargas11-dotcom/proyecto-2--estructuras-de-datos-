"""Formato de consola estable para los reportes de resolubilidad."""


def _motivo_no_resoluble(codigo):
    if codigo == "a":
        return "(a) llave_salida inobtenible"
    if codigo == "b":
        return (
            "(b) llave_salida obtenida, pero no se alcanza ninguna puerta "
            "hacia sala_salida que la requiera"
        )
    return None


def _formatear_ubicacion(ubicacion):
    texto = f"sala:{ubicacion.sala}"
    if ubicacion.enemigo is not None:
        texto += f", enemigo:{ubicacion.enemigo}"
    return texto


def _formatear_reporte_no_resoluble(resultado):
    motivo = _motivo_no_resoluble(resultado.motivo)
    if motivo is None:
        raise ValueError("Motivo de NO RESOLUBLE desconocido")

    llaves_obtenidas = sum(len(ronda) for ronda in resultado.orden_por_rondas)
    lineas = [
        "VEREDICTO: NO RESOLUBLE",
        f"MOTIVO: {motivo}",
        (
            f"REGION: salas={len(resultado.salas_alcanzables)} "
            f"| llaves_obtenidas={llaves_obtenidas}"
        ),
        "LLAVES_INOBTENIBLES:",
    ]
    for llave in resultado.llaves_inobtenibles:
        ubicaciones = "; ".join(
            _formatear_ubicacion(ubicacion)
            for ubicacion in llave.ubicaciones
        )
        lineas.append(
            f"  - id={llave.id} | ubicaciones=[{ubicaciones}] "
            f"| causa={llave.causa}"
        )

    lineas.append("FRONTERA_BLOQUEADA:")
    for puerta in resultado.frontera_bloqueada:
        llave = (
            puerta.llave
            if puerta.llave is not None and puerta.ubicaciones_llave
            else "inexistente"
        )
        lineas.append(
            f"  - origen={puerta.origen} | direccion={puerta.direccion} "
            f"| destino={puerta.destino} | llave={llave}"
        )

    lineas.append("CICLOS:")
    for ciclo in resultado.ciclos:
        llaves = " -> ".join(ciclo.llaves)
        puertas = "; ".join(
            f"origen={puerta.origen}, direccion={puerta.direccion}"
            for puerta in ciclo.puertas
        )
        lineas.append(f"  - llaves={llaves} | puertas=[{puertas}]")

    return "\n".join(lineas) + "\n"


def formatear_reporte(resultado):
    """Devuelve el reporte completo de un resultado de alcanzabilidad."""
    if resultado.veredicto == "RESOLUBLE":
        lineas = [
            "VEREDICTO: RESOLUBLE",
            "ORDEN_POR_RONDAS:",
        ]
        for numero, ronda in enumerate(resultado.orden_por_rondas):
            lineas.append(f"  RONDA {numero}:")
            for ubicacion in ronda:
                enemigo = (
                    ubicacion.enemigo
                    if ubicacion.enemigo is not None
                    else "ninguno"
                )
                lineas.append(
                    f"    - id={ubicacion.id} | sala={ubicacion.sala} "
                    f"| enemigo={enemigo}"
                )
        puerta = resultado.puerta_final
        lineas.append(
            f"PUERTA_FINAL: origen={puerta.origen} "
            f"| direccion={puerta.direccion} | destino={puerta.destino}"
        )
        return "\n".join(lineas) + "\n"
    if resultado.veredicto == "NO RESOLUBLE":
        return _formatear_reporte_no_resoluble(resultado)
    raise ValueError("Veredicto no admitido para un reporte de alcanzabilidad")


def formatear_resumen(resultado):
    """Devuelve solo el veredicto y, cuando aplica, el motivo no resoluble."""
    if resultado.veredicto == "RESOLUBLE":
        return "VEREDICTO: RESOLUBLE\n"
    if resultado.veredicto == "NO RESOLUBLE":
        motivo = _motivo_no_resoluble(resultado.motivo)
        if motivo is None:
            raise ValueError("Motivo de NO RESOLUBLE desconocido")
        return f"VEREDICTO: NO RESOLUBLE | MOTIVO: {motivo}\n"
    raise ValueError("Veredicto no admitido para un resultado de alcanzabilidad")


def formatear_no_verificable():
    """Devuelve la salida estable para un fallo de consulta de llaves."""
    return (
        "VEREDICTO: NO VERIFICABLE\n"
        "MOTIVO: consulta de llaves no disponible\n"
    )
