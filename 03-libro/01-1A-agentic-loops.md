# Capítulo 1 · 1A · Udemy 2 — Agentic Loops and Core API (el loop agéntico y la API básica)

*Tarea oficial 1.1 · Primer capítulo del módulo 1*

---

## Dónde estamos

Este capítulo cubre la tarea **1.1 Design and implement agentic loops for autonomous task execution** (diseñar e implementar loops agénticos para que un agente ejecute tareas de forma autónoma). Es del Dominio 1 y pesa 3,86% del examen. Ya la viste en otra conversación: acá la repasamos con este método, un poco más rápido, pero sin saltear ningún punto de la guía.

### Cómo leer este capítulo

Todo lo que leés acá **vale para el examen**, salvo que diga lo contrario. Cuando algo sale solo del curso (útil para entender, pero no central), lo marco con **📘 Curso**. Cuando Jacob dice algo distinto de lo que evalúa la guía, aparece un recuadro así:

> ⚠️ **En el curso vas a escuchar otra cosa.** … **Para el examen: …**

## De dónde venimos

Es el primer capítulo, así que no hay nada previo. Solo el escenario que vamos a usar en todo el libro:

TiendaX es una tienda online que vende zapatillas, ropa y accesorios. Recibe unos 3.000 mensajes de soporte por día. La mitad son siempre lo mismo: "¿dónde está mi pedido?", "quiero devolver esto", "me cobraron dos veces". La gerencia decidió usar Claude para atender esos mensajes. Al proyecto le pusieron **SoporteBot**, y vos sos el arquitecto. Lucas es el desarrollador que arma las primeras versiones.

## Mapa del capítulo

**Parte 1 — Del chatbot al agente.** Qué separa a un chatbot, un workflow y un agente, y qué necesita un modelo para poder actuar.
1. Chatbot, workflow y agente: quién decide el camino.
2. Tool use: darle a Claude la capacidad de actuar.

**Parte 2 — La mecánica de la API.** Cómo pide Claude una tool y cómo le devolvés el resultado.

3. La respuesta de Claude: bloques de contenido y `stop_reason`.
4. Devolver el resultado: `tool_result` y el historial.
5. Parallel tool use: varias tools en la misma respuesta.

**Parte 3 — El loop.** Repetir ese ida y vuelta hasta resolver el problema.

6. El agentic loop: decisiones guiadas por el modelo.
7. El context window como memoria de trabajo.

**Parte 4 — Cuándo termina el loop (y cuándo hay que frenarlo).**

8. Terminar por `stop_reason`, y los anti-patterns de terminación.
9. Condiciones de terminación y turn budget (la red de seguridad).
10. Spinning y escalamiento: iterar o pasarle el caso a un humano.

**Parte 5 — ¿Todo tiene que ser un agente?**

11. Cuándo un workflow le gana a un agente.
12. Los cinco patrones de workflow.
13. Elegir la arquitectura: ejes, over-engineering y complejidad incremental.

Cómo se conectan: el Tema 1 dice que un agente es el que decide su propio camino. Los Temas 2 a 5 muestran la pieza que lo hace posible (pedir una tool y recibir el resultado). Los Temas 6 y 7 repiten esa pieza en un loop. Los Temas 8 a 10 dicen cuándo y cómo se corta ese loop. Y los Temas 11 a 13 vuelven al principio: cuándo conviene **no** usar un agente.

---

# Parte 1 — Del chatbot al agente

## Tema 1 — Chatbot, workflow and agent (chatbot, workflow y agente): quién decide el camino

### Qué es

Un modelo de lenguaje, por sí solo, produce texto. No consulta bases de datos, no llama APIs, no cambia nada en el mundo. Produce **tokens** (los pedacitos de texto que genera), no acciones. Tampoco puede guardar nada fuera de lo que ve en la conversación, ni observar el resultado de una operación externa. Todo lo que sigue en el capítulo es la forma de darle a ese modelo la capacidad de actuar, y de decidir quién manda cuando actúa.

El examen distingue tres tipos de sistema, y la diferencia entre ellos no es qué tan inteligentes parecen, sino **quién decide el camino**: qué paso viene después de cuál. A eso se le llama **control flow** (flujo de control). Importa porque casi todas las preguntas de "¿esto es un agente?" se resuelven con esa sola pregunta.

- **Chatbot:** recibe un mensaje y responde un mensaje. Nada más. No actúa fuera de la conversación, y lo que "sabe" vive solo dentro de esa conversación. Nadie decide un camino, porque no hay camino: hay una respuesta.
- **Workflow** (flujo predefinido): el camino lo decide el desarrollador cuando escribe el código, en **design time** (tiempo de diseño). El modelo puede participar en algunos pasos ("llenar el contenido"), pero la secuencia está fija.
- **Agent** (agente): el camino lo decide el modelo mientras trabaja, en **inference time** (tiempo de inferencia: el momento en que el modelo está generando su respuesta). El modelo mira lo que pasa y elige qué hacer después: qué tool usar y cuándo.

Anthropic lo define así en su artículo "Building effective agents": los workflows son sistemas donde el modelo y las tools se orquestan con **caminos de código predefinidos**; los agentes son sistemas donde el modelo **dirige dinámicamente su propio proceso** y el uso de tools.

📘 **Curso:** más autonomía significa más capacidad, pero también más riesgo; por eso un agente necesita **guardrails** (barreras de protección) y límites de alcance.

### Ejemplo

La primera versión de SoporteBot la arma Lucas en una tarde. Cada mensaje del cliente va a Claude junto con un **system prompt** (las instrucciones fijas que el modelo recibe antes de la conversación) que dice "Sos el asistente de soporte de TiendaX". La respuesta de Claude vuelve al cliente.

Juan escribe: "¿Dónde está mi pedido TX-104233?".

SoporteBot contesta: "¡Hola Juan! Los pedidos suelen llegar en 3 a 5 días hábiles. Podés ver el estado en la sección Mis pedidos".

La respuesta es amable y no sirve para nada. SoporteBot no sabe dónde está el pedido, y no tiene forma de saberlo. Juan escribe de nuevo, enojado. Lo que construyó Lucas es un **chatbot**: para saber dónde está el pedido de Juan, SoporteBot necesita poder **hacer algo** (consultar el sistema de pedidos), no solo hablar.

### Para el examen

- La pregunta clave es **quién decide el camino**: el desarrollador en design time (workflow) o el modelo en inference time (agente).
- Un chatbot responde; no actúa sobre el mundo.
- Que el sistema use un modelo, o incluso que tenga tools, no lo vuelve agente. Lo que importa es quién elige el camino (vuelve en el Tema 11).

### Cómo se une

Para que el modelo pueda decidir algo más que texto, primero necesita una forma de actuar. Eso es el Tema 2.

---

## Tema 2 — Tool use (uso de tools): darle a Claude la capacidad de actuar

### Qué es

Una **tool** (herramienta) es una función que tu código sabe ejecutar y que le describís al modelo para que pueda pedirla. Es la pieza que le faltaba a SoporteBot: con una tool de "consultar pedido", Claude ya no tiene que inventar una respuesta genérica, puede pedir el dato real. En la llamada a la API de Claude (la **Messages API**, el endpoint con el que le mandás mensajes y recibís respuestas), mandás la lista de tools junto con los mensajes. Cada tool tiene tres campos:

- **`name`**: cómo se llama la tool.
- **`input_schema`**: un **JSON Schema** (un formato estándar para describir la forma de un JSON) que dice qué parámetros recibe.
- **`description`**: qué hace, en lenguaje natural. Es lo más importante de los tres.

¿Por qué la descripción es lo más importante? Porque **Claude elige qué tool usar leyendo la descripción en lenguaje natural**, no leyendo tu código: nunca ve cómo está implementada. La documentación de Anthropic dice que la descripción es, lejos, el factor que más pesa en qué tan bien se usan las tools. 📘 **Curso:** Jacob insiste en escribir descripciones que hasta alguien que no programa podría seguir. (Esto lo vemos a fondo en 2A, tool design.)

Hay un punto que confunde mucho: **Claude no ejecuta la tool. Solo la pide.** La ejecuta tu código: el **runtime**, que es el programa que rodea al modelo, recibe sus pedidos y los lleva a cabo. El resultado vuelve al modelo como una **observation** (observación). Tool use es lo que cierra la distancia entre lo que el modelo sabe y lo que pasa en el mundo, pero la mano que actúa siempre es la de tu programa.

Según quién las ejecuta, hay dos clases de tools. La diferencia importa porque define quién arma el resultado (y vuelve en el Tema 8 con `pause_turn`):
- **Client tools** (tools del cliente): las tuyas, como `get_order_status`. Las ejecuta tu código, y vos armás el resultado. La documentación lo resume así: el modelo pide, vos ejecutás, vos informás el resultado.
- **Server tools** (tools del servidor): las ejecuta Anthropic del lado del servidor, como la búsqueda web (`web_search`), `web_fetch` o `code_execution`. Vos nunca armás su resultado.

