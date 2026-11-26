# Capítulo 14 · 4C · Udemy 15 — Structured Output and Evaluation (salida estructurada, validación, Batches y revisión)

*Tareas oficiales 4.3, 4.4, 4.5 y 4.6 · Tercer y último capítulo del módulo 4*

---

## Dónde estamos

Seguimos en el **módulo 4: Prompt Engineering & Structured Output**. 4A y 4B ya están escritos. Este capítulo cubre **cuatro tareas**, cada una de 3,33% del examen (en total, un 13%):
- **4.3** Enforce structured output using tool use and JSON schemas (garantizar salida estructurada con tool use y JSON schemas).
- **4.4** Implement validation, retry, and feedback loops for extraction quality (validar, reintentar y aprender de los errores en una extracción).
- **4.5** Design efficient batch processing strategies (procesar grandes volúmenes en lote de forma eficiente).
- **4.6** Design multi-instance and multi-pass review architectures (revisar con varias instancias y en varias pasadas).

### Cómo leer este capítulo

Todo lo que leés acá **vale para el examen**, salvo que diga lo contrario. Cuando algo sale solo del curso (útil para entender, pero no central), lo marco con **📘 Curso**. Cuando Jacob dice algo distinto de lo que evalúa la guía, aparece un recuadro así:

> ⚠️ **En el curso vas a escuchar otra cosa.** … **Para el examen: …**

### Un aviso sobre este capítulo

Es el capítulo más largo del libro porque junta cuatro tareas. El curso explica bien la salida estructurada, la validación y la Batches API, pero **le faltan varios puntos concretos de la guía**: los enums con `"other"` y `"unclear"`, cuándo un reintento no sirve, `detected_pattern`, `calculated_total` vs. `stated_total`, cómo calcular la frecuencia de envío de un batch y la revisión por archivo más integración. Todos están acá. Las lecciones 96–97 (cómo evaluar prompts) la guía no las pregunta directo, así que van resumidas al final.

El escenario de examen que más usa este capítulo es el **6: Structured Data Extraction** (un sistema que extrae datos de documentos, los valida con JSON schemas y los manda a otros sistemas). En TiendaX, es la extracción de **facturas de proveedores** que empezaste a ver en 4B.

## De dónde venimos

En 2A viste que una tool tiene un **input schema** (los parámetros que acepta, en JSON Schema), que `strict: true` garantiza que los argumentos lo cumplan y que `tool_choice` controla si Claude tiene que llamar una tool y cuál. En 4B viste que los ejemplos dan **consistencia** pero no **garantía** de formato, y que la garantía la da un schema. Acá juntamos todo: usar una tool **como formato de salida**, validar lo que el schema no puede validar, procesar miles de documentos en lote y revisar el resultado con otra instancia.

## Mapa del capítulo

**Parte 1 — Salida estructurada (tarea 4.3).**
1. Tool use con JSON schema: la forma garantizada.
2. `tool_choice` en una extracción.
3. Diseñar el schema: required, nullable, enums con "other" y "unclear".
4. Errores de sintaxis vs. errores semánticos.

**Parte 2 — Validación y reintentos (tarea 4.4).**

5. Retry with error feedback (reintentar con el error).
6. Cuándo reintentar no sirve.
7. Que el propio resultado muestre los problemas: `calculated_total`, `conflict_detected` y `detected_pattern`.

**Parte 3 — Procesamiento en lote (tarea 4.5).**

8. La Message Batches API: qué es y cuándo usarla.
9. Operar un batch: frecuencia, fallas y muestra previa.

**Parte 4 — Revisión con varias instancias y pasadas (tarea 4.6).**

10. Por qué la auto-revisión falla: la instancia independiente.
11. Multi-pass review: por archivo y de integración.
12. 📘 Evaluar prompts (lecciones 96 y 97).

---

# Parte 1 — Salida estructurada

## Tema 1 — Tool use with JSON schema (tool use con JSON schema): la forma garantizada

### Qué es

Cuando la respuesta de Claude la va a leer **otro programa** (el sistema de cuentas a pagar de TiendaX, por ejemplo), no alcanza con que "casi siempre" venga bien. Si un día falta una coma, viene un campo con otro nombre o el monto llega como texto, el programa se rompe. Pedir "respondé solo en JSON" en el prompt, o dar ejemplos, mejora la consistencia pero **no garantiza** nada.

Lo que sí garantiza la forma es un **JSON schema** aplicado por la API. La guía dice que la forma más confiable es **tool use con un JSON schema**: definís una tool cuyo input schema es exactamente la estructura que querés extraer, Claude la "llama", y vos leés los datos del bloque `tool_use`. La tool **nunca se ejecuta**: es solo una forma de salida. Así desaparecen los errores de sintaxis del JSON (llaves que faltan, texto antes o después). Y si además marcás la tool con `strict: true`, también quedan garantizados los tipos y los campos obligatorios.

La documentación actual ofrece dos formas de llegar a la garantía, y las dos usan **constrained decoding** (decodificación restringida): mientras genera, Claude solo puede producir texto que cumpla el schema.
- **Strict tool use** (`strict: true` en la tool, que viste en 2A): garantiza que los **argumentos** de la tool cumplan el schema.
- **Structured outputs** (salidas estructuradas, parámetro `output_config.format`): garantiza que **toda la respuesta** sea un JSON que cumpla el schema.

Hay dos casos donde la garantía no se cumple, y por eso hay que mirar el `stop_reason` antes de usar el resultado: si Claude **se niega** a responder (`refusal`, que llega como una respuesta normal con código HTTP 200, no como error) o si la respuesta **se corta** por `max_tokens` (ahí se reintenta con un `max_tokens` más alto), el JSON puede venir incompleto o no venir.

### Cómo se configura

```python
extract_invoice = {
    "name": "extract_invoice",
    "description": "Registra los datos de una factura de proveedor.",
    "strict": True,
    "input_schema": {
        "type": "object",
        "properties": {
            "supplier":     {"type": "string"},
            "invoice_number": {"type": "string"},
            "total_cents":  {"type": "integer", "description": "Total de la factura en centavos."},
            "due_date":     {"type": ["string", "null"], "description": "Vencimiento en formato AAAA-MM-DD. null si el documento no lo menciona."},
        },
        "required": ["supplier", "invoice_number", "total_cents", "due_date"],
        "additionalProperties": False,
    },
}

resp = client.messages.create(
    model=MODEL, max_tokens=2048, tools=[extract_invoice],
    tool_choice={"type": "tool", "name": "extract_invoice"},
    messages=[{"role": "user", "content": f"<document>{factura}</document>"}],
)
datos = next(b.input for b in resp.content if b.type == "tool_use")   # ya es un dict válido
```

### Ejemplo

Antes, SoporteBot extraía las facturas pidiendo "devolvé un JSON con proveedor, número, total y vencimiento". Una de cada cincuenta respuestas rompía el parser: un texto antes del JSON, un campo `"total"` en vez de `"total_cents"`, un monto como `"$90.000"`. Con la tool `extract_invoice` y `strict: true`, esas fallas desaparecen: el resultado siempre tiene los cuatro campos con el tipo correcto.

> ⚠️ **En el curso vas a escuchar otra cosa.** El companion habla de un "JSON mode" que garantiza la sintaxis pero no el schema, y lo pone entre tool use y las instrucciones. **Para el examen:** la API de Claude no tiene un "JSON mode"; si aparece como opción, es inferior a **tool use con JSON schema**, que es la respuesta de la guía. Structured outputs (`output_config.format`) también garantiza la forma, y es igual de válido si aparece.

