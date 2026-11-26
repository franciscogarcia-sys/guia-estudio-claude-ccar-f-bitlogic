# Capítulo 8 · 3A · Udemy 9 — Claude Code Fundamentals (fundamentos de Claude Code)

*Tarea oficial 3.1 (base; se completa en 3B) · Primer capítulo del módulo 3*

---

## Dónde estamos

Empieza el **módulo 3: Claude Code Configuration & Workflows** (20% del examen, 6 tareas de 3,33% cada una). Este capítulo arma la base de:
- **3.1** Configure CLAUDE.md files with appropriate hierarchy, scoping, and modular organization (configurar los archivos CLAUDE.md con la jerarquía, el alcance y la organización modular adecuados).

También presenta piezas que la guía evalúa en otras tareas del módulo: **plan mode (modo plan)** y el **Explore subagent (subagente de exploración)** (3.4), y **`/compact`** (5.4). Acá van a nivel introductorio.

### Cómo leer este capítulo

Todo lo que leés acá **vale para el examen**, salvo que diga lo contrario. Cuando algo sale solo del curso (útil para entender, pero no central), lo marco con **📘 Curso**. Cuando Jacob dice algo distinto de lo que evalúa la guía, aparece un recuadro así:

> ⚠️ **En el curso vas a escuchar otra cosa.** … **Para el examen: …**

### Un aviso sobre este capítulo

El bloque 3A del curso explica bien qué es Claude Code, `/init` y el manejo del contexto. Pero **no menciona `/memory`, los imports con `@` ni `.claude/rules/`**, que son 3 de los 4 puntos de conocimiento de 3.1 (el curso los deja para 3B); esas partes salen de la guía oficial y de la documentación. Además, el curso tiene **varios datos equivocados**. Los tres que más pueden costarte una pregunta son `.claudeignore`, el orden entre hooks y permisos, y "sin CLAUDE.md no hay memoria". Cada uno aparece en un recuadro ⚠️ en su tema.

## De dónde venimos

En **1D** viste los **hooks** (`PreToolUse`, `PostToolUse`): código que se ejecuta antes o después de una tool y que **garantiza** reglas, porque no depende de que el modelo obedezca. En **1C** viste los **subagentes**, que trabajan en su propio contexto y devuelven un resumen, y también `--resume` y las sesiones con nombre. En **2C** viste las **built-in tools** (herramientas incorporadas) de Claude Code (Read, Write, Edit, Bash, Grep, Glob) y cómo explorar un código de a poco.

Hasta acá Claude Code aparecía como "el lugar donde corren las tools". Ahora lo miramos como **producto**: cómo funciona, cómo se le enseña tu proyecto (CLAUDE.md), cómo se maneja su memoria de trabajo (el contexto) y qué puede hacer sin pedirte permiso.

## Mapa del capítulo

**Parte 1 — Qué es Claude Code.**
1. What Claude Code is (qué es Claude Code): un agente, no un chat.
2. El loop de Claude Code, las sesiones y qué se puede deshacer.
3. El tool system (sistema de tools): qué tool para qué.

**Parte 2 — Enseñarle tu proyecto: CLAUDE.md (base de la tarea 3.1).**

4. CLAUDE.md: standing context (contexto permanente), no reglas que se imponen.
5. Los niveles de CLAUDE.md: user, project y directory.
6. Onboarding (puesta en marcha): arrancar desde la raíz y `/init`.
7. Modularizar: imports con `@` y `.claude/rules/`.
8. `/memory`: ver qué archivos cargó Claude.

**Parte 3 — El contexto.**

9. Context window (ventana de contexto): un presupuesto finito.
10. `/compact`, `/clear` y `/context`.
11. Excluir archivos: reglas `Read` deny, no `.claudeignore`.

**Parte 4 — Permisos y modos de trabajo.**

12. El modelo de permisos: settings, deny/allow y hooks.
13. Permission modes (modos de permiso).
14. Plan mode (modo plan) vs. direct execution (ejecución directa) y el Explore subagent (introducción).

---

# Parte 1 — Qué es Claude Code

## Tema 1 — What Claude Code is (qué es Claude Code): un agente, no un chat

### Qué es

**Claude Code** es la herramienta de Anthropic para programar con Claude. Corre en tu terminal, y también en el IDE, la web y la app de escritorio. Lo que lo distingue es que es **agentic** (agéntico): no te sugiere código para que lo copies, sino que **lee tu proyecto, ejecuta comandos, edita archivos y verifica** el resultado, encadenando decenas de pasos sin que tengas que intervenir en cada uno.

Para hacer eso, Claude Code ve mucho más que un archivo suelto: el proyecto entero, la terminal, el estado de git, tus archivos CLAUDE.md (Tema 4) y sus extensiones, como los servidores MCP (2B), las skills (3C) y los subagentes (1C).

📘 **Curso:** para que se vea la diferencia, el curso lo compara con dos herramientas conocidas. Un **chat** responde con texto y vos ejecutás lo que te dice. Un **plugin de autocompletado del IDE** ve solo el archivo que tenés abierto, sugiere líneas y no tiene acceso a la terminal. Claude Code no se parece a ninguno de los dos: hace el trabajo.

### Ejemplo

Le pedís a Claude Code: "El test `calcularEnvio` falla, arreglalo".
- **Un chat** te explicaría cuál puede ser el error, y vos tendrías que buscarlo y corregirlo.
- **Claude Code** corre el test, lee el error, busca la función, la corrige, vuelve a correr el test y te muestra que ahora pasa.

### Para el examen

- Claude Code = **agente con tools**. Las preguntas del dominio 3 suponen que **actúa** sobre el repo; lo que se discute es **cómo configurarlo** para que actúe bien.

### Cómo se une

Que "actúe" quiere decir que corre un loop: el mismo de 1A, envuelto en un producto.

---

## Tema 2 — El loop de Claude Code, las sesiones y qué se puede deshacer

### Qué es

**El loop.** Claude Code trabaja en un ciclo que la documentación describe en tres fases: **gather context** (juntar contexto: leer archivos, buscar), **take action** (actuar: editar, correr comandos) y **verify results** (verificar: correr los tests, mirar la salida). Las fases no van en un orden rígido, sino que se mezclan: cada paso decide el siguiente según lo que Claude aprendió en el anterior. Vos podés interrumpir en cualquier momento.

Es el **agentic loop** (loop agéntico) de 1A: el modelo razona, pide una tool, Claude Code la ejecuta y le devuelve el resultado, y así hasta terminar. A todo lo que rodea al modelo para que eso funcione (las tools, los permisos, el manejo del contexto) la documentación lo llama **agentic harness** (el arnés agéntico).

📘 **Curso:** el curso lo llama **"planning loop"** y le pone cuatro fases: plan, tool call, observe y repeat. Termina cuando la tarea está completa **o cuando Claude necesita una aclaración**. Es la misma idea con otros nombres; la guía no pregunta por los nombres de las fases.

**Las sesiones son independientes.** Una **sesión** es una conversación con Claude Code, desde que lo abrís hasta que lo cerrás o la vaciás. Todo lo que Claude tiene a la vista durante esa conversación (lo que hablaron, los archivos que leyó, la salida de los comandos) es su **contexto** (Tema 9). Cuando abrís una sesión nueva, ese contexto arranca de cero: Claude no recuerda lo que hablaron ayer. La documentación lo dice así: *"Each new session starts with a fresh context window, without the conversation history from previous sessions."*

Hay dos cosas que sí persisten entre sesiones, y la diferencia está en quién las escribe:
- **CLAUDE.md**: lo escribís **vos**, con instrucciones y reglas del proyecto.
- **Auto memory** (memoria automática): la escribe **Claude**, con cosas que aprendió trabajando. Se guarda en un archivo `MEMORY.md`, por máquina.

> ⚠️ **En el curso vas a escuchar otra cosa.** El companion dice que *"Claude Code has no persistent memory across sessions without [CLAUDE.md]"*, o sea, que sin CLAUDE.md no queda nada. Está desactualizado: hoy existe auto memory, y las propias slides del curso la muestran. **Para el examen: las sesiones no recuerdan la conversación anterior, y CLAUDE.md es la memoria persistente que controlás vos.**

**Qué se puede deshacer.** Antes de editar un archivo con sus tools, Claude Code guarda una copia. Esa copia es un **checkpoint** (punto de restauración; no es el checkpoint de estado de 1C). Si no te gusta lo que hizo, con `Esc` `Esc` (o `/rewind`) volvés atrás. Pero el checkpoint solo cubre lo que pasó por las tools de edición, así que hay dos cosas que no se recuperan:
- Un archivo que **solo tocó Bash** (por ejemplo, con un `rm` o un `sed`).
- Las acciones sobre sistemas remotos (una base de datos, una API, un deploy).

