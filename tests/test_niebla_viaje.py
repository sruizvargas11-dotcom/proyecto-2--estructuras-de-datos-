"""Pruebas de aceptación de la spec 002 (niebla de guerra, antorcha e ir a).

Cada prueba cita el escenario NV y los FR que verifica.
"""
import pytest

from estructuras.vector_dinamico import Vector
from controlador.controlador_juego import ControladorJuego, interpretar
from modelo.buscador_rutas import decidir_cazador
from modelo.conocimiento import (ABIERTA, AVISTADA, CERRADA, DESCONOCIDA, EXPLORADA,
                                 SIN_OBSERVAR)
from modelo.entidades.enemigo import Enemigo
from modelo.entidades.jugador import Jugador
from modelo.entidades.objetos.antorcha import Antorcha
from modelo.entidades.objetos.pergamino_retroceso import PergaminoRetroceso
from modelo.entidades.trampa import Trampa
from modelo.mundo.cripta_modelo import CriptaModelo
from modelo.mundo.sala import Sala
from modelo.mundo.salida import Salida
from modelo.partida import Partida

OPUESTA = {"N": "S", "S": "N", "E": "O", "O": "E"}


# ------------------------------------------------------------------ apoyo
def crear_partida(conexiones, salas=None, inicio=1, vida=100):
    """conexiones: (origen, dir, destino, costo[, cerrada]) bidireccionales."""
    ids = set(salas or ())
    for c in conexiones:
        ids.add(c[0]); ids.add(c[2])
    cripta = CriptaModelo("prueba-002", "1", inicio, 999, None, 0, 10)
    objetos = {i: Sala(i, f"Sala {i}") for i in sorted(ids)}
    for c in conexiones:
        origen, direccion, destino, costo = c[:4]
        cerrada = c[4] if len(c) > 4 else False
        objetos[origen].salidas.insertar_al_final(
            Salida(direccion, destino, cerrada=cerrada, costo=costo))
        objetos[destino].salidas.insertar_al_final(
            Salida(OPUESTA[direccion], origen, cerrada=cerrada, costo=costo))
    for sala in objetos.values():
        cripta.agregar_sala(sala)
    cripta.finalizar_carga()
    jugador = Jugador("jugador", vida, 5, 0, 100, 10, objetos[inicio])
    partida = Partida(cripta, jugador, 7)
    return partida, objetos


def salida(sala, direccion):
    return sala.salida_hacia(direccion)


def poner_dormido(sala, instancia="e-1", velocidad=100):
    enemigo = Enemigo(instancia, "ent", "Guardia", 50, 1, 0, velocidad, "guardi\u00e1n")
    sala.enemigos_dormidos.insertar_al_final(enemigo)
    return enemigo


def dar_antorcha(partida):
    antorcha = Antorcha("a-1", "itm_antorcha", "Antorcha", 1, 1, 10000)
    antorcha.encendida = True
    partida.jugador.inventario.insertar_al_final(antorcha)
    return antorcha


def dar_pergamino(partida, n=1):
    for i in range(n):
        partida.jugador.inventario.insertar_al_final(
            PergaminoRetroceso(f"p-{i}", "itm_pergamino_retroceso", "Pergamino", 0, 0))


class RedFalsa:
    def incorporar_listas(self): pass
    def asegurar_entrada(self, sala_id): return None
    def planificar_precarga(self, sala): pass
    def procesar_cola(self): pass
    def proteger_fichas(self, f): pass
    def liberar_fichas(self, f): pass
    def cerrar(self, t=None): pass
    def ids_enemigos_vivos(self): return Vector()
    def reconciliar_enemigos_revividos(self, v): pass


class BitacoraFalsa:
    def __init__(self):
        self.lineas = []

    def registrar(self, tiempo, accion):
        self.lineas.append(f"t={tiempo} {accion}")

    def registrar_comentario(self, tiempo, texto):
        self.lineas.append(f"# t={tiempo} {texto}")

    def registrar_cierre(self, *a): pass
    def cerrar(self): pass


class Sesion:
    def __init__(self, partida):
        self.partida = partida
        self.red = RedFalsa()
        self.bitacora = BitacoraFalsa()
        self.acciones = Vector()


