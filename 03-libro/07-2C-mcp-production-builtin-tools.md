# Capítulo 7 · 2C · Udemy 8 — MCP Production & Built-in Tools (MCP en producción y tools incorporadas)

*Tareas oficiales 2.4 (se completa acá) y 2.5 · Último capítulo del módulo 2*

---

## Dónde estamos

Último capítulo del **módulo 2: Tool Design & MCP Integration** (18% del examen). Cubre:
- **2.5** Select and apply built-in tools (Read, Write, Edit, Bash, Grep, Glob) effectively (elegir y usar bien las tools incorporadas). Pesa 3,6%.
- **2.4** Integrate MCP servers into Claude Code and agent workflows: acá se completa con transportes, seguridad y muchas tools.

### Cómo leer este capítulo

Todo lo que leés acá **vale para el examen**, salvo que diga lo contrario. Cuando algo sale solo del curso (útil para entender, pero no central), lo marco con **📘 Curso**. Cuando Jacob dice algo distinto de lo que evalúa la guía, aparece un recuadro así:

> ⚠️ **En el curso vas a escuchar otra cosa.** … **Para el examen: …**

### Un aviso sobre este capítulo

El curso llama "built-in tools" a **otra cosa**. Las lecciones 50 y 51 hablan de las tools que ofrece la **API de Claude**: `web_search`, `code_execution`, `computer`, `text_editor`, `bash`. La tarea oficial **2.5**, en cambio, habla de las tools de **Claude Code y del Agent SDK**: **Read, Write, Edit, Bash, Grep y Glob**. Son dos conjuntos distintos con el mismo nombre, y el curso **no cubre ninguno de los 9 puntos oficiales de 2.5**.

Por eso este capítulo arranca por la **Parte 1 (las built-in tools de Claude Code)**, que sale entera de la guía y la documentación y es la más importante. Las lecciones del curso quedan en la Parte 3, con sus errores corregidos.

## De dónde venimos

En **2A** viste que Claude elige una tool **leyendo su descripción**, y que tener demasiadas tools juntas empeora esa elección. En **2B** viste cómo se configura un servidor MCP (`.mcp.json`, `~/.claude.json`, `${VAR}`) y un caso típico: **"el agente usa Grep en vez de la tool MCP"**, que se arregla mejorando la descripción de la tool MCP.

Ahora vas a ver el otro lado: **qué es Grep** y las demás tools que Claude Code ya trae, cuándo usar cada una y cómo explorar un código que no conocés. Después, lo que faltaba de MCP para usarlo en serio.

## Mapa del capítulo

**Parte 1 — Las built-in tools de Claude Code (tarea 2.5, el núcleo oficial).**
1. Las seis built-in tools: Read, Write, Edit, Bash, Grep y Glob.
2. Grep vs. Glob: buscar **dentro** de archivos o buscar archivos **por nombre**.
3. Read, Write y Edit: archivo entero o cambio puntual.
4. Cuando Edit falla: el fallback Read + Write.
5. Explorar un **codebase (base de código)** de a poco: primero Grep, después Read siguiendo imports.
6. Rastrear una función a través de wrappers.
7. Bash y los permisos de las tools en el Agent SDK.

**Parte 2 — MCP en producción (se completa la tarea 2.4).**

8. Transports (transportes): stdio vs. Streamable HTTP (HTTP con streaming).
9. Seguridad de los servidores MCP en Claude Code.
10. Muchas tools MCP: tool search y límites de salida.
11. Built-in o MCP: quién gana y por qué.

**Parte 3 — Lo que agrega el curso (fuera del foco de la guía).**

12. Sampling, notificaciones y roots.
13. Servidores MCP en producción: least privilege, autenticación y versionado.
14. Las "built-in tools" de la API: server tools vs. client tools.

---

# Parte 1 — Las built-in tools de Claude Code

## Tema 1 — Las seis built-in tools (tools incorporadas): Read, Write, Edit, Bash, Grep y Glob

### Qué es

Las **built-in tools** son las tools que **ya vienen** con Claude Code y con el Agent SDK. A diferencia de las tools que diseñaste en 2A, acá no tenés que programar nada ni escribir una descripción: Claude ya sabe para qué sirve cada una y cómo usarla. Tu trabajo, y lo que evalúa el examen, es **elegir la correcta** para cada situación.

La guía evalúa seis. Cada una tiene un trabajo distinto, y algunas piden permiso antes de usarse (Claude Code te pregunta "¿lo permito?") y otras no:

| Tool | Qué hace | Pide permiso |
|---|---|---|
| **Read** | **Lee** un archivo completo (con números de línea) | No |
| **Write** | **Crea** un archivo nuevo o **sobrescribe** uno entero | Sí |
| **Edit** | Hace un **cambio puntual**: reemplaza un texto exacto por otro | Sí |
| **Bash** | **Ejecuta comandos** de terminal (tests, git, build) | Sí |
| **Grep** | **Busca texto dentro** de los archivos (con patrones) | No |
| **Glob** | **Busca archivos por nombre o ruta** con patrones (`**/*.ts`) | No |

La lógica de los permisos es simple: lo que **solo lee** no puede romper nada, así que no pregunta; lo que **modifica** sí puede, así que pregunta. Por la misma razón, el Agent SDK puede correr Read, Grep y Glob **en paralelo** (varias a la vez), mientras que Edit, Write y Bash corren **de a una**, para que dos cambios no se pisen.

Hay dos matices en la tabla. Read, Grep y Glob **sí** piden permiso cuando la ruta está fuera del directorio de trabajo (la carpeta del proyecto). Y Bash corre sin preguntar un grupo de comandos de solo lectura, como `ls` o `cat`.

### Ejemplo

El agente de productividad de TiendaX recibe el pedido "Arreglá el bug del cálculo de envío". Este agente es el **Scenario 4** de la guía, *"Developer Productivity with Claude"*: un agente armado con el Agent SDK, built-in tools y servidores MCP. Lo que hace, paso a paso:
1. Usa **Grep** con `calcularEnvio` para saber en qué archivos aparece la función.
2. Usa **Read** sobre `src/envios/calculo.ts` para entender el código.
3. Usa **Edit** para corregir la línea del bug.
4. Usa **Bash** para correr `npm test` y confirmar que los tests pasan.

> ⚠️ **En la documentación actual vas a leer otra cosa.** Hoy Claude Code en macOS, Linux y WSL **no incluye Grep ni Glob por defecto**: Claude busca con los comandos `grep` y `find` a través de Bash. En el Agent SDK, Grep y Glob aparecen si los nombrás en `allowedTools` o en `tools` (los ves en el Tema 7).
>
> **Para el examen:** la guía (y el Scenario 4) da por hecho que **Grep y Glob existen**. Respondé siempre con la regla: **Grep = contenido, Glob = nombres**.

### Para el examen

- Cada tool tiene un trabajo. Las preguntas de 2.5 son de **elegir la tool correcta** para una situación.
- **Ojo:** no confundas estas tools con las de la API que enseña el curso (`web_search`, `code_execution`…). Si la pregunta habla de explorar o modificar código con Claude Code o el Agent SDK, son **estas seis**.

### Cómo se une

La confusión más común es entre las dos que buscan: Grep y Glob.

---

## Tema 2 — Grep vs. Glob: buscar dentro de archivos o buscar archivos por nombre

### Qué es

Las dos tools "buscan", y por eso se confunden. La diferencia está en **qué miran**. Grep abre los archivos y mira **lo que tienen escrito adentro**. Glob no abre nada: mira solo **el nombre y la ruta** de cada archivo. Si lo que buscás es un texto del código, necesitás Grep; si lo que buscás es un tipo de archivo, necesitás Glob.

La guía las define así:

- **Grep = content search (búsqueda de contenido).** Busca **dentro** de los archivos las líneas que coinciden con un patrón: nombres de funciones, mensajes de error, `import`. Los ejemplos de la guía son *encontrar todos los que llaman a una función* (sus **callers**) y *ubicar un mensaje de error*.
- **Glob = file path pattern matching (búsqueda por patrón de ruta).** Busca archivos por **nombre o extensión**, sin mirar qué tienen adentro. El ejemplo de la guía es **`**/*.test.tsx`**: todos los archivos de test de React, en cualquier carpeta (`**` significa "cualquier carpeta, a cualquier profundidad").

