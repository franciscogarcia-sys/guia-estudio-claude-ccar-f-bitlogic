# Mapa de confusiones

*Los conceptos que el examen pone a competir entre sí, explicados lado a lado*

---

## Para qué sirve este capítulo

Las preguntas del CCAR-F casi nunca preguntan "¿qué es X?". Plantean una situación y te dan cuatro opciones. Varias son técnicas **reales y correctas en otro contexto**. Por eso el error más común no es no saber un tema: es **confundir dos herramientas parecidas** o elegir la correcta en general cuando el enunciado pedía otra cosa.

Este capítulo junta esos pares. Cada entrada tiene el mismo orden:
- **Qué es cada uno**, explicado desde cero, con el término en inglés (como aparece en el examen) y su traducción.
- **Cómo se ve en la práctica**: el campo, el flag o el archivo concreto, porque esos detalles aparecen en las opciones.
- **En qué se diferencian**: la idea que los separa.
- **La señal del enunciado**: las palabras que te dicen cuál va.
- **Un ejemplo** de TiendaX.
- Al final, una línea **🧠 Para recordar**.

Dos marcas:
- **⭐ Alta probabilidad de examen.** Hay una pregunta oficial de muestra sobre el tema, es central en un escenario que seguro aparece, o el curso dice algo distinto de la guía.
- **Trampa frecuente.** Bloques dentro de las entradas con una confusión que suele aparecer en las preguntas de práctica, explicada con sus distractores.

Al final hay una tabla con las 39 parejas en una línea cada una, para releer la noche anterior.

### Antes de empezar: los errores de lectura más comunes

La mayoría de los errores en las preguntas de práctica no son por falta de conocimiento, sino de lectura. Estos patrones explican casi todos.

**1. El alcance (scope).** Elegir una solución correcta en general que rompe una condición del enunciado. Las preguntas esconden la condición en frases como *"while keeping…"* (manteniendo…), *"without affecting…"* (sin afectar…), *"without losing…"* (sin perder…), *"separately"* (por separado). Antes de elegir, **subrayá mentalmente qué tiene que seguir funcionando** y descartá las opciones que lo rompen. Ejemplo: "reducir el ruido **sin dejar de detectar los errores de pagos**" descarta "apagar la categoría" aunque apagar reduzca el ruido.

**2. La causa nombrada (root cause).** Cuando el enunciado dice qué causó el problema ("un compañero agregó *only report high-confidence findings*" y después se escapó un bug), la respuesta correcta tiene que **eliminar esa causa**. Una opción que agrega algo bueno pero deja la causa en su lugar es incompleta.

**3. "Mejorar la descripción" como reflejo.** Ampliar la descripción de una tool o agregar ejemplos es la respuesta de la Q2 oficial, pero solo sirve para un problema: **Claude elige mal entre tools parecidas porque las descripciones son pobres**. Si el enunciado dice que las descripciones ya son buenas (*"already have clear, distinct descriptions"*), la causa está en otro lado: en el system prompt (entrada 35) o en una tool que puede hacer de más (entrada 33). Cuando una opción dice "mejorar la descripción" o "agregar ejemplos", preguntate: **¿el enunciado dice que el problema es elegir entre tools y que las descripciones son pobres?** Si no lo dice, casi seguro es el distractor.

**4. La segunda opción de las *Select TWO*.** En las preguntas de dos respuestas es común acertar una y elegir la otra con menos cuidado. Casi siempre, esa segunda opción equivocada es un distractor conocido de este mapa: `required` para forzar profundidad (entrada 21), desactivar el paralelo (entrada 34), filtrar por confianza autoinformada (entrada 20). La técnica: **marcá cada opción como verdadera o falsa por separado**, como si fuera una pregunta aparte, y recién después elegí las dos verdaderas.

Una señal más, que aparece seguido: cuando el enunciado dice **"your teammate/manager proposes…"** (tu compañero o tu jefe propone…) y te pregunta *"How should you evaluate this proposal?"*, la propuesta casi siempre tiene un problema. Leela buscando qué rompe.

---

# Dominio 1 — Agentic Architecture & Orchestration (arquitectura agéntica y orquestación)

## 1. `stop_reason` o turn budget: qué termina el loop ⭐
**Qué es cada uno.** El **agentic loop** (el ciclo del agente) es el ciclo en el que Claude pide una tool, tu código la ejecuta y le devuelve el resultado, y así hasta que la tarea está hecha. Hay dos mecanismos que tienen que ver con cuándo termina:
- El **`stop_reason`** (motivo de parada) es el campo de la respuesta que dice por qué Claude dejó de generar. Si vale `tool_use`, Claude está pidiendo una tool y el loop sigue. Si vale `end_turn`, Claude terminó su respuesta y el loop **termina**. Es el mecanismo **principal**.
- El **turn budget** (tope de vueltas; en el Agent SDK, `max_turns`) es un límite de seguridad: si el loop da, por ejemplo, 15 vueltas, se corta. Es una **red de seguridad** contra loops descontrolados, no la forma normal de terminar.

**Cómo se ve en la práctica.** Los valores de `stop_reason` que conviene reconocer:

| Valor | Qué significa | Qué hace el loop |
|---|---|---|
| `end_turn` | Claude terminó su respuesta | **Termina** |
| `tool_use` | Claude pide una o más tools | Ejecuta las tools y sigue |
| `max_tokens` | La respuesta se cortó por el límite de tokens de salida | Respuesta incompleta: subir `max_tokens` o continuar |
| `stop_sequence` | Apareció una secuencia de corte que definiste | Termina (es intencional) |
| `pause_turn` | El servidor pausó un turno largo (tools del lado del servidor) | Reenviar para que siga |
| `refusal` | Claude se negó a responder | No hay respuesta útil |

Una vuelta del loop se arma así: agregás la respuesta de Claude (con sus bloques `tool_use`) al historial, ejecutás cada tool, y mandás un mensaje del usuario con un bloque **`tool_result`** por cada tool, con el mismo **`tool_use_id`**. En el **Agent SDK**, el loop lo maneja el SDK; vos fijás `max_turns`, y si se alcanza, el resultado llega con **`subtype: "error_max_turns"`** en lugar de `"success"`. Hay que revisar ese subtipo antes de usar el resultado.

**En qué se diferencian.** El `stop_reason` dice "la tarea terminó". El tope dice "algo anda mal, cortemos". Llegar al tope **no** es éxito: es una falla que hay que investigar o escalar.

**La señal del enunciado.** "El loop termina cuando…" o "cómo detectar que la tarea está completa" → `stop_reason == "end_turn"`. Distractores típicos: terminar cuando la respuesta de Claude **contiene texto** (puede haber texto **y** un pedido de tool en la misma respuesta), terminar cuando aparece una frase como "DONE" en el texto, o usar solo un número fijo de vueltas.

**Ejemplo.** SoporteBot responde "Voy a revisar tu pedido" y en el mismo mensaje pide `lookup_order`. Si el código cortara al ver texto, el pedido nunca se buscaría. Como el `stop_reason` es `tool_use`, el loop sigue.

> 🧠 **Para recordar:** termina el **`end_turn`**; el tope es el **freno de emergencia**.

---

## 2. Prompt-based guidance o programmatic enforcement: dónde va una regla ⭐

**Qué es cada uno.**
- Una regla en el **prompt** (system prompt, CLAUDE.md) es **guidance** (una guía): Claude la sigue la gran mayoría de las veces, pero es **probabilística**. Alguna vez puede no cumplirla.
- Una regla en **código** es **enforcement** (una obligación): es **determinista** y se cumple siempre. Puede ser un **hook** (código que corre antes o después de una tool y puede bloquearla) o un **programmatic prerequisite** (prerrequisito programático; por ejemplo, que `process_refund` no funcione si antes no se llamó a `get_customer`).

**Cómo se ve en la práctica.**
- **Eventos de hooks:** **`PreToolUse`** corre **antes** de que se ejecute una tool y **puede impedirla**; **`PostToolUse`** corre **después** y solo puede reaccionar (formatear, registrar, avisar). Hay otros (`UserPromptSubmit`, `Stop`, `SessionStart`…), pero los dos primeros son los que más se preguntan.
- **Cómo bloquea un hook de Claude Code:** el script termina con **exit code 2**. Cualquier otro código distinto de 0 se toma como un error del hook y **la acción sigue**. Ese detalle es una trampa clásica.
- **El `matcher`** elige a qué tools se aplica el hook (por ejemplo, `"Edit|Write"`).
- **Dónde se configuran:** en Claude Code, en **`.claude/settings.json`** (equipo) o en tu configuración personal. En un agente hecho con el **Agent SDK**, en las opciones del agente (`hooks`), como funciones de tu código.
- Un hook de `PreToolUse` puede bloquear y devolverle a Claude un mensaje ("este reembolso supera USD 500, usá `escalate_to_human`"), así el agente sigue por el camino correcto.

**En qué se diferencian.** El prompt sirve para **guiar el juicio**: criterios, tono, cuándo escalar, qué cuenta como "bloqueante". El código sirve para lo que **no puede fallar nunca**, sobre todo si hay plata, datos sensibles o compliance de por medio.

**La señal del enunciado.** *"Must always"*, *"never"*, *"required for compliance"*, *"financial impact"*, un monto máximo → **código**. "Decidir cuándo", "calibrar", "casos ambiguos" → **prompt con criterios y ejemplos**. Si la regla ya está en el prompt y "a veces no se cumple", la respuesta casi nunca es "escribirla en mayúsculas" o "repetirla": es pasarla a código.

**Ejemplo.** "Ningún reembolso de más de USD 500 sin aprobación humana" → hook `PreToolUse` sobre `process_refund` que bloquea y redirige a escalamiento. Q1 de la guía va por este lado: verificar al cliente con `get_customer` antes de reembolsar se garantiza con un prerrequisito programático, no con una instrucción. "Escalar los casos que necesitan una excepción" → criterios en el prompt con ejemplos (Q3).

> 🧠 **Para recordar:** **siempre** = código (hook, exit 2); **juicio** = prompt.

---

## 3. Narrow task decomposition o coverage annotations ⭐

**Qué es cada uno.**
- La **task decomposition** (descomposición de tareas) es cómo el coordinador parte la tarea en subtareas para los subagentes. Si la parte **demasiado estrecha** (narrow decomposition), hay temas que **nadie investiga**.
- Las **coverage annotations** (anotaciones de cobertura) son lo que agrega el agente de síntesis para decir qué está bien respaldado y qué tiene huecos **porque una fuente falló**.

**En qué se diferencian.** Si un tema nunca se le asignó a nadie, el problema está en **el coordinador**, y se arregla en la descomposición. Es la Q7 de la guía: un informe sobre "IA en industrias creativas" que solo cubre artes visuales, porque el coordinador partió el tema así. Las anotaciones de cobertura **reportan** huecos causados por fallas; no arreglan un plan mal hecho.

**La señal del enunciado.** "Los subagentes hicieron bien su trabajo, pero faltan temas enteros" o "los logs muestran que el coordinador solo asignó…" → descomposición del coordinador. "Una fuente no respondió y el sistema siguió" → anotaciones de cobertura.

> 🧠 **Para recordar:** tema **nunca asignado** = coordinador; fuente **caída** = anotar el hueco.

---

## 4. Context passing entre agentes: todo, nada o lo justo

**Qué es cada uno.** Un **subagent** (subagente) arranca con un contexto aislado (**context isolation**): **no ve** la conversación del coordinador ni la de otros subagentes. Solo sabe lo que recibe en su prompt. Hay tres formas de darle información:
- **Nada**: el subagente no sabe lo necesario y adivina o repite trabajo.
- **Todo** (el transcript completo, los informes enteros): se llena de ruido y la precisión baja.
- **Lo justo** (**explicit context passing**, pasaje explícito de contexto): el coordinador le pasa explícitamente lo que necesita, con estructura (los hallazgos clave, las fuentes, el formato de salida).

**Cómo se ve en la práctica.** En el **Agent SDK**, el coordinador lanza un subagente llamando a la tool **`Task`** (en versiones recientes, `Agent`). Para que pueda hacerlo, esa tool tiene que estar en los **`allowedTools`** del coordinador. Cada subagente se define con un **`AgentDefinition`**: una `description` (cuándo usarlo), un `prompt` (sus instrucciones) y sus `tools` (las que puede usar). Para que corran **en paralelo**, el coordinador pide **varias llamadas a `Task` en la misma respuesta**; si las pide de a una, se ejecutan en serie.

**En qué se diferencian.** La guía siempre elige **pasar explícitamente lo necesario, de forma estructurada**. Y en sentido inverso, los subagentes devuelven **datos estructurados** (hechos clave, citas, metadatos), no su razonamiento completo.

**La señal del enunciado.** "El subagente no tiene la información de…" → pasarla en su prompt. "El sintetizador se queda sin espacio" → que los subagentes devuelvan datos estructurados. "Los subagentes de la fase 2 redescubren lo de la fase 1" → inyectar un **resumen** de la fase 1. "Tardan mucho, se ejecutan de a uno" → varias llamadas a `Task` en la misma respuesta.

