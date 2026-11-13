# Contrato CLI: Verificación de resolubilidad

## Modos

### Verificación sin partida

```text
python main.py --verificar <cripta>
python main.py --offline --verificar <cripta>
```

Verifica una cripta, imprime el reporte completo y no crea una instancia de vista ni
inicia una partida.

### Inicio normal y forzado

```text
python main.py --cripta <cripta>
python main.py --cripta <cripta> --forzar
python main.py --offline --cripta <cripta> --forzar
```

El inicio muestra un resumen antes de jugar. RESOLUBLE muestra solo el veredicto;
NO RESOLUBLE muestra veredicto y motivo. NO VERIFICABLE muestra el veredicto y el motivo
de fallo de consulta sin ubicaciones. Sin `--forzar`, NO RESOLUBLE o NO VERIFICABLE
bloquea; con `--forzar`, permite continuar. Los errores de datos siempre bloquean.

### Compatibilidad de modos

`--replay` conserva su comportamiento y no verifica (FR-023). `--bench` ejecuta la
medición headless. La combinación de `--verificar` con `--forzar`, `--gui`, `--replay`,
`--bench` o `--salida` no está definida por `spec.md`; ver hallazgos y propuestas en
[plan.md](../plan.md). Este contrato no fija su comportamiento.

## Códigos de salida de `--verificar`

| Código | Significado |
|---:|---|
| 0 | Reporte RESOLUBLE. |
| 1 | Reporte NO RESOLUBLE. |
| 2 | NO VERIFICABLE por fallo de consulta/presupuesto, o error de datos/red según la spec. |

Un resultado de error no debe ser convertido a código 0/1 ni a reporte de éxito. En un
inicio normal, los errores de datos no son forzables; los fallos de consulta se expresan
como NO VERIFICABLE.

## Formato estable propuesto

La spec fija los campos y sus órdenes, pero no la sintaxis textual exacta. La siguiente
plantilla es una propuesta para completar el contrato de presentación; no agrega reglas
de alcanzabilidad y debe confirmarse antes de tratarla como API estable.

Resultado resoluble:

```text
VEREDICTO: RESOLUBLE
ORDEN_POR_RONDAS:
  RONDA <n>:
    - id=<id> | sala=<id-sala> | enemigo=<id-enemigo|ninguno>
PUERTA_FINAL: origen=<id-sala> | direccion=<direccion> | destino=<id-sala-salida>
```

Resultado no resoluble:

```text
VEREDICTO: NO RESOLUBLE
MOTIVO: (a) llave_salida inobtenible
REGION: salas=<cantidad> | llaves_obtenidas=<cantidad>
LLAVES_INOBTENIBLES:
  - id=<id> | ubicacion=sala:<id>[, enemigo:<id>] | causa=<causa>
FRONTERA_BLOQUEADA:
  - origen=<id-sala> | direccion=<direccion> | destino=<id-sala> | llave=<id|inexistente>
CICLOS:
  - llaves=<id> -> <id> -> ... -> <id> | puertas=<puertas_en_el_mismo_orden>
```

Para motivo (b), `MOTIVO` identifica que se obtuvo `llave_salida` pero no se alcanza
ninguna puerta hacia `sala_salida` que la requiera. Ubicaciones múltiples se imprimen
en el orden normativo de la spec; los separadores internos aún requieren fijarse.

NO VERIFICABLE:

```text
VEREDICTO: NO VERIFICABLE
MOTIVO: consulta de llaves no disponible
```

El resumen del inicio omite los bloques de orden, ubicaciones, frontera y ciclos:

```text
VEREDICTO: RESOLUBLE
```

o:

```text
VEREDICTO: NO RESOLUBLE | MOTIVO: (a|b) <motivo>
```

o:

```text
VEREDICTO: NO VERIFICABLE | MOTIVO: consulta de llaves no disponible
```

La dirección se muestra con su identificador de entrada. El orden de esas direcciones,
la sintaxis para varias ubicaciones y la selección de puertas paralelas aún no están
completamente definidos en la spec; se listan como hallazgos en [plan.md](../plan.md).
La salida debe ser determinista, UTF-8 y conservar el orden de secciones/campos de estas
plantillas una vez aprobadas.

## Errores

- Error de datos: mensaje explícito, código 2 en `--verificar`, inicio bloqueado incluso
  con `--forzar`.
- Fallo de consulta o presupuesto: NO VERIFICABLE y código 2 en `--verificar`; inicio
  bloqueado salvo `--forzar`.
- No se crea una vista para procesar `--verificar`; se usa el formateador de presentación
  y salida de consola.
