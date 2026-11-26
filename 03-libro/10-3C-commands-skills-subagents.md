# Capítulo 10 · 3C · Udemy 11 — Commands, Skills, and Subagents (comandos, skills y subagentes)

*Tareas oficiales 3.2, 3.4 y 3.5 · Tercer capítulo del módulo 3*

---

## Dónde estamos

Seguimos en el **módulo 3: Claude Code Configuration & Workflows**. Este capítulo cubre tres tareas, cada una de 3,33% del examen:
- **3.2** Create and configure custom slash commands and skills (crear y configurar comandos y skills propios).
- **3.4** Determine when to use plan mode vs direct execution (decidir cuándo planificar primero y cuándo ejecutar directo).
- **3.5** Apply iterative refinement techniques for progressive improvement (técnicas para ir mejorando un resultado de a poco).

### Cómo leer este capítulo

Todo lo que leés acá **vale para el examen**, salvo que diga lo contrario. Cuando algo sale solo del curso (útil para entender, pero no central), lo marco con **📘 Curso**. Cuando Jacob dice algo distinto de lo que evalúa la guía, aparece un recuadro así:

> ⚠️ **En el curso vas a escuchar otra cosa.** … **Para el examen: …**

### Un aviso sobre este capítulo

El curso explica bien qué son los comandos, las skills, los subagentes y plan mode. Pero no enseña las técnicas de la tarea 3.5 y no explica bien los campos de configuración de skills que pide la guía; esas partes salen de la guía oficial (ver la revisión al final).

## De dónde venimos

En 3A y 3B viste cómo se le **enseña** el proyecto a Claude Code: CLAUDE.md para lo que aplica siempre y `.claude/rules/` para lo que aplica a ciertos archivos. También conociste plan mode y el Explore subagent por encima. Este capítulo agrega las herramientas para **extender** Claude Code con tareas que se usan a veces (comandos y skills), para **delegar** trabajo (subagentes), y para decidir **cómo trabajar** con Claude en una tarea (planificar primero o no, y cómo corregirlo).

## Mapa del capítulo

**Parte 1 — Comandos y skills (tarea 3.2).**
1. Custom slash commands (comandos propios).
2. Skills: qué son y cómo se activan.
3. `context: fork`: correr una skill aparte.
4. `allowed-tools` y `argument-hint`.
5. Tu versión personal de una skill del equipo.
6. ¿CLAUDE.md, rules, comando, skill o subagente?

**Parte 2 — Subagentes de Claude Code.**

7. Custom subagents (subagentes propios): cómo se definen.
8. Cuándo delegar y cuándo no.

**Parte 3 — Plan mode o ejecución directa (tarea 3.4).**

9. El criterio: cuándo planificar primero.
10. Combinar plan y ejecución, e iterar sobre el plan.

**Parte 4 — Mejorar el resultado de a poco (tarea 3.5).**

11. Ejemplos concretos de entrada y salida.
12. Test-driven iteration (iterar guiado por tests).
13. El interview pattern (patrón de entrevista).
14. ¿Todo en un mensaje o de a uno?

---

# Parte 1 — Comandos y skills

## Tema 1 — Custom slash commands (comandos propios)

### Qué es

Un **slash command** es un atajo que escribís en Claude Code empezando con `/`, por ejemplo `/review`. Claude Code ya trae varios (`/clear`, `/compact`, `/memory`), pero también podés crear los tuyos. Un comando propio es, en el fondo, **un prompt guardado**: en vez de escribir cada vez "Revisá este código con el checklist del equipo: seguridad, tests, nombres…", lo escribís una vez en un archivo y después lo llamás con `/review`.

Crear uno es muy simple: un archivo Markdown en la carpeta `commands`. **El nombre del archivo es el nombre del comando**, sin registrarlo en ningún lado. `review.md` se convierte en `/review`.

**¿Dónde va el archivo?** Es la misma lógica que ya viste con CLAUDE.md y con `.mcp.json`. Si lo ponés **en el repo**, lo tiene todo el equipo. Si lo ponés **en tu carpeta personal**, solo vos.

| Ubicación | Quién lo tiene |
|---|---|
| `.claude/commands/review.md` (dentro del repo) | Todo el equipo, apenas clona o hace pull: viaja por git |
| `~/.claude/commands/review.md` (tu carpeta personal) | Solo vos, en todos tus proyectos |

**Argumentos.** Si escribís `/fix-issue 1234`, el texto que va después del comando (`1234`) llega al prompt en el lugar donde pusiste **`$ARGUMENTS`**. Así un mismo comando sirve para cualquier issue.

**Comandos y skills hoy son lo mismo.** Claude Code unificó los comandos con las skills (Tema 2): `.claude/commands/deploy.md` y `.claude/skills/deploy/SKILL.md` crean el mismo `/deploy`. La carpeta `commands` sigue funcionando y es la que nombra la guía; para cosas nuevas se recomienda el formato de skill, porque permite agregar archivos de apoyo.

### Cómo se configura

`.claude/commands/review.md`:

```markdown
Revisá los cambios del branch actual contra main con el checklist del equipo:
1. ¿Los montos están en centavos (`priceCents`)?
2. ¿Cada componente nuevo tiene su `.test.tsx`?
3. ¿Hay algún secreto o token en el diff?
Respondé con una lista: ✅ lo que está bien, ❌ lo que hay que corregir y en qué archivo.
```

`.claude/commands/fix-issue.md`:

```markdown
Leé el issue #$ARGUMENTS de GitHub, reproducí el error con un test y arreglalo.
```

### Ejemplo

El tech lead de TiendaX quiere que todos revisen el código con el mismo checklist. Crea `.claude/commands/review.md` en el repo y lo commitea. Al día siguiente, Sofía hace `git pull` y ya puede escribir `/review`: no tuvo que instalar ni configurar nada. Esa es exactamente la pregunta oficial **Q4** de la guía.

### Para el examen

- Comando para **todo el equipo**, disponible al clonar → **`.claude/commands/` en el repo**. Comando personal → `~/.claude/commands/`.
- Los distractores de Q4: definir el comando **dentro de CLAUDE.md** (CLAUDE.md es para instrucciones y contexto, no para definir comandos) y un archivo **`.claude/config.json`** con un array de comandos (no existe).

### Cómo se une

Un comando es un prompt guardado que **vos** llamás. Una skill va un paso más allá: puede llamarla Claude sola cuando la tarea lo pide.

---

## Tema 2 — Skills: qué son y cómo se activan

### Qué es

Una **skill** es un paquete de instrucciones para hacer una tarea específica: un procedimiento (cómo hacer un deploy), un checklist (cómo revisar un PR) o material de referencia (la guía de estilo de la API). La diferencia con CLAUDE.md es **cuándo se carga**. CLAUDE.md entra al contexto en **todas** las sesiones, lo uses o no. El contenido de una skill entra **solo cuando se usa**. Por eso una skill puede ser larga y detallada sin costar nada mientras no se necesita.

La documentación da un criterio práctico para crear una: cuando te encontrás **pegando las mismas instrucciones una y otra vez** en el chat, o cuando una sección de tu CLAUDE.md dejó de ser un dato ("los montos van en centavos") y se convirtió en un **procedimiento** ("para hacer un release: 1, 2, 3…").

