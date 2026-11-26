# Capítulo 16 · 5B · Udemy 17 — Escalation and Error Propagation (cuándo escalar y cómo propagar errores)

*Tareas oficiales 5.2 y 5.3 · Segundo capítulo del módulo 5*

---

## Dónde estamos

Seguimos en el **módulo 5: Context Management & Reliability**. 5A ya está escrito. Este capítulo cubre dos tareas, de 2,5% cada una:
- **5.2** Design effective escalation and ambiguity resolution patterns (decidir cuándo escalar a una persona y cómo resolver la ambigüedad).
- **5.3** Implement error propagation strategies across multi-agent systems (cómo viajan los errores entre agentes).

### Cómo leer este capítulo

Todo lo que leés acá **vale para el examen**, salvo que diga lo contrario. Cuando algo sale solo del curso (útil para entender, pero no central), lo marco con **📘 Curso**. Cuando Jacob dice algo distinto de lo que evalúa la guía, aparece un recuadro así:

> ⚠️ **En el curso vas a escuchar otra cosa.** … **Para el examen: …**

### Un aviso sobre este capítulo

Este capítulo tiene **dos preguntas oficiales de muestra**: la **Q3** (calibrar el escalamiento) y la **Q8** (cómo vuelve un error al coordinador). Las dos ya aparecieron en el libro y acá se cierran.

Ojo con un punto: **el curso usa la confianza del modelo como disparador para escalar**, y la guía dice exactamente lo contrario. Además, al curso le faltan varios comportamientos concretos que la guía pregunta:
- Escalar ya cuando el cliente pide una persona.
- Qué hacer cuando el cliente está frustrado.
- Qué hacer cuando la política no dice nada sobre el pedido.
- Pedir más datos cuando hay varias coincidencias.
- Las anotaciones de cobertura en la síntesis.

Todo eso sale de la guía.

## De dónde venimos

Varias piezas ya las viste:
- **1D:** el **handoff** estructurado a un humano y la regla de "si tiene que cumplirse siempre, va en código (un hook)".
- **2A:** los **errores estructurados** de una tool (`isError`, la categoría del error, si se puede reintentar) y la diferencia entre "no pude buscar" y "no hay resultados".
- **1C:** que el coordinador solo ve lo que el subagente le devuelve.

Este capítulo las junta en dos preguntas. **¿Cuándo tiene que parar el agente y pasarle el caso a una persona?** Y **cuando un subagente falla, ¿qué le cuenta al coordinador?**

## Mapa del capítulo

**Parte 1 — Escalamiento y ambigüedad (tarea 5.2).**
1. Los tres disparadores correctos para escalar.
2. Pedido explícito de una persona vs. cliente frustrado.
3. Cuando la política no dice nada.
4. Disparadores que no sirven: sentimiento y confianza.
5. Varias coincidencias: pedir más datos.

**Parte 2 — Propagación de errores entre agentes (tarea 5.3).**

6. El contexto de error estructurado (Q8).
7. Falla de acceso vs. resultado vacío válido.
8. Recuperar localmente y propagar lo que no se puede resolver.
9. Anotaciones de cobertura en la síntesis.

---

# Parte 1 — Escalamiento y ambigüedad

## Tema 1 — Escalation triggers (disparadores de escalamiento): los tres correctos

### Qué es

**Escalar** es pasarle el caso a una persona. SoporteBot tiene una tool para eso (`escalate_to_human`), y la pregunta es **cuándo** usarla. Si escala de más, la resolución en el primer contacto se cae y el equipo humano se satura. Si escala de menos, se queda con casos que no le corresponden y los resuelve mal.

La guía nombra **tres disparadores** correctos:
1. **El cliente pide una persona.** Es su decisión, y se respeta.
2. **Una excepción o un hueco de la política.** Una **policy exception** (excepción a la política) es un caso que podría merecer algo que la política normalmente no da, y el agente no tiene autoridad para concederlo (por ejemplo, un cliente con un problema serio que pide un reembolso fuera de plazo y alega circunstancias especiales). Un **policy gap** (hueco) es cuando la política no dice nada o es ambigua sobre ese caso. En los dos, decidir le corresponde a una persona. Ojo: si el pedido simplemente está fuera de la política y la política ya da la respuesta, el agente lo rechaza (Tema 3).
3. **No poder avanzar de forma significativa.** El agente **lo intentó de verdad** y está trabado: las tools no le dan lo que necesita o da vueltas sin progresar. "Quizás no pueda" no alcanza; tiene que haber un intento real que falló. (📘 Curso: Jacob lo llama **retry ceiling**: después de 2 o 3 intentos fallidos, escalar con el registro de lo intentado.)

La guía agrega una aclaración importante: **"not just complex cases"**. Que un caso sea complejo **no** es motivo suficiente para escalar. Si la política lo cubre, el agente lo resuelve, aunque tenga varios pasos.

### Ejemplo

