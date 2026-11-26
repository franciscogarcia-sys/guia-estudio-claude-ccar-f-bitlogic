# Capítulo 9 · 3B · Udemy 10 — CLAUDE.md Configuration Hierarchy (la jerarquía de configuración de CLAUDE.md)

*Tareas oficiales 3.1 (se completa) y 3.3 · Segundo capítulo del módulo 3*

---

## Dónde estamos

Seguimos en el **módulo 3: Claude Code Configuration & Workflows** (20% del examen). Este capítulo cubre:
- **3.1** Configure CLAUDE.md files with appropriate hierarchy, scoping, and modular organization (configurar los CLAUDE.md con la jerarquía, el alcance y la organización modular adecuados): **se completa acá** (en 3A viste la base).
- **3.3** Apply path-specific rules for conditional convention loading (aplicar reglas por ruta para cargar convenciones solo cuando corresponden). Pesa 3,33%.

### Cómo leer este capítulo

Todo lo que leés acá **vale para el examen**, salvo que diga lo contrario. Cuando algo sale solo del curso (útil para entender, pero no central), lo marco con **📘 Curso**. Cuando Jacob dice algo distinto de lo que evalúa la guía, aparece un recuadro así:

> ⚠️ **En el curso vas a escuchar otra cosa.** … **Para el examen: …**

### Un aviso sobre este capítulo

Las **slides** de 3B están muy bien y coinciden casi siempre con la documentación. El problema es el **companion** (el texto que acompaña los videos), que en tres puntos dice lo contrario que las slides: que el CLAUDE.md del proyecto "pisa" al del usuario cuando se contradicen, que `.claudeignore` sirve para excluir archivos y que existe un nivel "team". Además, el companion no menciona `.claude/rules/` con `paths:`, que es justamente la respuesta oficial de la tarea 3.3 (pregunta de muestra Q6). En cada tema te marco qué responder.

## De dónde venimos

En **3A** viste que CLAUDE.md es **contexto, no reglas impuestas**: Claude lo lee como guía, así que lo que tiene que cumplirse siempre va en una deny rule o un hook. Viste los tres niveles que nombra la guía: **user** (`~/.claude/CLAUDE.md`, solo vos), **project** (en el repo, para el equipo) y **directory** (en una subcarpeta). Aprendiste que **`/memory`** muestra qué archivos se cargaron, que para no tener un CLAUDE.md gigante se usan imports con **`@ruta`** y **`.claude/rules/`** por tema, y que para excluir archivos se usan reglas **`Read` deny**, porque `.claudeignore` no tiene efecto.

Ahora completamos el cuadro: **en qué orden** se cargan los archivos, **qué pasa cuando dos niveles se contradicen**, **cuándo** se carga cada uno y cómo hacer que una convención se aplique **solo a ciertos archivos**, estén donde estén.

## Mapa del capítulo

**Parte 1 — La jerarquía completa (tarea 3.1).**
1. Los niveles: managed, user, project, local y directory.
2. Load order (orden de carga): qué lee Claude, cuándo y en qué orden.
3. Conflictos: no hay un nivel que "gane".
4. Diagnosticar: el fallo silencioso y `/memory`.

**Parte 2 — Convenciones por ruta (tarea 3.3).**

5. El CLAUDE.md de subdirectorio (directory-level).
6. Path-scoped rules (reglas por ruta): `.claude/rules/` con `paths:`.
7. Cómo leer los glob patterns (patrones de rutas).
8. Rules por ruta vs. CLAUDE.md de subdirectorio vs. skills vs. imports.
9. Compartir y recortar: imports, symlinks, rules de usuario y `claudeMdExcludes`.

**Parte 3 — Proteger archivos.**

10. Excluir archivos en serio: reglas deny en detalle.
11. Una directiva en CLAUDE.md no es una garantía.

**Parte 4 — Escribir instrucciones que Claude siga.**

12. Instrucciones efectivas: específicas, accionables y sin ambigüedad.
13. Patrones de CLAUDE.md para equipos reales.

---

# Parte 1 — La jerarquía completa

## Tema 1 — Los niveles: managed, user, project, local y directory

### Qué es

Un proyecto no tiene un solo CLAUDE.md: puede haber varios, cada uno en un lugar distinto y pensado para un público distinto. Lo que decide dónde va una instrucción es **a quién tiene que llegar**: a toda la empresa, a todo el equipo, solo a vos, o solo a quien toque cierta parte del código. Si la ponés en el lugar equivocado, le llega a quien no corresponde o no le llega a quien la necesita.

La guía evalúa **tres niveles**: user, project y directory. La documentación (y las slides del curso) muestran el cuadro completo, que agrega dos más: el **managed policy** (la política de la organización, un archivo que instala el área de IT en una ruta del sistema) y el **local** (`CLAUDE.local.md`, tus notas personales para un proyecto, que no se suben a git).

| Nivel | Dónde | Quién lo recibe | Qué va ahí |
|---|---|---|---|
| **Managed policy** (de la organización) | Ruta del sistema (la pone IT) | Toda la organización | Políticas de la empresa, seguridad, estándares obligatorios |
| **User** | `~/.claude/CLAUDE.md` | Solo vos, en todos tus proyectos | Tu estilo, cuánto detalle querés, tus preferencias |
| **Project** | `./CLAUDE.md` o `./.claude/CLAUDE.md` | Todo el equipo (git) | Convenciones compartidas, comandos, reglas de tests, anti-patterns del repo |
| **Local** | `./CLAUDE.local.md` (en `.gitignore`) | Solo vos, en este proyecto | Rutas de tu máquina, el nombre de tu base local |
| **Directory** | `CLAUDE.md` dentro de una subcarpeta | Todo el equipo (git) | Reglas de **esa** parte del código |

Lo más importante: los niveles **no se reemplazan entre sí, se suman**. Claude lee todos los que le corresponden y los junta en un solo texto. La documentación lo dice así: *"concatenated into context rather than overriding each other"*, y las slides: *"All scopes apply simultaneously - they're additive, not exclusive"*.

> ⚠️ **En el curso vas a escuchar otra cosa.** El companion y el glosario hablan de tres niveles: user, project y **"team"** (archivos compartidos entre proyectos con imports o symlinks). **Para el examen: los tres niveles son user / project / directory.** "Team" no es un nivel, sino una forma de **distribuir** un archivo (Tema 9); el nivel de la organización es el managed policy.

### Ejemplo

En TiendaX, cada instrucción está en el nivel de quien la necesita:
- **Managed** (lo pone IT): "Nunca incluir datos de tarjetas en logs".
- **User** de Lucas: "Explicame los cambios en español y con ejemplos cortos".
- **Project** (`storefront/CLAUDE.md`): "Montos en centavos. Tests con `npm test`".
- **Local** de Lucas: "Mi base de prueba es `tiendax_lucas_dev`".
- **Directory** (`storefront/infra/CLAUDE.md`): "Terraform: nunca destruir recursos de producción; siempre `plan` antes de `apply`".

### Para el examen

- Algo para **todo el equipo** → project (o directory si es de una carpeta).
- Algo **personal** → user (todos tus proyectos) o local (solo este proyecto).
- Algo **obligatorio para toda la organización** → managed policy.

### Cómo se une

Si todos los niveles se suman, importa **en qué orden** entran al contexto y **cuándo**.

---

## Tema 2 — Load order (orden de carga): qué lee Claude, cuándo y en qué orden

### Qué es

Cuando abrís Claude Code, antes de que escribas nada, arma su punto de partida: busca los CLAUDE.md que le corresponden y los pone uno detrás de otro, como si fueran un solo documento. Importa saber **cuáles** carga y **cuándo** por dos motivos. Lo que no se cargó, Claude no lo ve. Y lo que se cargó ocupa espacio en su memoria de trabajo (el **context**, contexto), aunque no lo use.