**Cómo se arma.** Una skill es una **carpeta** dentro de `.claude/skills/` con un archivo **`SKILL.md`** adentro. El nombre de la carpeta es el nombre de la skill (y su comando: `/release`). El `SKILL.md` empieza con un **frontmatter**: un bloque de configuración en YAML entre dos líneas `---`, igual que en las rules de 3B. Debajo van las instrucciones. En la misma carpeta podés agregar archivos de apoyo (ejemplos, scripts) que Claude lee solo si los necesita.

**Cómo se activa.** Hay dos formas:
1. **Vos la llamás** escribiendo `/release`.
2. **Claude la elige sola.** Al arrancar, Claude Code carga solamente la **`description`** de cada skill (una o dos líneas). Cuando le pedís algo, Claude compara tu pedido con esas descripciones y, si una coincide, carga la skill completa. Por eso la `description` es lo más importante del frontmatter: si es vaga, Claude no la elige cuando corresponde, o la elige cuando no.

Si una skill tiene **efectos que no se pueden deshacer** (hacer un release, mandar un mail), conviene que solo la pueda llamar una persona. Para eso está **`disable-model-invocation: true`**: Claude ya no la dispara por su cuenta, solo corre si alguien escribe `/release`.

> ⚠️ **En el curso vas a escuchar otra cosa.** El companion dice que `SKILL.md` necesita tres campos obligatorios (`name`, `description` y `trigger`) y que las skills pueden dispararse por eventos del sistema, como "terminó el build". **Para el examen:** no existe el campo `trigger` y **ningún campo es obligatorio** (si falta `name`, se usa el nombre de la carpeta). Una skill se activa porque la llamás o porque Claude la elige por su `description`. Lo que reacciona a eventos del sistema son los **hooks**, no las skills.

### Cómo se configura

`.claude/skills/release/SKILL.md`:

```markdown
---
description: Prepara y publica un release de storefront (changelog, versión, tag). Usar solo cuando se pida un release.
disable-model-invocation: true
---

1. Corré `npm test`; si algo falla, frená y avisá.
2. Generá el changelog desde el último tag con `git log`.
3. Subí la versión en `package.json` (semver).
4. Creá el tag `vX.Y.Z` y mostrame el resumen antes de hacer push.
```

### Ejemplo

Lucas se cansó de pegar el mismo procedimiento de release cada dos semanas. Lo pasa a `.claude/skills/release/SKILL.md` con `disable-model-invocation: true`. Desde entonces escribe `/release` y Claude sigue los pasos. Nunca arranca un release solo por haber leído la palabra "versión" en la conversación.

### Para el examen

- Una skill **no es determinista**: se carga solo si la llamás o si Claude decide que viene al caso, así que puede no cargarse. Por eso **no** sirve para convenciones que se tienen que aplicar siempre (eso es CLAUDE.md o rules, Q6 de 3B).
- Campo `trigger` o "skills que se disparan por eventos": es un distractor, porque ese campo no existe y lo que reacciona a eventos son los hooks.

### Cómo se une

Hasta acá la skill corre **en tu conversación**: todo lo que produce queda en tu contexto. A veces eso es un problema.

---

## Tema 3 — `context: fork`: correr una skill aparte

### Qué es

Imaginá una skill que analiza todo el código para encontrar funciones sin tests. Para eso lee decenas de archivos y genera mucha salida. Si corre en tu conversación, todo ese material queda en tu contexto: lo llena de cosas que no vas a volver a mirar, y el resto de la sesión trabaja peor (es la dilución de atención que viste en 1B).

**`context: fork`** resuelve esto. Con ese campo en el frontmatter, la skill **no corre en tu conversación**: Claude Code lanza un **subagente** (un Claude aparte, con su propio contexto), le da la skill como tarea, el subagente hace todo el trabajo pesado y a tu conversación vuelve **solo el resultado**. El subagente no ve tu historial, y tu historial no se ensucia con su trabajo.

La guía nombra dos casos típicos:
- Skills con **salida muy verbosa**, como un análisis del codebase.
- Skills **exploratorias**, como pensar varias alternativas (brainstorming), cuando no querés que todas las ideas descartadas queden en la conversación principal.

Un detalle: `context: fork` sirve para skills que son **una tarea concreta** ("analizá X y devolvé Y"). Una skill que es solo conocimiento ("usá estas convenciones") no tiene sentido en un fork, porque el subagente no tendría nada que hacer.

### Cómo se configura

`.claude/skills/coverage-audit/SKILL.md`:

```markdown
---
description: Busca funciones sin tests en src/ y devuelve un resumen.
context: fork
---

Recorré src/ y listá las funciones exportadas que no tienen ningún test que las llame.
Devolvé solo una tabla: archivo, función, motivo probable.
```

### Ejemplo

Sofía corre `/coverage-audit`. Un subagente revisa 180 archivos. A su conversación vuelve una tabla de 12 filas. Si la skill no tuviera `context: fork`, los 180 archivos habrían pasado por su contexto.

### Para el examen

- Skill que genera mucha salida o que explora alternativas, y no querés que **contamine la conversación principal** → **`context: fork`**.
- Distractor típico: "abrir una sesión nueva para correrla". Funciona, pero la respuesta de la guía es `context: fork`.

### Cómo se une

`context: fork` controla **dónde** corre la skill. Los otros dos campos que nombra la guía controlan **qué puede hacer** y **cómo se llama**.

---

## Tema 4 — `allowed-tools` y `argument-hint`

### Qué es

**`allowed-tools`.** Lista las herramientas con las que trabaja la skill. La guía lo presenta como una forma de **restringir** lo que puede hacer la skill mientras corre. Su ejemplo: una skill que solo debería escribir archivos se limita a esas operaciones, para que no pueda hacer nada destructivo, como borrar con Bash.

**`argument-hint`.** Es un texto corto que le indica al desarrollador **qué parámetros espera** la skill, por ejemplo `[número-de-issue]`. La guía lo presenta como la forma de **pedirle** al dev los parámetros requeridos cuando invoca la skill sin pasarlos.

> ⚠️ **En el curso vas a escuchar otra cosa.** Las slides dicen que `allowed-tools` "pre-aprueba" herramientas, o sea que las usa sin pedirte permiso pero no bloquea las demás, y que `argument-hint` es una pista del **autocomplete** (autocompletado). **Para el examen: respondé como la guía.** `allowed-tools` sirve para limitar las herramientas de la skill y `argument-hint` para pedir los parámetros que faltan, porque así están redactadas las tareas oficiales.

### Cómo se configura

```markdown
---
description: Genera el archivo de migración de base de datos para un ticket.
argument-hint: [número-de-ticket]
allowed-tools: Read, Write
---

Leé el ticket $ARGUMENTS y escribí la migración en db/migrations/.
No ejecutes nada.
```

### Ejemplo

El equipo de TiendaX tiene `/new-migration`. Si alguien escribe solo `/new-migration`, el autocompletado le muestra `[número-de-ticket]` y sabe qué pasar. Y como la skill solo debería **escribir** el archivo de migración, el equipo la configura con `allowed-tools: Read, Write`, para que no pueda correr la migración ni tocar la base.