La documentación lo resume en una frase: *"Where Glob finds files by name, Grep finds lines inside them"* (Glob encuentra archivos por nombre; Grep encuentra líneas dentro de ellos).

### Cómo se usa

**Grep** usa la sintaxis de **ripgrep** (una herramienta de búsqueda de texto) con **regex (expresiones regulares**, patrones de texto como `procesarReembolso\(`). Por defecto devuelve **solo las rutas** de los archivos que coinciden (modo `files_with_matches`), lo que ahorra contexto cuando solo querés saber *dónde* está algo. Con `output_mode: "content"` devuelve las líneas con su número. Podés filtrar por tipo de archivo (`type: "py"`) o por patrón (`glob: "**/*.tsx"`). Grep saltea los archivos listados en `.gitignore`; Glob, en cambio, no los saltea por defecto.

**Glob** acepta patrones como `**/*.js`, `src/**/*.ts` o `*.{json,yaml}`. Devuelve hasta 100 archivos, ordenados por fecha de modificación.

### Ejemplo

| Necesidad en TiendaX | Tool | Por qué |
|---|---|---|
| "¿Quién llama a `procesarReembolso()`?" | **Grep** `procesarReembolso\(` | Es texto **dentro** de los archivos |
| "¿Dónde aparece el error 'Stock insuficiente'?" | **Grep** `Stock insuficiente` | Es un mensaje **dentro** del código |
| "Listá todos los tests de componentes" | **Glob** `**/*.test.tsx` | Es un patrón de **nombre** |
| "¿Qué archivos de configuración hay?" | **Glob** `**/*.config.{js,ts}` | Es un patrón de **nombre** |

**Mal:** usar Glob `**/*procesarReembolso*` para encontrar quién llama a la función. Ese patrón solo encuentra archivos que **se llaman** así, no los que **usan** la función.

### Para el examen

- Palabras que piden **Grep**: callers (quién llama), usos, mensaje de error, imports, "dónde se usa", "qué archivos contienen".
- Palabras que piden **Glob**: "archivos que se llamen", extensión, "todos los `.test.tsx`", estructura de carpetas.
- **Trampa de la guía (Q6):** los patrones `paths: ["**/*.test.tsx"]` de `.claude/rules/` usan la **misma sintaxis glob**, pero **no son la tool Glob**. Son reglas que se cargan según la ruta (lo vas a ver en 3B).

### Cómo se une

Ya encontraste el archivo. Ahora hay que leerlo y cambiarlo, y para eso hay tres tools.

---

## Tema 3 — Read, Write y Edit: archivo entero o cambio puntual

### Qué es

Para trabajar sobre un archivo hay dos formas: tratarlo **entero** o tocar **solo una parte**. Read y Write trabajan con el archivo entero; Edit cambia solo un pedazo. La guía lo dice así: **Read/Write para operaciones sobre el archivo completo; Edit para cambios puntuales usando un texto único como ancla**.

- **Read** trae el archivo entero (o por partes, si es muy grande).
- **Write** escribe el archivo **entero**: crea uno nuevo o **reemplaza todo** el contenido de uno existente. No agrega al final ni combina con lo que había; la documentación lo dice así: *"It doesn't append or merge"*.
- **Edit** hace un **reemplazo exacto**: recibe un `old_string` (el texto que hay hoy) y un `new_string` (el texto nuevo). No usa regex ni búsqueda aproximada.

Elegir mal tiene costo. Si usás Write para cambiar una línea, tenés que reescribir todo el archivo, y cualquier detalle que se altere en el camino rompe algo que no querías tocar.

### Las reglas de Edit

Edit es preciso, pero por eso es exigente. Tiene tres reglas:
1. **Coincidencia exacta.** `old_string` tiene que estar en el archivo **tal cual**. Un espacio o una sangría distinta alcanzan para que falle, porque Edit no "se acerca": busca el texto idéntico.
2. **Unicidad.** `old_string` tiene que aparecer **exactamente una vez**. Ese texto es el **anchor (ancla)**: lo que le dice a Edit *dónde* hacer el cambio. Si aparece dos veces, Edit no sabe cuál tocar.
3. **Leer antes.** Claude lee el archivo en la conversación **antes** de editarlo, para que el `old_string` salga del contenido real y no de lo que Claude cree que hay. En modelos nuevos hay excepciones, pero la regla segura es: Read antes de Edit o Write sobre un archivo existente.

### Ejemplo: cuál usar

- Cambiar `const IVA = 0.19` por `const IVA = 0.21` en `config.ts`: **Edit**, porque es un cambio puntual y el texto es único.
- Crear `src/envios/README.md`: **Write**, porque es un archivo nuevo.
- Regenerar entero `fixtures/productos.json` con datos nuevos: **Write**, porque es una reescritura total.
- **Mal:** usar Write para cambiar una línea de un archivo de 800 líneas. Hay que reescribir las 800 (con el riesgo de perder o alterar algo) cuando Edit cambia solo esa. La documentación lo dice directo: *"For partial changes to an existing file, Claude uses Edit instead of Write."*

### Para el examen

- Cambio chico en un archivo existente → **Edit**.
- Archivo nuevo o reescritura completa → **Write**.
- Antes de modificar un archivo existente → **Read**.

### Cómo se une

¿Qué pasa si el texto que querés cambiar aparece varias veces? Edit no sabe cuál tocar.

---

## Tema 4 — Cuando Edit falla: el fallback (plan B) Read + Write

### Qué es

Como Edit exige un ancla única, a veces falla: el texto que querés cambiar aparece en dos o tres lugares del archivo. Para ese caso la guía tiene una regla concreta: **cuando Edit falla porque el texto no es único, se usa Read + Write como fallback (plan B) confiable**. Es decir, leer el archivo completo con Read, armar el contenido ya corregido y escribirlo entero con Write.

Funciona porque Write no necesita ningún ancla: reemplaza el archivo completo. Así desaparece el problema de "¿cuál de las tres ocurrencias cambio?", porque vos decidís el contenido final de todo el archivo.

> ⚠️ **En la documentación actual vas a leer otra cosa.** La documentación de Claude Code muestra dos caminos que se prueban **antes** de llegar a Read + Write:
> - **Alargar el `old_string`** con líneas de alrededor, hasta que ese texto más largo aparezca una sola vez.
> - Usar **`replace_all: true`**, pero **solo si querés cambiar todas** las ocurrencias.
>
> **Para el examen:**
> 1. Si una opción es **"leer el archivo completo con Read y escribirlo con Write"**, es la respuesta de la guía.
> 2. Si esa opción no está y aparece **"incluir más contexto en el texto a reemplazar"**, elegí esa.
> 3. **`replace_all`** solo si la consigna dice que hay que cambiar **todas**.

### Ejemplo

En `pedidos.ts` esta línea aparece tres veces:
```ts
if (estado === "pendiente") {
```
Hay que cambiar solo la del método `cancelar()`. Claude intenta Edit con ese `old_string` y falla, porque el texto no es único. Veamos las opciones:

- ❌ Reintentar el mismo Edit: va a fallar igual, porque el archivo no cambió.
- ❌ `replace_all: true`: cambia las tres, y solo había que cambiar una.
- ❌ Write solo con el método `cancelar()`: Write **reemplaza el archivo entero**, así que borrarías todo lo demás.
- ✅ **Read** de `pedidos.ts` completo, armar el archivo con el cambio en `cancelar()` y hacer **Write** del archivo completo.

### Para el examen

- "Edit falla por coincidencia no única" → **Read + Write**.
- Read + Write es el **fallback**, no la forma normal de editar. Para cambios puntuales, primero Edit.
- Si Edit falla por **un espacio o una sangría**, el problema no es la unicidad: hay que copiar el texto exacto de un Read reciente y reintentar Edit.

### Cómo se une

Hasta acá sabías qué archivo tocar. Pero en un código que no conocés, ¿por dónde empezás?

---

## Tema 5 — Incremental codebase exploration (explorar la base de código de a poco): primero Grep, después Read siguiendo imports

### Qué es

Cuando te toca un código que no conocés, la tentación es leerlo todo "para tener el panorama". Es un error: cada archivo leído ocupa **contexto** (el espacio de trabajo limitado de Claude en la conversación). Si leés 200 archivos "por las dudas", llenás el contexto de cosas que no importan y Claude pierde de vista lo importante; lo viste en 1B como **attention dilution** (dilución de la atención).

