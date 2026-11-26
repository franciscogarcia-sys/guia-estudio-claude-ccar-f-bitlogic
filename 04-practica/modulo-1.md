# Preguntas — Módulo 1 (Agentic Architecture & Orchestration · 1A–1D)

## Preguntas de fin de módulo

### P1 · 1D · 1.4 · Customer Support Resolution Agent
Your TiendaX support agent, built on the Claude Agent SDK, handles returns with `lookup_order`, `check_return_eligibility`, and `create_return_label`. Policy requires eligibility to be confirmed before any label is issued, because each label triggers a non-refundable carrier charge. An audit of 4,200 conversations shows that in 7% of them the agent called `create_return_label` without a prior `check_return_eligibility` call, usually after the customer insisted the item was "definitely within 30 days." Which change most reliably prevents ineligible labels from being issued?

A) Add a bolded rule at the top of the system prompt stating that `check_return_eligibility` must always be called before issuing any return label.

B) Add a programmatic gate that rejects `create_return_label` unless `check_return_eligibility` returned an eligible result for the same order_id in this session.

C) Rewrite the `create_return_label` tool description to state clearly that it may only be called after a successful eligibility check.

D) Run a nightly job that flags labels issued without an eligibility check and voids them before the carrier picks up the package.

<details>
<summary>Ver respuesta</summary>

**Respuesta correcta: B**

**Por qué (es):** Es un orden obligatorio con consecuencia económica. Un prompt o una descripción tienen una tasa de falla distinta de cero; un prerrequisito programático bloquea la tool de abajo hasta que el paso previo se cumplió, en el 100% de los casos.

**Distractores (es):**
- A: tienta porque es barato y directo; está mal porque sigue siendo probabilístico, y justo falla cuando el cliente presiona.
- C: tienta porque las descripciones son lo que más influye en la elección de tools; está mal porque guían la selección, no garantizan el orden.
- D: tienta porque "detecta y corrige"; está mal porque es reactivo: el cargo del carrier ya se generó y no ataca la causa.

**Repasar:** Capítulo 4 (1D), Tema 6 — Programmatic prerequisites; Trampa 1.

**Pista de lectura (es):** "triggers a non-refundable carrier charge" → "genera un cargo del transportista que no se devuelve" (hay plata en juego: hace falta enforcement en código).

</details>

### P2 · 1C · 1.2 · Multi-Agent Research System
Your TiendaX marketing research system uses a coordinator with four subagents: web search, document analysis, synthesis, and citation. Every query runs through all four in sequence. Usage data from the last month shows that 62% of queries are simple fact lookups, such as "What is Competitor B's current return window?", yet each one takes about 4 minutes and costs roughly $0.85, the same as a full multi-source competitive analysis. What's the most effective way to address this?

A) Train a separate classifier on historical queries to route simple lookups to a different single-agent system before they reach the coordinator.

B) Run the four subagents in parallel instead of in sequence so that simple lookups finish in the time of the slowest subagent.

C) Switch all four subagents to a smaller, cheaper model while keeping the coordinator on the larger model for complex analyses.

D) Have the coordinator analyze each query's requirements and invoke only the subagents it needs, such as a single search call for simple lookups.

<details>
<summary>Ver respuesta</summary>

**Respuesta correcta: D**

**Por qué (es):** La guía pide coordinadores que analizan la consulta y eligen dinámicamente qué subagents invocar, en vez de correr siempre el pipeline completo. Ataca la causa: trabajo innecesario en consultas simples.

**Distractores (es):**
- A: tienta porque suena a arquitectura con datos; está mal porque agrega un componente (y entrenamiento) para algo que es función del coordinador.
- B: tienta porque baja la latencia; está mal porque las etapas dependen entre sí y el costo de correr los cuatro sigue igual.
- C: tienta porque baja el costo por llamada; está mal porque se sigue haciendo trabajo que no hace falta y puede bajar la calidad en los casos complejos.

**Repasar:** Capítulo 3 (1C), Tema 5.3 — Dynamic selection; Trampa 6.

**Pista de lectura (es):** "Every query runs through all four in sequence" → "Cada consulta pasa por los cuatro, en secuencia" (siempre el pipeline completo).

</details>

