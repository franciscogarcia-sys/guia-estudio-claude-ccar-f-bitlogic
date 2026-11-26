# Capítulo 5 · 2A · Udemy 6 — Tool Design Fundamentals (diseño de tools)

*Tareas oficiales 2.1, 2.2 y 2.3 · Primer capítulo del módulo 2*

---

## Dónde estamos

Empieza el **módulo 2: Tool Design & MCP Integration** (18% del examen). Este capítulo cubre tres tareas, y cada una pesa 3,6% del examen:
- **2.1** Design effective tool interfaces with clear descriptions and boundaries (diseñar tools con descripciones claras y límites definidos).
- **2.2** Implement structured error responses for MCP tools (devolver errores estructurados desde las tools MCP).
- **2.3** Distribute tools appropriately across agents and configure tool choice (repartir bien las tools entre agentes y configurar `tool_choice`).

### Cómo leer este capítulo

Todo lo que leés acá **vale para el examen**, salvo que diga lo contrario. Cuando algo sale solo del curso (útil para entender, pero no central), lo marco con **📘 Curso**. Cuando Jacob dice algo distinto de lo que evalúa la guía, aparece un recuadro así:

> ⚠️ **En el curso vas a escuchar otra cosa.** … **Para el examen: …**

## De dónde venimos

Este capítulo usa tres ideas del módulo 1. En **1A** viste qué es una tool: una función de tu código que Claude puede pedir que se ejecute, definida con un `name`, una `description` y un `input_schema`. Viste que Claude elige cuál usar **leyendo su descripción**, porque no ve tu código, y que cuando una tool falla, el `tool_result` que vuelve lleva `is_error: true`. En **1C** viste que a cada subagent se le dan **solo** las tools que necesita (**least privilege**, mínimo privilegio) y el caso de la tool acotada `verify_fact`. En **1D** viste que hay errores transitorios y permanentes, y que solo vale la pena reintentar los transitorios.

Este capítulo baja todo eso a **cómo se diseña una tool**: cómo se describe, qué recibe, qué devuelve cuando falla y a qué agente se le da.

## Mapa del capítulo

**Parte 1 — Que Claude elija la tool correcta (tarea 2.1).** Cómo elige Claude, cómo se escribe una buena descripción, qué hacer cuando dos tools se pisan y cómo el system prompt puede arruinar todo.
1. Cómo elige Claude una tool.
2. Cómo se escribe una buena descripción.
3. Tools que se pisan: renombrar y dividir.
4. El system prompt también influye.

**Parte 2 — Que la llame bien (tarea 2.1, desde el curso y la documentación).** Qué parámetros recibe y cómo garantizar que lleguen bien.

5. Input schema: required, optional y enum.
6. Strict tool use: inputs garantizados.

**Parte 3 — Qué devuelve cuando falla (tarea 2.2).**

7. Errores estructurados: isError, errorCategory e isRetryable.
8. "No pude buscar" no es lo mismo que "no hay resultados".
9. Recuperar localmente y propagar lo que no se pudo resolver.

**Parte 4 — A quién se le da cada tool y cómo se fuerza su uso (tarea 2.3).**

10. Tool scoping: pocas tools por agente.
11. tool_choice: auto, any, tool y none.
12. Fallas de selección y cómo detectarlas.

---

# Parte 1 — Que Claude elija la tool correcta

## Tema 1 — How Claude selects tools (cómo elige Claude una tool)

### Qué es

Cuando Claude tiene varias tools disponibles, en cada turno decide si usa alguna y cuál. Para eso no mira tu código ni cómo está implementada la tool: solo ve su definición, y lo que más pesa de esa definición es la **descripción** (`description`). La guía la llama el **primary mechanism** (mecanismo principal) de selección, y la documentación dice que es, lejos, el factor que más influye en qué tan bien se usan las tools.

El **nombre** también ayuda, pero no decide. Un nombre son una o dos palabras; la descripción puede explicar para qué sirve la tool, cuándo usarla y cuándo no. Por eso, si el nombre dice una cosa y la descripción otra, Claude se guía por la descripción.

📘 **Curso:** una slide de "Exam Trap" avisa que en el examen los distractores presentan el **nombre** como mecanismo de **routing** (la decisión de a qué tool va cada pedido), y que la respuesta correcta apunta siempre a la descripción. El curso también nombra los cuatro resultados posibles cada vez que Claude elige, útiles como vocabulario para describir qué salió mal:
- **Correct call** (llamada correcta): elige la tool correcta.
- **Misroute** (ruteo equivocado): elige otra tool.
- **No call** (ninguna llamada): responde con texto en vez de usar una tool.
- **Fallback** (pedir aclaración): le pide al usuario que aclare, en vez de adivinar entre opciones poco claras.

### Ejemplo

SoporteBot, el agente de soporte de TiendaX, tiene dos tools:
- `get_customer`, con la descripción "Retrieves customer information".
- `lookup_order`, con la descripción "Retrieves order details".

Juan escribe: "Revisá mi pedido #12345". Claude lee las dos descripciones para decidir. Las dos son mínimas, ninguna dice qué identificadores acepta ni cuándo no usarla, y las dos aceptan identificadores parecidos. Claude termina llamando a `get_customer` en vez de `lookup_order`. Es un **misroute**, y la causa no es el modelo: son las descripciones, que no le dan cómo distinguir una tool de la otra.

### Para el examen

- La **descripción** es la señal principal para elegir. Una descripción **mínima** produce una elección poco confiable entre tools parecidas.
- Si una opción dice "renombrá la tool para que el modelo la elija", sospechá: el nombre ayuda, pero no es lo principal.

### Cómo se une

Es lo que viste en 1A: Claude no lee tu código, lee la descripción. Ahora vamos a ver cómo escribirla.

---

## Tema 2 — Writing tool descriptions (cómo se escribe una buena descripción)

### Qué es

Si la descripción es lo que Claude lee para elegir, tiene que darle todo lo necesario para decidir. Una descripción de una línea dice qué hace la tool, pero no cuándo usarla frente a otra parecida ni qué esperar de vuelta, y esos huecos Claude los llena adivinando. Según la guía, una buena descripción incluye:
- **qué hace** la tool;
- **input formats** (formatos de entrada que acepta);
- **example queries** (ejemplos de pedidos del usuario que la deberían disparar);
- **edge cases** (casos raros o límite);
- **boundaries** (límites): **cuándo usarla y cuándo NO**, comparada con tools parecidas;
- **qué devuelve**.

Los boundaries son los que separan dos tools parecidas: si cada descripción dice cuándo no usarla y qué tool usar en su lugar, Claude no tiene que adivinar. La documentación pide **al menos 3 o 4 oraciones** por descripción, y más si la tool es compleja.

📘 **Curso:** el curso nombra tres formas en que falla una descripción: **vague intent** (propósito vago: no queda claro para qué sirve), **missing scope** (alcance faltante: no dice cuándo no usarla) y **no output signal** (sin señal de salida: no dice qué devuelve).

### Ejemplo: mal y bien

**Mal:**
```json
{ "name": "lookup_order", "description": "Retrieves order details" }
```

**Bien:**
```json
{
  "name": "lookup_order",
  "description": "Returns the status, items, shipping carrier and delivery date of a TiendaX order. Use it when the customer asks about an order, a shipment, a delivery, or mentions an order number (format TX-NNNNNN or #NNNNN, e.g. 'where is my order #12345'). Requires a verified customer_id from get_customer. Do NOT use it for account data such as email, address or membership: use get_customer for that. If the order does not belong to the customer, it returns status 'not_found'."
}
```

La versión buena tiene qué hace, cuándo usarla (con ejemplos de pedidos y el formato del número), un prerrequisito, cuándo **no** usarla (y qué tool usar en ese caso) y qué devuelve en un caso límite. Con esta descripción, cuando Juan escribe "#12345", Claude reconoce el formato de número de pedido y va a `lookup_order`.

