"""Integración de la línea de tiempo con Niebla y Terreno (FR-004, FR-010, FR-012)."""

from adaptadores.datos_offline import DatosOffline
from controlador.controlador_juego import ControladorJuego
from controlador.guardado import cargar
from controlador.inicio_partida import nueva_partida
from modelo.conocimiento import AVISTADA, EXPLORADA
from modelo.entidades.enemigo import Enemigo
from modelo.entidades.objetos.antorcha import Antorcha
from modelo.entidades.objetos.pergamino_retroceso import PergaminoRetroceso
from modelo.resumen_historico import ResumenHistorico
from tests.test_controlador_juego import VistaGuion


_COSTOS = {
    (1, "N"): 25,
    (2, "S"): 25,
    (2, "N"): 50,
    (3, "S"): 50,
    (3, "N"): 30,
    (4, "S"): 30,
    (2, "E"): 40,
    (5, "O"): 40,
    (4, "E"): 15,
    (6, "O"): 15,
}


class DatosLineaTiempo(DatosOffline):
    def esqueleto_cripta(self, cripta_id, pagina):
        datos = super().esqueleto_cripta(cripta_id, pagina)
        for sala in datos["salas"]:
            for direccion, salida in sala["salidas"].items():
                costo = _COSTOS.get((sala["id"], direccion))
                if costo is not None:
                    salida["costo"] = costo
        return datos

    def contenido_salas(self, cripta_id, sala_ids):
        respuesta = super().contenido_salas(cripta_id, sala_ids)
        for contenido in respuesta["contenido"]:
            contenido["enemigos"] = []
            contenido["objetos"] = []
            contenido["trampas"] = []
        return respuesta


class VistaConResumen(VistaGuion):
    def __init__(self, comandos, partida=None, capturar_eventos=()):
        super().__init__(comandos)
        self.resumenes_historicos = []
        self.partida = partida
        self.capturar_eventos = capturar_eventos
        self.estados_eventos = {}

    def mostrar_resumen_historico(self, resumen):
        self.resumenes_historicos.append(resumen)

    def agregar_mensaje(self, tiempo, texto):
        super().agregar_mensaje(tiempo, texto)
        if (self.partida is not None and tiempo in self.capturar_eventos
                and ("entra en la sala" in texto or "te ataca" in texto)):
            self.estados_eventos[tiempo] = ResumenHistorico.desde_partida(
                self.partida
            )


def _nueva_sesion(tmp_path, nombre):
    return nueva_partida(
        DatosLineaTiempo(),
        "cripta-01",
        str(tmp_path / nombre),
        semilla=2026,
        verificar=False,
    )


def _agregar_antorcha(sesion):
    antorcha = Antorcha(
        "antorcha-historia", "itm_antorcha", "Antorcha", 1, 1, 10000
    )
    antorcha.encendida = True
    sesion.partida.jugador.inventario.insertar_al_final(antorcha)
    return antorcha


def _agregar_pergamino(sesion):
    pergamino = PergaminoRetroceso(
        "pergamino-historia", "itm_pergamino_retroceso", "Pergamino", 0, 0
    )
    sesion.partida.jugador.inventario.insertar_al_final(pergamino)
    return pergamino


def _mapa(resumen):
    return tuple(
        (sala.sala_id, sala.estado, sala.tiempo_rastro)
        for sala in resumen.mapa_conocido
    )


def _resumen_en(vista, tiempo):
    return next(
        resumen for resumen in vista.resumenes_historicos
        if resumen.tiempo == tiempo
    )


def _firma(resumen):
    return (
        resumen.tiempo,
        resumen.sala_id,
        resumen.vida,
        tuple(
            (enemigo.instancia_id, enemigo.vida)
            for enemigo in resumen.enemigos
        ),
        _mapa(resumen),
    )


