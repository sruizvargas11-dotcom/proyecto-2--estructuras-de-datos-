import os
from dataclasses import dataclass
from estructuras.vector_dinamico import Vector

from bitacora_partida import BitacoraPartida
from controlador.controlador_red import (
    ControladorRed,
    _carpeta_cache_por_defecto,
    _generales,
    cargar_cripta,
)
from controlador.semilla import generar_semilla, validar_semilla
from modelo.entidades.jugador import Jugador
from modelo.entidades.objetos.fabrica_objetos import FabricaObjetos
from modelo import efectos
from modelo.partida import Partida
from modelo.verificador_resolubilidad import verificar_resolubilidad
from persistencia.llaves_cripta import obtener_llaves


NOMBRE_JUGADOR_POR_DEFECTO = "Jugador"


class InicioBloqueado(RuntimeError):
    """Inicio rechazado; conserva el resultado para presentarlo al usuario."""

    def __init__(self, resultado):
        self.resultado = resultado
        super().__init__(
            f"Inicio bloqueado por veredicto {resultado.veredicto}."
        )


@dataclass(frozen=True)
class ResultadoNoVerificable:
    veredicto: str = "NO VERIFICABLE"
    motivo: str = "consulta de llaves no disponible"


def asegurar_inicio_permitido(resultado, forzar=False):
    """Bloquea resultados no favorables salvo que el usuario fuerce el inicio."""
    if (
        resultado.veredicto in ("NO RESOLUBLE", "NO VERIFICABLE")
        and not forzar
    ):
        raise InicioBloqueado(resultado)


class SesionPartida:
    """Lo que el controlador del juego necesita después del arranque."""

    def __init__(self, partida, red, fuente, bitacora=None, esqueleto_desde_cache=None,
                 nombre_jugador=None, resultado_resolubilidad=None):
        self.partida = partida
        self.red = red
        self.fuente = fuente
        self.bitacora = bitacora
        self.acciones = Vector()
        self.esqueleto_desde_cache = esqueleto_desde_cache
        self.resultado_resolubilidad = resultado_resolubilidad
        # Dato de presentación, no del modelo (no vive en Jugador): lo exige la
        # tabla de puntajes (§2.12) y se guarda con la partida. Nunca vacío.
        self.nombre_jugador = (nombre_jugador or NOMBRE_JUGADOR_POR_DEFECTO).strip() \
            or NOMBRE_JUGADOR_POR_DEFECTO


def ruta_bitacora_por_defecto(cripta_id, semilla, carpeta=None):
    if carpeta is None:
        raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        carpeta = os.path.join(raiz, "partidas", "bitacoras")
    return os.path.join(carpeta, f"{cripta_id}_{semilla}.log")


class _FuenteConGenerales:
    """Entrega a cargar_cripta los datos generales ya pedidos, sin repetir la
    solicitud; todo lo demás va a la fuente real."""

    def __init__(self, fuente, generales):
        self._fuente = fuente
        self._generales = generales

    def datos_cripta(self, cripta_id):
        return self._generales

    def __getattr__(self, nombre):
        return getattr(self._fuente, nombre)


def _resolvedor_fichas(red):
    """resolver_ficha para la Partida: memoria (LRU) -> disco -> red."""
    def resolver(tipo_id):
        ficha = red.ficha(tipo_id)
        if ficha is None:
            red.resolver_catalogo([tipo_id])
            ficha = red.ficha(tipo_id)
        return ficha
    return resolver


def _validar_jugador(generales):
    datos = generales.get("jugador")
    if not isinstance(datos, dict):
        raise ValueError("Datos de cripta inválidos: faltan las estadísticas del jugador.")
    for campo in ("vida_max", "ataque", "defensa", "velocidad"):
        if type(datos.get(campo)) is not int:
            raise ValueError(f"Datos de cripta inválidos: jugador.{campo} debe ser entero.")


