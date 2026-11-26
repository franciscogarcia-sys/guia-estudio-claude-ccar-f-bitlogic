# Preguntas — Módulo 3 (Claude Code Configuration & Workflows · 3A–3D)

## Preguntas de fin de módulo

### Escenario: Code Generation with Claude Code

You are building TiendaX's Claude Code setup for a TypeScript monorepo with `packages/checkout`, `packages/pagos`, and `packages/catalogo`. Fourteen developers use Claude Code daily to generate features, refactor, and write tests. The team wants conventions applied consistently on every machine, with each package receiving only the standards that apply to it.

#### P1 · 3B · 3.1 · Code Generation with Claude Code
Martina joined the checkout squad last week. In her sessions, Claude writes Jest tests and stores prices as floating-point numbers, while the tech lead's sessions consistently produce Vitest tests and integer cents. Running `/memory`, Martina sees `./CLAUDE.md` and `packages/checkout/CLAUDE.md`; the tech lead sees those two files plus `~/.claude/CLAUDE.md`, and neither project file mentions Vitest or cents. What is the most likely root cause?

A) `packages/checkout/CLAUDE.md` overrides the root file whenever Claude works in that package, so the shared testing and money rules are discarded.

B) Martina launched Claude Code from `packages/checkout`, so the root `CLAUDE.md` above her working directory never entered the session's context.

C) The testing and money conventions live in the tech lead's user-level configuration, which is never shared with teammates through version control.

D) The root `CLAUDE.md` has grown too long, so Claude skips its testing and money sections when it generates code for the checkout package.

<details>
<summary>Ver respuesta</summary>

**Respuesta correcta: C**

**Why (es):** `/memory` muestra la diferencia: el tech lead tiene un archivo más, su `~/.claude/CLAUDE.md` (user-level), y los archivos del proyecto no mencionan Vitest ni centavos. Las convenciones viven en el nivel de usuario, que no viaja por git. Es la Skill 1 de la guía para 3.1: el compañero nuevo no recibe las instrucciones porque están en user-level y no en project-level. La solución es pasarlas al `CLAUDE.md` del proyecto.

**Distractors (es):**
- A: tienta porque el companion del curso habla de "precedencia" y el archivo de la carpeta es más específico; está mal porque los CLAUDE.md se concatenan, no se pisan, y además ninguno de los dos archivos del proyecto tiene esas reglas.
- B: tienta porque los CLAUDE.md de subcarpetas sí cargan bajo demanda; está mal porque Claude Code sube por el árbol desde el cwd y carga los de arriba al arrancar, y `/memory` muestra `./CLAUDE.md` en la sesión de Martina.
- D: tienta porque un CLAUDE.md largo baja la adherencia (doc: <200 líneas); está mal porque el enunciado dice que los archivos del proyecto ni mencionan esas reglas: no hay sección que saltear.

**Review:** Capítulo 8 (3A), Tema 5 — Los niveles de CLAUDE.md y Tema 8 — `/memory`; Capítulo 9 (3B), Tema 3 — Conflictos y Tema 4 — Diagnosticar con `/memory`.

**Pista de lectura (es):** "the tech lead sees those two files plus `~/.claude/CLAUDE.md`, and neither project file mentions Vitest or cents" → "el tech lead ve esos dos archivos más `~/.claude/CLAUDE.md`, y ninguno de los archivos del proyecto menciona Vitest ni centavos" (la regla está solo en el nivel de usuario del tech lead).

</details>

#### P2 · 3B · 3.1 · Code Generation with Claude Code
The root `CLAUDE.md` says "Use named exports for all modules." Two years ago the catalog team added `packages/catalogo/CLAUDE.md` with "React components use default exports," and that exception is still intended. In catalog work, Claude used named exports for components in 9 of the last 20 sessions and default exports in the rest. Your teammate proposes leaving both files unchanged, since the directory-level file is more specific and therefore takes precedence. How should you evaluate this proposal?

A) Accept it, since directory-level instructions deterministically override project-level ones, so the mixed results must come from stale context in long sessions.

B) Reject it, since CLAUDE.md files are concatenated rather than overridden, and remove the contradiction by stating the catalog exception explicitly in the root rule.

C) Accept it, but mark the catalog rule as IMPORTANT so Claude gives the more specific file greater weight whenever the two instructions collide.

D) Reject it, and add a precedence setting to `.claude/settings.json` so Claude Code resolves conflicts between CLAUDE.md levels deterministically.

<details>
<summary>Ver respuesta</summary>

**Respuesta correcta: B**

**Why (es):** No hay un nivel de CLAUDE.md que "gane": todos los archivos se concatenan en el contexto y, ante dos reglas contradictorias, "Claude may pick one arbitrarily". El 9 de 20 es justo ese síntoma. Lo que corresponde es eliminar la contradicción en los archivos: que la regla de la raíz diga explícitamente la excepción de los componentes de catálogo (o que deje de contradecirla).

**Distractors (es):**
- A: tienta porque repite lo que dice el compañero y el curso ("precedence"); está mal porque la doc no define ningún override para CLAUDE.md, y culpar al contexto viejo ignora la contradicción escrita.
- C: tienta porque parece darle más peso a la regla correcta sin tocar nada más; está mal porque la contradicción sigue escrita, y apilar énfasis hace que Claude aplique la regla de más (best practices).
- D: tienta porque settings.json sí tiene precedencia estricta; está mal porque no existe un setting de precedencia entre niveles de CLAUDE.md: es un mecanismo inventado.

**Review:** Capítulo 9 (3B), Tema 3 — Conflictos: no hay un nivel que "gane"; Trampa 1 · "El del proyecto gana".