### P3 · 1A · 1.1 · Developer Productivity with Claude
Your team built an internal assistant that answers questions about TiendaX's codebase using a custom agentic loop and a `search_docs` tool. Logs show the agent calls `search_docs` with the identical query three or four times per session before answering, and answers often ignore what the search returned. Reviewing the loop code, you see that after each tool execution it appends a user message containing only the string `"search_docs returned 12 results"` to save tokens. What is the most likely root cause?

A) The loop does not return the actual tool output in the `tool_result`, so the model cannot reason about the results and keeps requesting them.

B) The `search_docs` description is too vague, so the model cannot tell whether the search succeeded and decides to call it again.

C) The loop has no iteration cap, so nothing stops the model from repeating the same tool call several times per session.

D) The sampling temperature is too high, which makes tool selection nondeterministic and causes the model to repeat identical calls.

<details>
<summary>Ver respuesta</summary>

**Respuesta correcta: A**

**Por qué (es):** El modelo solo sabe lo que está en el historial. Si el `tool_result` no trae el contenido real, no puede usarlo para razonar y vuelve a pedirlo. La guía exige agregar los resultados de las tools al contexto entre iteraciones.

**Distractores (es):**
- B: tienta porque la descripción es el factor más importante en el uso de tools; está mal porque el problema no es elegir la tool sino que el resultado nunca le llega.
- C: tienta porque hay llamadas repetidas; está mal porque un cap solo cortaría el síntoma, y el modelo seguiría sin datos.
- D: tienta porque suena técnico; está mal porque repetir la misma query exacta indica falta de información, no aleatoriedad.

**Repasar:** Capítulo 1 (1A), Trampa 3.

**Pista de lectura (es):** "appends a user message containing only the string … to save tokens" → "agrega un mensaje user que contiene solo el texto … para ahorrar tokens".

</details>

### P4 · 1D · 1.5 · Structured Data Extraction
Your agent reconciles TiendaX supplier invoices against purchase orders using two MCP tools. `erp_get_po` returns amounts as integer cents (`123450`), while `supplier_portal_get_invoice` returns locale-formatted strings (`"1.234,50"`). The system prompt already explains both formats. Even so, 3.4% of reconciliations are flagged as false mismatches, and logs show the agent occasionally reading `"1.234,50"` as 1.23450. Which change most reliably eliminates these errors?

A) Expand the system prompt with several worked examples converting each tool's format, plus an instruction to double-check every amount before comparing.

B) Ask the supplier portal vendor to change its API to return integer cents, matching the ERP format used by the rest of the system.

C) Add a PostToolUse hook that converts amounts from both tools into one canonical decimal format before the agent processes the results.

D) Add a PreToolUse hook on both tools that validates the requested document IDs before the call, rejecting malformed purchase order numbers.

<details>
<summary>Ver respuesta</summary>

**Respuesta correcta: C**

**Por qué (es):** Datos heterogéneos de distintas tools se normalizan en un hook PostToolUse, antes de que el modelo los vea. Es determinístico y se resuelve una vez, del lado propio.

**Distractores (es):**
- A: tienta porque los ejemplos mejoran mucho; está mal porque el prompt ya lo explica y sigue fallando: es probabilístico.
- B: tienta porque "ataca la raíz"; está mal porque no controlás ese sistema y le pasás el problema a otro.
- D: tienta porque también es un hook; está mal porque PreToolUse mira los argumentos de salida, no transforma lo que la tool devuelve.

**Repasar:** Capítulo 4 (1D), Tema 11 — PostToolUse que normaliza; Trampa 4.

**Pista de lectura (es):** "The system prompt already explains both formats. Even so…" → "El system prompt ya explica los dos formatos. Aun así…" (el prompt no alcanza).

</details>

### P5 · 1C · 1.7 · Code Generation with Claude Code
On Monday you ran a named Claude Code session, `checkout-migration`, that analyzed 40 files of TiendaX's checkout module and produced a migration plan. Between Tuesday and Thursday, teammates merged a large refactor that modified 31 of those 40 files and renamed two packages. You want to continue the migration work today. What's the most effective way to proceed?

A) Run `claude --resume checkout-migration` and ask Claude to continue the plan, since the session already contains the full analysis of the module.

