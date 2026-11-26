# Capítulo 13 · 4B · Udemy 14 — Advanced Prompting Techniques (few-shot, razonamiento y control de la salida)

*Tarea oficial 4.2 · Segundo capítulo del módulo 4*

---

## Dónde estamos

Seguimos en el **módulo 4: Prompt Engineering & Structured Output**. 4A ya está escrito (se cierra con las preguntas del módulo). Este capítulo cubre una tarea, de 3,33%:
- **4.2** Apply few-shot prompting to improve output consistency and quality (usar ejemplos en el prompt para que la salida sea consistente y de calidad).

### Cómo leer este capítulo

Todo lo que leés acá **vale para el examen**, salvo que diga lo contrario. Cuando algo sale solo del curso (útil para entender, pero no central), lo marco con **📘 Curso**. Cuando Jacob dice algo distinto de lo que evalúa la guía, aparece un recuadro así:

> ⚠️ **En el curso vas a escuchar otra cosa.** … **Para el examen: …**

### Un aviso sobre este capítulo

El curso dedica dos lecciones a los ejemplos (81 y 82) y seis a otros temas: chain-of-thought, extended thinking, cómo controlar el formato, temperature y conversaciones de varios turnos. **La guía solo evalúa los ejemplos**, y con un foco que el curso no tiene: casos ambiguos, razonamiento visible, falsos positivos y extracción de documentos. Por eso la **Parte 1 es la importante**. Las Partes 2 a 4 son más cortas: te sirven para entender y, sobre todo, para **reconocer distractores** (prefill, temperature, budget_tokens, que explico en los Temas 7 a 9), porque varios de esos datos del curso ya no valen en los modelos actuales.

## De dónde venimos

En 4A viste que una instrucción vaga obliga a Claude a suponer, y que en un revisor lo que baja los falsos positivos son los **criterios explícitos**: qué se reporta, qué se saltea y un ejemplo de código por nivel de severidad. Ese último punto ya era un adelanto de este capítulo: **un ejemplo muestra lo que una descripción no alcanza a explicar**. Y en 1D viste la pregunta oficial Q3, donde SoporteBot escalaba mal y la respuesta correcta era "criterios explícitos **con ejemplos**". Acá aprendés a diseñar esos ejemplos.

## Mapa del capítulo

**Parte 1 — Few-shot prompting (tarea 4.2).**
1. Qué es few-shot y por qué fija la forma de la salida.
2. Cómo se diseña un buen set de ejemplos.
3. Ejemplos para los casos ambiguos, con el razonamiento.
4. Ejemplos para bajar los falsos positivos de un revisor.
5. Ejemplos para extraer datos de documentos distintos.
6. Cuándo los ejemplos **no** son la respuesta.

**Parte 2 — Razonamiento (lecciones 83 y 84).**

7. Chain-of-thought y thinking.

**Parte 3 — Controlar la salida (lecciones 85 y 87).**

8. Steering sin prefill.
9. Temperature, top_p y top_k: parámetros que ya no se usan.

**Parte 4 — Conversaciones de varios turnos (lecciones 88 y 89).**

10. Multi-turn: la API no recuerda nada.

---

# Parte 1 — Few-shot prompting

## Tema 1 — Few-shot prompting (dar ejemplos en el prompt)

### Qué es

**Few-shot prompting** (prompting con pocos ejemplos) es incluir en el prompt algunos ejemplos resueltos: una entrada y la salida que querés para esa entrada. Si no das ningún ejemplo es **zero-shot**; con uno, **one-shot**; con dos o más, **few-shot** (la documentación también lo llama **multishot**).

Funciona porque **un ejemplo se imita, una descripción hay que interpretarla**. Cuando describís el formato en prosa ("devolvé la ubicación, el problema, la severidad y la corrección"), Claude tiene que decidir cómo se ve eso: en qué orden, con qué largo, con qué palabras. Cuando le mostrás dos o tres hallazgos ya escritos, copia la forma directamente. Un solo ejemplo transmite a la vez el formato, el tono, el largo y hasta el tipo de razonamiento, cosas que la prosa tiene que explicar de a una.

Por eso la guía dice que los ejemplos son **la técnica más efectiva para lograr una salida consistente y accionable** (que se puede usar directamente para actuar) cuando las instrucciones detalladas **ya no alcanzan**. Esa condición importa: si ya escribiste instrucciones claras y la salida sigue variando, agregar más instrucciones no suele arreglarlo; agregar ejemplos sí.

### Ejemplo

El bot de review de TiendaX ya tiene criterios claros (4A), pero cada hallazgo sale escrito distinto: a veces sin archivo, a veces sin corrección, a veces en un párrafo largo. El equipo agrega esto al prompt:

```xml
<examples>
<example>
<location>src/checkout/total.ts:42</location>
<issue>El descuento se resta en pesos, pero `totalCents` está en centavos.</issue>
<severity>Crítico</severity>
<fix>Usar `discountCents` o multiplicar por 100 antes de restar.</fix>
</example>
<example>
<location>src/orders/api.ts:88</location>
<issue>Si `items` está vacío, `items[0]` lanza una excepción y la API responde 500.</issue>
<severity>Importante</severity>
<fix>Validar el carrito vacío y responder 400 con un mensaje.</fix>
</example>
</examples>
```

Desde ese momento, todos los hallazgos salen con los cuatro campos y con el mismo nivel de detalle. Es exactamente el ejemplo de la guía: ejemplos que muestran el formato **location, issue, severity, suggested fix**. Fijate que acá los ejemplos muestran solo salidas: cuando lo que querés fijar es el formato, alcanza con eso. Cuando querés enseñar un criterio (Temas 3 a 5), cada ejemplo lleva la entrada y la salida.

### Cómo se configura

