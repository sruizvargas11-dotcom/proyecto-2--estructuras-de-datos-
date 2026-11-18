"""Pruebas de captura y restauracion de puntos de control."""

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
