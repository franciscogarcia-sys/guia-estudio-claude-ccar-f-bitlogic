# Preguntas — Módulo 4 (Prompt Engineering & Structured Output · 4A–4C)

## Preguntas de fin de módulo

### Escenario: Claude Code for Continuous Integration

You are building TiendaX's automated pull request reviewer, which runs Claude Code in the CI pipeline of a TypeScript monorepo (`checkout`, `pagos`, `catalogo`). It posts inline comments on every PR, and all money is stored as integer cents (`priceCents`). The team's goal is actionable feedback that developers trust, with minimal false positives.

#### P1 · 4A · 4.1 · Claude Code for Continuous Integration
The reviewer averaged 31 comments per PR, and a sample of 200 showed that most were about naming, formatting, or refactoring patterns used throughout the repo. A teammate already added "Only report findings you are highly confident about," which cut the average to 12 comments, but last week a PR that applied a discount in pesos to `priceCents` was merged without a single comment from the reviewer. What's the most effective way to address this?

A) Keep the high-confidence instruction, and have the reviewer attach a numeric confidence score to each finding so that only findings above 0.8 are posted.

B) Revert to the original prompt, and add a post-processing step that groups similar comments so that developers see fewer repeated naming remarks on each PR.

C) Replace the instruction with explicit categories to report, such as behavior-changing bugs and cents-versus-pesos mismatches, and categories to skip, such as anything ESLint enforces.

D) Expand the prompt's list of issues to report with detailed descriptions of money-handling bugs, so that the reviewer recognizes `priceCents` errors more reliably in future PRs.

<details>
<summary>Ver respuesta</summary>

**Respuesta correcta: C**

**Why (es):** "Only report high-confidence findings" no es un criterio: no le dice al revisor **qué** reportar, solo que reporte menos. Bajó el volumen, pero se perdió un bug real (baja el recall: la doc de los modelos actuales dice que con estas frases Claude puede encontrar el bug y no reportarlo). Lo que pide la guía para 4.1 es un criterio categórico: qué categorías se reportan (bugs que cambian el comportamiento, montos que no están en centavos) y cuáles se saltean (estilo, nombres, lo que ya chequea el linter, patrones del repo).

**Distractors (es):**
- A: tienta porque un umbral numérico suena medible; está mal porque la guía pide criterios "rather than relying on confidence-based filtering" y la confianza autoasignada no está calibrada: el bug de pesos podía salir con confianza alta o baja.
- B: tienta porque ataca el síntoma más visible (comentarios repetidos); está mal porque agrupar no cambia qué se reporta: siguen saliendo los de estilo, y no define ningún criterio.
- D: tienta porque es un criterio explícito y ataca el bug perdido; está mal porque solo dice qué reportar, no qué saltear (el ruido de estilo sigue) y deja vigente la frase de "high-confidence" que causó el problema.

**Review:** Capítulo 12 (4A), Tema 4 — Criterios explícitos en vez de "be conservative"; Trampa 1 · "Sé más conservador".

**Pista de lectura (es):** "A teammate already added 'Only report findings you are highly confident about,' which cut the average to 12 comments, but … was merged without a single comment" → "un compañero ya agregó 'reportá solo lo que tengas mucha confianza', lo que bajó el promedio a 12 comentarios, pero … se mergeó sin un solo comentario del revisor" (la frase de cautela bajó el ruido y también escondió un bug real).

</details>

#### P2 · 4A · 4.1 · Claude Code for Continuous Integration
The reviewer reports three categories: security, money handling, and performance. Over the last month, developers dismissed 64% of performance comments as false positives, most of them nested loops over arrays of three to five items, while security and money findings were confirmed over 90% of the time. A survey now shows that developers resolve every bot comment without reading it, including a valid finding about a database query not scoped to the customer. Which approach should you take while keeping the security and money findings in front of developers?

A) Temporarily disable only the performance category while you rewrite its criteria, and re-enable it once it performs well against past PRs with known outcomes.

B) Pause the reviewer on all PRs until the performance prompt is rewritten, so that developers stop learning to ignore its comments in the meantime.

C) Keep all three categories active, and label each performance comment as experimental so that developers know that this category is still being tuned.

D) Lower the reviewer's overall sensitivity so that it posts fewer comments in every category until the performance false positive rate falls below 20%.

<details>
<summary>Ver respuesta</summary>

**Respuesta correcta: A**

**Why (es):** Es la Skill de 4.1: los falsos positivos de una categoría hacen que el equipo desconfíe de **todas** (por eso ignoran hasta el hallazgo de seguridad). Se desactiva **temporalmente solo esa categoría** mientras se mejora su criterio, y se reactiva con evidencia (casos con respuesta conocida). Seguridad y montos siguen activas, que es justo lo que pide el alcance del enunciado.

**Distractors (es):**
- B: tienta porque corta de raíz el hábito de ignorar al bot; está mal porque rompe la condición "while keeping the security and money findings": se pierden las categorías que andan bien.
- C: tienta porque no se pierde ninguna categoría y "avisa" al equipo; está mal porque los falsos positivos siguen apareciendo y siguen erosionando la confianza en todo el revisor.
- D: tienta porque baja el ruido en general; está mal porque castiga a las categorías precisas (puede esconder hallazgos de seguridad reales) y no ataca la causa, que es el criterio de rendimiento.

**Review:** Capítulo 12 (4A), Tema 5 — Falsos positivos y confianza del equipo; Trampas 3 y 4.