Por eso la guía pide **construir el entendimiento del codebase de forma incremental**, en tres pasos:
1. Empezar con **Grep** para encontrar los **entry points (puntos de entrada)**: los lugares donde arranca el flujo que te interesa, por ejemplo el endpoint que recibe un pedido de reembolso.
2. Hacer **Read** de esos archivos y **seguir los imports**: cada archivo te dice de dónde trae sus funciones, y ese es el próximo archivo a leer.
3. **No leer todos los archivos de entrada.**

### Ejemplo

Pedido: "Explicame cómo se calcula el reembolso en TiendaX".

**Mal:** hacer Glob de `src/**/*.ts` y leer los 180 archivos uno por uno.

**Bien:**
1. Claude hace **Grep** de `reembolso` (solo rutas). Aparecen `api/reembolsos.ts`, `servicios/reembolso.ts` y `tests/reembolso.test.ts`.
2. Hace **Read** de `api/reembolsos.ts` y ve que llama a `calcularReembolso`, importado de `servicios/reembolso.ts`.
3. Hace **Read** de `servicios/reembolso.ts` y ve que importa `politicas/plazos.ts`.
4. Hace **Read** de `politicas/plazos.ts`: ahí está la regla de los 30 días.

Leyó cuatro archivos en vez de 180, y siguiendo el camino real del código.

### Relación con otros temas

Si la exploración igual va a generar muchísima salida, la guía (tareas 3.4 y 5.4, que vas a ver más adelante) recomienda delegarla en un **Explore subagent (subagente de exploración)**. Ese subagente explora en su propio contexto y le devuelve un **resumen** al agente principal, que así no se llena con todo lo leído. Es la misma idea de aislamiento de contexto de 1C.

### Para el examen

- Codebase desconocido → **Grep para los entry points, después Read siguiendo imports**.
- ❌ "Leer todos los archivos primero para tener el panorama completo" → siempre mal.
- ❌ "Glob de todo y Read de cada archivo" → igual de mal.

### Cómo se une

A veces seguir el flujo se complica: la función que buscás no se llama con su nombre original.

---

## Tema 6 — Wrapper modules (módulos envoltorio): rastrear una función que se re-exporta

### Qué es

Un **wrapper module (módulo envoltorio)** es un archivo que **importa funciones y las vuelve a exportar**, a veces con **otro nombre** (un alias). Es muy común: por ejemplo, un `index.ts` que junta todo lo de una carpeta para que el resto del código lo importe desde un solo lugar.

El problema aparece cuando buscás quién usa una función. Si hacés Grep solo del nombre original, **no encontrás** a los que la llaman con el nombre nuevo, porque en esas líneas el nombre original no está escrito. La búsqueda "funciona", pero devuelve una lista incompleta, y no te das cuenta.

Por eso la guía pide dos pasos: **primero identificar todos los nombres que exporta el wrapper, y después buscar cada nombre en el codebase**.

### Ejemplo

`servicios/pagos/index.ts`:
```ts
export { procesarReembolso as reembolsar } from "./reembolsos";
export { procesarReembolso } from "./reembolsos";
export { procesarReembolso as devolverPago } from "./reembolsos";
```

**Mal:** Grep de `procesarReembolso` encuentra 3 usos. Faltan los que llaman `reembolsar(...)` y `devolverPago(...)`, porque esos textos no contienen el nombre original.

**Bien:**
1. Claude hace **Read** de `servicios/pagos/index.ts` y anota los nombres exportados: `reembolsar`, `procesarReembolso` y `devolverPago`.
2. Hace **Grep** por **cada uno**: `reembolsar\(`, `procesarReembolso\(`, `devolverPago\(`.
3. Ahora tiene **todos** los lugares donde se usa la función.

### Para el examen

- "Faltan usos de la función; hay un módulo que la re-exporta" → **listar los nombres exportados y hacer Grep por cada uno**.
- ❌ "Grep con un regex más amplio del nombre original" → sigue sin encontrar el alias.

### Cómo se une

Queda la sexta tool, Bash, y cómo se controla qué tools tiene un agente.

---

## Tema 7 — Bash y los permisos de las tools en el Agent SDK

### Qué es

**Bash** ejecuta comandos de terminal: correr tests, usar `git`, compilar, instalar paquetes. Es la tool más poderosa, porque un comando puede hacer casi cualquier cosa (incluso borrar archivos), y por eso **pide permiso**. Dos detalles de la documentación:
- Cada comando corre en un **proceso separado**, así que las **variables de entorno no persisten** entre un comando y el siguiente.
- Tiene un timeout (tiempo máximo): 2 minutos por defecto, hasta 10.

**¿Cuándo Bash y cuándo una tool dedicada?** Para **ejecutar** algo (tests, build, git) no hay otra: es Bash. Para **leer, buscar o editar archivos**, si están Read, Grep, Glob y Edit, conviene la tool dedicada: las de lectura no piden permiso, corren en paralelo y se pueden controlar con reglas de permiso por ruta, cosas que un comando de Bash no te da.

(Como viste en el Tema 1, hoy Claude Code en Unix busca con `grep` y `find` por Bash. En preguntas al estilo de la guía, la respuesta sigue siendo Grep y Glob.)

### Cómo se configura en el Agent SDK

En el Agent SDK hay tres opciones que parecen iguales pero **no hacen lo mismo**. La diferencia clave es entre **aprobar** una tool (que se use sin preguntar) y **restringir** las tools (que las demás no existan para el agente):

| Opción | Qué hace | Ejemplo |
|---|---|---|
| **`allowedTools`** | **Auto-aprueba** esas tools (no pide permiso). **No restringe**: las otras siguen existiendo | `["Read", "Grep", "Glob"]` |
| **`disallowedTools`** | **Saca** la tool: Claude ni la ve. Con patrón, solo bloquea esas llamadas | `["Bash"]` o `["Bash(rm *)"]` |
| **`tools`** | Define **qué built-in tools existen** para el agente | `["Read", "Grep", "Glob"]` |

Para un subagente, el campo `tools` de su `AgentDefinition` (lo viste en 1C) lo limita al mínimo que necesita.

### Ejemplo

El subagente "auditor de código" de TiendaX solo tiene que **leer y buscar**.
- **Mal:** `allowedTools: ["Read", "Grep", "Glob"]` "para que solo lea". Write, Edit y Bash **siguen existiendo**: lo único que cambia es que esas tres dejan de pedir permiso.
- **Bien:** `tools: ["Read", "Grep", "Glob"]` en su definición. `disallowedTools: ["Write", "Edit", "Bash"]` también sirve, pero `tools` es más seguro: con una lista negra se te puede escapar alguna tool que no pensaste (por ejemplo `NotebookEdit`).

> ⚠️ **En la documentación actual vas a leer otra cosa.** En 1C y 2B usamos `allowedTools` como "la lista de tools del agente", y la guía también lo trata así (por ejemplo, en 1.3 dice que el `allowedTools` del coordinador *"must include Task"*). La documentación actual es más precisa: `allowedTools` **auto-aprueba**, y las tools no listadas siguen existiendo; si necesitan aprobación, la decisión pasa al permission mode y a `canUseTool`. (La documentación arma un agente "solo lectura" con `allowedTools` más `permissionMode: "dontAsk"`, que rechaza todo lo no listado.)
>
> **Para el examen:**
> 1. Si hay una opción con **`tools`** o **`disallowedTools`** para acotar un agente, elegila.
> 2. Si la única opción para acotar un subagente es "limitar su `allowedTools` a las tools de su rol" (el lenguaje de la guía), esa es la correcta.

### Para el examen

- Restringir qué puede hacer un agente → preferí **`tools`/`disallowedTools`** (con `allowedTools` como respuesta válida cuando es la única forma que ofrece la pregunta).
- Es el **least privilege** de 1C y el **tool scoping** de 2A aplicados a las built-in tools.

### Cómo se une

Con esto cerrás 2.5. Ahora vuelve MCP: lo que faltaba para usarlo en serio.

---

# Parte 2 — MCP en producción

## Tema 8 — Transports (transportes): stdio vs. Streamable HTTP

### Qué es

