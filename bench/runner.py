"""Punto de entrada de `python main.py --bench` (sin vista ni red)."""
import json
import platform
import subprocess
from datetime import datetime
from pathlib import Path

from bench.casos import CASOS
from bench.medicion import imprimir_tabla


def _obtener_commit():
    try:
        commit = subprocess.check_output(
            ['git', 'rev-parse', '--short', 'HEAD'],
            stderr=subprocess.DEVNULL, text=True).strip()
        status = subprocess.check_output(
            ['git', 'status', '--porcelain'],
            stderr=subprocess.DEVNULL, text=True).strip()
        if status:
            commit += ' +sin commit'
        return commit
    except Exception:
        return 'desconocido'


def _encabezado(semilla=42):
    commit = _obtener_commit()
    cpu = platform.processor() or platform.machine()
    so = f"{platform.system()} {platform.release()} ({platform.version().split()[0]})"
    py = platform.python_version()
    print(f"commit  : {commit}")
    print(f"python  : {py}")
    print(f"sistema : {so} · {cpu}")
    print(f"semilla : {semilla}")
    print(f"nota    : p95='---' cuando rep<20; valor real en evidencia JSON")
    print('-' * 68)
    return commit, py, so, cpu


def _datos_filas(filas):
    return [
        {
            'caso': f.caso,
            'variante': f.variante,
            'n': f.n,
            'ms_med': f.ms,
            'ms_min': f.ms_min,
            'ms_p95': f.ms_p95,
            'ms_max': f.ms_max,
            'n_rep': f.n_rep,
            'muestras': list(f.muestras),
            'extra': f.extra,
        }
        for f in filas
    ]


def _guardar_evidencia(filas, commit, py, so, cpu, semilla=42):
    directorio = Path(__file__).parent / 'resultados'
    directorio.mkdir(parents=True, exist_ok=True)
    marca = datetime.now().strftime('%Y-%m-%dT%H%M%S')
    ruta = directorio / f"{marca}_{commit}_bench.json"
    datos = {
        'commit': commit,
        'python': py,
        'sistema': so,
        'cpu': cpu,
        'semilla': semilla,
        'fecha': datetime.now().isoformat(timespec='seconds'),
        'filas': _datos_filas(filas),
    }
    ruta.write_text(json.dumps(datos, ensure_ascii=False, indent=2), encoding='utf-8')
    return ruta


def _ruta_reporte_especializado(tipo, commit):
    directorio = Path(__file__).parent / 'resultados'
    directorio.mkdir(parents=True, exist_ok=True)
    marca = datetime.now().strftime('%Y-%m-%dT%H%M%S')
    return directorio / f"{marca}_{commit}_{tipo}.json"


def main_bench(salida=None):
    commit, py, so, cpu = _encabezado()
    filas = []
    print("Ejecutando casos generales de estructuras y persistencia...", flush=True)
    for caso in CASOS:
        filas.extend(caso())

    # Los reportes específicos conservan sus propios formatos. La salida
    # solicitada por CLI sigue correspondiendo al reporte contractual del
    # cazador; el reporte de niebla se guarda junto a las demás evidencias.
    from bench.niebla_viaje import ejecutar_benchmark
    ruta_niebla = _ruta_reporte_especializado('niebla-viaje', commit)
    print("Midiendo niebla de guerra y viaje...", flush=True)
    _, filas_niebla = ejecutar_benchmark(ruta_niebla)
    filas.extend(filas_niebla)

    from bench.terreno_cazador import crear_reporte
    ruta_terreno = Path(salida) if salida is not None else _ruta_reporte_especializado(
        'terreno-cazador', commit
    )
    print(
        "Midiendo terreno y cazador (ocho escenarios sintéticos, cripta de referencia y "
        "comparación de escala; puede tardar varios minutos)...",
        flush=True,
    )
    reporte_terreno = crear_reporte(ruta_terreno)
    filas_resolubilidad = [fila for fila in filas if fila.caso == 'resolubilidad']
    if filas_resolubilidad:
        reporte_terreno['filas_resolubilidad'] = _datos_filas(filas_resolubilidad)
        ruta_terreno.write_text(
            json.dumps(reporte_terreno, ensure_ascii=False, indent=2) + "\n",
            encoding='utf-8',
        )

    imprimir_tabla(filas)
    ruta = _guardar_evidencia(filas, commit, py, so, cpu)
    print(f"\nevidencia general: {ruta}")
    print(f"evidencia niebla-viaje: {ruta_niebla}")
    print(f"evidencia terreno-cazador: {ruta_terreno}")
    return filas