### Para el examen

- Salida que otro sistema tiene que parsear sin fallar → **tool use con JSON schema** (o structured outputs).
- "Pedir JSON en el prompt", "agregar ejemplos de JSON" o "validar con regex después" → no garantizan.
- La garantía es de **forma**. Antes de usar el resultado, revisá el `stop_reason` (`refusal` o `max_tokens` rompen la garantía).

### Cómo se une

Para que Claude **use** la tool de extracción en lugar de responder con texto, hay que controlar `tool_choice`.

---

## Tema 2 — tool_choice en una extracción

### Qué es

Ya conocés los tres valores de la guía desde 2A. En extracción, cada uno tiene un uso claro:
- **`auto`**: Claude **puede** responder con texto en lugar de llamar la tool. En una extracción eso es un problema: si responde "esta factura parece de $90.000" en texto, el dato no llega a tu sistema.
- **`any`**: Claude **tiene que** llamar alguna tool, pero elige cuál. Es lo que se usa cuando tenés **varios schemas de extracción** (factura, remito, nota de crédito) y **no sabés qué tipo de documento** llegó: Claude elige la tool que corresponde, pero seguro devuelve datos estructurados.
- **Forced** (`{"type": "tool", "name": "extract_metadata"}`): Claude tiene que llamar **esa** tool. Se usa para garantizar que una extracción **corra primero**, antes de los pasos de **enrichment** (enriquecimiento: completar lo extraído con datos de otros sistemas, como buscar al proveedor por su CUIT en el sistema de cuentas a pagar). Para enriquecer, los metadatos tienen que estar extraídos antes. En los turnos siguientes se vuelve a `auto`.

### Ejemplo

A la casilla de TiendaX llegan facturas, remitos y notas de crédito mezclados, sin aviso de qué es cada uno. El equipo define tres tools (`extract_invoice`, `extract_delivery_note`, `extract_credit_note`) y usa `tool_choice: {"type": "any"}`. Claude mira el documento y llama la que corresponde; nunca responde con texto. Si la necesidad fuera otra (primero sacar siempre los metadatos y después enriquecer), se forzaría `extract_metadata` en el primer turno.

> ⚠️ **En la documentación actual vas a leer otra cosa.** En algunos modelos recientes (Opus 5.5, Sonnet 5.5, Fable y Mythos 5.1–5.2), `any` y `tool` devuelven error 400, y la alternativa es `auto` con `strict` o structured outputs. **Para el examen:** respondé como la guía (`any` con tipo de documento desconocido; forced para que una extracción vaya primero), salvo que la pregunta nombre esos modelos. Es lo mismo que viste en 2A.

### Para el examen

- Varios schemas y tipo de documento desconocido → **`any`**.
- Una extracción que tiene que correr antes que el enriquecimiento → **forced** con el nombre de la tool.
- `auto` en una extracción → puede devolver texto en vez de datos.

### Cómo se une

Garantizada la llamada y la forma, queda lo más importante: **qué campos** tiene el schema y cómo se definen. Un schema mal diseñado empuja a Claude a inventar.

---

## Tema 3 — Schema design (diseñar el schema): required, nullable, enums con "other" y "unclear"

### Qué es

El schema no solo define la forma: también **empuja** a Claude. Si un campo es obligatorio, Claude tiene que poner algo ahí, aunque el documento no tenga ese dato. Y cuando no hay dato pero hay que poner algo, **lo inventa**. Por eso la guía pide marcar como **opcionales (nullable)** los campos que **pueden no estar** en el documento. Así Claude tiene una salida honesta: `null` significa "el documento no lo dice".

En JSON Schema son dos cosas distintas, aunque la guía las nombra juntas. Un campo **nullable** acepta `null` como valor (`"type": ["string", "null"]`) y puede seguir siendo obligatorio: siempre aparece, a veces vacío. Un campo **opcional** queda fuera de `required`: puede no aparecer. Las dos le sacan a Claude la presión de inventar, y para el examen se responden igual. (📘 Doc: con `strict` hay un tope por request de 24 parámetros opcionales y 16 campos con unión de tipos como `["string", "null"]`.)

Lo mismo pasa con las categorías. Un **enum** (lista cerrada de valores permitidos) es útil porque el sistema que recibe el dato sabe exactamente qué valores esperar. Pero si un documento no encaja en ninguna categoría, un enum cerrado obliga a meterlo en una equivocada. La guía pide dos válvulas de escape:
- **`"other"` + un campo de detalle**: para una categoría válida que no está en la lista. Claude elige `"other"` y escribe cuál es en un string aparte. Así la lista se puede ampliar después, viendo qué aparece en ese detalle.
- **`"unclear"`**: para cuando el documento es **ambiguo** y no se puede decidir.

| Situación | Valor |
|---|---|
| El dato no está en el documento | `null` |
| El dato está, pero no encaja en ninguna categoría de la lista | `"other"` + detalle |
| El documento es ambiguo; no se puede decidir | `"unclear"` |

Dos detalles más. Las **descripciones de cada campo** son la herramienta principal para que Claude complete bien: qué es, en qué formato, y qué cosas parecidas **no** son ("la fecha de vencimiento, no la de emisión ni la de entrega"). Y si los documentos de origen vienen con formatos distintos (fechas como "15/12", "15 de diciembre" o "2026-12-15"; montos con punto o con coma), la guía pide incluir **reglas de normalización en el prompt** junto al schema. El schema exige el formato final, pero no le explica a Claude cómo convertir cada variante.

### Cómo se configura

```json
"category": {
  "type": "string",
  "enum": ["mercaderia", "flete", "servicios", "impuestos", "other", "unclear"],
  "description": "Rubro de la factura. 'other' si es un rubro real que no está en la lista; 'unclear' si el documento no permite decidir."
},
"category_detail": {
  "type": ["string", "null"],
  "description": "Si category es 'other', el rubro tal como aparece en la factura. Si no, null."
}
```

Y en el prompt: "Normalizá las fechas a AAAA-MM-DD. Si el año no figura, usá el año de emisión de la factura. Convertí los montos a centavos: '$90.000,50' es 9000050."

### Ejemplo

El schema de facturas de TiendaX tenía `due_date` y `purchase_order` como obligatorios. Los proveedores chicos no mandan número de orden de compra, y Claude completaba cosas como `"OC-0001"`, que no existían. El equipo cambia esos campos a nullable y lo explica en la descripción. Los valores inventados desaparecen. Y una factura de "alquiler de depósito", que antes salía como `"servicios"`, ahora sale como `"other"` con detalle `"alquiler"`: así el equipo descubre que necesita ese rubro en la lista.

### Para el examen

- Claude **inventa valores** cuando el dato falta → campos **opcionales / nullable**. No "decile que no invente", no más campos obligatorios.
- Categorías que no entran en el enum → **`"other"` + campo de detalle**. Documento ambiguo → **`"unclear"`**.
- Formatos de origen inconsistentes → **reglas de normalización en el prompt** junto al schema.

### Cómo se une

Con un buen schema, el JSON siempre viene bien formado y sin valores inventados. Pero eso no significa que los datos sean **correctos**. Esa diferencia es la base de toda la tarea 4.4.

---

## Tema 4 — Syntax vs. semantic errors (errores de sintaxis vs. errores semánticos)

### Qué es