📘 **Curso:** por eso el curso dice que **Bash es la tool más poderosa y la más peligrosa**: puede hacer cualquier cosa y no tiene un límite propio ni un undo. Lo que la controla son los **permisos y los hooks** (Temas 12 y 13).

### Ejemplo

El lunes, en una sesión, le explicaste a Claude que en TiendaX los montos se guardan en centavos. El martes abrís una sesión nueva y vuelve a tratarlos como pesos. **No es un bug:** la sesión del martes no sabe nada de la del lunes. Si es una regla del proyecto que tiene que valer siempre, va en el **CLAUDE.md** (Tema 4), que se carga en cada sesión.

### Para el examen

- Sesión nueva = contexto vacío (salvo CLAUDE.md y auto memory). Lo que se repite en cada sesión → CLAUDE.md.
- Ediciones con tools → reversibles. Bash y acciones remotas → no.

### Cómo se une

El loop usa tools. Ya las conocés de 2C; acá va el repaso rápido desde el lado del producto.

---

## Tema 3 — El tool system (sistema de tools): qué tool para qué

### Qué es

Sin tools, Claude solo puede responder texto. Las tools son las que le permiten leer, buscar, editar y ejecutar, y Claude Code trae un conjunto que se agrupa en cinco familias: operaciones de archivo, búsqueda, ejecución, web e inteligencia de código.

Para el examen importa saber **cuál elegir para cada necesidad**, porque varias se parecen. Grep y Glob, por ejemplo, las dos "buscan", pero una busca **dentro** de los archivos y la otra busca **nombres** de archivos. Edit y Write, las dos "escriben", pero Edit cambia líneas puntuales y Write reemplaza el archivo entero, así que lo que no pongas en el contenido nuevo se pierde.

La tabla resume la selección (es la tabla de la lección 53 del curso, completada con 2C):

| Necesidad | Tool |
|---|---|
| Ver el contenido de un archivo | **Read** (la más segura: solo lee; también imágenes, PDFs y notebooks) |
| Encontrar archivos por nombre | **Glob** |
| Encontrar texto dentro de los archivos | **Grep** |
| Cambiar líneas puntuales de un archivo que existe | **Edit** (la opción por defecto para código) |
| Crear un archivo o reescribirlo entero | **Write** (*"No partial update"*: lo que no esté en el contenido nuevo se pierde) |
| Correr tests, build, git, listar una carpeta (`ls`) | **Bash** |
| Información actual de la web | **WebSearch** / **WebFetch** |
| Una subtarea aislada, con su propio contexto | **Agent** (lanza un subagente) |

La **Agent tool** merece una explicación aparte. Cuando Claude la usa, crea un subagente con **su propio context window**: un Claude aparte que hace la subtarea sin llenar la conversación principal y devuelve solo el resultado. Es lo que viste en 1C, ahora como una tool más de Claude Code.

> ⚠️ **En el curso vas a escuchar otra cosa.** El glosario dice que el tool system es "Read, Write, Edit, Bash, WebSearch, and Agent", **sin Grep ni Glob**; las slides sí los incluyen, pero no explican en qué se diferencian. **Para el examen: Grep busca en el contenido y Glob busca por nombre de archivo**, que es la regla de la guía que viste en 2C.

### Ejemplo

En el repo de TiendaX:
- "¿Dónde se usa `priceCents`?": Claude usa **Grep**.
- "¿Qué archivos `*.test.tsx` hay?": Claude usa **Glob**.
- "Cambiá el texto del botón en `Checkout.tsx`": Claude usa **Edit**.
- "Corré `npm test`": Claude usa **Bash**.
- "Antes de tocar nada, investigá cómo se calculan los impuestos en todo el repo": Claude usa **Agent** (un subagente explora y devuelve un resumen).

### Para el examen

- Todo lo de 2C sigue valiendo (Grep vs. Glob, Edit vs. Write, Read + Write cuando Edit falla, exploración incremental).
- **Agent** = delegar en un subagente para no llenar el contexto principal.

### Cómo se une

Claude Code ya sabe *usar* tools. Lo que no sabe es **cómo es tu proyecto**: qué comando corre los tests, qué convenciones tienen, qué no tiene que tocar. Para eso está CLAUDE.md.

---

# Parte 2 — Enseñarle tu proyecto: CLAUDE.md

## Tema 4 — CLAUDE.md: standing context (contexto permanente), no reglas que se imponen

### Qué es

**CLAUDE.md** es un archivo Markdown con instrucciones sobre tu proyecto que Claude Code **carga al empezar cada sesión**. Como cada sesión arranca sin recordar las anteriores (Tema 2), CLAUDE.md es la forma de que Claude sepa siempre lo básico: cómo se corren los tests, qué convenciones usa el equipo, qué no se toca. 📘 El curso lo define muy bien como *"standing context, not a per-session briefing"*: contexto permanente, no un resumen que armás para una sola sesión.

Lo más importante para el examen es que CLAUDE.md **es contexto, no una configuración que se impone**. Claude Code lo entrega como un mensaje más, después del system prompt, y Claude lo tiene en cuenta igual que cualquier otra instrucción: lo sigue casi siempre, pero nada lo obliga. La documentación lo dice dos veces: *"Claude treats them as context, not enforced configuration"* y *"Instructions in your prompt or CLAUDE.md shape what Claude tries to do, but they don't change what Claude Code allows."*

En la práctica, CLAUDE.md **guía** a Claude, pero **no garantiza nada**. Si una regla **tiene** que cumplirse siempre (no leer `.env`, no hacer push a `main`), va en un **hook** o en una **regla de permiso** (Tema 12), que Claude Code aplica sin importar lo que el modelo decida. Es exactamente el criterio de 1D: lo probabilístico (instrucciones) contra lo determinístico (hooks y permisos).

### Qué poner y qué no

El criterio general es poner lo que Claude **no puede descubrir solo** leyendo el código, y dejar afuera lo que ya ve o lo que no le cambia nada. 📘 El curso lo resume así: incluí lo que **cambia lo que Claude haría** sin esa información; omití lo que no cambiaría nada.

**Sí va:**
- Comandos que Claude no puede adivinar: cómo correr tests, lint, build.
- Convenciones del equipo: "Los montos van en centavos (`int`)", "Usar 2 espacios".
- Decisiones que **no están en el código**: "No usar la librería X por un tema de licencias".
- Trampas del código: "`legacy/` no se toca: lo usa el sistema de facturación".
- Lo que ya tuviste que corregirle dos veces (*"Anything you've had to correct twice already"*).

**No va:**
- La descripción de toda la arquitectura y la estructura de carpetas, porque Claude ya la ve explorando (*"Claude reads the repo itself"*).
- Instrucciones vagas como "Escribí buen código", porque no le dicen qué hacer. Mejor específicas: *"Use 2-space indentation" instead of "Format code properly"*.
- Secretos o API keys, porque el archivo se commitea y lo ve todo el que tenga el repo.

**Largo.** La documentación recomienda **menos de 200 líneas** por archivo. El motivo es que todo CLAUDE.md ocupa contexto en cada sesión, y un archivo largo se respeta **peor**: *"Longer files consume more context and reduce adherence"*. Además, si dos reglas se contradicen, Claude no sabe cuál vale y *"may pick one arbitrarily"* (puede elegir cualquiera de las dos).

> ⚠️ **En el curso vas a escuchar otra cosa.** El curso pone *"architecture decisions"* entre lo que hay que incluir. La documentación dice que no hace falta describir la arquitectura ni las carpetas, porque Claude las lee del repo; sí van las decisiones **que no están en el repo** (por qué se eligió algo, qué no se puede usar). **Para el examen: un CLAUDE.md de proyecto conciso, con convenciones, comandos y restricciones del equipo.**

### Ejemplo

`CLAUDE.md` del repo `storefront` de TiendaX:

```markdown
# TiendaX storefront

## Comandos
- Tests: `npm test -- --runInBand`
- Lint: `npm run lint` (correr antes de cada commit)

## Convenciones
- Montos de dinero: enteros en centavos (`priceCents`), nunca float.
- Componentes React: funcionales, con hooks; nada de clases.
- Fechas: siempre UTC en la base; convertir a America/Cordoba solo en la UI.

## No tocar
- `src/legacy/` lo usa facturación: cualquier cambio pasa por el equipo de billing.
```

