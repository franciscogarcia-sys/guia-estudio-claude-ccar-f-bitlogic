# Capítulo 11 · 3D · Udemy 12 — Hooks, SDK & CI/CD (hooks, el Agent SDK e integración continua)

*Tarea oficial 3.6 (y complementa 1.5 y 1.7) · Último capítulo del módulo 3*

---

## Dónde estamos

Último capítulo del **módulo 3: Claude Code Configuration & Workflows**. Cubre:
- **3.6** Integrate Claude Code into CI/CD pipelines (integrar Claude Code en los pipelines de integración y entrega continua). Pesa 3,33%.

También completa dos tareas que ya viste: los **hooks** (1.5, en 1D los viste desde el Agent SDK; acá van los de Claude Code) y el **control de sesiones** (1.7, en 1C).

### Cómo leer este capítulo

Todo lo que leés acá **vale para el examen**, salvo que diga lo contrario. Cuando algo sale solo del curso (útil para entender, pero no central), lo marco con **📘 Curso**. Cuando Jacob dice algo distinto de lo que evalúa la guía, aparece un recuadro así:

> ⚠️ **En el curso vas a escuchar otra cosa.** … **Para el examen: …**

### Un aviso sobre este capítulo

De los 9 puntos oficiales de la tarea 3.6, el curso cubre solo 2, y los dos son sobre `-p`. Menciona `--output-format json`, pero no `--json-schema`. Lo demás (salida estructurada, CLAUDE.md en CI, revisión independiente, no repetir hallazgos, no duplicar tests) sale de la guía y la documentación. Además, el **companion** (el resumen escrito del curso) tiene **un error importante sobre los hooks**: dice que cualquier código de salida distinto de 0 bloquea. Las slides lo dicen bien (solo el 2 bloquea), y es una pregunta muy probable (Tema 9).

## De dónde venimos

En 1D viste que lo que **tiene** que pasar siempre no se le pide al modelo: se garantiza con código, con hooks y prerrequisitos. En 1C viste las sesiones (`--resume`, `fork_session`) y el aislamiento de contexto entre agentes. En 3A–3C armaste la configuración de Claude Code para un equipo: CLAUDE.md, rules, comandos, skills, subagentes y plan mode. Este capítulo da el último paso: **usar Claude Code sin una persona delante**, dentro de un pipeline, y **automatizar** con hooks lo que no puede depender de que Claude se acuerde.

## Mapa del capítulo

**Parte 1 — Claude Code en CI/CD (tarea 3.6).**
1. El modo no interactivo: `-p`.
2. Salida estructurada: `--output-format json` y `--json-schema`.
3. El contexto del proyecto en CI: CLAUDE.md.
4. Session context isolation (aislamiento del contexto de sesión): revisar con otra instancia.
5. Re-revisiones y tests: pasar lo que ya existe.
6. Otros controles útiles en un pipeline.

**Parte 2 — Hooks de Claude Code.**

7. Qué es un hook y dónde se configura.
8. Los eventos principales y qué puede hacer cada uno.
9. Exit codes (códigos de salida): qué bloquea y qué no.
10. Matchers y casos reales.

**Parte 3 — Agent SDK: control de sesiones.**

11. El Agent SDK: sesiones, límites y resultados.

---

# Parte 1 — Claude Code en CI/CD

## Tema 1 — El modo no interactivo: `-p`

### Qué es

Un **pipeline de CI/CD** (integración y entrega continua) es una serie de pasos automáticos que corren cada vez que alguien sube código: compilar, correr los tests, revisar el código, desplegar. Nadie está mirando la pantalla mientras corren: todo pasa en un servidor. A cada uno de esos pasos se le dice **job**.

Si en uno de esos pasos escribís `claude "Revisá este PR"`, Claude Code abre su **modo interactivo**: muestra su interfaz y espera que alguien escriba la siguiente instrucción o apruebe algo. En un servidor nadie va a escribir nada, así que el job **queda colgado** hasta que se vence el tiempo límite.

La solución es el **flag** (opción de la línea de comandos) **`-p`** (o `--print`): ejecuta el pedido, imprime el resultado en la salida estándar y **termina**. Además devuelve un **exit code** (código de salida): 0 si salió bien, otro número si falló, para que el pipeline sepa si seguir o no.

### Cómo se configura

```bash
claude -p "Analizá este PR buscando problemas de seguridad"

# También se le puede pasar contenido por la entrada estándar:
gh pr diff 482 | claude -p "Revisá este diff y listá bugs de correctitud"
```

### Ejemplo: la pregunta oficial Q10

El pipeline de TiendaX corre `claude "Analyze this pull request for security issues"` y el job queda colgado; los logs muestran que Claude Code espera una respuesta interactiva. ¿Cómo se corrige?
- ✅ **Agregar `-p`:** `claude -p "Analyze this pull request..."`.
- ❌ `CLAUDE_HEADLESS=true`: esa variable de entorno **no existe**.
- ❌ `--batch`: ese flag **no existe** (y no hay que confundirlo con la Message Batches API, que es otra cosa).
- ❌ Redirigir la entrada desde `/dev/null` (`< /dev/null`): es un truco de Unix, no la forma documentada de correr Claude Code sin interacción.

### Para el examen

- Job de CI colgado esperando input → **`claude -p`**.
- Distractores: variables o flags inventados (`CLAUDE_HEADLESS`, `--batch`, `--headless`) y `< /dev/null`.

### Cómo se une

Ya corre sin colgarse. Ahora, ¿qué hace el pipeline con lo que Claude responde?

---

## Tema 2 — Salida estructurada: `--output-format json` y `--json-schema`

### Qué es

En CI, la respuesta de Claude no la lee una persona: la lee **un script**. Por ejemplo, un script que toma cada problema encontrado y lo publica como **comentario inline** (en la línea exacta del código) en el pull request. Para eso el script necesita datos con una forma fija: archivo, línea, gravedad, descripción. Si Claude responde en texto libre, el script no tiene de dónde sacarlos.

