"""Registros vigentes de acciones, cambios y puntos de control."""

from estructuras.vector_dinamico import Vector


def _entero_positivo(valor, nombre, minimo=0):
    if type(valor) is not int or valor < minimo:
        raise ValueError(f"{nombre} debe ser un entero >= {minimo}.")
    return valor


class RegistroAccion:
    def __init__(self, numero, tiempo, datos):
        self.numero = numero
        self.tiempo = tiempo
        self.datos = datos


class MetadatoPuntoControl:
    def __init__(self, tiempo, numero_accion):
        self.tiempo = tiempo
        self.numero_accion = numero_accion


class RegistroCambio:
    def __init__(self, numero_accion, cambio):
        self.numero_accion = numero_accion
        self.cambio = cambio

    def revertir(self):
        self.cambio.revertir()


class Historia:
    """Arreglos ordenados de la linea vigente; K es un intervalo positivo."""

    def __init__(self, k):
        _entero_positivo(k, "K", 1)
        self.k = k
        self.acciones = Vector()
        self.puntos_control = Vector()
        self.cambios = Vector()
        self.puntos_control.agregarValor(MetadatoPuntoControl(0, 0))

    def registrar_accion(self, tiempo, datos):
        _entero_positivo(tiempo, "tiempo")
        if len(self.acciones) and tiempo < self.acciones.obtenerValor(
                len(self.acciones) - 1).tiempo:
            raise ValueError("Las acciones deben registrarse en orden de tiempo.")
        registro = RegistroAccion(len(self.acciones) + 1, tiempo, datos)
        self.acciones.agregarValor(registro)
        return registro

    def registrar_punto_control(self, tiempo, numero_accion):
        _entero_positivo(tiempo, "tiempo")
        _entero_positivo(numero_accion, "numero_accion")
        if numero_accion > len(self.acciones):
            raise ValueError("El punto de control excede las acciones vigentes.")
        anterior = self.puntos_control.obtenerValor(len(self.puntos_control) - 1)
        if tiempo <= anterior.tiempo or numero_accion <= anterior.numero_accion:
            raise ValueError("Los puntos de control deben aumentar en tiempo y accion.")
        punto = MetadatoPuntoControl(tiempo, numero_accion)
        self.puntos_control.agregarValor(punto)
        return punto

    def registrar_cambio(self, numero_accion, cambio):
        _entero_positivo(numero_accion, "numero_accion", 1)
        if numero_accion > len(self.acciones):
            raise ValueError("El cambio debe pertenecer a una accion vigente.")
        if not callable(getattr(cambio, "revertir", None)):
            raise TypeError("El cambio debe implementar revertir().")
        registro = RegistroCambio(numero_accion, cambio)
        self.cambios.agregarValor(registro)
        return registro

    def truncar(self, numero_accion):
        """Conserva las primeras N acciones e invierte/elimina lo posterior."""
        _entero_positivo(numero_accion, "numero_accion")
        if numero_accion > len(self.acciones):
            raise ValueError("No se puede truncar mas alla de las acciones vigentes.")

        while len(self.cambios):
            registro = self.cambios.obtenerValor(len(self.cambios) - 1)
            if registro.numero_accion <= numero_accion:
                break
            registro.revertir()
            self.cambios.eliminarUltimo()

        while len(self.acciones) > numero_accion:
            self.acciones.eliminarUltimo()
        while (len(self.puntos_control) > 1
               and self.puntos_control.obtenerValor(
                   len(self.puntos_control) - 1
               ).numero_accion > numero_accion):
            self.puntos_control.eliminarUltimo()