### La pregunta oficial de muestra

La guía trae una pregunta de muestra con exactamente el caso de Juan del Tema 1. Pide el **most effective first step** (primer paso más efectivo) para mejorar la selección. Un **few-shot** es un ejemplo resuelto que se pone en el prompt para mostrarle al modelo cómo responder; aparece como distractor:
- **✅ Expandir la descripción de cada tool** con formatos de entrada, ejemplos de pedidos, casos límite y límites frente a tools parecidas.
- ❌ **Agregar de 5 a 8 few-shot** al system prompt: suma tokens y no ataca la causa, que son las descripciones mínimas.
- ❌ **Una capa de routing** que lee el mensaje antes de cada turno y elige la tool por palabras clave: es sobreingeniería y se saltea la comprensión del lenguaje del modelo.
- ❌ **Consolidar las dos tools en una sola `lookup_entity`**: podría funcionar, pero es mucho más trabajo del que pide un "primer paso".

### Para el examen

- Si el problema es que Claude elige mal entre tools parecidas y las descripciones son mínimas, la respuesta es **mejorar las descripciones**.
- Fijate en "first step": la respuesta es lo más barato que ataca la causa.

### Cómo se une

La `description` de un **AgentDefinition** (1C) funciona igual: el coordinador elige a qué subagent delegar leyéndola. Las mismas reglas valen para los dos.

---

## Tema 3 — Tools que se pisan: renombrar y dividir

### Qué es

Una descripción puede estar bien escrita y fallar igual si otra tool dice casi lo mismo. Cuando dos tools tienen descripciones **ambiguas o superpuestas** (**overlapping**), Claude no tiene cómo saber cuál corresponde y se produce un **misrouting**: el pedido va a la tool que no era. La guía da dos soluciones, según de dónde venga la superposición.

**1. Rename (renombrar) y reescribir la descripción para eliminar la superposición.** Sirve cuando hay dos tools con propósitos distintos que están mal descriptos. Ejemplo de la guía: `analyze_content` y `analyze_document` tienen descripciones casi iguales. Se renombra `analyze_content` a **`extract_web_results`** y se le escribe una descripción específica para contenido web. Ahora cada una tiene un propósito distinto, y tanto el nombre como la descripción lo dicen.

**2. Split (dividir) una tool genérica en tools de propósito específico.** Sirve cuando el problema es una sola tool que hace demasiadas cosas. Una tool que "hace de todo" obliga a Claude a adivinar qué operación se pidió, y deja que un pedido inocente termine en una acción que no era. Ejemplo de la guía: una `analyze_document` genérica se divide en tres:
- `extract_data_points`: saca datos puntuales;
- `summarize_content`: resume;
- `verify_claim_against_source`: verifica una afirmación contra la fuente.

Cada una queda con un **contrato** claro, o sea, una definición precisa de qué recibe y qué devuelve.

### Ejemplo en TiendaX

SoporteBot tiene una tool `handle_order(order_id, what)` que "hace operaciones sobre pedidos". Un cliente pregunta por su pedido, Claude elige `handle_order` y, como el parámetro `what` es texto libre, a veces termina cancelando cuando el cliente solo quería consultar. Se divide en `get_order_status`, `cancel_order` y `change_shipping_address`, cada una con su descripción y sus límites. Ahora "¿dónde está mi pedido?" va a `get_order_status`, y no puede terminar en una cancelación.

> ⚠️ **En el curso vas a escuchar otra cosa.** El curso (p. 271–272) y la documentación de Anthropic sugieren **consolidar** operaciones relacionadas en una sola tool con un parámetro `action`; por ejemplo, juntar `create_pr`, `review_pr` y `merge_pr` en `github_pr(action=...)`. **Para el examen: seguí la guía**, que pide **dividir** las tools genéricas que generan ambigüedad y reemplazarlas por alternativas acotadas. Ante una tool genérica que causa confusión, dividila; ante dos tools superpuestas, renombralas y reescribí las descripciones. Ojo: consolidar no es siempre incorrecto. En la pregunta oficial del Tema 2 (`lookup_entity`) es un distractor porque se pide el **primer paso** y la causa son las descripciones mínimas: podría funcionar, pero es mucho más trabajo.

Otra práctica de la documentación que **no** choca con la guía es el **namespacing** (prefijo por sistema en el nombre), como `github_list_prs` o `slack_send_message`. Cuando un agente tiene tools de sistemas distintos, el prefijo deja claro a cuál pertenece cada una.

### Para el examen

- Descripciones superpuestas → **renombrar + reescribir** para que cada tool tenga un propósito distinto.
- Tool genérica ambigua → **dividirla** en tools específicas, con entradas y salidas claras.

### Cómo se une

Es la misma idea de las subtareas de 1B: **una sola responsabilidad**, con entradas y salidas definidas.

---

## Tema 4 — El system prompt también influye

### Qué es

La guía advierte algo que el curso no destaca: en la elección no influyen solo las descripciones, también la redacción del **system prompt** (las instrucciones generales que el agente recibe en cada llamada). El riesgo son las **keyword-sensitive instructions** (instrucciones que reaccionan a palabras clave), reglas del tipo "si aparece la palabra X, hacé Y". Una misma palabra aparece en contextos muy distintos, así que esas reglas crean asociaciones que no querías, y pueden **pisar** descripciones bien escritas.

### Ejemplo

El system prompt de SoporteBot dice: "Si el cliente menciona la palabra **cuenta**, usá `get_customer`". Martín escribe: "Me cobraron dos veces en la **cuenta** del pedido TX-104251". Claude ve la palabra "cuenta", aplica la regla y llama a `get_customer` en vez de `lookup_order`, aunque la descripción de `lookup_order` es perfecta y el mensaje habla de un pedido.

**Solución:** revisar el system prompt y sacar o reescribir las instrucciones atadas a palabras sueltas, para que la elección de la tool se apoye en las descripciones.

> ⚠️ **En el curso vas a escuchar otra cosa.** El curso sugiere agregar al system prompt **reglas de routing** y **tie-breakers** (desempates) para elegir entre tools parecidas. **Para el examen:** la guía advierte que esas instrucciones pueden pisar las descripciones. Primero se arreglan las descripciones; si el misrouting sigue, se **revisa el system prompt** buscando palabras clave que sesgan la elección.

### Para el examen

- "Las descripciones están bien, pero Claude elige mal cuando aparece cierta palabra" → **revisar el system prompt** buscando instrucciones atadas a palabras clave.

### Cómo se une

Es otro caso de "el prompt no es tan confiable como parece" (1D), pero al revés: acá el prompt **empeora** algo que estaba bien.

---

# Parte 2 — Que la llame bien

## Tema 5 — Input schema: required, optional y enum

### Qué es

Una vez que Claude eligió la tool, tiene que llamarla con los parámetros correctos. Los parámetros se definen en el **`input_schema`**, que es un **JSON Schema**: un formato estándar para describir la forma de un objeto JSON, o sea, qué campos tiene, de qué tipo es cada uno y cuáles son obligatorios. Claude lee ese schema para saber qué mandar. (En MCP el campo se llama **`inputSchema`**, en camelCase; lo vemos en 2B.)

📘 **Curso:** el curso agrega tres reglas prácticas para que los parámetros lleguen bien.

**1. La descripción de cada parámetro es un micro-prompt.** No alcanza con el tipo: hay que decir para qué es, qué valores son válidos y qué pasa en casos raros. Sin eso, el tipo puede ser correcto y el valor igual estar mal (un `string` con "pedido 12345" en vez de "TX-104233").

**2. Required solo lo indispensable.** Si marcás como **required** (obligatorio) algo que Claude no siempre sabe, lo va a **inventar** para cumplir con el schema. Los parámetros **optional** (opcionales) llevan un valor por defecto o la tool se arregla sin ellos.

