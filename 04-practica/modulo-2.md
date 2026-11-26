# Preguntas — Módulo 2 (Tool Design & MCP Integration · 2A–2C)

## Preguntas de fin de módulo

### Escenario: Customer Support Resolution Agent

You are building a customer support resolution agent for TiendaX with the Claude Agent SDK. The agent connects to an MCP server exposing `get_customer`, `lookup_order`, `search_orders`, `process_refund`, and `escalate_to_human`. It handles returns, refunds, and order-status questions. The target is 80%+ first-contact resolution while escalating genuine policy exceptions to human agents.

#### P1 · 2A · 2.1 · Customer Support Resolution Agent
Last month you expanded the descriptions of `get_customer` and `lookup_order` with input formats, example queries, and boundaries, and overall selection accuracy rose to 96%. However, when a message mentions a charge, as in "I was charged twice for order #48213," the agent still calls `get_customer` first in most cases. The system prompt includes the line "Whenever the customer mentions a charge or a payment, start with get_customer." What's the most effective way to address this?

A) Add more examples to the `lookup_order` description covering messages that mention a charge or payment together with an order number.

B) Add few-shot examples to the system prompt showing charge-related order questions being routed to `lookup_order` instead of `get_customer`.

C) Rewrite the keyword-based instruction in the system prompt so it no longer ties words like "charge" or "payment" to `get_customer`.

D) Add a preprocessing step that detects order numbers in each user message and pre-selects `lookup_order` before the model's turn.

<details>
<summary>Ver respuesta</summary>

**Respuesta correcta: C**

**Why (es):** Las descripciones ya están bien (subió la precisión al 96%) y la falla aparece solo con ciertas palabras. La causa es una instrucción del system prompt atada a palabras clave ("charge", "payment") que pisa las descripciones. La guía pide revisar el system prompt buscando ese tipo de instrucciones y corregirlas.

**Distractors (es):**
- A: tienta porque la descripción es el mecanismo principal de selección / está mal porque la descripción ya es buena: la regla del prompt la está pisando, y agregar ejemplos no la saca.
- B: tienta porque los few-shot mejoran el comportamiento y probablemente bajen el error / está mal porque deja la regla conflictiva en el prompt, suma tokens en cada llamada y no ataca la causa.
- D: tienta porque parece determinístico y "funciona" para los mensajes con número de pedido / está mal porque es un componente extra (sobreingeniería) que se saltea la comprensión del modelo, mientras la causa sigue en el prompt.

**Review:** Capítulo 5 (2A), Tema 4 — El system prompt también influye; Trampa 3.

**Pista de lectura (es):** "The system prompt includes the line 'Whenever the customer mentions a charge…'" → "El system prompt incluye la línea 'Cada vez que el cliente mencione un cobro…'" (una regla atada a palabras clave: la causa está en el prompt, no en las descripciones).

</details>

#### P2 · 2A · 2.1 · Customer Support Resolution Agent
Last sprint, two knowledge tools were added to the MCP server: `search_help`, described as "Searches TiendaX content for answers to customer questions," and `search_policy`, described as "Searches TiendaX content for answers about policies." `search_help` queries public FAQ articles, while `search_policy` queries the internal refund rules with their effective dates. In 27% of refund-eligibility conversations, the agent answers from FAQ articles that simplify those rules. Your teammate proposes merging both into a single `search_content` tool with a `source` parameter. How should you evaluate this proposal?

A) Reject it; rename `search_policy` to something like `get_refund_policy_rules` and rewrite both descriptions to state each source, output, and when to use it.

B) Accept it, since consolidating related operations behind one tool with a parameter removes the choice that is causing the misrouting.

C) Accept it, but also add few-shot examples to the system prompt showing which `source` value to pass for refund-eligibility questions.

D) Reject it; keep both tools unchanged and add a system prompt rule sending every message that mentions "refund" to `search_policy`.

<details>
<summary>Ver respuesta</summary>

**Respuesta correcta: A**

**Why (es):** Las dos tools tienen nombres y descripciones casi idénticos ("Searches TiendaX content for answers…") aunque consultan fuentes distintas. La guía pide eliminar la superposición renombrando y reescribiendo las descripciones para diferenciar propósito, fuente, salida y cuándo usar cada una. La propuesta no ataca la causa: la ambigüedad pasa de "qué tool" a "qué valor de `source`".

**Distractors (es):**
- B: tienta porque la documentación de Anthropic sugiere consolidar operaciones relacionadas / está mal porque la guía pide renombrar y diferenciar; la elección ambigua sigue existiendo, ahora en el parámetro, con la misma descripción vaga.
- C: tienta porque suma ejemplos que podrían mejorar el ruteo / está mal porque acepta la consolidación y agrega tokens sin arreglar las descripciones superpuestas.
- D: tienta porque rechaza la propuesta y parece determinístico / está mal porque deja las descripciones superpuestas y crea justo una instrucción atada a palabra clave que la guía señala como riesgo.