Es la pregunta oficial **Q3**, que ya viste en 1D y en 4B. SoporteBot tiene 55% de resolución en el primer contacto y el objetivo es 80%. Escala casos simples (un cambio por producto dañado con foto) y se queda con casos que necesitan una excepción a la política. Los límites de decisión no están claros. La respuesta correcta es **agregar al system prompt criterios explícitos de escalamiento con ejemplos** (few-shot) de cuándo escalar y cuándo resolver. Es lo proporcionado: arreglar el prompt antes de agregar infraestructura.

### Cómo se configura

```xml
<escalation_criteria>
Escalá con escalate_to_human cuando:
- El cliente pide hablar con una persona.
- El pedido necesita una excepción a la política, o la política no cubre el caso.
- Intentaste resolverlo y no podés avanzar.
No escales solo porque el caso tiene varios pasos o el cliente está molesto.
</escalation_criteria>

<examples>
<example>
Cliente: "Llegó rota la taza, te mando la foto."
Decisión: resolver. Daño en el envío con evidencia: la política cubre el cambio.
</example>
<example>
Cliente: "Compré hace 45 días, tuve una internación y no pude reclamar antes. ¿Me devuelven la plata?"
Decisión: escalar. Es fuera de plazo con una circunstancia especial: es una excepción, la decide una persona.
</example>
<example>
Cliente: "Quiero devolver esto, lo compré hace 60 días."
Decisión: resolver (rechazar). La política dice 30 días y no hay nada especial: se explica el motivo.
</example>
</examples>
```

📘 Curso: Jacob recomienda darle al agente una tool explícita para pedir ayuda (en SoporteBot, `escalate_to_human`). Lo que calibra **cuándo** la llama son los criterios con ejemplos.

### Para el examen

- Escalar cuando: **el cliente pide una persona**, hay una **excepción o un hueco de política**, o el agente **no puede avanzar**.
- Un caso complejo pero cubierto por la política **no** se escala.
- Escalamiento mal calibrado (Q3) → **criterios explícitos + ejemplos en el system prompt**.

### Cómo se une

El primer disparador, el pedido del cliente, tiene un matiz que el examen pregunta mucho: no es lo mismo que el cliente **pida** una persona que que esté **enojado**.

---

## Tema 2 — Explicit request vs. frustration (pedido explícito vs. cliente frustrado)

### Qué es

La guía distingue dos situaciones que se parecen, pero se resuelven distinto.

**El cliente pide explícitamente una persona** ("quiero hablar con alguien de verdad"). Se escala **inmediatamente**, **sin investigar primero**. No hace falta buscar el pedido ni intentar resolver antes: el cliente ya decidió, y hacerlo esperar lo frustra más.

**El cliente está frustrado, pero no pidió una persona**, y el problema **está dentro de lo que el agente puede resolver**. El agente **reconoce la frustración** y **ofrece resolverlo**. Escala solo si el cliente **reitera** que quiere hablar con una persona.

| Situación | Qué hace el agente |
|---|---|
| "Quiero hablar con una persona" | Escala ya, sin investigar |
| "¡Es la tercera vez que les escribo, qué desastre!" (caso simple) | Reconoce la frustración y ofrece resolver |
| El cliente frustrado insiste: "No, quiero una persona" | Escala |

### Ejemplo

Un cliente escribe: "¡Otra vez me llegó mal el pedido! Siempre lo mismo con ustedes". El problema es un cambio de talle, que SoporteBot resuelve en dos pasos. SoporteBot responde: "Entiendo que es frustrante que te pase de nuevo. Te gestiono el cambio ahora mismo: ¿me confirmás el talle que necesitás?". Si el cliente contesta "No, quiero que me atienda una persona", SoporteBot escala.

### El traspaso: qué recibe la persona

Cuando el agente escala, la persona que toma el caso **no ve la conversación**. Por eso, como viste en 1D, el escalamiento lleva un **resumen estructurado**: el ID del cliente, la causa del problema, el monto si lo hay y la acción recomendada. Escalar "ya" significa mandar ese resumen **con lo que ya se sabe**, no investigar más para completarlo.

📘 Curso: Jacob arma el **handoff payload** con cuatro campos: un resumen de la conversación, la pregunta que disparó el escalamiento (textual), lo que se intentó (tool, argumentos, resultado) y el siguiente paso sugerido. Y advierte contra el "narrative dump": pegar el transcript completo o un texto largo, que obliga a la persona a releer todo. Para el examen, la opción correcta es el **resumen estructurado**; pasar el transcript entero es un distractor.

### Para el examen

- Pedido **explícito** de una persona → **escalar ya**, sin investigar primero.
- Frustración en un caso resoluble → **reconocer y ofrecer resolver**; escalar si **reitera**.
- Distractores: investigar antes de honrar el pedido explícito, o escalar apenas el cliente se enoja.

### Cómo se une

