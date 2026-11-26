# Capítulo 3 · 1C · Udemy 4 — Multi-Agent Orchestration (orquestación de varios agentes)

*Tareas oficiales 1.2, 1.3 y 1.7*

---

## Dónde estamos

(1A y 1B ya están leídos. Se cierran con las preguntas del final del módulo 1.)

Este capítulo cubre tres tareas del Dominio 1, y cada una pesa 3,86% del examen:
- **1.2** Orchestrate multi-agent systems with coordinator-subagent patterns (orquestar sistemas de varios agentes con un coordinador y subagentes).
- **1.3** Configure subagent invocation, context passing, and spawning (configurar cómo se invocan los subagentes, cómo se les pasa contexto y cómo se lanzan).
- **1.7** Manage session state, resumption, and forking (manejar el estado de una sesión, retomarla y bifurcarla).

### Cómo leer este capítulo

Todo lo que leés acá **vale para el examen**, salvo que diga lo contrario. Cuando algo sale solo del curso (útil para entender, pero no central), lo marco con **📘 Curso**. Cuando Jacob dice algo distinto de lo que evalúa la guía, aparece un recuadro así:

> ⚠️ **En el curso vas a escuchar otra cosa.** … **Para el examen: …**

## De dónde venimos

En **1A** viste el **agentic loop** (el ciclo del agente): Claude pide tools, tu código las ejecuta y le devuelve los resultados, y eso se repite hasta que `stop_reason` es `end_turn`. En **1B** viste cómo partir una tarea grande en **subtareas**, cuándo correrlas en paralelo (**fan-out**, abrir en abanico) y cómo juntar después los resultados (**fan-in**, volver a juntar).

En 1B también apareció el patrón **orchestrator-workers** (orquestador y trabajadores): un modelo central reparte subtareas entre otros. Este capítulo trata justamente de eso, pero en el caso en que **cada subtarea la resuelve otro agente**.

## Mapa del capítulo

Los temas van en este orden, de lo más simple a lo más complejo:

1. **Coordinator y subagents**: qué son y qué hace cada uno.
2. **Context isolation**: qué ve un subagent y qué no ve. Es la idea más importante del capítulo.
3. **Cómo se configura un subagent**: `AgentDefinition`, la tool Task y `allowedTools`.
4. **Lanzar subagents en paralelo.**
5. **Cómo el coordinador reparte el trabajo y da instrucciones.**
6. **Pasar contexto entre agentes sin perder las fuentes.**
7. **Topologías**: quién habla con quién.
8. **Errores de los subagents.**
9. **Costo**: cuándo vale la pena usar varios agentes.
10. **Estado y checkpoints**: lo que dice el curso.
11. **Sesiones**: retomar, empezar de cero o bifurcar.

Los temas 1 a 9 son sobre **varios agentes trabajando juntos** (tareas 1.2 y 1.3). Los temas 10 y 11 son sobre **una sesión de trabajo que se corta y se retoma** (tarea 1.7).

---

## Tema 1 — Coordinator and subagents (coordinador y subagentes)

### Qué es

Un **multi-agent system** (sistema multi-agente) es un sistema en el que varios agentes trabajan juntos en una misma tarea. En vez de que un solo agente haga todo, el trabajo se reparte: un agente organiza y otros ejecutan partes. El patrón que evalúa el examen tiene dos roles:

- **Coordinator** (coordinador), también llamado **orchestrator** (orquestador). Es el agente que recibe la tarea completa, la divide en partes, decide qué agente hace cada parte y al final junta los resultados.
- **Subagent** (subagente). Es un agente que el coordinador lanza para resolver **una** parte. Hace su trabajo y le devuelve el resultado al coordinador.

Los subagents **no eligen** qué hacer: toda la lógica que decide a quién va cada tarea vive en el coordinador. Esto importa porque, si cada subagent decidiera por su cuenta qué tomar, nadie garantizaría que el trabajo quede cubierto sin huecos ni repeticiones. (El curso lo dice así: "subagents don't self-select".)

### Ejemplo general

TiendaX tiene un sistema de investigación para el equipo de marketing. Marketing pide: "Investigá las políticas de devolución de la competencia". El sistema tiene un coordinador y tres subagents:

- **search** (búsqueda): busca en la web las páginas con las políticas.
- **analysis** (análisis): lee cada política y saca los datos (días de plazo, condiciones, costos).
- **synthesis** (síntesis): arma el informe final.

El coordinador divide el pedido por rubro (zapatillas, ropa, electrónica). Primero lanza a search para cada rubro. Cuando vuelven los resultados, se los pasa a analysis. Por último, le pide a synthesis el informe con todo lo analizado.

### Las cuatro funciones del coordinador

**1. Task decomposition (descomposición de la tarea).** Es dividir el objetivo en subtareas, como viste en 1B. El riesgo que más pregunta el examen es que la descomposición quede **demasiado estrecha**: que el coordinador reparta un alcance más chico que el tema real. Lo peligroso es que ningún subagent falla, así que el hueco no se nota hasta leer el informe.

- **Mal:** el coordinador divide "políticas de devolución de la competencia" en tres subtareas: zapatillas, ropa y electrónica. Pero TiendaX también vende artículos de hogar y juguetes. El informe sale prolijo, sin hogar ni juguetes. Search, analysis y synthesis hicieron bien su trabajo: el hueco viene de **lo que les asignaron**.
- **Bien:** antes de repartir, el coordinador cubre **todo el alcance** del tema (los cinco rubros que vende TiendaX) y recién después lo divide.

La regla del examen sale de la pregunta oficial de muestra Q7 (el curso no lo menciona): si el resultado tiene temas sin cubrir **y cada subagent cumplió su tarea**, la causa es la descomposición del coordinador. No es culpa de los agentes que vienen después, porque ellos trabajaron con lo que recibieron.

**2. Delegation (delegación).** Es decidir qué subagent hace cada subtarea y, además, **cuáles hacen falta** según lo compleja que sea la consulta. No toda consulta necesita a todos los subagents. Lo vemos en detalle en el Tema 5.

**3. Result aggregation (agregación de resultados).** Es juntar lo que devolvieron los subagents en una sola respuesta. La guía la nombra como función del coordinador. 📘 Curso: la divide en tres pasos:
1. **Collect** (juntar): esperar a que terminen todos los subagents.
2. **Validate** (validar): revisar cada resultado contra un **schema** (esquema: la forma fija que tiene que tener la respuesta, con sus campos y tipos) y descartar los que no la cumplen.
3. **Synthesize** (sintetizar): combinar solo los resultados válidos en la respuesta final.

*Ejemplo:* llegan 5 resultados de search. Uno vino sin el campo `source_url`, así que no cumple el schema. El coordinador lo rechaza y sintetiza con los 4 válidos (`valid: 4, rejected: 1`). Validar antes de sintetizar evita que un resultado roto contamine el informe.

**4. Observability (observabilidad).** Es poder ver y reconstruir qué hizo el sistema. La guía la da como una de las razones para que todo pase por el coordinador (Tema 7): como es el **único** que ve todos los resultados, es el lugar natural para registrar. 📘 Curso: agrega cómo se hace. El coordinador **registra** cada decisión: a qué subagent mandó cada subtarea y **por qué**, cómo avanza el trabajo después de cada subagent, y los errores con el contexto que los causó.

*Ejemplo de registro (log):*

```json
{ "event": "assign", "subtask": "politicas-electronica",
  "agent": "search", "rationale": "subtarea de búsqueda web por rubro" }
```

El campo `rationale` (motivo) es la clave: sin el motivo, después nadie puede entender por qué el sistema hizo lo que hizo.

### Para el examen

- El coordinador **descompone, delega, agrega** y decide **qué subagents invocar según la complejidad**.
- **Cobertura incompleta + subagents que cumplieron = descomposición del coordinador demasiado estrecha.**
- 📘 La agregación **valida** antes de sintetizar.

### Cómo se une

Es el patrón **orchestrator-workers** de 1A y 1B, pero ahora cada "worker" es un agente completo, con su propio agentic loop.

---

## Tema 2 — Context isolation (aislamiento de contexto)

### Qué es

Un subagent **no ve la conversación del coordinador**. Arranca de cero, con su propio **context window** (ventana de contexto: todo lo que el modelo ve en una llamada). Es como si el coordinador abriera una conversación nueva con otro Claude: ese Claude no sabe nada de lo que se habló antes, salvo lo que le escriban en el primer mensaje.

Según la documentación del Agent SDK, lo que **sí** recibe un subagent es:
- su propio system prompt;
- sus tools;
- el CLAUDE.md del proyecto, si hay uno (el archivo de instrucciones del proyecto que Claude Code carga solo; lo vemos en 3B);
- **el prompt con el que el coordinador lo lanza**. Esto es lo único que le llega del coordinador.

Y lo que **no** recibe:
- el historial de la conversación del coordinador;
- lo que encontraron otros subagents, salvo que el coordinador lo ponga en su prompt;
- nada de una invocación anterior: no comparte memoria entre una vez y la siguiente.

A la vuelta pasa algo parecido: al coordinador **solo le llega el mensaje final** del subagent. Las tool calls que hizo el subagent en el medio quedan adentro de él.

### Por qué es así

📘 Curso: el aislamiento no es un defecto, es una decisión de diseño. Un subagent que solo carga lo que necesita no sufre **context bloat** (contexto inflado), no filtra información de un agente a otro y gasta menos tokens.

📘 Curso: de ahí sale una regla doble. Hay cosas que se **pass explicitly** (pasan explícitamente): las instrucciones de la tarea, los datos que necesita, el formato de salida, los criterios de éxito y las restricciones. Y hay cosas que se **withhold by default** (retienen por defecto): el historial completo del coordinador, las salidas de otros subagents que no necesita, system prompts ajenos y, sobre todo, **credentials** (credenciales).

> ⚠️ **En el curso vas a escuchar otra cosa.** La slide de Jacob pone "outputs from other subagents" en la lista de lo que se retiene por defecto. **Para el examen:** si el subagent depende del trabajo de otro, se le pasan **los hallazgos completos de los agentes anteriores** directamente en su prompt, con sus fuentes (Tema 6); por ejemplo, a synthesis se le pasan los resultados de search y de analysis. "Retener" vale solo para lo que **no** necesita.

### Ejemplo: mal y bien

SoporteBot ahora tiene un coordinador y un subagent de reembolsos. Martín escribió antes en la conversación: "Me cobraron dos veces el pedido TX-104251".