**Pista de lectura (es):** "while keeping the security and money findings in front of developers" → "manteniendo los hallazgos de seguridad y de montos a la vista de los devs" (condición de alcance: descarta apagar el bot o bajar la sensibilidad de todo).

</details>

#### P3 · 4A · 4.1 · Claude Code for Continuous Integration
The team wants to use the reviewer's "critical" label to block merges through branch protection. The prompt defines severity as "critical: serious issues; major: significant issues; minor: cosmetic issues." In PR #812, assigning a pesos amount to `priceCents` was labeled critical; in PR #839, the same kind of mistake was labeled minor. What change would most effectively make severity classification consistent?

A) Instruct the reviewer to reason step by step about each finding's impact before assigning a level, and to use its best judgment for borderline cases.

B) Have the reviewer self-report a confidence score with each severity, and automatically downgrade critical findings below 0.7 to major before they are posted.

C) Add three examples of critical findings, all involving conversions between cents and pesos, so that the reviewer learns exactly what a critical issue looks like.

D) Define each level by the kind of consequence that qualifies for it, and include a concrete TypeScript example for each level, drawn from different problem areas.

<details>
<summary>Ver respuesta</summary>

**Respuesta correcta: D**

**Why (es):** Con niveles definidos por adjetivos ("serious", "significant"), cada corrida decide distinto dónde está el límite. La guía pide para cada nivel un **criterio explícito** (qué tipo de consecuencia entra: pérdida de plata o datos, comportamiento incorrecto, confusión) y **un ejemplo de código concreto**. Variar el tema de los ejemplos evita que Claude confunda el tema con el nivel.

**Distractors (es):**
- A: tienta porque razonar suele mejorar las decisiones; está mal porque "use its best judgment" es exactamente lo que produce la inconsistencia: sigue sin haber un criterio por nivel.
- B: tienta porque agrega una regla en código; está mal porque la confianza autoasignada no define la severidad, y bajar a "major" un bug de centavos con confianza 0,65 lo dejaría mergear.
- C: tienta porque los ejemplos anclan la clasificación; está mal porque cubre un solo nivel y todos del mismo tema: Claude puede creer que "crítico" significa "centavos" y no aprende dónde termina "major".

**Review:** Capítulo 12 (4A), Tema 6 — Criterios de severidad con ejemplos de código; Trampa 5.

**Pista de lectura (es):** "The prompt defines severity as 'critical: serious issues; major: significant issues; minor: cosmetic issues.'" → "el prompt define la severidad como 'crítico: problemas serios; mayor: problemas significativos; menor: cosméticos'" (son adjetivos, no criterios: falta qué consecuencia entra en cada nivel y un ejemplo).

</details>

#### P4 · 4B · 4.2 · Claude Code for Continuous Integration
The prompt already contains a detailed paragraph specifying that every finding must include the file and line, a description of the issue, a severity, and a suggested fix. Even so, in last week's 150 comments, 38 had no file reference, many merged the fix into the description, and some ran to several paragraphs. Developers say these comments are hard to act on. What's the most effective way to address this?

A) Rewrite the format paragraph with stricter wording, stating in capital letters that each finding MUST contain all four fields in the specified order.

B) Add two or three complete example findings in `<example>` tags, each showing location, issue, severity, and suggested fix for a different kind of problem.

C) Set the temperature to 0 for the review job so that each finding is generated in the same format every time the pipeline runs.

D) Add a dozen example findings covering every category the reviewer can produce, so that each kind of comment has its own template to copy.

<details>
<summary>Ver respuesta</summary>

**Respuesta correcta: B**

**Why (es):** La guía dice que few-shot es la técnica más efectiva para lograr una salida consistente y accionable **cuando las instrucciones detalladas ya no alcanzan** — y el enunciado dice que ya están. Un ejemplo se imita; una descripción hay que interpretarla. El ejemplo de la guía es justo el formato location, issue, severity, suggested fix. Pocos ejemplos (2 a 4), variados en el tipo de problema.

**Distractors (es):**
- A: tienta porque parece que falta firmeza; está mal porque más instrucciones no arreglan lo que las instrucciones ya no lograron, y el tono agresivo en mayúsculas hace que los modelos actuales se pasen de rosca.
- C: tienta porque "menos azar = más consistencia"; está mal porque en los modelos actuales los parámetros de sampling dan error 400, y nunca garantizaron un formato igual.
- D: tienta porque más cobertura parece mejor; está mal porque la guía habla de pocos ejemplos dirigidos, no "uno por caso": gasta tokens y enseña plantillas en vez del formato.

**Review:** Capítulo 13 (4B), Tema 1 — Few-shot prompting y Tema 2 — Diseño de ejemplos; Trampa 1 · Más instrucciones.

**Pista de lectura (es):** "The prompt already contains a detailed paragraph specifying…" → "el prompt ya tiene un párrafo detallado que especifica…" ("already" + instrucciones detalladas que no alcanzan → ejemplos, no más instrucciones).

</details>

#### P5 · 4B · 4.2 · Claude Code for Continuous Integration
At TiendaX, failures in non-critical side effects, such as confirmation emails or analytics events, are logged and swallowed because the order is already saved. The reviewer's criteria were updated to "report swallowed errors only when the failure leaves money or order data in an inconsistent state," yet 40% of its `catch`-related comments still target email and analytics code. Which approach best reduces these false positives without making the reviewer miss swallowed errors in payment flows?

A) Add examples of severe swallowed errors in payment code, so that the reviewer has a clear picture of what a genuine problem looks like.

B) Remove swallowed errors from the reviewer's categories entirely, and rely on integration tests in CI to detect inconsistent order or payment states.