Hay dos formas de poner los ejemplos en el prompt:
- **Dentro del prompt, con etiquetas** `<example>` (varios dentro de `<examples>`), para que Claude no los confunda con las instrucciones. Es la misma idea de las XML tags de 4A, y es lo que recomienda la documentación.
- **Como pares de turnos** `user`/`assistant` **anteriores** al mensaje real: un mensaje de usuario con la entrada de ejemplo, una respuesta de assistant con la salida ideal, y recién después el pedido verdadero. La API acepta mensajes de assistant escritos por vos (no hace falta que los haya generado Claude).

### Para el examen

- Instrucciones detalladas y la salida **sigue inconsistente** → **agregar ejemplos** (few-shot). Más instrucciones no es la respuesta.
- Formato de hallazgos que varía → ejemplos con **location, issue, severity, suggested fix**.
- Los ejemplos dan **consistencia**, pero no garantizan un JSON válido: eso lo da un schema (4C).

### Cómo se une

Un ejemplo es poderoso porque se imita. Y eso tiene una contracara: Claude imita **todo** lo que ve en él, también lo que no querías. Por eso importa cómo se diseñan.

---

## Tema 2 — Example design (cómo se diseña un buen set de ejemplos)

### Qué es

Como Claude copia los ejemplos, cualquier rasgo accidental se convierte en regla. Si todos tus ejemplos son de envíos, va a tratar cada ticket como si fuera de envíos. Si todos tienen respuestas largas, todas las respuestas van a salir largas. Si uno tiene una frase rara, la va a repetir. El curso llama a esto **example contamination** (contaminación por los ejemplos). Y si los ejemplos se contradicen entre sí, Claude promedia y la salida queda confusa: por eso **un ejemplo bueno vale más que cinco inconsistentes**.

La documentación resume cómo tienen que ser los ejemplos en tres palabras:
- **Relevant** (relevantes): parecidos a los casos reales que va a recibir.
- **Diverse** (variados): distintos en largo, tema y forma, e incluyendo casos borde, para que Claude no tome un rasgo accidental como regla.
- **Structured** (separados): dentro de `<example>`, aparte de las instrucciones.

**¿Cuántos?** Acá las tres fuentes dan números distintos, y conviene saber cuál usar.

> ⚠️ **En el curso vas a escuchar otra cosa.** Jacob dice que **tres** ejemplos es el número más útil, y la documentación recomienda **entre 3 y 5**. **Para el examen:** la guía habla de **2 a 4 ejemplos dirigidos a los casos ambiguos**. Si una opción propone muchos ejemplos ("5-8 examples", "uno por cada caso posible"), es un distractor. Tres entra en los tres rangos, así que si dudás, tres está bien.

📘 Curso: Jacob agrega tres consejos que no están en la documentación. Poner el ejemplo más representativo **al final**, porque el último influye más. Elegir los ejemplos de forma dinámica, buscando los más parecidos al pedido actual (**dynamic few-shot**). Y **comparar contra zero-shot**: si sin ejemplos sale igual de bien, los ejemplos solo agregan tokens.

### Ejemplo

SoporteBot clasifica tickets en envío, pago, devolución u otro. El primer set tenía tres ejemplos, todos de clientes enojados por envíos demorados, escritos en mayúsculas. Resultado: clasificaba como "envío" cualquier mensaje en mayúsculas. El equipo lo reemplaza por tres ejemplos variados: uno de pago escrito con calma, uno de devolución largo y desordenado, y uno ambiguo ("me cobraron y no llegó") clasificado como pago, con la razón.

### Para el examen

- Calidad antes que cantidad: pocos ejemplos buenos y variados.
- Ejemplos todos parecidos (mismo tema, mismo largo, mismo tipo de documento) → Claude toma ese rasgo como regla.
- **2 a 4 ejemplos dirigidos.** Muchos ejemplos o "uno por caso" → distractor.

### Cómo se une

La palabra clave de la guía es **dirigidos**: los ejemplos no se eligen al azar, sino para los casos donde Claude se equivoca. Eso es el Tema 3.

---

## Tema 3 — Ambiguous cases (ejemplos para los casos ambiguos, con el razonamiento)

### Qué es

Los casos fáciles Claude ya los resuelve bien: no hace falta enseñárselos. Donde falla es en la **frontera**, en los casos que podrían ir para un lado o para el otro. Por eso la guía pide ejemplos **dirigidos a los casos ambiguos**: qué tool usar cuando el pedido podría ser de dos, si escalar o resolver un caso que está en el límite, si una rama de código sin test es un problema.

Y pide algo más: que cada ejemplo **muestre el razonamiento**, es decir, **por qué se eligió esa acción y no la alternativa que también parecía razonable**. Un ejemplo que solo dice "entrada → respuesta" enseña ese caso puntual. Un ejemplo que explica el porqué enseña el **criterio**, y con el criterio Claude puede resolver casos nuevos que no se parecen a ningún ejemplo. La guía lo dice así: los ejemplos permiten **generalizar el juicio a patrones nuevos** en lugar de solo reconocer los casos que ya estaban previstos. La documentación coincide: presentá cada ejemplo como el problema, el método que se aplica y la respuesta esperada.

### Ejemplo

Es la pregunta oficial **Q3** que viste en 1D. SoporteBot escala casos simples (un cambio de producto dañado con foto) y se queda intentando resolver casos que necesitan una excepción a la política. La respuesta correcta es **criterios explícitos de escalamiento en el system prompt, con ejemplos** de cuándo escalar y cuándo resolver. Un ejemplo bien armado se ve así:

```xml
<example>
<ticket>Me llegó la taza rota, te mando la foto. ¿Me mandan otra?</ticket>
<decision>Resolver</decision>
<reasoning>Es un daño en el envío con evidencia (foto) y el producto tiene stock:
la política cubre el cambio sin aprobación. Podría parecer un reclamo para
escalar porque el cliente está molesto, pero el enojo no cambia que el caso
esté dentro de la política.</reasoning>
</example>
<example>
<ticket>Compré hace 45 días y la licuadora dejó de andar. Quiero la plata.</ticket>
<decision>Escalar</decision>
<reasoning>La política cubre reembolsos hasta 30 días. Pedir un reembolso
fuera de plazo es una excepción, y las excepciones las aprueba una persona.
Podría parecer un caso simple de reembolso, pero el plazo lo saca de la política.</reasoning>
</example>
```