### Para el examen

- "Limitar las herramientas de una skill para evitar acciones destructivas" → **`allowed-tools`**.
- "El dev invoca la skill sin argumentos y no sabe qué pasar" → **`argument-hint`**.
- No los mezcles con `context: fork`: ese es para **aislar la salida**, no para limitar herramientas.

### Cómo se une

Las skills del equipo viven en el repo. ¿Qué pasa si querés tu propia versión de una?

---

## Tema 5 — Tu versión personal de una skill del equipo

### Qué es

A veces una skill del equipo casi te sirve, pero querés ajustarla a tu manera: por ejemplo, un `/review` que además te explique cada problema en detalle. No podés editar la del repo, porque afectarías a todos. La solución es crear **tu propia variante en `~/.claude/skills/`**, tu carpeta personal, que no viaja por git.

La guía agrega un detalle clave: hacelo **con otro nombre**. Si tu skill personal se llama igual que la del equipo, en tu máquina **la tuya tapa a la del equipo** (cuando hay dos skills con el mismo nombre, la personal tiene prioridad sobre la del proyecto). Entonces dejarías de ver lo que ven tus compañeros y no te enterarías cuando el equipo actualice la suya. Con otro nombre conviven las dos: `/review` (la del equipo) y `/review-detallado` (la tuya).

### Ejemplo

Lucas crea `~/.claude/skills/review-detallado/SKILL.md` con el checklist del equipo más explicaciones largas. Sofía y el resto siguen usando `/review` sin enterarse de nada.

### Para el examen

- Personalizar una skill **sin afectar al equipo** → copia en **`~/.claude/skills/` con otro nombre**.
- ❌ Editar la del repo · ❌ crear la personal con el mismo nombre.

### Cómo se une

Ya tenés muchas herramientas: CLAUDE.md, rules, comandos, skills… La guía pregunta mucho cuál elegir.

---

## Tema 6 — ¿CLAUDE.md, rules, comando, skill o subagente?

### Qué es

La pregunta que decide casi todo es: **¿esto tiene que estar siempre presente, o solo cuando se usa?**

- Lo que vale **siempre**, en cualquier tarea (convenciones del equipo, comandos de test), va en **CLAUDE.md**. Se carga en todas las sesiones.
- Lo que vale **solo para ciertos archivos**, va en **rules con `paths:`**. Se carga sola cuando Claude toca esos archivos (3B).
- Un **flujo que se usa a veces** (release, review, migración), va en una **skill** o un **comando**. Se carga cuando se invoca. La guía lo resume así: skills para tareas puntuales a demanda; CLAUDE.md para estándares universales siempre cargados.
- Trabajo que conviene hacer **aparte** (mucha salida, herramientas limitadas, una tarea que se resuelve sola y devuelve un resumen), va en un **subagente** (Tema 7).
- Algo que **tiene que pasar sí o sí** (formatear después de editar, bloquear un comando) no va en ninguno de estos: va en un **hook** o una regla de permiso, que son lo único determinista.

| Necesidad | Dónde va | Por qué |
|---|---|---|
| "Montos en centavos" (siempre) | CLAUDE.md | Aplica a todo, en cada sesión |
| Convenciones de los `*.test.tsx` | `.claude/rules/` con `paths:` | Solo a ciertos archivos, automático |
| `/review` del equipo | `.claude/commands/` o `.claude/skills/` | Se usa a demanda |
| Auditoría que lee todo el repo | Skill con `context: fork` o subagente | Mucha salida: mejor aparte |
| "Siempre correr el formatter tras editar" | Hook | Tiene que pasar siempre |

### Ejemplo

El CLAUDE.md de TiendaX tenía 80 líneas sobre "cómo hacer un release". Se usan dos veces por mes, pero ocupaban contexto en todas las sesiones. Se movieron a la skill `/release`, y el CLAUDE.md quedó con lo que aplica siempre.

### Para el examen

- Estándar universal → CLAUDE.md. Flujo puntual → skill. Convención por tipo de archivo → rules con `paths:`. Obligatorio → hook o deny.
- ❌ Convención que debe aplicarse automáticamente, puesta en una skill: la skill no es determinista.
- ❌ Procedimiento largo y ocasional, puesto en CLAUDE.md: gasta contexto en todas las sesiones.

### Cómo se une

Nombramos los subagentes varias veces. Ahora vemos cómo se definen los tuyos.

---

# Parte 2 — Subagentes de Claude Code

## Tema 7 — Custom subagents (subagentes propios): cómo se definen

### Qué es

En 1C viste los subagentes desde el Agent SDK. En Claude Code son la misma idea: un **Claude aparte**, con **su propio contexto**, **su propio system prompt** (las instrucciones de su rol) y **sus propias herramientas**, al que se le delega una tarea y que devuelve solo el resultado. Claude Code ya trae algunos (Explore, Plan, general-purpose), y podés crear los tuyos.

**Dónde se definen.** Un archivo Markdown por subagente. Igual que todo lo demás: en el repo para el equipo, en tu carpeta para vos.

| Ubicación | Quién lo tiene |
|---|---|
| `.claude/agents/code-reviewer.md` | Todo el equipo (git) |
| `~/.claude/agents/code-reviewer.md` | Solo vos |

**Qué tiene el archivo.** Un frontmatter con:
- **`name`** (obligatorio): el nombre del subagente.
- **`description`** (obligatorio): cuándo conviene usarlo. Es lo que Claude lee para decidir si le delega una tarea, igual que con las skills y las tools de 2A.
- **`tools`**: las herramientas que puede usar. **Si no ponés este campo, hereda todas.**
- **`model`** (opcional): por ejemplo, un modelo más rápido y barato para tareas simples.

El texto debajo del frontmatter es su **system prompt**.

**Qué ve y qué no ve.** El subagente **no ve tu conversación**: ni lo que hablaste, ni los archivos que Claude ya leyó. Arranca con su system prompt y un **delegation message** (mensaje de delegación) que Claude escribe resumiendo la tarea. Por eso, igual que en 1C, el contexto que necesita **hay que pasárselo explícitamente**. Lo que sí carga son tus CLAUDE.md (salvo Explore y Plan, que arrancan sin ellos para ser rápidos).

**Cómo se usa.** Claude delega solo cuando la tarea coincide con la `description` (si querés que lo haga seguido, la documentación sugiere poner "use proactively" en la descripción). También podés pedirlo directamente: "usá el subagente code-reviewer para revisar este cambio".

Restringir `tools` es una de sus ventajas más fuertes: un subagente con `tools: Read, Grep, Glob` **no puede** editar nada, y eso lo garantiza Claude Code, no depende de que el modelo obedezca un prompt.

> ⚠️ **En el curso vas a escuchar otra cosa.** El companion dice que los subagentes se lanzan con el comando `/agents` y que arrancan con un contexto "completamente vacío". **Para el examen:** los subagentes los lanza Claude con la tool Agent (o vos pidiéndoselo); `/agents` solo servía para crear y administrar sus configuraciones (en las versiones actuales solo muestra un recordatorio). Y no arrancan vacíos: no ven tu conversación, pero sí cargan su system prompt y tus CLAUDE.md. La idea que vale es la misma de 1C: **pasale explícitamente el contexto que necesita**.

