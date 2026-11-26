# Capítulo 6 · 2B · Udemy 7 — MCP Server Configuration (configuración de servidores MCP)

*Tarea oficial 2.4 (se completa en 2C) · Segundo capítulo del módulo 2*

---

## Dónde estamos

Seguimos en el **módulo 2: Tool Design & MCP Integration** (18% del examen). Este capítulo cubre la tarea:
- **2.4** Integrate MCP servers into Claude Code and agent workflows (integrar servidores MCP en Claude Code y en flujos de agentes). Pesa 3,6% del examen.

La tarea 2.4 se reparte entre 2B y 2C. Acá ves **qué es MCP, cómo se configura un servidor en Claude Code y cómo se construye uno**. En 2C vas a ver los transportes en detalle, la seguridad y las tools que ya trae Claude Code (Read, Grep, Glob…).

### Cómo leer este capítulo

Todo lo que leés acá **vale para el examen**, salvo que diga lo contrario. Cuando algo sale solo del curso (útil para entender, pero no central), lo marco con **📘 Curso**. Cuando Jacob dice algo distinto de lo que evalúa la guía, aparece un recuadro así:

> ⚠️ **En el curso vas a escuchar otra cosa.** … **Para el examen: …**

### Un aviso sobre este capítulo

El curso (lecciones 37–43) explica muy bien **qué es MCP y cómo se programa un servidor en Python**. Pero **no cubre 7 de los 9 puntos oficiales de 2.4**: no habla de `.mcp.json`, de `~/.claude.json`, de las variables de entorno, de los servidores de la comunidad ni del problema "el agente usa Grep en vez de la tool MCP". Esos puntos están en la **Parte 2** de este capítulo y salen de la guía y de la documentación. **La Parte 2 es la más importante para el examen.**

## De dónde venimos

En **2A** viste cómo se diseña una tool: la **descripción** es lo que Claude lee para elegirla, el `input_schema` define qué datos recibe y, cuando falla, la tool devuelve un error estructurado con **`isError`**. En **1C** viste el **least privilege** (mínimo privilegio): cada agente recibe solo las tools que necesita, y en el Agent SDK eso se controla con `allowedTools`.

Hasta ahora las tools eran funciones de tu propio código. Este capítulo muestra **MCP**: la forma estándar de **publicar** tools (y otras cosas) para que las use Claude Code o cualquier agente, sin reescribir la integración para cada uno.

## Mapa del capítulo

**Parte 1 — Qué es MCP.** El problema que resuelve y las tres cosas que puede ofrecer un servidor.
1. What MCP is (qué es MCP): cliente, servidor y host.
2. The three primitives (los tres primitivos): tools, resources y prompts.
3. Resources as content catalogs (resources como catálogos de contenido).

**Parte 2 — Configurar servidores MCP en Claude Code y en agentes (el núcleo oficial de 2.4).**

4. Scopes (alcances): `.mcp.json` del proyecto vs. `~/.claude.json` personal.
5. Environment variable expansion (expansión de variables de entorno): `${GITHUB_TOKEN}`.
6. Cómo se agrega un servidor: `claude mcp add` y el formato del archivo.
7. Varios servidores a la vez: todas las tools disponibles simultáneamente.
8. Que el agente use la tool MCP y no Grep: mejorar la descripción.
9. Community servers vs. custom servers (servidores de la comunidad vs. propios).
10. MCP en el Agent SDK: `mcpServers` y `allowedTools`.

**Parte 3 — Construir y conectar un servidor (lo que enseña el curso).**

11. Un servidor MCP en Python: tools con `@mcp.tool()`.
12. Resources en detalle: URI, templates y subscriptions.
13. Prompts en detalle: argumentos, `prompts/list` y `prompts/get`.
14. El cliente: transportes, conexión, discovery y errores.

---

# Parte 1 — Qué es MCP

## Tema 1 — What MCP is (qué es MCP): cliente, servidor y host

### Qué es

Una tool, como viste en 2A, es una función que Claude puede pedir que se ejecute. Hasta ahora esa función vivía dentro de tu aplicación, y si otra aplicación quería la misma tool, había que programarla de nuevo. **MCP (Model Context Protocol, protocolo de contexto para modelos)** resuelve eso: es un **estándar abierto** que define cómo una aplicación de IA se conecta con tools, datos y otras capacidades externas, **siempre de la misma manera**. Quien tiene los datos los publica una vez, y cualquier aplicación que hable MCP los puede usar.

📘 **Curso:** Jacob lo explica con el **problema N×M**. Antes de MCP, cada aplicación (un chat, un IDE, un dashboard) necesitaba un adaptador propio para cada sistema (base de datos, CRM, archivos): 3 aplicaciones por 3 sistemas daban **9 adaptadores**, cada uno con su propia autenticación y su propio código "pegamento". Si un sistema cambiaba su API, se rompían todos los adaptadores que lo usaban. Con MCP, cada sistema publica **un** servidor y cualquier aplicación compatible lo usa.

En MCP hay tres piezas, y conviene distinguirlas porque las preguntas las nombran. El **MCP server** (servidor MCP) es un proceso o servicio que **expone** (ofrece) capacidades: tools, resources y prompts, que vas a ver en el Tema 2. El **MCP client** (cliente MCP) es el componente que se conecta a **un** servidor, le pregunta qué ofrece y le hace pedidos. El **host** (aplicación anfitriona) es la aplicación de IA que usa la persona, por ejemplo **Claude Code**; el host crea **un cliente por cada servidor** al que se conecta. Por eso un host puede estar conectado a **varios servidores a la vez**, cada uno con su cliente (esto vuelve en el Tema 7).

| Pieza | Qué es | Ejemplo |
|---|---|---|
| **Server** | Expone tools, resources y prompts | `tiendax-pedidos` |
| **Client** | Se conecta a **un** servidor, descubre y pide | El cliente que Claude Code crea para `tiendax-pedidos` |
| **Host** | La aplicación de IA; crea un cliente por servidor | Claude Code, SoporteBot |

📘 **Curso:** Jacob agrega dos ideas. MCP es **model-agnostic** (independiente del modelo): no es exclusivo de Claude; el servidor no sabe qué modelo lo usa y el cliente no sabe quién programó el servidor. Y permite **equipos independientes**: el equipo de pagos publica su servidor, el de documentación el suyo, y la aplicación de soporte los usa sin conocer cómo están hechos por dentro; si un servidor se actualiza, los clientes no se rompen.

### Ejemplo

En TiendaX, el equipo de desarrollo usa **Claude Code**, que es el host. Claude Code se conecta a tres servidores MCP: `github`, para leer issues y pull requests; `jira`, para ver los tickets del sprint; y `tiendax-pedidos`, un servidor propio que consulta la base de pedidos. Para cada uno crea un cliente.

SoporteBot, que está hecho con el Agent SDK, también puede conectarse a `tiendax-pedidos` **sin escribir otra integración**. Ese es el beneficio de MCP: el servidor se programó una vez y lo usan dos hosts distintos.

### Para el examen

- MCP = estándar para conectar tools y datos externos de forma uniforme.
- Host (Claude Code, tu agente) → un cliente por servidor → varios servidores a la vez.
- **Ojo:** desplegar u hospedar servidores MCP (infraestructura, redes, contenedores) está **fuera del alcance** del examen. No te van a preguntar cómo montar el servidor en la nube.

### Cómo se une

Una tool de 2A era una función en tu código. Una tool MCP es lo mismo, pero publicada en un servidor para que la use cualquier host. Todo lo que aprendiste de **descripciones** y de **`isError`** sigue valiendo.

---

## Tema 2 — The three primitives (los tres primitivos): tools, resources y prompts

### Qué es

Un servidor MCP puede ofrecer tres tipos de cosas, que la especificación llama **primitives** (primitivos). Lo que los distingue no es tanto qué contienen, sino **quién decide usarlos**: el modelo, la aplicación o el usuario. Esta distinción es la que más se pregunta, porque las opciones incorrectas suelen decir que el modelo "elige" algo que en realidad elige otro.

