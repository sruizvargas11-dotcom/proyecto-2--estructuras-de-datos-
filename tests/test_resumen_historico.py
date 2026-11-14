"""Pruebas del resumen historico como datos del modelo."""

from types import SimpleNamespace

from modelo.efectos import EstadoVeneno
from modelo.entidades.enemigo import Enemigo
from modelo.resumen_historico import ResumenHistorico
from tests.fixtures.linea_tiempo import crear_partida_determinista


def test_resumen_historico_incluye_campos_de_fr004(tmp_path):
    """Verifica tiempo, jugador, inventario, efectos, enemigos y mapa (FR-004)."""
    partida = crear_partida_determinista(carpeta_cache=tmp_path / "cache")
    jugador = partida.jugador
    sala = jugador.sala_actual
    jugador.inventario.insertar_al_final(
        SimpleNamespace(instancia_id="obj-1", nombre="Pocion", clase="pocion")
    )
    jugador.estado_veneno = EstadoVeneno(2, 3)
    enemigo = Enemigo(
        "e-resumen", "tipo-resumen", "Guardián", 10, 4, 1, 100,
        "guardián", sala, vida=7,
    )
    sala.enemigos_activos.insertar_al_final(enemigo)
    sala_conocida = partida.cripta.sala_por_id(2)
    sala_conocida.tiempo_rastro = 15

    resumen = ResumenHistorico.desde_partida(partida)

    assert resumen.tiempo == partida.tiempo
    assert resumen.sala_id == sala.id
    assert resumen.sala_nombre == sala.nombre
    assert (resumen.vida, resumen.vida_max) == (jugador.vida, jugador.vida_max)
    assert (resumen.ataque, resumen.defensa, resumen.velocidad) == (
        jugador.ataque, jugador.defensa, jugador.velocidad
    )
    assert any(objeto.instancia_id == "obj-1" for objeto in resumen.inventario)
    assert any(efecto.tipo == "veneno" for efecto in resumen.efectos_activos)
    assert any(
        registro.instancia_id == enemigo.instancia_id
        and registro.vida == enemigo.vida
        for registro in resumen.enemigos
    )
    assert any(
        registro.sala_id == sala_conocida.id
        and registro.tiempo_rastro == sala_conocida.tiempo_rastro
        for registro in resumen.mapa_conocido
    )
