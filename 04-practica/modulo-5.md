# Preguntas — Módulo 5 (Context Management & Reliability · 5A–5D)

## Preguntas de fin de módulo

### Escenario: Customer Support Resolution Agent

You are building SoporteBot, TiendaX's customer support resolution agent, using the Claude Agent SDK. It handles returns, refunds, billing disputes, and order issues through four MCP tools: `get_customer`, `lookup_order`, `process_refund`, and `escalate_to_human`. The target is 80%+ first-contact resolution, escalating only the cases that genuinely need a human.

#### P1 · 5A · 5.1 · Customer Support Resolution Agent
To control context size, SoporteBot replaces every turn older than the last ten with a running summary. In conversations longer than 25 turns, QA found that 31% of refunds were issued for the wrong amount, and the agent often asked again for an order number the customer had already given. A teammate already added "Preserve all amounts, dates, and order numbers" to the summarizer prompt, with little effect. What's the most effective way to address this?

A) Summarize every five turns instead of every ten, so that each pass condenses less of the conversation and fewer details are dropped.

B) Extract amounts, dates, order numbers, and statuses into a case facts block included in every prompt, outside the summarized history.

C) Switch to a model with a larger context window and stop summarizing, so that the full conversation always fits without losing details.

D) Have the summarizer append a structured list of amounts, dates, and order numbers at the end of each summary it produces.

<details>
<summary>Ver respuesta</summary>

**Respuesta correcta: B**

**Why (es):** El resumen progresivo cambia precisión por fluidez: lo primero que se pierde son los números, las fechas y lo que el cliente dijo que esperaba, y la pérdida se acumula porque cada pasada resume el resumen anterior. La guía (5.1) pide **extraer los datos transaccionales a un bloque persistente de "case facts", incluido en cada prompt y fuera del historial resumido**: como el bloque no pasa por el resumidor, los datos no se degradan. El enunciado ya dice que pedirle al resumidor que conserve los números no alcanzó.

**Distractors (es):**
- A: tienta porque resúmenes más chicos parecen más controlados; está mal porque más pasadas de resumen significan más pérdida acumulada, y los datos siguen dependiendo del resumidor.
- C: tienta porque si no se resume no se pierde nada; está mal porque solo posterga el problema: con más tokens la precisión baja igual (context rot), y "modelo con más contexto" es un distractor clásico.
- D: tienta porque es estructurado y se parece a la correcta; está mal porque la lista queda **dentro** del resumen, así que en la próxima pasada se vuelve a condensar. La clave es que los hechos vivan **fuera** del historial resumido.

**Review:** Capítulo 15 (5A), Tema 2 — Por qué el resumen progresivo pierde datos y Tema 3 — El bloque de case facts; Trampa 1 · El monto que desaparece.

**Pista de lectura (es):** "A teammate already added 'Preserve all amounts, dates, and order numbers' to the summarizer prompt, with little effect" → "un compañero ya agregó 'conservá todos los montos, fechas y números de pedido' al prompt del resumidor, con poco efecto" ("already" + resumidor: cualquier opción que siga dependiendo del resumen está descartada).

</details>

#### P2 · 5A · 5.1 · Customer Support Resolution Agent
A customer reports two problems in one conversation: a TV from order 88213 that arrived broken ($450,000, replacement approved) and a duplicate charge on order 88247 ($12,500, under review by payments). SoporteBot's case facts block has a single `order_id`, `amount`, and `status`, which are overwritten whenever the customer switches topics. Twice this week, it called `process_refund` for $450,000 against order 88247. What change best prevents this without losing the details of either issue as the conversation moves between them?

A) Keep the single set of fields, and instruct the agent to confirm the order number with the customer before every `process_refund` call.

B) Keep only the issue under discussion in the case facts block, and move the other issue's details into the summarized history.

C) Replace the case facts block with a detailed summary that lists every order number, amount, and status from the conversation.

D) Store each issue as its own structured entry in the case facts block, with its own order ID, amount, and status.

<details>
<summary>Ver respuesta</summary>

**Respuesta correcta: D**

**Why (es):** En una sesión con varios problemas, un solo juego de campos que se pisa hace que los datos de un problema terminen aplicados al otro (el monto del televisor sobre el cobro duplicado). La guía (5.1) pide **extraer y persistir los datos estructurados de cada problema en una capa separada** (ID de pedido, monto y estado de cada uno). Así ninguno se pierde ni se mezcla cuando el cliente va y vuelve entre temas, que es justo la condición del enunciado.

**Distractors (es):**
- A: tienta porque la confirmación parece una red de seguridad; está mal porque no arregla la causa (los datos se siguen pisando: el monto equivocado puede salir igual con el pedido correcto) y es una instrucción probabilística.
- B: tienta porque deja el bloque chico y enfocado; está mal porque rompe la condición "without losing the details of either issue": el problema que pasa al resumen pierde su monto y su estado.
- C: tienta porque más detalle parece más precisión; está mal porque mezcla los dos problemas en un solo texto y además vuelve a depender de un resumen.

**Review:** Capítulo 15 (5A), Tema 3 — Una capa por cada problema; Trampa 2 · Dos problemas mezclados.

**Pista de lectura (es):** "which are overwritten whenever the customer switches topics" → "que se sobrescriben cada vez que el cliente cambia de tema" (un solo juego de campos para dos problemas: la causa del cruce) + "without losing the details of either issue" → "sin perder los datos de ninguno de los dos problemas" (condición de alcance: descarta mandar uno al resumen).

</details>

#### P3 · 5A · 5.1 · Customer Support Resolution Agent
`lookup_order` returns 43 fields per order, including billing address, line-item taxes, and carrier scan history. In return conversations, SoporteBot calls it three or four times, and after the third call it began confusing `purchased_at` with `delivered_at` when checking the 30-day return window. Return decisions use only five of those fields. Which approach should you take while keeping the full order record available to the other workflows that rely on it?

