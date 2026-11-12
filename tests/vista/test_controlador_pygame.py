"""ControladorPygame: eventos simulados -> mismas acciones que consola.

No importa pygame (controlador_pygame.py no lo necesita): son pruebas de
hilos y del protocolo de VistaConsola, no de render.
"""
import time

import pytest

from adaptadores.datos_offline import DatosOffline
from herramientas.generar_cripta_prueba import generar
from controlador.controlador_pygame import ControladorPygame

TIMEOUT = 5.0


def _fuente(tmp_path):
    carpeta = generar(tmp_path / "datos")
    return DatosOffline(str(carpeta))


def _controlador(tmp_path, **kwargs):
    return ControladorPygame(_fuente(tmp_path), carpeta_cache=str(tmp_path / "cache"),
                             partidas_dir=str(tmp_path / "partidas"), **kwargs)


def _esperar(condicion, timeout=TIMEOUT):
    limite = time.monotonic() + timeout
    while time.monotonic() < limite:
        if condicion():
            return True
        time.sleep(0.005)
    return False


def _iniciar(controlador, tmp_path, semilla=72, nombre="Ada"):
    controlador.iniciar_partida("cripta-prueba", nombre, semilla=semilla)
    assert _esperar(lambda: controlador.estado() is not None)


def test_iniciar_partida_publica_estado_inicial(tmp_path):
    c = _controlador(tmp_path)
    _iniciar(c, tmp_path)
    estado = c.estado()
    assert estado.sala_id == c.sesion.partida.cripta.sala_inicial_id
    assert estado.estado == "en_curso"
    assert estado.jugador.vida == estado.jugador.vida_max
    c.salir()


def test_una_accion_del_jugador_una_llamada_al_controlador(tmp_path):
    c = _controlador(tmp_path)
    _iniciar(c, tmp_path)
    t0 = c.estado().tiempo
    c.enviar_comando("R")   # recoger: cuesta tiempo, una sola llamada
    assert _esperar(lambda: c.estado().tiempo > t0)
    assert c.estado().acciones_jugador == 1
    c.salir()


def test_guardar_y_cargar_pasan_por_la_cola(tmp_path):
    c = _controlador(tmp_path)
    _iniciar(c, tmp_path)
    c.enviar_comando("R")
    assert _esperar(lambda: c.estado().acciones_jugador == 1)

    ruta = str(tmp_path / "partida.sav")
    c.guardar(ruta)
    assert _esperar(lambda: any("guardada" in m for m in c.mensajes()))

    c.enviar_comando("W")
    assert _esperar(lambda: c.estado().acciones_jugador == 2)

    c.cargar(ruta)
    assert _esperar(lambda: any("cargada" in m for m in c.mensajes()))
    assert _esperar(lambda: c.estado().acciones_jugador == 1)   # volvió al guardado
    c.salir()


def test_pergamino_pasa_por_la_cola_y_revierte_el_ultimo_intervalo(tmp_path):
    c = _controlador(tmp_path)
    _iniciar(c, tmp_path)
    # Recoge el pergamino (sala 1 de cripta-prueba lo trae en el suelo) y
    # espera una vez más: el pergamino debe revertir ESE 'esperar', no su
    # propia recogida.
    c.enviar_comando("R 5")   # 5to objeto del suelo = itm_pergamino_retroceso
    assert _esperar(lambda: c.estado().acciones_jugador == 1)
    assert _esperar(lambda: any(o.clase == "pergamino_retroceso" for o in c.estado().inventario))
    c.enviar_comando("W")
    assert _esperar(lambda: c.estado().acciones_jugador == 2)

    c.pergamino()
    assert _esperar(lambda: any("retrocede" in m for m in c.mensajes()))
    assert _esperar(lambda: c.estado().acciones_jugador == 1)
    # El pergamino se consume de forma irreversible al leerlo (README): la
    # recogida que lo trajo al inventario no se revierte, pero el objeto en
    # sí ya no está.
    assert not any(o.clase == "pergamino_retroceso" for o in c.estado().inventario)
    c.salir()


