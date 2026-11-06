"""Tabla hash propia con encadenamiento separado (B01).

Asocia claves (texto o entero) con valores sin usar dict ni set. Cada cubeta
es la cabeza de una cadena simple de _EntradaHash; el arreglo de cubetas es
una lista de Python de tamaño fijo usada como almacenamiento contiguo, igual
que en Vector: nunca se agrega ni se quita de ella, solo se reemplaza entera
al crecer.

Complejidad: buscar, insertar y eliminar O(1) esperado; O(n) en el peor caso
(todas las claves en la misma cubeta). Crecer cuesta O(n + m) y es poco
frecuente; repartido entre inserciones es O(1) amortizado.
"""

FNV_DESPLAZAMIENTO = 0x811C9DC5
FNV_PRIMO = 0x01000193
MASCARA_32 = 0xFFFFFFFF
MASCARA_64 = 0xFFFFFFFFFFFFFFFF

CUBETAS_MINIMAS = 8
FACTOR_CARGA_MAXIMO = 0.75


def _fnv1a(datos):
    h = FNV_DESPLAZAMIENTO
    for byte in datos:
        h ^= byte
        h = (h * FNV_PRIMO) & MASCARA_32
    return h


def hash_clave(clave):
    """Hash estable de 32 bits: el mismo valor en cualquier proceso y máquina.

    Acepta texto y enteros (los enteros se reducen a 64 bits en complemento a
    dos). bool y otros tipos se rechazan para no mezclar True con 1.
    """
    if type(clave) is str:
        return _fnv1a(clave.encode('utf-8'))
    if type(clave) is int:
        return _fnv1a((clave & MASCARA_64).to_bytes(8, 'little'))
    raise TypeError(
        f'La tabla hash solo acepta claves de texto o enteras, no {type(clave).__name__}.'
    )


class _EntradaHash:
    """Nodo de una cadena. Guarda el hash para crecer y comparar sin recalcular."""

    def __init__(self, clave, valor_hash, valor, siguiente=None):
        self.clave = clave
        self.valor_hash = valor_hash
        self.valor = valor
        self.siguiente = siguiente


def _cubetas_para(cantidad, factor_carga):
    """Menor potencia de 2 (>= CUBETAS_MINIMAS) que admite cantidad sin crecer."""
    cubetas = CUBETAS_MINIMAS
    while cantidad > cubetas * factor_carga:
        cubetas *= 2
    return cubetas


