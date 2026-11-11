"""Benchmark headless de rutas de costo para el cazador."""

import hashlib
import json
import os
import platform
import sys
import time
from datetime import datetime
from pathlib import Path

from modelo.entidades.enemigo import Enemigo
from modelo.entidades.jugador import Jugador
from modelo.mundo.cripta_modelo import CriptaModelo
from modelo.mundo.sala import Sala
from modelo.mundo.salida import Salida
from modelo.ejecutor_evento import EjecutorEvento
from modelo.partida import EN_CURSO, Partida
from modelo.reloj import Reloj


ROOT = Path(__file__).resolve().parent.parent
FIXTURE = ROOT / "bench" / "datos" / "bench-terreno-cazador-grid-16x16-v1.0.0.json"
INF = 10 ** 30


def _fixture():
    contenido = FIXTURE.read_bytes()
    return json.loads(contenido.decode("utf-8")), hashlib.sha256(contenido).hexdigest()


def _grafo(datos):
    salas = datos["salas"]
    vecinos = [[] for _ in range(len(salas) + 1)]
    for sala in salas:
        for direccion, salida in sala["salidas"].items():
            vecinos[sala["id"]].append(
                (salida["sala"], salida["costo"], direccion)
            )
    return vecinos


def _cola_insertar(cola, elemento):
    cola.append(elemento)
    indice = len(cola) - 1
    while indice:
        padre = (indice - 1) // 2
        if cola[padre] <= elemento:
            break
        cola[indice] = cola[padre]
        indice = padre
    cola[indice] = elemento


def _cola_extraer(cola):
    minimo = cola[0]
    ultimo = cola.pop()
    if cola:
        indice = 0
        while True:
            izquierdo = indice * 2 + 1
            if izquierdo >= len(cola):
                break
            derecho = izquierdo + 1
            menor = izquierdo
            if derecho < len(cola) and cola[derecho] < cola[izquierdo]:
                menor = derecho
            if cola[menor] >= ultimo:
                break
            cola[indice] = cola[menor]
            indice = menor
        cola[indice] = ultimo
    return minimo


def _puertas(datos, vecinos):
    resultado = []
    for puerta in datos["puertas"]:
        extremos = []
        for extremo in datos["puertas_extremos"][puerta]:
            origen, destino = extremo
            for indice, vecino in enumerate(vecinos[origen]):
                if vecino[0] == destino:
                    extremos.append((origen, indice))
        resultado.append(extremos)
    return resultado


def _distancias_desde_jugador(vecinos, jugador, cerradas):
    distancias = [INF] * len(vecinos)
    distancias[jugador] = 0
    entrantes = [[] for _ in vecinos]
    for origen in range(1, len(vecinos)):
        for indice, vecino in enumerate(vecinos[origen]):
            if (origen, indice) not in cerradas:
                entrantes[vecino[0]].append((origen, vecino[1]))
    cola = [(0, jugador)]
    while cola:
        costo_actual, actual = _cola_extraer(cola)
        if costo_actual != distancias[actual]:
            continue
        for origen, costo in entrantes[actual]:
            candidato = costo_actual + costo
            if candidato < distancias[origen]:
                distancias[origen] = candidato
                _cola_insertar(cola, (candidato, origen))
    return distancias


def _distancia_individual(vecinos, origen, jugador, cerradas):
    distancias = [INF] * len(vecinos)
    distancias[origen] = 0
    cola = [(0, origen)]
    while cola:
        costo_actual, actual = _cola_extraer(cola)
        if costo_actual != distancias[actual]:
            continue
        if costo_actual > rango:
            break
        if actual == jugador:
            break
        for indice, vecino in enumerate(vecinos[actual]):
            if (actual, indice) in cerradas:
                continue
            candidato = costo_actual + vecino[1]
            if candidato < distancias[vecino[0]]:
                distancias[vecino[0]] = candidato
                _cola_insertar(cola, (candidato, vecino[0]))
    return distancias[jugador]


def _decision_individual(vecinos, origen, jugador, rango, cerradas):
    if origen == jugador:
        return ("atacar", origen)
    distancias = [INF] * len(vecinos)
    primera_sala = [None] * len(vecinos)
    primer_costo = [None] * len(vecinos)
    distancias[origen] = 0
    cola = [(0, origen)]
    while cola:
        costo_actual, actual = _cola_extraer(cola)
        if costo_actual != distancias[actual]:
            continue
        if actual == jugador:
            break
        for indice, vecino in enumerate(vecinos[actual]):
            if (actual, indice) in cerradas:
                continue
            destino, costo, _ = vecino
            candidato = costo_actual + costo
            if candidato > rango:
                continue
            primera = destino if actual == origen else primera_sala[actual]
            primer_tramo = costo if actual == origen else primer_costo[actual]
            if (candidato < distancias[destino]
                    or (candidato == distancias[destino]
                        and (primera_sala[destino] is None
                             or primera < primera_sala[destino]))):
                distancias[destino] = candidato
                primera_sala[destino] = primera
                primer_costo[destino] = primer_tramo
                _cola_insertar(cola, (candidato, destino))
    if distancias[jugador] > rango or distancias[jugador] >= INF:
        return ("esperar", origen)
    return ("mover", (primera_sala[jugador], primer_costo[jugador]))