B) Run `claude --resume checkout-migration` and list the 31 modified files so Claude re-analyzes only those before continuing the plan.

C) Start a new session and inject a structured summary of the still-valid goals and decisions, letting Claude read the current code fresh.

D) Run `claude --resume checkout-migration --fork-session` to get a clean branch of the analysis without affecting the original session.

<details>
<summary>Ver respuesta</summary>

**Respuesta correcta: C**

**Por qué (es):** Con la mayoría de los tool results viejos (31 de 40 archivos cambiados), empezar de cero con un resumen estructurado es más confiable que retomar con resultados desactualizados.

**Distractores (es):**
- A: tienta porque "la sesión tiene todo"; está mal porque guarda la conversación, no los archivos: razona sobre código que ya no existe.
- B: tienta porque avisar qué cambió es correcto en otro contexto; está mal porque eso sirve cuando el contexto es mayormente válido, y acá casi todo está stale.
- D: tienta porque crea una sesión nueva; está mal porque el fork copia el historial, incluidos los resultados viejos.

**Repasar:** Capítulo 3 (1C), Tema 11.3 — ¿Retomar o empezar de cero?; Trampa 8.

**Pista de lectura (es):** "modified 31 of those 40 files" → "modificó 31 de esos 40 archivos" (el contexto previo está mayormente desactualizado).

</details>

### P6 · 1C · 1.3 · Multi-Agent Research System
Your team migrated the TiendaX market research coordinator to the Claude Agent SDK. Three subagents, `web-searcher`, `doc-analyzer`, and `synthesizer`, are registered through the `agents` option with clear descriptions, system prompts, and tool lists. The coordinator is configured with `allowedTools: ["Read", "Grep", "WebFetch"]`. Across 200 test runs, the coordinator never delegates: it fetches and summarizes every page itself, and the logs contain no subagent invocations. What is the most likely root cause?

A) The coordinator's allowedTools does not include "Task", so it has no mechanism to spawn any of the defined subagents.

B) The subagent descriptions are too generic, so the coordinator cannot tell which subagent fits each part of the research request.

C) Programmatic subagents are ignored by the SDK, so the definitions must be moved to markdown files under `.claude/agents/`.

D) The coordinator has WebFetch available, so it prefers doing the work itself; removing WebFetch would force it to delegate.

<details>
<summary>Ver respuesta</summary>

**Respuesta correcta: A**

**Por qué (es):** La tool Task es el mecanismo para lanzar subagents, y tiene que estar en `allowedTools` del coordinador. Sin ella no hay delegación posible, por buenas que sean las definiciones.

**Distractores (es):**
- B: tienta porque las descripciones deciden a quién delegar; está mal porque el enunciado dice que son claras y, sin Task, no hay a quién delegar.
- C: tienta porque existe la vía de filesystem; está mal porque la vía programática con `agents` es válida (y la recomendada en el SDK).
- D: tienta porque explica por qué hace todo solo; está mal porque sin Task igual no podría delegar: solo quedaría sin poder buscar.

**Repasar:** Capítulo 3 (1C), Tema 3 — AgentDefinition, Task y allowedTools; Trampa 2.

**Pista de lectura (es):** "configured with `allowedTools: ["Read", "Grep", "WebFetch"]`" → "configurado con estas tools permitidas" (fijate qué falta en la lista).

</details>

### P7 · 1B · 1.6 · Code Generation with Claude Code
You ask Claude Code to "remove the deprecated `LegacyPriceCalculator` from the monolith." Nobody knows how many call sites exist, and some are reached through reflection and configuration files. On the first attempt, Claude started editing files in alphabetical order; after 26 edits it hit a circular dependency between pricing and promotions, and the build broke in 14 places. How should you structure the task for the next attempt?

A) Write the full ordered list of files to change into CLAUDE.md so that Claude follows a fixed sequence that the team has reviewed in advance.

B) Split the work into a fixed pipeline: one pass per top-level directory in alphabetical order, followed by a single build-and-fix pass.

C) Use a model with a larger context window so that Claude can load the whole monolith at once and see every dependency before editing.

D) First map where and how the class is used, identify the high-risk call sites, then follow a prioritized plan that adapts as dependencies appear.

<details>
<summary>Ver respuesta</summary>

**Respuesta correcta: D**