A) Wrap `lookup_order` for the returns flow so that it returns only the five return-relevant fields before the result enters the context.

B) Enable context editing so that older `lookup_order` results are cleared from the history once the context passes a token threshold.

C) Change the orders API to return only the five return-relevant fields to every consumer, since support rarely needs the other 38.

D) Keep the full response, and instruct the agent to always use `delivered_at`, never `purchased_at`, when checking the return window.

<details>
<summary>Ver respuesta</summary>

**Respuesta correcta: A**

**Why (es):** Las respuestas de las tools se acumulan en el contexto y consumen tokens de forma desproporcionada (la guía usa justo el ejemplo de 40+ campos cuando importan 5). La Skill de 5.1 es **recortar la respuesta a los campos relevantes antes de que se acumule**, en el wrapper de la tool del flujo de devoluciones. La API completa no se toca, así que los otros flujos siguen recibiendo los 43 campos (condición de alcance).

**Distractors (es):**
- B: tienta porque libera espacio automáticamente y es una función real de la API; está mal porque actúa **después** de que el ruido se acumuló: la guía pide recortar **antes**.
- C: tienta porque también deja 5 campos y es la que más ahorra; está mal porque rompe la condición "while keeping the full order record available to the other workflows": el recorte va en el wrapper del flujo, no en la API de todos.
- D: tienta porque ataca el síntoma visible (las dos fechas confundidas); está mal porque los 43 campos siguen entrando en cada llamada y van a enterrar otros datos.

**Review:** Capítulo 15 (5A), Tema 4 — Recortar las respuestas de las tools antes de que se acumulen; Trampa 4 · Los 43 campos.

**Pista de lectura (es):** "while keeping the full order record available to the other workflows that rely on it" → "manteniendo el registro completo del pedido disponible para los otros flujos que lo usan" (el recorte es local al flujo de devoluciones, no global).

</details>

#### P4 · 5A · 5.1 · Customer Support Resolution Agent
To cut API costs, a developer changed SoporteBot's integration so that each request sends only the system prompt, the case facts block, and the customer's newest message. Since the release, the agent asks again for the size a customer requested two messages earlier and contradicts its own previous answers. The developer already verified that the case facts block is correct and present in every request. What is the most likely root cause?

A) The case facts block sits before the customer's message, so the model gives it less attention than the newest message in the request.

B) The context window is too small for the system prompt, so the API silently truncates earlier turns before they reach the model.

C) The API keeps no conversation state between requests, so any turn left out of a request no longer exists for the model.

D) The summarizer runs too rarely, so the turns the customer refers to have not yet been condensed into the conversation history.

<details>
<summary>Ver respuesta</summary>

**Respuesta correcta: C**

**Why (es):** La API es **stateless**: no recuerda nada entre llamadas. Para que Claude mantenga la coherencia, la aplicación tiene que **mandar el historial completo en cada request** (punto de Knowledge de 5.1). El cambio "para ahorrar" sacó el historial, así que lo que el cliente dijo dos mensajes antes no existe para el modelo. El tamaño se controla con case facts y recortes, no cortando el historial.

**Distractors (es):**
- A: tienta porque el orden del contenido importa (lost in the middle); está mal porque acá el dato perdido ni siquiera está en el request, y el enunciado dice que el bloque es correcto.
- B: tienta porque "se pierden los turnos viejos" suena a límite de ventana; está mal porque la API no trunca en silencio (devuelve error 400), y además los turnos ya no se mandan.
- D: tienta porque el resumen es el otro gran tema de 5.1; está mal porque no hay historial que resumir: el problema es que el request no lo incluye.

**Review:** Capítulo 15 (5A), Tema 1 — La ventana de contexto y el historial completo; Trampa 8 · El bot que no se acuerda.

**Pista de lectura (es):** "each request sends only the system prompt, the case facts block, and the customer's newest message" → "cada request manda solo el system prompt, el bloque de case facts y el último mensaje del cliente" ("only … the newest message" = el historial no viaja; lo que no está en el request, no existe).

</details>

#### P5 · 5B · 5.2 · Customer Support Resolution Agent
A customer's first message reads: "I want to talk to a real person about order 77120, not a bot." Logs show that SoporteBot then calls `get_customer` and `lookup_order`, explains that the order is out for delivery, and asks whether that solves the problem before calling `escalate_to_human`. In 40% of these conversations, the customer abandons the chat before reaching a person. What's the most effective way to address this?

A) Have the agent try to resolve the issue first whenever `lookup_order` shows that the order is in a state covered by policy.

B) Add a sentiment check that escalates immediately when the message scores as highly negative, and otherwise lets the agent investigate first.

C) Have the agent acknowledge the request and gather the full order details first, so that the human receives a complete handoff summary.

D) Instruct the agent to call `escalate_to_human` immediately when a customer explicitly asks for a person, passing along what it already knows.

<details>
<summary>Ver respuesta</summary>

**Respuesta correcta: D**

**Why (es):** La guía (5.2) dice que un **pedido explícito de una persona se honra de inmediato, sin investigar primero**. El cliente ya decidió; investigar antes (aunque sea "para ayudar") lo hace esperar y lo frustra más, como muestra el 40% de abandono. El traspaso lleva un resumen estructurado con **lo que ya se sabe** (cliente, pedido 77120, el pedido de hablar con una persona), no lo que habría que investigar.

**Distractors (es):**
- A: tienta porque resolver al primer contacto es la meta del escenario; está mal porque ignora la decisión del cliente: el pedido explícito es un disparador de escalamiento, no una oportunidad de resolver.
- B: tienta porque escala rápido a algunos clientes; está mal porque el sentimiento no es el disparador: un cliente educado que pide una persona igual tiene que ser escalado ya.
- C: tienta porque un handoff completo es buena práctica (1D); está mal porque reproduce el problema del enunciado: investigar antes de honrar el pedido. "Ya" significa con lo que se sabe.