Una **tool** es una **acción**: Claude, mientras razona, decide "necesito consultar el pedido" y la llama. Es exactamente lo que viste en 2A, y por eso se dice que es **model-controlled** (la controla el modelo). Un **resource** es **contenido para leer** que tiene una dirección, llamada **URI** (identificador del recurso, como `tiendax://politicas/devoluciones`). El modelo no lo "llama": lo elige la aplicación, o el usuario a través de la aplicación, y lo **inyecta** en el **contexto** (todo el texto que Claude tiene delante al responder). El modelo lo lee como cualquier otro texto, y por eso es **application-controlled** (lo controla la aplicación). Un **prompt** es una **plantilla** con parámetros que vive en el servidor; el **usuario** la elige explícitamente, desde un menú o un slash command, para arrancar una tarea. Es **user-controlled** (lo controla el usuario).

| Primitivo | Quién lo controla | Para qué sirve | Ejemplo |
|---|---|---|---|
| **Tools** | **Model-controlled** (lo controla el modelo) | **Acciones**: el modelo decide llamarlas | Consultar un pedido, crear un ticket, enviar un mail |
| **Resources** | **Application-controlled** (lo controla la aplicación) | **Datos/contenido** que la aplicación pone en el contexto | Un archivo, el esquema de una base, la lista de issues |
| **Prompts** | **User-controlled** (lo controla el usuario) | **Plantillas** que el usuario elige para arrancar una tarea | "Revisá este PR", "resumí este incidente" |

📘 **Curso:** Jacob marca esto como **"Exam Trap"** (trampa de examen): los resources los controla la aplicación, no los invoca el modelo; el host elige y el modelo lee, así que no hay que confundirlo con una llamada a tool. También da un árbol de decisión para elegir el primitivo: si el modelo necesita **hacer** algo (una acción o un cálculo), es una tool; si necesita **datos o contexto** antes de responder, es un resource; si es un **flujo reutilizable** que el usuario arranca a propósito, es un prompt.

### Ejemplo

El servidor `tiendax-pedidos` ofrece los tres. La **tool** `lookup_order(order_id)` la llama Claude cuando Juan pregunta por su pedido #12345. El **resource** `tiendax://politicas/devoluciones` es el texto de la política de devoluciones: la aplicación lo pone en el contexto y nadie lo "llama". El **prompt** `resumen_reclamo(order_id)` lo elige del menú un agente humano de soporte para generar un resumen con formato fijo.

### Cómo se ve en Claude Code

En Claude Code cada primitivo aparece de una forma distinta, y esa forma confirma quién lo controla:

- **Tools:** aparecen con el nombre `mcp__<servidor>__<tool>`, por ejemplo `mcp__tiendax-pedidos__lookup_order`. Claude las elige solo.
- **Resources:** se traen con una **@-mention** (mención con @), igual que un archivo: `@tiendax-pedidos:tiendax://politicas/devoluciones`. Aparecen en el autocompletado junto a los archivos. Los pide el usuario desde la aplicación.
- **Prompts:** se vuelven **slash commands** (comandos con barra): `/mcp__tiendax-pedidos__resumen_reclamo 12345`. También aparecen listados como `/tiendax-pedidos:resumen_reclamo (MCP)`; las dos formas funcionan. Los elige el usuario con `/`.

Un matiz: cuando el servidor ofrece resources, Claude Code además le da al modelo unas tools **propias del host** para listarlos y leerlos. Igual, para el examen el primitivo sigue siendo **application-controlled**: lo ofrece y lo maneja la aplicación, y esas tools no son del servidor.

### Para el examen

- **Tools = model · Resources = application · Prompts = user.** Si una opción dice "el modelo decide qué resources leer" o "el modelo invoca prompts", está mal.
- **Tools = acciones. Resources = contenido para leer.** La guía lo dice así: *"Resources for content catalogs, tools for actions"*.

### Cómo se une

El próximo tema muestra **para qué** usa la guía los resources: catálogos que le ahorran al agente un montón de llamadas.

---

## Tema 3 — Resources as content catalogs (resources como catálogos de contenido)

### Qué es

La guía le da a los resources un uso muy concreto: **exponer content catalogs** (catálogos de contenido), es decir, un índice de qué datos existen, para que el agente lo vea **sin tener que hacer exploratory tool calls** (llamadas exploratorias: llamadas que no resuelven la tarea, solo sirven para averiguar qué hay). Los ejemplos de la guía son tres: **issue summaries** (resúmenes de issues), **documentation hierarchies** (la estructura o índice de la documentación) y **database schemas** (esquemas de base de datos: qué tablas y columnas hay).

¿Qué problema resuelve? Sin catálogo, el agente no sabe qué existe, así que "tantea": llama `list_tables`, después `describe_table` para cada tabla, después recorre la documentación página por página. Son muchas llamadas solo para **descubrir** qué hay, y cada una gasta tiempo, tokens y turnos. Con un resource que ya trae el catálogo, el agente lo tiene en el contexto desde el principio y va directo a lo que necesita.

### Ejemplo

**Mal.** El agente de reportes de TiendaX tiene una sola tool, `run_query(sql)`. Para responder "¿cuántos pedidos se devolvieron en octubre?", primero ejecuta `SELECT table_name FROM information_schema...`, después mira las columnas de `orders`, después las de `returns`… Son seis llamadas antes de la consulta real.

**Bien.** El servidor expone el resource `tiendax://db/schema` con todas las tablas, columnas y relaciones, y la aplicación lo pone en el contexto. El agente ya sabe que existe `returns.created_at` y hace **una** consulta.

La tool `run_query` sigue existiendo, porque es la **acción**. El resource es el **mapa**.

### Para el examen

- Síntoma: *"el agente hace muchas llamadas exploratorias para descubrir qué datos/archivos/tablas hay"*.
- ✅ Respuesta: **exponer ese catálogo como un MCP resource**.
- ❌ No es: agregar una tool `list_everything` (sigue siendo una llamada exploratoria), ni pegar el catálogo a mano en el system prompt (queda desactualizado y no lo mantiene el servidor), ni subir `max_turns` (tapa el síntoma).

### Cómo se une

Con esto termina la Parte 1: ya sabés qué puede ofrecer un servidor. Ahora viene lo que más pesa en el examen: **cómo se configura**.

---

# Parte 2 — Configurar servidores MCP en Claude Code y en agentes

## Tema 4 — Scopes (alcances): `.mcp.json` del proyecto vs. `~/.claude.json` personal

### Qué es

Para que Claude Code use un servidor MCP, alguien tiene que escribir su configuración (cómo arrancarlo o a qué URL conectarse) en un archivo. Dónde está ese archivo decide su **scope** (alcance): si lo recibe todo el equipo o solo vos. Importa porque un servidor del equipo tiene que llegarle igual a todos sin pasos manuales, y uno que estás probando no tiene que molestar a nadie.

La guía lo resume en dos niveles. El **project-level** (nivel proyecto) es el archivo **`.mcp.json`** en la raíz del repositorio: se commitea, viaja por git, y todo el que clona el repo lo recibe; es para el **tooling compartido del equipo**. El **user-level** (nivel usuario) es **`~/.claude.json`**, un archivo en tu carpeta personal que no está en ningún repo; es para servidores **personales o experimentales**. Es la misma lógica que viste para los comandos en la pregunta de muestra Q4 de la guía: lo del proyecto (versionado) es para el equipo, lo de tu home es personal.

| Nivel | Archivo | Para qué | ¿Se comparte? |
|---|---|---|---|
| **Project-level (nivel proyecto)** | **`.mcp.json`** en la raíz del repositorio | **Tooling compartido del equipo** | **Sí**: se commitea y todos lo reciben |
| **User-level (nivel usuario)** | **`~/.claude.json`** en tu carpeta personal | Servidores **personales o experimentales** | **No**: es solo tuyo |

### El detalle de la documentación: en realidad son tres

La documentación de Claude Code divide el nivel personal en dos, así que tiene **tres** scopes, que se eligen con la opción `--scope`. El scope **`local`** es **el default** (el que se usa si no decís nada): se guarda en `~/.claude.json`, bajo la ruta de ese proyecto, y carga solo en ese proyecto. Sirve para servidores personales de un proyecto puntual, para experimentos o para servidores con credenciales que no querés en git. El scope **`user`** también se guarda en `~/.claude.json`, pero carga en **todos** tus proyectos; sirve para utilidades personales que usás en todos lados. Y **`project`** es el `.mcp.json` compartido.

| Scope | Dónde se guarda | Dónde carga | ¿Compartido? |
|---|---|---|---|
| `local` (**el default**) | `~/.claude.json`, bajo la ruta de ese proyecto | Solo en ese proyecto | No |
| `project` | `.mcp.json` en la raíz del proyecto | Ese proyecto | Sí, vía git |
| `user` | `~/.claude.json` | **Todos** tus proyectos | No |