**Por qué (es):** Es una tarea abierta: no se sabe qué se va a encontrar. La guía pide primero mapear la estructura, identificar las áreas de alto impacto y armar un plan priorizado que se adapta cuando aparecen dependencias (descomposición dinámica).

**Distractores (es):**
- A: tienta porque da control y revisión previa; está mal porque nadie conoce los usos todavía: la lista sería incompleta.
- B: tienta porque es una descomposición ordenada; está mal porque es un pipeline fijo para una tarea abierta y no reacciona a lo que descubre.
- C: tienta porque "ver todo" parece resolverlo; está mal porque más contexto no reemplaza el mapeo y la planificación.

**Repasar:** Capítulo 2 (1B), Trampa 3.

**Pista de lectura (es):** "Nobody knows how many call sites exist" → "Nadie sabe cuántos lugares lo llaman" (alcance desconocido: descomposición dinámica).

</details>

### P8 · 1D · 1.4 · Customer Support Resolution Agent
When SoporteBot cannot resolve a case, it calls `escalate_to_human` and fills a free-text `note` field, typically with messages such as "Customer has a billing problem, please assist." Human agents work in a separate ticketing tool and cannot see the conversation transcript. Average handle time after escalation is 14 minutes, and in 41% of escalated cases the human asks the customer again for the order number and what happened. What's the most effective way to address this?

A) Attach the full conversation transcript and every tool output to the ticket so the human agent has all the available information.

B) Make `escalate_to_human` require structured fields: customer ID, order ID, root cause found, amount involved, actions already taken, and recommended action.

C) Before escalating, have the agent ask the customer to write a short description of the problem that will be forwarded to the human agent.

D) Add a sentiment score and the agent's self-reported confidence to each ticket so human agents can prioritize the most urgent escalations.

<details>
<summary>Ver respuesta</summary>

**Respuesta correcta: B**

**Por qué (es):** El humano no tiene el transcript. La guía pide un resumen estructurado del traspaso (customer ID, causa raíz, monto, acción recomendada) para que pueda decidir sin rehacer el análisis.

**Distractores (es):**
- A: tienta porque "tiene toda la información"; está mal porque obliga al humano a rehacer el análisis que debió hacer el agente.
- C: tienta porque suma contexto; está mal porque le pasa el trabajo al cliente y sigue sin causa raíz ni recomendación.
- D: tienta porque ayuda a priorizar; está mal porque no dice qué pasó, y el sentimiento y la confianza autoinformada no son confiables.

**Repasar:** Capítulo 4 (1D), Tema 14 — Interruption points y handoff; Trampa 6.

**Pista de lectura (es):** "cannot see the conversation transcript" → "no pueden ver la transcripción de la conversación".

</details>

### P9 · 1C · 1.2 · Multi-Agent Research System
Your research coordinator spawns four search subagents in parallel for a report on home appliance pricing in Argentina. Each subagent receives the same prompt: "Research competitor pricing strategies for home appliances in Argentina." Logs show that 68% of the URLs retrieved appear in at least two subagents' results, and reviewers note that the final report says nothing about marketplace sellers or regulatory price agreements. What's the most effective way to address this?

A) Have the coordinator assign each subagent a distinct partition, such as retailer sites, marketplaces, industry news, and regulatory sources, with explicit boundaries.

B) Add a deduplication step to the synthesis subagent so that repeated sources are merged before the final report is written.

C) Replace the four search subagents with a single search subagent that runs longer, so no two agents can retrieve the same sources.

D) Raise the sampling temperature of each search subagent so that their queries diverge more and they naturally retrieve different sources.

<details>
<summary>Ver respuesta</summary>

**Respuesta correcta: A**

**Por qué (es):** Mismo prompt para todos = trabajo duplicado y huecos. La guía pide particionar el alcance entre subagents (subtemas o tipos de fuente distintos) para minimizar la duplicación y cubrir todo.

**Distractores (es):**
- B: tienta porque el informe sale sin repeticiones; está mal porque ataca el síntoma: se sigue pagando lo duplicado y los huecos siguen.
- C: tienta porque elimina la superposición; está mal porque pierde el paralelismo: el problema era el reparto, no la cantidad.
- D: tienta porque "diversifica"; está mal porque es azar, no una partición: no garantiza cubrir marketplaces ni regulación.