### Para el examen

- CLAUDE.md = **instrucciones de proyecto y contexto**. No define comandos (Q4 de la guía) ni impone reglas.
- "Ponerlo en mayúsculas / IMPORTANT en CLAUDE.md" para algo crítico → no alcanza (*"adding IMPORTANT probably won't fix it"*). Si tiene que pasar siempre → **hook o permiso**.

### Cómo se une

Hay más de un CLAUDE.md posible: el tuyo, el del equipo y el de una carpeta. La guía evalúa directamente **en cuál va cada cosa**.

---

## Tema 5 — Los niveles de CLAUDE.md: user, project y directory

### Qué es

No hay un solo CLAUDE.md: puede haber uno tuyo, uno del equipo y uno por carpeta. La diferencia entre ellos es **a quién le llega**, y eso depende de dónde está el archivo. Si está en tu carpeta personal, solo lo ves vos. Si está dentro del repo, viaja por git y lo tiene todo el que clone el proyecto.

La guía define una **jerarquía de tres niveles**:
- **User-level** (de usuario): `~/.claude/CLAUDE.md`, en tu carpeta personal. Sirve para tus preferencias, y se aplica en **todos** tus proyectos.
- **Project-level** (de proyecto): `CLAUDE.md` en la raíz del repo (o `.claude/CLAUDE.md`). Sirve para las convenciones del **equipo**.
- **Directory-level** (de carpeta): un `CLAUDE.md` dentro de una subcarpeta, con reglas de **esa parte** del código.

La frase clave de la guía es que lo que está en tu `~/.claude/CLAUDE.md` no les llega a tus compañeros por git: *"instructions in ~/.claude/CLAUDE.md are not shared with teammates via version control"*. Es la causa de un problema muy típico (ver el ejemplo).

| Nivel | Dónde | Para qué | ¿Lo recibe el equipo? |
|---|---|---|---|
| **User-level** | `~/.claude/CLAUDE.md` | Tus preferencias, en todos tus proyectos | **No** |
| **Project-level** | `CLAUDE.md` en la raíz o `.claude/CLAUDE.md` | Convenciones del equipo | **Sí**, por git |
| **Directory-level** | `CLAUDE.md` en una subcarpeta | Reglas de esa parte del código | Sí, por git |

**Lo que agrega la documentación.** Hay dos niveles más que la guía no nombra, y dos detalles de cómo se cargan:
- **Managed policy** (política administrada): un CLAUDE.md que pone la organización (IT o DevOps) para todos sus usuarios.
- **`CLAUDE.local.md`**: un archivo en la raíz del proyecto que es **personal para ese proyecto**. Se agrega a `.gitignore` para que no viaje por git.
- **Cómo se cargan:** Claude Code **sube por las carpetas** desde donde lo arrancaste y carga los CLAUDE.md que encuentra en el camino. Los de subcarpetas no se cargan al principio, sino **cuando Claude lee archivos de esa subcarpeta**.
- **No se pisan: se suman.** Todos los que encuentra se juntan en el contexto, en vez de reemplazarse: *"All discovered files are concatenated into context rather than overriding each other."*

(El orden exacto de carga y qué pasa cuando dos niveles se contradicen se ven en **3B**.)

> ⚠️ **En el curso vas a escuchar otra cosa.** El glosario habla de un nivel **"team-level"** y de un sistema de **"precedence"** (precedencia) entre niveles, y llama "path-specific rules" a un CLAUDE.md por subcarpeta. **Para el examen: los niveles son user, project y directory.** El del equipo es el project-level commiteado, los CLAUDE.md se concatenan (no hay uno que "gane"), y las **path-specific rules** son los archivos de **`.claude/rules/` con `paths:`** (Tema 7 y 3B), no un CLAUDE.md de subcarpeta.

### Ejemplo: el caso típico de la guía

Sofía entra al equipo de TiendaX. Clona el repo, abre Claude Code y Claude **no respeta las convenciones de montos en centavos**, que a vos sí te respeta siempre.

- **Causa:** las convenciones están en **tu** `~/.claude/CLAUDE.md` (user-level). Ese archivo vive en tu máquina y nunca le llegó a Sofía.
- **Solución:** moverlas al **`CLAUDE.md` del proyecto** y commitearlo, para que viajen con el repo.

Es literalmente la Skill 1 de la guía: *"a new team member not receiving instructions because they're in user-level rather than project-level configuration"*.

### Para el examen

- "Un compañero no recibe las instrucciones que yo sí veo" → están en **user-level**; pasarlas al **project-level**.
- Preferencias personales (tu estilo de explicaciones, tu editor) → `~/.claude/CLAUDE.md` (todos tus proyectos) o `CLAUDE.local.md` (solo este proyecto). **Nunca** en el CLAUDE.md compartido.
- Es el mismo razonamiento de la Q4 de la guía (`.claude/commands/` vs. `~/.claude/commands/`) y del `.mcp.json` vs. `~/.claude.json` de 2B: **en el repo = equipo; en tu home = personal**.

### Cómo se une

¿Cómo arranca un proyecto que todavía no tiene CLAUDE.md?

---

## Tema 6 — Onboarding (puesta en marcha): arrancar desde la raíz y `/init`

### Qué es

**Onboarding** es poner en marcha Claude Code en un proyecto por primera vez. Son dos pasos.

**Arrancar desde la raíz.** Abrí Claude Code (con el comando `claude`) **desde la carpeta raíz del repo**. Importa porque Claude Code busca su configuración a partir de la carpeta donde lo arrancás: desde la raíz descubre la estructura del proyecto, carga el CLAUDE.md del proyecto y el `.claude/settings.json` compartido (Tema 12).

**`/init`.** Este comando analiza el código (lenguajes, frameworks, archivos clave, comandos de build y test) y escribe un **borrador** de CLAUDE.md, para que no arranques de una hoja en blanco (*"Run `/init` to generate a starting CLAUDE.md automatically."*). Si el proyecto ya tiene un CLAUDE.md, no lo pisa: sugiere mejoras (*"suggests improvements rather than overwriting it"*).

La palabra clave es **borrador**. `/init` solo puede saber lo que se ve en el código, así que el resultado hay que revisarlo siempre (el curso insiste: *"always review and refine it"*). La revisión tiene dos partes:
- **Agregar** lo que el análisis no puede inferir: la política de ramas, los requisitos de tests, las decisiones del equipo.
- **Sacar** el ruido: lo que Claude ya ve leyendo el repo (como una lista de carpetas). La documentación coincide: *"From there the work is mostly removing lines"* (después, el trabajo es sobre todo borrar líneas).

📘 **Curso:** antes del primer uso, el curso propone un checklist de tres puntos: CLAUDE.md revisado, `permissions.deny` configurado para los archivos sensibles (Tema 11), y los comandos de test y build documentados.

**Para entender un codebase nuevo**, la documentación (en "common workflows") recomienda ir de lo general a lo particular: primero preguntas amplias ("give me an overview of this codebase"), después áreas concretas, y por último pedirle las convenciones y un glosario de los términos del proyecto.

### Ejemplo

El equipo de TiendaX empieza a usar Claude Code en `backoffice`:
1. Entra a la raíz del repo y arranca Claude Code: `cd backoffice && claude`.
2. Corre `/init`, que genera un CLAUDE.md con el stack (.NET 9, xUnit) y los comandos `dotnet build` y `dotnet test`.
3. El tech lead lo revisa: agrega "los endpoints públicos llevan `[Authorize]`; los internos, la policy `Backoffice`", que el análisis no podía saber, y borra la lista de 40 carpetas que había generado `/init`.
4. Lo commitea como CLAUDE.md del proyecto.

### Para el examen

- `/init` → **borrador que se revisa**: se agrega lo que el análisis no puede inferir y se saca lo que Claude ya ve leyendo el repo.
- ❌ "Commitear la salida de `/init` tal cual para todo el equipo": le faltan las decisiones del equipo y le sobra ruido.

### Cómo se une

A medida que el proyecto crece, el CLAUDE.md crece. Si se vuelve enorme, se respeta peor (Tema 4). La guía tiene dos herramientas para organizarlo.

---

## Tema 7 — Modularizar: imports con `@` y `.claude/rules/`

### Qué es

Un CLAUDE.md **monolítico** es uno que tiene todo en un solo archivo gigante: tests, API, deploy, frontend. El problema es el del Tema 4: cuanto más largo, peor se respeta, y además mezcla cosas que les importan a distintas partes del equipo. La guía nombra dos formas de partirlo. Acá va la base; el detalle es de 3B.