**Mal.** El coordinador lanza al subagent con este prompt:

```
Reembolsá el cobro duplicado.
```

El subagent no sabe de qué pedido se trata, porque no vio la conversación. Entonces le pregunta a Martín: "¿Cuál es tu número de pedido?". Martín ya lo había dicho y tiene que repetirlo.

**Bien.** El coordinador pone todo lo necesario en el prompt:

```
Reembolsá el cobro duplicado del pedido TX-104251 (cliente C-5521, Martín).
Cobros encontrados: PAY-88121 y PAY-88122, ambos de USD 120, el 14/11.
Reembolsá solo PAY-88122.
Devolvé: {refund_id, amount, status}.
```

Ahora el subagent tiene el pedido, el cliente, los dos cobros, cuál reembolsar y qué tiene que devolver. Puede trabajar sin preguntarle nada a nadie.

### Para el examen

- Los subagents **no heredan** el contexto del coordinador ni comparten memoria entre invocaciones.
- Todo lo que necesitan va **explícito en su prompt**, incluidos los **complete findings** (hallazgos completos) de los agentes anteriores. Por ejemplo, a synthesis hay que pasarle completos los resultados de search y de analysis.
- Si una opción dice "el subagent ya tiene acceso al historial" o "solo decile que continúe", es incorrecta.

### Cómo se une

En 1A viste que **la API no recuerda nada entre llamadas**: cada llamada recibe el historial completo. El subagent es el mismo caso. Si algo no está en lo que recibe, para él no existe.

---

## Tema 3 — Cómo se configura un subagent: AgentDefinition, Task y allowedTools

### Qué es

El **Agent SDK** es la librería de Anthropic para construir agentes. Ahí, cada tipo de subagent se describe con un **AgentDefinition** (definición de agente): un objeto que dice para qué sirve ese subagent, qué instrucciones tiene y qué puede hacer. Tiene tres campos clave:

- **`description`** (descripción): dice **cuándo** usar este subagent. El coordinador elige a quién delegar leyendo estas descripciones, igual que Claude elige tools leyendo sus descripciones (1A).
- **`prompt`**: es el **system prompt** del subagent, sus instrucciones fijas.
- **`tools`**: la lista de tools que el subagent **puede** usar. Una tool que no está en la lista **no existe** para él.

Para lanzar a un subagent, el coordinador usa una tool especial que se llama **Task**. Lanzar un subagent se llama **spawning** (lanzamiento). Como Task es una tool, el coordinador solo puede usarla si está en su lista de tools permitidas, que se llama **allowedTools** (`allowed_tools` en Python, `allowedTools` en TypeScript y en la guía). Este detalle es fácil de olvidar y el examen lo pregunta: si Task no está permitida, el coordinador no puede delegar en nadie, por bien definidos que estén los subagents.

### Ejemplo de configuración

```python
agents = {
  "reembolsos": AgentDefinition(
      # Cuándo usarlo: el coordinador lee esto para decidir a quién delegar
      description="Procesa reembolsos de TiendaX. Usalo cuando haya que devolver un cobro.",
      # Su system prompt
      prompt="Sos el agente de reembolsos de TiendaX. Nunca reembolses más que el monto cobrado.",
      # SOLO estas tools: el resto no existe para este subagent
      tools=["get_payment", "process_refund"],
  )
}

# El coordinador: "Task" tiene que estar en sus tools permitidas, o no puede lanzar subagents
options = ClaudeAgentOptions(agents=agents, allowed_tools=["Task", "get_order_status"])
```

(Es código ilustrativo. En el SDK real, las tools propias se registran en un servidor MCP y se llaman `mcp__<server>__<tool>`; lo vemos en 2B.)

Si **no** ponés `tools` en el AgentDefinition, el subagent **hereda todas** las tools disponibles. Por eso, para limitarlo, tenés que listarlas: el silencio no restringe nada.

La documentación agrega tres detalles más:
- `description` y `prompt` son **obligatorios**; `tools` es opcional. Hay otros campos opcionales, como **`model`** (qué modelo usa ese subagent, Tema 9), `disallowedTools` o `maxTurns`. Para el examen alcanza con los tres de la guía.
- El coordinador delega **solo**, leyendo la `description`, o **explícitamente**, si el prompt nombra al subagent ("usá el agente de reembolsos para…").
- Un subagent **puede** lanzar sus propios subagents (por defecto, hasta 3 niveles). La guía no lo evalúa; solo no elijas una opción que afirme que "los subagents nunca pueden lanzar otros".

**Un detalle de nombres.** En la documentación actual del SDK, la tool aparece como `"Agent"` en los bloques `tool_use` y como `"Task"` en la lista inicial de tools (se renombró en Claude Code v2.1.63). La guía del examen la llama **Task**, así que en el examen respondé **Task**. (📘 El curso no nombra ni Task ni `allowedTools` ni `AgentDefinition`: todo su código usa llamadas directas a la API.)

### Least privilege (mínimo privilegio) y authority boundary (límite de autoridad)

Restringir tools **por configuración** se llama **least privilege**: cada agente tiene solo las tools que necesita para su tarea. Si un subagent de análisis no tiene tool de escritura, no hay forma de que escriba, aunque se equivoque o lo engañen.

📘 Curso: lo amplía con el **authority boundary** (límite de autoridad), el conjunto de acciones que el subagent tiene permitidas, ni una más. Tiene tres partes:
- **Least privilege:** solo las tools y los datos que la subtarea necesita.
- **Explicit boundaries** (límites explícitos): el prompt dice qué está permitido y qué queda fuera de alcance.
- **No side effects** (sin efectos secundarios): el subagent no cambia estado compartido ni hace nada fuera de su tarea sin aprobación del coordinador.

¿Por qué el filtro tiene que ir en el código y no en el prompt? Porque, según la documentación, una tool que dejás afuera directamente no está en la sesión del subagent. En cambio, un prompt es **probabilístico**: casi siempre se cumple, pero no siempre. La instrucción en el prompt es un **complemento**, no reemplaza la configuración.

- **Mal:** darle al subagent de análisis la tool de escritura y ponerle en el prompt "no modifiques archivos".
- **Bien:** no incluir la tool de escritura en `tools`. Así es imposible que la use.

### Para el examen

- La tool **Task** es el mecanismo para lanzar subagents.
- **`allowedTools` del coordinador tiene que incluir `"Task"`.** Si las definiciones están perfectas pero el coordinador nunca delega, es lo primero que hay que revisar.
- `AgentDefinition` = **description** (cuándo usarlo) + **prompt** (system prompt) + **tools** (restricción de tools).
- Las restricciones van en la configuración, no en el prompt.
- Documentación: `Agent`; guía: **Task** → en el examen, **Task**.

### Cómo se une

La `description` cumple el mismo rol que la descripción de una tool en 1A: es lo que el modelo lee para decidir.

---

## Tema 4 — Lanzar subagents en paralelo

### Qué es

Si las subtareas son independientes (el **test de independencia** de 1B: ninguna necesita el resultado de otra), los subagents pueden correr **al mismo tiempo**. Para eso, el coordinador tiene que pedir **varias llamadas a Task en una sola respuesta**. En inglés: **multiple Task tool calls in a single response**.

Si, en cambio, el coordinador pide un Task, espera el resultado y recién en el turno siguiente pide otro, los subagents corren **uno detrás de otro**, aunque sean independientes. El sistema no los paraleliza solo: depende de cómo los pida el coordinador.

La documentación lo resume así: las subtareas independientes terminan en el tiempo **del más lento**, no en la suma de todos. En el sistema de investigación de Anthropic, el coordinador lanza de 3 a 5 subagents en paralelo, y eso recortó el tiempo hasta un 90%.

**Ojo: solo si son independientes.** Si un subagent necesita el resultado de otro (synthesis necesita lo de search), esos dos van en orden, porque el segundo no puede arrancar sin el primero. "Correr todo en paralelo" no es la respuesta cuando las etapas dependen entre sí, y tampoco arregla un pipeline que hace trabajo de más (para eso está el Tema 5.3).

### Ejemplo

El coordinador de marketing necesita buscar políticas de tres rubros, y cada búsqueda tarda unos 3 minutos.

**Mal (en serie).** En el turno 1 pide Task(search zapatillas) y espera 3 minutos. En el turno 2 pide Task(search ropa) y espera otros 3. En el turno 3 pide Task(search electrónica) y espera 3 más. En total, **9 minutos**.

**Bien (en paralelo).** En el turno 1 pide Task(search zapatillas), Task(search ropa) y Task(search electrónica), los tres en la misma respuesta. Los tres corren a la vez y el total es **3 minutos**, lo que tarda el más lento.

### Para el examen

- Paralelo = **varias llamadas a Task en la misma respuesta**, no en turnos separados.
- Si el problema es la lentitud **con subtareas independientes**, la solución es paralelizar. Pasar a otra topología (Tema 7) no es la respuesta.

### Cómo se une

Es el **fan-out** de 1B, hecho con subagents. Y en 1A viste que Claude puede pedir varias tools en una respuesta (parallel tool use). Task es una tool más, así que funciona igual.

---

## Tema 5 — Cómo el coordinador reparte el trabajo y da instrucciones

### Qué es

Este tema junta cuatro habilidades que pide la guía. Las cuatro tienen que ver con **cómo** delega el coordinador: qué pedazo le da a cada uno, cómo le explica la tarea, a cuántos llama y qué hace si el resultado quedó incompleto.

### 5.1 Partitioning (particionar el alcance)

**Qué es.** Particionar es darle a cada subagent un pedazo **distinto** del tema. Si dos subagents reciben el mismo pedido, van a hacer el mismo trabajo dos veces: se paga doble y no se cubre nada nuevo. Se puede partir por **subtema** o por **tipo de fuente**.

**Ejemplo.**
- **Mal:** dos subagents de search con "buscá políticas de devolución de la competencia". Los dos traen casi las mismas páginas.
- **Bien por subtema:** uno busca zapatillas, otro ropa y otro electrónica.
- **Bien por tipo de fuente:** uno busca sitios oficiales de las tiendas, otro reseñas de clientes y otro noticias.

### 5.2 Instrucciones: objetivos, no recetas

**Qué es.** El prompt que el coordinador le da a un subagent tiene que decir **qué lograr y cómo se mide si está bien**. En inglés: **research goals and quality criteria** (objetivos de investigación y criterios de calidad). **No** tiene que ser un paso a paso. La razón es que el subagent va a encontrar cosas que el coordinador no previó: con un objetivo claro puede adaptarse; con una receta, la sigue aunque no sirva.