Al modelo con estas capacidades sumadas, Anthropic y el curso lo llaman **augmented LLM** (modelo de lenguaje aumentado): un modelo al que se le suman **retrieval** (búsqueda de información), tools y memoria. Es el bloque básico: todo sistema agéntico se arma a partir de él.

El curso también clasifica las tools según lo que hacen. La clasificación sirve para ver dónde está el riesgo:
- **Data access** (acceso a datos): **leen**. Consultar un pedido, leer un archivo, traer un documento.
- **Computation** (cálculo): **calculan**, a veces en un entorno aislado. Sumar un carrito, correr código.
- **External APIs** (APIs externas): **escriben** en sistemas externos. Iniciar un reembolso, mandar un mail.

Las que escriben tienen **side effects** (efectos secundarios: cambios en el mundo) que no siempre se pueden deshacer. Un reembolso hecho no se "des-hace" borrando un mensaje. Guardá esa idea: es la razón por la que, más adelante (1D), algunas acciones van a necesitar aprobación humana.

### Ejemplo

El sistema de pedidos de TiendaX tiene un **endpoint** interno (una URL de su API que se llama con el número de pedido) que devuelve el estado de un pedido. Para que Claude lo use, le das esta tool.

### Cómo se configura

```json
{
  "name": "get_order_status",
  "description": "Devuelve el estado actual de un pedido de TiendaX (pendiente, enviado, entregado o cancelado), la empresa de envío y la fecha estimada de entrega. Usala cuando el cliente pregunta dónde está su pedido o cuándo llega. Necesita el número de pedido con formato TX-NNNNNN.",
  "input_schema": {
    "type": "object",
    "properties": {
      "order_id": { "type": "string", "description": "Número de pedido, por ejemplo TX-104233" }
    },
    "required": ["order_id"]
  }
}
```

Fijate que la descripción dice **qué devuelve**, **cuándo usarla** y **qué formato** necesita. Una descripción como "Hace algo con pedidos" dejaría a Claude adivinando.

### Para el examen

- Claude elige la tool por la **descripción**, no por el código.
- Claude **pide**; el **runtime ejecuta**. El modelo nunca corre la tool por su cuenta.
- Client tools: las ejecuta tu código y vos devolvés el resultado. Server tools: las ejecuta Anthropic.
- Las tools que **escriben** tienen efectos secundarios: son las que más riesgo traen.

### Cómo se une

Ya sabés qué es una tool. Ahora falta ver cómo se ve, en la API, el momento en que Claude la pide (Tema 3) y cómo le devolvés el resultado (Tema 4).

---

# Parte 2 — La mecánica de la API

## Tema 3 — Content blocks and stop_reason (bloques de contenido y motivo de parada)

### Qué es

Cuando Claude quiere usar una tool, no lo dice con una frase: lo indica con una estructura que tu runtime puede leer sin ambigüedad. Por eso hay que conocer la forma de la respuesta de la API. Trae dos cosas que importan acá:

- **`content`**: una **lista de bloques** (cada bloque es una pieza de la respuesta, con su tipo). Puede traer un bloque de texto (`type: "text"`), uno o más pedidos de tool (`type: "tool_use"`), o las dos cosas **en la misma respuesta**.
- **`stop_reason`** (motivo de parada): dice **por qué** Claude dejó de generar. Si vale `"tool_use"`, significa "paré porque necesito que ejecutes una tool". Si vale `"end_turn"`, significa "terminé mi respuesta".

Cada bloque `tool_use` trae tres datos: un **`id`** único (lo vas a necesitar para devolver el resultado), el **`name`** de la tool y el **`input`** con los parámetros. Con eso tu runtime sabe qué ejecutar y con qué valores.

(`stop_reason` tiene más valores además de estos dos. Los vemos todos en el Tema 8.)

### Ejemplo

Con la tool del Tema 2, Juan vuelve a preguntar por su pedido. Esta vez Claude no contesta con texto suelto.

### Cómo se ve

```json
{
  "stop_reason": "tool_use",
  "content": [
    { "type": "text", "text": "Voy a buscar tu pedido." },
    {
      "type": "tool_use",
      "id": "toolu_01A",
      "name": "get_order_status",
      "input": { "order_id": "TX-104233" }
    }
  ]
}
```

Fijate en dos cosas:
1. `content` trae **texto y un pedido de tool juntos**. Que haya texto no significa que Claude terminó. (Esto es la base del bug del Tema 8.)
2. `stop_reason` vale `"tool_use"`: Claude está esperando que tu runtime ejecute `get_order_status`.

Tu runtime llama al endpoint de pedidos y obtiene `{"status": "shipped", "carrier": "Andreani", "eta": "2026-11-18"}`.

### Para el examen

- El campo que dice por qué paró Claude es **`stop_reason`**. (Si una opción habla de `finish_reason`, es de otra API: no es Claude.)
- Una misma respuesta puede traer **texto + `tool_use`**.
- El `id` del `tool_use` es lo que conecta el pedido con su resultado.

### Cómo se une

Tu runtime ya tiene el resultado de la tool. Ahora tiene que devolvérselo a Claude, con reglas precisas (Tema 4).

---

## Tema 4 — Returning tool results (devolver el resultado): tool_result y el historial

### Qué es

Un dato clave antes de seguir: **la API no guarda la conversación**. Cada llamada es independiente y recibe una lista `messages` con todo lo que pasó hasta ahora: el **conversation history** (historial de la conversación). Si algo no está en esa lista, para Claude no existe. Cada mensaje tiene un **rol**:
- **`user`**: lo que llega desde tu lado (el cliente **o tu runtime**).
- **`assistant`**: lo que generó Claude.

Para devolver el resultado de una tool, tu runtime agrega **dos mensajes** al historial y vuelve a llamar a la API. Las reglas son estrictas porque la API las valida, y porque así Claude puede emparejar cada pedido con su respuesta:

1. Primero agregás la respuesta de Claude **completa**, como mensaje `assistant`, con el bloque `tool_use` incluido. No solo el texto: si falta el pedido, el resultado no tiene a qué responder.
2. Después, un mensaje con rol **`user`** que contiene un bloque **`tool_result`** (resultado de la tool). Va como `user` porque viene de tu lado, no de Claude.
3. El `tool_result` lleva **`tool_use_id`**, que tiene que ser igual al `id` del `tool_use` (`toolu_01A`). Así Claude sabe a qué pedido corresponde cada resultado.
4. El mensaje con los `tool_result` va **inmediatamente después** del mensaje `assistant` que los pidió. No puede haber ningún mensaje en el medio.
5. Dentro de ese mensaje `user`, **los `tool_result` van primero**. Si querés agregar texto, va después.
6. Si la tool falló, **igual devolvés un `tool_result`**, con **`"is_error": true`** y un mensaje que explique qué pasó. Claude pidió algo y tiene que enterarse de qué pasó con eso, aunque haya salido mal.

Qué puede llevar un `tool_result`:
- `type: "tool_result"` y `tool_use_id` (obligatorios).
- `content` (opcional): un texto, o una lista de bloques (texto, imagen, documento).
- `is_error` (opcional): `true` si la ejecución falló.

Cuando hay error, importa cómo está escrito el mensaje, porque es lo único que Claude tiene para decidir qué hacer. Tiene que ser **instructivo**: decir qué pasó y qué se puede hacer. Por ejemplo, "Rate limit exceeded. Retry after 60 seconds." (límite de pedidos superado, reintentá en 60 segundos), no un "failed" genérico. Con un error claro, Claude puede corregir el pedido: ante parámetros faltantes, suele reintentar 2 o 3 veces con correcciones. (Los tipos de error y cuáles se reintentan los vemos en 1D y 2A.)

Un detalle de la documentación que conviene saber: si después de los `tool_result` metés **texto suelto**, a veces Claude devuelve una **respuesta vacía con `end_turn`**. La solución es mandar **solo los `tool_result`**. Y no reenvíes la respuesta vacía tal cual: hay que cambiar lo que mandaste.

📘 **Curso:** las slides llaman a este par (`tool_use` del assistant + `tool_result` del user) una **atomic unit** (unidad atómica): no se separa ni se deja a medias.

### Ejemplo

Juan preguntó por el pedido TX-104233. Claude pidió `get_order_status` con el id `toolu_01A`. Tu runtime obtuvo el resultado y arma esto.

### Cómo se ve

```json
[
  { "role": "user", "content": "¿Dónde está mi pedido TX-104233?" },
  { "role": "assistant", "content": [ "...los dos bloques del Tema 3, completos: el texto y el tool_use..." ] },
  {
    "role": "user",
    "content": [
      {
        "type": "tool_result",
        "tool_use_id": "toolu_01A",
        "content": "{\"status\": \"shipped\", \"carrier\": \"Andreani\", \"eta\": \"2026-11-18\"}"
      }
    ]
  }
]
```

Con eso, Claude contesta: "Juan, tu pedido TX-104233 ya salió con Andreani y llega el 18/11".

Si el endpoint hubiera estado caído, el `tool_result` sería así (va igual, nunca se omite):

