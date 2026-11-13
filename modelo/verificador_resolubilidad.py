"""Verificación determinista de alcanzabilidad de una cripta."""

from dataclasses import dataclass

from estructuras.cola import Cola
from estructuras.ordenamientos import ordenar
from estructuras.tabla_hash import TablaHash
from estructuras.vector_dinamico import Vector


@dataclass(frozen=True)
class UbicacionLlaveResultado:
    id: str
    sala: int
    enemigo: str = None


@dataclass(frozen=True)
class PuertaFinal:
    origen: int
    direccion: str
    destino: int
    llave: str


@dataclass(frozen=True)
class _PuertaPendiente:
    origen: object
    salida: object


@dataclass
class ResultadoResolubilidad:
    veredicto: str
    orden_por_rondas: tuple
    puerta_final: object
    motivo: str
    salas_alcanzables: tuple
    llaves_inobtenibles: tuple = ()
    frontera_bloqueada: tuple = ()
    ciclos: tuple = ()


def _comparar(a, b):
    return (a > b) - (a < b)


def _comparar_ubicaciones(a, b):
    por_sala = _comparar(a.sala, b.sala)
    if por_sala:
        return por_sala
    return _comparar(a.id, b.id)


def _comparar_puertas(a, b):
    por_origen = _comparar(a.origen, b.origen)
    if por_origen:
        return por_origen
    return _comparar(a.direccion, b.direccion)


def _es_mejor_ubicacion(candidata, actual):
    if candidata.sala != actual.sala:
        return candidata.sala < actual.sala
    if candidata.enemigo is None:
        return actual.enemigo is not None
    if actual.enemigo is None:
        return False
    return candidata.enemigo < actual.enemigo


def _leer_ubicacion(entrada):
    if isinstance(entrada, dict):
        llave_id = entrada.get("id")
        sala_id = entrada.get("sala")
        enemigo = entrada.get("enemigo")
    else:
        llave_id = getattr(entrada, "id", None)
        sala_id = getattr(entrada, "sala", None)
        enemigo = getattr(entrada, "enemigo", None)

    if type(llave_id) is not str or not llave_id:
        raise ValueError("La ubicación de llave debe incluir un id de texto no vacío.")
    if type(sala_id) is not int:
        raise ValueError("La sala de una ubicación de llave debe ser un entero.")
    if enemigo is not None and type(enemigo) is not str:
        raise ValueError("El id de enemigo debe ser texto o nulo.")
    return UbicacionLlaveResultado(llave_id, sala_id, enemigo)


