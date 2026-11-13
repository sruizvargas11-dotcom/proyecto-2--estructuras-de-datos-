# Feature Specification: Verificación de resolubilidad de la cripta

**Feature Branch**: `spec/centeno`

**Created**: 2026-11-12

**Status**: Draft

**Input**: User description: "Determinar antes de iniciar una partida si la cripta puede ganarse, explicar los bloqueos y presentar un reporte determinista."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Conocer si la cripta puede ganarse (Priority: P1)

Al iniciar una partida, el jugador recibe el resultado de la verificación y, si la cripta no es resoluble, una explicación de los obstáculos. La partida solo comienza en ese caso si el jugador solicita forzarla.

**Why this priority**: Evita iniciar inadvertidamente una partida imposible y permite entender la causa.

**Independent Test**: Iniciar criptas resolubles y no resolubles y comprobar el reporte y si se permite comenzar.

**Acceptance Scenarios**:

1. **Dado** una cripta con la llave de salida tras la única puerta que dicha llave abre, **Cuando** se verifica, **Entonces** se informa NO RESOLUBLE por llave de salida inobtenible, la frontera bloqueada incluye esa puerta y se informa el ciclo de una llave consigo misma (G14; RS-FR-007, RS-FR-010, RS-FR-011, RS-FR-012).
2. **Dado** una llave asociada a un enemigo errante, **Cuando** se verifica, **Entonces** su ubicación para el reporte y la alcanzabilidad es la sala donde el enemigo inicia (G15; RS-FR-001, RS-FR-015).
3. **Dado** una cripta no resoluble y el inicio de una partida sin opción de forzar, **Cuando** se intenta iniciar, **Entonces** la partida no comienza y se muestra el reporte (G17; RS-FR-014).
4. **Dado** esa misma cripta y la opción de forzar, **Cuando** se intenta iniciar, **Entonces** se muestra el reporte y la partida comienza (G24; RS-FR-014).

---

### User Story 2 - Verificar sin iniciar una partida (Priority: P2)

Un evaluador o desarrollador puede solicitar la verificación de una cripta desde la consola, recibir el reporte y utilizar el resultado del proceso sin abrir la vista del juego.

**Why this priority**: Hace posible evaluar criptas de forma automatizada y separada de una partida.

**Independent Test**: Ejecutar la verificación aislada para criptas resolubles, no resolubles y con errores, observando reporte, código de salida y ausencia de vista.

**Acceptance Scenarios**:

1. **Dado** una cripta resoluble, **Cuando** se ejecuta `--verificar <cripta>`, **Entonces** se imprime el reporte, no se crea la vista y el código de salida es 0 (G22; RS-FR-013).
2. **Dado** una cripta no resoluble, **Cuando** se ejecuta `--verificar <cripta>`, **Entonces** se imprime el reporte, no se crea la vista y el código de salida es 1 (G22; RS-FR-013).
3. **Dado** un error de datos, una ubicación de llave que refiere a una sala o enemigo inexistente, o un error de red, **Cuando** se ejecuta `--verificar <cripta>`, **Entonces** el error se informa y el código de salida es 2 (G23; RS-FR-013, RS-FR-016, RS-FR-018).

---

### User Story 3 - Forzar el inicio de una cripta no resoluble (Priority: P3)

Un jugador que conoce el riesgo puede decidir comenzar aun cuando el reporte indique que la cripta no es resoluble.

**Why this priority**: Conserva una opción explícita para continuar sin ocultar el resultado de la verificación.

**Independent Test**: Intentar iniciar la misma cripta no resoluble con y sin `--forzar` y comparar el reporte y el inicio de la partida.

**Acceptance Scenarios**:

1. **Dado** una cripta no resoluble, **Cuando** el jugador inicia con `--forzar`, **Entonces** el reporte se muestra antes de que comience la partida (G17 y G24; RS-FR-014).

### Escenarios adicionales

