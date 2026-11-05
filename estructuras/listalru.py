"""
Caché LRU sobre una lista doble propia con índice hash propio (B01).

- La ListaDoble conserva el orden de uso: el frente es lo más reciente.
- La TablaHash asocia id_ficha -> NodoDoble de esa lista. Localizar una ficha
  cuesta O(1) esperado; moverla al frente, O(1).
- Desalojar recorre desde el fondo saltando las fichas protegidas
  (en_uso > 0): O(k) en el peor caso, con k = capacidad. Quitar la víctima
  de la lista y del índice es O(1) esperado. El contador
  protegidas_saltadas mide ese costo real.

indice="lineal" conserva la búsqueda anterior (recorrer la lista) con la
misma política de desalojo y protección. Existe para comparar en --bench la
misma caché con y sin índice; el juego usa siempre "hash".

El coordinador deberá persistir las fichas antes de que puedan
ser desalojadas de memoria.
"""

from estructuras.lista_doble import ListaDoble
from estructuras.tabla_hash import TablaHash

INDICES = ("hash", "lineal")


class _EntradaCatalogo:
    def __init__(self, id_ficha, ficha):
        self.id_ficha = id_ficha
        self.ficha = ficha
        self.en_uso = 0


class ListaLRU:
    def __init__(self, capacidad=25, indice="hash"):
        if type(capacidad) is not int or capacidad <= 0:
            raise ValueError(
                "La capacidad debe ser un entero positivo."
            )
        if indice not in INDICES:
            raise ValueError(f"indice debe ser uno de {INDICES}.")

        self._capacidad = capacidad
        self._lista = ListaDoble()
        self._modo_indice = indice
        # Dimensionada para la capacidad: en una partida nunca necesita crecer.
        self._indice = TablaHash(capacidad) if indice == "hash" else None

        self.contador_aciertos = 0
        self.contador_fallos = 0
        self.contador_desalojos = 0
        self.contador_inserciones = 0
        self.contador_actualizaciones = 0
        self.contador_rechazos_capacidad = 0
        self.contador_referencias_adquiridas = 0
        self.contador_referencias_liberadas = 0
        self.contador_comparaciones = 0
        self.contador_protegidas_saltadas = 0

    def __len__(self):
        return len(self._lista)

    # -- índice -----------------------------------------------------------

    def _tabla(self):
        """Índice hash vigente, o None en modo lineal.

        Una ListaLRU cargada de un guardado anterior a B01 no tiene índice:
        se reconstruye una sola vez a partir de la lista (O(k)), sin cambiar
        el orden, las fichas ni sus referencias. Así no hace falta cambiar el
        esquema del guardado.
        """
        if not hasattr(self, "_modo_indice"):
            self._modo_indice = "hash"
            self._indice = None
            self.contador_protegidas_saltadas = 0
        if self._modo_indice == "lineal":
            return None
        if self._indice is None:
            self._reconstruir_indice()
        return self._indice

    def _reconstruir_indice(self):
        tabla = TablaHash(max(self._capacidad, len(self._lista)))
        nodo = self._lista.head()
        while nodo is not None:
            tabla.insertar(nodo.valor.id_ficha, nodo)
            nodo = nodo.siguiente
        self._indice = tabla

    def _nodo(self, id_ficha):
        """Localiza una entrada sin cambiar su orden ni los aciertos/fallos."""
        tabla = self._tabla()

        if tabla is None:
            for nodo in self._lista.recorrer_desde_frente():
                self.contador_comparaciones += 1
                if nodo.valor.id_ficha == id_ficha:
                    return nodo
            return None

        antes = tabla.contador_comparaciones
        nodo = tabla.obtener(id_ficha)
        self.contador_comparaciones += tabla.contador_comparaciones - antes
        return nodo

    # -- operaciones ------------------------------------------------------

    def buscar(self, id_ficha):
        """Devuelve la ficha y la marca como recientemente consultada."""
        nodo = self._nodo(id_ficha)

        if nodo is None:
            self.contador_fallos += 1
            return None

        self.contador_aciertos += 1
        self._lista.mover_al_frente(nodo)

        return nodo.valor.ficha

    # Permite usar también el nombre empleado en el plan.
    obtener = buscar

    def contiene(self, id_ficha):
        """True si la ficha está en memoria; no cambia orden ni aciertos/fallos."""
        return self._nodo(id_ficha) is not None

    def insertar(self, id_ficha, ficha):
        """
        Devuelve True si la ficha quedó almacenada.

        Devuelve False si no hay espacio y todas las fichas
        existentes están protegidas.
        """
        if ficha is None:
            raise ValueError(
                "None se reserva para indicar una ficha ausente."
            )

        existente = self._nodo(id_ficha)

        if existente is not None:
            if (
                existente.valor.en_uso > 0
                and existente.valor.ficha is not ficha
            ):
                raise ValueError(
                    "No se sustituye una ficha mientras esté en uso."
                )

            existente.valor.ficha = ficha
            self._lista.mover_al_frente(existente)
            self.contador_actualizaciones += 1
            return True

        if len(self) >= self._capacidad:
            if not self._desalojar_si_es_posible():
                self.contador_rechazos_capacidad += 1
                return False

        entrada = _EntradaCatalogo(id_ficha, ficha)
        nodo = self._lista.insertar_al_frente(entrada)
        tabla = self._tabla()
        if tabla is not None:
            tabla.insertar(id_ficha, nodo)
        self.contador_inserciones += 1

        return True

    def marcar_en_uso(self, id_ficha):
        """Registra una nueva referencia activa a la ficha."""
        nodo = self._nodo(id_ficha)

        if nodo is None:
            raise KeyError(id_ficha)

        nodo.valor.en_uso += 1
        self.contador_referencias_adquiridas += 1

    def desmarcar_en_uso(self, id_ficha):
        """Libera una referencia activa, sin permitir valores negativos."""
        nodo = self._nodo(id_ficha)

        if nodo is None:
            raise KeyError(id_ficha)

        if nodo.valor.en_uso == 0:
            raise ValueError(
                "La ficha no tenía referencias activas."
            )

        nodo.valor.en_uso -= 1
        self.contador_referencias_liberadas += 1

    def _desalojar_si_es_posible(self):
        """Retira la ficha libre menos recientemente utilizada."""
        tabla = self._tabla()
        for nodo in self._lista.recorrer_desde_fondo():
            if nodo.valor.en_uso == 0:
                self._lista.eliminar_nodo(nodo)
                if tabla is not None:
                    tabla.eliminar(nodo.valor.id_ficha)
                self.contador_desalojos += 1
                return True
            self.contador_protegidas_saltadas += 1

        return False

    # -- métricas ---------------------------------------------------------

    def contadores(self):
        """Consultar las métricas no cambia el orden de la caché."""
        return (
            self.contador_aciertos,
            self.contador_fallos,
            self.contador_desalojos,
        )

    def contadores_operaciones(self):
        """Detalle adicional; contadores() conserva su contrato original."""
        self._tabla()
        return (
            ("busquedas", self.contador_aciertos + self.contador_fallos),
            ("aciertos", self.contador_aciertos),
            ("fallos", self.contador_fallos),
            ("desalojos", self.contador_desalojos),
            ("inserciones", self.contador_inserciones),
            ("actualizaciones", self.contador_actualizaciones),
            ("rechazos_capacidad", self.contador_rechazos_capacidad),
            ("referencias_adquiridas", self.contador_referencias_adquiridas),
            ("referencias_liberadas", self.contador_referencias_liberadas),
            ("comparaciones", self.contador_comparaciones),
            ("protegidas_saltadas", self.contador_protegidas_saltadas),
        )

    def estadisticas_indice(self):
        """Métricas propias del índice (no repite aciertos/fallos/desalojos).

        Prefijo indice_ para no chocar con las claves que ya usa el reporte.
        Calcular la cadena máxima es O(k + m); solo se usa al reportar.
        """
        tabla = self._tabla()
        if tabla is None:
            return (
                ("indice_modo", "lineal"),
                ("indice_protegidas_saltadas", self.contador_protegidas_saltadas),
            )
        busquedas = tabla.contador_busquedas
        return (
            ("indice_modo", "hash"),
            ("indice_cubetas", tabla.cantidad_cubetas()),
            ("indice_factor_carga", round(tabla.factor_carga(), 3)),
            ("indice_colisiones", tabla.contador_colisiones),
            ("indice_cadena_maxima", tabla.cadena_maxima()),
            ("indice_redimensionamientos", tabla.contador_redimensionamientos),
            ("indice_comparaciones_por_busqueda",
             round(tabla.contador_comparaciones / busquedas, 3) if busquedas else 0),
            ("indice_protegidas_saltadas", self.contador_protegidas_saltadas),
        )

    # -- verificación -----------------------------------------------------

    def _verificar_invariantes(self):
        """Lanza AssertionError si lista e índice no están sincronizados.

        No cambia orden ni contadores (recorre los enlaces directamente):
        - tamaño dentro de la capacidad y referencias en_uso no negativas
        - cada nodo pertenece a la lista y su id aparece una sola vez
        - en modo hash: mismo tamaño en índice y lista, y cada id del índice
          apunta exactamente a su nodo
        """
        tabla = self._tabla()
        assert len(self._lista) <= self._capacidad, "más fichas que la capacidad"
        vistos = TablaHash(len(self._lista))
        contados, nodo = 0, self._lista.head()
        while nodo is not None:
            assert self._lista.pertenece(nodo), "nodo ajeno a la lista"
            entrada = nodo.valor
            assert type(entrada) is _EntradaCatalogo, "entrada de tipo inválido"
            assert type(entrada.en_uso) is int and entrada.en_uso >= 0, "en_uso inválido"
            assert entrada.ficha is not None, "ficha ausente en la caché"
            assert vistos.insertar(entrada.id_ficha, True), \
                f"id repetido en la lista: {entrada.id_ficha!r}"
            if tabla is not None:
                indexada = tabla._buscar_sin_contar(entrada.id_ficha)
                assert indexada is not None, f"id sin índice: {entrada.id_ficha!r}"
                assert indexada.valor is nodo, f"el índice apunta a otro nodo: {entrada.id_ficha!r}"
            contados += 1
            nodo = nodo.siguiente
        assert contados == len(self._lista), "longitud de lista incorrecta"
        if tabla is not None:
            assert len(tabla) == len(self._lista), "índice y lista de distinto tamaño"
            tabla._verificar_invariantes()
        return True