**3. `enum` para valores fijos.** Si un parámetro tiene pocos valores posibles, se listan con **`enum`** (lista cerrada). Así se evitan variantes como "urgent", "URGENT" o "high-priority", que tu código tendría que interpretar. Funciona mejor con 2 a 10 valores estables.

La documentación también permite **`input_examples`**: ejemplos de inputs válidos que le muestran a Claude cómo llamar la tool. Cada ejemplo tiene que cumplir el schema, o el request se rechaza.

### Ejemplo

```json
{
  "name": "create_return_label",
  "description": "Creates a prepaid return shipping label for an eligible TiendaX order...",
  "input_schema": {
    "type": "object",
    "properties": {
      "order_id": {
        "type": "string",
        "description": "TiendaX order number, format TX-NNNNNN (e.g. TX-104233)."
      },
      "reason": {
        "type": "string",
        "enum": ["damaged", "wrong_item", "wrong_size", "changed_mind"],
        "description": "Main reason for the return, as stated by the customer."
      },
      "notes": {
        "type": "string",
        "description": "Optional free-text details from the customer. Omit if none."
      }
    },
    "required": ["order_id", "reason"]
  }
}
```

- `order_id` y `reason` son required: sin ellos no se puede crear la etiqueta.
- `reason` es un `enum`: no puede llegar "roto", "Damaged" o "se rompió".
- `notes` es opcional: si el cliente no dijo nada, Claude no tiene que inventar un texto.

### Para el examen

- Required mínimo, `enum` para valores fijos y descripciones claras por parámetro.
- Si Claude **inventa** valores en un parámetro, revisá si está marcado como required sin necesidad.

### Cómo se une

Es la validación de **schema** de 1D (Tema 2), pero **antes** de la llamada, en el diseño de la tool.

---

## Tema 6 — Strict tool use (uso estricto de tools): inputs garantizados

### Qué es

Un buen schema hace que Claude **casi siempre** mande inputs válidos, pero no lo garantiza: el modelo genera texto, y podría mandar un tipo equivocado o saltearse un campo. Si en la definición de la tool ponés **`"strict": true`**, eso deja de ser posible: Claude **solo puede generar** inputs que cumplan el `input_schema`. La documentación garantiza que:
- el input sigue estrictamente el schema (tipos correctos, campos required presentes);
- el nombre de la tool siempre es válido.

Funciona con **grammar-constrained sampling** (generación restringida por gramática): mientras Claude escribe el input, solo se le permite generar lo que mantiene el JSON dentro del schema, así que directamente no puede producir algo fuera de él. Los ejemplos de la documentación usan `"additionalProperties": false` en cada objeto, que prohíbe campos que no estén en el schema.

**Lo que NO garantiza** es que Claude **llame** a una tool. Strict controla cómo es el input cuando la llama; si Claude decide responder con texto, strict no interviene. Eso se controla con `tool_choice` (Tema 11).

Dos detalles más, en los que coinciden la documentación y el curso:
- Strict y **Structured Outputs** (salidas estructuradas) usan el mismo mecanismo de gramática. Strict restringe los **inputs de una tool**; Structured Outputs restringe la **respuesta final**. (Structured Outputs lo vemos en 4C.)
- Algunas restricciones de JSON Schema, como `minimum`, `maximum`, `minLength` y `maxLength`, **no** las garantiza la gramática: el SDK las saca del schema. Hay que validarlas en tu código.

### Ejemplo

```json
{
  "name": "create_return_label",
  "strict": true,
  "description": "...",
  "input_schema": {
    "type": "object",
    "properties": { "order_id": {"type": "string"}, "reason": {"type": "string", "enum": ["damaged", "wrong_item", "wrong_size", "changed_mind"]} },
    "required": ["order_id", "reason"],
    "additionalProperties": false
  }
}
```

Con `strict: true`, es imposible que llegue `reason: "roto"` o que falte `order_id`.

### Para el examen

- `strict: true` = **inputs válidos garantizados**. No obliga a llamar la tool.
- Para "llamar una tool **y** con inputs válidos", se combina `strict: true` con un parámetro que obliga a llamar, `tool_choice`, que vemos en el Tema 11.

### Cómo se une

Es el mismo principio de 1D: si algo tiene que cumplirse **siempre**, se garantiza con un mecanismo, no se pide en el prompt.

---

# Parte 3 — Qué devuelve cuando falla

## Tema 7 — Structured errors (errores estructurados): isError, errorCategory e isRetryable

### Qué es

Cuando una tool falla, el agente tiene que decidir qué hacer: reintentar, corregir el input, explicarle algo al cliente o seguir por otro camino. Para decidir bien necesita saber **qué tipo** de falla fue. Un error genérico, como "Operation failed", es igual para un timeout que para un reembolso fuera de plazo, así que el agente no tiene con qué decidir. La guía pide que el error lleve cuatro cosas.

**1. El flag de error.** Primero hay que marcar que el resultado es un error y no una respuesta normal. Es el mismo concepto en dos capas, escrito distinto:
- En **MCP**, el resultado de la tool lleva **`isError: true`** (el **isError flag pattern**).
- En la **API de Claude**, el bloque `tool_result` lleva **`is_error: true`** (lo viste en 1A).

**2. La categoría (`errorCategory`).** La guía usa cuatro valores, y cada uno pide una reacción distinta del agente:

| errorCategory | Qué significa | Ejemplo en TiendaX | ¿Se reintenta? |
|---|---|---|---|
| **transient** (transitorio) | falla temporal | timeout, servicio no disponible | Sí |
| **validation** (validación) | input inválido | número de pedido con formato incorrecto | No: corregir el input |
| **business** (negocio) | viola una regla de negocio | reembolso fuera de los 30 días | No: explicarle al cliente |
| **permission** (permiso) | sin autorización | el agente de soporte intenta ver datos de pago completos que solo puede ver Finanzas | No |

**3. `isRetryable`** (¿se puede reintentar?). Es un booleano que le dice al agente si vale la pena reintentar, para que no gaste intentos en algo que va a fallar igual. La guía también lo escribe como `retriable: false`: es lo mismo.

**4. Una descripción legible para personas.** En los errores de **negocio**, además, una **explicación apta para el cliente**, para que el agente le pueda decir la verdad en vez de inventar una excusa.

### Ejemplo: mal y bien

María pide el reembolso de unas zapatillas que compró hace 45 días. La política acepta hasta 30.

**Mal:**
```json
{ "isError": true, "content": [{"type": "text", "text": "Operation failed"}] }
```
SoporteBot no sabe si reintentar, corregir algo o explicar. Reintenta cinco veces y le dice a María "estamos con problemas técnicos". Es mentira.

**Bien:**
```json
{
  "isError": true,
  "content": [{
    "type": "text",
    "text": "{\"errorCategory\": \"business\", \"isRetryable\": false, \"message\": \"Refund window exceeded: delivered 45 days ago, policy allows 30.\", \"customerMessage\": \"Tu compra superó el plazo de 30 días para reembolsos. Podemos ofrecerte un cambio por otro talle.\"}"
  }]
}
```
SoporteBot lee `isRetryable: false` y no reintenta. Lee la categoría `business` y entiende que no es una falla técnica. Le explica a María el motivo real con el `customerMessage` y le ofrece el cambio de talle.

**Dónde va esa información.** Ni MCP ni la API de Claude tienen campos propios para `errorCategory` o `isRetryable`: son la convención que pide la guía, y viajan **dentro del contenido** del resultado.
- **En MCP**, el resultado de una tool tiene `content` (bloques de texto), opcionalmente `structuredContent` (un objeto JSON) e `isError`. Si usás `structuredContent`, la especificación pide mandarlo también serializado en un bloque de texto.
- **En la API de Claude**, el bloque `tool_result` tiene `type`, `tool_use_id`, `content` e `is_error`. 📘 **Curso:** lo resume así: el detalle del error va dentro de `content`.