El segundo disparador es la política. Ahí hay una diferencia fina entre que la política diga "no" y que no diga nada.

---

## Tema 3 — Policy gaps (huecos de la política): cuando la política no dice nada

### Qué es

Hay tres casos posibles cuando un cliente pide algo:
- **La política lo permite.** El agente lo resuelve.
- **La política lo prohíbe de forma clara** y no hay ninguna circunstancia especial. El agente lo **rechaza** y explica por qué. No hace falta escalar: la política ya tiene la respuesta. (Si el cliente plantea algo que podría justificar una excepción, eso sí se escala: Tema 1.)
- **La política es ambigua o no dice nada** sobre ese pedido. Ahí el agente **escala**, porque no tiene una regla para aplicar y decidir sería inventar la política.

El ejemplo de la guía es el **price matching** (igualar precios). La política de la tienda solo habla de ajustar el precio si **la propia tienda** lo bajó después de la compra. Si el cliente pide que le igualen el precio de **un competidor**, la política no dice nada sobre ese caso. Hay que escalar.

### Ejemplo

Un cliente de TiendaX escribe: "Compré la heladera a $900.000 y en otra tienda está a $820.000. ¿Me devuelven la diferencia?". La política de TiendaX dice: "Si TiendaX baja el precio dentro de los 7 días posteriores a la compra, se devuelve la diferencia". No dice nada de competidores. SoporteBot escala. En cambio, si el cliente pidiera devolver un producto a los 60 días y la política dice claramente "hasta 30 días", SoporteBot lo rechaza él mismo.

### Para el examen

- La política **no cubre** el pedido (ambigua o silenciosa) → **escalar**.
- La política **lo prohíbe claramente** → el agente **rechaza**; no escala.
- La política lo permite → el agente resuelve, aunque el caso sea complejo.

### Cómo se une

Esos son los disparadores correctos. El examen también pone disparadores que suenan razonables pero no sirven.

---

## Tema 4 — Disparadores que no sirven: sentimiento y confianza

### Qué es

La guía dice que hay dos señales que **no son buenas para decidir cuándo escalar**, porque no indican qué tan complejo es el caso:
- **Sentiment analysis** (análisis de sentimiento): medir qué tan enojado está el cliente. El enojo no dice nada de la complejidad. Un cliente furioso puede tener un problema de un paso, y uno amable puede pedir una excepción.
- **Self-reported confidence** (la confianza que el modelo se asigna): pedirle a Claude un puntaje de 1 a 10 y escalar si es bajo. Esa confianza está **mal calibrada**: el agente ya está seguro, equivocadamente, justo en los casos difíciles. Por eso se queda con ellos.

También es un distractor de la Q3 **entrenar un clasificador aparte** con tickets históricos: es excesivo antes de probar con el prompt.

> ⚠️ **En el curso vas a escuchar otra cosa.** Jacob propone un "confidence gate": si la confianza del modelo baja de un umbral (por ejemplo 0,7), se escala. Lo presenta como un "soft trigger" calibrable. **Para el examen:** la confianza **autoinformada** del modelo **no** es un disparador confiable para escalar (guía 5.2 y Q3). Si una opción dice "escalar cuando el modelo reporta confianza baja", es un distractor. (En 4C y 5D vas a ver que la confianza **sí** sirve para **enrutar revisiones**, pero solo con umbrales **calibrados** contra casos conocidos. Es otro uso.)

Una aclaración que conecta con 1D. Jacob también dice que los disparadores "duros" (un monto máximo, una acción destructiva) se ponen en el system prompt "sin juicio del modelo". Pero una regla en el prompt sigue siendo probabilística. Si una regla **tiene que cumplirse siempre**, por ejemplo "ningún reembolso de más de USD 500 sin aprobación", va en **código**: un hook que bloquea la acción y redirige a escalamiento.

### Para el examen

- Escalar por **sentimiento** o por **confianza autoinformada** → distractores.
- Clasificador entrenado aparte como primer paso → excesivo.
- Regla de escalamiento que tiene que cumplirse **siempre** → **hook o validación en código**, no solo el prompt.

### Cómo se une

La última parte de 5.2 no es sobre escalar sino sobre otro tipo de ambigüedad: cuando no está claro **de quién** es el pedido.

---

## Tema 5 — Multiple matches (varias coincidencias): pedir más datos

### Qué es

SoporteBot busca al cliente con `get_customer("Juan Pérez")` y la tool devuelve **tres clientes** con ese nombre. ¿Qué hace?

La guía es clara: **pedir identificadores adicionales al cliente** (el email, el DNI, el número de un pedido) y **no elegir por heurística**. Elegir "el más reciente" o "el que más compra" es adivinar, y si se equivoca, SoporteBot le muestra a una persona los datos de otra, o hace un reembolso en la cuenta equivocada.

Tampoco se escala: el agente puede resolver la ambigüedad solo, preguntando.

### Ejemplo