**Review:** Capítulo 5 (2A), Tema 3 — Tools que se pisan: renombrar y dividir (la contradicción consolidar vs. dividir); Trampa 1.

**Pista de lectura (es):** "described as 'Searches TiendaX content for answers…'" → "descripta como 'Busca en el contenido de TiendaX respuestas…'" (descripciones casi idénticas = superposición; "proposes" → hay que evaluar la propuesta, que suele estar mal o ser parcial).

</details>

#### P3 · 2A · 2.2 · Customer Support Resolution Agent
`process_refund` returns the string "Operation failed" for every failure. Logs show that when a refund falls outside the 30-day return window, the agent retries the call three or four times and then tells the customer to try again later because of a technical issue. What change would most effectively address this?

A) Limit `process_refund` to a single retry in the agent loop so that policy failures waste fewer calls before the agent responds.

B) Return a distinct error code such as `REFUND_WINDOW_EXPIRED` and list every code with its meaning in the system prompt.

C) Add a system prompt instruction to check the order date against the 30-day window before calling `process_refund`.

D) Return `isError: true` with `errorCategory: "business"`, `isRetryable: false`, and a customer-friendly explanation of the return-window policy.

<details>
<summary>Ver respuesta</summary>

**Respuesta correcta: D**

**Why (es):** Un error uniforme impide decidir cómo recuperarse. Es una violación de regla de negocio: no se arregla reintentando. La guía pide metadata estructurada (categoría, `isRetryable: false`) y una explicación apta para el cliente, para que el agente le diga la verdad (o escale) en vez de inventar un problema técnico.

**Distractors (es):**
- A: tienta porque reduce el desperdicio de llamadas / está mal porque sigue reintentando algo que nunca va a funcionar y el cliente sigue recibiendo una explicación falsa.
- B: tienta porque parece estructurado y "funciona" en parte / está mal porque el resultado no dice si es reintentable ni qué explicarle al cliente; depende de una tabla en el prompt que hay que mantener.
- C: tienta porque evita algunas llamadas inválidas / está mal porque es probabilístico y no arregla la respuesta genérica: cuando igual falla, el agente sigue sin saber por qué.

**Review:** Capítulo 5 (2A), Tema 7 — Structured errors: isError, errorCategory e isRetryable; Trampa 4.

**Pista de lectura (es):** "falls outside the 30-day return window" → "queda fuera del plazo de devolución de 30 días" (es un error de negocio: no reintentable).

</details>

#### P4 · 2A · 2.2 · Customer Support Resolution Agent
After a database migration, customers began reopening order-status tickets at a higher rate. Reviewing the transcripts, you find that when the orders database times out under peak load, the MCP server catches the exception inside `search_orders` and returns `{"orders": []}` without setting `isError`, so the agent confidently tells customers that no orders exist under their email address. This happens in about 4% of order-status conversations. Which approach best enables the agent to handle these cases correctly?

A) Have the agent automatically retry `search_orders` whenever it returns an empty list before telling the customer that no orders were found.

B) Return timeouts with `isError: true`, `errorCategory: "transient"`, and `isRetryable: true`, keeping the empty list only for successful searches with no matches.

C) Increase the database timeout in `search_orders` so that slow queries under peak load complete instead of being cut off.

D) Escalate every empty `search_orders` result to a human agent so that a person confirms whether the customer really has no orders.

<details>
<summary>Ver respuesta</summary>

**Respuesta correcta: B**

**Why (es):** Una falla de acceso devuelta como lista vacía exitosa es una falla silenciosa: el agente afirma algo falso. La guía pide distinguir la falla de acceso (error, transitorio, reintentable) del resultado vacío válido (éxito sin datos), para que el agente decida bien.

**Distractors (es):**
- A: tienta porque reintentar es correcto ante lo transitorio y a veces "funciona" / está mal porque el agente no puede distinguir un vacío válido de una falla: reintenta en vano los vacíos reales y, si el timeout persiste, sigue informando que no hay pedidos.
- C: tienta porque bajaría la frecuencia / está mal porque no corrige el patrón: el próximo timeout vuelve a parecer "no hay pedidos".
- D: tienta porque parece seguro / está mal porque sobre-escala los vacíos válidos (que son la mayoría) y castiga la meta de resolución en el primer contacto, sin arreglar la señal de error.

**Review:** Capítulo 5 (2A), Tema 8 — Access failure vs. valid empty result; Trampa 5.

**Pista de lectura (es):** "returns {"orders": []} without setting isError" → "devuelve una lista vacía sin marcar isError" (una falla disfrazada de resultado vacío válido).

</details>

#### P5 · 2A · 2.2 · Customer Support Resolution Agent
`lookup_order` fails in two situations: the customer gives a malformed number such as "TX-48A13," or the order belongs to a different customer account. In both cases the server returns `isError: true` with the text "Request could not be completed," and the agent usually repeats the identical call. What's the most effective way to enable appropriate recovery?

A) Enable `strict: true` on `lookup_order` with a pattern for valid order numbers so that malformed inputs are never sent to the server.

