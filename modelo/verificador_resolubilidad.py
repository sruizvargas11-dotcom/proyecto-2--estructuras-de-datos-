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
class PuertaBloqueada:
    origen: int
    direccion: str
    destino: int
    llave: str
    ubicaciones_llave: tuple


@dataclass(frozen=True)
class DependenciaLlave:
    id: str
    puertas: tuple


@dataclass
class LlaveInobtenible:
    id: str
    ubicaciones: tuple
    causa: str
    dependencias: tuple = ()
    relaciones: tuple = ()


@dataclass(frozen=True)
class CicloResolubilidad:
    llaves: tuple
    puertas: tuple


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


def _comparar_ubicaciones_detalle(a, b):
    por_sala = _comparar(a.sala, b.sala)
    if por_sala:
        return por_sala
    if a.enemigo is None:
        return 0 if b.enemigo is None else -1
    if b.enemigo is None:
        return 1
    return _comparar(a.enemigo, b.enemigo)


def _comparar_puertas(a, b):
    por_origen = _comparar(a.origen, b.origen)
    if por_origen:
        return por_origen
    return _comparar(a.direccion, b.direccion)


def _comparar_ciclos(a, b):
    por_inicio = _comparar(a.llaves[0], b.llaves[0])
    if por_inicio:
        return por_inicio
    return _comparar_secuencias(a.llaves, b.llaves)


def _comparar_dependencias(a, b):
    return _comparar(a.id, b.id)


def _comparar_secuencias(a, b):
    limite = min(len(a), len(b))
    for indice in range(limite):
        diferencia = _comparar(a[indice], b[indice])
        if diferencia:
            return diferencia
    return _comparar(len(a), len(b))


def _alcanzar_con_llaves(cripta, salas_por_id, llaves, sala_inicial_id):
    alcanzables = TablaHash(capacidad_inicial=max(1, len(cripta)))
    cola = Cola()
    inicial = salas_por_id.obtener(sala_inicial_id)
    alcanzables.insertar(inicial.id, True)
    cola.encolar(inicial)
    while not cola.esta_vacia():
        sala = cola.desencolar()
        for salida in sala.salidas:
            if salida.cerrada and (
                salida.llave is None or not llaves.contiene(salida.llave)
            ):
                continue
            destino = salas_por_id.obtener(salida.sala_destino_id)
            if not alcanzables.contiene(destino.id):
                alcanzables.insertar(destino.id, True)
                cola.encolar(destino)
    return alcanzables


def _puertas_de_dependencia(
    cripta,
    region,
    llave_id,
    ubicaciones_por_id,
):
    puertas = Vector()
    ubicaciones = ubicaciones_por_id.obtener(llave_id)
    if ubicaciones is None:
        return ()
    ubicaciones_ordenadas = Vector()
    for ubicacion in ubicaciones:
        ubicaciones_ordenadas.agregarValor(ubicacion)
    ordenar(ubicaciones_ordenadas, _comparar_ubicaciones_detalle)
    datos_ubicacion = tuple(
        ubicaciones_ordenadas.obtenerValor(indice)
        for indice in range(len(ubicaciones_ordenadas))
    )
    for sala in cripta.recorrer_salas():
        if not region.contiene(sala.id):
            continue
        for salida in sala.salidas:
            if (
                salida.cerrada
                and salida.llave == llave_id
                and not region.contiene(salida.sala_destino_id)
            ):
                puertas.agregarValor(PuertaBloqueada(
                    sala.id,
                    salida.direccion,
                    salida.sala_destino_id,
                    llave_id,
                    datos_ubicacion,
                ))
    ordenar(puertas, _comparar_puertas)
    return tuple(
        puertas.obtenerValor(indice)
        for indice in range(len(puertas))
    )


def _camino_hasta(nodo, padres):
    camino_inverso = Vector()
    actual = nodo
    while actual is not None:
        camino_inverso.agregarValor(actual)
        actual = padres.obtener(actual)
    camino = Vector()
    for indice in range(len(camino_inverso) - 1, -1, -1):
        camino.agregarValor(camino_inverso.obtenerValor(indice))
    return camino


def _canonizar_ciclo(camino):
    cantidad = len(camino) - 1
    minimo = camino.obtenerValor(0)
    indice_minimo = 0
    for indice in range(1, cantidad):
        actual = camino.obtenerValor(indice)
        if actual < minimo:
            minimo = actual
            indice_minimo = indice
    canonico = Vector()
    for desplazamiento in range(cantidad):
        indice = (indice_minimo + desplazamiento) % cantidad
        canonico.agregarValor(camino.obtenerValor(indice))
    canonico.agregarValor(canonico.obtenerValor(0))
    return tuple(canonico.obtenerValor(indice)
                 for indice in range(len(canonico)))