**Repasar:** Capítulo 3 (1C), Tema 5.1 — Partitioning; Trampa 11.

**Pista de lectura (es):** "Each subagent receives the same prompt" → "Cada subagent recibe el mismo prompt".

</details>

### P10 · 1D · 1.5 · Customer Support Resolution Agent
TiendaX policy states that discounts above 25% require supervisor approval. SoporteBot applies discounts with the `apply_discount` tool, and the rule currently lives in the system prompt. Last month, 2.8% of applied discounts exceeded 25%, almost all of them in conversations where the customer threatened to cancel their membership. Finance wants a guarantee that this never happens without approval. Which approach best meets this requirement?

A) Move the rule to the top of the system prompt in capital letters and repeat it inside the `apply_discount` tool description.

B) Add a PostToolUse hook on `apply_discount` that checks the percentage and immediately alerts a supervisor when it exceeds 25%.

C) Register a hook whose matcher is `apply_discount(percent>25)` so the hook only fires for discounts that exceed the approval threshold.

D) Add a PreToolUse hook on `apply_discount` that denies calls above 25% with a reason and redirects the agent to `escalate_to_human`.

<details>
<summary>Ver respuesta</summary>

**Respuesta correcta: D**

**Por qué (es):** "Guarantee" pide enforcement determinístico. Un hook PreToolUse intercepta la llamada antes de ejecutarse, la bloquea si viola la regla y redirige a un flujo alternativo (escalamiento humano).

**Distractores (es):**
- A: tienta porque sube el cumplimiento; está mal porque sigue siendo probabilístico, y falla justo bajo presión del cliente.
- B: tienta porque es un hook; está mal porque PostToolUse corre después: el descuento ya se aplicó.
- C: tienta porque parece más prolijo; está mal porque el matcher solo matchea nombres de tool; la condición del monto va dentro del callback.

**Repasar:** Capítulo 4 (1D), Temas 9 y 10 — hooks en el SDK y el hook que bloquea y redirige; Trampas 2 y 9.

**Pista de lectura (es):** "Finance wants a guarantee that this never happens" → "Finanzas quiere una garantía de que esto no pase nunca" (garantía = código, no prompt).

</details>

### P11 · 1C · 1.3 · Multi-Agent Research System
Your research coordinator passes web search results to the synthesis subagent as one long text block of extracted paragraphs, concatenated in retrieval order. Editors reviewing the final reports find that 22% of factual claims cannot be traced to any source, and in several cases a statistic is attributed to the wrong publication. The synthesis prompt already asks it to "cite sources for every claim." What's the most effective way to address this?

A) Strengthen the synthesis prompt with few-shot examples showing correctly cited claims and a rule to omit any statement it cannot attribute.

B) Pass findings as structured records that separate each claim's content from its metadata, such as source URL, document title, page, and date.

C) Pass the full raw HTML of every retrieved page to the synthesis subagent so it can locate the original source of each claim.

D) Add a citation-checker subagent after synthesis that searches the web to find and attach a source for each unattributed claim.

<details>
<summary>Ver respuesta</summary>

**Respuesta correcta: B**

**Por qué (es):** La síntesis no puede citar lo que no recibió separado. La guía pide datos estructurados que separen contenido de metadata (URL, documento, página) al pasar contexto entre agentes, para preservar la atribución.

**Distractores (es):**
- A: tienta porque los few-shot ayudan; está mal porque el prompt ya pide citar: la información de la fuente se perdió en el formato del handoff.
- C: tienta porque "más contexto, mejor"; está mal porque infla el contexto y sigue mezclando contenido con metadata.
- D: tienta porque suma control; está mal porque busca fuentes a posteriori (puede adjuntar una que no es) y no ataca la causa.

**Repasar:** Capítulo 3 (1C), Tema 6 — Pasar contexto sin perder las fuentes; Trampa 5.

**Pista de lectura (es):** "as one long text block of extracted paragraphs" → "como un solo bloque largo de texto con los párrafos extraídos".

</details>

