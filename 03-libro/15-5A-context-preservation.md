# Capítulo 15 · 5A · Udemy 16 — Context Preservation (no perder lo importante en conversaciones largas)

*Tarea oficial 5.1 · Primer capítulo del módulo 5*

---

## Dónde estamos

Arranca el último módulo: **módulo 5: Context Management & Reliability** (manejo del contexto y confiabilidad), que vale el **15%** del examen. Son seis tareas de 2,5% cada una. Este capítulo cubre una:
- **5.1** Manage conversation context to preserve critical information across long interactions (manejar el contexto de la conversación para no perder información crítica en interacciones largas).

### Cómo leer este capítulo

Todo lo que leés acá **vale para el examen**, salvo que diga lo contrario. Cuando algo sale solo del curso (útil para entender, pero no central), lo marco con **📘 Curso**. Cuando Jacob dice algo distinto de lo que evalúa la guía, aparece un recuadro así:

> ⚠️ **En el curso vas a escuchar otra cosa.** … **Para el examen: …**

### Un aviso sobre este capítulo

El curso cubre bien tres puntos de la guía: por qué los resúmenes pierden datos, el bloque de hechos persistente y recortar las respuestas de las tools. **Le faltan otros cuatro**: la capa separada por cada problema del cliente, el orden de la entrada para el efecto "lost in the middle", qué tienen que devolver los subagentes (metadatos y datos estructurados) y mandar el historial completo en cada request (el curso lo trata en 4B). Esos salen de la guía. También hay algunos datos del curso sobre la ventana de contexto que ya no son exactos; están marcados.

Esta tarea cae sobre todo en dos escenarios del examen: el **1, Customer Support Resolution Agent** (SoporteBot) y el **3, Multi-Agent Research System**.

## De dónde venimos

En 4B viste que la API es **stateless**: no recuerda nada, así que cada request lleva el historial completo. En 4A viste que los documentos largos van arriba y la pregunta al final. Y en 1C armaste un sistema con coordinador y subagentes. Este capítulo junta esas piezas con una pregunta: **cuando la conversación se hace larga, ¿cómo te asegurás de que Claude no pierda lo que importa?**

## Mapa del capítulo

**Parte 1 — La ventana de contexto (lecciones 98 y 99).**
1. Qué entra en la ventana y por qué más no es mejor.

**Parte 2 — Que los datos no se pierdan (lecciones 100 y 101).**

2. Por qué los resúmenes pierden datos.
3. El bloque de "case facts" y una capa por cada problema.

**Parte 3 — Las respuestas de las tools (lecciones 102 y 103).**

4. Recortar los tool results antes de que se acumulen.

**Parte 4 — Entradas largas y subagentes (guía oficial).**

5. Lost in the middle: dónde poner lo importante.
6. Qué tienen que devolver los subagentes.
7. 📘 Server-side compaction (deck 138).

---

# Parte 1 — La ventana de contexto

## Tema 1 — The context window (la ventana de contexto): qué entra y por qué más no es mejor

### Qué es

La **context window** (ventana de contexto) es todo lo que Claude puede ver en una llamada: el system prompt, el historial de la conversación, los documentos, las definiciones de las tools, los resultados de las tools y también la respuesta que está generando. Se mide en **tokens** (pedazos de texto; un token es más o menos una palabra corta o parte de una palabra). Todo eso cuenta contra el límite.

Como la API es **stateless** (no guarda nada entre llamadas), para que Claude "se acuerde" de la conversación tu aplicación tiene que **mandar el historial completo en cada request**. La guía lo pone como un punto de conocimiento de esta tarea: si mandás solo el último mensaje, Claude pierde el hilo.

El problema es que el historial crece con cada turno. Y **más contexto no es mejor**: a medida que crece la cantidad de tokens, la precisión baja (la documentación lo llama **context rot**, el contexto que "se pudre"). Los tokens irrelevantes no son neutrales: compiten por la atención del modelo con lo que sí importa. Por eso este capítulo trata de **qué** dejar en la ventana, no de cómo meter más.