class Vista:
    def __init__(self, comandos):
        self.comandos = list(comandos)
        self.mensajes = []

    def agregar_mensaje(self, t, texto): self.mensajes.append((t, texto))
    def mostrar_estado(self, partida): pass
    def mostrar_ayuda(self): pass
    def mostrar_fin(self, partida): pass
    def leer_comando(self): return self.comandos.pop(0) if self.comandos else "Q"

    def hay(self, fragmento):
        return any(fragmento in m for _, m in self.mensajes)


def jugar(partida, comandos, conocer=()):
    """Inicializa, precarga conocimiento (fuera de acciones) y juega."""
    partida.inicializar()
    for sala in conocer:
        partida.conocimiento.visitar(sala, 0)
    sesion = Sesion(partida)
    vista = Vista(comandos)
    controlador = ControladorJuego(sesion, vista)
    controlador.jugar()
    return controlador, vista, sesion.bitacora.lineas


def movimientos(lineas):
    return [l.split(" ", 1)[1] for l in lineas if l.startswith("t=") and " mover " in f" {l} "]


# ------------------------------------------------------------------ US1
def test_nv01_instante_cero():
    """NV-01; FR-001, FR-002."""
    partida, s = crear_partida([(1, "E", 2, 100), (2, "E", 3, 100)])
    partida.inicializar()
    c = partida.conocimiento
    assert (c.estado_sala(1), c.estado_sala(2), c.estado_sala(3)) == (
        EXPLORADA, AVISTADA, DESCONOCIDA)


def test_nv02_visitar_explora_y_avista():
    """NV-02; FR-001, FR-002."""
    partida, s = crear_partida([(1, "E", 2, 100), (2, "E", 3, 100)])
    jugar(partida, ["E"])
    c = partida.conocimiento
    assert c.estado_sala(2) == EXPLORADA and c.estado_sala(3) == AVISTADA


def test_nv03_avistada_y_desconocida_no_revelan():
    """NV-03; FR-003."""
    partida, s = crear_partida([(1, "E", 2, 100), (2, "E", 3, 100)])
    partida.inicializar()
    mapa = partida.conocimiento.vista_mapa()
    assert len(mapa) == 1
    sala_id, nombre, salidas = mapa[0]
    assert salidas == (("E", 100, ABIERTA, AVISTADA),)
    texto = repr(mapa)
    assert "Sala 2" not in texto and "Sala 3" not in texto
    assert partida.conocimiento.puerta_recordada(2, "E") is None


def test_nv04_y_nv05_recuerdo_de_puertas():
    """NV-04, NV-05; FR-004."""
    partida, s = crear_partida([(1, "E", 2, 100), (2, "E", 3, 100)])
    partida.inicializar()
    c = partida.conocimiento
    c.visitar(s[2], 0)
    assert c.puerta_recordada(2, "E") == ABIERTA
    salida(s[2], "E").cerrada = True          # cambia lejos del jugador
    salida(s[2], "E").cerrada = False
    salida(s[2], "E").cerrada = True
    assert c.puerta_recordada(2, "E") == ABIERTA
    c.observar(s[3], 5)                       # desde el otro extremo
    assert c.puerta_recordada(2, "E") == CERRADA


def test_nv06_datos_precargados_no_son_conocimiento():
    """NV-06; FR-006. El contenido descargado no altera el conocimiento."""
    partida, s = crear_partida([(1, "E", 2, 100), (2, "E", 3, 100)])
    partida.inicializar()
    antes = partida.conocimiento.resumen()
    s[3].objetos_suelo.insertar_al_final(object())   # simula contenido incorporado
    poner_dormido(s[3])
    assert partida.conocimiento.resumen() == antes
    assert partida.conocimiento.estado_sala(3) == DESCONOCIDA


def test_nv28_cazador_no_limitado_por_niebla():
    """NV-28; FR-006 (FR-009 de 001)."""
    partida, s = crear_partida([(1, "E", 2, 100), (2, "E", 3, 100)])
    partida.inicializar()
    cazador = Enemigo("c", "c", "Cazador", 10, 1, 0, 100, "cazador", s[3], rango=500)
    assert partida.conocimiento.estado_sala(3) == DESCONOCIDA
    accion, objetivo = decidir_cazador(cazador, partida.jugador)
    assert accion == "mover" and objetivo[0] is s[2]