def test_historia_muestra_mapa_historico_y_salas_reveladas_por_antorcha(
    tmp_path,
):
    sesion = _nueva_sesion(tmp_path, "cache-mapa")
    _agregar_antorcha(sesion)
    vista = VistaConResumen(["N", "N", "historia 0", "historia 25", "Q"])

    ControladorJuego(sesion, vista, checkpoint_cada=1).jugar()

    inicial = _resumen_en(vista, 0)
    tras_primera_entrada = _resumen_en(vista, 25)
    assert _mapa(inicial) == (
        (1, EXPLORADA, 0),
        (2, AVISTADA, -1),
    )
    assert _mapa(tras_primera_entrada) == (
        (1, EXPLORADA, 0),
        (2, EXPLORADA, 0),
        (3, EXPLORADA, -1),
        (4, AVISTADA, -1),
        (5, EXPLORADA, -1),
    )
    assert sesion.partida.conocimiento.explorada(4)
    assert next(
        sala.estado for sala in tras_primera_entrada.mapa_conocido
        if sala.sala_id == 4
    ) == AVISTADA


def test_mapa_historico_persiste_tras_ir_a_guardar_cargar_y_pergamino(
    tmp_path,
):
    sesion = _nueva_sesion(tmp_path, "cache-guardar")
    _agregar_antorcha(sesion)
    _agregar_pergamino(sesion)
    ruta = tmp_path / "viaje.sav"
    vista_antes = VistaConResumen(["N", "IR A 3", f"G {ruta}", "Q"])
    ControladorJuego(sesion, vista_antes, checkpoint_cada=1).jugar()

    sesion_receptora = _nueva_sesion(tmp_path, "cache-cargar")
    restaurada = cargar(str(ruta), sesion_receptora)
    vista_despues = VistaConResumen(
        ["historia 0", "historia 25", "historia 75", "P", "historia 25", "Q"]
    )
    ControladorJuego(restaurada, vista_despues).jugar()

    assert _mapa(_resumen_en(vista_despues, 0)) == (
        (1, EXPLORADA, 0),
        (2, AVISTADA, -1),
    )
    assert _mapa(_resumen_en(vista_despues, 25)) == (
        (1, EXPLORADA, 0),
        (2, EXPLORADA, 0),
        (3, EXPLORADA, -1),
        (4, AVISTADA, -1),
        (5, EXPLORADA, -1),
    )
    assert _mapa(_resumen_en(vista_despues, 75)) == (
        (1, EXPLORADA, 0),
        (2, EXPLORADA, 0),
        (3, EXPLORADA, 25),
        (4, EXPLORADA, -1),
        (5, EXPLORADA, -1),
        (6, AVISTADA, -1),
    )
    assert restaurada.partida.tiempo == 25
    assert restaurada.partida.acciones_jugador == 1
    assert restaurada.partida.conocimiento.estado_sala(4) == AVISTADA
    assert restaurada.partida.conocimiento.estado_sala(6) != EXPLORADA
    assert _mapa(_resumen_en(vista_despues, 25)) == _mapa(
        vista_despues.resumenes_historicos[-1]
    )


def test_reconstruccion_conserva_costos_de_movimiento_y_acciones_de_cazador(
    tmp_path,
):
    sesion = _nueva_sesion(tmp_path, "cache-cazador")
    partida = sesion.partida
    sala_cazador = partida.cripta.sala_por_id(4)
    cazador = Enemigo(
        "cazador-historia",
        "cazador-historia",
        "Cazador",
        100,
        1,
        0,
        100,
        "cazador",
        sala_cazador,
        rango=200,
    )
    sala_cazador.enemigos_dormidos.insertar_al_final(cazador)
    partida.activar_enemigos(sala_cazador)
    vista = VistaConResumen(
        ["N", "N", "W", "historia 100", "historia 130", "Q"],
        partida=partida,
        capturar_eventos=(100, 130),
    )

    ControladorJuego(sesion, vista, checkpoint_cada=100).jugar()

    acciones = sesion.partida.historia.acciones
    assert tuple(
        (acciones.obtenerValor(i).tiempo, acciones.obtenerValor(i).datos[2])
        for i in range(len(acciones))
    ) == ((0, 25), (25, 50), (75, 100))
    assert 100 in vista.estados_eventos
    assert 130 in vista.estados_eventos
    assert _firma(_resumen_en(vista, 100)) == _firma(vista.estados_eventos[100])
    assert _firma(_resumen_en(vista, 130)) == _firma(vista.estados_eventos[130])
    assert any(
        enemigo.instancia_id == cazador.instancia_id
        for enemigo in _resumen_en(vista, 100).enemigos
    )
