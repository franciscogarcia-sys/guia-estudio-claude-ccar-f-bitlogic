# Repasos (preguntas que mezclan módulos)

## Repaso mixto (módulos 1 y 2)

#### R1 · 1A · 1.1 · Structured Data Extraction
*Scenario:* You are building a TiendaX agent that extracts line items from multi-page supplier invoices, using a custom agentic loop over the Claude API.

Your agent reads each invoice with `fetch_invoice_page(page_number)` and finishes by calling `submit_invoice`. To keep requests small, the loop rebuilds `messages` on every turn from the original request, the latest assistant response, and only the newest `tool_result`. On invoices of three or more pages, the agent requests page 1 again, and submitted line items cover only the final page. What is the most likely root cause?

A) The invoices exceed the model's context window, so you should switch to a model with a larger window that can hold every page at once.

B) The `fetch_invoice_page` description does not explain pagination, so the model cannot tell which pages it has already retrieved.

C) The loop keeps only the newest `tool_result` in `messages`, so earlier pages no longer exist for the model when it continues or submits.

D) The `submit_invoice` schema does not require a per-page breakdown, so the model is not forced to include line items from every page.

<details>
<summary>Ver respuesta</summary>

**Respuesta correcta: C**

**Why (es):** El enunciado muestra el código del loop, y la causa está ahí: al reconstruir `messages` con solo el último `tool_result`, las páginas anteriores desaparecen del historial. El modelo no recuerda nada entre llamadas: lo que no está en el historial no existe. Por eso vuelve a pedir la página 1 y entrega solo los ítems de la última.

**Distractors (es):**
- A: tienta porque las facturas largas suenan a "no entra en el contexto"; está mal porque el loop recorta el historial a propósito: un modelo más grande recibiría el mismo historial recortado.
- B: tienta porque la descripción de la tool es lo que más pesa en 2A; está mal porque el modelo sabría qué páginas leyó si esas páginas siguieran en el historial.
- D: tienta porque un schema más estricto parece forzar la completitud; está mal porque el modelo no puede incluir ítems de páginas que ya no ve: ataca el síntoma en la salida, no la causa en el loop.

**Review:** Capítulo 1 (1A), Tema 7 (in-context memory); Trampa 3.

**Pista de lectura (es):** "the loop rebuilds `messages` on every turn from … only the newest `tool_result`" → "el loop rearma `messages` en cada vuelta con … solo el `tool_result` más nuevo" (el loop tira los resultados anteriores: la causa está en el código).

</details>

#### R2 · 1C · 1.7 · Developer Productivity with Claude
*Scenario:* You use Claude Code to explore and audit unfamiliar parts of TiendaX's .NET backend over several working days.

Yesterday you spent two hours in a named Claude Code session, `promo-engine-audit`, mapping how TiendaX's promotions engine applies discount rules across 36 files. Overnight, a teammate merged a small fix that touched only `CouponStacker.cs` and `RuleCache.cs`; the other 34 files are unchanged. You want to continue the audit today. What's the most effective way to proceed?

A) Run `claude --resume promo-engine-audit`, tell Claude that `CouponStacker.cs` and `RuleCache.cs` changed, and ask it to re-analyze only those two files.

B) Start a new session with a structured summary of yesterday's findings, and have Claude re-read the current code of all 36 files before continuing.

C) Run `claude --resume promo-engine-audit --fork-session` so the audit continues in a branch isolated from yesterday's outdated tool results.

D) Run `claude --resume promo-engine-audit` and ask Claude to continue the audit, since it will see both changes the next time it reads those files.

<details>
<summary>Ver respuesta</summary>

**Respuesta correcta: A**

**Why (es):** Cambiaron 2 de 36 archivos: el contexto de la sesión sigue mayormente válido. La guía dice retomar la sesión e informar qué archivos cambiaron, para un re-análisis dirigido (targeted re-analysis). Sesión nueva con resumen estructurado es para cuando los tool results quedaron mayormente stale, como en la pregunta original (31 de 40).

**Distractors (es):**
- B: tienta porque fue la correcta en la pregunta original del error; está mal porque acá casi todo el análisis sigue valiendo, y tirarlo para releer 36 archivos es caro e innecesario.
- C: tienta porque "aislado de lo viejo" suena a limpiar; está mal porque el fork copia el historial completo, con los resultados viejos incluidos, y sirve para divergir en dos caminos, no para actualizar.
- D: tienta porque retoma la sesión correcta; está mal porque la sesión guarda la conversación, no los archivos: Claude seguiría razonando con su análisis viejo de esos dos archivos sin saber que cambiaron.

**Review:** Capítulo 3 (1C), Tema 11.2–11.4 — Avisar qué cambió, retomar o empezar de cero, fork; Trampa 8.

**Pista de lectura (es):** "touched only `CouponStacker.cs` and `RuleCache.cs`; the other 34 files are unchanged" → "tocó solo esos dos archivos; los otros 34 no cambiaron" (contexto mayormente válido → resume + avisar).