SoporteBot responde: "Encontré más de una cuenta con ese nombre. ¿Me pasás el email con el que hiciste la compra o el número de pedido?". Con el email, `get_customer` devuelve un solo resultado y sigue.

### Para el examen

- Varias coincidencias → **pedir un identificador más**.
- Distractores: elegir por heurística (el más reciente, el más activo, el primero), o escalar a una persona.

### Cómo se une

Hasta acá, cómo decide el agente que habla con el cliente. La tarea 5.3 mira hacia adentro: qué pasa cuando **un agente interno falla**.

---

# Parte 2 — Propagación de errores entre agentes

## Tema 6 — Structured error context (contexto de error estructurado)

### Qué es

En un sistema con coordinador y subagentes, cuando un subagente falla, el coordinador tiene que decidir qué hacer:
- Reintentar con otra consulta.
- Usar otra fuente.
- Seguir con lo que tiene.

Para decidir bien necesita información. La guía pide que el subagente devuelva un **contexto de error estructurado** con cuatro cosas:
1. **El tipo de falla** (timeout, sin permiso, fuente caída).
2. **Qué se intentó** (la consulta exacta).
3. **Los resultados parciales** que sí obtuvo.
4. **Las alternativas posibles** (otra fuente, una consulta más acotada).

Un estado genérico como "search unavailable" (búsqueda no disponible) **esconde todo eso**: el coordinador no sabe si conviene reintentar, cambiar de enfoque o seguir.

### Ejemplo

Es la pregunta oficial **Q8**. El subagente de búsqueda web hace un timeout mientras investiga un tema complejo. ¿Cómo vuelve esa falla al coordinador?

- **✅ Correcta:** devolver el tipo de falla, la consulta intentada, los resultados parciales y las alternativas.
- **❌ Reintentar con backoff dentro del subagente y, si se agotan los reintentos, devolver "search unavailable".** El reintento está bien; lo que está mal es el estado genérico del final.
- **❌ Capturar el timeout y devolver una lista vacía marcada como éxito.** Esconde el error: el coordinador cree que no había nada.
- **❌ Propagar la excepción a un manejador que termina todo el flujo.** Una falla sola no justifica perder todo el trabajo.

```json
{
  "failure_type": "timeout",
  "attempted_query": "precios de heladeras no frost en Argentina 2026",
  "partial_results": [{"source": "comparador-A", "price_range": "$780.000–$950.000"}],
  "alternatives": ["consultar el informe de la Cámara de Comercio", "acotar la búsqueda a 3 marcas"]
}
```

📘 Curso: Jacob llama a esto el **propagation contract** (el contrato de propagación). Sus campos se corresponden en parte con los de la guía: `error_type` es el tipo de falla, `recovery_hint` son las alternativas y `completed_steps` se parece a los resultados parciales (aunque la guía habla de **resultados**, no de pasos). El curso no pide la consulta intentada, y agrega severidad e identificadores de traza, que sirven para el monitoreo. También propone una prueba para decidir qué subir: "¿cambia el alcance, el orden o los recursos del coordinador?". Y si el error es fatal, frena **la cadena de tareas que depende de ese paso**, no todo el flujo. Para el examen, la respuesta correcta nombra los **cuatro campos de la guía**.

### Para el examen

- Falla de un subagente → **tipo de falla + qué se intentó + resultados parciales + alternativas**.
- Distractores de Q8: estado genérico, vacío como éxito, terminar todo el flujo.

### Cómo se une

El caso "vacío como éxito" lleva a la distinción más importante de esta tarea: que una búsqueda **no encuentre nada** es muy distinto de que **no se haya podido hacer**.

---

## Tema 7 — Access failure vs. valid empty result (falla de acceso vs. resultado vacío válido)

### Qué es

Ya lo viste en 2A con las tools. Hay dos situaciones que pueden terminar en "no hay datos":
- **Valid empty result** (resultado vacío válido): la búsqueda **se hizo** y **no encontró** coincidencias. Es una respuesta: "este cliente no tiene reclamos previos". No se reintenta, porque va a dar lo mismo.
- **Access failure** (falla de acceso): la búsqueda **no se pudo hacer** (timeout, sin permiso, servicio caído). No es una respuesta. Alguien tiene que **decidir** qué hacer: reintentar, usar otra fuente o seguir sin ese dato.

Si una falla de acceso se devuelve como lista vacía, el coordinador cree que "no había nada" y toma una decisión equivocada con total seguridad. El curso lo llama **the silent bug** (el bug silencioso): nada falla a la vista, pero el resultado es falso.

📘 Curso: Jacob propone que el wrapper de cada tool devuelva siempre un **status** con cuatro valores: `success`, `empty_result`, `partial_result` y `access_failure`. Así el que recibe nunca tiene que adivinar qué significa una lista vacía.

### Ejemplo