Si el mismo nombre de servidor aparece en varios lugares, gana `local`, después `project`, después `user`. Se usa la entrada **entera** del que gana; no se mezclan campos de una y de otra. Y ojo con el nombre: el "local scope" de MCP vive en `~/.claude.json`, **no** en `.claude/settings.local.json`, aunque los dos digan "local".

> ⚠️ **En la documentación actual vas a leer otra cosa.** La documentación tiene tres scopes (`local`, `project` y `user`). **Para el examen:** la guía solo distingue dos niveles: **compartido → `.mcp.json`**; **personal o experimental → `~/.claude.json`**. Como `local` y `user` se guardan los dos en `~/.claude.json`, la respuesta "`~/.claude.json`" sirve para cualquier caso personal. No te van a pedir distinguir `local` de `user`, salvo que la pregunta lo diga explícitamente.

### Ejemplo

El servidor `github` lo usa todo el equipo de TiendaX, así que va en **`.mcp.json`** en la raíz del repo y se commitea. Cuando Ana clona el repo, ya lo tiene.

Lucas, en cambio, está probando un servidor experimental para generar diagramas y todavía no sabe si sirve. Lo pone en **`~/.claude.json`**: no molesta a nadie y no queda en git.

### Una consecuencia de seguridad

Como `.mcp.json` viene con el repositorio, cualquiera con acceso al repo podría meter un servidor malicioso, y ese servidor correría en la máquina de cada dev. Por eso Claude Code, en sesiones interactivas, **pide aprobación** antes de usar los servidores de un `.mcp.json` de proyecto. Esas decisiones se borran con `claude mcp reset-project-choices`.

En modo no interactivo (`claude -p`) y en el Agent SDK no hay nadie para aprobar, así que no hay prompt: los servidores del `.mcp.json` se cargan **sin preguntar**. Para bloquearlos existen `disabledMcpjsonServers` o `--strict-mcp-config`. El detalle de seguridad va en 2C.

### Para el examen

- "Todo el equipo tiene que tener el mismo servidor" → **`.mcp.json` en el repo**.
- "Un dev quiere probar un servidor sin afectar al equipo" → **`~/.claude.json`**.
- ❌ Poner el servidor del equipo en `~/.claude.json` y "mandarle a cada uno las instrucciones" → no es compartido ni versionado.

### Cómo se une

Si `.mcp.json` se commitea, ¿dónde van los tokens? No pueden ir en el archivo. Eso resuelve el próximo tema.

---

## Tema 5 — Environment variable expansion (expansión de variables de entorno): `${GITHUB_TOKEN}`

### Qué es

Muchos servidores necesitan una credencial: un token de GitHub, la contraseña de una base. Si la escribís en `.mcp.json`, queda commiteada y la ve todo el que tiene acceso al repo. La solución es la **environment variable expansion** (expansión de variables de entorno). Una **variable de entorno** es un valor con nombre que vive en la máquina de cada persona, fuera de cualquier archivo del repo (por ejemplo, `GITHUB_TOKEN`). En `.mcp.json` escribís **`${NOMBRE_VARIABLE}`** en lugar del valor, y Claude Code, al cargar la configuración, lo reemplaza por el valor que esa variable tiene en la máquina de quien lo está usando.

Así el archivo se puede commitear **sin secretos**, y cada dev usa su propio token. La guía usa exactamente este ejemplo, **`${GITHUB_TOKEN}`**, como la forma de manejar credenciales sin commitear secretos.

### Cómo se configura

```json
{
  "mcpServers": {
    "github": {
      "type": "http",
      "url": "https://api.githubcopilot.com/mcp/",
      "headers": { "Authorization": "Bearer ${GITHUB_TOKEN}" }
    },
    "tiendax-pedidos": {
      "command": "npx",
      "args": ["-y", "tiendax-pedidos-mcp"],
      "env": {
        "DB_URL": "${TIENDAX_DB_URL:-postgres://localhost:5432/tiendax}",
        "DB_PASSWORD": "${TIENDAX_DB_PASSWORD}"
      }
    }
  }
}
```

Hay dos formas de escribirla. **`${VAR}`** usa el valor de la variable tal cual. **`${VAR:-valor_por_defecto}`** usa el default si la variable no existe: en el ejemplo, si un dev no definió `TIENDAX_DB_URL`, se conecta a la base local. La expansión funciona en los campos `command`, `args`, `env`, `url` y `headers`.

¿Qué pasa si la variable no está definida y no tiene default? La configuración **igual carga**: Claude Code muestra un aviso en `claude mcp list` y en `/mcp`, y usa el texto literal `${VAR}`. O sea, no "explota" al arrancar; el servidor falla después, cuando intenta autenticarse con ese texto como si fuera el token.

### Ejemplo: mal y bien

**Mal:**
```json
"headers": { "Authorization": "Bearer ghp_A1b2C3d4E5..." }
```
Alguien dice "no pasa nada, el repo es privado". **Sí pasa.** Un repo privado no es un lugar seguro para secretos: lo ven todos los que tienen acceso, queda en el historial de git para siempre aunque después lo borres, y se copia en forks y backups.

**Bien:**
```json
"headers": { "Authorization": "Bearer ${GITHUB_TOKEN}" }
```
Cada dev exporta su `GITHUB_TOKEN` en su máquina, y el archivo se commitea tranquilo.

### Para el examen

- Servidor compartido que necesita credenciales → **`.mcp.json` + `${TOKEN}`**. Es literalmente la Skill 1 de la guía: *"Configuring shared MCP servers in project-scoped .mcp.json with environment variable expansion for authentication tokens"*.
- ❌ "Token en el archivo porque el repo es privado" → siempre mal.
- ❌ "Mover todo el servidor a `~/.claude.json` para no commitear el token" → resuelve el secreto pero **rompe lo compartido**: el equipo deja de recibir el servidor.

### Cómo se une

Ya sabés dónde va y cómo esconder los secretos. Ahora, cómo se agrega en la práctica.

---

## Tema 6 — Cómo se agrega un servidor: `claude mcp add` y el formato del archivo

### Qué es

Para agregar un servidor podés editar el JSON a mano o usar el comando **`claude mcp add`**, que escribe la entrada por vos en el archivo del scope que elijas. Esto es más "cómo se usa" que un concepto, pero conviene reconocerlo si aparece en una opción, sobre todo un detalle: si no indicás el scope, el servidor queda personal.

Hay dos tipos de servidor según dónde corre. Uno **remoto** está en una URL y Claude Code se conecta por **HTTP**. Uno **local** usa **stdio** (entrada y salida estándar): Claude Code arranca el servidor como un programa en tu máquina y le habla por la terminal (el detalle va en el Tema 14).

### Cómo se configura

**Servidor remoto (HTTP):**
```bash
claude mcp add --transport http --scope project github https://api.githubcopilot.com/mcp/
```

**Servidor local (stdio, un programa que corre en tu máquina):**
```bash
claude mcp add --transport stdio --env TIENDAX_DB_URL=postgres://... tiendax-pedidos -- npx -y tiendax-pedidos-mcp
```

Las opciones de Claude (`--transport`, `--scope`, `--env`, `--header`) van **antes** del nombre del servidor. El **`--`** separa esas opciones del comando que arranca el servidor: todo lo que va después de `--` se le pasa al servidor tal cual, para que Claude no lo confunda con sus propias opciones. Si no ponés `--scope`, el servidor queda en **`local`** (personal, solo ese proyecto). Otros comandos útiles son `claude mcp list`, `claude mcp get <nombre>` y `claude mcp remove <nombre>`; dentro de una sesión, **`/mcp`** muestra el estado de cada servidor y permite autenticarse.

En el JSON, cada tipo usa campos distintos. Un servidor local (stdio) usa `command`, `args` y `env`. Uno remoto usa `type` (`"http"`), `url` y `headers`. Por eso **una entrada con `url` pero sin `type` es un error de configuración**: sin `type`, Claude Code la interpreta como stdio. Y el transporte **SSE** (**Server-Sent Events**, eventos enviados por el servidor) está **deprecado**: para servidores remotos se usa HTTP.

| Tipo | Campos en el JSON | Flag |
|---|---|---|
| Local (stdio) | `command`, `args`, `env` | `--transport stdio` … `-- <comando>` |
| Remoto (HTTP) | `type: "http"`, `url`, `headers` | `--transport http <url>` |

### Ejemplo