def nueva_partida(fuente, cripta_id, carpeta_cache=None, semilla=None,
                  ruta_bitacora=None, cache_size=25, despachador=None,
                  nombre_jugador=None, forzar=False, verificar=True):
    """Crea e inicializa una partida. Devuelve SesionPartida.

    semilla=None  -> partida nueva: se genera automáticamente (nunca la elige el jugador).
    semilla=int   -> replay o carga: se reutiliza la guardada.
    ruta_bitacora -> si se da, se crea la bitácora append-only con la semilla en el
                     encabezado. Use ruta_bitacora_por_defecto(...) para la ubicación
                     estándar.
    despachador   -> None (DespachoInmediato) o DespachoEnHilos() para que la
                     precarga viaje en segundo plano; el orden sigue siendo
                     determinista gracias al buffer de reordenamiento.
    nombre_jugador -> quién juega (consola o GUI lo piden antes de llamar aquí);
                     no se guarda en el modelo, solo en la sesión. Si se omite,
                     usa NOMBRE_JUGADOR_POR_DEFECTO (p. ej. para el replay, que
                     hoy no guarda este dato en la bitácora).
    forzar         -> permite iniciar con NO RESOLUBLE o NO VERIFICABLE.
    verificar      -> False solo para flujos que no inician una partida nueva,
                     como replay.
    """
    semilla = generar_semilla() if semilla is None else validar_semilla(semilla)

    generales = _generales(fuente, cripta_id)        # 1 solicitud
    _validar_jugador(generales)
    cripta, desde_cache = cargar_cripta(_FuenteConGenerales(fuente, generales), cripta_id,
                                        carpeta_cache)

    resultado_resolubilidad = None
    if verificar:
        consulta_llaves = getattr(fuente, "llaves_cripta", None)
        if not callable(consulta_llaves):
            resultado_resolubilidad = ResultadoNoVerificable()
        else:
            carpeta_cache_llaves = (
                carpeta_cache
                if carpeta_cache is not None
                else _carpeta_cache_por_defecto()
            )
            try:
                respuesta_llaves = obtener_llaves(
                    fuente,
                    carpeta_cache_llaves,
                    cripta_id,
                    cripta.version,
                )
            except (OSError, RuntimeError):
                resultado_resolubilidad = ResultadoNoVerificable()
            else:
                if (
                    not isinstance(respuesta_llaves, dict)
                    or not isinstance(respuesta_llaves.get("llaves"), list)
                ):
                    raise ValueError("Respuesta de llaves inválida.")
                resultado_resolubilidad = verificar_resolubilidad(
                    cripta,
                    respuesta_llaves["llaves"],
                )
        asegurar_inicio_permitido(resultado_resolubilidad, forzar)

    # Dos fábricas con prefijo distinto: los ids del contenido dependen solo del
    # orden de número de las solicitudes; los del botín, solo de las acciones.
    fabrica_contenido = FabricaObjetos(prefijo="objeto")
    fabrica_botin = FabricaObjetos(prefijo="botin")
    red = ControladorRed(fuente, cripta, carpeta_cache, fabrica=fabrica_contenido,
                         cache_size=cache_size, despachador=despachador, completar_lotes=True)
    sala_inicial = cripta.sala_por_id(cripta.sala_inicial_id)
    # Encola primero las vecinas para incluirlas en el lote de la sala inicial.
    red.planificar_precarga(sala_inicial)
    red.garantizar_contenido(sala_inicial.id)
    # Para la bitácora; normalmente ya se obtuvo al resolver el catálogo del lote.
    version_catalogo = red.version_catalogo()

    jugador = Jugador.desde_generales(generales, sala_inicial)
    partida = Partida(cripta, jugador, semilla, version_catalogo,
                      fabrica=fabrica_botin, resolver_ficha=_resolvedor_fichas(red))
    partida.al_morir_enemigo.agregarValor(red.notificar_muerte_enemigo)
    partida.aplicar_efecto = efectos.aplicar_efecto_objeto
    partida.inicializar()

    bitacora = None
    if ruta_bitacora is not None:
        bitacora = BitacoraPartida.partida_nueva(
            ruta_bitacora, cripta.id, cripta.version, version_catalogo, semilla)
    return SesionPartida(
        partida,
        red,
        fuente,
        bitacora,
        desde_cache,
        nombre_jugador,
        resultado_resolubilidad,
    )