Fijate que cada razonamiento nombra **la alternativa tentadora** y por qué se descartó. Eso es lo que permite que Claude resuelva bien un caso nuevo, como un producto dañado sin foto, aplicando el criterio y no buscando un ejemplo igual.

**Los otros dos casos ambiguos que nombra la guía** funcionan igual:

- **Elegir la tool ante un pedido ambiguo.** Las tools de SoporteBot ya tienen buenas descripciones (2A), pero hay pedidos que de verdad podrían ir a dos: "quiero cancelar lo que compré ayer" ¿es `lookup_order` para ver si todavía se puede cancelar, o `cancel_order` directo? Un ejemplo con el razonamiento ("primero `lookup_order`, porque un pedido ya despachado no se cancela sino que se devuelve") enseña el criterio. Ojo: esto vale **cuando las descripciones ya están bien**. Si son mínimas, primero se amplían (es la Q2 del Tema 6).
- **Huecos de cobertura por rama** (branch-level test coverage gaps). Una función puede tener tests, pero no para todas sus ramas: el `if` está probado y el `else` no. El revisor tiene que decidir si esa rama sin test merece un comentario. Un ejemplo con razonamiento: "reportar: el `else` aplica el recargo a pedidos internacionales, cobra plata y no tiene test; podría parecer un detalle porque la función tiene 90% de cobertura, pero esa rama es justo la que mueve dinero". Y otro de contraste: "no reportar: la rama sin test solo arma un mensaje de log".

### Para el examen

- Casos ambiguos mal resueltos → **2 a 4 ejemplos de esos casos ambiguos, con el razonamiento** de por qué se eligió una opción frente a la alternativa plausible.
- Ejemplos solo de casos claros, o pares "entrada → etiqueta" sin el porqué → distractores: no enseñan la frontera.
- Una lista enorme de casos previstos → no enseña criterio; Claude solo reconoce lo que ya vio.
- Q3: **criterios + ejemplos**. Los distractores de Q3 son un **confidence score** que el modelo se autoasigna (está mal calibrado: el agente ya está seguro en los casos difíciles), un **clasificador entrenado aparte** (excesivo antes de probar con el prompt) y **análisis de sentimiento** (el enojo del cliente no indica qué tan complejo es el caso).

### Cómo se une

Un revisor de código tiene el mismo problema de frontera: hay código que parece un problema pero es aceptable. Ese es el Tema 4.

---

## Tema 4 — False positive reduction (ejemplos para bajar los falsos positivos)

### Qué es

En 4A viste que los criterios explícitos bajan los falsos positivos. Los ejemplos los complementan: muestran **dónde está la línea** entre un patrón de código aceptable y un problema real. La guía pide ejemplos que **distingan el código aceptable de los problemas genuinos**, para reducir los falsos positivos y, a la vez, permitir que Claude generalice.

La clave está en los **contrasting pairs** (pares contrastantes): dos fragmentos que se parecen, uno que hay que reportar y otro que no, con la razón. Si solo mostrás ejemplos obviamente malos, Claude no aprende nada nuevo sobre la frontera; los obvios ya los encontraba.

### Ejemplo

El bot de TiendaX marcaba como problema todos los `catch` que no relanzan el error. Pero en TiendaX hay un patrón aceptado: cuando falla el envío de un email de confirmación, se loguea y se sigue, porque el pedido ya está guardado. El equipo agrega este par:

````xml
<example>
<code>
```ts
try { await sendConfirmationEmail(order); }
catch (e) { logger.warn("email no enviado", { orderId: order.id, e }); }
```
</code>
<verdict>No reportar</verdict>
<reasoning>El email es secundario: el pedido ya se guardó y el error queda logueado
con el id. Tragar el error acá es el patrón del equipo.</reasoning>
</example>
<example>
<code>
```ts
try { await chargeCard(order); }
catch (e) { logger.warn("cobro fallido", { orderId: order.id }); }
markAsPaid(order);
```
</code>
<verdict>Reportar · Crítico</verdict>
<reasoning>Se parece al caso del email, pero acá el error se ignora y el pedido
se marca como pagado aunque el cobro falló.</reasoning>
</example>
````

Con este par, Claude aprende la regla de fondo (ignorar un error es aceptable solo si lo que falló es secundario) y la aplica a casos nuevos, como un fallo al actualizar las estadísticas de la home.

### Para el examen

- Revisor con falsos positivos → criterios explícitos (4A) **y** ejemplos que contrastan **código aceptable vs. problema real**.
- Solo ejemplos de errores obvios → distractor: no enseñan la frontera.

### Cómo se une

El otro gran uso de los ejemplos en la guía no es revisar código sino **extraer datos** de documentos que vienen en formas muy distintas.

---

## Tema 5 — Extraction examples (ejemplos para extraer datos de documentos distintos)

### Qué es

En una tarea de **extracción**, Claude lee un documento y completa campos: proveedor, monto, fecha, autor. Los documentos reales no tienen todos la misma forma, y eso produce dos fallas típicas:
- **Campos vacíos que no deberían estarlo.** El dato está en el documento, pero en un lugar o forma que Claude no espera (en medio de un párrafo en lugar de en una tabla), y el campo sale vacío o `null`.
- **Alucinación** (inventar datos). El dato no está, pero Claude completa algo plausible porque todos los ejemplos que vio tenían ese campo lleno.