Ana se suma al equipo de TiendaX. Clona el repo y abre Claude Code: le aparece el pedido de aprobación de `github` y `tiendax-pedidos`, que vienen en el `.mcp.json`. Aprueba, exporta su `GITHUB_TOKEN` y listo. Después quiere probar un servidor de diagramas solo para ella y escribe `claude mcp add diagramas -- npx -y diagramas-mcp`; como no puso `--scope`, queda personal. Con `claude mcp list` ve los tres servidores y su estado.

### Para el examen

- No memorices cada flag. Quedate con: **`--scope project` → `.mcp.json`**; sin scope → personal; `--` antes del comando del servidor; `url` sin `type` = error.

### Cómo se une

Ahora que tenés varios servidores configurados, ¿cómo los ve el agente? ¿Hay que elegir uno?

---

## Tema 7 — Varios servidores a la vez: todas las tools disponibles simultáneamente

### Qué es

Cuando Claude Code arranca, se conecta a **todos** los servidores configurados, le pregunta a cada uno qué tools tiene y junta todo en **una sola lista**. El agente ve al mismo tiempo las tools de `github`, de `jira` y de `tiendax-pedidos`, y en una misma tarea puede usar una de cada una. Por eso **no hay que "elegir un servidor" ni construir un router entre servidores**: el host ya hace ese trabajo. La guía lo dice así: las tools de todos los servidores MCP configurados se descubren al conectarse y quedan disponibles simultáneamente para el agente.

¿Y si dos servidores tienen una tool con el mismo nombre? Para que no choquen, Claude Code les pone un prefijo con el nombre del servidor: `mcp__github__search_issues` y `mcp__jira__search_issues` son tools distintas, aunque las dos se llamen `search_issues` en su servidor.

📘 **Curso:** Jacob lo explica desde el lado del cliente: un cliente puede tener conexiones a varios servidores al mismo tiempo, cada uno registrado con un **nombre único**; las llamadas se rutean al servidor dueño de cada tool, y los **namespace prefixes** (prefijos de espacio de nombres) evitan colisiones.

> ⚠️ **En la documentación actual vas a leer otra cosa.** Hoy Claude Code tiene **tool search** (búsqueda de tools) activado por defecto: al arrancar carga solo los **nombres** de las tools y trae la definición completa cuando la necesita. Eso ahorra contexto cuando hay muchísimas tools.
>
> **Para el examen:** la versión de la guía. **Todas las tools de todos los servidores están disponibles a la vez**, descubiertas al conectar. Si una opción propone "conectar un servidor por vez según la tarea" o "un agente router que decida a qué servidor ir", está mal.

### Ejemplo

Ana le pide a Claude Code: "Tomá el ticket TX-88 de Jira, buscá el issue relacionado en GitHub y fijate si el pedido 12345 de la base está afectado". En la misma sesión, Claude usa `mcp__jira__get_issue`, `mcp__github__search_issues` y `mcp__tiendax-pedidos__lookup_order`, sin ninguna configuración extra.

### Para el examen

- Varios servidores configurados → **sus tools conviven, todas disponibles a la vez**.
- Mismo nombre de tool en dos servidores → no hay conflicto: el prefijo `mcp__<servidor>__` las separa.
- Recordá lo de 2A: **muchas tools juntas pueden bajar la calidad de la elección**. Que estén todas disponibles no significa que convenga darle 40 tools a un subagent: el scoping de 2A sigue valiendo.

### Cómo se une

Si el agente tiene muchas tools disponibles a la vez —las de MCP y las que ya trae Claude Code— tiene que **elegir**. Y ahí aparece el problema del próximo tema.

---

## Tema 8 — Que el agente use la tool MCP y no Grep: mejorar la descripción

### Qué es

Claude Code ya trae **built-in tools** (tools incorporadas): `Read`, `Grep`, `Glob`, `Bash`… Son genéricas y Claude las conoce muy bien. Si agregás una tool MCP más potente pero con una descripción pobre, el agente **sigue prefiriendo la built-in**: por ejemplo, busca con `Grep` en los archivos del repo en vez de usar tu tool MCP que consulta la fuente real. No es que Claude "desconfíe" de tu tool; es que la descripción no le da ningún motivo para elegirla.

Lo que pide la guía es **mejorar la descripción de la tool MCP para explicar en detalle sus capacidades y lo que devuelve**, así el agente entiende por qué es mejor que la alternativa genérica. Es el mismo principio de 2A (Temas 1 y 2): **Claude elige leyendo descripciones**, así que, si la descripción no dice qué tiene de especial la tool, no hay razón para preferirla.

### Ejemplo: mal y bien

**Mal.** El servidor `tiendax-catalogo` tiene:
```
search_products: "Searches products."
```
Cuando Lucas pregunta "¿qué zapatillas talle 42 hay en stock?", Claude hace `Grep "zapatilla"` sobre los archivos JSON del repo. Encuentra **fixtures** (datos de prueba) viejos y responde mal.

**Bien:**
```
search_products: "Searches the LIVE TiendaX product catalog database (not repository
files). Supports filters by category, size, color, price range and in_stock. Returns
JSON with sku, name, current price, stock per warehouse and variants. Use this for any
question about current products, prices or stock; repository files only contain old
test fixtures."
```
Ahora Claude sabe que la tool consulta datos **en vivo**, qué filtros acepta, qué devuelve y por qué no conviene buscar en archivos.

### Para el examen

- Síntoma: *"el agente usa Grep/Read en vez de la tool MCP que hace eso mejor"*.
- ✅ **Mejorar la descripción de la tool MCP** (capacidades y salidas en detalle).
- ❌ **Sacarle Grep al agente:** Grep sirve para muchas otras cosas; romperías otros usos.
- ❌ **Agregar al system prompt "usá siempre search_products"**: no ataca la causa, y en 2A viste que las reglas del prompt atadas a palabras pueden traer otros problemas.
- ❌ **Agregar un hook que bloquee Grep** siempre: es otra forma de sacarle Grep; rompe usos legítimos y no arregla la descripción.

### Cómo se une

Hasta acá diste por hecho que tenías un servidor. Pero ¿lo construís vos o usás uno que ya existe?

---

## Tema 9 — Community servers vs. custom servers (servidores de la comunidad vs. propios)

### Qué es

Para sistemas conocidos (Jira, GitHub, Slack, Postgres) ya existen **community MCP servers** (servidores MCP de la comunidad): servidores mantenidos, probados y actualizados cuando cambia la API del sistema. Programar uno propio para lo mismo es trabajo extra, más código para mantener y más bugs, sin ganar nada. Por eso la guía pide: **para integraciones estándar (por ejemplo, Jira), elegir un servidor de la comunidad existente antes que programar uno propio**.

Los **custom servers** (servidores propios) quedan para lo que nadie más puede haber hecho: **workflows específicos del equipo**, como las reglas de negocio de tu empresa.

Igual hay que **confiar** en un servidor antes de conectarlo. La documentación advierte que un servidor que trae contenido externo puede exponerte a **prompt injection** (inyección de instrucciones: texto malicioso escondido en el contenido que intenta darle órdenes a Claude). La seguridad se ve en 2C.

### Ejemplo

TiendaX quiere que Claude Code lea tickets de **Jira**. Jira es un sistema estándar y ya hay un servidor para eso, así que usa uno existente. ✅

TiendaX también quiere que Claude consulte **su base de pedidos con sus reglas de negocio** (qué pedidos se pueden reembolsar, en qué estados). Para eso no hay servidor de la comunidad, así que programa `tiendax-pedidos`. ✅

### Para el examen

- "Integrar Jira/GitHub/Slack" → **primero evaluar el servidor de la comunidad**.
- "Exponer un proceso propio del equipo" → **servidor custom**.
- ❌ "Escribir un servidor custom para Jira para tener control total" → tienta, pero es más trabajo sin necesidad.
- Igual hay que **confiar** en el servidor antes de conectarlo (prompt injection → 2C).

### Cómo se une

Todo lo anterior fue en Claude Code. Los agentes que armás con el Agent SDK (como SoporteBot) también usan servidores MCP. Veamos qué cambia.

---

## Tema 10 — MCP en el Agent SDK: `mcpServers` y `allowedTools`

### Qué es

En el Agent SDK los servidores se configuran en código: se pasan con la opción **`mcpServers`** (TypeScript) o **`mcp_servers`** (Python), o se cargan desde el `.mcp.json` del proyecto. Las tools aparecen con el mismo formato de nombre que en Claude Code: `mcp__<servidor>__<tool>`.

