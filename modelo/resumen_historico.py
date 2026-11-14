"""Datos independientes para presentar un estado historico."""

from estructuras.vector_dinamico import Vector


class ObjetoHistorico:
    def __init__(self, instancia_id, nombre, clase):
        self.instancia_id = instancia_id
        self.nombre = nombre
        self.clase = clase


class EfectoHistorico:
    def __init__(self, tipo, dano_por_pulso=None, pulsos_restantes=None,
                 parametro=None, tiempo_fin=None, instancia_id=None):
        self.tipo = tipo
        self.dano_por_pulso = dano_por_pulso
        self.pulsos_restantes = pulsos_restantes
        self.parametro = parametro
        self.tiempo_fin = tiempo_fin
        self.instancia_id = instancia_id


class EnemigoHistorico:
    def __init__(self, instancia_id, nombre, vida, vida_max):
        self.instancia_id = instancia_id
        self.nombre = nombre
        self.vida = vida
        self.vida_max = vida_max


class SalaConocidaHistorica:
    def __init__(self, sala_id, nombre, tiempo_rastro):
        self.sala_id = sala_id
        self.nombre = nombre
        self.tiempo_rastro = tiempo_rastro


class ResumenHistorico:
    """Copia como datos los campos requeridos para una consulta historica."""

    def __init__(self, tiempo, sala_id, sala_nombre, vida, vida_max, ataque,
                 defensa, velocidad, inventario, efectos_activos, enemigos,
                 mapa_conocido):
        self.tiempo = tiempo
        self.sala_id = sala_id
        self.sala_nombre = sala_nombre
        self.vida = vida
        self.vida_max = vida_max
        self.ataque = ataque
        self.defensa = defensa
        self.velocidad = velocidad
        self.inventario = inventario
        self.efectos_activos = efectos_activos
        self.enemigos = enemigos
        self.mapa_conocido = mapa_conocido

    @classmethod
    def desde_partida(cls, partida):
        jugador = partida.jugador
        sala = jugador.sala_actual

        inventario = Vector()
        efectos = Vector()
        for nodo in jugador.inventario.recorrer_desde_frente():
            objeto = nodo.valor
            inventario.agregarValor(
                ObjetoHistorico(
                    objeto.instancia_id,
                    objeto.nombre,
                    objeto.clase,
                )
            )
            if getattr(objeto, "encendida", False):
                apagado = getattr(objeto, "evento_apagado", None)
                efectos.agregarValor(
                    EfectoHistorico(
                        "antorcha",
                        tiempo_fin=getattr(apagado, "tiempo", None),
                        instancia_id=objeto.instancia_id,
                    )
                )

        veneno = jugador.estado_veneno
        if veneno is not None:
            efectos.agregarValor(
                EfectoHistorico(
                    "veneno",
                    veneno.dano_por_pulso,
                    veneno.pulsos_restantes,
                )
            )
        for nodo in jugador.eventos_efectos.recorrer_desde_frente():
            entrada = nodo.valor
            if not entrada.valido or not entrada._en_heap:
                continue
            evento = entrada.dato
            if evento.tipo == "velocidad":
                efectos.agregarValor(
                    EfectoHistorico(
                        "velocidad",
                        parametro=evento.parametro,
                        tiempo_fin=entrada.tiempo,
                    )
                )

        enemigos = Vector()
        for enemigo in sala.enemigos_activos.recorrer_valores():
            enemigos.agregarValor(
                EnemigoHistorico(
                    enemigo.instancia_id,
                    enemigo.nombre,
                    enemigo.vida,
                    enemigo.vida_max,
                )
            )
        for enemigo in sala.enemigos_dormidos.recorrer_valores():
            enemigos.agregarValor(
                EnemigoHistorico(
                    enemigo.instancia_id,
                    enemigo.nombre,
                    enemigo.vida,
                    enemigo.vida_max,
                )
            )

        mapa_conocido = Vector()
        for sala_conocida in partida.cripta.recorrer_salas():
            if sala_conocida.tiempo_rastro >= 0:
                mapa_conocido.agregarValor(
                    SalaConocidaHistorica(
                        sala_conocida.id,
                        sala_conocida.nombre,
                        sala_conocida.tiempo_rastro,
                    )
                )

        return cls(
            partida.tiempo,
            sala.id,
            sala.nombre,
            jugador.vida,
            jugador.vida_max,
            jugador.ataque,
            jugador.defensa,
            jugador.velocidad,
            inventario,
            efectos,
            enemigos,
            mapa_conocido,
        )