Si te pasás del límite, la API **no recorta en silencio**: devuelve un error 400 ("prompt is too long"), o la respuesta se corta.

> ⚠️ **En el curso vas a escuchar otra cosa.** El resumen escrito del curso (companion) dice que una ventana llena produce "hard truncation" y recomienda elegir el modelo según el tamaño de la ventana: Haiku para tareas cortas, Opus para codebases enteros. Las slides de Jacob ya lo corrigen (muestran el error 400 y aclaran que Opus no tiene más ventana que Sonnet). **Para el examen:** la API no trunca sola, da error. Y "pasar a un modelo con una ventana más grande" casi siempre es un **distractor**: solo posterga el problema, porque con más tokens la precisión sigue bajando. La respuesta es dejar en la ventana solo lo que importa (Temas 3 a 6).

La guía también nombra los **token budgets** (presupuestos de tokens): repartir de antemano el espacio entre system prompt, historial, documentos y respuesta. 📘 Curso: Jacob agrega contar los tokens antes de mandar (`count_tokens`) y usar **prompt caching** (guardar en caché el prefijo que no cambia, como el system prompt) para bajar costo y latencia.

### Para el examen

- Cada request lleva **el historial completo** (la API es stateless).
- Más contexto no es mejor: lo irrelevante le quita atención a lo importante.
- "Usar un modelo con más contexto" → distractor.

### Cómo se une

Como el historial crece, la tentación es resumirlo. Ahí aparece el problema central de esta tarea.

---

# Parte 2 — Que los datos no se pierdan

## Tema 2 — Progressive summarization (resumen progresivo): por qué pierde datos

### Qué es

Una forma común de controlar el tamaño del historial es el **progressive summarization** (resumen progresivo): cada tanto, los turnos viejos se reemplazan por un resumen. El resumen se lee bien, pero **cambia precisión por fluidez**. Lo que se pierde son justo los datos concretos: los **números, los porcentajes, las fechas** y **lo que el cliente dijo que esperaba**. "El cliente pidió un reembolso de $450.000 por el pedido 88213 antes del viernes" se convierte en "el cliente pidió un reembolso por un pedido".

Y la pérdida **se acumula**: cada pasada resume un resumen anterior. Un límite que el cliente dijo en el turno 5 puede haber desaparecido del todo en el turno 20. Lo peor es que nadie avisa: el resumen no dice qué tiró.

📘 Curso: Jacob nombra los síntomas que vas a ver. El agente olvida un límite que ya se había acordado (**constraint amnesia**), confunde dos pedidos o dos personas (**entity confusion**) o cambia una decisión ya tomada (**decision drift**).

### Ejemplo

Un cliente de TiendaX tiene una conversación larga con SoporteBot sobre un televisor que llegó roto. En el turno 4 dice: "Pagué $450.000, el pedido es el 88213, y necesito la plata antes del 15 porque viajo". En el turno 18, después de dos resúmenes, SoporteBot le ofrece "un reembolso parcial" y le pregunta el número de pedido otra vez. Perdió el monto, el número y la fecha que el cliente esperaba.

### Para el examen

- El resumen progresivo **pierde números, porcentajes, fechas y expectativas del cliente**, y la pérdida se acumula.
- Distractores: "resumir más seguido", "mejorar el prompt del resumidor", "pedirle que conserve los números". Todos siguen dependiendo de un resumen.

### Cómo se une

Si el resumen pierde los datos, la solución es **sacarlos antes** y guardarlos aparte.

---

## Tema 3 — The case facts block (el bloque de hechos del caso) y una capa por cada problema

### Qué es

La guía pide **extraer los datos transaccionales** (montos, fechas, números de pedido, estados) a un bloque persistente de **"case facts"** (hechos del caso) que se **incluye en cada prompt**, **fuera del historial resumido**. El historial se puede resumir todo lo que quieras: el bloque no pasa por el resumidor, así que los datos nunca se pierden. El curso lo llama "extract first, summarize second": primero se sacan los hechos, después se resume.