**Trampa frecuente: qué vuelve de un subagente.** El **context isolation** (aislamiento de contexto) funciona **en las dos direcciones**:
- **Al arrancar**, un subagente normal no hereda la conversación del coordinador ni sus tool results. Recibe su propio system prompt, el prompt de delegación y el contexto del proyecto (como el CLAUDE.md). 📘 Un **fork** es la excepción: copia la conversación del coordinador **al arrancar**. Fork cambia lo que el subagente **recibe**, no lo que **devuelve**.
- **Al terminar**, al coordinador le vuelve **solo el mensaje final** del subagente. Todo lo que leyó y ejecutó (cada tool call, cada registro) queda en el contexto del subagente y nunca entra al del coordinador.

Por eso delegar una investigación grande protege el contexto del coordinador: el subagente puede leer decenas de registros y el coordinador recibe un informe corto. El costo es que el coordinador no ve los pasos intermedios. Entonces **el diseño correcto es pedir, en el prompt de delegación, qué tiene que traer el informe final**: la evidencia, los montos, los IDs, las fuentes.

Los distractores típicos:
- **Reenviar cada tool result al coordinador "para auditar"**: vuelve a llenar el contexto que la delegación quería proteger.
- **Compactar el transcript del subagente e insertarlo en el coordinador**: no existe ese mecanismo. La compactación resume **la propia sesión**, y el transcript del subagente nunca entra al coordinador.
- **No usar fork "para que no se mezcle"**: el fork no afecta lo que vuelve.

Señal: *"verbose output will exhaust the coordinator's context window"* → aislamiento + un informe final que traiga la evidencia.

> 🧠 **Para recordar:** entre agentes, **ni nada ni todo: lo justo, estructurado**; de un subagente vuelve **solo su mensaje final**.

---

## 5. Session resumption o fresh session con resumen

**Qué es cada uno.**
- **Session resumption** (retomar una sesión): en Claude Code, `claude --resume` (elegís una sesión anterior) o `claude --continue` (la última); en el Agent SDK, la opción `resume` con el id de sesión. Retoma **con todo su historial**, incluidos los resultados viejos de las tools.
- **Fresh session with a structured summary** (sesión nueva con un resumen estructurado): arranca de cero, pero le pasás un resumen de lo importante.
- 📘 **`fork_session`**: crea una rama de la sesión para probar otro camino sin perder la original.

**En qué se diferencian.** Si el contexto anterior **sigue siendo válido**, se retoma. Si los resultados de las tools **quedaron viejos** (**stale**: el código cambió, los datos cambiaron), retomar trae información falsa con apariencia de actual: conviene una **sesión nueva con un resumen**. La guía lo dice así: empezar de nuevo con un resumen estructurado es más confiable que retomar con resultados de tools viejos.

**La señal del enunciado.** "Al día siguiente", "después de un refactor grande", "los archivos cambiaron", *"stale tool results"* → sesión nueva con resumen. "Continuar donde quedó, nada cambió" → `--resume`. "Probar dos enfoques desde el mismo punto" → `fork_session`.

> 🧠 **Para recordar:** contexto **válido** = resume; contexto **viejo** = nuevo + resumen.

---

# Dominio 2 — Tool Design & MCP Integration (diseño de tools e integración MCP)

## 6. Tool descriptions, few-shot o dividir la tool ⭐

**Qué es cada uno.**
- La **tool description** (descripción de la tool) es lo principal que Claude usa para decidir cuándo llamarla.
- **Few-shot** son ejemplos de uso en el prompt.
- **Splitting a tool** (dividir una tool) genérica en varias específicas: por ejemplo, una `search` que hace todo, en tres tools con nombres claros.

**Cómo se ve en la práctica.** Cada tool se define con un **`name`**, una **`description`** y un **`input_schema`** (los parámetros, en JSON Schema). Una buena `description` dice:
- qué hace y qué devuelve;
- qué entradas acepta y en qué formato;
- ejemplos de consultas que le corresponden;
- casos borde;
- **en qué se diferencia de las tools parecidas** ("usá `lookup_order` para preguntas sobre un pedido; para datos de la cuenta del cliente, `get_customer`").

**En qué se diferencian.** Si Claude elige mal entre dos tools y **las descripciones son mínimas**, la causa es la descripción, y se arregla ahí. Es la Q2 de la guía: ampliar las descripciones, **no** agregar 5 a 8 ejemplos. Few-shot sirve cuando las descripciones ya están bien y el caso es **realmente ambiguo**. Dividir sirve cuando una tool hace demasiadas cosas distintas.

**La señal del enunciado.** "Ambas tools tienen descripciones de una línea" → mejorar descripciones. "Las descripciones son detalladas y aun así falla en pedidos que podrían ir a cualquiera de las dos" → ejemplos con razonamiento.

**Trampa frecuente: cuándo NO es la descripción.** Mejorar la descripción arregla un solo problema: **Claude elige mal entre tools que se parecen, porque las descripciones son pobres**. Antes de elegir esa opción, buscá en el enunciado esas dos condiciones. Si falta alguna, la causa está en otro lado:

| Síntoma en el enunciado | Dónde está la causa | Arreglo |
|---|---|---|
| Descripciones mínimas, tools parecidas | La descripción | Ampliarla (Q2) |
| *"Descriptions are already clear and distinct"*, y aun así elige mal o llama tools de más | El **system prompt**: una palabra que coincide con una tool, un "always call a tool", dos instrucciones que se contradicen | Corregir el prompt (entrada 35) |
| Hay **una sola tool**, y hace la operación equivocada o accede a algo que no debería | La **interfaz** de la tool: texto libre o una capacidad demasiado amplia | Tools específicas con schema, o una tool más angosta (entrada 33) |
| Un paso tiene que ocurrir **siempre** | Falta una garantía | `tool_choice` forzado (entrada 8) o un hook (entrada 2) |

La frase *"already have clear, distinct descriptions"* (ya tienen descripciones claras y distintas) descarta tocar las descripciones, y también agregar few-shot: los ejemplos son una ayuda secundaria cuando las descripciones ya están bien.

> 🧠 **Para recordar:** descripción **mínima** = mejorarla; descripción **buena** + caso ambiguo = ejemplos; descripción **buena** + ruteo malo = **mirá el prompt o la interfaz**.

---

## 7. Access failure o valid empty result ⭐

**Qué es cada uno.**
- Un **valid empty result** (resultado vacío válido): la consulta **se hizo** y **no encontró nada**. Es una respuesta ("el cliente no tiene pedidos").
- Un **access failure** (falla de acceso): la consulta **no se pudo hacer** (timeout, sin permiso, servicio caído). No es una respuesta.

**Cómo se ve en la práctica.**
- En la **API**, cuando una tool falla, el `tool_result` lleva **`is_error: true`** y un mensaje útil ("timeout después de 30 s consultando el sistema de pedidos"), no un genérico "failed".
- En **MCP**, el resultado de la tool lleva **`isError: true`**. Es un error de ejecución de la tool; no se manda como error de protocolo.
- La guía pide un **structured error** (error estructurado) con campos como **`errorCategory`** (transitorio, validación, permiso, regla de negocio) e **`isRetryable`** (si conviene reintentar), para que el agente sepa qué hacer.
- Entre agentes, la falla viaja con el tipo de falla y lo que se intentó (entrada 32).

**En qué se diferencian.** Si una falla se devuelve como lista vacía, el que recibe cree que "no hay nada" y decide mal con total seguridad. El vacío válido **no se reintenta** (va a dar lo mismo); la falla sí puede reintentarse si es transitoria.

**La señal del enunciado.** "Timeout… devolvió una lista vacía marcada como éxito" → distinguir falla de vacío. Distractor: "reintentar siempre que venga vacío" (reintenta también los vacíos reales).

> 🧠 **Para recordar:** **"no encontré" ≠ "no pude buscar"**.

---

## 8. `tool_choice`: `auto`, `any` o forced ⭐

**Qué es cada uno.** `tool_choice` es un parámetro de la llamada a la API que controla si Claude **tiene que** usar una tool.

| Valor (JSON) | Qué hace | Cuándo se usa |
|---|---|---|
| `{"type": "auto"}` | Claude decide si usa una tool o responde con texto. Es el **default** cuando hay tools | Un agentic loop normal |
| `{"type": "any"}` | Claude **tiene que** usar **alguna** tool, la que elija | Garantizar que llame una tool cuando hay varias posibles |
| `{"type": "tool", "name": "extract_metadata"}` | **Forced** (forzado): Claude **tiene que** usar **esa** tool | Que un paso específico vaya primero |
| `{"type": "none"}` | Claude no puede usar tools (default cuando no hay tools) | Un turno solo de texto. La guía no lo nombra |

**Detalles que aparecen en las opciones.**
- Con `any` o forzado, la respuesta empieza **directo con el `tool_use`**: no hay texto antes. Si querés una explicación además de la llamada, va `auto`.
- **`disable_parallel_tool_use: true`** va **adentro** de `tool_choice`, no aparte: con `auto`, como mucho una tool por respuesta; con `any` o forzado, exactamente una.
- `any` y forzado **no funcionan con extended thinking en modo manual** (dan error).
- El patrón de dos turnos: **forzar en el primer turno**, después **`auto`**. Si forzás en todos los turnos, el loop nunca termina con texto.

**En qué se diferencian.** `any` garantiza que haya una llamada, pero deja elegir cuál. Forzado garantiza **cuál**. En un loop normal se usa `auto`.

**La señal del enunciado.** "Varios schemas de extracción y no se sabe qué tipo de documento llegó; a veces responde con texto" → **`any`**. "Esta extracción tiene que correr **antes** que el enriquecimiento" → **forzado en el primer turno, después `auto`**.

**Detalle de la documentación actual.** En algunos modelos muy recientes, `any` y forzado devuelven error 400, y la alternativa es `auto` con `strict`. Para el examen, respondé como la guía, salvo que la pregunta nombre esos modelos.

**Trampa frecuente: `strict` no obliga a llamar la tool.** Son dos controles distintos, en dos lugares distintos:
- **`tool_choice`** va en la **llamada a la API** y decide **si** Claude llama una tool y **cuál**.
- **`strict: true`** va en la **definición de la tool** y garantiza que **los argumentos** cumplan su `input_schema`, una vez que la tool ya fue elegida. No hace que se elija.

Para "el primer turno siempre llama `get_customer`, para verificar la identidad", la única opción que garantiza **esa** tool es el modo forzado: `{"type": "tool", "name": "get_customer"}` en el primer pedido. Las otras fallan por razones distintas:
- **`any`**: garantiza **una** tool, no **esa**. Podría cumplir llamando `lookup_order`.
- **`auto` + una regla en el prompt**: es probabilístico. Si saltear la verificación puede mandar un reembolso a la persona equivocada, no alcanza.
- **`strict: true`**: resuelve otro problema (la forma de los argumentos).

Un detalle más: como el **parallel tool use** (varias tools en una respuesta) está activo por defecto, forzar una tool garantiza que **esa** se llame, pero no que sea la **única**. Para exactamente una, `disable_parallel_tool_use: true` dentro de `tool_choice`. Y al revés: si querés que dos subagentes corran en paralelo, **no** pongas `disable_parallel_tool_use`, porque hace lo contrario (entrada 34).

> 🧠 **Para recordar:** **any** = alguna; **forced** = esa, y primero; **`strict`** = argumentos válidos, no obliga a llamar.

---

## 9. MCP server scopes: `.mcp.json` o `~/.claude.json`

**Qué es cada uno.** Un **MCP server** (servidor MCP, del Model Context Protocol) le agrega tools, datos (**resources**) y prompts a Claude Code. Se puede configurar en tres **scopes** (alcances):

| Scope | Dónde vive | Quién lo tiene |
|---|---|---|
| **project** | `.mcp.json` en la raíz del repo | Todo el equipo; viaja por git |
| **user** | `~/.claude.json` | Solo vos, en todos tus proyectos |
| **local** | `~/.claude.json`, asociado a ese proyecto | Solo vos, solo en ese proyecto |

**Cómo se ve en la práctica.**
- Se agrega con `claude mcp add --scope project <nombre> …` (o `user`, o `local`).
- **Las credenciales nunca se escriben en el archivo**: se referencian como variables de entorno, con la sintaxis **`${GITHUB_TOKEN}`** (o `${VAR:-valor_por_defecto}`). Cada dev tiene su token en su entorno.
- **Transportes:** **stdio** para un servidor que corre en tu máquina (un proceso local); **HTTP** (streamable HTTP) para uno remoto.
- Un `.mcp.json` del proyecto pide aprobación la primera vez que se usa (salvo en modo no interactivo).
- Las tools de todos los servidores configurados están disponibles a la vez.