C) Add contrasting examples: a swallowed email failure marked as acceptable and a similar swallowed `chargeCard` failure marked critical, each with its reasoning.

D) Have the reviewer self-report confidence for each `catch` finding, and suppress those below 0.8 so that only the clearest problems are posted.

<details>
<summary>Ver respuesta</summary>

**Respuesta correcta: C**

**Why (es):** El criterio explícito (4.1) ya está y no alcanzó: el problema es la **frontera** entre un patrón aceptado y un bug real. La guía pide ejemplos que **distingan el código aceptable de los problemas genuinos**: pares contrastantes que se parecen (los dos tragan el error) pero tienen distinto veredicto, con el porqué. Así Claude aprende la regla de fondo y la generaliza, sin dejar de reportar los de pagos.

**Distractors (es):**
- A: tienta porque deja claro qué es un bug de verdad; está mal porque los obvios ya los encontraba: no muestra la frontera, así que el ruido en email y analytics sigue.
- B: tienta porque elimina de golpe los falsos positivos; está mal porque rompe la condición "without making the reviewer miss swallowed errors in payment flows".
- D: tienta porque suena medible; está mal porque filtrar por confianza autoasignada no es un criterio, y puede suprimir justo los errores de pago (también incumple el alcance).

**Review:** Capítulo 13 (4B), Tema 4 — Ejemplos para bajar los falsos positivos; Trampa 4 · Ejemplos solo de errores obvios.

**Pista de lectura (es):** "without making the reviewer miss swallowed errors in payment flows" → "sin que el revisor deje de detectar los errores tragados en los flujos de pago" (descarta las opciones que bajan el ruido apagando o filtrando).

</details>

#### P6 · 4B · 4.2 · Claude Code for Continuous Integration
The reviewer is supposed to comment on untested code branches, and its prompt says "report untested branches that affect behavior." In practice, it flags untested `else` branches that only build log messages, but it stayed silent on an untested branch in `pagos/shipping.ts` that applies the international surcharge, reasoning that the file already has 92% line coverage. Your teammates disagree on how to fix this, and you need the reviewer to handle new cases it hasn't seen. What's the most effective way to address this?

A) Add two to four examples of borderline branches, each showing whether it was reported and why, compared with the alternative that also seemed reasonable.

B) Add a rule to report untested branches only in files below 80% line coverage, using the coverage report that CI already generates as input.

C) Add a dozen input-output pairs that map branch snippets to "report" or "skip," leaving out the explanations to keep the prompt short.

D) Have a second reviewer instance check every coverage finding, and post only the untested branches that both instances agree should be reported.

<details>
<summary>Ver respuesta</summary>

**Respuesta correcta: A**

**Why (es):** Los huecos de cobertura por rama son uno de los casos ambiguos que nombra la guía para 4.2. La instrucción ya existe; falla en la frontera. La Skill es crear **2 a 4 ejemplos dirigidos a los casos ambiguos que muestren por qué se eligió una acción frente a la alternativa plausible** (reportar la rama del recargo aunque el archivo tenga 92%; saltear la que arma un log). Con el razonamiento, Claude generaliza a casos nuevos.

**Distractors (es):**
- B: tienta porque es una regla determinística con datos reales; está mal porque repite el error del enunciado: con 92% el archivo quedaría afuera y la rama que cobra plata seguiría sin comentario.
- C: tienta porque más ejemplos parece más cobertura; está mal porque sin el porqué no aprende el criterio (solo reconoce casos vistos) y la guía pide pocos ejemplos dirigidos.
- D: tienta porque la instancia independiente es buena práctica (4.6); está mal porque exigir acuerdo suprime hallazgos reales y no le enseña a ninguna de las dos instancias el criterio.

**Review:** Capítulo 13 (4B), Tema 3 — Ejemplos para los casos ambiguos, con el razonamiento; Trampa 2 · Muchos ejemplos, todos fáciles.

**Pista de lectura (es):** "reasoning that the file already has 92% line coverage … you need the reviewer to handle new cases it hasn't seen" → "razonando que el archivo ya tiene 92% de cobertura … necesitás que el revisor resuelva casos nuevos que no vio" (frontera ambigua + generalizar → ejemplos con razonamiento).

</details>

#### P7 · 4C · 4.6 · Claude Code for Continuous Integration
A separate CI job uses Claude Code to generate patches for failing tests. After writing each patch, the same session is asked, "Review your changes carefully and confirm they are correct," and it confirms 97% of them. In October, three confirmed patches were merged that converted `priceCents` values to floating-point numbers. Your teammate proposes enabling extended thinking in that session so that its self-review step goes deeper. How should you evaluate this proposal?

A) Accept it, since a larger reasoning budget during the review step lets the session reconsider its own decisions before it confirms each patch.

B) Accept it, and also move the session to a larger model, so that the same session has more capacity to catch subtle unit-conversion errors.

C) Reject it, and pass the full generation transcript to a second instance, so that it understands why each change was made before it judges the patch.

D) Reject it, and send each patch to a separate instance that receives only the diff and the review criteria, without the generator's reasoning context.

<details>
<summary>Ver respuesta</summary>

**Respuesta correcta: D**

**Why (es):** La sesión que generó el parche retiene su razonamiento y es poco probable que cuestione sus propias decisiones (por eso confirma el 97%). La guía dice que una **instancia independiente, sin el contexto de razonamiento previo**, detecta mejor los problemas sutiles que las instrucciones de autorrevisión **o el extended thinking**. La propuesta del compañero está mal.

