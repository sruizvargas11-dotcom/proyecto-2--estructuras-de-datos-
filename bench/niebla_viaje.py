"""Benchmark headless de niebla de guerra e ir a (spec 002, FR-017)."""
import json
import platform
import tempfile
from datetime import datetime
from pathlib import Path

from adaptadores.datos_offline import DatosOffline
from bench.medicion import Fila, medir
from bench.runner import _obtener_commit
from controlador.inicio_partida import nueva_partida

CRIPTA_REFERENCIA = "cripta-01"
SEMILLA = 42
REPETICIONES = 100
LIMITE_PASO_MS = 5.0
ORIGEN_PASO = 1
DESTINO_PASO = 4


def _preparar_conocimiento():
    with tempfile.TemporaryDirectory() as carpeta:
        sesion = nueva_partida(
            DatosOffline(), CRIPTA_REFERENCIA, carpeta,
            semilla=SEMILLA, ruta_bitacora=None,
        )
        try:
            partida = sesion.partida
            cripta = partida.cripta
            conocimiento = partida.conocimiento
            # Fuera de la medición: explorar todas las salas y observar sus
            # puertas desde ambos extremos, conservando el estado real.
            for sala in cripta.recorrer_salas():
                conocimiento.visitar(sala, 0)
            for sala in cripta.recorrer_salas():
                conocimiento.observar(sala, 0)
            return cripta, conocimiento
        finally:
            sesion.red.cerrar(5)


def _diccionario_medicion(medicion):
    return {
        "n_rep": medicion.n_rep,
        "ms_min": medicion.ms_min,
        "ms_med": medicion.ms_med,
        "ms_p95": medicion.ms_p95,
        "ms_max": medicion.ms_max,
        "muestras_ms": list(medicion.muestras),
    }


def ejecutar_benchmark(salida=None, repeticiones=REPETICIONES):
    cripta, conocimiento = _preparar_conocimiento()
    paso = conocimiento.siguiente_paso(ORIGEN_PASO, DESTINO_PASO)
    if paso is None:
        raise RuntimeError("siguiente_paso(1, 4) no devolvió un paso válido.")

    med_estado = medir(
        conocimiento.estado_sala, DESTINO_PASO, repeticiones=repeticiones
    )
    med_puerta = medir(
        conocimiento.puerta_recordada, 2, "E", repeticiones=repeticiones
    )
    med_paso = medir(
        conocimiento.siguiente_paso, ORIGEN_PASO, DESTINO_PASO,
        repeticiones=repeticiones,
    )

    commit = _obtener_commit()
    so = f"{platform.system()} {platform.release()} ({platform.version().split()[0]})"
    cpu = platform.processor() or platform.machine()
    py = platform.python_version()
    n_salas = len(cripta)
    cumple = med_paso.ms_max <= LIMITE_PASO_MS

    operaciones = {
        "estado_sala": _diccionario_medicion(med_estado),
        "puerta_recordada": _diccionario_medicion(med_puerta),
        "siguiente_paso": {
            **_diccionario_medicion(med_paso),
            "origen": ORIGEN_PASO,
            "destino": DESTINO_PASO,
            "paso": list(paso),
            "umbral_ms": LIMITE_PASO_MS,
            "cumple_5ms": cumple,
        },
    }
    reporte = {
        "benchmark": "niebla-viaje",
        "fecha": datetime.now().isoformat(timespec="seconds"),
        "cripta": cripta.id,
        "version_cripta": cripta.version,
        "salas": n_salas,
        "semilla": SEMILLA,
        "commit": commit,
        "python": py,
        "sistema_operativo": so,
        "cpu": cpu,
        "umbral_siguiente_paso_ms": LIMITE_PASO_MS,
        "cumple_5ms": cumple,
        "operaciones": operaciones,
    }

    if salida is not None:
        destino = Path(salida)
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(
            json.dumps(reporte, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    filas = [
        Fila.desde_medicion("niebla-viaje", "estado_sala", n_salas, med_estado),
        Fila.desde_medicion("niebla-viaje", "puerta_recordada", n_salas, med_puerta),
        Fila.desde_medicion(
            "niebla-viaje", "siguiente_paso", n_salas, med_paso,
            extra=f"<=5ms:{cumple}",
        ),
    ]
    return reporte, filas