B) Return malformed inputs as JSON-RPC protocol errors with code -32602, keeping `isError: true` only for the wrong-account case.

C) Include `errorCategory` "validation" or "permission", `isRetryable: false`, and a description of what went wrong in each error result.

D) Add a system prompt instruction telling the agent never to repeat a failed `lookup_order` call with the same arguments.

<details>
<summary>Ver respuesta</summary>

**Respuesta correcta: C**

**Why (es):** El `isError` ya está, pero el mensaje es uniforme. Con la categoría (validation: pedir el número de nuevo; permission: no compartir datos de otra cuenta), `isRetryable: false` y una descripción legible, el agente elige la recuperación correcta en cada caso.

**Distractors (es):**
- A: tienta porque `strict` garantiza inputs que cumplen el schema / está mal porque, a lo sumo, cubre el caso de validación; el de permiso sigue devolviendo el mismo error genérico.
- B: tienta porque parece más "estándar" del protocolo / está mal porque los errores de protocolo son los que el modelo tiene menos chances de usar para autocorregirse, y el caso de permiso sigue sin categoría.
- D: tienta porque corta la repetición / está mal porque es probabilístico y no le dice al agente qué hacer en lugar de repetir.

**Review:** Capítulo 5 (2A), Tema 7 — Structured errors (y errores de protocolo vs. de ejecución en MCP); Tema 6 — Strict tool use.

**Pista de lectura (es):** "In both cases the server returns … 'Request could not be completed'" → "En los dos casos el servidor devuelve … 'No se pudo completar la solicitud'" (error uniforme para dos causas distintas: falta categoría).

</details>

#### P6 · 2A · 2.3 · Customer Support Resolution Agent
To cover more requests, your team connected two more MCP servers, for catalog and marketing, so the support agent now has 18 tools instead of the original 5. Every new tool has a detailed description with example queries and boundaries. Since the change, correct tool selection on your evaluation set has dropped from 95% to 82%, mostly among tools the support role rarely needs. Which approach should you take?

A) Restrict the support agent to the tools its role needs and give catalog and marketing requests to specialized agents with their own scoped tools.

B) Expand the descriptions of all 18 tools further, adding more edge cases and explicit comparisons with each similar tool on the server.

C) Switch the support agent to a larger model with a longer context window so it can reason about all 18 tools at once.

D) Add few-shot examples to the system prompt that demonstrate correct selection for the most frequently confused groups of tools.

<details>
<summary>Ver respuesta</summary>

**Respuesta correcta: A**

**Why (es):** La guía: darle a un agente demasiadas tools (18 en vez de 4–5) degrada la elección por complejidad de decisión. Las descripciones ya son buenas; el problema es la cantidad y que hay tools fuera del rol. Se reparte con acceso acotado por rol.

**Distractors (es):**
- B: tienta porque la descripción es el mecanismo principal / está mal porque las descripciones ya son detalladas: el problema es la cantidad de opciones.
- C: tienta porque "razona mejor" / está mal porque no reduce la complejidad de la decisión ni saca las tools que no corresponden al rol.
- D: tienta porque podría mejorar algo / está mal porque suma tokens y sigue dejando 18 tools para elegir; no ataca la causa.

**Review:** Capítulo 5 (2A), Tema 10 — Tool scoping: pocas tools por agente; Trampa 6.

**Pista de lectura (es):** "mostly among tools the support role rarely needs" → "sobre todo entre tools que el rol de soporte casi no necesita" (tools fuera del rol: hay que acotar, no describir mejor).

</details>

---

### Escenario: Multi-Agent Research System

You are building a multi-agent research system for TiendaX's strategy team. A coordinator delegates to a web search subagent (`web_search`, `fetch_url`), a document analysis subagent (`extract_metadata`, `analyze_document`, enrichment tools), and a synthesis subagent that writes competitive reports. Reports must cite only verified sources and be delivered within 10 minutes.

#### P7 · 2A · 2.1 · Multi-Agent Research System
`analyze_document` is described as "Analyzes a document according to the instructions provided" and takes a free-text `instructions` parameter. The document analysis subagent uses it for three different jobs: pulling exact figures, summarizing long reports, and checking whether a claim appears in a source. Its output shape varies from call to call, and the synthesis subagent misreads summaries as quoted figures in 11% of reports. How should you restructure this tool?

A) Keep `analyze_document` and add an `action` parameter with an enum of operations, documenting each allowed value in the tool description.

B) Keep `analyze_document` and expand its description with example instructions, expected output formats, and edge cases for each kind of job.

C) Keep `analyze_document` and add a system prompt instruction requiring the subagent to return every result as labeled JSON.

D) Split it into `extract_data_points`, `summarize_content`, and `verify_claim_against_source`, each with defined inputs and a fixed output format.

<details>
<summary>Ver respuesta</summary>

**Respuesta correcta: D**

**Why (es):** Es una tool genérica que hace trabajos distintos con un contrato vago y salida variable. La guía pide dividir las tools genéricas en tools de propósito específico con contratos de entrada y salida definidos; así la síntesis recibe siempre la forma que espera.