**Review:** Capítulo 16 (5B), Tema 2 — Pedido explícito vs. cliente frustrado; Trampa 2 · "Quiero hablar con una persona".

**Pista de lectura (es):** "then calls `get_customer` and `lookup_order` … before calling `escalate_to_human`" → "después llama a `get_customer` y `lookup_order` … antes de llamar a `escalate_to_human`" (investiga antes de escalar: es justo lo que la guía dice que no hay que hacer ante un pedido explícito).

</details>

#### P6 · 5B · 5.2 · Customer Support Resolution Agent
After a change that escalates every message with strongly negative wording, the human queue doubled. In a sample of 300 of these escalations, 70% looked like a customer who wrote, "Third time you've sent the wrong size, this is ridiculous!" about a size exchange SoporteBot completes in two tool calls; none of them had asked for a person. Which approach should you take while still honoring customers who do want a human?

A) Have the agent acknowledge the frustration and offer to complete the exchange, escalating only if the customer then reiterates that they want a person.

B) Have the agent apologize and escalate only frustrated customers with high-value orders, so that the human queue focuses on revenue at risk.

C) Raise the negative-sentiment threshold so that only the angriest 10% of messages escalate, keeping the automatic escalation path otherwise unchanged.

D) Have the agent complete the exchange without addressing the complaint, and defer any request for a person until the exchange is confirmed.

<details>
<summary>Ver respuesta</summary>

**Respuesta correcta: A**

**Why (es):** La guía (5.2) distingue el pedido explícito de la frustración: si el cliente está frustrado pero **no pidió una persona** y el problema **está dentro de lo que el agente puede resolver**, el agente **reconoce la frustración y ofrece resolverlo**, y escala **solo si el cliente reitera** que quiere una persona. Eso baja la cola y respeta la condición del enunciado.

**Distractors (es):**
- B: tienta porque suena a priorización de negocio; está mal porque el valor del pedido no es un disparador de escalamiento de la guía, y sigue escalando casos simples.
- C: tienta porque baja la cola con un cambio mínimo; está mal porque el sentimiento no indica complejidad: un cliente muy enojado con un cambio de talle se seguiría escalando.
- D: tienta porque resuelve rápido; está mal porque rompe la condición "while still honoring customers who do want a human": postergar un pedido de persona es lo contrario de lo que pide la guía.

**Review:** Capítulo 16 (5B), Tema 2 — Pedido explícito vs. cliente frustrado y Tema 4 — Sentimiento y confianza no sirven; Trampa 3 · El cliente enojado.

**Pista de lectura (es):** "none of them had asked for a person" → "ninguno había pedido una persona" (frustración ≠ pedido explícito: se ofrece resolver) + "while still honoring customers who do want a human" → "respetando igual a los clientes que sí quieren una persona" (descarta postergar el pedido).

</details>

#### P7 · 5B · 5.2 · Customer Support Resolution Agent
TiendaX's policy states: "If TiendaX lowers the price of an item within 7 days of purchase, we refund the difference." It says nothing else about price adjustments. A customer who bought a refrigerator for $900,000 four days ago shows the same model at $820,000 on a competitor's site and asks for the difference, and SoporteBot has been approving such requests with `process_refund`. What's the correct approach to these requests without SoporteBot making decisions the policy does not support?

A) Reject the request, explaining that the policy covers only price drops on TiendaX's own site, and mark the conversation as resolved.

B) Approve the refund, since the purchase falls within the 7-day window and the policy's intent is to give customers the lowest price.

C) Escalate with `escalate_to_human`, since the policy is silent on competitor prices and that decision belongs to a person.

D) Ask the customer for a screenshot of the competitor's price, and approve the refund automatically once the difference is verified.

<details>
<summary>Ver respuesta</summary>

**Respuesta correcta: C**

**Why (es):** Es el ejemplo literal de la guía (5.2): **price matching de un competidor cuando la política solo cubre los ajustes del propio sitio**. La política no prohíbe ni permite: **no dice nada**. Ante una política ambigua o silenciosa, el agente **escala**, porque decidir sería inventar la política. Aprobar o rechazar son, las dos, decisiones que la política no respalda (la condición del enunciado).

**Distractors (es):**
- A: tienta porque la política "solo habla" del propio sitio y parece un no; está mal porque confunde un **hueco** (silencio → escalar) con una **prohibición clara** (→ el agente rechaza). La política no dice que no se igualan precios de competidores.
- B: tienta porque el plazo de 7 días se cumple; está mal porque es el comportamiento actual que hay que corregir: el agente interpreta una "intención" que la política no escribió.
- D: tienta porque agrega verificación y parece prudente; está mal porque igual aprueba algo que la política no cubre: inventa una regla nueva en vez de escalar.

**Review:** Capítulo 16 (5B), Tema 3 — Cuando la política no dice nada; Trampa 4 · El precio del competidor.

**Pista de lectura (es):** "It says nothing else about price adjustments" → "no dice nada más sobre ajustes de precio" (política silenciosa → escalar) + "without SoporteBot making decisions the policy does not support" → "sin que SoporteBot tome decisiones que la política no respalda" (descarta aprobar y también rechazar).

</details>

#### P8 · 5B · 5.2 · Customer Support Resolution Agent
SoporteBot escalates whenever a sentiment classifier scores a message below −0.6 or the agent rates its own confidence below 7 out of 10, and first-contact resolution sits at 58%. Reviews show it escalating polite customers with simple damaged-item exchanges whenever its confidence dips, while confidently handling angry customers' out-of-window refund requests that cite a hospitalization. Which TWO changes should you make? (Choose two.)