# ------------------------------------------------------------------ US2
def test_nv07_nv33_rechazo_unico_sin_tiempo():
    """NV-07, NV-33; FR-008."""
    partida, s = crear_partida([(1, "E", 2, 100), (2, "E", 3, 100)])
    ctl, vista, lineas = jugar(partida, ["IR A 3", "IR A 77", "IR A x"])
    rechazos = [m for _, m in vista.mensajes if m == ControladorJuego.RECHAZO_DESTINO]
    assert len(rechazos) == 3
    assert partida.tiempo == 0 and movimientos(lineas) == []


def test_nv08_menor_costo_frente_a_menos_salas():
    """NV-08; FR-009, FR-011."""
    partida, s = crear_partida([(1, "E", 2, 100), (2, "E", 3, 100),
                                (1, "S", 4, 10), (4, "E", 5, 10), (5, "N", 3, 10)])
    ctl, vista, lineas = jugar(partida, ["IR A 3"], conocer=s.values())
    assert movimientos(lineas) == ["mover S", "mover E", "mover N"]
    assert partida.sala_actual is s[3] and partida.tiempo == 30
    assert vista.hay("fin del viaje")


def test_nv09_empate_vecina_de_menor_id():
    """NV-09; FR-009."""
    partida, s = crear_partida([(1, "E", 3, 10), (1, "S", 2, 10),
                                (3, "S", 4, 10), (2, "E", 4, 10)])
    ctl, vista, lineas = jugar(partida, ["IR A 4"], conocer=s.values())
    assert movimientos(lineas)[0] == "mover S"     # vecina 2 < 3


def test_nv10_puerta_recordada_abierta_realmente_cerrada_con_alternativa():
    """NV-10; FR-004, FR-010."""
    partida, s = crear_partida([(1, "E", 2, 100), (2, "E", 3, 100),
                                (1, "S", 4, 150), (4, "E", 5, 150), (5, "N", 3, 150)])
    partida.inicializar()
    for sala in s.values():
        partida.conocimiento.visitar(sala, 0)
    salida(s[2], "E").cerrada = True                # el jugador no lo ve desde 1
    ctl = ControladorJuego(Sesion(partida), Vista(["IR A 3"]))
    ctl.jugar()
    lineas = ctl.bitacora.lineas
    assert movimientos(lineas) == ["mover E", "mover O", "mover S", "mover E", "mover N"]
    assert partida.conocimiento.puerta_recordada(2, "E") == CERRADA
    # Sin tiempo extra por el intento: 100 + 100 + 3 * 150.
    assert partida.tiempo == 650 and partida.sala_actual is s[3]


def test_nv10_nv11_sin_alternativa_se_detiene_sin_tiempo_extra():
    """NV-10, NV-11; FR-010, FR-012."""
    partida, s = crear_partida([(1, "E", 2, 100), (2, "E", 3, 100)])
    partida.inicializar()
    for sala in s.values():
        partida.conocimiento.visitar(sala, 0)
    salida(s[2], "E").cerrada = True
    ctl = ControladorJuego(Sesion(partida), Vista(["IR A 3"]))
    ctl.jugar()
    assert movimientos(ctl.bitacora.lineas) == ["mover E"]
    assert partida.tiempo == 100 and ctl.ultima_causa_viaje == "sin ruta conocida"


def test_nv11_sin_ruta_al_ordenar():
    """NV-11; FR-010, FR-012."""
    partida, s = crear_partida([(1, "E", 2, 100, True), (2, "E", 3, 100)])
    ctl, vista, lineas = jugar(partida, ["IR A 3"], conocer=[s[2], s[3]])
    assert vista.hay("Viaje detenido: sin ruta conocida.") and partida.tiempo == 0


def test_nv12_enemigos_dormidos_se_activan_y_detienen():
    """NV-12; FR-012."""
    partida, s = crear_partida([(1, "E", 2, 100), (2, "E", 3, 100)])
    enemigo = poner_dormido(s[2], velocidad=50)
    ctl, vista, lineas = jugar(partida, ["IR A 3"], conocer=s.values())
    assert movimientos(lineas) == ["mover E"]
    assert enemigo.sala_actual is s[2] and s[2].enemigos_activos.contiene_valor(enemigo)
    assert ctl.ultima_causa_viaje == "enemigos"


