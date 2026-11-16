"""Mediciones reproducibles de consulta y almacenamiento de la linea de tiempo."""
import gc
import json
import os
import tempfile
import tracemalloc

from adaptadores.datos_offline import DatosOffline
from bench.medicion import Fila, estadisticas, medir
from controlador.inicio_partida import nueva_partida
from modelo.historia import Historia, K_POR_DEFECTO
from modelo.reconstructor_historia import ReconstructorHistoria
from persistencia.estado_partida import codificar, decodificar

ACCIONES_BENCH = 5000
K_EVALUADOS = (10, 50, 100, 200)
CONSULTAS_POR_TIPO = 15
REPETICIONES_BENCH = 30
REPETICIONES_REFERENCIA_BENCH = 3
UMBRAL_P95_MS = 50.0
COSTO_ESPERAR = 100


def _construir_historia(k, cantidad):
    with tempfile.TemporaryDirectory() as carpeta:
        sesion = nueva_partida(
            DatosOffline(),
            "cripta-01",
            carpeta,
            semilla=2026,
            ruta_bitacora=None,
            verificar=False,
        )
        try:
            partida = sesion.partida
            gc.collect()
            tracemalloc.start()
            historia = Historia(k)
            partida.historia = historia
            historia.inicializar(partida)

            jugador = partida.jugador
            for _ in range(cantidad):
                partida.reloj.avanzar_hasta_turno(jugador)
                if partida.historial.registrando:
                    partida.historial.confirmar_accion()
                partida.historial.iniciar_accion(partida.reloj)
                partida.reloj.tomar_turno(jugador)
                partida.contar_accion_jugador()
                historia.registrar_accion(
                    partida.tiempo,
                    ("esperar", None, COSTO_ESPERAR),
                )
                partida.refrescar_rastro()
                partida.programar_siguiente_jugador(COSTO_ESPERAR)
                historia.registrar_checkpoint_partida(partida)

            partida.reloj.avanzar_hasta_turno(jugador)
            if partida.historial.registrando:
                partida.historial.confirmar_accion()
            _, memoria_pico = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            if len(historia.acciones) != cantidad:
                raise RuntimeError("La historia del benchmark quedó incompleta.")
            return historia, partida.tiempo, memoria_pico
        finally:
            if tracemalloc.is_tracing():
                tracemalloc.stop()
            sesion.red.cerrar(5)


def _puntos_consulta(historia, tiempo_actual):
    consultas = []
    ultima_accion = len(historia.acciones)
    for indice in range(CONSULTAS_POR_TIPO):
        tiempo = tiempo_actual * indice // max(1, CONSULTAS_POR_TIPO - 1)
        numero = max(
            1,
            ultima_accion * (indice + 1) // CONSULTAS_POR_TIPO,
        )
        consultas.append(("tiempo", tiempo))
        consultas.append(("accion", numero))
    return consultas


def _consultar(historia, tipo, valor, tiempo_actual):
    if tipo == "tiempo":
        return historia.consultar_tiempo(valor, tiempo_actual)
    return historia.consultar_accion(valor)


def _consultar_sin_puntos(historia, tipo, valor, tiempo_actual):
    inicial = historia.puntos_control.obtenerValor(0).punto_control
    if tipo == "tiempo":
        hasta_accion = 0
        while (hasta_accion < len(historia.acciones)
               and historia.acciones.obtenerValor(hasta_accion).tiempo < valor):
            hasta_accion += 1
        temporal = ReconstructorHistoria.reconstruir(
            inicial,
            historia.acciones,
            hasta_accion=hasta_accion,
            aplicar_accion=ReconstructorHistoria.aplicar_accion,
        )
        ReconstructorHistoria.avanzar_hasta_tiempo(temporal, valor)
    else:
        temporal = ReconstructorHistoria.reconstruir(
            inicial,
            historia.acciones,
            hasta_accion=valor - 1,
            aplicar_accion=ReconstructorHistoria.aplicar_accion,
        )
        ReconstructorHistoria.avanzar_hasta_decision(
            temporal,
            historia.acciones.obtenerValor(valor - 1).tiempo,
        )
    from modelo.resumen_historico import ResumenHistorico
    return ResumenHistorico.desde_partida(temporal)


def _firma(resumen):
    return (
        resumen.tiempo,
        resumen.sala_id,
        resumen.vida,
        tuple(
            (sala.sala_id, sala.estado, sala.tiempo_rastro)
            for sala in resumen.mapa_conocido
        ),
    )


def _verificar_referencia(historia, consultas, tiempo_actual):
    for tipo, valor in consultas:
        con_puntos = _consultar(historia, tipo, valor, tiempo_actual)
        sin_puntos = _consultar_sin_puntos(
            historia, tipo, valor, tiempo_actual
        )
        if _firma(con_puntos) != _firma(sin_puntos):
            raise RuntimeError(
                f"Las consultas con/sin puntos difieren para {tipo}={valor}."
            )