```json
{
  "type": "tool_result",
  "tool_use_id": "toolu_01A",
  "is_error": true,
  "content": "El sistema de pedidos no responde (timeout después de 10 s). El pedido no se pudo consultar; no significa que no exista."
}
```

### Para el examen

- Respuesta **completa** como `assistant` (con los `tool_use`), y después `tool_result` en rol **`user`**.
- `tool_use_id` = `id` del `tool_use`.
- `tool_result` **inmediatamente después** del assistant que lo pidió; dentro del mensaje, **primero los `tool_result`**, después el texto (si hay).
- Una falla se devuelve con **`is_error: true`** y un mensaje claro. Nunca se omite el `tool_result`.
- Guardar solo el texto del assistant (sin el `tool_use`) deja al `tool_result` **huérfano**: no tiene a qué pedido corresponder.

### Cómo se une

Hasta acá, Claude pidió una sola tool. Pero puede pedir varias de una vez (Tema 5).

---

## Tema 5 — Parallel tool use (llamadas a tools en paralelo)

### Qué es

A veces Claude pide **varias tools en la misma respuesta**: la respuesta trae dos o más bloques `tool_use`, cada uno con su `id`. Pasa cuando las llamadas son **independientes** entre sí, o sea que una no necesita el resultado de la otra. Así se ahorra vueltas: en vez de pedir una, esperar, y pedir la otra, pide las dos juntas.

La regla de la documentación para responder es: devolvés **un `tool_result` por cada `tool_use`**, **todos juntos**, en **un solo** mensaje `user`. Claude pidió todo en un turno, y espera todas las respuestas en el turno siguiente.

Mandarlos en mensajes `user` separados es un error común, porque parece más ordenado. La documentación avisa que, además de no ser el formato esperado, eso le "enseña" a Claude a **no** pedir tools en paralelo en el resto de la conversación: Claude imita el patrón que ve en el historial.

Si decidís **no** ejecutar una de las llamadas (por ejemplo, porque la anterior falló y ya no tiene sentido), igual devolvés su `tool_result`, con `is_error: true` y la explicación. Todo `tool_use` necesita su `tool_result`.

### Ejemplo

Martín pregunta por sus pedidos TX-104233 y TX-104251. Claude pide `get_order_status` dos veces en la misma respuesta (`toolu_01B` y `toolu_01C`). Tu runtime ejecuta las dos y devuelve los dos resultados en un solo mensaje.

### Cómo se ve

```python
# todos los tool_use de la respuesta
calls = [b for b in resp.content if b.type == "tool_use"]

# un tool_result por cada uno, con su tool_use_id
results = [{"type": "tool_result", "tool_use_id": c.id,
            "content": run_tool(c.name, c.input)} for c in calls]

messages += [{"role": "assistant", "content": resp.content},   # respuesta completa
             {"role": "user", "content": results}]             # TODOS los resultados en UN mensaje
```

### Para el examen

- Varios `tool_use` → **un solo** mensaje `user` con **todos** los `tool_result`, cada uno con su `tool_use_id`.
- Un mensaje por resultado es la opción "ordenada" que tienta y está mal.
- Aunque no ejecutes una llamada, su `tool_result` va igual, con `is_error: true`.

### Cómo se une

Ya tenés la pieza completa: Claude pide, tu runtime ejecuta, el resultado vuelve. Si repetís esa pieza hasta que el problema se resuelve, tenés un agentic loop (Tema 6).

---

# Parte 3 — El loop

## Tema 6 — Agentic loop (loop agéntico): decisiones guiadas por el modelo

### Qué es

Muchos problemas no se resuelven con una sola tool. Para una devolución, por ejemplo, hay que buscar el pedido, después ver la política, después iniciar el reembolso. El **agentic loop** (loop agéntico) es simplemente repetir el ida y vuelta de la Parte 2 hasta que Claude diga que terminó. Es el centro de la tarea 1.1. Su ciclo de vida, como lo describe la guía oficial:

1. Mandás el pedido a Claude (con el historial y las tools).
2. Inspeccionás `stop_reason`.
3. Si es `"tool_use"`, ejecutás las tools pedidas.
4. Agregás los resultados al historial y volvés al paso 1.
5. Si es `"end_turn"`, terminaste.

La idea más importante del tema es **quién decide la próxima tool**. Hay dos formas de armar un sistema con tools, y el examen pide distinguirlas:
- **Model-driven decision-making** (decisiones guiadas por el modelo): Claude razona qué tool llamar después, según lo que ve en el contexto.
- **Pre-configured decision trees or tool sequences** (árboles de decisión o secuencias de tools preconfiguradas): el desarrollador fijó el orden de antemano.

El loop es lo primero. Un árbol de `if` es lo segundo, aunque use tools. Es la misma pregunta del Tema 1 (quién decide el camino), ahora mirada en el código.

¿Por qué el loop funciona en casos que nadie previó? Porque **la observación es lo que hace que el loop se corrija solo**: cada resultado vuelve al contexto y Claude decide el siguiente paso mirándolo. Hay tres casos:
- Si el resultado es **exitoso**, entra al contexto y Claude sigue adelante.
- Si es un **error** o algo inesperado, Claude **replanifica** (cambia el plan o vuelve a llamar con otros datos).
- Si es **parcial**, Claude hace otra llamada para completarlo antes de seguir.

El curso cuenta el loop con cuatro fases que se repiten en cada vuelta:
- **Perception** (percepción): leer el contexto (instrucciones, historial, resultados anteriores) e identificar en qué estado está el objetivo.
- **Reasoning** (razonamiento): decidir la próxima acción, comparando lo que obtuvo con el objetivo.
- **Action** (acción): emitir un `tool_use` o una respuesta final.
- **Observation** (observación): el resultado vuelve al contexto y alimenta la siguiente percepción.

Al hecho de que el plan se arme o cambie durante la ejecución, según los resultados intermedios, el curso lo llama **dynamic planning** (planificación dinámica). 📘 **Curso:** en otra slide, las mismas fases aparecen como **four pillars of agency** (cuatro pilares): perception, selection, execution, iteration; es lo mismo con otros nombres.

Anthropic lo resume en tres fases: **gather context, take action, verify work** (juntar contexto, actuar y verificar el trabajo). Todas estas listas son la misma idea contada distinto. **En el examen, pensá en la mecánica de la API:** `stop_reason`, `tool_use_id`, rol `user`, historial completo.

### Ejemplo: mal y bien

María escribe: "Quiero devolver las zapatillas del pedido TX-104290, me quedaron chicas". Para resolverlo, SoporteBot tiene que buscar el pedido, ver la fecha de entrega, revisar la política de devoluciones y, si corresponde, iniciar el reembolso. Ya tenés esas cuatro tools. Pero el orden depende de lo que vaya apareciendo: si el pedido no está entregado, no tiene sentido revisar la política.

**Mal (árbol de decisiones).** Lucas propone: "si el mensaje dice 'devolver', llamo a `get_order_status`; si el status es entregado, llamo a `check_return_policy`…". Funciona para este caso. Pero María podría preguntar por otro pedido en el mismo mensaje, o el pedido podría estar partido en dos envíos. Cada caso nuevo es una rama más del árbol.

**Bien (loop).** Dejás que **Claude decida** qué tool llamar en cada paso. Tu código solo repite el ciclo:

- Primera vuelta: Claude pide `get_order_status("TX-104290")`.
- Segunda: ve que se entregó hace 12 días y pide `check_return_policy`.
- Tercera: la política permite 30 días; pide `start_refund`.
- Cuarta: con el reembolso confirmado, responde a María con texto y `stop_reason: "end_turn"`. El loop termina.

Nadie programó esa secuencia. Claude la armó mirando cada resultado. Y si algo sale distinto, el loop se corrige solo: si `get_order_status` hubiera devuelto un error, Claude habría replanificado (por ejemplo, pedirle a María que confirme el número). Si hubiera devuelto un resultado parcial (un pedido en dos envíos), habría hecho otra llamada para completar.

### Cómo se configura

```python
messages = [{"role": "user", "content": mensaje_de_maria}]

while True:
    resp = client.messages.create(
        model="claude-sonnet-5-5", max_tokens=2048,
        system=system_prompt, tools=tools, messages=messages)

    messages.append({"role": "assistant", "content": resp.content})  # respuesta completa

    if resp.stop_reason != "tool_use":
        break      # Claude terminó, o pasó otra cosa: revisar cuál (Tema 8)

    # ejecutar(b) corre la tool y devuelve un bloque tool_result con tool_use_id=b.id
    # (si falla, el mismo bloque con is_error=True y un mensaje claro)
    resultados = [ejecutar(b) for b in resp.content if b.type == "tool_use"]
    messages.append({"role": "user", "content": resultados})   # todos los tool_result juntos
```

Esta es la **forma canónica** de la documentación: seguir **mientras** `stop_reason` sea `"tool_use"`, y salir con cualquier otro valor. (Por qué así, y no al revés, en el Tema 8.)

### Para el examen