def _buscar_ciclo_minimo(llave_inicial, llaves_por_id):
    inicio = llaves_por_id.obtener(llave_inicial)
    if inicio is None:
        return None

    padres = TablaHash(capacidad_inicial=max(1, len(llaves_por_id)))
    distancias = TablaHash(capacidad_inicial=max(1, len(llaves_por_id)))
    visitadas = TablaHash(capacidad_inicial=max(1, len(llaves_por_id)))
    cola = Cola()
    visitadas.insertar(llave_inicial, True)
    padres.insertar(llave_inicial, None)
    distancias.insertar(llave_inicial, 0)

    for vecino in inicio.dependencias:
        if vecino == llave_inicial:
            return (llave_inicial, llave_inicial)
        if llaves_por_id.contiene(vecino) and not visitadas.contiene(vecino):
            visitadas.insertar(vecino, True)
            padres.insertar(vecino, llave_inicial)
            distancias.insertar(vecino, 1)
            cola.encolar(vecino)

    mejor = None
    longitud_mejor = None
    while not cola.esta_vacia():
        actual = cola.desencolar()
        distancia = distancias.obtener(actual)
        if longitud_mejor is not None and distancia + 1 > longitud_mejor:
            break
        llave_actual = llaves_por_id.obtener(actual)
        for vecino in llave_actual.dependencias:
            if vecino == llave_inicial:
                camino = _camino_hasta(actual, padres)
                camino.agregarValor(llave_inicial)
                candidato = _canonizar_ciclo(camino)
                longitud = len(candidato) - 1
                if (
                    longitud_mejor is None
                    or longitud < longitud_mejor
                    or (
                        longitud == longitud_mejor
                        and _comparar_secuencias(candidato, mejor) < 0
                    )
                ):
                    mejor = candidato
                    longitud_mejor = longitud
            elif (
                llaves_por_id.contiene(vecino)
                and not visitadas.contiene(vecino)
            ):
                visitadas.insertar(vecino, True)
                padres.insertar(vecino, actual)
                distancias.insertar(vecino, distancia + 1)
                cola.encolar(vecino)
    return mejor


def _crear_ciclos(llaves_inobtenibles):
    llaves_por_id = TablaHash(capacidad_inicial=max(1, len(llaves_inobtenibles)))
    for llave in llaves_inobtenibles:
        llaves_por_id.insertar(llave.id, llave)

    ciclos = Vector()
    for llave in llaves_inobtenibles:
        secuencia = _buscar_ciclo_minimo(llave.id, llaves_por_id)
        if secuencia is None:
            continue
        puertas = Vector()
        for indice in range(len(secuencia) - 1):
            desde = llaves_por_id.obtener(secuencia[indice])
            hacia = secuencia[indice + 1]
            for relacion in desde.relaciones:
                if relacion.id == hacia:
                    for puerta in relacion.puertas:
                        puertas.agregarValor(puerta)
                    break
        ordenar(puertas, _comparar_puertas)
        ciclos.agregarValor(CicloResolubilidad(
            secuencia,
            tuple(puertas.obtenerValor(indice)
                  for indice in range(len(puertas))),
        ))

    ordenar(ciclos, _comparar_ciclos)
    participantes = TablaHash(capacidad_inicial=max(1, len(llaves_inobtenibles)))
    for ciclo in ciclos:
        for indice in range(len(ciclo.llaves) - 1):
            participantes.insertar(ciclo.llaves[indice], True)
    for llave in llaves_inobtenibles:
        if participantes.contiene(llave.id):
            llave.causa = "en ciclo"
    return tuple(ciclos.obtenerValor(indice) for indice in range(len(ciclos)))