Lo importante es que **las tools MCP necesitan permiso explícito**. Sin permiso, Claude **ve** que existen pero **no puede llamarlas**. Es una protección: conectar un servidor no debería darle al agente, automáticamente, el poder de ejecutar todo lo que el servidor ofrece. El permiso se da con **`allowedTools`**, y se pueden usar comodines para habilitar todas las tools de un servidor:

```typescript
const options = {
  mcpServers: {
    pedidos: { command: "npx", args: ["-y", "tiendax-pedidos-mcp"],
               env: { DB_PASSWORD: process.env.TIENDAX_DB_PASSWORD } }
  },
  allowedTools: ["mcp__pedidos__*"]   // todas las tools del servidor "pedidos"
};
```

Tres detalles más. El modo `acceptEdits` **no** aprueba tools MCP, solo ediciones de archivos; `bypassPermissions` sí las aprueba, pero apaga casi todas las protecciones, así que la documentación recomienda **`allowedTools`**. Si un servidor no se puede conectar, el SDK **no tira excepción**: el estado aparece en el mensaje inicial (`system` / `init`) como `connected`, `failed`, `needs-auth`, etc., y conviene revisarlo. Y también podés crear un servidor **dentro de tu propia aplicación** (**in-process**, en el mismo proceso), sin un programa aparte, con `createSdkMcpServer` (TS) o `create_sdk_mcp_server` (Python).

### Ejemplo

SoporteBot tiene configurado el servidor `pedidos`, pero cuando Juan pregunta por su pedido, Claude responde "no tengo forma de consultar pedidos". Los logs muestran que la tool está listada pero nunca se llama. La causa: faltaba `allowedTools: ["mcp__pedidos__*"]`.

### Para el examen

- Esto sale de la documentación, no de la guía. Es un detalle práctico, no el centro de 2.4.
- Tools MCP visibles pero nunca usadas en el Agent SDK → mirá **`allowedTools`**.
- Conecta con 1C: `allowedTools` también es la herramienta del **least privilege** (cada subagent, solo las tools de su rol).

### Cómo se une

Con esto cerrás la parte de **configuración**, que es la que más pesa. La Parte 3 es lo que enseña el curso: cómo se construye un servidor por dentro.

---

# Parte 3 — Construir y conectar un servidor (lo que enseña el curso)

> Esta parte sale sobre todo del curso. La guía oficial **no pregunta por la API de Python** ni por los internals del protocolo. Leela para entender cómo funciona; para el examen, quedate con las ideas de cada "Para el examen".

## Tema 11 — Un servidor MCP en Python: tools con `@mcp.tool()`

### Qué es

Con el SDK oficial de Python, un servidor se arma en tres pasos: **crear** el servidor, **registrar** tools, resources y prompts con **decoradores** (las líneas con `@` que se ponen arriba de una función para "anotarla") y **arrancarlo**. La gracia es que no tenés que escribir el JSON de la tool a mano: el SDK lo saca de la propia función.

### Cómo se configura

```python
from mcp.server.mcpserver import MCPServer
# ToolError viene del SDK (la ruta exacta del import depende de la versión)

mcp = MCPServer("tiendax-pedidos")

@mcp.tool()
async def lookup_order(order_id: str, include_items: bool = False) -> dict:
    """Return the status, dates and total of one TiendaX order by its ID (format: 5 digits).
    Read-only: does not modify the order. Returns an error if the order does not exist."""
    order = await db.get_order(order_id, include_items)
    if order is None:
        raise ToolError(f"Order {order_id} not found")
    return order

mcp.run(transport="stdio")
```

Esto es lo que el SDK hace solo con esa función. El **nombre de la función** pasa a ser el nombre de la tool (`lookup_order`). El **docstring** (el texto entre `"""` debajo de la función) pasa a ser la **description** que lee el modelo, así que todo lo de 2A sobre descripciones se aplica acá. Los **type hints** (anotaciones de tipo, como `order_id: str`) generan el **`inputSchema`** (esquema de entrada). 📘 Y, según el curso, los parámetros **sin valor por defecto** quedan como **required** (`order_id`), y los que tienen default quedan opcionales (`include_items`).

| En el código | En la tool MCP |
|---|---|
| Nombre de la función | Nombre de la tool |
| Docstring | `description` |
| Type hints | `inputSchema` |
| Parámetro sin default | Required |

📘 **Curso:** Jacob agrega varias reglas prácticas:
- **Text vs. structured result** (resultado de texto vs. estructurado): devolvé un **string** cuando el modelo tiene que leer y resumir, y un **dict** (JSON) cuando otro código o tool va a procesar el resultado.
- **Errores:** para avisar que la tool falló, **lanzá una excepción** (`raise ToolError(...)`). El SDK la convierte en un resultado con **`isError: true`**. **Un dict devuelto NO es un error**, aunque diga `{"error": "..."}`: llega como contenido normal. (Es el mismo `isError` de 2A.)
- **Reglas para la descripción:** ser específico sobre qué devuelve, declarar los **side effects** (efectos secundarios: si escribe, borra o envía algo) y listar **límites** (paginación, **rate limits** —límites de frecuencia—, tamaños).
- **Registrar todo antes de `run()`** (el curso dice que lo que se registra después no llega al cliente) y **no bloquear el event loop** (el bucle que atiende todas las tareas async) con operaciones síncronas lentas.
- **Lifespan** (ciclo de vida): un `@asynccontextmanager` que se pasa con `MCPServer("tiendax-pedidos", lifespan=lifespan)`. Lo que va antes del `yield` corre al arrancar (abrir la conexión a la base); lo que va en el `finally` corre al apagar (cerrarla).
- **MCP Inspector:** una herramienta (`npx @modelcontextprotocol/inspector`) para probar cada tool sin escribir un cliente.

Una regla que sí es de la documentación: en un servidor **stdio**, **nunca escribas en stdout** (por ejemplo, con `print()`). En stdio, stdout es el canal por donde viajan los mensajes del protocolo, así que cualquier texto suelto los corrompe. Los logs van a stderr.

> ⚠️ **En el curso vas a escuchar otra cosa.** Jacob a veces usa el nombre **`FastMCP`** y dice que lo registrado después de `run()` nunca llega al cliente. **Para el examen: no se evalúa ninguna de las dos.** En la versión 2 del SDK oficial de Python esa clase se llama **`MCPServer`** (los decoradores no cambiaron), y lo de `run()` es una simplificación: la especificación permite avisar cambios con **`listChanged`** (Tema 14).

### Ejemplo

La primera versión de `lookup_order` hacía `return {"error": "not found"}` cuando el pedido no existía. SoporteBot recibía eso como un resultado **exitoso** y le decía a Juan "tu pedido está en estado: error". Al cambiarlo por `raise ToolError(...)`, el resultado llega con `isError: true` y Claude entiende que la consulta falló.

### Para el examen

- **Docstring = description**, y la description es lo que Claude usa para elegir (2A).
- Falla de una tool MCP → resultado con **`isError: true`** (y, como viste en 2A, con categoría y si es reintentable).

### Cómo se une

Las tools son el primitivo que ya conocías. Ahora los otros dos, empezando por los resources.

---

## Tema 12 — Resources en detalle: URI, templates y subscriptions

### Qué es

Un **resource** es un contenido identificado por una **URI** (su dirección). Según la especificación, lo único obligatorio es **`uri`** y **`name`**; `description`, `mimeType` (el tipo de contenido, como `application/json`) y `size` son opcionales. El contenido puede ser texto o binario. En Python se registra con un decorador, igual que una tool:

```python
@mcp.resource("tiendax://db/schema", mime_type="application/json")
def db_schema() -> str:
    """Tables, columns and relations of the TiendaX orders database."""
    return json.dumps(load_schema())
```

Dos mecanismos de la especificación resuelven casos frecuentes. Cuando hay demasiados recursos para listarlos uno por uno (un recurso por pedido, por ejemplo), se usan **resource templates** (plantillas de recurso): una URI con parámetros, como `file:///{path}` o `tiendax://pedidos/{order_id}`. Se descubren con `resources/templates/list`, aparte de `resources/list`. Y cuando un recurso cambia y el cliente necesita enterarse, se usan **subscriptions** (suscripciones): el cliente se suscribe a una URI (`resources/subscribe`), el servidor le avisa cuando cambia (`notifications/resources/updated`) y el cliente la vuelve a leer. Así no hace falta **polling** (consultar una y otra vez por si cambió).