**La señal del enunciado.** "Que todo el equipo tenga el servidor al clonar" → `.mcp.json` (scope project). "Un servidor que solo uso yo para probar" → user o local. "Sin commitear el token" → `${VARIABLE}`.

> 🧠 **Para recordar:** **equipo = `.mcp.json` en el repo**; **personal = `~/.claude.json`**; **secretos = `${VAR}`**.

---

## 10. Grep, Glob, Edit o Read + Write

**Qué es cada uno.** Son **built-in tools** (tools que ya trae Claude Code).
- **Grep** busca **dentro del contenido** de los archivos ("¿dónde se llama `processRefund`?").
- **Glob** busca **por nombre o ruta**, con patrones: `**/*.test.tsx` = todos los archivos de test de React, en cualquier carpeta.
- **Edit** reemplaza un fragmento (`old_string` → `new_string`) que tiene que ser **único** en el archivo. Si aparece varias veces, falla. Se arregla con un fragmento más largo que sea único, con `replace_all` si querés cambiar todas las apariciones, o con **Read + Write** (leer el archivo y reescribirlo entero).

**La señal del enunciado.** "Encontrar archivos por su nombre o extensión" → Glob. "Encontrar dónde se usa algo" → Grep. "Edit falla porque el texto no es único" → un ancla más larga, o Read + Write. "Explorar un codebase que no conocés" → de a poco: Glob para ver la estructura, Grep para seguir un nombre, Read solo de lo relevante (**incremental exploration**).

**Trampa frecuente: Grep usa regex.** La tool Grep de Claude Code está hecha sobre **ripgrep**, así que el patrón se interpreta como **regular expression** (expresión regular), no como texto literal. Llaves `{}`, puntos `.`, paréntesis `()` y corchetes `[]` son **metacaracteres**: tienen un significado especial. Para buscar el `interface{}` de Go, hay que escaparlos: `interface\{\}`. Si el patrón no es válido, Grep devuelve un error con el diagnóstico de ripgrep.

Ese error es **determinista**: el mismo patrón falla siempre. Por eso los distractores no sirven:
- **Reintentar**: los reintentos son para fallas transitorias (timeouts), no para una entrada inválida.
- **Cambiar a Glob** "porque las llaves son de patrones de rutas": Glob busca **nombres** de archivo, no contenido.
- **`multiline: true`**: permite que un patrón **válido** abarque varias líneas; no cambia cómo se interpretan los metacaracteres.

**Trampa frecuente: Grep devuelve solo las rutas.** Grep tiene tres modos de salida (`output_mode`): `files_with_matches` (**el default**: solo las rutas de los archivos con coincidencias, que gasta pocos tokens), `content` (las **líneas** que coinciden, con el número de línea) y `count` (cuántas coincidencias hay por archivo). Si el agente necesita **citar** el texto encontrado, lo eficiente es `output_mode: "content"`: leer cada archivo entero con Read funciona, pero carga documentos completos para usar unas pocas líneas. Y `multiline` no agrega líneas de contexto: solo permite que un patrón abarque varias líneas.

> 🧠 **Para recordar:** Grep = **adentro**; Glob = **el nombre**; Grep es **regex**: escapá `{ } ( ) [ ] .`; para ver las líneas, `output_mode: "content"`

---

# Dominio 3 — Claude Code Configuration & Workflows (configuración y flujos de Claude Code)

## 11. CLAUDE.md, rules, skill, slash command o subagent ⭐
**Qué es cada uno.** Son cinco formas de darle instrucciones o capacidades a Claude Code, y se diferencian por **cuándo se cargan** y **quién las dispara**:
- **CLAUDE.md**: instrucciones que se cargan **siempre**, en todas las sesiones. Para convenciones generales del proyecto.
- **Rules** (`.claude/rules/*.md` con `paths:`): instrucciones que se cargan **automáticamente solo cuando Claude trabaja en ciertos archivos** (por ejemplo, `**/*.graphql`). Ahorran tokens y **se aplican garantizado** en esos archivos.
- **Skill** (`.claude/skills/<nombre>/SKILL.md`): un procedimiento que se carga **solo cuando se usa**. Claude decide cargarla según su descripción, o la llamás vos. Como depende de que Claude la elija, **no está garantizado** que se aplique.
- **Slash command** (comando, `.claude/commands/<nombre>.md`): un prompt guardado que **vos** llamás con `/nombre`. Hoy comandos y skills son prácticamente lo mismo.
- **Subagent** (subagente, `.claude/agents/<nombre>.md`): otra instancia con su propio contexto, sus tools y su prompt, para delegar trabajo.

**Cómo se ve en la práctica: el frontmatter** (el bloque YAML entre `---` al principio del archivo).
- **Rule:** `paths: ["**/*.graphql"]`. Sin `paths`, la rule se carga siempre, como si fuera parte de CLAUDE.md.
- **Skill:**
  - `name` y `description`: la descripción es lo que Claude usa para decidir cuándo cargarla.
  - `allowed-tools`: limita las tools mientras corre la skill.
  - `context: fork`: la skill corre en un contexto aparte y devuelve solo el resultado.
  - `disable-model-invocation: true`: solo vos la podés llamar; Claude no la carga sola.
  - `argument-hint`: muestra qué argumento espera.
- **Comando:** el texto que escribís después de `/nombre` llega al prompt donde pusiste **`$ARGUMENTS`** (`/fix-issue 1234` → "Arreglá el issue #$ARGUMENTS").
- **Subagente:** `name`, `description` (cuándo delegarle), `tools` (por ejemplo, solo `Read, Grep, Glob`) y `model`.
- **Dónde va cada uno:** en `.claude/…` dentro del repo, para el equipo (viaja por git); en `~/.claude/…`, solo para vos.

**En qué se diferencian.** La pregunta clave es: **¿tiene que aplicarse siempre, solo en ciertos archivos, o solo cuando se pide?**

| Necesito… | Uso… |
|---|---|
| Que se aplique siempre, en todo el proyecto | CLAUDE.md |
| Que se aplique automáticamente en ciertos archivos, ahorrando tokens | Rules con `paths:` |
| Un procedimiento que se usa a veces | Skill (o comando) |
| Un atajo que llamo yo con `/` | Comando (Q4 de la guía: en `.claude/commands/`, para todo el equipo) |
| Delegar trabajo con contexto aislado | Subagente |

**La señal del enunciado.** "Reducir tokens **manteniendo las convenciones aplicadas** en Terraform" → rules con `paths:` (no skill: no hay garantía de que se cargue). Distractores de Q4: definir el comando dentro de CLAUDE.md, o un `.claude/config.json` con una lista de comandos (no existe).

**Ejemplo.** Las convenciones de GraphQL que solo importan en `*.graphql` → rule con `paths: ["**/*.graphql"]`. El procedimiento para crear una migración → skill `/new-migration`.

**Trampa frecuente: cuándo se carga una rule.** Las rules de `.claude/rules/` se cargan de una de dos formas:
- **Sin `paths`**: se cargan **siempre, al arrancar**, igual que el CLAUDE.md del proyecto.
- **Con `paths`** (**path-scoped rules**): quedan **fuera del contexto** hasta que Claude **lee, escribe o edita** un archivo que coincide con el glob, en cualquier momento de la sesión. Ver el archivo con un comando de lectura por Bash (como `cat`) también cuenta.

Entonces, si en una sesión Claude solo trabaja en `src/handlers/` y nunca toca un archivo de test, la rule de testing **nunca entra**. No es un error: es lo que se busca, porque así ahorra contexto.

Los distractores típicos describen mecanismos que no existen:
- **"Hay que importarla desde CLAUDE.md con `@`"**: no. Las rules de `.claude/rules/` se descubren solas. Los imports con `@` son para partir un CLAUDE.md en varios archivos, y lo importado se carga **al arrancar**, no según el archivo.
- **"Se evalúan una sola vez al arrancar"**: no. Una rule con `paths` puede entrar en cualquier momento de la sesión.
- **"Los globs solo aceptan carpetas"**: no. Aceptan extensiones en todo el árbol (`**/*.test.ts`).

Por eso una rule con glob es mejor que un CLAUDE.md de carpeta para convenciones repartidas por todo el repo: el glob coincide por **tipo de archivo** en cualquier carpeta, y el CLAUDE.md de carpeta solo cubre **esa** carpeta.

> 🧠 **Para recordar:** **siempre** = CLAUDE.md; **ciertos archivos** = rules; **a pedido** = skill/comando; una rule con `paths` entra **cuando se toca un archivo que coincide**.

---

## 12. CLAUDE.md hierarchy: usuario, proyecto, carpeta
**Qué es cada uno.** La **CLAUDE.md hierarchy** (jerarquía de CLAUDE.md) tiene varios niveles:
- **User** (usuario, `~/.claude/CLAUDE.md`): tuyo, para todos tus proyectos. **No viaja por git.**
- **Project** (proyecto, `./CLAUDE.md` en el repo): de todo el equipo.
- **Directory** (carpeta, `packages/x/CLAUDE.md`): se carga **cuando Claude trabaja en esa carpeta**.
- 📘 Además existen el nivel **managed** (lo define la organización y no se puede desactivar) y **`CLAUDE.local.md`** (personal dentro de un proyecto, fuera de git).

**Cómo se ve en la práctica.**
- **`/memory`** muestra qué archivos de memoria se cargaron en la sesión. Es la forma de diagnosticar "a mí no me aplica la regla".
- Los **imports con `@`** (`@docs/testing.md` dentro de un CLAUDE.md) sirven para **organizar** en varios archivos, pero **se cargan igual** al arrancar: no ahorran tokens. Para ahorrar, van las rules con `paths:`.
- **`claudeMdExcludes`** (en settings) excluye archivos CLAUDE.md que no querés cargar, por ejemplo los de otros equipos en un monorepo.

**Lo que se confunde.** Ningún nivel "gana" sobre otro: **se suman todos** al contexto. Si dos reglas se contradicen, Claude puede seguir cualquiera de las dos, así que hay que **eliminar la contradicción**, no confiar en que "el más específico manda".

**La señal del enunciado.** "Un compañero nuevo no recibe las convenciones que el tech lead sí tiene" → estaban en el nivel de **usuario** del tech lead; hay que pasarlas al del **proyecto**.

> 🧠 **Para recordar:** **se suman, no se pisan**; lo del equipo, **en el repo**; `@` organiza, no ahorra.

---

## 13. La versión personal de un comando o skill del equipo
**Qué es.** El equipo tiene `/release-notes` en el repo (`.claude/commands/release-notes.md` o `.claude/skills/release-notes/`), y vos querés una variante para vos.

**Lo que se confunde.** Ponerla en tu carpeta personal (`~/.claude/…`) con **el mismo nombre** no alcanza: con el mismo nombre, una tapa a la otra. La variante personal va en tu carpeta personal **y con otro nombre** (`~/.claude/skills/release-notes-slack/`).

**La señal del enunciado.** "Sin afectar a nadie más" y "sin cambiar la del equipo" → carpeta personal + **nombre distinto**.

> 🧠 **Para recordar:** personal = **tu carpeta + otro nombre**.

---

## 14. `allowed-tools`, reglas `deny` o un hook: el alcance de la restricción
**Qué es cada uno.** Son tres formas de impedir que Claude haga algo, con **alcances** distintos:
- **`allowed-tools`** en el frontmatter de una skill: limita qué tools puede usar Claude **mientras corre esa skill**. Para la guía, restringe a esas tools.
- **Permission rules** (reglas de permisos) en `settings.json`: `allow`, `ask` y **`deny`**. Por ejemplo, `"deny": ["Edit(config/secrets/**)", "Bash(rm -rf *)"]`. Se aplican a **toda la sesión**. Si una regla `allow` y una `deny` chocan, gana `deny`.
- **Hook** (`PreToolUse` con exit 2): se aplica a **toda la sesión** (o a todo el repo, según dónde se configure), puede mirar los argumentos y decidir con lógica propia.
- 📘 En la CLI, `--allowedTools` **aprueba** tools sin preguntar, mientras que `--disallowedTools` o `--tools` las **restringen**.

**En qué se diferencian.** El mecanismo tiene que tener **el mismo alcance que el problema**. Si el problema es que **una skill** hace algo de más, se acota esa skill. Un hook que bloquea Bash en todo el repo es "más fuerte", pero rompe los demás flujos que usan Bash legítimamente.

**La señal del enunciado.** "Sin afectar los otros flujos que usan Bash" → `allowed-tools` de la skill. "Nadie debe poder editar `config/secrets/` nunca" → regla `deny` o hook global.

> 🧠 **Para recordar:** el arreglo tiene **el alcance del problema**.

---

## 15. Plan mode o direct execution ⭐

**Qué es cada uno.**
- **Plan mode** (modo plan): Claude explora el código y propone un plan **sin modificar nada**, y vos lo aprobás antes de que actúe.
- **Direct execution** (ejecución directa): Claude hace el cambio.