def _diagnosticar_no_resoluble(
    cripta,
    salas_por_id,
    sala_inicial_id,
    ubicaciones_por_id,
    ids_llaves,
    adquiridas,
    region,
    puertas_pendientes,
):
    inobtenibles = Vector()
    inobtenibles_por_id = TablaHash(capacidad_inicial=max(1, len(ids_llaves)))
    for indice in range(len(ids_llaves)):
        llave_id = ids_llaves.obtenerValor(indice)
        if adquiridas.contiene(llave_id):
            continue
        ubicaciones = ubicaciones_por_id.obtener(llave_id)
        ordenar(ubicaciones, _comparar_ubicaciones_detalle)
        llave = LlaveInobtenible(
            llave_id,
            tuple(ubicaciones.obtenerValor(posicion)
                  for posicion in range(len(ubicaciones))),
            "sala inalcanzable aun con todas las llaves",
            Vector(),
            Vector(),
        )
        inobtenibles.agregarValor(llave)
        inobtenibles_por_id.insertar(llave_id, llave)

    todas_llaves = TablaHash(capacidad_inicial=max(1, len(ids_llaves)))
    for indice in range(len(ids_llaves)):
        todas_llaves.insertar(ids_llaves.obtenerValor(indice), True)
    region_todas = _alcanzar_con_llaves(
        cripta, salas_por_id, todas_llaves, sala_inicial_id
    )
    alcanzables_con_todas = TablaHash(
        capacidad_inicial=max(1, len(inobtenibles))
    )
    for llave in inobtenibles:
        for ubicacion in llave.ubicaciones:
            if region_todas.contiene(ubicacion.sala):
                alcanzables_con_todas.insertar(llave.id, True)
                break

    for indice_retirada in range(len(ids_llaves)):
        llave_retirada = ids_llaves.obtenerValor(indice_retirada)
        llaves_otorgadas = TablaHash(capacidad_inicial=max(1, len(ids_llaves)))
        for indice in range(len(ids_llaves)):
            llave_id = ids_llaves.obtenerValor(indice)
            if llave_id != llave_retirada:
                llaves_otorgadas.insertar(llave_id, True)
        region_sin_llave = _alcanzar_con_llaves(
            cripta, salas_por_id, llaves_otorgadas, sala_inicial_id
        )
        puertas_dependencia = None
        for llave in inobtenibles:
            if not alcanzables_con_todas.contiene(llave.id):
                continue
            tiene_ubicacion = False
            for ubicacion in llave.ubicaciones:
                if region_sin_llave.contiene(ubicacion.sala):
                    tiene_ubicacion = True
                    break
            if not tiene_ubicacion:
                llave.dependencias.agregarValor(llave_retirada)
                if puertas_dependencia is None:
                    puertas_dependencia = _puertas_de_dependencia(
                        cripta,
                        region_sin_llave,
                        llave_retirada,
                        ubicaciones_por_id,
                    )
                llave.relaciones.agregarValor(DependenciaLlave(
                    llave_retirada,
                    puertas_dependencia,
                ))

    for llave in inobtenibles:
        ordenar(llave.dependencias, _comparar)
        llave.dependencias = tuple(
            llave.dependencias.obtenerValor(indice)
            for indice in range(len(llave.dependencias))
        )
        ordenar(llave.relaciones, _comparar_dependencias)
        llave.relaciones = tuple(
            llave.relaciones.obtenerValor(indice)
            for indice in range(len(llave.relaciones))
        )
        if llave.dependencias:
            llave.causa = "depende de " + ", ".join(llave.dependencias)

    frontera = Vector()
    for pendiente in puertas_pendientes:
        salida = pendiente.salida
        if (
            region.contiene(pendiente.origen.id)
            and not region.contiene(salida.sala_destino_id)
            and (
                salida.llave is None
                or not adquiridas.contiene(salida.llave)
            )
        ):
            ubicaciones = (
                ubicaciones_por_id.obtener(salida.llave)
                if salida.llave is not None
                else None
            )
            ubicaciones_ordenadas = Vector()
            if ubicaciones is not None:
                for ubicacion in ubicaciones:
                    ubicaciones_ordenadas.agregarValor(ubicacion)
                ordenar(ubicaciones_ordenadas, _comparar_ubicaciones_detalle)
            etiqueta_llave = (
                salida.llave
                if ubicaciones is not None
                else "inexistente"
            )
            frontera.agregarValor(PuertaBloqueada(
                pendiente.origen.id,
                salida.direccion,
                salida.sala_destino_id,
                etiqueta_llave,
                tuple(
                    ubicaciones_ordenadas.obtenerValor(indice)
                    for indice in range(len(ubicaciones_ordenadas))
                ),
            ))
    ordenar(frontera, _comparar_puertas)
    return (
        tuple(inobtenibles.obtenerValor(indice)
              for indice in range(len(inobtenibles))),
        tuple(frontera.obtenerValor(indice)
              for indice in range(len(frontera))),
    )


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
    ubicaciones_por_id = TablaHash(capacidad_inicial=max(1, len(cripta)))
    llaves_vistas = TablaHash(capacidad_inicial=max(1, len(cripta)))
    ids_llaves = Vector()
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
        ubicaciones_llave = ubicaciones_por_id.obtener(ubicacion.id)
        if ubicaciones_llave is None:
            ubicaciones_llave = Vector()
            ubicaciones_por_id.insertar(ubicacion.id, ubicaciones_llave)
        ubicaciones_llave.agregarValor(ubicacion)
        if not llaves_vistas.contiene(ubicacion.id):
            llaves_vistas.insertar(ubicacion.id, True)
            ids_llaves.agregarValor(ubicacion.id)
    ordenar(ids_llaves, _comparar)

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
    puertas_pendientes = Vector()
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
                elif salida.llave is None:
                    puertas_pendientes.agregarValor(_PuertaPendiente(sala, salida))
                elif salida.llave is not None and adquiridas.contiene(salida.llave):
                    cruzar(sala, salida)
                else:
                    pendiente = _PuertaPendiente(sala, salida)
                    puertas_pendientes.agregarValor(pendiente)
                    pendientes = pendientes_por_llave.obtener(salida.llave)
                    if pendientes is None:
                        pendientes = Vector()
                        pendientes_por_llave.insertar(salida.llave, pendientes)
                    pendientes.agregarValor(pendiente)

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
            llaves_inobtenibles, frontera = _diagnosticar_no_resoluble(
                cripta,
                salas_por_id,
                sala_inicial_id,
                ubicaciones_por_id,
                ids_llaves,
                adquiridas,
                region,
                puertas_pendientes,
            )
            ciclos = _crear_ciclos(llaves_inobtenibles)
            return ResultadoResolubilidad(
                "NO RESOLUBLE",
                tuple(rondas),
                None,
                motivo,
                salas_ordenadas(),
                llaves_inobtenibles,
                frontera,
                ciclos,
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