**Distractors (es):**
- A: tienta porque más razonamiento suena a revisión más profunda; está mal porque la guía pone explícitamente al extended thinking por debajo de la instancia independiente: sigue siendo la misma sesión con el mismo sesgo.
- B: tienta porque "modelo más grande" parece más capacidad; está mal porque el problema es el contexto compartido, no la capacidad; lo que importa es que el revisor no haya visto la generación.
- C: tienta porque usa una segunda instancia; está mal porque le pasa el razonamiento del generador, que es justo lo que hay que dejar afuera para que no herede el sesgo.

**Review:** Capítulo 14 (4C), Tema 10 — Por qué la auto-revisión falla: la instancia independiente; Trampa 15.

**Pista de lectura (es):** "the same session is asked … and it confirms 97% of them" → "a la misma sesión se le pide … y confirma el 97%" (misma sesión = mismo razonamiento; "proposes" → evaluá la propuesta, suele estar mal).

</details>

#### P8 · 4C · 4.6 · Claude Code for Continuous Integration
A PR modifies 22 files across `checkout` and `pagos` to make `getCartTotal` return cents instead of pesos. The single-pass review left detailed comments on the first files and one-line remarks on the last ones, flagged a `Math.round` call in `cart.ts` while approving the identical call in `coupon.ts`, and missed that `refund.ts` still multiplies the returned value by 100. Which TWO changes should you make? (Choose two.)

A) Switch to a model with a larger context window, so that all 22 files fit in a single review pass with plenty of room to spare.

B) Review each file in its own focused pass that looks for local issues, so that every file receives the same depth of analysis.

C) Run the single-pass review three times on the full PR, and post only the findings that appear in at least two of the three runs.

D) Add an instruction to the single-pass prompt to give every file equal attention, and list the changed files in order of business risk.

E) Add a separate integration pass that traces data flowing between files, such as every caller that consumes the value of `getCartTotal`.

<details>
<summary>Ver respuesta</summary>

**Respuesta correcta: B+E**

**Why (es):** Los tres síntomas (profundidad despareja, hallazgos contradictorios entre archivos, un bug entre archivos que nadie vio) son de **dilución de la atención** en una sola pasada. La guía (4.6) pide partir la revisión en **pasadas por archivo** para los problemas locales (B) **y una pasada de integración** para el flujo de datos entre archivos (E): sin E, nadie ve que `refund.ts` sigue tratando el valor como pesos.

**Distractors (es):**
- A: tienta porque "entran todos los archivos"; está mal porque el problema es cómo se reparte la atención, no el espacio.
- C: tienta porque el consenso parece más confiable; está mal porque suprime bugs reales que solo encontró una corrida y sigue revisando todo junto.
- D: tienta porque ataca el síntoma con una instrucción; está mal porque pedir "atención pareja" no cambia la arquitectura: la dilución sigue y no hay quien mire el flujo entre archivos.

**Review:** Capítulo 14 (4C), Tema 11 — Revisión en varias pasadas: por archivo y de integración; Trampa 16 · El PR de 14 archivos (Q12).

**Pista de lectura (es):** "missed that `refund.ts` still multiplies the returned value by 100" → "no detectó que `refund.ts` todavía multiplica por 100 el valor devuelto" (un bug **entre** archivos: por eso hace falta la pasada de integración además de las pasadas por archivo).

</details>

#### P9 · 4C · 4.6 · Claude Code for Continuous Integration
After moving to per-file and integration passes, the reviewer catches more real bugs, but some of its findings are uncertain. The team wants uncertain findings checked by the staff engineer on call before they reach the author, without adding that human wait to PRs whose findings are all reliable. A teammate notes that, in a pilot, findings the model rated above 0.9 were wrong 18% of the time. What's the correct approach to routing these findings?

A) Add a verification pass that reports confidence with each finding, and set routing thresholds calibrated against a labeled set of past PRs with known outcomes.

B) Add a verification pass that reports confidence with each finding, and auto-post every finding above 0.9 while sending the rest to the on-call engineer.

C) Send every finding to the on-call engineer before posting, so that no uncertain result reaches the author regardless of the model's confidence.

D) Instruct the finding passes to report only issues they are highly confident about, so that uncertain findings never appear and need no routing.

<details>
<summary>Ver respuesta</summary>

**Respuesta correcta: A**

**Why (es):** La guía (4.6, Skill 3) pide **pasadas de verificación donde el modelo reporta su confianza por hallazgo para enrutar la revisión**, y 5.5 aclara que los umbrales se **calibran con un set etiquetado** (casos con respuesta conocida). El piloto muestra que la confianza cruda está mal calibrada (0,9 y 18% de errores), así que el umbral fijo no sirve; calibrado, permite publicar directo lo confiable y mandar a la persona solo lo dudoso.

**Distractors (es):**
- B: tienta porque usa la misma pasada de verificación que la correcta; está mal porque usa la confianza cruda con un umbral fijo, y el enunciado ya muestra que 0,9 no significa 90% de acierto.
- C: tienta porque es lo más seguro; está mal porque rompe la condición "without adding that human wait to PRs whose findings are all reliable".
- D: tienta porque elimina el problema del enrutamiento; está mal porque es la trampa de 4.1: "only high-confidence" baja el recall y esconde bugs reales.

**Review:** Capítulo 14 (4C), Tema 11 — confianza por hallazgo para enrutar, con umbrales calibrados; Capítulo 12 (4A), Tema 4 (por qué "high-confidence" no es criterio).