- Ciclo de vida: request → inspeccionar `stop_reason` → ejecutar tools → devolver resultados → repetir; terminar con `end_turn`.
- **Model-driven** (Claude decide la próxima tool según el contexto) vs. **árbol de decisión / secuencia preconfigurada** (la decidió el desarrollador). El examen pide reconocer cuál es cuál.
- Si te dan las fases (perception/reasoning/action/observation o gather/act/verify), son la misma idea que la mecánica de la API.

### Cómo se une

Usa todo lo de la Parte 2 en cada vuelta. Y depende de que el historial lleve todo: eso es el Tema 7.

---

## Tema 7 — Context window as working memory (el context window como memoria de trabajo)

### Qué es

El **context window** (ventana de contexto) es todo lo que Claude ve en una llamada: instrucciones, historial y resultados de tools. **Claude no recuerda nada entre llamadas**: cada llamada a la API recibe la conversación entera, y Claude razona solo con eso. Por eso **los resultados de las tools tienen que entrar al historial**. Si no agregás el `tool_result`, Claude no sabe qué pasó y no puede razonar el siguiente paso.

Durante una sesión, en el contexto se va acumulando todo lo que pasó. El curso lo llama **in-context memory** (memoria en contexto) y distingue cuatro cosas:
- **Inputs**: las instrucciones, el mensaje del usuario y los documentos iniciales.
- **Actions**: cada `tool_use` que emitió el agente.
- **Observations**: cada `tool_result` que devolvió el runtime.
- **Reasoning**: el razonamiento intermedio.

Todo eso es **efímero**: el context window es **memoria de trabajo, no memoria permanente**. Cuando la sesión termina, se pierde. Lo que tenga que sobrevivir entre conversaciones tiene que guardarse afuera (lo ves en 1C y en 5C).

### Ejemplo

En la tercera vuelta del loop de María, Claude tiene en contexto: el mensaje de María, el `tool_use` y el `tool_result` de `get_order_status` ("entregado hace 12 días") y los de `check_return_policy` ("30 días"). Con eso decide pedir `start_refund`.

Si Lucas, "para ahorrar tokens", hubiera reemplazado el resultado de la política por un resumen propio ("política OK") **antes de que Claude lo viera**, Claude no tendría el dato del plazo para explicárselo a María. Y si hubiera guardado solo el texto del assistant, sin el `tool_use`, el `tool_result` quedaría huérfano.

### Para el examen

- Lo que no está en el historial, para Claude **no pasó**.
- "Resumir el resultado de la tool antes de que Claude lo vea, para ahorrar tokens" es un distractor.
- El context window es **efímero**: lo que tiene que durar entre sesiones va afuera.

### Cómo se une

Con los Temas 6 y 7 el loop funciona. Ahora falta lo más preguntado: **cuándo termina** (Tema 8).

---

# Parte 4 — Cuándo termina el loop

## Tema 8 — Terminating on stop_reason (terminar por stop_reason) y los anti-patterns de terminación

### Qué es

Un loop necesita saber cuándo parar, y la señal tiene que ser confiable: si corta antes, el cliente queda sin respuesta; si no corta nunca, gasta sin fin. La **única señal confiable** es **`stop_reason`**, porque es un campo estructurado que la API pone exactamente por ese motivo. La regla de la guía es simple: el loop **sigue** cuando `stop_reason` es `"tool_use"` y **termina** cuando es `"end_turn"`.

La guía nombra tres **anti-patterns** (soluciones que parecen correctas pero son errores de diseño) para decidir la terminación. Los tres tienen en común que reemplazan la señal estructurada por una suposición:
1. **Parsing natural language signals** (parsear señales en lenguaje natural): buscar en el texto "listo", "done", "task complete" para decidir si terminar.
2. **Checking for assistant text content** (usar la presencia de texto del assistant) como indicador de que la tarea está completa.
3. **Arbitrary iteration caps as the primary stopping mechanism** (usar un límite arbitrario de vueltas como mecanismo **principal** de parada). Este lo vemos en el Tema 9.

La API tiene más valores de `stop_reason` que los dos de la guía. No todos significan "terminé bien", así que conviene saber qué hacer con cada uno:

| `stop_reason` | Qué significa | Qué hace el runtime |
|---|---|---|
| `tool_use` | Claude pide una o más tools | Ejecutarlas, devolver los `tool_result`, seguir |
| `end_turn` | Claude terminó su respuesta de forma natural | Fin del loop: usar la respuesta |
| `max_tokens` | Se cortó por el límite de tokens de salida (`max_tokens`) | **No** es un fin normal: la respuesta está truncada. Subir `max_tokens` o pedir que continúe. Si el último bloque es un `tool_use` cortado a la mitad, reintentar con más `max_tokens` (ese pedido no se puede ejecutar) |
| `stop_sequence` | Claude generó una de las secuencias de corte que vos definiste | Ver cuál fue (campo `stop_sequence`) y actuar |
| `pause_turn` | Un loop de **server tools** llegó a su límite de iteraciones (por defecto, 10 del lado del servidor) | Reenviar la respuesta tal cual para que continúe |
| `refusal` | Claude se negó a responder | Manejarlo aparte. Llega como respuesta exitosa (HTTP 200), no como error. Se puede ver el detalle en `stop_details` y reintentar con otro modelo |
| `model_context_window_exceeded` | La respuesta llenó el context window del modelo | Tratarla como truncada |

Dos aclaraciones de la documentación:
- Los `stop_reason` vienen en una respuesta **exitosa**. Si la llamada falla (por ejemplo, un error 429 o 500), eso es un **error HTTP** y se maneja aparte, no con `stop_reason`.
- `pause_turn` solo aparece con server tools. Una respuesta con un `tool_use` de una client tool pendiente **nunca** trae `pause_turn`. SoporteBot usa client tools, así que no le pasa.

Por eso el loop del Tema 6 dice `if resp.stop_reason != "tool_use": break` y después revisás **cuál** fue el motivo. Salir del loop de client tools es correcto con cualquiera de esos valores, pero `max_tokens` o `refusal` **no** significan "tarea completa". **Salir del loop no es lo mismo que terminar la tarea.**

### Ejemplo: el bug del "Voy a revisar"

Una semana después aparecen conversaciones raras. Pedro pregunta por su pedido y SoporteBot le contesta "Voy a revisar tu pedido". Y nada más. Pedro espera. Nadie le responde.

Lucas había cambiado la condición de salida del loop. Su razonamiento: "si Claude ya escribió texto para el cliente, terminó".

```python
if resp.content[0].type == "text":
    break        # MAL: hay texto, asumo que terminó
```

¿Te acordás de la respuesta del Tema 3? Traía un bloque de texto ("Voy a buscar tu pedido") **y** un `tool_use`. Con la condición de Lucas, el loop corta justo cuando Claude estaba por actuar. El pedido de la tool queda sin ejecutar. Es el anti-pattern 2.

Otra desarrolladora, Sofía, había probado algo parecido en un prototipo: buscar en el texto frases como "listo" o "ya está resuelto". Falla igual: Claude puede decir "listo, ahora reviso la política" y seguir trabajando, o terminar sin usar ninguna de esas palabras. Es el anti-pattern 1.

Lucas vuelve a `stop_reason` y Pedro recibe su respuesta.

### Cómo se configura: la forma canónica y el código de las slides

```python
# BIEN (forma canónica de la documentación): seguir MIENTRAS sea tool_use
if resp.stop_reason != "tool_use":
    break
    # después: si fue end_turn → usar la respuesta;
    #          si fue max_tokens / model_context_window_exceeded → truncada;
    #          si fue refusal → manejar aparte
```

> ⚠️ **En el curso vas a escuchar otra cosa.** El ejemplo `agent_loop.py` de las slides hace `if resp.stop_reason == "end_turn": break` y, en cualquier otro caso, ejecuta tools. Si la respuesta vino con `max_tokens`, ese código intentaría ejecutar tools que no existen (o que quedaron cortadas). **Para el examen:** la forma canónica es la inversa (seguir **mientras** sea `tool_use`, salir con cualquier otro valor): continuar con `tool_use`, terminar con `end_turn`, y no tratar `max_tokens` como fin normal.

### Para el examen

- Terminar por **`stop_reason`**, nunca por texto ni por palabras clave.
- Texto + `tool_use` en la misma respuesta es lo que rompe la condición "hay texto".
- `max_tokens` = respuesta **truncada**, no tarea completa. `end_turn` no es un error.
- `refusal` llega como HTTP 200; los errores de la API son HTTP 4xx/5xx.
- `pause_turn` = server tools: reenviar para que siga.

### Cómo se une

El anti-pattern 3 (el límite de vueltas como mecanismo principal) es el que más confunde, porque el curso propone justamente un límite. Lo vemos en el Tema 9.

---

## Tema 9 — Termination conditions and turn budget (condiciones de terminación y presupuesto de vueltas)

### Qué es