**Ejemplo.**
- **Mal (receta):** "Buscá en Google 'política devoluciones', abrí los 5 primeros resultados y copiá el texto."
- **Bien (objetivo + criterio):** "Encontrá las políticas de devolución vigentes de al menos 3 tiendas de electrónica. Cada política tiene que venir de la página oficial de la tienda e indicar plazo, condiciones y fecha de actualización."

📘 Curso: una buena instrucción tiene tres cosas. Un **narrow scope** (alcance acotado), que dice qué entra y qué no. Un **output format** (formato de salida) preciso, para que la agregación funcione. Y **success criteria** (criterios de éxito) explícitos, para que el subagent sepa cuándo terminó.

📘 Curso: también nombra los tres errores que vuelven frágil a un subagent:
- **overly broad scope** (alcance demasiado amplio): se le pide demasiado de una vez;
- **underpowered context** (contexto insuficiente): no se le pasó lo que necesitaba (Tema 2);
- **unclear success criteria** (criterio de éxito poco claro): no sabe cuándo terminó.

El blog de Anthropic sobre su sistema de investigación coincide: cada subagent necesita un **objetivo**, un **formato de salida**, orientación sobre qué tools y fuentes usar y **límites claros** de la tarea. Cuando las instrucciones eran vagas, los subagents duplicaban trabajo o dejaban huecos.

### 5.3 Dynamic selection (selección dinámica)

**Qué es.** El coordinador analiza la consulta y decide **qué subagents hacen falta**. En inglés: **dynamically select subagents**. No siempre corre el **pipeline** completo (la cadena search, analysis y synthesis, uno detrás de otro). Correrlo siempre parece consistente, pero hace que una pregunta simple cueste lo mismo que una investigación entera.

**Ejemplo.**
- "¿Cuántos días de devolución da TiendaY?" es una consulta simple: alcanza con un solo search.
- "Compará las políticas de devolución de todo el mercado" es una consulta compleja: necesita search, analysis y synthesis.

El blog de Anthropic da la escala: un dato simple se resuelve con **1 agente y de 3 a 10 tool calls**; una investigación compleja puede usar **más de 10 subagents**.

**Quién elige:** el propio coordinador. Si el problema es que las consultas simples cuestan lo mismo que las complejas, la respuesta no es agregar un clasificador aparte antes del coordinador, ni pasar todo a modelos más chicos, ni correr el pipeline en paralelo. La respuesta es que el coordinador **invoque solo lo que la consulta necesita**.

### 5.4 Iterative refinement loop (ciclo de refinamiento iterativo)

**Qué es.** Aunque la descomposición sea buena, el primer informe puede salir con huecos. El loop de refinamiento lo resuelve así: después de la síntesis, el coordinador **revisa el resultado buscando huecos**. Si encuentra alguno, vuelve a delegar a search y a analysis con **consultas dirigidas a ese hueco**, y pide una síntesis nueva.

**Ejemplo.** El informe tiene datos de zapatillas y ropa, pero de electrónica hay una sola tienda. El coordinador lo nota, lanza un search específico ("políticas de devolución de 3 tiendas de electrónica") y después vuelve a sintetizar.

Hay tres detalles que separan la respuesta correcta de las que tientan:
- **Quién evalúa:** el **coordinador**, no synthesis. Pedirle a synthesis que "complete los huecos" por su cuenta no es el loop, porque synthesis no tiene cómo buscar datos nuevos.
- **Qué relanza:** solo **consultas dirigidas** al hueco, no el pipeline entero de nuevo.
- **Cuándo para:** como todo loop, necesita una **condición de corte** (por ejemplo, un máximo de vueltas). La documentación de Anthropic lo pide para cualquier agente que itera, porque sin corte puede no terminar nunca.

### Para el examen

- Si los subagents **duplican trabajo** → **particionar** el alcance (por subtema o por tipo de fuente).
- Las instrucciones del coordinador son **objetivos y criterios de calidad**, no procedimientos.
- El coordinador **elige qué subagents invocar** según la complejidad.
- Para los huecos: primero, una **buena descomposición** (1B). Además, un **loop de refinamiento** que detecta los huecos que queden y vuelve a delegar con consultas dirigidas.

### Cómo se une

Particionar es aplicar a varios agentes las propiedades de una buena subtarea de 1B (una sola responsabilidad, alcance acotado). El loop de refinamiento se parece al **evaluator-optimizer** de 1A y 1B: alguien revisa y se vuelve a intentar.

---

## Tema 6 — Pasar contexto entre agentes sin perder las fuentes

### Qué es

Cuando un agente le pasa información a otro, hay que separar dos cosas. Por un lado, **el contenido**: el dato en sí ("TiendaY da 60 días"). Por otro, **la metadata** (metadatos): de dónde salió ese dato (URL de la fuente, nombre del documento, número de página, fecha).

Si van mezclados en un texto corrido, el agente que recibe tiene el dato pero no sabe de dónde salió, y no puede citarlo. Si van separados en **structured data** (datos estructurados, por ejemplo un JSON con un campo para cada cosa), el agente que recibe puede decir de qué fuente sale cada dato. A eso se le llama **attribution** (atribución).

### Ejemplo: mal y bien

**Mal.** Search le pasa a synthesis un bloque de texto plano:

```
TiendaY acepta devoluciones por 60 días, vi esto en su web el 14/11, también TiendaZ da 30 días según una nota de prensa...
```

Synthesis escribe "TiendaY acepta devoluciones por 60 días", pero no puede citar la fuente: la URL quedó mezclada con el texto o directamente no está.

**Bien.** Search devuelve datos estructurados:

```json
{
  "findings": [
    {
      "claim": "TiendaY acepta devoluciones hasta 60 días desde la entrega",
      "source_url": "https://tienday.com/ayuda/devoluciones",
      "document": "Política de devoluciones",
      "retrieved_at": "2026-11-14"
    }
  ]
}
```

Acá `claim` es el **contenido**, y `source_url`, `document` y `retrieved_at` son la **metadata**: de dónde salió y cuándo. Synthesis copia el dato y, cuando lo cita, conserva la fuente.

La guía nombra tres tipos de metadata: **source URLs** (URLs de la fuente), **document names** (nombres de documento) y **page numbers** (números de página). Si el hallazgo sale de un PDF, por ejemplo el informe anual de TiendaY, el JSON lleva también `"page": 14`.

### Para el examen (lo que pide la guía)

- Pasar los **complete findings** (hallazgos completos).
- Usar **datos estructurados que separen el contenido de la metadata** (URLs, documentos, páginas) para preservar la atribución.

### El handoff según el curso

📘 Curso: todo lo que sigue sale de dos lecciones del curso. La guía no lo evalúa con estos nombres: lo que pide es lo de arriba (hallazgos completos y datos estructurados con metadata). Estas ideas ayudan a reconocer las respuestas correctas, pero si una opción habla de atribución, gana la de **contenido separado de la metadata**.

**6.1 Qué es un handoff.** Un **handoff** (traspaso) es el momento en que un agente le pasa trabajo a otro. Como el que recibe no ve el contexto del que envía (Tema 2), el traspaso tiene que llevar todo. El curso pide un **handoff schema** (esquema de traspaso) con cuatro elementos, más la versión:

```json
{
  "schema_version": "1.2",
  "task": "Reembolsar el cobro duplicado PAY-88122",
  "context": {
    "order_id": "TX-104251",
    "customer_id": "C-5521",
    "charges": ["PAY-88121", "PAY-88122"],
    "amount_usd": 120
  },
  "output_format": {"refund_id": "string", "amount": "number", "status": "string"},
  "constraints": ["No reembolsar más que el monto cobrado", "Un solo reembolso"]
}
```

- **task**: qué hay que hacer.
- **context**: todo lo necesario para hacerlo **sin ver el contexto de quien envía**.
- **output_format**: qué tiene que devolver y con qué forma.
- **constraints** (restricciones): los límites.
- **schema_version**: la versión del esquema (ver 6.3).

**6.2 Ni de menos ni de más.** Hay dos errores opuestos. Un handoff **under-specified** (subespecificado) deja al que recibe sin información, entonces adivina o falla; por ejemplo, "Reembolsá el cobro duplicado", sin número de pedido. Un handoff **over-specified** (sobreespecificado) le pasa todo el contexto de quien envía, incluso las 40 vueltas de conversación con Martín: sube el costo, hay más ruido y el dato importante se pierde entre lo que no importa. La regla es incluir todo lo que el receptor necesita para actuar y nada de lo que no necesita (historial, deliberaciones internas, estado del que envía).

**6.3 Versionado.** Los esquemas cambian con el tiempo, y un cambio no debería romper a los agentes que reciben mensajes viejos. Por eso cada mensaje lleva su **schema version** (versión del esquema). El receptor tolera que falte un campo **opcional** y usa un valor por defecto. Si se agrega un campo **obligatorio**, hace falta un **migration adapter** (adaptador de migración) que convierta los mensajes viejos al formato nuevo.

*Ejemplo:* se agrega el campo opcional `reason` ("motivo del reembolso"). Un mensaje de la versión 1.1 llega sin ese campo. El receptor no falla: usa `reason = "no especificado"` y sigue.

**6.4 Probar el esquema antes de usarlo.** La validación tiene que pasar **antes** de que el receptor empiece a trabajar, no cuando ya falló. El curso propone **contract tests** (pruebas de contrato): tests automáticos que confirman que un mensaje sin `task` se rechaza y que uno completo pasa. Y propone simular al receptor con **solo** el esquema, para ver si alcanza para hacer la tarea.

**6.5 Confirmación de recepción (ACK).** El handoff está completo cuando el receptor confirma que recibió todo y que tiene lo que necesita. A eso se le llama **ACK** (*acknowledgment*, confirmación). Recién entonces el emisor suelta la tarea, así nada queda en el aire.

*Ejemplo:* el subagent de reembolsos recibe el handoff y ve que falta `amount_usd`. En vez de arrancar, pide el dato faltante. El coordinador lo completa y espera el ACK antes de pasar a otra cosa.

**6.6 Sustituibilidad.** El esquema describe **qué** se pide (la interfaz), no **quién** lo resuelve. Gracias a eso se puede cambiar el agente de reembolsos por una versión nueva sin tocar al coordinador. Esto se llama **substitutability** (sustituibilidad). También permite **probar cada subagent por separado**: si funciona solo con sus entradas explícitas, se puede testear sin el resto del sistema.