Cuando la conversación trata **varios problemas a la vez** (el televisor roto y además un cobro duplicado), la guía pide guardar los datos estructurados **de cada problema por separado** (su número de pedido, su monto, su estado), en una capa aparte. Así no se mezclan: el monto del televisor no termina asociado al cobro duplicado.

📘 Curso: Jacob agrega tres detalles prácticos:
- El lugar más confiable para el bloque es una sección dedicada del **system prompt**.
- Hay que **decirle explícitamente** a Claude que lo consulte ("antes de responder, revisá `<case_facts>`"). Un bloque que nadie le dice que use no sirve.
- Si un dato cambia (el cliente corrige el monto), hay que decidir si se reemplaza o si se guarda la historia del cambio. Si el cambio es importante, se registran los dos valores y se le pregunta al cliente cuál vale.
- (Doc) Si el bloque cambia en cada turno y está al principio del system prompt, invalida la caché de todo lo que viene después; conviene ubicarlo después de las partes que no cambian.

### Cómo se configura

```xml
<case_facts>
customer_id: C-20431
expectation: "necesito la plata antes del 15 porque viajo"

issue_1:
  order_id: 88213
  item: Televisor 50"
  amount_cents: 45000000
  status: reembolso aprobado, pendiente de acreditación

issue_2:
  order_id: 88247
  problem: cobro duplicado
  amount_cents: 1250000
  status: en revisión por pagos
</case_facts>

Antes de responder, revisá <case_facts> para los números de pedido, montos, fechas y lo que el cliente espera.
```

### Ejemplo

Con este bloque, SoporteBot puede resumir los primeros 15 turnos de la conversación sin problema. En el turno 18 sigue sabiendo el monto exacto, el número de pedido y la fecha que el cliente necesita, porque esos datos están en `<case_facts>`, no en el resumen.

### Para el examen

- Se pierden montos, fechas o números en conversaciones largas → **bloque de case facts, incluido en cada prompt y fuera del historial resumido**.
- Varios problemas en la misma sesión → **datos estructurados separados por problema**.
- Distractores: meter los hechos **dentro** del resumen, ponerlos solo al principio de la conversación (después se resumen), o un resumen único que mezcla todos los problemas.

### Cómo se une

El bloque protege los datos que ya están. La otra fuente de ruido en una conversación larga son las respuestas de las tools, que traen mucho más de lo necesario.

---

# Parte 3 — Las respuestas de las tools

## Tema 4 — Trimming tool outputs (recortar las respuestas de las tools) antes de que se acumulen

### Qué es

Las APIs devuelven muchos más datos de los que una tarea necesita. La guía da el ejemplo de una consulta de pedido que trae **más de 40 campos cuando solo 5 son relevantes**. Cada campo de más cuesta tokens, y además **se acumula**: después de cinco llamadas a tools, el historial tiene cinco respuestas enormes llenas de ruido, y el dato importante queda enterrado.

La solución de la guía es **recortar la respuesta a los campos relevantes antes de que entre al contexto**. No después, cuando el historial ya está lleno: antes. Se hace en el código que envuelve a la tool (el **wrapper**), con una lista de campos permitidos (**allowlist**): la tool consulta la API completa, pero a Claude solo le devuelve lo que necesita para esa tarea.

📘 Curso: Jacob distingue tres formas de recortar:
- **Filter** (filtrar): quedarse con una lista fija de campos. Es lo que pide la guía, y sirve cuando la estructura de la respuesta es estable.
- **Summarize** (resumir): pasar la respuesta por un modelo chico que extrae lo relevante. Lo propone solo cuando cada proveedor devuelve una estructura distinta.
- **Reference** (referenciar): guardar la respuesta entera afuera y pasarle a Claude solo un identificador, para que la pida si la necesita.

Agrega dos consejos más: recortar **en el modelo**, no solo en lo que se muestra en pantalla, y **registrar qué campos se descartan**, para revisar el registro cuando algo falla más adelante.

