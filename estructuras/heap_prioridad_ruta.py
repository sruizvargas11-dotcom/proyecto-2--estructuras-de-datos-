"""Cola de prioridad propia para búsquedas de rutas ponderadas."""

from estructuras.vector_dinamico import Vector


class ColaPrioridadRuta:
    def __init__(self):
        self._elementos = Vector()

    def __len__(self):
        return len(self._elementos)

    @staticmethod
    def _menor(a, b):
        return (a[1], a[0].id) < (b[1], b[0].id)

    def insertar(self, elemento):
        self._elementos.agregarValor(elemento)
        datos = self._elementos.almacenamiento()
        indice = len(self._elementos) - 1
        clave = (elemento[1], elemento[0].id)
        while indice > 0:
            padre = (indice - 1) // 2
            valor_padre = datos[padre]
            if clave >= (valor_padre[1], valor_padre[0].id):
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
        clave_ultimo = (ultimo[1], ultimo[0].id)
        while True:
            izquierdo = indice * 2 + 1
            if izquierdo >= cantidad:
                break
            derecho = izquierdo + 1
            menor = izquierdo
            if (derecho < cantidad
                    and (datos[derecho][1], datos[derecho][0].id)
                    < (datos[izquierdo][1], datos[izquierdo][0].id)):
                menor = derecho
            hijo = datos[menor]
            if (hijo[1], hijo[0].id) >= clave_ultimo:
                break
            datos[indice] = hijo
            indice = menor
        datos[indice] = ultimo
        return minimo

    def recorrer(self):
        return iter(self._elementos)
