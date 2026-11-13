# Feature Specification: Verificación de resolubilidad de la cripta

**Feature Branch**: `003-resolubilidad`

**Created**: 2026-11-12

**Status**: Draft

**Input**: User description: "Determinar antes de iniciar una partida si la cripta puede ganarse, explicar los bloqueos y presentar un reporte determinista."

## Clarifications

### Session 2026-11-12

- Q: ¿Qué ocurre si falla la consulta de llaves o se agota el presupuesto de solicitudes? → A: Se informa NO VERIFICABLE; `--verificar` termina con código 2 y, al iniciar, `--forzar` permite comenzar mostrando el veredicto y el motivo.
- Q: ¿Cómo se trata una ubicación de llave que refiere a una sala o enemigo inexistente? → A: Es error de datos, `--verificar` termina con código 2 y no se permite forzar el inicio.
- Decisión fija: si la sala inicial o la sala de salida no existe en el esqueleto, se informa error de datos, código 2, y no se permite forzar el inicio.
- Decisión fija: la llave de salida ubicada en la sala inicial es válida y pertenece a la ronda 0. Si la sala inicial y la sala de salida coinciden, igualmente se exige entrar cruzando una puerta que requiera la llave de salida.
- Decisión fija: si varias puertas válidas llevan a la sala de salida, se informa la primera cruzable al aplicar el orden por id numérico de sala de origen y luego por dirección; el corte del orden es la ronda en que esa puerta seleccionada se vuelve cruzable.
- Decisión fija: si el mismo id de llave aparece en varias ubicaciones, basta con que una sea alcanzable para obtenerla; el orden informa la ubicación de menor id de sala y la lista de llaves inobtenibles incluye todas sus ubicaciones.
- Decisión fija: la causa «depende de» enumera todas las llaves indispensables para la llave afectada, ordenadas por id de llave.
- Decisión fija: los ids de sala se comparan numéricamente; los ids de llave y enemigo, lexicográficamente por código de carácter.
- Decisión fija: se incluye la ronda completa en que la puerta final se vuelve cruzable y el orden termina en esa ronda.
- Decisión fija: el rendimiento se mide sobre al menos cinco repeticiones; se informa p95 y máximo. Se excluyen red, carga de datos y renderizado. Hasta que exista la cripta publicada más grande, se mide la mayor disponible y criptas sintéticas.
- Decisión editorial incorporada: la ubicación de una llave soltada por un enemigo es la sala donde ese enemigo inicia, sea errante o no.
- Q: ¿Qué cantidad de ciclos de dependencia debe incluir el reporte cuando existen muchos ciclos posibles? → A: Como máximo un ciclo determinista por cada llave participante en ciclos; se elige el de secuencia de ids lexicográficamente menor, comenzando por el id menor, y se informan sus puertas en el orden de la secuencia.
- Q: ¿Qué información del reporte debe ver el jugador antes de iniciar una partida si contiene ubicaciones que la niebla de guerra aún oculta? → A: Al inicio se muestra solo el veredicto y el motivo; el reporte completo se obtiene únicamente con `--verificar`.
- Q: ¿Qué límite medible debe definir el crecimiento aproximadamente lineal del tiempo al aumentar el tamaño de la cripta? → A: En criptas sintéticas deterministas, duplicar salas, salidas y llaves entre tamaños consecutivos aumenta el p95 como máximo 2.5 veces; comprobar al menos tres tamaños y cinco repeticiones por tamaño.
- Q: ¿Debe el modo `--replay` ejecutar la verificación de resolubilidad, además del inicio normal, `--verificar` y `--bench`? → A: No; se verifica al iniciar partidas nuevas y con `--verificar`, `--bench` mide el verificador sin vista y `--replay` permanece sin cambios.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Conocer si la cripta puede ganarse (Priority: P1)

Al iniciar una partida, el jugador recibe el veredicto y, si la cripta no es resoluble, su motivo. El reporte completo se obtiene por separado; la partida no resoluble solo comienza si el jugador solicita forzarla.

**Why this priority**: Evita iniciar inadvertidamente una partida imposible y permite entender la causa.

