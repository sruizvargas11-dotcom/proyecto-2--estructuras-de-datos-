"""Escenarios RS-E28–RS-E29 para ciclos y prioridad de causas."""

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
    for origen, direccion, destino, llave in puertas:
        for sala in salas:
            if sala.id == origen:
                sala.salidas.insertar_al_final(
                    Salida(direccion, destino, cerrada=True, llave=llave)
                )
                break
    cripta.finalizar_carga()
    return cripta


def test_rs_e28_ciclo_mas_corto_y_desempate_lexicografico_por_llave():
    """RS-E28: cada llave recibe su ciclo mínimo con desempate lexicográfico (FR-012, FR-021)."""
    from modelo.verificador_resolubilidad import verificar_resolubilidad

    cripta = _crear_cripta(
        "sintetica-rs-e28",
        10,
        99,
        "key-a",
        (10, 20, 30, 35, 40, 45, 50, 70, 99),
        (
            (10, "Z", 20, "key-b"),
            (10, "A", 20, "key-b"),
            (20, "C", 30, "key-c"),
            (30, "E", 35, "key-e"),
            (10, "B", 40, "key-a"),
            (10, "C", 45, "key-a"),
            (10, "D", 50, "key-a"),
            (10, "F", 70, "key-d"),
            (35, "Z", 99, "key-a"),
        ),
    )
    ubicaciones = (
        UbicacionLlave("key-a", 35),
        UbicacionLlave("key-b", 40),
        UbicacionLlave("key-c", 70),
        UbicacionLlave("key-d", 50),
        UbicacionLlave("key-e", 45),
    )

    resultado = verificar_resolubilidad(cripta, ubicaciones)
    ciclos = tuple(ciclo.llaves for ciclo in resultado.ciclos)

    ciclo_ab = ("key-a", "key-b", "key-a")
    ciclo_ae = ("key-a", "key-e", "key-a")
    ciclo_acd = ("key-a", "key-c", "key-d", "key-a")
    assert sum(ciclo == ciclo_ab for ciclo in ciclos) == 2
    assert sum(ciclo == ciclo_ae for ciclo in ciclos) == 1
    assert sum(ciclo == ciclo_acd for ciclo in ciclos) == 2
    assert all(ciclo[0] == min(ciclo[:-1]) for ciclo in ciclos)

    for ciclo in resultado.ciclos:
        puertas = tuple(
            (puerta.origen, puerta.direccion)
            for puerta in ciclo.puertas
        )
        assert all(
            puertas[indice] <= puertas[indice + 1]
            for indice in range(len(puertas) - 1)
        )


def test_rs_e29_participantes_de_ciclo_preceden_a_causas_dependientes():
    """RS-E29: solo participantes reportados reciben «en ciclo» (FR-011)."""
    from modelo.verificador_resolubilidad import verificar_resolubilidad

    cripta = _crear_cripta(
        "sintetica-rs-e29",
        10,
        99,
        "key-a",
        (10, 20, 30, 40, 99),
        (
            (10, "A", 20, "key-b"),
            (10, "B", 30, "key-a"),
            (10, "C", 40, "key-b"),
            (20, "Z", 99, "key-a"),
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
        ("key-a", "en ciclo"),
        ("key-b", "en ciclo"),
        ("key-c", "depende de key-b"),
    )