### Errores de protocolo vs. errores de ejecución (MCP)

La especificación de MCP separa dos tipos de error, y la diferencia importa porque solo uno de los dos lo puede aprovechar el modelo.

Los **protocol errors** (errores de protocolo) aparecen cuando la tool no existe o el pedido está mal formado. Son errores **JSON-RPC** (el formato de mensajes que usa MCP), con un código como `-32602` ("Invalid params", parámetros inválidos). El modelo casi nunca puede arreglarlos solo, porque el problema está en el código o en la configuración, y ahí se corrigen.

Los **tool execution errors** (errores de ejecución) aparecen cuando la tool corrió y falló, por ejemplo por una API caída, un input inválido o una regla de negocio. Van en el resultado con `isError: true`, y **el modelo sí puede usarlos para corregirse** y volver a intentar con otros parámetros.

> ⚠️ **En el curso vas a escuchar otra cosa.** El curso arma el error con cuatro campos (`code`, `message`, `context`, `suggested_action`) y separa errores de **usuario** y de **sistema**. **Para el examen: usá el vocabulario de la guía**, que es `isError`, **`errorCategory`** con 4 valores e **`isRetryable`**. Equivalencia aproximada: el "error de usuario" del curso corresponde a validation, business o permission (no reintentable); el "error de sistema transitorio", a transient (reintentable).

### Para el examen

- Errores **uniformes** ("Operation failed") impiden que el agente decida bien cómo recuperarse.
- Error estructurado = **`isError` + `errorCategory` + `isRetryable` + mensaje legible**.
- Errores de negocio: **`isRetryable: false` + explicación para el cliente**.

### Cómo se une

Es el **structured error context** de 1C y la clasificación transitorio/permanente de 1D, ahora con los nombres exactos que usa la guía.

---

## Tema 8 — Access failure vs. valid empty result (no pude buscar ≠ no hay resultados)

### Qué es

La guía pide distinguir dos situaciones que, mal devueltas, se ven iguales. Una **access failure** (falla de acceso) es cuando la búsqueda **no se pudo hacer**: timeout, falta de permiso, servicio caído. Ahí hay que decidir si reintentar. Un **valid empty result** (resultado vacío válido) es cuando la búsqueda **se hizo bien** y no encontró nada; es una respuesta correcta y no hay nada que reintentar.

El peligro es devolver una falla de acceso como una lista vacía marcada como éxito. El agente lee "no hay nada" cuando en realidad la tool "no pudo mirar", y le afirma al usuario algo que nadie verificó.

### Ejemplo

Rosa pregunta si tiene pedidos pendientes.

**Caso A.** `search_orders` corre bien y no encuentra pedidos pendientes. Devuelve `{"orders": []}` sin error, y SoporteBot responde: "No tenés pedidos pendientes". Es correcto.

**Caso B.** La base de pedidos hace timeout.
- **Mal:** la tool devuelve `{"orders": []}` como éxito. SoporteBot le dice a Rosa que no tiene pedidos, y eso es falso: nadie llegó a mirar.
- **Bien:** la tool devuelve `isError: true` con `errorCategory: "transient"` e `isRetryable: true`. SoporteBot reintenta, y si sigue fallando le dice a Rosa que no pudo consultar.

### Para el examen

- "Devolver una lista vacía marcada como exitosa ante un timeout" es un distractor clásico (aparece en una pregunta de muestra oficial).
- Vacío válido = éxito sin datos. Falla de acceso = error, con su categoría.

### Cómo se une

Es la **silent failure** de 1D (Tema 2): una salida que parece exitosa pero esconde una falla.

---

## Tema 9 — Recuperar localmente y propagar lo que no se pudo resolver

### Qué es

En un sistema multi-agente hay un **coordinador** que reparte el trabajo entre **subagents** (1C). Cuando un subagent se topa con una falla, la pregunta es quién la resuelve. La guía pide que cada **subagent resuelva localmente las fallas transitorias** (por ejemplo, con un reintento) y que **propague al coordinador solo lo que no pudo resolver**, junto con:
- los **partial results** (resultados parciales);
- **qué intentó**;
- **potential alternative approaches** (alternativas posibles).

La razón es doble. El coordinador no se llena de errores que el subagent podía resolver solo, y cuando le llega uno, trae lo necesario para decidir: qué se consiguió, qué ya se probó y qué otra cosa se podría intentar.

### Ejemplo

El subagent de search busca las políticas de devolución de 5 tiendas.
1. La tienda 2 da timeout una vez. El subagent **reintenta**, funciona, y el coordinador ni se entera.
2. La tienda 4 da timeout tres veces seguidas. El subagent ya no lo puede resolver, así que **propaga**:
   `{"errorCategory": "transient", "isRetryable": true, "attempted": "3 intentos a tiendaD.com/devoluciones", "partial_results": [4 tiendas OK], "alternatives": ["buscar la política en el sitio de defensa del consumidor"]}`.
3. Con eso, el coordinador decide: sigue con 4 tiendas y marca el hueco, o prueba la otra fuente.

📘 **Curso:** el curso suma tres patrones que no aparecen en la guía ni en la documentación oficial consultada; son buenas prácticas, no la respuesta oficial:
- **Idempotency key** (clave de idempotencia): una clave que manda el cliente para que, si una operación se reintenta, no se ejecute dos veces (por ejemplo, que un reembolso no salga doble).
- **`partial_success`** (éxito parcial): en operaciones por lote, devolver una lista de lo que salió bien (`succeeded`) y otra de lo que falló (`failed`), en vez de un error genérico.
- **Circuit breaker** (cortacircuitos): después de muchas fallas seguidas, se dejan de mandar pedidos a un servicio por un tiempo y se usa una alternativa.

### Para el examen

- Los subagents resuelven lo transitorio **localmente** y propagan **solo lo que no pudieron resolver**, con resultados parciales y lo que intentaron.

### Cómo se une

Completa 1C (Tema 8): allá el coordinador recibía un error estructurado. Acá se ve **quién** lo resuelve y **cuándo** se sube.

---

# Parte 4 — A quién se le da cada tool y cómo se fuerza su uso

## Tema 10 — Tool scoping (alcance de tools): pocas tools por agente

### Qué es

Darle a un agente todas las tools disponibles parece cómodo, pero empeora sus decisiones. Cada tool es una opción más que Claude tiene que considerar en cada turno, y cuantas más opciones parecidas hay, más fácil es elegir mal. La guía lo dice así: **demasiadas tools** degradan la confiabilidad de la elección, porque complican la decisión. Su ejemplo: **18 tools en vez de 4 o 5**.

Hay un segundo problema: un agente que tiene tools **fuera de su especialidad** tiende a usarlas mal. Ejemplo de la guía: un agente de **síntesis** (el que arma la respuesta con lo que encontraron otros) que se pone a hacer búsquedas web por su cuenta.

De ahí salen cuatro reglas de la guía:
1. **Scoped tool access** (acceso acotado): cada agente tiene solo las tools de su rol.
2. **Restringir el set de tools** de cada subagent a lo relevante para su rol.
3. **Reemplazar tools genéricas por alternativas acotadas.** Ejemplo de la guía: cambiar `fetch_url` (que baja cualquier URL) por **`load_document`**, que **valida** que la URL sea de un documento permitido. La validación queda en la tool, y no depende de que el modelo obedezca.
4. **Cross-role tools acotadas** (tools que cruzan de rol) para necesidades **frecuentes**. Es el caso de `verify_fact` para synthesis (1C, Tema 7): una tool chica para lo que se repite mucho, mientras lo complejo sigue pasando por el coordinador.