`stop_reason` dice cuándo Claude terminó. Pero hay situaciones en las que conviene cortar aunque Claude no haya terminado, porque el loop se rompió. El curso ordena esas situaciones en cuatro **termination conditions** (condiciones de terminación) legítimas:
- **Task complete** (tarea completa): el agente logró el objetivo. En la API, eso es `end_turn`.
- **Error threshold** (umbral de errores): demasiadas fallas seguidas. Mejor parar que quemar vueltas en un camino roto.
- **Budget exhausted** (presupuesto agotado): se llegó al límite de vueltas o de tokens. Se corta **sea cual sea el estado de la tarea**.
- **Stop signal** (señal de parada): el **orchestrator** (orquestador: el componente que coordina al agente y le asigna trabajo; lo ves a fondo en 1C) o el usuario piden parar.

¿Por qué hacen falta las otras tres? Porque un loop puede no terminar nunca. El curso da tres causas típicas de **loops infinitos**:
- No hay condición de parada: el agente nunca declara la tarea completa.
- Una tool que **siempre falla** y se reintenta sin límite.
- **Razonamiento circular**: el modelo vuelve a la misma decisión sin información nueva.

Para cortarlos, el curso propone un **turn budget** (presupuesto de vueltas): un máximo de vueltas (`MAX_ITERATIONS = 10`) que se fija **antes** de empezar y que cuenta el **runtime** (la capa de orquestación), **no el modelo**. Lo cuenta el runtime porque un modelo atrapado en un loop roto no es confiable para darse cuenta de que está atrapado. Al llegar al límite, el runtime corta y devuelve el **progreso parcial**.

La pregunta que confunde es qué papel tiene ese límite. La respuesta: el mecanismo **principal de terminación** es `stop_reason` (el loop termina cuando Claude dice `end_turn`), y el turn budget es una **red de seguridad** que corta loops descontrolados, pero no decide cuándo la tarea está hecha. Por eso llegar al límite **no** es un éxito: es una falla o un caso para escalar. Y si un agente termina "demasiado pronto" porque choca contra el límite, la solución **no** es subir el límite: hay que mirar por qué no llega a `end_turn`. El extremo opuesto ("nunca pongas límites") también está mal: "Building effective agents" recomienda incluir **stopping conditions** (condiciones de parada), como un máximo de iteraciones, **para mantener el control**.

> ⚠️ **En el curso vas a escuchar otra cosa.** Las slides llaman al turn budget "la defensa programática **principal** contra loops descontrolados" (*runaway loops*). La guía, en cambio, marca como anti-pattern usar un límite arbitrario de iteraciones **como mecanismo principal de parada**. **Para el examen:** `stop_reason` es el mecanismo principal; el límite es la red de seguridad. No se contradicen del todo: el límite sí es la defensa contra loops *rotos*, pero no es lo que decide que la tarea terminó.

**En el Agent SDK.** El Agent SDK de Anthropic es la librería para construir agentes que trae el loop ya armado: el loop sigue hasta que Claude produce una respuesta sin tool calls. Como no escribís el loop, el resguardo no es código sino configuración:
- **`max_turns`** (`maxTurns` en TypeScript): máximo de vueltas con tool use. **Por defecto no tiene límite.**
- **`max_budget_usd`** (`maxBudgetUsd`): corta cuando el gasto estimado pasa ese monto. Por defecto, sin límite. La documentación dice que poner un presupuesto es un buen valor por defecto para agentes en producción.

Al terminar, el SDK devuelve un **`ResultMessage`** con un campo **`subtype`** que dice cómo terminó. Mirarlo es la forma de saber si la tarea se completó o si se cortó por un límite:

| `subtype` | Qué significa |
|---|---|
| `success` | Terminó bien. Es el **único** caso que trae el campo `result` con la respuesta final |
| `error_max_turns` | Llegó a `max_turns`. **La tarea no terminó** |
| `error_max_budget_usd` | Llegó al presupuesto. La tarea no terminó |
| `error_during_execution` | Hubo un error durante la ejecución |
| `error_max_structured_output_retries` | Agotó los reintentos para producir la salida estructurada pedida |

El `ResultMessage` también trae su propio `stop_reason` (`end_turn`, `max_tokens`, `refusal`, etc.).

Un matiz: ante `error_max_turns`, la documentación del SDK muestra cómo **reanudar la sesión con un límite mayor**. Eso tiene sentido cuando el agente **venía avanzando** y la tarea es larga de verdad. Si estaba girando en falso (Tema 10), más vueltas solo cuestan más plata. **En el examen**, ante un agente que "termina antes de tiempo" o choca seguido contra el límite, la respuesta es **diagnosticar la causa**, no subir el cap.

### Ejemplo: el loop que no paraba

Un viernes a la noche se cae el endpoint de pedidos. Rosa pregunta por el pedido TX-104300. SoporteBot llama a `get_order_status`. Error. Lo vuelve a llamar con los mismos parámetros. Error. Y otra vez. A la mañana siguiente, esa conversación tiene 180 llamadas y la factura de la API del fin de semana es tres veces la normal. Rosa nunca recibió respuesta.

Es la segunda causa de loop infinito: una tool que siempre falla, reintentada sin límite. Con un turn budget de 10 vueltas, el runtime hubiera cortado en la décima y devuelto un resultado parcial. Pero eso **no** es "tarea resuelta": es una falla que hay que escalar (Tema 10).

### Cómo se configura

```python
# Versión del curso, corregida con la forma canónica del Tema 8
MAX_ITERATIONS = 10                       # lo cuenta el runtime, no el modelo
for turn in range(MAX_ITERATIONS):
    resp = client.messages.create(model="claude-sonnet-5-5", max_tokens=2048,
                                  tools=tools, messages=messages)
    messages.append({"role": "assistant", "content": resp.content})
    if resp.stop_reason != "tool_use":    # terminación PRINCIPAL: stop_reason
        break
    messages.append({"role": "user", "content": ejecutar_tools(resp)})
else:
    # red de seguridad: se agotó el presupuesto. NO es éxito.
    reportar_progreso_parcial_y_escalar(messages)
```

```python
# Agent SDK: el resguardo es configuración
options = ClaudeAgentOptions(max_turns=10, max_budget_usd=0.50)
# al final: if result.subtype == "error_max_turns": la tarea NO terminó → diagnosticar o escalar
```

### Para el examen

- Terminación principal: **`stop_reason`**. Turn budget / `max_turns` / `max_budget_usd`: **red de seguridad**.
- Llegar al límite = **falla o escalamiento**, nunca "completado". `error_max_turns` no es `success`.
- "Subir el límite" no arregla un agente que no llega a `end_turn`. "Sacar el límite" tampoco.
- El límite lo cuenta el **runtime**, no el modelo.

### Cómo se une

El turn budget corta el loop de Rosa, pero recién en la décima vuelta y sin decirle nada útil. Para darse cuenta antes y hacer algo mejor, está el Tema 10.

---

## Tema 10 — Spinning and escalation (girar en falso y escalar a un humano)

### Qué es

No toda vuelta del loop es progreso. Un agente **avanza** (*making progress*) cuando cada vuelta trae algo nuevo: un dato, un paso completado, menos incertidumbre. Un agente **gira en falso** (**spinning**) cuando repite acciones parecidas sin resultados nuevos: las tools devuelven los mismos errores, el plan no cambia, el contexto crece pero el objetivo no se acerca. El turn budget lo termina cortando, pero tarde; conviene detectarlo antes.

El curso propone detectarlo con lógica explícita en el runtime:
- **Comparar observaciones sucesivas**: ¿son realmente distintas?
- **Contar llamadas repetidas** a la misma tool con los **mismos parámetros**.
- **Mirar la distancia** entre el estado actual y el objetivo, vuelta a vuelta.

📘 **Curso:** la comparación de observaciones no tiene texto oficial; es un patrón válido, no texto de la guía.

Cuando el agente está trabado, hay dos opciones, y la elección depende de si queda algo nuevo para probar:
- **Iterate** (iterar): solo si hay **información nueva** o un **enfoque distinto** para probar.
- **Escalate** (escalar): pasarle el caso a un humano (o a un sistema de respaldo) si no hay nada nuevo para probar, si falta información, o si la decisión excede lo que el agente está **autorizado** a hacer.

Escalar es una **válvula de seguridad diseñada, no un fracaso**: un agente que nunca escala puede terminar tomando decisiones que no se pueden deshacer. Y el control del loop no es solo un tema de rendimiento: es de **confiabilidad**. Un agente descontrolado agota cuotas de la API y genera costos inesperados; condiciones de terminación bien definidas hacen que el comportamiento sea predecible y auditable.

"Building effective agents" va en la misma línea: el agente tiene que obtener información real del entorno en cada paso (los resultados de las tools) y puede **pausar para pedir feedback humano** en puntos de control o cuando se traba.

### Ejemplo

Con detección de spinning, SoporteBot hubiera visto **a la tercera vuelta** que `get_order_status("TX-104300")` devolvía siempre el mismo error. No hay información nueva ni otro enfoque posible (el sistema está caído), así que corresponde **escalar**, no iterar.