Hay dos clases de error muy distintas, y la guía insiste en separarlas:
- **Errores de sintaxis o de schema**: el JSON está mal formado, falta un campo obligatorio, un número viene como texto. **Tool use con schema elimina el JSON mal formado**, y con `strict: true` también garantiza los tipos y los campos obligatorios.
- **Errores semánticos**: el JSON es perfecto, pero **lo que dice está mal**. Las líneas de la factura no suman el total. La fecha de vencimiento quedó en el campo de la fecha de emisión. El proveedor es el cliente. **El schema no los puede ver**, porque solo controla la forma.

Por eso "ya usamos `strict`, no hace falta validar" es un error clásico. Los errores semánticos se encuentran con **validación en tu código** (reglas de negocio: ¿suman las líneas?, ¿el vencimiento es posterior a la emisión?) y se corrigen con los reintentos de la Parte 2.

### Ejemplo

Una factura extraída con `strict: true` llega con `total_cents: 9000000` y tres líneas que suman 8.100.000. El JSON es válido; el schema no tiene nada que objetar. Una regla en el código ("la suma de las líneas tiene que dar el total") detecta el problema.

### Para el examen

- Errores de sintaxis → los elimina **tool use con schema**.
- Totales que no suman, valores en el campo equivocado → errores **semánticos**: el schema **no** los evita. Hace falta **validación en código** y reintento.
- Distractores para un error semántico: `additionalProperties: false`, más campos obligatorios o cambiar `tool_choice`. Ninguno mira los valores.

### Cómo se une

Detectar el error es la mitad. La otra mitad es pedirle a Claude que lo corrija bien.

---

# Parte 2 — Validación y reintentos

## Tema 5 — Retry with error feedback (reintentar con el error)

### Qué es

Cuando la validación encuentra un problema, se le puede pedir a Claude que corrija. Lo que importa es **cómo** se lo pedís. Un "intentá de nuevo" no le da nada nuevo: va a repetir el mismo error. La guía pide un pedido de corrección con **tres cosas**:
1. **El documento original**, para que vuelva a mirar la fuente.
2. **La extracción que falló**, para que vea qué había respondido.
3. **El error de validación específico**: qué regla falló y en qué campo.

Con eso Claude puede comparar su respuesta con la fuente y arreglar exactamente lo que está mal. Las slides agregan un buen detalle: pedirle que **corrija solo los campos que fallaron** y deje el resto igual.

📘 Curso: Jacob recomienda un **tope de 2 a 3 reintentos** y, si se agota, **escalar** (devolver un error o pasarlo a una persona), nunca quedarse en silencio. También sugiere mirar la tasa de reintentos: si muchas extracciones necesitan reintento, el problema está en el prompt o en el schema, no en casos sueltos.

### Cómo se configura

```python
retry_prompt = f"""<document>{factura}</document>

<previous_extraction>{json.dumps(datos)}</previous_extraction>

<validation_error>
Las líneas suman 8.100.000 centavos, pero total_cents es 9.000.000.
</validation_error>

Volvé a revisar el documento y corregí solo los campos involucrados en este error.
Dejá los demás campos sin cambios."""
```

> ⚠️ **En el curso vas a escuchar otra cosa.** El companion dice que, si Claude repite el mismo error, conviene "a small temperature bump" en cada reintento. **Para el examen:** la temperatura no es la palanca (en los modelos actuales ni siquiera se puede cambiar, como viste en 4B; las propias slides lo corrigen). Lo que hace funcionar un reintento es **el error específico, el documento y la extracción anterior**.

### Para el examen

- Reintento útil = **documento original + extracción fallida + error específico**.
- "Try again", o un reintento sin reenviar el documento → distractores.
- Subir la temperatura en el reintento → distractor.

### Cómo se une

Un reintento bien armado arregla muchos errores. Pero hay un caso donde ningún reintento sirve, y el examen lo pregunta.

---

## Tema 6 — When retries are ineffective (cuándo reintentar no sirve)

### Qué es

Un reintento sirve cuando el dato **está** en el documento y Claude se equivocó al leerlo o al escribirlo: un formato mal convertido, un campo en el lugar equivocado, una estructura incompleta. En esos casos, con el error a la vista, Claude puede corregir.

Pero si la información **no está en el documento**, reintentar no sirve: Claude no la puede sacar de la nada. El ejemplo de la guía es un dato que solo existe en **otro documento que no le pasaste**: la factura dice "según la orden de compra adjunta", pero la orden no vino. Reintentar diez veces da diez veces lo mismo, o peor, un valor inventado. Lo correcto es dejar el campo en `null`, marcarlo como faltante, pedir el documento que falta o escalar a una persona.

| El error es… | ¿Reintentar sirve? |
|---|---|
| Formato mal convertido ("15/12" → fecha incorrecta) | Sí |
| Estructura de salida incompleta o campo en el lugar equivocado | Sí |
| El dato está en otro documento que no se envió | **No** |
| El dato no existe en la fuente | **No** |

### Ejemplo

La validación marca que una factura de un proveedor de fletes no tiene `purchase_order`. El texto dice "OC según remito adjunto", pero el remito no llegó con el email. El sistema no reintenta: guarda `purchase_order: null`, marca la factura como "documentación incompleta" y le avisa al equipo de compras para que pida el remito.

### Para el examen

- Dato ausente del documento, o que está en un documento externo no provisto → **reintentar no sirve**. Null, marcar como faltante, pedir el documento o escalar.
- Error de formato o de estructura → reintentar **sí** sirve.
- "Subir la cantidad de reintentos" cuando el dato no está → distractor.

### Cómo se une

Hasta acá, el código detecta los errores. La guía propone además que **el propio resultado** traiga la información para encontrarlos.

---

## Tema 7 — Self-correction fields (campos que muestran los problemas): calculated_total, conflict_detected y detected_pattern

### Qué es

La guía propone agregar al schema campos que no son el dato en sí, sino **información para validar y aprender**. Son tres.

**`calculated_total` y `stated_total`.** En vez de pedir solo "el total", pedís dos valores: el total que **dice** la factura (`stated_total`) y el que **resulta** de sumar las líneas (`calculated_total`). Si no coinciden, hay un problema, y queda a la vista. Lo importante es que Claude **no corrija en silencio** uno de los dos: si la factura tiene un error de suma, el sistema tiene que enterarse.

**`conflict_detected`.** Un booleano que Claude pone en `true` cuando **el propio documento se contradice**: dos fechas de vencimiento distintas, un CUIT en el encabezado y otro en el pie. Así el conflicto no se resuelve eligiendo uno al azar: se marca y lo revisa alguien.

**`detected_pattern`.** Este viene del escenario de **code review**, no de facturas. Cada hallazgo del bot de review lleva un campo que dice **qué construcción del código lo disparó** (por ejemplo, `"catch sin relanzar"` o `"map dentro de map"`). Cuando los devs descartan hallazgos, se puede analizar qué patrones generan más descartes, es decir, cuáles son los falsos positivos sistemáticos. Es la forma de saber **qué categoría** desactivar o mejorar, como viste en 4A, en lugar de ajustar el prompt a ciegas.

### Cómo se configura

```json
{
  "stated_total_cents": 9000000,
  "calculated_total_cents": 8100000,
  "conflict_detected": true,
  "conflict_description": "El total impreso no coincide con la suma de las líneas."
}
```

```json
{
  "location": "src/orders/api.ts:88",
  "issue": "El error de cobro se ignora.",
  "severity": "Crítico",
  "detected_pattern": "catch sin relanzar"
}
```

### Ejemplo

