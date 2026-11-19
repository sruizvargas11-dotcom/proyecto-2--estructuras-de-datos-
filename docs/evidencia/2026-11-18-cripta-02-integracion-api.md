# Validación de integración con `cripta-02`

**Fecha:** 18 de noviembre de 2026  
**Entorno:** Windows, Python 3.12.10  
**Tipo de prueba:** exploratoria contra el servicio HTTP real; no es una prueba automatizada de CI.

## Primera ejecución: integración parcial

Se eligió `cripta-02` porque aparece en el catálogo del servicio y no forma parte de las criptas locales offline. La ejecución comprobó la carga y validación de datos remotos, el inicio de una partida nueva y un movimiento del jugador. Se usaron carpetas temporales para aislar caché, puntajes y reportes de la partida.

### Resultados

- El servicio respondió al listado de criptas y devolvió `cripta-02` (`Catacumbas menores`).
- `python main.py --verificar cripta-02` produjo el veredicto **RESOLUBLE**. La ruta reportada usa la llave de bronce para abrir la conexión hacia la sala 2 y la llave negra para llegar a la salida en la sala 18.
- La partida inició con las versiones de cripta `52532a77ee04` y catálogo `4b9e75a42be5`.
- La sala inicial informó la salida norte a sala 2 como abierta, con costo efectivo 60. El comando `N` trasladó al jugador a esa sala y el estado mostró sus salidas, objetos y costo de regreso.
- La partida se cerró con `Q` después de ese movimiento. El reporte de red registró 8 solicitudes de un presupuesto de 23 y 10 salas incorporadas; no informó errores de precarga.

### Límites de la primera ejecución

Esta primera ejecución validó solo una parte del flujo online: no alcanzó la salida ni probó en juego las llaves, enemigos y trampas. Su alcance quedó ampliado por la segunda ejecución registrada abajo.

## Segunda ejecución: partida completa

**Fecha:** 18 de noviembre de 2026
**Entorno:** Windows 11, Python 3.12.10
**Cripta:** `cripta-02`, versión `52532a77ee04`
**Catálogo:** versión `4b9e75a42be5`
**Tipo de prueba:** partida manual contra el servicio HTTP real, con caché, partidas y reportes aislados en una carpeta temporal.

### Resultado

- La partida terminó en **victoria** al llegar a la sala de salida 18. Se registraron 39 acciones del jugador, 7 enemigos derrotados y tiempo virtual final 3185.
- Se recogieron y usaron la llave de bronce y la llave negra; se abrió la puerta final entre las salas 17 y 18.
- La partida ejercitó combate contra ratas gigantes, un guardián óseo y un sabueso óseo, además de la activación de una trampa y el uso de pociones. La salida inicial conservó el costo efectivo 60 observado en la primera ejecución.
- El reporte registró 10 solicitudes de un presupuesto de 23, 20 salas incorporadas desde el servicio, cero errores de precarga y cero esperas bloqueantes.
- La semilla de esta partida fue `1535542461`. Se ejecutó con nombre `CodexQA` y se aisló su tabla de puntajes para no mezclarla con datos de usuario.

### Alcance restante

La partida completa valida el flujo normal de lectura HTTP, resolución, exploración, combate, objetos, puerta cerrada y victoria en `cripta-02`. No fuerza fallos de red, respuestas malformadas, incompatibilidad de versiones, agotamiento del presupuesto ni recuperación desde una caché ya poblada. Esos casos deben cubrirse mediante pruebas controladas del adaptador; esta sesión en vivo no demuestra su comportamiento. La evidencia tampoco afirma cobertura de todas las combinaciones del juego.