### Cómo se configura

`.claude/agents/code-reviewer.md`:

```markdown
---
name: code-reviewer
description: Revisa cambios de código buscando bugs, problemas de seguridad y tests faltantes. Usar después de cada cambio importante.
tools: Read, Grep, Glob
model: sonnet
---

Sos un revisor de código de TiendaX. Revisá el diff que te indiquen.
Devolvé una lista ordenada por gravedad: archivo, línea, problema y cómo arreglarlo.
No edites nada.
```

### Ejemplo

Lucas termina un cambio en el checkout y le pide a Claude que lo revise. Claude delega en `code-reviewer`: el subagente lee el diff y los archivos que necesita, y devuelve una lista de 5 problemas. La conversación de Lucas recibe solo esa lista. Y aunque el revisor "quisiera" arreglar algo, no puede: no tiene Edit ni Write.

### Para el examen

- Subagente del equipo → `.claude/agents/`. Personal → `~/.claude/agents/`.
- Limitar lo que puede hacer → campo **`tools`** (si lo omitís, hereda todas).
- No ve tu conversación → hay que pasarle el contexto.

### Cómo se une

Tener subagentes no significa que haya que usarlos siempre.

---

## Tema 8 — Cuándo delegar y cuándo no

### Qué es

Delegar en un subagente tiene un costo: el subagente arranca sin tu conversación, así que Claude tiene que resumirle la tarea, y lo que no esté en ese resumen se pierde. Además gasta tokens extra. Por eso conviene delegar solo cuando el aislamiento aporta algo.

**Conviene un subagente cuando:**
- La tarea genera **mucha salida** que no necesitás en tu conversación (buscar en todo el repo, analizar logs).
- Querés **limitar herramientas o permisos** (un revisor que no pueda editar).
- El trabajo **se resuelve solo** y alcanza con un resumen al final.
- Querés una **mirada fresca**, sin el sesgo de lo que ya se habló (un revisor independiente).

**Conviene seguir en la conversación principal cuando:**
- La tarea necesita **ida y vuelta** con vos o refinamiento iterativo.
- Varias etapas **comparten mucho contexto** (planificar, implementar y probar lo mismo).
- Es un **cambio rápido y puntual**.

Un matiz de la documentación actual: delegar **no hace que la respuesta sea mejor**; solo la aísla. Lo que sí mejora es pedirle a un subagente **nuevo** que revise algo, porque no arrastra las suposiciones de la conversación.

📘 **Curso:** antes de delegar, el curso propone responder tres preguntas: cuál es la tarea, qué contexto necesita y en qué formato tiene que devolver el resultado (idealmente estructurado, con un estado de "terminado / falló"). Es la misma idea de 1C de pasar el contexto y pedir una salida estructurada.

### Ejemplo

- "Buscá en todo el **monorepo** (un solo repo con varios proyectos) dónde se usa la API vieja de pagos": conviene un **subagente**, porque genera mucha salida y alcanza con la lista final.
- "Cambiemos juntos el texto de este botón y vemos cómo queda": conviene la **conversación principal**, porque hay ida y vuelta y es un cambio rápido.

### Para el examen

- Salida verbosa, herramientas restringidas o tarea autocontenida → subagente.
- Iteración con vos o cambio rápido → conversación principal.

### Cómo se une

Esto cierra las herramientas. Ahora pasamos a **cómo trabajar** con Claude en una tarea, empezando por si planificar primero.

---

# Parte 3 — Plan mode o ejecución directa

## Tema 9 — El criterio: cuándo planificar primero

### Qué es

En 3A viste qué es **plan mode**: Claude lee el código, explora y escribe un plan, pero **no modifica nada** hasta que lo aprobás. Lo opuesto es la **direct execution** (ejecución directa): Claude empieza a cambiar el código enseguida.

¿Por qué no planificar siempre? Porque planificar cuesta tiempo. En un cambio chico y claro, el plan no agrega nada: ya sabés qué hay que hacer. ¿Y por qué no ejecutar siempre directo? Porque en un cambio grande, si Claude arranca sin entender las dependencias, puede tomar un camino equivocado y descubrirlo cuando ya tocó 30 archivos. Rehacer eso es caro. La guía lo dice así: plan mode permite **explorar y diseñar de forma segura antes de comprometerse con cambios, y así evitar retrabajo costoso**.

El criterio de la guía es la **complejidad**:

**Plan mode** cuando la tarea tiene:
- **Cambios a gran escala** o en **muchos archivos** (la guía da el ejemplo de una migración de librería que afecta 45 archivos o más).
- **Varias formas válidas** de hacerlo, y hay que elegir.
- **Decisiones de arquitectura** (reestructurar en microservicios, elegir entre dos integraciones con distinta infraestructura).

**Ejecución directa** cuando el cambio es **simple y con alcance claro**:
- Un bug en **un archivo** con un **stack trace** (la lista de llamadas que muestra dónde ocurrió el error) que señala el lugar.
- Agregar **una validación** a una función (por ejemplo, validar una fecha).

En 3A viste la pregunta oficial **Q5** (reestructurar un monolito en microservicios). La lección que deja: si la complejidad **ya está en el enunciado**, plan mode **desde el principio**, no "arrancar directo y pasar a plan mode si aparece complejidad".

### Ejemplo

| Pedido en TiendaX | Modo | Por qué |
|---|---|---|
| "Migrar de Moment.js a date-fns en todo el storefront (60 archivos)" | Plan | Muchos archivos, conviene ver todos los usos antes |
| "Elegir entre Stripe y MercadoPago para el checkout" | Plan | Dos enfoques válidos con distinta infraestructura |
| "`calcularEnvio` tira `TypeError: Cannot read properties of null` en la línea 42 (stack trace adjunto)" | Directa | Un archivo, el error ya dice dónde |
| "Validar que la fecha de entrega no sea anterior a hoy" | Directa | Un cambio chico y claro |

### Para el examen

- Multi-archivo, arquitectura o varios enfoques válidos → **plan mode**.
- Un archivo, alcance claro → **ejecución directa** (plan mode sería un paso de más).
- Complejidad ya conocida → plan mode **desde el inicio**.

### Cómo se une

La guía no los presenta como opciones excluyentes: lo mejor muchas veces es **combinarlos**.

---

## Tema 10 — Combinar plan y ejecución, e iterar sobre el plan

### Qué es

**Plan para investigar, ejecución para implementar.** El flujo que premia la guía en tareas grandes es: primero plan mode para entender el código y diseñar el enfoque; después, con el plan aprobado, ejecución directa para hacer los cambios. Su ejemplo: planificar una migración de librería y después ejecutar el enfoque planificado.

**Iterar sobre el plan.** Cuando Claude termina el plan, te lo muestra y te da tres opciones:
- **Aprobarlo** y dejar que ejecute (con aprobación automática de ediciones o pidiéndote permiso en cada una).
- **Editarlo vos mismo** antes de aprobarlo: con `Ctrl+G` se abre en tu editor de texto. 📘 El curso dice que editar el plan directamente suele ser más rápido que pedir uno nuevo.
- **"No, keep planning"** (seguir planificando): le decís qué cambiar y Claude rehace el plan.