Después de un mes con `detected_pattern`, el equipo de TiendaX cruza los hallazgos con lo que los devs marcaron como "no aplica". Descubre que el 70% de los descartes vienen de un solo patrón: `"map dentro de map"`. Ya sabe exactamente qué criterio reescribir.

### Para el examen

- Detectar facturas con errores de suma → extraer **`calculated_total` y `stated_total`** y comparar. No "corregir el total" en silencio.
- Documento que se contradice → **`conflict_detected`**.
- Los devs descartan muchos hallazgos y no sabés por qué → **`detected_pattern`** para analizar qué patrones generan falsos positivos.

### Cómo se une

Hasta acá, un documento por vez. Cuando hay miles, aparece la pregunta del costo y del tiempo: la Parte 3.

---

# Parte 3 — Procesamiento en lote

## Tema 8 — Message Batches API: qué es y cuándo usarla

### Qué es

La **Message Batches API** (API de lotes de mensajes) permite mandar muchos requests juntos para que se procesen **de forma asíncrona**: los enviás, la API los procesa cuando puede, y vos consultás más tarde los resultados. A cambio de no tener respuesta inmediata, **cuesta un 50% menos**. Cada request del lote da el mismo resultado que daría la API normal.

Lo central para el examen es el trato: la mayoría de los lotes terminan en menos de una hora, pero el **techo es de 24 horas** y **no hay garantía de latencia** (no hay un tiempo de respuesta comprometido). Por eso:
- Sirve para trabajo que **nadie está esperando**: reportes nocturnos, auditorías semanales, generación nocturna de tests, procesar el archivo histórico de facturas.
- **No** sirve para nada que **bloquea** a una persona o a un pipeline: un check que tiene que terminar antes del merge, una respuesta a un cliente.

Hay dos detalles técnicos que la guía pregunta:
- **No hay tool calling de varios turnos dentro de un request.** Cada request del lote es una sola llamada: Claude puede pedir una tool, pero vos no podés ejecutarla y devolverle el resultado en el mismo request para que siga. Si el flujo necesita ese ida y vuelta, no va en batch.

> ⚠️ **En la documentación actual vas a leer otra cosa.** La doc dice que los batches admiten tool use (incluidas las tools que ejecuta Anthropic del lado del servidor) y conversaciones de varios turnos como historial de entrada. Lo que sigue sin poder hacerse es el ida y vuelta de **una tool tuya** dentro de un request. **Para el examen:** si el flujo necesita ejecutar tus tools y seguir con el resultado, va en la API síncrona.
- **`custom_id`**: cada request lleva un identificador que vos elegís (por ejemplo, el id de la factura). Los resultados **no vuelven en el orden en que los mandaste**, así que se correlacionan por `custom_id`. Leerlos por posición es un error que falla en silencio: cada resultado queda pegado a la factura equivocada.

📘 Datos de la documentación: un lote admite hasta **100.000 requests o 256 MB**, y los resultados quedan disponibles **29 días**. No hay notificación al terminar: se consulta el estado periódicamente (polling).

### Ejemplo

Es la pregunta oficial **Q11**, que viste en 3D. TiendaX tiene dos flujos: el **check pre-merge** del bot de review (los devs esperan el resultado para mergear) y un **reporte nocturno de deuda técnica**. El gerente propone pasar los dos a Batches para ahorrar el 50%. La respuesta correcta: **Batches solo para el reporte nocturno; el pre-merge sigue en tiempo real**.

### Para el examen

- No bloqueante y tolera demora (nocturno, semanal) → **Batches**. Bloqueante (pre-merge, interactivo) → **API síncrona**.
- Distractores de Q11: pasar los dos a batch "con polling" (no hay garantía de tiempo), pasar los dos con "fallback a tiempo real si tarda" (complejidad innecesaria), y mantener los dos en tiempo real "para evitar problemas con el orden de los resultados" (eso se resuelve con `custom_id`).
- El flujo necesita ejecutar tus tools y seguir → **no** va en batch.
- Correlacionar resultados → **`custom_id`**, nunca por posición.

### Cómo se une

Saber cuándo usar Batches es la mitad de 4.5. La otra mitad es operarlo bien: cada cuánto mandar, qué hacer con lo que falla y cómo no desperdiciar plata.

---

## Tema 9 — Operar un batch: frecuencia de envío, fallas y muestra previa

### Qué es

**Calcular cada cuánto enviar.** Si tenés un compromiso de tiempo (un **SLA**, service level agreement: "toda factura recibida queda procesada en 30 horas"), tenés que contar el peor caso. Una factura puede llegar justo después de un envío y esperar hasta el siguiente; después, el lote puede tardar hasta 24 horas. Entonces: **espera hasta el próximo envío + 24 horas ≤ SLA**. Con un SLA de 30 horas quedan 6 horas para la espera, y la guía da como ejemplo **enviar cada 4 horas**, lo que deja margen. Enviar cada 6 horas llega justo, sin colchón.

**Reenviar solo lo que falló.** Cuando termina un lote, cada resultado tiene un estado: `succeeded` (salió bien), `errored` (hubo un error), `expired` (no se procesó en 24 horas) o `canceled`. Los tres últimos no se cobran. Si un `errored` fue por un pedido mal armado, hay que corregirlo antes de reenviar; si fue un error del servidor, se reenvía tal cual. Si de 1.000 facturas fallaron 40, se reenvían **solo esas 40**, identificadas por `custom_id`, no el lote entero (pagarías de nuevo las 960 que ya salieron). Y **con las modificaciones necesarias**: si una falló porque el documento era demasiado largo para el contexto, reenviarla igual va a fallar igual; hay que **partirla en pedazos** (chunking) antes.

**Probar con una muestra antes del volumen.** Antes de mandar 8.000 documentos, refiná el prompt con una muestra chica (por ejemplo, 200). Si hay un error en el prompt, lo encontrás con 200 documentos y no después de pagar 8.000 y tener que reenviarlos todos. Además, la API recién valida cada request del lote cuando lo procesa, así que conviene probar uno con la API normal antes de armar el lote.

### Ejemplo

TiendaX va a procesar el archivo histórico de 8.000 facturas, con un SLA interno de 30 horas para las facturas nuevas que llegan todos los días.
1. Prueba el prompt con 200 facturas en la API normal, ajusta las reglas de normalización y recién después arma el lote.
2. Para las nuevas, programa un envío cada 4 horas: en el peor caso, una factura espera 4 horas más 24 de procesamiento, y quedan 2 de margen.
3. En el primer lote fallan 40: 35 por un error de servidor y 5 por exceder el contexto. Reenvía solo esas 40 por `custom_id`, y las 5 largas, partidas en dos.

### Para el examen

- Frecuencia según SLA → **intervalo de envío + 24 h ≤ SLA** (30 h → cada 4 h).
- Fallas parciales → reenviar **solo las fallidas, por `custom_id`**, con modificaciones (chunking si excedieron el contexto).
- Volumen grande → **refinar el prompt con una muestra** primero.

### Cómo se une

Con esto la extracción produce datos bien formados, validados y a escala. La última tarea del módulo es cómo **revisar** un resultado (código o datos) para atrapar lo que se escapó.

---

# Parte 4 — Revisión con varias instancias y pasadas

## Tema 10 — Self-review limitations (por qué la auto-revisión falla): la instancia independiente

### Qué es

Cuando Claude genera código y en la **misma sesión** le pedís que lo revise, revisa con el mismo razonamiento que usó para escribirlo. Ya "sabe" por qué tomó cada decisión, así que es poco probable que las cuestione. Es lo mismo que le pasa a una persona que revisa su propio texto: lee lo que quiso escribir, no lo que escribió.