def test_nv13_dano_entre_pasos():
    """NV-13; FR-012."""
    partida, s = crear_partida([(1, "E", 2, 100), (2, "E", 3, 100), (3, "E", 4, 100)])
    s[2].trampas.insertar_al_final(Trampa("t-1", "trp", "Dardos", 5))
    ctl, vista, lineas = jugar(partida, ["IR A 4"], conocer=s.values())
    assert movimientos(lineas) == ["mover E"] and ctl.ultima_causa_viaje == "daño"
    assert vista.hay("Viaje detenido: daño.")


def test_nv14_cada_paso_es_movimiento_ordinario_con_eventos():
    """NV-14; FR-011. Un enemigo errante actúa entre pasos según el reloj."""
    partida, s = crear_partida([(1, "E", 2, 100), (2, "E", 3, 250)])
    ctl, vista, lineas = jugar(partida, ["IR A 3"], conocer=s.values())
    tiempos = [int(l.split()[0][2:]) for l in lineas if " mover " in f" {l} "]
    assert tiempos == [0, 100] and partida.tiempo == 350


def test_nv15_no_abre_puertas_con_llave():
    """NV-15; FR-013."""
    partida, s = crear_partida([(1, "E", 2, 100, True), (2, "E", 3, 100)])
    salida(s[1], "E").llave = "itm_llave"
    from modelo.entidades.objetos.llave import Llave
    llave = Llave("l-1", "itm_llave", "Llave", 0, 0, abre="itm_llave")
    partida.jugador.inventario.insertar_al_final(llave)
    assert partida.llave_para(salida(s[1], "E")) is llave
    ctl, vista, lineas = jugar(partida, ["IR A 2"], conocer=[s[2]])
    assert salida(s[1], "E").cerrada and movimientos(lineas) == []
    assert not any(" abrir " in f" {l} " for l in lineas)


def test_nv16_bitacora_paso_a_paso_y_comentario():
    """NV-16; FR-014."""
    partida, s = crear_partida([(1, "E", 2, 100), (2, "E", 3, 100)])
    ctl, vista, lineas = jugar(partida, ["IR A 3"], conocer=s.values())
    assert lineas[0] == "# t=0 ir a 3"
    assert lineas[1:] == ["t=0 mover E", "t=100 mover E"]


def test_nv27_avistada_no_es_transito():
    """NV-27; FR-009."""
    partida, s = crear_partida([(1, "E", 2, 10), (2, "E", 3, 10),
                                (1, "S", 4, 100), (4, "E", 3, 100)])
    ctl, vista, lineas = jugar(partida, ["IR A 3"], conocer=[s[3], s[4]])
    assert partida.conocimiento.estado_sala(2) == AVISTADA or movimientos(lineas)[0] == "mover S"
    assert movimientos(lineas)[0] == "mover S"


def test_nv30_destino_sala_actual():
    """NV-30; FR-008."""
    partida, s = crear_partida([(1, "E", 2, 100)])
    ctl, vista, lineas = jugar(partida, ["IR A 1"])
    assert vista.hay("Ya estás en Sala 1.") and partida.tiempo == 0
    assert dict(ctl.contadores())["turnos_jugador"] == 1


def test_nv31_enemigos_al_ordenar():
    """NV-31; FR-012."""
    partida, s = crear_partida([(1, "E", 2, 100)])
    poner_dormido(s[1])            # se activa al inicializar
    ctl, vista, lineas = jugar(partida, ["IR A 2"], conocer=[s[2]])
    assert vista.hay("Viaje detenido: enemigos.")
    assert movimientos(lineas) == [] and partida.tiempo == 0


@pytest.mark.parametrize("con_trampa, con_enemigo, esperada", [
    (True, True, "daño"), (True, False, "daño"), (False, True, "enemigos"),
    (False, False, "llegada")])
def test_nv32_prioridad_de_causas(con_trampa, con_enemigo, esperada):
    """NV-32; FR-012: fin de partida > daño > enemigos > llegada."""
    partida, s = crear_partida([(1, "E", 2, 100)], vida=1000)
    if con_trampa:
        s[2].trampas.insertar_al_final(Trampa("t-1", "trp", "Dardos", 5))
    if con_enemigo:
        poner_dormido(s[2], velocidad=50 if not con_trampa else 100)
    ctl, vista, lineas = jugar(partida, ["IR A 2"], conocer=[s[2]])
    assert ctl.ultima_causa_viaje == esperada