**Pista de lectura (es):** "9 of the last 20 sessions … and default exports in the rest" → "en 9 de las últimas 20 sesiones … y default exports en el resto" (resultado mezclado = contradicción sin resolver; "proposes" → la propuesta suele estar mal).

</details>

#### P3 · 3A/3B · 3.1 · Code Generation with Claude Code
The root `CLAUDE.md` has grown to 840 lines, mixing testing, API, and deployment conventions with two standards documents: PCI-DSS card-handling rules that only `packages/pagos` needs and SEO markup rules that only `packages/catalogo` needs. Developers complain that it is hard to find and update anything, and the maintainers of each package, who know exactly which standards apply to their code, want to decide what their package receives without editing a file that every other package also depends on. Which TWO changes should you make? (Choose two.)

A) Split the testing, API, and deployment sections into focused topic files such as `testing.md`, `api-conventions.md`, and `deployment.md` in `.claude/rules/`.

B) Replace each section of the root `CLAUDE.md` with an `@` import of its own file, so that every standard loads only when Claude decides it is relevant.

C) Move the PCI-DSS and SEO standards into the `~/.claude/CLAUDE.md` of each package's maintainers, since they know which standards apply to their code.

D) Keep both standards in the root `CLAUDE.md`, and mark the PCI-DSS section as IMPORTANT so Claude prioritizes it when working in `packages/pagos`.

E) Move each standard into its own file, and have each package's `CLAUDE.md` include only the relevant ones through `@` imports chosen by its maintainers.

<details>
<summary>Ver respuesta</summary>

**Respuesta correcta: A+E**

**Why (es):** Son dos Skills de 3.1 al pie de la letra. A: partir un CLAUDE.md monolítico en archivos por tema dentro de `.claude/rules/` (el ejemplo de la guía es testing.md, api-conventions.md, deployment.md). E: usar `@import` para incluir selectivamente en el CLAUDE.md de cada paquete los estándares que le corresponden "based on maintainer domain knowledge". Así cada paquete recibe solo lo suyo y los mantenedores lo deciden sin tocar el archivo de todos.

**Distractors (es):**
- B: tienta porque `@` es la sintaxis modular que nombra la guía; está mal porque los archivos importados se cargan igual al arrancar, no "cuando Claude decide", y desde la raíz todos los paquetes seguirían recibiendo todo.
- C: tienta porque los mantenedores son los que saben; está mal porque `~/.claude/CLAUDE.md` es personal: los demás devs que toquen pagos no recibirían el estándar PCI.
- D: tienta porque la regla PCI es crítica y "IMPORTANT" suena a prioridad; está mal porque no resuelve ni el desorden ni que catálogo y checkout carguen PCI, y el énfasis hace que Claude aplique la regla de más.

**Review:** Capítulo 8 (3A), Tema 7 — Modularizar: imports con `@` y `.claude/rules/`; Capítulo 9 (3B), Tema 9 — Compartir y recortar; Trampas 4 y 6.

**Pista de lectura (es):** "the maintainers of each package, who know exactly which standards apply to their code, want to decide what their package receives" → "los mantenedores de cada paquete, que saben qué estándares aplican a su código, quieren decidir qué recibe su paquete" (eco literal de "based on maintainer domain knowledge" → `@import` por paquete).

</details>

#### P4 · 3B · 3.3 · Code Generation with Claude Code
TiendaX's API mocks follow strict conventions, and the `*.mock.ts` files sit next to the code they fake, across about 40 directories in all three packages. Today the conventions are copied into a `CLAUDE.md` in 11 of those directories; three copies have already drifted apart, and new mock folders get no conventions at all. What's the most maintainable way to ensure Claude applies the same mock conventions automatically?

A) Keep the directory-level files, and add a CI check that fails whenever any copy differs from a canonical version stored at the repository root.

B) Create a single `.claude/rules/mocks.md` with `paths: ["*.mock.ts"]` in its frontmatter, and delete the 11 directory-level copies.

C) Create a project skill whose description tells Claude to apply the mock conventions whenever it creates or edits a mock file.

D) Create a single `.claude/rules/mocks.md` with `paths: ["**/*.mock.ts"]` in its frontmatter, and delete the 11 directory-level copies.

<details>
<summary>Ver respuesta</summary>

**Respuesta correcta: D**

**Why (es):** La convención depende del tipo de archivo, no de la carpeta, y los mocks están dispersos. Una sola rule en `.claude/rules/` con `paths` y el glob `**/*.mock.ts` la aplica a todo mock "regardless of directory location", también en carpetas nuevas, y se carga solo cuando Claude trabaja con esos archivos. Es el principio de Q6 con otro tipo de archivo.

**Distractors (es):**
- A: tienta porque ataca el síntoma visible (las copias que se desincronizan); está mal porque mantiene el mecanismo atado a carpetas ("directory-bound"): las carpetas nuevas siguen sin convenciones y suma infraestructura.
- B: tienta porque es casi idéntica a la correcta; está mal porque `*.mock.ts` sin `**/` solo coincide en la raíz del proyecto, y ningún mock vive ahí.
- C: tienta porque las skills también se cargan solo cuando hace falta; está mal porque dependen de que alguien la invoque o de que Claude decida cargarla, y el enunciado pide aplicación automática.

**Review:** Capítulo 9 (3B), Tema 6 — Path-scoped rules, Tema 7 — Cómo leer los glob patterns y Tema 8 — Rules vs. CLAUDE.md de subdirectorio vs. skills; Trampas 3 y 5.