**Si la realidad no coincide con el plan.** A veces, ejecutando, Claude descubre algo que el plan no previó (un archivo que no existe, una dependencia oculta). Lo correcto es **frenar, avisar y volver a planificar**, no improvisar en silencio. Si ves que Claude se desvía, `Esc` lo interrumpe.

**El Explore subagent en tareas largas.** La guía también pide usar el **Explore subagent** para las fases de descubrimiento que generan mucha salida, así el contexto no se agota en una tarea de varias fases. En la práctica: Explore recorre el código y devuelve un resumen; con ese resumen se planifica; con el plan se implementa.

### Ejemplo

Migración de Moment.js a date-fns en TiendaX:
1. Lucas entra en **plan mode**. Claude usa **Explore** para encontrar los 60 usos y devuelve un resumen agrupado por tipo de uso.
2. Claude propone un plan en 6 pasos. Lucas lo abre con `Ctrl+G` y cambia el orden: primero los helpers compartidos.
3. Aprueba. Claude pasa a **ejecución directa** y migra archivo por archivo.
4. En el paso 4 aparece un uso de zonas horarias que date-fns maneja distinto. Claude frena, avisa, y Lucas vuelve a plan mode para decidir ese caso.

### Para el examen

- Tarea grande → **plan para investigar + ejecución para implementar**.
- Descubrimiento con mucha salida en una tarea larga → **Explore subagent**.
- El plan no coincide con la realidad → frenar y re-planificar.

### Cómo se une

Plan mode decide **cómo arrancar**. La tarea 3.5 trata de **cómo corregir** cuando el resultado todavía no es el que querés.

---

# Parte 4 — Mejorar el resultado de a poco (tarea 3.5)

## Tema 11 — Ejemplos concretos de entrada y salida

### Qué es

A veces describís en palabras lo que querés y Claude lo interpreta distinto cada vez. No es que Claude "no entienda": la descripción en prosa admite varias lecturas. La guía dice que en ese caso lo más efectivo es **mostrar 2 o 3 ejemplos concretos de entrada y salida**: "con esto, quiero esto". Un ejemplo no deja lugar a interpretación.

Lo mismo vale para los **edge cases** (casos borde), las situaciones poco comunes que el código suele manejar mal. Si falla con valores nulos, en vez de decir "manejá bien los nulos", dale **un caso de prueba concreto**: esta entrada con un nulo, y esta es la salida esperada.

### Ejemplo

**Mal (prosa):** "Normalizá los nombres de los productos para que queden prolijos." Una vez Claude pone todo en mayúsculas, otra quita las tildes, otra deja todo igual.

**Bien (ejemplos):**

```
Entrada: "  zapatillas RUNNING  pro "   → Salida: "Zapatillas Running Pro"
Entrada: "remera-básica"               → Salida: "Remera Básica"
Entrada: "BUZO   oversize"             → Salida: "Buzo Oversize"
```

Con tres ejemplos queda claro: sacar espacios de más, cambiar guiones por espacios, mayúscula al principio de cada palabra y respetar las tildes.

**Caso borde:** el script de migración rompe cuando un producto no tiene precio. En vez de "arreglá los nulos", le pasás esta entrada: `{ "sku": "ZAP-01", "price": null }`, y le decís que la salida esperada es `{ "sku": "ZAP-01", "priceCents": 0, "needsReview": true }`.

### Para el examen

- "La descripción en lenguaje natural da resultados inconsistentes" → **2–3 ejemplos concretos de entrada y salida**.
- "Falla un caso borde" (por ejemplo, nulos) → **un caso de prueba específico con entrada y salida esperada**.
- ❌ "Reescribir la descripción más larga y más precisa": sigue siendo prosa interpretable.

### Cómo se une

Un ejemplo de entrada y salida ya es casi un test. La técnica siguiente lleva eso al extremo.

---

## Tema 12 — Test-driven iteration (iterar guiado por tests)

### Qué es

La idea es **escribir los tests antes que el código**. Los tests describen el comportamiento esperado: los casos normales, los casos borde y, si importa, los requisitos de rendimiento. Después Claude implementa, corre los tests, y si algo falla, **le pasás el fallo**. Claude lo lee, corrige y vuelve a correr los tests, hasta que pasen todos.

¿Por qué funciona tan bien? Porque un test da una respuesta objetiva: pasa o no pasa. Claude no tiene que adivinar si "quedó bien"; tiene un criterio claro y puede cerrar el ciclo solo. La documentación lo dice así: si le das algo que responde "pasa o falla", Claude puede hacer el cambio, correr la verificación y arreglar lo que se rompió sin que vos intervengas.

### Ejemplo

Hay que implementar `calcularEnvio(peso, provincia, cupon)`:
1. Primero se escriben los tests: envío normal a Córdoba; envío gratis con cupón; peso 0 (caso borde); provincia inexistente (caso borde); 10.000 cálculos en menos de 1 segundo (rendimiento).
2. Claude implementa. Fallan 2 de 5.
3. Le pasás la salida de esos 2 tests. Claude ve que el cupón no se aplica cuando el peso es 0, lo corrige y vuelve a correr todo.
4. Pasan los 5.

### Para el examen

- Mejorar de forma progresiva, con un criterio objetivo → **tests primero** (comportamiento esperado, casos borde, rendimiento) e **iterar compartiendo los fallos**.
- ❌ Implementar primero y escribir los tests al final.

### Cómo se une

Los tests sirven cuando ya sabés qué tiene que pasar. ¿Y si todavía no lo sabés?

---

## Tema 13 — El interview pattern (patrón de entrevista)

### Qué es

Cuando trabajás en un tema que no conocés bien, el riesgo es que no sepas qué preguntar ni qué decisiones hay que tomar. El **interview pattern** da vuelta la situación: en vez de que vos le expliques todo a Claude, **le pedís que te entreviste**. Claude te hace preguntas para descubrir lo que no habías pensado, y recién después implementa.

La guía da dos ejemplos de lo que suele aparecer en esas preguntas: **cache invalidation strategies** (estrategias de invalidación de caché: cuándo un dato guardado queda viejo y hay que borrarlo) y **failure modes** (modos de falla: qué pasa si un servicio no responde). Son cosas que un desarrollador que no conoce el dominio puede olvidar por completo.

La documentación da un prompt modelo: "Quiero agregar **rate limiting** (limitar cuántos pedidos por minuto acepta la API) a la API pública pero no lo pensé a fondo. Entrevistame hasta que puedas escribir la especificación y después escribila en SPEC.md."

### Ejemplo

Lucas tiene que agregar una caché al catálogo de TiendaX y nunca trabajó con cachés. Le pide a Claude que lo entreviste primero. Claude pregunta:
- ¿Cada cuánto cambian los precios?
- ¿Qué pasa si un precio cambia mientras está en caché?
- ¿Qué hacemos si el servidor de caché se cae: mostramos error o vamos a la base?

Lucas no había pensado en la segunda ni en la tercera. Con las respuestas, Claude escribe una especificación y recién después implementa.

### Para el examen

- Dominio desconocido, consideraciones de diseño que podrían pasarse por alto → **interview pattern**.
- No hace falta cuando la transformación ya está clara: ahí van ejemplos de entrada y salida (Tema 11).