El **transport (transporte)** es el canal por donde viajan los mensajes entre el cliente MCP (Claude Code, tu agente) y el servidor MCP. Elegirlo depende de **dónde corre el servidor y quiénes lo usan**. Hay dos vigentes.

Con **stdio**, el cliente arranca el servidor como un **proceso hijo** en tu propia máquina y se hablan por la entrada y salida estándar (stdin/stdout), como dos programas conectados por un caño. Es simple y no necesita red, pero solo sirve para **un cliente** en **esa máquina**. Con **Streamable HTTP**, el servidor es un **servicio con una URL**, en otro lado, y los clientes le mandan pedidos HTTP (POST/GET), con respuestas en streaming si hace falta. Así lo pueden usar **muchos clientes** desde cualquier lugar.

| | **stdio** | **Streamable HTTP** |
|---|---|---|
| Dónde corre el servidor | En **tu máquina**, como **proceso hijo** del cliente | En otro lado, como **servicio en una URL** |
| Cómo se comunican | Por la entrada y salida estándar (stdin/stdout) | Por HTTP (POST/GET), con streaming opcional |
| Cuántos clientes | **Uno** | **Muchos** |
| Ideal para | Herramientas locales, scripts, acceso directo al sistema | Servicios compartidos, remotos, en la nube |

La documentación de Claude Code lo dice así: *"HTTP servers are the recommended option for connecting to remote MCP servers"*, mientras que los servidores stdio *"run as local processes on your machine"*.

**SSE (Server-Sent Events, eventos enviados por el servidor)** como transporte separado está **deprecado** (se mantiene por compatibilidad, pero no se usa para cosas nuevas). Hoy SSE es **una parte dentro** de Streamable HTTP, la que sirve para mandar eventos en streaming, no un transporte aparte. 📘 **Curso:** Jacob lo marca como una confusión común.

📘 **Curso:** la regla de Jacob sirve para el examen: **si cruza un límite de red o lo usa más de un usuario, stdio queda descartado y va Streamable HTTP.**

Desplegar u hospedar el servidor (infraestructura, redes, contenedores) está **fuera del alcance** de la guía.

> ⚠️ **En el curso vas a escuchar otra cosa.** El companion dice que *"Claude Code uses STDIO as its native MCP transport"* y que los servidores salen "del archivo de settings". **Para el examen:** Claude Code soporta stdio y **HTTP (recomendado para remotos)**, y los servidores se definen en **`.mcp.json` / `~/.claude.json`** (2B), no en `settings.json`.

### Ejemplo

- `tiendax-pedidos` corre en la laptop de cada dev y lee una base local de prueba: **stdio**, porque es local y lo usa una sola persona.
- El servidor de pedidos de producción lo usan SoporteBot y los 40 agentes humanos de soporte: **Streamable HTTP**, porque es remoto y compartido.
- Alguien configura un servidor nuevo con `--transport sse`: ❌ está deprecado; hay que usar `--transport http`.

### Para el examen

- Local y un usuario → **stdio**. Remoto o compartido → **Streamable HTTP**.
- "SSE" como opción para un servidor nuevo → deprecado.

### Cómo se une

Un servidor compartido o que viene en un repo implica riesgos. ¿Cómo los controla Claude Code?

---

## Tema 9 — MCP server security (seguridad de los servidores MCP) en Claude Code

### Qué es

Un servidor MCP es **código de terceros** que corre con tus permisos y le pasa texto a Claude. Eso abre dos riesgos: que el servidor haga algo que no querés, y que el texto que devuelve manipule a Claude. Por eso Claude Code tiene varias capas de control.

**1. Aprobación de los servidores del proyecto.** El `.mcp.json` viaja con el repo, así que cualquiera que escribe en ese repo puede agregar un servidor. Por eso Claude Code **pregunta antes de usar** esos servidores en sesiones interactivas. Un repo tampoco puede saltearse esa pregunta: la documentación dice *"A cloned repository can't approve its own servers"*, o sea que un repo no confiable no puede auto-aprobarse poniendo `enableAllProjectMcpServers` en su propio `.claude/settings.json`.

Ojo con la automatización. En **`claude -p`** (modo no interactivo) y en el **Agent SDK** no hay una persona a quien preguntar, así que los servidores del `.mcp.json` **se cargan sin preguntar**. Para bloquear uno se usa `disabledMcpjsonServers`, un setting que lista servidores del `.mcp.json` a rechazar (vale desde cualquier archivo de settings). Para usar solo los servidores que vos pasás, se usa `--strict-mcp-config`.

**2. Control de la organización.** La empresa puede decidir qué servidores se usan:
- **`managed-mcp.json`** da control **exclusivo**: solo se pueden usar los servidores que define la empresa, y los usuarios no pueden agregar otros.
- **`allowedMcpServers` / `deniedMcpServers`** son una **allowlist / denylist** (lista de permitidos / de bloqueados). Cada entrada identifica al servidor por **`serverUrl`** (su URL), **`serverCommand`** (el comando exacto que lo arranca) o **`serverName`** (su nombre).

Dos reglas de estas listas. `serverName` **no es un control de seguridad**, porque el nombre lo elige quien escribe el `.mcp.json`: cualquiera puede ponerle a un servidor malicioso el nombre de uno permitido. Y si un servidor está en la de bloqueados, **queda bloqueado aunque esté en la de permitidos** (*"Nothing overrides a denylist match"*).

**3. Confianza y prompt injection.** La **prompt injection (inyección de instrucciones)** es cuando un contenido externo (una página, un ticket) trae texto que intenta darle órdenes a Claude. Un servidor que trae contenido de afuera puede meter ese texto en la conversación. La documentación lo advierte: *"Verify you trust each server before connecting it. Servers that fetch external content can expose you to prompt injection risk."* Además, Anthropic **no audita** los servidores MCP: elegí servidores propios o de proveedores confiables.

**4. Credenciales.** Lo de 2B: `${VAR}` en `.mcp.json`, para no escribir secretos en el archivo. Para servidores remotos, Claude Code soporta **OAuth**: te autenticás desde `/mcp` y los tokens se guardan y renuevan solos. Los detalles de protocolos de autenticación (OAuth, rotación de API keys) están **fuera del alcance** de la guía.

### Ejemplo

- Lucas clona un repo open source que trae un `.mcp.json` con un servidor desconocido. Claude Code le pregunta si lo aprueba, y Lucas lo revisa antes de decir que sí.
- El pipeline de CI de TiendaX corre `claude -p` sobre ese mismo repo. Ahí nadie responde, así que el servidor **se cargaría sin preguntar**. La solución es `--strict-mcp-config` con solo los servidores aprobados, o `disabledMcpjsonServers`.
- El área de seguridad de TiendaX quiere que nadie use servidores fuera de una lista: usa **`managed-mcp.json`**.

### Para el examen

- Repo clonado con `.mcp.json` → **pide aprobación** (interactivo). No asumas que "se conecta solo".
- Automatización (`-p`, SDK) → **no pregunta**: hay que limitar explícitamente.
- Bloqueado gana sobre permitido.

### Cómo se une

Además de seguro, el servidor tiene que escalar: ¿qué pasa cuando hay cientos de tools?

---

## Tema 10 — Muchas tools MCP: tool search y límites de salida

### Qué es

Cada definición de tool (nombre, descripción, schema) ocupa contexto. Con varios servidores conectados podés llegar a cientos de tools y decenas de miles de tokens **solo en definiciones**, antes de que el usuario escriba nada. Y hay un segundo problema: la elección de la tool correcta **se degrada con más de 30–50 tools** disponibles. Es lo de 2A: con muchas tools parecidas, Claude elige peor.

**Tool search (búsqueda de tools)** resuelve las dos cosas. Las definiciones no entran todas al contexto desde el principio; cuando Claude necesita una tool, **la busca**, y recién ahí se carga su definición completa. En Claude Code, al arrancar se cargan solo los **nombres** de las tools. En la API es más estricto: las tools diferidas no entran al contexto ni siquiera por nombre; al principio solo están la tool de búsqueda y las que no se difirieron.

**En Claude Code y el Agent SDK** tool search está **activado por defecto** para las tools MCP. Si las tools de un servidor se usan en todos los turnos, buscarlas cada vez es un paso de más; para eso está **`alwaysLoad: true`** en la entrada de ese servidor, que carga todas sus tools. Si se quiere una sola, el autor del servidor la marca con `_meta["anthropic/alwaysLoad"]`.

