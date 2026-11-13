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
python main.py --gui --forzar
```

El inicio muestra un resumen antes de jugar. RESOLUBLE muestra solo el veredicto;
NO RESOLUBLE muestra veredicto y motivo. NO VERIFICABLE muestra el veredicto y el motivo
de fallo de consulta sin ubicaciones. Sin `--forzar`, NO RESOLUBLE o NO VERIFICABLE
bloquea; con `--forzar`, permite continuar. Los errores de datos siempre bloquean.

### Compatibilidad de modos

- `--verificar` combinado con `--replay` o `--bench` se rechaza como error de uso antes
  de consultar datos o comenzar la verificación.
- `--forzar` se ignora en modo `--verificar`; el resultado/código es el mismo que sin
  esa opción.
- `--replay` conserva su comportamiento y no verifica (FR-023).
- `--forzar` se propaga al inicio con `--gui` y permite iniciar NO RESOLUBLE o
  NO VERIFICABLE, pero no un error de datos.
- El caso de resolubilidad de `--bench` se ejecuta con y sin `--salida`.

## Códigos de salida de `--verificar`

| Código | Significado |
|---:|---|
| 0 | Reporte RESOLUBLE. |
| 1 | Reporte NO RESOLUBLE. |
| 2 | NO VERIFICABLE por fallo de consulta/presupuesto, o error de datos/red según la spec. |

Un resultado de error no debe ser convertido a código 0/1 ni a reporte de éxito. En un
inicio normal, los errores de datos no son forzables; los fallos de consulta se expresan
como NO VERIFICABLE.

## Formato estable

Las siguientes plantillas son normativas para el reporte completo y el resumen inicial
(FR-024). La codificación es UTF-8. Las listas conservan el orden especificado en
`spec.md`; direcciones se ordenan lexicográficamente por código de carácter.

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
  - id=<id> | ubicaciones=[sala:<id>[, enemigo:<id>]; ...] | causa=<causa>
FRONTERA_BLOQUEADA:
  - origen=<id-sala> | direccion=<direccion> | destino=<id-sala> | llave=<id|inexistente>
CICLOS:
  - llaves=<id> -> <id> -> ... -> <id> | puertas=[origen=<id>, direccion=<dir>; ...]
```

Para motivo (b), `MOTIVO` identifica que se obtuvo `llave_salida` pero no se alcanza
ninguna puerta hacia `sala_salida` que la requiera. Las ubicaciones de cada llave se
ordenan por sala numérica, ubicación sin enemigo primero y luego id de enemigo
lexicográfico. La causa es `en ciclo`, `depende de <ids ordenados>` o `sala inalcanzable
aun con todas las llaves`, según FR-011. Puertas de ciclo: por sala de origen y dirección.

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

La salida debe conservar exactamente las etiquetas y orden de secciones/campos de estas
plantillas. Para una puerta cerrada cuyo id de llave sea nulo, ausente o no aparezca en
la consulta, `llave=inexistente`.

## Errores

- Error de datos: mensaje explícito, código 2 en `--verificar`, inicio bloqueado incluso
  con `--forzar`.
- Fallo de consulta o presupuesto: NO VERIFICABLE y código 2 en `--verificar`; inicio
  bloqueado salvo `--forzar`.
- No se crea una vista para procesar `--verificar`; se usa el formateador de presentación
  y salida de consola.