**Distractors (es):**
- A: tienta porque la documentación de Anthropic recomienda consolidar con un parámetro `action` y también "funciona" / está mal porque la guía pide dividir, y una sola tool sigue sin un contrato de salida fijo por tipo de trabajo.
- B: tienta porque expandir descripciones suele ser el primer paso / está mal porque el problema no es solo de selección: la salida no tiene contrato y sigue variando.
- C: tienta porque apunta a la salida / está mal porque es probabilístico y "JSON etiquetado" no define qué campos tiene cada tipo de trabajo.

**Review:** Capítulo 5 (2A), Tema 3 — Tools que se pisan: renombrar y dividir; Trampa 2.

**Pista de lectura (es):** "Its output shape varies from call to call" → "La forma de su salida cambia de una llamada a otra" (falta un contrato de salida: dividir en tools específicas).

</details>

#### P8 · 2A · 2.1 · Multi-Agent Research System
The document analysis subagent recently gained `extract_figures`, described as "Extracts data from a document," next to `extract_metadata`, described as "Extracts metadata from a document." Logs show that 23% of requests for a report's publication date or author now go to `extract_figures`. What's the most effective first step to fix this?

A) Merge `extract_metadata` and `extract_figures` into one `extract_document_info` tool that returns both metadata and figures on every call.

B) Expand both descriptions with the fields each returns, example requests, edge cases, and when to use each one instead of the other.

C) Add a rule to the subagent's system prompt stating that any request mentioning a date or an author must use `extract_metadata`.

D) Rename `extract_figures` to `extract_numeric_figures` so that its name signals more clearly that it does not return metadata.

<details>
<summary>Ver respuesta</summary>

**Respuesta correcta: B**

**Why (es):** Dos descripciones mínimas y casi iguales son la causa raíz. La descripción es el mecanismo principal de selección; expandirla con qué devuelve, ejemplos, casos límite y cuándo usar cada una es el primer paso más barato y efectivo.

**Distractors (es):**
- A: tienta porque elimina la elección y podría funcionar / está mal porque es más trabajo del que pide un "first step" y devuelve datos de más en cada llamada.
- C: tienta porque es rápido y parece preciso / está mal porque crea una instrucción atada a palabras clave ("date", "author") que puede pisar descripciones y generar asociaciones no deseadas (p. ej., fechas de cifras trimestrales).
- D: tienta porque el nombre parece importante / está mal porque lo que pesa es la descripción; renombrar sin reescribirla no alcanza.

**Review:** Capítulo 5 (2A), Tema 2 — Writing tool descriptions; Trampa 1.

**Pista de lectura (es):** "described as 'Extracts data from a document' … 'Extracts metadata from a document'" → "descripta como 'Extrae datos de un documento' … 'Extrae metadatos de un documento'" (descripciones mínimas y casi iguales; "first step" → el cambio mínimo).

</details>

#### P9 · 2A · 2.3 · Multi-Agent Research System
To fill small gaps, the synthesis subagent was given `web_search` and `fetch_url`. Since then, 30% of its reports cite blogs and forums that the web search subagent would have filtered out, and synthesis takes 40% longer. Reviewing its calls, you find that 85% of its searches only confirm a single figure or date that already appears in the findings it received, while the rest require a new multi-source investigation. Which TWO changes should you make? (Choose two.)

A) Add a system prompt instruction telling the synthesis subagent to search only when necessary and to prefer well-known, reputable domains.

B) Remove `web_search` and `fetch_url` from the synthesis subagent so that it can only use the tools that belong to its role.

C) Give the synthesis subagent the full web search toolset plus a source-quality scoring tool so it can verify findings on its own.

D) Have the coordinator collect every verification request and run them in one batch after the synthesis subagent finishes its draft.

E) Add a scoped `verify_fact` tool for simple confirmations, and route new multi-source investigations through the coordinator to the web search subagent.

<details>
<summary>Ver respuesta</summary>

**Respuesta correcta: B+E**

**Why (es):** Un agente con tools fuera de su especialidad las usa mal (síntesis haciendo búsquedas web). La guía pide restringir cada subagent a las tools de su rol y, para la necesidad frecuente de otro rol (85% son confirmaciones simples), darle una cross-role tool acotada como `verify_fact`, mientras lo complejo pasa por el coordinador.

**Distractors (es):**
- A: tienta porque es rápido / está mal porque es probabilístico: mientras tenga la tool, puede seguir usándola mal.
- C: tienta porque parece resolver la calidad de la verificación / está mal porque sobre-aprovisiona y rompe la separación de responsabilidades.
- D: tienta porque reduce idas y vueltas / está mal porque crea dependencias bloqueantes: el borrador puede apoyarse en datos que todavía no se verificaron.

**Review:** Capítulo 5 (2A), Tema 10 — Tool scoping (cross-role tools acotadas); Trampa 7.

