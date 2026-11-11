"""Búsqueda determinista de rutas para el comportamiento cazador."""

from estructuras.vector_dinamico import Vector
from estructuras.heap_prioridad_ruta import ColaPrioridadRuta


def _registro(sala, costo, anterior=None):
    return [sala, costo, anterior]


def _buscar(registros, sala):
    datos = registros.almacenamiento()
    izquierda = 0
    derecha = len(registros) - 1
    while izquierda <= derecha:
        medio = (izquierda + derecha) // 2
        registro = datos[medio]
        if registro[0].id == sala.id:
            return registro
        if registro[0].id < sala.id:
            izquierda = medio + 1
        else:
            derecha = medio - 1
    return None


def _crear_indice_registros(cripta):
    distancias = Vector()
    maximo = 0
    for sala in cripta.recorrer_salas():
        if sala.id > maximo:
            maximo = sala.id
        distancias.agregarValor([sala, None, None, None])
    indice = None
    if maximo <= len(distancias) * 4:
        indice = Vector()
        for _ in range(maximo + 1):
            indice.agregarValor(None)
        datos_indice = indice.almacenamiento()
        for registro in distancias:
            datos_indice[registro[0].id] = registro
    return distancias, indice


def _registro_indice(registros, indice, sala):
    if indice is not None:
        return indice.almacenamiento()[sala.id]
    return _buscar(registros, sala)


def _construir_entrantes(cripta):
    entrantes = Vector()
    for sala in cripta.recorrer_salas():
        entrantes.agregarValor([sala, Vector()])
    for origen in cripta.recorrer_salas():
        for salida in origen.salidas_abiertas():
            registro = _buscar(entrantes, salida.sala_destino)
            registro[1].agregarValor((origen, salida.costo))
    return entrantes


def construir_entrantes(cripta):
    """Construye las aristas inversas abiertas para un ciclo de decisiones."""
    return _construir_entrantes(cripta)


def _distancias_hacia_jugador(cripta, jugador, entrantes=None):
    distancias = Vector()
    for sala in cripta.recorrer_salas():
        distancias.agregarValor([sala, None])
    if entrantes is None:
        entrantes = _construir_entrantes(cripta)
    objetivo = _buscar(distancias, jugador.sala_actual)
    objetivo[1] = 0
    frontera = ColaPrioridadRuta()
    frontera.insertar(_registro(jugador.sala_actual, 0))
    while len(frontera):
        registro = frontera.extraer_minimo()
        sala, costo = registro[0], registro[1]
        registro = _buscar(distancias, sala)
        if registro[1] != costo:
            continue
        entrantes_sala = _buscar(entrantes, sala)[1]
        for origen, costo_salida in entrantes_sala:
            anterior = _buscar(distancias, origen)
            nuevo = costo + costo_salida
            if anterior[1] is None or nuevo < anterior[1]:
                anterior[1] = nuevo
                frontera.insertar(_registro(origen, nuevo))
    return distancias


class CacheDistanciasCazador:
    """Reutiliza distancias mientras jugador y puertas no hayan cambiado."""

    def __init__(self, cripta):
        self.cripta = cripta
        self._sala_jugador = None
        self._puertas = Vector()
        self._distancias = None
        self._entrantes = None

    def obtener(self, jugador):
        puertas = Vector()
        for sala in self.cripta.recorrer_salas():
            for salida in sala.salidas:
                puertas.agregarValor((sala.id, salida.direccion, salida.cerrada))
        invalida = self._sala_jugador is not jugador.sala_actual
        if not invalida and self._puertas is not None:
            if len(puertas) != len(self._puertas):
                invalida = True
            else:
                for i in range(len(puertas)):
                    if puertas.obtenerValor(i) != self._puertas.obtenerValor(i):
                        invalida = True
                        break
        if invalida or self._distancias is None:
            self._entrantes = _construir_entrantes(self.cripta)
            self._distancias = _distancias_hacia_jugador(
                self.cripta, jugador, self._entrantes
            )
            self._sala_jugador = jugador.sala_actual
            self._puertas = puertas
        return self._distancias


def _decidir_cazador_individual(cazador, jugador):
    inicio = cazador.sala_actual
    distancias, indice = _crear_indice_registros(inicio.cripta)
    registros_por_id = (indice.almacenamiento()
                        if indice is not None else None)
    frontera = ColaPrioridadRuta()
    origen = (registros_por_id[inicio.id] if registros_por_id is not None
              else _buscar(distancias, inicio))
    origen[1] = 0
    frontera.insertar([inicio, 0, None, None])
    while len(frontera):
        registro = frontera.extraer_minimo()
        sala, costo = registro[0], registro[1]
        actual = (registros_por_id[sala.id] if registros_por_id is not None
                  else _buscar(distancias, sala))
        if actual[1] != costo:
            continue
        # Los costos de salida son positivos. Cuando el mínimo pendiente ya
        # supera el rango, ninguna ruta restante puede habilitar persecución.
        if costo > cazador.rango:
            break
        if sala is jugador.sala_actual:
            break
        for salida in sala.salidas:
            if salida.cerrada:
                continue
            destino_sala = salida.sala_destino
            destino = (registros_por_id[destino_sala.id]
                       if registros_por_id is not None
                       else _buscar(distancias, destino_sala))
            nuevo = costo + salida.costo
            if nuevo > cazador.rango:
                continue
            primer_id = (destino_sala.id if sala is inicio
                         else registro[2])
            primer_costo = (salida.costo if sala is inicio
                            else registro[3])
            if (destino[1] is None or nuevo < destino[1]
                    or (nuevo == destino[1] and primer_id < destino[2])):
                destino[1] = nuevo
                destino[2] = primer_id
                destino[3] = primer_costo
                frontera.insertar([
                    destino_sala, nuevo, primer_id, primer_costo
                ])
    final = (registros_por_id[jugador.sala_actual.id]
             if registros_por_id is not None
             else _buscar(distancias, jugador.sala_actual))
    if final[1] is None or final[1] > cazador.rango:
        return ("esperar", None)
    return ("mover", (
        registros_por_id[final[2]][0] if registros_por_id is not None
        else inicio.cripta.sala_por_id(final[2]), final[3]
    ))


def decidir_cazador(cazador, jugador, distancias=None, entrantes=None):
    """Devuelve ``(acción, destino)`` o ``(acción, (destino, costo))``."""
    if distancias is None:
        return _decidir_cazador_individual(cazador, jugador)
    final = _buscar(distancias, cazador.sala_actual)
    if final is None or final[1] is None or final[1] > cazador.rango:
        return ("esperar", None)

    if final[1] == 0:
        return ("atacar", jugador)

    mejor_salida = None
    for salida in cazador.sala_actual.salidas_abiertas():
        distancia = _buscar(distancias, salida.sala_destino)
        if distancia is not None and distancia[1] is not None and (
                salida.costo + distancia[1] == final[1]
                and (mejor_salida is None
                     or salida.sala_destino.id < mejor_salida.sala_destino.id)):
            mejor_salida = salida
    if mejor_salida is None:
        return ("esperar", None)
    return ("mover", (mejor_salida.sala_destino, mejor_salida.costo))


def decisiones_cazadores_compartidas(cazadores, jugador, cripta):
    distancias = CacheDistanciasCazador(cripta).obtener(jugador)
    decisiones = Vector()
    for cazador in cazadores:
        decisiones.agregarValor(decidir_cazador(cazador, jugador, distancias))
    return decisiones
