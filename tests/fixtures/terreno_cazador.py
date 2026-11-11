"""Constructores de payloads deterministas para terreno y cazador."""


def salida(destino, *, costo_ausente=True, costo=100, cerrada=False):
    dato = {"sala": destino, "cerrada": cerrada}
    if not costo_ausente:
        dato["costo"] = costo
    return dato


def conexion_bidireccional(origen, destino, *, costo_a=None, costo_b=None):
    primero = salida(destino, costo_ausente=costo_a is None, costo=costo_a)
    segundo = salida(origen, costo_ausente=costo_b is None, costo=costo_b)
    return {
        origen: {"id": origen, "salidas": {"E": primero}},
        destino: {"id": destino, "salidas": {"O": segundo}},
    }


def ficha_cazador(*, rango=1, comportamiento="cazador"):
    return {
        "id": "bench-cazador",
        "nombre": "Cazador de benchmark",
        "vida_max": 100,
        "ataque": 1,
        "defensa": 0,
        "velocidad": 100,
        "comportamiento": comportamiento,
        "rango": rango,
        "suelta": [],
        "regeneracion": 0,
    }