**Cómo se ve en la práctica.** Se entra a plan mode con **Shift+Tab** (alterna los modos de permiso) o arrancando con `claude --permission-mode plan`. Para la exploración pesada, Claude Code puede usar el **Explore subagent**: un subagente de solo lectura que busca en su propio contexto y devuelve un resumen, así la conversación principal no se llena.

**En qué se diferencian.** Plan mode conviene cuando el cambio es **grande, con varios caminos posibles o con dependencias que no conocés**. Es la Q5 de la guía: migrar un monolito a microservicios → plan mode para explorar, entender las dependencias y diseñar antes de cambiar. La ejecución directa conviene cuando el cambio es **chico y claro** (corregir un typo, agregar un campo). Se pueden combinar: planificar y después ejecutar.

**La señal del enunciado.** "Varios archivos", "arquitectura", "no conocés el código", "decisiones de diseño" → plan mode. "Un cambio acotado y bien definido" → directo.

> 🧠 **Para recordar:** **grande o incierto** = plan; **chico y claro** = directo.

---

## 16. Iterative refinement: un mensaje o varios
**Qué es.** En el **iterative refinement** (refinamiento iterativo), cuando tenés varios problemas para corregir, podés mandarlos **todos en un mensaje** o **de a uno**.

**En qué se diferencian.** Si los problemas **interactúan** (arreglar uno cambia el otro), van **juntos**, para que Claude los resuelva de forma coherente. Si son **independientes**, conviene **de a uno**, para verificar cada cambio. En la misma pregunta puede haber de los dos tipos: algunos juntos y uno aparte.

**Lo que acompaña.** Las otras técnicas de la tarea 3.5:
- **Ejemplos concretos de entrada y salida**, cuando las descripciones en prosa no alcanzan.
- **Test-driven iteration** (iterar guiado por tests): escribir los tests primero y pedirle que los haga pasar.
- **Interview pattern** (patrón de entrevista): que Claude te haga preguntas antes de implementar algo poco definido.

**La señal del enunciado.** *"Separately"*, "un typo en un log que no tiene nada que ver" → aparte. "Los límites de peso y el cupón se afectan entre sí" → juntos.

**Trampa frecuente: en test-driven iteration, los tests no se tocan.** Escribir los tests primero funciona porque los tests son **el contrato**: definen el comportamiento esperado, y lo único que cambia hasta que pasen es la implementación. Pero si el prompt no lo dice, Claude puede tomar "que pasen todos los tests" como el objetivo y llegar por el camino más barato: **editar la expectativa del test** que falla. La suite queda en verde y el bug sigue (por ejemplo, los `null` mal manejados en una migración).

El arreglo es decirlo explícitamente: **"los tests no se borran ni se editan; iterá solo sobre la implementación"**. La guía de prompting de Anthropic lo recomienda tal cual para flujos test-first, porque editar un test esconde funcionalidad faltante o con bugs. Si el equipo quiere una **garantía** y no solo una instrucción, un hook `PreToolUse` que bloquee la edición de los archivos de test (guidance frente a enforcement, entrada 2).

Los distractores:
- **Más ejemplos de casos límite**: mejoran cómo generaliza la implementación, pero el test ya estaba bien. Lo que hay que prohibir es editarlo, y los ejemplos no prohíben nada.
- **Regenerar en sesiones nuevas hasta que pase**: repite el mismo comportamiento sin cambiar la instrucción.
- **Que autoevalúe su confianza en cada test y descarte los dudosos**: invita a borrar tests, y la confianza autoinformada no es confiable (entrada 20).

Señal: *"Claude edits that test's expected value so all the tests pass"* → los tests son fijos; se cambia solo el código.

> 🧠 **Para recordar:** **interactúan = juntos**; **independientes = de a uno**; en test-first, **el test no se toca**.

---

## 17. Claude Code en CI: `-p`, output formats y `--json-schema` ⭐

**Qué es cada uno.** En un pipeline de **CI/CD** (integración continua) no hay nadie mirando, así que Claude Code corre en **modo no interactivo** (también se lo llama *headless*).

| Flag | Qué hace |
|---|---|
| **`-p`** (o `--print`) | Modo no interactivo: ejecuta el prompt, imprime el resultado y **termina**. Sin `-p`, el job se queda esperando input hasta el timeout (Q10 de la guía) |
| `--output-format text` | La respuesta en texto plano (default) |
| `--output-format json` | Envuelve el resultado en un JSON con metadatos (costo, duración, id de sesión). **El texto de adentro sigue libre** |
| `--output-format stream-json` | Una línea JSON por evento, a medida que ocurren |
| **`--json-schema`** | Obliga a que la respuesta cumpla un schema; el resultado validado viene en el campo **`structured_output`** |
| `--allowedTools` / `--disallowedTools` | Aprueba o prohíbe tools sin preguntar (en CI no hay quien apruebe) |
| `--max-turns` | Tope de vueltas para que el job no quede girando |
| `--permission-mode` | El modo de permisos de la corrida |

**Lo que se confunde.**
- `--output-format json` solo **no** alcanza para que un script lea los hallazgos de forma confiable: hace falta **`--json-schema`**.
- No existen `--batch` ni `CLAUDE_HEADLESS=true`: son distractores. Redirigir la entrada desde `/dev/null` es un truco, no el modo documentado.
- No confundir con la **Message Batches API** (que es de la API, no de Claude Code).

**Cómo se ve en la práctica.**
```bash
claude -p "Revisá el diff de este PR con los criterios de CLAUDE.md" \
  --output-format json --json-schema review-schema.json
```
El CLAUDE.md del repo le da en CI los criterios de review, los estándares de testing y los fixtures disponibles. Para revisar con una **instancia independiente** (entrada 25), la revisión es **otra invocación** de `claude -p` que recibe solo el diff, no la sesión que generó el código. Al re-revisar después de nuevos commits, se le pasan los hallazgos anteriores y se le pide solo lo nuevo o lo no resuelto, para no duplicar comentarios.

**Comparado con la API.** Con la API directa armás vos el loop, definís las tools y usás `strict` o `output_config.format` para la forma. Con `claude -p`, Claude Code trae el loop, las tools built-in y el CLAUDE.md del repo; vos solo elegís flags.

> 🧠 **Para recordar:** CI = **`-p`**; forma garantizada = **`--json-schema`** → `structured_output`.

---

# Dominio 4 — Prompt Engineering & Structured Output (ingeniería de prompts y salida estructurada)

## 18. Explicit criteria, few-shot o JSON schema ⭐
**La idea central.** En el dominio 4 hay tres herramientas que se parecen porque las tres "mejoran la salida" de Claude. Pero cada una ataca **un problema distinto**, y elegir bien depende de identificar cuál es el problema.

**Explicit criteria (criterios explícitos, tarea 4.1).** Atacan la **vaguedad**. Cuando una instrucción admite varias lecturas ("revisá que el código esté bien", "reportá lo importante"), Claude elige una interpretación por su cuenta, y esa elección cambia de una corrida a otra. Un criterio explícito dice **qué** hacer, en términos concretos y verificables: qué se reporta y qué no, cuándo se escala y cuándo no. La pregunta que responde es "**¿qué quiero exactamente?**".

**Few-shot examples (ejemplos, tarea 4.2).** Atacan la **inconsistencia** cuando las instrucciones **ya están claras y no alcanzan**. Un ejemplo transmite a la vez el formato, el largo, el tono y el criterio, cosas que la prosa tiene que explicar de a una. Y sirve especialmente para mostrar **la frontera**: los casos ambiguos, donde la regla escrita no alcanza para decidir. La pregunta que responde es "**¿cómo se ve una buena respuesta, sobre todo en los casos difíciles?**". La guía pide **2 a 4 ejemplos** dirigidos a los casos ambiguos, cada uno con el **razonamiento** de por qué se eligió una opción y no la otra.

**JSON schema (tarea 4.3).** Garantiza la **forma** de la salida: que sea un JSON válido, con los campos y los tipos correctos. Se aplica con tool use o con structured outputs (entrada 22). No dice nada sobre si el contenido es correcto. La pregunta que responde es "**¿un programa va a poder leer esto siempre?**".

**En qué se diferencian.** Se piensan en orden:
1. ¿Está claro **qué** querés? Si no → **criterios**.
2. ¿Está claro, pero sale distinto cada vez o falla en los casos límite? → **ejemplos**.
3. ¿Tiene que salir **siempre** con una forma exacta para que la lea un programa? → **schema**.

A menudo se combinan: criterios + ejemplos (Q3: escalamiento), o schema + reglas de normalización (entrada 21).

**La señal del enunciado.**
- *"Too many false positives"*, *"be conservative didn't help"* → criterios.
- *"Detailed instructions already… yet inconsistent"* → ejemplos.
- *"Parse errors"*, *"missing fields"*, *"malformed JSON"* → schema.
- Few-shot cuando el problema son descripciones de tools mínimas (Q2) → distractor.

**Para cerrar la idea.** El bot de review de TiendaX deja comentarios sobre nombres de variables (falta **criterio**: decir qué no se reporta). Ya tiene criterios, pero cada hallazgo sale escrito distinto (faltan **ejemplos** del formato). Y el sistema que publica los comentarios falla porque a veces llega texto en vez de JSON (falta **schema**).

**Trampa frecuente: cuándo los ejemplos sí son la respuesta.** Una instrucción subjetiva como *"handle null values gracefully"* admite varias lecturas razonables (saltear, poner un valor por defecto, rechazar), y cada corrida elige una. Reforzar la redacción ("tiene que ser consistente") **sube la prioridad pero no agrega información**. Lo que funciona es **mostrar** el comportamiento con 2 o 3 ejemplos concretos de entrada y salida ("fila con email nulo → registro sin el campo email"). La diferencia con la entrada 6: allá lo esperado **ya estaba claro** y algo lo desviaba; acá lo esperado **nunca se dijo**.

> 🧠 **Para recordar:** **qué** = criterios; **cómo se ve y dónde está el borde** = ejemplos; **forma garantizada** = schema.

---

## 19. Confidence-based filtering o explicit categorical criteria ⭐
**La idea central.** Cuando un revisor automático genera demasiado ruido, hay dos formas de intentar reducirlo: pedirle que sea **más cauteloso**, o decirle **qué cuenta como problema**. La guía dice que la primera no funciona y la segunda sí.

**El problema: false positives.** Un **false positive** (falso positivo) es un hallazgo que el revisor reporta pero que no es un problema real. Cuando hay muchos, los desarrolladores dejan de leer los comentarios del bot. La **precision** (precisión) es la proporción de hallazgos reportados que son reales; el **recall** (exhaustividad) es la proporción de los problemas reales que el revisor efectivamente reporta. Lo que se busca es subir la precisión **sin perder** recall.

**Por qué falla la cautela.** Frases como *"Be conservative"* (sé conservador), *"Only report findings you are highly confident about"* (reportá solo lo que tengas mucha confianza) u *"Only report important issues"* (solo lo importante) parecen razonables, pero **no definen nada**. Le dicen al revisor **cuánto** reportar, no **qué**. Claude tiene que decidir solo qué significa "mucha confianza" o "importante", y pasan tres cosas:
1. **Inconsistencia:** cada corrida interpreta distinto.
2. **El ruido sigue mezclado:** reporta menos de todo, incluidos los bugs, no solo menos estilo.
3. **Se pierden bugs reales:** puede encontrar un problema y no reportarlo porque "no estaba seguro". Sube la precisión, pero baja el recall, y nadie se entera.

Lo mismo vale para filtrar con un umbral numérico ("publicar solo los hallazgos con confianza > 0,8"): la confianza que el modelo se asigna no es un criterio, y la guía pide criterios por categoría *"rather than relying on confidence-based filtering"*.

**Qué funciona: explicit categorical criteria.** Los **criterios explícitos por categoría** reemplazan "cuánto" por "qué". Se escriben **dos listas**:
- **Qué se reporta:** las categorías que importan (bugs que cambian el comportamiento, problemas de seguridad, comentarios que contradicen lo que hace el código).
- **Qué no se reporta:** lo que es ruido para el equipo (estilo menor, nombres, patrones que se repiten en todo el repo, lo que ya chequea el linter).

Con eso, el revisor no decide según su confianza: para cada hallazgo se pregunta "¿esto cae en una categoría que se reporta?". Hacen falta **las dos listas**: si solo decís qué reportar, el ruido de estilo sigue. El ejemplo de la guía: *"check that comments are accurate"* es vago; *"flag comments only when claimed behavior contradicts actual code behavior"* es un criterio explícito.

**Cuando el enunciado nombra la causa.** Si dice que alguien **ya agregó** la frase de cautela y después se escapó un bug, esa frase es **la causa**. La respuesta correcta tiene que **sacarla** y reemplazarla por categorías. Agregar categorías dejando la frase no resuelve el problema.