**En qué orden los pone.** Primero lo más general y al final lo más específico: el de la organización (managed), después el tuyo personal (user), después el del proyecto y al final tu `CLAUDE.local.md`. Si abrís Claude Code dentro de una subcarpeta, además sube carpeta por carpeta hasta la raíz y carga los CLAUDE.md que encuentra en el camino, ordenados desde la raíz hacia tu carpeta; dentro de cada carpeta, `CLAUDE.local.md` va después de `CLAUDE.md`. Así, lo más cercano a donde estás trabajando queda al final. Ojo: quedar al final **no** significa ganar. Si dos instrucciones se contradicen, Claude puede seguir cualquiera (lo ves en el Tema 3).

**Cuándo entra cada uno.** No todo se carga al arrancar. Los CLAUDE.md de tu carpeta y de las de arriba entran apenas abrís la sesión. Los de subcarpetas más abajo entran recién cuando Claude **abre un archivo** de esa subcarpeta. Esto se llama **carga bajo demanda** (**on demand**): Claude no gasta espacio en reglas de partes del código que quizás no toque en toda la sesión. La documentación lo dice así: *"Files in subdirectories load on demand when Claude reads files in those directories."* Y las slides: *"Being in the folder isn't enough; the read is what triggers the load"* (estar en la carpeta no alcanza: lo que dispara la carga es leer un archivo de ahí). Con las reglas de `.claude/rules/` pasa lo mismo: si tienen `paths:`, entran solo cuando Claude trabaja con un archivo que coincide (Tema 6); si no tienen, entran siempre.

| Archivo | Cuándo se carga |
|---|---|
| CLAUDE.md (y CLAUDE.local.md) de tu carpeta y de las de arriba | Al arrancar la sesión |
| CLAUDE.md de subcarpetas | Cuando Claude lee un archivo de esa subcarpeta |
| Rules de `.claude/rules/` **sin** `paths:` | Al arrancar la sesión |
| Rules **con** `paths:` | Cuando Claude trabaja con un archivo que coincide con el patrón |

> ⚠️ **En el curso vas a escuchar otra cosa.** El companion dice que todos los niveles se cargan juntos al inicio (*"all three levels load simultaneously at session start"*). **Para el examen: los de subcarpetas y las reglas con `paths:` se cargan bajo demanda.** Justamente eso es lo que evalúa la tarea 3.3.

### Ejemplo

Abrís Claude Code en `storefront/` y le pedís arreglar un bug del carrito. Al arrancar carga tu CLAUDE.md personal y el del proyecto (y, si existen, el managed y tu `storefront/CLAUDE.local.md`). El de `storefront/infra/` no lo carga: el carrito no tiene nada que ver con la infraestructura. Si más tarde le pedís revisar `infra/main.tf`, en el momento en que abre ese archivo entra también `infra/CLAUDE.md` con las reglas de Terraform.

### Para el examen

- Orden: managed → user → project → local; de la raíz hacia la carpeta actual.
- Subcarpetas y rules con `paths:` → **bajo demanda**, al trabajar con sus archivos.

### Cómo se une

Si el del proyecto se lee después del del usuario, ¿quiere decir que **gana** cuando se contradicen?

---

## Tema 3 — Conflictos: no hay un nivel que "gane"

### Qué es

No. Como los CLAUDE.md se suman en un solo texto, Claude no tiene una regla fija que diga "el del proyecto le gana al del usuario". Si en ese texto hay dos instrucciones opuestas, Claude ve las dos y elige una, y no siempre la misma. La documentación lo dice sin vueltas: *"If two rules contradict each other, Claude may pick one arbitrarily."* (Si dos reglas se contradicen, Claude puede elegir cualquiera.) Las slides del curso coinciden: *"On a genuine conflict there's no reliable precedence"* y *"Claude may pick either one"*.

**Qué hacer entonces.** Como no hay un orden confiable, la solución es **no dejar el conflicto escrito**: revisar los CLAUDE.md, sacar la regla que sobra o moverla al nivel correcto. Si de verdad hay una excepción, conviene escribirla de forma explícita en el CLAUDE.md del proyecto, por ejemplo: "En este repo usamos tabs, aunque tu configuración personal diga espacios". Así Claude no tiene que adivinar cuál aplicar.

📘 **Curso:** las slides distinguen dos casos. Las instrucciones **complementary** (complementarias) hablan de cosas distintas, como "User: sé conciso" y "Project: siempre agregar type hints"; se aplican las dos y no hay problema. Un **conflict** (conflicto real) es cuando el mismo comportamiento tiene instrucciones opuestas, como tabs vs. espacios; ahí hay que sacar una.

**El contraste con settings.json.** Acá está la trampa. En **settings.json** sí hay una precedencia estricta, que viste en 3A: managed > línea de comandos > local > project > user. Si dos niveles de settings definen el mismo valor, siempre gana el más alto. En CLAUDE.md eso no existe, porque no se eligen valores: se juntan textos.

| | ¿Hay un nivel que gana? |
|---|---|
| `settings.json` | **Sí**: el nivel más alto. Las reglas deny, además, se combinan y **una deny en cualquier nivel bloquea** |
| `CLAUDE.md` | **No**: se concatenan; ante una contradicción, Claude elige |

Un matiz de la documentación: para las **rules** sí habla de prioridad (*"User-level rules are loaded before project rules, giving project rules higher priority"*), pero la explica por el orden de lectura (lo del proyecto se lee último), no como una garantía.

> ⚠️ **En el curso vas a escuchar otra cosa.** El companion dice que el del proyecto pisa al del usuario (*"Project-level overrides user-level on conflicts because project config is version-controlled"*), y el deck 140 dice que las rules del proyecto *"win"* ("Loaded Second, Wins"). **Para el examen: CLAUDE.md no tiene un override determinista.** Si una opción elimina la contradicción (sacar la regla, moverla al nivel correcto), es la mejor; si una opción dice que un nivel de CLAUDE.md gana siempre, es falsa; y si la pregunta pide un nivel que gane de forma estricta, eso es **settings.json**.

### Ejemplo

El `~/.claude/CLAUDE.md` de Lucas dice "Usá punto y coma siempre". El del proyecto dice "Sin punto y coma (estilo Standard)". Claude ve las dos instrucciones juntas y a veces pone punto y coma y a veces no. Pensar "el del proyecto gana porque está en git" no sirve: no está garantizado. Lo que funciona es que Lucas saque esa regla de su user-level (o la limite a sus proyectos personales). El proyecto queda con una sola regla y Claude deja de dudar.

### Para el examen

- Conflicto entre niveles de CLAUDE.md → **resolverlo en los archivos**, no confiar en un orden.

### Cómo se une

Muchas veces el problema no es un conflicto, sino que una regla **no llega**. Y eso no avisa.

---

## Tema 4 — Diagnosticar: el fallo silencioso y `/memory`

### Qué es

Hay errores de configuración que no dan ningún aviso. El más común es poner los estándares del equipo en tu **user-level** (`~/.claude/CLAUDE.md`). En tu máquina todo funciona, porque ese archivo lo tenés vos; pero no está en el repo, así que a tus compañeros nunca les llega. No hay error ni advertencia: Claude simplemente no sabe esas reglas cuando trabaja con ellos. Las slides lo llaman el anti-pattern que **"silently fails"** (falla en silencio), y es el caso del compañero nuevo que viste en 3A. Otro anti-pattern del mismo tipo es dejar el CLAUDE.md del proyecto **fuera de git**.

