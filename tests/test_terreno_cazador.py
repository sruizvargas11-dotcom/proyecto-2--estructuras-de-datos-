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


def test_mapa_ids_sala_dispersa_comparte_y_recalcula_individual():
    cripta = CriptaModelo("prueba-dispersa", "1", 10, 1001, None, 0, 10)
    salas = [Sala(10, "diez"), Sala(300, "trescientos"), Sala(1001, "mil")]
    salas[0].salidas.insertar_al_final(Salida("E", 300, costo=3))
    salas[1].salidas.insertar_al_final(Salida("E", 1001, costo=5))
    for sala in salas:
        cripta.agregar_sala(sala)
    cripta.finalizar_carga()

    jugador = Jugador("j", 100, 1, 1, 100, 10, salas[2])
    cazador = Enemigo("e", "cazador", "Cazador", 100, 1, 0, 100,
                      "cazador", salas[0], rango=8)

    individual = decidir_cazador(cazador, jugador)
    from modelo.buscador_rutas import CacheDistanciasCazador
    compartida = CacheDistanciasCazador(cripta)
    accion_compartida, objetivo_compartido = decidir_cazador(
        cazador, jugador, compartida.obtener(jugador)
    )

    assert individual == ("mover", (salas[1], 3))
    assert (accion_compartida, objetivo_compartido) == individual


def test_cache_invalida_por_revision_de_puerta_no_por_consulta_sin_cambio():
    from modelo.buscador_rutas import CacheDistanciasCazador
    _, salas = _mapa(1)
    jugador = Jugador("j", 100, 1, 1, 100, 10, salas[2])
    cache = CacheDistanciasCazador(salas[0].cripta)
    primera = cache.obtener(jugador)
    assert cache.obtener(jugador) is primera

    salida = next(iter(salas[0].salidas.recorrer_valores()))
    revision = salas[0].cripta.revision_puertas
    salida.cerrada = True
    assert salas[0].cripta.revision_puertas == revision + 1
    segunda = cache.obtener(jugador)
    assert segunda is not primera
    assert cache.obtener(jugador) is segunda


def test_cache_reconstruye_tras_deshacer_puerta_en_historial():
    from modelo.buscador_rutas import CacheDistanciasCazador
    from modelo.historial import Historial
    from modelo.deltas import DeltaPuerta

    cripta, salas = _mapa(1)
    jugador = Jugador("j", 100, 1, 1, 100, 10, salas[2])
    salida = next(iter(salas[0].salidas.recorrer_valores()))
    cache = CacheDistanciasCazador(cripta)
    inicial = cache.obtener(jugador)

    historial = Historial()
    delta = DeltaPuerta(salida)
    salida.cerrada = True
    delta.revertir()
    restaurada = cache.obtener(jugador)
    assert restaurada is not inicial


def test_cache_carga_puerta_restaurada_invalida_desde_estado_cargado():
    from modelo.buscador_rutas import CacheDistanciasCazador
    from modelo.entidades.jugador import Jugador
    from modelo.partida import Partida
    from persistencia.estado_partida import codificar, decodificar

    cripta, salas = _mapa(1)
    jugador = Jugador("j", 100, 1, 1, 100, 10, salas[2])
    partida = Partida(cripta, jugador, 42)
    partida.inicializar()
    cache = CacheDistanciasCazador(cripta)
    inicial = cache.obtener(jugador)

    referencia, registros = codificar(partida)
    partida_cargada = decodificar(referencia, registros)
    cargada = partida_cargada.cache_rutas_cazador
    if cargada is None:
        from modelo.buscador_rutas import CacheDistanciasCazador
        cargada = CacheDistanciasCazador(partida_cargada.cripta)
    reconstruida = cargada.obtener(partida_cargada.jugador)
    assert reconstruida is not inicial


