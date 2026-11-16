"""Reconstruccion de una copia temporal desde un punto de control."""

from modelo import efectos


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

    @staticmethod
    def aplicar_accion(temporal, accion):
        """Reproduce una acción registrada sobre la copia temporal."""
        datos = accion.datos
        if not isinstance(datos, tuple) or len(datos) != 3:
            raise ValueError("La acción histórica no contiene sus datos de replay.")
        nombre, argumento, costo = datos
        ReconstructorHistoria.avanzar_hasta_decision(
            temporal, accion.tiempo
        )

        historial = temporal.historial
        if historial.registrando:
            historial.confirmar_accion()
        historial.iniciar_accion(temporal.reloj)
        temporal.reloj.tomar_turno(temporal.jugador)
        jugador = temporal.jugador
        sala = jugador.sala_actual

        if nombre == "mover":
            salida = sala.salida_hacia(argumento)
            if salida is None:
                raise ValueError("No se puede reproducir un movimiento histórico.")
            destino = temporal.cripta.sala_por_id(salida.sala_destino_id)
            if destino is None:
                raise ValueError("Falta una sala para reproducir un movimiento.")
            temporal.entrar_a_sala(destino)
        elif nombre == "atacar":
            enemigo = _elemento(sala.enemigos_activos, argumento)
            if enemigo is None:
                raise ValueError("Falta el enemigo de una acción histórica.")
            temporal.atacar(enemigo)
        elif nombre == "esperar":
            pass
        elif nombre == "recoger":
            objeto = _elemento(sala.objetos_suelo, argumento)
            if objeto is None or not jugador.recoger(objeto):
                raise ValueError("Falta el objeto de una acción histórica.")
        elif nombre == "soltar":
            nodo = _nodo_inventario(jugador, argumento)
            if nodo is None:
                raise ValueError("Falta el objeto de una acción histórica.")
            jugador.soltar_nodo(nodo)
        elif nombre == "equipar":
            nodo = _nodo_inventario(jugador, argumento)
            if nodo is None or not jugador.equipar_nodo(nodo):
                raise ValueError("No se puede reproducir el equipo histórico.")
        elif nombre == "desequipar":
            nodo = _nodo_inventario(jugador, argumento)
            if nodo is None or not jugador.desequipar_nodo(nodo):
                raise ValueError("No se puede reproducir el equipo histórico.")
        elif nombre == "apagar":
            nodo = _nodo_inventario(jugador, argumento)
            if nodo is None or not efectos.apagar_antorcha(
                    temporal.reloj, nodo.valor):
                raise ValueError("No se puede reproducir el efecto histórico.")
        elif nombre == "usar":
            nodo = _nodo_inventario(jugador, argumento)
            if nodo is None or not temporal.usar_objeto(nodo):
                raise ValueError("No se puede reproducir el objeto histórico.")
        elif nombre == "abrir":
            salida = sala.salida_hacia(argumento)
            if salida is None or not temporal.abrir(salida):
                raise ValueError("No se puede reproducir la puerta histórica.")
        else:
            raise ValueError(f"Acción histórica desconocida: {nombre}.")

        temporal.contar_accion_jugador()
        if nombre != "mover":
            temporal.refrescar_rastro()
        if not temporal.terminada and jugador.vivo:
            temporal.programar_siguiente_jugador(costo)

    @staticmethod
    def avanzar_hasta_decision(temporal, tiempo):
        entrada = temporal.reloj.avanzar_hasta_turno(temporal.jugador)
        if entrada is None or entrada.tiempo != tiempo:
            raise ValueError(
                "La línea histórica no coincide con el tiempo de la acción."
            )
        return entrada

    @staticmethod
    def avanzar_hasta_tiempo(temporal, tiempo):
        reloj = temporal.reloj
        while True:
            entrada = reloj.proximo()
            if entrada is None or entrada.tiempo > tiempo:
                reloj.tiempo_actual = tiempo
                return
            evento = entrada.dato
            if (evento.tipo == "accion"
                    and evento.dueno is temporal.jugador):
                if entrada.tiempo < tiempo:
                    raise ValueError(
                        "Falta una acción registrada antes del instante solicitado."
                    )
                reloj.tiempo_actual = tiempo
                return
            if evento.tipo == "accion":
                reloj.extraer_siguiente(entrada)
                temporal.ejecutar_accion_enemigo(evento.dueno)
                temporal.programar_siguiente_enemigo(evento.dueno)
            else:
                reloj.extraer_siguiente(entrada)
                reloj.ejecutar_evento(entrada)
                temporal.verificar_fin()


def _elemento(iterable, numero):
    indice = 1
    for valor in iterable:
        if indice == numero:
            return valor
        indice += 1
    return None


def _nodo_inventario(jugador, numero):
    indice = 1
    for nodo in jugador.inventario.recorrer_desde_frente():
        if indice == numero:
            return nodo
        indice += 1
    return None