**Pista de lectura (es):** "sit next to the code they fake, across about 40 directories" → "están al lado del código que simulan, repartidos en unas 40 carpetas" (archivos dispersos por tipo → rule con `paths` y `**/`).

</details>

#### P5 · 3B · 3.3 · Code Generation with Claude Code
`/context` shows the project's instructions consuming about 18,000 tokens on every request, even in sessions that only touch React components. Last sprint a teammate moved the Terraform conventions for `infra/` and the GraphQL schema conventions, used in `*.graphql` files across every package, into separate files referenced from `CLAUDE.md` with `@` imports, but the token count did not change. What's the most effective way to reduce this cost while keeping the conventions applied where they matter?

A) Move both sets of conventions into `.claude/rules/` files without frontmatter, so each topic loads separately from the main `CLAUDE.md`.

B) Move both sets of conventions into project skills with clear descriptions, so Claude loads each one when it judges the task relevant.

C) Move both sets of conventions into `.claude/rules/` files whose `paths` are `infra/**/*` and `**/*.graphql`, respectively.

D) Nest the imported files one level deeper, so Claude Code resolves them lazily the first time a matching file is opened.

<details>
<summary>Ver respuesta</summary>

**Respuesta correcta: C**

**Why (es):** Los imports organizan pero no ahorran: "imported files still load and enter the context window at launch". Por eso el conteo no bajó. Lo que carga de forma condicional es una rule con `paths`: entra al contexto solo cuando Claude trabaja con archivos que coinciden (`infra/**/*`, como el `terraform/**/*` de la guía, y `**/*.graphql` para los dispersos), y se aplica sola, sin depender de que alguien la invoque.

**Distractors (es):**
- A: tienta porque "rules" suena a carga condicional; está mal porque una rule sin `paths` se carga al arrancar, con la misma prioridad que `.claude/CLAUDE.md`: no ahorra nada.
- B: tienta porque las skills sí ahorran tokens (solo la descripción está siempre); está mal porque son convenciones que tienen que aplicarse siempre que se toquen esos archivos, y una skill depende de que Claude decida cargarla (Q6, opción C).
- D: tienta porque menciona carga "lazy"; está mal porque los imports anidados (hasta 4 niveles) se cargan igual al arrancar: no existe carga diferida de imports.

**Review:** Capítulo 9 (3B), Tema 6 — Path-scoped rules y Tema 8 — Rules por ruta vs. CLAUDE.md de subdirectorio vs. skills vs. imports; Trampa 4 · Imports para ahorrar tokens.

**Pista de lectura (es):** "with `@` imports, but the token count did not change" → "con imports `@`, pero la cantidad de tokens no cambió" (los imports no reducen contexto → hace falta carga condicional).

</details>

### Escenario: Code Generation with Claude Code (equipo de plataforma)

You are building a shared toolkit of slash commands and skills for TiendaX's platform team, which maintains the `backoffice` repository used by nine developers. The toolkit covers code review, database migrations, and codebase analysis. It must reach every developer through the repository and fit the team's existing CLAUDE.md conventions.

#### P6 · 3C · 3.2 · Code Generation with Claude Code
Tomás wrote a `/release-notes` command in `~/.claude/commands/` last month, and the team now wants it available to everyone as soon as they pull. Tomás also wants to keep his own version, which posts a Slack-formatted summary, without affecting anyone. Where should each version live?

A) Team: `.claude/commands/release-notes.md` in the repository; Tomás: `~/.claude/skills/release-notes-slack/SKILL.md`

B) Team: `.claude/commands/release-notes.md` in the repository; Tomás: `~/.claude/commands/release-notes.md`

C) Team: `~/.claude/commands/release-notes.md` on every machine; Tomás: `CLAUDE.local.md` in the repository

D) Team: a "Commands" section in the root `CLAUDE.md`; Tomás: `~/.claude/skills/release-notes-slack/SKILL.md`

<details>
<summary>Ver respuesta</summary>

**Respuesta correcta: A**

**Why (es):** Para el equipo, el comando va en `.claude/commands/` del repo: viaja por git y lo tiene todo el que haga pull (Q4 de la guía). Para la versión personal, la guía (3.2 K4) pide una variante en `~/.claude/skills/` **con otro nombre**, para no afectar ni tapar la del equipo.

**Distractors (es):**
- B: tienta porque el equipo queda bien y Tomás no cambia nada; está mal porque con el mismo nombre su versión personal tapa la del equipo en su máquina (personal > proyecto) y deja de ver los cambios del equipo; la guía pide otro nombre.
- C: tienta porque `~/.claude/commands/` también crea un `/release-notes`; está mal porque es personal, no viaja por git, y `CLAUDE.local.md` es para instrucciones, no para definir comandos.
- D: tienta porque CLAUDE.md sí se comparte; está mal porque CLAUDE.md es para instrucciones y contexto, no para definir comandos.

**Review:** Capítulo 10 (3C), Tema 1 — Custom slash commands y Tema 5 — Tu versión personal de una skill del equipo; Trampas 1 y 4.

**Pista de lectura (es):** "available to everyone as soon as they pull … his own version … without affecting anyone" → "disponible para todos apenas hagan pull … su propia versión … sin afectar a nadie" (equipo → repo; personal → `~/.claude/skills/` con otro nombre).

</details>

#### P7 · 3C · 3.2 · Code Generation with Claude Code
The team's `/map-dependencies` skill walks the `backoffice` codebase and prints about 600 lines of module-by-module findings before its final summary. Developers usually run it in the middle of a feature, and afterwards Claude keeps referring to unrelated modules from that output and loses track of earlier decisions. Only the final summary is needed. What change would most effectively address this?

