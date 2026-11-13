"""Persistencia versionada de ubicaciones de llaves de una cripta."""

import os

from persistencia.cache_json import (
    cargar_cache,
    guardar_cache,
    validar_identificador,
)


def ruta_cache_llaves(carpeta_cache, cripta_id):
    """Devuelve la ruta de caché sin aceptar ids que puedan escapar del directorio."""
    validar_identificador(cripta_id)
    return os.path.join(carpeta_cache, cripta_id, "llaves.json")


def _respuesta_valida(datos):
    if not isinstance(datos, dict) or not isinstance(datos.get("llaves"), list):
        return False
    for llave in datos["llaves"]:
        if not isinstance(llave, dict):
            return False
        if not isinstance(llave.get("id"), str) or not llave["id"]:
            return False
        if type(llave.get("sala")) is not int:
            return False
        if (
            "enemigo" in llave
            and llave["enemigo"] is not None
            and not isinstance(llave["enemigo"], str)
        ):
            return False
    return True


def cargar_llaves_cache(carpeta_cache, cripta_id, version):
    """Carga solo una respuesta bien formada de la versión e identidad solicitadas."""
    datos = cargar_cache(
        ruta_cache_llaves(carpeta_cache, cripta_id),
        version,
        cripta_id,
    )
    return datos if _respuesta_valida(datos) else None


def guardar_llaves_cache(carpeta_cache, cripta_id, version, datos):
    """Guarda la respuesta validada usando escritura atómica versionada."""
    if not _respuesta_valida(datos):
        raise ValueError("Respuesta de llaves inválida.")
    guardar_cache(
        ruta_cache_llaves(carpeta_cache, cripta_id),
        version,
        cripta_id,
        datos,
    )


def obtener_llaves(fuente, carpeta_cache, cripta_id, version):
    """Reutiliza la caché válida; ante una ausencia consulta y persiste la fuente."""
    datos = cargar_llaves_cache(carpeta_cache, cripta_id, version)
    if datos is not None:
        return datos
    datos = fuente.llaves_cripta(cripta_id)
    guardar_llaves_cache(carpeta_cache, cripta_id, version, datos)
    return datos
