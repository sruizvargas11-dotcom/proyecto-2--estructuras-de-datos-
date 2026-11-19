# Validación de integración con `cripta-02`

**Fecha:** 18 de noviembre de 2026  
**Entorno:** Windows, Python 3.12.10  
**Tipo de prueba:** exploratoria contra el servicio HTTP real; no es una prueba automatizada de CI.

## Alcance

Se eligió `cripta-02` porque aparece en el catálogo del servicio y no forma parte de las criptas locales offline. La ejecución comprobó la carga y validación de datos remotos, el inicio de una partida nueva y un movimiento del jugador. Se usaron carpetas temporales para aislar caché, puntajes y reportes de la partida.

## Resultados

- El servicio respondió al listado de criptas y devolvió `cripta-02` (`Catacumbas menores`).
- `python main.py --verificar cripta-02` produjo el veredicto **RESOLUBLE**. La ruta reportada usa la llave de bronce para abrir la conexión hacia la sala 2 y la llave negra para llegar a la salida en la sala 18.
- La partida inició con las versiones de cripta `52532a77ee04` y catálogo `4b9e75a42be5`.
- La sala inicial informó la salida norte a sala 2 como abierta, con costo efectivo 60. El comando `N` trasladó al jugador a esa sala y el estado mostró sus salidas, objetos y costo de regreso.
- La partida se cerró con `Q` después de ese movimiento. El reporte de red registró 8 solicitudes de un presupuesto de 23 y 10 salas incorporadas; no informó errores de precarga.

## Límites de esta evidencia

Esto valida una parte del flujo online con una cripta no incluida en los datos offline, pero **no** demuestra una partida completa. No se alcanzó la salida ni se probaron en juego todas las llaves, enemigos, trampas, fallos de red, recarga desde caché o cambios de versión. El resultado no debe presentarse como cobertura completa de los casos borde.

El siguiente paso para cerrar esta brecha es ejecutar y registrar una partida hasta victoria o derrota en `cripta-02`, y probar por separado los casos borde del servicio que el equipo haya comprometido en el enunciado. Mantener la evidencia de cada ejecución sin reemplazar reportes anteriores.