**Independent Test**: Iniciar criptas resolubles y no resolubles y comprobar el reporte y si se permite comenzar.

**Acceptance Scenarios**:

1. **Dado** que la llave de salida está detrás de la única puerta que ella misma abre, **Cuando** se verifica, **Entonces** se informa NO RESOLUBLE por llave de salida inobtenible, la frontera muestra esa puerta y el reporte incluye el ciclo de una llave consigo misma (G14; FR-008, FR-011, FR-012, FR-013).
2. **Dado** que una llave la suelta un enemigo, **Cuando** se verifica, **Entonces** la ubicación de la llave es la sala donde ese enemigo inicia (G15; FR-001, FR-016).
3. **Dado** que existen varios órdenes válidos, **Cuando** se ejecuta la verificación dos veces, **Entonces** ambas ejecuciones producen exactamente el mismo orden por rondas (G16; FR-010, FR-017).
4. **Dado** que la cripta no es resoluble y se intenta iniciar sin `--forzar`, **Cuando** se solicita el inicio, **Entonces** no comienza la partida y se muestran el veredicto y el motivo (G17; FR-015).

**Acceptance Scenarios adicionales**:

1. **Dado** una cripta no resoluble, **Cuando** se intenta iniciar con `--forzar`, **Entonces** se muestran el veredicto y el motivo y comienza la partida (RS-E01; FR-015, FR-018).
2. **Dado** que dos llaves parecen requerirse mutuamente, pero existe una ruta alternativa hacia una de ellas, **Cuando** se verifica, **Entonces** no se reporta un ciclo entre esas llaves (RS-E02; FR-012).
3. **Dado** una cadena A → B → C en que C es inobtenible, **Cuando** se informa la causa de cada llave, **Entonces** A y B enumeran todas las llaves indispensables de las que dependen (RS-E03; FR-011, FR-022).
4. **Dado** que una llave abre una región con varias llaves, **Cuando** se genera el orden por rondas, **Entonces** las nuevas llaves aparecen en la ronda siguiente y obtener otra llave no exige repetir el trabajo sobre la región ya alcanzada (RS-E04; FR-009, FR-010).
5. **Dado** que la sala de salida solo es alcanzable por una puerta abierta y ninguna puerta que requiera la llave de salida, **Cuando** se verifica, **Entonces** se informa NO RESOLUBLE por motivo (b) (RS-E05; FR-008, FR-011).
6. **Dado** una puerta de frontera que requiere una llave ausente de la lista de ubicaciones, **Cuando** se genera el reporte, **Entonces** la ubicación de esa llave se indica como «inexistente», sin que eso sea un error de datos (RS-E06; FR-013).
7. **Dado** una cripta, **Cuando** cambian únicamente los costos de sus salidas, **Entonces** no cambian el veredicto ni el orden de llaves (RS-E07; FR-007).
8. **Dado** que una salida está descrita desde A hacia B y no hay salida desde B hacia A, **Cuando** se determina la región alcanzable desde A, **Entonces** esa salida no permite considerar A alcanzable desde B (RS-E08; FR-002).
9. **Dado** una llave ya obtenida que abre varias puertas cerradas, **Cuando** se cruzan esas puertas, **Entonces** se puede cruzar cada una sin consumir la llave (RS-E09; FR-003).
10. **Dado** una cripta en la que falla la consulta de llaves o no queda presupuesto de solicitudes, **Cuando** se intenta verificar o iniciar, **Entonces** se informa NO VERIFICABLE, `--verificar` termina con código 2 y el inicio solo se permite con `--forzar` mostrando NO VERIFICABLE (RS-E10; FR-018).
11. **Dado** una cripta cuya lista de llaves persistida corresponde a otra versión, **Cuando** se verifica la cripta actual, **Entonces** esa lista no se considera válida (RS-E11; FR-001).
12. **Dado** criptas sintéticas con muchas llaves encadenadas y una semilla determinada, **Cuando** se ejecuta `--bench`, **Entonces** se comparan la verificación incremental y la evaluación completa repetida por cada llave y se reproducen los mismos datos para la misma semilla (RS-E12; SC-002).
13. **Dado** una salida afectada por trampa o cierre automático, **Cuando** se verifica si puede cruzarse conforme a los supuestos, **Entonces** esos efectos no impiden el cruce (RS-E13; FR-005).
14. **Dado** un enemigo no errante en una sala alcanzable que suelta una llave, **Cuando** se verifica, **Entonces** se considera derrotado y la llave se ubica en la sala donde ese enemigo inicia (RS-E14; FR-004, FR-016).
15. **Dado** una cripta cuyo esqueleto no contiene la sala inicial o la sala de salida, **Cuando** se verifica o se intenta iniciar, **Entonces** se informa error de datos con código 2 y no se permite forzar (RS-E15; FR-019).
16. **Dado** que la llave de salida está en la sala inicial, **Cuando** se forma el orden, **Entonces** aparece en la ronda 0; si la sala inicial es también la sala de salida, aún se requiere cruzar una puerta que pida esa llave (RS-E16; FR-020).
17. **Dado** que hay varias puertas válidas hacia la sala de salida, **Cuando** se selecciona la puerta final entre las cruzables, **Entonces** se informa la primera según sala de origen ascendente y dirección (RS-E17; FR-008, FR-009).
18. **Dado** que un mismo id de llave aparece en varias ubicaciones, **Cuando** al menos una ubicación es alcanzable, **Entonces** la llave se considera obtenida y se reporta la ubicación alcanzable de menor id de sala; si ninguna es alcanzable, se incluyen todas las ubicaciones (RS-E18; FR-016).
19. **Dado** ids de sala, llave y enemigo con representaciones que no tienen el mismo orden textual y numérico, **Cuando** se ordena el reporte, **Entonces** los ids de sala se comparan numéricamente y los de llave y enemigo lexicográficamente por código de carácter (RS-E19; FR-021).
20. **Dado** que la puerta final se vuelve cruzable en una ronda con varias llaves nuevas, **Cuando** se genera el orden, **Entonces** se incluye la ronda completa y el orden termina allí (RS-E20; FR-009).
21. **Dado** que una llave depende de más de una llave indispensable, **Cuando** se informa su causa, **Entonces** se enumeran todas esas llaves por id (RS-E21; FR-022).
22. **Dado** criptas sintéticas de una misma familia determinista, **Cuando** salas, salidas y llaves se duplican entre tamaños consecutivos, **Entonces** el p95 aumenta como máximo 2.5 veces durante al menos tres tamaños y cinco repeticiones por tamaño (RS-E22; SC-004).
23. **Dado** la cripta más grande disponible y criptas sintéticas, **Cuando** se mide localmente la verificación durante al menos cinco repeticiones, **Entonces** el p95 es menor que 200 ms, se documenta el máximo y se excluyen red, carga de datos y renderizado (RS-E27; SC-001).