📘 **Curso:** Jacob agrega dos criterios de diseño:
- **Static vs. dynamic resources** (estáticos vs. dinámicos): uno estático no cambia (un archivo de configuración, una política) y se puede cachear; uno dinámico se genera en cada pedido (el resultado de una consulta) y no se cachea sin cuidado.
- **Diseño de URIs:** usar un prefijo por tipo de dato (`file://`, `db://`, `config://`), mantener las rutas **estables** (cambiarlas rompe a los clientes) y **no meter datos volátiles** como tokens de sesión en la URI.

> ⚠️ **En el curso vas a escuchar otra cosa.** El companion dice que un resource "requiere" URI, MIME type y un handler de lectura; las slides, en cambio, dicen que solo URI y nombre son obligatorios. **Para el examen: `mimeType` es opcional**, como dicen las slides y la especificación.

### Ejemplo

`tiendax-pedidos` expone tres cosas. `tiendax://politicas/devoluciones` es **estático**: cambia una vez por año, así que se puede cachear. `tiendax://db/schema` es el catálogo del Tema 3: la aplicación lo inyecta y se suscribe para enterarse si se agrega una tabla. Y el template `tiendax://pedidos/{order_id}` es **dinámico**: Ana escribe `@tiendax-pedidos:tiendax://pedidos/12345` en Claude Code y el detalle de ese pedido entra al contexto.

### Para el examen

- Lo que importa no es la sintaxis, sino **para qué**: resources = **catálogos de contenido** para que el agente vea qué hay sin llamadas exploratorias (Tema 3), y **los controla la aplicación**, no el modelo (Tema 2).

### Cómo se une

Falta el tercer primitivo: el que elige el usuario.

---

## Tema 13 — Prompts en detalle: argumentos, `prompts/list` y `prompts/get`

### Qué es

Un **prompt** MCP es una **plantilla con argumentos** que vive en el servidor y que el **usuario elige explícitamente**. Tiene `name`, una `description` opcional y `arguments`, cada uno con nombre, descripción y si es obligatorio. El cliente descubre qué prompts hay con **`prompts/list`** y pide uno ya armado con **`prompts/get`**, mandando el nombre y los valores de los argumentos. El servidor devuelve los mensajes listos para meter en la conversación.

```python
@mcp.prompt()
def resumen_reclamo(order_id: str, tono: str = "formal") -> str:
    """Structured summary of a customer complaint about one order."""
    return (f"Resumí el reclamo del pedido {order_id} en tono {tono}. "
            "Incluí: problema, fecha, monto en juego y acción recomendada.")
```

### Ejemplo

Lucía, del equipo de soporte humano, escribe en Claude Code `/mcp__tiendax-pedidos__resumen_reclamo 12345` (o lo elige del menú como `/tiendax-pedidos:resumen_reclamo (MCP)`). El texto armado se inyecta en la conversación y Claude genera el resumen siempre con la misma estructura. Si mañana el equipo agrega "canal de contacto" a la plantilla, se cambia una vez en el servidor y todos lo reciben.

📘 **Curso:** Jacob agrega para qué sirven y cómo cuidarlos:
- **Para qué sirven:** dar a todos el **mismo set de instrucciones probado** (consistencia), actualizarlo una vez en el servidor y que llegue a todos (mantenimiento) y poder revisarlo o aprobarlo (auditoría, cumplimiento).
- **Versionado:** versión en el nombre (`review-v2`), versión como argumento o una marca de "deprecated".
- **Argumentos:** pocos obligatorios, defaults razonables y tipados. (Es una recomendación del curso; no figura en la guía ni en la especificación.)

### Para el examen

- Prompt MCP = **plantilla que elige el usuario**. Si una opción dice que el modelo decide usar un prompt por su cuenta, está mal.

### Cómo se une

Ya viste qué ofrece un servidor. El último tema mira el otro lado: cómo se conecta el cliente.

---

## Tema 14 — El cliente: transportes, conexión, discovery y errores

### Qué es

**Transportes (cómo viajan los mensajes).** Cliente y servidor se hablan con mensajes **JSON-RPC** (un formato estándar de pedido y respuesta en JSON). Lo que cambia es el canal por donde viajan, y eso define dónde corre el servidor y cuántos lo pueden usar. Con **stdio** (entrada/salida estándar), el cliente arranca el servidor como un **proceso hijo en tu máquina** (un programa que lanza y controla él mismo) y le habla por stdin/stdout: es local, de un solo usuario y sin red, ideal para herramientas en la compu del dev. Con **Streamable HTTP** (HTTP con streaming), el servidor es un **servicio remoto** en una URL que atiende a muchos clientes a la vez: es para infraestructura compartida. El detalle de transportes y producción va en 2C.

**Conexión y discovery (descubrimiento).** Antes de usar un servidor, el cliente tiene que averiguar qué ofrece. El curso y la especificación 2025-06-18 lo describen con un **handshake** (saludo inicial) en tres pasos: el cliente manda `initialize` con la versión del protocolo, el servidor responde con su versión y sus **capabilities** (capacidades: qué funciones soporta), y el cliente confirma con `initialized`. Después el cliente pregunta qué hay: `tools/list`, `resources/list`, `prompts/list`.

> ⚠️ **En el curso vas a escuchar otra cosa.** Jacob explica el handshake `initialize` / `initialized` como la forma de conectarse. Eso es exacto para la especificación 2025-06-18, pero **la especificación vigente (2026-07-28) eliminó ese handshake** e hizo MCP *stateless* (sin estado), con un nuevo `server/discover`. **Para el examen: quedate con la idea común a las dos versiones**: al conectar, el cliente descubre qué tools, resources y prompts ofrece cada servidor (eso dice la guía en K3). La guía no evalúa internals del protocolo.

**Catálogo actualizado.** Las tools de un servidor pueden cambiar mientras la sesión está abierta. Si el servidor declara la capability **`listChanged`**, avisa con una notificación cuando cambian sus tools o resources, y el cliente las vuelve a listar. En sesión interactiva, Claude Code lo hace sin reconectar; en `claude -p` y en el Agent SDK solo refresca la lista de tools. 📘 **Curso:** el protocolo no tiene mensaje de cierre; la conexión se termina cerrando el transporte (stdin o la conexión HTTP).

**Dos tipos de error del lado del cliente** (ya lo viste en 2A, Tema 7). No es lo mismo que la tool falle a que el pedido esté mal armado. Un **error de ejecución de la tool** (el pedido no existe, la base no responde) llega como resultado con **`isError: true`**: el modelo lo ve y puede decidir qué hacer. Un **error de protocolo** (tool desconocida, argumentos inválidos) llega como error JSON-RPC, porque el pedido ni siquiera se pudo procesar. 📘 En el SDK de Python aparece como excepción **`McpError`** y se maneja con try/except.

| Error | Ejemplo | Cómo llega |
|---|---|---|
| Ejecución de la tool | Pedido inexistente | Resultado con `isError: true` (lo ve el modelo) |
| Protocolo | Tool que no existe, argumentos inválidos | Error JSON-RPC (`McpError` en Python) |

### Ejemplo

Claude Code arranca `tiendax-pedidos` por **stdio** como proceso hijo y se conecta por **HTTP** a `github`. Llama `lookup_order("99999")` y recibe `isError: true` ("Order not found"): Claude lo ve y le avisa a Juan. Si el cliente pidiera `lookup_ordr` (una tool que no existe), recibiría un **error JSON-RPC** de protocolo, no un `isError`.

### Para el examen

- stdio = local, proceso hijo · Streamable HTTP = remoto, compartido.
- Al conectar se **descubren** las capacidades de **cada** servidor.
- `isError` (falla de la tool) ≠ error de protocolo.

### Cómo se une

Cierra el capítulo: ahora entendés el recorrido completo, desde que un servidor publica una tool hasta que Claude Code la descubre, la elige por su descripción y recibe el resultado o el `isError`.

---

## Cómo se une todo

**MCP** es el estándar para publicar tools y datos una vez y usarlos desde cualquier host (Tema 1). Un servidor ofrece tres primitivos que se distinguen por quién los controla: las **tools** las elige el modelo, los **resources** la aplicación y los **prompts** el usuario (Tema 2). El uso que más le importa a la guía es el de los **resources** como **catálogos**, que le evitan al agente las llamadas exploratorias (Tema 3).

