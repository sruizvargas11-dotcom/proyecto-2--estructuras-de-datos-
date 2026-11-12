# Fase B: revisión y preparación de José

Fecha: 2026-11-05. Responsable de esta preparación: José. Rama: `spec/jose`.
Base revisada: `feature/spec-kit-copilot`, commit `3dee3f019bebe216c6d727b673d10197fd9d1fdc`.
Estado: tareas documentales de José preparadas localmente. El equipo acordó usar Spec Kit `1.2.6.dev0`. La publicación queda pendiente de confirmación de José.

## Alcance y resultado

El plan del equipo asigna a José revisar el diff de configuración y preparar un borrador en texto plano de niebla de guerra e ir a. Daniel ya creó la constitución compartida y la capacidad 001. No se reinicializó Spec Kit ni se ejecutó de nuevo constitution. No se generaron spec, plan, tasks ni código de la capacidad de José.

- El equipo acordó usar Spec Kit `1.2.6.dev0`, la versión declarada por la configuración heredada de Daniel. El CLI instalado de José sigue en `1.2.3`. Antigravity reconoce los skills del proyecto derivados de los archivos de Daniel.
- La rama de Daniel trae skills para Copilot y comandos para Gemini. Se añadieron diez skills idénticos a los de Copilot en `.agents/skills/`, la ubicación de Antigravity, sin modificar las fuentes de Daniel.
- `.specify/integration.json` conserva Copilot instalado y añade `agy` como integración predeterminada; `init-options.json` queda coherente. Se añadió el manifiesto de archivos de Antigravity con sus SHA-256.
- La adaptación fue manual: no se ejecutó `specify integration install`, pues Windows bloquea `specify.exe`. No se modificó la protección de Windows ni se certifica que el CLI haya sido actualizado.
- Antigravity mostró los diez skills en la configuración del proyecto; el proyecto quedó seleccionado con Claude Opus 5.5 Low. Esto comprueba descubrimiento, no ejecución completa del flujo.
- El borrador está en [BORRADOR_NIEBLA_VIAJE_JOSE.md](BORRADOR_NIEBLA_VIAJE_JOSE.md). Es entrada de la fase C, no una spec aprobada ni un prompt enviado al agente.

## Revisión de la constitución de Daniel

Se contrastó `.specify/memory/constitution.md` (1.0.0) con P2 §2.3:

| Principio exigido | Resultado de revisión documental |
| --- | --- |
| Estructuras propias; restricciones de índices, cachés y bibliotecas | Cubierto por I |
| Determinismo de cripta, semilla y acciones | Cubierto por II |
| MVC; replay y bench sin vista | Cubierto por III |
| Sin datos de criptas concretas dentro del código | Cubierto por IV |
| Presupuesto de solicitudes | Cubierto por V |
| Rendimiento demostrado con bench | Cubierto por VI |
| Especificación confirmada antes de implementación | Cubierto por VII |

También exige requisitos estables, trazabilidad y revisión de artefactos. No se cambió la constitución. La revisión documental favorable no representa la aprobación personal de los cuatro integrantes.

## Pendientes que requieren coordinación del equipo

1. Todos deben leer y aprobar la constitución. No se registra aprobación en nombre de Daniel, Centeno, Sebastián o José.
2. La constitución y T026 de Daniel apuntan a `docs/DECISIONES.md`; la fase A de José propone el documento principal en la raíz. Al integrar las ramas se debe conservar el documento principal y el enlace de compatibilidad, y acordar la referencia canónica antes de nuevos cambios. No se trasladaron documentos en esta rama.
3. Pedir a Daniel el commit, la referencia de origen o el comando que usó para instalar `1.2.6.dev0`, y documentarlo para que el equipo pueda reproducir la instalación del CLI.
4. La barrera de la fase B exige configuración y constitución integradas en main. Esta preparación en rama no satisface esa barrera ni autoriza PR o merge. Tampoco certifica el cierre de B01-B05 de otros integrantes en fase A.
5. Antes de implementar, revisar el análisis de consistencia de la capacidad 001; la existencia de tasks.md no prueba que analyze haya sido ejecutado sin bloqueos.

## Siguiente fase, después de autorización y barreras del equipo

José trabajará sobre `specs/002-niebla-viaje/`; Daniel será su revisor. En el chat de Antigravity se usará speckit-specify con el borrador, después speckit-clarify. Confirmar explícitamente la carpeta objetivo y comprobar que no se edita la 001. La especificación debe confirmarse antes de plan o código, conforme a la constitución. Plan, tasks y analyze corresponden a la fase D del plan del equipo.

No se ha creado un puntero local hacia la 001 ni hacia una 002 inexistente. El nombre de rama no sustituye la selección de capacidad que usa Spec Kit. José añadirá personalmente los prompts reales al finalizar su fase; no se añadieron entradas a PROMPTS_LLM.md.

## Verificación de esta preparación

Diez archivos SKILL.md comparados por SHA-256 con sus fuentes de Daniel; manifiesto y JSON de configuración comprobados; diff sin errores de whitespace; enlaces relativos nuevos comprobados. Solo documentación/configuración: no se ejecutó la suite del juego ni se afirman resultados de nuevas funcionalidades.