**En la API** se activa agregando la tool de búsqueda y marcando las demás con **`defer_loading: true`**. Detalles:
- Conviene con **10 o más tools** o más de **10k tokens** de definiciones.
- **Al menos una tool no se difiere** (la de búsqueda nunca). La recomendación es dejar **3–5 tools frecuentes sin diferir**.
- `defer_loading` **no** evita mandar las definiciones: se envían igual en cada request; solo cambia lo que entra al contexto.
- Ahorro típico: **más del 85%** de los tokens de definiciones.

Como Claude busca por nombre y descripción, conviene que tengan **palabras clave específicas**: `search_slack_messages` se encuentra mejor que `query_slack`.

**Límites de salida en Claude Code.** Dos variables de entorno controlan cuánto puede pesar y tardar un servidor:
- `MAX_MCP_OUTPUT_TOKENS`: tope de salida de una tool MCP (default **25.000** tokens; avisa desde 10.000).
- `MCP_TIMEOUT`: cuánto espera Claude Code a que arranque un servidor (default **30 s**).

> ⚠️ **En la documentación actual vas a leer otra cosa (ya visto en 2B).** La guía dice que las tools de todos los servidores están *"available simultaneously"* (disponibles a la vez). Tool search no lo contradice del todo: todas siguen disponibles, solo que su definición se carga cuando hace falta. **Para el examen:** si preguntan por varios servidores, la respuesta es la de la guía (todas disponibles, sin un router que elija servidor).

### Ejemplo

TiendaX conecta GitHub, Jira, Slack, Sentry y su servidor de pedidos: unas 180 tools. Sin tool search, las definiciones ocupan ~50k tokens en cada turno y Claude empieza a confundir `search_issues` de GitHub con el de Jira. Con tool search activo, Claude carga solo los nombres y trae 3–5 definiciones cuando las necesita. Como SoporteBot usa `lookup_order` en casi todos los turnos, el servidor de pedidos queda con `alwaysLoad: true` (o el autor del servidor marca solo esa tool con `_meta["anthropic/alwaysLoad"]`).

### Para el examen

- Muchas tools y contexto saturado → **tool search** (ya activo por defecto en Claude Code).
- Una tool crítica en cada turno → no se difiere (`alwaysLoad` / sin `defer_loading`).

### Cómo se une

Último tema de la parte oficial: cerrar el caso Grep vs. MCP desde las built-in tools.

---

## Tema 11 — Built-in vs. MCP tools (incorporadas vs. MCP): quién gana y por qué

### Qué es

Es la Skill 3 de 2.4 que quedó abierta en 2B: *mejorar las descripciones de las tools MCP para explicar capacidades y salidas en detalle, así el agente no prefiere built-in tools como Grep frente a tools MCP más capaces*.

Ahora que conocés las built-in, entendés **por qué** pasa. Grep, Read y Glob son tools generales, que Claude conoce bien y que **siempre funcionan** sobre archivos. Si la tool MCP tiene una descripción como "Searches products.", Claude no tiene ningún motivo para preferirla: desde lo que lee, Grep parece igual de bueno y más conocido.

La solución es que la descripción de la tool MCP diga **lo que Grep no puede hacer**: consultar datos **en vivo**, filtrar por campos, devolver datos estructurados, incluir información que no está en los archivos. Así Claude tiene un motivo concreto para elegirla.

### Cuándo Grep **sí** es lo correcto

No se trata de que MCP siempre gane. Si lo que buscás es un **texto exacto en el código** (un nombre de función, un mensaje de error), **Grep** es la herramienta justa. Si necesitás **datos vivos de un sistema** (el stock actual, el estado de un ticket, un pedido), va la **tool MCP**, porque esos datos no están en ningún archivo.

### Ejemplo

El agente del Scenario 4 en TiendaX tiene el servidor MCP `tiendax-codeintel`, con la tool `find_references(symbol)`. Esa tool usa el índice del compilador y encuentra referencias **aunque estén renombradas o re-exportadas**.
- Con la descripción original, "Finds references.", Claude usa Grep y se pierde los alias (Tema 6).
- Con la descripción mejorada, Claude la elige: "Finds ALL references to a TypeScript symbol using the compiler index, including aliases, re-exports and dynamic imports that text search (Grep) misses. Returns file, line and kind of reference. Prefer this over Grep when tracing where a function is used."

### Para el examen

- El agente usa Grep cuando hay una tool MCP mejor → **mejorar la descripción de la tool MCP**.
- ❌ Quitar Grep, ❌ regla en el system prompt, ❌ hook que bloquee Grep.

### Cómo se une

Con esto quedan cubiertos los 9 puntos de 2.4 y los 9 de 2.5. La Parte 3 es contenido del curso: útil para entender, pero lejos del foco del examen.

---

# Parte 3 — Lo que agrega el curso

> Esta parte sale mayormente del curso (📘) y tiene **varios datos desactualizados o equivocados**, que corrijo en cada tema. La guía no nombra estos temas en los puntos de 2.4 ni de 2.5. Leela para entender; no le dediques horas.

## Tema 12 — Sampling, notificaciones y roots

### Qué es

📘 **Curso:** Jacob presenta tres capacidades "avanzadas" de MCP. Las tres son formas en que el servidor y el cliente se comunican **además** de las llamadas a tools.

**Sampling (muestreo).** Normalmente el cliente le pide cosas al servidor. Con sampling es al revés: el **servidor** le pide al **cliente** que haga una llamada al modelo (`sampling/createMessage`). El cliente la hace con **sus** credenciales y **sus** reglas, y puede pedirle aprobación al usuario. La ventaja es que el servidor no necesita API keys propias.

**Notifications (notificaciones).** Mensajes que el servidor manda sin que nadie los pida, de dos tipos:
- **Progress (progreso):** valores numéricos (`progress` / `total`) atados a un `progressToken` de la llamada original, para mostrar una barra de avance en operaciones largas.
- **Log:** mensajes de diagnóstico con nivel de severidad.

La diferencia es para quién son: log es para **observabilidad** (quien depura el sistema); progress es para mostrarle el estado **al usuario**.

**Roots (raíces).** La lista de carpetas que el cliente le informa al servidor como zona de trabajo.

Una corrección importante: **en la especificación vigente de MCP (2026-07-28), Sampling, Roots y Logging están deprecados.** La spec recomienda pasar carpetas por parámetros o configuración, llamar a la API del proveedor directamente y loguear a stderr u OpenTelemetry. `notifications/progress` sigue existiendo.

> ⚠️ **En el curso vas a escuchar otra cosa.** El companion dice que un servidor *"no tiene acceso implícito a ninguna ruta sin una lista de roots"*, como si los roots otorgaran permisos. **Para el examen: los roots son informativos (advisory), no un mecanismo de seguridad.** Un servidor stdio corre con los permisos de tu usuario; el límite real lo ponen los **permisos del sistema operativo o un sandbox**. (Las propias slides del curso dicen esto mismo.)

### Ejemplo

El servidor `tiendax-catalogo` tiene una tool `reindexar_catalogo` que tarda 2 minutos. Mientras corre, manda notificaciones de **progress** (`3/10`, `4/10`…) para que la interfaz muestre una barra, y mensajes de **log** ("lote 4: 120 productos sin imagen") para quien depura. Si para clasificar productos necesitara al modelo, con **sampling** se lo pediría al cliente en vez de tener su propia API key.

### Para el examen

- Si aparece: sampling = el servidor pide inferencia **a través del cliente**; progress = barra de avance; roots = carpetas **informadas**, no un mecanismo de seguridad.
- No son parte del texto oficial de 2.4.

### Cómo se une

El otro bloque del curso es cómo poner un servidor en producción.

---

## Tema 13 — Servidores MCP en producción: least privilege, autenticación y versionado

### Qué es

📘 **Curso:** ideas de las lecciones 48–49 sobre cómo construir y operar un servidor MCP propio.

