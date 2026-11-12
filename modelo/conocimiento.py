"""Conocimiento del jugador sobre la cripta (niebla de guerra, spec 002).

Separado del mapa real: guarda qué salas exploró o avistó el jugador y el
último estado observado de cada puerta. Las referencias a ``Sala``/``Salida``
solo se usan para leer nombre, salidas y, al observar, el estado real.
Toda mutación pasa por el historial compartido (deltas) para el pergamino.
"""
from estructuras.vector_dinamico import Vector
from estructuras.heap_prioridad_ruta import ColaPrioridadRuta
from modelo.deltas import DeltaAtributos, DeltaLongitud

EXPLORADA = "explorada"
AVISTADA = "avistada"
DESCONOCIDA = "desconocida"

ABIERTA = "abierta"
CERRADA = "cerrada"
SIN_OBSERVAR = "sin observar"


class RecuerdoPuerta:
    """Último estado observado de una salida: None si nunca se observó."""

    def __init__(self, origen, salida):
        self.origen = origen
        self.direccion = salida.direccion
        self.destino_id = salida.sala_destino_id
        self.costo = salida.costo
        self.salida = salida
        self.destino = None      # RegistroSala, se enlaza al construir
        self.cerrada = None


class RegistroSala:
    def __init__(self, sala):
        self.id = sala.id
        self.sala = sala
        self.explorada = False
        self.avistamientos = 0
        self.recuerdos = Vector()
        self.entrantes = Vector()
        self.dist = None
        self.marca = 0

    @property
    def estado(self):
        if self.explorada:
            return EXPLORADA
        return AVISTADA if self.avistamientos > 0 else DESCONOCIDA


