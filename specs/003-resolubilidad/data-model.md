# Modelo de datos: Verificación de resolubilidad

Este documento describe los datos que entran y salen del verificador. No define reglas
de partida nuevas y no prescribe el formato textual, que pertenece a la presentación.

## Entradas lógicas

### Cripta

Vista de solo lectura de `CriptaModelo`, `Sala` y `Salida`.

| Campo | Tipo lógico | Validación/uso |
|---|---|---|
| `salas` | colección de salas | IDs no densos; cada destino de salida debe existir. |
| `sala_inicial_id` | entero | Debe identificar una sala. |
| `sala_salida_id` | entero | Debe identificar una sala. |
| `llave_salida` | id de llave en la spec; nullable en el modelo actual | Identifica la llave y las puertas de salida relevantes. La semántica de `None` requiere aclaración. |
| salida `direccion` | dirección | Salida dirigida desde su sala de origen. |
| salida `sala_destino_id` | entero | Destino de esa salida, sin inferir el arco inverso. |
| salida `cerrada` | booleano | Determina si requiere una llave para el cruce hipotético. |
| salida `llave` | id opcional en el modelo actual | Llave que permite cruzar la puerta cerrada. La semántica de una salida cerrada sin ID de llave no está fijada por la spec. |
| salida `costo` | entero | Se conserva en el modelo, pero no interviene en la decisión. |

El modelo no cambia `Salida`, sus cierres, trampas o el estado de una partida. Para la
verificación, una salida abierta se cruza; una cerrada se cruza si ya se otorgó su llave.

### Ubicación de llave

Una entrada lógica por ubicación reportada:

| Campo | Tipo lógico | Validación/uso |
|---|---|---|
| `id` | texto no vacío | Identidad de la llave; orden lexicográfico por código de carácter. |
| `sala` | entero | Sala de obtención. Si hay `enemigo`, es la sala donde ese enemigo inicia. |
| `enemigo` | texto opcional | Identidad del enemigo que la suelta; no es necesario para la alcanzabilidad. |

Un mismo `id` puede aparecer en varias ubicaciones. Basta una ubicación alcanzable para
obtener la llave; el orden elige la ubicación alcanzable de menor ID numérico. Si ninguna
es alcanzable, el diagnóstico conserva todas las ubicaciones.

## Estado lógico de recorrido

### Puerta pendiente

Representa una salida cerrada cuyo origen ya está en la región actual y cuya llave aún
no se ha otorgado.

| Campo | Uso |
|---|---|
| sala de origen | Orden de reporte y validación de pertenencia a región. |
| dirección | Identifica la salida y contribuye al orden determinista. |
| sala de destino | Se incorpora a la región cuando se libera la puerta. |
| llave requerida | Índice para localizar puertas al obtener esa llave. |

Las salidas abiertas se expanden directamente. Una salida cerrada cuyo ID de llave no
aparece en la consulta permanece pendiente y puede aparecer en la frontera con ubicación
«inexistente». Esto no resuelve el caso distinto de una salida cerrada cuyo campo de
llave es nulo o falta.

### Ronda

| Campo | Uso |
|---|---|
| número | 0 para las llaves alcanzables sin cruzar cerradas; luego números consecutivos. |
| llaves nuevas | Llaves alcanzables usando solo las rondas anteriores, ordenadas por sala numérica e id lexicográfico. |
| ubicaciones elegidas | Para cada llave obtenida, ubicación alcanzable de menor sala. |

El lote completo de llaves de una ronda se determina y ordena antes de habilitar las
puertas que esas llaves abren. La ronda en que la puerta final pasa a ser cruzable se
incluye completa. El orden termina allí.

## Resultado y reporte

### Estado

El resultado de modelo distingue:

- `RESOLUBLE`: llave de salida obtenida y una puerta que la requiere puede cruzarse
  hacia `sala_salida`.
- `NO RESOLUBLE`: falta la llave de salida o no hay puerta final válida alcanzable.
- `NO VERIFICABLE`: no se pudo consultar la fuente de llaves o no había presupuesto.
- `ERROR DE DATOS`: entrada inválida, sala/enemigo referenciado inexistente o extremos
  requeridos ausentes. No es forzable.

`NO VERIFICABLE` y `ERROR DE DATOS` no se presentan como veredictos de alcanzabilidad
con éxito o fracaso; el serializador/CLI conserva su distinción.

### Resultado resoluble

Contiene veredicto, orden de llaves por rondas, puerta final y datos necesarios para
comprobar validez, completitud y determinismo. La puerta final es la primera cruzable
por sala de origen numérica y dirección, según el orden de dirección que la especificación
debe completar.

### Resultado no resoluble

Contiene motivo (a)/(b), cantidad de salas alcanzables, cantidad de llaves obtenidas,
llaves inobtenibles con ubicaciones y causa, frontera bloqueada y ciclos. La frontera se
captura en el recorrido base. Las llaves se ordenan por ID; frontera por sala de origen
y dirección; dependencias por ID. El desempate exacto de direcciones y ubicaciones
duplicadas iguales requiere la aclaración listada en el plan.

### Error de datos

Los errores de datos incluyen sala inicial/salida inexistentes y ubicación de llave que
refiere a sala o enemigo inexistente. Los errores se propagan de manera explícita al
controlador para impedir `--forzar`. La capacidad de validar el roster del enemigo con
los datos actualmente disponibles está pendiente del contrato del servicio.

## Relaciones

- Una cripta tiene muchas salas; una sala tiene cero o más salidas dirigidas.
- Una llave puede tener una o más ubicaciones.
- Una salida cerrada puede requerir una llave; varias salidas pueden requerir el mismo ID.
- Una llave obtenida libera todas las puertas pendientes indexadas por ese ID; no se
  consume.
- Una llave indispensable crea una relación dirigida de dependencia para el diagnóstico.
- El resultado de verificación contiene el subconjunto de reporte correspondiente a su
  estado.

## Validaciones

1. Confirmar existencia de sala inicial y de salida antes de recorrer.
2. Confirmar que todas las salidas apuntan a destinos existentes.
3. Confirmar que cada ubicación de llave apunta a una sala válida y que referencias de
   enemigo son válidas conforme al contrato de fuente.
4. Considerar obsoleta la caché de llaves si su versión difiere de `CriptaModelo.version`.
5. No rechazar una puerta solo porque su llave no aparezca en la lista: esa llave se
   reporta como inexistente y la puerta nunca se libera.
6. No permitir que el costo, cierres automáticos o trampas cambien la alcanzabilidad
   hipotética.