Para configurar, el servidor del equipo va en **`.mcp.json`** en el repo, y el personal o experimental en **`~/.claude.json`** (Tema 4). Los secretos van con **`${VAR}`**, nunca literales, aunque el repo sea privado (Tema 5). `claude mcp add` agrega servidores con `--scope`, y una entrada con `url` sin `type` es un error (Tema 6). Las tools de **todos** los servidores se descubren al conectar y están **disponibles a la vez**, sin router (Tema 7). Si el agente prefiere **Grep**, se **mejora la descripción** de la tool MCP (Tema 8). Para una integración estándar se usa un **servidor de la comunidad**, y para un flujo propio uno **custom** (Tema 9). En el Agent SDK, las tools MCP necesitan **`allowedTools`** (Tema 10).

Por dentro, el docstring se convierte en la description, los type hints en el `inputSchema` y una falla en `isError` (Temas 11–13). El cliente se conecta por **stdio** o **HTTP** y descubre las capacidades de cada servidor (Tema 14).

## Lo que viene

En **2C** se completa la tarea 2.4 y el módulo 2: los transportes en producción, la seguridad de los servidores (aprobaciones, prompt injection, credenciales) y las **built-in tools** de Claude Code (`Read`, `Write`, `Edit`, `Bash`, `Grep`, `Glob`): cuándo usar cada una. Ahí vuelve el caso de **Grep vs. tool MCP** desde el otro lado.

---

## Las trampas del examen

Cada trampa tiene el mismo orden: la situación, **qué elegir en el examen (✅)**, las opciones que tientan (❌) con por qué tientan y por qué están mal, y una regla para recordar.

### Grupo: Dónde va la configuración

#### Trampa 1 · El servidor que tiene que usar todo el equipo

**La situación.** El equipo de TiendaX quiere que todos los devs tengan el servidor de GitHub configurado igual en Claude Code (Tema 4).

**✅ En el examen elegí:** configurarlo en **`.mcp.json`** en la raíz del repositorio y commitearlo.

**❌ Las que tientan:**

❌ **"Que cada dev lo agregue en su `~/.claude.json` siguiendo un README".**
- *Tienta porque:* funciona y no toca el repo.
- *Está mal porque:* no es compartido ni versionado; cada uno puede terminar con una configuración distinta.

❌ **"Agregarlo con `claude mcp add` sin scope y avisar al equipo".**
- *Tienta porque:* es el comando oficial.
- *Está mal porque:* sin `--scope` queda en `local`: solo vos lo tenés.

> 🧠 **Para recordar:** compartido = `.mcp.json` en el repo.

#### Trampa 2 · "El repo es privado, el token puede ir en el archivo"

**La situación.** El `.mcp.json` compartido necesita un token de GitHub (Tema 5).

**✅ En el examen elegí:** **`"Authorization": "Bearer ${GITHUB_TOKEN}"`** y que cada dev tenga la variable de entorno.

**❌ Las que tientan:**

❌ **"Dejar el token literal porque el repo es privado".**
- *Tienta porque:* parece que nadie de afuera lo ve.
- *Está mal porque:* un repo privado no es un lugar para secretos: queda en el historial, lo ven todos los que tienen acceso y viaja en forks y backups.

❌ **"Mover el servidor a `~/.claude.json` de cada uno para no commitear el token".**
- *Tienta porque:* el secreto deja de estar en git.
- *Está mal porque:* rompe lo compartido. La guía resuelve las dos cosas juntas: `.mcp.json` **+** expansión de variables.

> 🧠 **Para recordar:** compartido y con secreto = `.mcp.json` + `${VAR}`.

#### Trampa 3 · El servidor experimental

**La situación.** Un dev quiere probar un servidor nuevo sin afectar a nadie (Tema 4).

**✅ En el examen elegí:** **`~/.claude.json`** (user/local scope).

**❌ Las que tientan:**

❌ **"Agregarlo a `.mcp.json` en una rama aparte".**
- *Tienta porque:* no toca `main`.
- *Está mal porque:* sigue siendo configuración de proyecto pensada para compartir; para experimentar en tu máquina está `~/.claude.json`.

❌ **"Ponerlo en `.claude/settings.local.json`".**
- *Tienta porque:* "local" suena a personal.
- *Está mal porque:* el local scope de MCP vive en `~/.claude.json`, no en ese archivo.

> 🧠 **Para recordar:** personal o experimental = `~/.claude.json`.

### Grupo: El agente no usa lo que debería

#### Trampa 4 · El agente usa Grep en vez de la tool MCP

**La situación.** Hay una tool MCP `search_products` que consulta el catálogo en vivo, pero el agente busca con Grep en archivos del repo (Tema 8).

**✅ En el examen elegí:** **mejorar la descripción de la tool MCP**, explicando en detalle qué puede hacer y qué devuelve.

**❌ Las que tientan:**

❌ **"Sacarle Grep al agente".**
- *Tienta porque:* elimina la alternativa.
- *Está mal porque:* Grep sirve para muchas otras tareas; rompés usos legítimos y no atacás la causa.

❌ **"Agregar al system prompt: 'para productos usá siempre search_products'".**
- *Tienta porque:* parece directo.
- *Está mal porque:* la causa es la descripción pobre; las reglas atadas a palabras clave en el prompt traen otros problemas (2A, Tema 4).

❌ **"Un hook PreToolUse que bloquee Grep cuando la consulta habla de productos".**
- *Tienta porque:* es programático, y en 1D viste que lo programático es confiable.
- *Está mal porque:* lo programático es para reglas de negocio críticas; acá el problema es que la descripción no explica la tool. Además el filtro por palabras falla con frases distintas.

> 🧠 **Para recordar:** si eligen la tool equivocada, mirá la descripción. También con MCP.

#### Trampa 5 · Muchas llamadas solo para descubrir qué hay

**La situación.** El agente hace 6–8 llamadas a `list_tables` / `describe_table` antes de cada consulta real (Tema 3).

**✅ En el examen elegí:** **exponer el esquema de la base como un MCP resource** (catálogo).

**❌ Las que tientan:**

❌ **"Subir `max_turns` para que le alcancen las iteraciones".**
- *Tienta porque:* el agente a veces se queda sin turnos.
- *Está mal porque:* tapa el síntoma; las llamadas exploratorias siguen ahí.

❌ **"Crear una tool `list_all_data` que devuelva todo".**
- *Tienta porque:* una llamada en vez de seis.
- *Está mal porque:* sigue siendo una llamada exploratoria a una tool; para catálogos la guía dice **resources** ("resources for content catalogs, tools for actions").

> 🧠 **Para recordar:** catálogo = resource; acción = tool.

#### Trampa 6 · ¿Hay que elegir qué servidor usar?

**La situación.** Claude Code tiene configurados GitHub, Jira y `tiendax-pedidos`. Una tarea necesita los tres (Tema 7).

**✅ En el examen elegí:** **no hace falta nada**: las tools de todos los servidores se descubren al conectar y están disponibles a la vez.

**❌ Las que tientan:**

❌ **"Un agente router que decida a qué servidor mandar cada pedido".**
- *Tienta porque:* parece organizado.
- *Está mal porque:* es sobreingeniería; el host ya junta todas las tools en una lista.

❌ **"Conectar un servidor por vez según la etapa de la tarea".**
- *Tienta porque:* ahorraría contexto.
- *Está mal porque:* contradice la guía (disponibles simultáneamente) y obliga a reconectar.

> 🧠 **Para recordar:** varios servidores = todas sus tools juntas.

#### Trampa 7 · La tool MCP existe pero nunca se llama (Agent SDK)

**La situación.** SoporteBot tiene `mcpServers` configurado, la tool aparece en la lista, pero Claude dice que no puede consultar pedidos (Tema 10).

**✅ En el examen elegí:** **agregar la tool a `allowedTools`** (por ejemplo `mcp__pedidos__*`).

**❌ Las que tientan:**

❌ **"Pasar a `permissionMode: 'acceptEdits'`".**
- *Tienta porque:* parece "aprobar automáticamente".
- *Está mal porque:* `acceptEdits` no aprueba tools MCP.

❌ **"Reescribir la descripción de la tool".**
- *Tienta porque:* es la respuesta típica de 2A.
- *Está mal porque:* acá Claude **no puede** llamarla (permiso), no es que elija mal.

> 🧠 **Para recordar:** visible pero bloqueada = falta permiso (`allowedTools`).

### Grupo: Qué construir

#### Trampa 8 · Integrar Jira