Agregás tres defensas: el loop sale con cualquier `stop_reason` distinto de `tool_use` (Tema 8), un turn budget como red de seguridad (Tema 9) y una regla que escala a un humano ante llamadas repetidas idénticas. Rosa recibe: "Estamos con un problema en el sistema de pedidos; una persona del equipo te escribe en cuanto se resuelva". No es perfecto, pero es honesto.

### Cómo se configura

```python
# 📘 spin_guard del curso: misma tool con los mismos parámetros, más de 'limit' veces
import json
from collections import Counter
seen = Counter()

def is_spinning(call, limit=2):
    key = (call.name, json.dumps(call.input, sort_keys=True))
    seen[key] += 1
    return seen[key] > limit

if is_spinning(call):
    escalate("llamada idéntica repetida")   # a la tercera vez: escalar
```

### Para el examen

- Spinning = repetir sin nada nuevo. Se detecta con llamadas idénticas repetidas y observaciones que no cambian.
- **Iterar** solo con información nueva o enfoque distinto; si no, **escalar**.
- Escalar es un diseño, no una falla.
- Reintentar un error que no es transitorio (endpoint caído, credencial vencida) no cambia nada. (Los tipos de error vuelven en 1D y 2A.)

### Cómo se une

Con los Temas 8 a 10, SoporteBot sabe cuándo terminar, cuándo frenar y cuándo pedir ayuda. Queda una pregunta previa: ¿todo tiene que ser un agente? (Tema 11).

---

# Parte 5 — ¿Todo tiene que ser un agente?

## Tema 11 — When workflows outperform agents (cuándo un workflow le gana a un agente)

### Qué es

Después de ver lo que puede hacer un agente, la tentación es usarlo para todo. Pero si el camino se puede escribir de antemano, dejar que el modelo lo decida solo agrega costo y riesgo sin aportar nada. Un **workflow** le gana a un agente cuando se cumplen tres señales:
- La **entrada** es predecible y está bien definida.
- La **salida** tiene un formato conocido y se puede testear.
- **Todos los pasos** se pueden escribir en design time.

El curso lo resume así: la mayoría de las tareas reales están más cerca del workflow de lo que parece; **primero estructura, y agencia solo donde aporta valor**. Anthropic dice lo mismo: empezar por la solución más simple posible.

¿Por qué no usar un agente "por las dudas"? Porque los agentes tienen **costos ocultos**, que no se ven en la demo pero sí en producción:
- Más **tokens** por corrida.
- Más **latencia** (replanificar lleva tiempo que no planeaste).
- Más **failure surface** (superficie de falla): cada decisión autónoma es un punto donde algo puede salir mal, y un error se puede propagar.
- Más difícil de **depurar**: reconstruir el contexto de muchas vueltas lleva mucho más que leer los logs de un workflow.

¿Cuándo sí se justifica un agente? Cuando el problema es **abierto** y es difícil o imposible prever cuántos pasos va a llevar. El curso lo baja a tres señales: el objetivo es abierto, la secuencia de tools no se puede prever en design time, y hace falta **replanificar** en el medio.

Una trampa sutil: **que un paso use un modelo no lo convierte en agente.** Y que el sistema tenga tools tampoco lo vuelve agéntico. Las slides lo muestran con prompt chaining (Tema 12): parece agéntico porque hay un modelo en cada paso, pero la secuencia la fijó el desarrollador. Lo que importa es quién decide el camino (Tema 1).

### Ejemplo

Entusiasmada con SoporteBot, la gerencia pide dos cosas más:
1. Que cada lunes se genere un **reporte** con los reclamos de la semana, agrupados por categoría.
2. Que cada mail que entra a soporte@tiendax.com se **clasifique** (envío, reembolso, producto, otro) y vaya a la bandeja del equipo correcto.

Lucas propone: "Hagamos un agente para cada cosa".

Antes de decir que sí, mirás las tareas. El reporte siempre tiene los mismos pasos: traer los reclamos, agruparlos, resumirlos, armar el documento. La clasificación también: leer el mail, elegir una categoría de cuatro, mandarlo. En ninguna de las dos hay que improvisar el camino. Las dos son **workflows**.

¿Y la devolución de María (Tema 6)? Esa sí es un agente: no sabés de antemano cuántos pasos va a llevar.

### Para el examen

- Entrada predecible + salida conocida + pasos escribibles de antemano → **workflow**.
- Objetivo abierto + secuencia imprevisible + replanificación → **agente**.
- "Usa Claude para decidir algo" no alcanza para ser agente: tiene que decidir **el camino**.

### Cómo se une

Si es un workflow, ¿qué forma tiene? Anthropic describe cinco patrones (Tema 12).

---

## Tema 12 — Workflow patterns (los cinco patrones de workflow)

### Qué es

Una vez que decidiste que algo es un workflow, no hace falta inventar la forma desde cero: Anthropic describe cinco patrones en "Building effective agents", y el examen espera que los reconozcas por su descripción. Un **prompt** es el texto de instrucciones que se le manda al modelo; varios patrones encadenan o combinan prompts:

- **Prompt chaining** (encadenar prompts): pasos fijos en secuencia, donde la salida de uno es la entrada del siguiente. Cada paso es angosto y se puede testear por separado.
- **Routing** (ruteo): clasificar la entrada y mandarla al camino especializado que corresponde. El router puede usar un modelo para clasificar, pero **la topología queda fija**: las ramas las escribió el desarrollador.
- **Parallelization** (paralelización): correr partes en paralelo y juntar los resultados en un punto de sincronización.
- **Orchestrator-workers** (orquestador y trabajadores): un modelo central divide la tarea y reparte subtareas que **no se pueden predecir de antemano**. (Lo ves en 1B y 1C.)
- **Evaluator-optimizer** (evaluador-optimizador): un modelo genera y otro evalúa y pide mejoras, en ciclos. Sirve cuando hay **criterios claros** para evaluar y refinar mejora el resultado.

> ⚠️ **En el curso vas a escuchar otra cosa.** El companion (el resumen escrito del curso) habla de "cuatro patrones": chaining, routing, parallelization y orchestrator-subagent, y deja afuera evaluator-optimizer. Las slides sí listan los cinco de Anthropic en la p. 46, pero en la p. 41 nombran otros cinco (Sequential, Conditional, Iterative, Parallel, Retrieval) que **no** son la lista oficial. **Para el examen:** reconocé los **cinco de Anthropic**, con evaluator-optimizer. Si aparece "un modelo redacta y otro critica y pide mejoras", es evaluator-optimizer.

### Ejemplo

- El **reporte de los lunes** es **prompt chaining**: traer los reclamos, agruparlos, resumirlos y armar el documento, siempre en ese orden y cada paso con la salida del anterior.
- La **clasificación de mails** es **routing**: Claude elige una categoría y el código manda el mail a la bandeja fija de esa categoría.

### Cómo se ve: routing en TiendaX

```python
BANDEJAS = {"envio": bandeja_envios, "reembolso": bandeja_reembolsos,
            "producto": bandeja_productos, "otro": bandeja_general}

categoria = client.messages.create(
    model="claude-sonnet-5-5", max_tokens=5,
    system="Clasificá el mail. Respondé con una palabra: envio, reembolso, producto u otro.",
    messages=[{"role": "user", "content": mail}],
).content[0].text.strip().lower()

BANDEJAS.get(categoria, bandeja_general).enviar(mail)   # topología fija: la eligió el desarrollador
```

Claude decide **la categoría**, no el camino. Sigue siendo workflow.

### Para el examen

- Los cinco: **prompt chaining, routing, parallelization, orchestrator-workers, evaluator-optimizer**.
- Routing con un modelo clasificando sigue siendo **workflow**.
- Orchestrator-workers es el que se usa cuando las subtareas **no** se pueden prever.

### Cómo se une

Ya sabés reconocer cada patrón. Falta el criterio para elegir entre workflow, agente o una mezcla (Tema 13).

---

## Tema 13 — Choosing the architecture (elegir la arquitectura): ejes, over-engineering y complejidad incremental

### Qué es

Elegir entre workflow y agente no es elegir "el mejor": cada uno gana algo y pierde algo. El curso propone evaluar cada elección en tres pares de **tradeoff axes** (ejes de compensación), que ayudan a ver qué estás cambiando por qué:
- **Cost vs. capability** (costo vs. capacidad): un agente gasta más tokens por corrida; se justifica solo si esa capacidad hace falta **hoy**.
- **Auditability vs. flexibility** (auditabilidad vs. flexibilidad): un workflow se audita paso a paso; un agente cambia auditabilidad por flexibilidad.
- **Reliability vs. adaptability** (confiabilidad vs. adaptabilidad): un workflow falla de forma predecible en pasos conocidos; un agente se adapta, pero falla de formas más variadas y difíciles de reproducir.

📘 **Curso:** el resumen de la p. 59 de las slides dice "tres ejes" y lista cuatro palabras sueltas (costo, auditabilidad, confiabilidad, adaptabilidad); es la misma idea.