### Cómo se configura

```python
RETURN_FIELDS = ["order_id", "status", "delivered_at", "total_cents", "return_eligible_until"]

def lookup_order_for_returns(order_id: str) -> dict:
    full = orders_api.get(order_id)                # 43 campos
    return {k: full[k] for k in RETURN_FIELDS}     # a Claude le llegan 5
```

### Ejemplo

SoporteBot atiende devoluciones. `lookup_order` devolvía 43 campos (dirección de facturación, historial de envíos, impuestos por línea, datos del transportista…). En una conversación con tres consultas, el historial tenía unos 6.000 tokens de datos de pedido, y Claude empezó a confundir la fecha de entrega con la de compra. El equipo arma un wrapper que devuelve solo los cinco campos que importan para una devolución. El ruido desaparece y la confusión también.

### Para el examen

- Tool results que llenan el contexto → **recortar a los campos relevantes antes de que se acumulen** (en el wrapper de la tool).
- Distractores: guardar la respuesta completa "por si acaso", recortar o resumir **después** de que el historial se llenó, recortar solo en la interfaz.

La guía solo nombra **filtrar a los campos relevantes**. Si una opción ofrece "resumir el tool output con otro modelo" frente a "devolver solo los campos relevantes", elegí filtrar, salvo que el enunciado diga que la estructura de las respuestas cambia y no se puede prever (que es justo el caso en que Jacob propone el resumen).

La documentación tiene además **context editing**, que borra del historial los tool results viejos cuando el contexto pasa un umbral. Sirve, pero actúa **después** de que se acumularon; la guía pide recortar **antes**.

### Cómo se une

Recortar evita que lo importante quede enterrado entre ruido. Pero aunque el contenido sea todo relevante, si es largo aparece otro problema: **dónde** está cada cosa.

---

# Parte 4 — Entradas largas y subagentes

## Tema 5 — Lost in the middle (perdido en el medio): dónde poner lo importante

### Qué es

La guía describe el efecto **lost in the middle**: en una entrada larga, el modelo procesa bien lo que está **al principio y al final**, pero puede **omitir** lo que queda en el medio. No es un problema de razonamiento: es un problema de posición. El mismo hallazgo se encuentra si está arriba y se pierde si está en la mitad.

Esto pega fuerte en el escenario de investigación: un agente de síntesis recibe los resultados de diez subagentes concatenados, y los de las fuentes del medio no aparecen en el informe final.

La solución de la guía tiene dos partes:
1. Poner un **resumen de los hallazgos clave al principio** de la entrada agregada.
2. Organizar los resultados detallados con **encabezados explícitos por sección**, para que cada parte sea fácil de ubicar.

Es la misma idea de 4A (documentos con etiquetas), aplicada a la salida de varios agentes. Y no se contradice con "documentos arriba, pregunta al final": el resumen encabeza el bloque de datos, y la consigna para el sintetizador sigue yendo al final.

### Ejemplo

El agente de investigación de TiendaX analiza el mercado de electrodomésticos con diez subagentes, uno por fuente. El informe final siempre cita las fuentes 1, 2, 9 y 10, y casi nunca las del medio, aunque la fuente 5 tenía el dato más importante (un competidor que bajó precios un 20%). El equipo cambia cómo se arma la entrada del sintetizador: arriba, un bloque "Hallazgos clave", con una línea por fuente; después, cada resultado bajo su encabezado (`## Fuente 5 — Informe de precios Q3`). El dato de la fuente 5 empieza a aparecer.

### Para el examen

- La síntesis omite hallazgos de las secciones del medio → **resumen de hallazgos clave al principio + encabezados por sección**.
- Distractores: "pedirle que preste atención a todas las secciones", culpar a la fuente o al subagente del medio, o usar un modelo con más contexto.

### Cómo se une

Para que el sintetizador pueda armar ese resumen y atribuir bien, los subagentes tienen que devolver la información en la forma correcta.

---

