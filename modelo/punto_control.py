"""Captura aislada de un estado de partida restaurable."""

from copy import deepcopy

from estructuras.vector_dinamico import Vector
from modelo.historial import Historial

_CALLBACKS = (
    "al_morir_enemigo",
    "al_entrar_sala",
    "al_mensaje",
    "al_mover_enemigo",
    "al_activar_trampa",
    "al_atacar",
)


def _validar_entero(valor, nombre):
    if type(valor) is not int or valor < 0:
        raise ValueError(f"{nombre} debe ser un entero no negativo.")


def _vaciar(vector):
    while len(vector):
        vector.eliminarUltimo()


def _excluir_pergaminos(jugador):
    inventario = jugador.inventario
    nodo = inventario.head()
    while nodo is not None:
        siguiente = nodo.siguiente
        if getattr(nodo.valor, "clase", None) == "pergamino_retroceso":
            inventario.eliminar_nodo(nodo)
        nodo = siguiente
    if not inventario.pertenece(jugador.cursor):
        jugador.cursor = inventario.head()


def _preparar_copia(partida, incluir_historial=True):
    historial = Historial() if incluir_historial else None
    partida.historial = historial
    partida.reloj.historial = historial
    partida.rastro.historial = historial
    partida._resolver_ficha = None
    for nombre in _CALLBACKS:
        _vaciar(getattr(partida, nombre))
    _excluir_pergaminos(partida.jugador)


def _copiar_sin_auxiliares(partida):
    historial = partida.historial
    reloj_historial = partida.reloj.historial
    rastro_historial = partida.rastro.historial
    resolver_ficha = partida._resolver_ficha
    callbacks = Vector()
    for nombre in _CALLBACKS:
        callbacks.agregarValor((nombre, getattr(partida, nombre)))

    inventario = partida.jugador.inventario
    contadores_inventario = (
        inventario.contador_inserciones,
        inventario.contador_eliminaciones,
    )
    pergaminos = Vector()
    try:
        nodo = inventario._head
        while nodo is not None:
            siguiente = nodo.siguiente
            if getattr(nodo.valor, "clase", None) == "pergamino_retroceso":
                pergaminos.agregarValor((nodo, nodo.anterior, nodo.siguiente))
                inventario.eliminar_nodo(nodo)
            nodo = siguiente

        partida.historial = None
        partida.reloj.historial = None
        partida.rastro.historial = None
        partida._resolver_ficha = None
        for nombre, _ in callbacks:
            setattr(partida, nombre, Vector())
        estado = deepcopy(partida)
        _preparar_copia(estado, incluir_historial=False)
        return estado
    finally:
        for indice in range(len(pergaminos) - 1, -1, -1):
            pergamino, anterior, siguiente = pergaminos.obtenerValor(indice)
            inventario.restaurar_nodo(pergamino, anterior, siguiente)
        inventario.contador_inserciones = contadores_inventario[0]
        inventario.contador_eliminaciones = contadores_inventario[1]
        partida.historial = historial
        partida.reloj.historial = reloj_historial
        partida.rastro.historial = rastro_historial
        partida._resolver_ficha = resolver_ficha
        for nombre, callback in callbacks:
            setattr(partida, nombre, callback)


class PuntoControl:
    def __init__(self, tiempo, numero_accion, estado):
        _validar_entero(tiempo, "tiempo")
        _validar_entero(numero_accion, "numero_accion")
        self.tiempo = tiempo
        self.numero_accion = numero_accion
        self._estado = estado

    @classmethod
    def capturar(cls, partida, numero_accion=None):
        if numero_accion is None:
            numero_accion = getattr(partida, "acciones_jugador", 0)
        _validar_entero(numero_accion, "numero_accion")
        estado = _copiar_sin_auxiliares(partida)
        return cls(partida.tiempo, numero_accion, estado)

    def restaurar(self):
        """Devuelve una instancia fresca sin historial ni pergaminos copiados."""
        estado = deepcopy(self._estado)
        _preparar_copia(estado)
        return estado