**1. Imports con `@` (lo que la guía llama "@import syntax").** Desde un CLAUDE.md podés traer el contenido de otro archivo escribiendo `@` seguido de la ruta. Así un estándar se escribe una sola vez y cada CLAUDE.md lo incluye si le corresponde.

```markdown
# CLAUDE.md de packages/pagos
@../../docs/estandares/seguridad-pagos.md
@../../docs/estandares/api-conventions.md
```

Hay cuatro detalles que conviene saber:
- La sintaxis es **`@ruta`**. "@import" es el nombre del concepto, no una palabra que se escribe en el archivo.
- Las rutas relativas se resuelven desde **el archivo que importa**, no desde donde arrancaste Claude Code.
- Un archivo importado puede importar otro, hasta **4 niveles** de profundidad (*"maximum depth of four hops"*).
- **Los imports no ahorran contexto.** Los archivos importados se cargan igual al arrancar, como si estuvieran escritos en el CLAUDE.md (*"imported files still load and enter the context window at launch"*). Sirven para **organizar y reutilizar**, no para cargar menos.

La Skill 2 de la guía es justamente esto: usar `@import` para incluir **selectivamente** en el CLAUDE.md de cada paquete los estándares que le corresponden, según lo que saben sus mantenedores. Por ejemplo, el paquete de pagos importa el estándar de seguridad de pagos; el de catálogo, no.

**2. El directorio `.claude/rules/`.** En vez de un CLAUDE.md con todo, ponés las reglas en archivos separados **por tema** dentro de `.claude/rules/`:

```
.claude/rules/
├── testing.md
├── api-conventions.md
└── deployment.md
```

Estos archivos funcionan de dos maneras:
- **Sin configuración extra**, se cargan **siempre**, como si fueran parte del CLAUDE.md. La ganancia es de orden: cada tema tiene su archivo y es fácil de mantener.
- **Con un frontmatter que tenga `paths:`**, se cargan **solo cuando Claude trabaja con archivos que coinciden**. Un **frontmatter** es un bloque de configuración al principio del archivo, escrito en YAML entre dos líneas `---`. Por ejemplo, con `paths: ["**/*.test.tsx"]` la regla entra solo cuando Claude toca un test. Eso es la tarea 3.3 y se ve en 3B.

La Skill 3 de la guía es partir un CLAUDE.md grande en archivos de tema en `.claude/rules/` (`testing.md`, `api-conventions.md`, `deployment.md`).

### Ejemplo

El CLAUDE.md de TiendaX llegó a 700 líneas: convenciones de tests, de API, de deploy, de React… y Claude empieza a ignorar reglas.
- **Bien:** pasar cada bloque a `.claude/rules/testing.md`, `.claude/rules/api-conventions.md` y `.claude/rules/deployment.md`, y dejar en el CLAUDE.md solo lo general.
- **Bien también:** en `packages/pagos/CLAUDE.md`, importar con `@` solo el estándar de seguridad de pagos, que es el que necesita ese paquete.

### Para el examen

- CLAUDE.md enorme / monolítico → **`.claude/rules/` por tema** (o `@` para incluir el estándar que corresponde a cada paquete).
- ❌ "`@import` reduce el uso de contexto" → falso.
- ❌ "Escribir `@import ruta`" como sintaxis → es `@ruta`.

### Cómo se une

Con varios niveles, imports y rules, aparece la pregunta: **¿qué cargó Claude, realmente?**

---

## Tema 8 — `/memory`: ver qué archivos cargó Claude

### Qué es

Con tantos lugares posibles para las instrucciones (tu CLAUDE.md, el del proyecto, el de una carpeta, imports, rules), es fácil que Claude esté leyendo algo distinto de lo que creés. **`/memory`** sirve para salir de la duda: lista **todos los CLAUDE.md, CLAUDE.local.md y archivos de rules cargados en la sesión actual**, y te deja abrirlos para editarlos (y también activar o desactivar la auto memory).

Es una herramienta de **diagnóstico**: no carga ni cambia nada, te muestra lo que hay. La Skill 4 de la guía la usa así: verificar qué archivos de memoria están cargados para diagnosticar un comportamiento inconsistente entre sesiones. La sección de troubleshooting (resolución de problemas) de la documentación lo dice directo: si un archivo no aparece en la lista, Claude no lo ve (*"Run `/memory` to verify your CLAUDE.md and CLAUDE.local.md files are being loaded. If a file isn't listed, Claude can't see it."*).

### Ejemplo

Lucas dice: "A mí Claude me respeta la regla de los centavos y a Sofía no". Cada uno corre `/memory`:
- Lucas ve `~/.claude/CLAUDE.md` (con la regla) y `./CLAUDE.md`.
- Sofía ve solo `./CLAUDE.md`.

En un minuto tienen el diagnóstico: la regla vive en el user-level de Lucas (Tema 5), y hay que pasarla al CLAUDE.md del proyecto.

### Para el examen

- "Comportamiento distinto entre personas o sesiones; ¿qué configuración está cargando?" → **`/memory`**.
- ❌ "`/memory` hace que se carguen los archivos": no carga nada, **muestra** lo que se cargó. Es diagnóstico.
- `/context` también muestra qué CLAUDE.md se cargaron, pero la respuesta de la guía es **`/memory`**.

### Cómo se une

Todo lo que se carga (CLAUDE.md, imports, archivos leídos) ocupa lugar. Y el lugar es limitado.

---

# Parte 3 — El contexto

## Tema 9 — Context window (ventana de contexto): un presupuesto finito

### Qué es

La **context window** es la memoria de trabajo de la sesión: todo lo que Claude tiene a la vista en un momento dado. Ahí entran la conversación, el contenido de los archivos leídos, la salida de los comandos, los CLAUDE.md, la auto memory, las skills cargadas y las instrucciones del sistema. Tiene un tamaño máximo, así que cada cosa que entra le quita lugar a otra.

Pero el problema no es solo el tamaño. Cuanto más material irrelevante hay en el contexto, peor atiende Claude a lo que importa: es la **attention dilution** (dilución de la atención) que viste en 1B. Por eso cargar todo "por las dudas" empeora los resultados.

📘 **Curso:** el curso lo plantea como un **presupuesto (budget)**: decidir qué cargar es una decisión de rendimiento, no de prolijidad (*"Context loading is a performance decision, not just project housekeeping"*). Y lo resume así: un contexto chico y preciso rinde más que uno grande y con ruido (*"A smaller, accurate context window outperforms a large, noisy one"*).

**Formas de agregar contexto en una sesión.** La más directa es escribir **`@archivo`** en el prompt: Claude Code incluye el contenido de ese archivo sin esperar a que Claude decida leerlo. Si escribís `@carpeta/`, te muestra la lista de archivos de la carpeta, no su contenido. La misma sintaxis sirve para los resources MCP (2B). También podés nombrar la ruta de un archivo, pegar una URL o dar instrucciones en el mismo mensaje.

**Qué pasa cuando se llena.** Claude Code libera lugar solo: **primero borra salidas viejas de tools y después resume la conversación**. En ese resumen se pueden perder las instrucciones que diste al principio de la charla. Por eso la documentación aconseja poner las reglas persistentes en CLAUDE.md y no confiar en el historial de la conversación (*"Put persistent rules in CLAUDE.md rather than relying on conversation history"*): CLAUDE.md se vuelve a cargar, la charla no.

### Ejemplo

**Mal:** "@src/ — leé todo y después te digo qué necesito". Llenás el contexto de archivos que no importan para la tarea.

**Bien:** "@src/envios/calculo.ts — el envío gratis no se aplica cuando hay cupón; ¿por qué?". Claude tiene justo el archivo que necesita y una pregunta concreta.

### Para el examen

- Más contexto ≠ mejores resultados. Lo justo y relevante.
- Una regla que tiene que durar toda la sesión (o todas) → CLAUDE.md, no un mensaje al principio.

### Cómo se une

¿Qué hacés cuando el contexto ya está lleno o cuando cambiás de tarea?

---

## Tema 10 — `/compact`, `/clear` y `/context`

### Qué es

Hay tres comandos para manejar el contexto, y la diferencia entre los dos primeros se evalúa directamente.

**`/compact`** resume la conversación y sigue en la **misma** charla. Sirve cuando el contexto se llenó de material largo (exploración, logs) pero todavía estás en la misma tarea y querés conservar lo importante. El costo es que se pierde el detalle textual a cambio de espacio (📘 el curso lo dice así: *"trades verbatim history for a summary"*).