La guía dice que los ejemplos son efectivos contra las dos: mostrale a Claude **documentos con estructuras variadas** y cómo se extrae bien de cada uno. Los ejemplos de la guía son tres situaciones típicas:
- **Citas dentro del texto vs. bibliografía al final.** En un paper, las referencias pueden estar en una lista al final o metidas en el texto ("como mostró García en 2021…"). Si todos los ejemplos tienen bibliografía, Claude devuelve la lista de referencias vacía para los papers que citan dentro del texto. Un ejemplo de cada forma le enseña a buscar en los dos lugares.
- **Sección de metodología vs. detalles mezclados.** Algunos documentos tienen un apartado "Metodología"; otros cuentan el método de a poco en distintos párrafos. Un ejemplo de cada uno le enseña que el dato puede estar repartido.
- **Medidas informales.** Una receta dice "un puñado de nueces" o "una pizca de sal". Si el campo pide gramos, Claude puede inventar un número. Un ejemplo que muestra la salida correcta (guardar el texto literal "un puñado", o `null` en el campo numérico) le enseña a no convertir lo que no se puede convertir.

Y conviene incluir un ejemplo donde el dato **realmente no está** y la salida correcta es `null`, para que Claude aprenda que vacío es una respuesta válida y no invente.

### Ejemplo

TiendaX extrae datos de las facturas de sus proveedores: proveedor, número de factura, total y fecha de vencimiento. Los proveedores grandes mandan PDFs con tabla; los chicos mandan un email: "Te paso la factura 0012 por las 30 tazas, son $90.000, pagás cuando puedas a fin de mes". El campo `due_date` salía vacío en los emails, y a veces aparecía una fecha inventada.

El equipo agrega tres ejemplos: una factura con tabla; un email donde el vencimiento está en la frase ("a fin de mes" → último día del mes de emisión); y un email sin ningún vencimiento, con `"due_date": null` y la explicación "el documento no menciona un vencimiento; no se infiere".

### Para el examen

- Extracción que deja vacíos campos que **sí están** en el documento → ejemplos con **estructuras de documento variadas**.
- Extracción que **inventa** valores → ejemplos que incluyan el caso del dato ausente, manejado con `null`.
- Distractores: instrucciones como "nunca dejes campos vacíos" (empujan a inventar), reintentar o post-procesar sin atacar la causa, o ejemplos todos del mismo tipo de documento.
- La forma garantizada (campos obligatorios u opcionales, tipos) la da el schema, que vemos en 4C. Los ejemplos enseñan **cómo** encontrar el dato.

### Cómo se une

Los ejemplos son muy útiles, pero no son la respuesta a todo. El examen también pone few-shot como distractor cuando la causa es otra.

---

## Tema 6 — When few-shot is not the answer (cuándo los ejemplos no son la respuesta)

### Qué es

Few-shot es la respuesta cuando el problema es **un criterio poco claro en los casos ambiguos** o **un formato inconsistente a pesar de las instrucciones**. Si la causa es otra, los ejemplos agregan tokens y no la arreglan. La guía tiene una pregunta oficial sobre esto.

**Q2 (de 2A).** El agente llama `get_customer` cuando el usuario pregunta por un pedido. Las dos tools tienen descripciones mínimas. Una opción propone agregar **5 a 8 ejemplos** de pedidos que van a `lookup_order`. Es incorrecta: la causa es la **descripción de la tool**, y la respuesta es ampliarla. La guía lo explica: los ejemplos agregan tokens sin corregir el problema de fondo.

| Si el problema es… | La respuesta es… | No es… |
|---|---|---|
| Tool equivocada con descripciones mínimas | Mejorar las descripciones (2A) | Few-shot |
| Tool ambigua con descripciones ya buenas | **Few-shot** con el razonamiento (Tema 3) | Más texto en la descripción |
| Revisor sin criterio de qué reportar | Criterios explícitos (4A), y después ejemplos | Solo ejemplos |
| Necesito un JSON siempre válido | Un schema: structured outputs o tool use (4C) | Few-shot ni prefill |
| Una regla que no puede fallar nunca | Un hook o un control en código (1D) | Un ejemplo más |
| Casos ambiguos o formato que varía | **Few-shot** | Más instrucciones |

### Para el examen

- Antes de elegir "agregar ejemplos", preguntate **cuál es la causa**. Si es una descripción de tool, un criterio que falta, una garantía de formato o una regla obligatoria, few-shot es el distractor.

### Cómo se une

Hasta acá, la tarea 4.2. Las partes que siguen son las otras lecciones del curso: te sirven para entender, y para no caer en opciones que suenan bien pero ya no funcionan.

---

# Parte 2 — Razonamiento

## Tema 7 — Chain-of-thought and thinking (razonamiento en el texto y en la API)

### Qué es

Hay dos formas de que Claude razone antes de responder, y el curso las distingue bien.

**Chain-of-thought** (CoT, cadena de razonamiento) es una técnica **de texto**: le pedís en el prompt que piense paso a paso antes de dar la respuesta, y el razonamiento aparece en la respuesta misma. No hace falta ningún parámetro de la API. Ayuda en tareas de varios pasos (cálculos, lógica, planificación, instrucciones complejas) y no aporta nada en tareas simples, como buscar un dato o clasificar algo obvio: solo agrega costo y demora.

**Thinking** es una **feature de la API**: Claude razona en bloques aparte (**thinking blocks**) antes de la respuesta final, y vos lo activás con un parámetro. En los modelos actuales es **adaptive thinking** (razonamiento adaptativo): Claude decide cuánto pensar según la dificultad, y vos regulás la profundidad con el parámetro **`effort`** (esfuerzo: `low`, `medium`, `high`, `xhigh`, `max`). Cuanto más alto, más razona y más tokens gasta. En algunos modelos recientes el thinking está siempre activo.

```python
client.messages.create(
    model="claude-opus-5-5",
    max_tokens=16000,                       # limita thinking + respuesta juntos
    thinking={"type": "adaptive"},
    output_config={"effort": "high"},
    messages=[{"role": "user", "content": "Planificá la migración de la tabla de pedidos…"}],
)
```

Según la documentación, con thinking desactivado el CoT escrito en el prompt sigue siendo el **plan B**. Y una indicación general como "pensá a fondo" suele funcionar mejor que escribirle un plan paso a paso.