A) Raise the confidence threshold from 7 to 9, so that the agent escalates more of the difficult cases it currently keeps for itself.

B) Replace both triggers with explicit escalation criteria in the system prompt: a person requested, a policy exception or gap, or no progress.

C) Train a classifier on last year's escalated tickets to predict which conversations need a human, and use it in place of both triggers.

D) Lower the sentiment threshold to −0.9, so that only extremely negative messages escalate and fewer polite customers reach the queue.

E) Add few-shot examples of when to resolve and when to escalate, such as a damaged item with photos versus a late refund citing hospitalization.

<details>
<summary>Ver respuesta</summary>

**Respuesta correcta: B+E**

**Why (es):** La guía (5.2) dice que el **sentimiento** y la **confianza autoinformada** no sirven para escalar: no reflejan la complejidad real, y el agente ya está seguro (equivocadamente) justo en los casos difíciles, como muestra el enunciado. Lo que calibra el escalamiento son **criterios explícitos** (los tres disparadores de la guía, en B) **con ejemplos few-shot** de cuándo escalar y cuándo resolver (E). Las dos juntas son la Skill 1 de 5.2: el criterio define la regla y los ejemplos marcan la frontera.

**Distractors (es):**
- A: tienta porque parece "calibrar" el umbral; está mal porque la confianza autoinformada está mal calibrada: el agente maneja los casos difíciles con confianza **alta**, así que subir el umbral escala más casos simples y no los difíciles.
- C: tienta porque usa datos reales; está mal porque es excesivo (datos etiquetados e infraestructura de ML) antes de probar con el prompt, igual que en la Q3 oficial.
- D: tienta porque reduce las escalaciones; está mal porque los educados se escalan por la confianza, no por el sentimiento, y el sentimiento sigue sin decir nada de la complejidad.

**Review:** Capítulo 16 (5B), Tema 1 — Los tres disparadores correctos y Tema 4 — Sentimiento y confianza no sirven; Trampa 1 · Calibrar el escalamiento (Q3).

**Pista de lectura (es):** "while confidently handling angry customers' out-of-window refund requests that cite a hospitalization" → "mientras maneja con seguridad los pedidos de reembolso fuera de plazo de clientes enojados que alegan una internación" (seguro en el caso difícil = la confianza no sirve; enojado pero no escalado = el sentimiento tampoco).

</details>

#### P9 · 5B · 5.2 · Customer Support Resolution Agent
A customer writes, "I'm Juan Pérez, refund my last order, it arrived broken." `get_customer("Juan Pérez")` returns three accounts. To avoid stalling, SoporteBot was instructed to choose the account with the most recent order, and last week it refunded $45,000 to the wrong Juan Pérez. What's the most effective way to handle multiple matches while keeping these cases within first-contact resolution?

A) Escalate every multiple-match result with `escalate_to_human`, so that a person compares the accounts and selects the correct customer.

B) Have the agent ask the customer for an additional identifier, such as the purchase email or an order number, and continue with that account.

C) Have the agent pick the account whose latest order best matches the complaint, and confirm the choice by reading back its delivery address.

D) Require high self-reported confidence in the account choice before calling `process_refund`, and escalate whenever confidence falls below it.

<details>
<summary>Ver respuesta</summary>

**Respuesta correcta: B**

**Why (es):** La guía (5.2) dice que **varias coincidencias se resuelven pidiendo identificadores adicionales al cliente, no eligiendo por heurística**. "El pedido más reciente" es adivinar, y por eso se hizo un reembolso en la cuenta equivocada. Preguntar el email o un número de pedido lo resuelve el propio agente en el mismo contacto, que es la condición del enunciado.

**Distractors (es):**
- A: tienta porque una persona no se equivoca de cuenta; está mal porque la ambigüedad la resuelve el agente preguntando, y escalar rompe la condición "while keeping these cases within first-contact resolution".
- C: tienta porque agrega una confirmación; está mal porque sigue eligiendo por heurística y, al leer la dirección, le muestra a un cliente datos personales de otro.
- D: tienta porque frena el reembolso cuando hay duda; está mal porque la confianza autoinformada no es confiable y no resuelve la ambigüedad: o elige mal con seguridad o escala de más.

**Review:** Capítulo 16 (5B), Tema 5 — Varias coincidencias: pedir más datos; Trampa 5 · Los tres Juan Pérez.

**Pista de lectura (es):** "was instructed to choose the account with the most recent order" → "se le indicó elegir la cuenta con el pedido más reciente" (heurística = adivinar) + "while keeping these cases within first-contact resolution" → "manteniendo estos casos dentro de la resolución al primer contacto" (descarta escalar).

</details>

### Escenario: Multi-Agent Research System

You are building TiendaX's market research system with the Claude Agent SDK. A coordinator agent delegates work to three subagents for web search, document analysis, and synthesis, and the system produces a monthly report on the home appliance market (refrigerators, washing machines, air conditioners) for the purchasing team. Every figure must be traceable to its source.

#### P10 · 5B · 5.3 · Multi-Agent Research System
The document analysis subagent processes nine industry reports per run. On the sixth, the publisher's portal returns HTTP 403 because TiendaX's subscription has expired, and the subagent returns `{"status": "error", "message": "analysis failed"}`. Unable to tell what happened, the coordinator relaunches the whole analysis task, which re-analyzes the first five reports and fails at the same point. What's the most effective way to address this without reprocessing reports that were already analyzed?

A) Have the subagent retry the download with exponential backoff up to five times, and return the "analysis failed" status only after every attempt has failed.

B) Have the subagent skip the inaccessible report and return the five completed analyses as a successful result, so that the coordinator can move on.