**6.7 Registro de handoffs.** El curso pide un **audit log** (registro de auditoría) de cada traspaso: quién envía, quién recibe, cuándo, un resumen del pedido, si hubo ACK o no y el error con su contexto. Con eso, una falla que habría pasado inadvertida se puede diagnosticar.

### Cómo se une

El handoff es lo mismo que los **handoff points** de 1B (las interfaces entre subtareas), pero entre agentes. Y sigue valiendo la regla del Tema 2: el que recibe solo sabe lo que le pasaste.

---

## Tema 7 — Topologies (topologías): quién habla con quién

### Qué es

Una **topology** (topología) es la forma en que se conectan los agentes: quién le habla a quién y por dónde pasa la información. 📘 Curso: describe cuatro, cada una con sus ventajas y costos. Para cada una va un ejemplo de TiendaX.

**1. Hub-and-spoke (centro y radios).** Todo pasa por el coordinador: los subagents no hablan entre sí, solo con él.
- *Ejemplo:* el sistema de investigación de marketing. El coordinador habla con search, analysis y synthesis por separado.
- *Ventajas:* hay un solo lugar donde auditar y desde donde recuperarse de errores.
- *Costos:* el coordinador es un **single point of failure** (punto único de falla: si él se cae, se cae todo), puede ser un **bottleneck** (cuello de botella) y su contexto puede inflarse.

**2. Pipeline (cadena).** Cada agente le pasa su resultado al siguiente, en un orden fijo.
- *Ejemplo:* la carga nocturna de facturas de proveedores: un agente extrae los datos, otro los valida y otro los carga en la base.
- *Costos:* la **latency** (latencia, el tiempo total) es la suma de todas las etapas, y si una etapa falla se bloquea todo lo que viene después.

**3. Peer-to-peer (P2P, entre pares).** Los agentes hablan directamente entre sí, sin coordinador.
- *Ejemplo:* varios agentes que revisan productos del catálogo y se pasan entre ellos los duplicados que encuentran.
- *Ventajas:* menos latencia, y no hay un punto único de falla.
- *Costos:* es difícil de auditar porque no hay un registro central.

**4. Evaluator-optimizer (de 1A y 1B).** Aparece también en "Building effective agents" de Anthropic. Un **generator** (generador) produce un borrador. Un **evaluator** (evaluador) lo critica contra una **rubric** (rúbrica, la lista de criterios). El ciclo se repite hasta pasar el **threshold** (umbral de calidad) o llegar al máximo de iteraciones.
- *Ejemplo:* un agente escribe la respuesta a un reclamo y otro la revisa contra la política de tono de TiendaX.
- Siempre necesita una **condición de terminación** (máximo de iteraciones). Si no la tiene, puede no terminar nunca.

### Cómo elegir según el curso

📘 Curso: la elección arranca mirando **cómo fluyen los datos**. Si hay un controlador que reparte trabajo entre especialistas, encaja hub-and-spoke. Si los datos imponen un orden y cada paso necesita el anterior, encaja un pipeline. Si las partes son independientes, sin estado compartido ni orden obligatorio, encaja peer-to-peer.

| Cómo fluyen los datos | Topología |
|---|---|
| Un controlador delega en especialistas | Hub-and-spoke |
| Orden obligatorio; cada paso necesita el anterior | Pipeline |
| Partes independientes, sin estado compartido ni orden | Peer-to-peer |

📘 Curso: también nombra dos **anti-patterns** (diseños que parecen bien pero son errores):
- **Hub without hierarchy** (hub sin jerarquía): poner un coordinador en una tarea que no lo necesita. Suma latencia sin aportar control.
- **P2P without audit trail** (P2P sin registro de auditoría): usar peer-to-peer cuando hace falta un registro completo de decisiones. Con el estado repartido, después no se puede reconstruir qué pasó.

📘 Curso: los sistemas reales suelen ser **hybrid topologies** (topologías híbridas). Por ejemplo, un coordinador hub-and-spoke delega en un pipeline. En cada frontera entre patrones tiene que haber un contrato de handoff explícito (Tema 6).

### Lo que pide la guía

La guía oficial evalúa **hub-and-spoke**: el coordinador maneja **toda** la comunicación entre subagents, el manejo de errores y el ruteo de la información. La razón es que el coordinador es el único que ve el sistema completo, y eso da tres ventajas:
1. **Observability** (observabilidad): se puede ver y registrar todo (Tema 1).
2. **Manejo de errores consistente**: todos los errores llegan al mismo lugar (Tema 8).
3. **Flujo de información controlado**: cada agente recibe solo lo que el coordinador decide (Tema 2).

> ⚠️ **En el curso vas a escuchar otra cosa.** Jacob presenta peer-to-peer como una alternativa válida, con menos latencia. **Para el examen:** toda la comunicación pasa por el coordinador, y la comunicación directa entre subagents es un distractor.

### Ejemplo: el caso de la tool acotada

Este es un caso real de las preguntas de muestra de la guía (Q9; la guía la asigna a la tarea 2.3, pero se apoya en el hub-and-spoke de 1.2).

Synthesis necesita verificar datos mientras escribe el informe. Hoy lo hace así: le pide al coordinador, el coordinador le pide a search, search responde y la respuesta vuelve por el mismo camino. Esa ida y vuelta agrega un 40% de latencia. El 85% de las verificaciones son simples ("¿TiendaY da 60 días?") y el 15% necesita investigar a fondo.

- **✅ Correcto:** darle a synthesis una **scoped tool** (tool acotada) llamada `verify_fact`, que sirve solo para verificaciones simples. Las complejas siguen pasando por el coordinador hacia search. Es least privilege (Tema 3) aplicado al caso común: resuelve el 85% sin abrir más de lo necesario.
- **❌ Darle a synthesis todas las tools de búsqueda:** tendría más poder del que necesita y se mezclarían las responsabilidades.
- **❌ Juntar todas las verificaciones y hacerlas al final:** synthesis necesita los datos ya verificados para seguir escribiendo.
- **❌ Que search guarde de antemano más información de cada fuente:** no se puede adivinar qué va a hacer falta verificar.

### Para el examen

- Toda la comunicación pasa **por el coordinador**.
- Si hay una ida y vuelta cara y repetida en el caso más común, la solución es una **tool acotada** para ese caso. No se conectan los subagents entre sí ni se les dan todas las tools.

### Cómo se une

Esto refuerza el Tema 1: el coordinador es el único que ve todo. Si los subagents hablaran directo entre ellos, el coordinador dejaría de verlo.

---

## Tema 8 — Errores de los subagents

### Qué es

Cuando un subagent falla, el coordinador es el que tiene que decidir qué hacer: reintentar, buscar por otro lado o seguir sin ese dato. Para decidir bien, el error tiene que llegarle **con suficiente información**. Eso se llama **structured error context** (error estructurado con contexto).

📘 Curso: distingue dos tipos de falla. En una **transparent failure** (falla transparente), el subagent devuelve un error estructurado: el coordinador se entera y puede reaccionar. En una **silent failure** (falla silenciosa), el traspaso **parece** exitoso pero se perdió información: nadie ve un error, el sistema sigue con datos equivocados y el problema aparece mucho después, cuando ya es difícil de rastrear.

📘 Curso: hay dos formas típicas de causar una falla silenciosa:
- **Swallowing errors** (tragarse el error): el subagent atrapa la excepción y devuelve una respuesta vacía. El coordinador cree que salió bien.
- **Undifferentiated errors** (errores indiferenciados): toda falla devuelve el mismo código genérico, por ejemplo "E9999". El coordinador no puede distinguir un timeout, que se puede reintentar, de una violación de una regla, que no.

### Ejemplo: mal y bien

Es la pregunta oficial de muestra Q8. El subagent de search hace **timeout** (se agota el tiempo de espera) buscando políticas de electrónica.

**Mal (tres formas):**
- Devuelve `"status": "unavailable"` sin más detalle. Es un error indiferenciado: el coordinador no sabe qué pasó ni qué probar.
- Devuelve una lista vacía marcada como éxito. Es tragarse el error: el informe sale sin electrónica y nadie se entera.
- Lanza una excepción que corta todo el sistema, aunque los otros rubros ya estaban listos.

**Bien:**

```json
{
  "status": "error",
  "error_type": "timeout",
  "attempted_query": "políticas de devolución tiendas de electrónica Argentina",
  "partial_results": [{"claim": "TiendaE da 10 días", "source_url": "https://tiendae.com/..."}],
  "alternatives": ["buscar por tienda puntual", "usar el sitio de defensa del consumidor"]
}
```

### Qué hace el coordinador con ese error

Según la guía, con ese error el coordinador puede **reintentar con otra consulta**, **probar otro enfoque** o **seguir con los resultados parciales**. 📘 Curso: lo ordena en tres pasos, que se prueban en este orden:

1. **Retry** (reintentar): si quedan reintentos, vuelve a lanzar la tarea, igual o ajustada. *Ejemplo:* como el error es `timeout`, reintenta con una consulta más acotada: "política de devoluciones de TiendaE".
2. **Substitute** (sustituir): si no quedan reintentos, manda la tarea a otro agente o a otra fuente. *Ejemplo:* usa la alternativa "sitio de defensa del consumidor".
3. **Escalate** (escalar): si no hay alternativa, se lo pasa a un humano. *Ejemplo:* el informe sale con una nota: "Electrónica: datos parciales (1 tienda). Revisar a mano".

Todo esto es posible porque el error trajo `error_type`, `partial_results` y `alternatives`. Con un "unavailable" a secas, el coordinador no habría tenido nada con qué decidir.

### Para el examen

- Error estructurado: **tipo de falla, consulta intentada, resultados parciales y alternativas**.
- Las opciones incorrectas son: un estado genérico ("unavailable"), un resultado vacío marcado como éxito o cortar todo el flujo.
- Ojo con la opción "reintentar con backoff dentro del subagent y después devolver 'unavailable'": no está mal por reintentar, está mal porque al final devuelve un estado **genérico**.
- (Esta pregunta de la guía corresponde a la tarea 5.3; la vemos a fondo en 5B.)

### Cómo se une

En 1A viste que un `tool_result` con error tiene que llevar un mensaje claro (`is_error: true`). Esto es lo mismo, pero entre agentes.

---

## Tema 9 — Costo y fit: cuándo vale la pena usar varios agentes

### Qué es