Una aclaración de nombres: **extended thinking** (razonamiento extendido) es el nombre de la feature, y es el término que usa la guía. Antes se configuraba en modo manual, con un presupuesto fijo de tokens (`budget_tokens`); hoy el modo es **adaptive**.

> ⚠️ **En el curso vas a escuchar otra cosa.** El companion dice que extended thinking "sets a token budget" (el viejo parámetro `budget_tokens`) y que primero conviene probar CoT. **Para el examen:** en algunos modelos actuales el thinking está siempre activo, así que ese orden ya no aplica; y `budget_tokens` está deprecado y devuelve **error 400 desde los modelos 4.7**; hoy se usa adaptive thinking con `effort` (las slides de Jacob ya lo marcan como "legacy"). La guía casi no menciona thinking. Lo único que dice es que, para encontrar errores en código, una **instancia de review independiente** funciona mejor que pedirle a la misma sesión que se autorrevise o que use extended thinking (lo ves en 4C).

### Ejemplo

SoporteBot clasifica tickets: es una tarea simple y no gana nada razonando, así que va con `effort` bajo y sin pedir CoT. El agente que planifica la migración de la base de pedidos, en cambio, tiene muchos pasos y restricciones: va con adaptive thinking y `effort` alto. Y en un modelo con thinking desactivado, el equipo le pide en el prompt que piense antes de responder y que ponga la respuesta final en `<answer>`.

### Para el examen

- CoT = pedido en el texto del prompt; thinking = parámetro de la API.
- Más razonamiento en modelos actuales → **adaptive thinking + `effort`**, no `budget_tokens`.
- Para atrapar errores en el propio código → **instancia independiente**, no extended thinking.

### Cómo se une

Thinking regula cuánto razona Claude. Para regular **cómo se ve** la respuesta había otra técnica, el prefill, que ya no se puede usar.

---

# Parte 3 — Controlar la salida

## Tema 8 — Steering (guiar la salida) sin prefill

### Qué es

El **prefill** (prellenado de la respuesta) consistía en terminar la lista de mensajes con un mensaje de `assistant` a medio escribir, por ejemplo `{`, para que Claude siguiera desde ahí y respondiera en JSON. **Desde los modelos 4.6, si la conversación termina en un mensaje de assistant, la API devuelve error 400.** El curso lo marca como "legacy" y retiró la lección que lo enseñaba (la 86).

Hay un detalle que confunde: los ejemplos few-shot armados como pares `user`/`assistant` **antes** del último mensaje del usuario **siguen siendo válidos**. Lo que da 400 es que la conversación **termine** en assistant.

Las alternativas oficiales dependen de lo que querés lograr:

| Querés… | Usá… |
|---|---|
| Que toda la respuesta sea JSON válido | **Structured outputs** (salidas estructuradas: le pasás un schema; lo ves en 4C) |
| Que los argumentos de una tool cumplan el schema | **`strict: true`** en la tool (2A) |
| Una clasificación entre etiquetas fijas | Una tool con un campo `enum`, o structured outputs |
| Un tono, un estilo o que no empiece con "Aquí tenés…" | Una instrucción en el **system prompt** |

📘 Curso: Jacob agrega dos consejos de estilo. Un límite fijo de palabras ("menos de 100 palabras") corta igual una pregunta fácil que una difícil; nombrar el público y el propósito ancla mejor el largo. Y cada regla tiene que estar **en un solo lugar**: repetir la misma regla en varios lugares empeora la salida.

### Ejemplo

El integrador de tickets de TiendaX terminaba cada request con un mensaje de assistant que decía `{`, para forzar JSON. Al pasar a un modelo nuevo, todas las llamadas empezaron a fallar con 400. La migración correcta: sacar ese último mensaje y pasar el schema del ticket con structured outputs. Y la regla "respondé sin introducción" pasa al system prompt.

### Para el examen

- Prefill en el último turno → **400** en modelos actuales. Es un distractor.
- Formato garantizado → structured outputs o `strict` tool use. Tono → system prompt.
- Un par few-shot user/assistant previo **no** es prefill.

### Cómo se une

La otra perilla clásica para controlar la salida era la temperatura. También quedó en el pasado.

---

## Tema 9 — Temperature, top_p y top_k: parámetros que ya no se usan

### Qué es

Son **sampling parameters** (parámetros de muestreo): controlan cómo Claude elige la próxima palabra entre las posibles.
- **temperature**: cuánto azar hay. Baja = más predecible; alta = más variada.
- **top_p**: considera solo las opciones más probables hasta sumar cierta probabilidad.
- **top_k**: considera solo las k opciones más probables.

Durante mucho tiempo el consejo fue "temperatura baja para clasificar y extraer, alta para escribir creativamente". **En los modelos actuales eso ya no aplica**: desde los modelos 4.7, mandar valores distintos de los default devuelve **error 400**, y en la versión más nueva de la API los tres parámetros directamente no existen. Además, la documentación aclara que `temperature = 0` **nunca garantizó** respuestas idénticas.

> ⚠️ **En el curso vas a escuchar otra cosa.** El companion recomienda temperatura baja para clasificación y extracción, y vas a encontrar en internet la regla "no uses temperature y top_p juntos". **Para el examen:** esa regla era de un modelo viejo (Opus 4.1). Hoy, para que la salida sea **consistente**, la respuesta es **few-shot, criterios explícitos o structured outputs**, no la temperatura. Las propias slides del curso ya marcan estos parámetros como legacy.

### Para el examen

- "Bajar la temperatura" para lograr consistencia, o para bajar falsos positivos → **distractor**.
- El comportamiento se controla con el **prompt**; la profundidad del razonamiento, con **`effort`**.

### Cómo se une

Hasta acá, una sola llamada. Las dos últimas lecciones del curso tratan conversaciones que duran varios turnos.

---

# Parte 4 — Conversaciones de varios turnos

## Tema 10 — Multi-turn conversations (conversaciones de varios turnos): la API no recuerda nada