C) Have the subagent return the failure type, the report and request it attempted, the five completed analyses, and alternatives such as the publisher's public summary.

D) Have the coordinator cache every file the subagent downloads, so that a relaunched task only downloads the reports it hadn't retrieved before the failure.

<details>
<summary>Ver respuesta</summary>

**Respuesta correcta: C**

**Why (es):** Es la idea de la Q8 aplicada a otra falla. Con un estado genérico ("analysis failed") el coordinador no sabe si conviene reintentar, cambiar de fuente o seguir, así que relanza todo. La guía pide un **contexto de error estructurado**: tipo de falla (acceso denegado, no se arregla reintentando), qué se intentó, los **resultados parciales** (las cinco ya analizadas, que así no se reprocesan) y **alternativas**. Con eso el coordinador sigue con lo que tiene y elige otra fuente.

**Distractors (es):**
- A: tienta porque el reintento local es buena práctica; está mal porque un 403 por suscripción vencida no se arregla esperando (Trampa 9) y al final devuelve el mismo estado genérico que esconde todo.
- B: tienta porque cumple el alcance (no reprocesa nada) y el flujo sigue; está mal porque es suprimir el error: el coordinador cree que el análisis está completo y el informe sale sin decir que faltó un reporte.
- D: tienta porque ataca el síntoma del alcance (no volver a descargar); está mal porque el coordinador sigue sin saber por qué falló, vuelve a analizar los cinco y vuelve a chocar con el 403.

**Review:** Capítulo 16 (5B), Tema 6 — Contexto de error estructurado (Q8) y Tema 8 — Recuperar localmente; Trampas 7 y 9.

**Pista de lectura (es):** "Unable to tell what happened, the coordinator relaunches the whole analysis task" → "como no puede saber qué pasó, el coordinador relanza toda la tarea de análisis" (el estado genérico es la causa: al coordinador le falta información para decidir).

</details>

#### P11 · 5B · 5.3 · Multi-Agent Research System
In 14% of last month's runs, the report stated that no prices were available for some air conditioner models, even though the price-comparison site listed them. Logs show that, in those runs, the search tool hit its 30-second timeout and returned an empty list marked as successful. Other queries legitimately find nothing, because some discontinued models aren't listed anywhere. What change would most effectively address this?

A) Have the search tool distinguish an access failure, reported with its failure type and query, from a completed search that found no matches, returned as a valid empty result.

B) Have the coordinator re-run every search that returns an empty list up to three times before accepting that no data exists for that model.

C) Instruct the synthesis agent to omit any model whose searches returned no results, so that the report never claims that prices are unavailable.

D) Increase the search tool's timeout from 30 to 120 seconds, so that slow responses from the comparison site complete instead of returning an empty list.

<details>
<summary>Ver respuesta</summary>

**Respuesta correcta: A**

**Why (es):** "No encontré nada" y "no pude buscar" se ven iguales si los dos vuelven como `[]`. Es el **bug silencioso**: el coordinador cree que no hay precios y lo afirma con seguridad. La guía pide **distinguir la falla de acceso (con su tipo y la consulta) del resultado vacío válido**. Así el timeout se trata como falla (se reintenta o se usa otra fuente) y los modelos discontinuados siguen siendo una respuesta válida que no se reintenta.

**Distractors (es):**
- B: tienta porque cubriría los timeouts; está mal porque también reintenta los vacíos válidos (los discontinuados, que van a dar lo mismo) y el coordinador sigue sin saber qué pasó (Trampa 8).
- C: tienta porque saca la afirmación falsa del informe; está mal porque esconde el problema en vez de resolverlo: los modelos con precio igual desaparecen del informe sin aviso.
- D: tienta porque ataca el síntoma (el timeout); está mal porque cuando el sitio falle por otro motivo o tarde más, la falla vuelve a llegar como vacío exitoso.

**Review:** Capítulo 16 (5B), Tema 7 — Falla de acceso vs. resultado vacío válido; Trampa 8.

**Pista de lectura (es):** "returned an empty list marked as successful … Other queries legitimately find nothing" → "devolvió una lista vacía marcada como exitosa … otras consultas legítimamente no encuentran nada" (hay vacíos falsos y vacíos válidos: la solución tiene que separarlos, no tratarlos igual).

</details>

#### P12 · 5B · 5.3 · Multi-Agent Research System
During yesterday's run, the web search subagent hit 37 errors. Thirty-one were HTTP 429 or 503 responses that would have succeeded on a second attempt, and six were "invalid API key" errors from the trade association's portal, the only source of air conditioner sales data. Every error currently goes straight to the coordinator, which spent most of its context handling them and, after the sixth key error, aborted the run, discarding the completed refrigerator and washing machine findings. Which TWO changes should you make? (Choose two.)

A) Keep sending every error to the coordinator, but compress each one into a single line so that error handling no longer consumes most of its context.

B) Have the subagent retry transient failures locally with a limit, and propagate only unresolved failures, such as the invalid key, with the query and partial results.

C) Have the coordinator stop the run whenever a source with no alternative fails, so that the purchasing team never receives a report with a missing section.

D) Fill the air conditioner section with figures from retailer listings and news articles, so that the report still covers every category it was asked for.

E) Have the synthesis agent annotate which findings are well supported and which topics, such as air conditioner sales, have gaps due to unavailable sources.

<details>
<summary>Ver respuesta</summary>

**Respuesta correcta: B+E**

**Why (es):** Hay dos problemas. Primero, **cada error menor sube al coordinador**: la guía pide que el subagente **recupere localmente lo transitorio** (429, 503) y **propague solo lo que no puede resolver** (la clave inválida, que no se arregla reintentando), con la consulta y los parciales (B). Segundo, el coordinador **terminó todo el flujo** por una sola fuente: lo correcto es seguir con lo que hay y que la síntesis tenga **anotaciones de cobertura** que digan qué está respaldado y qué tema tiene un hueco (E).