**`/clear`** vacía el contexto por completo y arranca una conversación nueva. Sirve cuando pasás a una **tarea que no tiene nada que ver** con la anterior: lo viejo ya no te sirve y solo diluye la atención. La documentación lo recomienda sin vueltas: *"`/clear` between unrelated tasks. It costs nothing"*. Y agrega un consejo: si ya corregiste a Claude dos veces por lo mismo, `/clear` más un prompt nuevo que incluya lo aprendido suele funcionar mejor que seguir corrigiendo.

**`/context`** no cambia nada: muestra cuánto contexto ocupa cada cosa, para ver qué está llenando el lugar.

Algunos detalles de `/compact`:
- Claude Code también compacta solo cuando se acerca al límite; eso es la **auto-compaction** (compactación automática). 📘 Para el curso, `/compact` es *"the same summarization, on demand"*: lo mismo, cuando vos querés.
- Podés **guiar** el resumen para que conserve lo que te importa: `/compact enfocate en las decisiones sobre el cálculo de envío`. También podés dejar esas indicaciones fijas en una sección "Compact Instructions" del CLAUDE.md.
- **Qué sobrevive:** el CLAUDE.md de la raíz **se vuelve a leer del disco** después de `/compact`, así que sus instrucciones no se pierden. Los de subcarpetas y las rules con `paths:` se recargan cuando vuelven a hacer falta.

La tarea 5.4 de la guía usa `/compact` en este sentido: reducir el uso de contexto en sesiones largas de exploración, cuando el contexto se llena de salida verbosa.

| Comando | Qué hace | Cuándo |
|---|---|---|
| **`/compact`** `[instrucciones]` | **Resume** la conversación y sigue en la **misma** charla | Contexto lleno de salida verbosa y querés **seguir con la misma tarea** |
| **`/clear`** | **Vacía** el contexto: conversación nueva | Pasás a una **tarea sin relación** |
| **`/context`** | Muestra cuánto contexto usa cada cosa | Para ver qué ocupa lugar |

### Ejemplo

- Lucas lleva una hora explorando el módulo de pagos: decenas de Grep y Read. El contexto está al 85% y todavía tiene que implementar el cambio. Como sigue en la misma tarea, usa **`/compact enfocate en lo que descubrimos del flujo de reembolsos`**.
- Terminó con pagos y ahora quiere revisar un tema de CSS. Lo de pagos no le sirve para nada, así que usa **`/clear`**.

### Para el examen

- Misma tarea, contexto lleno → `/compact`. Tarea nueva sin relación → `/clear`.
- ❌ "Después de `/compact` se pierden las instrucciones del CLAUDE.md" → el de la raíz se re-inyecta.

### Cómo se une

La mejor forma de no gastar contexto es que Claude no cargue lo que no debe. Y algunos archivos no los tiene que leer **nunca**.

---

## Tema 11 — Excluir archivos: reglas `Read` deny, no `.claudeignore`

### Qué es

Hay archivos que Claude Code no debería leer: secretos (como `.env`), binarios grandes, código generado. Pedírselo en CLAUDE.md no alcanza, porque CLAUDE.md es contexto y no se impone (Tema 4). Lo que sí funciona es una **regla de permiso deny** (de denegación) sobre la tool Read, en `.claude/settings.json`: Claude Code bloquea la lectura antes de que ocurra, decida lo que decida el modelo.

```json
{
  "permissions": {
    "deny": [
      "Read(./.env)",
      "Read(./.env.*)",
      "Read(./secrets/**)",
      "Read(./dist/**)"
    ]
  }
}
```

Una regla `Read(...)` deny cubre más que la lectura: también bloquea Edit y Write sobre esa ruta. Para Grep y Glob, la documentación lo describe como un intento de "mejor esfuerzo" (*best-effort*), o sea que no está garantizado del todo. NotebookEdit se cubre con una regla `Edit(...)` deny.

> ⚠️ **En el curso vas a escuchar otra cosa.** El companion dice *"Configure `.claudeignore` to exclude secrets, large binaries, and auto-generated files"*. La documentación dice lo contrario: *"If your project has a `.claudeignore` file, it has no effect, so move its entries into `Read` deny rules."* (Las slides y el glosario del curso sí dicen lo correcto.) **Para el examen: excluir archivos se hace con `permissions.deny` y reglas `Read(...)`. Si aparece `.claudeignore`, es un distractor.**

### Ejemplo

TiendaX tiene un `.env` con la clave del procesador de pagos. Escribir en CLAUDE.md "no leas el .env" **no lo garantiza**: Claude probablemente lo respete, pero nada lo obliga. Con `"deny": ["Read(./.env)"]`, Claude Code **no puede** leerlo, aunque el modelo lo intente.

### Para el examen

- Secreto o archivo que **nunca** se debe leer → **deny rule** (determinística).
- ❌ `.claudeignore`: según la documentación, no tiene efecto.
- ❌ Una instrucción en CLAUDE.md: es contexto, no se impone.

### Cómo se une

Las reglas deny son parte del **modelo de permisos**, que decide qué puede hacer Claude Code sin preguntarte.

---

# Parte 4 — Permisos y modos de trabajo

## Tema 12 — El modelo de permisos: settings, deny/allow y hooks

### Qué es

**Los archivos de settings.** La configuración de Claude Code (permisos, hooks, modo por defecto) vive en archivos `settings.json`. Igual que con CLAUDE.md, hay uno personal, uno del equipo y otros, y dónde está cada archivo decide a quién afecta:

| Scope (alcance) | Archivo | A quién afecta |
|---|---|---|
| **User** | `~/.claude/settings.json` | A vos, en todos tus proyectos |
| **Project** (compartido) | `.claude/settings.json` | A todo el equipo (se commitea) |
| **Local** | `.claude/settings.local.json` | A vos, en este proyecto (no se commitea) |
| **Managed** | Lo pone la organización | A todos; **gana siempre** |

Cuando dos niveles configuran lo mismo distinto, manda la **precedencia** (el orden de prioridad): managed, después la línea de comandos, después local, después project y por último user. Fijate la diferencia con CLAUDE.md: los CLAUDE.md **se suman**, pero en settings **gana el nivel más alto**. La excepción son las listas de permisos, que se combinan entre niveles. Y un detalle de 2B: los servidores MCP **no** van en settings.json, sino en `.mcp.json` (equipo) o `~/.claude.json` (personal).

**Reglas allow, ask y deny.** Cada regla de permiso describe una acción (por ejemplo `Bash(npm test *)`) y dice qué hacer con ella. **allow** la deja ejecutar sin preguntar. **ask** hace que Claude Code te pregunte siempre, aunque haya una regla allow que coincida. **deny** la bloquea.

Lo importante es el orden: Claude Code evalúa **primero deny, después ask y por último allow** (*"Rules are evaluated in order: deny, then ask, then allow."*). Por eso **deny gana siempre**, y no se puede abrir una excepción con una allow más específica (*"An allow rule can't carve an exception out of a deny rule."*). Si necesitás una excepción, hay que replantear la regla deny.

**Hooks y permisos.** Los hooks **`PreToolUse` corren antes** del chequeo de permisos. Eso permite que un hook bloquee una acción primero (saliendo con exit code 2). Pero no funciona al revés: un hook que responde "allow" **no saltea** una regla deny, porque deny sigue mandando.

> ⚠️ **En el curso vas a escuchar otra cosa.** El companion dice *"If a permission blocks an action, no tool call happens and no hook fires"*, o sea, que si un permiso bloquea, no corre ningún hook. Es incorrecto para PreToolUse (las slides sí dicen bien: *"A PreToolUse hook runs before the permission check and can deny first."*). Lo único cierto es que, si el permiso bloquea, la tool no se ejecuta y por eso no corre **PostToolUse**. **Para el examen: PreToolUse corre antes de los permisos, y deny siempre gana.**

### Ejemplo

En `.claude/settings.json` de TiendaX:
```json
{
  "permissions": {
    "allow": ["Bash(npm test *)", "Bash(npm run lint)"],
    "deny":  ["Bash(git push *)", "Read(./.env)"]
  }
}
```
Con esto, Claude corre tests y lint sin preguntar, nunca hace push y nunca lee `.env`. Si alguien agrega `"allow": ["Bash(git push origin feature/*)"]` para permitir solo las ramas de feature, **no funciona**: la deny de `git push *` se evalúa primero y gana.