### P12 · 1A · 1.1 · Claude Code for CI/CD
Your CI pipeline runs an agent that generates a release summary for each merged PR. The loop is `while response.stop_reason == "tool_use"`: execute tools, append results, call again; when the loop exits, the last text block is published to the release notes. In 9% of runs, published summaries end mid-sentence and lack the required "Risks" section. Logs for those runs show `stop_reason: "max_tokens"`. Which change most effectively fixes this?

A) Add an iteration cap of 15 turns so the loop always exits in a controlled way before the response grows long enough to be cut off.

B) Instruct Claude in the system prompt to keep every release summary short and to write the "Risks" section before all other sections.

C) After the loop exits, inspect `stop_reason`: publish only on `end_turn`, and treat `max_tokens` as truncation by raising the limit or continuing.

D) Before publishing, check whether the final text block contains a "Risks" heading, and if it does not, call the model again.

<details>
<summary>Ver respuesta</summary>

**Respuesta correcta: C**

**Por qué (es):** Salir del loop no es lo mismo que terminar. `end_turn` indica respuesta completa; `max_tokens` es truncamiento y hay que manejarlo explícitamente. La decisión se toma con `stop_reason`, no con el texto.

**Distractores (es):**
- A: tienta porque los caps "controlan" el loop; está mal porque el problema no es la cantidad de vueltas sino la longitud de una respuesta.
- B: tienta porque reduciría los cortes; está mal porque es probabilístico y no detecta cuándo igual se corta.
- D: tienta porque detecta el síntoma; está mal porque es parsear lenguaje natural para decidir si terminó, un anti-pattern de la guía.

**Repasar:** Capítulo 1 (1A), Trampa 1 ("salir no es lo mismo que terminar").

**Pista de lectura (es):** "Logs for those runs show `stop_reason: "max_tokens"`" → "Los logs de esas corridas muestran stop_reason max_tokens".

</details>

### P13 · 1C · 1.7 · Developer Productivity with Claude
You spent 90 minutes in a Claude Code session named `catalog-cache-analysis`, mapping how TiendaX's catalog service reads and invalidates its cache. The analysis is accurate and the code has not changed since. You now want to prototype two competing designs, Redis write-through and an in-process LRU with event-based invalidation, and compare them, without either exploration contaminating the other or losing the shared analysis. What's the most effective approach?

A) Fork the named session twice, once per design, so each branch starts from the shared analysis and diverges independently.

B) Resume the session, explore the Redis design, run `/compact`, and then explore the LRU design within the same conversation.

C) Start two new sessions and ask each one to re-map the catalog caching layer from scratch before prototyping its design.

D) Run `claude --continue` in two terminals, one per design, so both explorations resume from the latest session in parallel.

<details>
<summary>Ver respuesta</summary>

**Respuesta correcta: A**

**Por qué (es):** `fork_session` (en CLI, `--resume <nombre> --fork-session`) crea ramas independientes desde una base de análisis compartida para explorar enfoques divergentes. El original queda intacto.

**Distractores (es):**
- B: tienta porque reutiliza la sesión; está mal porque la segunda exploración arrastra la primera: `/compact` resume, no separa.
- C: tienta porque asegura aislamiento; está mal porque tira 90 minutos de análisis que sigue siendo válido.
- D: tienta porque parece paralelo; está mal porque `--continue` sin fork retoma la misma sesión y los dos terminales intercalan mensajes en un solo transcript.

**Repasar:** Capítulo 3 (1C), Tema 11.4 — Fork; Trampa 8.

**Pista de lectura (es):** "without either exploration contaminating the other or losing the shared analysis" → "sin que una exploración contamine a la otra ni perder el análisis compartido".

</details>

### P14 · 1D · 1.4 · Customer Support Resolution Agent
A customer writes: "My order A-5512 arrived with a broken blender, I was charged twice for A-5498, and I need to change the delivery address for A-5530, which ships tomorrow." Production data shows that in 38% of messages containing several issues, SoporteBot resolves only the first one, and 60% of those customers contact support again within 48 hours. What's the most effective way to address this?

A) Route every message that mentions more than one order directly to `escalate_to_human`, since multi-issue cases are too complex for the agent.

B) Add a system prompt reminder telling the agent to read the entire message carefully and avoid ending the conversation too early.

C) Ask the customer to open a separate ticket for each issue so that the agent can handle one clear request per conversation.

