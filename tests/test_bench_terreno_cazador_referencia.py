import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "bench" / "datos" / "manifest.json"
SNAPSHOT = ROOT / "bench" / "datos" / "cripta-06-terreno-cazador-vf9ed9afa683d.json"

UBICACIONES_ESPERADAS = (
    8, 11, 17, 19, 34, 41, 60, 98, 108, 134,
    148, 151, 152, 163, 176, 190, 216, 230, 241, 251,
    256, 268, 283, 289, 295,
)


def test_snapshot_referencia_tiene_versiones_escala_y_cazadores():
    assert SNAPSHOT.is_file()
    datos = json.loads(SNAPSHOT.read_text(encoding="utf-8"))

    assert datos["cripta"] == "cripta-06"
    assert datos["version_cripta"] == "f9ed9afa683d"
    assert datos["version_catalogo"] == "4b9e75a42be5"
    assert datos["sala_inicial"] == 141
    assert datos["dimensiones"]["salas"] == 300
    assert len(datos["cazadores"]) == 25
    ubicaciones = tuple(cazador["sala"] for cazador in datos["cazadores"])
    assert ubicaciones == UBICACIONES_ESPERADAS
    assert all(cazador["rango"] == 600 for cazador in datos["cazadores"])


def test_manifest_referencia_registra_archivo_version_y_sha256():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    referencia = manifest["referencia_cripta_06"]
    snapshot = SNAPSHOT.read_bytes()

    assert referencia["archivo"] == SNAPSHOT.name
    assert referencia["cripta"] == "cripta-06"
    assert referencia["version_cripta"] == "f9ed9afa683d"
    assert referencia["version_catalogo"] == "4b9e75a42be5"
    assert referencia["salas"] == 300
    assert referencia["cazadores"] == 25
    assert len(referencia["ubicaciones"]) == 25
    assert tuple(referencia["ubicaciones"]) == UBICACIONES_ESPERADAS
    import hashlib
    assert referencia["sha256"] == hashlib.sha256(snapshot).hexdigest()


def test_repeticion_referencia_mide_1000_ciclos_y_no_discrepa():
    from bench.terreno_cazador import _correr_referencia

    datos = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    duraciones, discrepancias = _correr_referencia(datos)

    assert len(duraciones) == 1000
    assert all(type(duracion) is int and duracion >= 0 for duracion in duraciones)
    assert not discrepancias