**Least privilege (mínimo privilegio) desde el diseño.** La idea es que cada tool pueda hacer solo lo justo, para que un error del modelo, o alguien que lo manipule con prompt injection, no pueda hacer mucho daño. En la práctica:
- Una tool por **operación lógica**, no una tool "hacé cualquier SQL en cualquier base". Una tool tan amplia le da acceso total al modelo y a cualquiera que lo manipule.
- **Schema constraints (restricciones en el schema):** `enum` en vez de texto libre (lo viste en 2A).
- **Filtrar la salida** según lo que puede ver quien llama.
- **Sanitizar** cada argumento en el servidor, tratando toda entrada como no confiable.
- 📘 Las slides hablan de tres capas: schema, autorización en el servidor y permisos del sistema operativo.

**Autenticación.** La spec de MCP usa **OAuth 2.1** y la autorización es **opcional**; en stdio, las credenciales salen del entorno. Igual, **OAuth y la rotación de API keys están fuera del alcance de la guía.**

> ⚠️ **En el curso vas a escuchar otra cosa.** El companion dice *"OAuth 2.0 is the MCP-specified authentication mechanism"*. **Para el examen:** la spec usa OAuth 2.1 y la autorización es opcional; de todos modos, OAuth está fuera del alcance de la guía.

**Versionado.** Agregar tools o campos opcionales es compatible: los clientes viejos siguen funcionando. Quitar o renombrar tools, o cambiar argumentos obligatorios, rompe a los clientes; en ese caso va una **versión mayor + período de migración**.

**Operación.** **Rate limiting (límite de pedidos por cliente)** con HTTP **429** + `Retry-After`; **health endpoints (URLs de chequeo de salud)**; timeouts duros. Todo esto es **hosting (alojar y operar el servidor)**, que está **fuera del alcance**: puede aparecer como distractor.

### Ejemplo

**Mal:** el servidor de TiendaX expone `run_sql(query)` con acceso de escritura a toda la base.
**Bien:** expone `lookup_order(order_id)`, `list_returns(customer_id, status: enum)` y nada que escriba sin necesidad. Cada una valida sus argumentos y devuelve solo los campos que el agente de soporte puede ver.

### Para el examen

- La idea que sí conecta con la guía: **tools acotadas** (2A, Tema 10) y **pocas tools por agente**. Si una opción es "una tool genérica que ejecuta cualquier consulta", sospechá.
- OAuth, rate limiting y deploy → no son lo que evalúa el examen.

### Cómo se une

Lo último que enseña el curso son las tools que ofrece la API, que el curso llama "built-in tools".

---

## Tema 14 — Las "built-in tools" de la API: server tools vs. client tools (las que ejecuta Anthropic vs. las que ejecuta tu app)

### Qué es

📘 **Curso:** las lecciones 50–51 presentan las tools que ofrece la **API de Claude** y que se activan con un `type`, sin escribir un schema. Son distintas de las built-in de Claude Code (Tema 1): las usa una aplicación que llama a la API directamente.

La documentación las divide en dos grupos según **quién las ejecuta**, y eso define a qué pueden llegar. Las **server tools** las ejecuta Anthropic en su infraestructura: vos no hacés nada, pero tampoco llegan a tu red. Las **client tools** con schema de Anthropic las ejecuta **tu aplicación**: Anthropic define cómo se llaman, Claude pide usarlas, vos las ejecutás y devolvés el resultado, así que llegan a lo que vos les conectes.

| | **Server tools** | **Client tools** con schema de Anthropic |
|---|---|---|
| Quién las ejecuta | **Anthropic**, en su infraestructura | **Tu aplicación** (vos ejecutás y devolvés el resultado) |
| Ejemplos | `web_search`, `web_fetch`, `code_execution`, `tool_search` | `bash`, `text_editor`, `computer`, `memory` |
| ¿Llegan a tu red privada? | **No** | **Sí**, a lo que vos les conectes |

Detalles:
- `web_search`: Claude arma la consulta; `max_uses` limita cuántas búsquedas hace; las fuentes vuelven como citas.
- `text_editor`: tiene un `str_replace` con la **misma regla de unicidad** que Edit: el texto tiene que aparecer exactamente una vez.
- 📘 Las slides dicen literalmente que en la API *"no built-in glob or grep tool exists"*: se usa `bash`. Es otra señal de que **no** son las mismas tools que las built-in de Claude Code.

> ⚠️ **En el curso vas a escuchar otra cosa.** El companion dice que `computer_use` *"operates inside a sandboxed environment... cannot reach the host"*, que `code_execution` *"runs in an ephemeral container... State does not persist"* y que hay "five built-ins". **Para el examen:** `computer` es una **client tool** que corre en el entorno que **vos** proveés, y Anthropic recomienda que **vos** lo aísles (VM o contenedor con permisos mínimos; las slides del curso dicen lo mismo). `code_execution` usa por defecto un contenedor nuevo por request, pero **se puede reutilizar pasando el container ID** (los archivos persisten; expira a los 30 días). Y la documentación no habla de "cinco": tiene la lista de server y client tools de arriba.

### Ejemplo

SoporteBot, armado sobre la API, usa `web_search` (server tool) para un dato público, como el horario de un correo. Para consultar el pedido TX-104233 usa el servidor MCP propio de TiendaX dentro de su red. No podría hacerlo con `web_search`: esa tool corre en la infraestructura de Anthropic y nunca llegaría a la base privada de pedidos.

### Built-in o custom

📘 **Curso** (coincide con la idea oficial): la decisión depende de dónde están los datos.
- Conviene una built-in de la API si encaja y los datos son públicos (buscar en la web, correr un cálculo).
- Conviene algo **custom** (un servidor MCP propio dentro de tu red) si hay **APIs internas**, **datos regulados**, **schemas de tu dominio** o **auditoría**, porque una server tool corre en la infraestructura de Anthropic y no llega a tu red privada.
- Es el mismo espíritu de 2B, Tema 9: lo estándar ya existe; lo propio del negocio, se construye.

### Para el examen

- **No confundas:** la tarea 2.5 = **Read, Write, Edit, Bash, Grep, Glob** (Claude Code / Agent SDK). Si en una pregunta de explorar o editar código aparece `web_search` o `code_execution` como opción, es un distractor.

### Cómo se une

Cierra el capítulo y el módulo 2: ya tenés cómo se diseñan las tools (2A), cómo se publican y configuran con MCP (2B), y cómo se eligen las incorporadas y se opera MCP en serio (2C).

---

## Cómo se une todo

Claude Code y el Agent SDK traen **seis built-in tools**: Read, Write, Edit, Bash, Grep y Glob (Tema 1). Las dos que buscan se distinguen por qué miran: **Grep busca contenido** (callers, errores, imports) y **Glob busca nombres y rutas** (`**/*.test.tsx`) (Tema 2). Para modificar, **Edit** hace cambios puntuales con un ancla única, **Write** crea o reescribe archivos completos y **Read** va antes de modificar (Tema 3). Si Edit falla porque el texto no es único, el plan B es **Read + Write** del archivo completo (Tema 4).

Para entender un codebase desconocido, se entra con **Grep a los entry points** y se sigue con **Read por los imports**, sin leer todo (Tema 5); si hay wrappers, primero se **listan los nombres exportados** y se hace Grep por cada uno (Tema 6). En el SDK, **`allowedTools` aprueba pero no restringe**; lo que restringe es `tools` o `disallowedTools` (Tema 7).

Del lado de MCP: **stdio** es para lo local y de un usuario, **Streamable HTTP** para lo remoto y compartido, y SSE como transporte está deprecado (Tema 8). Los servidores de un repo **piden aprobación**, salvo en `-p` y el SDK; la organización controla con `managed-mcp.json` y listas allow/deny, donde deny gana (Tema 9). Con muchas tools se usa **tool search** y pocas tools siempre cargadas (Tema 10). Si el agente prefiere Grep a una tool MCP mejor, se **mejora la descripción** de la tool MCP (Tema 11). Lo que agrega el curso (sampling, roots y logging, hoy deprecados; producción y OAuth, fuera de alcance; las "built-in" de la API, que son otra cosa) está en los Temas 12–14.

## Lo que viene

Termina el módulo 2. Lo próximo son las **preguntas de fin del módulo 2**, que cubren 2A, 2B y 2C (tareas 2.1 a 2.5): de a una, con el formato del examen real y corrección inmediata. Después arranca el **módulo 3: Claude Code Configuration & Workflows** (CLAUDE.md, comandos, skills, plan mode, CI/CD). Ahí vuelven Glob (en las reglas por ruta) y el Explore subagent.

---

## Las trampas del examen