La solución de la guía es una **instancia independiente**: otra llamada a Claude, **sin el contexto de razonamiento** de la que generó el código. Solo recibe el código (y los criterios de review). Esa instancia encuentra problemas sutiles que la auto-revisión no ve. La guía es explícita: es **más efectiva que pedirle que se autorrevise y que usar extended thinking**.

> ⚠️ **En el curso vas a escuchar otra cosa.** Jacob presenta la auto-revisión como una opción válida "más barata", y la revisión cruzada como usar "otro modelo, a menudo más fuerte". **Para el examen:** la auto-revisión en la misma sesión es una **limitación**, no una alternativa económica. Y lo que importa de la instancia independiente es que **no tiene el contexto del generador**, no que sea un modelo más grande. Puede ser el mismo modelo.

### Ejemplo

El agente de TiendaX que genera migraciones de base de datos termina cada tarea con "revisá tu migración y confirmá que es segura". Siempre confirma. El equipo cambia el flujo: la migración se manda a una **segunda instancia**, que solo recibe el archivo y un checklist ("¿la migración es reversible?, ¿bloquea la tabla de pedidos?"). En la primera semana encuentra dos migraciones que bloqueaban la tabla.

### Para el examen

- Revisar código generado → **una segunda instancia independiente, sin el razonamiento del generador**.
- Distractores: pedirle a la misma sesión que revise "con cuidado", activar extended thinking, usar un modelo más grande en la misma sesión.

### Cómo se une

Una instancia independiente resuelve el problema del sesgo. Cuando el material a revisar es muy grande, aparece otro problema: la atención.

---

## Tema 11 — Multi-pass review (revisión en varias pasadas): por archivo y de integración

### Qué es

Es la pregunta oficial **Q12**, que viste en detalle en 1B. Cuando se revisa un PR de muchos archivos en una sola pasada, la atención se reparte (**attention dilution**, dilución de la atención): unos archivos se revisan a fondo y otros por arriba, los resultados cambian entre corridas y hasta aparecen hallazgos contradictorios.

La solución es dividir la revisión en dos tipos de pasada:
- **Pasadas por archivo**: cada archivo se revisa por separado, con toda la atención, buscando **problemas locales**.
- **Una pasada de integración**: mira cómo **fluyen los datos entre archivos** (una función que cambió su firma, un campo que un archivo produce y otro consume mal). Sin esta pasada, se pierden justamente los problemas que solo aparecen al juntar archivos.

La guía agrega un tercer elemento: **pasadas de verificación en las que el modelo reporta su confianza en cada hallazgo**, para **enrutar** la revisión. Los hallazgos de confianza alta pueden publicarse directo, y los de confianza baja van a una persona. Ojo con un matiz que vas a ver en 5D: la confianza que el modelo se asigna no es confiable por sí sola (lo dijo la Q3), así que los umbrales hay que **calibrarlos** con casos cuya respuesta ya conocés.

### Ejemplo

Un PR de TiendaX toca 14 archivos del checkout. El bot lo revisa con una pasada por cada uno de los 14 archivos (en paralelo) y una de integración. La de integración encuentra que `cart.ts` ahora devuelve montos en centavos, pero `invoice.ts` los sigue tratando como pesos: ninguna pasada por archivo lo podía ver. Cada hallazgo sale con su confianza; los de confianza baja quedan como "para revisar" en lugar de comentario directo.

### Para el examen

- PR grande con revisión inconsistente → **pasadas por archivo + pasada de integración** (Q12).
- Distractores de Q12: pedir PRs más chicos (traslada el problema a los devs), usar un modelo con más contexto (el problema es la atención, no el espacio) y correr tres pasadas completas y quedarse con lo que aparece en dos de tres (suprime bugs reales).
- Solo pasadas por archivo, sin integración → se pierden los problemas entre archivos.
- Enrutar hallazgos según la confianza que reporta el modelo → vale, **con umbrales calibrados**.

### Cómo se une

Revisar bien un resultado es una forma de evaluarlo. El curso dedica dos lecciones a evaluar los prompts de forma sistemática.

---

## Tema 12 — 📘 Evaluar prompts (lecciones 96 y 97)

### Qué es

Esto es **solo del curso**: la guía no evalúa estos temas directo, pero la idea te sirve para entender el resto.

Probar un prompt con cinco casos "a ojo" no alcanza: no cubre casos borde ni entradas maliciosas, y no deja registro. La alternativa es una **eval** (evaluación): un **dataset** (conjunto de casos) con la salida esperada, contra el que corrés el prompt cada vez que lo cambiás. Jacob propone medir la **tasa de aciertos**, la **tasa de regresiones** (casos que antes andaban y ahora fallan), la latencia y el costo. Y correr **la suite completa** en cada cambio, no solo los casos relacionados: un arreglo que rompe otra cosa no es una mejora.

Para corregir las respuestas hay dos opciones. La **corrección por código** sirve cuando la respuesta correcta se puede expresar como una regla (el JSON tiene tal valor): es rápida y determinista. La **corrección con un modelo** (model-based grading) sirve para respuestas abiertas, pero hay que **calibrarla** contra el juicio de personas antes de confiar en sus notas.

### Para el examen

- Si aparece, la idea es: **medir contra un set de casos con respuesta conocida**, no "parece que anda". Es lo mismo que viste en 4A para reactivar una categoría.

### Cómo se une

Es la misma herramienta que hace falta para calibrar los umbrales de confianza del Tema 11: un set de casos con la respuesta correcta conocida. En 5D se retoma para medir la confianza y la precisión de un sistema.

---

## Cómo se une todo

Para que otro sistema pueda leer lo que extrae Claude, la forma se garantiza con **tool use y un JSON schema** (o structured outputs), revisando el `stop_reason` (Tema 1). Con **`any`**, Claude tiene que llamar alguna de varias tools de extracción; con **forced**, una en particular va primero (Tema 2). El schema define cómo responde Claude cuando falta algo: **nullable** para lo que puede no estar, **`"other"` + detalle** para categorías nuevas, **`"unclear"`** para lo ambiguo, y reglas de normalización en el prompt (Tema 3). Pero el schema solo elimina errores de **sintaxis**: los **semánticos** (sumas, campos cruzados) necesitan validación en código (Tema 4).

Cuando la validación falla, el reintento lleva **el documento, la extracción fallida y el error específico** (Tema 5), y no se reintenta si el dato **no está** en el documento (Tema 6). Campos como **`calculated_total` / `stated_total`**, **`conflict_detected`** y **`detected_pattern`** hacen que el resultado muestre sus propios problemas (Tema 7).

A escala, la **Batches API** cuesta la mitad pero puede tardar 24 horas: sirve para lo que no bloquea, se correlaciona por **`custom_id`** y no admite ida y vuelta de tools (Tema 8). Se envía con una frecuencia que respete el SLA, se reenvía solo lo que falló y se prueba antes con una muestra (Tema 9). Y para revisar, una **instancia independiente** sin el razonamiento del generador (Tema 10), con **pasadas por archivo y de integración** cuando el material es grande (Tema 11).

## Lo que viene

Termina el módulo 4. Lo próximo son las **preguntas de fin del módulo 4** (4A a 4C, tareas 4.1 a 4.6), de a una y con el formato del examen. Después arranca el **módulo 5: Context Management & Reliability** (manejo del contexto largo, escalamiento, propagación de errores, conocimiento entre sesiones y confianza).

