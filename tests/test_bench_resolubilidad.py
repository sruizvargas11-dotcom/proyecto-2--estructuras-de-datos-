"""Integración del caso de resolubilidad en --bench (SC-002, RS-E12, RS-E33)."""

from types import SimpleNamespace

import pytest

from bench.casos import resolubilidad
from bench.medicion import Fila


def test_caso_mide_incremental_y_referencia_tras_comprobar_equivalencia(monkeypatch):
    from bench.casos import CASOS

    monkeypatch.setattr(resolubilidad, "TAMANOS_BENCH", (4, 8))
    monkeypatch.setattr(resolubilidad, "REPETICIONES_BENCH", 1)

    filas = resolubilidad.correr()

    assert resolubilidad.correr in CASOS
    assert len(filas) == 4
    assert all(isinstance(fila, Fila) for fila in filas)
    assert [fila.variante for fila in filas] == [
        "incremental",
        "referencia",
        "incremental",
        "referencia",
    ]
    assert all("semilla=42" in fila.extra for fila in filas)


def test_familia_duplica_salas_salidas_y_llaves_en_tres_tamanos():
    conteos = []
    for cantidad_llaves in (4, 8, 16):
        sintetica = resolubilidad.generar_cripta_sintetica(
            semilla=42,
            cantidad_llaves=cantidad_llaves,
            estructura="cadena",
            duplicar_topologia=True,
        )
        salidas = 0
        for sala in sintetica.cripta.recorrer_salas():
            salidas += len(sala.salidas)
        conteos.append((len(sintetica.cripta), salidas, len(sintetica.ubicaciones)))

    assert conteos[1] == tuple(valor * 2 for valor in conteos[0])
    assert conteos[2] == tuple(valor * 2 for valor in conteos[1])


def test_discrepancia_de_equivalencia_falla_antes_de_cronometrar(monkeypatch):
    monkeypatch.setattr(resolubilidad, "TAMANOS_BENCH", (2,))
    monkeypatch.setattr(
        resolubilidad,
        "recorrido_completo_repetido",
        lambda *args: SimpleNamespace(
            veredicto="NO RESOLUBLE",
            orden_por_rondas=(),
            puerta_final=None,
            frontera=(),
        ),
    )
    monkeypatch.setattr(
        resolubilidad,
        "medir",
        lambda *args, **kwargs: pytest.fail("No debe medir antes de comparar"),
    )
    sintetica = resolubilidad.generar_cripta_sintetica(
        semilla=42, cantidad_llaves=2
    )

    with pytest.raises(ValueError, match="discrepancias antes de medir"):
        resolubilidad.validar_equivalencia(sintetica)


def test_runner_sin_salida_incluye_el_caso(monkeypatch, tmp_path):
    from bench import runner

    filas = [Fila("resolubilidad", "incremental", 2, 0.1)]
    llamadas = []

    def caso():
        llamadas.append(True)
        return filas

    monkeypatch.setattr(runner, "CASOS", [caso])
    monkeypatch.setattr(runner, "_encabezado", lambda: ("commit", "python", "os", "cpu"))
    monkeypatch.setattr(
        runner,
        "_guardar_evidencia",
        lambda *args: tmp_path / "bench.json",
    )
    monkeypatch.setattr(runner, "imprimir_tabla", lambda filas: None)

    assert runner.main_bench() == filas
    assert llamadas == [True]


def test_runner_con_salida_conserva_reporte_y_ejecuta_caso(monkeypatch, tmp_path):
    from bench import runner, terreno_cazador

    filas = [Fila("resolubilidad", "incremental", 2, 0.1)]
    reportes = []
    casos = []
    monkeypatch.setattr(
        terreno_cazador,
        "crear_reporte",
        lambda ruta: reportes.append(ruta),
    )
    monkeypatch.setattr(
        resolubilidad,
        "correr",
        lambda: casos.append(True) or filas,
    )
    monkeypatch.setattr(runner, "imprimir_tabla", lambda filas: None)
    ruta = tmp_path / "terreno.json"

    assert runner.main_bench(ruta) == filas
    assert reportes == [ruta]
    assert casos == [True]


def test_bench_cli_pasa_la_ruta_solicitada(monkeypatch, tmp_path):
    import main
    from bench import runner

    llamadas = []
    monkeypatch.setattr(
        runner,
        "main_bench",
        lambda salida=None: llamadas.append(salida) or [],
    )
    monkeypatch.setattr(main, "informar", lambda mensaje: None)
    ruta = tmp_path / "terreno.json"

    assert main.main(["--bench", "--salida", str(ruta)]) == 0
    assert llamadas == [str(ruta)]
