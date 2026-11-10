"""Constructores deterministas para las pruebas de la linea de tiempo."""

from adaptadores.datos_offline import DatosOffline
from controlador.inicio_partida import nueva_partida


class RegistroAccionFixture:
    def __init__(self, numero, tiempo, datos):
        self.numero = numero
        self.tiempo = tiempo
        self.datos = datos


class PuntoControlFixture:
    def __init__(self, tiempo, numero_accion):
        self.tiempo = tiempo
        self.numero_accion = numero_accion


class HistoriaFixture:
    def __init__(self, acciones, puntos_control):
        self.acciones = tuple(acciones)
        self.puntos_control = tuple(puntos_control)


def crear_partida_determinista(semilla=2026, carpeta_cache=None):
    """Crea una partida inicializada sin solicitudes de red."""
    if carpeta_cache is None:
        raise ValueError("carpeta_cache es obligatoria para aislar los datos.")
    return nueva_partida(
        DatosOffline(),
        "cripta-01",
        str(carpeta_cache),
        semilla=semilla,
    ).partida


def crear_historia_determinista(cantidad_acciones=8, k=4):
    """Crea registros sinteticos estables, con puntos cada K acciones."""
    if type(cantidad_acciones) is not int or cantidad_acciones < 0:
        raise ValueError("cantidad_acciones debe ser un entero no negativo.")
    if type(k) is not int or k <= 0:
        raise ValueError("k debe ser un entero positivo.")
    acciones = []
    puntos_control = [PuntoControlFixture(0, 0)]
    for numero in range(1, cantidad_acciones + 1):
        acciones.append(
            RegistroAccionFixture(numero, numero * 100, ("esperar", numero))
        )
        if numero % k == 0:
            puntos_control.append(PuntoControlFixture(numero * 100, numero))
    return HistoriaFixture(acciones, puntos_control)
