"""Prueba de aceptacion G23: rechazo explicito de guardados de Parte I (FR-013)."""

import pytest

from adaptadores.datos_offline import DatosOffline
from controlador.guardado import cargar, guardar
from controlador.inicio_partida import nueva_partida


def test_g23_rechaza_archivo_parte_i(tmp_path):
    """Un archivo con el esquema anterior se rechaza sin migrarlo ni cargarlo (FR-013, G23)."""
    sesion = nueva_partida(
        DatosOffline(),
        "cripta-01",
        str(tmp_path / "cache"),
        semilla=2026,
    )
    ruta = tmp_path / "partida-parte-i.sav"
    guardar(sesion, str(ruta))

    contenido = bytearray(ruta.read_bytes())
    marcador_esquema_actual = b'"esquema_estado": 2'
    posicion = contenido.find(marcador_esquema_actual)
    assert posicion >= 0, "El fixture debe contener la marca del esquema actual."
    contenido[posicion + len(marcador_esquema_actual) - 1] = ord("1")
    ruta.write_bytes(contenido)

    with pytest.raises(
        ValueError,
        match=r"Guardado incompatible: esquema de estado 1.*no se puede cargar",
    ):
        cargar(str(ruta), sesion)

