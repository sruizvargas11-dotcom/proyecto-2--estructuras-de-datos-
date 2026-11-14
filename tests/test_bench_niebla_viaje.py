"""Pruebas de contrato para el benchmark de niebla de guerra e ir a (NV-29; FR-017)."""
import json

import pytest

from bench.niebla_viaje import _preparar_conocimiento, ejecutar_benchmark
from main import main
from modelo.conocimiento import ABIERTA, CERRADA, EXPLORADA


def test_nv29_preparacion_explora_y_conserva_puertas_cerradas():
    """NV-29; FR-004, FR-016, FR-017."""
    cripta, conocimiento = _preparar_conocimiento()
    assert cripta.id == "cripta-01" and len(cripta) == 6
    for sala in cripta.recorrer_salas():
        assert conocimiento.estado_sala(sala.id) == EXPLORADA
    assert conocimiento.puerta_recordada(1, "N") == ABIERTA
    assert conocimiento.puerta_recordada(2, "E") == CERRADA
    assert conocimiento.puerta_recordada(4, "E") == CERRADA
    assert conocimiento.siguiente_paso(1, 4) == ("N", 2, 100, 300)


def test_nv29_contrato_json_desde_main(tmp_path):
    """NV-29; FR-017. Contrato del reporte JSON desde main sin imponer umbral temporal."""
    ruta_json = tmp_path / "niebla_viaje_bench.json"
    ruta_reportes = tmp_path / "reportes_red.txt"
    codigo = main([
        "--bench",
        "--bench-caso", "niebla-viaje",
        "--salida", str(ruta_json),
        "--reportes", str(ruta_reportes),
    ])
    assert codigo == 0
    assert ruta_json.exists()

    datos = json.loads(ruta_json.read_text(encoding="utf-8"))
    assert datos["benchmark"] == "niebla-viaje"
    assert datos["cripta"] == "cripta-01"
    assert datos["salas"] == 6
    assert datos["semilla"] == 42
    assert isinstance(datos["commit"], str) and datos["commit"]
    assert isinstance(datos["python"], str) and datos["python"]
    assert isinstance(datos["sistema_operativo"], str) and datos["sistema_operativo"]
    assert isinstance(datos["cpu"], str) and datos["cpu"]
    assert datos["umbral_siguiente_paso_ms"] == 5.0
    assert isinstance(datos["cumple_5ms"], bool)

    operaciones = datos["operaciones"]
    assert set(operaciones) == {"estado_sala", "puerta_recordada", "siguiente_paso"}
    for nombre in ("estado_sala", "puerta_recordada", "siguiente_paso"):
        op = operaciones[nombre]
        assert op["n_rep"] == 100
        assert len(op["muestras_ms"]) == 100
        assert 0.0 <= op["ms_min"] <= op["ms_med"] <= op["ms_p95"] <= op["ms_max"]

    paso = operaciones["siguiente_paso"]
    assert paso["origen"] == 1 and paso["destino"] == 4
    assert paso["paso"] == ["N", 2, 100, 300]
    assert paso["umbral_ms"] == 5.0
    assert isinstance(paso["cumple_5ms"], bool)


def test_nv29_bench_caso_requiere_bench():
    with pytest.raises(SystemExit):
        main(["--bench-caso", "niebla-viaje"])


def test_nv29_ejecutar_benchmark_sin_archivo():
    reporte, filas = ejecutar_benchmark(salida=None, repeticiones=5)
    assert len(filas) == 3
    assert [f.variante for f in filas] == [
        "estado_sala", "puerta_recordada", "siguiente_paso"
    ]
    assert reporte["operaciones"]["siguiente_paso"]["n_rep"] == 5