El error que estos ejes buscan evitar es el **over-engineering** (sobreingeniería): agregar complejidad (por ejemplo, autonomía agéntica) que cuesta y arriesga más de lo que aporta para la tarea real. Para no caer ahí, el curso propone **cuatro preguntas** ante cada tarea nueva:
1. ¿Cada paso se puede escribir de antemano?
2. ¿El formato de salida se conoce y se puede testear?
3. ¿Hace falta elegir tools en tiempo de ejecución?
4. ¿Recuperarse de una falla requiere decisiones dinámicas en el medio?

Cuantas más respuestas apunten a "no se puede prever" (la slide pide **al menos dos**), más se justifica un agente. 📘 **Curso:** la slide cuenta "no" en las cuatro, aunque en la 3 y la 4 la respuesta que apunta a agente es "sí"; lo que importa es la dirección, cuántas apuntan a "no se puede prever".

Si igual hace falta algo de agencia, el consejo de diseño del curso es la **incremental complexity** (complejidad incremental), que consiste en agregarla de a poco y solo donde se demuestra necesaria:
1. Armá y validá primero el workflow.
2. Encontrá el paso **específico** que falla porque necesita flexibilidad.
3. Reemplazá **solo ese paso** por comportamiento agéntico.

El porqué: simplificar después es mucho más difícil que agregar agencia de a poco.

Tampoco hay que elegir todo o nada. Existen los **híbridos**: un workflow que rutea y prepara, y un agente que resuelve el caso abierto. El curso da tres escenarios tipo:
- **Workflow:** extraer datos estructurados de un documento con formato fijo; alcanza con un prompt chain con validación.
- **Agente:** investigar un tema en fuentes web abiertas; hace falta un agente con planificación.
- **Híbrido:** rutear consultas a especialistas y después sintetizar las respuestas; un workflow (ruteo fijo) alimenta a un agente (síntesis dinámica).

### Ejemplo

El reporte queda como prompt chaining. La clasificación de mails, como routing. SoporteBot sigue siendo el único agente, porque es el único que atiende problemas abiertos.

Y si mañana la clasificación de mails empieza a fallar con un tipo de mail ambiguo, no se convierte todo en agente: se reemplaza **solo el paso** que falla.

### Para el examen

- Ante la duda, la respuesta correcta suele ser **la arquitectura más simple que resuelve el problema**.
- La opción "un agente autónomo, más flexible" para una tarea predecible es **over-engineering**.
- Complejidad incremental: workflow primero, agencia solo en el paso que la necesita.
- Una secuencia fija va **en código**, no escrita como pasos en el system prompt de un agente.

### Cómo se une

Cierra el círculo del Tema 1: el agente es la herramienta para cuando el camino no se puede dibujar de antemano. Para todo lo demás, workflow.

---

## Cómo se une todo

1. Lo que separa chatbot, workflow y agente es **quién decide el camino**: nadie, el desarrollador o el modelo (Tema 1).
2. Para actuar, el modelo necesita **tools**: las elige por la **descripción**, las **pide** y tu runtime las **ejecuta** (Tema 2).
3. La respuesta trae **bloques** (texto y `tool_use` juntos) y un **`stop_reason`** que dice por qué paró (Tema 3).
4. El resultado vuelve como **`tool_result`** en rol `user`, con su `tool_use_id`, justo después de la respuesta **completa** del assistant; si falló, con `is_error: true` (Tema 4).
5. Si Claude pide varias tools juntas, **todos los resultados van en un solo mensaje** (Tema 5).
6. Repetir eso hasta resolver es el **agentic loop**: Claude decide la siguiente tool mirando cada resultado, no un árbol fijo (Tema 6).
7. Todo vive en el **context window**, que es memoria de trabajo efímera: lo que no está en el historial no pasó (Tema 7).
8. El loop **termina por `stop_reason`**, nunca por texto ni por palabras clave; `max_tokens` no es "terminado" (Tema 8).
9. El **turn budget** (y `max_turns` en el SDK) es una **red de seguridad**, no el mecanismo principal; llegar al límite es una falla (Tema 9).
10. Si el agente **gira en falso**, se escala a un humano (Tema 10).
11. Y antes de todo eso: si el camino se puede escribir de antemano, es un **workflow** (Temas 11 a 13).

## Lo que viene

SoporteBot ya resuelve consultas de un paso y de varios pasos. Entonces llega el mensaje de Martín: "El pedido TX-104233 llegó con una zapatilla rota, me cobraron dos veces el TX-104251 y quiero cambiar la dirección de envío del TX-104300, que todavía no salió". SoporteBot resuelve el cobro doble a fondo… y responde, sin tocar los otros dos problemas. El loop funcionó perfecto: lo que faltó es **partir un problema grande en partes** antes de empezar. De eso se trata 1B · Task Decomposition & Planning.

---

## Las trampas del examen

Cada trampa tiene el mismo orden: la situación, **qué elegir en el examen (✅)**, las opciones que tientan (❌) con por qué tientan y por qué están mal, y una regla para recordar.

### Grupo: Cuándo termina el loop

#### Trampa 1 · ¿Cómo sabe el loop que terminó?

**La situación.** SoporteBot le contestó a Pedro "Voy a revisar tu pedido" y no hizo nada más (Tema 8).

**✅ En el examen elegí:** decidir por `stop_reason`. Si es `"tool_use"`, ejecutás las tools y seguís. Con cualquier otro valor salís del loop y revisás **cuál** fue: `end_turn` es la tarea completa, pero `max_tokens` es una respuesta cortada.

**❌ Las que tientan:**

❌ **"Cortar el loop cuando la respuesta trae texto"** (por ejemplo, si `content[0].type == "text"`).
- *Tienta porque:* parece lógico; si Claude ya le habló al cliente, ya debería haber terminado.
- *Está mal porque:* Claude puede mandar texto **y** un `tool_use` en la misma respuesta. Cortás justo antes de que actúe.

❌ **"Buscar en el texto palabras como 'listo', 'done' o '[DONE]'"** (aunque se lo pidas en el system prompt).
- *Tienta porque:* es fácil de programar y parece confiable si Claude "promete" decirlo.
- *Está mal porque:* el lenguaje natural es ambiguo. Claude puede decir "listo" a mitad de camino o terminar sin decirlo. La guía lo nombra como anti-pattern.

❌ **"Si el loop salió, la tarea está completa"** (sin mirar qué `stop_reason` fue).
- *Tienta porque:* salió del loop y hay texto para mostrar.
- *Está mal porque:* si fue `max_tokens`, la respuesta está truncada. Hay que subir el límite o pedir que continúe.

❌ **"Terminar cuando `finish_reason` sea `stop`".**
- *Tienta porque:* suena a un campo real.
- *Está mal porque:* `finish_reason` es de otra API. En Claude el campo es `stop_reason`.

> 🧠 **Para recordar:** el texto no termina el loop. Lo termina `stop_reason`, y salir no es lo mismo que terminar.

#### Trampa 2 · El agente choca contra el límite de vueltas

**La situación.** Un agente de TiendaX llega seguido a su límite de 10 vueltas y deja tareas a medias (Temas 9 y 10).

**✅ En el examen elegí:** mantener el límite **como red de seguridad** y **diagnosticar** por qué no llega a `end_turn`. Puede estar girando en falso, puede fallar una tool o puede faltarle información. Si repite la misma llamada sin nada nuevo, se escala a un humano.

**❌ Las que tientan:**

❌ **"Subir el límite a 50" o "reanudar con más vueltas".**
- *Tienta porque:* el síntoma es "se corta antes", y subir el límite lo hace desaparecer.
- *Está mal porque:* no ataca la causa. Si el agente gira en falso, más vueltas solo cuestan más plata. (Reanudar con más vueltas solo vale si el agente venía avanzando de verdad.)

❌ **"Sacar el límite: los caps son un anti-pattern".**
- *Tienta porque:* la guía critica los caps.
- *Está mal porque:* lo que critica es usarlos como mecanismo **principal** de parada. Sin límite, un loop roto corre para siempre.

❌ **"Reintentar automáticamente la tool que falla".**
- *Tienta porque:* los reintentos parecen robustos.
- *Está mal porque:* si el error no es transitorio (un endpoint caído, una credencial vencida), reintentar no cambia nada.

> 🧠 **Para recordar:** el límite corta loops rotos; `stop_reason` termina tareas.

### Grupo: La mecánica de la API

#### Trampa 3 · Cómo devolver los resultados al historial

**La situación.** Claude pide `get_order_status` para dos pedidos de Martín en la misma respuesta, y el historial ya es largo (Temas 4, 5 y 7).

**✅ En el examen elegí:** agregar la respuesta de Claude **completa** como mensaje `assistant` (con los bloques `tool_use`), y después **un solo** mensaje `user` con **todos** los `tool_result`, cada uno con su `tool_use_id`. Si alguno falló, va igual, con `is_error: true` y un mensaje claro.

**❌ Las que tientan:**

❌ **"Un mensaje `user` por cada resultado".**
- *Tienta porque:* parece más ordenado.
- *Está mal porque:* la API espera todos los resultados juntos. Separarlos rompe el formato y le enseña a Claude a no pedir tools en paralelo.