**Lo que viene junto: developer trust.** Los falsos positivos de **una** categoría hacen que el equipo desconfíe de **todo** el revisor (**developer trust**, la confianza del equipo en la herramienta). Si la categoría "rendimiento" falla la mitad de las veces, los devs empiezan a ignorar también los comentarios de seguridad. La guía pide **temporarily disable the high false-positive category** (desactivar temporalmente solo esa categoría) mientras se reescribe su criterio. Las demás siguen activas. Se reactiva después de **medir** el nuevo criterio contra PRs cuya respuesta ya conocés, no porque "parece que mejoró".

**Y para la severidad:** cada nivel ("crítico", "importante", "menor") se define con un **criterio** (qué consecuencia lo hace entrar en ese nivel) y **un ejemplo de código concreto**. Definirlos solo con adjetivos ("crítico = serio") hace que el mismo problema salga con un nivel distinto en cada PR.

**La señal del enunciado.** *"Too many false positives"*, *"developers ignore the bot"*, *"be conservative didn't help"* → criterios por categoría. *"Developers now ignore all findings, including valid ones"* → desactivar temporalmente la categoría ruidosa. *"Same issue labeled critical in one PR and minor in another"* → criterio + ejemplo por nivel.

**Para cerrar la idea.** El bot de TiendaX deja 31 comentarios por PR, casi todos de nombres. Alguien agrega "only report high-confidence findings": bajan a 12, pero se escapa un descuento aplicado en pesos sobre `priceCents`. La solución: sacar esa frase y escribir "Reportá: bugs que cambian el comportamiento, montos que no están en centavos, seguridad. No reportes: nombres, formato, patrones del repo".

> 🧠 **Para recordar:** contra el ruido, **qué reportar y qué no**, nunca "cuánta confianza"; si la frase de cautela causó el problema, **se va**.

---

## 20. Self-reported confidence: para escalar no, para enrutar revisiones sí (calibrada) ⭐

**La idea central.** El modelo puede informar qué tan seguro está de una respuesta. Ese número aparece en varias tareas del examen, y **el veredicto cambia según para qué se use**. Entender por qué es la clave.

**Qué es la confianza autoinformada.** La **self-reported confidence** es un número (de 1 a 10, o de 0 a 1) que Claude escribe porque se lo pediste, por ejemplo en un campo del schema. **No es una probabilidad interna del modelo**: es una estimación que el modelo hace sobre sí mismo. Y esa estimación suele estar **poorly calibrated** (mal calibrada): un 0,9 no significa que acierte el 90% de las veces. Peor: el modelo suele estar **muy seguro justamente en los casos difíciles** en los que se equivoca.

**Por qué no sirve para escalar (tarea 5.2, Q3).** Si decidís escalar un caso de soporte "cuando la confianza es baja", el agente va a escalar casos simples en los que dudó y va a quedarse con casos complejos en los que estaba equivocadamente seguro. Es exactamente lo que describe la Q3. Para escalar, la respuesta son **criterios explícitos de escalamiento con ejemplos**.

**Por qué sí sirve para enrutar revisiones (tareas 4.6 y 5.5), con una condición.** Cuando hay que decidir **qué extracciones o hallazgos revisa una persona**, la confianza es útil si se cumplen dos cosas:
- **Por campo o por hallazgo**, no un número único por documento: un documento puede tener el total seguro y el vencimiento dudoso.
- **Calibrated thresholds** (umbrales calibrados): el umbral no se elige "a ojo". Se toma un **labeled validation set** (un conjunto de casos cuya respuesta correcta ya conocés, etiquetados por personas), se compara la confianza del modelo con los aciertos reales, y se elige el umbral con datos: "con confianza ≥ 0,93, este campo acierta el 99% de las veces".

Calibrado, el número deja de ser una opinión del modelo y pasa a ser una medida verificada.

**Y para filtrar hallazgos de un revisor (tarea 4.1).** Filtrar por confianza rinde menos que los criterios por categoría (entrada 19).

**La señal del enunciado.**
- "Escalar cuando la confianza es baja" → distractor.
- "Decidir qué revisa una persona, con umbrales calibrados contra casos etiquetados" → correcto.
- *"In a pilot, findings rated above 0.9 were wrong 18% of the time"* → hay que **calibrar**.

**Para cerrar la idea.** SoporteBot escala cuando su confianza baja de 7: escala devoluciones simples y se queda con reembolsos fuera de plazo (mal). En cambio, la extracción de facturas manda a revisión los campos con confianza por debajo de un umbral calibrado con 500 facturas etiquetadas (bien).

> 🧠 **Para recordar:** confianza **cruda** = nunca; **calibrada y por campo** = solo para enrutar revisiones.

---

## 21. Nullable, `"other"` + detail o `"unclear"` en un schema

**La idea central.** Un schema no solo define la forma de la salida: también **empuja** el comportamiento de Claude. Si el schema no le da una forma honesta de decir "no sé" o "no está", Claude **inventa** algo para cumplirlo. Estas tres opciones son las salidas honestas.

**Required vs. nullable/optional.** Un campo **required** (obligatorio) tiene que tener un valor. Si el documento no trae ese dato, Claude se ve forzado a poner algo, y lo inventa (**fabrication**). Un campo **nullable** acepta `null` como valor (`"type": ["string", "null"]`); un campo **optional** (opcional) queda fuera de la lista `required`. Las dos variantes le permiten a Claude decir "el documento no lo dice". La guía pide marcar así los campos que **pueden no estar** en la fuente.

**Enums con escape.** Un **enum** es una lista cerrada de valores permitidos (`"merchandise"`, `"freight"`, `"services"`). Es útil porque el sistema que recibe el dato sabe qué esperar. Pero si un documento no encaja en ninguna categoría, un enum cerrado obliga a meterlo en la más parecida, aunque sea incorrecta. La guía pide dos salidas:
- **`"other"` + un campo de detalle** (por ejemplo, `category_detail`): para un valor **válido que no está en la lista**. Claude elige `"other"` y escribe cuál es. Así la lista sigue cerrada (se puede validar) y además se puede ampliar viendo qué aparece en el detalle.
- **`"unclear"`**: para cuando el documento es **ambiguo** y no permite decidir.

**Format normalization rules.** Si los documentos traen el mismo dato en formatos distintos (fechas como "15/12", "15 de diciembre" o "2026-12-15"), el schema exige el formato final, pero no le explica a Claude cómo convertir cada variante. Por eso la guía pide **reglas de normalización en el prompt**, junto al schema: "normalizá las fechas a AAAA-MM-DD; si no hay año, usá el de emisión".

| Situación | Salida |
|---|---|
| El dato **no está** en el documento | `null` |
| El dato está, pero **no encaja** en la lista | `"other"` + detalle |
| El documento es **ambiguo** | `"unclear"` |

**La señal del enunciado.** "Completa números de orden que no existen" → nullable. "Las facturas de alquiler terminan como servicios" → `"other"` + detalle. "Facturas mezcladas que no se pueden clasificar" → `"unclear"`. Si piden "mantener la lista cerrada", reemplazar el enum por texto libre es distractor. "Decirle que no invente" no saca la presión del campo obligatorio.

**Para cerrar la idea.** Los proveedores chicos de TiendaX no mandan número de orden de compra, y `purchase_order` (obligatorio) salía como "OC-0001". Pasa a nullable y aparece `null`. Las facturas de alquiler pasan de `"services"` a `"other"` con detalle `"alquiler"`.

> 🧠 **Para recordar:** **ausente** = null; **no listado** = other + detalle; **ambiguo** = unclear.

---

## 22. Syntax errors o semantic errors: qué garantiza el schema ⭐

**La idea central.** Hay dos clases de error muy distintas en una salida estructurada, y el schema solo resuelve una. Confundirlas lleva a creer que "con el schema ya está todo validado".

**Cómo se garantiza la forma.** La guía dice que la forma más confiable de lograr una salida que cumpla un schema es **tool use with a JSON schema**: definís una tool cuyo `input_schema` es la estructura que querés extraer, Claude la "llama", y vos leés los datos del bloque `tool_use`. La tool **nunca se ejecuta**: es solo una forma de salida.
- **`strict: true`** en la definición de la tool garantiza que **los argumentos** cumplan el schema: tipos correctos y campos obligatorios presentes.
- **Structured outputs** (`output_config.format` con un JSON schema) garantiza que **toda la respuesta** sea un JSON que cumpla el schema.
- Las dos usan **constrained decoding** (decodificación restringida): mientras genera, Claude solo puede producir texto que cumpla el schema.
- **Dos excepciones:** si el `stop_reason` es **`refusal`** (Claude se negó; llega como respuesta normal, no como error) o **`max_tokens`** (se cortó), el JSON puede venir incompleto. Hay que revisar el `stop_reason` antes de usar el resultado.

**Qué resuelve y qué no.**
- **Syntax / schema errors** (errores de sintaxis o de schema): JSON mal formado, un campo obligatorio que falta, un número que vino como texto. **Los elimina** tool use con schema (y `strict`).
- **Semantic errors** (errores semánticos): el JSON es perfecto, pero **el contenido está mal**: las líneas no suman el total, la fecha de emisión quedó en el campo del vencimiento. **El schema no los ve**, porque solo mira la forma.

Los errores semánticos se detectan con **validación en código** (reglas de negocio: ¿suman las líneas?, ¿el vencimiento es posterior a la emisión?) y se corrigen con un reintento que lleva el error (entrada 23).

**La señal del enunciado.** "Con `strict` los errores de parseo bajaron a cero, **pero**…" → semántico. Distractores: endurecer el schema (`additionalProperties: false`, más campos obligatorios), cambiar `tool_choice`, agregar ejemplos de JSON. Ninguno mira los valores.

**Para cerrar la idea.** Una factura sale con `total_cents: 9000000` y tres líneas que suman 8.100.000. El JSON es válido y el schema no tiene nada que objetar. La regla "las líneas tienen que sumar el total", escrita en código, detecta el problema.

> 🧠 **Para recordar:** el schema garantiza la **forma**; los **valores** se validan en código.

---

## 23. Retry with error feedback: cuándo y cómo reintentar ⭐
**La idea central.** Un reintento solo sirve si Claude tiene **algo nuevo** con qué corregir **y** si la información necesaria **está disponible**. Hay tres preguntas distintas, y el examen pregunta las tres.

**1. ¿Qué lleva un buen reintento?** La guía lo llama **retry with error feedback** (reintentar con el error). Un "intentá de nuevo" no le da a Claude ninguna información nueva, así que repite el mismo error. El reintento útil lleva **tres cosas**:
- **El documento original**, para que vuelva a mirar la fuente.
- **La extracción que falló**, para que vea qué había respondido.
- **El error de validación específico**: qué regla falló, en qué campo y con qué valores ("`due_date` 2026-11-01 es anterior a `issue_date` 2026-11-15").

Conviene pedirle que corrija **solo** los campos afectados y deje el resto igual. Subir la temperatura no es la palanca (y en los modelos actuales ni se puede cambiar).

**2. ¿Cuándo un reintento no sirve?** Un reintento corrige errores de **lectura o de escritura**: un formato mal convertido, un campo en el lugar equivocado, una estructura incompleta. Pero si **el dato no está** en lo que recibió Claude (por ejemplo, porque está en **otro documento que no se mandó**), ningún reintento lo hace aparecer. Ahí va `null`, se marca como pendiente, se pide el documento o se escala. Sacarlo de otro lado (las facturas anteriores del proveedor) es **inventarlo**.

**3. ¿Qué se reintenta localmente entre agentes?** Las fallas **transitorias** (timeout, HTTP 429 de rate limit, 503) se reintentan con un límite, idealmente con **exponential backoff** (esperar cada vez más entre intentos). Las fallas de **permiso o autenticación** (401, 403, credencial vencida) no se arreglan esperando: se propagan enseguida con su contexto.

**Lo que acompaña: campos que ayudan a validar.**
- **`calculated_total` y `stated_total`:** el modelo extrae el total que **suma** de las líneas y el que **dice** el documento. Si no coinciden, el problema queda a la vista, en lugar de "corregirse" en silencio.
- **`conflict_detected`:** un booleano que marca cuando el propio documento se contradice (por ejemplo, dos vencimientos distintos).
- **`detected_pattern`:** en un revisor de código, registra qué construcción disparó cada hallazgo. Cuando los devs descartan hallazgos, permite analizar qué patrones generan falsos positivos.

**La señal del enunciado.**
- *"Retries return exactly the same values"* (devuelven exactamente lo mismo que el primer intento) → falta el error específico.
- *"The delivery note arrives separately, hours later"* (el remito llega aparte, horas después) o *"exists only in an external document"* → no reintentar.
- *"Credential expired"*, *"403"* (por ejemplo, por suscripción) → propagar sin reintentar.

**Para cerrar la idea.** La validación de TiendaX detecta un vencimiento anterior a la emisión: reintenta con la factura, la extracción y la regla que falló, y se corrige. Otra factura dice "OC según remito adjunto", pero el remito no vino: no se reintenta; queda `purchase_order: null` y pendiente del remito.