D) Decompose the message into distinct issues, investigate each one in parallel using the shared customer context, then send one unified resolution.

<details>
<summary>Ver respuesta</summary>

**Respuesta correcta: D**

**Por qué (es):** La guía pide descomponer los pedidos con varios problemas en ítems distintos, investigarlos en paralelo con contexto compartido y sintetizar una resolución unificada.

**Distractores (es):**
- A: tienta porque parece prudente; está mal porque escala casos que el agente puede resolver y empeora la resolución en el primer contacto.
- B: tienta porque va al síntoma; está mal porque no cambia la estructura de la tarea: sigue tratando el mensaje como un solo problema.
- C: tienta porque simplifica al agente; está mal porque le pasa el problema al cliente.

**Repasar:** Capítulo 4 (1D), Tema 13 — Pedidos con varios problemas.

**Pista de lectura (es):** "resolves only the first one" → "resuelve solo el primero".

</details>

### P15 · 1B · 1.6 · Claude Code for CI/CD
Your CI runs a single Claude agent on every front-end PR with the instruction "review this change for any issues you find relevant." Team policy requires every PR to be checked for security, performance, and accessibility. An audit of 300 reviews shows accessibility was never mentioned in 31% of them, performance in 18%, and the depth of each review varied widely from PR to PR. How should you restructure the review?

A) Replace the single agent with an orchestrator that inspects each diff and dynamically decides which specialist subagents to spawn for that PR.

B) Use a fixed prompt chain that runs a dedicated step for security, performance, and accessibility on every PR, followed by a consolidation step.

C) Add a line to the prompt stating that every review must always cover security, performance, and accessibility with equal depth.

D) Run the same open-ended review three times per PR and publish the union of all findings so fewer aspects are missed.

<details>
<summary>Ver respuesta</summary>

**Respuesta correcta: B**

**Por qué (es):** Es una revisión predecible de varios aspectos fijos: la guía pide prompt chaining (pipeline fijo) para ese caso. Cada aspecto obligatorio tiene su paso y no depende de que el modelo "se acuerde".

**Distractores (es):**
- A: tienta porque suena más inteligente; está mal porque la decisión dinámica es justo lo que hace que se salteen aspectos obligatorios.
- C: tienta porque es un cambio de una línea; está mal porque es probabilístico y no cambia la estructura.
- D: tienta porque suma cobertura; está mal porque triplica el costo y sigue sin garantizar cada aspecto en cada PR.

**Repasar:** Capítulo 2 (1B), Trampa 3 — ¿Pipeline fijo o descomposición dinámica?

**Pista de lectura (es):** "Team policy requires every PR to be checked for security, performance, and accessibility" → "La política exige revisar cada PR en seguridad, rendimiento y accesibilidad" (aspectos fijos y conocidos).

</details>

### P16 · 1C · 1.3 · Multi-Agent Research System
Your coordinator researches e-commerce return policies in five independent regional markets, delegating one market to each search subagent. Each subagent takes about 4 minutes. Logs show the coordinator emits one Task call, waits for its result, then emits the next one in a later turn, so the full run takes about 22 minutes. Product wants results in under 6 minutes without reducing coverage. What's the most effective way to achieve this?

A) Switch to a peer-to-peer topology so each search subagent can hand its results directly to the next one without waiting for the coordinator.

B) Reduce to two search subagents, each covering two or three markets, so there are fewer round trips between the coordinator and subagents.

C) Have the coordinator emit all five Task calls in a single response so the search subagents run concurrently instead of one per turn.

D) Lower each search subagent's maxTurns so that every market finishes faster, accepting slightly shallower results to meet the time target.

<details>
<summary>Ver respuesta</summary>

**Respuesta correcta: C**

**Por qué (es):** Para correr subagents en paralelo, el coordinador tiene que emitir varias llamadas a Task en una misma respuesta, no en turnos separados. Cinco de 4 minutos en paralelo tardan cerca de lo que tarda el más lento.

**Distractores (es):**
- A: tienta porque el curso dice que P2P baja la latencia; está mal porque la lentitud venía de no paralelizar, y la guía exige rutear por el coordinador.
- B: tienta porque menos rondas parece más rápido; está mal porque cada subagent hace más trabajo en serie.
- D: tienta porque baja el tiempo; está mal porque viola "sin reducir cobertura" y no ataca la causa.