class ConocimientoJugador:
    def __init__(self, cripta, historial=None):
        self.historial = historial
        self.registros = Vector()
        self.cambios = Vector()      # (tiempo, tipo, sala_id, direccion, valor)
        self._marca = 0
        # Las salas de la cripta ya están ordenadas por ID: búsqueda binaria.
        for sala in cripta.recorrer_salas():
            self.registros.agregarValor(RegistroSala(sala))
        for registro in self.registros:
            for salida in registro.sala.salidas:
                recuerdo = RecuerdoPuerta(registro, salida)
                registro.recuerdos.agregarValor(recuerdo)
                destino = self.registro(salida.sala_destino_id)
                recuerdo.destino = destino
                if destino is not None:
                    destino.entrantes.agregarValor(recuerdo)

    # ------------------------------------------------------------ consultas
    def registro(self, sala_id):
        datos = self.registros.almacenamiento()
        izquierda, derecha = 0, len(self.registros) - 1
        while izquierda <= derecha:
            medio = (izquierda + derecha) // 2
            actual = datos[medio]
            if actual.id == sala_id:
                return actual
            if actual.id < sala_id:
                izquierda = medio + 1
            else:
                derecha = medio - 1
        return None

    def estado_sala(self, sala_id):
        registro = self.registro(sala_id)
        return DESCONOCIDA if registro is None else registro.estado

    def explorada(self, sala_id):
        registro = self.registro(sala_id)
        return registro is not None and registro.explorada

    def puerta_recordada(self, sala_id, direccion):
        """ABIERTA / CERRADA / SIN_OBSERVAR, o None si la sala no está explorada."""
        registro = self.registro(sala_id)
        if registro is None or not registro.explorada:
            return None
        for recuerdo in registro.recuerdos:
            if recuerdo.direccion == direccion:
                return _texto_puerta(recuerdo)
        return None

    def vista_mapa(self):
        """Solo lo conocido: tuplas (id, nombre, salidas) de las exploradas.

        Cada salida es (direccion, costo, estado_recordado, destino), con destino
        ``(id, nombre)`` si está explorado o ``AVISTADA`` si no; nunca aparece
        información de salas desconocidas.
        """
        mapa = Vector()
        for registro in self.registros:
            if not registro.explorada:
                continue
            salidas = Vector()
            for recuerdo in registro.recuerdos:
                destino = recuerdo.destino
                visible = ((destino.id, destino.sala.nombre)
                           if destino is not None and destino.explorada else AVISTADA)
                salidas.agregarValor((recuerdo.direccion, recuerdo.costo,
                                      _texto_puerta(recuerdo), visible))
            mapa.agregarValor((registro.id, registro.sala.nombre, tuple(salidas)))
        return tuple(mapa)

    def resumen(self):
        """Estado comparable completo (para pruebas, guardado e historia)."""
        filas = Vector()
        for registro in self.registros:
            puertas = tuple((r.direccion, r.cerrada) for r in registro.recuerdos)
            filas.agregarValor((registro.id, registro.estado, puertas))
        return tuple(filas)

    # ------------------------------------------------------------ cambios
    def _asignar(self, objeto, campo, valor):
        if self.historial is not None:
            self.historial.registrar(DeltaAtributos(objeto, campo))
        setattr(objeto, campo, valor)

    def _anotar(self, tiempo, tipo, sala_id, direccion, valor):
        if self.historial is not None:
            self.historial.registrar(DeltaLongitud(self.cambios))
        self.cambios.agregarValor((tiempo, tipo, sala_id, direccion, valor))

    def explorar(self, registro, tiempo):
        """Marca explorada y avista sus destinos: O(salidas de la sala)."""
        if registro.explorada:
            return False
        self._asignar(registro, "explorada", True)
        self._anotar(tiempo, "explorar", registro.id, None, True)
        for recuerdo in registro.recuerdos:
            destino = recuerdo.destino
            if destino is not None:
                self._asignar(destino, "avistamientos", destino.avistamientos + 1)
        return True

    def recordar(self, recuerdo, cerrada, tiempo):
        if recuerdo.cerrada is cerrada:
            return False
        self._asignar(recuerdo, "cerrada", cerrada)
        self._anotar(tiempo, "puerta", recuerdo.origen.id, recuerdo.direccion, cerrada)
        return True

    def observar(self, sala, tiempo):
        """El jugador está en ``sala``: ve el estado real de toda puerta con un
        extremo aquí (salidas propias y salidas de otras salas que llegan)."""
        registro = self.registro(sala.id)
        if registro is None:
            return 0
        cambios = 0
        for recuerdo in registro.recuerdos:
            cambios += self.recordar(recuerdo, bool(recuerdo.salida.cerrada), tiempo)
        for recuerdo in registro.entrantes:
            cambios += self.recordar(recuerdo, bool(recuerdo.salida.cerrada), tiempo)
        return cambios

    def visitar(self, sala, tiempo, antorcha=False):
        """Entrada física: explora, observa y, con antorcha, explora vecinas
        sin observar sus puertas remotas ni tocar su contenido."""
        registro = self.registro(sala.id)
        if registro is None:
            return
        self.explorar(registro, tiempo)
        self.observar(sala, tiempo)
        if antorcha:
            for recuerdo in registro.recuerdos:
                if recuerdo.destino is not None:
                    self.explorar(recuerdo.destino, tiempo)

    # ------------------------------------------------------------ historia
    def reconstruir_en(self, tiempo):
        """Conocimiento que existía en ``tiempo``: objeto nuevo, sin historial,
        que no comparte estado mutable con el actual."""
        copia = ConocimientoJugador(self.registros.obtenerValor(0).sala.cripta
                                    if len(self.registros) else _CriptaVacia())
        for cambio in self.cambios:
            if cambio[0] > tiempo:
                break
            _, tipo, sala_id, direccion, valor = cambio
            registro = copia.registro(sala_id)
            if tipo == "explorar":
                copia.explorar(registro, cambio[0])
            else:
                for recuerdo in registro.recuerdos:
                    if recuerdo.direccion == direccion:
                        copia.recordar(recuerdo, valor, cambio[0])
        return copia

    # ------------------------------------------------------------ rutas
    def _usable(self, recuerdo):
        destino = recuerdo.destino
        return (recuerdo.origen.explorada and destino is not None
                and destino.explorada and recuerdo.cerrada is False)

    def siguiente_paso(self, origen_id, destino_id):
        """Primer paso de una ruta conocida de costo mínimo.

        Devuelve ``(direccion, destino_paso_id, costo_salida, costo_total)`` o
        None. Solo usa salas exploradas y puertas recordadas abiertas; en
        empate elige la vecina de menor ID (misma regla que el cazador).
        """
        origen = self.registro(origen_id)
        destino = self.registro(destino_id)
        if (origen is None or destino is None or not origen.explorada
                or not destino.explorada or origen is destino):
            return None
        self._marca += 1
        marca = self._marca
        destino.marca, destino.dist = marca, 0
        frontera = ColaPrioridadRuta()
        frontera.insertar([destino, 0])
        while len(frontera):
            registro, costo = frontera.extraer_minimo()
            if registro.dist != costo:
                continue
            if registro is origen:
                break
            for recuerdo in registro.entrantes:
                if not self._usable(recuerdo):
                    continue
                previo = recuerdo.origen
                nuevo = costo + recuerdo.costo
                if previo.marca != marca or nuevo < previo.dist:
                    previo.marca, previo.dist = marca, nuevo
                    frontera.insertar([previo, nuevo])
        if origen.marca != marca:
            return None
        total = origen.dist
        mejor = None
        for recuerdo in origen.recuerdos:
            vecino = recuerdo.destino
            if (self._usable(recuerdo) and vecino.marca == marca
                    and recuerdo.costo + vecino.dist == total
                    and (mejor is None or vecino.id < mejor.destino.id)):
                mejor = recuerdo
        if mejor is None:
            return None
        return (mejor.direccion, mejor.destino.id, mejor.costo, total)


class _CriptaVacia:
    def recorrer_salas(self):
        return iter(())


def _texto_puerta(recuerdo):
    if recuerdo.cerrada is None:
        return SIN_OBSERVAR
    return CERRADA if recuerdo.cerrada else ABIERTA
