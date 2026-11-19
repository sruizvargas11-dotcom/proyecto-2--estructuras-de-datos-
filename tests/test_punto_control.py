"""Pruebas de captura y restauracion de puntos de control."""

from copy import deepcopy

from modelo.mundo.cripta_modelo import CriptaModelo
from modelo.mundo.sala import Sala
from modelo.mundo.salida import Salida
from modelo.conocimiento import ConocimientoJugador
from modelo.punto_control import PuntoControl
from tests.fixtures.linea_tiempo import crear_partida_determinista


class PergaminoPrueba:
    clase = "pergamino_retroceso"
    instancia_id = "pergamino-prueba"


def _eventos(partida):
    return tuple(
        (entrada.tiempo, entrada.secuencia, entrada.dato.tipo)
        for entrada in partida.reloj.agenda.vista_ordenada(
            len(partida.reloj.agenda)
        )
    )


def test_punto_control_restaura_estado_aleatorio_agenda_y_mapa(tmp_path):
    """Verifica que se captura el estado requerido y no la historia del pergamino (FR-009, FR-012)."""
    partida = crear_partida_determinista(carpeta_cache=tmp_path / "cache")
    partida.jugador.inventario.insertar_al_final(PergaminoPrueba())
    estado_azar = partida.reloj.azar.getstate()
    eventos = _eventos(partida)
    marcas = tuple(
        (sala.id, sala.tiempo_rastro)
        for sala in partida.cripta.recorrer_salas()
    )

    punto = PuntoControl.capturar(partida)
    restaurada = punto.restaurar()

    assert restaurada is not partida
    assert restaurada.tiempo == partida.tiempo
    assert restaurada.reloj.azar.getstate() == estado_azar
    assert _eventos(restaurada) == eventos
    assert tuple(
        (sala.id, sala.tiempo_rastro)
        for sala in restaurada.cripta.recorrer_salas()
    ) == marcas
    assert restaurada.historial is not partida.historial
    assert len(restaurada.historial) == 0
    assert all(
        nodo.valor.clase != "pergamino_retroceso"
        for nodo in restaurada.jugador.inventario.recorrer_desde_frente()
    )
    assert len(partida.jugador.inventario) == 1
    assert partida.jugador.inventario.head().valor.clase == "pergamino_retroceso"


def test_restauraciones_son_independientes_entre_si(tmp_path):
    """Verifica que mutar una copia restaurada no cambia el punto ni la partida (FR-009, FR-012)."""
    partida = crear_partida_determinista(carpeta_cache=tmp_path / "cache")
    vida_inicial = partida.jugador.vida
    punto = PuntoControl.capturar(partida)

    primera = punto.restaurar()
    primera.jugador.vida = 1
    segunda = punto.restaurar()

    assert partida.jugador.vida == vida_inicial
    assert segunda.jugador.vida == vida_inicial


def test_copiar_cripta_extensa_conserva_enlaces_sin_recursion():
    """Un mapa extenso debe poder copiarse para los checkpoints de partida."""
    cantidad = 1500
    cripta = CriptaModelo("larga", "v1", 0, cantidad - 1, None, 0, 10)
    salas = [Sala(indice, f"Sala {indice}") for indice in range(cantidad)]
    for indice, sala in enumerate(salas):
        cripta.agregar_sala(sala)
        if indice + 1 < cantidad:
            sala.salidas.insertar_al_final(
                Salida("este", indice + 1, costo=1)
            )
    cripta.finalizar_carga()

    copia = deepcopy(cripta)
    conocimiento = ConocimientoJugador(cripta)
    conocimiento_copiado = deepcopy(conocimiento)

    assert copia is not cripta
    assert len(copia) == cantidad
    assert copia.sala_por_id(0) is not salas[0]
    assert conocimiento_copiado is not conocimiento
    assert len(conocimiento_copiado.registros) == cantidad
    for indice, sala_copiada in enumerate(copia.recorrer_salas()):
        assert sala_copiada.cripta is copia
        registro = conocimiento_copiado.registro(indice)
        assert registro.sala is not salas[indice]
        assert registro.sala.cripta is conocimiento_copiado.registro(0).sala.cripta
        if indice + 1 < cantidad:
            salida = next(sala_copiada.salidas.recorrer_valores())
            assert salida.cripta is copia
            assert salida.sala_destino is copia.sala_por_id(indice + 1)
            vecinos = copia.adjacencia_individual().obtenerValor(indice)
            assert vecinos.obtenerValor(0)[1] is salida
            recuerdo = registro.recuerdos.obtenerValor(0)
            assert recuerdo.destino is conocimiento_copiado.registro(indice + 1)


def test_punto_control_copia_una_cripta_de_256_salas_con_cazadores():
    from bench.terreno_cazador import _crear_partida, _fixture

    datos, _ = _fixture()
    partida, _ = _crear_partida(datos, [1000, 10000])
    restaurada = PuntoControl.capturar(partida).restaurar()

    assert len(restaurada.cripta) == 256
    assert restaurada.cripta is not partida.cripta
    sala = restaurada.jugador.sala_actual
    assert sala is restaurada.cripta.sala_por_id(sala.id)
    assert restaurada.conocimiento.registro(sala.id).sala is sala
    for registro in restaurada.conocimiento.registros:
        for recuerdo in registro.recuerdos:
            assert recuerdo.origen is registro
            assert any(salida is recuerdo.salida for salida in registro.sala.salidas)
            assert recuerdo.destino is restaurada.conocimiento.registro(recuerdo.destino_id)
            if recuerdo.destino is not None:
                assert any(entrante is recuerdo for entrante in recuerdo.destino.entrantes)
    assert restaurada.reloj.proximo().dato.dueno is restaurada.jugador