Cada trampa tiene el mismo orden: la situación, **qué elegir en el examen (✅)**, las opciones que tientan (❌) con por qué tientan y por qué están mal, y una regla para recordar.

### Grupo: Elegir la built-in tool correcta

#### Trampa 1 · Encontrar todos los que llaman a una función

**La situación.** Hay que encontrar todos los lugares donde se llama a `procesarReembolso()` (Tema 2).

**✅ En el examen elegí:** **Grep** por `procesarReembolso` en el codebase.

**❌ Las que tientan:**

❌ **"Glob con `**/*procesarReembolso*`".**
- *Tienta porque:* Glob "busca" y el patrón incluye el nombre.
- *Está mal porque:* Glob busca **nombres de archivo**, no contenido. Solo encontraría archivos llamados así.

❌ **"Read de todos los archivos de `src/` y buscar a mano".**
- *Tienta porque:* parece exhaustivo.
- *Está mal porque:* llena el contexto con cientos de archivos; Grep hace exactamente eso en una llamada.

> 🧠 **Para recordar:** adentro del archivo → Grep.

#### Trampa 2 · Encontrar los archivos de test

**La situación.** Hay que listar todos los archivos de test de componentes React (Tema 2).

**✅ En el examen elegí:** **Glob** con `**/*.test.tsx`.

**❌ Las que tientan:**

❌ **"Grep por `describe(` o `test(`".**
- *Tienta porque:* todos los tests tienen esas palabras.
- *Está mal porque:* mezcla contenido con nombres; trae archivos que no son tests y se pierde los que usan otra sintaxis. El patrón de nombre es exacto.

❌ **"Bash con `find . -name '*.test.tsx'`".**
- *Tienta porque:* funciona.
- *Está mal porque:* en preguntas al estilo de la guía, la tool dedicada para patrones de nombre es Glob: es justo el criterio que evalúa 2.5.

> 🧠 **Para recordar:** por nombre o extensión → Glob.

#### Trampa 3 · Edit falla porque el texto aparece varias veces

**La situación.** Edit devuelve error: el `old_string` aparece 3 veces en el archivo y solo hay que cambiar una (Tema 4).

**✅ En el examen elegí:** **Read del archivo completo + Write** del archivo corregido. (Si esa opción no está: agregar más contexto al texto a reemplazar para que sea único.)

**❌ Las que tientan:**

❌ **"Reintentar el mismo Edit".**
- *Tienta porque:* "a veces falla de casualidad".
- *Está mal porque:* Edit exige que el texto aparezca exactamente una vez. Va a fallar igual.

❌ **"Usar `replace_all: true`".**
- *Tienta porque:* hace que Edit funcione.
- *Está mal porque:* cambia las **tres** ocurrencias, y solo había que cambiar una.

❌ **"Write solo con el bloque corregido".**
- *Tienta porque:* parece más liviano.
- *Está mal porque:* Write **reemplaza el archivo entero**: borrarías todo lo demás.

> 🧠 **Para recordar:** Edit no único → Read + Write (del archivo completo).

#### Trampa 4 · Cambiar una línea con Write

**La situación.** Hay que cambiar el valor de una constante en un archivo de 600 líneas (Tema 3).

**✅ En el examen elegí:** **Edit** con un ancla única.

**❌ Las que tientan:**

❌ **"Read + Write porque es más confiable".**
- *Tienta porque:* la guía lo menciona como confiable.
- *Está mal porque:* es el **fallback** para cuando Edit falla, no la forma normal. Reescribir 600 líneas para cambiar una arriesga alterar otras.

> 🧠 **Para recordar:** puntual → Edit; Read + Write solo como plan B.

### Grupo: Explorar código

#### Trampa 5 · Entender un codebase desconocido

**La situación.** El agente del Scenario 4 tiene que explicar cómo funciona el flujo de reembolsos en un sistema legacy de 2.000 archivos (Tema 5).

**✅ En el examen elegí:** **Grep para encontrar los entry points y después Read siguiendo los imports**, de forma incremental.

**❌ Las que tientan:**

❌ **"Leer todos los archivos primero para tener el panorama completo".**
- *Tienta porque:* "con todo el contexto no se le escapa nada".
- *Está mal porque:* agota el contexto y diluye la atención; la guía lo descarta explícitamente ("rather than reading all files upfront").

❌ **"Glob de todo el proyecto y leer los archivos más recientes".**
- *Tienta porque:* parece un filtro razonable.
- *Está mal porque:* la fecha no dice dónde está el flujo; Grep sí.

> 🧠 **Para recordar:** Grep para entrar, Read para seguir el hilo.

#### Trampa 6 · Faltan usos de una función que pasa por un wrapper

**La situación.** Grep de `procesarReembolso` encuentra 3 usos, pero hay más: un `index.ts` la re-exporta como `reembolsar` (Tema 6).

**✅ En el examen elegí:** **identificar todos los nombres que exporta el wrapper y hacer Grep por cada uno.**

**❌ Las que tientan:**

❌ **"Un regex más amplio: `.*Reembols.*`".**
- *Tienta porque:* "atrapa más".
- *Está mal porque:* sigue sin cubrir alias arbitrarios (`devolverPago`) y trae muchísimo ruido.

❌ **"Read de todos los archivos que importan el módulo de pagos".**
- *Tienta porque:* parece completo.
- *Está mal porque:* es leer de más; con la lista de exports, Grep lo resuelve.

> 🧠 **Para recordar:** wrapper → primero los nombres exportados, después Grep por cada uno.

### Grupo: Permisos y MCP

#### Trampa 7 · "allowedTools para que solo lea"

**La situación.** Un subagente del Agent SDK tiene que poder solo leer y buscar (Tema 7).

**✅ En el examen elegí:** limitarlo con **`tools: ["Read", "Grep", "Glob"]`** (o sacar las otras con `disallowedTools`).

**❌ Las que tientan:**

❌ **"`allowedTools: ["Read", "Grep", "Glob"]`".**
- *Tienta porque:* el nombre dice "permitidas".
- *Está mal porque:* `allowedTools` **auto-aprueba**, no restringe. Write, Edit y Bash siguen existiendo.
- *Salvedad:* si ninguna opción usa `tools` o `disallowedTools`, "limitar el `allowedTools` del subagente a las tools de su rol" es la respuesta con el lenguaje de la guía (ver Tema 7).

> 🧠 **Para recordar:** allowed = sin preguntar; tools/disallowed = qué existe.

#### Trampa 8 · Servidor para todo el equipo de soporte remoto

**La situación.** El servidor de pedidos lo van a usar 40 agentes de soporte desde distintas máquinas (Tema 8).

**✅ En el examen elegí:** **Streamable HTTP**.

**❌ Las que tientan:**

❌ **"stdio, porque es más simple y no necesita configuración de red".**
- *Tienta porque:* es verdad que es más simple.
- *Está mal porque:* stdio es un proceso hijo **local**, de **un** cliente. Si cruza la red o lo usan varios, queda descartado.

❌ **"SSE".**
- *Tienta porque:* suena a "streaming remoto".
- *Está mal porque:* el transporte SSE está deprecado; hoy SSE va dentro de Streamable HTTP.

> 🧠 **Para recordar:** red o varios usuarios → Streamable HTTP.

#### Trampa 9 · El repo clonado trae su propio servidor

**La situación.** Un pipeline de CI corre `claude -p` sobre un repo que trae un `.mcp.json` con un servidor desconocido (Tema 9).

**✅ En el examen elegí:** **limitar explícitamente los servidores** (`--strict-mcp-config` con los aprobados, o `disabledMcpjsonServers`), porque en `-p` **no hay prompt de aprobación**.

**❌ Las que tientan:**

❌ **"No pasa nada: Claude Code siempre pide aprobación para los servidores del proyecto".**
- *Tienta porque:* en sesiones interactivas es así.
- *Está mal porque:* en `-p` y en el Agent SDK los carga **sin preguntar**.

❌ **"Bloquearlo por `serverName` en `deniedMcpServers`".**
- *Tienta porque:* es una denylist.
- *Está mal porque:* el nombre lo elige el que escribe el `.mcp.json`; *"serverName … is not a security control"*. Se bloquea por URL o comando.

> 🧠 **Para recordar:** interactivo pregunta; automatizado no.

#### Trampa 10 · Demasiadas tools MCP

