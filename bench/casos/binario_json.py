"""Compara tamaño y tiempos del guardado binario frente a JSON."""
import json
import os
import tempfile

from bench.bench_bloque3 import generar_estado
from bench.medicion import Fila, medir
from estructuras.vector_dinamico import Vector
from estructuras.ordenamientos import ordenar
from persistencia.PartidaBinaria import PartidaBinaria

TAMANOS_SALAS = (50, 500, 5000)


def _cmp_ids(a, b):
    return (a > b) - (a < b)


def _medir_tamano(n):
    estado_global, estado_salas = generar_estado(n)

    ids = Vector()
    for sid in estado_salas:
        ids.agregarValor(sid)
    ordenar(ids, _cmp_ids)
    sala_media = ids.obtenerValor(n // 2)

    pares_salas = [(sid, datos) for sid, datos in estado_salas.items()]
    estado_equiv = {'global': estado_global, 'salas': estado_salas}

    with tempfile.TemporaryDirectory(prefix='cripta-bench-') as carpeta:
        ruta_bin = os.path.join(carpeta, f'partida_{n}.bin')
        ruta_json = os.path.join(carpeta, f'partida_{n}.json')
        partida = PartidaBinaria(ruta_bin)

        def guardar_bin():
            partida.guardar(estado_global, pares_salas)

        def guardar_json():
            with open(ruta_json, 'w', encoding='utf-8') as f:
                json.dump(estado_equiv, f)

        def cargar_todo_bin():
            partida.cargar_todo()

        def cargar_todo_json():
            with open(ruta_json, 'r', encoding='utf-8') as f:
                json.load(f)

        def cargar_sala_bin():
            partida.cargar_sala_binaria(sala_media)

        # Configuración inicial: crea los archivos antes del primer medir().
        guardar_bin()
        guardar_json()
        tam_bin = os.path.getsize(ruta_bin)
        tam_json = os.path.getsize(ruta_json)

        m_guardar_bin      = medir(guardar_bin)
        m_guardar_json     = medir(guardar_json)
        m_cargar_todo_bin  = medir(cargar_todo_bin)
        m_cargar_todo_json = medir(cargar_todo_json)
        m_cargar_sala_bin  = medir(cargar_sala_bin)
        m_cargar_sala_json = m_cargar_todo_json  # JSON no tiene índice

        return (tam_bin, tam_json,
                m_guardar_bin, m_guardar_json,
                m_cargar_todo_bin, m_cargar_todo_json,
                m_cargar_sala_bin, m_cargar_sala_json)


def correr():
    filas = []
    for n in TAMANOS_SALAS:
        (tam_bin, tam_json,
         m_guardar_bin, m_guardar_json,
         m_cargar_todo_bin, m_cargar_todo_json,
         m_cargar_sala_bin, m_cargar_sala_json) = _medir_tamano(n)

        filas.append(Fila.desde_medicion('guardado',    'binario', n, m_guardar_bin,
                                         f'bytes={tam_bin}'))
        filas.append(Fila.desde_medicion('guardado',    'json',    n, m_guardar_json,
                                         f'bytes={tam_json}'))
        filas.append(Fila.desde_medicion('carga_total', 'binario', n, m_cargar_todo_bin))
        filas.append(Fila.desde_medicion('carga_total', 'json',    n, m_cargar_todo_json))
        filas.append(Fila.desde_medicion('carga_1_sala', 'binario', n, m_cargar_sala_bin,
                                         'usa índice'))
        filas.append(Fila.desde_medicion('carga_1_sala', 'json',    n, m_cargar_sala_json,
                                         'lee todo'))
    return filas