📘 **Curso:** el curso agrega tres ideas. **Tool bloat** (exceso de tools): cada tool consume tokens **en cada turno**, aunque no se use. **"Default to removal, not addition"**: antes de agregar una tool, ver si alcanza con mejorar la descripción de una existente. Y el coordinador no debería tener las tools de dominio de sus subagents; algunas, como las de logging o de estado, son compartidas a propósito.

### Ejemplo

SoporteBot tenía las 18 tools de TiendaX: pedidos, pagos, logística, catálogo, marketing, informes… Elegía mal seguido. Se reparte así:
- **coordinador:** `get_customer` y Task (para delegar);
- **subagent de pedidos:** `lookup_order`, `get_order_status`, `cancel_order`, `change_shipping_address`;
- **subagent de reembolsos:** `get_payment`, `process_refund`, `escalate_to_human`;
- **subagent de logística:** `get_shipment`, `create_return_label`.

Cada uno tiene 2 a 4 tools, así que cada decisión es entre pocas opciones de su tema. Y el de reembolsos no puede cancelar pedidos, porque esa tool no existe para él.

### Para el examen

- Muchas tools en un agente → **reducir y repartir** por rol (4 o 5 por agente).
- Agente que usa mal una tool de otra especialidad → **sacársela**.
- Tool genérica peligrosa (`fetch_url`) → **reemplazarla por una acotada** (`load_document`).
- Necesidad frecuente de otro rol → **una tool acotada** para eso, no todas las tools del otro rol.

### Cómo se une

Es el **least privilege** de 1C (Tema 3), ahora visto como un problema de **calidad de elección**, no solo de seguridad.

---

## Tema 11 — tool_choice: auto, any, tool y none

### Qué es

Hasta acá, Claude decidía solo si usar una tool. A veces necesitás garantizar que la use, o que use una en particular. Para eso está **`tool_choice`**, un parámetro de la llamada a la API que controla **si Claude tiene que usar una tool, y cuál**. Tiene cuatro valores:

| Valor | Qué hace | Cuándo se usa |
|---|---|---|
| `{"type": "auto"}` | Claude decide si usa una tool o responde con texto. Es el **default** cuando hay tools. | El caso normal, en un agentic loop. |
| `{"type": "any"}` | Claude **tiene que** usar **alguna** tool, la que elija. | Garantizar que llame una tool y no responda con texto. |
| `{"type": "tool", "name": "..."}` | Claude **tiene que** usar **esa** tool (**forced**, forzada). | Garantizar que una tool específica vaya **primero**. |
| `{"type": "none"}` | Claude **no puede** usar tools. Es el default cuando no hay tools. | Un turno solo de texto, aunque haya tools definidas. |

El **agentic loop** es el ciclo de 1A: Claude pide una tool, tu código la ejecuta y le devuelve el resultado, y así hasta que Claude responde con texto. La guía nombra tres valores: **auto**, **any** y **forced** (`tool`). `none` está en la documentación, pero no en la guía.

### Ejemplos de la guía

**1. Forzar una tool primero.** Para procesar un documento de proveedor, antes de enriquecer los datos hay que extraer los metadatos. Si se lo pedís en el prompt, Claude podría saltear ese paso. Por eso se fuerza `{"type": "tool", "name": "extract_metadata"}` en la **primera** llamada, y en los **turnos siguientes** se vuelve a `auto`, para que Claude use las tools de enriquecimiento que necesite.

**2. Garantizar una tool en vez de texto.** En una extracción de facturas, Claude a veces responde en texto "Esta factura parece de USD 1.200" en vez de llamar a `save_invoice_data`, y ese dato no llega a tu sistema. Con `{"type": "any"}` tiene que llamar a alguna tool. Si hay varias tools de extracción y no sabés cuál aplica, `any` le deja elegir.

### Cómo se configura: el patrón de dos turnos

```python
# Turno 1: forzar la extracción de metadatos
resp = client.messages.create(
    model=MODEL, max_tokens=1024, tools=tools, messages=messages,
    tool_choice={"type": "tool", "name": "extract_metadata"},   # SOLO esta tool
)
# ... ejecutar extract_metadata y agregar el tool_result al historial ...

# Turnos siguientes: Claude decide qué tools de enriquecimiento usar
resp = client.messages.create(
    model=MODEL, max_tokens=1024, tools=tools, messages=messages,
    tool_choice={"type": "auto"},
)
```

### Detalles que pueden aparecer

Estos detalles salen de la documentación y suelen aparecer como opciones que mezclan nombres o lugares:
- Con `any` o `tool`, la respuesta empieza **directamente** con el `tool_use`, sin texto antes.
- **`disable_parallel_tool_use: true`** (desactivar llamadas en paralelo) va **adentro** de `tool_choice`, no como parámetro aparte: `{"type": "auto", "disable_parallel_tool_use": true}`. Con `auto`, Claude llama **como mucho una** tool por respuesta; con `any` o `tool`, **exactamente una**.
- `any` y `tool` no funcionan con **extended thinking** (razonamiento extendido, cuando Claude razona antes de responder) en modo manual: dan error.
- Cambiar `tool_choice` invalida la parte de los mensajes guardada en caché (**prompt caching**, caché de prompts, que vemos en 5A).
- Para "llamar una tool **y** con inputs válidos": `any` + `strict: true` (Tema 6).

> ⚠️ **En la documentación actual vas a leer otra cosa.** La documentación dice que en **Claude Fable 5.2, Mythos 5.2, Opus 5.5, Sonnet 5.5, Fable 5.1 y Mythos 5.1**, `any` y `tool` devuelven **error 400**; en esos modelos se usa `auto` con strict tool use o structured outputs, y `none` sigue funcionando. **Para el examen: respondé según la guía**, que igual evalúa el concepto auto/any/forced: `any` para garantizar que llame alguna tool, forced para que una tool específica vaya primero y `auto` en un agentic loop normal. Elegí "auto + strict" solo si la pregunta menciona explícitamente esos modelos.

### Para el examen

- `any` = **alguna** tool. `tool` (forced) = **esa** tool. No los confundas.
- Para un paso obligatorio al principio: forced en el primer turno, y después los turnos siguientes con `auto`.
- En un agentic loop normal, `auto`. Forzar en todos los turnos haría que el loop nunca termine con texto.

### Cómo se une

En 1A, el loop terminaba cuando Claude respondía con `end_turn` en vez de pedir tools. Con `tool_choice` controlás **si** puede responder con texto o **tiene** que actuar.

---

## Tema 12 — Selection failures (fallas de selección) y cómo detectarlas

### Qué es

📘 **Curso:** este tema viene del curso; la guía no lo nombra así, pero ayuda a razonar las preguntas de misrouting.

El curso describe dos fallas típicas al elegir. En la primera, **no good match** (ninguna encaja), ninguna descripción cubre el pedido, así que Claude usa una tool genérica o responde con texto. En la segunda, **two good matches** (dos encajan), dos descripciones cubren el pedido y Claude elige casi al azar. Las dos se corrigen sobre todo con **verbos distintos** en cada descripción y **alcances estrechos**, para que cada pedido encaje en una sola tool.

Para detectar estos problemas antes de que lleguen a los clientes, el curso propone dos herramientas:
- **Tests de routing**, de tres tipos: **positivos** (este pedido tiene que ir a esta tool), **negativos** (este pedido **no** tiene que ir a esta tool) y **de desambiguación** (entre estas dos parecidas, va a esta). Para correrlos se usa `tool_choice: any`, así Claude siempre elige una tool, y se verifica cuál eligió.
- **Selection drift** (deriva de la selección): registrar cada elección y medir con qué frecuencia se usa cada tool. Si una cae por debajo de lo normal, alertar: puede que una descripción nueva le esté "robando" pedidos.