> 🧠 **Para recordar:** reintento = **documento + respuesta + error**; si el dato **no está**, no se reintenta; **permisos**, no se reintentan.

---

## 24. Message Batches API o synchronous API ⭐
**La idea central.** La **Message Batches API** (API de lotes) cambia **tiempo por costo**: es más barata, pero no responde en el momento. Todo lo que pregunta el examen sale de entender ese intercambio y sus dos consecuencias: **no sirve para lo que alguien espera**, y **los plazos se calculan con el peor caso**.

**Qué es cada una.**
- La **synchronous API** (API normal, síncrona) responde en el momento: mandás un pedido y esperás la respuesta.
- La **Message Batches API** procesa muchos pedidos de forma **asíncrona**: los mandás todos juntos y la API los procesa cuando puede. Cuesta **50% menos**. La mayoría de los lotes terminan en menos de una hora, pero la API solo garantiza **hasta 24 horas**, y **no hay SLA de latencia** (no hay un tiempo de respuesta comprometido).

**Cómo se ve en la práctica.**
- Se crea un lote con **`messages.batches.create`**, con una lista de pedidos. Cada uno lleva un **`custom_id`** que elegís vos (por ejemplo, el número de factura) y los mismos parámetros que un pedido normal.
- No hay aviso cuando termina: se **consulta periódicamente** el estado (`processing_status`) hasta que diga que terminó (polling).
- Cada resultado vuelve con uno de cuatro estados: **`succeeded`** (salió bien), **`errored`** (hubo un error), **`expired`** (no se procesó en 24 horas) o **`canceled`**. Los tres últimos no se cobran.
- Los resultados **vuelven en cualquier orden**, por eso se cruzan por **`custom_id`**. Leerlos por posición es un error que falla en silencio: cada resultado queda pegado al documento equivocado.
- 📘 Límites de la documentación: hasta **100.000 pedidos o 256 MB** por lote, y los resultados quedan disponibles **29 días**.
- **Cada pedido del lote es un solo turno.** Claude puede pedir una tool, pero vos no podés ejecutarla y devolverle el resultado dentro del mismo pedido para que siga. Si el flujo necesita ese ida y vuelta, no va en lote.

**Cuándo va cada una.** Si algo **bloquea** a una persona o a un proceso (el check antes del merge, la respuesta a un cliente), va en la API normal. Si **nadie espera** (reportes nocturnos, auditorías semanales, generación nocturna de tests, procesar un archivo histórico), va en lotes. Es la Q11 de la guía: el reporte nocturno de deuda técnica pasa a lotes; el check pre-merge sigue en la API normal. Sus distractores: pasar los dos a lotes "con polling" (no hay garantía de tiempo), pasar los dos con "fallback a tiempo real si tarda" (complejidad innecesaria), o mantener los dos en tiempo real "por el orden de los resultados" (se resuelve con `custom_id`).

**El SLA, paso a paso.** Un **SLA** (service level agreement, acuerdo de nivel de servicio) es un compromiso de tiempo: "toda factura que llega se procesa en **30 horas** como máximo". La pregunta del examen es **cada cuánto hay que mandar un lote** para cumplirlo.

Pensalo con una sola factura, en el **peor caso**. Su recorrido tiene dos esperas:
1. **Esperar a que salga el próximo lote.** Si mandás un lote cada X horas, en el peor caso la factura llega justo después de un envío y espera **X horas** enteras.
2. **Esperar a que el lote se procese.** En el peor caso, **24 horas**.

En el peor caso, la factura tarda **X + 24 horas**. Para cumplir el SLA: **X + 24 ≤ 30**, o sea **X ≤ 6 horas**.

| Mandás un lote cada… | Peor caso | ¿Cumple 30 h? |
|---|---|---|
| 24 horas (una vez por noche) | 24 + 24 = 48 h | ✗ |
| 6 horas | 6 + 24 = 30 h | Justo, sin margen |
| **4 horas** | 4 + 24 = 28 h | ✓ con 2 h de margen |

Por eso la guía da como ejemplo **"4-hour windows to guarantee a 30-hour SLA"**.

La trampa típica: el enunciado dice *"most test batches completed in under an hour"* (la mayoría terminó en menos de una hora). Si calculás con eso, un lote por noche parece suficiente. Pero un SLA es una **garantía**, y una garantía se calcula con el **peor caso**, no con lo que suele pasar.

**Las fallas, paso a paso.** Cuando termina un lote de 1.000 facturas y fallaron 40:
- Se reenvían **solo las 40**, identificadas por `custom_id`. Reenviar las 1.000 es pagar de nuevo las 960 que ya salieron.
- Se reenvían **corregidas según la causa**: las que fallaron por un error del servidor, igual; las que **excedieron el contexto**, **partidas en pedazos** (chunking) antes, porque reenviarlas igual falla igual.
- **Antes de procesar un volumen grande**, se prueba el prompt con una muestra chica (por ejemplo, 200 de 8.000). Si hay un error en el prompt, aparece con 200 documentos y no después de pagar 8.000.

**Para cerrar la idea.** TiendaX procesa su archivo histórico de 8.000 facturas en lotes, después de probar el prompt con 200. Las facturas nuevas salen en un lote cada 4 horas. El check de PRs sigue en la API normal, porque los devs esperan el resultado para mergear.

> 🧠 **Para recordar:** **alguien espera** = API normal; **intervalo + 24 h ≤ SLA** (peor caso); reenviar **solo lo fallido, por `custom_id`, corregido**.

---

## 25. Self-review, extended thinking o independent review instance ⭐

**La idea central.** Revisar bien depende menos de "pensar más" que de **no compartir el razonamiento** de quien hizo el trabajo.

**Qué es cada uno.**
- **Self-review** (auto-revisión): la sesión que generó el código lo revisa. Tiene el mismo razonamiento que usó para escribirlo, así que difícilmente cuestione sus propias decisiones. Es como releer tu propio texto: leés lo que quisiste escribir, no lo que escribiste.
- **Extended thinking** en esa misma sesión: más razonamiento, pero con el mismo sesgo.
- **Independent review instance** (instancia de revisión independiente): otra llamada que recibe **solo el código y los criterios**, sin el razonamiento del generador.

**En qué se diferencian.** La guía dice que la instancia independiente encuentra más problemas sutiles que las otras dos. No hace falta que sea un modelo más grande: lo que importa es que **no tenga el contexto del generador**. Pasarle el transcript completo a la segunda instancia arruina la independencia, porque hereda el mismo sesgo.

**Cómo se ve en la práctica.** En CI: un job genera el parche con `claude -p` y **otro job distinto** lo revisa con `claude -p`, recibiendo solo el diff y los criterios del CLAUDE.md. En el Agent SDK: un subagente revisor con su propio prompt, al que se le pasa solo el resultado.

**La señal del enunciado.** *"The same session is asked to review"*, *"confirms 97%"*, *"proposes enabling extended thinking for the self-review"* → instancia independiente.

> 🧠 **Para recordar:** revisar = **otra instancia, sin el contexto del generador**.

---

## 26. Per-file pass o cross-file integration pass ⭐

**La idea central.** Cuando el material a revisar es grande, el problema no es el espacio sino **cómo se reparte la atención**.

**Qué es cada uno.** Cuando un PR toca muchos archivos, revisarlo de una vez produce **attention dilution** (dilución de la atención): unos archivos se revisan a fondo y otros por arriba, y aparecen hallazgos contradictorios.
- **Per-file passes** (pasadas por archivo): cada archivo con toda la atención, para los **problemas locales**.
- **Cross-file integration pass** (pasada de integración): mira cómo **fluyen los datos entre archivos** (una función que cambió lo que devuelve y otro archivo que lo sigue usando igual).

**En qué se diferencian.** Hacen falta **las dos** (Q12 de la guía). Sin la de integración, se pierden los bugs que solo aparecen al juntar archivos.

**Lo que acompaña.** La guía agrega **verification passes** (pasadas de verificación) donde el modelo informa su confianza en cada hallazgo, para enrutar: lo de confianza alta se publica y lo dudoso va a una persona, siempre con **umbrales calibrados** (entrada 20).

**La señal del enunciado.** *"Inconsistent depth"*, *"contradictory findings"*, *"missed a bug across files"* → por archivo + integración. Distractores de Q12: un modelo con más contexto (el problema es la atención, no el espacio), tres pasadas completas y quedarse con lo que aparece en dos de tres (descarta bugs reales), pedir PRs más chicos (le traslada el problema al equipo).

**Trampa frecuente: lo mismo vale para documentos largos.** Un contrato largo, extraído en una sola pasada, muestra los mismos síntomas que el PR grande: algunas secciones salen extraídas a fondo y otras por arriba, y una cláusula se captura en una sección y se pierde en otra idéntica. Esto se suele llamar **context rot** (degradación por contexto); la calidad del análisis baja a medida que crece lo que el modelo tiene que procesar, **mucho antes** de llenar la ventana de contexto. La ventana es un límite de **capacidad**; la calidad es otro límite, más blando, que aparece antes. Por eso un modelo con más contexto no lo arregla.

El arreglo tiene las mismas dos partes que la Q12:
- **Per-section passes** (pasadas por sección): cada sección recibe la misma cantidad de análisis, así la profundidad queda pareja.
- **Reconciliation pass** (pasada de reconciliación): una etapa aparte que compara lo extraído **entre secciones** y detecta huecos e inconsistencias (la cláusula capturada en una sección y perdida en otra). Ninguna pasada local puede verlo, porque cada una mira solo su sección.

Los distractores:
- **Marcar todos los campos como `required` "para que extraiga cada sección con la misma profundidad"**: `required` controla la **forma** de la salida, no qué tan bien se analiza. Y si la sección no tiene el dato, empuja a inventarlo (entrada 21).
- **Correr la extracción tres veces y quedarse con lo que aparece en dos**: las tres corridas tienen el mismo problema, y el voto descarta extracciones reales que salieron una sola vez.

> 🧠 **Para recordar:** mucho material (código **o** documento) = **por partes + una pasada de integración**.

---

# Dominio 5 — Context Management & Reliability (manejo del contexto y confiabilidad)

## 27. Case facts block, scratchpad file, `/compact` o server-side compaction ⭐

**Qué es cada uno.** Los cuatro tienen que ver con no perder información en sesiones largas, pero cada uno corresponde a una situación:
- **Case facts block** (bloque de hechos del caso, tarea 5.1): en una **conversación con un cliente**, los montos, fechas, números de pedido, estados y lo que el cliente espera se sacan a un bloque que va **en cada prompt, fuera del historial resumido**. Con varios problemas, **una entrada por problema**, cada una con su número de pedido, monto y estado.
- **Scratchpad file** (archivo de notas, tarea 5.4): en una **exploración de código**, un archivo donde se anotan los hallazgos (clases, rutas, valores exactos) y que se **consulta antes de cada pregunta**.
- **`/compact`** (tarea 5.4): resume la conversación de Claude Code para liberar contexto **en la misma tarea**. Acepta un foco: `/compact conservá las clases del flujo de reembolsos`. Es un resumen, así que puede perder valores exactos.
- **Server-side compaction** (compactación automática; documentación, no está en la guía): la API resume sola cuando la conversación crece. También es un resumen.

**Por qué los resúmenes pierden datos.** El **progressive summarization** (resumen progresivo) cambia precisión por fluidez: se pierden números, porcentajes, fechas y lo que el cliente dijo que esperaba. Y la pérdida se acumula en cada pasada. Por eso lo que **no se puede perder** va **afuera del resumen**. Pedirle al resumidor que "conserve los números" no alcanza.

**Cómo se ve en la práctica.**
- **El bloque de case facts** va en una sección propia del prompt (por ejemplo, `<case_facts>` en el system prompt), con una instrucción explícita de consultarlo antes de responder.
- **El scratchpad** se hace leer nombrándolo en el CLAUDE.md o cargándolo con un hook **`SessionStart`**, y conviene actualizarlo antes de cerrar cada sesión.
- **Las respuestas de las tools** se recortan a los campos relevantes **antes** de entrar al contexto (*"40+ fields when only 5 are relevant"*), en el código que envuelve a la tool.
- **En entradas largas** (por ejemplo, los resultados de varios subagentes), el resumen de hallazgos va **al principio**, con encabezados por sección, por el efecto **lost in the middle**: lo del medio se pierde.

**La señal del enunciado.** "Soporte, conversación larga, se pierde el monto" → case facts. "Exploración de código, habla de *typical patterns* en vez de las clases que encontró" → scratchpad. "El contexto se llenó de salida de búsquedas y la tarea sigue" → `/compact`. "Activar compaction para no perder datos" o "pedirle al resumidor que conserve los números" → distractores.

> 🧠 **Para recordar:** **cliente** = case facts; **código** = scratchpad; **resúmenes** = pierden detalle.

---

## 28. `/compact`, `/clear` o una sesión nueva