**La situación.** Con cinco servidores conectados (180 tools), las definiciones ocupan ~50k tokens por turno y Claude confunde tools parecidas (Tema 10).

**✅ En el examen elegí:** **tool search** (diferir la carga) y dejar **pocas tools frecuentes siempre cargadas**.

**❌ Las que tientan:**

❌ **"Diferir todas las tools, incluida la de búsqueda".**
- *Tienta porque:* ahorra el máximo.
- *Está mal porque:* la API exige al menos una sin diferir (error 400), y las 3–5 más usadas conviene tenerlas a mano.

❌ **"Un agente router que elija el servidor antes de cada turno".**
- *Tienta porque:* "reduce" las tools.
- *Está mal porque:* es sobreingeniería; tool search ya resuelve eso y la guía dice que todas están disponibles a la vez.

> 🧠 **Para recordar:** muchas tools → tool search, no un router.

### Grupo: Confusiones del curso

#### Trampa 11 · Las "built-in tools" equivocadas

**La situación.** Una pregunta del Scenario 4 pide elegir cómo el agente encuentra un mensaje de error en el código. Entre las opciones aparece `web_search` o `code_execution` (Temas 1 y 14).

**✅ En el examen elegí:** **Grep**.

**❌ Las que tientan:**

❌ **"`code_execution` para correr un script que busque".**
- *Tienta porque:* el curso la presenta como "built-in".
- *Está mal porque:* corre en un contenedor de Anthropic **sin acceso a tu código local**; la tarea 2.5 habla de las tools de Claude Code.

> 🧠 **Para recordar:** 2.5 = Read, Write, Edit, Bash, Grep, Glob.

#### Trampa 12 · Roots como seguridad

**La situación.** Una opción dice que, para evitar que un servidor MCP lea archivos sensibles, alcanza con no incluir esa carpeta en los roots (Tema 12).

**✅ En el examen elegí:** la que use **permisos reales**: permisos del sistema operativo o un sandbox donde corre el servidor, tools acotadas, o reglas deny sobre las tools MCP (`mcp__servidor__tool`).

**❌ Las que tientan:**

❌ **"Los roots otorgan acceso explícito; sin root no hay acceso".**
- *Tienta porque:* el companion del curso lo dice así.
- *Está mal porque:* los roots son **informativos**; el servidor corre con los permisos del usuario. Además, están deprecados en la spec vigente.

> 🧠 **Para recordar:** roots informan, no protegen.

---

## Checklist oficial

**Tarea 2.5 — Select and apply built-in tools (Read, Write, Edit, Bash, Grep, Glob) effectively**

*Knowledge of*
- [x] Grep para buscar contenido (nombres de funciones, mensajes de error, imports) → **Tema 2** (Trampa 1)
- [x] Glob para buscar archivos por patrón de ruta (nombre o extensión) → **Tema 2** (Trampa 2)
- [x] Read/Write para operaciones sobre archivos completos; Edit para cambios puntuales con texto único → **Tema 3** (Trampa 4)
- [x] Cuando Edit falla por coincidencias no únicas, Read + Write como fallback → **Tema 4** (Trampa 3)

*Skills in*
- [x] Elegir Grep para buscar en el código (callers de una función, mensajes de error) → **Tema 2** (Trampa 1)
- [x] Elegir Glob para archivos con patrones de nombre (`**/*.test.tsx`) → **Tema 2** (Trampa 2)
- [x] Read del archivo completo y después Write cuando Edit no encuentra un ancla única → **Tema 4** (Trampa 3)
- [x] Entender el codebase de a poco: Grep para entry points, Read siguiendo imports, sin leer todo de entrada → **Tema 5** (Trampa 5)
- [x] Rastrear el uso de funciones a través de wrappers: listar los nombres exportados y buscar cada uno → **Tema 6** (Trampa 6)

**Tarea 2.4 — se completa acá** (los demás puntos, en 2B)
- [x] Mejorar las descripciones de tools MCP para que el agente no prefiera built-in tools como Grep → **2B Tema 8 + 2C Tema 11**
- [x] In-scope "multi-server simultaneous access" y muchas tools → **Tema 10** (Trampa 10)

**De la documentación, no de la guía** (vale saberlo; la guía no lo pregunta directo): Grep y Glob ausentes por defecto en Unix, ripgrep, `output_mode`, tope de 100 de Glob (Temas 1–2) · read-before-edit, `replace_all` (Temas 3–4) · `allowedTools`/`disallowedTools`/`tools` (Tema 7) · aprobación de `.mcp.json`, `-p`/SDK, `managed-mcp.json`, allow/deny (Tema 9) · tool search, `alwaysLoad`, `defer_loading`, `MAX_MCP_OUTPUT_TOKENS`, `MCP_TIMEOUT` (Tema 10).

**📘 Curso (útil para entender; lecciones 44–51 y deck 135):** regla de transporte y "SSE no es un transporte aparte" (Tema 8) · sampling, progress vs. log, roots (Tema 12) · least privilege, sanitización, versionado, 429 (Tema 13) · server vs. client tools, built-in vs. custom (Tema 14) · tool search: umbrales y números (Tema 10).

---

## Autoevaluación oral

1. ¿Qué diferencia hay entre Grep y Glob? Dame dos ejemplos de TiendaX para cada una.
2. ¿Cuándo usás Edit y cuándo Write? Edit falla porque el texto aparece tres veces: ¿qué hacés y por qué no sirven `replace_all` ni "Write del bloque"?
3. Te dan un sistema legacy desconocido. ¿Cómo lo explorás? ¿Qué hacés si la función que buscás pasa por un `index.ts` que la re-exporta con otro nombre?
4. ¿Cuándo un servidor MCP va por stdio y cuándo por Streamable HTTP? ¿Qué pasa con los servidores de un `.mcp.json` en una sesión interactiva y en `claude -p`?
5. ¿Qué resuelve tool search? ¿Por qué `allowedTools` no sirve para limitar un subagente?

---

## Preguntas tipo examen

Las preguntas tipo examen de este capítulo están en [`04-practica/modulo-2.md`](../04-practica/modulo-2.md), junto con las del resto del módulo 2. Hacelas cuando termines **todos** los capítulos del módulo, de a una y sin mirar la respuesta.

> Nota: **ninguna pregunta de muestra de la guía oficial evalúa 2.4 ni 2.5**. Las de este capítulo se arman con el texto oficial de las tareas y el **Scenario 4 (Developer Productivity with Claude)**, que es donde aparecen las built-in tools y MCP juntos.

---

## Revisión contra el blueprint oficial

Qué puede salir en el examen de 2.4 y 2.5 que el curso de Jacob **no cubre o cubre flojo**, y dónde quedó explicado acá:

1. **Toda la tarea 2.5.** El curso no menciona Read/Write/Edit/Grep/Glob de Claude Code ni cuándo usar cada una: sus "built-in tools" son las de la API. → Temas 1–7.
2. **Grep vs. Glob** con los ejemplos de la guía (callers, mensajes de error, `**/*.test.tsx`). → Tema 2.
3. **Edit con ancla única y el fallback Read + Write.** → Temas 3 y 4.
4. **Exploración incremental y wrappers** (Skills 4 y 5 de 2.5). → Temas 5 y 6.
5. **Grep vs. tool MCP** (Skill 3 de 2.4). → Tema 11.
6. **Seguridad práctica de MCP en Claude Code** (aprobación, `-p`/SDK, managed, allow/deny): el curso habla de seguridad del servidor, no de cómo Claude Code controla los servidores. → Tema 9.
7. **Datos del curso que están mal o viejos:** "Claude Code usa stdio como transporte nativo"; roots como permiso; OAuth 2.0 "obligatorio"; `code_execution` "efímero"; `computer_use` "con sandbox de Anthropic"; sampling/roots/logging sin aclarar que están deprecados. → Temas 8, 12, 13 y 14.
8. **Fuera de alcance según la guía:** hosting/deploy de servidores y detalles de OAuth/rotación de keys. Si aparecen, suelen ser distractores. → Temas 8, 9 y 13.

Qué responder cuando la documentación actual choca con la guía: **Grep/Glob existen** (aunque hoy no vengan por defecto en Unix); **Edit no único → Read + Write**; **todas las tools de todos los servidores disponibles a la vez** (aunque exista tool search).