### Qué es

El hecho técnico más importante es este: **la Messages API es stateless** (no guarda estado). No recuerda la conversación entre una llamada y otra. Para que Claude "se acuerde" de lo que se habló, **en cada request se reenvía el historial completo** de mensajes. Si SoporteBot manda solo el último mensaje del cliente, Claude no sabe de qué pedido se estaba hablando. La guía lo pide en la tarea 5.1 (módulo 5).

Como el historial se reenvía y crece, con el tiempo trae **ruido**: datos viejos, temas que ya no importan. El curso llama **context drift** (deriva del contexto) a cuando la conversación se va alejando del objetivo de a poco, sin que ningún turno esté claramente mal. Se corrige recordando el objetivo, o arrancando una conversación nueva que lleve solo las decisiones y restricciones importantes.

📘 Curso: Jacob da reglas prácticas que no están en la documentación, pero son razonables:
- **Clarification turn** (turno de aclaración): si el pedido es ambiguo, hacé **una** pregunta concreta sobre la ambigüedad que más riesgo tiene, no cinco ni un genérico "¿podés contarme más?".
- **Una meta por turno**, usando la salida anterior como entrada del siguiente.
- **Corregir de a un problema por vez**, nombrando el error concreto.
- **Continuar o reiniciar**: seguir si el historial es coherente; empezar de nuevo, llevando un resumen de las decisiones, si hay mucho ruido o cambió la tarea. El manejo del contexto largo lo vemos en 5A.

### Ejemplo

Un cliente le escribe a SoporteBot: "¿Dónde está mi pedido?". En el siguiente mensaje dice: "¿Y lo puedo cambiar por otro color?". Si la aplicación manda a la API solo el segundo mensaje, Claude no sabe de qué pedido se habla. La aplicación tiene que mandar **los dos mensajes del cliente y la respuesta anterior de Claude**.

### Para el examen

- Claude "no recuerda" lo dicho antes → la API es stateless: **reenviar el historial completo**.
- Conversación larga que se desvía → recordar el objetivo o reiniciar con un resumen.

### Cómo se une

Esto cierra el capítulo. En 4C se completa el módulo: salida estructurada con schemas, validación y reintentos, Batches y revisión en varias pasadas.

---

## Cómo se une todo

Cuando las instrucciones claras de 4A no alcanzan para que la salida sea consistente, la herramienta más efectiva son los **ejemplos**: se imitan en lugar de interpretarse (Tema 1). Como se imita todo, tienen que ser pocos (2 a 4), buenos y variados, separados con `<example>` (Tema 2). Y tienen que estar **dirigidos a los casos ambiguos**, mostrando **por qué** se eligió una opción frente a la alternativa plausible, para que Claude generalice el criterio (Tema 3). En un revisor, los pares de código aceptable vs. problema real marcan la frontera y bajan los falsos positivos (Tema 4). En extracción, los ejemplos con documentos de estructuras distintas, incluido el caso del dato ausente, evitan los campos vacíos y las alucinaciones (Tema 5). Pero si la causa es otra (una descripción de tool, un criterio que falta, una garantía de formato), los ejemplos son el distractor (Tema 6).

El resto del capítulo te prepara para descartar opciones viejas. El razonamiento se pide con CoT en el texto o con adaptive thinking y `effort` en la API, no con `budget_tokens` (Tema 7). El prefill da 400: el formato se garantiza con structured outputs o `strict`, y el tono con el system prompt (Tema 8). La temperatura no es la forma de lograr consistencia (Tema 9). Y la API no recuerda nada: cada request lleva el historial completo (Tema 10).

## Lo que viene

**4C · Udemy 15 — Structured Output & Evaluation**, el último capítulo del módulo 4 y el que más tareas tiene: **4.3** (salida estructurada con tool use y JSON schemas), **4.4** (validación, reintentos y feedback), **4.5** (Batches) y **4.6** (revisión con varias instancias y varias pasadas). Después, las preguntas del módulo 4.

---

## Las trampas del examen

Cada trampa tiene el mismo orden: la situación, **qué elegir en el examen (✅)**, las opciones que tientan (❌) con por qué tientan y por qué están mal, y una regla para recordar.

### Grupo: Cuándo y cómo usar few-shot (tarea 4.2)

#### Trampa 1 · Más instrucciones

**La situación.** El bot de review ya tiene instrucciones detalladas sobre cómo escribir cada hallazgo, pero el formato sigue variando entre corridas (Tema 1).

**✅ En el examen elegí:** **agregar algunos ejemplos de hallazgos bien escritos** (location, issue, severity, suggested fix).

**❌ Las que tientan:**

❌ **"Hacer las instrucciones de formato todavía más detalladas".**
- *Tienta porque:* parece que falta precisión.
- *Está mal porque:* la guía dice que los ejemplos son lo más efectivo justamente cuando las instrucciones detalladas solas no alcanzan.

❌ **"Bajar la temperatura para que responda siempre igual".**
- *Tienta porque:* menos azar suena a más consistencia.
- *Está mal porque:* en los modelos actuales da 400, y nunca garantizó salidas iguales.

> 🧠 **Para recordar:** si las instrucciones ya no alcanzan, **mostrá** en vez de **explicar**.

#### Trampa 2 · Muchos ejemplos, todos fáciles

**La situación.** SoporteBot escala mal los casos que están en el límite de la política. El equipo quiere agregar ejemplos (Tema 3).

**✅ En el examen elegí:** **2 a 4 ejemplos de los casos ambiguos, cada uno con el razonamiento** de por qué se escaló o se resolvió frente a la otra opción.

**❌ Las que tientan:**

❌ **"Agregar 10 ejemplos que cubran todos los tipos de ticket".**
- *Tienta porque:* más cobertura parece mejor.
- *Está mal porque:* la guía pide 2 a 4 dirigidos; una lista larga enseña a reconocer casos, no criterio, y gasta tokens.

