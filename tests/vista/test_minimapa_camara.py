"""Regresión: mapas grandes no invaden vida/equipo y siguen la sala actual."""
import pygame
import pytest
from vista_pygame.render.render_sala import dibujar_minimapa
from vista_pygame.config_vista import COLOR_ORO


@pytest.mark.parametrize('actual',[1,25,50])
def test_mapa_de_50_salas_se_recorta_y_sigue_al_jugador(actual):
    im=pygame.Surface((500,500));im.fill((220,0,220));antes=im.copy()
    rect=pygame.Rect(80,30,292,100)
    layout=[(i,0,1-i) for i in range(1,51)]+[(51,30,0),(52,-30,0)]
    dibujar_minimapa(im,rect,layout,list(range(1,actual+1)),actual,None)
    # La barra de vida, equipo y las zonas exteriores conservan cada píxel.
    for region in (pygame.Rect(0,0,500,rect.top),pygame.Rect(0,rect.bottom,500,500-rect.bottom),
                   pygame.Rect(0,0,rect.left,500),pygame.Rect(rect.right,0,500-rect.right,500)):
        assert pygame.image.tobytes(im.subsurface(region),'RGB')==pygame.image.tobytes(antes.subsurface(region),'RGB')
    assert im.get_at(rect.center)[:3]==COLOR_ORO
    assert im.get_clip()==im.get_rect()


def test_minimapa_respeta_y_restaura_un_recorte_preexistente():
    im=pygame.Surface((400,240));im.fill((220,0,220))
    clip=pygame.Rect(100,80,80,70);im.set_clip(clip)
    dibujar_minimapa(im,pygame.Rect(20,20,300,150),[(1,0,0),(2,0,-1)],[1],1,None)
    assert im.get_clip()==clip
    assert im.get_at((20,20))[:3]==(220,0,220)
    dibujar_minimapa(im,pygame.Rect(20,20,300,150),[],[],1,None)
    assert im.get_clip()==clip


def test_escena_recalcula_layout_minimapa_cuando_cambia_topologia():
    from controlador.controlador_pygame import SalaTopologia
    from vista_pygame.escenas.partida import EscenaPartida

    class ControladorFalso:
        def __init__(self):
            self.topologia = [
                SalaTopologia(1, "Entrada", [("N", 2)]),
                SalaTopologia(2, "", []),
            ]
        def esperando_red(self): return False
        def estado(self): return None
        def revision_sesion(self): return 0
        def error_pendiente(self): return None
        def topologia_cripta(self): return list(self.topologia)
        def sala_inicial_id(self): return 1
        def eventos_nuevos(self): return []

    class ContextoFalso:
        def __init__(self, controlador):
            self.controlador = controlador
            self.entrada_cinematica = False

    ctl = ControladorFalso()
    escena = EscenaPartida(ContextoFalso(ctl))
    escena.al_entrar(None)
    escena.actualizar(16)
    assert [sid for sid, _, _ in escena._layout_minimapa] == [1, 2]

    # Al explorar la sala 2 se revelan sus salidas hacia 3 y 5.
    ctl.topologia = [
        SalaTopologia(1, "Entrada", [("N", 2)]),
        SalaTopologia(2, "Pasillo", [("S", 1), ("N", 3), ("E", 5)]),
        SalaTopologia(3, "", []),
        SalaTopologia(5, "", []),
    ]
    escena.actualizar(16)
    assert [sid for sid, _, _ in escena._layout_minimapa] == [1, 2, 3, 5]

    # Al retroceder vuelve a la topología previa.
    ctl.topologia = [
        SalaTopologia(1, "Entrada", [("N", 2)]),
        SalaTopologia(2, "", []),
    ]
    escena.actualizar(16)
    assert [sid for sid, _, _ in escena._layout_minimapa] == [1, 2]