def _decision(vecinos, origen, jugador, rango, cerradas, distancias=None):
    dist = (distancias[origen] if distancias is not None
            else _distancia_individual(vecinos, origen, jugador, cerradas))
    if origen == jugador:
        return ("atacar", origen)
    if dist > rango or dist >= INF:
        return ("esperar", origen)
    mejor = None
    for indice, vecino in enumerate(vecinos[origen]):
        if (origen, indice) in cerradas:
            continue
        destino, costo, _ = vecino
        restante = (distancias[destino] if distancias is not None
                    else _distancia_individual(vecinos, destino, jugador, cerradas))
        if costo + restante != dist:
            continue
        if mejor is None or destino < mejor[0]:
            mejor = (destino, costo)
    return ("mover", mejor) if mejor is not None else ("esperar", origen)


def _estado(datos, rangos):
    posiciones = list(datos["estado_inicial"]["cazadores"]["salas"])
    rangos_actores = []
    for rango in rangos:
        for _ in range(10):
            rangos_actores.append(rango)
    return posiciones, rangos_actores


def _alternar_puerta(cerradas, puerta):
    for extremo in puerta:
        if extremo in cerradas:
            cerradas.remove(extremo)
        else:
            cerradas.append(extremo)


def _debe_alternar_puerta(ciclo, frecuencia):
    return ciclo % frecuencia == 0


def _registrar_observacion(enemigo, accion, posiciones, indice):
    destino = enemigo.sala_actual.id
    if accion == "mover":
        observacion = ("mover", (destino, enemigo.costo_ultima_accion))
    elif accion == "atacar":
        observacion = ("atacar", destino)
    else:
        observacion = ("esperar", destino)
    posiciones[indice] = destino
    return enemigo.instancia_id, observacion


def _crear_partida(datos, rangos):
    salas = []
    for dato in datos["salas"]:
        salas.append(Sala(dato["id"], "Sala " + str(dato["id"])))
    cripta = CriptaModelo(
        datos["identidad"], datos["version"], 136, 256, None, 0, 10
    )
    for sala in salas:
        cripta.agregar_sala(sala)
    for dato, sala in zip(datos["salas"], salas):
        for direccion, salida in dato["salidas"].items():
            sala.salidas.insertar_al_final(
                Salida(direccion, salida["sala"], costo=salida["costo"])
            )
    cripta.finalizar_carga()
    jugador = Jugador("jugador-bench", 1000000000, 10, 5, 100, 10,
                      cripta.sala_por_id(136))
    partida = Partida(cripta, jugador, datos["semilla"])
    partida.inicializar()
    enemigos = []
    posiciones = datos["estado_inicial"]["cazadores"]["salas"]
    rangos_actores = []
    for rango in rangos:
        for _ in range(10):
            rangos_actores.append(rango)
    for indice, sala_id in enumerate(posiciones):
        enemigo = Enemigo(
            "cazador-%02d" % (indice + 1), "bench-cazador",
            "Cazador de benchmark", 100, 1, 0, 100, "cazador",
            cripta.sala_por_id(sala_id), rango=rangos_actores[indice]
        )
        enemigo.sala_actual.enemigos_activos.insertar_al_final(enemigo)
        partida.reloj.vincular_actor(enemigo)
        partida.reloj.programar(
            enemigo, 100, partida.ejecutor_enemigo(enemigo)
        )
        enemigos.append(enemigo)
    return partida, enemigos


def _alternar_puerta_produccion(partida, datos, nombre):
    for origen, destino in datos["puertas_extremos"][nombre]:
        sala = partida.cripta.sala_por_id(origen)
        salida = next(s for s in sala.salidas if s.sala_destino_id == destino)
        salida.cerrada = not salida.cerrada


