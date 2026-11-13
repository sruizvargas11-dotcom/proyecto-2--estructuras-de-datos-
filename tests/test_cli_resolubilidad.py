"""Contrato CLI de --verificar (FR-014, FR-024; RS-E23–RS-E25, RS-E30–RS-E31, RS-E34)."""

import pytest

import main
from modelo.mundo.cripta_modelo import CriptaModelo
from modelo.mundo.sala import Sala
from modelo.mundo.salida import Salida
from vista.formato_resolubilidad import formatear_reporte


class _FuenteLlaves:
    def __init__(self, llaves=None, error=None):
        self.llaves = llaves or []
        self.error = error
        self.consultas_llaves = 0

    def llaves_cripta(self, cripta_id):
        self.consultas_llaves += 1
        if self.error is not None:
            raise self.error
        return {"llaves": self.llaves}


def _cripta(llave_en_salida=False):
    cripta = CriptaModelo("cripta-sintetica", "v1", 10, 99, "key-exit", 0, 0)
    inicial = Sala(10, "Inicial")
    salida = Sala(99, "Salida")
    inicial.salidas.insertar_al_final(
        Salida("N", 99, cerrada=True, llave="key-exit")
    )
    cripta.agregar_sala(inicial)
    cripta.agregar_sala(salida)
    cripta.finalizar_carga()
    ubicacion = 99 if llave_en_salida else 10
    return cripta, [{"id": "key-exit", "sala": ubicacion}]


def _preparar(monkeypatch, tmp_path, cripta, fuente):
    salidas = []
    monkeypatch.setattr(main, "crear_fuente", lambda argumentos: fuente)
    monkeypatch.setattr(
        main, "cargar_cripta", lambda fuente, cripta_id, cache: (cripta, False)
    )
    monkeypatch.setattr(main, "informar", salidas.append)
    return salidas


def _argumentos(tmp_path, *extra):
    return [
        "--offline",
        "--cripta",
        "cripta-sintetica",
        "--cache-dir",
        str(tmp_path / "cache"),
        *extra,
    ]


def test_cli_verificar_resoluble_imprime_reporte_y_codigo_cero(monkeypatch, tmp_path):
    cripta, llaves = _cripta()
    fuente = _FuenteLlaves(llaves)
    salidas = _preparar(monkeypatch, tmp_path, cripta, fuente)
    from modelo.verificador_resolubilidad import verificar_resolubilidad

    esperado = formatear_reporte(verificar_resolubilidad(cripta, llaves)).rstrip("\n")

    codigo = main.main(_argumentos(tmp_path, "--verificar"))

    assert codigo == 0
    assert salidas == [esperado]
    assert fuente.consultas_llaves == 1


def test_cli_verificar_acepta_identificador_en_la_opcion(monkeypatch, tmp_path):
    cripta, llaves = _cripta()
    fuente = _FuenteLlaves(llaves)
    salidas = _preparar(monkeypatch, tmp_path, cripta, fuente)

    codigo = main.main(
        [
            "--offline",
            "--verificar",
            "cripta-sintetica",
            "--cache-dir",
            str(tmp_path / "cache"),
        ]
    )

    assert codigo == 0
    assert salidas[0].startswith("VEREDICTO: RESOLUBLE\n")
    assert fuente.consultas_llaves == 1


def test_cli_verificar_no_resoluble_imprime_reporte_y_codigo_uno(monkeypatch, tmp_path):
    cripta, llaves = _cripta(llave_en_salida=True)
    fuente = _FuenteLlaves(llaves)
    salidas = _preparar(monkeypatch, tmp_path, cripta, fuente)
    from modelo.verificador_resolubilidad import verificar_resolubilidad

    esperado = formatear_reporte(verificar_resolubilidad(cripta, llaves)).rstrip("\n")

    codigo = main.main(_argumentos(tmp_path, "--verificar"))

    assert codigo == 1
    assert salidas == [esperado]


def test_cli_verificar_error_de_datos_devuelve_dos(monkeypatch, tmp_path):
    cripta, llaves = _cripta()
    llaves[0]["sala"] = 700
    fuente = _FuenteLlaves(llaves)
    salidas = _preparar(monkeypatch, tmp_path, cripta, fuente)

    codigo = main.main(_argumentos(tmp_path, "--verificar"))

    assert codigo == 2
    assert salidas and "error" in salidas[0].lower()


def test_cli_verificar_fallo_de_consulta_devuelve_dos_y_no_verificable(
    monkeypatch, tmp_path
):
    cripta, _ = _cripta()
    fuente = _FuenteLlaves(error=RuntimeError("consulta fallida"))
    salidas = _preparar(monkeypatch, tmp_path, cripta, fuente)

    codigo = main.main(_argumentos(tmp_path, "--verificar"))

    assert codigo == 2
    assert salidas == [
        "VEREDICTO: NO VERIFICABLE\n"
        "MOTIVO: consulta de llaves no disponible"
    ]


def test_cli_verificar_no_instancia_vista(monkeypatch, tmp_path):
    import vista.vista_consola

    cripta, llaves = _cripta()
    fuente = _FuenteLlaves(llaves)
    _preparar(monkeypatch, tmp_path, cripta, fuente)
    monkeypatch.setattr(
        vista.vista_consola,
        "VistaConsola",
        lambda *args, **kwargs: pytest.fail("No debe crearse la vista"),
    )

    assert main.main(_argumentos(tmp_path, "--verificar")) == 0


@pytest.mark.parametrize("conflicto", ["--replay", "--bench"])
def test_cli_rechaza_conflictos_antes_de_consultar(monkeypatch, tmp_path, conflicto):
    cripta, _ = _cripta()
    fuente = _FuenteLlaves(error=AssertionError("No debe consultar"))
    _preparar(monkeypatch, tmp_path, cripta, fuente)
    argumentos = _argumentos(tmp_path, "--verificar", conflicto)
    if conflicto == "--replay":
        argumentos.append("partida.log")

    with pytest.raises(SystemExit) as contexto:
        main.main(argumentos)

    assert contexto.value.code == 2
    assert fuente.consultas_llaves == 0


def test_cli_verificar_ignora_forzar(monkeypatch, tmp_path):
    cripta, llaves = _cripta(llave_en_salida=True)
    fuente = _FuenteLlaves(llaves)
    salidas = _preparar(monkeypatch, tmp_path, cripta, fuente)

    sin_forzar = main.main(_argumentos(tmp_path, "--verificar"))
    salida_sin_forzar = tuple(salidas)
    salidas.clear()
    con_forzar = main.main(_argumentos(tmp_path, "--verificar", "--forzar"))

    assert (con_forzar, tuple(salidas)) == (sin_forzar, salida_sin_forzar)
