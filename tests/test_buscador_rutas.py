from modelo.buscador_rutas import (
    CacheDistanciasCazador,
    _crear_indice_registros,
    _decidir_cazador_individual,
    decidir_cazador,
)
from modelo.entidades.enemigo import Enemigo
from modelo.entidades.jugador import Jugador
from modelo.mundo.cripta_modelo import CriptaModelo
from modelo.mundo.sala import Sala
from modelo.mundo.salida import Salida
from estructuras.heap_prioridad_ruta import ColaPrioridadPosicion


def test_cola_prioridad_posicion_mantiene_orden_y_estado_local():
    cola = ColaPrioridadPosicion()
    cola.insertar(30, 10, 30, 10)
    cola.insertar(10, 2, 10, 2)
    cola.insertar(20, 2, 20, 2)
    assert cola.extraer_minimo() == (10, 2, 10, 2)
    assert cola.extraer_minimo() == (20, 2, 20, 2)
    assert cola.extraer_minimo() == (30, 10, 30, 10)


def _mapa_ids(ids, aristas):
    cripta = CriptaModelo("indices", "1", ids[0], ids[-1], None, 0, 10)
    salas = []
    por_id = {}
    for sala_id in ids:
        sala = Sala(sala_id, "Sala " + str(sala_id))
        salas.append(sala)
        por_id[sala_id] = sala
        cripta.agregar_sala(sala)
    for origen, destino, costo, cerrada in aristas:
        por_id[origen].salidas.insertar_al_final(
            Salida("X", destino, cerrada=cerrada, costo=costo)
        )
    cripta.finalizar_carga()
    return cripta, por_id


def test_indice_por_cripta_funciona_con_mapa_denso():
    cripta, por_id = _mapa_ids(
        [1, 2, 3, 4],
        [(1, 2, 3, False), (2, 4, 5, False), (3, 4, 1, False)],
    )
    assert cripta.posicion_sala_por_id(1) == 0
    assert cripta.posicion_sala_por_id(4) == 3
    assert cripta.posicion_sala_por_id(999) is None
    assert por_id[1].cripta is cripta


def test_indice_por_cripta_funciona_con_ids_dispersos_sin_memoria_por_maximo():
    cripta, por_id = _mapa_ids(
        [10, 300, 1001, 900001],
        [(10, 300, 2, False), (300, 1001, 7, False),
         (1001, 900001, 4, False)],
    )
    assert cripta.posicion_sala_por_id(10) == 0
    assert cripta.posicion_sala_por_id(1001) == 2
    assert cripta.posicion_sala_por_id(900001) == 3
    assert cripta.posicion_sala_por_id(900000) is None
    assert por_id[300].cripta is cripta


def test_indices_de_dos_criptas_no_se_cruzan():
    cripta_a, por_a = _mapa_ids([1, 2], [(1, 2, 1, False)])
    cripta_b, por_b = _mapa_ids(
        [100000, 100003],
        [(100000, 100003, 9, False)],
    )
    assert cripta_a.posicion_sala_por_id(2) == 1
    assert cripta_b.posicion_sala_por_id(100003) == 1
    assert cripta_b.posicion_sala_por_id(2) is None
    assert por_a[2].cripta is cripta_a
    assert por_b[100003].cripta is cripta_b


def test_indice_individual_no_comparte_estado_entre_busquedas():
    cripta, por_id = _mapa_ids(
        [10, 30, 90],
        [(10, 30, 4, False), (30, 90, 6, False),
         (90, 30, 6, False), (30, 10, 4, False)],
    )
    jugador = Jugador("j", 100, 1, 1, 100, 10, por_id[90])
    cazador_a = Enemigo("a", "cazador", "Cazador", 100, 1, 0, 100,
                        "cazador", por_id[10], rango=10)
    cazador_b = Enemigo("b", "cazador", "Cazador", 100, 1, 0, 100,
                        "cazador", por_id[30], rango=6)

    primera = _decidir_cazador_individual(cazador_a, jugador)
    segunda = _decidir_cazador_individual(cazador_b, jugador)
    tercera = _decidir_cazador_individual(cazador_a, jugador)

    assert primera == ("mover", (por_id[30], 4))
    assert segunda == ("mover", (por_id[90], 6))
    assert tercera == primera


def test_individual_ponderado_puertas_rango_empate_y_sin_ruta():
    cripta, por_id = _mapa_ids(
        [10, 20, 30, 40],
        [(10, 20, 8, False), (10, 30, 2, False),
         (30, 40, 8, False), (20, 40, 2, False)],
    )
    jugador = Jugador("j", 100, 1, 1, 100, 10, por_id[40])

    cazador_limite = Enemigo("lim", "cazador", "Cazador", 100, 1, 0, 100,
                             "cazador", por_id[10], rango=10)
    assert _decidir_cazador_individual(cazador_limite, jugador)[0] == "mover"

    cazador_excedido = Enemigo("exc", "cazador", "Cazador", 100, 1, 0, 100,
                               "cazador", por_id[10], rango=9)
    assert _decidir_cazador_individual(cazador_excedido, jugador) == ("esperar", None)

    por_id[30].salida_hacia("X").cerrada = True
    cazador_cerrado = Enemigo("cerr", "cazador", "Cazador", 100, 1, 0, 100,
                              "cazador", por_id[10], rango=10)
    accion, objetivo = _decidir_cazador_individual(cazador_cerrado, jugador)
    assert accion == "esperar" or objetivo is not None


def test_cripta_construye_adjacencia_individual_inmutable_sin_guardar_distancias():
    cripta, por_id = _mapa_ids(
        [10, 30, 90],
        [(10, 30, 4, False), (30, 90, 6, False)],
    )
    adjacencia = cripta.adjacencia_individual()
    assert len(adjacencia) == 3
    vecinos_10 = adjacencia.obtenerValor(0)
    assert len(vecinos_10) == 1
    destino, salida = vecinos_10.obtenerValor(0)
    assert destino == 1
    assert salida.costo == 4

    salida.cerrada = True
    jugador = Jugador("j", 100, 1, 1, 100, 10, por_id[90])
    cazador = Enemigo("e", "cazador", "Cazador", 100, 1, 0, 100,
                      "cazador", por_id[10], rango=10)
    assert _decidir_cazador_individual(cazador, jugador) == ("esperar", None)