A) Add `allowed-tools: Read, Grep, Glob` to the skill's frontmatter, so its analysis is limited to read-only tools and produces less output.

B) Rewrite the skill body to print only a 20-line summary, so the module-by-module findings never appear in the conversation.

C) Ask developers to run `/compact` after each analysis, so the module-by-module findings are summarized before they continue the feature.

D) Add `context: fork` to the skill's frontmatter, so the analysis runs in an isolated subagent and only its result returns to the session.

<details>
<summary>Ver respuesta</summary>

**Respuesta correcta: D**

**Why (es):** Es el uso que da la guía para `context: fork`: aislar skills de salida verbosa (como el análisis del codebase) para que no contaminen la sesión principal. El subagente hace todo el trabajo en su propio contexto y a la conversación solo vuelve el resultado.

**Distractors (es):**
- A: tienta porque es otro campo de la misma lista de la guía; está mal porque `allowed-tools` limita qué herramientas usa la skill, no dónde queda su salida: las lecturas igual llenan la conversación.
- B: tienta porque achica lo que se imprime; está mal porque la skill sigue corriendo en la conversación principal y todas las lecturas y búsquedas que hace para el análisis quedan ahí.
- C: tienta porque `/compact` reduce contexto; está mal porque es manual y reactivo, pierde detalle de las decisiones previas, y la guía da un mecanismo específico: `context: fork`.

**Review:** Capítulo 10 (3C), Tema 3 — `context: fork`: correr una skill aparte; Trampa 2 · La skill que llena el contexto.

**Pista de lectura (es):** "prints about 600 lines of module-by-module findings … Only the final summary is needed" → "imprime unas 600 líneas de hallazgos módulo por módulo … Solo hace falta el resumen final" (salida verbosa → `context: fork`).

</details>

#### P8 · 3C · 3.2 · Code Generation with Claude Code
The `/new-migration` skill reads the current schema and writes a new SQL file under `db/migrations/`; it never needs to run anything. Its body already says "Do not execute commands." Even so, in 2 of the last 40 runs Claude decided to "verify" the migration and ran `npm run db:reset` through Bash, wiping the seed data of the shared development database. Other skills and workflows in the repository legitimately run Bash for builds and tests. What's the most effective way to prevent this without affecting those workflows?

A) Repeat the restriction in capital letters at the top and bottom of the skill body, and add an example of the skill finishing without running commands.

B) Add `allowed-tools` to the skill's frontmatter listing only the file read and write tools it needs, so its tool access is restricted while it runs.

C) Add `context: fork` to the skill's frontmatter, so any command it runs executes inside an isolated subagent instead of the main session.

D) Add a PreToolUse hook to `.claude/settings.json` that blocks every Bash command in the repository, so no session can reset the database.

<details>
<summary>Ver respuesta</summary>

**Respuesta correcta: B**

**Why (es):** La guía (3.2 S3) dice exactamente esto: configurar `allowed-tools` en el frontmatter de la skill para restringir las herramientas durante su ejecución, "limiting to file write operations to prevent destructive actions". Afecta solo a esa skill. (La doc actual dice que `allowed-tools` otorga permiso y no restringe —para eso existen `disallowed-tools` o deny rules—, pero donde guía y doc difieren, la respuesta del examen sigue la guía.)

**Distractors (es):**
- A: tienta porque refuerza la instrucción que ya existe; está mal porque sigue siendo una instrucción (probabilística), y el enunciado muestra que ya falla aunque esté escrita.
- C: tienta porque "aislar" suena a "proteger"; está mal porque `context: fork` aísla el contexto, no las herramientas: el subagente igual podría correr `db:reset` contra la misma base.
- D: tienta porque un hook es determinista; está mal porque bloquea todo Bash en todas las sesiones y rompe los builds y tests que el enunciado dice que hay que preservar.

**Review:** Capítulo 10 (3C), Tema 4 — `allowed-tools` y `argument-hint`; Trampa 3 · La skill que no debería poder borrar nada.

**Pista de lectura (es):** "it never needs to run anything … Other skills and workflows … legitimately run Bash" → "nunca necesita ejecutar nada … Otras skills y flujos … usan Bash legítimamente" (restringir las tools de esta skill, no de todo el repo).

</details>

#### P9 · 3C · 3.2 · Code Generation with Claude Code
`CLAUDE.md` contains a 110-line procedure for reviewing database migrations, which developers use about twice a month by typing "review migration" followed by an ID. Reviews often start on the wrong migration because the ID is missing, and since the procedure was added, adherence to the file's everyday coding standards has dropped. What's the most effective way to restructure this?

A) Move the procedure into `.claude/rules/migration-review.md` without frontmatter, and ask developers to always include the migration ID in their first message.

B) Move the procedure into a file imported from `CLAUDE.md` with `@`, and state at the top of that file that the migration ID is always required.

C) Move the procedure into a project skill in `.claude/skills/` with `argument-hint: [migration-id]`, keeping only always-applicable standards in `CLAUDE.md`.

D) Move the procedure into a skill in each developer's `~/.claude/skills/` with `argument-hint: [migration-id]`, keeping team standards in `CLAUDE.md`.

<details>
<summary>Ver respuesta</summary>

**Respuesta correcta: C**

**Why (es):** Es un flujo de uso puntual (dos veces por mes): va en una skill on-demand, y CLAUDE.md queda para los estándares universales que aplican siempre (3.2 S5). Al salir de CLAUDE.md deja de ocupar contexto en cada sesión y mejora la adherencia al resto. Como skill del proyecto, viaja por git a todo el equipo, y `argument-hint` (según la guía) le indica al dev el parámetro requerido cuando la invoca sin argumentos.

