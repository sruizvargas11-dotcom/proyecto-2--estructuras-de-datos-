"""Datos sintéticos y referencia lenta para verificar alcanzabilidad."""

import random
from dataclasses import dataclass

from estructuras.cola import Cola
from estructuras.ordenamientos import ordenar
from estructuras.tabla_hash import TablaHash
from estructuras.vector_dinamico import Vector
from bench.medicion import Fila, medir
from modelo.mundo.cripta_modelo import CriptaModelo
from modelo.mundo.sala import Sala
from modelo.mundo.salida import Salida
from modelo.verificador_resolubilidad import verificar_resolubilidad


SEMILLA_BENCH = 42
TAMANOS_BENCH = (96, 192, 384)
REPETICIONES_BENCH = 50


@dataclass(frozen=True)
class UbicacionLlave:
    id: str
    sala: int
    enemigo: str = None


@dataclass(frozen=True)
class CriptaSintetica:
    cripta: CriptaModelo
    ubicaciones: tuple
    semilla: int
    estructura: str


@dataclass(frozen=True)
class PuertaReferencia:
    origen: int
    direccion: str
    destino: int
    llave: str = None


@dataclass(frozen=True)
class ResultadoReferencia:
    veredicto: str
    orden_por_rondas: tuple
    puerta_final: object
    salas_alcanzables: tuple
    frontera: tuple
    recorridos_completos: int


def _comparar_ids(a, b):
    return (a > b) - (a < b)


def _comparar_ubicaciones(a, b):
    por_sala = _comparar_ids(a.sala, b.sala)
    if por_sala:
        return por_sala
    return _comparar_ids(a.id, b.id)


def _comparar_puertas(a, b):
    por_origen = _comparar_ids(a.origen, b.origen)
    if por_origen:
        return por_origen
    return _comparar_ids(a.direccion, b.direccion)


def _ordenar(vector, comparar):
    ordenar(vector, comparar)
    return tuple(vector.obtenerValor(i) for i in range(len(vector)))


def generar_cripta_sintetica(
    semilla=42,
    cantidad_llaves=8,
    estructura="cadena",
    duplicar_topologia=False,
):
    """Genera una cripta dirigida, no densa y repetible a partir de una semilla."""
    if type(semilla) is not int:
        raise ValueError("La semilla debe ser un entero.")
    if type(cantidad_llaves) is not int or cantidad_llaves < 1:
        raise ValueError("cantidad_llaves debe ser un entero positivo.")
    if type(duplicar_topologia) is not bool:
        raise ValueError("duplicar_topologia debe ser booleano.")
    if estructura not in ("cadena", "ciclo", "alternativa"):
        raise ValueError("estructura debe ser cadena, ciclo o alternativa.")
    if estructura != "cadena" and cantidad_llaves < 2:
        raise ValueError("Las estructuras ciclo y alternativa requieren dos llaves.")
    if duplicar_topologia and (estructura != "cadena" or cantidad_llaves < 4):
        raise ValueError(
            "La duplicación de topología requiere cadena y al menos cuatro llaves."
        )

    azar = random.Random(semilla)
    base = 100 + (semilla % 17) * 3
    cantidad_salas = (
        cantidad_llaves * 2
        if duplicar_topologia
        else cantidad_llaves + 2
    )
    ids_salas = [base + indice * 3 for indice in range(cantidad_salas)]
    salas = [Sala(sala_id, f"Sala sintética {indice}")
             for indice, sala_id in enumerate(ids_salas)]
    ids_llaves = [f"llave-{indice:04d}" for indice in range(cantidad_llaves)]
    ubicaciones = []

    def agregar_salida(origen, destino, direccion, llave=None):
        salas[origen].salidas.insertar_al_final(
            Salida(
                direccion,
                ids_salas[destino],
                cerrada=llave is not None,
                llave=llave,
                costo=azar.randint(1, 1000),
            )
        )

    if estructura == "cadena":
        agregar_salida(0, 1, "A")
        for indice in range(1, cantidad_llaves):
            agregar_salida(indice, indice + 1, "A", ids_llaves[indice - 1])
        for indice, llave_id in enumerate(ids_llaves):
            ubicaciones.append(UbicacionLlave(llave_id, ids_salas[indice + 1]))
        if duplicar_topologia:
            primera_lateral = cantidad_llaves + 2
            agregar_salida(0, primera_lateral, "X")
            for indice in range(primera_lateral, cantidad_salas - 1):
                agregar_salida(indice, indice + 1, "Y")
            agregar_salida(cantidad_salas - 1, 0, "Z")
    elif estructura == "ciclo":
        agregar_salida(0, 1, "A", ids_llaves[1])
        agregar_salida(0, 2, "B", ids_llaves[0])
        for indice in range(2, cantidad_llaves):
            agregar_salida(indice, indice + 1, "A", ids_llaves[indice - 1])
        for indice, llave_id in enumerate(ids_llaves):
            ubicaciones.append(UbicacionLlave(llave_id, ids_salas[indice + 1]))
    else:
        agregar_salida(0, 1, "A")
        agregar_salida(0, 1, "B", ids_llaves[1])
        agregar_salida(1, 2, "C", ids_llaves[0])
        for indice in range(2, cantidad_llaves):
            agregar_salida(indice, indice + 1, "A", ids_llaves[indice - 1])
        for indice, llave_id in enumerate(ids_llaves):
            ubicaciones.append(UbicacionLlave(llave_id, ids_salas[indice + 1]))

    agregar_salida(
        cantidad_llaves,
        cantidad_llaves + 1,
        "Z",
        ids_llaves[-1],
    )
    cripta = CriptaModelo(
        f"sintetica-{semilla}-{estructura}-{cantidad_llaves}",
        f"semilla-{semilla}",
        ids_salas[0],
        ids_salas[cantidad_llaves + 1],
        ids_llaves[-1],
        presupuesto_solicitudes=0,
        inventario_max=0,
    )
    for sala in salas:
        cripta.agregar_sala(sala)
    cripta.finalizar_carga()
    return CriptaSintetica(cripta, tuple(ubicaciones), semilla, estructura)