Usar varios agentes cuesta bastante más que usar uno. Según Anthropic (y el curso da las mismas cifras), comparado con un chat simple, un agente usa unas **4×** más tokens y un sistema multi-agente usa unas **15×** más tokens. Comparado con resolver lo mismo con **un solo agente**, el blog de Anthropic da entre **3× y 10×** más tokens. Por eso la pregunta no es solo "¿funciona?", sino "¿vale lo que cuesta?".

### De dónde sale el costo

📘 Curso: el costo viene de tres lugares. Primero, el **orchestrator overhead** (costo del coordinador): antes de que empiece el trabajo real, el coordinador gasta tokens en planificar y repartir. Segundo, el **parallel fan-out** (abrir en paralelo): cada subagent arma su propio contexto desde cero y razona por su cuenta, así que el gasto se multiplica. Tercero, el **result stitching** (unir resultados): combinar todo en una respuesta coherente es otra pasada cara del modelo.

📘 Curso: además del costo en tokens hay un costo de coordinación. Hay que repartir bien desde el principio, los subagents se pueden desviar o duplicar trabajo si las instrucciones no son precisas, y al final hay que juntar y reconciliar todo.

### El fit (cuándo encaja)

📘 Curso: da tres condiciones, y tienen que cumplirse **las tres**:
1. El trabajo es **realmente paralelo**: **breadth-first** (a lo ancho, con muchas ramas independientes).
2. Cada rama se beneficia de **tener su propio contexto**.
3. El resultado **vale el costo**.

No encaja con el trabajo **tightly coupled** (fuertemente acoplado), donde todos los agentes necesitarían el mismo contexto: separarlos obligaría a pasarse todo de un lado a otro, y se pierde la ventaja. **La mayoría de las tareas de código caen acá.** Anthropic lo dice igual: en el código hay menos tareas realmente paralelizables que en la investigación.

### Ejemplo

- **Encaja:** la investigación de marketing. Cada rubro es independiente y cada search se beneficia de tener solo su rubro en el contexto.
- **No encaja:** el bot que ayuda a los desarrolladores a cambiar el checkout. Cada cambio depende de los otros archivos y todos los agentes necesitarían ver el mismo código.

**Para bajar el costo.** 📘 Curso: usar un modelo potente para el coordinador y para combinar los resultados, y modelos más livianos para las subtareas. En el SDK se configura con el campo `model` del AgentDefinition, y es lo que hizo Anthropic en su sistema de investigación (Opus como coordinador, Sonnet en los subagents).

### Para el examen

- Multi-agente solo cuando el trabajo es paralelo, se beneficia de contextos separados y vale el costo.
- Para trabajo acoplado (la mayoría del código) conviene **un solo agente**.

### Cómo se une

Es la misma idea de 1A ("no hagas un agente para todo") llevada un nivel más arriba: tampoco hagas multi-agente para todo.

---

## Tema 10 — State and checkpoints (estado y puntos de guardado)

### Qué es

📘 Curso: **todo este tema sale del curso.** La guía no lo evalúa con estos nombres, pero el curso le dedica dos lecciones y es la base del Tema 11 y de los capítulos 5A a 5C. Lo dividimos en cuatro partes.

### 10.1 Dónde vive el estado

**Qué es.** El **state** (estado) es la información que un agente necesita para seguir trabajando: el plan, lo que ya hizo, los resultados parciales. Si una tarea larga se corta y el estado se perdió, hay que empezar de nuevo. Por eso importa dónde vive. Hay dos lugares posibles:

- **In-context state** (estado en el contexto): está dentro del context window. Es inmediato y no cuesta tool calls, pero el espacio es limitado y se pierde cuando la sesión termina o el contexto se recorta.
- **External memory** (memoria externa): está guardado fuera del modelo. Persiste, pero cada vez que el agente lo consulta es una tool call más. Hay tres tipos:
  - **Key-value store** (almacén clave-valor): búsqueda exacta por identificador. *Ejemplo:* el estado del pedido TX-104233.
  - **Relational database** (base de datos relacional): consultas con filtros y joins. *Ejemplo:* el registro de todos los reembolsos del mes.
  - **Vector index** (índice vectorial): **semantic retrieval** (búsqueda por significado, no por clave exacta). *Ejemplo:* "conversaciones anteriores donde un cliente se quejó del envío", aunque no usen las mismas palabras.

### 10.2 Qué guardar y qué no

**Qué es.** Guardar todo afuera es caro y llena la memoria de ruido; no guardar nada hace que se pierda trabajo. La pregunta central del curso es: **¿este dato tiene que sobrevivir después de esta sesión?** Si no lo vas a necesitar en la próxima sesión, queda en el contexto. Si lo vas a necesitar, la segunda pregunta es si se puede reconstruir barato: si se puede, no se guarda (es **reconstructable state**, estado reconstruible); si no se puede, se guarda afuera.

Para decidir, el curso propone cuatro preguntas:
- ¿Sobrevive a una interrupción sin guardarlo afuera?
- ¿Hay que buscarlo por significado (y entonces va a un vector index)?
- ¿Lo necesita otra sesión u otro usuario?
- ¿Se puede reconstruir barato desde la fuente?

**Hot and cold tiers (niveles caliente y frío).** Casi todos los agentes en producción usan los dos lugares a la vez. El **hot tier** (nivel caliente) es lo que se usa ahora: el plan activo, el resultado del paso actual y las salidas recientes de las tools; va **en el contexto**. El **cold tier** (nivel frío) es lo que se usa poco: resultados terminados, configuración e historial; va **en la memoria externa**. Al retomar, se carga **solo lo mínimo** que hace falta para seguir.

*Ejemplo:* SoporteBot atiende a María. El pedido que está revisando ahora es hot y está en el contexto. Los reclamos que María hizo el año pasado son cold: están en la base y se consultan solo si hacen falta. El estado del pedido no se guarda aparte, porque se reconstruye llamando a `get_order_status`.

**Memory hygiene (higiene de la memoria).** Con el tiempo, lo guardado se vuelve viejo o engañoso, y un agente que lo lee puede razonar con datos que ya no son ciertos. Por eso hay que hacer **pruning** (podar): sacar lo que ya no sirve, del contexto (para liberar tokens) y de la memoria externa (para bajar el ruido). Antes de podar, se pregunta si hay que **archivarlo** primero.

### 10.3 Checkpoints (puntos de guardado)

**Qué es.** Un **checkpoint** es una foto del progreso de una tarea larga, guardada afuera, para poder retomarla desde ahí si se corta. Retomar sin repetir lo ya hecho se llama **session resumption** (reanudación de sesión). Lo difícil es decidir cuándo sacar la foto y qué poner en ella.

**Cuándo se guarda:**
- al **final de cada fase** importante, no después de cada tool call;
- **antes de cualquier acción irreversible** (por ejemplo, un reembolso). Si se guarda después y el proceso se cae justo en el medio, al reiniciar se repetiría el reembolso;
- **antes de un handoff** entre agentes, para poder reintentar desde ahí si el traspaso falla.

**Qué tiene que tener como mínimo:**
- **phase marker** (marca de fase): qué fase terminó bien;
- **step outputs** (salidas de los pasos): los resultados que las fases siguientes necesitan;
- **task inputs** (entradas de la tarea): los parámetros originales;
- **timestamp** (fecha y hora): cuándo se guardó.

**Coarse vs. fine-grained (grueso o fino).** Los **coarse checkpoints** (gruesos) se guardan solo al final de cada fase. Son más simples, aunque si algo falla se puede repetir parte de la fase actual. **Es lo recomendado en la mayoría de los casos.** Los **fine-grained checkpoints** (finos) se guardan después de cada paso: se repite muy poco, pero hay muchas escrituras y el estado es complejo. Se justifican solo si cada paso es caro o tiene efectos secundarios.

**Cómo se retoma:**
1. Al arrancar, se busca si hay un checkpoint.
2. Si hay, se **verifica que esté íntegro** antes de confiar en él.
3. Se carga y se saltean las fases ya terminadas.
4. Si el checkpoint cubre solo una parte, se sigue desde ahí y se **marca el hueco**.

*Ejemplo:* el proceso nocturno de conciliación de pagos tiene tres fases: traer los pagos, cruzarlos con los pedidos y emitir los reembolsos pendientes.

```python
for phase in ["traer_pagos", "cruzar", "emitir_reembolsos"]:
    if phase in state["completed"]:
        continue                       # ya se hizo: se saltea
    if phase == "emitir_reembolsos":   # lo que sigue es irreversible
        save_checkpoint(state)         # se guarda ANTES de actuar
    state["outputs"][phase] = run_phase(phase, state)
    state["completed"].append(phase)
    save_checkpoint(state)             # se guarda al final de cada fase
```

Si el proceso se cae en la fase 3, al reiniciar no vuelve a traer ni a cruzar los pagos, y no repite los reembolsos ya emitidos.

### 10.4 Cuando el mundo cambió desde el checkpoint

**Qué es.** Entre que se guardó el checkpoint y que se retoma, el entorno puede haber cambiado. Si el proceso sigue como si nada, trabaja sobre supuestos falsos. Para detectarlo, el curso propone **state versioning** (versionado del estado): al guardar, se registra un **environment hash** (una huella del entorno, como un código que cambia si cambia algo). Al retomar se compara: si coincide, se sigue; si no coincide, se **marca un conflicto** en vez de seguir con datos viejos.

*Ejemplo:* el checkpoint del lunes se guardó con la configuración de la pasarela de pagos A. El martes, la pasarela es B. La huella no coincide, así que el proceso frena y avisa: "Conflicto: el entorno cambió desde el 16/11 a las 02:00".

### Para el examen

- 📘 Es contenido del curso. La guía lo evalúa de otra forma, en el Tema 11: **avisar qué archivos cambiaron** al retomar.
- Ideas que sirven para descartar opciones: guardar antes de lo irreversible, checkpoints por fase, no seguir con estado viejo sin avisar.

### Cómo se une

El environment hash del curso y el "avisar qué archivos cambiaron" de la guía (Tema 11) son la misma idea: **no seguir trabajando como si el mundo no hubiera cambiado**.

---

## Tema 11 — Sessions (sesiones): retomar, empezar de cero o bifurcar

### Qué es una sesión

Una **session** (sesión) es el historial completo de una conversación de trabajo con Claude: los prompts, las tool calls, los resultados y las respuestas. Claude Code y el Agent SDK la guardan en disco, así que se puede **retomar** más tarde y Claude vuelve a tener todo lo que se habló.