La guía nombra dos flags que se usan **juntos**:
- **`--output-format json`**: la respuesta llega envuelta en un JSON con metadatos (el texto en el campo `result`, el ID de la sesión, el costo).
- **`--json-schema`**: le pasás un **JSON Schema** (la descripción de qué campos y tipos tiene que tener el resultado) y Claude Code devuelve un JSON **validado** contra ese esquema, en el campo **`structured_output`**.

¿Por qué hacen falta los dos? Porque `--output-format json` solo cambia el **sobre**: el texto de adentro sigue siendo libre. Lo que garantiza la forma de los hallazgos es `--json-schema`. Es la misma idea de 4.3 (que vas a ver en el módulo 4) y de `strict` en 2A: si la forma importa, se garantiza con un esquema, no pidiéndolo en el prompt.

Un detalle: si la corrida termina sin un resultado válido (por ejemplo, si Claude se negó), el campo `structured_output` **no aparece**. El script tiene que verificarlo antes de usarlo.

### Cómo se configura

```bash
gh pr diff 482 | claude -p "Revisá el diff y reportá problemas de correctitud." \
  --output-format json \
  --json-schema '{
    "type": "object",
    "properties": {
      "findings": { "type": "array", "items": {
        "type": "object",
        "properties": {
          "file": {"type": "string"}, "line": {"type": "integer"},
          "severity": {"type": "string", "enum": ["high","medium","low"]},
          "message": {"type": "string"}
        },
        "required": ["file","line","severity","message"] } }
    },
    "required": ["findings"]
  }' | jq '.structured_output.findings'
```

### Ejemplo

El job de review de TiendaX recibe `structured_output.findings` con 3 hallazgos. Un script recorre la lista y publica cada uno como comentario en la línea indicada del PR. Antes, con texto libre, el script fallaba cada vez que Claude cambiaba el formato de su respuesta.

### Para el examen

- Hallazgos que un script tiene que parsear para publicarlos como comentarios → **`--output-format json` + `--json-schema`**.
- ❌ Solo `--output-format json`: no garantiza la forma de los hallazgos.
- ❌ Pedir "devolvé JSON válido" en el prompt o en CLAUDE.md: es probabilístico.

### Cómo se une

Claude ya devuelve datos útiles. Pero para revisar bien, tiene que conocer las reglas del proyecto.

---

## Tema 3 — El contexto del proyecto en CI: CLAUDE.md

### Qué es

En CI, Claude Code revisa o genera código del repo igual que en tu máquina, pero sin nadie que le explique nada. ¿Cómo sabe cuáles son los estándares de testing del equipo, qué **fixtures** (datos de prueba preparados) existen o qué cuenta como problema en una revisión? La guía es clara: el mecanismo para darle ese contexto es **CLAUDE.md**. Como el CLAUDE.md del proyecto está en el repo, cualquier corrida en CI lo carga automáticamente.

La guía pide documentar ahí tres cosas en particular:
- **Estándares de testing:** cómo se escriben los tests, qué framework, qué convenciones.
- **Qué es un test valioso:** por ejemplo, "probar comportamiento y casos borde; no tests que solo verifican que una función existe". Sin esto, Claude tiende a generar muchos tests de poco valor.
- **Fixtures disponibles:** para que los use en vez de inventar datos.

La documentación de GitHub Actions dice lo mismo: definí en el CLAUDE.md del repo el estilo de código, los criterios de review y las reglas del proyecto. Y como Claude lo lee en cada corrida, conviene que sea conciso.

> ⚠️ **En la documentación actual vas a leer otra cosa.** Hoy existe un flag `--bare` que, para que las corridas en CI sean más rápidas y reproducibles, **saltea** la carga de CLAUDE.md, hooks y skills. La documentación lo recomienda para scripts. **Para el examen:** la guía no lo nombra y es explícita: el contexto del proyecto en CI se da con **CLAUDE.md**.

### Ejemplo

El job que genera tests en TiendaX producía tests como "verifica que `calcularEnvio` existe". El equipo agrega al CLAUDE.md:

```markdown
## Tests
- Un test valioso prueba un comportamiento o un caso borde, nunca solo que algo existe.
- Usar los fixtures de `tests/fixtures/` (productos.json, clientes.json); no inventar datos.
- Framework: Vitest + Testing Library.
```

En la corrida siguiente, los tests nuevos usan los fixtures y prueban casos como "peso 0" y "provincia inexistente".

### Para el examen

- Estándares de testing, fixtures o criterios de review para Claude en CI → **CLAUDE.md del repo**.
- Tests de bajo valor → documentar en CLAUDE.md **qué es un test valioso** y **qué fixtures hay**.
- ❌ Repetir los estándares en el prompt de cada job: la guía nombra CLAUDE.md.

### Cómo se une

Con el contexto resuelto, la pregunta siguiente es **quién** revisa el código.

---

## Tema 4 — Session context isolation: revisar con otra instancia

### Qué es

Cuando una sesión de Claude genera código, su contexto queda lleno del razonamiento que usó para escribirlo: por qué eligió tal enfoque, qué supuso. Si después le pedís a **esa misma sesión** que revise lo que hizo, tiende a ver el código a través de ese mismo razonamiento, y los errores que vienen de una mala suposición no los ve. Es lo mismo que le pasa a una persona que revisa su propio texto.

La guía lo dice así: la misma sesión que generó el código **es menos efectiva para revisarlo** que una **instancia de revisión independiente**, que no tiene ese razonamiento previo. (Es la misma idea de 4.6, que vas a ver en el módulo 4: un modelo conserva el razonamiento de la generación.)

En CI esto se traduce en que **la revisión es otra corrida**: otro `claude -p`, otro job o un subagente, que recibe el código y los criterios, pero no la conversación que lo generó. La documentación lo aplica igual: el comando `/code-review` revisa el diff en un subagente nuevo, al que no lo influye el razonamiento que produjo el código.

### Ejemplo

El pipeline de TiendaX tenía un solo job: Claude implementaba un fix y, en la misma sesión, se le pedía "ahora revisá lo que hiciste". Siempre respondía "se ve bien". Se separó en dos jobs: el segundo corre `claude -p` nuevo con el diff y el checklist del equipo. En la primera semana encontró dos casos borde sin cubrir.

### Para el examen

