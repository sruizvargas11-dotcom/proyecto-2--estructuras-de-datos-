<!--
Sync Impact Report
Version change: sin versión establecida → 1.0.0
Modified principles: se definen los siete principios del proyecto en lugar de los marcadores de plantilla.
Added sections: Trazabilidad y aceptación; Flujo de cambios y decisiones.
Removed sections: ninguna.
Follow-up TODOs: ninguno.
-->

# Constitución del Proyecto CRIPTA

## Principios Fundamentales

### I. Estructuras de datos implementadas a mano
Las estructuras de datos evaluadas DEBEN implementarse en el proyecto. Se prohíbe usar `dict`
como índice o caché y se prohíben `set` en esos mismos usos. También se prohíben las
implementaciones equivalentes de bibliotecas, incluidas `heapq`, `bisect`, `collections`
(`deque`, `OrderedDict`, `defaultdict`, `Counter`), `networkx` y cualquier biblioteca de grafos
o búsqueda de rutas. Esto garantiza que el trabajo ejercite las estructuras objeto del curso.

### II. Determinismo de las partidas
Una misma cripta, semilla y secuencia de acciones DEBE producir siempre la misma partida,
incluidos sus resultados observables. Esto permite reproducir errores y validar el juego.

### III. Separación MVC en modos sin interfaz
Los modos `--replay` y `--bench` NO DEBEN instanciar la vista. Estos modos operan sin interfaz
para conservar la separación MVC y permitir su ejecución automatizada.

### IV. Datos de criptas externos al código
El código NO DEBE contener datos específicos de una cripta concreta. Las criptas deben
provenir de los datos de entrada o de configuración del proyecto, no de valores particulares
incorporados a la lógica.

### V. Respeto al presupuesto de solicitudes
Toda ejecución DEBE respetar `presupuesto_solicitudes`; ninguna acción puede exceder el
presupuesto establecido. Esto preserva el límite definido para la interacción con el sistema.

### VI. Afirmaciones de rendimiento verificables
Toda afirmación sobre rendimiento DEBE estar respaldada por resultados de `--bench`. Las
afirmaciones deben corresponder a mediciones reproducibles y no a estimaciones no verificadas.

### VII. Especificación antes que implementación
La especificación DEBE preceder a la implementación, sin excepciones. El historial de Git
DEBE mostrar que la especificación se confirmó antes que el código correspondiente. Si la
especificación es incorrecta, primero se corrige y se confirma en un commit separado antes
de modificar el código.

## Trazabilidad y aceptación

Cada requisito funcional DEBE tener un identificador estable con el formato `FR-NNN`. Cada
caso del Apéndice B DEBE constituir un escenario de aceptación y contar con al menos una prueba
que cite el identificador de requisito que verifica. Cada tarea de `tasks.md` DEBE referenciar
los identificadores de los requisitos que atiende. Esta trazabilidad vincula requisitos,
escenarios, pruebas e implementación.

## Flujo de cambios y decisiones

Todo cambio del proyecto DEBE documentarse en `docs/DECISIONES.md`. Las especificaciones,
planes y tareas DEBEN ajustarse a esta constitución; si la contradicen, se corrigen esos
artefactos y no se elude la constitución. Los cambios de código se revisan contra los
principios, requisitos y escenarios de aceptación aplicables.

## Gobierno

Esta constitución prevalece sobre las demás prácticas y artefactos del proyecto. Para
enmendarla, se documenta la decisión en `docs/DECISIONES.md`, se actualiza esta constitución
y se verifica la coherencia de los artefactos dependientes antes de implementar los cambios
afectados. Cuando una especificación resulte incorrecta, su corrección y confirmación en Git
preceden, en un commit separado, a los cambios de código.

La versión sigue SemVer: MAJOR para cambios incompatibles en principios o gobierno, MINOR
para principios o secciones nuevas o ampliaciones sustanciales, y PATCH para aclaraciones y
correcciones sin cambio semántico. En cada revisión, quienes preparan y revisan cambios DEBEN
comprobar su conformidad con esta constitución y corregir cualquier incumplimiento antes de
integrarlos.

**Versión**: 1.0.0 | **Ratificada**: 2026-11-04 | **Última enmienda**: 2026-11-04