### Cómo se une

La última técnica es sobre **cómo dar el feedback**: todo junto o de a partes.

---

## Tema 14 — ¿Todo en un mensaje o de a uno?

### Qué es

Supongamos que el resultado tiene varios problemas. ¿Se los decís todos juntos o de a uno? Depende de si los problemas **se afectan entre sí**.

- **Si interactúan** (arreglar uno cambia cómo hay que arreglar el otro), van **todos juntos en un solo mensaje detallado**. Si los mandás de a uno, Claude arregla el primero sin saber del segundo y después tiene que rehacer el trabajo, o el segundo arreglo rompe el primero.
- **Si son independientes** (no tienen nada que ver entre sí), conviene **de a uno**: cada corrección es más simple, más fácil de verificar, y si una sale mal no arrastra a las otras.

Un consejo extra de la documentación: si ya corregiste dos veces lo mismo y sigue mal, no insistas con una tercera corrección en la misma conversación. `/clear` y un prompt nuevo que incluya todo lo que aprendiste suele funcionar mejor.

### Ejemplo

- **Interactúan:** el cálculo de envío está mal **y** el cupón de envío gratis también. El cupón depende del cálculo: si arreglás primero uno sin mencionar el otro, el segundo arreglo puede romper el primero. Conviene mandar **un solo mensaje** que explique los dos y cómo se relacionan.
- **Independientes:** un typo en el botón "Comprar" y un color equivocado en el footer. Van **de a uno**, porque no se tocan.

### Para el examen

- Problemas que **interactúan** → **un solo mensaje detallado con todos**.
- Problemas **independientes** → **secuencial**, de a uno.

### Cómo se une

Cierra el capítulo. En 3D vas a ver cómo llevar todo esto a la automatización: hooks, el Agent SDK y Claude Code en CI/CD.

---

## Cómo se une todo

Un **comando** es un prompt guardado que llamás con `/nombre`; si es del equipo va en `.claude/commands/` dentro del repo, y si es tuyo en `~/.claude/commands/` (Tema 1). Una **skill** es un procedimiento o material que se carga solo cuando se usa, ya sea porque la llamás o porque Claude la elige por su `description`; no existe un campo `trigger` y no es determinista (Tema 2). Con **`context: fork`** la skill corre en un subagente y no ensucia tu conversación (Tema 3); con **`allowed-tools`** se limitan sus herramientas y con **`argument-hint`** se indican los parámetros (Tema 4). Tu versión personal va en `~/.claude/skills/` **con otro nombre** (Tema 5).

Para elegir dónde va cada cosa, la pregunta es si aplica siempre (CLAUDE.md), a ciertos archivos (rules), a demanda (skill o comando), aparte (subagente) o si tiene que pasar sí o sí (hook) (Tema 6). Los **subagentes propios** se definen en `.claude/agents/` con `name`, `description`, `tools` y `model`; no ven tu conversación, así que hay que pasarles el contexto (Tema 7), y conviene usarlos para salida verbosa, herramientas restringidas o tareas autocontenidas, no para ida y vuelta (Tema 8).

**Plan mode** va cuando hay muchos archivos, arquitectura o varios enfoques válidos; la **ejecución directa**, para cambios chicos y claros (Tema 9). En tareas grandes se combinan: plan para investigar, directa para implementar, Explore para el descubrimiento verboso (Tema 10). Para mejorar un resultado: **ejemplos de entrada y salida** cuando la prosa se interpreta distinto (Tema 11), **tests primero** y compartir los fallos (Tema 12), **entrevista** en un dominio desconocido (Tema 13), y los problemas que interactúan **en un solo mensaje** (Tema 14).

## Lo que viene

**3D · Udemy 12 — Hooks, SDK & CI/CD:** cómo correr Claude Code sin una persona delante (modo no interactivo, `-p`), integrarlo en un pipeline de CI/CD (tarea 3.6) y usar hooks para automatizar lo que tiene que pasar siempre.

---

## Las trampas del examen

Cada trampa tiene el mismo orden: la situación, **qué elegir en el examen (✅)**, las opciones que tientan (❌) con por qué tientan y por qué están mal, y una regla para recordar.

### Grupo: Comandos y skills

#### Trampa 1 · El comando de todo el equipo (Q4)

**La situación.** Un `/review` con el checklist del equipo tiene que estar disponible para todos apenas clonan el repo (Tema 1).

**✅ En el examen elegí:** **`.claude/commands/` dentro del repo**.

**❌ Las que tientan:**

❌ **"En `~/.claude/commands/` de cada desarrollador".**
- *Tienta porque:* también crea un `/review`.
- *Está mal porque:* es personal y no viaja por git; cada uno tendría que crearlo a mano.

❌ **"En el CLAUDE.md del proyecto".**
- *Tienta porque:* CLAUDE.md sí se comparte.
- *Está mal porque:* CLAUDE.md es para instrucciones y contexto, no para definir comandos.

❌ **"En `.claude/config.json` con un array `commands`".**
- *Tienta porque:* suena a configuración formal.
- *Está mal porque:* ese mecanismo no existe.

> 🧠 **Para recordar:** comando del equipo = `.claude/commands/` en el repo.

#### Trampa 2 · La skill que llena el contexto

**La situación.** Una skill de análisis del codebase deja cientos de líneas de salida en la conversación y la sesión empieza a funcionar peor (Tema 3).

**✅ En el examen elegí:** **`context: fork`** en el frontmatter de la skill.

**❌ Las que tientan:**

❌ **"Correr la skill en una sesión nueva cada vez".**
- *Tienta porque:* también evita ensuciar la conversación.
- *Está mal porque:* es un parche manual; la guía da un mecanismo específico: `context: fork`.

❌ **"Agregarle `allowed-tools` con menos herramientas".**
- *Tienta porque:* es otro campo de la misma lista de la guía.
- *Está mal porque:* `allowed-tools` limita **qué hace** la skill, no **dónde queda su salida**.

> 🧠 **Para recordar:** salida verbosa o exploratoria → `context: fork`.

#### Trampa 3 · La skill que no debería poder borrar nada

**La situación.** Una skill genera archivos de migración y el equipo quiere que no pueda ejecutar comandos destructivos (Tema 4).

**✅ En el examen elegí:** **`allowed-tools`** limitado a las operaciones que necesita (leer y escribir archivos).

**❌ Las que tientan:**

❌ **"Escribir en el cuerpo de la skill 'no ejecutes comandos'".**
- *Tienta porque:* es directo.
- *Está mal porque:* es una instrucción, no una restricción de herramientas.

❌ **"`context: fork` para aislarla".**
- *Tienta porque:* "aislar" suena a "proteger".
- *Está mal porque:* aísla el contexto, no limita las herramientas.

> 🧠 **Para recordar:** limitar herramientas de una skill → `allowed-tools` (según la guía).

#### Trampa 4 · Mi versión del `/review` del equipo

**La situación.** Lucas quiere un `/review` que además le explique cada problema en detalle, sin afectar a nadie (Tema 5).

**✅ En el examen elegí:** **una skill en `~/.claude/skills/` con otro nombre** (por ejemplo `review-detallado`).

**❌ Las que tientan:**