def test_salir_hace_join_sin_dejar_el_hilo_a_medias(tmp_path):
    c = _controlador(tmp_path)
    _iniciar(c, tmp_path)
    ruta_log = c.sesion.bitacora.ruta
    c.salir()
    assert c._hilo is None
    with open(ruta_log, encoding="utf-8") as f:
        contenido = f.read()
    assert " fin " in contenido   # registrar_cierre ya corrió: cierre ordenado


def test_excepcion_en_hilo_no_muere_en_silencio(tmp_path, monkeypatch):
    c = _controlador(tmp_path)
    _iniciar(c, tmp_path)

    def explota(*_a, **_k):
        raise RuntimeError("fallo simulado del modelo")
    monkeypatch.setattr(c._controlador, "ciclo", explota)

    c.enviar_comando("W")
    assert _esperar(lambda: c.error_pendiente() is not None)
    assert "fallo simulado del modelo" in c.error_pendiente()
    # El hilo terminó solo (la excepción no lo dejó colgado): join inmediato.
    c._hilo.join(timeout=TIMEOUT)
    assert not c._hilo.is_alive()


def test_hooks_enemigos_llegan_como_eventos_sin_referencias_pygame(tmp_path):
    c = _controlador(tmp_path)
    _iniciar(c, tmp_path, semilla=2026)
    # Mover a la sala 2 activa enemigos que atacan (ver tests/test_partida.py).
    c.enviar_comando("N")
    assert _esperar(lambda: c.estado().sala_id == 2)
    time.sleep(0.05)   # deja que los turnos de los enemigos ya programados lleguen
    eventos = c.eventos_nuevos()
    tipos = [getattr(e, "tipo", None) for e in eventos]
    assert "ataque" in tipos
    c.salir()


def test_snapshot_y_topologia_ocultan_avistadas_y_desconocidas_y_revelan_al_explorar(tmp_path):
    from vista_pygame.render.render_sala import calcular_layout_minimapa

    c = ControladorPygame(DatosOffline(), carpeta_cache=str(tmp_path / "cache"),
                          partidas_dir=str(tmp_path / "partidas"))
    c.iniciar_partida("cripta-01", "Ada", semilla=72)
    assert _esperar(lambda: c.estado() is not None)

    estado0 = c.estado()
    assert len(estado0.salidas) == 1
    assert estado0.salidas[0].direccion == "N"
    assert estado0.salidas[0].nombre_destino == "sala avistada"
    assert estado0.salidas[0].costo == 100

    topologia0 = c.topologia_cripta()
    por_id0 = {s.sala_id: s for s in topologia0}
    assert set(por_id0) == {1, 2}
    assert por_id0[1].nombre == "Entrada derruida"
    assert por_id0[1].salidas == [("N", 2)]
    assert por_id0[2].nombre == "" and por_id0[2].salidas == []
    for desconocida in (3, 4, 5, 6):
        assert desconocida not in por_id0

    layout0 = calcular_layout_minimapa(topologia0, c.sala_inicial_id())
    assert [sid for sid, _, _ in layout0] == [1, 2]

    c.enviar_comando("N")
    assert _esperar(lambda: c.estado().sala_id == 2)
    estado2 = c.estado()
    salidas2 = {s.direccion: s for s in estado2.salidas}
    assert salidas2["S"].nombre_destino == "Entrada derruida"
    assert salidas2["N"].nombre_destino == "sala avistada"
    assert salidas2["E"].nombre_destino == "sala avistada"

    topologia2 = c.topologia_cripta()
    por_id2 = {s.sala_id: s for s in topologia2}
    assert set(por_id2) == {1, 2, 3, 5}
    assert por_id2[2].nombre == "Pasillo de las urnas"
    assert por_id2[3].nombre == "" and por_id2[3].salidas == []
    assert por_id2[5].nombre == "" and por_id2[5].salidas == []
    for desconocida in (4, 6):
        assert desconocida not in por_id2

    layout2 = calcular_layout_minimapa(topologia2, c.sala_inicial_id())
    assert set(sid for sid, _, _ in layout2) == {1, 2, 3, 5}
    c.salir()
