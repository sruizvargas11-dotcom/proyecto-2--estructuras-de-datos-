from modelo.buscador_rutas import decidir_cazador
from modelo.entidades.enemigo import Enemigo
from modelo.entidades.jugador import Jugador
from modelo.mundo.cripta_modelo import CriptaModelo
from modelo.mundo.sala import Sala
from modelo.mundo.salida import Salida
from modelo.reloj import Reloj


def _mapa(costo=1):
    cripta = CriptaModelo("prueba", "1", 1, 3, None, 0, 10)
    salas = [Sala(1, "uno"), Sala(2, "dos"), Sala(3, "tres")]
    salas[0].salidas.insertar_al_final(Salida("E", 2, costo=costo))
    salas[1].salidas.insertar_al_final(Salida("O", 1, costo=costo))
    salas[1].salidas.insertar_al_final(Salida("E", 3, costo=costo))
    salas[2].salidas.insertar_al_final(Salida("O", 2, costo=costo))
    for sala in salas:
        cripta.agregar_sala(sala)
    cripta.finalizar_carga()
    return cripta, salas


def test_intervalo_costo_uno_no_es_cero():
    assert Reloj.intervalo(1, 1000) == 1


def test_cazador_avanza_un_paso_y_usa_costo():
    _, salas = _mapa(7)
    jugador = Jugador("j", 100, 1, 1, 100, 10, salas[2])
    cazador = Enemigo("e", "cazador", "Cazador", 100, 1, 0, 100,
                      "cazador", salas[0], rango=14)
    accion, objetivo = decidir_cazador(cazador, jugador)
    assert accion == "mover"
    assert objetivo[0] is salas[1]
    assert objetivo[1] == 7


def test_cazador_espera_fuera_de_rango():
    _, salas = _mapa(7)
    jugador = Jugador("j", 100, 1, 1, 100, 10, salas[2])
    cazador = Enemigo("e", "cazador", "Cazador", 100, 1, 0, 100,
                      "cazador", salas[0], rango=13)
    assert decidir_cazador(cazador, jugador) == ("esperar", None)


def test_cazador_ataca_solo_en_sala_compartida():
    _, salas = _mapa()
    jugador = Jugador("j", 100, 1, 1, 100, 10, salas[0])
    cazador = Enemigo("e", "cazador", "Cazador", 100, 1, 0, 100,
                      "cazador", salas[0], rango=1)
    assert cazador.decidir_accion(jugador, 0, None)[0] == "atacar"


def test_cazador_elige_vecina_de_menor_id_en_empate():
    cripta = CriptaModelo("prueba", "1", 1, 4, None, 0, 10)
    salas = [Sala(i, str(i)) for i in range(1, 5)]
    salas[0].salidas.insertar_al_final(Salida("E", 3, costo=2))
    salas[0].salidas.insertar_al_final(Salida("S", 2, costo=2))
    salas[1].salidas.insertar_al_final(Salida("E", 4, costo=2))
    salas[2].salidas.insertar_al_final(Salida("S", 4, costo=2))
    for sala in salas:
        cripta.agregar_sala(sala)
    cripta.finalizar_carga()
    jugador = Jugador("j", 100, 1, 1, 100, 10, salas[3])
    cazador = Enemigo("e", "cazador", "Cazador", 100, 1, 0, 100,
                      "cazador", salas[0], rango=4)
    accion, objetivo = decidir_cazador(cazador, jugador)
    assert accion == "mover" and objetivo[0] is salas[1]


def test_cazador_recalcula_si_se_cierra_la_salida():
    _, salas = _mapa(7)
    jugador = Jugador("j", 100, 1, 1, 100, 10, salas[2])
    cazador = Enemigo("e", "cazador", "Cazador", 100, 1, 0, 100,
                      "cazador", salas[0], rango=14)
    next(iter(salas[0].salidas.recorrer_valores())).cerrada = True
    accion, objetivo = decidir_cazador(cazador, jugador)
    assert accion == "esperar" and objetivo is None