def _acciones_reconstruidas(historia, tipo, valor):
    if tipo == "accion":
        punto = historia.buscar_punto_control_accion(valor)
        return valor - 1 - punto.numero_accion

    indice = historia.buscar_indice_punto_control_tiempo(valor)
    punto = historia.puntos_control.obtenerValor(indice)
    while (punto.numero_accion > 0
           and historia.acciones.obtenerValor(
               punto.numero_accion - 1
           ).tiempo >= valor):
        indice -= 1
        punto = historia.puntos_control.obtenerValor(indice)
    hasta_accion = punto.numero_accion
    while (hasta_accion < len(historia.acciones)
           and historia.acciones.obtenerValor(hasta_accion).tiempo < valor):
        hasta_accion += 1
    return hasta_accion - punto.numero_accion


def _medir_consultas(historia, consultas, tiempo_actual, repeticiones):
    muestras = []
    muestras_tiempo = []
    muestras_accion = []
    for tipo, valor in consultas:
        medicion = medir(
            _consultar,
            historia,
            tipo,
            valor,
            tiempo_actual,
            repeticiones=repeticiones,
        )
        for muestra in medicion.muestras:
            muestras.append(muestra)
            if tipo == "tiempo":
                muestras_tiempo.append(muestra)
            else:
                muestras_accion.append(muestra)
    return (
        estadisticas(muestras),
        estadisticas(muestras_tiempo),
        estadisticas(muestras_accion),
    )


def _indice_lineal(historia, tiempo):
    resultado = 0
    for indice in range(len(historia.puntos_control)):
        punto = historia.puntos_control.obtenerValor(indice)
        if punto.tiempo > tiempo:
            break
        resultado = indice
    return resultado


def _buscar_binario(historia, tiempo):
    return historia.buscar_indice_punto_control_tiempo(tiempo)


def _medir_busquedas(historia, consultas, repeticiones):
    muestras_binaria = []
    muestras_lineal = []
    for tipo, valor in consultas:
        if tipo != "tiempo":
            continue
        if _buscar_binario(historia, valor) != _indice_lineal(
                historia, valor):
            raise RuntimeError(
                "La búsqueda lineal y la búsqueda binaria discrepan."
            )
        for variante, funcion in (
            ("binaria", _buscar_binario),
            ("lineal", _indice_lineal),
        ):
            medicion = medir(
                funcion,
                historia,
                valor,
                repeticiones=repeticiones,
            )
            for muestra in medicion.muestras:
                if variante == "binaria":
                    muestras_binaria.append(muestra)
                else:
                    muestras_lineal.append(muestra)
    return (
        estadisticas(muestras_binaria),
        estadisticas(muestras_lineal),
    )


def _codificar_json(raiz):
    referencia, registros = codificar(raiz)
    return json.dumps(
        [referencia, registros], ensure_ascii=False
    ).encode("utf-8")


def _bytes_puntos_control(historia):
    total = 0
    for indice in range(len(historia.puntos_control)):
        punto = historia.puntos_control.obtenerValor(indice).punto_control
        total += len(_codificar_json(punto))
    return total


def _leer_archivo(ruta):
    with open(ruta, "rb") as archivo:
        return archivo.read()


def _medir_punto(historia, repeticiones):
    punto = historia.puntos_control.obtenerValor(
        len(historia.puntos_control) // 2
    ).punto_control
    referencia, registros = codificar(punto)
    serializado = json.dumps(
        [referencia, registros], ensure_ascii=False
    ).encode("utf-8")
    with tempfile.TemporaryDirectory() as carpeta:
        ruta = os.path.join(carpeta, "punto.json")
        with open(ruta, "wb") as archivo:
            archivo.write(serializado)
        datos_leidos = _leer_archivo(ruta)
        leido = json.loads(datos_leidos)
        return (
            len(serializado),
            medir(
                _leer_archivo,
                ruta,
                repeticiones=repeticiones,
            ),
            medir(
                json.loads,
                datos_leidos,
                repeticiones=repeticiones,
            ),
            medir(
                decodificar,
                leido[0],
                leido[1],
                repeticiones=repeticiones,
            ),
            medir(punto.restaurar, repeticiones=repeticiones),
        )


def _k_de_variante(variante):
    return int(variante.partition("=")[2])


def proponer_k(filas):
    """Devuelve el mayor K medido cuyo p95 estricto es menor a 50 ms."""
    mejor = None
    for fila in filas:
        if (fila.caso == "linea-tiempo"
                and fila.variante.startswith("consulta_K=")
                and fila.ms_p95 < UMBRAL_P95_MS):
            k = _k_de_variante(fila.variante)
            if mejor is None or k > mejor:
                mejor = k
    return mejor