**Pista de lectura (es):** "85% of its searches only confirm a single figure or date" → "el 85% de sus búsquedas solo confirma una cifra o una fecha" (necesidad frecuente y simple: tool acotada, no todo el set de búsqueda).

</details>

#### P10 · 2A · 2.3 · Multi-Agent Research System
The web search subagent uses `fetch_url` to retrieve the analyst reports that its searches find. In 9% of runs, `fetch_url` follows a result to a login wall, a cookie banner, or a search-results page, and the raw HTML is passed to the document analysis subagent as if it were a report. What's the correct approach to prevent this?

A) Replace `fetch_url` with a `load_document` tool that validates the URL points to a supported document before returning its extracted text.

B) Expand the `fetch_url` description to say it must only be used for analyst reports and never for search pages or login walls.

C) Strip HTML tags from every `fetch_url` response so that the document analysis subagent receives clean text instead of raw markup.

D) Add a reviewer subagent that reads every fetched page and decides whether it is a real report before analysis begins.

<details>
<summary>Ver respuesta</summary>

**Respuesta correcta: A**

**Why (es):** `fetch_url` es una tool genérica que baja cualquier cosa. La guía pide reemplazar tools genéricas por alternativas acotadas (`fetch_url` → `load_document`, que valida que la URL sea de un documento).

**Distractors (es):**
- B: tienta porque la descripción guía el uso / está mal porque la tool sigue siendo genérica y el problema es a dónde lleva el link, no solo cuándo se la llama.
- C: tienta porque limpia la salida / está mal porque el contenido sigue siendo de una página que no es un informe; solo cambia el formato.
- D: tienta porque filtraría las páginas malas y "funciona" / está mal porque agrega un agente entero (latencia, costo) para algo que resuelve una tool acotada.

**Review:** Capítulo 5 (2A), Tema 10 — Tool scoping (reemplazar tools genéricas por acotadas); Trampa 9.

**Pista de lectura (es):** "follows a result to a login wall … as if it were a report" → "sigue un resultado hasta una pantalla de login … como si fuera un informe" (la tool genérica acepta cualquier URL).

</details>

#### P11 · 2A · 2.3 · Multi-Agent Research System
The document analysis subagent must call `extract_metadata` on each document before any enrichment tool, because enrichment looks up the company and fiscal period that `extract_metadata` returns. The system prompt already says "Always call extract_metadata first," yet in 6% of documents the subagent calls `lookup_company_profile` first and enriches the wrong entity. After metadata is extracted, the enrichment tools needed vary by document. Which configuration most reliably fixes this?

A) Set `tool_choice` to `"any"` for every request so that the subagent must call a tool and cannot skip straight to a text answer.

B) Set `strict: true` on `extract_metadata` so that its call is guaranteed and its inputs always match the tool's schema.

C) Force `{"type": "tool", "name": "extract_metadata"}` on every request in the loop so that metadata is always extracted before enrichment.

D) Force `{"type": "tool", "name": "extract_metadata"}` on the first request, then switch `tool_choice` to `"auto"` for the follow-up turns.

<details>
<summary>Ver respuesta</summary>

**Respuesta correcta: D**

**Why (es):** Para garantizar que una tool específica vaya primero, la guía pide forced tool selection en el primer turno y procesar los pasos siguientes en turnos posteriores con `auto`, porque las tools de enriquecimiento varían por documento. (La guía evalúa auto/any/forced aunque la documentación actual dé 400 con forced en algunos modelos nuevos.)

**Distractors (es):**
- A: tienta porque "any" suena a obligatorio / está mal porque obliga a llamar alguna tool, no `extract_metadata`: puede seguir empezando por `lookup_company_profile`.
- B: tienta porque "strict" suena a garantía / está mal porque garantiza inputs válidos, no que la tool se llame ni el orden.
- C: tienta porque usa el mecanismo correcto / está mal porque forzarlo en todos los turnos impide llamar a las tools de enriquecimiento y el loop nunca avanza.

**Review:** Capítulo 5 (2A), Tema 11 — tool_choice: auto, any, tool y none (patrón de dos turnos); Trampa 8.

**Pista de lectura (es):** "the enrichment tools needed vary by document" → "las tools de enriquecimiento necesarias cambian según el documento" (después del primer paso, Claude decide: `auto`).

</details>

### Escenario: Developer Productivity with Claude

You are building a developer productivity agent for TiendaX's engineering team with the Claude Agent SDK. The agent explores and modifies a 1,800-file TypeScript monorepo using the built-in tools Read, Write, Edit, Bash, Grep, and Glob. It also connects to internal MCP servers, including `tiendax-codeintel`, to answer developers' questions and implement small changes.

#### P12 · 2C · 2.5 · Developer Productivity with Claude
A developer asks the agent to explain why checkout sometimes shows the message "Coupon cannot be combined with free shipping." Trace logs show the agent ran Glob with `src/**/*.ts` and then began calling Read on each of the 1,140 matching files; the session hit its context limit after 310 files without producing an answer. Which approach should the agent take instead?

