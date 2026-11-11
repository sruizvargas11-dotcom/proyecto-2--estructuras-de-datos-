import pytest

from modelo.entidades.enemigo import Enemigo


def test_rango_de_cazador_es_entero_positivo():
    ficha = {
        "id": "c",
        "nombre": "Cazador",
        "vida_max": 10,
        "ataque": 1,
        "defensa": 0,
        "velocidad": 100,
        "comportamiento": "cazador",
        "rango": 1,
    }
    assert Enemigo.desde_ficha("e", ficha).rango == 1


@pytest.mark.parametrize("rango", [None, 0, -1, 1.5])
def test_rango_invalido_se_rechaza(rango):
    ficha = {
        "id": "c",
        "nombre": "Cazador",
        "vida_max": 10,
        "ataque": 1,
        "defensa": 0,
        "velocidad": 100,
        "comportamiento": "cazador",
        "rango": rango,
    }
    with pytest.raises(ValueError):
        Enemigo.desde_ficha("e", ficha)
