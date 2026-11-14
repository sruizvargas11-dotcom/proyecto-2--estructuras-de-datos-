# Borrador de requisitos: niebla de guerra y viaje automático

Autor asignado: José. Revisor asignado: Daniel. Preparación de fase B, 2026-11-05.
Destino previsto de la fase C: `specs/002-niebla-viaje/spec.md`.
Estado: borrador para revisión; no es la especificación generada/aprobada.
Fuentes: enunciado CRIPTA Parte II §3.3, §3.4, §5.3, §6.1, §6.3, §7.3 y Apéndice B. Aplicar las enmiendas oficiales si el equipo recibe alguna.

## Lo que debe poder hacer el jugador

1. Consultar un mapa que muestre exclusivamente lo que conoce de la cripta.
2. Distinguir salas exploradas, avistadas y desconocidas. La sala inicial está explorada desde el instante 0. Una sala visitada queda explorada; una sala no explorada que sea destino de una salida de una explorada está avistada; las demás son desconocidas. La antorcha también puede explorar salas sin visitarlas.
3. De una explorada, conocer nombre, salidas, costo de cada salida y el último estado observado de sus puertas. De una avistada, conocer solo su existencia detrás de la salida; no revelar nombre, contenido ni salidas propias. De una desconocida, no revelar información.
4. Observar el estado real de una puerta cuando el jugador esté en cualquiera de sus extremos. Recordar esa última observación aunque la puerta cambie lejos del jugador. El mapa puede estar desactualizado deliberadamente; no actualizarlo usando información que el jugador no observó.
5. Con la antorcha encendida, al entrar a una sala explorar también todas sus vecinas a través de salidas abiertas o cerradas. Revelar sus nombres y salidas sin revelar su contenido ni activar enemigos o trampas. Actualizar las salas avistadas que resulten de las nuevas salas exploradas.
6. Mantener separado el conocimiento del jugador del mapa real completo y de la precarga. Descargar datos por infraestructura no equivale a explorarlos. La vista y el viaje automático solo pueden usar conocimiento del jugador. El cazador mantiene el conocimiento completo definido por su propia capacidad.
7. Guardar y cargar el conocimiento; restaurarlo exactamente al usar retroceso; permitir reconstruir el conocimiento que existía en cada consulta histórica. La consulta histórica debe ser aislada del conocimiento actual.

## Comportamiento de ir a

8. Aceptar `ir a <sala>` para un destino explorado. Rechazar destino no explorado sin consumir tiempo virtual.
9. Elegir un camino compuesto solo por salas exploradas y salidas recordadas abiertas. Minimizar el costo total de tránsito. Si varios primeros pasos permiten el costo mínimo, elegir la vecina de menor ID, con la misma regla observable que el cazador.
10. Recalcular antes de cada paso con el conocimiento vigente. Si una nueva observación revela una puerta cerrada, actualizar el recuerdo y buscar alternativa conocida. Si no existe, detenerse sin consumo de tiempo adicional por el intento fallido.
11. Ejecutar cada paso como movimiento ordinario completo: aplicar su tiempo según las reglas compartidas de terreno/velocidad y ejecutar normalmente los eventos del reloj entre pasos. No teletransportar ni omitir efectos del juego.
12. Detener el viaje al llegar al destino, entrar a una sala con enemigos activos o dormidos, recibir daño o perder toda ruta conocida. Mostrar la causa de la parada. Los enemigos dormidos de la sala a la que se entra se activan conforme a P1.
13. No abrir puertas automáticamente, incluso si el jugador posee la llave.
14. Registrar cada paso individualmente en partida.log y la orden ir a como comentario de depuración. Conservar la reproducción determinista.
15. El pergamino revierte solo el último paso, con sus cambios asociados; no reinicia ni continúa automáticamente el viaje interrumpido.

## Operaciones y mediciones exigidas

16. Consultar frecuentemente el estado conocido de salas y puertas sin depender de una vista concreta. Explorar nuevas salas debe costar proporcionalmente a las salas reveladas, no al total del mapa conocido. Registrar/invertir cambios de conocimiento debe ser barato y compatible con historia.
17. Medir en --bench las consultas de estados, recuerdos de puertas y el cálculo de un paso de ir a. El cálculo del paso debe cumplir 5 ms con el mapa conocido completo de la cripta de referencia, sin red ni renderizado, salvo enmienda oficial. Conservar datos reproducibles y describir entorno, semilla y resultados; no afirmar cumplimiento sin medir.
18. Ofrecer mapa conocido, ejecución de ir a y causa de parada en la interfaz mínima del proyecto; coordinar su presentación con las vistas existentes sin filtrar información del mapa real.

## Casos obligatorios de aceptación a trasladar a la spec

- Destino no explorado: rechazo y cero tiempo consumido.
- Puerta recordada abierta pero realmente cerrada: actualizar al observarla y recalcular; tomar alternativa conocida o detenerse sin tiempo adicional si no queda ruta.
- Entrada en sala con enemigos dormidos: activación ordinaria y detención del viaje.
- Entrada con antorcha encendida: vecinas exploradas incluso tras puertas cerradas; ningún enemigo o trampa de esas vecinas se activa por la revelación.
- Retroceso de entrada con antorcha: cada sala y recuerdo afectado vuelve a su estado anterior, conservando lo que ya se conocía antes.
- Retroceso durante viaje: solo último paso revertido; viaje sin reanudación.

Agregar escenarios para menor costo frente a menos salas, empate de primer paso, ruta inexistente, daño entre pasos, puertas que cambian sin observación, guardado/carga y conocimiento histórico sin filtración del estado actual. Los seis casos anteriores provienen del Apéndice B; los adicionales verifican reglas del cuerpo del enunciado. No asignar números globales G sin coordinarlos con la matriz del equipo.

## Coordinación antes del diseño técnico

- Daniel y José: contrato del cálculo de ruta para aceptar exclusivamente las salas y puertas que cada consumidor puede conocer, aplicar costos y desempates, y evitar que ir a use el conocimiento completo del cazador.
- Sebastián y José: cambios de conocimiento reversibles, persistencia e historia; definir el estado antes/después y el corte de un viaje al retroceder.
- Centeno y José: la caché/precarga no debe revelar conocimiento ni duplicar solicitudes fuera del presupuesto.
- Daniel y José: coordinar archivos compartidos de vistas y controladores; acordar responsables antes de integración.

## Puntos que debe resolver clarify

Precisar con Daniel el caso destino igual a la sala actual, el comportamiento si ya hay enemigos al emitir la orden y el orden de causas cuando coinciden llegada, daño y enemigos. Definir el mensaje ante ID inexistente y formato del mapa sin exponer salas desconocidas. Aclarar el alcance de la observación de puertas de vecinas reveladas por antorcha sin confundir revelación con presencia física. No inventar decisiones definitivas antes de esa revisión.

Las estructuras ya acordadas por el equipo, los algoritmos, las clases y los módulos se documentarán en plan.md durante la fase D; no forman parte del qué del juego. Este documento no registra prompts como si hubieran sido enviados ni declara completadas las fases C/D.