</details>

#### R3 · 1D · 1.4 · Customer Support Resolution Agent
*Scenario:* You are building SoporteBot, TiendaX's support agent on the Claude Agent SDK, which resolves account and order issues and escalates to human agents.

Production logs show two separate problems. In 4% of conversations the agent calls `issue_store_credit` before `verify_identity` has returned a match, and several credits went to the wrong account. Separately, it escalates routine size exchanges to humans while attempting policy-exception requests on its own. Your team wants a single change set that fixes both. Which approach should you take?

A) Add a PreToolUse hook that blocks `issue_store_credit` without a verified identity, and a second hook that forces escalation whenever a policy exception is detected.

B) Add explicit rules and few-shot examples to the system prompt covering both the verification order and when to escalate versus resolve.

C) Block `issue_store_credit` until verification succeeds, and have the agent escalate whenever its self-reported confidence in a resolution falls below 7 out of 10.

D) Block `issue_store_credit` in code until `verify_identity` returns a match, and add explicit escalation criteria with few-shot examples to the system prompt.

<details>
<summary>Ver respuesta</summary>

**Respuesta correcta: D**

**Why (es):** Son dos reglas de tipo distinto. El orden verificar → acreditar es determinístico y hay plata en juego: prerrequisito programático (o hook) que bloquea la tool hasta que la verificación devuelva un match. Cuándo escalar es un juicio (¿es una excepción a la política?): criterios explícitos con few-shot en el prompt. La única opción que usa cada herramienta para lo suyo es D.

**Distractors (es):**
- A: tienta porque los hooks "garantizan" y la primera mitad es correcta; está mal porque detectar una excepción a la política es juicio, no un `if`: un hook no puede decidirlo.
- B: tienta porque la segunda mitad es correcta y es barato; está mal porque deja la verificación de identidad en el prompt, que es probabilístico, con dinero en juego.
- C: tienta porque la primera mitad es correcta y el umbral suena objetivo; está mal porque la confianza autoinformada está mal calibrada: el agente se siente seguro justo en los casos difíciles.

**Review:** Capítulo 4 (1D), Tema 6 — Programmatic prerequisites y Tema 12 — ¿Hook o prompt?; Trampas 1 y 5.

**Pista de lectura (es):** "Production logs show two separate problems" → "los logs muestran dos problemas distintos" (cada uno pide un mecanismo distinto: código para el orden, prompt para el juicio).

</details>

#### R4 · 2C · 2.5 · Claude Code for CI/CD
*Scenario:* You run Claude Code non-interactively in TiendaX's CI pipeline to perform automated maintenance on a large React repository.

A nightly job asks Claude Code to migrate every React test that still calls the deprecated helper `renderWithStore(`. The job log shows Claude ran Glob with `**/*renderWithStore*`, received zero results, and reported that no migration was needed, even though developers know dozens of the repository's 1,400 `*.test.tsx` files still use the helper. Which approach should Claude take instead?

A) Run Glob with `**/*.test.tsx` to list every test file, then Read each match to check whether it calls the deprecated helper.

B) Run Grep for `renderWithStore\(` with a `**/*.test.tsx` glob filter, then Read only the matching files before editing them.

C) Run Glob with a broader pattern such as `**/*{render,Store}*.test.tsx` so test files with related names are also included.

D) Run a Bash command such as `find . -name "*.test.tsx" | xargs grep -l renderWithStore` to combine both searches in one step.

<details>
<summary>Ver respuesta</summary>

**Respuesta correcta: B**

**Why (es):** Glob busca archivos por nombre; Grep busca líneas dentro de los archivos. "Qué tests llaman a `renderWithStore(`" es búsqueda de contenido: Grep por el patrón, acotado a `**/*.test.tsx` con su filtro `glob`, y después Read solo de los archivos encontrados (exploración incremental).

**Distractors (es):**
- A: tienta porque Glob `**/*.test.tsx` es el ejemplo de la guía para listar tests; está mal porque después lee 1.400 archivos uno por uno para hacer lo que Grep resuelve en una búsqueda (y llena el contexto).
- C: tienta porque "ampliar el patrón" parece arreglar el cero; está mal porque sigue buscando por nombre de archivo, y el helper está en el contenido.
- D: tienta porque funciona; está mal porque en preguntas al estilo de la guía se usan las tools dedicadas (Grep/Glob) para buscar, y Bash queda para ejecutar (tests, build, git).

**Review:** Capítulo 7 (2C), Tema 2 — Grep vs. Glob y Tema 5 — Incremental codebase exploration; Trampas 2 y 5.

**Pista de lectura (es):** "ran Glob with `**/*renderWithStore*`, received zero results" → "usó Glob con `**/*renderWithStore*` y obtuvo cero resultados" (buscó por nombre de archivo algo que está dentro del código).

</details>