def _alcanzables(cripta, llaves):
    """Recorre desde el inicio usando las llaves actuales, sin inferir arcos inversos."""
    visitadas = TablaHash(capacidad_inicial=len(cripta))
    cola = Cola()
    inicial = cripta.sala_por_id(cripta.sala_inicial_id)
    if inicial is None:
        return visitadas
    visitadas.insertar(inicial.id, True)
    cola.encolar(inicial)
    while not cola.esta_vacia():
        sala = cola.desencolar()
        for salida in sala.salidas:
            if salida.cerrada and (
                salida.llave is None or not llaves.contiene(salida.llave)
            ):
                continue
            destino = salida.sala_destino
            if destino is not None and not visitadas.contiene(destino.id):
                visitadas.insertar(destino.id, True)
                cola.encolar(destino)
    return visitadas


def _ubicacion_alcanzable(ubicaciones, llave_id, region):
    elegida = None
    for ubicacion in ubicaciones:
        if ubicacion.id != llave_id or not region.contiene(ubicacion.sala):
            continue
        if elegida is None or ubicacion.sala < elegida.sala:
            elegida = ubicacion
        elif ubicacion.sala == elegida.sala:
            if elegida.enemigo is not None and ubicacion.enemigo is None:
                elegida = ubicacion
            elif (
                elegida.enemigo is not None
                and ubicacion.enemigo is not None
                and ubicacion.enemigo < elegida.enemigo
            ):
                elegida = ubicacion
    return elegida


def _nuevas_llaves(cripta, ubicaciones, llaves_adquiridas):
    region = _alcanzables(cripta, llaves_adquiridas)
    candidatas = TablaHash(capacidad_inicial=len(ubicaciones))
    ids_candidatos = Vector()
    for ubicacion in ubicaciones:
        if (
            region.contiene(ubicacion.sala)
            and not llaves_adquiridas.contiene(ubicacion.id)
            and not candidatas.contiene(ubicacion.id)
        ):
            candidatas.insertar(ubicacion.id, True)
            ids_candidatos.agregarValor(ubicacion.id)

    nuevas = Vector()
    recorridos = 1
    for indice in range(len(ids_candidatos)):
        llave_id = ids_candidatos.obtenerValor(indice)
        recorridos += 1
        region_repetida = _alcanzables(cripta, llaves_adquiridas)
        ubicacion = _ubicacion_alcanzable(ubicaciones, llave_id, region_repetida)
        if ubicacion is not None:
            nuevas.agregarValor(ubicacion)
    return _ordenar(nuevas, _comparar_ubicaciones), recorridos


def _puerta_final(cripta, llaves, region):
    candidatas = Vector()
    for sala in cripta.recorrer_salas():
        if not region.contiene(sala.id):
            continue
        for salida in sala.salidas:
            if (
                salida.cerrada
                and salida.llave == cripta.llave_salida
                and llaves.contiene(cripta.llave_salida)
                and salida.sala_destino_id == cripta.sala_salida_id
            ):
                candidatas.agregarValor(PuertaReferencia(
                    sala.id,
                    salida.direccion,
                    salida.sala_destino_id,
                    salida.llave,
                ))
    if len(candidatas) == 0:
        return None
    return _ordenar(candidatas, _comparar_puertas)[0]