Lo importante es qué **no** guarda: una sesión guarda **la conversación, no los archivos**. Si el código cambió después, la sesión no se entera sola. Claude va a seguir creyendo que los archivos son como los leyó la última vez.

### El ejemplo que usamos en todo el tema

Sofía usa Claude Code para analizar el módulo de pagos (el legacy de 1B). El lunes trabaja dos horas: Claude mapea la estructura y encuentra las áreas de alto impacto. El martes quiere seguir. Durante la noche, Lucas cambió dos archivos: `RefundProcessor.cs` y `PaymentGateway.cs`.

### 11.1 Retomar una sesión por nombre (named session resumption)

Si Sofía quiere seguir el martes exactamente donde dejó, le conviene ponerle nombre a la sesión el lunes, así la encuentra sin buscar IDs:

```bash
claude -n pagos-analisis          # inicia una sesión llamada "pagos-analisis"
# (o, con la sesión abierta: /rename pagos-analisis)
```

El martes la retoma por nombre, con todo su historial:

```bash
claude --resume pagos-analisis    # retoma ESA sesión, con todo su historial
```

Hay otra opción que se confunde con esta: `--continue`. La diferencia es que `--continue` no te deja elegir; agarra la última sesión del directorio, sea cual sea.

| Comando | Qué retoma |
|---|---|
| `claude --resume <nombre>` | una sesión **específica**, la que elegís |
| `claude --continue` | la sesión **más reciente** del directorio, sin elegir |

En el Agent SDK es lo mismo con parámetros: `resume=<session_id>` para una sesión específica y `continue_conversation=True` para la más reciente. El `session_id` viene en el mensaje de resultado.

### 11.2 Avisar qué cambió

Como la sesión no sabe que Lucas cambió dos archivos, Sofía se lo dice al retomar:

```
Desde ayer, Lucas modificó RefundProcessor.cs y PaymentGateway.cs.
Volvé a analizar solo esos dos archivos y actualizá el mapa.
```

Esto se llama **targeted re-analysis** (re-análisis dirigido): Claude revisa solo lo que cambió, en vez de explorar todo el módulo de nuevo. Se aprovecha lo que sigue valiendo y se corrige solo lo que quedó viejo.

### 11.3 ¿Retomar o empezar de cero?

Retomar no siempre es lo mejor. Si casi todo lo que Claude leyó ya cambió, la sesión vieja trae más conclusiones falsas que útiles. La guía da un criterio claro:

- **Resume (retomar)** cuando el contexto anterior **sigue siendo mayormente válido**. Por ejemplo, si cambiaron 2 archivos de 40: se retoma y se avisa qué cambió.
- **Empezar una sesión nueva con un structured summary** (resumen estructurado) cuando los **tool results anteriores están stale** (desactualizados). Por ejemplo, si durante la noche se refactorizó medio módulo: el análisis del lunes ya no sirve.

Así se ve un resumen estructurado para la sesión nueva:

```
Contexto: análisis del módulo de pagos de TiendaX.
Hallazgos que siguen vigentes: los reembolsos y la conciliación son las áreas de mayor riesgo.
Lo que cambió: se refactorizó PaymentGateway y todo lo que lo usa.
Objetivo de esta sesión: volver a mapear las dependencias de PaymentGateway.
```

¿Por qué no retomar igual? Porque Claude seguiría razonando con resultados viejos que ya no son ciertos. Es menos confiable que arrancar de cero con un buen resumen. La documentación del Agent SDK dice lo mismo con otras palabras: guardar los resultados que necesitás como estado de tu aplicación y pasarlos en el prompt de una sesión nueva suele ser **más robusto** que depender de retomar la sesión.

**Cómo decidir en una pregunta.** Fijate en **qué proporción** de lo analizado cambió. Si cambiaron **pocos archivos** de muchos (2 de 40), conviene retomar y avisar cuáles cambiaron. Si cambió **la mayoría** (31 de 40, o un refactor grande que renombró paquetes), conviene una sesión nueva con un resumen estructurado de los objetivos y decisiones que siguen valiendo, y que Claude lea el código actual. En ese segundo caso, "retomar y listar los 31 archivos" tienta, pero el contexto viejo ya es mayormente stale: casi todo habría que re-analizarlo igual, y Claude seguiría arrastrando conclusiones sobre código que ya no existe.

| Cuánto cambió | Qué hacer |
|---|---|
| Pocos archivos de muchos (2 de 40) | **Resume + avisar cuáles cambiaron** |
| La mayoría (31 de 40, refactor grande) | **Sesión nueva con resumen estructurado** |

### 11.4 Fork (bifurcar)

Sofía ahora quiere comparar dos estrategias de tests: con **mocks** (objetos simulados) o con una base de datos real en un contenedor. Las dos parten del mismo análisis del lunes, y no quiere que lo que pruebe en una contamine la otra.

Para eso está **fork_session** (bifurcar la sesión). Crea una sesión **nueva** que arranca con una **copia** del historial y desde ahí va por su lado. El fork tiene su propio ID de sesión, y la sesión original queda intacta.

```bash
claude --resume pagos-analisis --fork-session   # rama A: estrategia con mocks
claude --resume pagos-analisis --fork-session   # rama B: base de datos en contenedor
```

En el SDK es `resume=<session_id>` con `fork_session=True`. Con la sesión abierta, `/branch` hace lo mismo. Igual que la sesión, el fork copia la **conversación**, no los archivos.

### Para el examen

- **`--resume <nombre>`**: retomar una sesión específica por nombre, por ejemplo para seguir una investigación entre jornadas.
- **Avisar qué archivos cambiaron** al retomar, para un re-análisis dirigido.
- **Resume** si el contexto sigue mayormente válido; **sesión nueva con resumen estructurado** si los tool results están desactualizados. Lo que decide es **cuánto** cambió (Tema 11.3).
- **`fork_session`**: para explorar **dos caminos distintos desde la misma base**, por ejemplo comparar dos estrategias de tests o de refactor.
- `--continue` retoma la más reciente; `fork` es para divergir, no para seguir en la misma línea.

### Cómo se une

Resume y fork resuelven el mismo problema que el **context isolation** del Tema 2, pero en el tiempo: qué contexto tiene el agente cuando arranca. En el Tema 2 se lo pasás en el prompt. Acá lo trae la sesión, y tenés que avisarle lo que la sesión no sabe.

---

## Cómo se une todo

Un **coordinator** reparte el trabajo entre **subagents** (Tema 1). Cada subagent arranca **sin el contexto del coordinador**, así que todo lo que necesita, incluidos los hallazgos completos de otros agentes, va en su prompt (Tema 2). Se configuran con **AgentDefinition**, y el coordinador los lanza con **Task**, que tiene que estar en sus **allowedTools** (Tema 3). Si las subtareas son independientes, se lanzan **en paralelo**, con varias llamadas a Task en la misma respuesta (Tema 4).

Al delegar, el coordinador **reparte sin superposición**, da **objetivos en vez de recetas**, elige **qué subagents usar** y **revisa los huecos** (Tema 5). Los resultados viajan como **datos estructurados**, con el contenido separado de las fuentes (Tema 6). Toda la comunicación pasa **por el coordinador**, y para un caso común costoso se usa una **tool acotada** (Tema 7). Los errores le llegan **con contexto** para que pueda decidir (Tema 8). Todo esto cuesta unas **15× tokens**, así que se usa solo cuando el trabajo es ancho e independiente (Tema 9).

Cuando el trabajo dura más de una sesión, se **retoma** por nombre avisando qué cambió, se **empieza de cero** con un resumen si el contexto está viejo, o se **bifurca** para comparar caminos (Temas 10 y 11).

## Lo que viene

Rosa pide un reembolso de USD 900. La política de TiendaX dice que los reembolsos de más de USD 500 necesitan la aprobación de un supervisor, y eso está escrito en el system prompt del subagent de reembolsos. El 97% de las veces se cumple, y el caso de Rosa cae en el otro 3%. En el capítulo 4 (1D · Reliability & Human Oversight) vas a ver cómo hacer que una regla de negocio se cumpla **siempre**, con código en lugar de un prompt.

---

## Las trampas del examen

Cada trampa tiene el mismo orden: la situación, **qué elegir en el examen (✅)**, las opciones que tientan (❌) con por qué tientan y por qué están mal, y una regla para recordar.

### Grupo: Lanzar subagents y pasarles contexto

#### Trampa 1 · El subagent no tiene la información

**La situación.** Un subagent pide datos que el coordinador ya tenía, o sintetiza sin los hallazgos de los agentes anteriores (Tema 2).

**✅ En el examen elegí:** pasar **todo explícitamente en el prompt** del subagent, incluidos los **hallazgos completos** de los agentes anteriores. Los subagents no heredan el historial del coordinador ni comparten memoria entre invocaciones.

**❌ Las que tientan:**

❌ **"El subagent tiene acceso al historial del coordinador; solo hay que decirle 'continuá'".**
- *Tienta porque:* parece que los agentes de un mismo sistema "comparten la conversación".
- *Está mal porque:* cada subagent arranca sin el historial del coordinador. Lo único que le llega del coordinador es su prompt.

❌ **"Pasarle un resumen corto, para ahorrar tokens".**
- *Tienta porque:* ahorra tokens.
- *Está mal porque:* la guía pide hallazgos **completos**. Un resumen pierde datos y atribución.

> 🧠 **Para recordar:** lo que no está en el prompt del subagent, para él no existe.

#### Trampa 2 · Las definiciones están bien, pero no se lanza ningún subagent

**La situación.** Los AgentDefinition tienen buenas descripciones, prompts y tools, pero el coordinador nunca delega (Tema 3).

**✅ En el examen elegí:** agregar **`"Task"` a `allowedTools`** del coordinador. Task es la tool que lanza los subagents.

**❌ Las que tientan:**

❌ **"Mejorar las `description` de los subagents".**
- *Tienta porque:* las descripciones deciden a quién delegar.
- *Está mal porque:* sin la tool Task, el coordinador no puede delegar en nadie, por buenas que sean las descripciones.

❌ **"Agregar al system prompt del coordinador: 'usá siempre los subagents'".**
- *Tienta porque:* parece ir directo al síntoma.
- *Está mal porque:* no podés pedirle que use una tool que no tiene habilitada.

> 🧠 **Para recordar:** sin Task en allowedTools, no hay subagents.

#### Trampa 3 · Los subagents corren uno detrás de otro