Como el fallo no avisa, hace falta una forma de ver qué cargó Claude realmente:
- **`/memory`** lista los CLAUDE.md, CLAUDE.local.md y rules que están cargados. Es la respuesta de la guía para diagnosticar. La documentación lo resume así: *"If a file isn't listed, Claude can't see it."*
- **`/context`** muestra qué ocupa el contexto, incluidos los CLAUDE.md cargados.
- El **hook `InstructionsLoaded`** se dispara cada vez que se carga un CLAUDE.md o una rule, al arrancar o bajo demanda, e indica **por qué** se cargó: inicio de sesión, carpeta anidada, coincidencia con `paths:`, import o después de compactar. Sirve para **registrar** qué se carga y cuándo; no bloquea nada.

### Ejemplo

Sofía dice que Claude nunca aplica las reglas de Terraform. Mientras trabaja en `infra/`, corre `/memory`: aparece `storefront/CLAUDE.md`, pero no `infra/CLAUDE.md`. Revisando, ve que Claude todavía no había leído ningún archivo de `infra/`, y el CLAUDE.md de una subcarpeta se carga al **leer** un archivo, no al entrar (Tema 2). Le pide que abra `infra/main.tf`, vuelve a correr `/memory` y ahora sí aparece.

### Para el examen

- "Comportamiento inconsistente; ¿qué está cargado?" → **`/memory`**.
- Estándares del equipo en user-level → **fallo silencioso** → moverlos al proyecto.

### Cómo se une

Con la jerarquía completa, pasamos a la tarea 3.3: convenciones que se aplican **solo a ciertos archivos**.

---

# Parte 2 — Convenciones por ruta (tarea 3.3)

## Tema 5 — El CLAUDE.md de subdirectorio (directory-level)

### Qué es

Un `CLAUDE.md` dentro de una subcarpeta agrega reglas que valen **solo para esa parte del código**. Sirve para que las convenciones de, por ejemplo, la infraestructura no ocupen contexto mientras trabajás en el frontend. Tiene tres características:
- Usa **lazy-load** (carga diferida): se carga recién cuando Claude lee un archivo de esa carpeta (Tema 2).
- Es **augmentation, not replacement** (suma, no reemplaza): las reglas de las carpetas de arriba siguen activas.
- No hay que registrarlo en ningún lado: alcanza con crear el archivo.

📘 **Curso:** las slides dan casos típicos: `/frontend` (hooks de React, naming, orden de imports), `/tests` (fixtures de pytest, cobertura), `/infrastructure` (Terraform, nunca borrar recursos vivos) y `/generated` (no modificar; pero eso CLAUDE.md no lo puede garantizar, ver Tema 11).

**Su límite.** Este archivo está **atado a una carpeta** (*"directory-bound"*). Funciona muy bien cuando la convención es de **un área del árbol**, porque todo lo que la necesita vive ahí. Falla cuando la convención es de un **tipo de archivo** repartido por todo el repo, porque tendrías que copiar el mismo CLAUDE.md en cada carpeta, y esas copias terminan desincronizadas.

### Ejemplo

Las reglas de Terraform en `storefront/infra/CLAUDE.md` funcionan bien: todo el Terraform está en `infra/`, así que un solo archivo cubre todo. En cambio, las convenciones de tests no encajan: hay tests en `src/cart/`, `src/checkout/`, `src/catalog/` y decenas de carpetas más. Para cubrirlas con este mecanismo necesitarías 40 copias del mismo archivo, y apenas alguien cambie una, dejan de coincidir.

### Para el examen

- Convención de **una carpeta** → el CLAUDE.md de subdirectorio sirve.
- Convención de un **tipo de archivo en muchas carpetas** → no sirve: va el Tema 6.

### Cómo se une

Para el caso de archivos dispersos, la guía tiene una respuesta concreta.

---

## Tema 6 — Path-scoped rules (reglas por ruta): `.claude/rules/` con `paths:`

### Qué es

Una **path-scoped rule** es un archivo de `.claude/rules/` que se carga **solo cuando Claude trabaja con ciertos archivos**, estén en la carpeta que estén. Resuelve justo el problema del Tema 5: en vez de atar la convención a una carpeta, la atás a un **patrón de nombres** de archivo, como "todos los que terminan en `.test.tsx`".

Para eso, el archivo empieza con un **frontmatter YAML**: un bloque de configuración entre dos líneas `---` al principio. Ahí va el campo **`paths:`**, una lista de **glob patterns** (patrones de rutas, Tema 7). Mientras Claude no toque un archivo que coincida, la rule no ocupa contexto. La guía lo describe en sus palabras: *".claude/rules/ files with YAML frontmatter paths fields containing glob patterns for conditional rule activation"*, y destaca el beneficio: *"How path-scoped rules load only when editing matching files, reducing irrelevant context and token usage"* (se cargan solo al editar archivos que coinciden, y así se reduce el contexto irrelevante y los tokens).

### Cómo se configura

`.claude/rules/testing.md`:

```markdown
---
paths:
  - "**/*.test.tsx"
  - "**/*.test.ts"
---

# Convenciones de tests

- Usar React Testing Library; nunca Enzyme.
- Un `describe` por componente; nombres de test en español: "muestra el precio en pesos".
- Mockear `fetch` con `msw`; nunca llamar a la API real.
```

`.claude/rules/terraform.md` (con la forma corta de la lista y el ejemplo literal de la guía; en TiendaX sería `["infra/**/*"]`):

```markdown
---
paths: ["terraform/**/*"]
---

- Siempre `terraform plan` antes de `apply`.
- Todo recurso lleva los tags `team` y `env`.
```

Detalles que conviene saber:
- La clave es **`paths`**. No `globs`, ni `include`, ni `pattern`.
- Podés poner varios patrones y usar llaves (**brace expansion**, expansión de llaves): `"src/**/*.{ts,tsx}"` cubre TypeScript y TSX.
- **Sin `paths:`**, la rule se carga **siempre** al arrancar, igual que el CLAUDE.md del proyecto: organiza, pero no ahorra contexto.
- Claude Code también busca rules en subcarpetas de `.claude/rules/` (`.claude/rules/frontend/`, `.claude/rules/backend/`).

**"Editing" vs. "reads".** La guía dice que la rule se carga *"when editing matching files"* (al editar), y la documentación dice *"trigger when Claude reads files matching the pattern"* (al leer). En la práctica es lo mismo, porque para editar un archivo Claude primero lo lee. En el examen, "editing" es correcto: no descartes una opción por esa palabra.

### Ejemplo

Lucas le pide a Claude: "Agregá un test para `PriceTag`". Claude abre `src/catalog/PriceTag.test.tsx`. Ese nombre coincide con `**/*.test.tsx`, así que la rule de tests entra al contexto y Claude escribe el test con React Testing Library y `msw`. Si en cambio Lucas le pide arreglar un estilo CSS, Claude nunca abre un archivo de test, la rule nunca se carga y no ocupa contexto.

### Para el examen

- Convención por **tipo de archivo**, en cualquier carpeta → **`.claude/rules/` con `paths:`**.
- Beneficio que nombra la guía: **menos contexto irrelevante y menos tokens**.

### Cómo se une

Todo depende de escribir bien el patrón. Un `**` de menos y la rule nunca se carga.

---

## Tema 7 — Cómo leer los glob patterns (patrones de rutas)

### Qué es

Un **glob** es un patrón que describe un conjunto de rutas de archivos usando comodines. Hace falta leerlos con cuidado porque una diferencia mínima cambia qué archivos coinciden, y si el patrón no coincide, la rule no se carga y nada te avisa. Hay tres piezas:
- **`*`** reemplaza cualquier texto **dentro de un solo nivel** de carpeta.
- **`**`** reemplaza cualquier cantidad de carpetas (cero o más niveles).
- **`{a,b}`** significa una de las opciones.

La tabla de la documentación, con ejemplos:

