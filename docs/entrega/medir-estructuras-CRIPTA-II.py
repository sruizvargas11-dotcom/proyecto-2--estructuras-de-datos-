import json
from pathlib import Path
from time import perf_counter_ns
from bench.ciclo import RedPrecargada, PuertoMedicion, ejecutar_intervalo, resumen
from bench.terreno_cazador import _fixture, _crear_partida
from controlador.controlador_juego import ControladorJuego
from controlador.inicio_partida import SesionPartida

datos, checksum = _fixture()
resultados = {}
for perfil in ('reglas-anteriores-simuladas','carga-parte-II'):
 ciclos, retrocesos = [], []
 for _ in range(5):
  partida, actores = _crear_partida(datos,[1000,10000])
  if perfil == 'reglas-anteriores-simuladas':
   for enemigo in actores:
    enemigo.comportamiento = 'guardián'
   for sala in partida.cripta.recorrer_salas():
    for salida in sala.salidas:
     salida.costo = 100
  controlador = ControladorJuego(SesionPartida(partida,RedPrecargada(),None,None),PuertoMedicion())
  for n in range(205):
   partida.reloj.tiempo_actual = partida.reloj.proximo().tiempo
   inicio = perf_counter_ns()
   ejecutar_intervalo(controlador)
   if n >= 5:
    ciclos.append((perf_counter_ns()-inicio)/1e6)
   if n >= 5 and n % 5 == 4:
    inicio = perf_counter_ns()
    exito = partida.historial.revertir()
    retrocesos.append((perf_counter_ns()-inicio)/1e6)
    if not exito:
     raise RuntimeError('No hay intervalo para revertir')
    partida.historia.truncar(partida.acciones_jugador)
    controlador.vista.direccion = 'O' if controlador.vista.direccion == 'E' else 'E'
 resultados[perfil] = dict(ciclo=resumen(ciclos), retroceso=resumen(retrocesos), ciclos=len(ciclos), reversiones=len(retrocesos))
Path(__file__).with_name('CRIPTA-II-medicion-estructuras.json').write_text(json.dumps(dict(fixture=checksum,resultados=resultados),indent=2),encoding='utf-8')
print(resultados)