1. **Dado** llaves A y B que parecen requerirse mutuamente, pero existe una ruta alternativa que permite llegar a A, **Cuando** se verifica, **Entonces** no se reporta un ciclo de dependencia entre ellas (G18; RS-FR-011).
2. **Dado** una cadena de dependencias A → B → C en que C no puede obtenerse, **Cuando** se informa sobre las llaves inobtenibles, **Entonces** las causas de A y B identifican correctamente la llave inobtenible de la que dependen (G19; RS-FR-011).
3. **Dado** una llave que abre una región con varias llaves, **Cuando** se genera el orden por rondas, **Entonces** las llaves nuevas de esa región aparecen en la ronda siguiente, sin repetir el trabajo sobre la región previamente alcanzada (G20; RS-FR-009, RS-PR-002).
4. **Dado** una sala de salida alcanzable únicamente por una puerta abierta y ninguna puerta hacia ella que requiera la llave de salida, **Cuando** se verifica, **Entonces** el resultado es NO RESOLUBLE por motivo (b) (G21; RS-FR-007, RS-FR-010).
5. **Dado** una puerta de frontera que requiere una llave ausente de la lista de ubicaciones, **Cuando** se genera el reporte, **Entonces** la ubicación de esa llave se indica como «inexistente» (G25; RS-FR-012).
6. **Dado** una cripta, **Cuando** sus costos de salida cambian sin cambiar otros datos, **Entonces** no cambian el veredicto ni el orden de llaves (G26; RS-FR-006).
7. **Dado** una cripta con más de un orden válido de obtención de llaves, **Cuando** se ejecuta la verificación dos veces, **Entonces** ambas ejecuciones producen exactamente el mismo orden por rondas (G16; RS-FR-009, RS-FR-016).
8. **Dado** criptas sintéticas con muchas llaves encadenadas y una semilla determinada, **Cuando** se ejecuta `--bench`, **Entonces** se compara la verificación incremental con una referencia que vuelve a evaluar la cripta por cada llave y se repite el mismo conjunto de datos para la misma semilla (G27; RS-PR-003).
9. **Dado** una cripta cuya lista de llaves persistida corresponde a otra versión, **Cuando** se verifica la cripta actual, **Entonces** esa lista no se considera válida para la versión actual (G28; RS-FR-001).
10. **Dado** una salida descrita desde A hacia B y ninguna salida desde B hacia A, **Cuando** se determina la región alcanzable desde A, **Entonces** B puede alcanzarse desde A pero A no se considera alcanzable desde B por esa salida (G29; RS-FR-002).
11. **Dado** una puerta cerrada que requiere una llave ya obtenida y una llave que abre más de una puerta, **Cuando** se cruza la primera puerta y luego la segunda, **Entonces** ambas se consideran cruzables sin consumir la llave (G30; RS-FR-003).
12. **Dado** una consulta de llaves fallida o presupuesto insuficiente, **Cuando** se verifica, **Entonces** se informa NO VERIFICABLE y `--verificar` termina con código 2; **Y dado** que se intenta iniciar, **Entonces** sin `--forzar` no comienza la partida y con `--forzar` se muestra el reporte y comienza (G31; RS-FR-001, RS-FR-017).
13. **Dado** la cripta publicada más grande, **Cuando** se mide localmente la verificación completa sin red ni renderizado, **Entonces** el tiempo no supera 200 ms (G32; RS-PR-001).
14. **Dado** criptas de distintos tamaños con salas, salidas y llaves crecientes, **Cuando** se compara el trabajo de verificación, **Entonces** este crece aproximadamente en proporción a esas cantidades y obtener otra llave no requiere repetir el trabajo sobre la región ya alcanzada (G33; RS-PR-002).
15. **Dado** un enemigo en una sala alcanzable, **Cuando** se verifica una llave que ese enemigo suelta, **Entonces** se considera que el enemigo puede ser derrotado y que la llave se obtiene en la sala inicial del enemigo (G34; RS-FR-004, RS-FR-015).
16. **Dado** una salida afectada por trampa o cierre automático, **Cuando** se verifica si puede cruzarse conforme a los supuestos, **Entonces** esos efectos no impiden el cruce (G35; RS-FR-005).

### Edge Cases

- La sala de salida no existe en el esqueleto o no hay ninguna puerta dirigida hacia ella que requiera la llave de salida.
- Una llave no se obtiene porque su sala no es alcanzable, aunque se otorguen todas las llaves.
- Una llave depende de otras llaves inobtenibles, incluidas dependencias que forman un ciclo o que aparentan formarlo pero tienen ruta alternativa.
- Varias llaves pueden obtenerse en una misma ronda; deben ordenarse por id de sala ascendente y luego por id de llave ascendente.
- La llave de salida puede obtenerse antes de que sea alcanzable el origen de la puerta final.
- Si falla la consulta de ubicaciones de llaves o no queda presupuesto de solicitudes, se informa NO VERIFICABLE; `--verificar` termina con código 2, el inicio se bloquea salvo que se use `--forzar`.
- Si una ubicación de llave menciona una sala o un enemigo inexistente, se informa error de datos con código 2 en `--verificar` y no se inicia la partida, incluso con `--forzar`.

## Requirements *(mandatory)*

### Definiciones