**Distractors (es):**
- A: tienta porque ataca el síntoma del contexto lleno; está mal porque el coordinador sigue atendiendo 31 errores que el subagente podía resolver solo, y un resumen de una línea pierde el contexto que necesita para decidir.
- C: tienta porque evita entregar un informe incompleto; está mal porque es el anti-patrón de terminar todo el flujo: tira heladeras y lavarropas por una sola falla (Trampa 10).
- D: tienta porque el informe queda "completo"; está mal porque presenta como sólido un tema con datos débiles, sin decir que faltó la fuente principal.

**Review:** Capítulo 16 (5B), Tema 8 — Recuperar localmente y propagar lo que no se puede resolver; Tema 9 — Anotaciones de cobertura; Trampas 9 y 10.

**Pista de lectura (es):** "aborted the run, discarding the completed refrigerator and washing machine findings" → "abortó la corrida y descartó los hallazgos ya terminados de heladeras y lavarropas" (terminar todo por una sola falla es un anti-patrón: se sigue y se anota qué falta).

</details>

#### P13 · 5D · 5.6 · Multi-Agent Research System
The purchasing team challenged the report's claim that "inverter washing machines account for 41% of unit sales," and nobody could tell which of the 23 sources in its bibliography supported it. Logs show that the document analysis subagent returns a two-paragraph prose summary of each document, which the synthesis agent merges into the report. What's the most effective way to address this?

A) Have the synthesis agent add a citation after each paragraph of the report, listing every document whose summary contributed to that paragraph.

B) Have the synthesis agent search the web for each statistic after drafting the report, and attach the first URL that contains a matching figure.

C) Expand the bibliography with each source's URL, publisher, and access date, and sort it by how many figures the report draws from each source.

D) Have the analysis subagent return claim-source mappings with the URL, document name, and excerpt for each claim, and have synthesis preserve and merge them.

<details>
<summary>Ver respuesta</summary>

**Respuesta correcta: D**

**Why (es):** La atribución se pierde **en el paso de compresión**: el subagente devuelve prosa y, cuando la síntesis la mezcla, ya nadie sabe qué dato vino de qué documento. La guía pide que los subagentes devuelvan **claim-source mappings estructurados** (afirmación, URL, nombre del documento, fragmento) y que el agente de síntesis **los conserve y los combine**.

**Distractors (es):**
- A: tienta porque acerca la cita al dato; está mal porque cita a nivel de párrafo con todos los documentos que aportaron: sigue sin decir de qué fuente sale el 41%, y la síntesis no tiene ese dato porque el subagente nunca lo devolvió.
- B: tienta porque termina con una URL junto a cada número; está mal porque es una atribución a posteriori: la primera página con un 41% puede no ser la fuente que se usó (o hablar de otra cosa).
- C: tienta porque mejora la bibliografía; está mal porque una lista al final dice qué se leyó, no qué dato sale de cada fuente (Trampa 5).

**Review:** Capítulo 18 (5D), Tema 5 — Claim-source mappings; Trampa 5 · La bibliografía al final.

**Pista de lectura (es):** "returns a two-paragraph prose summary of each document, which the synthesis agent merges" → "devuelve un resumen en prosa de dos párrafos por documento, que el agente de síntesis combina" (ahí se pierde la procedencia: hay que estructurarla desde el subagente).

</details>

#### P14 · 5D · 5.6 · Multi-Agent Research System
This month's report has two discrepancies. For refrigerator unit growth in Q3 2026, the chamber of commerce reports 12% and a consulting firm reports 8%; the synthesis agent kept 12% because that source is "more authoritative." For Brand X's market share, one source says 30% and another says 22%, and the report calls them contradictory, but the analysis subagent's output doesn't record when either figure was collected. Which approach should you take?

A) Have the analysis subagent keep the most recently published value for each metric, and list the other value and its source in a footnote for transparency.

B) Have the analysis subagent record each source's publication or collection date, and return same-period disagreements with both values attributed and flagged for the coordinator.

C) Have the analysis subagent pause and request a decision from a human analyst whenever two sources disagree, before passing any findings to the coordinator.

D) Have the analysis subagent report the midpoint of two conflicting values, citing both sources, so that the report presents a single figure for each metric.

<details>
<summary>Ver respuesta</summary>

**Respuesta correcta: B**

**Why (es):** Son dos casos distintos. El 12% vs. 8% mide **el mismo período** (Q3 2026): es un conflicto real, y la guía dice **no elegir**: el subagente completa su análisis con **los dos valores con su fuente, marcados como conflicto**, y **decide el coordinador** cómo reconciliarlos. El 30% vs. 22% **no tiene fechas**: puede ser una tendencia (2024 → 2026) y no una contradicción. Por eso los subagentes tienen que incluir la **fecha de publicación o de recolección** de cada fuente.

**Distractors (es):**
- A: tienta porque es el "prefer-newer" del curso y deja la otra cifra a la vista; está mal porque sigue eligiendo un valor arbitrariamente, y "el más nuevo" publicado no dice cuándo se midió cada dato.
- C: tienta porque nadie decide solo; está mal porque el subagente tiene que **completar** el análisis con los dos valores anotados: frenarse bloquea todo el informe, y la guía pone la decisión en el coordinador.
- D: tienta porque cita las dos fuentes; está mal porque inventa un número (10%) que ninguna fuente dijo, y promediar 30% y 22% mezcla años distintos.

**Review:** Capítulo 18 (5D), Tema 6 — Fuentes que se contradicen y Tema 7 — Fechas; Trampas 6 y 7.