**Pista de lectura (es):** "findings the model rated above 0.9 were wrong 18% of the time" → "los hallazgos que el modelo calificó por encima de 0,9 estaban mal el 18% de las veces" (la confianza autoasignada no está calibrada: hay que calibrar los umbrales con casos conocidos).

</details>

### Escenario: Structured Data Extraction

You are building TiendaX's extraction pipeline for supplier invoices, delivery notes, and credit notes that arrive by email as PDFs and plain text. Claude extracts each document through tool use with JSON schemas, and the results feed the accounts payable system, which posts payments automatically. The team targets 95% straight-through processing.

#### P10 · 4C · 4.3 · Structured Data Extraction
The shared mailbox receives invoices, delivery notes, and credit notes mixed together, with nothing indicating which is which. You defined `extract_invoice`, `extract_delivery_note`, and `extract_credit_note`, and call the API with `tool_choice: {"type": "auto"}`. Production logs show that in 6% of requests Claude replies with a prose summary such as "This appears to be a credit note for $12,400" and no `tool_use` block, so nothing reaches accounts payable. What's the most effective way to address this?

A) Add a system prompt instruction stating that every response must call one of the three extraction tools and must never contain plain prose.

B) Force `extract_invoice` through `tool_choice`, and add optional delivery-note and credit-note fields to its schema so it captures every document type.

C) Set `tool_choice` to `{"type": "any"}`, so Claude must call one of the extraction tools while still choosing the one that matches the document.

D) Add a classification request that labels each document's type first, then force the matching extraction tool in a second request for that document.

<details>
<summary>Ver respuesta</summary>

**Respuesta correcta: C**

**Why (es):** Con `auto` Claude **puede** responder con texto; eso es exactamente el 6%. Hay varios schemas y no se sabe qué tipo de documento llegó: es el caso de manual de `tool_choice: any`. Obliga a llamar alguna tool (siempre hay datos estructurados) y deja que Claude elija cuál corresponde. Es la Skill de 4.3 al pie de la letra.

**Distractors (es):**
- A: tienta porque ataca el síntoma directo; está mal porque una instrucción es probabilística: con `auto` el texto sigue siendo una salida permitida.
- B: tienta porque forzar una tool garantiza la llamada; está mal porque fuerza la tool de facturas para remitos y notas de crédito, y mezclar tres schemas en uno lo llena de campos opcionales ambiguos.
- D: tienta porque "funciona" (es la opción defendible); está mal porque agrega un componente y un request extra para algo que `any` resuelve en una sola llamada (sobredimensionado).

**Review:** Capítulo 14 (4C), Tema 2 — tool_choice en una extracción; Trampa 2 · auto, any o forced.

**Pista de lectura (es):** "with nothing indicating which is which" → "sin nada que indique cuál es cuál" (tipo de documento desconocido + varios schemas = `any`); "and no `tool_use` block" → "y sin bloque `tool_use`" (`auto` permite texto).

</details>

#### P11 · 4C · 4.3 · Structured Data Extraction
Two problems appear in invoice extractions. Small suppliers rarely print a purchase order number, yet the required `purchase_order` field arrives filled with plausible values like "OC-0001" that do not exist in procurement. Meanwhile, the `expense_category` enum (`merchandise`, `freight`, `services`, `taxes`) forces warehouse-rent and software-license invoices into `services`, and invoices whose lines mix freight and merchandise are labeled inconsistently. You need to fix both problems while keeping `expense_category` a closed list that accounts payable can validate. Which TWO changes should you make? (Choose two.)

A) Add a system prompt rule telling Claude never to invent purchase order numbers and to copy them only when they literally appear on the document.

B) Make `purchase_order` nullable, and state in its description that it must be null whenever the document does not show a purchase order number.

C) Replace the `expense_category` enum with a free-text string, so Claude can record any category exactly as the supplier describes it on the invoice.

D) Validate each purchase order number against the procurement system, and retry the extraction with that error whenever the number does not exist.

E) Add `other` with a companion `expense_category_detail` string for valid unlisted categories, and `unclear` for invoices whose category cannot be determined.

<details>
<summary>Ver respuesta</summary>

**Respuesta correcta: B+E**

**Why (es):** Son dos problemas de diseño del schema, uno para cada mitad. B: un campo obligatorio que el documento puede no tener **empuja a inventar**; la respuesta de la guía es hacerlo opcional/nullable y explicar cuándo va `null`. E: el enum cerrado sin salida mete rubros nuevos en el más parecido; `other` + string de detalle deja ver los rubros que faltan (alquiler, software), y `unclear` cubre las facturas ambiguas (flete + mercadería). La lista sigue cerrada, como pide el alcance.

**Distractors (es):**
- A: tienta porque ataca el síntoma; está mal porque el campo sigue siendo obligatorio y la presión para completarlo sigue ahí (probabilístico).
- C: tienta porque acepta cualquier rubro; está mal porque rompe la condición "keeping a closed list": accounts payable ya no puede validar y aparecen variantes de lo mismo.
- D: tienta porque detecta los números falsos y usa el patrón de retry correcto; está mal porque el dato no está en el documento: reintentar no lo hace aparecer (y puede inventar otro).

**Review:** Capítulo 14 (4C), Tema 3 — Schema design; Trampa 4 · El campo obligatorio que no existe; Trampa 5 · El enum sin salida.

**Pista de lectura (es):** "while keeping `expense_category` a closed list that accounts payable can validate" → "manteniendo `expense_category` como una lista cerrada que cuentas a pagar pueda validar" (descarta el string libre); "the required `purchase_order` field" → "el campo obligatorio `purchase_order`" (la causa del invento es que sea obligatorio).