### Para el examen

- Regla que **tiene** que cumplirse → **deny rule o hook** (determinístico), no CLAUDE.md (contexto).
- Permisos del equipo → `.claude/settings.json` (commiteado). Personales → `.claude/settings.local.json` o `~/.claude/settings.json`.

### Cómo se une

Además de reglas puntuales, hay **modos** que cambian cuánto pregunta Claude Code en general.

---

## Tema 13 — Permission modes (modos de permiso)

### Qué es

Un **permission mode** define, en general, **qué hace Claude Code sin pedirte permiso**. Las reglas allow/deny del Tema 12 son puntuales (este comando sí, este archivo no); el modo es la actitud de base para todo lo demás. Hoy hay seis, que van de "pregunta casi todo" a "no pregunta nada":

| Modo | Qué corre sin preguntar | Para qué |
|---|---|---|
| **`default`** (en la interfaz: **Manual**) | Solo lecturas | Revisar cada acción |
| **`acceptEdits`** | Lecturas + ediciones + comandos de archivos (`mkdir`, `mv`, `cp`…) **dentro** del directorio de trabajo | Iterar sobre código que vas revisando |
| **`plan`** | Lecturas y comandos de solo lectura (lo demás te lo pregunta o lo revisa el clasificador); **no edita** hasta que apruebes el plan | Explorar antes de cambiar (Tema 14) |
| **`auto`** | Todo, con un **clasificador** que revisa cada acción | Tareas largas, menos interrupciones |
| **`dontAsk`** | Solo lo preaprobado; **todo lo demás se rechaza** | CI y scripts cerrados |
| **`bypassPermissions`** | Todo, sin preguntar | **Solo** en contenedores o VMs aisladas |

El **clasificador** del modo `auto` es un modelo aparte que mira cada acción antes de que se ejecute y frena las riesgosas, para que no tengas que aprobar todo a mano.

Algunos detalles:
- **Ojo con el nombre:** `default` **no es el modo con el que se arranca**. Desde la versión 2.1.283, las sesiones interactivas arrancan en `auto`; `claude -p` y el Agent SDK arrancan en Manual.
- **Cómo se cambia:** con **Shift+Tab** durante la sesión (ciclo `default`, `acceptEdits`, `plan`), con `--permission-mode` al arrancar, o con `permissions.defaultMode` en settings.
- **`bypassPermissions` es peligroso fuera de un entorno aislado**, porque no protege contra **prompt injection** (instrucciones maliciosas escondidas en el contenido que Claude lee): *"offers no protection against prompt injection"*. Nunca en la máquina de un dev "para ir más rápido".
- **Rutas protegidas:** hay carpetas (`.git`, `.claude`, `.vscode`…) que ningún modo escribe sin preguntar, salvo `bypassPermissions`.
- 📘 **Curso:** la regla del curso es exploración con `plan`, supervisión media con `acceptEdits` y sin supervisión con `dontAsk`.

### Ejemplo

- Lucía revisa cada cambio de un refactor delicado, así que usa `default`.
- Lucas itera rápido sobre tests que va mirando, así que usa `acceptEdits`.
- El job nocturno de CI de TiendaX usa `dontAsk` con las tools preaprobadas.

### Para el examen

**La guía no evalúa los permission modes.** De todo esto, solo nombra **plan mode**, como opuesto a "direct execution" (tarea 3.4). Leé la tabla para entender cómo funciona Claude Code; no la memorices.

### Cómo se une

El único modo que sí entra en el examen es plan mode. Y la pregunta es **cuándo** usarlo.

---

## Tema 14 — Plan mode vs. direct execution y el Explore subagent (introducción)

### Qué es

**Plan mode (modo plan)** es una forma de trabajar en la que Claude primero investiga y propone, y recién después cambia. Lee archivos, corre comandos para explorar y escribe un plan, pero **no edita tu código** hasta que lo aprobás (*"Claude reads files, runs shell commands to explore, and writes a plan, but does not edit your source."*). Cuando ves el plan, podés aprobarlo, refinarlo o pedirle que siga planificando.

**Direct execution (ejecución directa)** es lo contrario: Claude empieza a cambiar el código enseguida.

¿Cuándo conviene cada uno? La guía (tarea 3.4, que se completa en 3C) da el criterio de la **complejidad**. En una tarea compleja, arrancar directo es arriesgado: si Claude no entendió las dependencias, puede tomar un camino equivocado y descubrirlo cuando ya tocó muchos archivos, y rehacer eso es caro. En un cambio chico y claro, en cambio, planificar no agrega nada.
- **Plan mode** para tareas **complejas**: cambios en **muchos archivos**, **varias formas válidas** de hacerlo, **decisiones de arquitectura**.
- **Ejecución directa** para cambios **chicos y claros**: un bug en un archivo, con la solución evidente.

**La pregunta oficial Q5.** Hay que reestructurar un monolito en microservicios, con cambios en decenas de archivos y decisiones sobre los límites entre servicios. La respuesta correcta es **entrar en plan mode para explorar, entender las dependencias y diseñar el enfoque antes de cambiar nada**. Los distractores son tres:
- "Ejecución directa y que la implementación revele los límites": las dependencias aparecen tarde y el retrabajo es caro.
- "Ejecución directa con instrucciones exhaustivas": supone que ya sabés cómo es el código sin haberlo explorado.
- "Ejecución directa y pasar a plan mode **si aparece** complejidad": la complejidad **ya está en el enunciado**, así que no hay nada que esperar.

**El Explore subagent.** Antes de planificar algo grande, Claude necesita recorrer mucho código, y eso genera mucha salida que llenaría tu contexto. Para eso Claude Code trae el **Explore subagent**: un subagente **de solo lectura** (tiene prohibidos Write y Edit) que busca y entiende código **en su propio contexto** y devuelve solo un resumen. Es el aislamiento de 1C aplicado a la exploración. Un detalle: Explore arranca **sin tus CLAUDE.md**, para ser más rápido y barato. (El curso de 3A no lo menciona; solo habla de la Agent tool genérica.)

La tarea 3.4 de la guía lo pide así: usar el Explore subagent en fases de descubrimiento verbosas, para no agotar el contexto en tareas de varias fases.

> ⚠️ **En el curso vas a escuchar otra cosa.** El glosario dice que plan mode propone un plan *"before executing any tools"*, o sea, antes de usar cualquier tool. Es impreciso. **Para el examen: en plan mode Claude sí usa tools de lectura y comandos de exploración; lo único que no hace es editar.**

### Ejemplo

- "Migrar los 60 endpoints de TiendaX de la API v1 a la v2, con cambio de autenticación": muchos archivos y decisiones de diseño, así que va **plan mode**.
- "El botón 'Comprar' tiene un typo en `Checkout.tsx`": un archivo y un arreglo evidente, así que va **ejecución directa**.
- "Antes de migrar, entendé cómo usan la autenticación los 60 endpoints": el **Explore subagent** recorre el código y devuelve un resumen, y el contexto principal queda limpio para planificar.

### Para el examen

- Complejidad **ya conocida** (muchos archivos, arquitectura, varias opciones) → **plan mode desde el principio**.
- Cambio chico y claro → ejecución directa (plan mode sería un paso de más).
- Exploración que va a generar mucha salida → **Explore subagent**.

### Cómo se une

Cierra el capítulo. En 3B se completa 3.1: el orden fino de la jerarquía, qué pasa con los conflictos, y `.claude/rules/` con `paths:` (tarea 3.3).

---

## Cómo se une todo

Claude Code es un **agente**: lee, ejecuta, edita y verifica en un loop (Temas 1 y 2). Cada sesión arranca **sin recordar las anteriores**; las ediciones hechas con tools se pueden deshacer, pero lo que hizo Bash y las acciones remotas no (Tema 2). Cada tool tiene su trabajo, y **Agent** delega en un subagente con su propio contexto (Tema 3).

Para enseñarle tu proyecto está **CLAUDE.md**, que es contexto permanente y no reglas impuestas: corto, específico, con lo que Claude no puede adivinar (Tema 4). Hay tres niveles: **user** (`~/.claude/CLAUDE.md`, personal), **project** (en el repo, para el equipo) y **directory** (en una subcarpeta), y se **suman** (Tema 5). `/init` genera un **borrador** que siempre se revisa (Tema 6). Si CLAUDE.md crece demasiado, se parte en **`.claude/rules/`** por tema o se incluye el estándar de cada paquete con **`@ruta`**, sabiendo que los imports no ahorran contexto (Tema 7). Y **`/memory`** muestra qué archivos se cargaron de verdad (Tema 8).