El subagente de antecedentes consulta el sistema de fraude para un cliente. El sistema hace un timeout y el subagente devuelve `[]`. El coordinador lee "sin alertas de fraude" y aprueba un reembolso de $450.000. Con el status correcto (`access_failure`, `failure_type: timeout`), el coordinador habría reintentado o frenado el reembolso hasta tener el dato.

### Para el examen

- La búsqueda se hizo y no encontró nada → **resultado vacío válido**; no se reintenta.
- La búsqueda no se pudo hacer → **falla de acceso**; se informa como falla, **nunca como vacío**.

### Cómo se une

Ahora, ¿quién maneja cada falla? No todas tienen que llegar al coordinador.

---

## Tema 8 — Local recovery (recuperar localmente) y propagar lo que no se puede resolver

### Qué es

Si cada pequeño error subiera al coordinador, el coordinador pasaría el tiempo atendiendo problemas menores. La guía pide que **cada subagente recupere localmente las fallas transitorias** y **propague solo lo que no puede resolver**, junto con lo que intentó y los resultados parciales.

- **Falla transitoria** (timeout, límite de requests, error 5xx del servidor): el subagente reintenta él mismo, con un límite.
- **Falla que no se arregla reintentando** (credencial revocada, sin permiso, la fuente no existe): se propaga **enseguida** con su contexto. Esperar no arregla un permiso. Es lo mismo que viste en 2A con `isRetryable`, y el companion del curso también lo dice: clasificar el error como reintentable o no antes de reintentar.

La guía marca **dos anti-patrones opuestos**:
- **Suprimir el error** (devolver vacío como éxito): el sistema sigue con datos falsos.
- **Terminar todo el flujo** por una sola falla: se pierde todo el trabajo que sí salió bien. Lo correcto es seguir con lo que se tiene y retomar desde donde se cortó.

### Ejemplo

El agente de investigación de TiendaX usa cinco subagentes. El de la fuente B tiene un timeout: reintenta dos veces y en la tercera funciona; el coordinador ni se entera. El de la fuente D recibe "credencial vencida": no reintenta y le devuelve al coordinador el tipo de falla, la consulta y la sugerencia de usar la fuente E. El coordinador sigue con cuatro fuentes y lanza la E. Nadie terminó el flujo.

### Para el examen

- Falla transitoria → **reintento local con límite**. Si no se resuelve, se propaga con contexto.
- Falla de permiso o autenticación → **propagar ya**, sin reintentar.
- **Ni suprimir el error ni terminar todo el flujo.**
- Propagar cada error menor al coordinador → también es un error de diseño.

### Cómo se une

Si una fuente no estuvo disponible y el sistema siguió sin ella, el resultado final tiene que decirlo. Eso es lo último de 5.3.

---

## Tema 9 — Coverage annotations (anotaciones de cobertura) en la síntesis

### Qué es

Cuando el sistema sigue adelante sin alguna fuente, el informe final **no puede presentarse como completo**. La guía pide que la síntesis incluya **anotaciones de cobertura**:
- Qué hallazgos están **bien respaldados** (varias fuentes, datos firmes).
- Qué temas tienen **huecos** porque una fuente no estuvo disponible.

Así quien lee el informe sabe qué tan sólido es cada parte, en vez de creer que todo está igual de verificado.

Un detalle que conecta con 1C: las anotaciones **reportan** huecos causados por fuentes que fallaron. No arreglan un problema de descomposición. Si el coordinador nunca le pidió a nadie investigar un tema (la Q7 de 1C), la solución es corregir cómo el coordinador reparte el trabajo, no anotar.

### Ejemplo

El informe de mercado de TiendaX termina con:

```markdown
## Cobertura
- Precios de heladeras: bien respaldado (4 fuentes coinciden).
- Lavarropas: respaldo parcial (2 fuentes).
- Aires acondicionados: SIN DATOS: la fuente principal (Informe D) no estuvo disponible por un error de acceso.
```

### Para el examen

- Síntesis con fuentes que fallaron → **anotar qué está bien respaldado y qué temas tienen huecos**.
- Distractores: rellenar el tema con material débil para que no quede vacío, u omitir el tema sin decir nada.

---

## Cómo se une todo

Para escalar hay **tres disparadores**: el cliente pide una persona, la política tiene una excepción o un hueco, o el agente no puede avanzar. "Complejo" no alcanza (Tema 1). Un pedido explícito se honra **ya**. Un cliente frustrado con un caso resoluble recibe una oferta de solución, y se escala si insiste (Tema 2). Si la política no dice nada, se escala; si dice que no, el agente rechaza (Tema 3). El sentimiento y la confianza autoinformada **no** sirven como disparadores: lo que calibra el escalamiento son **criterios explícitos con ejemplos** (Tema 4). Y con varias coincidencias se **piden más datos**, no se adivina (Tema 5).