- Revisar código generado por Claude → **instancia o sesión independiente**, sin el razonamiento de la generación.
- ❌ "Pedirle a la misma sesión que revise su trabajo con más cuidado".

### Cómo se une

La revisión independiente arranca sin contexto previo. Eso es bueno para no arrastrar sesgos, pero trae un problema cuando el PR cambia y hay que revisar de nuevo.

---

## Tema 5 — Re-revisiones y tests: pasar lo que ya existe

### Qué es

Como cada corrida en CI arranca de cero (📘 el curso lo dice así: el agente no tiene memoria de corridas anteriores salvo que le pases ese contexto), hay dos situaciones donde **hay que darle lo que ya existe**.

**1. Re-revisar después de nuevos commits.** El desarrollador corrigió algunos problemas del primer review y subió commits nuevos. Si el review corre otra vez desde cero, vuelve a comentar todo: los problemas ya resueltos y los pendientes, duplicando comentarios. La guía pide **incluir los hallazgos del review anterior** en el contexto e indicarle a Claude que reporte **solo los problemas nuevos o los que siguen sin resolver**.

Ojo con dos atajos que parecen razonables. Revisar **solo el diff del último commit** esconde los problemas del review anterior que todavía no se arreglaron. Y **retomar la sesión anterior** trae resultados de herramientas sobre código que ya cambió (como viste en 1C). Lo recomendado es una corrida nueva sobre el PR completo, con los hallazgos previos inyectados.

**2. Generar tests.** Si Claude genera tests sin ver los que ya existen, propone escenarios que ya están cubiertos. La guía pide **pasarle los archivos de test existentes** para que no duplique.

### Ejemplo

- **Re-review:** el primer review del PR #482 reportó 4 problemas. El dev arregla 3 y sube un commit. El segundo job recibe la lista de los 4 hallazgos con la instrucción "reportá solo lo nuevo o lo que sigue sin resolver". Resultado: un comentario sobre el que quedó pendiente y uno sobre un bug nuevo que introdujo el commit, en lugar de repetir los 4.
- **Tests:** el job de tests recibe `calcularEnvio.test.ts` (que ya cubre el envío normal y el cupón) y genera solo los casos que faltan: peso 0 y provincia inexistente.

### Para el examen

- Re-review con comentarios duplicados → **pasar los hallazgos previos** y pedir **solo nuevos o no resueltos**.
- Tests que repiten escenarios → **pasar los tests existentes** en el contexto.

### Cómo se une

Estos son los puntos de la guía. Hay otros controles que ayudan a que un pipeline sea seguro y predecible, y algunos aparecen como distractores.

---

## Tema 6 — Otros controles útiles en un pipeline

### Qué es

**Límites.** En CI conviene ponerle techo a una corrida, para que un error no termine en un job que da vueltas una hora: `--max-turns` (cantidad máxima de vueltas del loop) y `--max-budget-usd` (gasto máximo). Si llega al límite, `claude -p` termina con error (un exit distinto de 0) y, con `--output-format json`, el resultado trae un subtipo como `error_max_turns` (lo ves en el Tema 11). El pipeline tiene que tratarlo como falla y no publicar un resultado vacío.

**Permisos en CI.** Nadie va a aprobar nada, así que los permisos se definen de antemano. Lo que viste en 2C vale igual acá: `--allowedTools` **pre-aprueba** herramientas (no restringe); para limitar qué herramientas existen se usa `--tools` o `--disallowedTools`. El modo `dontAsk` rechaza todo lo que no esté preaprobado, y está pensado para CI cerrado. `bypassPermissions` solo va en un entorno aislado (un contenedor), nunca en un servidor compartido.

> ⚠️ **En el curso vas a escuchar otra cosa.** Jacob dice que `--allowedTools` limita qué herramientas puede usar la corrida. **Para el examen:** `--allowedTools` pre-aprueba; para limitar se usa `--tools` o `--disallowedTools`.

**GitHub Actions.** Para GitHub, la integración documentada es la acción **`anthropics/claude-code-action`** (se instala con `/install-github-app`). Tiene dos modos: si no le das un `prompt`, espera que alguien escriba `@claude` en un comentario; si le das un `prompt`, corre sola. La API key va en los **secrets** de GitHub, nunca en el repositorio.

**Tiempo real o Batches (pregunta oficial Q11).** La **Message Batches API** cuesta 50% menos, pero puede tardar hasta 24 horas y no garantiza tiempo de respuesta. Por eso sirve para lo que **no bloquea** a nadie (un reporte nocturno de deuda técnica) y **no** para un check que tiene que terminar antes de que el desarrollador pueda hacer merge. (El detalle de Batches va en el módulo 4.)

**PR grande, revisión inconsistente (pregunta oficial Q12).** Ya la viste en 1B: se divide en una pasada por archivo para los problemas locales más una pasada de integración para el flujo entre archivos.

### Ejemplo

El job nocturno de TiendaX que genera el reporte de deuda técnica pasa a Batches y cuesta la mitad. El check de seguridad que bloquea el merge sigue en tiempo real, con `--max-turns 10` y `--permission-mode dontAsk`.

### Para el examen

- Check que bloquea el merge → **tiempo real**. Reporte nocturno → **Batches**.
- Limitar herramientas → `--tools` / `--disallowedTools` (no `--allowedTools`).
- ❌ Plan mode en CI "por seguridad": espera una aprobación humana que en CI no existe.

### Cómo se une

Con esto termina la tarea 3.6. La Parte 2 vuelve a algo que ya conocés desde el Agent SDK: los hooks, ahora en Claude Code.

---

# Parte 2 — Hooks de Claude Code

## Tema 7 — Qué es un hook y dónde se configura

### Qué es

Un **hook** (gancho) es un comando (normalmente un script) que Claude Code ejecuta **automáticamente** en un momento fijo de su funcionamiento: antes de usar una herramienta, después de editar un archivo, cuando termina de responder. La clave es que **no depende del modelo**: Claude no decide si correrlo ni puede saltearlo. Por eso los hooks son la forma de **garantizar** algo, a diferencia de CLAUDE.md, que es una guía que Claude puede no seguir (3A).