**La situación.** El coordinador lanza tres search independientes (zapatillas, ropa, electrónica) de a uno por turno, y la búsqueda tarda 9 minutos (Tema 4).

**✅ En el examen elegí:** que el coordinador emita **varias llamadas a Task en una sola respuesta**.

**❌ Las que tientan:**

❌ **"Lanzarlos en turnos sucesivos, para controlar mejor el orden".**
- *Tienta porque:* parece más ordenado.
- *Está mal porque:* así corren en serie. Para que corran en paralelo, las llamadas tienen que ir en la misma respuesta.

❌ **"Pasar a peer-to-peer para bajar la latencia".**
- *Tienta porque:* el curso dice que P2P tiene menos latencia.
- *Está mal porque:* la guía pide pasar todo por el coordinador, y la lentitud venía de no paralelizar.

> 🧠 **Para recordar:** paralelo es varias llamadas a Task en la misma respuesta.

### Grupo: Cómo trabaja el coordinador

#### Trampa 4 · Subagents que hablan entre sí o que tienen todas las tools

**La situación.** Lucas quiere que search le pase resultados directo a synthesis, y que synthesis tenga todas las tools de búsqueda para verificar datos (Tema 7).

**✅ En el examen elegí:** **pasar toda la comunicación por el coordinador** (observabilidad, errores consistentes, flujo controlado). Si hay una ronda costosa y repetida en el caso común, darle al subagent una **tool acotada** para ese caso (`verify_fact`), y que lo complejo siga pasando por el coordinador.

**❌ Las que tientan:**

❌ **"Comunicación directa entre subagents".**
- *Tienta porque:* baja la latencia, y el curso presenta P2P como válido.
- *Está mal porque:* se pierde la observabilidad y el control de errores. La guía exige el ruteo por el coordinador.

❌ **"Darle a synthesis todas las tools de búsqueda".**
- *Tienta porque:* resuelve todas las verificaciones de una vez.
- *Está mal porque:* sobre-aprovisiona y rompe la separación de responsabilidades. Least privilege es lo justo para el caso común.

❌ **"Juntar todas las verificaciones y hacerlas al final de la síntesis".**
- *Tienta porque:* menos rondas, sin cambiar la arquitectura.
- *Está mal porque:* los pasos siguientes de la síntesis necesitan datos ya verificados. Crea dependencias que bloquean.

❌ **"Que search cachee de antemano más contexto de cada fuente".**
- *Tienta porque:* parece anticiparse a las verificaciones.
- *Está mal porque:* no se puede prever qué habrá que verificar. Es caché especulativa.

> 🧠 **Para recordar:** todo pasa por el coordinador; para el caso común, una tool chica, no todas.

#### Trampa 5 · El informe perdió las fuentes

**La situación.** Synthesis cita datos sin poder decir de qué fuente salen (Tema 6).

**✅ En el examen elegí:** pasar el contexto en **datos estructurados que separen el contenido de la metadata** (URL, documento, página, fecha).

**❌ Las que tientan:**

❌ **"Pedirle a synthesis en el prompt que 'cite siempre las fuentes'".**
- *Tienta porque:* es un cambio rápido.
- *Está mal porque:* no puede citar lo que no recibió separado. El problema está en el formato del handoff.

❌ **"Pasar el texto completo de cada página".**
- *Tienta porque:* "más contexto, mejor".
- *Está mal porque:* infla el contexto y sigue mezclando contenido con metadata. ("Hallazgos completos" significa el hallazgo entero con su fuente, no la página cruda.)

> 🧠 **Para recordar:** contenido por un lado y de dónde salió por el otro.

#### Trampa 6 · Cómo instruye el coordinador

**La situación.** El coordinador da recetas paso a paso y siempre corre los tres subagents, incluso para preguntas simples (Tema 5).

**✅ En el examen elegí:** prompts con **objetivos y criterios de calidad** (no procedimientos), **selección dinámica** de subagents según la complejidad de la consulta, y un **loop de refinamiento** que busca huecos en la síntesis y vuelve a delegar con consultas dirigidas.

**❌ Las que tientan:**

❌ **"Instrucciones paso a paso, así el subagent no se desvía".**
- *Tienta porque:* parece más controlado y predecible.
- *Está mal porque:* el subagent no puede adaptarse a lo que encuentra.

❌ **"Correr siempre el pipeline completo, por consistencia".**
- *Tienta porque:* todas las consultas reciben el mismo tratamiento.
- *Está mal porque:* gasta tiempo y tokens en consultas que no lo necesitan. El coordinador tiene que elegir.

> 🧠 **Para recordar:** el coordinador dice qué lograr y cómo se mide, no cómo hacerlo.

#### Trampa 7 · Un subagent falla

**La situación.** El subagent de search hace timeout en un tema complejo (Tema 8).

**✅ En el examen elegí:** devolverle al coordinador un **error estructurado**: tipo de falla, consulta intentada, resultados parciales y alternativas. Así el coordinador decide si reintenta, cambia de enfoque o sigue con lo parcial.

**❌ Las que tientan:**

❌ **"Reintentar adentro del subagent y, si falla, devolver 'unavailable'".**
- *Tienta porque:* reintentar parece robusto.
- *Está mal porque:* el estado genérico esconde lo que el coordinador necesita para recuperarse.

❌ **"Devolver un resultado vacío marcado como éxito".**
- *Tienta porque:* el flujo sigue sin cortarse.
- *Está mal porque:* es un falso éxito. El informe sale con un hueco que nadie ve.

❌ **"Cortar todo el workflow con una excepción".**
- *Tienta porque:* parece lo más seguro.
- *Está mal porque:* la recuperación era posible.

> 🧠 **Para recordar:** el error viaja con contexto hasta quien puede decidir.

### Grupo: Sesiones

#### Trampa 8 · Retomar, empezar de cero o bifurcar

**La situación.** Sofía retoma el martes el análisis del lunes. Lucas cambió dos archivos durante la noche. Además, quiere comparar dos estrategias de tests (Tema 11).

**✅ En el examen elegí:**
- **`--resume <nombre>`** si el contexto sigue mayormente válido, **avisando qué archivos cambiaron** para que los vuelva a analizar.
- **Una sesión nueva con un resumen estructurado** si los tool results anteriores están desactualizados.
- **`fork_session`** para explorar dos enfoques distintos desde la misma base.

**❌ Las que tientan:**

❌ **"Retomar sin decir nada: el agente se va a dar cuenta de los cambios".**
- *Tienta porque:* la sesión "tiene todo".
- *Está mal porque:* la sesión guarda la conversación, no los archivos. El agente sigue razonando con lo viejo.

❌ **"Pedirle que vuelva a explorar todo el módulo".**
- *Tienta porque:* es lo más seguro.
- *Está mal porque:* si cambiaron dos archivos, alcanza con un re-análisis dirigido de esos dos.

❌ **"Retomar aunque casi todo el análisis esté desactualizado".**
- *Tienta porque:* parece más rápido que empezar de cero.
- *Está mal porque:* razonar sobre tool results viejos es menos confiable que arrancar con un resumen estructurado.

❌ **"`--continue` para retomar una sesión específica".**
- *Tienta porque:* suena a "continuar lo de ayer".
- *Está mal porque:* `--continue` retoma la **más reciente** del directorio, no la que elegís. Para una específica, `--resume <nombre>`.

❌ **"`fork_session` para seguir trabajando en la misma línea".**
- *Tienta porque:* crea una sesión que arranca con todo el historial.
- *Está mal porque:* fork sirve para **divergir** y comparar caminos. Para seguir en la misma línea, resume.

❌ **"Hacer un fork para limpiar el contexto o refrescar resultados viejos".**
- *Tienta porque:* el fork es una sesión nueva.
- *Está mal porque:* el fork **copia** el historial, incluidos los resultados viejos. Para empezar limpio hace falta una sesión nueva con un resumen.

❌ **"Usar `/compact` en vez de retomar la sesión".**
- *Tienta porque:* achica el contexto.
- *Está mal porque:* `/compact` resume el historial **dentro** de la sesión actual. No retoma una sesión anterior ni actualiza resultados viejos.

> 🧠 **Para recordar:** resume si sigue valiendo, y avisá qué cambió; fresh con resumen si está viejo; fork para comparar caminos.

### Grupo: Diseñar el sistema multi-agente

#### Trampa 9 · Multi-agente para todo

**La situación.** La gerencia quiere multi-agente también para el bot de código (Tema 9).

**✅ En el examen elegí:** multi-agente **solo** si el trabajo es realmente paralelo, cada rama se beneficia de su propio contexto y el resultado vale el costo (~15× tokens frente a un chat). Para trabajo acoplado, como casi todo el código, un solo agente.

**❌ Las que tientan:**

❌ **"Multi-agente siempre es más capaz".**
- *Tienta porque:* el sistema de investigación mejoró mucho con varios agentes.
- *Está mal porque:* en tareas acopladas, el costo de coordinación supera el beneficio.

> 🧠 **Para recordar:** varios agentes para trabajo ancho e independiente; uno solo para trabajo acoplado.

#### Trampa 10 · Limitar a un subagent con el prompt

**La situación.** El subagent de análisis solo debería leer documentos, pero tiene la tool de escritura (Tema 3).

**✅ En el examen elegí:** restringir las tools **por configuración** (`tools` en el AgentDefinition).

**❌ Las que tientan:**

❌ **"Agregar al prompt: 'no modifiques archivos'".**
- *Tienta porque:* es rápido y suele funcionar.
- *Está mal porque:* un prompt es probabilístico. Una tool que no está en la lista directamente no existe para el subagent.

> 🧠 **Para recordar:** los límites van en la configuración, no en la buena voluntad del modelo.

#### Trampa 11 · Dos subagents traen lo mismo

**La situación.** El coordinador lanzó search dos veces y las dos trajeron casi las mismas fuentes (Tema 5).

**✅ En el examen elegí:** **particionar el alcance** al delegar: cada subagent recibe un subtema distinto (zapatillas, ropa, electrónica) o un tipo de fuente distinto.

**❌ Las que tientan:**

❌ **"Deduplicar los resultados en synthesis".**
- *Tienta porque:* el informe final sale sin repeticiones.
- *Está mal porque:* ataca el síntoma. Se sigue pagando el trabajo duplicado, y lo que quedó sin cubrir sigue faltando.

❌ **"Usar menos subagents".**
- *Tienta porque:* menos agentes, menos superposición.
- *Está mal porque:* se pierde el paralelismo. El problema era el reparto, no la cantidad.