def _frontera(cripta, llaves, region):
    puertas = Vector()
    for sala in cripta.recorrer_salas():
        if not region.contiene(sala.id):
            continue
        for salida in sala.salidas:
            if (
                salida.cerrada
                and salida.sala_destino_id is not None
                and not region.contiene(salida.sala_destino_id)
                and (
                    salida.llave is None
                    or not llaves.contiene(salida.llave)
                )
            ):
                puertas.agregarValor(PuertaReferencia(
                    sala.id,
                    salida.direccion,
                    salida.sala_destino_id,
                    salida.llave,
                ))
    return _ordenar(puertas, _comparar_puertas)


def recorrido_completo_repetido(cripta, ubicaciones):
    """Referencia lenta: vuelve a recorrer la cripta por cada llave candidata."""
    llaves_adquiridas = TablaHash(capacidad_inicial=len(ubicaciones))
    rondas = []
    recorridos = 0

    while True:
        nuevas, cantidad_recorridos = _nuevas_llaves(
            cripta, ubicaciones, llaves_adquiridas
        )
        recorridos += cantidad_recorridos
        rondas.append(nuevas)
        for ubicacion in nuevas:
            llaves_adquiridas.insertar(ubicacion.id, True)

        region = _alcanzables(cripta, llaves_adquiridas)
        recorridos += 1
        puerta_final = _puerta_final(cripta, llaves_adquiridas, region)
        if puerta_final is not None:
            veredicto = "RESOLUBLE"
            break
        if len(nuevas) == 0:
            veredicto = "NO RESOLUBLE"
            break

    salas = Vector()
    for sala in cripta.recorrer_salas():
        if region.contiene(sala.id):
            salas.agregarValor(sala.id)
    salas_ordenadas = _ordenar(salas, _comparar_ids)
    return ResultadoReferencia(
        veredicto,
        tuple(rondas),
        puerta_final,
        salas_ordenadas,
        _frontera(cripta, llaves_adquiridas, region),
        recorridos,
    )


def _firma(resultado):
    rondas = tuple(
        tuple((llave.id, llave.sala, llave.enemigo) for llave in ronda)
        for ronda in resultado.orden_por_rondas
    )
    puerta = resultado.puerta_final
    puerta_final = (
        None
        if puerta is None
        else (puerta.origen, puerta.direccion, puerta.destino, puerta.llave)
    )
    frontera = getattr(resultado, "frontera_bloqueada", None)
    if frontera is None:
        frontera = resultado.frontera
    puertas = tuple(
        (puerta.origen, puerta.direccion, puerta.destino, puerta.llave)
        for puerta in frontera
    )
    return resultado.veredicto, rondas, puerta_final, puertas


def validar_equivalencia(sintetica):
    """Compara resultados completos antes de iniciar cualquier medición."""
    incremental = verificar_resolubilidad(
        sintetica.cripta, sintetica.ubicaciones
    )
    referencia = recorrido_completo_repetido(
        sintetica.cripta, sintetica.ubicaciones
    )
    if _firma(incremental) != _firma(referencia):
        raise ValueError(
            "El benchmark de resolubilidad detectó discrepancias antes de medir."
        )
    return incremental, referencia


def correr():
    """Mide la verificación incremental frente al recorrido repetido de referencia."""
    filas = []
    for cantidad_llaves in TAMANOS_BENCH:
        sintetica = generar_cripta_sintetica(
            SEMILLA_BENCH,
            cantidad_llaves,
            "cadena",
            duplicar_topologia=True,
        )
        _, referencia = validar_equivalencia(sintetica)
        salas = len(sintetica.cripta)
        salidas = 0
        for sala in sintetica.cripta.recorrer_salas():
            salidas += len(sala.salidas)
        extra = (
            f"S={salas} E={salidas} K={cantidad_llaves} "
            f"semilla={SEMILLA_BENCH}"
        )
        filas.append(
            Fila.desde_medicion(
                "resolubilidad",
                "incremental",
                cantidad_llaves,
                medir(
                    verificar_resolubilidad,
                    sintetica.cripta,
                    sintetica.ubicaciones,
                    repeticiones=REPETICIONES_BENCH,
                ),
                extra=extra,
            )
        )
        filas.append(
            Fila.desde_medicion(
                "resolubilidad",
                "referencia",
                cantidad_llaves,
                medir(
                    recorrido_completo_repetido,
                    sintetica.cripta,
                    sintetica.ubicaciones,
                    repeticiones=REPETICIONES_BENCH,
                ),
                extra=f"{extra} recorridos={referencia.recorridos_completos}",
            )
        )
    return filas