❌ **"Ejemplos de casos claros, para que vea bien la diferencia".**
- *Tienta porque:* los ejemplos claros son fáciles de entender.
- *Está mal porque:* Claude ya resuelve bien los claros; falla en la frontera.

❌ **"Pares ticket → decisión, sin explicación, para ahorrar tokens".**
- *Tienta porque:* el formato queda claro igual.
- *Está mal porque:* sin el porqué no aprende el criterio y no generaliza a casos nuevos.

> 🧠 **Para recordar:** ejemplos **de la frontera**, **con el porqué**.

#### Trampa 3 · Calibrar el escalamiento (Q3)

**La situación.** SoporteBot tiene 55% de resolución en el primer contacto y el objetivo es 80%. Escala casos simples y se queda con casos que necesitan una excepción (Tema 3).

**✅ En el examen elegí:** **criterios explícitos de escalamiento en el system prompt, con ejemplos de cuándo escalar y cuándo resolver**.

**❌ Las que tientan:**

❌ **"Que el agente se asigne un puntaje de confianza y escale si es bajo".**
- *Tienta porque:* suena medible.
- *Está mal porque:* la confianza que se autoasigna está mal calibrada: ya está seguro en los casos difíciles.

❌ **"Entrenar un clasificador aparte con tickets históricos".**
- *Tienta porque:* parece una solución robusta.
- *Está mal porque:* es excesivo antes de probar con el prompt.

❌ **"Escalar cuando el análisis de sentimiento detecta enojo".**
- *Tienta porque:* los clientes enojados parecen casos difíciles.
- *Está mal porque:* el enojo no indica la complejidad del caso.

> 🧠 **Para recordar:** límite de decisión poco claro = **criterios + ejemplos**: la respuesta proporcional, antes de agregar infraestructura.

#### Trampa 4 · Ejemplos solo de errores obvios

**La situación.** El revisor marca como problema patrones que el equipo acepta. Quieren bajar los falsos positivos sin perder los bugs reales (Tema 4).

**✅ En el examen elegí:** **ejemplos que contrastan código aceptable con problemas reales**, con la razón de cada uno.

**❌ Las que tientan:**

❌ **"Ejemplos de bugs graves y obvios para que sepa qué es un problema de verdad".**
- *Tienta porque:* deja claro qué es un bug.
- *Está mal porque:* no muestra la frontera; los obvios ya los encontraba.

> 🧠 **Para recordar:** los falsos positivos se corrigen con **pares que se parecen** pero tienen distinto veredicto.

#### Trampa 5 · El campo que sale vacío

**La situación.** La extracción de facturas deja `due_date` vacío cuando el proveedor escribe el vencimiento dentro de un párrafo, y a veces inventa una fecha cuando no hay ninguna (Tema 5).

**✅ En el examen elegí:** **ejemplos con documentos de estructuras variadas** (tabla, texto narrativo) **y uno donde el dato no está y la salida correcta es `null`**.

**❌ Las que tientan:**

❌ **"Agregar 'nunca dejes campos vacíos'".**
- *Tienta porque:* ataca directamente el síntoma.
- *Está mal porque:* empuja a inventar valores cuando el dato no está.

❌ **"Reintentar la extracción cuando un campo sale vacío".**
- *Tienta porque:* a veces la segunda vez sale bien.
- *Está mal porque:* no le enseña a encontrar el dato en una estructura que no conoce.

❌ **"Ejemplos, pero todos de facturas con tabla".**
- *Tienta porque:* son los documentos más comunes.
- *Está mal porque:* no le muestran las otras estructuras, que es donde falla.

> 🧠 **Para recordar:** extracción = ejemplos de **formatos distintos**, con **null honesto**.

#### Trampa 6 · Few-shot para elegir la tool (Q2)

**La situación.** El agente llama `get_customer` cuando le preguntan por pedidos. Las dos tools tienen descripciones de una línea (Tema 6).

**✅ En el examen elegí:** **ampliar las descripciones de las tools** (qué entradas aceptan, ejemplos de consultas, cuándo usar cada una frente a la otra).

**❌ Las que tientan:**

❌ **"Agregar 5 a 8 ejemplos de pedidos que van a `lookup_order`".**
- *Tienta porque:* few-shot es la técnica más efectiva para consistencia.
- *Está mal porque:* la causa es la descripción; los ejemplos agregan tokens sin corregirla.

> 🧠 **Para recordar:** antes de few-shot, **buscá la causa**.

### Grupo: Opciones viejas que suenan bien

#### Trampa 7 · El prefill para forzar JSON

**La situación.** Necesitás que SoporteBot devuelva siempre un JSON válido para el sistema de tickets (Tema 8).

**✅ En el examen elegí:** **structured outputs** (un schema), o tool use con `strict: true` si son argumentos de una tool.

**❌ Las que tientan:**

❌ **"Terminar los mensajes con un `assistant` que empiece con `{`".**
- *Tienta porque:* era la técnica clásica.
- *Está mal porque:* en los modelos actuales devuelve error 400.

❌ **"Agregar ejemplos de JSON bien formado".**
- *Tienta porque:* los ejemplos dan consistencia.
- *Está mal porque:* dan consistencia, no garantía; para JSON siempre válido, el schema.

> 🧠 **Para recordar:** forma **garantizada** = schema; ejemplos = forma **consistente**.

#### Trampa 8 · Más razonamiento con budget_tokens

**La situación.** Un agente de planificación responde rápido pero mal en tareas complejas. Querés que razone más (Tema 7).

**✅ En el examen elegí:** **adaptive thinking con un `effort` más alto**.

**❌ Las que tientan:**

❌ **"Activar extended thinking con `budget_tokens` alto".**
- *Tienta porque:* es lo que enseñaba el curso.
- *Está mal porque:* está deprecado y da 400 desde los modelos 4.7.

> 🧠 **Para recordar:** profundidad de razonamiento = **`effort`**.

#### Trampa 9 · Que se revise a sí mismo con thinking

