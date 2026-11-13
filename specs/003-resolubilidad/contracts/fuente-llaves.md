# Contrato de fuente de llaves

## Operación lógica

Agregar a `FuenteDeDatos`:

```text
llaves_cripta(cripta_id) -> { "llaves": [...] }
```

Adaptadores existentes:

| Adaptador | Operación |
|---|---|
| `DatosHTTP` | `GET /criptas/<cripta_id>/llaves`, ejecutado mediante `_get()`. |
| `DatosOffline` | Leer `datos_offline/<cripta_id>/llaves.json`. |
| `DatosSimulado` | Delegar a la fuente envuelta mediante su mecanismo de demora determinista. |

`herramientas/descargar_offline.py` debe guardar los datos de la misma consulta lógica.
Ese archivo no existe aún en `datos_offline/`.

## Forma lógica propuesta

```json
{
  "llaves": [
    {
      "id": "id-llave",
      "sala": 12,
      "enemigo": "id-enemigo"
    }
  ]
}
```

`enemigo` es opcional; si aparece, `sala` representa la sala donde inicia ese enemigo.
Los IDs de llaves y enemigos son texto; el ID de sala es entero. La lista puede contener
varias ubicaciones del mismo ID de llave. El esquema/envoltorio HTTP y el significado de
una lista vacía deben confirmarse contra el servicio; una respuesta vacía, si es válida,
no debe confundirse con una falla de consulta.

La respuesta real del servicio aún debe confirmarse. La verificación valida que `sala`
exista, pero no valida la existencia del id de `enemigo`, porque el esqueleto no incluye
un roster completo y el contenido de salas se carga bajo demanda.

## Presupuesto y fallos

- Cada intento HTTP de la consulta se cuenta dentro de `presupuesto_solicitudes` porque
  usa `DatosHTTP._get()`. Cada reintento cuenta como otro intento, igual que los demás
  GET.
- Transporte, timeout, indisponibilidad del servicio, cancelación, reintentos agotados o
  presupuesto insuficiente producen NO VERIFICABLE; no se sustituye por una lista vacía.
- Para `--verificar`, NO VERIFICABLE devuelve código 2.
- Al inicio, NO VERIFICABLE bloquea salvo `--forzar`. El forzado no altera los datos de
  entrada ni convierte un error de datos en resultado válido.
- JSON ilegible, estructura/campo/tipo inválido o referencia a sala inexistente se
  considera error de datos (código 2 y no forzable). Un id de enemigo inexistente no es
  validado y no produce error si la sala indicada existe.
- `llave_salida` ausente o nula, así como sala inicial/salida inexistentes, es error de
  datos del esqueleto y no se puede forzar (FR-019).
- Los estados HTTP deben clasificarse según el contrato de error del servicio: una
  respuesta que declare datos/referencias inválidas es error de datos; una falla de
  disponibilidad es NO VERIFICABLE. `DatosHTTP._get()` hoy agrupa estados no exitosos
  como `RuntimeError`, por lo que habrá que conservar el estado/categoría al propagarlo.
- Una puerta cuyo ID de llave requerido no aparece en la lista no es error; se informa
  «inexistente» en la frontera, conforme a FR-013.
- La ausencia del archivo offline de llaves es una consulta offline no disponible y se
  representa como NO VERIFICABLE, no como conjunto vacío.

## Persistencia y versión

La copia de caché debe usar `persistencia/cache_json.py`, bajo la ruta propuesta
`partidas/cache/<cripta_id>/llaves.json`, con:

- versión igual a `CriptaModelo.version`;
- identificador igual al ID de cripta;
- datos serializados como objeto que contiene `llaves`;
- escritura atómica mediante la utilidad común.

Una copia con versión distinta, formato inválido o identificador diferente no es válida
y no puede participar en el veredicto; se descarta y se consulta la fuente. La consulta
de llaves se persiste por separado del esqueleto para no cambiar el formato de
`esqueleto.json`.

El archivo de datos offline puede incluir la versión de origen junto a la respuesta, o
validarse contra la versión de `general.json`; el formato final debe decidirse con el
descargador y `DatosOffline` antes del código. En ambos casos, la versión debe coincidir
con el esqueleto cargado.