El curso también recuerda que lo que devuelve una tool **no es confiable**: puede traer texto que intenta manipular al modelo (**indirect prompt injection**, inyección indirecta de prompt). Por eso ese contenido se queda en el `tool_result` y nunca se copia al system prompt, donde tendría peso de instrucción.

### Ejemplo

Después de agregar `get_shipment`, el uso de `lookup_order` cae 40%. Al revisar, la descripción de `get_shipment` dice "Returns information about an order's delivery", que se superpone con `lookup_order`: los pedidos sobre "mi pedido" ahora encajan en las dos. Se reescribe: "Returns carrier tracking events for a shipment ID. Do NOT use for order status: use lookup_order". El uso de `lookup_order` vuelve a lo normal.

### Para el examen

- Misrouting entre dos tools → descripciones con **propósitos distintos** y límites explícitos (Temas 2 y 3).
- Esto es del curso. En el examen va a aparecer con el vocabulario de la guía: **overlapping descriptions** (descripciones superpuestas), **misrouting**.

### Cómo se une

Cierra la Parte 1: escribir buenas descripciones es la prevención, y medir la selección es la detección.

---

## Cómo se une todo

Claude elige tools **leyendo la descripción**, no el nombre (Tema 1). Por eso una buena descripción dice qué hace la tool, con qué entradas, ejemplos de pedidos, casos límite, **cuándo no usarla** y qué devuelve (Tema 2). Si dos tools se pisan, se **renombran y se reescriben**; si una es genérica y ambigua, se **divide**, y en el examen se divide aunque la documentación sugiera consolidar (Tema 3). Además, un **system prompt** con reglas atadas a palabras clave puede pisar buenas descripciones (Tema 4).

Una vez elegida, la tool tiene que recibir bien sus parámetros. El **input schema** los define: required mínimo, `enum` para valores fijos (Tema 5), y **`strict: true`** garantiza que los inputs cumplan el schema (Tema 6). Cuando falla, la tool devuelve **`isError` + `errorCategory` + `isRetryable` + mensaje**, nunca "Operation failed" (Tema 7). "No pude buscar" se devuelve como error, distinto de "no hay resultados" (Tema 8), y los subagents **resuelven localmente** lo transitorio y **propagan** lo demás con resultados parciales, lo intentado y alternativas (Tema 9).

Por último, cada agente tiene **pocas tools, las de su rol**, más alguna **acotada** para necesidades frecuentes (Tema 10). **`tool_choice`** decide si Claude puede responder con texto (`auto`), tiene que usar alguna tool (`any`) o una específica (`tool`) (Tema 11). Y el curso agrega cómo **detectar** fallas de selección (Tema 12).

## Lo que viene

Hasta acá las tools eran funciones de tu código. En 2B vas a ver **MCP** (Model Context Protocol): la forma estándar de publicar tools para que las use Claude Code o cualquier agente. Ahí aparece de nuevo `isError`, junto con `inputSchema` y otras dos cosas que un servidor MCP puede ofrecer además de tools.

---

## Las trampas del examen

Cada trampa tiene el mismo orden: la situación, **qué elegir en el examen (✅)**, las opciones que tientan (❌) con por qué tientan y por qué están mal, y una regla para recordar.

### Grupo: Que Claude elija la tool correcta (tarea 2.1)

#### Trampa 1 · Claude elige la tool equivocada entre dos parecidas

**La situación.** `get_customer` y `lookup_order` tienen descripciones de una línea y Claude las confunde (Temas 1 y 2).

**✅ En el examen elegí:** **expandir las descripciones** con formatos de entrada, ejemplos de pedidos, casos límite y cuándo usar cada una frente a la otra.

**❌ Las que tientan:**

❌ **"Agregar few-shot al system prompt con ejemplos de ruteo correcto".**
- *Tienta porque:* los ejemplos mejoran mucho el comportamiento.
- *Está mal porque:* suma tokens en cada llamada y no ataca la causa: las descripciones siguen siendo mínimas.

❌ **"Una capa de routing por palabras clave antes de cada turno".**
- *Tienta porque:* parece determinístico.
- *Está mal porque:* es sobreingeniería y se saltea la comprensión del lenguaje del modelo.

❌ **"Consolidar las dos en una `lookup_entity`".**
- *Tienta porque:* elimina la elección.
- *Está mal porque:* según la guía podría funcionar, pero es mucho más trabajo del que pide un "primer paso", y no ataca la causa (descripciones mínimas).

❌ **"Renombrarlas con nombres más claros".**
- *Tienta porque:* el nombre parece importante.
- *Está mal porque:* lo que pesa es la descripción. Renombrar sin reescribir no alcanza.

> 🧠 **Para recordar:** si Claude elige mal, primero mirá las descripciones.

#### Trampa 2 · Una tool genérica que hace de todo

**La situación.** `analyze_document` hace extracción, resúmenes y verificación, y Claude la usa mal (Tema 3).

**✅ En el examen elegí:** **dividirla** en tools de propósito específico (`extract_data_points`, `summarize_content`, `verify_claim_against_source`), cada una con entradas y salidas claras.

**❌ Las que tientan:**

❌ **"Agregarle un parámetro `action` con un enum de operaciones".**
- *Tienta porque:* la documentación de Anthropic y el curso lo sugieren.
- *Está mal porque:* la guía del examen pide **dividir** las tools genéricas ambiguas. En el examen manda la guía.

❌ **"Explicar mejor en el system prompt cuándo usar cada modo".**
- *Tienta porque:* no toca las tools.
- *Está mal porque:* sigue habiendo una tool ambigua, y las reglas en el prompt pueden pisar las descripciones.

> 🧠 **Para recordar:** tool genérica ambigua → dividir en tools específicas.

#### Trampa 3 · Las descripciones están bien, pero falla con cierta palabra

**La situación.** Cuando el cliente dice "cuenta", Claude llama a `get_customer` aunque hable de un pedido (Tema 4).

**✅ En el examen elegí:** **revisar el system prompt** buscando instrucciones atadas a palabras clave que pisan las descripciones.

**❌ Las que tientan:**

❌ **"Seguir mejorando la descripción de `lookup_order`".**
- *Tienta porque:* las descripciones son lo principal.
- *Está mal porque:* la descripción ya está bien. La regla del prompt la está pisando.

❌ **"Agregar más reglas de routing al system prompt para desempatar".**
- *Tienta porque:* el curso lo sugiere.
- *Está mal porque:* suma más instrucciones del mismo tipo que causan el problema.

> 🧠 **Para recordar:** si el error aparece con una palabra, buscá esa palabra en el system prompt.

### Grupo: Qué devuelve cuando falla (tarea 2.2)

#### Trampa 4 · El error genérico

**La situación.** `process_refund` devuelve "Operation failed" para todo, y SoporteBot reintenta un reembolso fuera de plazo cinco veces (Tema 7).

**✅ En el examen elegí:** devolver un **error estructurado**: `isError: true`, `errorCategory` (`business`), `isRetryable: false` y un mensaje claro, con una explicación apta para el cliente.

**❌ Las que tientan:**

❌ **"Limitar los reintentos a 2".**
- *Tienta porque:* reduce el desperdicio.
- *Está mal porque:* sigue reintentando lo que nunca va a funcionar, y el cliente sigue sin saber la verdad.

❌ **"Devolver un código HTTP distinto para cada caso".**
- *Tienta porque:* parece estructurado.
- *Está mal porque:* sin categoría, sin `isRetryable` y sin mensaje, el agente sigue sin saber qué hacer.

> 🧠 **Para recordar:** el error tiene que decir qué tipo es, si se reintenta y qué decirle al cliente.

#### Trampa 5 · Vacío no es lo mismo que falla

**La situación.** La búsqueda de pedidos hace timeout y la tool devuelve una lista vacía marcada como éxito (Tema 8).