### User Story 2 - Verificar sin iniciar una partida (Priority: P2)

Un evaluador o desarrollador puede solicitar la verificación de una cripta desde la consola, recibir el reporte y utilizar el resultado del proceso sin abrir la vista del juego.

**Why this priority**: Hace posible evaluar criptas de forma automatizada y separada de una partida.

**Independent Test**: Ejecutar `--verificar` para criptas resolubles, no resolubles y con errores, observando reporte, código de salida y ausencia de vista.

**Acceptance Scenarios**:

1. **Dado** una cripta resoluble o no resoluble, **Cuando** se ejecuta `--verificar <cripta>`, **Entonces** se imprime el reporte, no se crea la vista y el código de salida es 0 o 1, respectivamente (RS-E23; FR-014).
2. **Dado** una ubicación de llave que refiere a una sala o enemigo inexistente, **Cuando** se ejecuta `--verificar <cripta>`, **Entonces** se informa error de datos y el código de salida es 2 (RS-E24; FR-019).
3. **Dado** que el reporte completo contiene ubicaciones de salas que el jugador aún no conoce, **Cuando** se inicia una partida, **Entonces** solo se muestran el veredicto y el motivo; `--verificar` sigue mostrando el reporte completo (RS-E25; FR-014, FR-015).
4. **Dado** que se usa `--replay`, **Cuando** se reproduce una partida, **Entonces** no se ejecuta la verificación de resolubilidad; `--bench` compara el rendimiento del verificador sin crear la vista (RS-E26; FR-023).

