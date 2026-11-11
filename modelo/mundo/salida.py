"""Salida de una sala a otra."""


class Salida:
    def __init__(
        self,
        direccion,
        sala_destino_id,
        cerrada=False,
        llave=None,
        cierre_automatico=None,
        costo=100,
    ):
        if type(costo) is not int or costo < 1:
            raise ValueError("El costo de una salida debe ser un entero >= 1.")
        self.direccion = direccion
        self.sala_destino_id = sala_destino_id

        # Se enlaza con la instancia de Sala al finalizar la carga.
        self.sala_destino = None

        self.cerrada = cerrada
        self.llave = llave
        self.cierre_automatico = cierre_automatico
        self.evento_cierre = None
        self.costo = costo