---

## Las trampas del examen

Cada trampa tiene el mismo orden: la situación, **qué elegir en el examen (✅)**, las opciones que tientan (❌) con por qué tientan y por qué están mal, y una regla para recordar.

### Grupo: Salida estructurada (tarea 4.3)

#### Trampa 1 · Pedir JSON en el prompt

**La situación.** El sistema de cuentas a pagar falla cada tanto porque la extracción de Claude viene con texto extra o con un campo mal nombrado (Tema 1).

**✅ En el examen elegí:** **definir una tool de extracción con un JSON schema** (tool use) y leer los datos del `tool_use`.

**❌ Las que tientan:**

❌ **"Reforzar en el system prompt: 'respondé solo con JSON válido'".**
- *Tienta porque:* ataca el síntoma directamente.
- *Está mal porque:* sigue siendo probabilístico; no garantiza la forma.

❌ **"Agregar ejemplos de JSON bien formado".**
- *Tienta porque:* few-shot da consistencia (4B).
- *Está mal porque:* consistencia no es garantía.

❌ **"Limpiar la respuesta con una regex antes de parsear".**
- *Tienta porque:* parece robusto.
- *Está mal porque:* parchea después en lugar de garantizar en la generación.

> 🧠 **Para recordar:** forma garantizada = **tool use + JSON schema**.

#### Trampa 2 · auto, any o forced

**La situación.** Llegan facturas, remitos y notas de crédito mezclados. Hay una tool de extracción para cada tipo y no se sabe qué tipo es cada documento. A veces Claude responde con texto en lugar de extraer (Tema 2).

**✅ En el examen elegí:** **`tool_choice: {"type": "any"}`**.

**❌ Las que tientan:**

❌ **"Dejar `auto` y pedir en el prompt que siempre use una tool".**
- *Tienta porque:* `auto` es el default.
- *Está mal porque:* con `auto`, Claude puede responder con texto.

❌ **"Forzar `extract_invoice`".**
- *Tienta porque:* garantiza una llamada.
- *Está mal porque:* fuerza la tool de facturas aunque llegue un remito.

> 🧠 **Para recordar:** varios schemas y tipo desconocido = **any**; una que va primero = **forced**.

#### Trampa 3 · Que la extracción de metadatos vaya primero

**La situación.** En el pipeline de facturas, `extract_metadata` tiene que correr siempre antes de las tools de enriquecimiento, porque estas necesitan el CUIT y el número de factura (Tema 2).

**✅ En el examen elegí:** **forzar la tool en el primer turno**: `tool_choice: {"type": "tool", "name": "extract_metadata"}`, y después volver a `auto`.

**❌ Las que tientan:**

❌ **"Usar `tool_choice: any`".**
- *Tienta porque:* garantiza que Claude llame una tool.
- *Está mal porque:* deja que Claude elija cuál; puede empezar por una de enriquecimiento.

❌ **"Indicarlo en el prompt: 'primero extraé los metadatos'".**
- *Tienta porque:* suele funcionar.
- *Está mal porque:* es probabilístico; forzar la tool lo garantiza.

> 🧠 **Para recordar:** **any** = alguna; **forced** = esa, y primero.

#### Trampa 4 · El campo obligatorio que no existe

**La situación.** La extracción completa `purchase_order` con números que no existen cuando el proveedor no manda orden de compra (Tema 3).

**✅ En el examen elegí:** **hacer el campo opcional / nullable** y explicar en la descripción cuándo va `null`.

**❌ Las que tientan:**

❌ **"Agregar al prompt 'no inventes datos'".**
- *Tienta porque:* ataca el síntoma.
- *Está mal porque:* el schema sigue obligando a poner algo; la presión viene del campo obligatorio.

❌ **"Agregar una validación que rechace los números de orden que no existen y reintentar".**
- *Tienta porque:* detecta el problema.
- *Está mal porque:* el dato no está en el documento; reintentar no lo hace aparecer (Tema 6).

> 🧠 **Para recordar:** campo que puede faltar = **nullable**.

#### Trampa 5 · El enum sin salida

**La situación.** El enum de rubros tiene cuatro valores. Las facturas de rubros nuevos terminan clasificadas en el más parecido, y nadie se entera de que faltan rubros (Tema 3).

**✅ En el examen elegí:** **agregar `"other"` con un campo de detalle** (y `"unclear"` para los casos ambiguos).

**❌ Las que tientan:**

❌ **"Cambiar el enum por un string libre".**
- *Tienta porque:* acepta cualquier rubro.
- *Está mal porque:* el sistema que recibe el dato pierde la lista cerrada y aparecen variantes de lo mismo.

❌ **"Agregar todos los rubros posibles al enum".**
- *Tienta porque:* parece completo.
- *Está mal porque:* nunca vas a prever todos; la lista tiene que poder crecer.

> 🧠 **Para recordar:** categoría nueva = **other + detalle**; ambiguo = **unclear**; ausente = **null**.

#### Trampa 6 · "Ya usamos strict, no hace falta validar"

**La situación.** Las facturas extraídas con `strict: true` a veces tienen líneas que no suman el total (Tema 4).

**✅ En el examen elegí:** **agregar validación semántica en código** (la suma de las líneas contra el total) y reintentar con el error.

**❌ Las que tientan:**

❌ **"Agregar `additionalProperties: false` y más campos obligatorios".**
- *Tienta porque:* endurece el schema.
- *Está mal porque:* el schema controla la forma, no los valores.

❌ **"No hace falta: con strict el resultado es válido".**
- *Tienta porque:* strict garantiza el schema.
- *Está mal porque:* garantiza la sintaxis, no la semántica.

> 🧠 **Para recordar:** el schema garantiza la **forma**; los **valores** se validan en código.

### Grupo: Validación y reintentos (tarea 4.4)

#### Trampa 7 · "Intentá de nuevo"

**La situación.** La validación detecta que el vencimiento es anterior a la emisión. El sistema reintenta con "La extracción tuvo un error, intentá de nuevo" (Tema 5).

**✅ En el examen elegí:** **reintentar con el documento original, la extracción fallida y el error específico** ("due_date 2026-11-01 es anterior a issue_date 2026-11-15").

**❌ Las que tientan:**

❌ **"Reintentar con una temperatura un poco más alta para que salga distinto".**
- *Tienta porque:* el companion lo sugiere.
- *Está mal porque:* no le da información nueva, y en los modelos actuales ni se puede cambiar.

❌ **"Reintentar mandando solo el error, sin el documento".**
- *Tienta porque:* ahorra tokens.
- *Está mal porque:* Claude necesita volver a mirar la fuente para corregir.

> 🧠 **Para recordar:** reintento = **documento + respuesta fallida + error específico**.

#### Trampa 8 · Reintentar lo que no está

**La situación.** Una factura dice "OC según remito adjunto", pero el remito no vino. La validación marca `purchase_order` vacío (Tema 6).

**✅ En el examen elegí:** **no reintentar**: dejar `null`, marcar la factura como incompleta y pedir el documento que falta (o escalar).

**❌ Las que tientan:**

❌ **"Reintentar hasta 5 veces con el error específico".**
- *Tienta porque:* es el patrón correcto de reintento.
- *Está mal porque:* el dato no está en lo que Claude recibe; ningún reintento lo hace aparecer.

> 🧠 **Para recordar:** si el dato **no está**, reintentar **no sirve**.

#### Trampa 9 · Corregir el total en silencio

**La situación.** Querés detectar las facturas de proveedores que vienen con errores de suma (Tema 7).