- **Región alcanzable**: salas a las que se llega desde la sala inicial con las llaves obtenidas.
- **Resoluble**: partiendo de la sala inicial, se obtiene la llave de salida **y** se entra a la sala de salida cruzando una puerta que requiere la llave de salida. Llegar a la sala de salida por una puerta abierta o por una puerta que requiere otra llave no cuenta.
- **Frontera bloqueada**: puertas cerradas cuyo origen está dentro de la región alcanzable y cuyo destino está fuera de ella.
- **Llave indispensable**: la llave `kj` es indispensable para `ki` si la sala de `ki` sigue siendo inalcanzable aun otorgando todas las llaves excepto `kj`.
- **Ciclo**: secuencia `k1 → k2 → … → k1` donde cada llave es indispensable para la anterior; incluye `k → k`. Si existe una ruta alternativa, no hay ciclo y no debe reportarse.

### Functional Requirements

- **RS-FR-001**: La verificación MUST usar el esqueleto de la cripta —salas, sala inicial, sala de salida, llave de salida y salidas— y las ubicaciones de llaves provistas por la consulta «llaves» del servicio. La consulta MUST contar en `presupuesto_solicitudes`. Si se usan ubicaciones persistidas, MUST considerarse inválidas cuando cambie la versión de la cripta. (G15, G28, G31)
- **RS-FR-002**: Cada salida MUST considerarse únicamente en el sentido descrito desde su sala de origen; la presencia de una salida de A a B MUST NOT implicar una salida de B a A. (G29)
- **RS-FR-003**: Para esta verificación, MUST poder cruzarse toda salida abierta y toda salida cerrada cuya llave requerida ya se haya obtenido; las llaves MUST NOT consumirse. Estos supuestos no cambian las reglas de la partida. (G14, G20, G30)
- **RS-FR-004**: Para esta verificación, MUST suponerse que todo enemigo puede ser derrotado; este supuesto no cambia las reglas de la partida. (G34)
- **RS-FR-005**: Para esta verificación, trampas y cierres automáticos MUST NOT bloquear el cruce; este supuesto no cambia las reglas de la partida. (G35)
- **RS-FR-006**: El costo de las salidas MUST NOT afectar el veredicto ni el orden de llaves; solo MUST considerarse la alcanzabilidad. (G26)
- **RS-FR-007**: La cripta MUST declararse resoluble únicamente si se obtiene la llave de salida y se cruza hacia la sala de salida una puerta que requiere esa llave. (G14, G21)
- **RS-FR-008**: Si la cripta es resoluble, el reporte MUST indicar RESOLUBLE y la puerta final mediante la sala de origen y la dirección de la salida que conduce a la sala de salida y requiere la llave de salida. (G14, G21)
- **RS-FR-009**: Si la cripta es resoluble, el reporte MUST incluir cada llave de su orden con su id, sala donde se obtiene y enemigo que la suelta si aplica. La ronda 0 MUST incluir las llaves alcanzables sin cruzar puertas cerradas; cada ronda posterior MUST incluir llaves nuevas alcanzables usando llaves de rondas anteriores. Dentro de cada ronda, las llaves MUST ordenarse por id de sala ascendente y luego por id de llave ascendente. El orden MUST terminar en la ronda en que la puerta final se vuelve cruzable y puede incluir otras llaves obtenidas antes de ese corte. El reporte MUST permitir comprobar validez, completitud y determinismo: cada llave es alcanzable usando solo llaves anteriores, la llave de salida está incluida y permite cruzar la puerta final, y la misma cripta produce el mismo orden. (G16, G20)
- **RS-FR-010**: Si la cripta no es resoluble, el reporte MUST indicar NO RESOLUBLE y uno de estos motivos: (a) la llave de salida es inobtenible; (b) se obtiene la llave de salida pero no se alcanza ninguna puerta hacia la sala de salida que la requiera, incluida la ausencia de tal puerta. MUST resumir la cantidad de salas alcanzables y de llaves obtenidas. (G14, G21)
- **RS-FR-011**: Para cada llave inobtenible, el reporte MUST incluir ubicación (sala y enemigo, si aplica) y causa: en un ciclo, depende de una llave inobtenible identificada por id, o su sala sigue inalcanzable aun otorgando todas las llaves. Los ciclos MUST respetar la definición de indispensabilidad, excluir dependencias con una ruta alternativa, incluir sus llaves y puertas en orden, comenzar por la llave de menor id y ordenarse por esa llave. Las llaves inobtenibles MUST ordenarse por id. (G14, G18, G19)
- **RS-FR-012**: El reporte MUST enumerar la frontera bloqueada ordenada por sala de origen y dirección, con origen, dirección, destino y llave requerida. MUST indicar la ubicación de la llave requerida o «inexistente» si no figura en la lista de llaves; la ausencia de esa llave no constituye por sí misma un error. (G14, G25)
- **RS-FR-013**: `--verificar <cripta>` MUST verificar e imprimir el reporte en consola sin crear la vista. MUST terminar con código 0 si es resoluble, 1 si no es resoluble y 2 ante un error de datos o red. (G22, G23)
- **RS-FR-014**: Al iniciar una partida, el sistema MUST verificar siempre la cripta y mostrar el reporte tanto si es resoluble como si no. Si no es resoluble, sin `--forzar` la partida MUST NOT comenzar; con `--forzar`, MUST mostrarse el reporte y comenzar la partida. (G17, G24)
- **RS-FR-015**: Si una llave está asociada a un enemigo errante, su ubicación para la verificación MUST ser la sala donde ese enemigo inicia. (G15)
- **RS-FR-016**: El reporte completo MUST ser determinista: para la misma cripta y los mismos datos de entrada válidos, el veredicto, las causas, el orden por rondas, la puerta final, la frontera y los ciclos MUST ser idénticos. Los datos específicos de una cripta MUST provenir de las entradas y MUST NOT incorporarse como datos particulares en el comportamiento de la verificación. (G16, G23)
- **RS-FR-017**: Si falla la consulta de llaves o no queda presupuesto de solicitudes, el reporte MUST indicar NO VERIFICABLE y `--verificar` MUST terminar con código 2. Al iniciar, sin `--forzar` la partida MUST NOT comenzar; con `--forzar` MUST mostrarse el reporte y comenzar la partida. (G31)
- **RS-FR-018**: Si una ubicación de llave refiere a una sala o un enemigo inexistente, MUST informarse un error de datos; `--verificar` MUST terminar con código 2 y una partida MUST NOT comenzar, incluso con `--forzar`. (G23)