**Pista de lectura (es):** "For refrigerator unit growth in Q3 2026 … but the analysis subagent's output doesn't record when either figure was collected" → "para el crecimiento de unidades de heladeras en el tercer trimestre de 2026 (las dos cifras miden ese período) … pero la salida del subagente no registra cuándo se recolectó cada cifra" (mismo período = conflicto real; sin fecha = no sabés si es conflicto o tendencia).

</details>

#### P15 · 5D · 5.6 · Multi-Agent Research System
Reviewers say the report reads as if every finding were equally certain. A consultant's "preliminary estimate" that air conditioner sales will rise 15% appears as "Sales will rise 15%," a trend confirmed by four sources sits next to a claim from a single trade blog, and price comparisons, sector news, and energy-efficiency test results are all rendered as one bullet list. How should you restructure the report without dropping any findings the purchasing team relies on?

A) Separate well-established findings from contested ones, preserving each source's characterization and method, and use tables for prices, prose for news, and lists for test results.

B) Rewrite every finding in a consistent, confident voice with a confidence score beside it, and keep the uniform bullet format so that the report is easy to scan.

C) Remove every finding supported by a single source, and convert the whole report to prose paragraphs so that each remaining claim is explained in its context.

D) Separate well-established findings from contested ones, and convert every section into a table with source, value, and date columns so that all entries are comparable.

<details>
<summary>Ver respuesta</summary>

**Respuesta correcta: A**

**Why (es):** La guía pide dos cosas para el informe. **Secciones que separan lo bien establecido de lo disputado**, conservando **cómo caracterizó el dato la fuente** ("estimación preliminar" no se vuelve un hecho) y el **contexto metodológico**. Y **el formato según el tipo de contenido**: datos financieros en tablas, noticias en prosa, hallazgos técnicos en listas estructuradas.

**Distractors (es):**
- B: tienta porque un puntaje de confianza parece informar la certeza; está mal porque la voz segura borra la caracterización de la fuente (el "preliminar") y el formato uniforme es justo lo que hace que todo se lea igual.
- C: tienta porque saca lo dudoso; está mal porque rompe la condición "without dropping any findings": los hallazgos de una sola fuente van a la sección de disputados, no se borran. Y todo en prosa también es formato uniforme.
- D: tienta porque la primera mitad es correcta; está mal porque convierte noticias y resultados técnicos en tablas (formato único) y no conserva cómo lo dijo cada fuente.

**Review:** Capítulo 18 (5D), Tema 8 — Cómo se arma el informe final; Trampa 8 · El informe parejo.

**Pista de lectura (es):** "A consultant's 'preliminary estimate' … appears as 'Sales will rise 15%'" → "la 'estimación preliminar' de una consultora … aparece como 'Las ventas van a subir un 15%'" (se perdió cómo caracterizó el dato la fuente).

</details>

### Escenario: Developer Productivity with Claude

You are building a developer productivity workflow with Claude Code to help TiendaX engineers explore a large TypeScript monorepo of 40 packages, including `checkout`, `pagos`, and `catalogo`. Developers run long exploration sessions using Read, Grep, Glob, and subagents, and a nightly multi-agent audit maps the codebase. Answers must name specific classes and files.

#### P16 · 5C · 5.4 · Developer Productivity with Claude
A developer has spent two hours with Claude Code tracing how `checkout` applies promotions. Early on, Claude identified `PromoEngine.apply()` and `CartPricing.recalculate()`, but it now describes "the typical promotion service in an e-commerce platform" and contradicts its earlier answer about where discounts are rounded. Most of the context is Grep output and full file reads, and she has already run `/compact` twice, losing several exact file paths. What's the most effective way to address this for the rest of the exploration?

A) Switch the session to a model with a larger context window, so that the earlier findings and all the search output fit without being summarized.

B) Run `/clear` and restart the exploration, loading the directory tree of all 40 packages at the start so that Claude has the full structure available.

C) Run `/compact` every 30 minutes with a focus instruction that lists the classes and file paths that each summary must preserve.

D) Keep key findings and file paths in a scratchpad file that Claude reads before each new question, and delegate broad searches to subagents that return summaries.

<details>
<summary>Ver respuesta</summary>

**Respuesta correcta: D**

**Why (es):** "Typical patterns" en vez de las clases que ya encontró y respuestas inconsistentes son **el síntoma literal de la degradación del contexto** en la guía. Lo descubierto se guarda **fuera del contexto**, en un **scratchpad file que se consulta antes de cada pregunta**, y la búsqueda verbosa se **delega a subagentes** que devuelven solo un resumen, mientras la sesión principal coordina. Así deja de llenarse de Grep.

**Distractors (es):**
- A: tienta porque "no le entra todo"; está mal porque es degradación por cantidad de tokens (context rot), no falta de espacio: con más ventana el ruido crece igual.
- B: tienta porque el contexto queda limpio; está mal porque `/clear` borra todo lo encontrado (es para una tarea distinta) y cargar el árbol entero agrega más ruido (Trampa 1).
- C: tienta porque `/compact` es la herramienta de la guía para un contexto lleno de descubrimiento; está mal porque el enunciado dice que **ya** compactó y perdió rutas exactas: un resumen puede desdibujar valores, y lo que no se puede perder va a un archivo (Trampa 7). Además, sigue haciendo la búsqueda pesada en la sesión principal.

**Review:** Capítulo 17 (5C), Tema 1 — Degradación del contexto, Tema 2 — Scratchpad files y Tema 3 — Delegar a subagentes; Trampas 1, 3 y 7.

**Pista de lectura (es):** "she has already run `/compact` twice, losing several exact file paths" → "ya corrió `/compact` dos veces y perdió varias rutas exactas" (compactar no alcanza: lo exacto tiene que vivir en un archivo).

</details>