## Tema 6 — Qué tienen que devolver los subagentes: metadatos y datos estructurados

### Qué es

En un sistema de varios agentes, lo que devuelve un subagente se convierte en la entrada de otro. La guía pide dos cosas sobre esa salida:

**Metadatos.** Cada subagente tiene que incluir en su salida estructurada las **fechas**, la **ubicación de la fuente** (qué documento, qué página, qué URL) y el **contexto metodológico** (cómo se obtuvo el dato: encuesta, estimación, medición). Sin eso, el sintetizador no puede atribuir bien ni saber si dos datos que difieren son de fechas distintas. Lo retomamos en 5D, cuando veas la procedencia de la información.

**Datos estructurados en vez de texto largo.** Si el agente que recibe tiene un **presupuesto de contexto limitado**, el que envía no le tiene que mandar todo su razonamiento ni el contenido completo que leyó. Tiene que devolver **datos estructurados**: los hechos clave, las citas y un puntaje de relevancia. Eso ocupa mucho menos y es justo lo que el siguiente necesita.

### Cómo se configura

```json
{
  "source": "Informe de precios Q3 — Cámara de Comercio, p. 12",
  "published": "2026-10-05",
  "method": "relevamiento de 40 comercios",
  "key_facts": ["El competidor X bajó un 20% los precios de heladeras en septiembre."],
  "citation": "…los precios de lista de heladeras cayeron un 20%…",
  "relevance": 0.9
}
```

### Ejemplo

El subagente de búsqueda devolvía al sintetizador tres páginas de texto por fuente, con todo su razonamiento ("primero busqué…, después encontré…"). Con diez fuentes, el sintetizador se quedaba sin espacio y perdía datos. El equipo cambia el contrato: cada subagente devuelve el JSON de arriba. La entrada del sintetizador pasa de unos 40.000 tokens a 4.000, y cada dato llega con su fecha y su fuente.

### Para el examen

- La síntesis atribuye mal o confunde fechas → los subagentes tienen que devolver **metadatos** (fecha, ubicación de la fuente, método).
- El agente que recibe tiene poco contexto → el que envía devuelve **datos estructurados** (hechos clave, citas, relevancia), no razonamiento ni contenido completo.

### Cómo se une

Hasta acá, todo lo que pide la guía. El curso agrega un suplementario sobre una función de la API que resume el contexto automáticamente.

---

## Tema 7 — 📘 Server-side compaction (compactación del lado del servidor, deck 138)

### Qué es

**Server-side compaction** es una función de la API (en beta) que, cuando la conversación pasa cierto tamaño, **resume automáticamente** los turnos anteriores y sigue desde ese resumen. La documentación la presenta como la estrategia principal de manejo de contexto para flujos agénticos largos, y te ahorra tener que programar tu propio resumidor.

Lo importante es que **sigue siendo un resumen**: tiene el mismo problema del Tema 2. Jacob lo dice en el deck: lo que no quedó en el resumen desaparece del contexto, así que hay que tratar el historial resumido como "la idea general, no el registro", y **guardar el estado importante fuera del historial**.

La documentación permite indicarle qué tiene que conservar el resumen (con `instructions`, que **reemplazan** las instrucciones por defecto, no se suman). Igual, para el examen, ante un monto o una fecha la respuesta sigue siendo el bloque de case facts.

La guía no nombra esta función. La única compactación que menciona es `/compact` de Claude Code, que vemos en 5C.

### Para el examen

- Si una opción propone "activar compaction" o "un resumen automático" para no perder un monto o una fecha → **distractor**. La respuesta sigue siendo el **bloque de case facts**.

---

## Cómo se une todo