</details>

#### P12 · 4C · 4.3 · Structured Data Extraction
After moving extraction to tool use with `strict: true`, JSON parse failures in the accounts payable import dropped to zero. However, a reconciliation audit finds that 3% of invoices have line items that do not add up to the extracted total, and in several credit notes the issue date was placed in `due_date`. A teammate proposes adding `additionalProperties: false` and making every field required to tighten the schema. How should you evaluate this proposal?

A) Reject it, since these are semantic errors the schema cannot see; add validation in code for line sums and date order, and retry failures with the specific error.

B) Accept it, since a stricter schema with no extra properties and more required fields leaves Claude less room to put values in the wrong fields.

C) Reject it, and instead add few-shot examples of correctly formatted JSON outputs so Claude learns the exact structure the import expects.

D) Accept it, but also switch from strict tool use to structured outputs, since `output_config.format` constrains the whole response rather than only tool arguments.

<details>
<summary>Ver respuesta</summary>

**Respuesta correcta: A**

**Why (es):** El schema ya garantiza la **forma** (por eso los errores de parseo bajaron a cero). Las líneas que no suman y la fecha en el campo equivocado son errores **semánticos**: el JSON es válido pero lo que dice está mal, y el schema no puede verlo. Se detectan con reglas de negocio en código y se corrigen con retry con el error específico.

**Distractors (es):**
- B: tienta porque "endurecer el schema" suena a más control; está mal porque `additionalProperties` y `required` controlan qué campos hay, no si los valores son correctos. Además, más obligatorios empujan a inventar.
- C: tienta porque few-shot da consistencia de formato; está mal porque el formato ya está garantizado: el problema son los valores.
- D: tienta porque structured outputs es real y también garantiza la forma; está mal porque tampoco mira los valores: es un cambio de mecanismo para un problema que no es de forma.

**Review:** Capítulo 14 (4C), Tema 4 — Syntax vs. semantic errors; Trampa 6 · "Ya usamos strict, no hace falta validar".

**Pista de lectura (es):** "JSON parse failures … dropped to zero. However, … line items that do not add up" → "los errores de parseo bajaron a cero. Sin embargo, … líneas que no suman" (la forma ya está bien; lo que falla es el contenido); "proposes" → propuesta, evaluala con sospecha.

</details>

#### P13 · 4C · 4.4 · Structured Data Extraction
Your validation layer checks that `due_date` is later than `issue_date` and that line items sum to `stated_total_cents`. When a check fails, the pipeline resends the original document followed by the message "Your previous extraction failed validation. Please extract the invoice again carefully." Logs show that 70% of these retries return exactly the same values as the first attempt. What change would most effectively improve the retry success rate?

A) Raise the temperature slightly on each retry, so the model explores a different reading of the document instead of repeating its earlier answer.

B) Increase the retry limit from two to five attempts, and escalate the invoice to a person only after every one of those attempts has failed.

C) Send only the failed fields and the validation error, omitting the document, so the retry request stays small and focused on what broke.

D) Include the previous extraction and the specific failed rule with its values next to the document, and ask Claude to correct only the affected fields.

<details>
<summary>Ver respuesta</summary>

**Respuesta correcta: D**

**Why (es):** Un retry útil lleva tres cosas: el **documento original**, la **extracción fallida** y el **error de validación específico** ("due_date 2026-11-01 es anterior a issue_date 2026-11-15"). El pipeline ya manda el documento, pero "intentá de nuevo con cuidado" no le da a Claude ninguna información nueva: por eso repite lo mismo el 70% de las veces. Pedir que corrija solo los campos afectados evita que cambie lo que estaba bien.

**Distractors (es):**
- A: tienta porque el companion del curso sugiere "a small temperature bump"; está mal porque no aporta información nueva, y la guía (y los modelos actuales) no usan la temperatura como palanca.
- B: tienta porque escalar al final es buena práctica; está mal porque más intentos sin información nueva dan más veces el mismo resultado (el parche que no ataca la causa).
- C: tienta porque ahorra tokens y nombra el error; está mal porque sin el documento Claude no puede volver a mirar la fuente para corregir.

**Review:** Capítulo 14 (4C), Tema 5 — Retry with error feedback; Trampa 7 · "Intentá de nuevo".

**Pista de lectura (es):** "resends the original document followed by the message 'Your previous extraction failed validation…'" → "reenvía el documento original seguido de 'tu extracción anterior falló la validación…'" (el documento ya está; faltan la extracción anterior y el error concreto).

</details>

#### P14 · 4C · 4.4 · Structured Data Extraction
Validation flags about 120 freight invoices per week with a null `purchase_order`. Each one says "PO as per attached delivery note," but those suppliers email the delivery note separately, and it arrives in a different message hours later. The pipeline currently retries every flagged invoice up to three times with the document, the previous extraction, and the error. You need to stop wasting these retries without letting the invoices post to accounts payable with fabricated purchase orders. Which approach should you take?

A) Keep the three retries, but add a few-shot example showing how to infer the purchase order from that supplier's previous invoices in the system.

B) Skip retries for this case, keep `purchase_order` null, mark the invoice as pending the referenced delivery note, and re-extract once that document is linked.

C) Make `purchase_order` required again, so the schema forces Claude to find the number in the invoice before the extraction is accepted downstream.

D) Raise the retry limit to five, and add to the error message that the purchase order appears in the delivery note mentioned in the invoice text.

<details>
<summary>Ver respuesta</summary>