#### P17 · 5C · 5.4 · Developer Productivity with Claude
The nightly audit runs 12 mapping tasks in phase 1, each covering a group of packages, and then launches phase 2 subagents to find every place that converts pesos to `priceCents`. Last night the process crashed at 03:40 after 7 of the 12 mapping tasks had finished, and the restart re-ran all of them. In earlier runs, phase 2 subagents re-discovered the package structure and sometimes contradicted phase 1. Which design best enables recovery without rerunning completed work?

A) Resume the coordinator's previous session after a crash and ask it to list which mapping tasks had finished, then relaunch only the tasks it reports as incomplete.

B) Launch phase 2 subagents as forks of the coordinator's conversation so that they inherit every phase 1 report, and rerun the full audit after a crash for consistency.

C) Have each agent export its state to a known location tracked in a manifest the coordinator loads on resume, and inject a summary of phase 1 findings into phase 2 prompts.

D) Have each agent export its state to a known location, and pass the complete phase 1 reports to every phase 2 subagent so that no detail is lost between phases.

<details>
<summary>Ver respuesta</summary>

**Respuesta correcta: C**

**Why (es):** La guía pide **persistencia estructurada del estado**: cada agente exporta su estado a un **lugar conocido**, el coordinador mantiene un **manifest** y, al reanudar, lo **carga**, saltea las 7 tareas terminadas e inyecta los exports en las que siguen. Para el segundo problema, entre fases se pasa un **resumen de los hallazgos clave** en el prompt inicial de los subagentes nuevos: ni nada (re-descubren y contradicen) ni todo (ruido).

**Distractors (es):**
- A: tienta porque el coordinador "estuvo ahí"; está mal porque su memoria de la conversación no es confiable (y puede no haber llegado a registrar todo antes del corte): el estado tiene que estar escrito (Trampa 8).
- B: tienta porque los subagentes "saben todo"; está mal porque el fork carga toda la salida de la fase 1 (justo el ruido que hay que evitar) y relanzar todo rompe la condición del enunciado.
- D: tienta porque la primera mitad es correcta; está mal porque no hay un manifest que el coordinador cargue para saber qué saltear, y pasar los reportes completos vuelve a llenar el contexto de la fase 2 (Trampa 5).

**Review:** Capítulo 17 (5C), Tema 4 — Resumen entre fases y Tema 6 — Crash recovery con manifests; Trampas 5 y 8.

**Pista de lectura (es):** "after 7 of the 12 mapping tasks had finished, and the restart re-ran all of them" → "después de que 7 de las 12 tareas de mapeo habían terminado, y el reinicio las volvió a correr todas" (falta un estado escrito que el coordinador cargue al reanudar).

</details>

### Escenario: Structured Data Extraction

You are building a structured data extraction pipeline that uses Claude to pull the supplier, amounts in cents, due date, and purchase order number from TiendaX's supplier documents: PDF invoices, emailed invoices from small suppliers, and credit notes. Extracted data flows into the payments system, and two reviewers check extractions. The goal is to reduce manual review safely.

#### P18 · 5D · 5.5 · Structured Data Extraction
Across 12,000 documents last quarter, extraction accuracy was 96.8%, above the 95% target. The model returns one confidence score per document, and your manager proposes sending every document scored 0.9 or higher straight to payments without review, which would cover 88% of volume. Emailed invoices are 9% of volume, and one large supplier changed its invoice layout last month. The team wants to cut review load without losing the ability to detect new error patterns. How should you evaluate this proposal?

A) Accept it, since 96.8% exceeds the target, and send only documents scored below 0.9 to the reviewers so that their limited time goes where errors are.

B) Reject it until accuracy is measured by document type and field, then auto-accept using per-field thresholds calibrated on labeled data and sample accepted extractions by stratum.

C) Accept it with the threshold raised to 0.98, and have the reviewers audit a random 2% of all documents each week to catch any errors that remain.

D) Reject it, and keep the reviewers checking every extraction in arrival order, since any automation risks sending confidently wrong values to payments.

<details>
<summary>Ver respuesta</summary>

**Respuesta correcta: B**

**Why (es):** La propuesta tiene tres problemas que la guía de 5.5 nombra. (1) El 96,8% es un **promedio** que puede esconder un segmento malo (los emails son 9%): hay que **medir por tipo de documento y por campo antes de automatizar**. (2) Un puntaje **por documento** y sin calibrar esconde el campo débil: la confianza va **por campo** y con **umbrales calibrados con un set etiquetado**. (3) Lo que se acepta solo se sigue midiendo con **muestreo aleatorio estratificado de las extracciones de alta confianza**, que detecta patrones nuevos como el cambio de formato del proveedor.

**Distractors (es):**
- A: tienta porque cumple la meta y usa a los revisores en lo dudoso; está mal porque automatiza por el número global y, sin muestrear lo aceptado, los errores confiados (el proveedor que cambió el formato) nunca se ven: rompe la condición del enunciado.
- C: tienta porque parece más conservador y agrega una muestra; está mal porque el umbral sigue sin calibrar ni mirar segmentos, y una muestra al azar sobre todo el volumen puede dejar afuera los grupos chicos o de más riesgo.
- D: tienta porque es lo más seguro; está mal porque no reduce la carga de revisión (el objetivo del escenario) y revisar en orden de llegada desperdicia a los revisores en casos fáciles.

**Review:** Capítulo 18 (5D), Tema 1 — Accuracy agregada, Tema 2 — Confianza por campo calibrada y Tema 3 — Muestreo estratificado; Trampas 1, 2 y 3.

**Pista de lectura (es):** "The model returns one confidence score per document … one large supplier changed its invoice layout last month" → "el modelo devuelve un solo puntaje de confianza por documento … un proveedor grande cambió el formato de su factura el mes pasado" (puntaje por documento = esconde campos débiles; cambio de formato = hace falta seguir muestreando lo automatizado).

</details>