### User Story 3 - Forzar el inicio de una cripta no resoluble (Priority: P3)

Un jugador que conoce el riesgo puede decidir comenzar aun cuando el reporte indique que la cripta no es resoluble.

**Why this priority**: Conserva una opción explícita para continuar sin ocultar el resultado de la verificación.

**Independent Test**: Intentar iniciar la misma cripta no resoluble con y sin `--forzar` y comparar el reporte y el inicio de la partida.

**Acceptance Scenarios**:

1. **Dado** una cripta no resoluble, **Cuando** el jugador inicia con `--forzar`, **Entonces** se muestran el veredicto y el motivo antes de que comience la partida (RS-E01; FR-015).

### Edge Cases

- La llave de salida es inobtenible o se obtiene, pero no se alcanza ninguna puerta hacia la sala de salida que la requiera.
- Una llave no se obtiene porque todas sus ubicaciones siguen siendo inalcanzables aun otorgando todas las llaves.
- Las llaves dependen de otras llaves inobtenibles, incluidas dependencias que forman un ciclo o que aparentan formarlo pero tienen ruta alternativa.
- Varias llaves pueden obtenerse en una misma ronda; deben ordenarse por sala numérica ascendente y luego por id de llave lexicográfico.
- La llave de salida puede obtenerse antes de que sea alcanzable el origen de la puerta final.
- La consulta de llaves puede fallar o no contar con presupuesto de solicitudes suficiente; se informa NO VERIFICABLE y puede forzarse el inicio.
- Una ubicación de llave puede referir a una sala o enemigo inexistente; es un error de datos que no puede forzarse.
- La sala inicial o la sala de salida puede faltar en el esqueleto; es un error de datos que no puede forzarse.
- La sala inicial puede coincidir con la sala de salida; aun así debe cruzarse una puerta que requiera la llave de salida.
- Una llave puede aparecer en varias ubicaciones o estar en la sala inicial.

## Requirements *(mandatory)*

### Definiciones

- **Región alcanzable**: salas a las que se llega desde la sala inicial con las llaves obtenidas.
- **Resoluble**: partiendo de la sala inicial, se obtiene la llave de salida **y** se entra a la sala de salida cruzando una puerta que requiere la llave de salida. Llegar a la sala de salida por una puerta abierta o por una puerta que requiere otra llave no cuenta.
- **Frontera bloqueada**: puertas cerradas cuyo origen está dentro de la región alcanzable y cuyo destino está fuera de ella.
- **Llave indispensable**: la llave `kj` es indispensable para `ki` si la sala de `ki` sigue siendo inalcanzable aun otorgando todas las llaves excepto `kj`.
- **Ciclo**: secuencia `k1 → k2 → … → k1` donde cada llave es indispensable para la anterior; incluye `k → k`. Si existe una ruta alternativa, no hay ciclo y no debe reportarse.

### Functional Requirements