**Respuesta correcta: B**

**Why (es):** El retry sirve cuando el dato **está** en el documento y Claude lo leyó mal. Acá el dato vive en **otro documento que no se le pasó** (el remito llega aparte): es el ejemplo exacto de la guía de cuándo reintentar no sirve. Lo correcto es dejar `null`, marcar como faltante y volver a extraer cuando llegue el remito. Así se dejan de gastar reintentos y, a la vez, no se postea nada inventado.

**Distractors (es):**
- A: tienta porque few-shot y el historial del proveedor suenan inteligentes; está mal porque "inferir" la OC de facturas viejas es fabricar un dato: rompe la segunda mitad de la condición.
- C: tienta porque "forzar" parece obligar a encontrarlo; está mal porque un campo obligatorio sin dato en la fuente empuja a inventar (Trampa 4).
- D: tienta porque es el patrón de retry correcto con más contexto; está mal porque el remito no está en el request: ningún reintento lo hace aparecer, y gasta más reintentos (contradice "stop wasting").

**Review:** Capítulo 14 (4C), Tema 6 — When retries are ineffective; Trampa 8 · Reintentar lo que no está.

**Pista de lectura (es):** "it arrives in a different message hours later" → "llega en otro mensaje horas después" (el dato no está en lo que Claude recibe); "without letting the invoices post … with fabricated purchase orders" → "sin dejar que las facturas se registren con órdenes de compra inventadas" (descarta inferir o forzar).

</details>

#### P15 · 4C · 4.4 · Structured Data Extraction
Finance discovered that some suppliers send invoices whose printed total does not match the sum of their line items, usually by a few hundred pesos. Today Claude extracts a single `total_cents`, and spot checks show it sometimes copies the printed total and sometimes silently uses the line-item sum. Finance wants every such invoice routed to the disputes team, while preserving exactly what the supplier printed. What's the most effective way to achieve this?

A) Extract both `stated_total_cents` and `calculated_total_cents` plus a `conflict_detected` boolean, and route invoices to disputes whenever the two totals differ.

B) Instruct Claude to always use the line-item sum as `total_cents`, since it reflects the goods actually invoiced rather than the supplier's arithmetic.

C) Add a `confidence` score for `total_cents` to the schema, and route invoices to disputes whenever Claude reports a confidence below 0.8.

D) Instruct Claude to always copy the printed total, and have the disputes team review a random 5% sample of invoices each week for mismatches.

<details>
<summary>Ver respuesta</summary>

**Respuesta correcta: A**

**Why (es):** Es el flujo de autocorrección de la guía: extraer **las dos cosas** (lo que dice el documento y lo que resulta de sumar las líneas) y marcar el conflicto con un booleano, en lugar de "arreglar" uno en silencio. Cumple las dos condiciones: cada discrepancia queda visible y se enruta, y el total impreso se conserva tal cual.

**Distractors (es):**
- B: tienta porque deja un total "correcto"; está mal porque corrige en silencio: se pierde lo que imprimió el proveedor y nadie se entera del error (rompe "preserving exactly what the supplier printed").
- C: tienta porque enrutar por confianza aparece en 4.6; está mal porque es autoevaluación del modelo, y Claude puede estar muy seguro de un total que no coincide con las líneas. No compara nada.
- D: tienta porque conserva el total impreso; está mal porque un muestreo del 5% deja pasar casi todas las discrepancias y no cumple "every such invoice".

**Review:** Capítulo 14 (4C), Tema 7 — Self-correction fields; Trampa 9 · Corregir el total en silencio.

**Pista de lectura (es):** "sometimes silently uses the line-item sum" → "a veces usa en silencio la suma de las líneas" (el problema es la corrección silenciosa); "every such invoice … while preserving exactly what the supplier printed" → "cada factura así … conservando exactamente lo que imprimió el proveedor" (hay que guardar los dos valores).

</details>

#### P16 · 4C · 4.5 · Structured Data Extraction
TiendaX's accounts payable policy requires every supplier document to be extracted within 30 hours of arrival. To save 50%, you are moving extraction of the roughly 2,500 daily documents to the Message Batches API, which completed most test batches in under an hour. Documents arrive continuously between 7:00 and 23:00. Your manager proposes a single batch submission at 23:30 each night. How should you evaluate this proposal?

A) Accept it, since most batches finish within an hour, so even documents that arrive at 7:00 are extracted well before the 30-hour deadline.

B) Reject it, and keep every document on the synchronous API, since the Batches API offers no latency guarantee that could satisfy any deadline.

C) Accept it, but split the nightly submission into four smaller batches sent at 23:30, so that each batch completes faster than one large batch.

D) Reject it, and submit a batch every 4 hours, so a document waits at most 4 hours for submission plus 24 for processing, within the 30 hours.

<details>
<summary>Ver respuesta</summary>

**Respuesta correcta: D**

**Why (es):** El SLA se calcula con el **peor caso**: espera hasta el próximo envío + 24 h de techo del batch ≤ SLA. Con un envío nocturno, un documento de las 7:00 espera 16,5 h y después hasta 24 h: 40,5 h, fuera de las 30. Con envíos cada 4 h: 4 + 24 = 28 h, con margen. Es el ejemplo de la guía (ventanas de 4 h para un SLA de 30 h).