**✅ En el examen elegí:** devolver la falla como **error** (`isError: true`, `transient`, `isRetryable: true`), separada de un resultado vacío válido.

**❌ Las que tientan:**

❌ **"Devolver vacío, que el agente igual le avisa al cliente que no hay pedidos".**
- *Tienta porque:* el flujo sigue sin cortarse.
- *Está mal porque:* el agente afirma algo falso: que no hay pedidos.

❌ **"Cortar todo el flujo con una excepción".**
- *Tienta porque:* parece lo más seguro.
- *Está mal porque:* el error era recuperable.

❌ **"Reintentar con backoff y, si sigue fallando, devolver 'search unavailable'".**
- *Tienta porque:* reintenta, que es correcto para lo transitorio.
- *Está mal porque:* el estado genérico final esconde lo que el coordinador necesita: tipo de falla, consulta intentada, resultados parciales y alternativas.

> 🧠 **Para recordar:** "no pude buscar" se informa como error, con contexto; "no encontré nada" es un éxito vacío.

### Grupo: A quién se le da cada tool y cómo se fuerza su uso (tarea 2.3)

#### Trampa 6 · Demasiadas tools

**La situación.** SoporteBot tiene 18 tools y elige mal seguido (Tema 10).

**✅ En el examen elegí:** **reducir y repartir** las tools por rol: 4 o 5 por agente, cada uno con lo de su especialidad.

**❌ Las que tientan:**

❌ **"Mejorar las 18 descripciones".**
- *Tienta porque:* las descripciones son lo principal.
- *Está mal porque:* el problema es la **cantidad**: hay demasiadas opciones para decidir bien.

❌ **"Usar un modelo más grande".**
- *Tienta porque:* "razona mejor".
- *Está mal porque:* no ataca la complejidad de la decisión.

> 🧠 **Para recordar:** con muchas tools, el problema es la cantidad, no la descripción.

#### Trampa 7 · Un agente que usa tools de otro rol

**La situación.** El agente de síntesis hace búsquedas web por su cuenta y trae fuentes de baja calidad (Tema 10).

**✅ En el examen elegí:** **sacarle** las tools que no son de su rol. Si tiene una necesidad frecuente, darle una **tool acotada** para eso (como `verify_fact`).

**❌ Las que tientan:**

❌ **"Decirle en el prompt que no busque en la web".**
- *Tienta porque:* es rápido.
- *Está mal porque:* es probabilístico. Mientras tenga la tool, puede usarla.

❌ **"Darle todas las tools de búsqueda para que verifique mejor".**
- *Tienta porque:* parece que resuelve la verificación.
- *Está mal porque:* sobre-aprovisiona y rompe la separación de responsabilidades.

> 🧠 **Para recordar:** cada agente, las tools de su rol; para lo frecuente de otro rol, una tool chica.

#### Trampa 8 · `any` vs. `tool` vs. `auto`

**La situación.** Hay que garantizar que se extraigan los metadatos antes de enriquecer, o que Claude no responda con texto (Tema 11).

**✅ En el examen elegí:**
- Una tool específica primero → **forced** `{"type": "tool", "name": "extract_metadata"}` en el primer turno, y `auto` en los turnos siguientes.
- Que use **alguna** tool en vez de texto → **`any`**.
- Un agentic loop normal → **`auto`**.

**❌ Las que tientan:**

❌ **"`any` para que llame `extract_metadata`".**
- *Tienta porque:* "any" suena a "obligatorio".
- *Está mal porque:* `any` obliga a llamar **alguna** tool, no **esa**.

❌ **"Pedirle en el system prompt que siempre llame primero a `extract_metadata`".**
- *Tienta porque:* es simple.
- *Está mal porque:* es probabilístico. `tool_choice` lo garantiza.

❌ **"`strict: true` para que llame la tool".**
- *Tienta porque:* strict suena a "obligatorio".
- *Está mal porque:* strict garantiza **inputs válidos**, no que la llame.

> 🧠 **Para recordar:** any = alguna, tool = esa, auto = decide Claude, strict = inputs válidos.

#### Trampa 9 · `fetch_url` para todo

**La situación.** Un subagent usa `fetch_url` y a veces baja páginas que no son documentos del proveedor (Tema 10).

**✅ En el examen elegí:** **reemplazar la tool genérica por una acotada**, como `load_document`, que valida que la URL sea de un documento permitido.

**❌ Las que tientan:**

❌ **"Agregar al prompt la lista de dominios permitidos".**
- *Tienta porque:* no requiere cambiar la tool.
- *Está mal porque:* es probabilístico. La validación tiene que estar en la tool.

> 🧠 **Para recordar:** tool genérica peligrosa → tool acotada que valida.

#### Trampa 10 · Verificaciones que pasan por el coordinador

**La situación.** El agente de síntesis verifica datos pidiéndoselo al coordinador, que se lo pide al agente de búsqueda. Son 2 o 3 idas y vueltas por verificación y ~40% más de latencia. El 85% son verificaciones simples (Tema 10; pregunta oficial de muestra).

**✅ En el examen elegí:** darle a síntesis una **tool acotada `verify_fact`** para las verificaciones simples. Las complejas siguen pasando por el coordinador hacia búsqueda.

**❌ Las que tientan:**

❌ **"Juntar todas las verificaciones y mandarlas en un lote al final".**
- *Tienta porque:* menos idas y vueltas.
- *Está mal porque:* los pasos siguientes de la síntesis necesitan los datos ya verificados. Crea dependencias que bloquean.

❌ **"Darle a síntesis todas las tools de búsqueda web".**
- *Tienta porque:* resuelve todas las verificaciones directamente.
- *Está mal porque:* sobre-aprovisiona y rompe la separación de responsabilidades.

❌ **"Que el agente de búsqueda cachee contexto de cada fuente por adelantado".**
- *Tienta porque:* parece anticiparse.
- *Está mal porque:* no se puede predecir qué va a hacer falta verificar.

> 🧠 **Para recordar:** para lo frecuente y simple, una tool chica; lo complejo, por el coordinador.

### Grupo: Detalles técnicos

#### Trampa 11 · Detalles técnicos que se confunden

**La situación.** Opciones que mezclan nombres o capas (Temas 7 y 11).

**✅ En el examen elegí:**
- `is_error` es de la **API de Claude** (en el `tool_result`); `isError` es de **MCP**. Es el mismo concepto en dos capas.
- Un **error de protocolo** (`-32602`, tool desconocida, pedido mal formado) se corrige en el código o la configuración. Un **error de ejecución** (`isError: true`) es el que el modelo usa para corregirse.
- `disable_parallel_tool_use` va **dentro** de `tool_choice`.
- `isRetryable: false` significa "no repitas **esta** llamada", **no** "abandoná la tarea".

**❌ Las que tientan:**

❌ **"Manejar la tool desconocida en el loop de recuperación del agente".**
- *Tienta porque:* parece robusto.
- *Está mal porque:* es un error de protocolo. Se arregla en el schema o en el cliente, no reintentando.

❌ **"`disable_parallel_tool_use` como parámetro aparte del request".**
- *Tienta porque:* suena a un flag independiente.
- *Está mal porque:* va adentro de `tool_choice`.

❌ **"Ante `isRetryable: false`, cerrar el caso y escalar siempre".**
- *Tienta porque:* "no se puede reintentar".
- *Está mal porque:* el agente puede seguir de otra forma: explicarle al cliente, corregir el input u ofrecer una alternativa.

> 🧠 **Para recordar:** is_error en la API, isError en MCP; protocolo se arregla en código; no reintentable no es lo mismo que terminado.

---

## Checklist oficial

**Tarea 2.1 — Effective tool interfaces with clear descriptions and boundaries**