def correr():
    filas = []
    resumenes_k = []
    filas_k = []
    repeticiones = REPETICIONES_BENCH
    for posicion_k, k in enumerate(K_EVALUADOS):
        historia, tiempo_actual, memoria_pico = _construir_historia(
            k, ACCIONES_BENCH
        )
        consultas = _puntos_consulta(historia, tiempo_actual)
        conteos = tuple(
            _acciones_reconstruidas(historia, tipo, valor)
            for tipo, valor in consultas
        )
        maximo_reconstruido = max(conteos) if conteos else 0
        if maximo_reconstruido > k:
            raise RuntimeError(
                f"Una consulta reconstruyó más de K={k} acciones."
            )
        if posicion_k == 0:
            _verificar_referencia(historia, consultas, tiempo_actual)

        conjunta, por_tiempo, por_accion = _medir_consultas(
            historia, consultas, tiempo_actual, repeticiones
        )
        binaria, lineal = _medir_busquedas(
            historia, consultas, repeticiones
        )
        bytes_registros = _codificar_json(
            (historia.acciones, historia.cambios)
        )
        bytes_puntos = _bytes_puntos_control(historia)
        (bytes_muestra, lectura, lectura_json, decodificacion,
         restauracion) = _medir_punto(historia, repeticiones)
        extra_consulta = (
            f"puntos={len(consultas)}; rep/punto={repeticiones}; "
            "acciones_reconstruidas_por_consulta="
            + ",".join(
                f"{tipo}:{valor}={conteo}"
                for (tipo, valor), conteo in zip(consultas, conteos)
            )
            + f"; acciones_reconstruidas_max={maximo_reconstruido}; "
            f"bytes_registros={len(bytes_registros)}; "
            f"bytes_puntos_bloques={bytes_puntos}; "
            f"memoria_pico_MiB={memoria_pico / (1024 * 1024):.2f}; "
            f"SC001_p95_lt_50ms={conjunta.ms_p95 < UMBRAL_P95_MS}"
        )
        fila_k = Fila.desde_medicion(
            "linea-tiempo",
            f"consulta_K={k}",
            ACCIONES_BENCH,
            conjunta,
            extra_consulta,
        )
        filas_k.append(fila_k)
        resumenes_k.append((k, conjunta.ms_p95))
        filas.extend((
            fila_k,
            Fila.desde_medicion(
                "linea-tiempo",
                f"tiempo_K={k}",
                CONSULTAS_POR_TIPO,
                por_tiempo,
            ),
            Fila.desde_medicion(
                "linea-tiempo",
                f"accion_K={k}",
                CONSULTAS_POR_TIPO,
                por_accion,
            ),
            Fila.desde_medicion(
                "linea-tiempo",
                f"binaria_K={k}",
                len(consultas) // 2,
                binaria,
            ),
            Fila.desde_medicion(
                "linea-tiempo",
                f"lineal_K={k}",
                len(consultas) // 2,
                lineal,
            ),
            Fila.desde_medicion(
                "linea-tiempo",
                f"leer_punto_K={k}",
                bytes_muestra,
                lectura,
            ),
            Fila.desde_medicion(
                "linea-tiempo",
                f"JSON_K={k}",
                bytes_muestra,
                lectura_json,
            ),
            Fila.desde_medicion(
                "linea-tiempo",
                f"decodificar_K={k}",
                bytes_muestra,
                decodificacion,
            ),
            Fila.desde_medicion(
                "linea-tiempo",
                f"restaurar_K={k}",
                bytes_muestra,
                restauracion,
            ),
        ))

    historia_base, tiempo_base, _ = _construir_historia(
        K_EVALUADOS[0], ACCIONES_BENCH
    )
    consultas_base = _puntos_consulta(historia_base, tiempo_base)
    muestras_sin_puntos = []
    for tipo, valor in consultas_base:
        medicion = medir(
            _consultar_sin_puntos,
            historia_base,
            tipo,
            valor,
            tiempo_base,
            repeticiones=REPETICIONES_REFERENCIA_BENCH,
        )
        for muestra in medicion.muestras:
            muestras_sin_puntos.append(muestra)
    sin_puntos = estadisticas(muestras_sin_puntos)
    maximo_sin_puntos = max(
        valor - 1 if tipo == "accion" else sum(
            1 for indice in range(len(historia_base.acciones))
            if historia_base.acciones.obtenerValor(indice).tiempo < valor
        )
        for tipo, valor in consultas_base
    )
    filas.append(
        Fila.desde_medicion(
            "linea-tiempo",
            "sin_puntos",
            ACCIONES_BENCH,
            sin_puntos,
            f"puntos={len(consultas_base)}; "
            f"rep/punto={REPETICIONES_REFERENCIA_BENCH}; "
            f"acciones_reconstruidas_max={maximo_sin_puntos}",
        )
    )

    propuesta = proponer_k(filas_k)
    print(
        "linea-tiempo: no existe variante de reconstrucción histórica "
        "hacia atrás; se compara re-simulación hacia delante."
    )
    print(
        "linea-tiempo: p95 conjunto por K: "
        + ", ".join(
            f"K={k}: {p95:.3f} ms" for k, p95 in resumenes_k
        )
    )
    valor_propuesto = str(propuesta) if propuesta is not None else "ninguno"
    coincide = propuesta == K_POR_DEFECTO
    print(
        f"linea-tiempo: K propuesto={valor_propuesto}; "
        f"K_POR_DEFECTO actual={K_POR_DEFECTO}; "
        f"coincide={'sí' if coincide else 'no'}."
    )
    return filas