La documentación lo resume así: si algo **tiene** que pasar siempre, hacelo un hook, una regla deny o una configuración administrada; CLAUDE.md es para guías. Pero también advierte lo contrario: un hook es para una regla **sin excepciones**. "Preferí exports con nombre" tiene excepciones, así que se queda en CLAUDE.md.

**Dónde se configuran.** Los hooks van en los archivos de **settings**, nunca en CLAUDE.md. Con la lógica de siempre: el del equipo en el repo, el personal en tu carpeta.

| Archivo | Para qué |
|---|---|
| `.claude/settings.json` (en el repo) | Hooks del **equipo** (se commitea) |
| `.claude/settings.local.json` | Tus hooks para este proyecto (no se comparte) |
| `~/.claude/settings.json` | Tus hooks para todos tus proyectos |
| Managed (de la organización) | Los impone la empresa |

Con `/hooks` ves los que están configurados.

Un hook recibe por la **entrada estándar** un JSON con lo que está pasando (por ejemplo, qué herramienta se va a usar y con qué parámetros) y responde con un **exit code** y, opcionalmente, un JSON (Tema 9).

> ⚠️ **En el curso vas a escuchar otra cosa.** El curso habla de "four hook types" (cuatro tipos de hook). **Para el examen:** hoy hay muchos más eventos (más de treinta) y varios tipos de hook. Lo que importa son los eventos principales del Tema 8 y la regla de exit codes del Tema 9.

### Cómo se configura

`.claude/settings.json` de TiendaX:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          { "type": "command",
            "command": "jq -r '.tool_input.file_path' | xargs npx prettier --write" }
        ]
      }
    ]
  }
}
```

Cada vez que Claude edita o escribe un archivo, este hook lo formatea con Prettier.

### Para el examen

- Algo que tiene que pasar **siempre** en Claude Code → **hook** en settings, no una línea en CLAUDE.md.
- Hook del equipo → `.claude/settings.json` commiteado.
- ❌ Hooks definidos en CLAUDE.md.

### Cómo se une

Lo que define qué puede hacer un hook es **en qué momento** corre.

---

## Tema 8 — Los eventos principales y qué puede hacer cada uno

### Qué es

Cada hook se engancha a un **evento**: el momento en que se dispara. Lo más importante es entender que **no todos los eventos pueden frenar algo**. Un evento que ocurre **antes** de una acción puede impedirla; uno que ocurre **después** solo puede reaccionar, porque la acción ya pasó.

| Evento | Cuándo se dispara | ¿Puede bloquear? | Uso típico |
|---|---|---|---|
| **PreToolUse** | Antes de que se ejecute una herramienta | **Sí**: impide la llamada | Bloquear `rm -rf` o la edición de `.env` |
| **PostToolUse** | Después de que la herramienta ya corrió | **No** puede deshacerla (sí darle feedback a Claude) | Formatear, correr tests, registrar |
| **UserPromptSubmit** | Cuando mandás un mensaje, antes de que llegue a Claude | Sí: frena el mensaje | Validar o agregar contexto al pedido |
| **Stop** | Cuando Claude termina de responder | Sí: lo obliga a **seguir trabajando** | "No termines hasta que pase el typecheck" |
| **SessionStart** | Al arrancar o retomar una sesión | No | Cargar contexto (lo que imprime entra al contexto) |
| **Notification** | Cuando Claude necesita tu atención | No | Avisarte con una notificación del sistema |
| **PermissionRequest** | Cuando Claude Code te iba a pedir permiso | Sí, con su respuesta en JSON | Aprobar o negar un pedido puntual |

La regla que más se pregunta: **para impedir que una herramienta se ejecute, el evento es PreToolUse**. PostToolUse llega tarde: el archivo ya se editó, el comando ya corrió. 📘 El curso llama a esto el error de "Wrong Event Type" (elegir mal el evento).

Otra distinción útil para registrar lo que pasa: un hook en **PreToolUse** registra los **intentos**, incluso los que se bloquearon; uno en **PostToolUse** registra los **resultados** de lo que sí se ejecutó.

> ⚠️ **En el curso vas a escuchar otra cosa.** El companion dice que PreToolUse es el único hook que puede bloquear. **Para el examen:** también pueden bloquear UserPromptSubmit, Stop y otros. Pero si la pregunta es **impedir una llamada a una herramienta**, la respuesta es **PreToolUse**.

### Ejemplo

En TiendaX, para que nadie edite `.env` se usa **PreToolUse**, porque corre antes de que el archivo se escriba y puede impedirlo. Para formatear cada archivo editado se usa **PostToolUse**, porque necesita el archivo ya escrito. Para que Claude no dé por terminada una tarea mientras `tsc` (el **typecheck**, chequeo de tipos) falla, se usa **Stop**. Y para recibir un aviso en la computadora cuando Claude espera una respuesta, **Notification**.

### Para el examen

- Impedir una acción → **PreToolUse**. Reaccionar después (formatear, registrar, correr tests) → **PostToolUse**.
- ❌ PostToolUse para prevenir algo: la herramienta ya corrió.

### Cómo se une

El evento dice **cuándo** corre el hook. Cómo comunica su decisión depende del **exit code**.

---

## Tema 9 — Exit codes (códigos de salida): qué bloquea y qué no

### Qué es

Cuando un programa termina, devuelve un número llamado **exit code**: por convención, 0 significa "terminé bien" y cualquier otro número, algún tipo de problema. Claude Code mira ese número para saber qué decidió el hook. Esta es probablemente la regla más preguntada de los hooks:

- **Exit 0:** todo bien, la acción sigue. (Ojo: en PreToolUse, salir con 0 **no aprueba** la herramienta: simplemente sigue el flujo normal de permisos.)
- **Exit 2:** **bloquea**, en los eventos que pueden bloquear. Lo que el hook escribió en **stderr** (la salida de errores) le llega a Claude como explicación, así puede cambiar de enfoque.
- **Cualquier otro (1, 3…):** es un **error del hook que no bloquea**. En la mayoría de los eventos, la acción **sigue igual** y se muestra un aviso de "hook error".

¿Por qué importa tanto? Porque un **guardrail** (una protección) que termina con exit 1 no protege nada: la acción pasa. Para bloquear hay que usar exit 2.

**Respuesta en JSON.** En vez de usar solo el exit code, un hook puede salir con 0 e imprimir un JSON con su decisión. Los campos más comunes:
- En **PreToolUse**: `permissionDecision` (`allow`, `deny`, `ask`) dentro de `hookSpecificOutput`.
- En **PostToolUse**, **Stop** y otros: `decision: "block"` con un `reason` (el motivo, que lee Claude).
- **`additionalContext`**: texto que se agrega al contexto de Claude (también dentro de `hookSpecificOutput`).

Si hay varios hooks para el mismo evento, corren **en paralelo** y gana el más restrictivo: un `deny` le gana a un `allow`.

> ⚠️ **En el curso vas a escuchar otra cosa.** El companion dice "Exit code 0 means continue; any non-zero exit means block" (cualquier código distinto de 0 bloquea). **Para el examen: solo el exit 2 bloquea.** El exit 1 es un error que **deja pasar** la acción. El riesgo real es el contrario del que plantea el curso: un guardrail que falla con exit 1 no frena nada.

### Cómo se configura

`.claude/hooks/proteger-env.sh`:

```bash
#!/bin/bash
archivo=$(jq -r '.tool_input.file_path')
if [[ "$(basename "$archivo")" == ".env" ]]; then
  echo "Bloqueado: .env contiene secretos; usá .env.example" >&2   # stderr → Claude lo lee
  exit 2                                                          # 2 = bloquear