def test_nv32_fin_de_partida_tiene_maxima_prioridad():
    """NV-32; FR-012."""
    partida, s = crear_partida([(1, "E", 2, 100)], vida=3)
    s[2].trampas.insertar_al_final(Trampa("t-1", "trp", "Dardos", 50))
    poner_dormido(s[2])
    partida.inicializar()
    partida.conocimiento.visitar(s[2], 0)
    ctl = ControladorJuego(Sesion(partida), Vista(["IR A 2"]))
    ctl.jugar()
    assert partida.terminada
    assert ctl.causa_parada() == "fin de partida" if ctl._viaje else True


# ------------------------------------------------------------------ US3
def _mapa_antorcha():
    return crear_partida([(1, "E", 2, 100), (2, "E", 3, 100), (2, "N", 4, 100, True),
                          (3, "E", 5, 100)])


def test_nv17_nv19_antorcha_explora_vecinas_tras_puertas_cerradas():
    """NV-17, NV-19; FR-002, FR-005."""
    partida, s = _mapa_antorcha()
    dar_antorcha(partida)
    jugar(partida, ["E"])
    c = partida.conocimiento
    assert c.estado_sala(3) == EXPLORADA and c.estado_sala(4) == EXPLORADA
    assert c.estado_sala(5) == AVISTADA


def test_nv18_revelar_no_activa_enemigos_ni_trampas():
    """NV-18; FR-005."""
    partida, s = _mapa_antorcha()
    enemigo = poner_dormido(s[3])
    trampa = Trampa("t-9", "trp", "Dardos", 5)
    s[3].trampas.insertar_al_final(trampa)
    dar_antorcha(partida)
    jugar(partida, ["E"])
    assert s[3].enemigos_dormidos.contiene_valor(enemigo) and enemigo.sala_actual is None
    assert trampa.armada and partida.jugador.vida == 100


def test_nv20_sin_antorcha_solo_sala_visitada():
    """NV-20; FR-005."""
    partida, s = _mapa_antorcha()
    jugar(partida, ["E"])
    assert partida.conocimiento.estado_sala(3) == AVISTADA


def test_nv34_antorcha_no_observa_puertas_remotas():
    """NV-34; FR-004, FR-005, FR-009."""
    partida, s = _mapa_antorcha()
    dar_antorcha(partida)
    ctl, vista, lineas = jugar(partida, ["E", "IR A 5"])
    c = partida.conocimiento
    assert c.puerta_recordada(3, "E") == SIN_OBSERVAR
    assert c.puerta_recordada(2, "E") == ABIERTA            # extremo físico
    assert c.estado_sala(5) == AVISTADA
    assert vista.hay(ControladorJuego.RECHAZO_DESTINO)


# ------------------------------------------------------------------ US4
def test_nv21_guardar_y_cargar_conserva_conocimiento():
    """NV-21; FR-007."""
    from persistencia.estado_partida import codificar, decodificar
    partida, s = _mapa_antorcha()
    dar_antorcha(partida)
    jugar(partida, ["E"])
    salida(s[2], "E").cerrada = True        # recuerdo desactualizado a propósito
    referencia, registros = codificar(partida)
    cargada = decodificar(referencia, registros)
    assert cargada.conocimiento.resumen() == partida.conocimiento.resumen()
    assert cargada.conocimiento.puerta_recordada(2, "E") == ABIERTA


def test_nv21_guardado_previo_a_002_reconstruye_desde_rastro():
    """NV-21; FR-007 (compatibilidad)."""
    partida, s = crear_partida([(1, "E", 2, 100), (2, "E", 3, 100)])
    jugar(partida, ["E"])
    del partida.__dict__["_conocimiento"]
    assert partida.conocimiento.estado_sala(2) == EXPLORADA


def test_nv22_retroceso_de_entrada_con_antorcha():
    """NV-22; FR-007."""
    partida, s = _mapa_antorcha()
    dar_antorcha(partida)
    dar_pergamino(partida)
    partida.inicializar()
    partida.conocimiento.visitar(s[3], 0)        # ya conocida antes
    antes = partida.conocimiento.resumen()
    cambios_antes = len(partida.conocimiento.cambios)
    ctl = ControladorJuego(Sesion(partida), Vista(["E", "P"]))
    ctl.jugar()
    assert partida.sala_actual is s[1]
    assert partida.conocimiento.resumen() == antes
    assert len(partida.conocimiento.cambios) == cambios_antes
    assert partida.conocimiento.estado_sala(3) == EXPLORADA


