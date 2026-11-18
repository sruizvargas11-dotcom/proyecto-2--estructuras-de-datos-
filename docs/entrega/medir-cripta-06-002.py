import json, platform, subprocess
from pathlib import Path
from time import perf_counter_ns
from adaptadores.datos_http import DatosHTTP
from controlador.controlador_red import cargar_esqueleto_completo
from modelo.conocimiento import ConocimientoJugador
from bench.medicion import medir

fuente = DatosHTTP(max_reintentos=0)
cripta = cargar_esqueleto_completo(fuente, 'cripta-06')
salas = list(cripta.recorrer_salas())
assert len(salas) == 300
conocimiento = ConocimientoJugador(cripta)
for sala in salas:
    conocimiento.visitar(sala, 0)
for sala in salas:
    conocimiento.observar(sala, 0)
assert all(conocimiento.explorada(s.id) for s in salas)
solicitudes = fuente.requests_realizados
# Longest accessible route from the entrance by weighted cost.
entrada = 141
rutas = [(paso[3], sala.id) for sala in salas if (paso := conocimiento.siguiente_paso(entrada, sala.id))]
costo, destino = max(rutas)
m = medir(conocimiento.siguiente_paso, entrada, destino, repeticiones=100)
assert fuente.requests_realizados == solicitudes
r = dict(commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
         python=platform.python_version(), so=platform.platform(), cpu=platform.processor(),
         cripta=cripta.id, version=cripta.version, salas=len(salas), origen=entrada, destino=destino,
         costo=costo, preparacion_http=solicitudes, http_durante_medicion=0,
         mediana_ms=m.ms_med, p95_ms=m.ms_p95, max_ms=m.ms_max, muestras_ms=list(m.muestras))
Path('cripta-06-benchmark-002.json').write_text(json.dumps(r,indent=2),encoding='utf-8')
print({k:v for k,v in r.items() if k!='muestras_ms'})