Cuando un subagente falla, devuelve **tipo de falla, qué intentó, resultados parciales y alternativas** (Tema 6). Una falla de acceso **nunca** se devuelve como vacío (Tema 7). Lo transitorio se recupera localmente, y se propaga solo lo que no se puede resolver: ni suprimir ni terminar todo (Tema 8). Y el informe final dice qué está respaldado y qué tiene huecos (Tema 9).

## Lo que viene

**5C · Udemy 18 — Context Efficiency for Large Codebases**, tarea 5.4: cómo manejar el contexto cuando Claude Code explora un codebase grande (scratchpads, subagentes de exploración, `/compact` y recuperación después de un corte).

---

## Las trampas del examen

Cada trampa tiene el mismo orden: la situación, **qué elegir en el examen (✅)**, las opciones que tientan (❌) con por qué tientan y por qué están mal, y una regla para recordar.

### Grupo: Escalamiento (tarea 5.2)

#### Trampa 1 · Calibrar el escalamiento (Q3)

**La situación.** SoporteBot escala casos simples y se queda con casos que necesitan una excepción. La resolución en el primer contacto está en 55% (Tema 1).

**✅ En el examen elegí:** **criterios explícitos de escalamiento en el system prompt, con ejemplos de cuándo escalar y cuándo resolver**.

**❌ Las que tientan:**

❌ **"Que el agente se asigne un puntaje de confianza y escalar si es bajo".**
- *Tienta porque:* el curso lo enseña como "confidence gate".
- *Está mal porque:* la confianza autoinformada está mal calibrada; el agente ya está seguro en los casos difíciles.

❌ **"Escalar cuando el análisis de sentimiento detecta frustración".**
- *Tienta porque:* los clientes enojados parecen casos difíciles.
- *Está mal porque:* el enojo no indica la complejidad del caso.

❌ **"Entrenar un clasificador con tickets históricos".**
- *Tienta porque:* parece robusto.
- *Está mal porque:* es excesivo antes de probar con el prompt.

> 🧠 **Para recordar:** límites poco claros = **criterios + ejemplos**.

#### Trampa 2 · "Quiero hablar con una persona"

**La situación.** Un cliente escribe: "Quiero hablar con una persona, por favor". Su problema parece simple (Tema 2).

**✅ En el examen elegí:** **escalar inmediatamente, sin investigar primero**.

**❌ Las que tientan:**

❌ **"Buscar primero el pedido para pasarle más contexto al humano".**
- *Tienta porque:* el humano recibiría más información.
- *Está mal porque:* la guía dice escalar sin investigar primero; el cliente ya decidió.

❌ **"Ofrecerle resolverlo, ya que el caso es simple".**
- *Tienta porque:* subiría la resolución en el primer contacto.
- *Está mal porque:* eso es para el cliente frustrado que **no** pidió una persona.

> 🧠 **Para recordar:** pedido explícito = **escalar ya**.

#### Trampa 3 · El cliente enojado

**La situación.** Un cliente escribe furioso porque le llegó mal el talle por segunda vez. No pidió una persona. El cambio es simple y está dentro de lo que SoporteBot resuelve (Tema 2).

**✅ En el examen elegí:** **reconocer la frustración y ofrecer resolverlo**; escalar solo si el cliente insiste en una persona.

**❌ Las que tientan:**

❌ **"Escalar de inmediato porque el cliente está muy molesto".**
- *Tienta porque:* parece lo más empático.
- *Está mal porque:* el enojo no es un disparador; el caso se puede resolver.

> 🧠 **Para recordar:** frustración = **reconocer + ofrecer**; escalar si **reitera**.

#### Trampa 4 · El precio del competidor

**La situación.** Un cliente pide que le igualen el precio de otra tienda. La política solo habla de ajustes cuando TiendaX baja su propio precio (Tema 3).

**✅ En el examen elegí:** **escalar**: la política no cubre ese pedido.

**❌ Las que tientan:**

❌ **"Rechazarlo, porque la política no lo menciona".**
- *Tienta porque:* "si no está permitido, está prohibido".
- *Está mal porque:* la política no lo prohíbe: no dice nada. Decidir sería inventar la política.

❌ **"Aplicar la regla del ajuste de precio propio, que es la más parecida".**
- *Tienta porque:* parece razonable extender la regla.
- *Está mal porque:* es una excepción que el agente no tiene autoridad para hacer.

> 🧠 **Para recordar:** política **silenciosa** = escalar; política que **prohíbe** = rechazar.

#### Trampa 5 · Los tres Juan Pérez

**La situación.** `get_customer("Juan Pérez")` devuelve tres cuentas (Tema 5).

**✅ En el examen elegí:** **pedirle al cliente un identificador más** (email, DNI o número de pedido).

**❌ Las que tientan:**

❌ **"Usar la cuenta con la compra más reciente".**
- *Tienta porque:* es la más probable.
- *Está mal porque:* es una heurística; si se equivoca, expone datos de otra persona.