**Distractors (es):**
- A: tienta porque saca el procedimiento del CLAUDE.md; está mal porque una rule sin `paths` se carga siempre, igual que CLAUDE.md, y el ID queda librado a la memoria de cada dev.
- B: tienta porque modulariza con la sintaxis de la guía; está mal porque el archivo importado se carga al arrancar: el costo de contexto y la baja de adherencia no cambian.
- D: tienta porque tiene el mecanismo correcto (skill + `argument-hint`); está mal porque `~/.claude/skills/` es personal: cada dev tendría que crearla a mano y las copias divergen.

**Review:** Capítulo 10 (3C), Tema 4 — `allowed-tools` y `argument-hint` y Tema 6 — ¿CLAUDE.md, rules, comando, skill o subagente?; Trampa 6 · El procedimiento de release en CLAUDE.md.

**Pista de lectura (es):** "use about twice a month … adherence to the file's everyday coding standards has dropped" → "lo usan unas dos veces por mes … bajó la adherencia a los estándares de todos los días" (uso puntual → skill on-demand; siempre → CLAUDE.md).

</details>

### Escenario: Developer Productivity with Claude

You are building a developer productivity workflow for TiendaX's engineering team using Claude Code. Developers use it daily on a 1,600-file TypeScript monorepo that holds the storefront, checkout, and shipping services. The team shares its configuration through the repository, including CLAUDE.md, custom commands, and subagents under `.claude/`.

#### P10 · 3C · 3.4 · Developer Productivity with Claude
Your team must replace the in-house `httpClient` wrapper with the platform's new `fetchWithRetry` across the storefront. A first Grep finds 57 call sites in 41 files, and three of them stream file uploads, which the new API handles through a different mechanism that nobody on the team has evaluated yet. A teammate suggests starting the edits right away and stopping only if something breaks. Which approach should you take?

A) Start in direct execution on the simplest call sites, and switch to plan mode only if the upload cases cause failures during the migration.

B) Run plan mode separately for each file as it is migrated, so every edit is preceded by a plan scoped to that single file.

C) Use plan mode to map all call sites and decide how to handle uploads, then switch to direct execution to implement the approved plan.

D) Use direct execution for all 41 files in a single pass, then run the full test suite and ask Claude to fix whatever fails afterward.

<details>
<summary>Ver respuesta</summary>

**Respuesta correcta: C**

**Why (es):** La complejidad ya está en el enunciado: 41 archivos y un caso (uploads) con un enfoque todavía sin decidir. La guía premia combinar: plan mode para investigar y diseñar (ver todos los usos y decidir cómo tratar los uploads) y, con el plan aprobado, ejecución directa para implementar.

**Distractors (es):**
- A: tienta porque es lo que propone el compañero y "arrancar por lo fácil" suena eficiente; está mal porque la complejidad ya se conoce: si ya está en el enunciado, plan mode desde el principio, no "pasar a plan si aparece" (lección de la oficial Q5).
- B: tienta porque usa plan mode y parece prolijo; está mal porque planificar archivo por archivo pierde la vista de conjunto (la decisión de los uploads afecta a todo el diseño) y suma un paso de más en cada cambio simple.
- D: tienta porque los tests "atrapan" los errores; está mal porque es el retrabajo costoso que plan mode evita: descubrir el problema de los uploads después de tocar 41 archivos.

**Review:** Capítulo 10 (3C), Tema 9 — El criterio: cuándo planificar primero, y Tema 10 — Combinar plan y ejecución.

**Pista de lectura (es):** "which the new API handles through a different mechanism that nobody on the team has evaluated yet" → "que la API nueva maneja con un mecanismo distinto que nadie del equipo evaluó todavía" (hay una decisión de diseño abierta, además de muchos archivos: plan primero).

</details>

#### P11 · 3C · 3.4 · Developer Productivity with Claude
Your team lead wants developers to stop entering plan mode by default, after noticing that planning a one-line fix took longer than the fix itself. The current backlog contains the five items below. Which TWO items should still start in plan mode? (Choose two.)

A) Fix the `TypeError` thrown during checkout, whose stack trace points to line 88 of `cartTotals.ts`, where a null discount is dereferenced.

B) Decide whether order notifications should move from the monolith's cron jobs to a queue-based service, then implement the chosen design.

C) Add a check to `validateCheckout` that rejects delivery dates earlier than today, returning the error type the function already uses.

D) Upgrade the date library across the storefront, where 63 files call formatting and time-zone helpers that the new major version renames.

E) Rename a prop in `ProductCard.tsx`, used only inside that component, so that it matches the design system's naming convention.

<details>
<summary>Ver respuesta</summary>

**Respuesta correcta: B+D**

**Why (es):** Plan mode va cuando hay decisiones de arquitectura o varios enfoques válidos (B: cron del monolito vs. servicio con colas) o cambios a gran escala en muchos archivos (D: 63 archivos con helpers renombrados). El resto son cambios chicos con alcance claro: ejecución directa.

**Distractors (es):**
- A: tienta porque es checkout (suena crítico) y es un bug en producción; está mal porque es un archivo y el stack trace ya dice dónde: es el ejemplo de la guía de ejecución directa.
- C: tienta porque toca la validación del checkout; está mal porque agregar una validación a una función es el otro ejemplo de la guía de ejecución directa.
- E: tienta porque "renombrar" suena a refactor; está mal porque el prop se usa solo dentro de ese componente: alcance chico y claro.

