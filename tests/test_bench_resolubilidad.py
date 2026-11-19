"""Integración de resolubilidad y casos especializados en --bench."""

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


@pytest.mark.parametrize("con_salida", [False, True])
def test_runner_integra_casos_niebla_y_terreno(monkeypatch, tmp_path, con_salida):
    from bench import niebla_viaje, runner, terreno_cazador

    fila_base = Fila("resolubilidad", "incremental", 2, 0.1)
    fila_niebla = Fila("niebla-viaje", "siguiente_paso", 6, 0.2)
    llamadas = []
    reportes = []
    ruta_niebla = tmp_path / "niebla.json"
    ruta_terreno = tmp_path / "terreno.json"
    salida = tmp_path / "solicitado.json" if con_salida else None

    def caso():
        llamadas.append("caso")
        return [fila_base]

    def benchmark_niebla(ruta):
        llamadas.append("niebla")
        assert ruta == ruta_niebla
        return {}, [fila_niebla]

    monkeypatch.setattr(runner, "CASOS", [caso])
    monkeypatch.setattr(runner, "_encabezado", lambda: ("commit", "python", "os", "cpu"))
    monkeypatch.setattr(runner, "_guardar_evidencia", lambda *args: tmp_path / "bench.json")
    monkeypatch.setattr(
        runner,
        "_ruta_reporte_especializado",
        lambda tipo, commit: ruta_niebla if tipo == "niebla-viaje" else ruta_terreno,
    )
    monkeypatch.setattr(niebla_viaje, "ejecutar_benchmark", benchmark_niebla)
    monkeypatch.setattr(
        terreno_cazador,
        "crear_reporte",
        lambda ruta: reportes.append(ruta) or {"benchmark": "terreno-y-cazador"},
    )
    monkeypatch.setattr(runner, "imprimir_tabla", lambda filas: None)

    assert runner.main_bench(salida) == [fila_base, fila_niebla]
    assert llamadas == ["caso", "niebla"]
    assert reportes == [salida or ruta_terreno]
    import json
    evidencia = json.loads((salida or ruta_terreno).read_text(encoding="utf-8"))
    assert evidencia["benchmark"] == "terreno-y-cazador"
    assert evidencia["filas_resolubilidad"][0]["variante"] == "incremental"
    assert evidencia["filas_resolubilidad"][0]["ms_med"] == 0.1


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