| Patrón | Qué coincide |
|---|---|
| `**/*.ts` | Todos los `.ts`, **en cualquier carpeta** |
| `src/**/*` | Todos los archivos debajo de `src/` |
| `*.md` | Los `.md` **solo de la raíz** del proyecto |
| `src/components/*.tsx` | Los `.tsx` de esa carpeta (no de sus subcarpetas) |
| `src/**/*.{ts,tsx}` | `.ts` y `.tsx` debajo de `src/` |
| `**/*.test.tsx` | Todos los tests de React, **estén donde estén** (ejemplo de la guía) |

El error típico es escribir `*.test.tsx` sin `**/` adelante. Como `*` no cruza carpetas, ese patrón solo coincide con tests que estén en la **raíz** del proyecto. Para cubrir todo el repo hace falta `**/*.test.tsx`.

### Ejemplo

| Archivo | `**/*.test.tsx` | `*.test.tsx` | `src/**/*` |
|---|---|---|---|
| `Button.test.tsx` (en la raíz) | ✅ | ✅ | ❌ |
| `src/cart/Cart.test.tsx` | ✅ | ❌ | ✅ |
| `src/cart/Cart.tsx` | ❌ | ❌ | ✅ |

### Para el examen

- "Para todos los archivos de un tipo, en cualquier carpeta" → **`**/*.extensión`**.
- Ojo con las opciones que tienen el patrón sin `**/`.

### Cómo se une

Ya tenés todas las herramientas. La guía pregunta **cuál** elegir en cada situación.

---

## Tema 8 — Rules por ruta vs. CLAUDE.md de subdirectorio vs. skills vs. imports

### Qué es

Hay varias formas de darle a Claude una convención, y la tarea 3.3 se decide eligiendo la correcta. Para elegir, hacete tres preguntas: **cuándo** entra al contexto, si sirve para archivos **repartidos** por muchas carpetas y si **ahorra tokens**. La única que responde bien a las tres es la rule con `paths:`.

| Mecanismo | Cuándo entra al contexto | ¿Sirve para archivos dispersos? | ¿Ahorra tokens? |
|---|---|---|---|
| CLAUDE.md raíz con secciones por área | Siempre | Depende de que Claude **infiera** qué sección aplica | No |
| CLAUDE.md de subdirectorio | Al leer archivos **de esa carpeta** | **No**: atado a la carpeta | Sí, por carpeta |
| `.claude/rules/` **sin** `paths:` | Siempre | Igual que el CLAUDE.md raíz | No (solo organiza) |
| **`.claude/rules/` con `paths:`** | Al trabajar con archivos que **coinciden con el glob** | **Sí** | **Sí** |
| Import con `@ruta` | Siempre, junto con el archivo que lo importa | No | **No** |
| Skill | La descripción siempre; el contenido cuando se invoca o Claude decide usarla | No es automática ni determinista | Sí |

Las slides lo resumen en una frase: *"Pattern scope crosses folders; a subdirectory file cannot"* (el alcance por patrón cruza carpetas; un archivo de subcarpeta no puede).

**Rule vs. skill.** Una **rule** es una **convención permanente**: cómo se escribe cierto código, cada vez que se toca. Una **skill** es un **procedimiento o material que se usa a veces** (un checklist de deploy, una guía de la API) y se carga cuando alguien la invoca o cuando Claude decide que viene al caso; por eso no sirve si la convención tiene que aplicarse siempre. Un matiz nuevo: las skills también aceptan un campo `paths`. No cambia la respuesta: para **convenciones de código**, la guía elige **rules**.

### La pregunta oficial Q6

**Situación:** el codebase tiene áreas con convenciones distintas (componentes React con hooks, handlers de API con async/await y manejo de errores, modelos con patrón repositorio). Los tests están **repartidos por todo el código**, al lado del archivo que prueban (`Button.test.tsx` junto a `Button.tsx`), y todos tienen que seguir las mismas convenciones. ¿Cuál es la forma **más mantenible** de que Claude aplique **automáticamente** la convención correcta?

- ✅ **A:** rules en `.claude/rules/` con frontmatter YAML y glob patterns, para aplicar las convenciones según la ruta del archivo. La explicación oficial: funcionan *"regardless of directory location—essential for test files spread throughout the codebase"*.
- ❌ **B:** todo en el CLAUDE.md raíz con encabezados por área. Depende de que Claude adivine qué sección aplica: *"relies on inference rather than explicit matching"*.
- ❌ **C:** una skill por tipo de código. Hay que invocarla o esperar que Claude decida cargarla (*"requires manual skill invocation or relies on Claude choosing to load them"*), y el enunciado pide aplicación **automática y determinista**.
- ❌ **D:** un CLAUDE.md en cada subcarpeta. Está atado a la carpeta (*"CLAUDE.md files are directory-bound"*), así que no maneja archivos repartidos.

**Palabras del enunciado que llevan a A:** *"spread throughout"*, *"regardless of location"*, *"automatically"*, *"most maintainable"*.

### Para el examen

- Tipo de archivo en muchas carpetas → **rule con `paths:`**.
- Un área de una carpeta → sirven el CLAUDE.md de subdirectorio y una rule con `paths: ["infra/**/*"]`. Si el enunciado habla de archivos **dispersos**, rule.
- Querés **menos tokens** → rules **con** `paths:`. No imports ni rules sin `paths:`.
- Procedimiento que se usa a veces → **skill**.

### Cómo se une

Quedan herramientas para **compartir** configuración entre repos y **recortar** lo que sobra en un monorepo.

---

## Tema 9 — Compartir y recortar: imports, symlinks, rules de usuario y `claudeMdExcludes`

### Qué es

**Imports con `@ruta`** (lo que la guía llama "@import"). Como viste en 3A, un import trae el contenido de otro archivo al CLAUDE.md: las rutas relativas se resuelven desde el archivo que importa y se puede anidar hasta 4 niveles. Ojo: **no ahorran contexto**, porque lo importado se carga junto con el archivo que lo importa. Para lo que sirven es para **elegir qué estándares lleva cada paquete**. La guía los usa así: cada paquete incluye en su CLAUDE.md los estándares que le corresponden, según lo que saben sus mantenedores.

```markdown
# packages/pagos/CLAUDE.md
@../../standards/seguridad-pci.md
@../../standards/api-conventions.md
```
```markdown
# packages/catalogo/CLAUDE.md
@../../standards/api-conventions.md
@../../standards/imagenes.md
```

**Compartir reglas entre repos.** Cuando varios repos tienen que seguir las mismas reglas, copiarlas a mano hace que se desincronicen. La documentación ofrece tres formas de compartirlas:
- **Symlinks** (enlaces simbólicos) dentro de `.claude/rules/`: el archivo vive en un solo lugar y cada repo lo enlaza, por ejemplo `ln -s ~/estandares-tiendax/seguridad.md .claude/rules/seguridad.md`.
- **Rules de usuario** en `~/.claude/rules/`: aplican en todos tus proyectos y se cargan antes que las del proyecto.
- Un **plugin** (un paquete instalable de Claude Code con rules, skills y hooks), cuando varios repos necesitan un set completo.

Esto es lo que el curso llama "team-level", pero es una forma de **distribuir** archivos, no un nivel nuevo (Tema 1).

**Recortar en un monorepo con `claudeMdExcludes`.** Un **monorepo** es un solo repositorio con varios paquetes, a veces de equipos distintos. Ahí puede haber CLAUDE.md o rules de otros equipos que no te sirven y solo ocupan contexto. **`claudeMdExcludes`** es un setting que recibe patrones glob, aplicados sobre **rutas absolutas**, con los archivos que **no querés cargar**:

