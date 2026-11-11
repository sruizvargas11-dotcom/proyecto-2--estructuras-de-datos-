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
        'filas': [
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
        ],
    }
    ruta.write_text(json.dumps(datos, ensure_ascii=False, indent=2), encoding='utf-8')
    return ruta


def main_bench(salida=None):
    if salida is not None:
        from bench.terreno_cazador import crear_reporte
        crear_reporte(salida)
        print(f"evidencia: {salida}")
        return []
    commit, py, so, cpu = _encabezado()
    filas = []
    for caso in CASOS:
        filas.extend(caso())
    imprimir_tabla(filas)
    if salida is None:
        ruta = _guardar_evidencia(filas, commit, py, so, cpu)
    print(f"\nevidencia: {ruta}")
    return filas