**Review:** Capítulo 10 (3C), Tema 9 — El criterio: cuándo planificar primero.

**Pista de lectura (es):** "63 files call formatting and time-zone helpers that the new major version renames" → "63 archivos usan helpers de formato y zona horaria que la nueva versión mayor renombra" (gran escala, multi-archivo: plan). Y en E, "used only inside that component" → "usado solo dentro de ese componente" (alcance acotado: directa).

</details>

#### P12 · 3C · 3.4 · Developer Productivity with Claude
In a multi-phase caching task, Claude's discovery phase runs about 70 Grep and Read calls in the main conversation. By the design phase, it ignores constraints the developer stated at the start. What's the most effective way to address this?

A) Delegate the stock-reading discovery to the Explore subagent so that only its summarized findings return to the main conversation for planning.

B) Run `/compact` after every ten tool calls during discovery so the conversation stays well below the context limit throughout the task.

C) Switch to a model with a larger context window so the discovery output and the original constraints both fit in the conversation.

D) Restate the original constraints in CLAUDE.md so they reload automatically, and keep running the discovery in the main conversation.

<details>
<summary>Ver respuesta</summary>

**Respuesta correcta: A**

**Why (es):** La causa es que la fase de descubrimiento, muy verbosa, llena el contexto principal. La guía pide usar el Explore subagent para el descubrimiento verboso: recorre el código aparte y devuelve un resumen, así el contexto no se agota en una tarea de varias fases.

**Distractors (es):**
- B: tienta porque `/compact` libera contexto; está mal porque es reactivo y con pérdida: resume en caliente (puede perder justo las restricciones) y el ruido de las 70 llamadas sigue entrando.
- C: tienta porque el síntoma es "no le alcanza el contexto"; está mal porque es el parche de "ventana más grande": sigue llenando el contexto con salida que no hace falta y la atención se diluye igual.
- D: tienta porque CLAUDE.md "se recarga solo"; está mal porque no ataca la causa (el descubrimiento sigue inundando la conversación) y mete en CLAUDE.md, que aplica siempre a todo el equipo, restricciones de una sola tarea.

**Review:** Capítulo 10 (3C), Tema 10 — El Explore subagent en tareas largas, y Tema 8 — Cuándo delegar.

**Pista de lectura (es):** "Claude's discovery phase runs about 70 Grep and Read calls in the main conversation" → "la fase de descubrimiento de Claude hace unas 70 llamadas a Grep y Read en la conversación principal" (descubrimiento verboso en el contexto principal: va a un subagente Explore).

</details>

#### P13 · 3C · 3.5 · Developer Productivity with Claude
A developer asks Claude to write `formatOrderRef`, which turns raw order identifiers from three legacy systems into the format printed on invoices. Her prompt is a 180-word paragraph describing prefixes, padding, and separators. Across four attempts, Claude produced four different outputs for the same input `ar-00731/b`, and each one is consistent with some reading of the paragraph. What's the most effective way to get consistent results?

A) Rewrite the paragraph with more precise wording, defining terms such as "prefix" and "separator" so that only one interpretation remains.

B) Ask Claude to interview her about the invoice format first, so that it can surface design considerations she may not have thought about.

C) Ask Claude to rate its confidence in each interpretation and keep the implementation it scores as most likely to match her intent.

D) Provide two or three raw identifiers with the exact formatted output expected for each, covering more than one of the legacy systems.

<details>
<summary>Ver respuesta</summary>

**Respuesta correcta: D**

**Why (es):** Cuando la descripción en prosa da resultados inconsistentes, la guía pide 2–3 ejemplos concretos de entrada y salida: un ejemplo no deja lugar a interpretación. El enunciado lo confirma: cada salida "encaja con alguna lectura" del párrafo.

**Distractors (es):**
- A: tienta porque ataca la ambigüedad; está mal porque sigue siendo prosa interpretable (ya son 180 palabras): la guía lo descarta frente a los ejemplos.
- B: tienta porque el interview pattern es otra técnica de 3.5; está mal porque sirve para un dominio desconocido con consideraciones que se pueden pasar por alto, y acá la desarrolladora sabe lo que quiere: el problema es cómo se lo transmite.
- C: tienta porque parece elegir "la mejor"; está mal porque confía en la autoevaluación del modelo, que no sabe cuál es la intención real.

**Review:** Capítulo 10 (3C), Tema 11 — Ejemplos concretos de entrada y salida, y Tema 13 — El interview pattern.

**Pista de lectura (es):** "each one is consistent with some reading of the paragraph" → "cada una es coherente con alguna lectura del párrafo" (la prosa admite varias interpretaciones: faltan ejemplos).

</details>

#### P14 · 3C · 3.5 · Developer Productivity with Claude
Claude's implementation of `calculateShipping` fails review with three problems. The weight-tier boundaries are off by one gram, and the free-shipping coupon, which is applied on top of the tier price, therefore discounts the wrong amount; separately, a log message misspells the carrier's name. A teammate suggests reporting one problem per message so each fix is easy to verify. Which approach should you take?

A) Send all three problems in a single detailed message, so Claude has the complete list of issues before it changes any code.

B) Describe the tier-boundary and coupon problems together in one detailed message, then report the log typo in a separate message.

C) Report each of the three problems in its own message, fixing the tier boundaries first because the coupon logic depends on them.

D) Run `/clear` and send a new prompt restating the original requirements, since the implementation already contains three separate defects.

<details>
<summary>Ver respuesta</summary>

**Respuesta correcta: B**