Cada request lleva el historial completo, porque la API no recuerda nada, pero más contexto no es mejor: lo irrelevante compite con lo importante (Tema 1). Cuando el historial se resume, se pierden justo los números, las fechas y lo que el cliente esperaba (Tema 2). Por eso esos datos se **extraen a un bloque de case facts**, incluido en cada prompt y fuera del resumen, con una capa separada por cada problema (Tema 3). Las respuestas de las tools se **recortan a los campos relevantes antes** de entrar al contexto (Tema 4). En entradas largas, lo importante va **arriba**, con encabezados por sección, porque lo del medio se pierde (Tema 5). Y los subagentes devuelven **datos estructurados con metadatos**, no texto largo (Tema 6). La compactación automática es útil, pero es un resumen más (Tema 7).

## Lo que viene

**5B · Udemy 17 — Escalation and Error Propagation**, tareas 5.2 y 5.3: cuándo escalar a una persona y cómo resolver la ambigüedad, y cómo propagar errores entre agentes sin esconderlos ni frenar todo el sistema.

---

## Las trampas del examen

Cada trampa tiene el mismo orden: la situación, **qué elegir en el examen (✅)**, las opciones que tientan (❌) con por qué tientan y por qué están mal, y una regla para recordar.

### Grupo: Datos que se pierden

#### Trampa 1 · El monto que desaparece

**La situación.** En conversaciones largas, SoporteBot olvida el monto del reembolso, el número de pedido y la fecha que el cliente pidió. El historial se resume cada 10 turnos (Temas 2 y 3).

**✅ En el examen elegí:** **extraer esos datos a un bloque de case facts, incluido en cada prompt y fuera del historial resumido**.

**❌ Las que tientan:**

❌ **"Instruir al resumidor para que conserve todos los números y fechas".**
- *Tienta porque:* ataca el problema directamente.
- *Está mal porque:* sigue dependiendo de un resumen, que condensa y pierde datos en cada pasada.

❌ **"Usar un modelo con una ventana más grande y no resumir".**
- *Tienta porque:* si no se resume, no se pierde nada.
- *Está mal porque:* solo posterga el problema; con más tokens la precisión baja igual.

❌ **"Resumir más seguido para que cada resumen sea más chico".**
- *Tienta porque:* parece más controlado.
- *Está mal porque:* más pasadas de resumen significan más pérdida acumulada.

> 🧠 **Para recordar:** los datos **se extraen antes** de resumir y viven **fuera** del resumen.

#### Trampa 2 · Dos problemas mezclados

**La situación.** Un cliente reclama por un televisor roto y por un cobro duplicado en la misma conversación. SoporteBot termina aplicando el monto de uno al otro (Tema 3).

**✅ En el examen elegí:** **guardar los datos estructurados de cada problema por separado** (número de pedido, monto y estado de cada uno).

**❌ Las que tientan:**

❌ **"Un resumen más detallado de toda la conversación".**
- *Tienta porque:* más detalle parece más precisión.
- *Está mal porque:* sigue mezclando los dos problemas en un solo texto.

> 🧠 **Para recordar:** varios problemas = **una capa por problema**.

#### Trampa 3 · La compactación automática

**La situación.** Para no perder datos en sesiones largas, alguien propone activar la compactación automática del lado del servidor (Tema 7).

**✅ En el examen elegí:** **el bloque de case facts**, con o sin compactación.

**❌ Las que tientan:**

❌ **"Activar server-side compaction para que se encargue del contexto".**
- *Tienta porque:* la documentación la recomienda para conversaciones largas.
- *Está mal porque:* es un resumen, y tiene la misma pérdida de números y fechas.

> 🧠 **Para recordar:** cualquier resumen es **la idea general, no el registro**.

### Grupo: Tool results

#### Trampa 4 · Los 43 campos

**La situación.** Después de tres o cuatro consultas de pedidos, el contexto de SoporteBot está lleno y empieza a confundir fechas. `lookup_order` devuelve 43 campos y la tarea usa 5 (Tema 4).

**✅ En el examen elegí:** **recortar la respuesta de la tool a los campos relevantes antes de que entre al contexto**.

**❌ Las que tientan:**

❌ **"Guardar la respuesta completa por si después hace falta algún campo".**
- *Tienta porque:* parece más seguro.
- *Está mal porque:* cada campo de más se acumula en cada turno y entierra lo importante.