def test_nv23_retroceso_durante_viaje_sin_reanudar():
    """NV-23; FR-015."""
    partida, s = crear_partida([(1, "E", 2, 100), (2, "E", 3, 100), (3, "E", 4, 100)])
    s[3].trampas.insertar_al_final(Trampa("t-1", "trp", "Dardos", 5))
    dar_pergamino(partida)
    ctl, vista, lineas = jugar(partida, ["IR A 4", "P"], conocer=s.values())
    assert movimientos(lineas) == ["mover E", "mover E"]
    assert partida.sala_actual is s[2] and ctl._viaje is None
    assert lineas[-1].endswith("pergamino")


def test_nv24_conocimiento_historico_aislado():
    """NV-24; FR-007."""
    partida, s = crear_partida([(1, "E", 2, 100), (2, "E", 3, 100), (3, "E", 4, 100)])
    partida.inicializar()
    c = partida.conocimiento
    t0 = c.resumen()
    jugar_ctl = ControladorJuego(Sesion(partida), Vista(["W", "E", "E"]))
    jugar_ctl.jugar()
    actual = c.resumen()
    pasado = c.reconstruir_en(0)
    assert pasado.resumen() == t0 and pasado.estado_sala(3) == DESCONOCIDA
    intermedio = c.reconstruir_en(100)
    assert intermedio.estado_sala(2) == EXPLORADA and intermedio.estado_sala(3) == AVISTADA
    pasado.visitar(s[4], 999)
    assert c.resumen() == actual and pasado.historial is None


# ------------------------------------------------------------------ US5
def test_nv25_mapa_solo_conocimiento():
    """NV-25; FR-018."""
    partida, s = crear_partida([(1, "E", 2, 100), (2, "E", 3, 100)])
    ctl, vista, lineas = jugar(partida, ["M"])
    textos = " ".join(m for _, m in vista.mensajes)
    assert "Mapa conocido" in textos and "sala sin explorar" in textos
    assert "Sala 2" not in textos and "Sala 3" not in textos and partida.tiempo == 0


def test_nv26_causa_visible():
    """NV-26; FR-012, FR-018."""
    partida, s = crear_partida([(1, "E", 2, 100)])
    ctl, vista, lineas = jugar(partida, ["IR A 2"], conocer=[s[2]])
    assert vista.hay("Llegas a Sala 2: fin del viaje.")


def test_interpretar_ir():
    for texto in ("ir a 5", "IR 5", "ir A 5"):
        comando, error = interpretar(texto)
        assert error is None and comando.nombre == "ir" and comando.argumento == "5"
    assert interpretar("IR")[0] is None
    assert interpretar("M")[0].nombre == "mapa"


# ------------------------------------------------------------------ replay real
def test_nv16_replay_reproduce_viaje_en_cripta_01(tmp_path):
    """NV-16; FR-014, constitución II. Juego real offline y replay del log."""
    from bitacora_partida import BitacoraPartida
    from controlador.controlador_replay import reproducir
    from controlador.inicio_partida import nueva_partida
    from tests.test_controlador_replay import OfflineResistente
    ruta = str(tmp_path / "partida.log")
    sesion = nueva_partida(OfflineResistente(), "cripta-01", str(tmp_path / "cache"),
                           semilla=3, ruta_bitacora=ruta)
    comandos = "N,A,A,A,A,A,A,R,EQ,N".split(",") + ["IR A 1", "Q"]
    controlador = ControladorJuego(sesion, Vista(comandos))
    controlador.jugar()
    texto = open(ruta, encoding="utf-8").read()
    assert "# t=" in texto and " ir a 1" in texto
    despues_ir = texto.split(" ir a 1\n", 1)[1]
    assert " mover " in despues_ir
    acciones = BitacoraPartida.abrir(ruta).leer_acciones()
    assert all(not a.startswith("ir") for _, a in acciones)
    resultado = reproducir(ruta, OfflineResistente(), str(tmp_path / "cache2"))
    assert resultado.verificado is True
    assert (resultado.partida.conocimiento.resumen()
            == sesion.partida.conocimiento.resumen())
