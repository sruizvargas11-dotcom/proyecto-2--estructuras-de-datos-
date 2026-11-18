"""Mapa de la cripta con consultas por identificador de sala."""

from estructuras.vector_dinamico import Vector
from estructuras.ordenamientos import ordenar


def comparar_salas(a, b):
    return (a.id > b.id) - (a.id < b.id)


class CriptaModelo:
    def __init__(
        self,
        cripta_id,
        version,
        sala_inicial_id,
        sala_salida_id,
        llave_salida,
        presupuesto_solicitudes,
        inventario_max,
    ):
        self.id = cripta_id
        self.version = version
        self.sala_inicial_id = sala_inicial_id
        self.sala_salida_id = sala_salida_id
        self.llave_salida = llave_salida
        self.presupuesto_solicitudes = presupuesto_solicitudes
        self.inventario_max = inventario_max

        self.ultimo_algoritmo = None
        self._salas = Vector()
        self._ordenadas = False
        self.revision_puertas = 0
        self._indice_salas_directo = None
        self._indice_salas_ids = None
        self._indice_salas_posiciones = None
        self._adjacencia_individual = None

    def __len__(self):
        return len(self._salas)

    def agregar_sala(self, sala):
        self._salas.agregarValor(sala)
        self._ordenadas = False

    def finalizar_carga(self):
        """Ordena las salas y enlaza los destinos de sus salidas."""
        self._ordenadas = False

        self.ultimo_algoritmo = ordenar(
            self._salas,
            comparar_salas,
        )

        for i in range(1, len(self._salas)):
            anterior = self._salas.obtenerValor(i - 1)
            actual = self._salas.obtenerValor(i)

            if anterior.id == actual.id:
                raise ValueError(
                    f"ID de sala repetido: {actual.id}"
                )

        self._ordenadas = True
        self._construir_indice_salas()

        # Todas las salas ya están disponibles y ordenadas.
        for sala in self.recorrer_salas():
            sala.cripta = self
            for salida in sala.salidas:
                salida.cripta = self
                salida.sala_destino = self.sala_por_id(
                    salida.sala_destino_id
                )
        self._construir_adjacencia_individual()

    def registrar_cambio_puerta(self):
        self.revision_puertas += 1

    def _construir_indice_salas(self):
        maximo = 0
        for sala in self._salas:
            if sala.id > maximo:
                maximo = sala.id
        if maximo <= len(self._salas) * 4:
            directo = Vector()
            for _ in range(maximo + 1):
                directo.agregarValor(-1)
            datos = directo.almacenamiento()
            for posicion in range(len(self._salas)):
                datos[self._salas.obtenerValor(posicion).id] = posicion
            self._indice_salas_directo = directo
            self._indice_salas_ids = None
            self._indice_salas_posiciones = None
        else:
            ids = Vector()
            posiciones = Vector()
            for posicion in range(len(self._salas)):
                ids.agregarValor(self._salas.obtenerValor(posicion).id)
                posiciones.agregarValor(posicion)
            self._indice_salas_directo = None
            self._indice_salas_ids = ids
            self._indice_salas_posiciones = posiciones

    def _construir_adjacencia_individual(self):
        adjacencia = Vector()
        for posicion in range(len(self._salas)):
            origen = self._salas.obtenerValor(posicion)
            vecinos = Vector()
            for salida in origen.salidas:
                destino_posicion = self.posicion_sala_por_id(
                    salida.sala_destino_id
                )
                if destino_posicion is not None:
                    vecinos.agregarValor((destino_posicion, salida))
            adjacencia.agregarValor(vecinos)
        self._adjacencia_individual = adjacencia

    def adjacencia_individual(self):
        if self._adjacencia_individual is None:
            raise RuntimeError(
                "Debes finalizar la carga antes de consultar la adyacencia."
            )
        return self._adjacencia_individual

    def posicion_sala_por_id(self, sala_id):
        if type(sala_id) is not int:
            return None
        if not self._ordenadas:
            raise RuntimeError(
                "Debes finalizar la carga antes de buscar posiciones de sala."
            )
        if self._indice_salas_directo is not None:
            if sala_id < 0 or sala_id >= len(self._indice_salas_directo):
                return None
            posicion = self._indice_salas_directo.obtenerValor(sala_id)
            return posicion if posicion >= 0 else None
        izquierda = 0
        derecha = len(self._indice_salas_ids) - 1
        while izquierda <= derecha:
            medio = (izquierda + derecha) // 2
            actual = self._indice_salas_ids.obtenerValor(medio)
            if actual == sala_id:
                return self._indice_salas_posiciones.obtenerValor(medio)
            if actual < sala_id:
                izquierda = medio + 1
            else:
                derecha = medio - 1
        return None

    def sala_por_id(self, sala_id):
        """Busca en O(log n); devuelve None si el ID no existe."""
        if not self._ordenadas:
            raise RuntimeError(
                "Debes finalizar la carga antes de buscar salas."
            )

        izquierda = 0
        derecha = len(self._salas) - 1

        while izquierda <= derecha:
            medio = (izquierda + derecha) // 2
            sala = self._salas.obtenerValor(medio)

            if sala.id == sala_id:
                return sala

            if sala.id < sala_id:
                izquierda = medio + 1
            else:
                derecha = medio - 1

        return None

    def recorrer_salas(self):
        for i in range(len(self._salas)):
            yield self._salas.obtenerValor(i)