❌ **"Escalar a una persona para que identifique al cliente".**
- *Tienta porque:* evita el riesgo.
- *Está mal porque:* el agente lo puede resolver solo preguntando.

> 🧠 **Para recordar:** varias coincidencias = **pedir un dato más**.

#### Trampa 6 · El tope que tiene que cumplirse siempre

**La situación.** Ningún reembolso de más de USD 500 puede hacerse sin aprobación humana. Hoy está en el system prompt y se escapan algunos (Tema 4).

**✅ En el examen elegí:** **un hook o validación en código** que bloquea el reembolso y redirige a escalamiento.

**❌ Las que tientan:**

❌ **"Reforzar la regla en el system prompt como 'hard trigger'".**
- *Tienta porque:* el curso la llama disparador "duro".
- *Está mal porque:* en el prompt sigue siendo probabilística.

> 🧠 **Para recordar:** "siempre" + plata = **código**.

### Grupo: Propagación de errores (tarea 5.3)

#### Trampa 7 · El timeout del buscador (Q8)

**La situación.** El subagente de búsqueda web hace un timeout. ¿Cómo informa la falla al coordinador? (Tema 6)

**✅ En el examen elegí:** **devolver el tipo de falla, la consulta intentada, los resultados parciales y las alternativas**.

**❌ Las que tientan:**

❌ **"Reintentar con backoff y, si se agotan los reintentos, devolver 'search unavailable'".**
- *Tienta porque:* el reintento local es correcto.
- *Está mal porque:* el estado genérico del final le esconde al coordinador todo lo que necesita.

❌ **"Capturar el timeout y devolver una lista vacía marcada como éxito".**
- *Tienta porque:* el flujo sigue sin errores.
- *Está mal porque:* el coordinador cree que no había nada.

❌ **"Propagar la excepción a un manejador que termina el flujo".**
- *Tienta porque:* no esconde el error.
- *Está mal porque:* pierde todo el trabajo por una sola falla.

> 🧠 **Para recordar:** error útil = **tipo + intento + parciales + alternativas**.

#### Trampa 8 · Sin alertas de fraude

**La situación.** El sistema de fraude no respondió y el subagente devolvió `[]`. El coordinador aprobó un reembolso grande creyendo que no había alertas (Tema 7).

**✅ En el examen elegí:** **distinguir la falla de acceso del resultado vacío**: devolver `access_failure` con su tipo.

**❌ Las que tientan:**

❌ **"Que el coordinador reintente siempre que reciba una lista vacía".**
- *Tienta porque:* cubriría el caso de la falla.
- *Está mal porque:* reintentaría también los vacíos válidos, que van a dar lo mismo, y sigue sin saber qué pasó.

> 🧠 **Para recordar:** **"no encontré" ≠ "no pude buscar"**.

#### Trampa 9 · Reintentar una credencial vencida

**La situación.** Un subagente recibe "credencial vencida" de una fuente (Tema 8).

**✅ En el examen elegí:** **propagar enseguida** al coordinador con el tipo de falla y la alternativa, sin reintentar.

**❌ Las que tientan:**

❌ **"Reintentar con backoff exponencial antes de propagar".**
- *Tienta porque:* es el patrón correcto para fallas transitorias.
- *Está mal porque:* esperar no arregla un permiso; solo agrega demora.

> 🧠 **Para recordar:** transitorio = reintentar local; permiso = **propagar ya**.

#### Trampa 10 · El informe que parece completo

**La situación.** Una de las cinco fuentes del informe de mercado no estuvo disponible. El sistema siguió con las otras cuatro (Tema 9).

**✅ En el examen elegí:** **anotar en el informe qué hallazgos están bien respaldados y qué temas tienen huecos por la fuente que faltó**.

**❌ Las que tientan:**

❌ **"Completar ese tema con lo que haya en las otras fuentes, aunque sea poco".**
- *Tienta porque:* el informe queda completo.
- *Está mal porque:* presenta como sólido algo que no lo es.

❌ **"Frenar el informe hasta que vuelva la fuente".**
- *Tienta porque:* evita entregar algo incompleto.
- *Está mal porque:* desperdicia lo que ya se obtuvo y deja al equipo sin nada por una sola falla; lo correcto es entregar con anotaciones de cobertura.

> 🧠 **Para recordar:** se sigue con lo que hay, y **se dice qué falta**.

---

## Checklist oficial

**Tarea 5.2 — Design effective escalation and ambiguity resolution patterns**

*Knowledge of*
- [x] Disparadores adecuados: el cliente pide una persona, excepciones o huecos de la política (no solo casos complejos) y no poder avanzar → **Tema 1** (Trampa 1)
- [x] La diferencia entre escalar de inmediato cuando el cliente lo pide explícitamente y ofrecer resolver cuando el problema es simple → **Tema 2** (Trampas 2 y 3)
- [x] Por qué el sentimiento y la confianza autoinformada son malos indicadores de la complejidad real → **Tema 4** (Trampa 1)
- [x] Varias coincidencias requieren pedir más identificadores, no elegir por heurística → **Tema 5** (Trampa 5)