class TablaHash:
    def __init__(self, capacidad_inicial=CUBETAS_MINIMAS,
                 factor_carga_maximo=FACTOR_CARGA_MAXIMO, funcion_hash=None):
        """capacidad_inicial: claves que deben caber sin crecer.

        funcion_hash existe para las pruebas (forzar colisiones). Con None se
        usa hash_clave y no se guarda ninguna función en el objeto, de modo que
        la tabla se puede guardar con la partida.
        """
        if type(capacidad_inicial) is not int or capacidad_inicial < 0:
            raise ValueError('La capacidad inicial debe ser un entero no negativo.')
        if (type(factor_carga_maximo) not in (int, float)
                or not 0 < factor_carga_maximo <= 1):
            raise ValueError('El factor de carga máximo debe estar en (0, 1].')
        if funcion_hash is not None and not callable(funcion_hash):
            raise ValueError('funcion_hash debe ser invocable.')

        self._factor_carga_maximo = factor_carga_maximo
        self._funcion_hash = funcion_hash
        self._cubetas = [None] * _cubetas_para(capacidad_inicial, factor_carga_maximo)
        self._tamano = 0

        self.contador_busquedas = 0
        self.contador_comparaciones = 0      # claves comparadas dentro de cadenas
        self.contador_inserciones = 0
        self.contador_actualizaciones = 0
        self.contador_eliminaciones = 0
        self.contador_colisiones = 0         # inserciones en una cubeta ya ocupada
        self.contador_redimensionamientos = 0

    def __len__(self):
        return self._tamano

    def esta_vacia(self):
        return self._tamano == 0

    def cantidad_cubetas(self):
        return len(self._cubetas)

    def factor_carga(self):
        return self._tamano / len(self._cubetas)

    # -- internos ---------------------------------------------------------

    def _hash(self, clave):
        if self._funcion_hash is None:
            return hash_clave(clave)
        valor_hash = self._funcion_hash(clave)
        if type(valor_hash) is not int or valor_hash < 0:
            raise ValueError('funcion_hash debe devolver un entero no negativo.')
        return valor_hash

    def _indice(self, valor_hash):
        return valor_hash & (len(self._cubetas) - 1)

    def _localizar(self, clave, valor_hash):
        """Entrada con esa clave, o None. Cuenta comparaciones de clave."""
        entrada = self._cubetas[self._indice(valor_hash)]
        while entrada is not None:
            if entrada.valor_hash == valor_hash:
                self.contador_comparaciones += 1
                if entrada.clave == clave:
                    return entrada
            entrada = entrada.siguiente
        return None

    def _crecer(self):
        """Duplica las cubetas y reubica las mismas entradas. O(n + m)."""
        anteriores = self._cubetas
        self._cubetas = [None] * (len(anteriores) * 2)
        for cabeza in anteriores:
            entrada = cabeza
            while entrada is not None:
                siguiente = entrada.siguiente
                indice = self._indice(entrada.valor_hash)
                entrada.siguiente = self._cubetas[indice]
                self._cubetas[indice] = entrada
                entrada = siguiente
        self.contador_redimensionamientos += 1

    # -- operaciones ------------------------------------------------------

    def obtener(self, clave, defecto=None):
        """Valor asociado a la clave, o defecto si no está. O(1) esperado."""
        self.contador_busquedas += 1
        entrada = self._localizar(clave, self._hash(clave))
        return defecto if entrada is None else entrada.valor

    def contiene(self, clave):
        self.contador_busquedas += 1
        return self._localizar(clave, self._hash(clave)) is not None

    def insertar(self, clave, valor):
        """Asocia clave con valor. True si la clave era nueva, False si se actualizó."""
        valor_hash = self._hash(clave)
        entrada = self._localizar(clave, valor_hash)
        if entrada is not None:
            entrada.valor = valor
            self.contador_actualizaciones += 1
            return False

        if self._tamano + 1 > len(self._cubetas) * self._factor_carga_maximo:
            self._crecer()

        indice = self._indice(valor_hash)
        if self._cubetas[indice] is not None:
            self.contador_colisiones += 1
        self._cubetas[indice] = _EntradaHash(clave, valor_hash, valor, self._cubetas[indice])
        self._tamano += 1
        self.contador_inserciones += 1
        return True

    def eliminar(self, clave):
        """Quita la clave. True si estaba, False si no. O(1) esperado."""
        valor_hash = self._hash(clave)
        indice = self._indice(valor_hash)
        anterior, entrada = None, self._cubetas[indice]
        while entrada is not None:
            if entrada.valor_hash == valor_hash:
                self.contador_comparaciones += 1
                if entrada.clave == clave:
                    if anterior is None:
                        self._cubetas[indice] = entrada.siguiente
                    else:
                        anterior.siguiente = entrada.siguiente
                    entrada.siguiente = None
                    self._tamano -= 1
                    self.contador_eliminaciones += 1
                    return True
            anterior, entrada = entrada, entrada.siguiente
        return False

    def recorrer_claves(self):
        """Claves en orden de cubeta (determinista, no de inserción)."""
        for cabeza in self._cubetas:
            entrada = cabeza
            while entrada is not None:
                yield entrada.clave
                entrada = entrada.siguiente

    # -- diagnóstico ------------------------------------------------------

    def cadena_maxima(self):
        """Longitud de la cadena más larga. O(n + m): solo para reportes."""
        maxima = 0
        for cabeza in self._cubetas:
            largo, entrada = 0, cabeza
            while entrada is not None:
                largo += 1
                entrada = entrada.siguiente
            if largo > maxima:
                maxima = largo
        return maxima

    def cubetas_ocupadas(self):
        ocupadas = 0
        for cabeza in self._cubetas:
            if cabeza is not None:
                ocupadas += 1
        return ocupadas

    def contadores(self):
        """Métricas sin modificar los contadores ni la tabla."""
        return (
            ("busquedas", self.contador_busquedas),
            ("comparaciones", self.contador_comparaciones),
            ("inserciones", self.contador_inserciones),
            ("actualizaciones", self.contador_actualizaciones),
            ("eliminaciones", self.contador_eliminaciones),
            ("colisiones", self.contador_colisiones),
            ("redimensionamientos", self.contador_redimensionamientos),
        )

    def _buscar_sin_contar(self, clave):
        """Para verificaciones: no altera contadores."""
        valor_hash = self._hash(clave)
        entrada = self._cubetas[self._indice(valor_hash)]
        while entrada is not None:
            if entrada.valor_hash == valor_hash and entrada.clave == clave:
                return entrada
            entrada = entrada.siguiente
        return None

    def _verificar_invariantes(self):
        """Lanza AssertionError si la tabla es inconsistente. No altera contadores.

        - la cantidad de cubetas es potencia de 2 y la carga no supera el máximo
        - cada entrada está en la cubeta que indica su hash guardado
        - el hash guardado coincide con el de su clave
        - no hay claves repetidas y el tamaño coincide con las entradas
        """
        m = len(self._cubetas)
        assert m >= CUBETAS_MINIMAS and m & (m - 1) == 0, 'cubetas no es potencia de 2'
        assert self._tamano <= m * self._factor_carga_maximo, 'carga por encima del máximo'
        total = 0
        for indice in range(m):
            entrada = self._cubetas[indice]
            while entrada is not None:
                assert type(entrada) is _EntradaHash, 'entrada de tipo inválido'
                assert entrada.valor_hash == self._hash(entrada.clave), 'hash guardado incorrecto'
                assert self._indice(entrada.valor_hash) == indice, 'entrada en cubeta equivocada'
                otra = entrada.siguiente
                while otra is not None:
                    assert otra.clave != entrada.clave, f'clave repetida: {entrada.clave!r}'
                    otra = otra.siguiente
                total += 1
                assert total <= self._tamano, 'más entradas que el tamaño (¿ciclo?)'
                entrada = entrada.siguiente
        assert total == self._tamano, 'el tamaño no coincide con las entradas'
        return True