fi
exit 0
```

Registrado en `.claude/settings.json` bajo `PreToolUse` con `"matcher": "Edit|Write"`.

### Ejemplo

El primer guardrail de TiendaX terminaba con `exit 1` cuando detectaba `.env`. Claude editaba `.env` igual, y en la pantalla aparecía un "hook error". Al cambiarlo a `exit 2`, la edición se bloquea y Claude recibe el mensaje "usá .env.example", así que edita ese archivo en su lugar.

### Para el examen

- ¿Qué exit code bloquea? → **2**. ¿Y el 1? → error **no** bloqueante: la acción sigue.
- El motivo del bloqueo le llega a Claude por **stderr** (con exit 2) o por el `reason` del JSON.

### Cómo se une

Falta definir **a qué herramientas** se aplica cada hook, y ver los usos más comunes.

---

## Tema 10 — Matchers y casos reales

### Qué es

**El matcher** (filtro por herramienta) dice a qué herramientas aplica un hook de PreToolUse o PostToolUse. Se escribe con el nombre de la herramienta: `"Bash"`, o varias separadas por `|`: `"Edit|Write"`. Si lo dejás vacío o ponés `"*"`, aplica a todas. Dos detalles:
- Distingue mayúsculas y minúsculas.
- Si usás caracteres especiales, se interpreta como una expresión regular sin anclar: `Edit.*` también coincide con `NotebookEdit`. Para que coincida solo con Edit: `^Edit$`.

El matcher filtra por **herramienta**, no por argumento. Para filtrar por lo que hace la herramienta (por ejemplo, solo los comandos Bash que empiezan con `rm`), existe el campo **`if`** (`"if": "Bash(rm *)"`) o se resuelve dentro del script. Algunos eventos, como Stop y UserPromptSubmit, no usan matcher: se disparan siempre.

**Casos reales** que muestra la documentación:
1. **Formatear tras editar:** PostToolUse con `Edit|Write` que corre el formatter. Ya no importa si Claude "se acuerda" de formatear, porque no es Claude quien lo hace.
2. **Proteger archivos:** PreToolUse con `Edit|Write` que hace exit 2 si el archivo es `.env`, `package-lock.json` o algo dentro de `.git/`.
3. **Bloquear comandos peligrosos:** PreToolUse con `Bash` que hace exit 2 ante `rm -rf` o `drop table`.
4. **Notificaciones:** Notification que muestra un aviso del sistema operativo cuando Claude espera input.
5. **No terminar hasta que pase el typecheck:** Stop que corre `tsc` y, si falla, hace exit 2 con el error en stderr. Cuidado con los loops: el hook tiene que leer el campo `stop_hook_active` y dejar terminar si ya está forzando la continuación (Claude Code corta igual después de 8 bloqueos seguidos).
6. **Volver a cargar contexto después de compactar:** SessionStart con el matcher `compact`; lo que imprime entra al contexto.

### Ejemplo

El `.claude/settings.json` de TiendaX termina con tres hooks. Uno de PostToolUse con matcher `Edit|Write` corre Prettier sobre cada archivo editado. Otro de PreToolUse con el mismo matcher corre `proteger-env.sh`. Y un tercero de PreToolUse con matcher `Bash` corre un script que revisa el comando y bloquea el push directo a `main`. Se filtra dentro del script y no solo con `if`, porque la documentación aclara que `if` funciona como "mejor esfuerzo" y, para un bloqueo estricto, recomienda reglas de permiso o lógica propia.

### Para el examen

- Aplicar un hook a ciertas herramientas → **matcher** (`"Edit|Write"`). Filtrar por argumento → `if` o lógica en el script.
- Stop que bloquea siempre → loop: hay que mirar `stop_hook_active`.

### Cómo se une

Los hooks automatizan dentro de Claude Code. La última parte mira el **Agent SDK**, que es Claude Code usado como librería dentro de tu propio programa.

---

# Parte 3 — Agent SDK: control de sesiones

## Tema 11 — El Agent SDK: sesiones, límites y resultados

### Qué es

El **Claude Agent SDK** es el mismo motor de Claude Code (las mismas herramientas, el mismo loop, el mismo manejo de contexto), pero para usarlo **desde tu código** en Python o TypeScript. De hecho, `claude -p` es esa misma maquinaria usada desde la línea de comandos. 📘 El curso lo resume así: el SDK es para **sesiones agénticas** (varias vueltas, con herramientas); para una pregunta y una respuesta sueltas alcanza con la API directa.

Hay dos formas de usarlo:
- **`query()`**: para una tarea **puntual**. Cada llamada arranca una sesión nueva.
- **`ClaudeSDKClient`**: para una **conversación continua** en la misma sesión, y permite **interrumpir** a Claude a mitad de una respuesta (`interrupt()`).

**Sesiones.** Lo que viste en 1C (retomar, bifurcar) se configura con estas opciones: `resume` (retomar una sesión por su ID), `continue_conversation` (seguir la última), `fork_session` (al retomar, crear una sesión nueva a partir de la vieja, sin modificarla).

**Límites.** Igual que con `-p`: `max_turns` (máximo de vueltas del loop con uso de herramientas) y `max_budget_usd` (gasto máximo).

**Resultados.** Al terminar, el SDK devuelve un mensaje de resultado con un **subtipo**: `success` si salió bien, o un error específico como `error_max_turns` (se quedó sin turnos) o `error_max_budget_usd` (llegó al tope de gasto). El texto de la respuesta **solo existe cuando es `success`**: tu código tiene que mirar el subtipo antes de usarlo. Todos los resultados traen el ID de la sesión, así que se puede retomar incluso después de un error.

Antes se llamaba **Claude Code SDK** (así figura en el companion); hoy es **Claude Agent SDK**, el nombre que usa la guía. Si una opción usa el nombre viejo, es lo mismo.

### Cómo se configura

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage

opciones = ClaudeAgentOptions(
    cwd="/repos/storefront",
    allowed_tools=["Read", "Grep", "Glob"],   # pre-aprueba; no restringe (ver Trampa 12)
    max_turns=15,
    max_budget_usd=2.0,
)

async def main():
    async for mensaje in query(prompt="Listá los endpoints sin tests", options=opciones):
        if isinstance(mensaje, ResultMessage):
            if mensaje.subtype == "success":
                print(mensaje.result)
            else:
                print("Falló:", mensaje.subtype, "— sesión", mensaje.session_id)

asyncio.run(main())
```