*Skills in*
- [x] Criterios explícitos de escalamiento con ejemplos en el system prompt → **Tema 1** (Trampa 1)
- [x] Honrar el pedido explícito de una persona de inmediato, sin investigar antes → **Tema 2** (Trampa 2)
- [x] Reconocer la frustración y ofrecer resolver cuando está al alcance del agente; escalar solo si el cliente reitera → **Tema 2** (Trampa 3)
- [x] Escalar cuando la política es ambigua o no dice nada (price matching de competidores) → **Tema 3** (Trampa 4)
- [x] Instruir al agente para pedir identificadores adicionales cuando hay varias coincidencias → **Tema 5** (Trampa 5)

**Tarea 5.3 — Implement error propagation strategies across multi-agent systems**

*Knowledge of*
- [x] Contexto de error estructurado (tipo de falla, consulta intentada, resultados parciales, alternativas) para que el coordinador decida cómo recuperarse → **Tema 6** (Trampa 7)
- [x] La diferencia entre fallas de acceso (timeouts que requieren decidir si reintentar) y resultados vacíos válidos → **Tema 7** (Trampa 8)
- [x] Por qué un estado genérico ("search unavailable") le esconde contexto al coordinador → **Tema 6** (Trampa 7)
- [x] Por qué suprimir errores (vacío como éxito) y terminar todo el flujo por una falla son anti-patrones → **Temas 6 y 8** (Trampas 7 y 10)

*Skills in*
- [x] Devolver contexto de error estructurado con tipo de falla, qué se intentó, resultados parciales y alternativas → **Tema 6** (Trampa 7)
- [x] Distinguir fallas de acceso de resultados vacíos válidos al informar errores → **Tema 7** (Trampa 8)
- [x] Que los subagentes recuperen localmente las fallas transitorias y propaguen solo lo que no pueden resolver, con lo intentado y los parciales → **Tema 8** (Trampa 9)
- [x] Estructurar la síntesis con anotaciones de cobertura: qué está bien respaldado y qué temas tienen huecos por fuentes no disponibles → **Tema 9** (Trampa 10)

**Complementa otras tareas:** hooks para reglas obligatorias de 1.4/1.5 (Tema 4) · errores estructurados de tools de 2.2 (Temas 6 y 7) · descomposición del coordinador de 1.2 / Q7 (Tema 9).

**📘 Curso (útil para entender):** retry ceiling y tool para pedir ayuda (Tema 1) · handoff payload (Tema 2) · propagation contract (Tema 6) · status enum `success / empty_result / partial_result / access_failure` y "the silent bug" (Tema 7).

---

## Autoevaluación oral

1. ¿Cuáles son los tres disparadores correctos para escalar? ¿Por qué "es un caso complejo" no alcanza? Contá la Q3.
2. ¿Qué hacés si el cliente pide una persona? ¿Y si está enojado pero no la pidió? ¿Y si la política no dice nada de su pedido?
3. ¿Por qué el sentimiento y la confianza del modelo no sirven para escalar? ¿Qué hacés con tres clientes del mismo nombre?
4. ¿Qué cuatro cosas tiene que devolver un subagente cuando falla? Contá la Q8 y sus tres distractores.
5. ¿Por qué "no encontré nada" y "no pude buscar" no pueden verse igual? ¿Qué se recupera localmente y qué se propaga? ¿Qué dice el informe cuando faltó una fuente?

---

## Preguntas tipo examen

Las preguntas tipo examen de este capítulo están en [`04-practica/modulo-5.md`](../04-practica/modulo-5.md), junto con las del resto del módulo 5. Hacelas cuando termines **todos** los capítulos del módulo, de a una y sin mirar la respuesta.

---

## Revisión contra el blueprint oficial

Qué puede salir en el examen de 5.2 y 5.3 que el curso de Jacob **no cubre o cubre flojo**, y dónde quedó explicado:

1. **Pedido explícito → escalar ya; frustración → ofrecer resolver.** El curso no lo distingue. → Tema 2.
2. **Política silenciosa o ambigua (price matching).** → Tema 3.
3. **La confianza autoinformada no sirve para escalar.** El curso enseña lo contrario. → Tema 4.
4. **Varias coincidencias → pedir más identificadores.** La lección 109 del curso, "Disambiguation", trata de otra cosa (vacío vs. falla). → Tema 5.
5. **Los cuatro campos del error según la guía**, que no coinciden del todo con el "envelope" del curso. → Tema 6.
6. **No reintentar fallas de permiso.** El companion pide clasificar los errores, pero el wrapper de las lecciones 108–109 reintenta toda falla de acceso, incluida la de autenticación. → Tema 8.
7. **Anotaciones de cobertura en la síntesis.** → Tema 9.

No encontré otros huecos para 5.2 y 5.3.