❌ **"Resumir los resultados, o guardar solo el texto del assistant, para ahorrar tokens".**
- *Tienta porque:* ahorra tokens y parece prolijo.
- *Está mal porque:* Claude no recuerda nada entre llamadas. Lo que no está en el historial, no pasó. Y sin el bloque `tool_use`, el `tool_result` queda huérfano.

❌ **"No devolver el resultado de la tool que falló, para que Claude la reintente".**
- *Tienta porque:* parece que así la reintenta solo.
- *Está mal porque:* todo `tool_use` necesita su `tool_result`. El error se informa con `is_error: true`.

❌ **"Poner primero un texto explicando el error y después los `tool_result`".**
- *Tienta porque:* agregar contexto parece útil.
- *Está mal porque:* dentro del mensaje, los `tool_result` van primero. El texto, si hace falta, va después.

> 🧠 **Para recordar:** respuesta completa como assistant; un solo mensaje user con todos los resultados.

### Grupo: ¿Todo tiene que ser un agente?

#### Trampa 4 · ¿Workflow o agente?

**La situación.** La gerencia pide clasificar los mails de soporte en cuatro bandejas, y Lucas propone un agente (Temas 11 a 13).

**✅ En el examen elegí:** un **workflow** (en este caso, routing). Si los pasos se pueden escribir de antemano y la salida se conoce, es un workflow. El agente se reserva para cuando el camino no se puede prever.

**❌ Las que tientan:**

❌ **"Un agente autónomo, que es más flexible".**
- *Tienta porque:* suena más moderno y más capaz.
- *Está mal porque:* no hay nada que decidir en el camino. Suma costo, latencia y formas de fallar (over-engineering).

❌ **"Es un agente porque usa Claude para decidir la categoría".**
- *Tienta porque:* hay un modelo tomando una decisión.
- *Está mal porque:* lo que define a un agente es que el modelo elige **el camino**. En el routing las ramas y el orden los fijó el desarrollador.

❌ **"Un agente con los pasos escritos en orden en el system prompt".**
- *Tienta porque:* parece que "fija" la secuencia.
- *Está mal porque:* una secuencia fija va en código, no en un prompt. En el prompt es menos confiable y menos auditable.

> 🧠 **Para recordar:** si podés dibujar el camino antes de empezar, es un workflow.

---

## Checklist oficial

**Tarea 1.1 — Design and implement agentic loops for autonomous task execution**

*Knowledge of*
- [x] El ciclo de vida del agentic loop: mandar requests a Claude, inspeccionar `stop_reason` (`"tool_use"` vs `"end_turn"`), ejecutar las tools pedidas y devolver los resultados para la siguiente iteración → **Temas 3, 4 y 6**
- [x] Cómo se agregan los resultados de las tools al historial para que el modelo razone la siguiente acción → **Temas 4, 5 y 7** (rol user, `tool_use_id`, orden, paralelo)
- [x] La diferencia entre decisiones guiadas por el modelo y árboles de decisión o secuencias de tools preconfiguradas → **Temas 1, 6 y 11**

*Skills in*
- [x] Implementar el control de flujo del loop: continuar con `"tool_use"`, terminar con `"end_turn"` → **Temas 6 y 8**
- [x] Agregar los resultados de las tools al contexto entre iteraciones → **Temas 4, 6 y 7** (y Trampa 3)
- [x] Evitar los anti-patterns: parsear lenguaje natural para decidir terminar, usar límites arbitrarios de iteraciones como mecanismo principal de parada, y usar el texto del assistant como indicador de finalización → **Temas 8 y 9** (Trampas 1 y 2)

**De la documentación, no de la guía** (vale saberlo; la guía no lo pregunta directo): client vs. server tools (Tema 2) · reglas de formato del `tool_result` e `is_error` (Tema 4) · reglas del parallel tool use (Tema 5) · todos los valores de `stop_reason` y su manejo (Tema 8) · Agent SDK: `max_turns`, `max_budget_usd` y los `subtype` del `ResultMessage` (Tema 9).

**📘 Curso (útil para entender; lecciones 1–6):** chatbot vs. workflow vs. agente, LLM solo = tokens (Tema 1) · augmented LLM, client vs. server tools, calidad de las descripciones, categorías de tools y side effects (Tema 2) · atomic unit (Tema 4) · llamadas en paralelo (Tema 5) · perception/reasoning/action/observation, four pillars, dynamic planning, gather/act/verify, éxito/error/parcial (Tema 6) · in-context memory efímera (Tema 7) · cuatro condiciones de terminación, causas de loops infinitos, turn budget (Tema 9) · spinning, iterar vs. escalar, loop control como confiabilidad (Tema 10) · señales de workflow, costos ocultos de los agentes (Tema 11) · cinco patrones de workflow, router con topología fija (Tema 12) · ejes de decisión, over-engineering, cuatro preguntas, complejidad incremental, híbridos y escenarios tipo (Tema 13).

---

## Autoevaluación oral

Respondé en voz alta, sin mirar:

1. ¿Qué diferencia a un chatbot, un workflow y un agente? ¿Quién decide el camino en cada uno?
2. Claude devolvió una respuesta con un bloque de texto y un bloque `tool_use`. Contá paso a paso qué hace tu runtime y qué mensajes agrega al historial.
3. ¿Por qué "hay texto en la respuesta" y "dice 'listo'" son malas señales de terminación? ¿Cuál es la buena? ¿Qué hacés si `stop_reason` es `max_tokens`?
4. Un agente choca seguido contra su límite de 10 vueltas (o el SDK devuelve `error_max_turns`). ¿Qué significa eso y qué hacés (y qué no hacés)?
5. Te piden automatizar la clasificación de facturas de proveedores en tres categorías. ¿Workflow o agente? ¿Qué patrón? ¿Qué te haría cambiar de opinión?

---

## Preguntas tipo examen

Las preguntas tipo examen de este capítulo están en [`04-practica/modulo-1.md`](../04-practica/modulo-1.md), junto con las del resto del módulo 1. Hacelas cuando termines **todos** los capítulos del módulo, de a una y sin mirar la respuesta.

---

## Revisión contra el blueprint oficial

Qué puede salir en el examen sobre la tarea 1.1 que el curso de Jacob **no cubre o cubre flojo**, y dónde quedó explicado acá:

1. **Todos los valores de `stop_reason`.** El curso solo usa `tool_use` y `end_turn`. La documentación tiene siete: también `max_tokens` (truncado; si cortó un `tool_use`, reintentar con más tokens), `stop_sequence`, `pause_turn` (solo server tools: reenviar), `refusal` (HTTP 200, no error) y `model_context_window_exceeded`. Los errores de la API son HTTP 4xx/5xx, no un `stop_reason`. → Tema 8.
2. **Los tres anti-patterns de terminación con el nombre de la guía** (parsear lenguaje natural, texto del assistant como señal, cap de vueltas como mecanismo principal). El curso no los nombra como anti-patterns y llama al turn budget "la defensa principal". → Temas 8 y 9, con el recuadro de qué responder.
3. **Forma canónica del loop** (seguir mientras sea `tool_use`, salir con cualquier otro valor). El código de las slides hace lo inverso (`== "end_turn"`) y ejecutaría tools con `max_tokens`. → Temas 6 y 8.
4. **Reglas de formato del `tool_result`.** El curso muestra el "atomic unit", pero no las reglas: inmediatamente después del assistant, sin mensajes en el medio; `tool_result` primero y texto después; `is_error: true` con mensaje instructivo; `content` como texto o bloques; respuesta vacía con `end_turn` si se mete texto después de los resultados. → Tema 4.
5. **Parallel tool use.** El curso dice "todos en un turno"; la documentación agrega que separarlos le enseña a Claude a no paralelizar, y que una llamada que no ejecutás igual lleva su `tool_result` con `is_error`. → Tema 5.
6. **Agent SDK: `max_turns`, `max_budget_usd` y los `subtype` del resultado** (`error_max_turns`, `error_max_budget_usd`, `error_during_execution`, `error_max_structured_output_retries`; solo `success` trae `result`). Por defecto no hay límite. Llegar al límite = la tarea no terminó. El curso no lo menciona. → Tema 9.
7. **Cinco patrones de workflow, con evaluator-optimizer.** El companion dice cuatro. → Tema 12, con el recuadro de qué responder.
8. **Client vs. server tools** (quién arma el `tool_result`) y su relación con `pause_turn`. El curso lo menciona en una línea. → Temas 2 y 8.

Una nota: según las copias de la guía, ninguna de las 12 preguntas de muestra oficiales trata directamente sobre agentic loops o `stop_reason`. Las preguntas de esta tarea van a tener la forma de los distractores de las Trampas 1 a 3. No encontré otros huecos para 1.1. Lo que el curso agrega por su cuenta (detección de spinning comparando observaciones, las cuatro preguntas con umbral de dos) queda marcado como 📘: es útil, pero no es texto oficial.