*Knowledge of*
- [x] Las descripciones son el mecanismo principal de selección; las mínimas producen elecciones poco confiables entre tools parecidas → **Tema 1** (Trampa 1)
- [x] Incluir formatos de entrada, ejemplos de pedidos, casos límite y límites en las descripciones → **Tema 2**
- [x] Las descripciones ambiguas o superpuestas causan misrouting (`analyze_content` vs. `analyze_document`) → **Tema 3**
- [x] La redacción del system prompt influye en la elección: instrucciones atadas a palabras clave crean asociaciones no deseadas → **Tema 4** (Trampa 3)

*Skills in*
- [x] Escribir descripciones que diferencien propósito, entradas, salidas y cuándo usar cada tool frente a alternativas parecidas → **Tema 2** (Trampa 1)
- [x] Renombrar tools y actualizar descripciones para eliminar la superposición (`analyze_content` → `extract_web_results`) → **Tema 3**
- [x] Dividir tools genéricas en tools de propósito específico con contratos de entrada y salida → **Tema 3** (Trampa 2)
- [x] Revisar el system prompt buscando instrucciones atadas a palabras clave que pisen buenas descripciones → **Tema 4** (Trampa 3)

**Tarea 2.2 — Structured error responses for MCP tools**

*Knowledge of*
- [x] El patrón del flag `isError` de MCP para comunicar fallas → **Tema 7**
- [x] La distinción entre errores transient, validation, business y permission → **Tema 7**
- [x] Por qué los errores uniformes ("Operation failed") impiden decidir bien la recuperación → **Tema 7** (Trampa 4)
- [x] La diferencia entre errores reintentables y no reintentables, y cómo la metadata estructurada evita reintentos inútiles → **Tema 7** (Trampa 4)

*Skills in*
- [x] Devolver metadata estructurada: `errorCategory`, `isRetryable` y una descripción legible → **Tema 7**
- [x] Incluir `retriable: false` y explicaciones aptas para el cliente en violaciones de reglas de negocio → **Tema 7** (ejemplo de María)
- [x] Recuperación local en subagents para fallas transitorias, y propagar al coordinador solo lo no resuelto, con resultados parciales y lo intentado → **Tema 9**
- [x] Distinguir fallas de acceso (requieren decidir si reintentar) de resultados vacíos válidos → **Tema 8** (Trampa 5)

**Tarea 2.3 — Distribute tools across agents and configure tool choice**

*Knowledge of*
- [x] Demasiadas tools (18 en vez de 4–5) degradan la confiabilidad de la elección → **Tema 10** (Trampa 6)
- [x] Los agentes con tools fuera de su especialidad tienden a usarlas mal (síntesis haciendo búsquedas) → **Tema 10** (Trampa 7)
- [x] Acceso acotado: cada agente solo con las tools de su rol, más tools acotadas de otro rol para necesidades frecuentes → **Tema 10**
- [x] Opciones de `tool_choice`: `auto`, `any` y forced (`{"type": "tool", "name": "..."}`) → **Tema 11** (Trampa 8)

*Skills in*
- [x] Restringir el set de tools de cada subagent a su rol → **Tema 10**
- [x] Reemplazar tools genéricas por alternativas acotadas (`fetch_url` → `load_document`) → **Tema 10** (Trampa 9)
- [x] Tools acotadas de otro rol para necesidades frecuentes (`verify_fact`), con los casos complejos por el coordinador → **Tema 10** (Trampa 10; y 1C, Tema 7)
- [x] Forced selection para que una tool vaya primero (`extract_metadata` antes del enriquecimiento) y los pasos siguientes en turnos posteriores → **Tema 11** (Trampa 8)
- [x] `tool_choice: "any"` para garantizar que el modelo llame una tool en vez de responder con texto → **Tema 11** (Trampa 8)

**📘 Curso (útil para entender; lecciones 29–36 y decks 133–134):** routing outcomes y "Exam Trap" del nombre (Tema 1) · vague intent / missing scope / no output signal (Tema 2) · consolidación con `action` y namespacing (Tema 3) · reglas de routing en el system prompt (Tema 4) · descripción de parámetros como micro-prompt, required mínimo, enum (Tema 5) · `code`/`message`/`context`/`suggested_action`, errores de usuario vs. sistema, los 3 campos del `tool_result` (Tema 7) · idempotency key, `partial_success`, circuit breaker (Tema 9) · tool bloat, "default to removal" (Tema 10) · semántica de `tool_choice`, arranque directo con el `tool_use`, invalidación de caché (Tema 11) · no good match / two good matches, tests de routing, selection drift, indirect injection (Tema 12).

---

## Autoevaluación oral

1. ¿Qué tiene que tener una buena descripción de tool? ¿Por qué "mejorar la descripción" le gana a "agregar few-shot" o "una capa de routing"?
2. Dos tools se pisan y otra hace de todo. ¿Qué hacés en cada caso? ¿Qué dice la documentación y qué responde el examen?
3. Armá el error que devuelve `process_refund` cuando el reembolso está fuera de plazo. ¿Qué campos lleva y por qué?
4. ¿Qué diferencia hay entre "la búsqueda no encontró nada" y "la búsqueda no se pudo hacer"? ¿Cómo se devuelve cada una?
5. ¿Qué hace `tool_choice` con `auto`, `any`, `tool` y `none`? ¿Cuál usás para que `extract_metadata` vaya primero? ¿Qué agrega `strict: true`?

---

## Preguntas tipo examen

Las preguntas tipo examen de este capítulo están en [`04-practica/modulo-2.md`](../04-practica/modulo-2.md), junto con las del resto del módulo 2. Hacelas cuando termines **todos** los capítulos del módulo, de a una y sin mirar la respuesta.

---

## Revisión contra el blueprint oficial

Qué puede salir en el examen de 2.1–2.3 que el curso de Jacob **no cubre o cubre flojo**, y dónde quedó explicado acá:

1. **Instrucciones del system prompt atadas a palabras clave** (2.1). El curso no lo trata como riesgo y hasta sugiere agregar reglas de routing al prompt. → Tema 4.
2. **Renombrar y dividir tools con los ejemplos de la guía** (`analyze_content` → `extract_web_results`; `analyze_document` → tres tools). El curso empuja a **consolidar**. → Tema 3, con la contradicción explicada.
3. **Vocabulario de errores de la guía**: `errorCategory` con 4 valores, `isRetryable`/`retriable` e `isError`. El curso usa otros nombres (`code`, user/system error). → Tema 7.
4. **Falla de acceso vs. resultado vacío válido** (2.2). El curso no lo distingue explícitamente, y es el distractor de una pregunta de muestra oficial. → Tema 8.
5. **Recuperación local en subagents y qué propagar** (2.2). → Tema 9.
6. **Las cifras de la guía** (18 vs. 4–5 tools), la **especialización** (síntesis buscando en la web) y **`fetch_url` → `load_document`** (2.3). El curso habla de "tool bloat" sin estos ejemplos. → Tema 10.
7. **`tool_choice` como pide la guía**: el deck suplementario del curso tiene "un paso obligatorio → `tool`", pero no el patrón completo de forzar el primer turno y **volver a `auto`** en los siguientes. → Tema 11.
8. **La pregunta oficial de `verify_fact`** (2.3): el curso no la trabaja con sus distractores (lote al final, todas las tools, caché especulativa). → Tema 10 y Trampa 10.
9. **Qué propaga un subagent**: incluye **alternativas posibles**, además de resultados parciales y lo intentado (pregunta oficial de timeout). → Temas 8 y 9.
10. **Solo de la documentación, no de la guía:** `strict`, `none` y `disable_parallel_tool_use`. Hay que saberlos, pero no esperes que sean la respuesta central. → Temas 6 y 11.

No encontré otros huecos para estas tres tareas. Lo que el curso agrega por su cuenta (idempotency key, circuit breaker, `partial_success`, selection drift) queda marcado como 📘: es útil, pero no es la respuesta "oficial".

