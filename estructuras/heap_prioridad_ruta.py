"""Cola de prioridad propia para búsquedas de rutas ponderadas."""

from estructuras.vector_dinamico import Vector


class ColaPrioridadRuta:
    def __init__(self):
        self._elementos = Vector()

    def __len__(self):
        return len(self._elementos)

    @staticmethod
    def _menor(a, b):
        clave_a = a[1], (a[0].id if hasattr(a[0], "id") else a[0])
        clave_b = b[1], (b[0].id if hasattr(b[0], "id") else b[0])
        return clave_a < clave_b

    @staticmethod
    def _clave(elemento):
        posicion = elemento[0]
        posicion = posicion.id if hasattr(posicion, "id") else posicion
        return elemento[1], posicion

    def insertar(self, elemento):
        self._elementos.agregarValor(elemento)
        datos = self._elementos.almacenamiento()
        indice = len(self._elementos) - 1
        clave = self._clave(elemento)
        while indice > 0:
            padre = (indice - 1) // 2
            valor_padre = datos[padre]
            if clave >= self._clave(valor_padre):
                break
            datos[indice] = valor_padre
            indice = padre
        datos[indice] = elemento

    def extraer_minimo(self):
        if len(self._elementos) == 0:
            raise IndexError("La cola de rutas está vacía.")
        datos = self._elementos.almacenamiento()
        minimo = datos[0]
        ultimo = self._elementos.eliminarUltimo()
        if len(self._elementos) == 0:
            return minimo

        indice = 0
        cantidad = len(self._elementos)
        clave_ultimo = self._clave(ultimo)
        while True:
            izquierdo = indice * 2 + 1
            if izquierdo >= cantidad:
                break
            derecho = izquierdo + 1
            menor = izquierdo
            if (derecho < cantidad
                    and self._clave(datos[derecho])
                    < self._clave(datos[izquierdo])):
                menor = derecho
            hijo = datos[menor]
            if self._clave(hijo) >= clave_ultimo:
                break
            datos[indice] = hijo
            indice = menor
        datos[indice] = ultimo
        return minimo

    def recorrer(self):
        return iter(self._elementos)


class ColaPrioridadPosicion:
    """Cola propia para Dijkstra individual con posiciones compactas.

    Mantiene cuatro vectores paralelos para evitar crear registros/tuplas de
    ruta en cada inserción y extracción. Es estado local de una búsqueda.
    """

    def __init__(self):
        self._posiciones = []
        self._costos = []
        self._primer_ids = []
        self._primer_costos = []

    def __len__(self):
        return len(self._posiciones)

    @staticmethod
    def _menor(posicion_a, costo_a, posicion_b, costo_b):
        return (costo_a, posicion_a) < (costo_b, posicion_b)

    def insertar(self, posicion, costo, primer_id, primer_costo):
        self._posiciones.append(posicion)
        self._costos.append(costo)
        self._primer_ids.append(primer_id)
        self._primer_costos.append(primer_costo)

        posiciones = self._posiciones
        costos = self._costos
        primer_ids = self._primer_ids
        primer_costos = self._primer_costos
        indice = len(posiciones) - 1
        while indice > 0:
            padre = (indice - 1) // 2
            if not self._menor(
                posiciones[indice],
                costos[indice],
                posiciones[padre],
                costos[padre],
            ):
                break
            posiciones[indice], posiciones[padre] = (
                posiciones[padre], posiciones[indice]
            )
            costos[indice], costos[padre] = costos[padre], costos[indice]
            primer_ids[indice], primer_ids[padre] = (
                primer_ids[padre], primer_ids[indice]
            )
            primer_costos[indice], primer_costos[padre] = (
                primer_costos[padre], primer_costos[indice]
            )
            indice = padre

    def extraer_minimo(self):
        if len(self._posiciones) == 0:
            raise IndexError("La cola de posiciones está vacía.")

        posiciones = self._posiciones
        costos = self._costos
        primer_ids = self._primer_ids
        primer_costos = self._primer_costos
        resultado = (
            posiciones[0],
            costos[0],
            primer_ids[0],
            primer_costos[0],
        )

        ultima_posicion = posiciones.pop()
        ultimo_costo = costos.pop()
        ultimo_primer_id = primer_ids.pop()
        ultimo_primer_costo = primer_costos.pop()
        if len(posiciones) == 0:
            return resultado

        indice = 0
        cantidad = len(self._posiciones)
        while True:
            izquierdo = indice * 2 + 1
            if izquierdo >= cantidad:
                break
            derecho = izquierdo + 1
            menor = izquierdo
            if (derecho < cantidad
                    and self._menor(
                        posiciones[derecho],
                        costos[derecho],
                        posiciones[izquierdo],
                        costos[izquierdo],
                    )):
                menor = derecho
            if not self._menor(
                posiciones[menor],
                costos[menor],
                ultima_posicion,
                ultimo_costo,
            ):
                break
            posiciones[indice] = posiciones[menor]
            costos[indice] = costos[menor]
            primer_ids[indice] = primer_ids[menor]
            primer_costos[indice] = primer_costos[menor]
            indice = menor

        posiciones[indice] = ultima_posicion
        costos[indice] = ultimo_costo
        primer_ids[indice] = ultimo_primer_id
        primer_costos[indice] = ultimo_primer_costo
        return resultado