def _correr_escenario(datos, vecinos, puertas, rangos, frecuencia, modalidad):
    partida, enemigos = _crear_partida(datos, rangos)
    posiciones = list(datos["estado_inicial"]["cazadores"]["salas"])
    jugador = datos["estado_inicial"]["jugador"]["sala"]
    cerradas = []
    duraciones = []
    discrepancias = []
    puerta_actual = 0
    for ciclo in range(1, 1001):
        referencia_posiciones = list(posiciones)
        inicio = time.perf_counter_ns()
        if _debe_alternar_puerta(ciclo, frecuencia):
            _alternar_puerta(cerradas, puertas[puerta_actual])
            _alternar_puerta_produccion(
                partida, datos, datos["puertas"][puerta_actual]
            )
            puerta_actual = (puerta_actual + 1) % len(puertas)
        observadas = []
        distancias = (
            partida.cache_rutas_cazador.obtener(partida.jugador)
            if modalidad == "compartida" else None
        )
        entrada_jugador = partida.reloj.proximo()
        if entrada_jugador is not partida.jugador.evento_actual:
            raise RuntimeError("El ciclo no comenzó en la decisión del jugador.")
        partida.reloj.tiempo_actual = entrada_jugador.tiempo
        partida.reloj.tomar_turno(partida.jugador)
        partida.contar_accion_jugador()
        partida.refrescar_rastro()
        partida.programar_siguiente_jugador(100)
        while partida.reloj.proximo() is not partida.jugador.evento_actual:
            entrada = partida.reloj.extraer_siguiente()
            enemigo = entrada.dato.dueno
            indice = enemigos.index(enemigo)
            accion = partida.ejecutar_accion_enemigo(
                enemigo, usar_cache=modalidad == "compartida",
                distancias=distancias
            )
            observadas.append(_registrar_observacion(
                enemigo, accion, posiciones, indice
            ))
            partida.programar_siguiente_enemigo(
                enemigo, enemigo.costo_ultima_accion
            )
        duraciones.append(time.perf_counter_ns() - inicio)
        referencia = []
        for instancia_id, observada in observadas:
            indice = next(
                i for i, enemigo in enumerate(enemigos)
                if enemigo.instancia_id == instancia_id
            )
            esperada = _decision_individual(
                vecinos, referencia_posiciones[indice], jugador,
                (rangos[0] if indice < 10 else rangos[1]), cerradas
            )
            referencia.append((instancia_id, esperada))
            if observada != esperada:
                discrepancias.append({
                    "ciclo": ciclo,
                    "cazador": instancia_id,
                    "esperada": esperada,
                    "observada": observada,
                })
            if observada[0] == "mover":
                referencia_posiciones[indice] = observada[1][0]
    return duraciones, discrepancias


def crear_reporte(ruta):
    datos, checksum = _fixture()
    vecinos = _grafo(datos)
    puertas = _puertas(datos, vecinos)
    escenarios = []
    for nombre, rangos in (("pequeno", [1, 100]), ("grande", [1000, 10000])):
        for frecuencia in (1, 100):
            for modalidad in ("individual", "compartida"):
                repeticiones = []
                for numero in range(1, 31):
                    duraciones, discrepancias = _correr_escenario(
                        datos, vecinos, puertas, rangos, frecuencia, modalidad
                    )
                    repeticiones.append({
                        "numero": numero,
                        "duraciones_ciclo_ns": duraciones,
                        "maximo_ciclo_ns": max(duraciones),
                        "discrepancias": discrepancias,
                    })
                    print(
                        "Benchmark %s/%s, frecuencia %s, %s: repeticion %s/30"
                        % (nombre, rangos, frecuencia, modalidad, numero),
                        flush=True,
                    )
                escenarios.append({
                    "perfil_rango": nombre,
                    "rangos": rangos,
                    "cambio_puerta_cada_ciclos": frecuencia,
                    "modalidad": modalidad,
                    "repeticiones": repeticiones,
                })
    equipo = {
        "sistema_operativo": platform.platform(),
        "procesador": platform.processor() or platform.machine(),
        "nucleos": os.cpu_count() or 1,
        "memoria_bytes": _memoria_instalada(),
        "entorno_ejecucion": "python",
        "version_entorno": sys.version,
        "perfil_energia": "no disponible",
    }
    reporte = {
        "benchmark": "terreno-y-cazador",
        "fecha": datetime.now().isoformat(timespec="seconds"),
        "fixture": {
            "identidad": datos["identidad"],
            "version": datos["version"],
            "sha256": checksum,
            "filas": datos["filas"],
            "columnas": datos["columnas"],
            "salas": 256,
            "conexiones": 480,
        },
        "equipo": equipo,
        "semilla": datos["semilla"],
        "estado_inicial": datos["estado_inicial"],
        "escenarios": escenarios,
        "cumple_umbral": all(
            repeticion["maximo_ciclo_ns"] <= 20_000_000
            for escenario in escenarios
            for repeticion in escenario["repeticiones"]
        ),
        "decisiones_correctas": all(
            not repeticion["discrepancias"]
            for escenario in escenarios
            for repeticion in escenario["repeticiones"]
        ),
    }
    destino = Path(ruta)
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(
        json.dumps(reporte, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return reporte


def _memoria_instalada():
    if sys.platform != "win32":
        return 0
    import ctypes

    class EstadoMemoria(ctypes.Structure):
        _fields_ = [
            ("longitud", ctypes.c_ulong),
            ("porcentaje", ctypes.c_ulong),
            ("total", ctypes.c_ulonglong),
            ("libre", ctypes.c_ulonglong),
            ("total_archivo", ctypes.c_ulonglong),
            ("libre_archivo", ctypes.c_ulonglong),
            ("total_virtual", ctypes.c_ulonglong),
            ("libre_virtual", ctypes.c_ulonglong),
            ("libre_virtual_ext", ctypes.c_ulonglong),
        ]

    estado = EstadoMemoria()
    estado.longitud = ctypes.sizeof(EstadoMemoria)
    if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(estado)):
        return estado.total
    return 0