❌ **"Resumir el historial cuando se llena".**
- *Tienta porque:* libera espacio.
- *Está mal porque:* actúa **después** de que el ruido se acumuló, y el resumen pierde datos.

❌ **"Activar context editing para que borre los tool results viejos".**
- *Tienta porque:* libera espacio automáticamente.
- *Está mal porque:* actúa después de que se acumularon; la guía pide recortar antes.

❌ **"Mostrar solo los 5 campos en la interfaz del agente".
- *Tienta porque:* el operador ve lo correcto.
- *Está mal porque:* el modelo sigue recibiendo los 43.

> 🧠 **Para recordar:** se recorta **en la tool, antes** de que entre al contexto.

### Grupo: Entradas largas y subagentes

#### Trampa 5 · Las fuentes del medio

**La situación.** El informe del agente de investigación cita siempre las primeras y las últimas fuentes, y casi nunca las del medio (Tema 5).

**✅ En el examen elegí:** **un resumen de hallazgos clave al principio de la entrada y encabezados explícitos por sección**.

**❌ Las que tientan:**

❌ **"Agregar al prompt: 'Considerá todas las fuentes por igual'".**
- *Tienta porque:* pide justo lo que falta.
- *Está mal porque:* es un efecto de posición; se corrige con estructura, no con una instrucción.

❌ **"Revisar los subagentes que procesan las fuentes del medio".**
- *Tienta porque:* parece que fallan esos subagentes.
- *Está mal porque:* sus resultados llegan bien; se pierden en la síntesis por la posición.

> 🧠 **Para recordar:** lo importante, **arriba**; el resto, **con encabezados**.

#### Trampa 6 · Datos sin fecha ni fuente

**La situación.** El informe final atribuye un dato a la fuente equivocada y presenta como contradicción dos cifras que eran de años distintos (Tema 6).

**✅ En el examen elegí:** **que los subagentes devuelvan salida estructurada con metadatos**: fecha, ubicación de la fuente y método.

**❌ Las que tientan:**

❌ **"Pedirle al sintetizador que verifique las fechas en internet".**
- *Tienta porque:* buscaría el dato que falta.
- *Está mal porque:* el dato ya lo tenía el subagente; hay que pedirle que lo devuelva.

> 🧠 **Para recordar:** sin **metadatos**, el sintetizador no puede atribuir.

#### Trampa 7 · El razonamiento que no entra

**La situación.** El sintetizador tiene poco espacio de contexto y recibe de cada subagente varias páginas con todo su razonamiento (Tema 6).

**✅ En el examen elegí:** **que los subagentes devuelvan datos estructurados**: hechos clave, citas y relevancia.

**❌ Las que tientan:**

❌ **"Darle al sintetizador un modelo con más contexto".**
- *Tienta porque:* entra todo.
- *Está mal porque:* el problema es lo que se manda; más contexto no mejora la precisión.

❌ **"Que el sintetizador resuma cada entrada antes de usarla".**
- *Tienta porque:* reduce el tamaño.
- *Está mal porque:* gasta el contexto en leer todo igual; el recorte tiene que venir del que envía.

> 🧠 **Para recordar:** entre agentes, **datos**, no razonamiento.

#### Trampa 8 · El bot que no se acuerda

**La situación.** Para ahorrar tokens, la aplicación manda a la API solo el último mensaje del cliente, y SoporteBot pierde el hilo (Tema 1).

**✅ En el examen elegí:** **mandar el historial completo en cada request** (y controlar el tamaño con case facts y recortes, no cortando el historial).

**❌ Las que tientan:**

❌ **"Activar una opción para que la API recuerde la conversación".**
- *Tienta porque:* parece lo natural.
- *Está mal porque:* la API es stateless: el historial lo manda tu aplicación.

> 🧠 **Para recordar:** la API no recuerda; **el historial lo mandás vos**.

---

## Checklist oficial

**Tarea 5.1 — Manage conversation context to preserve critical information across long interactions**