```json
{
  "claudeMdExcludes": [
    "**/monorepo/packages/legacy-billing/CLAUDE.md",
    "/home/lucas/monorepo/packages/legacy-billing/.claude/rules/**"
  ]
}
```

Se puede poner en cualquier nivel de settings; lo típico es `.claude/settings.local.json`, porque es una preferencia tuya. Hay una excepción: el archivo de la organización no se puede excluir (*"Managed policy CLAUDE.md files cannot be excluded."*).

Otro detalle de los monorepos: los `.claude/settings.json` **no se heredan** de la carpeta padre. Si arrancás Claude Code en un subpaquete, no ves el `settings.json` de la raíz.

### Ejemplo

El monorepo de TiendaX tiene `packages/pagos`, `packages/catalogo` y `packages/legacy-billing`, este último de otro equipo y con un CLAUDE.md enorme que no le sirve a Lucas. Lucas trabaja en pagos. Su `packages/pagos/CLAUDE.md` importa con `@` el estándar PCI, así que Claude lo tiene apenas arranca. El CLAUDE.md de `legacy-billing` no se carga al arrancar en `pagos`, pero entraría apenas Claude lea un archivo de ese paquete (Tema 2). Para evitarlo, Lucas lo excluye con `claudeMdExcludes` en su `.claude/settings.local.json`.

### Para el examen

- Estándares distintos por paquete → **`@ruta` en el CLAUDE.md de cada paquete**.
- CLAUDE.md de otros equipos que molestan en un monorepo → **`claudeMdExcludes`**.

### Cómo se une

Hasta acá, todo era **qué le decimos** a Claude. La Parte 3 es **qué no puede tocar**.

---

# Parte 3 — Proteger archivos

## Tema 10 — Excluir archivos en serio: reglas deny en detalle

### Qué es

Como viste en 3A, para que Claude no lea un archivo se usa una regla **`Read(...)`** en **`permissions.deny`** (la lista de permisos denegados de settings.json). Es la única forma real: Claude Code la hace cumplir, en vez de pedirle a Claude que se porte bien. Acá vemos los detalles que pueden aparecer en el examen.

**Los "tres mitos".** Las slides los listan y coinciden con la documentación. Primero, no existe `.claudeignore` (*"and there never has been"*). Segundo, **`.gitignore` no limita** lo que Claude puede leer: solo le dice a git qué no versionar. Tercero, no hay una variable de entorno para ignorar archivos.

**Sintaxis.** Las reglas `Read(...)` y `Edit(...)` usan la misma sintaxis de patrones que `.gitignore`. Lo delicado es desde dónde se cuenta cada ruta:

| Regla | Qué bloquea |
|---|---|
| `Read(./.env)` | El `.env` relativo a la carpeta actual |
| `Read(.env)` o `Read(**/.env)` | Cualquier `.env`, a cualquier profundidad |
| `Read(./secrets/**)` | Todo lo que está debajo de `secrets/` |
| `Read(~/.ssh/**)` | Esa ruta, desde tu home |
| `Read(//etc/secret)` | Ruta **absoluta** (con doble barra) |

Ojo con `/ruta` con una sola barra: **no** es absoluta, sino relativa a **la fuente de settings** (en los settings del proyecto, la raíz del proyecto).

**Qué cubre y qué no.** La regla deny la hace cumplir Claude Code, así que solo alcanza a lo que Claude Code puede ver:
- **Cubre** las tools de archivos de Claude (Read, Edit…), los comandos de Bash que Claude Code reconoce (`cat`, `head`, `tail`, `sed`, `tee`) y las redirecciones.
- Cubre como **best-effort** (mejor esfuerzo, sin garantía) Grep, Glob y las menciones `@archivo`.
- **No cubre** un comando que lee sin nombrar el archivo (`grep -r … .`) ni un **script** (Python, Node) que abre el archivo por su cuenta. Para eso hace falta un **sandbox** (un aislamiento a nivel sistema operativo que limita lo que puede tocar cualquier proceso).

**Settings vs. permisos.** En los settings comunes gana el nivel más alto (Tema 3), pero **las reglas de permisos se combinan** entre todos los niveles, y **una deny en cualquier nivel, aunque sea de usuario, bloquea** una allow de otro nivel. Así nadie puede abrir por accidente lo que otro nivel cerró.

📘 **Curso:** según las slides, lo primero que conviene proteger es `.env` y `.env.*`, las carpetas de secretos, `~/.ssh/` y las credenciales de la nube: *"Credential exposure is the highest-value reason to write deny rules."*

> ⚠️ **En el curso vas a escuchar otra cosa.** El companion recomienda excluir `node_modules` y `.git` "por performance" con `.claudeignore`. **Para el examen: `.claudeignore` no tiene efecto, y las deny son por seguridad, no por performance.** Claude Code no carga el repo entero al contexto, sino que lee archivos cuando los necesita; para ahorrar contexto se usan rules con `paths:`.

### Ejemplo

`.claude/settings.json` de TiendaX:
```json
{
  "permissions": {
    "deny": [
      "Read(./.env)",
      "Read(./.env.*)",
      "Read(./secrets/**)",
      "Read(~/.aws/**)"
    ]
  }
}
```
Con esto, Claude no puede leer esos archivos con sus tools ni con `cat` (y con `@.env`, en la medida del mejor esfuerzo). Pero si Claude corre `python scripts/debug.py` y ese script abre `.env`, la regla no lo frena: Claude Code solo ve que se ejecutó un script, no qué archivos abrió adentro. Para ese caso hace falta el sandbox.

### Para el examen

- Excluir archivos → **`permissions.deny` con `Read(...)`**. Ni `.claudeignore` ni `.gitignore`.
- "Un script igual lee el secreto" → las deny no cubren subprocesos → **sandbox**.

### Cómo se une

Lo mismo vale para las directivas tipo "no edites esta carpeta" que el curso pone en CLAUDE.md.

---

## Tema 11 — Una directiva en CLAUDE.md no es una garantía

### Qué es

Escribir "nunca edites esta carpeta" en un CLAUDE.md no impide que Claude la edite. CLAUDE.md es contexto: Claude lo lee como una guía y puede decidir que en un caso concreto no aplica. La documentación es tajante: *"An instruction like 'never edit .env' in CLAUDE.md or a skill is a request, not a guarantee."* (Es un pedido, no una garantía.) Y agrega: *"If something has to happen every time, make it a hook, a deny rule, or a managed setting. CLAUDE.md is for guidelines, and Claude is allowed to decide a guideline doesn't apply."*

**La regla para decidir.** La documentación da un criterio simple: *"a hook is for a rule with zero exceptions"* (un hook es para una regla sin excepciones). Si la regla admite excepciones, va en CLAUDE.md, porque ahí Claude puede usar criterio; por ejemplo, "Preferí exports con nombre". Si no admite ninguna, va en una deny o un hook, porque solo eso se cumple siempre; por ejemplo, "Nunca editar `generated/`" se resuelve con una `Edit` deny.

> ⚠️ **En el curso vas a escuchar otra cosa.** El curso propone poner en CLAUDE.md directivas como *"never-delete constraints in /infrastructure"* o *"a single no-edit directive in /generated"*, y algunas slides dicen que eso queda "enforced" o "blocked by directive". **Para el examen: una directiva en CLAUDE.md es un pedido; la garantía es una deny rule, un hook o el managed policy.** Las propias slides del curso, en otras páginas, coinciden: el enforcement real es el managed policy, las deny rules y el sandbox.

### Ejemplo

TiendaX genera el cliente de la API en `src/generated/`, y cualquier edición a mano se pierde en el próximo build. La solución tiene dos partes. Como **guía**, en CLAUDE.md: "Si hace falta cambiar el cliente de la API, modificá `openapi.yaml` y corré `npm run codegen`". Como **garantía**, en settings: `"deny": ["Edit(./src/generated/**)"]`. Las dos juntas son lo ideal: la deny **impide** el error y el CLAUDE.md le dice a Claude **qué hacer en su lugar**, para que no se quede trabado.