❌ **"Una skill personal que también se llame `review`".**
- *Tienta porque:* así "reemplaza" la del equipo solo para él.
- *Está mal porque:* en su máquina tapa a la del equipo y deja de ver los cambios que haga el equipo; la guía pide otro nombre.

❌ **"Editar la skill del repo y agregarle sus explicaciones".**
- *Tienta porque:* es lo más rápido.
- *Está mal porque:* afecta a todo el equipo.

> 🧠 **Para recordar:** personal + otro nombre + `~/.claude/skills/`.

#### Trampa 5 · Una skill que "se dispara sola" con un evento

**La situación.** Una opción propone una skill con un campo `trigger` que se ejecuta automáticamente cuando termina el build (Tema 2).

**✅ En el examen elegí:** lo que reacciona a eventos es un **hook**. Las skills se activan cuando las llamás o cuando Claude las elige por su `description`.

**❌ Las que tientan:**

❌ **"Una skill con `trigger: build-complete`".**
- *Tienta porque:* lo dice el companion del curso.
- *Está mal porque:* el campo `trigger` no existe.

> 🧠 **Para recordar:** eventos → hooks; skills → a demanda.

#### Trampa 6 · El procedimiento de release en CLAUDE.md

**La situación.** El CLAUDE.md tiene 80 líneas sobre cómo hacer un release, que se usa dos veces por mes (Tema 6).

**✅ En el examen elegí:** **moverlo a una skill** (a demanda) y dejar en CLAUDE.md solo lo que aplica siempre.

**❌ Las que tientan:**

❌ **"Dejarlo en CLAUDE.md para que Claude siempre lo tenga a mano".**
- *Tienta porque:* "más contexto = mejor".
- *Está mal porque:* ocupa contexto en todas las sesiones y baja la adherencia al resto del CLAUDE.md.

> 🧠 **Para recordar:** siempre → CLAUDE.md; a veces → skill.

### Grupo: Subagentes

#### Trampa 7 · El revisor que terminó editando código

**La situación.** Un subagente revisor en `.claude/agents/` no tiene el campo `tools` y a veces "arregla" cosas en lugar de solo reportarlas (Tema 7).

**✅ En el examen elegí:** **definir `tools: Read, Grep, Glob`** en su frontmatter.

**❌ Las que tientan:**

❌ **"Agregar a su system prompt 'nunca edites archivos'".**
- *Tienta porque:* es lo más simple.
- *Está mal porque:* es un pedido que el modelo puede no cumplir; `tools` lo garantiza.

> 🧠 **Para recordar:** sin `tools`, hereda todas.

#### Trampa 8 · El subagente que "no sabía" lo que habíamos hablado

**La situación.** Después de una hora definiendo con Claude cómo funciona el descuento, se delega la implementación a un subagente y la hace mal (Temas 7 y 8).

**✅ En el examen elegí:** **pasarle explícitamente al subagente el contexto que necesita** (o hacer esa tarea en la conversación principal, si requiere mucho ida y vuelta).

**❌ Las que tientan:**

❌ **"El subagente ve la conversación del padre, así que el problema es otro".**
- *Tienta porque:* parece lógico que lo "herede".
- *Está mal porque:* no ve tu historial; solo recibe el mensaje de delegación.

> 🧠 **Para recordar:** lo que no le pasás, el subagente no lo sabe.

### Grupo: Plan mode

#### Trampa 9 · La migración de 45 archivos

**La situación.** Hay que migrar una librería que se usa en 45 archivos (Tema 9).

**✅ En el examen elegí:** **plan mode** para investigar y diseñar, y después **ejecución directa** para implementar.

**❌ Las que tientan:**

❌ **"Ejecución directa con instrucciones muy detalladas".**
- *Tienta porque:* "si le explico todo, no hace falta planificar".
- *Está mal porque:* supone que ya conocés todas las dependencias sin haber explorado.

❌ **"Ejecución directa y pasar a plan mode si aparece algo raro".**
- *Tienta porque:* parece pragmático.
- *Está mal porque:* la complejidad ya está en el enunciado (Q5).

> 🧠 **Para recordar:** multi-archivo o arquitectura → plan primero.

#### Trampa 10 · Plan mode para un bug con stack trace

**La situación.** Un bug en un solo archivo, con el stack trace que marca la línea del error (Tema 9).

**✅ En el examen elegí:** **ejecución directa**.

**❌ Las que tientan:**

❌ **"Plan mode siempre, por seguridad".**
- *Tienta porque:* planificar parece lo prudente.
- *Está mal porque:* para un cambio chico y claro es un paso de más; la guía da este caso como ejemplo de ejecución directa.

> 🧠 **Para recordar:** un archivo, alcance claro → directo.

### Grupo: Refinamiento iterativo

#### Trampa 11 · La prosa que Claude interpreta distinto

**La situación.** Describiste cómo normalizar los nombres de productos y cada corrida sale distinta (Tema 11).

**✅ En el examen elegí:** **2–3 ejemplos concretos de entrada y salida**.

**❌ Las que tientan:**

❌ **"Reescribir la descripción más larga y precisa".**
- *Tienta porque:* "si explico mejor, entiende".
- *Está mal porque:* sigue siendo prosa con varias lecturas posibles.

❌ **"Usar el interview pattern".**
- *Tienta porque:* también es una técnica de la guía.
- *Está mal porque:* sirve para descubrir consideraciones en un dominio desconocido; acá ya sabés qué querés, solo falta mostrarlo.

> 🧠 **Para recordar:** inconsistente → ejemplos de entrada y salida.

#### Trampa 12 · Dos problemas que se afectan

**La situación.** El cálculo de envío y el cupón de envío gratis están mal, y uno depende del otro (Tema 14).

**✅ En el examen elegí:** **un solo mensaje detallado** con los dos problemas y cómo se relacionan.

**❌ Las que tientan:**

❌ **"De a uno, para que cada corrección sea más simple".**
- *Tienta porque:* es lo recomendable para problemas independientes.
- *Está mal porque:* acá interactúan: el segundo arreglo puede romper el primero.

> 🧠 **Para recordar:** interactúan → juntos; independientes → de a uno.

#### Trampa 13 · Una caché en un dominio que no conocés

**La situación.** Lucas tiene que agregar una caché al catálogo y nunca trabajó con cachés (Tema 13).

**✅ En el examen elegí:** **el interview pattern**: pedirle a Claude que lo entreviste para descubrir consideraciones (invalidación, modos de falla) antes de implementar.

**❌ Las que tientan:**

❌ **"Escribir él mismo una especificación en prosa y pasársela".**
- *Tienta porque:* parece lo más ordenado.
- *Está mal porque:* en un dominio que no conoce, su especificación va a omitir justo lo que no sabe que tiene que considerar.

> 🧠 **Para recordar:** dominio desconocido → que Claude te pregunte primero.

#### Trampa 14 · Implementar y testear al final

**La situación.** Hay que implementar `calcularEnvio` con varios casos borde y un requisito de rendimiento, y mejorarlo de forma progresiva (Tema 12).

**✅ En el examen elegí:** **escribir primero los tests** (comportamiento esperado, casos borde, rendimiento) e iterar compartiendo los fallos.

**❌ Las que tientan:**