### Ejemplo

El script nocturno de TiendaX usa `query()` con `max_turns=15`. Una noche el repo creció y el agente se quedó sin turnos: el resultado vino con `error_max_turns`. Como el script mira el subtipo, no publicó un reporte vacío: registró el error y, a la mañana siguiente, retomaron con `resume` y un límite más alto.

### Para el examen

- Tarea puntual → `query()`. Conversación continua con interrupciones → `ClaudeSDKClient`.
- Limitar costo o iteraciones → `max_turns` / `max_budget_usd`, y **revisar el subtipo** del resultado.

### Cómo se une

Cierra el capítulo y el módulo 3. Lo que sigue son las preguntas de fin de módulo.

---

## Cómo se une todo

En CI no hay nadie mirando, así que Claude Code corre con **`-p`**: ejecuta, imprime y termina (Tema 1). Para que un script pueda usar lo que responde, la salida se pide con **`--output-format json` y `--json-schema`**, y se lee de `structured_output` (Tema 2). Los estándares del equipo, los fixtures y los criterios de review llegan por el **CLAUDE.md** del repo (Tema 3). La revisión la hace **otra instancia**, sin el razonamiento que generó el código (Tema 4), y como cada corrida arranca de cero, hay que pasarle **los hallazgos previos** al re-revisar y **los tests existentes** al generar tests nuevos (Tema 5). Límites, permisos y la elección entre tiempo real y Batches completan el pipeline (Tema 6).

Para lo que tiene que pasar sí o sí, están los **hooks**: van en settings y Claude no puede saltearlos (Tema 7). **PreToolUse** puede impedir una acción; **PostToolUse** solo reacciona (Tema 8). **Solo el exit 2 bloquea**; cualquier otro código distinto de 0 es un error que deja pasar la acción (Tema 9). El **matcher** elige las herramientas, y los usos típicos son formatear, proteger archivos, notificar y no terminar hasta que pasen los checks (Tema 10). Finalmente, el **Agent SDK** pone el mismo motor en tu código, con sesiones, límites y un **subtipo** de resultado que hay que revisar (Tema 11).

## Lo que viene

Termina el módulo 3. Lo próximo son las **preguntas de fin del módulo 3** (3A a 3D, tareas 3.1 a 3.6), de a una y con el formato del examen. Después arranca el **módulo 4: Prompt Engineering & Structured Output** (criterios explícitos, few-shot, salida estructurada con esquemas, Batches y revisión en varias pasadas).

---

## Las trampas del examen

Cada trampa tiene el mismo orden: la situación, **qué elegir en el examen (✅)**, las opciones que tientan (❌) con por qué tientan y por qué están mal, y una regla para recordar.

### Grupo: CI/CD

#### Trampa 1 · El job que se cuelga (Q10)

**La situación.** El pipeline corre `claude "Analizá este PR"` y el job queda esperando input hasta el timeout (Tema 1).

**✅ En el examen elegí:** **`claude -p "Analizá este PR"`**.

**❌ Las que tientan:**

❌ **"`CLAUDE_HEADLESS=true` antes del comando".**
- *Tienta porque:* "headless" es como se llama a correr sin interfaz.
- *Está mal porque:* esa variable no existe.

❌ **"Agregar `--batch`".**
- *Tienta porque:* suena a "modo por lotes" y existe una Batches API.
- *Está mal porque:* ese flag no existe; la Batches API es otra cosa.

❌ **"Redirigir stdin desde `/dev/null`".**
- *Tienta porque:* en Unix suele cortar la espera de input.
- *Está mal porque:* es un truco, no el modo no interactivo documentado.

> 🧠 **Para recordar:** CI = `-p`.

#### Trampa 2 · Hallazgos que el script no puede leer

**La situación.** Un script tiene que publicar cada hallazgo como comentario inline, pero Claude responde en texto libre y el formato cambia entre corridas (Tema 2).

**✅ En el examen elegí:** **`--output-format json` + `--json-schema`** con el esquema de los hallazgos.

**❌ Las que tientan:**

❌ **"Solo `--output-format json`".**
- *Tienta porque:* "json" suena a estructurado.
- *Está mal porque:* solo envuelve la respuesta; el texto de los hallazgos sigue libre.

❌ **"Pedir en el prompt 'respondé siempre en este JSON'".**
- *Tienta porque:* suele funcionar.
- *Está mal porque:* es probabilístico; el esquema lo garantiza.