- **FR-001**: La verificación DEBE usar el esqueleto de la cripta y las ubicaciones de llaves provistas por la consulta «llaves» del servicio. La consulta DEBE contar en `presupuesto_solicitudes`. Las ubicaciones persistidas DEBEN considerarse inválidas cuando cambie la versión de la cripta. (G15, RS-E10, RS-E11)
- **FR-002**: Cada salida DEBE considerarse únicamente en el sentido descrito desde su sala de origen; una salida de A a B no implica una salida de B a A. (RS-E08)
- **FR-003**: Para esta verificación, se DEBE poder cruzar toda salida abierta y toda salida cerrada cuya llave requerida ya se haya obtenido; las llaves no se consumen. Estos supuestos no cambian las reglas de la partida. (RS-E09)
- **FR-004**: Para esta verificación se DEBE suponer que todo enemigo puede ser derrotado; este supuesto no cambia las reglas de la partida. (RS-E14)
- **FR-005**: Para esta verificación, trampas y cierres automáticos no bloquean el cruce; este supuesto no cambia las reglas de la partida. (RS-E13)
- **FR-006**: El costo de las salidas no afecta el veredicto ni el orden de llaves; solo importa la alcanzabilidad. (RS-E07)
- **FR-007**: La cripta se declara resoluble únicamente si se obtiene la llave de salida y se cruza hacia la sala de salida una puerta que requiere esa llave. (G14, RS-E05, RS-E16)
- **FR-008**: Si la cripta es resoluble, el reporte indica RESOLUBLE y la puerta final mediante sala de origen y dirección. Si hay varias puertas válidas cruzables, se informa la primera aplicando el orden por sala de origen numérica ascendente y luego dirección. El orden de llaves termina en la ronda en que la puerta seleccionada se vuelve cruzable. (RS-E17)
- **FR-009**: Si la cripta es resoluble, el reporte incluye el id de cada llave, la sala donde se obtiene y el enemigo que la suelta si aplica. La ronda 0 contiene las llaves alcanzables sin cruzar puertas cerradas; cada ronda posterior contiene llaves nuevas alcanzables usando llaves de rondas anteriores. Las llaves dentro de una ronda se ordenan por id de sala numérico ascendente y luego por id de llave lexicográfico. La ronda en que la puerta final se vuelve cruzable se incluye completa y el orden termina en ella. Obtener otra llave no exige repetir el trabajo sobre la región ya alcanzada. (G16, RS-E04, RS-E16, RS-E18, RS-E19, RS-E20)
- **FR-010**: El reporte resoluble permite comprobar validez, completitud y determinismo: cada llave es alcanzable usando solo llaves anteriores en el orden, la llave de salida está incluida y permite cruzar la puerta final, y la misma cripta produce el mismo orden. (G16)
- **FR-011**: Si la cripta no es resoluble, el reporte indica NO RESOLUBLE y uno de estos motivos: (a) la llave de salida es inobtenible; (b) se obtiene la llave de salida pero no se alcanza ninguna puerta hacia la sala de salida que la requiera, incluida la ausencia de tal puerta. También resume la cantidad de salas alcanzables y llaves obtenidas. Las llaves inobtenibles se ordenan por id e incluyen sus ubicaciones y una causa: en un ciclo, depende de una o más llaves inobtenibles, o su sala sigue inalcanzable aun otorgando todas las llaves. (G14, RS-E03, RS-E05)
- **FR-012**: El reporte excluye dependencias con ruta alternativa y, para cada llave que participe en ciclos, incluye como máximo un ciclo determinista que la contenga. Se elige el ciclo con la secuencia de ids de llave lexicográficamente menor, comenzando por el id menor; sus puertas se informan siguiendo el orden de la secuencia de llaves y los ciclos se ordenan por su primer id. (G14, RS-E02)
- **FR-013**: El reporte enumera la frontera bloqueada por sala de origen numérica y dirección, con origen, dirección, destino y llave requerida. Indica la ubicación de la llave requerida o «inexistente» si no aparece en la lista de llaves; esa ausencia no es un error. (G14, RS-E06)
- **FR-014**: `--verificar <cripta>` verifica e imprime el reporte en consola sin crear la vista. Termina con código 0 si es resoluble, 1 si no lo es y 2 ante un error de datos o red. (RS-E23, RS-E24)
- **FR-015**: Al iniciar una partida, se verifica la cripta y se muestra el veredicto; si no es resoluble, se muestra también el motivo. El detalle de ubicaciones no se muestra en el inicio; el reporte completo queda disponible mediante `--verificar`. Si no es resoluble, sin `--forzar` la partida no comienza; con `--forzar`, se muestra el veredicto y motivo y la partida comienza. (G17, RS-E01, RS-E25)
- **FR-016**: Si una llave está asociada a un enemigo, errante o no, su ubicación para la verificación es la sala donde ese enemigo inicia. Si un mismo id de llave aparece en varias ubicaciones, basta con que una sea alcanzable para obtenerla; el orden informa la ubicación alcanzable de menor id de sala. Si ninguna es alcanzable, la lista de inobtenibles incluye todas las ubicaciones. (G15, RS-E14, RS-E18)
- **FR-017**: El reporte completo es determinista para la misma cripta y los mismos datos de entrada válidos. Los datos específicos de una cripta provienen de las entradas y no se incorporan como datos particulares en el comportamiento de la verificación. (G16, RS-E12)
- **FR-018**: Si falla la consulta de llaves o no queda presupuesto de solicitudes, el reporte indica NO VERIFICABLE y `--verificar` termina con código 2. Al iniciar, sin `--forzar` la partida no comienza; con `--forzar` se muestran el veredicto y el motivo y comienza la partida. (RS-E10)
- **FR-019**: Si la ubicación de una llave refiere a una sala o enemigo inexistente, o si el esqueleto no contiene la sala inicial o la sala de salida, se informa un error de datos; `--verificar` termina con código 2 y una partida no comienza, incluso con `--forzar`. (RS-E15, RS-E24)
- **FR-020**: Una llave de salida ubicada en la sala inicial se considera obtenida en la ronda 0. Si sala inicial y sala de salida coinciden, la cripta solo es resoluble al entrar cruzando una puerta que requiera la llave de salida. (RS-E16)
- **FR-021**: Los ids de sala se comparan numéricamente; los ids de llave y enemigo se comparan lexicográficamente por código de carácter. (RS-E19)
- **FR-022**: La causa «depende de» enumera todas las llaves indispensables para la llave afectada, ordenadas por id de llave. (RS-E03, RS-E21)
- **FR-023**: La verificación se ejecuta al iniciar partidas nuevas y con `--verificar`. `--bench` compara el rendimiento del verificador sin crear la vista; `--replay` no ejecuta la verificación y conserva su comportamiento. (RS-E12, RS-E26)