> 🧠 **Para recordar:** a cada subagent, un pedazo distinto del tema.

#### Trampa 12 · Al informe le faltan temas y cada subagent cumplió

**La situación.** El informe de devoluciones de la competencia cubre zapatillas, ropa y electrónica, pero no hogar ni juguetes, que TiendaX también vende. Los logs muestran que search, analysis y synthesis hicieron bien lo que les pidieron (Tema 1).

**✅ En el examen elegí:** **la descomposición del coordinador es demasiado estrecha.** Les asignó a los subagents un alcance que no cubría todo el tema.

**❌ Las que tientan:**

❌ **"Synthesis no tiene instrucciones para detectar huecos de cobertura".**
- *Tienta porque:* el hueco se ve en el informe final, que es lo que hace synthesis.
- *Está mal porque:* synthesis trabajó con lo que recibió. El hueco viene de antes.

❌ **"Las consultas de search no son lo bastante amplias".**
- *Tienta porque:* parece que "buscó poco".
- *Está mal porque:* search buscó exactamente lo que le asignaron.

❌ **"Analysis está filtrando las fuentes de otros rubros".**
- *Tienta porque:* podría explicar que falten datos.
- *Está mal porque:* no hay evidencia de eso, y el problema está antes, en el reparto.

> 🧠 **Para recordar:** si todos cumplieron y falta algo, el error está en el reparto del coordinador.

---

## Checklist oficial

**Tarea 1.2 — Coordinator-subagent patterns**

*Knowledge of*
- [x] Arquitectura hub-and-spoke donde el coordinador maneja toda la comunicación entre subagents, el manejo de errores y el ruteo de la información → **Tema 7**
- [x] Los subagents operan con contexto aislado: no heredan automáticamente el historial del coordinador → **Tema 2**
- [x] El rol del coordinador: descomposición, delegación, agregación de resultados y decidir qué subagents invocar según la complejidad → **Tema 1** (y Tema 5)
- [x] Riesgo de una descomposición demasiado estrecha que deja temas sin cubrir → **Tema 1** (Trampa 12; también 1B)

*Skills in*
- [x] Coordinadores que analizan la consulta y eligen dinámicamente a qué subagents invocar, sin correr siempre el pipeline completo → **Tema 5** (Trampa 6)
- [x] Particionar el alcance entre subagents para minimizar la duplicación (subtemas o tipos de fuente distintos) → **Tema 5** (Trampa 11)
- [x] Loops de refinamiento iterativo: el coordinador evalúa la síntesis buscando huecos y vuelve a delegar con consultas dirigidas → **Tema 5** (Trampa 6)
- [x] Rutear toda la comunicación de los subagents por el coordinador (observabilidad, errores consistentes, flujo controlado) → **Tema 7** (Trampa 4)

**Tarea 1.3 — Subagent invocation, context passing, and spawning**

*Knowledge of*
- [x] La tool Task como mecanismo para lanzar subagents, y que `allowedTools` debe incluir `"Task"` → **Tema 3** (Trampa 2)
- [x] El contexto del subagent se pasa explícitamente en el prompt: no hereda el contexto del padre ni comparte memoria entre invocaciones → **Tema 2** (Trampa 1)
- [x] La configuración AgentDefinition: descriptions, system prompts y restricción de tools por tipo de subagent → **Tema 3** (Trampa 10)
- [x] Manejo de sesiones con fork para explorar enfoques divergentes desde una base compartida → **Tema 11**

*Skills in*
- [x] Incluir los hallazgos completos de agentes anteriores en el prompt del subagent → **Tema 2** (Trampa 1)
- [x] Datos estructurados que separan contenido de metadata (URLs, documentos, páginas) para preservar la atribución → **Tema 6** (Trampa 5)
- [x] Lanzar subagents en paralelo con varias llamadas a Task en una sola respuesta del coordinador → **Tema 4** (Trampa 3)
- [x] Prompts del coordinador con objetivos y criterios de calidad, no procedimientos paso a paso → **Tema 5** (Trampa 6)

**Tarea 1.7 — Session state, resumption, and forking**

*Knowledge of*
- [x] Retomar sesiones por nombre con `--resume <session-name>` → **Tema 11**
- [x] `fork_session` para crear ramas independientes desde una base de análisis compartida → **Tema 11**
- [x] Avisarle al agente qué archivos cambiaron al retomar una sesión → **Tema 11** (Trampa 8)
- [x] Por qué una sesión nueva con un resumen estructurado es más confiable que retomar con tool results desactualizados → **Tema 11** (Trampa 8)

*Skills in*
- [x] Usar `--resume` con nombres de sesión para seguir investigaciones entre jornadas de trabajo → **Tema 11**
- [x] Usar `fork_session` para ramas de exploración en paralelo (por ejemplo, dos estrategias de tests) → **Tema 11**
- [x] Elegir entre resume (contexto mayormente válido) y empezar de cero con un resumen (tool results desactualizados) → **Tema 11** (Trampa 8)
- [x] Avisar a la sesión retomada qué archivos cambiaron, para un re-análisis dirigido en vez de explorar todo → **Tema 11**

**📘 Curso (útil para entender; lecciones 13–20 y deck 131):** agregación collect → validate → synthesize, registro de decisiones (Tema 1) · pass explicitly / withhold by default (Tema 2) · authority boundary: least privilege, explicit boundaries, no side effects (Tema 3) · narrow scope, output format, success criteria y los tres anti-patterns de subagents (Tema 5) · handoff schema, under/over-specified, versionado y migration adapter, contract tests, ACK, substitutability, audit log (Tema 6) · las cuatro topologías, elección por flujo de datos, hub without hierarchy, P2P without audit trail, topologías híbridas (Tema 7) · transparent vs. silent failure, swallowing y undifferentiated errors, retry → substitute → escalate (Tema 8) · costo 4×/15× y 3–10×, de dónde sale el costo, fit rule, modelos más livianos (Tema 9) · in-context vs. external memory, tipos de store, hot/cold tiers, reconstructable state, memory hygiene, checkpoints (cuándo, contenido mínimo, coarse vs. fine-grained, recuperación), state versioning con environment hash (Tema 10).

---

## Autoevaluación oral

1. ¿Qué recibe un subagent cuando lo lanzan, y qué **no** recibe? ¿Qué tiene que llevar su prompt?
2. Las definiciones de los subagents están bien, pero el coordinador nunca delega. ¿Qué revisás primero? ¿Y si los subagents corren en serie?
3. ¿Por qué la guía pide pasar toda la comunicación por el coordinador? ¿Qué hacés si eso agrega mucha latencia en un caso común?
4. ¿Cómo le pasás a synthesis los hallazgos de search sin perder las fuentes?
5. Retomás el análisis de ayer y cambiaron dos archivos. ¿Resume, sesión nueva o fork? ¿Qué cambia si lo que cambió es medio módulo? ¿Y si querés comparar dos enfoques?

---

## Preguntas tipo examen

Las preguntas tipo examen de este capítulo están en [`04-practica/modulo-1.md`](../04-practica/modulo-1.md), junto con las del resto del módulo 1. Hacelas cuando termines **todos** los capítulos del módulo, de a una y sin mirar la respuesta.

---

## Revisión contra el blueprint oficial

Qué puede salir en el examen de 1.2, 1.3 y 1.7 que el curso de Jacob **no cubre o cubre flojo**, y dónde quedó explicado acá. (Las slides de 1C no nombran nada del Agent SDK: ni Task, ni `allowedTools`, ni `AgentDefinition`, ni sesiones.)

1. **La tool Task y `"Task"` en `allowedTools`** (1.3). El curso no la nombra. Es la respuesta cuando las definiciones están bien y el coordinador no delega. En la documentación actual se llama `Agent`; en el examen, **Task**. → Tema 3, Trampa 2.
2. **`AgentDefinition`: `description` + `prompt` + `tools`** (1.3). El curso solo filtra tools a mano en el código. Si se omite `tools`, el subagent hereda todas. → Tema 3, Trampa 10.
3. **Paralelismo = varias llamadas a Task en una sola respuesta**, no en turnos separados (1.3). El curso no lo detalla. Solo vale si las subtareas son independientes. → Tema 4, Trampa 3.
4. **Hallazgos completos en el prompt del subagent** (1.3). El curso pone "outputs from other subagents" en lo que se retiene por defecto; la guía pide pasarlos completos cuando el subagent los necesita. → Tema 2 (recuadro), Trampa 1.
5. **Datos estructurados que separan contenido de metadata** (URL, documento, página) para preservar la atribución (1.3). El handoff schema del curso (task/context/output_format/constraints) no habla de fuentes. → Tema 6, Trampa 5.
6. **Dynamic selection** (1.2): el coordinador invoca solo los subagents que la consulta necesita. El curso no lo tiene. → Tema 5.3, Trampa 6.
7. **Iterative refinement loop** (1.2): el coordinador busca huecos en la síntesis y re-delega con consultas dirigidas. El curso no lo tiene. → Tema 5.4, Trampa 6.
8. **Objetivos y criterios de calidad, no procedimientos paso a paso** (1.3). El curso pide alcance, formato y criterio de éxito, pero no contrapone "objetivo vs. receta". → Tema 5.2, Trampa 6.
9. **Sesiones: `--resume <nombre>`, `fork_session`, avisar qué archivos cambiaron y sesión nueva con resumen estructurado** (1.7). El curso solo trata checkpoints genéricos. La decisión depende de **cuánto** cambió (la P5 del módulo). → Tema 11, Trampa 8.
10. **Las tres preguntas oficiales del escenario Multi-Agent Research System:** Q7 (descomposición demasiado estrecha; el curso no la menciona) → Tema 1, Trampa 12 · Q8 (error estructurado con tipo, consulta, parciales y alternativas; la guía la asigna a 5.3) → Tema 8, Trampa 7 · Q9 (`verify_fact`, tool acotada; la guía la asigna a 2.3) → Tema 7, Trampa 4.
11. **Solo de la documentación, no de la guía:** campos opcionales de `AgentDefinition` (`model`, `maxTurns`…) y subagents que lanzan subagents. Conviene reconocerlos, pero no esperes que sean la respuesta central. → Tema 3.

No encontré otros huecos para estas tres tareas. Lo que el curso agrega por su cuenta (topologías pipeline y peer-to-peer, handoff schema, ACK, versionado, checkpoints, hot/cold tiers, environment hash) queda marcado como 📘: es útil, pero no es la respuesta "oficial". Y peer-to-peer, en el examen, es distractor.

