"""Reconstruccion de una copia temporal desde un punto de control."""


def _validar_indice(valor, nombre):
    if type(valor) is not int or valor < 0:
        raise ValueError(f"{nombre} debe ser un entero no negativo.")


class ReconstructorHistoria:
    @staticmethod
    def reconstruir(punto_control, acciones=None, hasta_accion=None,
                    aplicar_accion=None):
        temporal = punto_control.restaurar()
        if acciones is None:
            if hasta_accion is not None or aplicar_accion is not None:
                raise ValueError("Se requieren acciones para avanzar desde el punto.")
            return temporal

        if not callable(getattr(acciones, "obtenerValor", None)):
            raise TypeError("Las acciones deben almacenarse en un Vector.")
        if hasta_accion is None:
            hasta_accion = len(acciones)
        _validar_indice(hasta_accion, "hasta_accion")
        inicio = punto_control.numero_accion
        if inicio > len(acciones) or hasta_accion < inicio:
            raise ValueError("El intervalo solicitado no parte del punto de control.")
        if hasta_accion > len(acciones):
            raise ValueError("La accion solicitada no existe.")
        if hasta_accion > inicio and not callable(aplicar_accion):
            raise TypeError("Se necesita aplicar_accion para avanzar la reconstruccion.")

        for indice in range(inicio, hasta_accion):
            aplicar_accion(temporal, acciones.obtenerValor(indice))
        return temporal
