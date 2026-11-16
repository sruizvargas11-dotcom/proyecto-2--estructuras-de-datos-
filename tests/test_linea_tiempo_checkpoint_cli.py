import pytest

from adaptadores.datos_offline import DatosOffline
import main as modulo_main
from modelo.historia import K_POR_DEFECTO
from tests.test_controlador_replay import _jugar


@pytest.mark.parametrize("argumento", ["0", "-1", "invalido"])
def test_checkpoint_cada_rechaza_valores_no_positivos(argumento, capsys):
    with pytest.raises(SystemExit) as error:
        modulo_main.main(["--checkpoint-cada", argumento])

    assert error.value.code == 2
    assert "K debe ser un entero positivo" in capsys.readouterr().err


@pytest.mark.parametrize(
    "argumentos, esperado",
    [
        ([], K_POR_DEFECTO),
        (["--checkpoint-cada", "7"], 7),
    ],
)
def test_checkpoint_cada_se_pasa_a_la_partida(
    argumentos, esperado, monkeypatch
):
    recibidos = []
    monkeypatch.setattr(
        modulo_main,
        "jugar",
        lambda fuente, cripta_id, opciones: (
            recibidos.append(opciones.checkpoint_cada) or 0
        ),
    )

    assert modulo_main.main(
        ["--offline", "--cripta", "cripta-01"] + argumentos
    ) == 0
    assert recibidos == [esperado]


def test_hasta_solo_se_acepta_con_replay():
    with pytest.raises(SystemExit) as error:
        modulo_main.main(["--hasta", "100"])

    assert error.value.code == 2


def test_replay_offline_explicito_no_hace_solicitudes_http(tmp_path, monkeypatch):
    import requests

    ruta, _, _ = _jugar(
        tmp_path, ["N"], fuente=DatosOffline(), nombre="replay-local.log"
    )
    monkeypatch.setattr(
        requests,
        "get",
        lambda *args, **kwargs: pytest.fail("El replay no debe hacer solicitudes HTTP."),
    )

    assert modulo_main.main(
        [
            "--offline",
            "--replay",
            ruta,
            "--hasta",
            "0",
            "--cache-dir",
            str(tmp_path / "cache-replay"),
            "--reportes",
            str(tmp_path / "reportes.txt"),
            "--silencioso",
        ]
    ) == 0


def test_replay_sin_offline_no_fuerza_fuente_offline(monkeypatch):
    argumentos_fuente = []
    monkeypatch.setattr(
        modulo_main,
        "crear_fuente",
        lambda argumentos: (argumentos_fuente.append(argumentos) or object()),
    )
    monkeypatch.setattr(modulo_main, "reproducir", lambda fuente, opciones: 0)

    assert modulo_main.main(["--replay", "partida.log"]) == 0
    assert argumentos_fuente == [[]]