❌ **"Que Claude implemente y después escriba tests para lo que hizo".**
- *Tienta porque:* es el orden habitual.
- *Está mal porque:* los tests terminan validando lo que el código ya hace, no lo que tenía que hacer; se pierde el criterio objetivo para iterar.

> 🧠 **Para recordar:** tests primero, fallos como feedback.

---

## Checklist oficial

**Tarea 3.2 — Create and configure custom slash commands and skills**

*Knowledge of*
- [x] Comandos de proyecto en `.claude/commands/` (compartidos por git) vs. de usuario en `~/.claude/commands/` (personales) → **Tema 1** (Trampa 1)
- [x] Skills en `.claude/skills/` con `SKILL.md` y frontmatter: `context: fork`, `allowed-tools`, `argument-hint` → **Temas 2, 3 y 4**
- [x] `context: fork` para correr una skill en un subagente aislado y no contaminar la conversación principal → **Tema 3** (Trampa 2)
- [x] Variantes personales en `~/.claude/skills/` con otro nombre para no afectar al equipo → **Tema 5** (Trampa 4)

*Skills in*
- [x] Crear comandos de proyecto en `.claude/commands/` para todo el equipo → **Tema 1** (Trampa 1)
- [x] Usar `context: fork` para aislar skills con salida verbosa (análisis del codebase) o exploratoria (brainstorming) → **Tema 3** (Trampa 2)
- [x] Configurar `allowed-tools` para restringir las herramientas de la skill (solo escritura de archivos, sin acciones destructivas) → **Tema 4** (Trampa 3)
- [x] Usar `argument-hint` para pedir los parámetros cuando se invoca sin argumentos → **Tema 4**
- [x] Elegir entre skills (a demanda, tareas puntuales) y CLAUDE.md (estándares universales, siempre cargados) → **Tema 6** (Trampa 6)

**Tarea 3.4 — Determine when to use plan mode vs direct execution**

*Knowledge of*
- [x] Plan mode para tareas complejas: cambios a gran escala, varios enfoques válidos, decisiones de arquitectura, varios archivos → **Tema 9** (Trampa 9)
- [x] Ejecución directa para cambios simples y acotados (una validación en una función) → **Tema 9** (Trampa 10)
- [x] Plan mode permite explorar y diseñar antes de comprometerse con cambios, evitando retrabajo costoso → **Tema 9**
- [x] El Explore subagent para aislar el descubrimiento verboso y devolver resúmenes → **Tema 10** (y 3A)

*Skills in*
- [x] Plan mode para tareas con implicancias de arquitectura (microservicios, migraciones de 45+ archivos, elegir entre integraciones) → **Tema 9** (Trampa 9)
- [x] Ejecución directa para cambios con alcance claro (bug de un archivo con stack trace, una validación de fecha) → **Tema 9** (Trampa 10)
- [x] Explore subagent en fases de descubrimiento verbosas para no agotar el contexto → **Tema 10**
- [x] Combinar plan mode para investigar y ejecución directa para implementar → **Tema 10** (Trampa 9)

**Tarea 3.5 — Apply iterative refinement techniques for progressive improvement**

*Knowledge of*
- [x] Ejemplos concretos de entrada y salida como lo más efectivo cuando la prosa se interpreta de forma inconsistente → **Tema 11** (Trampa 11)
- [x] Test-driven iteration: tests primero, iterar compartiendo los fallos → **Tema 12**
- [x] Interview pattern: que Claude pregunte para hacer surgir consideraciones antes de implementar → **Tema 13**
- [x] Cuándo dar todos los problemas en un mensaje (interactúan) y cuándo de a uno (independientes) → **Tema 14** (Trampa 12)

*Skills in*
- [x] Dar 2–3 ejemplos concretos de entrada y salida cuando la descripción da resultados inconsistentes → **Tema 11** (Trampa 11)
- [x] Escribir tests del comportamiento esperado, casos borde y rendimiento antes de implementar, e iterar con los fallos → **Tema 12**
- [x] Usar el interview pattern para descubrir consideraciones de diseño (invalidación de caché, modos de falla) en dominios desconocidos → **Tema 13**
- [x] Dar casos de prueba específicos con entrada y salida esperada para arreglar casos borde (nulos en una migración) → **Tema 11**
- [x] Resolver varios problemas que interactúan en un solo mensaje detallado, y los independientes de a uno → **Tema 14** (Trampa 12)

**De la documentación, no de la guía** (vale saberlo; la guía no lo pregunta directo): fusión de comandos y skills, `disable-model-invocation`, carga por `description` (Temas 1–2) · prioridad personal/proyecto en skills y al revés en subagentes (Temas 5 y 7) · frontmatter de subagentes y qué cargan (Tema 7) · `Ctrl+G`, "keep planning", `/clear` tras dos correcciones (Temas 10 y 14).

**📘 Curso (útil para entender):** las tres preguntas antes de delegar y la salida estructurada (Tema 8) · editar el plan suele ser más rápido que rehacerlo (Tema 10).

---

## Autoevaluación oral

1. ¿Dónde creás un comando que tiene que tener todo el equipo al clonar el repo? ¿Por qué no en CLAUDE.md ni en tu carpeta personal?
2. Explicá qué hacen `context: fork`, `allowed-tools` y `argument-hint`, con un ejemplo de cada uno. ¿Qué dice la guía y qué dice la documentación de los dos últimos?
3. Querés tu versión del `/review` del equipo. ¿Dónde va y por qué con otro nombre? ¿Cómo decidís entre CLAUDE.md, rules, skill y subagente?
4. ¿Cuándo usás plan mode y cuándo ejecución directa? Dame un ejemplo de cada uno y explicá cómo se combinan en una migración grande.
5. Nombrá las cuatro técnicas de refinamiento iterativo de la guía y en qué situación usás cada una.

---

## Preguntas tipo examen

Las preguntas tipo examen de este capítulo están en [`04-practica/modulo-3.md`](../04-practica/modulo-3.md), junto con las del resto del módulo 3. Hacelas cuando termines **todos** los capítulos del módulo, de a una y sin mirar la respuesta.

---

## Revisión contra el blueprint oficial

Qué puede salir en el examen de 3.2, 3.4 y 3.5 que el curso de Jacob **no cubre o cubre flojo**, y dónde quedó explicado:

1. **Los tres campos de skills que nombra la guía** (`context: fork`, `allowed-tools`, `argument-hint`). Las slides los nombran, pero no explican qué hace `context: fork` y describen `allowed-tools` distinto de la guía. → Temas 3 y 4.
2. **Variantes personales con otro nombre.** No está en el curso. → Tema 5.
3. **Skill vs. CLAUDE.md** como "a demanda" vs. "siempre cargado". → Tema 6.
4. **Toda la tarea 3.5.** El curso no enseña ninguna de las cuatro técnicas: su lección de "iterar" es sobre editar el plan. → Temas 11–14.
5. **Plan + ejecución combinados y el Explore subagent dentro de 3.4.** → Tema 10.
6. **Datos del curso que están mal:** el campo `trigger` y las skills "por eventos" (Tema 2); `/agents` para lanzar subagentes y el "contexto completamente vacío" (Tema 7).

No encontré otros huecos para estas tres tareas.