### Para el examen

- Enunciado con "must never", "ensure", "guarantee" → **deny rule o hook**.
- Enunciado que pide **guiar** una convención → CLAUDE.md o una rule.

### Cómo se une

Lo que sí va en CLAUDE.md tiene que estar bien escrito para que Claude lo siga.

---

# Parte 4 — Escribir instrucciones que Claude siga

## Tema 12 — Instrucciones efectivas: específicas, accionables y sin ambigüedad

### Qué es

Que una instrucción esté cargada no alcanza: tiene que estar escrita de forma que Claude la siga siempre igual. Una instrucción vaga, como "formateá bien el código", deja que Claude decida qué significa "bien", y cada vez puede decidir distinto. El curso define una buena instrucción como **specific, actionable, unambiguous** (específica, que se pueda llevar a la acción y con un solo significado). La documentación coincide: *"write instructions that are concrete enough to verify"* (lo bastante concretas como para poder verificarlas).

| ❌ Vaga | ✅ Concreta |
|---|---|
| "Formateá bien el código" | "Indentación de 2 espacios" |
| "Probá tus cambios" | "Corré `npm test` antes de cada commit" |
| "Mantené los archivos ordenados" | "Los handlers de la API van en `src/api/handlers/`" |
| "Usá una versión moderna de Node" | "Node 22 LTS" |

**La forma también importa.** Claude lee la estructura igual que una persona (*"Claude scans structure the same way readers do"*), así que una regla enterrada en un párrafo se pierde fácil, sobre todo después de compactar la conversación. Por eso conviene:
- usar **encabezados y viñetas**, no párrafos;
- escribir **una directiva por línea**, agrupadas por tema (Comandos, Estilo, Tests, Git, Seguridad);
- mantener el archivo en **menos de 200 líneas**; si crece, pasar lo específico a rules con `paths:`.

**Qué no poner.** Todo lo que sobra alarga el archivo y diluye lo importante:
- **Conocimiento general** (sintaxis de Python, qué es REST, cómo usar git): Claude ya lo sabe.
- **Lo que ya controla el linter o el formatter**: tener la misma regla en dos lugares crea *"conflicting sources of truth"* (dos fuentes de verdad que se contradicen). El formatter se corre con un **hook PostToolUse** (un hook que se ejecuta después de cada uso de una herramienta), no como instrucción.
- **Énfasis apilado** ("IMPORTANT", "YOU MUST", mayúsculas): según la documentación, *"piling on emphasis mostly makes Claude over-apply the rule. If it's a rule that can't bend, turn it into a hook or a deny rule."* (Apilar énfasis hace que Claude aplique la regla de más; si no admite excepciones, va en un hook o una deny.)
- **Contradicciones** (Tema 3).

**Cuándo agregar algo.** Cuando Claude comete **el mismo error por segunda vez**, cuando un code review encuentra algo que Claude debería haber sabido, cuando escribís la misma corrección que en la sesión anterior, o cuando un compañero nuevo necesitaría ese dato para trabajar.

### Ejemplo

**Antes:**
> Es muy importante que el código sea de calidad y siga buenas prácticas. Tratá de escribir tests y de mantener el estilo del proyecto. IMPORTANTE: NUNCA uses float para la plata.

**Después:**
```markdown
## Dinero
- Montos en centavos, tipo `int` (`priceCents`). Nunca `float`.

## Tests
- `npm test -- --runInBand` antes de cada commit.
- Todo componente nuevo lleva un `.test.tsx` al lado.
```

La versión de antes no le dice a Claude qué hacer en concreto, y el "IMPORTANTE" en mayúsculas no agrega información. La de después tiene reglas que se pueden verificar, una por línea y bajo un encabezado.

### Para el examen

- Claude ignora una regla → primero: ¿es **vaga**? ¿el archivo es **largo**? ¿hay una **contradicción**? Si la regla no admite excepciones → hook o deny.
- ❌ "Ponerla en mayúsculas y con IMPORTANT".

### Cómo se une

Último tema: qué suelen poner los equipos reales.

---

## Tema 13 — Patrones de CLAUDE.md para equipos reales

### Qué es

📘 **Curso:** el curso propone qué conviene codificar según el tipo de equipo. Sirve como lista de ideas a la hora de armar un CLAUDE.md:
- **Frontend:** naming (PascalCase para componentes), metodología de CSS, manejo de estado, accesibilidad.
- **Backend:** diseño de la API, ORM vs. SQL directo, manejo de errores.
- **Full-stack:** tipos compartidos, estructura del monorepo, límites entre servicios.
- **Seguridad:** nada de credenciales en el código, política de `.env`, uso del vault, autenticación. Según el curso, son *"the highest-value entries"* (las entradas que más valen).
- **Tests:** `.test` vs. `.spec`, cobertura, fixtures, mocks.

La documentación agrega lo que no puede faltar en ningún equipo: los comandos exactos (test, lint, build), los lugares donde el código engaña y las decisiones que no están escritas en el repo.

### Ejemplo

Así queda organizado TiendaX después de este capítulo, con cada cosa en el mecanismo que le corresponde:

```
storefront/
├── CLAUDE.md                  # comandos, dinero en centavos, seguridad (corto)
├── CLAUDE.local.md            # (gitignored) la base local de cada uno
├── .claude/
│   ├── settings.json          # deny: .env, secrets/**; Edit deny: src/generated/**
│   └── rules/
│       ├── testing.md         # paths: ["**/*.test.tsx", "**/*.test.ts"]
│       ├── api.md             # paths: ["src/api/**/*"]
│       └── react.md           # paths: ["src/**/*.tsx"]
└── infra/
    └── CLAUDE.md              # Terraform: plan antes de apply, tags obligatorios
```

### Para el examen

- No se pregunta "qué patrón usa un equipo de frontend". Lo que sí se pregunta es **dónde va cada cosa** y **cómo se carga** (Temas 1–11).

### Cómo se une

Cierra el capítulo y la tarea 3.1. Con la configuración resuelta, en 3C vas a ver cómo **extender** Claude Code: comandos, skills y subagentes.

---

## Cómo se une todo

1. Niveles: **managed → user → project → local**, más **directory** (subcarpeta). La guía evalúa **user / project / directory** (Tema 1).
2. De la carpeta actual para arriba → **al arrancar**. Subcarpetas y rules con `paths:` → **bajo demanda**, al trabajar con sus archivos (Tema 2).
3. Los CLAUDE.md **se suman**: no hay un nivel que gane. Ante un conflicto, **sacarlo de los archivos**. La precedencia estricta es de **settings.json** (Tema 3).
4. Estándares en user-level = **fallo silencioso**; diagnosticar con **`/memory`** (Tema 4).
5. El CLAUDE.md de subdirectorio está **atado a una carpeta** (Tema 5).
6. **`.claude/rules/` con `paths:`** = convención por tipo de archivo, en cualquier carpeta, cargada solo cuando hace falta (Tema 6).
7. **`**/*.test.tsx`** coincide en todo el repo; `*.test.tsx` solo en la raíz (Tema 7).
8. Q6: archivos dispersos → **rules con `paths:`**; ni CLAUDE.md por carpeta, ni skills, ni secciones en el raíz. Los imports no ahorran tokens (Tema 8).
9. Estándares por paquete → **`@ruta`**; CLAUDE.md de otros equipos → **`claudeMdExcludes`** (Tema 9).
10. Excluir → **`Read` deny** (no `.claudeignore`, no `.gitignore`); los scripts necesitan sandbox (Tema 10).
11. "Nunca" en CLAUDE.md es un pedido; la garantía es **deny o hook** (Tema 11).
12. Instrucciones **concretas**, en viñetas, cortas, sin énfasis apilado (Tema 12).