### Key Entities

- **Cripta**: conjunto de salas, sala inicial, sala de salida, llave de salida y salidas dirigidas; cada salida tiene dirección, destino, estado abierto/cerrado, llave requerida si aplica y costo.
- **Ubicación de llave**: id de llave y sala; opcionalmente, enemigo que la suelta. Cualquier enemigo asociado ubica la llave en la sala donde inicia. Una llave puede tener varias ubicaciones.
- **Reporte de verificación**: veredicto, orden por rondas y puerta final si es resoluble; o motivo, resumen de región alcanzable, llaves inobtenibles, frontera bloqueada y ciclos si no es resoluble.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El tiempo de verificación, medido durante al menos cinco repeticiones y excluyendo red, carga de datos y renderizado, tiene p95 menor que 200 ms; el máximo también se documenta. Mientras no exista la cripta publicada más grande, la medición usa la mayor disponible y criptas sintéticas. (RS-E27)
- **SC-002**: `--bench` compara la verificación incremental con repetir la evaluación completa por cada llave, usando criptas sintéticas con muchas llaves encadenadas y datos deterministas según la semilla. (RS-E12)
- **SC-003**: Dos verificaciones de la misma cripta y datos de entrada producen reportes idénticos, incluido el orden por rondas. (G16, RS-E12)
- **SC-004**: En criptas sintéticas de una misma familia determinista, cada duplicación de salas, salidas y llaves entre al menos tres tamaños consecutivos aumenta como máximo 2.5 veces el p95 del tiempo local de verificación, medido en al menos cinco repeticiones por tamaño y excluyendo red, carga de datos y renderizado (RS-E22).
- **SC-005**: En todos los escenarios de aceptación, el reporte permite distinguir cripta resoluble, no resoluble, no verificable y error de datos, y aplicar el resultado correspondiente a inicio o código de salida. (FR-001–FR-023)

## Assumptions

- El esqueleto de la cripta provee salas, sala inicial, sala de salida, llave de salida y salidas con dirección, destino, estado, llave requerida si aplica y costo.
- Las salidas son dirigidas y la llave se obtiene al alcanzar cualquiera de sus ubicaciones válidas.
- Si una llave se vincula a un enemigo, errante o no, se usa la sala donde ese enemigo inicia.
- Para la verificación, las llaves no se consumen y todo enemigo puede ser derrotado; las trampas y cierres automáticos no bloquean.
- No se calculan rutas de menor costo. Caché, niebla de guerra, línea de tiempo y cazadores quedan fuera del cálculo de resolubilidad.
- El costo de salida se conserva como dato de entrada, pero no cambia la alcanzabilidad, el veredicto ni el orden.