**Repasar:** Capítulo 3 (1C), Tema 4 — Lanzar subagents en paralelo; Trampa 3.

**Pista de lectura (es):** "emits the next one in a later turn" → "emite la siguiente en un turno posterior" (serie, no paralelo).

</details>

### P17 · 1D · 1.5 · Code Generation with Claude Code
TiendaX's CLAUDE.md says: "Never edit migration files under `db/migrations/` that have already been applied." Applied migrations are listed in `db/applied.txt`. In 3 of the last 50 Claude Code sessions, Claude edited an applied migration anyway, causing checksum failures in staging that took hours to untangle. You need this rule enforced every time, not most of the time. Which change achieves this?

A) Add a PreToolUse hook matching `Edit|Write` that checks `file_path` against `db/applied.txt` and exits with code 2, with the reason on stderr.

B) Add a PostToolUse hook matching `Edit|Write` that detects edits to applied migrations and exits with code 2 to block the change.

C) Repeat the rule in capital letters at the top of CLAUDE.md and also add it to a CLAUDE.md file inside `db/migrations/`.

D) Add a PreToolUse hook matching `Edit|Write` that checks `file_path` against `db/applied.txt` and exits with code 1 when it matches.

<details>
<summary>Ver respuesta</summary>

**Respuesta correcta: A**

**Por qué (es):** "Every time" pide un hook, no instrucciones. PreToolUse previene antes de ejecutar, el filtro por path va dentro del hook (el matcher solo ve el nombre de la tool) y exit 2 bloquea y le manda el motivo a Claude.

**Distractores (es):**
- B: tienta porque exit 2 bloquea en otros eventos; está mal porque en PostToolUse la edición ya ocurrió: exit 2 solo le muestra el mensaje.
- C: tienta porque CLAUDE.md es el lugar de las reglas del proyecto; está mal porque es guía probabilística: ya está ahí y falla.
- D: tienta porque es casi igual a la correcta; está mal porque exit 1 es un error no bloqueante: la edición sigue.

**Repasar:** Capítulo 4 (1D), Tema 8 — exit codes y ¿bloquea u observa?; Tema 12; Trampas 2 y 3.

**Pista de lectura (es):** "enforced every time, not most of the time" → "que se cumpla siempre, no casi siempre".

</details>

### P18 · 1C · 1.2 · Multi-Agent Research System
Your research system produces a report on consumer financing for electronics in Latin America. The coordinator runs search, analysis, and synthesis once and returns the result. Reviewers find that 40% of reports ship with notes such as "No data was found on BNPL adoption in Peru or Colombia," even though a targeted search usually finds that data in minutes. What's the most effective way to address this?

A) Let the synthesis subagent call the search subagent directly whenever it detects a gap, so missing data is fetched without involving the coordinator.

B) Have the coordinator evaluate each synthesis draft for gaps, re-delegate targeted queries to search and analysis, and re-synthesize until coverage criteria are met.

C) Instruct the search subagents to retrieve three times as many sources on the first pass so that gaps are less likely to appear later.

D) Give the synthesis subagent the full set of web search tools so it can fill any gap on its own while writing the report.

<details>
<summary>Ver respuesta</summary>

**Respuesta correcta: B**

**Por qué (es):** La guía pide un loop de refinamiento iterativo: el coordinador evalúa la síntesis, detecta huecos, vuelve a delegar con consultas dirigidas y re-sintetiza. Todo pasa por el coordinador.

**Distractores (es):**
- A: tienta porque es más rápido; está mal porque es comunicación directa entre subagents: se pierde observabilidad y control de errores.
- C: tienta porque se anticipa; está mal porque es especulativo, cuesta más y no garantiza cubrir el hueco puntual.
- D: tienta porque resuelve en un paso; está mal porque sobre-aprovisiona tools y rompe la separación de responsabilidades.

**Repasar:** Capítulo 3 (1C), Tema 5.4 — Iterative refinement loop; Trampa 6.

**Pista de lectura (es):** "runs search, analysis, and synthesis once and returns the result" → "corre búsqueda, análisis y síntesis una sola vez y devuelve el resultado" (no hay ciclo de refinamiento).

</details>