> 🧠 **Para recordar:** forma garantizada = `--json-schema`.

#### Trampa 3 · Tests de bajo valor en CI

**La situación.** El job que genera tests produce muchos tests triviales y no usa los fixtures del equipo (Tema 3).

**✅ En el examen elegí:** **documentar en el CLAUDE.md** del repo los estándares de testing, qué es un test valioso y qué fixtures hay.

**❌ Las que tientan:**

❌ **"Pasar a un modelo más grande".**
- *Tienta porque:* "es más inteligente".
- *Está mal porque:* no le falta inteligencia, le falta el contexto del proyecto.

❌ **"Correr con `--bare` y pasar los estándares con `--append-system-prompt-file`".**
- *Tienta porque:* la documentación recomienda `--bare` para CI.
- *Está mal porque:* la guía nombra CLAUDE.md como el mecanismo, y `--bare` saltea CLAUDE.md.

❌ **"Filtrar los tests generados con un segundo job".**
- *Tienta porque:* parece control de calidad.
- *Está mal porque:* ataca el síntoma; la causa es que no conoce los criterios.

> 🧠 **Para recordar:** contexto del proyecto en CI = CLAUDE.md.

#### Trampa 4 · Que se revise a sí mismo

**La situación.** El mismo job que genera un fix le pide a Claude, en la misma sesión, que revise lo que hizo; casi nunca encuentra problemas (Tema 4).

**✅ En el examen elegí:** **una instancia de revisión independiente** (otra corrida, sin el razonamiento de la generación).

**❌ Las que tientan:**

❌ **"Pedirle a la misma sesión que revise 'con ojo crítico'".**
- *Tienta porque:* el prompt suena exigente.
- *Está mal porque:* sigue viendo el código con el mismo razonamiento que lo produjo.

> 🧠 **Para recordar:** quien escribió no revisa.

#### Trampa 5 · Comentarios duplicados en cada push

**La situación.** Cada commit nuevo dispara un review que vuelve a comentar los mismos problemas, incluso los ya resueltos (Tema 5).

**✅ En el examen elegí:** **pasarle los hallazgos del review anterior** y pedirle que reporte **solo los nuevos o los no resueltos**.

**❌ Las que tientan:**

❌ **"Revisar solo el diff del último commit".**
- *Tienta porque:* reduce el alcance.
- *Está mal porque:* esconde los problemas anteriores que todavía no se arreglaron.

❌ **"Retomar la sesión del review anterior con `--resume`".**
- *Tienta porque:* "ya tiene el contexto".
- *Está mal porque:* arrastra resultados de herramientas sobre código que cambió.

> 🧠 **Para recordar:** re-review = corrida nueva + hallazgos previos.

#### Trampa 6 · El check pre-merge en Batches (Q11)

**La situación.** El manager propone pasar a la Batches API tanto el check que bloquea el merge como el reporte nocturno, por el 50% de ahorro (Tema 6).

**✅ En el examen elegí:** **Batches solo para el reporte nocturno**; el check pre-merge sigue en tiempo real.

**❌ Las que tientan:**

❌ **"Los dos a Batches, con polling (preguntar cada tanto si terminaron)".**
- *Tienta porque:* "muchas veces terminan rápido".
- *Está mal porque:* sin garantía de tiempo, el desarrollador puede quedar esperando horas.

❌ **"Los dos a Batches, con fallback a tiempo real si tardan demasiado".**
- *Tienta porque:* parece cubrir el peor caso.
- *Está mal porque:* el check igual espera hasta el timeout antes de caer a tiempo real, y suma complejidad sin garantía.

> 🧠 **Para recordar:** bloquea a alguien → tiempo real.

### Grupo: Hooks

#### Trampa 7 · El guardrail con exit 1

**La situación.** Un hook de PreToolUse detecta un `rm -rf` y termina con `exit 1`, pero el comando se ejecuta igual (Tema 9).

**✅ En el examen elegí:** **cambiar a `exit 2`** (o salir con 0 y un JSON con `hookSpecificOutput.permissionDecision: "deny"`).

**❌ Las que tientan:**

❌ **"Cualquier código distinto de 0 bloquea; el problema es otro".**
- *Tienta porque:* lo dice el companion del curso.
- *Está mal porque:* solo el 2 bloquea; el 1 es un error que deja pasar la acción.

> 🧠 **Para recordar:** bloquear = exit 2.

#### Trampa 8 · Prevenir con PostToolUse

**La situación.** Se quiere impedir que Claude edite `.env`, y alguien configura el hook en PostToolUse (Tema 8).

**✅ En el examen elegí:** **PreToolUse** con matcher `Edit|Write`.

**❌ Las que tientan:**

❌ **"PostToolUse que revierte el cambio con git".**
- *Tienta porque:* "lo arregla después".
- *Está mal porque:* el archivo ya se escribió; PostToolUse no puede impedir lo que ya pasó.

> 🧠 **Para recordar:** impedir = antes (PreToolUse).

#### Trampa 9 · La regla obligatoria en CLAUDE.md

**La situación.** El equipo quiere que todo archivo editado quede formateado, y lo escribe en CLAUDE.md en mayúsculas; a veces Claude se olvida (Tema 7).

**✅ En el examen elegí:** **un hook PostToolUse** en `.claude/settings.json` que corre el formatter.

**❌ Las que tientan:**

❌ **"Reforzar la instrucción en CLAUDE.md con IMPORTANT".**
- *Tienta porque:* parece que le da más peso.
- *Está mal porque:* sigue siendo una guía que Claude puede no aplicar; el hook no depende de Claude.

❌ **"Ponerlo en `~/.claude/settings.json`".**
- *Tienta porque:* también es un hook.
- *Está mal porque:* es personal; al resto del equipo no le llega.

> 🧠 **Para recordar:** siempre, para todos = hook en `.claude/settings.json`.

#### Trampa 10 · El Stop hook que no deja terminar nunca

**La situación.** Un hook de Stop hace exit 2 si `tsc` falla, y Claude queda en un loop (Tema 10).

**✅ En el examen elegí:** **leer `stop_hook_active`** y dejar terminar si ya se está forzando la continuación.

