"""Integración del índice hash con ControladorRed y el reporte de red (B01).

- estadisticas_cache() conserva sus claves y agrega las del índice.
- Una LRU llena de fichas protegidas ya no rompe la incorporación de salas:
  la ficha rechazada se lee de la caché persistente, sin solicitudes de red.
- El reporte agrega una línea del índice sin repetir aciertos ni fallos.
"""
import pytest

from adaptadores.datos_offline import DatosOffline
from controlador.controlador_red import (CacheFichasLlenaError, ControladorRed,
                                         cargar_esqueleto_completo)
from controlador.reporte_red import construir_reporte
from tests.test_reporte_red import AHORA, FuenteContadaRed, _sesion_jugada


@pytest.fixture
def offline():
    fuente = DatosOffline()
    return fuente, cargar_esqueleto_completo(fuente, 'cripta-01')


def test_estadisticas_cache_conserva_claves_y_agrega_indice(offline, tmp_path):
    fuente, cripta = offline
    red = ControladorRed(fuente, cripta, tmp_path)
    red.resolver_catalogo(['ent_rata_gigante', 'itm_llave_bronce'])
    nombres = [n for n, _ in red.estadisticas_cache()]
    assert nombres[:6] == ['aciertos', 'fallos', 'desalojos', 'capacidad',
                           'en_memoria', 'salas_incorporadas']
    assert 'rechazos_capacidad' in nombres and 'indice_cubetas' in nombres
    assert nombres.count('aciertos') == 1 and nombres.count('fallos') == 1
    red._fichas._verificar_invariantes()


def _red_llena_de_protegidas(fuente, cripta, carpeta):
    red = ControladorRed(fuente, cripta, carpeta, cache_size=1)
    red.resolver_catalogo(['itm_llave_bronce'])
    red._fichas.marcar_en_uso('itm_llave_bronce')
    return red


def test_ficha_rechazada_por_capacidad_se_lee_de_disco(offline, tmp_path):
    fuente, cripta = offline
    red = _red_llena_de_protegidas(fuente, cripta, tmp_path)
    red.resolver_catalogo(['itm_antorcha'])
    assert red._fichas.contador_rechazos_capacidad == 1
    assert not red._fichas.contiene('itm_antorcha') and len(red._fichas) == 1
    solicitudes = red.contador_solicitudes_catalogo
    disco = red.contador_fichas_desde_disco
    assert red.ficha('itm_antorcha')['id'] == 'itm_antorcha'
    assert red.contador_solicitudes_catalogo == solicitudes      # sin red
    assert red.contador_fichas_desde_disco == disco + 1          # una lectura de disco


def test_al_liberar_espacio_la_ficha_vuelve_a_memoria(offline, tmp_path):
    fuente, cripta = offline
    red = _red_llena_de_protegidas(fuente, cripta, tmp_path)
    red.resolver_catalogo(['itm_antorcha'])
    red._fichas.desmarcar_en_uso('itm_llave_bronce')
    red.resolver_catalogo(['itm_antorcha'])
    assert red._fichas.contiene('itm_antorcha') and len(red._sin_espacio) == 0
    red._fichas._verificar_invariantes()


@pytest.mark.parametrize('sala_id', [1, 3, 5])
def test_sala_con_objetos_se_incorpora_aunque_la_cache_este_llena(offline, tmp_path, sala_id):
    """Antes: RuntimeError 'La ficha ... no se resolvió antes de incorporar'."""
    fuente, cripta = offline
    red = _red_llena_de_protegidas(fuente, cripta, tmp_path)
    red.garantizar_contenido(sala_id)
    assert red.contenido_cargado(sala_id)
    assert len(red._fichas) <= 1
    red._fichas._verificar_invariantes()


def test_enemigo_sin_espacio_para_protegerse_da_error_claro(offline, tmp_path):
    fuente, cripta = offline
    red = _red_llena_de_protegidas(fuente, cripta, tmp_path)
    red.resolver_catalogo(['ent_guardian_oseo'])
    with pytest.raises(CacheFichasLlenaError, match='--cache-size'):
        red._proteger_ficha_enemigo('ent_guardian_oseo')
    # RuntimeError: main.py lo informa como fallo de carga, sin traceback.
    assert issubclass(CacheFichasLlenaError, RuntimeError)


