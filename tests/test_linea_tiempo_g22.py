"""Prueba de aceptacion G22: replay historico y fin anticipado (FR-011)."""

from adaptadores.datos_offline import DatosOffline
from controlador.controlador_juego import ControladorJuego
from controlador.inicio_partida import nueva_partida
from main import main
from modelo.resumen_historico import ResumenHistorico
from tests.test_controlador_juego import VistaGuion
from tests.test_controlador_replay import OfflineResistente
from vista.vista_consola import VistaConsola


class VistaConResumen(VistaGuion):
    def __init__(self, comandos):
        super().__init__(comandos)
        self.resumenes_historicos = []

    def mostrar_resumen_historico(self, resumen):
        self.resumenes_historicos.append(resumen)


def _ejecutar_replay(capsys, ruta, hasta, tmp_path):
    argumentos = [
        "--offline",
        "--replay", str(ruta),
        "--hasta", str(hasta),
        "--cache-dir", str(tmp_path / f"cache-{hasta}"),
        "--reportes", str(tmp_path / f"reportes-{hasta}.txt"),
    ]
    try:
        codigo = main(argumentos)
    except SystemExit as error:
        codigo = error.code
    salida = capsys.readouterr()
    return codigo, salida.out + salida.err


def test_g22_replay_reutiliza_historia_y_avisa_fin_anticipado(
    tmp_path, monkeypatch, capsys
):
    """Compara historia t con replay --hasta t, sin vista y con aviso final (FR-011, G22)."""
    ruta = tmp_path / "partida.log"
    sesion = nueva_partida(
        OfflineResistente(),
        "cripta-01",
        str(tmp_path / "cache-juego"),
        semilla=3,
        ruta_bitacora=str(ruta),
    )
    vista = VistaConResumen(["W", "W", "historia 100", "Q"])
    ControladorJuego(sesion, vista).jugar()

    representacion_interactiva = []
    representacion_final = []
    renderizar = getattr(VistaConsola, "mostrar_resumen_historico", None)
    if callable(renderizar):
        vista_consola = VistaConsola(escribir=representacion_interactiva.append)
        if vista.resumenes_historicos:
            renderizar(vista_consola, vista.resumenes_historicos[0])
        vista_final = VistaConsola(escribir=representacion_final.append)
        renderizar(vista_final, ResumenHistorico.desde_partida(sesion.partida))

    instancias_vista = []

    def registrar_instancia(*args, **kwargs):
        instancias_vista.append(True)

    monkeypatch.setattr(VistaConsola, "__init__", registrar_instancia)
    codigo_alcanzado, salida_alcanzado = _ejecutar_replay(
        capsys, ruta, 100, tmp_path
    )
    codigo_posterior, salida_posterior = _ejecutar_replay(
        capsys, ruta, 300, tmp_path
    )

    assert codigo_alcanzado == 0, (
        "El CLI debe aceptar --replay partida.log --hasta t y emitir el resumen; "
        f"codigo={codigo_alcanzado}, salida={salida_alcanzado!r}"
    )
    assert codigo_posterior == 0, (
        "El replay posterior al final debe terminar normalmente; "
        f"codigo={codigo_posterior}, salida={salida_posterior!r}"
    )
    assert not instancias_vista, "El modo replay no debe instanciar la vista."
    assert len(vista.resumenes_historicos) == 1
    assert callable(renderizar), "La vista interactiva debe presentar el resumen historico."
    assert representacion_interactiva
    for linea in representacion_interactiva:
        assert linea in salida_alcanzado
    assert representacion_final
    for linea in representacion_final:
        assert linea in salida_posterior
    assert "t=100" in salida_alcanzado
    assert "t=200" in salida_posterior
    assert any(
        frase in salida_posterior.lower()
        for frase in ("termino antes", "terminó antes", "finalizo antes", "finalizó antes")
    )