*Knowledge of*
- [x] Los riesgos del resumen progresivo: condensar números, porcentajes, fechas y expectativas del cliente en resúmenes vagos → **Tema 2** (Trampa 1)
- [x] El efecto "lost in the middle": el modelo procesa bien el principio y el final, pero puede omitir lo del medio → **Tema 5** (Trampa 5)
- [x] Cómo los tool results se acumulan y consumen tokens de forma desproporcionada (40+ campos cuando importan 5) → **Tema 4** (Trampa 4)
- [x] La importancia de pasar el historial completo en cada request para mantener la coherencia → **Tema 1** (Trampa 8)

*Skills in*
- [x] Extraer los datos transaccionales (montos, fechas, números de pedido, estados) a un bloque persistente de "case facts" incluido en cada prompt, fuera del historial resumido → **Tema 3** (Trampa 1)
- [x] Extraer y persistir datos estructurados por problema (IDs, montos, estados) en una capa separada para sesiones con varios problemas → **Tema 3** (Trampa 2)
- [x] Recortar las respuestas de las tools a los campos relevantes antes de que se acumulen → **Tema 4** (Trampa 4)
- [x] Poner un resumen de hallazgos clave al principio de las entradas agregadas y organizar los detalles con encabezados por sección → **Tema 5** (Trampa 5)
- [x] Pedir a los subagentes metadatos (fechas, ubicación de la fuente, contexto metodológico) en su salida estructurada → **Tema 6** (Trampa 6)
- [x] Que los agentes de arriba devuelvan datos estructurados (hechos clave, citas, relevancia) en vez de contenido largo y razonamiento cuando el agente de abajo tiene poco contexto → **Tema 6** (Trampa 7)

**De la documentación, no de la guía** (vale saberlo; la guía no lo pregunta directo): context rot y el error 400 al pasarse (Tema 1) · context editing (Tema 4) · server-side compaction (Tema 7).

**📘 Curso (útil para entender):** `count_tokens` y prompt caching (Tema 1) · constraint amnesia, entity confusion, decision drift (Tema 2) · dónde poner el bloque y decirle que lo use (Tema 3) · filter, summarize, reference y registrar lo descartado (Tema 4).

---

## Autoevaluación oral

1. ¿Por qué la API necesita el historial completo en cada request? ¿Por qué "más contexto" no es la solución?
2. ¿Qué datos pierde un resumen progresivo? ¿Cómo funciona el bloque de case facts y dónde va? ¿Qué hacés si hay varios problemas en la misma conversación?
3. ¿Por qué hay que recortar las respuestas de las tools y **cuándo**? ¿Dónde se hace?
4. ¿Qué es "lost in the middle" y cómo se corrige?
5. ¿Qué tienen que devolver los subagentes al sintetizador, y por qué?

---

## Preguntas tipo examen

Las preguntas tipo examen de este capítulo están en [`04-practica/modulo-5.md`](../04-practica/modulo-5.md), junto con las del resto del módulo 5. Hacelas cuando termines **todos** los capítulos del módulo, de a una y sin mirar la respuesta.

---

## Revisión contra el blueprint oficial

Qué puede salir en el examen de 5.1 que el curso de Jacob **no cubre o cubre flojo**, y dónde quedó explicado:

1. **Las expectativas del cliente** como dato que pierde el resumen (la guía las nombra explícitamente). → Tema 2.
2. **Una capa separada por cada problema** en sesiones con varios problemas. → Tema 3.
3. **Lost in the middle y su solución**: resumen arriba y encabezados por sección. El curso lo menciona solo como síntoma. → Tema 5.
4. **Metadatos y datos estructurados en la salida de los subagentes.** → Tema 6.
5. **El historial completo en cada request** (el curso lo trata en 4B, no acá). → Tema 1.
6. **Datos del curso que no valen:** "hard truncation" y elegir el modelo por el tamaño de la ventana. → Tema 1.

No encontré otros huecos para 5.1.