def test_cache_reutiliza_indices_entrantes_y_distancias():
    from modelo.buscador_rutas import (
        CacheDistanciasCazador,
        _construir_entrantes,
        _distancias_hacia_jugador,
    )
    _, salas = _mapa(1)
    jugador = Jugador("j", 100, 1, 1, 100, 10, salas[2])
    cripta = salas[0].cripta
    cache = CacheDistanciasCazador(cripta)
    primera = cache.obtener(jugador)

    assert cache.indice_entrantes is not None
    assert cache.indice_distancias is not None
    entrantes = _construir_entrantes(
        cripta, cache.indice_entrantes
    )
    distancias = _distancias_hacia_jugador(
        cripta,
        jugador,
        entrantes,
        cache.indice_distancias,
        cache.indice_entrantes,
    )
    assert distancias is not primera
    assert cache.indice_entrantes is not None


def test_cache_reutiliza_topologia_y_consulta_estado_actual_de_puertas():
    from modelo.buscador_rutas import CacheDistanciasCazador

    cripta, salas = _mapa(1)
    jugador = Jugador("j", 100, 1, 1, 100, 10, salas[2])
    cazador = Enemigo("e", "cazador", "Cazador", 100, 1, 0, 100,
                      "cazador", salas[0], rango=2)
    cache = CacheDistanciasCazador(cripta)

    distancias_abiertas = cache.obtener(jugador)
    topologia = cache._entrantes
    assert decidir_cazador(cazador, jugador, distancias_abiertas)[0] == "mover"

    jugador.sala_actual = salas[1]
    distancias_jugador_movido = cache.obtener(jugador)
    assert distancias_jugador_movido is not distancias_abiertas
    assert cache._entrantes is topologia
    assert decidir_cazador(cazador, jugador, distancias_jugador_movido) == (
        "mover", (salas[1], 1)
    )
    jugador.sala_actual = salas[2]
    distancias_abiertas = cache.obtener(jugador)

    salida = next(iter(salas[0].salidas.recorrer_valores()))
    salida.cerrada = True
    distancias_cerradas = cache.obtener(jugador)
    assert cache._entrantes is topologia
    assert distancias_cerradas is not distancias_abiertas
    assert decidir_cazador(cazador, jugador, distancias_cerradas) == ("esperar", None)

    salida.cerrada = False
    distancias_reabiertas = cache.obtener(jugador)
    assert cache._entrantes is topologia
    assert decidir_cazador(cazador, jugador, distancias_reabiertas)[0] == "mover"


def test_topologia_cacheada_funciona_con_ids_dispersos_y_reversion_de_puerta():
    from modelo.buscador_rutas import CacheDistanciasCazador
    from modelo.deltas import DeltaPuerta

    cripta = CriptaModelo("prueba-dispersa", "1", 10, 1001, None, 0, 10)
    salas = [Sala(10, "diez"), Sala(300, "trescientos"), Sala(1001, "mil")]
    salas[0].salidas.insertar_al_final(Salida("E", 300, costo=3))
    salas[1].salidas.insertar_al_final(Salida("E", 1001, costo=5))
    for sala in salas:
        cripta.agregar_sala(sala)
    cripta.finalizar_carga()

    jugador = Jugador("j", 100, 1, 1, 100, 10, salas[2])
    cazador = Enemigo("e", "cazador", "Cazador", 100, 1, 0, 100,
                      "cazador", salas[0], rango=8)
    cache = CacheDistanciasCazador(cripta)
    distancias_abiertas = cache.obtener(jugador)
    topologia = cache._entrantes
    assert decidir_cazador(cazador, jugador, distancias_abiertas) == (
        "mover", (salas[1], 3)
    )

    salida = next(iter(salas[0].salidas.recorrer_valores()))
    delta = DeltaPuerta(salida)
    salida.cerrada = True
    distancias_cerradas = cache.obtener(jugador)
    assert cache._entrantes is topologia
    assert decidir_cazador(cazador, jugador, distancias_cerradas) == ("esperar", None)

    delta.revertir()
    distancias_revertidas = cache.obtener(jugador)
    assert cache._entrantes is topologia
    assert decidir_cazador(cazador, jugador, distancias_revertidas) == (
        "mover", (salas[1], 3)
    )