**Distractors (es):**
- A: tienta porque usa el dato del enunciado ("under an hour"); está mal porque eso es el caso típico, no una garantía: el techo es 24 h (es el distractor B de la Q11).
- B: tienta porque "no latency SLA" es una frase de la guía; está mal porque la carga no bloquea a nadie y tolera demora: con la frecuencia correcta, el batch cumple el SLA y ahorra el 50%.
- C: tienta porque lotes más chicos "suenan" más rápidos; está mal porque no cambia el techo de 24 h ni la espera de 16,5 h de los documentos de la mañana.

**Review:** Capítulo 14 (4C), Tema 9 — Operar un batch (frecuencia de envío); Trampa 14 · La frecuencia que no llega al SLA.

**Pista de lectura (es):** "Documents arrive continuously between 7:00 and 23:00" → "los documentos llegan de forma continua entre las 7:00 y las 23:00" (el de las 7:00 espera hasta las 23:30); "completed most test batches in under an hour" → "la mayoría de los lotes de prueba terminaron en menos de una hora" (dato típico, no garantía).

</details>

#### P17 · 4C · 4.5 · Structured Data Extraction
You submitted the historical backlog of 8,000 invoices as one batch, using each invoice ID as its `custom_id`. When processing ends, 7,880 results are `succeeded`, 90 are `errored` because of transient server errors, and 30 are `errored` because multi-hundred-page supplier statements exceeded the context window. What's the most effective way to complete the backlog while minimizing cost?

A) Resubmit the full 8,000-invoice batch, since partial failures may mean the run was inconsistent and every result should come from the same batch.

B) Resubmit the 120 failed requests unchanged in a new batch, and match the new results to invoices by their position in the results file.

C) Resubmit only the 120 failed invoices by `custom_id`, sending the 90 unchanged and splitting the 30 oversized statements into chunks first.

D) Move the 120 failed invoices to the synchronous API with a higher `max_tokens` value, so they are processed immediately and complete in one pass.

<details>
<summary>Ver respuesta</summary>

**Respuesta correcta: C**

**Why (es):** Se reenvían **solo los fallidos**, identificados por `custom_id`, y **con las modificaciones necesarias**: los errores de servidor se reenvían tal cual; los que excedieron el contexto van a volver a fallar si no se parten en pedazos (chunking). Seguir en batch mantiene el 50% de ahorro, que es la condición de costo.

**Distractors (es):**
- A: tienta porque "todo en la misma corrida" parece más prolijo; está mal porque pagás de nuevo las 7.880 que ya salieron bien.
- B: tienta porque reenvía solo lo fallido; está mal por dos cosas: los 30 largos van a fallar igual sin chunking, y los resultados no vuelven en orden (se correlaciona por `custom_id`, nunca por posición).
- D: tienta porque "inmediato" y "más tokens" suenan a solución; está mal porque `max_tokens` limita la salida, no la entrada que excedió el contexto, y la API síncrona cuesta el doble.

**Review:** Capítulo 14 (4C), Tema 8 (`custom_id`) y Tema 9 — Operar un batch (fallas); Trampa 13 · Reenviar el lote entero.

**Pista de lectura (es):** "30 are `errored` because … exceeded the context window" → "30 dieron error porque … excedieron la ventana de contexto" (esos necesitan modificación: chunking); "while minimizing cost" → "minimizando el costo" (solo los fallidos, y en batch).

</details>

#### P18 · 4B · 4.2 · Structured Data Extraction
Your extraction prompt includes three examples, all PDF invoices from large suppliers with a "Vencimiento" row in the totals table. For small suppliers who email plain text, `due_date` comes back null in 35% of cases even when the message says things like "pay by the end of the month," and for messages with no payment terms Claude sometimes fills in a date 30 days after issue. The field is already nullable with a clear description. What's the most effective way to address both problems?

A) Replace the examples with varied ones: a table invoice, a narrative email whose due date sits in a sentence, and an email with no terms showing `due_date` as null.

B) Add an instruction stating that `due_date` must never be left empty, and that Claude should apply a 30-day default when the document states no date.

C) Make `due_date` required and non-nullable, so Claude is forced to locate the date in narrative emails instead of returning null for them.

D) Add three more PDF invoice examples with the due-date row in different positions of the totals table, so Claude learns to search more carefully.

<details>
<summary>Ver respuesta</summary>

**Respuesta correcta: A**

**Why (es):** Las dos fallas vienen de los ejemplos: todos son del mismo tipo (PDF con tabla), así que Claude no aprende a encontrar el vencimiento en una frase, y nunca vio un caso donde la respuesta correcta es `null`. La guía pide ejemplos con **estructuras de documento variadas** (contra los campos vacíos que sí tienen dato) e **incluir el caso del dato ausente con `null`** (contra la alucinación). El schema ya está bien: el enunciado lo dice.

**Distractors (es):**
- B: tienta porque "nunca vacío" parece arreglar el primer problema; está mal porque empuja a inventar, y el default de 30 días convierte la alucinación en regla.
- C: tienta porque obliga a buscar el dato; está mal porque un campo obligatorio sin dato en la fuente fuerza a inventar: empeora el segundo problema.
- D: tienta porque agrega variedad y más ejemplos; está mal porque siguen siendo todos PDFs con tabla: no muestran el email narrativo ni el caso `null`.

**Review:** Capítulo 13 (4B), Tema 5 — Extraction examples; Trampa 5 de 4B (estructuras variadas con null honesto). Capítulo 14 (4C), Tema 3 (nullable).

**Pista de lectura (es):** "all PDF invoices from large suppliers" → "todas facturas PDF de proveedores grandes" (ejemplos de un solo tipo = la causa); "The field is already nullable" → "el campo ya es nullable" (descarta tocar el schema; la respuesta está en los ejemplos).

</details>