**La situación.** Querés que el código generado por Claude se revise para encontrar errores sutiles (Tema 7).

**✅ En el examen elegí:** **una instancia de review independiente**, sin el contexto que generó el código.

**❌ Las que tientan:**

❌ **"Activar extended thinking en la misma sesión para que revise mejor".**
- *Tienta porque:* más razonamiento parece más revisión.
- *Está mal porque:* la sesión que generó el código arrastra su razonamiento; la guía dice que la instancia independiente encuentra más.

> 🧠 **Para recordar:** revisar = **otra instancia**, no más thinking.

#### Trampa 10 · El bot que se olvida

**La situación.** En el segundo mensaje, SoporteBot ya no sabe de qué pedido le hablaba el cliente (Tema 10).

**✅ En el examen elegí:** **reenviar el historial completo de la conversación en cada request**.

**❌ Las que tientan:**

❌ **"Aumentar `max_tokens` para que tenga más memoria".**
- *Tienta porque:* parece una cuestión de espacio.
- *Está mal porque:* `max_tokens` limita la respuesta; la API no guarda nada entre llamadas.

> 🧠 **Para recordar:** la API es **stateless**: el historial lo mandás vos.

---

## Checklist oficial

**Tarea 4.2 — Apply few-shot prompting to improve output consistency and quality**

*Knowledge of*
- [x] Few-shot como la técnica más efectiva para lograr una salida consistente y accionable cuando las instrucciones detalladas solas no alcanzan → **Tema 1** (Trampa 1)
- [x] El rol de los ejemplos para mostrar cómo resolver casos ambiguos (qué tool elegir ante un pedido ambiguo, huecos de cobertura de tests por rama) → **Tema 3** (Trampas 2 y 3)
- [x] Cómo los ejemplos permiten generalizar el juicio a patrones nuevos en lugar de reconocer solo casos previstos → **Tema 3** (Trampa 2)
- [x] La efectividad de los ejemplos para reducir alucinaciones en extracción (medidas informales, estructuras de documento variadas) → **Tema 5** (Trampa 5)

*Skills in*
- [x] Crear 2 a 4 ejemplos dirigidos a escenarios ambiguos que muestren por qué se eligió una acción frente a alternativas plausibles → **Temas 2 y 3** (Trampa 2)
- [x] Incluir ejemplos que muestren el formato de salida deseado (location, issue, severity, suggested fix) → **Tema 1** (Trampa 1)
- [x] Dar ejemplos que distingan patrones de código aceptables de problemas reales, para bajar falsos positivos y permitir generalizar → **Tema 4** (Trampa 4)
- [x] Usar ejemplos para mostrar cómo manejar estructuras de documento variadas (citas en el texto vs. bibliografía, sección de metodología vs. detalles en el texto) → **Tema 5** (Trampa 5)
- [x] Agregar ejemplos de extracción correcta de documentos con formatos variados para corregir campos obligatorios que salen vacíos o null → **Tema 5** (Trampa 5)

**Complementa otras tareas:** Q3 y el escalamiento de 5.2 (Tema 3) · Q2 y las descripciones de tools de 2.1 (Tema 6) · historial completo de 5.1 (Tema 10) · instancia independiente de 4.6 (Tema 7).

**De la documentación, no de la guía** (vale saberlo; la guía no lo pregunta directo): `<example>` tags y Relevant/Diverse/Structured (Temas 1–2) · adaptive thinking, `effort`, `budget_tokens` deprecado (Tema 7) · prefill 400 y sus alternativas (Tema 8) · sampling parameters con 400 (Tema 9).

**📘 Curso (útil para entender):** contaminación, el mejor ejemplo al final, dynamic few-shot y comparar con zero-shot (Tema 2) · cuándo ayuda CoT (Tema 7) · límites de largo y una regla en un solo lugar (Tema 8) · clarification turn, drift y reinicio (Tema 10).

---

## Autoevaluación oral

1. ¿Por qué un ejemplo fija el formato mejor que una descripción? ¿En qué situación dice la guía que few-shot es lo más efectivo?
2. ¿Cuántos ejemplos y de qué casos? ¿Por qué cada ejemplo tiene que mostrar el razonamiento y nombrar la alternativa descartada?
3. ¿Cómo usás ejemplos para bajar los falsos positivos de un revisor? ¿Y para que una extracción no deje campos vacíos ni invente datos?
4. Contá la Q2 y la Q3: ¿en cuál few-shot es la respuesta y en cuál es el distractor, y por qué?
5. ¿Qué pasa hoy con el prefill, con `budget_tokens` y con la temperatura? ¿Qué se usa en su lugar? ¿Por qué SoporteBot "se olvida" de un mensaje al siguiente?

---

## Preguntas tipo examen

Las preguntas tipo examen de este capítulo están en [`04-practica/modulo-4.md`](../04-practica/modulo-4.md), junto con las del resto del módulo 4. Hacelas cuando termines **todos** los capítulos del módulo, de a una y sin mirar la respuesta.

---

## Revisión contra el blueprint oficial

Qué puede salir en el examen de 4.2 que el curso de Jacob **no cubre o cubre flojo**, y dónde quedó explicado:

1. **Ejemplos dirigidos a los casos ambiguos, con el razonamiento** frente a la alternativa plausible, y la generalización a patrones nuevos. El curso habla de calidad y formato, no de esto. → Tema 3.
2. **Ejemplos de código aceptable vs. problema real** para bajar falsos positivos. → Tema 4.
3. **Extracción**: estructuras variadas, campos vacíos, alucinación y `null`. → Tema 5.
4. **2 a 4 ejemplos** (el curso dice 3; la doc, 3 a 5). → Tema 2.
5. **Cuándo few-shot es distractor** (Q2) y cuándo es la respuesta (Q3). → Temas 3 y 6.
6. **Datos del curso desactualizados:** `budget_tokens` (Tema 7), temperatura baja para clasificar (Tema 9). Las slides ya corrigen ambos; el companion no.

No encontré otros huecos para 4.2.