El contexto es un **presupuesto**: conviene cargar lo justo y relevante (Tema 9). Con el contexto lleno, **`/compact`** si seguís con la misma tarea y **`/clear`** si pasás a una nueva (Tema 10). Para que Claude nunca lea un archivo, una regla **`Read` deny**; `.claudeignore` no tiene efecto (Tema 11). En los permisos, **deny gana**, managed gana, y **PreToolUse corre antes** del chequeo de permisos (Tema 12). Los **permission modes** no los evalúa la guía, salvo plan mode (Tema 13). Con complejidad conocida, **plan mode** desde el principio; para un cambio chico, ejecución directa; y para la exploración verbosa, el **Explore subagent** (Tema 14).

## Lo que viene

**3B · Udemy 10 — CLAUDE.md Configuration Hierarchy:** el orden exacto en que se cargan los CLAUDE.md, qué pasa cuando dos niveles se contradicen, y las **path-specific rules** (`.claude/rules/` con `paths:`), que son la tarea 3.3.

---

## Las trampas del examen

Cada trampa tiene el mismo orden: la situación, **qué elegir en el examen (✅)**, las opciones que tientan (❌) con por qué tientan y por qué están mal, y una regla para recordar.

### Grupo: Dónde va cada instrucción

#### Trampa 1 · Un compañero nuevo no recibe las convenciones

**La situación.** Sofía clona el repo y Claude Code no respeta las convenciones que a vos sí te respeta (Temas 5 y 8).

**✅ En el examen elegí:** las convenciones están en **tu `~/.claude/CLAUDE.md`** (user-level): **moverlas al CLAUDE.md del proyecto** y commitearlo. (Para confirmarlo: `/memory` en las dos máquinas.)

**❌ Las que tientan:**

❌ **"Que Sofía copie tu `~/.claude/CLAUDE.md` a su máquina".**
- *Tienta porque:* funciona enseguida.
- *Está mal porque:* no es compartido ni versionado; al próximo cambio vuelven a divergir.

❌ **"Repetir las convenciones en el prompt de cada sesión".**
- *Tienta porque:* Claude las ve seguro.
- *Está mal porque:* depende de que cada uno se acuerde; para eso existe el CLAUDE.md de proyecto.

> 🧠 **Para recordar:** en tu home = solo vos; en el repo = el equipo.

#### Trampa 2 · Preferencias personales en el CLAUDE.md del equipo

**La situación.** Lucas quiere que Claude le explique todo con ejemplos en C#, pero el resto del equipo no (Tema 5).

**✅ En el examen elegí:** **`~/.claude/CLAUDE.md`** (o `CLAUDE.local.md` si es solo para este proyecto).

**❌ Las que tientan:**

❌ **"Agregarlo al CLAUDE.md del proyecto con la aclaración 'solo para Lucas'".**
- *Tienta porque:* queda todo en un lugar.
- *Está mal porque:* le llega a todo el equipo y suma ruido al contexto de todos.

> 🧠 **Para recordar:** personal → nivel de usuario o local, nunca el compartido.

#### Trampa 3 · "Lo pongo en CLAUDE.md con IMPORTANT"

**La situación.** Claude Code a veces lee `.env`. Alguien propone agregar al CLAUDE.md: "IMPORTANT: NUNCA leas el archivo .env" (Temas 4 y 11).

**✅ En el examen elegí:** una **regla `Read` deny** en `permissions.deny` de `.claude/settings.json`.

**❌ Las que tientan:**

❌ **"La instrucción en CLAUDE.md, en mayúsculas".**
- *Tienta porque:* es lo más fácil.
- *Está mal porque:* CLAUDE.md es contexto, no se impone; *"adding IMPORTANT probably won't fix it"*.

❌ **"Un archivo `.claudeignore` con `.env`".**
- *Tienta porque:* el companion del curso lo recomienda y se parece a `.gitignore`.
- *Está mal porque:* según la documentación, `.claudeignore` **no tiene efecto**.

> 🧠 **Para recordar:** "nunca" o "siempre" → deny rule o hook, no CLAUDE.md.

### Grupo: Organizar CLAUDE.md

#### Trampa 4 · El CLAUDE.md de 700 líneas

**La situación.** El CLAUDE.md creció con convenciones de tests, API, deploy y React, y Claude empieza a ignorar reglas (Temas 4 y 7).

**✅ En el examen elegí:** **partirlo en archivos por tema en `.claude/rules/`** (`testing.md`, `api-conventions.md`, `deployment.md`), o importar con `@` el estándar de cada paquete en su CLAUDE.md.

**❌ Las que tientan:**

❌ **"Agregar encabezados claros por área en el mismo archivo".**
- *Tienta porque:* parece más ordenado.
- *Está mal porque:* sigue siendo monolítico y largo, y depende de que Claude "infiera" qué sección aplica (es el distractor de la Q6).

❌ **"Usar imports con `@` para que cargue menos contexto".**
- *Tienta porque:* "modular" suena a "más liviano".
- *Está mal porque:* los archivos importados se cargan igual al arrancar; los imports organizan, no ahorran.

> 🧠 **Para recordar:** monolítico → `.claude/rules/` por tema.

#### Trampa 5 · ¿Qué cargó Claude?

**La situación.** Claude se comporta distinto en dos sesiones del mismo proyecto y no sabés por qué (Tema 8).

**✅ En el examen elegí:** **`/memory`** para ver qué CLAUDE.md, CLAUDE.local.md y rules se cargaron.

**❌ Las que tientan:**

❌ **"Borrar y regenerar el CLAUDE.md con `/init`".**
- *Tienta porque:* "empezar de cero" parece limpiar el problema.
- *Está mal porque:* no diagnostica nada; capaz el problema está en otro nivel (user, subcarpeta).

❌ **"Correr `/memory` para que se recarguen los archivos".**
- *Tienta porque:* el nombre suena a "cargar memoria".
- *Está mal porque:* `/memory` **lista** los archivos cargados y permite editarlos; no carga ni recarga nada.

> 🧠 **Para recordar:** diagnosticar la configuración cargada → `/memory`.

#### Trampa 6 · Commitear `/init` tal cual

**La situación.** El equipo corre `/init` y quiere commitear el resultado directamente (Tema 6).

**✅ En el examen elegí:** **revisarlo**: agregar lo que el análisis no infiere (políticas, decisiones del equipo) y sacar ruido.

**❌ Las que tientan:**

❌ **"Commitearlo así, porque refleja el código real".**
- *Tienta porque:* lo generó Claude a partir del repo.
- *Está mal porque:* es un borrador: le faltan las decisiones del equipo y le sobran cosas que Claude ya ve leyendo el repo.

> 🧠 **Para recordar:** `/init` = borrador.

### Grupo: Contexto

#### Trampa 7 · Cambio de tarea con el contexto lleno

**La situación.** Terminaste de explorar el módulo de pagos y ahora vas a trabajar en algo de CSS que no tiene relación (Tema 10).

**✅ En el examen elegí:** **`/clear`**.

**❌ Las que tientan:**

❌ **"`/compact` para conservar lo aprendido".**
- *Tienta porque:* "no perder nada" suena bien.
- *Está mal porque:* `/compact` es para **seguir la misma tarea** con menos contexto; acá lo de pagos es ruido para la tarea nueva.

> 🧠 **Para recordar:** misma tarea → `/compact`; tarea nueva → `/clear`.

#### Trampa 8 · "Sin CLAUDE.md no hay memoria"

**La situación.** Una opción afirma que Claude Code recuerda la conversación del día anterior, o que sin CLAUDE.md no persiste absolutamente nada (Tema 2).

**✅ En el examen elegí:** **cada sesión arranca sin el historial de la conversación anterior**; lo que tiene que persistir como regla va en **CLAUDE.md**.

**❌ Las que tientan:**

❌ **"Claude Code recuerda la sesión anterior del mismo proyecto".**
- *Tienta porque:* existe `--resume`.
- *Está mal porque:* `--resume` retoma **esa** sesión a propósito (1C); una sesión nueva no sabe nada de las anteriores.

❌ **"Sin CLAUDE.md, Claude Code no tiene ninguna memoria entre sesiones".**
- *Tienta porque:* lo dice el companion del curso.
- *Está mal porque:* hoy existe auto memory (la escribe Claude en `MEMORY.md`). Igual, para las reglas del proyecto la respuesta es CLAUDE.md.