**Why (es):** La regla de la guía depende de si los problemas interactúan. El cupón se aplica sobre el precio del tramo, así que esos dos se afectan entre sí: van juntos en un mensaje detallado. El typo del log es independiente: conviene aparte, de a uno.

**Distractors (es):**
- A: tienta porque "todo junto" es lo correcto para los que interactúan, y también funcionaría; está mal porque mete el problema independiente en el mismo cambio, y la guía pide tratar lo independiente de forma secuencial.
- C: tienta porque ordena por dependencia y sigue la propuesta del compañero; está mal porque, si los mandás de a uno, Claude arregla el tramo sin saber del cupón y después tiene que rehacer o romper el primer arreglo.
- D: tienta porque `/clear` y un prompt nuevo es un consejo real de la documentación; está mal porque es para cuando ya corregiste dos veces lo mismo sin éxito, no para un primer feedback con problemas bien identificados.

**Review:** Capítulo 10 (3C), Tema 14 — ¿Todo en un mensaje o de a uno?

**Pista de lectura (es):** "which is applied on top of the tier price, therefore discounts the wrong amount; separately, a log message…" → "que se aplica sobre el precio del tramo, por eso descuenta mal; aparte, un mensaje de log…" (dos problemas que interactúan y uno independiente).

</details>

---

### Escenario: Claude Code for CI/CD

You are integrating Claude Code into TiendaX's CI/CD pipeline. A GitHub Actions workflow runs Claude Code non-interactively on every pull request to review changes and generate missing tests, and a script posts the results as inline comments on the PR. Reviews must finish before developers can merge.

#### P15 · 3D · 3.6 · Claude Code for CI/CD
The review job runs `claude -p` with `--output-format json`, and its prompt ends with "Return the findings as a JSON array with file, line, severity, and message." The posting script reads the `result` field and parses it. In about 1 of every 15 runs, parsing fails because `result` starts with a sentence before the array or names the field `lineNumber`. What change would most reliably fix this?

A) Move the output format instructions into CLAUDE.md together with an example array, so every CI run loads the same format definition.

B) Retry the job when parsing fails, up to three times, and post the first response whose `result` field parses as valid JSON.

C) Replace `--output-format json` with `--output-format stream-json` so the script receives each finding as a separate JSON event.

D) Pass the findings structure with `--json-schema` and have the script read the validated `structured_output` field instead of `result`.

<details>
<summary>Ver respuesta</summary>

**Respuesta correcta: D**

**Why (es):** `--output-format json` solo cambia el sobre: el texto de `result` sigue siendo libre. Para que un script publique comentarios inline, la guía pide `--output-format json` + `--json-schema`: la salida se valida contra el esquema y llega en `structured_output`. "Most reliably" pide una garantía, no un pedido en el prompt.

**Distractors (es):**
- A: tienta porque la guía usa CLAUDE.md para dar contexto en CI; está mal porque sigue siendo una instrucción probabilística: la forma se garantiza con un esquema.
- B: tienta porque baja la tasa de fallas; está mal porque es el parche de "más reintentos": no ataca la causa y suma tiempo a un check que bloquea el merge.
- C: tienta porque es un formato real y "más JSON"; está mal porque sirve para recibir eventos en streaming, no valida la forma de los hallazgos.

**Review:** Capítulo 11 (3D), Tema 2 — Salida estructurada: `--output-format json` y `--json-schema`.

**Pista de lectura (es):** "names the field `lineNumber`" → "le pone `lineNumber` al campo" (la forma no está garantizada: el sobre es JSON, pero el contenido no está validado).

</details>

#### P16 · 3D · 3.6 · Claude Code for CI/CD
On PR #915, the first review posted five comments; the developer fixed two issues and pushed a new commit. The workflow then reran the review, and each run starts a fresh `claude -p` invocation with the full PR diff and the team's checklist. The second run posted four comments: three repeating unresolved issues that already had open threads, and one new bug. What is the most likely root cause?

A) The second run receives no record of the first review's findings, so it cannot separate already-reported issues from new ones.

B) The checklist does not define which issues are blocking, so Claude re-flags minor issues that the developer decided not to fix.

C) The second run reviews only the diff of the latest commit, so it loses track of which earlier issues the developer has fixed.

D) The review runs in the same session that generated the code, so its earlier reasoning biases it toward repeating its own findings.

<details>
<summary>Ver respuesta</summary>

**Respuesta correcta: A**

**Why (es):** Cada corrida en CI arranca de cero: lo que no está en el contexto, no existe. Si el segundo review no recibe los hallazgos del primero, no puede saber qué ya se comentó y vuelve a publicarlo. La guía pide incluir los hallazgos previos e indicar que reporte solo lo nuevo o lo que sigue sin resolver.

**Distractors (es):**
- B: tienta porque explicaría comentarios "de más"; está mal porque el enunciado dice que los tres son problemas sin resolver ya comentados: el problema es la duplicación, no la gravedad.
- C: tienta porque revisar solo el último commit es un atajo común; está mal porque el enunciado dice que cada corrida recibe el diff completo del PR (y si revisara solo el último commit no repetiría los problemas viejos).
- D: tienta porque la independencia de la revisión es un tema de 3.6; está mal porque cada corrida es un `claude -p` nuevo: no hay sesión compartida con la generación.

**Review:** Capítulo 11 (3D), Tema 5 — Re-revisiones y tests: pasar lo que ya existe; Tema 4 — Revisar con otra instancia.

**Pista de lectura (es):** "each run starts a fresh `claude -p` invocation with the full PR diff and the team's checklist" → "cada corrida arranca una invocación nueva de `claude -p` con el diff completo del PR y el checklist del equipo" (descarta C y D, y muestra qué recibe: nada del review anterior).