A) Switch the agent to a model with a larger context window so that all matching TypeScript files fit in a single session.

B) Use Glob with `**/*coupon*` to narrow the file set, then Read every returned file before answering the developer's question.

C) Grep for the error message to locate its entry point, then Read that file and follow its imports to the relevant logic.

D) Read the twenty most recently modified files under `src/checkout/` first, since recent changes most likely introduced the behavior.

<details>
<summary>Ver respuesta</summary>

**Respuesta correcta: C**

**Why (es):** La guía pide explorar de forma incremental: Grep para encontrar los entry points (acá, el mensaje de error, que es texto dentro de un archivo) y después Read siguiendo los imports, en lugar de leer todo de entrada. Así se leen 3 o 4 archivos en vez de 1.140, y se sigue el camino real del código.

**Distractors (es):**
- A: tienta porque el síntoma visible es "se quedó sin contexto"; está mal porque es el parche de "modelo más grande": sigue leyendo todo y diluye la atención, sin atacar la causa.
- B: tienta porque achica la lista y usa una tool de búsqueda; está mal porque Glob busca por nombre de archivo, no por contenido (el mensaje puede estar en un archivo que no se llama "coupon"), y sigue leyendo todo de entrada.
- D: tienta porque "lo último que cambió" suena a buen filtro; está mal porque la fecha de modificación no dice dónde está el flujo; Grep sí.

**Review:** Capítulo 7 (2C), Tema 5 — Incremental codebase exploration y Tema 2 — Grep vs. Glob; Trampas 1 y 5.

**Pista de lectura (es):** "began calling Read on each of the 1,140 matching files" → "empezó a llamar a Read sobre cada uno de los 1.140 archivos que coincidían" (está leyendo todo de entrada: falta exploración incremental).

</details>

#### P13 · 2C · 2.5 · Developer Productivity with Claude
The agent must raise the retry count for the `andreani` carrier only, in `src/shipping/carriers.config.ts`. Its Edit call with `old_string: "retries: 3,"` fails because that exact line appears in four carrier blocks, and the other three carriers must keep their current value. A teammate notes that Edit has handled every other change this week without problems. What's the correct approach to complete this change?

A) Read the entire file, produce the full content with only the `andreani` value changed, and Write the complete file back.

B) Repeat the Edit call with `replace_all: true` so the tool no longer rejects the change for matching several locations.

C) Write only the corrected `andreani` block to `carriers.config.ts`, leaving the remaining carrier blocks out of the operation.

D) Configure the agent to use Read plus Write for every file modification, so ambiguous matches can never block it again.

<details>
<summary>Ver respuesta</summary>

**Respuesta correcta: A**

**Why (es):** Edit necesita que `old_string` aparezca exactamente una vez. Cuando falla por coincidencia no única, la guía indica Read + Write como fallback confiable: leer el archivo completo, armar el contenido corregido y escribirlo entero.

**Distractors (es):**
- B: tienta porque hace que Edit "funcione"; está mal porque `replace_all` cambia las cuatro ocurrencias y solo había que cambiar la de `andreani`.
- C: tienta porque parece más liviano escribir solo el bloque; está mal porque Write reemplaza el archivo entero: se borrarían los otros tres carriers y todo lo demás.
- D: tienta porque Read + Write es "el confiable"; está mal porque es el plan B, no la forma normal: para cambios puntuales con ancla única se usa Edit (el compañero confirma que Edit anda bien en los demás casos), y reescribir archivos enteros por una línea arriesga alterar otras.

**Review:** Capítulo 7 (2C), Tema 4 — Cuando Edit falla: Read + Write, y Tema 3 — Read, Write y Edit; Trampas 3 y 4.

**Pista de lectura (es):** "that exact line appears in four carrier blocks" → "esa línea exacta aparece en cuatro bloques de transportistas" (el ancla no es única: Edit no puede elegir cuál).

</details>

#### P14 · 2C · 2.5 · Developer Productivity with Claude
A developer asks the agent to list every call site of `processRefund` before its signature changes. The agent runs Grep for `processRefund\(` and reports six call sites, all in `src/orders/`, although the developer knows checkout also issues refunds. Reviewing the code, you find that `src/payments/index.ts` re-exports the function under other names, including `export { processRefund as refund }` and `export { processRefund as issueStoreCredit }`, and 140 modules import from that index file. How should the agent find the complete set of call sites?

A) Run Grep again with a broader regular expression such as `.*[Rr]efund.*` so that variations of the original name are also matched.

B) Use Glob with `**/*refund*` across the repository to locate every file related to refunds, then report those files as call sites.

C) Grep for imports of `src/payments`, then Read every importing file in full and inspect each refund-related call by hand.

D) Read `src/payments/index.ts` to identify every name it exports for the function, then run Grep for each of those names.

<details>
<summary>Ver respuesta</summary>

**Respuesta correcta: D**

**Why (es):** El índice es un wrapper module que re-exporta la función con otros nombres. La guía pide identificar primero todos los nombres que exporta el wrapper y después hacer Grep por cada uno (`refund(`, `issueStoreCredit(`, `processRefund(`).