> 🧠 **Para recordar:** lo que tenés que repetir en cada sesión → CLAUDE.md.

### Grupo: Permisos y modos

#### Trampa 9 · Una excepción dentro de una regla deny

**La situación.** Hay `deny: ["Bash(git push *)"]` y alguien agrega `allow: ["Bash(git push origin feature/*)"]` para permitir solo las ramas de feature (Tema 12).

**✅ En el examen elegí:** **no funciona: deny gana**. Hay que replantear la regla deny (por ejemplo, negar solo `git push origin main`).

**❌ Las que tientan:**

❌ **"La regla más específica gana".**
- *Tienta porque:* así funcionan muchos sistemas de configuración.
- *Está mal porque:* en Claude Code no: *"An allow rule can't carve an exception out of a deny rule."*

> 🧠 **Para recordar:** deny → ask → allow; deny siempre primero.

#### Trampa 10 · ¿Corre el hook si el permiso bloquea?

**La situación.** Una opción dice que, si una regla de permiso bloquea una tool, ningún hook se ejecuta (Tema 12).

**✅ En el examen elegí:** el hook **PreToolUse corre antes** del chequeo de permisos. Lo que no corre es el **PostToolUse**, porque la tool nunca se ejecutó.

**❌ Las que tientan:**

❌ **"Los permisos se evalúan primero y, si bloquean, no corre ningún hook".**
- *Tienta porque:* lo dice el companion del curso.
- *Está mal porque:* contradice la documentación y las propias slides del curso.

> 🧠 **Para recordar:** PreToolUse → permisos → tool → PostToolUse.

#### Trampa 11 · Plan mode "si aparece complejidad"

**La situación.** Una migración que toca decenas de archivos y obliga a decidir límites entre servicios (Tema 14, Q5 oficial).

**✅ En el examen elegí:** **plan mode desde el principio** para explorar, entender dependencias y diseñar el enfoque.

**❌ Las que tientan:**

❌ **"Ejecución directa y pasar a plan mode si aparece complejidad".**
- *Tienta porque:* parece pragmático.
- *Está mal porque:* la complejidad **ya está en el enunciado**.

❌ **"Ejecución directa con instrucciones exhaustivas".**
- *Tienta porque:* "si le explico todo, no hace falta planificar".
- *Está mal porque:* supone que ya conocés la estructura sin haber explorado el código.

> 🧠 **Para recordar:** complejidad conocida → plan mode ya.

#### Trampa 12 · bypassPermissions "para ir más rápido"

**La situación.** Un dev propone usar `bypassPermissions` en su máquina porque los pedidos de permiso lo frenan (Tema 13).

**✅ En el examen elegí:** **no**: `bypassPermissions` es solo para contenedores o VMs aisladas. Para menos interrupciones: reglas `allow` para lo seguro y frecuente, `acceptEdits`, o el modo `auto` (la documentación lo recomienda para reducir el *prompt fatigue*, el cansancio de aprobar todo).

**❌ Las que tientan:**

❌ **"Sí, total tiene reglas deny configuradas".**
- *Tienta porque:* las deny siguen aplicando.
- *Está mal porque:* sin aislamiento no hay protección contra prompt injection ni contra comandos destructivos no previstos.

> 🧠 **Para recordar:** bypass = solo en un entorno aislado.

---

## Checklist oficial

**Tarea 3.1 — Configure CLAUDE.md files with appropriate hierarchy, scoping, and modular organization** *(base; se completa en 3B)*

*Knowledge of*
- [x] La jerarquía de CLAUDE.md: user-level (`~/.claude/CLAUDE.md`), project-level (`.claude/CLAUDE.md` o `CLAUDE.md` en la raíz) y directory-level (CLAUDE.md en subcarpetas) → **Tema 5**
- [x] Lo de user-level aplica solo a ese usuario: no se comparte por control de versiones → **Tema 5** (Trampa 1)
- [~] La sintaxis de imports con `@` para mantener CLAUDE.md modular (estándares por paquete) → **Tema 7**. *Se amplía en 3B.*
- [~] `.claude/rules/` para organizar reglas por tema en vez de un CLAUDE.md monolítico → **Tema 7** (Trampa 4). *Se amplía en 3B.*

*Skills in*
- [x] Diagnosticar problemas de jerarquía (un compañero nuevo no recibe las instrucciones porque están en user-level) → **Temas 5 y 8** (Trampa 1)
- [~] Usar `@` para incluir selectivamente en el CLAUDE.md de cada paquete los estándares que le corresponden → **Tema 7**. *Se amplía en 3B.*
- [~] Partir un CLAUDE.md grande en archivos de tema en `.claude/rules/` (`testing.md`, `api-conventions.md`, `deployment.md`) → **Tema 7** (Trampa 4). *Se amplía en 3B.*
- [x] Usar `/memory` para verificar qué archivos de memoria están cargados y diagnosticar comportamiento inconsistente entre sesiones → **Tema 8** (Trampa 5)

**De otras tareas, presentado acá (se completan más adelante):** plan mode vs. ejecución directa y Explore subagent (3.4) → **Tema 14** (Trampa 11) · `/compact` en exploraciones largas (5.4) → **Tema 10** (Trampa 7).

**De la documentación, no de la guía** (vale saberlo; la guía no lo pregunta directo): managed policy y `CLAUDE.local.md`, concatenación (Tema 5) · límite de 4 niveles y "no ahorran contexto" de los imports (Tema 7) · `/context` (Temas 8 y 10) · scopes de settings y precedencia (Tema 12) · los seis permission modes (Tema 13).

**📘 Curso (útil para entender; lecciones 52–55 y deck 136):** agente vs. chat vs. plugin del IDE (Tema 1) · loop de 4 fases, Bash sin undo (Tema 2) · tabla de selección de tools y Agent tool (Tema 3) · "standing context", qué incluir y omitir (Tema 4) · `/init` como borrador y checklist de onboarding (Tema 6) · contexto como presupuesto (Tema 9) · compaction (Tema 10) · modos y rutas protegidas (Tema 13).

---

## Autoevaluación oral

1. ¿Por qué CLAUDE.md no sirve para garantizar que Claude nunca lea `.env`? ¿Qué usás en su lugar? ¿Y `.claudeignore`?
2. Nombrá los tres niveles de CLAUDE.md de la guía, dónde vive cada uno y quién lo recibe. Un compañero nuevo no ve tus convenciones: ¿qué pasó y cómo lo confirmás?
3. Tu CLAUDE.md tiene 700 líneas. ¿Qué dos herramientas te da la guía para organizarlo? ¿Los imports con `@` ahorran contexto?
4. ¿Cuándo usás `/compact` y cuándo `/clear`? ¿Qué pasa con el CLAUDE.md después de compactar?
5. ¿Cuándo plan mode y cuándo ejecución directa? ¿Para qué sirve el Explore subagent?

---

## Preguntas tipo examen

Las preguntas tipo examen de este capítulo están en [`04-practica/modulo-3.md`](../04-practica/modulo-3.md), junto con las del resto del módulo 3. Hacelas cuando termines **todos** los capítulos del módulo, de a una y sin mirar la respuesta.

---

## Revisión contra el blueprint oficial

Qué puede salir en el examen sobre lo de este capítulo que el curso de Jacob **no cubre o cubre flojo**, y dónde quedó explicado:

1. **`/memory`** (Skill 4 de 3.1). El curso no lo menciona. → Tema 8.
2. **Imports con `@` y `.claude/rules/`** (Knowledge 3 y 4, Skills 2 y 3). El curso de 3A no los trata. → Tema 7 (base; se completan en 3B).
3. **"User-level no se comparte por git" y el caso del compañero nuevo** (Knowledge 2, Skill 1). El curso no lo plantea como diagnóstico. → Temas 5 y 8.
4. **Plan mode vs. ejecución directa con el criterio de la guía y la Q5 oficial.** El curso presenta plan mode como un modo de permiso más. → Tema 14.
5. **Explore subagent** (3.4). No aparece en 3A. → Tema 14.
6. **Datos del curso que están mal:** `.claudeignore` (Tema 11), el orden hooks/permisos (Tema 12), "sin CLAUDE.md no hay memoria" (Tema 2), "team-level" y "precedence" de CLAUDE.md (Tema 5), "path-specific rules = CLAUDE.md por subcarpeta" (Tema 5), "plan mode no usa tools" (Tema 14).
7. **Lo que el curso da y la guía no evalúa:** los seis permission modes. Leelos para entender; no son el centro. → Tema 13.

