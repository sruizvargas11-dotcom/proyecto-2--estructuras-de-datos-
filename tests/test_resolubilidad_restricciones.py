"""Revisa las restricciones de estructuras y determinismo (FR-009, FR-010, FR-012,
FR-013, FR-017, FR-021; SC-003; G16; RS-E19, RS-E28, RS-E36).
"""

import ast
from pathlib import Path

import pytest


RAIZ = Path(__file__).resolve().parents[1]
ARCHIVOS_MODELO = (
    "modelo/verificador_resolubilidad.py",
    "vista/formato_resolubilidad.py",
    "bench/casos/resolubilidad.py",
)
ARCHIVOS_FUENTE = (
    "adaptadores/fuente_datos.py",
    "adaptadores/datos_http.py",
    "adaptadores/datos_offline.py",
    "adaptadores/datos_simulado.py",
    "persistencia/llaves_cripta.py",
    "herramientas/descargar_offline.py",
)
MODULOS_PROHIBIDOS = {
    "collections",
    "heapq",
    "bisect",
    "networkx",
    "igraph",
    "networkit",
    "rustworkx",
}


def _leer_arbol(ruta):
    return ast.parse((RAIZ / ruta).read_text(encoding="utf-8"), filename=ruta)


def _raiz_modulo(nombre):
    return nombre.split(".", 1)[0]


def _modulos_importados(arbol):
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.Import):
            for alias in nodo.names:
                yield _raiz_modulo(alias.name)
        elif isinstance(nodo, ast.ImportFrom) and nodo.module:
            yield _raiz_modulo(nodo.module)


def _es_contenedor_nativo(nodo):
    if isinstance(nodo, (ast.Dict, ast.Set)):
        return True
    return (
        isinstance(nodo, ast.Call)
        and isinstance(nodo.func, ast.Name)
        and nodo.func.id in ("dict", "set")
    )


def _nombre_objetivo(nodo):
    if isinstance(nodo, ast.Name):
        return nodo.id.lower()
    if isinstance(nodo, ast.Attribute):
        return nodo.attr.lower()
    return ""


def _asignaciones_de_indice_o_cache(arbol):
    tokens = ("indice", "index", "cache", "_por_id", "_por_sala")
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.Assign) and _es_contenedor_nativo(nodo.value):
            if any(
                any(token in _nombre_objetivo(destino) for token in tokens)
                for destino in nodo.targets
            ):
                yield nodo
        elif isinstance(nodo, ast.AnnAssign) and _es_contenedor_nativo(nodo.value):
            if any(token in _nombre_objetivo(nodo.target) for token in tokens):
                yield nodo


@pytest.mark.parametrize("ruta", ARCHIVOS_MODELO + ARCHIVOS_FUENTE)
def test_no_importa_bibliotecas_prohibidas(ruta):
    arbol = _leer_arbol(ruta)

    assert not (set(_modulos_importados(arbol)) & MODULOS_PROHIBIDOS), ruta


@pytest.mark.parametrize("ruta", ARCHIVOS_MODELO)
def test_logica_no_crea_indices_nativos_ni_usa_hash_o_sorted(ruta):
    arbol = _leer_arbol(ruta)
    llamadas = [
        nodo.func.id
        for nodo in ast.walk(arbol)
        if isinstance(nodo, ast.Call) and isinstance(nodo.func, ast.Name)
    ]

    assert not any(_es_contenedor_nativo(nodo) for nodo in ast.walk(arbol)), ruta
    assert "hash" not in llamadas, ruta
    assert "sorted" not in llamadas, ruta


@pytest.mark.parametrize("ruta", ARCHIVOS_MODELO)
def test_orden_de_reporte_no_depende_de_iteracion_de_mapeos(ruta):
    arbol = _leer_arbol(ruta)
    metodos_de_mapeo = {"items", "keys", "values"}
    iteraciones_nativas = [
        nodo
        for nodo in ast.walk(arbol)
        if isinstance(nodo, (ast.For, ast.comprehension))
        and isinstance(nodo.iter, ast.Call)
        and isinstance(nodo.iter.func, ast.Attribute)
        and nodo.iter.func.attr in metodos_de_mapeo
    ]

    assert not iteraciones_nativas, ruta


@pytest.mark.parametrize("ruta", ARCHIVOS_FUENTE)
def test_mapeos_de_json_no_se_guardan_como_indices_o_cache(ruta):
    arbol = _leer_arbol(ruta)

    # Los dict recibidos/creados para JSON y su acceso por campo son permitidos;
    # no se permite conservarlos como índices o cachés propios.
    assert not list(_asignaciones_de_indice_o_cache(arbol)), ruta