## Lo que viene

**3C · Udemy 11 — Commands, Skills, and Subagents:** slash commands, skills, subagentes y, en detalle, **plan mode vs. ejecución directa** (tareas 3.2, 3.4 y 3.5).

---

## Las trampas del examen

Cada trampa tiene el mismo orden: la situación, **qué elegir en el examen (✅)**, las opciones que tientan (❌) con por qué tientan y por qué están mal, y una regla para recordar.

### Grupo: Jerarquía y conflictos

#### Trampa 1 · "El del proyecto gana"

**La situación.** El `~/.claude/CLAUDE.md` de un dev dice una cosa y el del proyecto, la contraria; Claude a veces sigue una y a veces la otra (Tema 3).

**✅ En el examen elegí:** **eliminar la contradicción**: sacar la regla del user-level (o dejar explícita la excepción en el CLAUDE.md del proyecto).

**❌ Las que tientan:**

❌ **"No hace falta hacer nada: el CLAUDE.md del proyecto tiene precedencia porque está versionado".**
- *Tienta porque:* lo dice el companion del curso y el del proyecto se lee después.
- *Está mal porque:* los CLAUDE.md se concatenan; ante una contradicción, *"Claude may pick one arbitrarily"*.

❌ **"Repetir la regla del proyecto con IMPORTANT".**
- *Tienta porque:* parece que le da más peso.
- *Está mal porque:* el conflicto sigue escrito, y apilar énfasis hace que Claude aplique la regla de más.

> 🧠 **Para recordar:** CLAUDE.md se suma; los conflictos se arreglan en los archivos.

#### Trampa 2 · Todos los CLAUDE.md cargan al arrancar

**La situación.** Una opción dice que el CLAUDE.md de `infra/` se carga apenas abrís Claude Code en la raíz (Tema 2).

**✅ En el examen elegí:** los CLAUDE.md de **subcarpetas** cargan **bajo demanda**, cuando Claude lee archivos de esa carpeta.

**❌ Las que tientan:**

❌ **"Todos los niveles se cargan juntos al inicio de la sesión".**
- *Tienta porque:* lo dice el companion.
- *Está mal porque:* solo los de la carpeta actual para arriba cargan al inicio.

❌ **"El de `infra/` carga apenas entrás a trabajar en esa carpeta".**
- *Tienta porque:* el glosario del curso dice "when operating in that directory".
- *Está mal porque:* lo que dispara la carga es que Claude **lea un archivo** de ahí.

> 🧠 **Para recordar:** subcarpeta = carga al leer un archivo de ahí.

### Grupo: Elegir el mecanismo (3.3)

#### Trampa 3 · Tests repartidos por todo el repo (Q6)

**La situación.** Los `*.test.tsx` están al lado de cada componente, en decenas de carpetas, y todos tienen que seguir las mismas convenciones (Temas 6 y 8).

**✅ En el examen elegí:** **una rule en `.claude/rules/` con `paths: ["**/*.test.tsx"]`**.

**❌ Las que tientan:**

❌ **"Un CLAUDE.md en cada carpeta que tenga tests".**
- *Tienta porque:* el CLAUDE.md de subdirectorio es oficial y se carga solo donde hace falta.
- *Está mal porque:* está atado a la carpeta: tendrías decenas de copias que se desincronizan.

❌ **"Una skill de testing".**
- *Tienta porque:* se carga solo cuando hace falta.
- *Está mal porque:* depende de que alguien la invoque o de que Claude decida usarla; el enunciado pide aplicación **automática**.

❌ **"Una sección 'Tests' en el CLAUDE.md raíz".**
- *Tienta porque:* es lo más simple.
- *Está mal porque:* depende de que Claude infiera cuándo aplica, y ocupa contexto siempre.

> 🧠 **Para recordar:** tipo de archivo disperso → rule con `paths:`.

#### Trampa 4 · Imports para ahorrar tokens

**La situación.** El CLAUDE.md consume mucho contexto y alguien propone partirlo en archivos importados con `@` "para cargar menos" (Temas 8 y 9).

**✅ En el examen elegí:** **rules con `paths:`** para lo que aplica a una parte del código.

**❌ Las que tientan:**

❌ **"Partirlo en imports con `@`".**
- *Tienta porque:* es la sintaxis modular que nombra la guía.
- *Está mal porque:* los archivos importados se cargan igual al arrancar.

❌ **"Pasarlo todo a `.claude/rules/` sin `paths:`".**
- *Tienta porque:* "rules" suena a carga condicional.
- *Está mal porque:* sin `paths:` se cargan siempre, igual que el CLAUDE.md.

> 🧠 **Para recordar:** organizar → imports o rules; **ahorrar** → rules **con** `paths:`.

#### Trampa 5 · El glob que no coincide

**La situación.** La rule de tests tiene `paths: ["*.test.tsx"]` y nunca se carga cuando Claude edita `src/cart/Cart.test.tsx` (Tema 7).

**✅ En el examen elegí:** cambiar el patrón a **`**/*.test.tsx`**.

**❌ Las que tientan:**

❌ **"Cambiar la clave a `globs:`".**
- *Tienta porque:* otras herramientas (como Cursor) usan esa clave.
- *Está mal porque:* en Claude Code la clave es `paths`; el problema es el patrón.

> 🧠 **Para recordar:** sin `**/` adelante, solo la raíz.

#### Trampa 6 · Estándares distintos por paquete

**La situación.** En el monorepo, el paquete de pagos tiene que seguir el estándar PCI y el de catálogo no; los mantenedores de cada paquete saben qué estándares le corresponden (Tema 9).

**✅ En el examen elegí:** **importar con `@` en el CLAUDE.md de cada paquete** los estándares que le corresponden.

**❌ Las que tientan:**

❌ **"Poner todos los estándares en el CLAUDE.md raíz".**
- *Tienta porque:* queda todo en un lugar.
- *Está mal porque:* cada paquete carga estándares que no le aplican; la guía pide incluirlos **selectivamente**.

> 🧠 **Para recordar:** estándar por paquete → `@ruta` en ese paquete.

### Grupo: Proteger archivos

#### Trampa 7 · `.gitignore` como protección

**La situación.** `.env` está en `.gitignore` y alguien asume que Claude no lo va a leer (Tema 10).

**✅ En el examen elegí:** **`Read(./.env)` en `permissions.deny`**.

**❌ Las que tientan:**

❌ **"Ya está protegido porque está en `.gitignore`".**
- *Tienta porque:* Grep, por ejemplo, saltea lo que está en `.gitignore`.
- *Está mal porque:* `.gitignore` no limita lo que Claude puede leer.

❌ **"Agregarlo a `.claudeignore`".**
- *Tienta porque:* lo recomienda el companion.
- *Está mal porque:* según la documentación no tiene efecto.

> 🧠 **Para recordar:** la única exclusión real es `Read` deny.

#### Trampa 8 · El script que lee el secreto

**La situación.** Hay `Read(./.env)` en deny, pero un script de Python que Claude ejecuta abre `.env` y lo imprime (Tema 10).

**✅ En el examen elegí:** **sandbox** a nivel sistema operativo (las deny no cubren subprocesos que abren archivos por su cuenta).

**❌ Las que tientan:**

❌ **"Agregar `Read(**/.env)` además de `Read(./.env)`".**
- *Tienta porque:* parece que la regla no era lo bastante amplia.
- *Está mal porque:* el problema no es el patrón: las deny no alcanzan a un script que abre el archivo por su cuenta.

> 🧠 **Para recordar:** deny cubre las tools de Claude; los scripts, el sandbox.