**✅ En el examen elegí:** **extraer `stated_total` y `calculated_total`**, y marcar `conflict_detected` cuando no coinciden.

**❌ Las que tientan:**

❌ **"Pedirle que, si el total no coincide, use la suma de las líneas".**
- *Tienta porque:* el dato queda "correcto".
- *Está mal porque:* esconde el error del proveedor; nadie se entera.

> 🧠 **Para recordar:** los conflictos **se marcan**, no se arreglan en silencio.

#### Trampa 10 · Los hallazgos que nadie quiere

**La situación.** Los devs descartan el 40% de los hallazgos del bot y el equipo no sabe por qué (Tema 7).

**✅ En el examen elegí:** **agregar `detected_pattern` a cada hallazgo** para analizar qué construcciones generan los descartes.

**❌ Las que tientan:**

❌ **"Reescribir el prompt para que sea más estricto".**
- *Tienta porque:* hay que bajar el ruido.
- *Está mal porque:* sin saber qué patrón genera los descartes, se ajusta a ciegas.

> 🧠 **Para recordar:** antes de corregir, **medí qué patrón** falla.

### Grupo: Batches (tarea 4.5)

#### Trampa 11 · Todo a Batches (Q11)

**La situación.** El gerente quiere pasar a Batches el check pre-merge y el reporte nocturno de deuda técnica, por el 50% de ahorro (Tema 8).

**✅ En el examen elegí:** **Batches solo para el reporte nocturno; el pre-merge sigue en tiempo real**.

**❌ Las que tientan:**

❌ **"Pasar los dos a Batches y hacer polling hasta que termine".**
- *Tienta porque:* casi siempre termina en menos de una hora.
- *Está mal porque:* no hay garantía: puede tardar 24 horas y bloquear el merge.

❌ **"Pasar los dos a Batches con fallback a tiempo real si tarda demasiado".**
- *Tienta porque:* parece tener lo mejor de los dos.
- *Está mal porque:* agrega complejidad sin sentido; alcanza con usar cada API en su caso.

❌ **"Mantener los dos en tiempo real por los problemas de orden de los resultados".**
- *Tienta porque:* los resultados vuelven desordenados.
- *Está mal porque:* eso se resuelve con `custom_id`.

> 🧠 **Para recordar:** si **alguien espera**, no va en batch.

#### Trampa 12 · El agente con tools en un batch

**La situación.** Un flujo de conciliación necesita que Claude consulte el sistema de pagos (una tool tuya) y siga razonando con el resultado. Quieren pasarlo a Batches (Tema 8).

**✅ En el examen elegí:** **mantener ese flujo en la API síncrona**: un request de batch no puede ejecutar tus tools y seguir.

**❌ Las que tientan:**

❌ **"Mandarlo en batch y ejecutar la tool cuando vuelva el resultado".**
- *Tienta porque:* el resultado sí trae el pedido de tool.
- *Está mal porque:* para seguir hace falta otro request; el ida y vuelta no entra en un request de batch.

> 🧠 **Para recordar:** batch = **un turno por request**.

#### Trampa 13 · Reenviar el lote entero

**La situación.** De un lote de 1.000 facturas, fallaron 40: algunas por error del servidor y otras por exceder el contexto (Tema 9).

**✅ En el examen elegí:** **reenviar solo las 40, identificadas por `custom_id`**, partiendo en pedazos las que excedieron el contexto.

**❌ Las que tientan:**

❌ **"Reenviar el lote completo para asegurarse".**
- *Tienta porque:* parece más seguro.
- *Está mal porque:* pagás de nuevo las 960 que ya salieron bien.

❌ **"Reenviar las 40 tal cual".**
- *Tienta porque:* es lo más simple.
- *Está mal porque:* las que excedieron el contexto van a volver a fallar.

> 🧠 **Para recordar:** se reenvían **solo las fallidas**, **por `custom_id`** y **corregidas**.

#### Trampa 14 · La frecuencia que no llega al SLA

**La situación.** Las facturas nuevas tienen que estar procesadas en 30 horas, y el batch puede tardar hasta 24 (Tema 9).

**✅ En el examen elegí:** **enviar un lote cada 4 horas** (o con un intervalo que deje margen: espera + 24 h ≤ 30 h).

**❌ Las que tientan:**

❌ **"Un lote por día, a la noche".**
- *Tienta porque:* es lo más barato de operar.
- *Está mal porque:* una factura que llega a la mañana puede esperar casi 24 horas más otras 24 de procesamiento.

❌ **"Calcular con el tiempo típico, que es menos de una hora".**
- *Tienta porque:* es lo que suele pasar.
- *Está mal porque:* el SLA se calcula con el peor caso, 24 horas.

> 🧠 **Para recordar:** **intervalo + 24 h ≤ SLA**.

### Grupo: Revisión (tarea 4.6)

#### Trampa 15 · Que se revise a sí mismo

**La situación.** Un agente genera código y querés atrapar errores sutiles antes del merge (Tema 10).

**✅ En el examen elegí:** **una segunda instancia independiente, sin el contexto de razonamiento del generador**.

**❌ Las que tientan:**

❌ **"Pedirle a la misma sesión que revise su código con cuidado".**
- *Tienta porque:* es simple y barato.
- *Está mal porque:* revisa con el mismo razonamiento que usó para escribirlo.

❌ **"Activar extended thinking en la sesión que generó el código".**
- *Tienta porque:* más razonamiento parece más revisión.
- *Está mal porque:* la guía dice que la instancia independiente es más efectiva.

> 🧠 **Para recordar:** revisar = **otra instancia, sin el contexto del generador**.

#### Trampa 16 · El PR de 14 archivos (Q12)

**La situación.** La revisión de un PR de 14 archivos sale inconsistente: algunos archivos revisados a fondo, otros por arriba, y hallazgos contradictorios (Tema 11).

**✅ En el examen elegí:** **pasadas por archivo para los problemas locales + una pasada de integración para el flujo entre archivos**.

**❌ Las que tientan:**

❌ **"Usar un modelo con una ventana de contexto más grande".**
- *Tienta porque:* entran todos los archivos.
- *Está mal porque:* el problema es cómo se reparte la atención, no el espacio.

❌ **"Tres pasadas completas y reportar lo que aparezca en dos de tres".**
- *Tienta porque:* el consenso parece más confiable.
- *Está mal porque:* descarta bugs reales que una sola pasada encontró, y sigue revisando todo junto.

❌ **"Pedir a los devs PRs de 3 o 4 archivos".**
- *Tienta porque:* achica el problema.
- *Está mal porque:* le traslada el problema al equipo en vez de resolverlo en la revisión.

> 🧠 **Para recordar:** mucho material = **por archivo + integración**.

---

## Checklist oficial

**Tarea 4.3 — Enforce structured output using tool use and JSON schemas**

*Knowledge of*
- [x] Tool use con JSON schemas como la forma más confiable de lograr salida que cumple el schema, eliminando errores de sintaxis → **Tema 1** (Trampa 1)
- [x] La diferencia entre `tool_choice` `auto` (puede responder con texto), `any` (tiene que llamar alguna tool) y forced (tiene que llamar esa tool) → **Tema 2** (Trampa 2)
- [x] Que los schemas strict eliminan errores de sintaxis pero no errores semánticos (líneas que no suman el total, valores en el campo equivocado) → **Tema 4** (Trampa 6)
- [x] Diseño del schema: campos obligatorios vs. opcionales, enums con `"other"` + string de detalle para categorías extensibles → **Tema 3** (Trampas 4 y 5)