**Qué es cada uno.**
- **`/compact [foco]`**: resume y sigue **la misma tarea**.
- **`/clear`**: borra todo el contexto; para pasar a **otra tarea**.
- **Sesión nueva con un resumen**: cuando el contexto anterior **quedó viejo** (entrada 5).

**La señal del enunciado.** "Seguir con el mismo mapeo" → `/compact`. "Empezar algo no relacionado" → `/clear`. "El código cambió desde ayer" → sesión nueva con resumen.

> 🧠 **Para recordar:** **misma** tarea = compact; **otra** tarea = clear; **contexto viejo** = nueva + resumen.

---

## 29. Escalation: escalar, rechazar, ofrecer resolver o pedir más datos ⭐

**Qué es.** La **escalation** (escalamiento) es pasarle el caso a una persona; en SoporteBot, con la tool `escalate_to_human`. La guía dice cuándo va cada respuesta:

| Situación | Respuesta |
|---|---|
| El cliente **pide explícitamente** una persona (**explicit request for a human**) | **Escalar ya**, sin investigar primero |
| El cliente está **frustrado**, el caso es simple y no pidió una persona | **Reconocer y ofrecer resolver**; escalar si **insiste** |
| La política **no dice nada** o es ambigua sobre el pedido (**policy gap**, como igualar el precio de un competidor) | **Escalar** |
| El pedido necesita una **excepción** que el agente no puede dar (**policy exception**) | **Escalar** |
| La política **prohíbe claramente** el pedido y no hay nada especial | **Rechazar** y explicar |
| El agente **lo intentó de verdad y no puede avanzar** (**inability to make progress**) | **Escalar** |
| La búsqueda devuelve **varias coincidencias** (**multiple matches**) | **Pedir un dato más** al cliente; no elegir ni escalar |
| El caso es **complejo**, pero la política lo cubre | **Resolver** |

**Lo que no sirve para escalar:** el **sentiment** (análisis de sentimiento: el enojo no indica complejidad) y la **self-reported confidence** (entrada 20). Para calibrar el escalamiento, **criterios explícitos con ejemplos** en el system prompt (Q3). Si una regla de escalamiento tiene que cumplirse **siempre** (un monto máximo), va en código, con un hook (entrada 2).

**El traspaso.** Al escalar, la persona **no ve la conversación**. Se le pasa un **structured handoff summary** (resumen estructurado de traspaso): ID del cliente, causa, monto y acción recomendada. No el transcript completo. Cómo se diseña ese resumen con un schema, en la entrada 36.

**Trampa frecuente: no investigar "para el handoff".** El ticket decía *"route this straight to an on-call engineer, do not attempt an automated fix"*, y la falla parecía trivial. Escalar ya significa **no hacer nada más**:
- **No intentar el arreglo**, aunque parezca fácil. "Intentar primero y escalar si falla" es el patrón correcto **solo** cuando nadie pidió una persona.
- **No correr diagnósticos "para que el ingeniero reciba contexto completo"**. Los diagnósticos **son** investigación, y el pedido la descartó. Era la opción tentadora, porque suena a ayudar.
- **No autoevaluar la confianza** para decidir si escalar: el pedido explícito ya es la señal más clara posible.

El handoff se arma con lo que ya hay: el contenido del ticket y el motivo del escalamiento. Ignorar una instrucción explícita para "mostrar lo que el agente puede hacer" daña la confianza en la automatización mucho más que saltearse un arreglo fácil.

Señal: el pedido de una persona viene **con una prohibición explícita** (*"do not attempt"*, *"do not investigate"*) → escalar sin hacer **ningún** trabajo previo.

> 🧠 **Para recordar:** **pide persona** = ya, **sin investigar ni "preparar contexto"**; **enojado** = ofrecer; **política muda** = escalar; **política que prohíbe** = rechazar; **varios clientes** = preguntar.

---

## 30. Conflicting sources: elegir, promediar o anotar ⭐

**Qué es.** Dos fuentes confiables dan cifras distintas (12% y 8%).

**Lo que se confunde.** El curso propone reglas automáticas ("quedarse con la más nueva", "con la más autorizada"). La guía pide **no elegir arbitrariamente**: el subagente que analiza devuelve **los dos valores con su fuente, marcados como conflicto**, y **decide el coordinador** cómo reconciliarlos. Promediar inventa un número que nadie dijo. Y antes de llamarlo conflicto, hay que mirar **las fechas**: si una cifra es de 2024 y otra de 2026, puede ser un cambio en el tiempo, no una contradicción. Por eso la guía pide que los subagentes incluyan la **publication or collection date** (fecha de publicación o de recolección) de cada dato.

**Lo que acompaña.**
- Cada afirmación viaja con su fuente: un **claim-source mapping** (mapeo afirmación-fuente) con la URL, el nombre del documento, el fragmento y la fecha. La síntesis lo **conserva y combina**. Una bibliografía al final no alcanza, porque no dice qué dato sale de qué fuente.
- El informe separa hallazgos **well-established** (establecidos) de **contested** (disputados), conservando cómo lo dijo la fuente ("estimación preliminar" sigue siendo preliminar).
- Cada contenido va en su formato: **tablas para números, prosa para noticias, listas para lo técnico**.

> 🧠 **Para recordar:** conflicto = **los dos, con fuente y fecha; decide el coordinador**.

---

## 31. Aggregate accuracy, accuracy por segmento y stratified sampling ⭐

**Qué es cada uno.**
- **Aggregate accuracy** (accuracy total): el porcentaje de aciertos de todo el sistema. Puede **esconder** un tipo de documento o un campo que sale mal.
- **Accuracy by document type and field** (accuracy por segmento): medida por tipo de documento y por campo. Se mide **antes de automatizar**.
- **Stratified random sampling of high-confidence extractions** (muestreo aleatorio estratificado de las de alta confianza): una vez que lo de confianza alta se acepta sin revisión, se sigue revisando una muestra al azar **dentro de cada grupo** (por tipo de documento, por proveedor), para **medir el error real** y **detectar errores nuevos**.

**Lo que se confunde.** El curso usa el muestreo estratificado para "encontrar más errores en lo dudoso". La guía lo usa para **vigilar lo que se automatiza**. Lo dudoso va directo a revisión humana (junto con los documentos ambiguos o contradictorios); eso es **routing to human review** (enrutar a revisión), no muestrear.

> 🧠 **Para recordar:** **antes** de automatizar, medir por segmento; **después**, muestrear lo de **alta** confianza.

---

## 32. Structured error context o generic error status ⭐

**Qué es.** Cuando un subagente falla, puede devolver un **generic error status** (estado genérico, como *"search unavailable"*) o un **structured error context** (contexto de error estructurado) con cuatro cosas: **failure type** (tipo de falla), **attempted query** (qué se intentó), **partial results** (resultados parciales) y **alternative approaches** (alternativas).

**En qué se diferencian.** Con el estado genérico, el coordinador no sabe si reintentar, cambiar de fuente o seguir. Con el contexto estructurado, decide bien (Q8 de la guía). Los otros dos distractores de Q8: devolver vacío como éxito (esconde el error) y terminar todo el flujo (pierde el trabajo hecho). Reintentar con backoff dentro del subagente **está bien**; lo que estaba mal en Q8 era el estado genérico del final.

**Cómo se ve en la práctica.**
```json
{
  "failure_type": "timeout",
  "attempted_query": "precios de heladeras no frost 2026",
  "partial_results": [{"source": "comparador-A", "price_range": "$780.000–$950.000"}],
  "alternatives": ["usar el informe de la Cámara de Comercio", "acotar a 3 marcas"]
}
```
El subagente **recupera localmente** lo transitorio y **propaga** solo lo que no puede resolver. Y si el sistema sigue sin una fuente, la síntesis lo dice con **coverage annotations** (entrada 3).

> 🧠 **Para recordar:** error útil = **tipo + intento + parciales + alternativas**.

---

# Más confusiones frecuentes (entradas 33 a 39)

Estas entradas cubren confusiones que aparecen seguido en las preguntas de práctica y que no encajaban en ninguna de las 32 anteriores. La mayoría son de los dominios 1 y 2, y varias dependen de detalles concretos de la API, de MCP o de Claude Code.

## 33. Describir el comportamiento o restringir la tool: arreglar una tool que hace de más ⭐

*Dominio 2 · tarea 2.1*

**La idea central.** Claude elige una tool por su nombre, su descripción y su `input_schema`, y produce una llamada **estructurada** que tu código ejecuta. Lo que construís **en la interfaz** de la tool se cumple siempre. Lo que solo **describís en texto** (en la descripción o en el prompt) es una sugerencia. Es la misma diferencia que entre guidance y enforcement (entrada 2), aplicada al diseño de la tool.

**Caso 1: una tool con un parámetro de texto libre.** Todas las operaciones de cuenta pasan por una sola tool, `manage_account`, con un único parámetro `instruction` de texto libre que el servidor interpreta. Resultado: se aplica un crédito cuando el cliente quería cambiar la dirección.

El problema está en la **interfaz**. El **input schema es el contrato** de una tool, y acá el contrato real es lenguaje natural, que ni la API ni el backend pueden validar. El arreglo es **dividirla en tools específicas** (`apply_credit`, `update_address`, `change_plan`), cada una con su `input_schema` tipado: la decisión de **qué operación** hacer pasa a la **selección de la tool**, y los parámetros los valida la API antes de que se ejecute nada. 📘 La documentación también acepta agrupar acciones relacionadas en una tool con un parámetro **restringido** (un `enum` llamado `action`). Lo que está mal no es tener una sola tool: es el **texto libre sin restricción**.

**Caso 2: una tool con una capacidad demasiado amplia.** Para responder con documentos de política oficiales, el agente tiene una tool genérica `fetch_url`, y la usa también para traer páginas de buscadores y sitios externos. El arreglo es una **constrained alternative** (alternativa restringida): reemplazarla por `get_policy_document`, que acepta **solo identificadores válidos**. Con esa tool, traer una página de un buscador es **imposible**, no solo desaconsejado. Es el **principle of least privilege** (principio de menor privilegio) aplicado a la interfaz.

| Mecanismo | Tipo | Por qué |
|---|---|---|
| Regla en el system prompt, descripción más larga | **Probabilistic** (probabilístico) | Influye en lo que hace el modelo; no garantiza nada sobre cómo usa una tool amplia |
| **Denylist** (lista de lo prohibido) | **Reactive** (reactivo) | Bloquea solo lo que ya viste; lo inesperado pasa |
| Validar contra lo permitido (**allowlist**, IDs válidos, un `enum`) | **Deterministic** (determinista) | La capacidad no existe fuera de su alcance |

**Los distractores típicos:** ampliar la descripción con ejemplos (ayuda a **elegir** entre tools, pero acá el problema es lo que la tool permite), una regla en el prompt (probabilística) y reintentar con otra redacción (en una cuenta, el crédito equivocado **ya se aplicó**).

**La señal del enunciado.** *"A single tool that takes one free-text parameter"* → tools específicas con schema. *"A generic tool… the agent also fetches…"*, *"most reliably prevents this misuse"* → una tool restringida. *"Most reliably"* y *"prevents"* apuntan a lo determinista.

> 🧠 **Para recordar:** si la tool **puede** hacer algo de más, **achicá la tool**; no le pidas que se contenga.

---

## 34. Varias tools en un turno: cómo se devuelven los resultados ⭐

*Dominio 1 · tareas 1.1 y 1.3*

**La idea central.** El **parallel tool use** (uso de tools en paralelo) no es un modo que se activa: es que **una sola respuesta** de Claude traiga **varios bloques `tool_use`**, con `stop_reason: "tool_use"`. Está activo por defecto. Claude propone el grupo de llamadas y **tu código** decide cómo ejecutarlas.

**Las reglas para devolver los resultados.** Son estrictas, y la API las hace cumplir con un error 400 si no se respetan:
1. Los resultados van en un mensaje del **usuario** (`role: "user"`). No existe un rol especial para tools, y tampoco van en un mensaje del asistente.
2. Ese mensaje va **inmediatamente después** de la respuesta que pidió las tools.
3. Lleva **un `tool_result` por cada `tool_use`**, unido por el **`tool_use_id`**, **todos juntos en ese único mensaje**.
4. **Dentro del mensaje, los `tool_result` van primero**; cualquier texto, después.
5. Si una tool **falló** (por ejemplo, un timeout), **igual** va su `tool_result`, con **`is_error: true`** y una explicación corta. Así Claude decide: reintentar, seguir con lo que tiene o escalar.

```json
{
  "role": "user",
  "content": [
    {"type": "tool_result", "tool_use_id": "toolu_01",
     "content": "{\"customer_id\": \"C-4821\", \"name\": \"Ana Pérez\"}"},
    {"type": "tool_result", "tool_use_id": "toolu_02", "is_error": true,
     "content": "Timeout después de 30 s consultando el sistema de pedidos"}
  ]
}
```

