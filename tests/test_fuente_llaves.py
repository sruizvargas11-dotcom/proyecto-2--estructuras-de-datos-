"""Contrato HTTP para consultar ubicaciones de llaves (FR-001, FR-018, FR-019)."""

from unittest.mock import MagicMock, patch

import pytest
import requests

from adaptadores.datos_http import DatosHTTP


def _respuesta(status_code, datos=None):
    respuesta = MagicMock()
    respuesta.status_code = status_code
    respuesta.text = ""
    respuesta.json.return_value = datos
    return respuesta


def test_llaves_http_acepta_lista_con_ubicaciones_y_enemigo_desconocido():
    """Un id de enemigo es metadato; la validación de sala pertenece al modelo (FR-016)."""
    datos = {"llaves": [{"id": "key-a", "sala": 7, "enemigo": "enemy-desconocido"}]}
    respuesta = _respuesta(200, datos)
    with patch("adaptadores.datos_http.requests.get", return_value=respuesta) as get:
        fuente = DatosHTTP()
        assert fuente.llaves_cripta("cripta-sintetica") == datos

    assert get.call_count == 1
    assert get.call_args.args[0].endswith("/criptas/cripta-sintetica/llaves")
    assert fuente.requests_realizados == 1


def test_llaves_http_acepta_una_lista_vacia_valida():
    """Una respuesta vacía no se confunde con un fallo de consulta (FR-001, RS-E10)."""
    respuesta = _respuesta(200, {"llaves": []})
    with patch("adaptadores.datos_http.requests.get", return_value=respuesta):
        fuente = DatosHTTP()
        assert fuente.llaves_cripta("cripta-sintetica") == {"llaves": []}


def test_reintentos_de_llaves_cuentan_en_el_presupuesto():
    """Cada intento, incluido el reintento 429, consume presupuesto (FR-001, FR-018)."""
    respuestas = [
        _respuesta(200, {"id": "cripta-sintetica", "presupuesto_solicitudes": 3}),
        _respuesta(429, {"reintentar_en": 0}),
        _respuesta(200, {"llaves": []}),
    ]
    with patch("adaptadores.datos_http.requests.get", side_effect=respuestas) as get:
        fuente = DatosHTTP(max_reintentos=1)
        fuente.datos_cripta("cripta-sintetica")
        with patch.object(fuente, "_esperar_reintento"):
            assert fuente.llaves_cripta("cripta-sintetica") == {"llaves": []}

    assert get.call_count == 3
    assert fuente.requests_realizados == fuente.presupuesto == 3
    assert fuente.dentro_del_presupuesto


def test_consulta_de_llaves_no_empieza_si_se_agoto_el_presupuesto():
    """El intento que excedería el presupuesto se rechaza sin solicitud HTTP (FR-018)."""
    with patch(
        "adaptadores.datos_http.requests.get",
        return_value=_respuesta(
            200, {"id": "cripta-sintetica", "presupuesto_solicitudes": 1}
        ),
    ) as get:
        fuente = DatosHTTP()
        fuente.datos_cripta("cripta-sintetica")
        with pytest.raises(RuntimeError, match="Presupuesto"):
            fuente.llaves_cripta("cripta-sintetica")

    assert get.call_count == 1
    assert fuente.requests_realizados == 1


def test_falla_de_transporte_y_datos_invalidos_tienen_tipos_distintos():
    """La indisponibilidad no se transforma en respuesta vacía (FR-018, FR-019)."""
    with patch(
        "adaptadores.datos_http.requests.get",
        side_effect=requests.ConnectionError("sin conexión"),
    ):
        with pytest.raises(RuntimeError):
            DatosHTTP().llaves_cripta("cripta-sintetica")

    respuesta = _respuesta(200)
    respuesta.json.side_effect = ValueError("JSON inválido")
    with patch("adaptadores.datos_http.requests.get", return_value=respuesta):
        with pytest.raises(ValueError):
            DatosHTTP().llaves_cripta("cripta-sintetica")


def test_cache_llaves_coincidente_se_reutiliza_sin_consultar_fuente(tmp_path):
    """La caché solo se reutiliza para la versión e id de cripta esperados (FR-001)."""
    from persistencia.llaves_cripta import (
        guardar_llaves_cache,
        obtener_llaves,
    )

    respuesta = {"llaves": [{"id": "key-a", "sala": 2}]}
    guardar_llaves_cache(tmp_path, "cripta-sintetica", "v1", respuesta)

    class Fuente:
        def llaves_cripta(self, cripta_id):
            raise AssertionError("la fuente no debe consultarse")

    assert obtener_llaves(Fuente(), tmp_path, "cripta-sintetica", "v1") == respuesta


def test_cache_llaves_obsoleta_se_descarta_y_consulta_fuente(tmp_path):
    """Una versión anterior no participa y la respuesta nueva se persiste (FR-001)."""
    from persistencia.llaves_cripta import (
        cargar_llaves_cache,
        guardar_llaves_cache,
        obtener_llaves,
    )

    guardar_llaves_cache(
        tmp_path, "cripta-sintetica", "v1",
        {"llaves": [{"id": "key-old", "sala": 1}]},
    )
    nueva = {"llaves": [{"id": "key-new", "sala": 3}]}

    class Fuente:
        llamadas = 0

        def llaves_cripta(self, cripta_id):
            self.llamadas += 1
            return nueva

    fuente = Fuente()
    assert obtener_llaves(fuente, tmp_path, "cripta-sintetica", "v2") == nueva
    assert fuente.llamadas == 1
    assert cargar_llaves_cache(tmp_path, "cripta-sintetica", "v2") == nueva


def test_cache_llaves_invalida_se_descarta_y_error_de_fuente_se_propaga(tmp_path):
    """Un archivo corrupto no se convierte en respuesta ni oculta fallos (FR-018, FR-019)."""
    import json

    from persistencia.cache_json import guardar_cache
    from persistencia.llaves_cripta import obtener_llaves, ruta_cache_llaves

    ruta = ruta_cache_llaves(tmp_path, "cripta-sintetica")
    guardar_cache(ruta, "v1", "cripta-sintetica", {"llaves": "inválido"})

    class Fuente:
        def llaves_cripta(self, cripta_id):
            raise RuntimeError("fuente no disponible")

    with pytest.raises(RuntimeError, match="fuente no disponible"):
        obtener_llaves(Fuente(), tmp_path, "cripta-sintetica", "v1")

    with open(ruta, encoding="utf-8") as archivo:
        assert json.load(archivo)["datos"]["llaves"] == "inválido"