def test_reporte_incluye_indice_sin_repetir_aciertos(tmp_path):
    sesion = _sesion_jugada(tmp_path, FuenteContadaRed())
    lineas = list(construir_reporte(sesion.red._fuente, sesion, 'http', 'fin', ahora=AHORA))
    indice = [l for l in lineas if l.startswith('indice_hash: ')]
    assert len(indice) == 1 and 'cubetas' in indice[0] and 'cadena máx' in indice[0]
    assert any(l.startswith('fichas_lru_protegidas: ') for l in lineas)
    assert sum(l.startswith('fichas_lru_aciertos: ') for l in lineas) == 1


def test_cache_size_no_cambia_la_partida(tmp_path):
    """Con capacidades menores que los tipos de un lote, las fichas desalojadas
    se recuperan de disco y la partida es idéntica a la de capacidad 25.
    Antes del índice, 10 y 3 fallaban al iniciar."""
    from controlador.controlador_juego import ControladorJuego
    from controlador.estado_final import lineas_estado
    from controlador.inicio_partida import nueva_partida
    from herramientas.verificar_determinismo import VistaGuion
    comandos = list('NWSEN') + ['T', 'N', 'E', 'S', 'W', 'N', 'N', 'E', 'T', 'S', 'S', 'W', 'N', 'E', 'E', 'N'] * 3
    resultados = []
    for cache in (25, 10, 3):
        raiz = tmp_path / str(cache)
        sesion = nueva_partida(DatosOffline(), 'cripta-01', str(raiz / 'cache'), semilla=3,
                               ruta_bitacora=str(raiz / 'partida.log'), cache_size=cache)
        sesion.partida.jugador.vida_max = sesion.partida.jugador.vida = 100000
        vista = VistaGuion(comandos)
        ControladorJuego(sesion, vista).jugar()
        assert len(sesion.red._fichas) <= cache
        sesion.red._fichas._verificar_invariantes()
        resultados.append((list(lineas_estado(sesion.partida)), vista.mensajes,
                           (raiz / 'partida.log').read_bytes()))
    assert resultados[0] == resultados[1] == resultados[2]


def test_fallo_al_proteger_no_publica_el_lote(offline, tmp_path):
    """Todo o nada: si un enemigo del lote no se puede proteger, ninguna sala
    del lote queda publicada ni con referencias en_uso a medias."""
    fuente, cripta = offline
    red = ControladorRed(fuente, cripta, tmp_path, cache_size=1)
    red.resolver_catalogo(['ent_rata_gigante'])
    red._fichas.marcar_en_uso('ent_rata_gigante')
    referencias = red._fichas.contador_referencias_adquiridas
    with pytest.raises(CacheFichasLlenaError):
        red.garantizar_contenido(4)              # trae un guardián óseo
    assert not red.contenido_cargado(4)
    assert red._fichas._nodo('ent_rata_gigante').valor.en_uso == 1
    adquiridas = red._fichas.contador_referencias_adquiridas - referencias
    assert adquiridas == red._fichas.contador_referencias_liberadas
    red._fichas._verificar_invariantes()


def test_cache_de_una_ficha_con_varios_enemigos_se_detiene_sin_duplicar(tmp_path):
    """Con capacidad 1 no se pueden proteger dos tipos de enemigo vivos a la
    vez: la partida se detiene con el motivo en vez de seguir corrupta."""
    from controlador.controlador_juego import ControladorJuego
    from controlador.inicio_partida import nueva_partida
    from herramientas.verificar_determinismo import VistaGuion
    comandos = list('NWSEN') + ['T', 'N', 'E', 'S', 'W', 'N', 'N', 'E'] * 3
    with pytest.raises(CacheFichasLlenaError, match='--cache-size'):
        sesion = nueva_partida(DatosOffline(), 'cripta-01', str(tmp_path / 'cache'),
                               semilla=3, cache_size=1)
        sesion.partida.jugador.vida_max = sesion.partida.jugador.vida = 100000
        ControladorJuego(sesion, VistaGuion(comandos)).jugar()