**Distractors (es):**
- A: tienta porque "atrapa más"; está mal porque no cubre alias arbitrarios (`issueStoreCredit` no contiene "refund") y trae muchísimo ruido.
- B: tienta porque Glob también "busca"; está mal porque busca nombres de archivo, no llamadas dentro del código: un archivo de checkout que llama `refund()` no se llama así.
- C: tienta porque parece exhaustivo y encontraría los usos; está mal porque obliga a leer 140 módulos enteros cuando, con la lista de exports, Grep lo resuelve en pocas llamadas.

**Review:** Capítulo 7 (2C), Tema 6 — Wrapper modules; Trampa 6.

**Pista de lectura (es):** "re-exports the function under other names" → "vuelve a exportar la función con otros nombres" (hay alias: buscar el nombre original no alcanza).

</details>

#### P15 · 2B · 2.4 · Developer Productivity with Claude
The `tiendax-codeintel` MCP server provides `find_references(symbol)`, which queries the TypeScript compiler index and resolves aliases, re-exports, and dynamic imports. Its description reads only "Finds references." Over the last 200 sessions, the agent chose Grep instead in 87% of "where is this used?" questions, and its answers missed aliased call sites. Grep remains the right tool for locating error messages and log strings. What's the most effective way to address this?

A) Remove Grep from the agent's `allowedTools` so that `find_references` becomes the only available option for locating where a symbol is used.

B) Expand the `find_references` description to explain its compiler-index resolution of aliases and re-exports, what it returns, and when to prefer it over Grep.

C) Add a `PreToolUse` hook that blocks Grep whenever the search pattern looks like a code identifier, forcing the agent to retry with `find_references`.

D) Add a system prompt instruction stating that the agent must always call `find_references` whenever a developer asks where a symbol is used.

<details>
<summary>Ver respuesta</summary>

**Respuesta correcta: B**

**Why (es):** Claude elige tools leyendo sus descripciones. "Finds references." no dice nada que Grep no haga, así que el agente prefiere la built-in conocida. La guía pide mejorar la descripción de la tool MCP explicando en detalle sus capacidades y lo que devuelve, para que el agente vea por qué es mejor que la alternativa genérica.

**Distractors (es):**
- A: tienta porque elimina la alternativa; está mal porque Grep tiene usos legítimos (el propio enunciado lo dice: mensajes de error y logs) y no se arregla la causa.
- C: tienta porque es programático y en 1D lo programático era lo confiable; está mal porque el enforcement es para reglas críticas, acá el problema es una descripción pobre, y el filtro "parece un identificador" bloquearía búsquedas válidas.
- D: tienta porque es directo y barato; está mal porque no ataca la causa (la descripción) y es una regla atada a frases que falla cuando la pregunta viene redactada de otra forma.

**Review:** Capítulo 6 (2B), Tema 8 — Que el agente use la tool MCP y no Grep; Capítulo 7 (2C), Tema 11 — Built-in vs. MCP tools; Trampa 4 de 2B.

**Pista de lectura (es):** "Its description reads only "Finds references."" → "Su descripción dice solamente 'Encuentra referencias.'" (la descripción no explica qué la hace mejor que Grep).

</details>

---

### Escenario: Code Generation with Claude Code

Your team uses Claude Code in TiendaX's shared `storefront` repository, where twelve developers work on the checkout and catalog services. The team wants consistent integrations with GitHub, Jira, and an internal `tiendax-pedidos` MCP server that exposes order data, while letting individual developers try other tools without affecting their colleagues.

#### P16 · 2B · 2.4 · Code Generation with Claude Code
Lucía wants to try a community MCP server that generates architecture diagrams. She is not sure it is useful yet, and her colleagues should neither see it nor be prompted to approve it. Where should she configure it?

A) In the project's `.mcp.json`, committed on her own feature branch

B) In `.claude/settings.local.json` inside the repository

C) In her user-level `~/.claude.json`

D) In the repository's `CLAUDE.md`, under an MCP servers section

<details>
<summary>Ver respuesta</summary>

**Respuesta correcta: C**

**Why (es):** La guía distingue dos niveles: `.mcp.json` del proyecto para el tooling compartido del equipo, y `~/.claude.json` para servidores personales o experimentales. Un servidor que solo quiere probar ella va en su `~/.claude.json`.

**Distractors (es):**
- A: tienta porque una rama no toca `main`; está mal porque `.mcp.json` es configuración de proyecto pensada para compartir: cuando la rama se comparta o se mergee, a los demás les aparece el pedido de aprobación.
- B: tienta porque "local" suena a personal y ese archivo no se commitea; está mal porque ahí no se definen servidores MCP: el "local scope" de MCP vive en `~/.claude.json`.
- D: tienta porque `CLAUDE.md` es la memoria del proyecto; está mal porque son instrucciones en lenguaje natural, no configuración de servidores, y además se comparte con todo el equipo.