**La situación.** El equipo quiere que Claude Code lea y comente tickets de Jira (Tema 9).

**✅ En el examen elegí:** **usar un servidor MCP de la comunidad existente para Jira**.

**❌ Las que tientan:**

❌ **"Programar un servidor custom para tener control total".**
- *Tienta porque:* control y personalización suenan bien.
- *Está mal porque:* Jira es una integración estándar; custom es trabajo y mantenimiento extra sin beneficio. Custom se reserva para flujos propios del equipo.

❌ **"Que Claude llame la API de Jira con `Bash` y `curl`".**
- *Tienta porque:* no hay que instalar nada.
- *Está mal porque:* no hay tools con descripciones ni manejo de errores estructurado; es frágil.

> 🧠 **Para recordar:** estándar → comunidad; propio del equipo → custom.

### Grupo: Primitivos y errores

#### Trampa 9 · ¿Quién decide usar un resource?

**La situación.** Una opción dice que "Claude decide qué resource leer durante su razonamiento, igual que una tool" (Tema 2).

**✅ En el examen elegí:** la que diga que **los resources los controla la aplicación** (el host elige qué inyectar; el modelo lee).

**❌ Las que tientan:**

❌ **"Los resources son tools de solo lectura que el modelo llama".**
- *Tienta porque:* las dos traen datos.
- *Está mal porque:* las tools las controla el modelo; los resources, la aplicación. (Aunque Claude Code le dé al modelo tools del host para leer resources, el primitivo sigue siendo application-controlled.)

❌ **"Los prompts MCP los elige el modelo según la tarea".**
- *Tienta porque:* "prompt" suena a algo del modelo.
- *Está mal porque:* los prompts MCP los elige el **usuario**.

> 🧠 **Para recordar:** tools = modelo · resources = aplicación · prompts = usuario.

#### Trampa 10 · El error que no es error

**La situación.** Una tool MCP en Python hace `return {"error": "Order not found"}` y el agente sigue como si todo estuviera bien (Tema 11).

**✅ En el examen elegí:** **marcar la falla con `isError: true`** (en Python, `raise ToolError(...)`), idealmente con la categoría y si es reintentable (2A).

**❌ Las que tientan:**

❌ **"Agregar al prompt: 'si el resultado tiene la clave error, tratalo como falla'".**
- *Tienta porque:* el texto del error ya está.
- *Está mal porque:* el protocolo ya tiene la forma correcta: `isError`. Un dict devuelto es contenido normal.

❌ **"Devolver el string 'ERROR: Order not found'".**
- *Tienta porque:* el texto es clarísimo.
- *Está mal porque:* sigue siendo contenido normal, sin `isError`; el agente no tiene una señal estructurada de falla.

> 🧠 **Para recordar:** falla = `isError: true`, no un dict que dice "error".

---

## Checklist oficial

**Tarea 2.4 — Integrate MCP servers into Claude Code and agent workflows** *(se completa en 2C)*

*Knowledge of*
- [x] Scopes: project-level (`.mcp.json`) para tooling compartido vs. user-level (`~/.claude.json`) para servidores personales/experimentales → **Tema 4** (Trampas 1 y 3)
- [x] Expansión de variables de entorno en `.mcp.json` (`${GITHUB_TOKEN}`) para credenciales sin commitear secretos → **Tema 5** (Trampa 2)
- [x] Las tools de todos los servidores configurados se descubren al conectar y están disponibles simultáneamente → **Tema 7** (Trampa 6)
- [x] Resources como mecanismo para exponer catálogos de contenido (issue summaries, documentation hierarchies, database schemas) y reducir llamadas exploratorias → **Temas 3 y 12** (Trampa 5)

*Skills in*
- [x] Configurar servidores compartidos en `.mcp.json` con expansión de variables para tokens → **Temas 5 y 6** (Trampa 2)
- [x] Configurar servidores personales/experimentales en `~/.claude.json` → **Tema 4** (Trampa 3)
- [~] Mejorar las descripciones de tools MCP para que el agente no prefiera built-in tools como Grep → **Tema 8** (Trampa 4). *Se completa en 2C con las built-in tools.*
- [x] Elegir servidores de la comunidad antes que custom para integraciones estándar (Jira); custom para workflows del equipo → **Tema 9** (Trampa 8)
- [x] Exponer catálogos como resources para dar visibilidad sin llamadas exploratorias → **Tema 3** (Trampa 5)

**De la documentación, no de la guía** (vale saberlo; la guía no lo pregunta directo): tres scopes y precedencia, `claude mcp add`, aprobación de `.mcp.json`, `url` sin `type`, tool search (Temas 4, 6, 7) · `mcpServers`, `allowedTools`, `acceptEdits` y servidores in-process en el Agent SDK (Tema 10).

**📘 Curso (útil para entender; lecciones 37–43):** problema N×M y model-agnostic (Tema 1) · árbol de decisión de primitivos y "Exam Trap" de resources (Tema 2) · `@mcp.tool()`, docstring → description, type hints → inputSchema, text vs. structured, `ToolError`, Inspector, lifespan, no bloquear el event loop (Tema 11) · static/dynamic, diseño de URIs, templates, subscriptions (Tema 12) · versionado y diseño de argumentos de prompts (Tema 13) · handshake, `listChanged`, `McpError`, multi-server con namespaces (Temas 7 y 14).

---

## Autoevaluación oral

1. ¿Qué diferencia hay entre tools, resources y prompts? ¿Quién controla cada uno? Dame un ejemplo de TiendaX de cada uno.
2. El equipo necesita un servidor compartido con un token y un dev quiere probar otro servidor. ¿Dónde va cada uno y cómo manejás el token? ¿Por qué "el repo es privado" no alcanza?
3. Hay tres servidores configurados. ¿Cómo ve el agente sus tools? ¿Hace falta un router?
4. El agente usa Grep en vez de tu tool MCP. ¿Qué cambiás, y por qué no le sacás Grep?
5. ¿Cuándo usás un servidor de la comunidad y cuándo uno propio? ¿Cuándo un resource en vez de una tool?

---

## Preguntas tipo examen

Las preguntas tipo examen de este capítulo están en [`04-practica/modulo-2.md`](../04-practica/modulo-2.md), junto con las del resto del módulo 2. Hacelas cuando termines **todos** los capítulos del módulo, de a una y sin mirar la respuesta.

> Nota: **ninguna pregunta de muestra de la guía oficial evalúa 2.4**. Las preguntas del módulo 2 sobre MCP se arman a partir del texto oficial de la tarea (Knowledge/Skills) y de los escenarios donde aparece MCP (Customer Support Resolution Agent y Developer Productivity with Claude).

---

## Revisión contra el blueprint oficial

Qué puede salir en el examen de 2.4 que el curso de Jacob **no cubre o cubre flojo**, y dónde quedó explicado acá:

1. **Scopes `.mcp.json` vs. `~/.claude.json`** (K1, S1, S2). El curso no los menciona. → Tema 4.
2. **Expansión de variables `${GITHUB_TOKEN}`** (K2, S1). El curso no la menciona. → Tema 5.
3. **Tools de todos los servidores disponibles a la vez** (K3). El curso lo toca desde el cliente Python (multi-server, namespaces), no desde Claude Code. → Tema 7.
4. **Resources como catálogos para evitar llamadas exploratorias** (K4, S5). El curso explica resources, pero no este uso concreto con los ejemplos de la guía. → Tema 3.
5. **Descripciones MCP vs. Grep** (S3). El curso no lo trata. → Tema 8 (y se completa en 2C).
6. **Community vs. custom servers** (S4). El curso no lo trata. → Tema 9.
7. **Qué está fuera del alcance:** desplegar/hospedar servidores MCP. No le dediques tiempo. → Tema 1.
8. **Diferencias que pueden confundir:** 2 scopes en la guía vs. 3 en la documentación; "disponibles a la vez" vs. tool search; handshake eliminado en la spec vigente; `FastMCP` → `MCPServer`; `mimeType` opcional. Qué responder: 2 vs. 3 scopes y "disponibles a la vez" vs. tool search → **la versión de la guía**; `mimeType` → **la especificación** (es opcional); handshake → **la idea común**: al conectar se descubren las capacidades; `FastMCP`/`MCPServer` → no se evalúa. → Temas 4, 7, 11, 12 y 14.

Lo que agrega el curso por su cuenta (lifespan, versionado de prompts, diseño de URIs, Inspector) queda marcado como 📘: sirve para entender, pero no es la respuesta "oficial".