*Skills in*
- [x] Definir tools de extracción con JSON schemas como parámetros y sacar los datos del `tool_use` → **Tema 1**
- [x] Usar `tool_choice: "any"` cuando hay varios schemas y el tipo de documento es desconocido → **Tema 2** (Trampa 2)
- [x] Forzar una tool (`{"type": "tool", "name": "extract_metadata"}`) para que una extracción corra antes del enriquecimiento → **Tema 2** (Trampa 3)
- [x] Diseñar campos opcionales (nullable) cuando el documento puede no tener el dato, para que el modelo no invente → **Tema 3** (Trampa 4)
- [x] Agregar valores como `"unclear"` para casos ambiguos y `"other"` + detalle para categorías extensibles → **Tema 3** (Trampa 5)
- [x] Incluir reglas de normalización de formato en el prompt junto con el schema strict → **Tema 3**

**Tarea 4.4 — Implement validation, retry, and feedback loops for extraction quality**

*Knowledge of*
- [x] Retry-with-error-feedback: agregar los errores de validación específicos al prompt del reintento → **Tema 5** (Trampa 7)
- [x] Los límites del reintento: no sirve si la información no está en el documento (a diferencia de los errores de formato o estructura) → **Tema 6** (Trampa 8)
- [x] Diseño del feedback loop: registrar qué construcciones de código disparan hallazgos (`detected_pattern`) para analizar los descartes → **Tema 7** (Trampa 10)
- [x] La diferencia entre errores semánticos (valores que no suman, campo equivocado) y errores de sintaxis (eliminados por tool use) → **Tema 4** (Trampa 6)

*Skills in*
- [x] Pedidos de corrección con el documento original, la extracción fallida y los errores específicos → **Tema 5** (Trampa 7)
- [x] Identificar cuándo un reintento no va a servir (dato en un documento externo no provisto) y cuándo sí (formato, estructura) → **Tema 6** (Trampa 8)
- [x] Agregar `detected_pattern` a los hallazgos para analizar patrones de falsos positivos cuando los devs los descartan → **Tema 7** (Trampa 10)
- [x] Flujos de autocorrección: `calculated_total` junto a `stated_total`, y `conflict_detected` para datos de origen inconsistentes → **Tema 7** (Trampa 9)

**Tarea 4.5 — Design efficient batch processing strategies**

*Knowledge of*
- [x] La Message Batches API: 50% de ahorro, hasta 24 horas, sin SLA de latencia → **Tema 8** (Trampa 11)
- [x] Batch para cargas no bloqueantes que toleran demora (reportes nocturnos, auditorías semanales, tests nocturnos), no para flujos bloqueantes (pre-merge) → **Tema 8** (Trampa 11)
- [x] La Batches API no admite tool calling de varios turnos dentro de un request → **Tema 8** (Trampa 12)
- [x] `custom_id` para correlacionar pedidos y respuestas → **Tema 8** (Trampas 11 y 13)

*Skills in*
- [x] Elegir la API según la latencia requerida: síncrona para pre-merge, batch para análisis nocturno o semanal → **Tema 8** (Trampa 11)
- [x] Calcular la frecuencia de envío según el SLA (ventanas de 4 h para un SLA de 30 h) → **Tema 9** (Trampa 14)
- [x] Manejar fallas: reenviar solo los documentos fallidos (por `custom_id`) con modificaciones (chunking) → **Tema 9** (Trampa 13)
- [x] Refinar el prompt con una muestra antes de procesar grandes volúmenes → **Tema 9**

**Tarea 4.6 — Design multi-instance and multi-pass review architectures**

*Knowledge of*
- [x] Límites de la auto-revisión: el modelo retiene el contexto de razonamiento de la generación → **Tema 10** (Trampa 15)
- [x] Las instancias de revisión independientes son más efectivas que la auto-revisión o el extended thinking → **Tema 10** (Trampa 15)
- [x] Multi-pass review: pasadas locales por archivo + pasadas de integración entre archivos, para evitar la dilución de la atención y los hallazgos contradictorios → **Tema 11** (Trampa 16)

*Skills in*
- [x] Usar una segunda instancia independiente para revisar código generado, sin el contexto del generador → **Tema 10** (Trampa 15)
- [x] Dividir las revisiones grandes en pasadas por archivo y pasadas de integración del flujo de datos → **Tema 11** (Trampa 16)
- [x] Pasadas de verificación donde el modelo reporta su confianza en cada hallazgo, para enrutar la revisión → **Tema 11**

**De la documentación, no de la guía** (vale saberlo; la guía no lo pregunta directo): structured outputs con `output_config.format` y las excepciones `refusal` y `max_tokens` (Tema 1) · `any` y `tool` con 400 en algunos modelos recientes (Tema 2) · 100.000 requests o 256 MB y 29 días (Tema 8).

**📘 Curso (útil para entender):** tope de 2 a 3 reintentos y escalar (Tema 5) · evaluación de prompts, regresiones y model-based grading (Tema 12).

---

## Autoevaluación oral

1. ¿Por qué tool use con JSON schema es más confiable que pedir JSON en el prompt? ¿Qué errores elimina y cuáles no? ¿Cuándo usás `any` y cuándo forzás una tool?
2. ¿Cuándo un campo tiene que ser nullable? ¿Para qué sirven `"other"` + detalle y `"unclear"`, y en qué se diferencian de `null`?
3. ¿Qué lleva un buen reintento? ¿En qué caso reintentar no sirve? ¿Para qué sirven `calculated_total`, `conflict_detected` y `detected_pattern`?
4. ¿Qué ofrece y qué no ofrece la Batches API? Contá la Q11. ¿Cada cuánto enviás con un SLA de 30 horas? ¿Qué hacés si fallan 40 de 1.000?
5. ¿Por qué una instancia independiente revisa mejor que la misma sesión? Contá la Q12 y sus distractores.

---

## Preguntas tipo examen

Las preguntas tipo examen de este capítulo están en [`04-practica/modulo-4.md`](../04-practica/modulo-4.md), junto con las del resto del módulo 4. Hacelas cuando termines **todos** los capítulos del módulo, de a una y sin mirar la respuesta.

---

## Revisión contra el blueprint oficial

Qué puede salir en el examen de 4.3 a 4.6 que el curso de Jacob **no cubre o cubre flojo**, y dónde quedó explicado:

1. **Enums con `"other"` + detalle y `"unclear"`**, y reglas de normalización junto al schema. → Tema 3.
2. **Cuándo un reintento no sirve** (dato ausente o en un documento externo). → Tema 6.
3. **`detected_pattern`, `calculated_total` / `stated_total` y `conflict_detected`.** → Tema 7.
4. **Frecuencia de envío según el SLA**, reenviar solo los fallidos por `custom_id` con chunking. → Tema 9.
5. **Pasada por archivo + pasada de integración (Q12)** y **confianza por hallazgo para enrutar**. → Tema 11.
6. **La auto-revisión como limitación** (el curso la presenta como opción barata) y que la instancia independiente no necesita ser un modelo más grande. → Tema 10.
7. **Datos del curso que no valen:** "JSON mode" (Tema 1), "temperature bump" en los reintentos (Tema 5) y, en el glosario, "10.000 requests por batch" (son 100.000; Tema 8).
8. **No hay preguntas de muestra de 4.3 y 4.4** en la guía: el escenario 6 se va a preguntar con los patrones de este capítulo.

No encontré otros huecos para 4.3 a 4.6.