#### Trampa 9 · "No editar `/generated`" en CLAUDE.md

**La situación.** Claude a veces edita `src/generated/`, y alguien propone un CLAUDE.md en esa carpeta con "NUNCA modificar estos archivos" (Tema 11).

**✅ En el examen elegí:** **`Edit(./src/generated/**)` en deny** (o un hook), y opcionalmente explicar en CLAUDE.md cómo regenerar.

**❌ Las que tientan:**

❌ **"Un CLAUDE.md de subdirectorio con la directiva en mayúsculas".**
- *Tienta porque:* el curso lo propone así.
- *Está mal porque:* es un pedido, no una garantía.

> 🧠 **Para recordar:** cero excepciones → deny o hook.

### Grupo: Escritura

#### Trampa 10 · Claude ignora una regla del CLAUDE.md

**La situación.** El CLAUDE.md tiene 600 líneas en párrafos y Claude ignora la regla de los centavos (Tema 12).

**✅ En el examen elegí:** **acortarlo y estructurarlo** (viñetas, una regla por línea, lo específico a rules con `paths:`), y escribir la regla de forma concreta.

**❌ Las que tientan:**

❌ **"Repetir la regla en tres secciones distintas".**
- *Tienta porque:* "si la ve más veces, la sigue".
- *Está mal porque:* alarga el archivo, que es justamente lo que baja la adherencia.

❌ **"Usar un modelo con más contexto".**
- *Tienta porque:* "así le entra todo".
- *Está mal porque:* el problema no es el espacio sino la adherencia: un archivo largo y en párrafos se respeta peor.

> 🧠 **Para recordar:** corto, concreto y en viñetas.

---

## Checklist oficial

**Tarea 3.1 — Configure CLAUDE.md files with appropriate hierarchy, scoping, and modular organization** *(se completa acá)*

*Knowledge of*
- [x] La jerarquía user / project / directory → **3A Tema 5 + 3B Temas 1, 2 y 5**
- [x] Lo de user-level no se comparte por git → **3A Tema 5 + 3B Tema 4** (Trampa 1 de 3A)
- [x] Imports con `@` para mantener CLAUDE.md modular (estándares por paquete) → **3A Tema 7 + 3B Tema 9** (Trampas 4 y 6)
- [x] `.claude/rules/` para reglas por tema en vez de un CLAUDE.md monolítico → **3A Tema 7 + 3B Tema 6**

*Skills in*
- [x] Diagnosticar problemas de jerarquía (compañero nuevo sin las instrucciones) → **3A Temas 5 y 8 + 3B Tema 4**
- [x] Usar `@` para incluir selectivamente los estándares de cada paquete → **3B Tema 9** (Trampa 6)
- [x] Partir un CLAUDE.md grande en `.claude/rules/` por tema (`testing.md`, `api-conventions.md`, `deployment.md`) → **3A Tema 7 + 3B Temas 6 y 13** (Trampa 10)
- [x] Usar `/memory` para ver qué archivos están cargados y diagnosticar comportamiento inconsistente → **3A Tema 8 + 3B Tema 4**

**Tarea 3.3 — Apply path-specific rules for conditional convention loading**

*Knowledge of*
- [x] Archivos de `.claude/rules/` con frontmatter YAML y un campo `paths` con glob patterns para activarlos condicionalmente → **Tema 6**
- [x] Las rules por ruta se cargan solo al editar archivos que coinciden, y así se reduce el contexto irrelevante y los tokens → **Temas 6 y 8** (Trampa 4)
- [x] La ventaja de las rules con glob sobre los CLAUDE.md de carpeta para convenciones que cruzan varias carpetas (tests repartidos) → **Tema 8** (Trampa 3)

*Skills in*
- [x] Crear rules con frontmatter `paths` (por ejemplo `paths: ["terraform/**/*"]`) para que se carguen solo al editar esos archivos → **Tema 6**
- [x] Usar glob patterns para aplicar convenciones por tipo de archivo, sin importar la carpeta (`**/*.test.tsx`) → **Temas 6 y 7** (Trampas 3 y 5)
- [x] Elegir rules por ruta en vez de CLAUDE.md de subdirectorio cuando las convenciones aplican a archivos repartidos por el código → **Tema 8** (Trampa 3)

**De la documentación, no de la guía** (vale saberlo; la guía no lo pregunta directo): managed policy y CLAUDE.local.md (Tema 1) · orden fino de carga (Tema 2) · prioridad de rules de proyecto sobre las de usuario (Tema 3) · hook `InstructionsLoaded` (Tema 4) · `paths` en skills (Tema 8) · symlinks, `~/.claude/rules/`, plugins, `claudeMdExcludes`, settings que no se heredan (Tema 9) · anclas de rutas y alcance de las deny (Tema 10).

**Del curso, coincide con la documentación** (lecciones 56–61 y deck 140): qué va en cada scope (Tema 1) · "silently fails" (Tema 4) · "pattern scope crosses folders" (Tema 8) · los tres mitos de exclusión (Tema 10) · specific/actionable/unambiguous, no duplicar el linter (Tema 12).

**📘 Curso (útil para entender):** complementarias vs. conflicto (Tema 3) · casos por carpeta (Tema 5) · qué proteger primero (Tema 10) · patrones por tipo de equipo (Tema 13).

---

## Autoevaluación oral

1. Nombrá los cinco niveles (cuatro scopes más directory) y en qué orden se cargan. ¿Cuáles cargan al arrancar y cuáles bajo demanda?
2. Tu user-level y el del proyecto se contradicen. ¿Cuál gana? ¿Qué hacés? ¿En qué se diferencia de settings.json?
3. Los tests están repartidos por todo el repo. ¿Qué mecanismo usás y por qué no un CLAUDE.md por carpeta, una skill o una sección en el raíz? Escribí el frontmatter.
4. ¿Qué diferencia hay entre `*.test.tsx` y `**/*.test.tsx`? ¿Los imports con `@` ahorran tokens? ¿Y las rules sin `paths:`?
5. ¿Cómo evitás que Claude lea `.env`? ¿Qué no cubre esa regla? ¿Por qué "NUNCA editar `/generated`" en CLAUDE.md no alcanza?

---

## Preguntas tipo examen

Las preguntas tipo examen de este capítulo están en [`04-practica/modulo-3.md`](../04-practica/modulo-3.md), junto con las del resto del módulo 3. Hacelas cuando termines **todos** los capítulos del módulo, de a una y sin mirar la respuesta.

---

## Revisión contra el blueprint oficial

Qué puede salir en el examen de 3.1 y 3.3 que el curso de Jacob **no cubre o cubre flojo**, y dónde quedó explicado:

1. **`.claude/rules/` con `paths:`** (toda la tarea 3.3 y la Q6). El **companion** no lo menciona; el deck suplementario 140 sí. → Temas 6–8.
2. **Por qué no un CLAUDE.md por carpeta, ni skills, ni secciones en el raíz** (los tres distractores de Q6). → Tema 8.
3. **Imports con `@` para estándares por paquete** (3.1). El curso no da la sintaxis. → Tema 9.
4. **`/memory`** (3.1). → Tema 4.
5. **Datos del curso que están mal:** "project-level pisa a user-level" (Tema 3), "todo carga al inicio" (Tema 2), `.claudeignore` (Tema 10), nivel "team" (Tema 1), directivas de CLAUDE.md como "enforced" (Tema 11).
6. **Matices de la documentación que pueden aparecer como distractores:** imports y rules sin `paths:` no ahorran tokens (Tema 8), `*.md` solo coincide en la raíz (Tema 7), skills con `paths` (Tema 8), "editing" vs. "reads" (Tema 6).

No encontré otros huecos para 3.1 y 3.3.