def verificar_resolubilidad(cripta, ubicaciones):
    """Calcula el veredicto, las rondas y la primera puerta final válida.

    Las salas, ubicaciones, puertas y rondas se indexan con estructuras propias;
    el recorrido topológico es dirigido y no consulta costos de salida.
    """
    llave_salida = getattr(cripta, "llave_salida", None)
    if type(llave_salida) is not str or not llave_salida:
        raise ValueError("La llave de salida debe existir y no puede ser nula.")
    sala_inicial_id = getattr(cripta, "sala_inicial_id", None)
    sala_salida_id = getattr(cripta, "sala_salida_id", None)
    if type(sala_inicial_id) is not int or type(sala_salida_id) is not int:
        raise ValueError("La sala inicial y la sala de salida deben ser enteros.")
    if ubicaciones is None:
        raise ValueError("La lista de ubicaciones de llaves no puede ser nula.")

    salas_por_id = TablaHash(capacidad_inicial=max(1, len(cripta)))
    for sala in cripta.recorrer_salas():
        if type(sala.id) is not int or not salas_por_id.insertar(sala.id, sala):
            raise ValueError(f"Id de sala inválido o repetido: {sala.id!r}.")
    if not salas_por_id.contiene(sala_inicial_id):
        raise ValueError("La sala inicial no existe en el esqueleto.")
    if not salas_por_id.contiene(sala_salida_id):
        raise ValueError("La sala de salida no existe en el esqueleto.")

    ubicaciones_por_sala = TablaHash(capacidad_inicial=max(1, len(cripta)))
    todas_ubicaciones = Vector()
    for entrada in ubicaciones:
        ubicacion = _leer_ubicacion(entrada)
        if not salas_por_id.contiene(ubicacion.sala):
            raise ValueError(
                f"La sala {ubicacion.sala} de una ubicación de llave no existe."
            )
        todas_ubicaciones.agregarValor(ubicacion)
        ubicaciones_sala = ubicaciones_por_sala.obtener(ubicacion.sala)
        if ubicaciones_sala is None:
            ubicaciones_sala = Vector()
            ubicaciones_por_sala.insertar(ubicacion.sala, ubicaciones_sala)
        ubicaciones_sala.agregarValor(ubicacion)

    for sala in cripta.recorrer_salas():
        for salida in sala.salidas:
            if (
                type(getattr(salida, "direccion", None)) is not str
                or type(getattr(salida, "cerrada", None)) is not bool
                or type(getattr(salida, "sala_destino_id", None)) is not int
                or not salas_por_id.contiene(salida.sala_destino_id)
            ):
                raise ValueError("Una salida contiene datos inválidos.")

    adquiridas = TablaHash(capacidad_inicial=max(1, len(todas_ubicaciones)))
    region = TablaHash(capacidad_inicial=max(1, len(cripta)))
    pendientes_por_llave = TablaHash(capacidad_inicial=max(1, len(cripta)))
    candidatas_por_id = TablaHash(capacidad_inicial=max(1, len(todas_ubicaciones)))
    ids_candidatas = Vector()
    cola = Cola()
    puerta_final = Vector()
    rondas = []

    sala_inicial = salas_por_id.obtener(sala_inicial_id)
    region.insertar(sala_inicial_id, True)
    cola.encolar(sala_inicial)

    def agregar_candidata(ubicacion):
        if adquiridas.contiene(ubicacion.id):
            return
        actual = candidatas_por_id.obtener(ubicacion.id)
        if actual is None:
            candidatas_por_id.insertar(ubicacion.id, ubicacion)
            ids_candidatas.agregarValor(ubicacion.id)
        elif _es_mejor_ubicacion(ubicacion, actual):
            candidatas_por_id.insertar(ubicacion.id, ubicacion)

    def cruzar(origen, salida):
        if (
            salida.cerrada
            and salida.llave == llave_salida
            and salida.sala_destino_id == sala_salida_id
        ):
            puerta_final.agregarValor(PuertaFinal(
                origen.id,
                salida.direccion,
                salida.sala_destino_id,
                salida.llave,
            ))
        destino = salas_por_id.obtener(salida.sala_destino_id)
        if not region.contiene(destino.id):
            region.insertar(destino.id, True)
            cola.encolar(destino)

    def expandir_region():
        while not cola.esta_vacia():
            sala = cola.desencolar()
            ubicaciones_sala = ubicaciones_por_sala.obtener(sala.id)
            if ubicaciones_sala is not None:
                for ubicacion in ubicaciones_sala:
                    agregar_candidata(ubicacion)

            for salida in sala.salidas:
                if not salida.cerrada:
                    cruzar(sala, salida)
                elif salida.llave is not None and adquiridas.contiene(salida.llave):
                    cruzar(sala, salida)
                elif salida.llave is not None:
                    pendientes = pendientes_por_llave.obtener(salida.llave)
                    if pendientes is None:
                        pendientes = Vector()
                        pendientes_por_llave.insertar(salida.llave, pendientes)
                    pendientes.agregarValor(_PuertaPendiente(sala, salida))

    def candidatas_ordenadas():
        ubicaciones = Vector()
        for indice in range(len(ids_candidatas)):
            ubicaciones.agregarValor(
                candidatas_por_id.obtener(ids_candidatas.obtenerValor(indice))
            )
        ordenar(ubicaciones, _comparar_ubicaciones)
        return tuple(ubicaciones.obtenerValor(indice)
                     for indice in range(len(ubicaciones)))

    def salas_ordenadas():
        ids = Vector()
        for sala in cripta.recorrer_salas():
            if region.contiene(sala.id):
                ids.agregarValor(sala.id)
        ordenar(ids, _comparar)
        return tuple(ids.obtenerValor(indice) for indice in range(len(ids)))

    def resolver_puerta_final():
        if len(puerta_final) == 0:
            return None
        ordenar(puerta_final, _comparar_puertas)
        return puerta_final.obtenerValor(0)

    expandir_region()
    while True:
        nuevas = candidatas_ordenadas()
        rondas.append(nuevas)
        if not nuevas:
            motivo = "b" if adquiridas.contiene(llave_salida) else "a"
            return ResultadoResolubilidad(
                "NO RESOLUBLE",
                tuple(rondas),
                None,
                motivo,
                salas_ordenadas(),
            )

        for ubicacion in nuevas:
            adquiridas.insertar(ubicacion.id, True)

        candidatas_por_id = TablaHash(capacidad_inicial=max(1, len(todas_ubicaciones)))
        ids_candidatas = Vector()
        for ubicacion in nuevas:
            pendientes = pendientes_por_llave.obtener(ubicacion.id)
            if pendientes is not None:
                for pendiente in pendientes:
                    cruzar(pendiente.origen, pendiente.salida)

        expandir_region()
        final = resolver_puerta_final()
        if final is not None and adquiridas.contiene(llave_salida):
            return ResultadoResolubilidad(
                "RESOLUBLE",
                tuple(rondas),
                final,
                None,
                salas_ordenadas(),
            )
