"""G15: una llave asociada a un enemigo se ubica donde ese enemigo inicia."""

from bench.casos.resolubilidad import UbicacionLlave
from modelo.mundo.cripta_modelo import CriptaModelo
from modelo.mundo.sala import Sala
from modelo.mundo.salida import Salida


def _cripta_g15():
    cripta = CriptaModelo(
        "sintetica-g15", "v1", 10, 30, "key-exit", 0, 0
    )
    inicial = Sala(10, "Inicial")
    sala_enemigos = Sala(20, "Inicio de enemigos")
    salida = Sala(30, "Salida")
    inicial.salidas.insertar_al_final(Salida("E", 20))
    sala_enemigos.salidas.insertar_al_final(
        Salida("N", 30, cerrada=True, llave="key-exit")
    )
    for sala in (inicial, sala_enemigos, salida):
        cripta.agregar_sala(sala)
    cripta.finalizar_carga()
    ubicaciones = (
        UbicacionLlave("key-errante", 20, "enemy-errante"),
        UbicacionLlave("key-guard", 20, "enemy-no-errante"),
        UbicacionLlave("key-exit", 20, "enemy-no-registrado"),
    )
    return cripta, ubicaciones


def test_g15_llaves_de_enemigos_errantes_y_no_errantes_se_ubican_en_su_inicio():
    """G15 aplica la misma regla a cualquier enemigo y no valida su existencia (FR-004, FR-016)."""
    from modelo.verificador_resolubilidad import verificar_resolubilidad

    cripta, ubicaciones = _cripta_g15()
    resultado = verificar_resolubilidad(cripta, ubicaciones)
    entradas = tuple(
        entrada
        for ronda in resultado.orden_por_rondas
        for entrada in ronda
    )

    assert resultado.veredicto == "RESOLUBLE"
    assert tuple(
        (entrada.id, entrada.sala, entrada.enemigo)
        for entrada in entradas
    ) == (
        ("key-errante", 20, "enemy-errante"),
        ("key-exit", 20, "enemy-no-registrado"),
        ("key-guard", 20, "enemy-no-errante"),
    )
    assert resultado.puerta_final.origen == 20
    assert resultado.puerta_final.direccion == "N"
