"""Pruebas unitarias de aislamiento y truncamiento del modelo."""

from types import SimpleNamespace

from adaptadores.datos_offline import DatosOffline
from controlador.inicio_partida import nueva_partida
from modelo.historia import Historia
from modelo.punto_control import PuntoControl
from modelo.reconstructor_historia import ReconstructorHistoria


def _firma_cache(cache):
    entradas = tuple(
        (nodo.valor.id_ficha, nodo.valor.en_uso)
        for nodo in cache._lista.recorrer_desde_frente()
    )
    return entradas, cache.contadores(), cache.contadores_operaciones()


def _firma_partida(partida):
    agenda = partida.reloj.agenda
    return (
        partida.tiempo,
        partida.estado,
        partida.jugador.vida,
        partida.jugador.sala_actual.id,
        partida.acciones_jugador,
        partida.reloj.azar.getstate(),
        tuple(
            (entrada.tiempo, entrada.secuencia, entrada.dato.tipo, entrada.valido)
            for entrada in agenda._datos
        ),
        len(partida.historial),
        partida.historial.contadores(),
        tuple(
            nodo.valor.instancia_id
            for nodo in partida.jugador.inventario.recorrer_desde_frente()
        ),
    )


def test_reconstruccion_no_altera_estado_pergamino_ni_cache(tmp_path):
    """Verifica que reconstruir solo altere el estado temporal (FR-006, FR-007)."""
    sesion = nueva_partida(
        DatosOffline(),
        "cripta-01",
        str(tmp_path / "cache"),
        semilla=2026,
    )
    partida = sesion.partida
    pergamino = SimpleNamespace(
        clase="pergamino_retroceso",
        instancia_id="pergamino-prueba",
    )
    partida.jugador.inventario.insertar_al_final(pergamino)
    partida.historial.iniciar_accion(partida.reloj)
    partida.jugador.recibir_dano(1)
    partida.historial.confirmar_accion()
    partida.acciones_jugador = 1

    cache = sesion.red._fichas
    cache.insertar("ficha-prueba", SimpleNamespace(id="ficha-prueba"))
    resolver_original = partida._resolver_ficha
    firma_partida_antes = _firma_partida(partida)
    firma_cache_antes = _firma_cache(cache)

    punto = PuntoControl.capturar(partida, numero_accion=0)
    historia = Historia(2)
    historia.registrar_accion(10, ("consulta",))

    def aplicar(temporal, accion):
        temporal.jugador.vida -= 2
        temporal.reloj.tiempo_actual = accion.tiempo

    temporal = ReconstructorHistoria.reconstruir(
        punto,
        historia.acciones,
        hasta_accion=1,
        aplicar_accion=aplicar,
    )

    assert temporal is not partida
    assert temporal._resolver_ficha is None
    assert temporal.jugador.buscar_nodo(pergamino.instancia_id) is None
    assert temporal.jugador.vida == partida.jugador.vida - 2
    assert temporal.tiempo == 10
    assert _firma_partida(partida) == firma_partida_antes
    assert _firma_cache(cache) == firma_cache_antes
    assert partida._resolver_ficha is resolver_original


class CambioPrueba:
    def __init__(self):
        self.reversiones = 0

    def revertir(self):
        self.reversiones += 1


def test_truncar_despues_de_m_elimina_cambios_y_puntos_posteriores():
    """Verifica el corte de historia y controles posteriores a m (FR-008)."""
    historia = Historia(2)
    cambios = []
    for numero in range(1, 7):
        historia.registrar_accion(numero * 10, ("esperar", numero))
        cambio = CambioPrueba()
        cambios.append(cambio)
        historia.registrar_cambio(numero, cambio)
        if numero % historia.k == 0:
            historia.registrar_punto_control(numero * 10, numero)

    historia.truncar(3)

    assert [accion.numero for accion in historia.acciones] == [1, 2, 3]
    assert [cambio.numero_accion for cambio in historia.cambios] == [1, 2, 3]
    assert [punto.numero_accion for punto in historia.puntos_control] == [0, 2]
    assert [cambio.reversiones for cambio in cambios] == [0, 0, 0, 1, 1, 1]