</details>

#### P17 · 3D · 3.6 · Claude Code for CI/CD
A second job generates tests for changed modules. Reviewers reject most of its output: many tests only assert that exported functions exist, others rebuild customer data inline although `tests/fixtures/` already provides it, and for `couponRules.ts` it regenerated three scenarios that `couponRules.test.ts` already covers. The team's testing conventions currently live in a wiki page that the job never sees. Which approach should you take?

A) Add an independent Claude instance that reviews the generated tests and discards trivial or duplicated ones before the job commits them.

B) Run the job with `--bare` for reproducible runs, and paste the wiki's testing conventions into the prompt of every test-generation call.

C) Document testing standards, what makes a test valuable, and the available fixtures in CLAUDE.md, and pass the existing test files as context.

D) Have the job rate the value of each generated test from 1 to 10 and keep only the tests that it scores at seven or higher.

<details>
<summary>Ver respuesta</summary>

**Respuesta correcta: C**

**Why (es):** Son tres síntomas con dos causas: le falta el contexto del proyecto (qué es un test valioso, qué fixtures hay) y no ve los tests que ya existen. La guía pide documentar estándares de testing, criterios de valor y fixtures en CLAUDE.md (que se carga en cada corrida de CI) y pasar los archivos de test existentes para no duplicar escenarios.

**Distractors (es):**
- A: tienta porque la revisión independiente es una práctica de 3.6 y filtraría parte del ruido; está mal porque es un componente extra que no ataca la causa: el generador sigue sin saber los estándares ni qué tests ya existen.
- B: tienta porque `--bare` existe y la documentación lo recomienda para scripts; está mal porque la guía nombra CLAUDE.md como el mecanismo para el contexto del proyecto en CI, y además esta opción no le pasa los tests existentes (seguiría duplicando).
- D: tienta porque parece un control de calidad; está mal porque confía en la autoevaluación del modelo, que no sabe qué cubre `couponRules.test.ts` ni qué fixtures hay.

**Review:** Capítulo 11 (3D), Tema 3 — El contexto del proyecto en CI: CLAUDE.md, y Tema 5 — pasar los tests existentes.

**Pista de lectura (es):** "it regenerated three scenarios that `couponRules.test.ts` already covers" → "volvió a generar tres escenarios que `couponRules.test.ts` ya cubre" (no vio los tests existentes); y "a wiki page that the job never sees" → "una página de wiki que el job nunca ve" (los estándares no están en CLAUDE.md).

</details>

#### P18 · 3D · 1.5 (hooks de Claude Code) · Claude Code for CI/CD
The review job may also apply small fixes. TiendaX's CLAUDE.md says "Never edit files under `config/secrets/`" and "Mark a finding as blocking when it could change what customers are charged." After a month, logs show edits to `config/secrets/payments.yml` in 3 of 240 runs, and the blocking label is applied inconsistently across similar pull requests, so that last week a rounding change in `cartTotals.ts` that alters order totals was marked minor while a renamed price variable was marked blocking. What's the most effective way to address both problems?

A) Rewrite both rules in capital letters at the top of CLAUDE.md, adding a short justification for each so that Claude weighs them more heavily.

B) Add a PreToolUse hook matching `Edit|Write` in `.claude/settings.json` that exits with code 2 for `config/secrets/`, and add explicit blocking criteria with examples to CLAUDE.md.

C) Add a PreToolUse hook that exits with code 2 for `config/secrets/`, and a Stop hook that blocks completion until findings mentioning prices are labeled blocking.

D) Add a PreToolUse hook matching `Edit|Write` in `.claude/settings.json` that exits with code 1 for `config/secrets/`, and add explicit blocking criteria with examples to CLAUDE.md.

<details>
<summary>Ver respuesta</summary>

**Respuesta correcta: B**

**Why (es):** Son dos problemas de tipo distinto. "Nunca editar `config/secrets/`" se chequea con un `if` sobre el path: es determinístico y falla a veces (3 de 240), así que va en un hook PreToolUse del equipo (`.claude/settings.json`) que sale con 2 y bloquea. Decidir si un hallazgo "puede cambiar lo que se le cobra al cliente" es juicio: criterios explícitos con ejemplos en CLAUDE.md (los criterios de review en CI van ahí). Cada mecanismo para lo suyo.

**Distractors (es):**
- A: tienta porque refuerza las dos reglas; está mal porque una instrucción, por más mayúsculas que tenga, sigue siendo probabilística: "Never" ya estaba y falló en 3 corridas.
- C: tienta porque los hooks "garantizan" y la primera mitad es correcta; está mal porque un hook por palabras clave no puede juzgar el impacto: el cambio de redondeo en `cartTotals.ts` no dice "price" y quedaría afuera, y la variable de precio renombrada (que lo menciona) quedaría bloqueante sin serlo.
- D: tienta porque es igual a la correcta; está mal porque exit 1 es un error no bloqueante: la edición de `config/secrets/` sigue pasando.

**Review:** Capítulo 11 (3D), Temas 7–9 — Hooks: dónde se configuran, eventos y exit codes; Capítulo 4 (1D), Tema 12 — ¿Hook o prompt?.

**Pista de lectura (es):** "a rounding change in `cartTotals.ts` that alters order totals was marked minor" → "un cambio de redondeo en `cartTotals.ts` que altera los totales de los pedidos se marcó como menor" (decidir la gravedad es juicio: criterios con ejemplos, no un hook).

</details>