### Performance Requirements

- **RS-PR-001**: La verificación completa MUST tomar como máximo 200 ms en la cripta publicada más grande, medida localmente y excluyendo red y renderizado. (G32)
- **RS-PR-002**: El trabajo MUST crecer aproximadamente en proporción a la cantidad de salas, salidas y llaves; obtener una llave nueva MUST NOT requerir volver a recorrer la región ya explorada. (G20, G33)
- **RS-PR-003**: `--bench` MUST comparar la verificación incremental con repetir la evaluación completa por cada llave, usando criptas sintéticas con muchas llaves encadenadas y datos deterministas según la semilla. (G27)

### Key Entities

- **Cripta**: conjunto de salas, sala inicial, sala de salida, llave de salida y salidas dirigidas; cada salida tiene dirección, destino, estado abierto/cerrado, llave requerida si aplica y costo.
- **Ubicación de llave**: id de llave y sala; opcionalmente, enemigo que la suelta. Si hay enemigo errante, su sala de obtención es la sala donde inicia.
- **Reporte de verificación**: veredicto, orden por rondas y puerta final si es resoluble; o motivo, resumen de región alcanzable, llaves inobtenibles, frontera bloqueada y ciclos si no es resoluble.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: En la cripta publicada más grande, la verificación completa tarda como máximo 200 ms en medición local excluyendo red y renderizado (RS-PR-001).
- **SC-002**: `--bench` presenta la comparación solicitada para criptas sintéticas con muchas llaves encadenadas y reproduce los mismos datos para una misma semilla (RS-PR-003).
- **SC-003**: Dos verificaciones de una misma cripta y datos de entrada producen reportes idénticos, incluido el orden por rondas (RS-FR-009, RS-FR-016).
- **SC-004**: En todos los casos de aceptación, el reporte permite distinguir las criptas resolubles de las no resolubles, explica el motivo requerido y aplica la política correcta de inicio o de código de salida (RS-FR-007–RS-FR-014).
- **SC-005**: Una llave nueva no requiere repetir el recorrido de la región previamente alcanzada, y el trabajo medido aumenta aproximadamente en proporción a salas, salidas y llaves (RS-PR-002).

## Assumptions

- El esqueleto identifica una sala inicial, una sala de salida y una llave de salida.
- Las salidas son dirigidas; sus direcciones y destinos provienen del esqueleto de la cripta.
- La llave se obtiene al alcanzar la sala indicada; si se vincula con un enemigo errante, se usa la sala inicial del enemigo.
- Para la verificación, las llaves no se consumen y todo enemigo puede ser derrotado; las trampas y cierres automáticos no bloquean.
- No se calculan rutas de menor costo. Caché, niebla de guerra, línea de tiempo y cazadores quedan fuera de alcance.
- El costo de salida se conserva como dato de entrada, pero no cambia la alcanzabilidad, el veredicto ni el orden.
- Una consulta de llaves fallida o sin presupuesto produce NO VERIFICABLE; el forzado permite iniciar pese a ese resultado.
- Una ubicación de llave que refiere a una sala o un enemigo inexistente constituye un error de datos que no puede forzarse.