**Lo que rompe las reglas:** devolver solo el resultado exitoso (queda un `tool_use` sin respuesta), reemplazar el fallido por una frase de texto, repartir los resultados en varios mensajes, o poner un texto **antes** de los `tool_result`. Y `is_error: true` significa "la tool falló": **no** relaja ninguna regla de formato. Un error 400 de formato es determinista, así que reintentar no sirve.

**Con subagentes es igual.** Para que dos corran en paralelo, el coordinador pide **las dos llamadas a `Task` en la misma respuesta**, y tu código devuelve **los dos resultados juntos** en el siguiente mensaje. Devolver cada resultado en su propio mensaje es el formato incorrecto según la documentación, y además le enseña al modelo a no agrupar. **`disable_parallel_tool_use: true`** hace lo **contrario**: con `auto`, limita a una tool por respuesta.

> 🧠 **Para recordar:** varias tools en un turno → **un mensaje del usuario, un `tool_result` por llamada, primero los resultados, los fallidos con `is_error`**.

---

## 35. El system prompt también elige tools ⭐

*Dominio 2 · tarea 2.1*

**La idea central.** Cuando un pedido incluye tools, la API arma **un único system prompt** que combina las definiciones de las tools, **tu system prompt** y la configuración de tools. Tus instrucciones y las descripciones terminan en el mismo contexto, y **juntas** deciden qué tool se usa. Si las tools están bien descritas y Claude igual elige mal, el siguiente lugar donde mirar es el system prompt.

**Tres patrones que desvían la elección:**
1. **Una palabra del prompt coincide con el nombre de una tool.** *"Always search for relevant context"* arrastra al agente hacia `search_wiki`, aunque lo correcto sea Grep. El arreglo es **reescribir la instrucción describiendo el objetivo**, sin esa palabra.
2. **Una instrucción general que obliga a usar tools.** *"Always call a tool first before responding"* hace que llame tools hasta en preguntas de charla (**over-triggering**). Si una llamada tiene que estar **garantizada**, el mecanismo es `tool_choice`; si no, la redacción tiene que ser **proporcionada**.
3. **Dos instrucciones que se contradicen.** Dos secciones nombran tools **distintas** como obligatorias para lo mismo, y el ruteo parece aleatorio. Igual que con dos CLAUDE.md que se contradicen (entrada 12): hay que **eliminar la contradicción**.

**Lo que no es la causa:** ampliar las descripciones (ya eran buenas), la falta de few-shot (ayuda secundaria), que el system prompt vaya después de las definiciones de las tools (es el orden normal), forzar una tool con `tool_choice` en cada pedido (bloquea usos válidos) o un clasificador de ruteo aparte (sobreingeniería).

**La señal del enunciado.** *"After the team added the line…"*, *"reviewing the system prompt, you find…"*, *"despite detailed, distinct tool descriptions"* → el problema está en el prompt, y casi siempre el enunciado **cita** la frase culpable.

> 🧠 **Para recordar:** descripciones **buenas** + ruteo **malo** = revisá el **system prompt**: palabras que coinciden con una tool, "always", contradicciones.

---

## 36. El schema de un handoff: completo y sin datos del caso adentro ⭐

*Dominios 1 y 5 · tareas 1.4 y 5.2*

**La idea central.** El **handoff** (traspaso) a una persona que no ve la conversación tiene que ser un documento **completo por sí solo** (entrada 29). Su diseño tiene dos preocupaciones: que esté **completo** y que los datos estén **seguros**.

**Completitud: un schema con campos obligatorios.** Cada handoff se valida contra un JSON schema que exige **customer ID, root cause, refund amount y recommended action**. Con **structured outputs**, un handoff sin el monto **no puede** llegar a la cola sin que nadie lo note. Diferencia con la entrada 21: ahí `required` era un problema porque el dato **podía no estar** en el documento; acá los campos **siempre existen** en un escalamiento, así que marcarlos como obligatorios es correcto.

**Seguridad de los datos.** 📘 Según la documentación de structured outputs, prompts y respuestas se procesan con **zero data retention**, pero **el JSON schema puede quedar en caché hasta 24 horas**. Por eso los datos sensibles de un caso (IDs, montos) van **en los valores de la salida**, nunca dentro del schema: ni en **nombres de propiedades**, ni en **`enum`** o **`const`**, ni en **patrones regex**.

**Los distractores típicos:** adjuntar el transcript completo (le pasa volumen en lugar del estado del caso) y filtrar los handoffs por confianza autoinformada (no es confiable y puede bloquear justo los casos que más necesitan a una persona).

> 🧠 **Para recordar:** handoff = **schema con los campos obligatorios**; los **datos del caso en los valores**, nunca en el schema.

---

## 37. MCP: tools o resources, servidor existente o propio ⭐

*Dominio 2 · tarea 2.4*

**Tools o resources.** Un servidor MCP puede ofrecer dos cosas distintas:
- **Tools**: **acciones** que el modelo ejecuta y que pueden cambiar algo (hacer un reembolso, crear un ticket).
- **Resources**: **datos para leer** (documentos, schemas, listas de códigos). Funcionan como un catálogo: el servidor publica la lista (`resources/list`, cada una con URI, nombre y descripción) y el contenido se lee con `resources/read`.

Si el agente gasta llamadas a tools solo para **descubrir** qué políticas, códigos de estado o campos existen, lo que falta es un **catálogo de resources**: así arranca sabiendo qué hay disponible. Una tool `get_reference_data` que hay que llamar al principio sigue siendo una llamada (y reconstruye a mano lo que las resources ya hacen). Y al revés, una acción que cambia algo (`process_refund`) nunca se modela como resource.

**Servidor existente o propio.**
- **Integraciones estándar** (Jira, GitHub, Slack): se usa un **servidor MCP existente** del directorio de conectores. Ya resuelve la API, la autenticación y las descripciones, y lo mantiene otro.
- **Lógica propia del negocio** (las reglas de reembolso de la empresa): **servidor MCP propio**, con tools específicas que hagan cumplir esas reglas.
- Reemplazar las tools propias por un servidor genérico que hace consultas directas a la base de datos **saltea las reglas** del negocio: es lo contrario de la entrada 33.

> 🧠 **Para recordar:** **tools = acciones**, **resources = datos para leer**; **lo estándar, ya hecho**; **lo propio, a medida**.

---

## 38. Hook o prompt cuando la regla tiene excepciones que requieren juicio

*Dominio 1 · tareas 1.4 y 1.5*

**La idea central.** La entrada 2 dice que lo que **siempre** tiene que cumplirse va en código. Pero hay reglas con un **"normalmente… salvo que…"** que depende de **entender la conversación**: "normalmente ofrecé un reemplazo antes del reembolso, **salvo que el cliente insista** en el reembolso". Para saber si el cliente insistió hay que interpretar lo que dijo, y eso es juicio del modelo.

- **Regla fija, sin interpretación** (un monto máximo, un permiso, un orden obligatorio): **hook** o prerrequisito en código.
- **Regla con una excepción que depende de la intención del cliente**: **system prompt**, con la regla y su excepción explicadas.

Un hook `PreToolUse` que bloquee **todos** los reembolsos hasta que se ofrezca un reemplazo rompe la propia política: el cliente que insiste tampoco puede recibir su reembolso. El problema no es el hook en sí (un hook puede tener lógica condicional), sino usar un mecanismo determinista para una decisión que necesita juicio. Los otros distractores: un hook `PostToolUse` (corre **después** de que el reembolso ya se hizo) y escalar todos los reembolsos a una persona (destruye la resolución en el primer contacto).

> 🧠 **Para recordar:** regla **fija** = hook; regla con **excepción que requiere juicio** = prompt.

---

## 39. Interview pattern, plan mode o seguir en la misma sesión

*Dominio 3 · tareas 3.4 y 3.5*

**La idea central.** El **interview pattern** (que Claude te entreviste) tiene **dos mitades**:
1. **La entrevista**: Claude pregunta por la implementación, los casos límite, las preocupaciones y los compromisos, sobre todo en las partes difíciles.
2. **El documento**: Claude escribe una **especificación completa** en un archivo (`SPEC.md`), y la implementación se hace en una **sesión nueva**, con el contexto limpio y enfocado en la especificación.

Una buena especificación se entiende sola: nombra los archivos y las interfaces, dice qué queda afuera y termina con una forma de verificar el resultado.

**Lo que se confunde.**
- **Plan mode** controla **permisos** (Claude investiga y propone sin editar archivos hasta que aprobás; entrada 15). La entrevista sirve para **descubrir requisitos**. Repetir la entrevista en plan mode es hacer el trabajo dos veces.
- **Seguir en la misma sesión** deja la conversación larga, con idas y vueltas, como fuente de verdad.
- **`/compact`** resume y puede perder detalles exactos (entrada 27); no es el paso documentado de este patrón.

> 🧠 **Para recordar:** después de la entrevista, **`SPEC.md` + sesión nueva**.

---

# La noche anterior: las 39 parejas en una línea

| # | Si dudás entre… | La regla |
|---|---|---|
| 1 | `stop_reason` o turn budget | Termina `end_turn`; `max_turns` es el freno de emergencia |
| 2 | Prompt o enforcement | "Always", plata, compliance = código (hook `PreToolUse`, exit 2); juicio = prompt |
| 3 | Narrow decomposition o coverage annotations | Tema nunca asignado = coordinador; fuente caída = anotar |
| 4 | Context passing | Ni nada ni todo: lo justo, estructurado; paralelo = varias `Task` en una respuesta |
| 5 | `--resume` o fresh session | Contexto válido = resume; stale = nuevo + resumen |
| 6 | Description, few-shot o split | Descripción mínima = mejorarla primero (Q2) |
| 7 | Access failure o valid empty result | "No encontré" ≠ "no pude buscar"; `is_error`/`isError` |
| 8 | `auto`, `any` o forced | Any = alguna; forced = esa y primero, después auto |
| 9 | MCP scopes | Equipo en `.mcp.json`; personal en `~/.claude.json`; secretos en `${VAR}` |
| 10 | Grep o Glob | Grep = adentro; Glob = el nombre (`**/*.test.tsx`) |
| 11 | CLAUDE.md, rules, skill, command, subagent | Siempre / ciertos archivos (`paths:`) / a pedido / delegar |
| 12 | CLAUDE.md hierarchy | Se suman; lo del equipo en el repo; `@` organiza, no ahorra |
| 13 | Versión personal | Tu carpeta + otro nombre |
| 14 | `allowed-tools`, `deny` o hook | El arreglo tiene el alcance del problema |
| 15 | Plan mode o direct | Grande o incierto = plan (Q5) |
| 16 | Un mensaje o varios | Interactúan = juntos; independientes = de a uno |
| 17 | CI | `-p`; forma garantizada = `--json-schema` → `structured_output` |
| 18 | Criteria, few-shot o schema | Qué / borde y consistencia / forma |
| 19 | Confidence filtering o categorías | Qué reportar y qué no; sacar la frase de cautela; desactivar solo la categoría ruidosa |
| 20 | Self-reported confidence | Cruda nunca; calibrada y por campo solo para enrutar |
| 21 | null, other, unclear | Ausente / no listado / ambiguo |
| 22 | Syntax o semantic | Schema (`strict`) = forma; valores en código |
| 23 | Retry | Documento + respuesta + error; no si falta el dato; no permisos |
| 24 | Batch o sync | Alguien espera = sync; intervalo + 24 h ≤ SLA; reenviar por `custom_id`, corregido |
| 25 | Quién revisa | Otra instancia, sin el contexto del generador |
| 26 | PR grande | Por archivo + integración (Q12) |
| 27 | Case facts, scratchpad, compact | Cliente = case facts; código = scratchpad; resumen pierde |
| 28 | compact, clear, nueva | Misma tarea / otra tarea / contexto viejo |
| 29 | Escalation | Pide persona = ya; enojado = ofrecer; policy gap = escalar; prohíbe = rechazar; multiple matches = preguntar |
| 30 | Conflicting sources | Los dos, con fuente y fecha; decide el coordinador |
| 31 | Accuracy y sampling | Medir por segmento antes; muestrear lo de alta confianza después |
| 32 | Error entre agentes | Tipo + intento + parciales + alternativas (Q8) |
| 33 | Describir o restringir la tool | Si la tool puede hacer de más, achicala: tools con schema, o una que acepte solo lo válido |
| 34 | Varias tools en un turno | Un mensaje del usuario, un `tool_result` por llamada, primero los resultados, los fallidos con `is_error` |
| 35 | Ruteo malo con descripciones buenas | Revisá el system prompt: palabra que coincide, "always", contradicciones |
| 36 | Schema de un handoff | Campos obligatorios; los datos del caso en los valores, nunca en el schema |
| 37 | Tools o resources; servidor existente o propio | Acciones = tools, datos para leer = resources; lo estándar ya hecho, lo propio a medida |
| 38 | Hook o prompt con excepción | Regla fija = hook; excepción que requiere juicio = prompt |
| 39 | Después de una entrevista | `SPEC.md` + sesión nueva; plan mode es otra cosa |