**❌ Las que tientan:**

❌ **"Pasar el hook a PostToolUse".**
- *Tienta porque:* evita el loop.
- *Está mal porque:* pierde el objetivo: que Claude no termine con errores.

> 🧠 **Para recordar:** Stop que bloquea → controlar `stop_hook_active`.

### Grupo: Agent SDK y permisos del CLI

#### Trampa 11 · Leer el resultado sin mirar el subtipo

**La situación.** Un script del Agent SDK publica un reporte vacío cuando el agente se queda sin turnos (Tema 11).

**✅ En el examen elegí:** **revisar el `subtype` del resultado** (`success` o un error como `error_max_turns`) antes de usar el texto.

**❌ Las que tientan:**

❌ **"Sacar el `max_turns` para que nunca se corte".**
- *Tienta porque:* elimina el error.
- *Está mal porque:* deja el agente sin techo de costo ni de iteraciones (es el anti-pattern de 1A).

> 🧠 **Para recordar:** primero el subtipo, después el resultado.

#### Trampa 12 · Restringir herramientas en CI con `--allowedTools`

**La situación.** El job de review debería poder solo leer, y alguien lo configura con `--allowedTools "Read,Grep"` (Tema 6).

**✅ En el examen elegí:** **`--tools` (o `--disallowedTools`)** para limitar qué herramientas existen.

**❌ Las que tientan:**

❌ **"`--allowedTools` ya lo limita".**
- *Tienta porque:* el nombre lo sugiere.
- *Está mal porque:* pre-aprueba esas herramientas, no saca las demás (2C).

> 🧠 **Para recordar:** allowed = aprobar; tools/disallowed = limitar.

---

## Checklist oficial

**Tarea 3.6 — Integrate Claude Code into CI/CD pipelines**

*Knowledge of*
- [x] El flag `-p` (o `--print`) para correr Claude Code sin interacción en pipelines → **Tema 1** (Trampa 1)
- [x] `--output-format json` y `--json-schema` para forzar salida estructurada en CI → **Tema 2** (Trampa 2)
- [x] CLAUDE.md como mecanismo para dar contexto del proyecto (estándares de testing, fixtures, criterios de review) a Claude Code en CI → **Tema 3** (Trampa 3)
- [x] Aislamiento del contexto de sesión: la misma sesión que generó el código revisa peor que una instancia independiente → **Tema 4** (Trampa 4)

*Skills in*
- [x] Correr Claude Code en CI con `-p` para evitar que se cuelgue esperando input → **Tema 1** (Trampa 1)
- [x] Usar `--output-format json` con `--json-schema` para hallazgos parseables que se publican como comentarios inline → **Tema 2** (Trampa 2)
- [x] Incluir los hallazgos previos al re-revisar después de nuevos commits, pidiendo solo lo nuevo o no resuelto → **Tema 5** (Trampa 5)
- [x] Pasar los tests existentes para que la generación de tests no duplique escenarios → **Tema 5**
- [x] Documentar en CLAUDE.md los estándares de testing, qué es un test valioso y los fixtures disponibles → **Tema 3** (Trampa 3)

**Complementa otras tareas:** hooks de Claude Code para 1.5 (Temas 7–10) · control de sesiones del Agent SDK para 1.7 (Tema 11) · Q11 (4.5) y Q12 (4.6) del escenario de CI (Tema 6).

**De la documentación, no de la guía** (vale saberlo; la guía no lo pregunta directo): `--bare` (Tema 3) · `--max-turns`, `--max-budget-usd`, `--tools`, `dontAsk`, GitHub Actions (Tema 6) · tabla de eventos, JSON de decisión, `if`, `stop_hook_active` (Temas 8–10) · `query()` vs `ClaudeSDKClient` y subtipos de resultado (Tema 11).

**📘 Curso (útil para entender):** "Wrong Event Type" y logging de intentos vs. resultados (Tema 8) · corridas autocontenidas (Tema 5) · SDK para sesiones agénticas vs. API para llamadas sueltas (Tema 11).

---

## Autoevaluación oral

1. Un job de CI se cuelga. ¿Qué flag falta y por qué las otras opciones típicas (`CLAUDE_HEADLESS`, `--batch`, `/dev/null`) no sirven?
2. ¿Para qué sirven `--output-format json` y `--json-schema`, y por qué el primero solo no alcanza? ¿Dónde viene el resultado?
3. ¿Cómo le das a Claude en CI los estándares de testing y los fixtures? ¿Por qué la revisión tiene que hacerla otra instancia? ¿Qué le pasás al re-revisar y al generar tests?
4. ¿Qué evento usás para impedir una acción y cuál para formatear después? ¿Qué hace cada exit code (0, 2, 1)?
5. En el Agent SDK, ¿cuándo `query()` y cuándo `ClaudeSDKClient`? ¿Por qué hay que mirar el subtipo del resultado?

---

## Preguntas tipo examen

Las preguntas tipo examen de este capítulo están en [`04-practica/modulo-3.md`](../04-practica/modulo-3.md), junto con las del resto del módulo 3. Hacelas cuando termines **todos** los capítulos del módulo, de a una y sin mirar la respuesta.

---

## Revisión contra el blueprint oficial

Qué puede salir en el examen de 3.6 que el curso de Jacob **no cubre o cubre flojo**, y dónde quedó explicado:

1. **`--output-format json` + `--json-schema`** y el campo `structured_output`. → Tema 2.
2. **CLAUDE.md como contexto en CI** (estándares, fixtures, criterios de review, qué es un test valioso). → Tema 3.
3. **Revisión con una instancia independiente.** → Tema 4.
4. **Hallazgos previos al re-revisar y tests existentes al generar.** → Tema 5.
5. **Las preguntas oficiales del escenario de CI** (Q10, Q11, Q12). → Temas 1 y 6.
6. **Datos del companion que están mal** (las slides los dicen bien o no los tocan): "cualquier exit distinto de 0 bloquea" (Tema 9), "solo PreToolUse bloquea" (Tema 8), "four hook types" (Tema 7), "Claude Code SDK" (Tema 11).

No encontré otros huecos para 3.6.