def test_cazador_entra_en_sala_ocupada_sin_bloquearse():
    _, salas = _mapa(1)
    jugador = Jugador("j", 100, 1, 1, 100, 10, salas[2])
    otro = Enemigo("o", "errante", "Otro", 100, 1, 0, 100,
                   "errante", salas[1])
    cazador = Enemigo("e", "cazador", "Cazador", 100, 1, 0, 100,
                      "cazador", salas[0], rango=2)
    accion, objetivo = decidir_cazador(cazador, jugador)
    assert accion == "mover" and objetivo[0] is otro.sala_actual


def test_cazador_prefiere_mayor_numero_de_salas_si_cuesta_menos():
    cripta = CriptaModelo("prueba", "1", 1, 5, None, 0, 10)
    salas = [Sala(i, str(i)) for i in range(1, 6)]
    salas[0].salidas.insertar_al_final(Salida("E", 5, costo=9))
    salas[0].salidas.insertar_al_final(Salida("S", 2, costo=2))
    salas[1].salidas.insertar_al_final(Salida("E", 3, costo=2))
    salas[2].salidas.insertar_al_final(Salida("E", 4, costo=2))
    salas[3].salidas.insertar_al_final(Salida("E", 5, costo=2))
    salas[4].salidas.insertar_al_final(Salida("O", 1, costo=9))
    salas[1].salidas.insertar_al_final(Salida("O", 1, costo=2))
    salas[2].salidas.insertar_al_final(Salida("O", 2, costo=2))
    salas[3].salidas.insertar_al_final(Salida("O", 3, costo=2))
    salas[4].salidas.insertar_al_final(Salida("O", 4, costo=2))
    for sala in salas:
        cripta.agregar_sala(sala)
    cripta.finalizar_carga()
    jugador = Jugador("j", 100, 1, 1, 100, 10, salas[4])
    cazador = Enemigo("e", "cazador", "Cazador", 100, 1, 0, 100,
                      "cazador", salas[0], rango=10)
    accion, objetivo = decidir_cazador(cazador, jugador)
    assert accion == "mover" and objetivo[0] is salas[1]


def test_desempate_prioriza_id_aunque_las_primeras_salidas_cuesten_distinto():
    cripta = CriptaModelo("prueba", "1", 1, 5, None, 0, 10)
    salas = [Sala(i, str(i)) for i in range(1, 6)]
    salas[0].salidas.insertar_al_final(Salida("E", 2, costo=8))
    salas[0].salidas.insertar_al_final(Salida("S", 3, costo=2))
    salas[1].salidas.insertar_al_final(Salida("E", 5, costo=2))
    salas[2].salidas.insertar_al_final(Salida("E", 4, costo=2))
    salas[3].salidas.insertar_al_final(Salida("E", 5, costo=6))
    for sala in salas:
        cripta.agregar_sala(sala)
    cripta.finalizar_carga()
    jugador = Jugador("j", 100, 1, 1, 100, 10, salas[4])
    cazador = Enemigo("e", "cazador", "Cazador", 100, 1, 0, 100,
                      "cazador", salas[0], rango=10)
    accion, objetivo = decidir_cazador(cazador, jugador)
    assert accion == "mover" and objetivo[0] is salas[1]


def test_cache_compartida_reutiliza_e_invalida_por_puerta_y_jugador():
    from modelo.buscador_rutas import CacheDistanciasCazador
    _, salas = _mapa(1)
    jugador = Jugador("j", 100, 1, 1, 100, 10, salas[2])
    cache = CacheDistanciasCazador(salas[0].cripta)
    primera = cache.obtener(jugador)
    assert cache.obtener(jugador) is primera
    salida = next(iter(salas[0].salidas.recorrer_valores()))
    salida.cerrada = True
    segunda = cache.obtener(jugador)
    assert segunda is not primera
    jugador.sala_actual = salas[1]
    assert cache.obtener(jugador) is not segunda