**Review:** Capítulo 6 (2B), Tema 4 — Scopes: `.mcp.json` vs. `~/.claude.json`; Trampa 3.

**Pista de lectura (es):** "her colleagues should neither see it nor be prompted to approve it" → "sus compañeros no deberían verlo ni recibir el pedido de aprobación" (es personal: nada que viva en el repo).

</details>

#### P17 · 2B · 2.4 · Code Generation with Claude Code
Today each developer adds the GitHub and Jira MCP servers by running `claude mcp add` without a scope, following a wiki page, and their configurations have drifted apart. Your tech lead wants them standardized. A draft pull request commits the servers with a personal Jira API token in plain text, arguing that the repository is private. Another teammate suggests writing a custom Jira MCP server for full control, although the team only needs to read and comment on tickets. Which TWO actions should you take? (Choose two.)

A) Commit both server entries to `.mcp.json` at the repository root, referencing `${GITHUB_TOKEN}` and `${JIRA_API_TOKEN}` from each developer's environment.

B) Keep the literal Jira token in the committed `.mcp.json`, since only TiendaX employees with repository access can read the file.

C) Update the wiki so each developer adds both servers to their own `~/.claude.json`, keeping every credential out of version control.

D) Adopt an existing community-maintained Jira MCP server instead of building a custom one, since ticket access is a standard integration.

E) Load the GitHub and Jira servers in separate Claude Code sessions so that only one server's tools are available at any time.

<details>
<summary>Ver respuesta</summary>

**Respuesta correcta: A+D**

**Why (es):** A: lo que usa todo el equipo va en `.mcp.json` del proyecto (compartido y versionado), y la expansión `${VAR}` permite commitearlo sin secretos: cada dev tiene su token en su entorno. D: para integraciones estándar como Jira, la guía pide usar un servidor de la comunidad antes que programar uno propio; los custom quedan para flujos propios del equipo (como `tiendax-pedidos`).

**Distractors (es):**
- B: tienta porque "nadie de afuera lo ve"; está mal porque un repo privado no es lugar para secretos: queda en el historial de git, lo ven todos los que tienen acceso y viaja en forks y backups.
- C: tienta porque saca los secretos de git; está mal porque es justo lo que causó el problema: no es compartido ni versionado y las configuraciones vuelven a divergir.
- E: tienta porque parece evitar conflictos entre tools; está mal porque las tools de todos los servidores configurados se descubren al conectar y están disponibles a la vez (el prefijo `mcp__<servidor>__` evita choques de nombres).

**Review:** Capítulo 6 (2B), Temas 4, 5, 7 y 9 — Scopes, `${VAR}`, varios servidores a la vez y community vs. custom; Trampas 1, 2, 6 y 8.

**Pista de lectura (es):** "although the team only needs to read and comment on tickets" → "aunque el equipo solo necesita leer y comentar tickets" (es una integración estándar: no justifica un servidor propio).

</details>

#### P18 · 2B · 2.4 · Code Generation with Claude Code
The custom `tiendax-pedidos` server exposes `list_tables`, `describe_table`, and `run_query`. Session logs show that before almost every real query, Claude makes five to seven `list_tables` and `describe_table` calls just to discover which of the 46 tables and their columns exist. Migrations add or alter tables in most sprints. What change would most effectively reduce these calls?

A) Add a `describe_all_tables` tool that returns every table and column in one response, replacing the separate discovery calls.

B) Expose the current database schema as an MCP resource on `tiendax-pedidos`, giving Claude a catalog of the available tables and columns.

C) Paste the full schema into the project's `CLAUDE.md` so that Claude has every table and column in context from the start of each session.

D) Split the server into separate schema and query servers so that Claude connects to the schema server only when it needs to explore.

<details>
<summary>Ver respuesta</summary>

**Respuesta correcta: B**

**Why (es):** La guía usa los resources para exponer catálogos de contenido (esquemas de base de datos, índices de documentación, resúmenes de issues) y así el agente ve qué datos hay sin hacer llamadas exploratorias. Las tools quedan para las acciones (`run_query`). Como lo mantiene el servidor, el catálogo sigue al día con las migraciones.

**Distractors (es):**
- A: tienta porque reduce siete llamadas a una; está mal porque sigue siendo una llamada exploratoria a una tool: "resources for content catalogs, tools for actions".
- C: tienta porque pone el esquema en contexto desde el principio; está mal porque es una copia a mano que nadie mantiene, y con migraciones casi todos los sprints queda desactualizada enseguida.
- D: tienta porque separa responsabilidades; está mal porque las tools de todos los servidores están disponibles a la vez y las llamadas exploratorias siguen ahí: es sobreingeniería que no ataca la causa.

**Review:** Capítulo 6 (2B), Tema 3 — Resources as content catalogs; Trampa 5.

**Pista de lectura (es):** "just to discover which of the 46 tables and their columns exist" → "solo para descubrir cuáles de las 46 tablas y sus columnas existen" (llamadas exploratorias: falta un catálogo).

</details>
