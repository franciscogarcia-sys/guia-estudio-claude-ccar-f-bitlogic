# Capítulo 4 · 1D · Udemy 5 — Reliability & Human Oversight (confiabilidad y supervisión humana)

*Hooks and Programmatic Enforcement · Tareas oficiales 1.4 y 1.5*

---

## Dónde estamos

Este capítulo cubre dos tareas del Dominio 1, y cada una pesa 3,86% del examen:
- **1.4** Implement multi-step workflows with enforcement and handoff patterns (implementar flujos de varios pasos que **obligan** a cumplir reglas y que **traspasan** el caso a un humano cuando hace falta).
- **1.5** Apply Agent SDK hooks for tool call interception and data normalization (usar **hooks** del Agent SDK para interceptar llamadas a tools y normalizar datos).

### Cómo leer este capítulo

Todo lo que leés acá **vale para el examen**, salvo que diga lo contrario. Cuando algo sale solo del curso (útil para entender, pero no central), lo marco con **📘 Curso**. Cuando Jacob dice algo distinto de lo que evalúa la guía, aparece un recuadro así:

> ⚠️ **En el curso vas a escuchar otra cosa.** … **Para el examen: …**

### Un aviso sobre este capítulo

La Parte 1 (Temas 1 a 4, qué hacer cuando algo falla) sale casi entera del curso: sirve para razonar, pero la guía no la evalúa de forma directa en 1.4 y 1.5. El corazón de estas dos tareas está en las Partes 2 y 3: hacer que las reglas se cumplan con código y hooks, y pasarle el caso a un humano.

## De dónde venimos

En **1A** viste el **agentic loop** (el ciclo en el que el modelo pide una tool, recibe el resultado y decide el paso siguiente) y que un `tool_result` con error lleva `is_error: true` y un mensaje claro. También viste que el loop tiene un límite de vueltas como red de seguridad, y que hay que escalar a un humano cuando el agente no avanza. En **1B** viste que algunas acciones son **irreversibles** (un reembolso, un mail enviado), que antes de hacerlas conviene preguntar, y un `guard` en código que pedía confirmación antes de ciertas tools. En **1C** viste que los errores tienen que viajar **con contexto** (structured error context) y que el coordinador decide entre reintentar, sustituir o escalar.

Este capítulo junta todo eso y responde una pregunta: **¿cómo hacés que una regla se cumpla siempre, y qué hacés cuando algo falla?**

## Mapa del capítulo

**Parte 1 — Cuando algo falla (lo que dice el curso).** Primero se clasifica el error, después se detecta, se reintenta si corresponde y, si nada funciona, se usa una alternativa o se escala.
1. Error types (tipos de error): de dónde viene la falla.
2. Error detection (detectar errores) antes de que se propaguen.
3. Retry logic (lógica de reintentos): cuándo reintentar y cuándo abortar.
4. Fallback chains (cadenas de alternativas) y graceful degradation (degradación controlada).

**Parte 2 — Hacer que las reglas se cumplan (el corazón de 1.4 y 1.5).** El prompt no alcanza para las reglas obligatorias, así que van en código. Los hooks son la forma concreta de ponerlas en código.

5. Por qué el prompt no alcanza: guidance (guía) vs. enforcement (obligación).
6. Programmatic prerequisites (prerrequisitos programáticos).
7. Validation layers (capas de validación): antes, después y durante.
8. Hooks: qué son y qué eventos existen.
9. Hooks en el Agent SDK: cómo se configuran.
10. Un hook que bloquea y redirige: el reembolso de más de USD 500.
11. Un hook que normaliza datos: PostToolUse.
12. ¿Hook o prompt? Cómo decidir.

**Parte 3 — Varios problemas y el traspaso a un humano.** Qué hacer cuando el cliente trae varios problemas juntos, y cómo pasarle el caso a una persona cuando el hook lo bloquea.

13. Pedidos con varios problemas: descomponer e investigar en paralelo.
14. Interruption points (puntos de pausa) y handoff (traspaso) a un humano.

---

# Parte 1 — Cuando algo falla

## Tema 1 — Error types (tipos de error): de dónde viene la falla

### Qué es

Cuando un agente falla, la reacción más natural es reintentar. Pero no todos los errores se arreglan igual: algunos se resuelven solos si esperás un poco, otros van a fallar cada vez, y otros ni siquiera son culpa de la tool. Por eso, antes de decidir qué hacer con un error, hay que saber **de dónde viene**.

El curso divide los errores en tres grupos según su origen. Un **tool error** (error de la tool) es cuando la tool que el agente llamó falló; por ejemplo, la API de pedidos no respondió. Un **reasoning error** (error de razonamiento) es cuando la tool funcionó, pero **el modelo** se equivocó: eligió la tool equivocada, armó un plan malo o interpretó mal un resultado. Un **environment error** (error del entorno) es cuando falla algo que está **debajo** de la tool, como la red, el disco o una credencial vencida.

Los errores de tool, a su vez, se separan según si repetir el pedido podría cambiar el resultado. Un error **transient** (transitorio) podría salir bien si se reintenta, porque la causa es momentánea: un timeout, un **rate limit** (límite de pedidos por minuto) o un servicio caído por un momento. Un error **permanent** (permanente) va a fallar igual cada vez, porque el problema está en el pedido mismo: un dato inválido, un permiso denegado o un recurso que no existe.

Los códigos HTTP dan una pista. Los **5xx** (errores del servidor) suelen ser transitorios. Los **4xx** (errores del pedido) suelen ser permanentes, salvo **408** (timeout) y **429** (rate limit), que son transitorios.

La clasificación importa porque cada tipo se recupera de forma distinta:

| Tipo | Qué hacer | Por qué |
|---|---|---|
| Transitorio | Reintentar, esperando un poco entre intentos (Tema 3) | La causa es momentánea |
| Permanente | No reintentar | Repetir el mismo pedido da el mismo error |
| De razonamiento | No reintentar: corregir el prompt o el contexto, o escalar | El problema está en lo que decidió el modelo, no en la tool |

> ⚠️ **En el curso vas a escuchar otra cosa.** Jacob clasifica los errores en tool, reasoning y environment. La guía oficial no usa esa clasificación: en la tarea 2.2 usa un campo **errorCategory** (categoría del error) con cuatro valores, **transient** (transitorio), **validation** (dato inválido), **business** (regla de negocio, como "reembolso fuera de plazo") y **permission** (permiso), más un campo **isRetryable** (si se puede reintentar). **Para el examen: buscá la opción que devuelve un error estructurado con categoría y si es reintentable.** La idea de fondo es la misma: solo se reintenta lo transitorio.

### Ejemplo

SoporteBot intenta reembolsar el pedido TX-104233. Según lo que pase, la respuesta correcta cambia:
- `process_refund` devuelve **503** (servicio no disponible). Es **transitorio**: el servicio puede volver en segundos, así que SoporteBot reintenta un poco después.
- `process_refund` devuelve **400** "el monto supera lo cobrado". Es **permanente**: el mismo monto va a fallar siempre, así que no reintenta; hay que corregir el monto.
- SoporteBot llamó a `process_refund` con el ID de **otro** pedido porque leyó mal el historial. Es un **error de razonamiento**: la tool hizo lo que le pidieron. Reintentar no sirve; hay que corregir el contexto o escalar.

### Para el examen

- Error de una tool → **error estructurado con categoría e `isRetryable`** (la forma de la guía).
- Solo se reintenta lo **transitorio**.

### Cómo se une

Es la versión detallada del `is_error: true` de 1A y del structured error context de 1C: el error dice **qué tipo** de falla es, para que quien lo recibe sepa qué hacer.

---

## Tema 2 — Error detection (detectar errores) antes de que se propaguen

### Qué es

El error más peligroso es el que **no se ve**. Una **silent failure** (falla silenciosa) es una salida que **parece** exitosa pero está mal: no hay excepción ni código de error, y la ejecución sigue normalmente. Los pasos siguientes construyen sobre ese dato malo, y cuando el error por fin aparece, ya está a varios pasos de distancia de donde se originó, así que cuesta mucho rastrearlo.

Para cortar la cadena, se pone un **validation gate** (punto de validación) entre los pasos: un control que revisa la salida de un paso antes de dejarla pasar al siguiente.

📘 **Curso:** las tres formas de detectar, las cuatro responsabilidades del gate y el logging en cada frontera salen del curso.

### Las tres formas de detectar

**1. Output validation (validar la salida).** Se revisa el resultado contra reglas fijas antes de pasarlo al paso siguiente. Hay tres chequeos típicos. El **schema check** (chequeo de esquema) confirma que estén los campos obligatorios, con el tipo correcto y sin valores nulos inesperados. El **range check** (chequeo de rango) confirma que los números estén dentro de los límites esperados. El **completeness check** (chequeo de completitud) confirma que no falten secciones y que la respuesta no esté cortada.

```python
class StepResult(BaseModel):
    order_id: str                              # schema: obligatorio
    total: float = Field(ge=0, le=100_000)     # rango: entre 0 y 100.000
    summary: str = Field(min_length=20)        # completitud: no vacío ni cortado
    line_items: list[dict] = Field(min_length=1)

result = StepResult.model_validate_json(tool_output)   # falla ANTES de pasar al siguiente paso
```

(`BaseModel` es de **Pydantic**, una librería de Python que valida datos contra una clase. Si el JSON no cumple, tira un error.)

Ojo con un límite: la validación de **schema** confirma la **forma**, no si el contenido es correcto. Un JSON puede tener todos los campos bien tipados y aun así decir algo falso. Para eso está la **semantic validation** (validación semántica), que se pregunta si el resultado tiene sentido dado lo que se pidió.

*Ejemplo:* el agente de reembolsos devuelve `{"order_id": "TX-104233", "amount": 120, "status": "ok"}`. Pasa el schema. Pero el pedido TX-104233 costaba USD 85. La validación semántica detecta que el reembolso es mayor que lo cobrado.

**2. State verification (verificar el estado).** Después de una acción, se confirma que el mundo **realmente** cambió. Que la API devuelva "200 OK" no garantiza que el cambio se haya hecho, así que se vuelve a leer el dato para comprobarlo.

*Ejemplo:* `process_refund` devuelve 200. SoporteBot vuelve a leer el pedido y confirma que el reembolso figura. Si no figura, el "éxito" era falso.

**3. Sanity checks (chequeos de sentido común).** No revisan una regla exacta, sino si la salida es **plausible**. Atrapan lo que pasa los chequeos formales pero no cierra. Algunas preguntas típicas:
- Si la consulta era larga y compleja, ¿la respuesta tiene una sola palabra?
- ¿Aparecen en la salida los datos clave de la entrada (el cliente, el pedido)?
- ¿La salida contradice algo que estaba en el contexto?

### Qué hace el validation gate cuando algo falla

Cuando el gate encuentra un problema, no frena todo de una: primero prueba lo más barato y sube de nivel solo si eso no funciona. El curso le da cuatro responsabilidades, en este orden:
1. **Inspect** (revisar): esquema, rangos, completitud y sentido común.
2. **Retry** (reintentar): si falló, se reintenta **con el dato o el prompt corregido**, no idéntico, porque repetir exactamente lo mismo daría el mismo resultado.
3. **Fallback** (alternativa): si se acabaron los reintentos, se usa un camino alternativo (Tema 4).
4. **Escalate** (escalar): si la alternativa también falla, se avisa a un humano.

*Ejemplo:* el resumen de un reclamo vuelve con 3 palabras, así que falla el chequeo de completitud. El gate lo reintenta pidiendo explícitamente un resumen de al menos dos oraciones. Si vuelve a fallar, usa una plantilla fija con los datos del reclamo (fallback). Si tampoco se puede, marca el reclamo para que lo resuma una persona (escalate).

Además, el curso pide **registrar** (loguear) las entradas y salidas en **cada frontera entre pasos**, no solo cuando hay errores, y con un formato estructurado que se pueda consultar después. Así, cuando aparece un problema, se puede reconstruir qué recibió y qué devolvió cada etapa.

*Ejemplo:* cada vez que SoporteBot pasa de "verificar cliente" a "buscar pedido", queda un registro como `{"step": "lookup_order", "input": {"order_id": "TX-104233"}, "output_status": "ok", "ts": "..."}`. Si una semana después aparece un reembolso raro, se puede reconstruir paso a paso qué pasó.

### Para el examen

- Silent failures = las más peligrosas → se cortan con validación **entre** pasos.
- "La API devolvió 200" no prueba que el cambio se hizo → verificar el estado.

### Cómo se une

Es la misma idea de la **validación en las fronteras** de 1B y de la validación por schema en la agregación del coordinador (1C, Tema 1).

---

## Tema 3 — Retry logic (lógica de reintentos): cuándo reintentar y cuándo abortar

### Qué es

Reintentar solo sirve si el error podría desaparecer. La pregunta clave es: **¿el mismo pedido podría salir bien si lo repito?** Si la respuesta es sí (error transitorio), se reintenta. Si es no (error permanente o de razonamiento), reintentar solo gasta tiempo y dinero, y atrasa el momento en que alguien se entera de la falla.

📘 **Curso:** las formas de esperar, las políticas por tipo y el retry budget son del curso. La regla "solo se reintenta lo transitorio" sí coincide con la guía.

Cuando se reintenta, importa **cuánto se espera** entre intentos. Hay tres formas. El **immediate retry** (reintento inmediato) no espera nada; casi nunca es lo correcto, porque si el servicio está saturado lo saturás más. El **fixed delay** (espera fija) espera siempre lo mismo; es mejor que nada, pero no se adapta a cuánto tarda el servicio en recuperarse. El **exponential backoff with jitter** (espera exponencial con variación aleatoria) duplica la espera en cada fallo (1 s, 2 s, 4 s, 8 s, hasta un tope), y el **jitter** (variación aleatoria) le suma un poco de azar para que muchos clientes no reintenten todos al mismo tiempo. Es lo estándar para errores transitorios.

### Políticas por tipo de error

El curso da una política para cada tipo:

| Tipo | Qué hacer |
|---|---|
| Rate limit (429) | Backoff exponencial con jitter, respetando el encabezado `Retry-After` si viene |
| Timeout | Espera corta, de 1 a 3 intentos, y después abortar y escalar |
| Dato inválido (400) | Abortar ya: el mismo dato va a fallar igual |
| Error de razonamiento | Abortar y escalar: repetir el mismo prompt no arregla un plan equivocado |

El SDK de Anthropic ya trae reintentos con backoff para errores transitorios (429, 5xx y errores de conexión, entre otros): `anthropic.Anthropic(max_retries=3)`.

### Retry budget (presupuesto de reintentos) y cuándo abortar

Cada reintento suma costo y tiempo, así que no se puede reintentar para siempre. Por eso se fija un **retry budget**: un máximo de intentos. Se **aborta** en dos casos:
1. Se agotó el presupuesto y el error sigue.
2. El error es permanente desde el primer intento, así que no tiene sentido reintentar.

En los dos casos se aborta **y se escala**: nunca se falla en silencio, porque una falla que nadie ve es una silent failure (Tema 2).

### Ejemplo

SoporteBot consulta el estado del pedido TX-104300:
- Intento 1: 503. Espera ~1 s.
- Intento 2: 503. Espera ~2 s.
- Intento 3: 200. Sigue.

Si en el intento 1 hubiera venido **403** (permiso denegado), abortaría de inmediato y escalaría. Reintentar un 403 solo atrasa la falla.

### Para el examen

- **Solo se reintenta lo transitorio** (en la guía: lo que trae `isRetryable` en verdadero).
- Reintentar más no arregla un error permanente ni uno de razonamiento. Es el mismo distractor que "subir el límite de vueltas" en 1A.

### Cómo se une

En 1A, el agente que repetía la misma llamada con el mismo error estaba "girando en falso". La lógica de reintentos con presupuesto y aborto es lo que lo evita.

---

## Tema 4 — Fallback chains (cadenas de alternativas) y graceful degradation (degradación controlada)

### Qué es

A veces el camino principal falla y reintentar no alcanza, pero existe otra forma de conseguir el dato, aunque sea peor. Una **fallback chain** es una lista ordenada de esas alternativas: cada paso se prueba solo si el anterior falló. La cadena **siempre** termina en un paso final explícito (escalar o devolver un resultado parcial), para que nunca quede sin salida.

```python
CHAIN = [live_pricing_api, backup_pricing_service, cached_price]

def get_price(sku):
    for step in CHAIN:
        try:
            return step(sku), step is not CHAIN[0]   # (precio, ¿degradado?)
        except Exception as e:
            log.warning("%s failed: %s", step.__name__, e)
    raise EscalateToHuman(f"all fallbacks failed for {sku}")   # paso final explícito
```

Primero se intenta la API de precios en vivo, después un servicio de respaldo y por último un precio guardado. Si todo falla, se escala.

### Graceful vs. silent degradation

Cuando se usa una alternativa, el resultado suele ser **peor** (por ejemplo, un precio de hace una hora). Lo importante es si el resto del sistema se entera.

En la **graceful degradation** (degradación controlada), se devuelve el resultado **avisando** que es de menor calidad, con una marca en la salida: `{"price": 89.9, "degraded": true, "source": "cache"}`. El siguiente paso lee la marca y ajusta: baja la confianza o lo marca como parcial.

En la **silent degradation** (degradación silenciosa), se devuelve el resultado peor **sin avisar**, y el resto del sistema lo toma como si fuera completo. Es una silent failure (Tema 2).

### Anti-patterns de las cadenas

Un **anti-pattern** es una práctica que parece razonable pero causa problemas. El curso marca tres en las cadenas:

- **Untested fallbacks** (alternativas sin probar): una alternativa que nunca se probó puede fallar justo cuando más hace falta. Por eso cada paso se valida antes de ponerlo en producción.
- **Silent masking** (ocultar la degradación): es la silent degradation de arriba.
- **No terminal step** (sin paso final): sin un final explícito, la cadena puede quedar dando vueltas en vez de fallar de forma limpia.

### ¿Degradar o escalar?

No todo resultado degradado se puede usar. El curso lo decide por **riesgo** y **reversibilidad**: si equivocarse es barato o se puede deshacer, se acepta el resultado con su marca; si es caro y no tiene vuelta atrás, decide una persona.

| Situación | Qué hacer |
|---|---|
| Bajo riesgo o reversible | Aceptar el resultado degradado, con la marca, y seguir |
| Alto riesgo e irreversible (borrar, pagar, enviar) | **Escalar a un humano** |

*Ejemplo:* SoporteBot muestra el precio de una zapatilla desde la caché, con la marca "puede no estar actualizado": es de bajo riesgo. En cambio, si la cadena que calcula el **monto de un reembolso** falla y solo hay un dato viejo, no reembolsa con ese dato: escala.

Lo mismo vale para los resultados parciales. Si una alternativa devolvió 3 de 5 registros, se devuelven con la marca solo si un resultado incompleto no causa daño. Si lo causa, no se devuelve nada y se escala.

### Para el examen

- 📘 **Curso:** backoff con jitter, retry budget y fallback chains son buenas prácticas del curso; la guía no los nombra en 1.4 y 1.5. Si aparecen en una opción, juzgalos con la regla general: **no esconder fallas** y **escalar lo irreversible**.
- Resultado peor → **con marca** (graceful), nunca en silencio.

### Cómo se une

Es el "reintentar, sustituir o escalar" del coordinador en 1C, aplicado a un solo paso.

---

# Parte 2 — Hacer que las reglas se cumplan

## Tema 5 — Por qué el prompt no alcanza: guidance (guía) vs. enforcement (obligación)

### Qué es

Hay dos formas de hacer que un agente respete una regla, y la diferencia entre ellas es una de las ideas más preguntadas del examen.

La primera es la **prompt guidance** (guía por prompt): escribir la regla en las instrucciones, por ejemplo "Nunca reembolses más de USD 500 sin aprobación". El modelo lee la regla y **elige** cumplirla en cada respuesta. También entran acá los **few-shot examples** (ejemplos de muestra): casos resueltos que se ponen en el prompt para mostrarle al modelo cómo actuar.

La segunda es el **programmatic enforcement** (obligación por código): un código que **impide** la acción si no se cumple la regla, haga lo que haga el modelo. El modelo ni siquiera tiene la oportunidad de equivocarse.

La diferencia clave es que el prompt es **probabilistic** (probabilístico): se cumple casi siempre, pero no siempre. El código es **deterministic** (determinístico): se cumple siempre. La guía lo dice así: cuando hace falta cumplimiento garantizado, las instrucciones en el prompt tienen una **non-zero failure rate** (tasa de falla mayor que cero).

### Por qué falla el prompt

📘 **Curso:** los tres motivos y la separación por riesgo de esta parte vienen del curso.

- **Context drift** (deriva del contexto): en conversaciones largas, las instrucciones del principio pierden peso. En la vuelta 40, la regla se "olvida" más fácil.
- **Adversarial inputs** (entradas maliciosas): un usuario puede escribir algo pensado para que el modelo saltee la regla.
- **Edge cases** (casos raros): situaciones nuevas que el modelo no maneja bien.

### Cuándo alcanza el prompt y cuándo no

La pregunta es cuánto cuesta el 1% o el 3% de las veces que el prompt falla. Si ese error es barato, el prompt alcanza. Si es caro, no.

- **Alcanza** para caminos de **bajo riesgo**: tono, estilo, formato y acciones reversibles sin consecuencias legales ni económicas. Si falla, el error es barato.
- **No alcanza** para caminos de **alto riesgo**: transacciones de dinero, **PII** (datos personales, como el DNI de un cliente), acciones de seguridad o irreversibles. Si falla, hay pérdida económica, exposición legal o daño.

### Ejemplo

Rosa pide un reembolso de USD 900. La regla "más de USD 500 necesita supervisor" está en el system prompt del agente de reembolsos, y se cumple el 97% de las veces. El caso de Rosa cae en el 3% restante y el reembolso sale sin aprobación. Para una regla de dinero, un 3% de falla no es aceptable.

### El principio de diseño

**El prompt guía; el código obliga.** No se reemplazan entre sí, se complementan: el prompt **baja la frecuencia** de los intentos que no cumplen la regla, y el código **bloquea** los que igual se escapan. Por eso las dos capas van juntas.

### Para el examen

- Regla de **cumplimiento obligatorio** (dinero, identidad, PII, acciones irreversibles) → **código**: un prerrequisito programático o un hook.
- Las opciones que tientan son "reforzar el system prompt", "ponerlo en mayúsculas", "agregar few-shot" y "bajar la **temperature**" (el parámetro que controla cuánta variación aleatoria tiene la respuesta; con 0 el modelo es más predecible). Todas siguen siendo probabilísticas.

### Cómo se une

En 1C viste que limitar tools por configuración es más fuerte que decir "no edites archivos" en el prompt. Es el mismo principio, aplicado a reglas de negocio.

---

## Tema 6 — Programmatic prerequisites (prerrequisitos programáticos)

### Qué es

En muchos flujos, el **orden** de los pasos es parte de la regla: primero se verifica quién es el cliente y recién después se tocan sus pedidos. Si el modelo se saltea un paso, el resultado puede ser grave. Un **programmatic prerequisite** es un control en código que **bloquea** una tool hasta que se haya completado un paso previo. Así el orden de las llamadas deja de depender de que el modelo se acuerde.

### Ejemplo: la pregunta oficial de muestra (Q1 de la guía)

Es la pregunta de muestra Q1 de la guía (escenario Customer Support), adaptada a SoporteBot. Los datos de producción de SoporteBot muestran que en el **12%** de los casos el agente se saltea `get_customer` (verificar la identidad del cliente) y llama a `lookup_order` usando el nombre que dijo el cliente. Resultado: cuentas equivocadas y reembolsos a la persona incorrecta.

**✅ La solución correcta:** un prerrequisito programático que bloquea `lookup_order` y `process_refund` hasta que `get_customer` devuelva un **ID de cliente verificado**.

```python
verified_customer_id = None   # estado de la sesión

def before_tool(name, args):
    if name in ("lookup_order", "process_refund") and verified_customer_id is None:
        return {"blocked": True,
                "reason": "Primero verificá al cliente con get_customer."}
    return {"blocked": False}

def after_tool(name, result):
    global verified_customer_id
    if name == "get_customer" and result.get("verified"):
        verified_customer_id = result["customer_id"]   # recién ahora se habilitan las otras tools
```

Paso a paso: si Claude intenta llamar a `lookup_order` sin haber verificado, `before_tool` lo bloquea y le devuelve el motivo. Claude lee ese motivo y llama a `get_customer`. Cuando la verificación sale bien, `after_tool` guarda el ID y recién ahí las otras tools quedan habilitadas. Ahora es **imposible** que `process_refund` corra sin verificar al cliente, haga lo que haga el modelo.

**❌ Por qué fallan las otras opciones de esa pregunta:**
- **Hacer obligatoria la verificación en el system prompt:** sigue siendo probabilístico. Con consecuencias económicas, no alcanza.
- **Agregar few-shot** con ejemplos que llaman primero a `get_customer`: también es probabilístico.
- **Un routing classifier** (clasificador que decide qué tools habilitar según el pedido): resuelve **qué tools están disponibles**, no **en qué orden se llaman**.

### Para el examen

- Secuencia de tools crítica y con consecuencias (dinero, identidad) → **prerrequisito programático**.
- Reescribir la descripción de la tool para "imponer el orden" tampoco sirve: las descripciones guían la elección (1A), no garantizan el orden.

### Cómo se une

Es el `guard` de 1B (pedir confirmación antes de tools riesgosas), pero ahora el control no es "preguntale a un humano" sino "no se puede hasta que pase X". En el Tema 9 vas a ver que el lugar natural para escribir este control es un **hook**.

---

## Tema 7 — Validation layers (capas de validación): antes, después y durante

### Qué es

Un solo control en código no atrapa todo: algunos problemas se ven en la entrada, otros recién en la salida y otros a lo largo de toda la ejecución. Por eso los controles se organizan en **capas**, cada una en un momento distinto.

📘 **Curso:** la organización en tres capas y las tres respuestas (hard block, soft warning, escalation) son del curso. En el Agent SDK y en Claude Code se implementan con hooks (Temas 8 a 11).

**1. Pre-execution gate (control antes de ejecutar).** Revisa la **entrada** antes de que el agente actúe: que el pedido tenga la forma correcta (**schema**), que los valores estén dentro de lo permitido (**rango**) y que quien pide esté autorizado (**permisos**). Es el más barato, porque frenar un dato malo antes de actuar cuesta mucho menos que deshacer una acción hecha.

**2. Post-execution gate (control después de ejecutar).** Revisa la **salida** antes de guardarla o pasarla al siguiente paso:
- **schema** de la salida;
- **reglas de negocio** (por ejemplo, que la fecha de vencimiento no sea anterior a la de emisión);
- **anomalías**: valores con la forma correcta pero sospechosos, como una factura 12 veces mayor que el promedio del cliente.

**3. Runtime checks (controles durante la ejecución).** Vigilan al agente **mientras corre**, no en un punto fijo:
- **cost limits** (límites de costo): presupuesto de tokens o de gasto;
- **iteration caps** (tope de vueltas), el límite de 1A;
- **scope enforcement** (control de alcance): que no acceda a recursos fuera de lo permitido.

*Ejemplo en SoporteBot:* una conversación tiene un presupuesto de 40.000 tokens (cost limit) y un máximo de 12 vueltas (iteration cap). Además, el agente solo puede consultar pedidos del cliente verificado: si intenta leer el pedido de otro cliente, se frena (scope enforcement).

### Ejemplo con dos capas

El código de abajo pone un control antes (la regla de dinero) y uno después (tapar datos personales). El primero impide que se ejecute un reembolso grande; el segundo limpia el resultado antes de que vuelva al modelo.

```python
REFUND_LIMIT = 500
DNI = re.compile(r"\b\d{2}\.?\d{3}\.?\d{3}\b")

def handle_tool_call(name, args):
    # Pre-execution: regla de dinero ANTES de ejecutar
    if name == "process_refund" and args["amount"] > REFUND_LIMIT:
        raise PermissionError("El reembolso supera el límite: necesita aprobación humana")
    result = TOOLS[name](**args)
    # Post-execution: tapar datos personales ANTES de que vuelvan al modelo
    return DNI.sub("[REDACTED]", str(result))
```

### Qué hace el control cuando algo no pasa

No todas las reglas merecen la misma reacción. El curso da tres respuestas, según el riesgo:
- **Hard block** (bloqueo duro): rechaza y frena. Para reglas **no negociables**: límites de dinero, permisos, seguridad.
- **Soft warning** (advertencia suave): registra y deja seguir. Para reglas **orientativas**.
- **Escalation trigger** (disparador de escalamiento): pausa y pasa el caso a un humano. Para casos **realmente ambiguos**.

*Ejemplos en SoporteBot:*
- Un reembolso de USD 900 recibe un **hard block**, porque es una regla de dinero no negociable.
- Una respuesta al cliente que no usa el saludo estándar de TiendaX recibe un **soft warning**: se registra y sale igual.
- Un cliente pide un reembolso de un producto comprado hace 31 días (el límite es 30) y dice que llegó tarde por culpa del correo. Va a **escalation**: es ambiguo y lo decide una persona.

Ser demasiado estricto también es un problema: si todo es hard block, el flujo se traba y el agente no puede resolver nada. Hard block solo para lo no negociable.

### Para el examen

- **Prevenir** una acción → control **antes** (pre-execution).
- Revisar o limpiar un resultado → control **después** (post-execution).
- Las capas se **suman**: prompt, antes, después y durante. Cada una atrapa lo que se le escapa a la anterior.

### Cómo se une

En el Agent SDK y en Claude Code, la forma concreta de implementar estas capas son los **hooks** (Temas 8 a 11): PreToolUse es el control "antes" y PostToolUse es el control "después".

---

## Tema 8 — Hooks: qué son y qué eventos existen

### Qué es

Un **hook** es un código que **registrás para que se ejecute solo** cuando pasa un evento determinado del agente: por ejemplo, justo antes de que se ejecute una tool. A esos eventos se los llama **lifecycle events** (eventos del ciclo de vida). Lo importante es que el hook no depende de que el modelo "se acuerde" de nada: corre siempre que ocurre el evento. Por eso es la herramienta natural para el enforcement del Tema 5.

> ⚠️ **En el curso vas a escuchar otra cosa.** El deck de Jacob sobre hooks (deck 132) habla **solo de hooks de Claude Code**: scripts de consola que responden con exit codes. No muestra cómo se registran ni menciona el Agent SDK. **Para el examen: la tarea 1.5 pide hooks del Agent SDK**, que son **funciones** con `HookMatcher` y `permissionDecision` (Tema 9). Los eventos son los mismos, pero cambia la forma de responder: si el escenario usa el Agent SDK (como el de Customer Support), pensá en el Tema 9; si habla de Claude Code, en los exit codes de este tema.

### Los eventos más importantes

Los eventos se agrupan según cada cuánto ocurren. Para cada uno, lo que más importa saber es si **puede bloquear** (frenar lo que está por pasar) o si **solo observa** (se entera, pero no puede impedir nada).

📘 **Curso:** el agrupamiento por frecuencia y los eventos PreCompact y Notification salen del curso; los demás eventos y si bloquean coinciden con la documentación.

**Una vez por sesión:**
- **SessionStart**: cuando empieza o se retoma una sesión. Sirve para cargar contexto. Solo observa: no puede bloquear.
- **SessionEnd**: cuando termina la sesión. Sirve para limpiar. Solo observa.

**Una vez por turno:**
- **UserPromptSubmit**: cuando el usuario manda un mensaje, antes de que Claude lo lea. **Puede bloquear** el mensaje o agregarle contexto.
- **Stop**: cuando Claude termina de responder. **Puede bloquear** el final y obligarlo a seguir trabajando.

**En cada llamada a una tool:**
- **PreToolUse**: **antes** de que la tool se ejecute. **Puede bloquear** la llamada o cambiar sus parámetros. Es el control "antes" del Tema 7.
- **PostToolUse**: **después** de que la tool se ejecutó bien. **No puede bloquear**, porque la tool ya corrió. Sirve para reaccionar, registrar o **transformar el resultado** antes de que Claude lo vea. Es el control "después".

**En momentos puntuales:**
- **PreCompact**: antes de que se resuma el contexto. Puede bloquearlo.
- **Notification**: cuando Claude Code manda una notificación. Solo observa.
- **PermissionRequest**: cuando una tool necesita permiso. Responde con un objeto de decisión.

Hay más eventos, como **PostToolUseFailure** (cuando una tool falló) y **SubagentStart**/**SubagentStop** (cuando arranca o termina un subagent), pero los de arriba son los que hay que saber. Un detalle de la documentación: en el Agent SDK de **Python**, SessionStart y SessionEnd no se registran como funciones (solo en TypeScript, o como hooks de consola en la configuración).

### La regla más útil: ¿bloquea u observa?

Si de los eventos te quedás con una sola idea, que sea esta: lo que hay que **impedir** se frena antes de que pase, y lo que hay que **ajustar** se trata después.

| Para… | Evento |
|---|---|
| **Impedir** algo | **PreToolUse** |
| **Reaccionar** a un resultado (registrar, formatear, normalizar) | **PostToolUse** |
| **Preparar** la sesión (📘 Curso) | **SessionStart** |

### Cómo "habla" un hook en Claude Code: exit codes

En **Claude Code**, un hook es un script de consola. Recibe el evento como JSON por **stdin** (la entrada estándar) y le contesta a Claude Code con su **exit code** (código de salida, el número con el que termina un programa). Ese número decide si la acción sigue o se frena:

| Exit code | Qué pasa |
|---|---|
| **0** | Éxito: la acción sigue. Si el hook imprimió JSON, Claude Code lo lee. |
| **2** | **Bloqueo**: en los eventos que pueden bloquear, la acción se frena y el texto de **stderr** (la salida de error) se le pasa a Claude como motivo. |
| **Otro** (por ejemplo, 1) | Error **no bloqueante**: se muestra el error, pero la acción **sigue igual**. |

```python
import json, sys

event = json.load(sys.stdin)                       # el evento llega por stdin
cmd = event.get("tool_input", {}).get("command", "")

if event.get("tool_name") == "Bash" and "rm -rf" in cmd:
    print("Bloqueado: comando destructivo", file=sys.stderr)   # el motivo va a stderr
    sys.exit(2)                                     # 2 = bloquear

sys.exit(0)                                         # 0 = seguir
```

*En SoporteBot*, el mismo patrón sirve para otras cosas: un hook PreToolUse que bloquea (exit 2) cualquier llamada a `send_email` dirigida a una dirección que no sea la del cliente verificado.

Dos detalles que se preguntan:
- En **PostToolUse**, el exit 2 **no bloquea nada**, porque la tool ya corrió. Solo le muestra el mensaje a Claude.
- **Exit 1 no bloquea.** Aunque en programación 1 suele significar "error", acá es un error que deja seguir. Si querés bloquear, es 2.

### Para el examen

- PreToolUse **previene**; PostToolUse **reacciona**. Usar PostToolUse para "evitar" algo es un distractor clásico.
- Exit 0 → sigue; exit 2 → bloquea; cualquier otro → error que no bloquea.

### Cómo se une

Los hooks son la forma concreta de las capas del Tema 7 y de los prerrequisitos del Tema 6. Ahora los vas a ver en el Agent SDK, que es lo que pide la tarea 1.5.

---

## Tema 9 — Hooks en el Agent SDK: cómo se configuran

### Qué es

En el **Agent SDK** (la librería para construir agentes que viste en 1C), los hooks no son scripts de consola sino **funciones** de tu código, que se registran en las opciones del agente. Para cada evento definís uno o más **matchers** (filtros) que dicen **a qué tools** se aplica el hook. Así, un hook de reembolsos solo corre cuando se llama a la tool de reembolsos, y no en cada llamada.

### Cómo se registra

```python
from claude_agent_sdk import ClaudeAgentOptions, HookMatcher

options = ClaudeAgentOptions(
    hooks={
        "PreToolUse": [
            # matcher: el NOMBRE de la tool a la que se aplica el hook
            HookMatcher(matcher="mcp__tiendax__process_refund", hooks=[limitar_reembolsos]),
        ],
        "PostToolUse": [
            HookMatcher(matcher="^mcp__", hooks=[normalizar_datos]),   # todas las tools MCP
        ],
    }
)
```

La clave del diccionario (`"PreToolUse"`, `"PostToolUse"`) es el **evento**. El **`matcher`** filtra por **nombre de tool**: puede ser un nombre exacto, varios separados con `|` (`"Write|Edit"`) o una expresión regular (`"^mcp__"` = todas las tools MCP). Las tools de un MCP server se llaman `mcp__<server>__<tool>` (lo vemos en 2B). Sin matcher, el hook se aplica a todas.

Ojo: **el matcher solo mira el nombre de la tool**, no sus argumentos. Si querés filtrar por un argumento (por ejemplo, el monto), lo hacés **adentro** de la función.

### Qué recibe y qué devuelve la función

La función recibe `(input_data, tool_use_id, context)`. En `input_data` vienen, entre otros, `tool_name` y `tool_input` (los parámetros de la llamada). En PostToolUse viene además la respuesta de la tool.

Lo que la función devuelve decide qué pasa. Si devuelve **`{}`** (vacío), no cambia nada y todo sigue normal. Para cambiar algo, completa un objeto **`hookSpecificOutput`** con campos que dependen del evento. Lo más importante es saber **a quién le habla** cada campo: algunos los lee Claude y otros solo el usuario.

En **PreToolUse**, dentro de `hookSpecificOutput`:
- **`permissionDecision`**: `"allow"` (permitir), `"deny"` (bloquear), `"ask"` (preguntarle al usuario) o `"defer"` (cortar el turno para resolver la llamada más tarde; solo funciona en modo no interactivo y con una única tool call en el turno).
- **`permissionDecisionReason`**: el motivo. Con `"deny"`, **Claude lo lee**, así que sirve para decirle qué hacer en lugar de eso. Con `"ask"` lo ve el usuario. Con `"allow"` solo queda en el log de depuración.
- **`updatedInput`**: parámetros nuevos para la tool (por ejemplo, corregir un dato). Va **dentro** de `hookSpecificOutput` (afuera no se aplica) y se combina con `"allow"` o `"ask"`; con `"defer"` se ignora.

En **PostToolUse**, dentro de `hookSpecificOutput`:
- **`updatedToolOutput`**: **reemplaza** el resultado de la tool **antes de que Claude lo vea**. Tiene que respetar la **forma** de salida de la tool. En las tools nativas, si no la respeta, se ignora y Claude ve la salida original; en las tools MCP pasa sin validar.
- **`additionalContext`**: agrega información para Claude junto al resultado.

Afuera de `hookSpecificOutput` está **`systemMessage`**: un mensaje para **el usuario**, no para el modelo. Para hablarle al modelo se usa `permissionDecisionReason` o `additionalContext`.

### Reglas de funcionamiento

Cuando hay varios controles a la vez (varios hooks, reglas, modos), hay que saber cuál gana. Estas reglas lo definen:

- Si varios hooks aplican a la misma llamada, **corren en paralelo** y gana el **más restrictivo**: deny > defer > ask > allow. No dependen del orden en que los registraste: el orden en que terminan no es predecible, así que cada hook se escribe para funcionar solo. (Algunas guías de la comunidad dicen que corren en el orden de registro: en el examen, respondé lo de la documentación.)
- Además de los hooks, el SDK tiene **permission rules** (reglas de permiso: listas de tools permitidas o prohibidas) y **permission modes** (modos de permiso: por ejemplo, uno que pregunta antes de cada acción y otro, `bypassPermissions`, que aprueba todo). Los hooks se evalúan **antes** que todo eso, y un `deny` de un hook se aplica **incluso** en `bypassPermissions`. Por eso, para un control que tiene que correr en **todas** las llamadas, el lugar es un hook PreToolUse.
- Al revés no funciona igual: un hook que devuelve `allow` **no** se saltea las reglas que prohíben o piden confirmación (deny y ask rules). Y el **`canUseTool`** (la función que el SDK llama para pedirle aprobación a una persona en el momento) **nunca se llama** para las tools que ya están aprobadas por una regla o por el modo de permiso: un control puesto solo ahí se saltea en silencio.

### Cómo se traducen las respuestas del Tema 7

Las respuestas del curso (Tema 7) tienen su forma concreta en un hook PreToolUse. La más importante para el examen es la última: bloquear y, en el mismo motivo, mandar a Claude a otro flujo.

| Respuesta | En un hook PreToolUse |
|---|---|
| **Hard block** | `permissionDecision: "deny"` (o exit 2 en Claude Code) |
| **Soft warning** | Dejar seguir y avisar: al modelo con `additionalContext`, al usuario con `systemMessage` |
| **Pedir aprobación humana en el momento** | `permissionDecision: "ask"` |
| **Escalation** | `deny` y, en el `permissionDecisionReason`, **redirigir** a otro flujo (por ejemplo, `escalate_to_human`). Es lo que pide la guía y lo que hace el Tema 10 |

### Ejemplo

Los Temas 10 y 11 son dos ejemplos completos: un hook PreToolUse que bloquea reembolsos y un hook PostToolUse que normaliza datos.

### Para el examen

- Hooks del SDK: **PreToolUse** para interceptar llamadas **salientes** (antes de ejecutar) y **PostToolUse** para interceptar **resultados** (antes de que el modelo los procese).
- Bloquear = `permissionDecision: "deny"` con un `permissionDecisionReason` que oriente a Claude.
- El matcher filtra por nombre de tool, no por argumentos.
- Para hablarle al **modelo**: `permissionDecisionReason` o `additionalContext`. `systemMessage` le habla al **usuario**.

### Cómo se une

Es el `before_tool`/`after_tool` del Tema 6, escrito en la forma oficial del SDK.

---

## Tema 10 — Un hook que bloquea y redirige: el reembolso de más de USD 500

### Qué es

La guía pide algo más que bloquear. Si el hook solo dice "no", Claude queda sin saber qué hacer y el caso del cliente queda colgado. Por eso el patrón completo es **interceptar** la llamada que viola la regla, **bloquearla** y **redirigir** el caso a otro flujo, por ejemplo **escalar a un humano**.

### Ejemplo: el reembolso de Rosa

La regla: los reembolsos de más de USD 500 necesitan aprobación de un supervisor. En vez de confiar en el prompt (Tema 5), se escribe un hook PreToolUse:

```python
async def limitar_reembolsos(input_data, tool_use_id, context):
    monto = input_data["tool_input"].get("amount", 0)
    if monto > 500:
        return {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",          # la tool NO se ejecuta
                "permissionDecisionReason": (           # Claude lee esto
                    f"Reembolso de USD {monto} supera el límite de USD 500. "
                    "No lo proceses. Escalá con escalate_to_human e incluí "
                    "customer_id, causa, monto y acción recomendada."
                ),
            }
        }
    return {}   # USD 500 o menos: sigue normal

# Registrado con matcher="mcp__tiendax__process_refund" (Tema 9)
```

**Qué pasa con Rosa:**
1. Claude llama a `process_refund` con `amount: 900`.
2. El hook corre **antes** de que se ejecute y devuelve `deny`. La tool no corre.
3. Claude recibe el motivo: tiene que escalar.
4. Claude llama a `escalate_to_human` con un resumen estructurado del caso (Tema 14).

El reembolso de USD 900 **nunca** puede salir sin aprobación, sin importar qué diga el modelo ni cuán larga sea la conversación.

### Para el examen

- Regla de negocio que **se tiene que cumplir siempre** → hook de interceptación (PreToolUse) que **bloquea y redirige** a un flujo alternativo (escalamiento).
- Un hook PostToolUse **no sirve** para esto: cuando corre, el reembolso ya se hizo.

### Cómo se une

Es el caso con el que cerró 1C. El prompt lo cumplía el 97% de las veces; el hook lo cumple el 100%.

---

## Tema 11 — Un hook que normaliza datos: PostToolUse

### Qué es

**Data normalization** (normalización de datos) es convertir datos que vienen en **formatos distintos** a **un formato común**, antes de que el modelo los use. Pasa mucho cuando el agente usa varias tools MCP de sistemas distintos, porque cada sistema representa los datos a su manera:
- una devuelve fechas como **Unix timestamp** (segundos desde 1970, por ejemplo `1794873600`);
- otra como **ISO 8601** (por ejemplo `"2026-11-17T00:00:00Z"`);
- otra devuelve el estado como **código numérico** (`3`) en vez de texto (`"enviado"`).

Si Claude recibe todo mezclado, puede comparar mal las fechas o interpretar mal un estado. La guía pide resolverlo con un hook **PostToolUse**: el hook transforma el resultado **antes** de que Claude lo procese, así el modelo siempre ve un único formato y no tiene que interpretar nada.

El curso no trata la normalización (en su deck, PostToolUse solo sirve para "reaccionar, registrar o revisar"); este tema sale de la guía y de la documentación.

### Ejemplo

SoporteBot usa dos tools:
- `get_order_status` (sistema de pedidos): `{"order_id": "TX-104233", "status": 3, "updated": 1794873600}`
- `get_shipment` (sistema de logística): `{"tracking": "AR123", "delivered_at": "2026-11-17T14:20:00Z"}`

Un hook PostToolUse normaliza los dos al mismo formato:

```python
import json
from datetime import datetime, timezone

ESTADOS = {1: "pendiente", 2: "preparando", 3: "enviado", 4: "entregado"}

async def normalizar_datos(input_data, tool_use_id, context):
    data = dict(input_data["tool_response"])   # resultado original (ya es un objeto; su forma depende de la tool)
    if "status" in data and isinstance(data["status"], int):
        data["status"] = ESTADOS[data["status"]]          # 3 -> "enviado"
    if "updated" in data and isinstance(data["updated"], int):
        data["updated"] = (datetime.fromtimestamp(data["updated"], tz=timezone.utc)
                           .isoformat().replace("+00:00", "Z"))   # 1794873600 -> "2026-11-17T00:00:00Z"
    return {
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "updatedToolOutput": data,   # misma forma que la salida original; Claude ve ESTO
        }
    }
```

Paso a paso: `get_order_status` corre y devuelve su resultado. Antes de que llegue a Claude, el hook cambia el `3` por `"enviado"` y el `1794873600` por `"2026-11-17T00:00:00Z"`, y devuelve el resultado nuevo en `updatedToolOutput`. Claude ve ese resultado, con las fechas en el mismo formato ISO 8601 que las de logística. Ojo: el resultado nuevo mantiene **la misma forma** que el original (los mismos campos); solo cambian los valores.

### Para el examen

- Formatos heterogéneos de distintas tools (timestamps Unix, ISO 8601, códigos numéricos) → **hook PostToolUse** que normaliza **antes** de que el agente procese.
- Pedirle en el prompt al modelo que "interprete bien las fechas" es la opción que tienta, y es probabilística.
- Para cambiar lo que ve Claude → **`updatedToolOutput`**. En PostToolUse también existe `decision: "block"` con un `reason`, pero eso solo **agrega** el motivo: Claude igual ve la salida **original**.

### Cómo se une

Es el post-execution gate del Tema 7, en su versión de transformación: no frena nada, pero **limpia** lo que va a ver el modelo. Es parecido al filtro de datos personales del Tema 7.

---

## Tema 12 — ¿Hook o prompt? Cómo decidir

### Qué es

Después de tantos hooks, es fácil pensar que todo se resuelve con código. No es así: un hook solo puede chequear lo que se escribe como una condición exacta. La pregunta que decide es **qué tipo de regla** es.

Una **regla determinística** es siempre igual y no necesita interpretación: "no reembolsar más de USD 500", "verificar al cliente antes de buscar pedidos", "no ejecutar `rm -rf`". Va en un **hook o un prerrequisito en código**, porque tiene que cumplirse siempre y se puede chequear con un `if`.

Un **judgment call** (criterio de juicio) requiere evaluar el caso: "escalar cuando el cliente pide una excepción a la política", "escalar cuando el caso es complejo". Va en **criterios explícitos en el prompt, con few-shot** (ejemplos de cuándo sí y cuándo no), porque un `if` no puede decidir si un caso es "complejo"; eso lo tiene que juzgar el modelo, y los ejemplos le enseñan a juzgarlo bien.

### Ejemplo: la otra pregunta oficial de muestra (Q3 de la guía)

Es la pregunta de muestra Q3 de la guía. La guía la asigna a otra tarea (de cuándo escalar), pero toca el escalamiento de 1.4. SoporteBot escala casos simples (como un cambio estándar con foto del producto dañado) y se queda intentando casos complejos que necesitan una excepción a la política. La **first-contact resolution** (casos resueltos en el primer contacto) está en 55%, y el objetivo es 80%.

- **✅ Correcto:** agregar al system prompt **criterios explícitos de escalamiento** con **few-shot** que muestren cuándo escalar y cuándo resolver.
- **❌ Que el agente informe su confianza del 1 al 10 y escale si es baja:** la autoevaluación del modelo está mal calibrada, y el agente ya se siente seguro justo en los casos difíciles.
- **❌ Entrenar un clasificador con tickets históricos:** es sobreingeniería, porque necesita datos etiquetados e infraestructura antes de probar lo simple.
- **❌ Análisis de sentimiento:** que el cliente esté enojado no indica que el caso sea complejo.

Fijate la diferencia con el Tema 6: ahí la respuesta era **código**, porque había un **orden obligatorio** con consecuencias de dinero. Acá es **prompt**, porque se trata de **calibrar un juicio**.

### Para el examen

| Si la pregunta habla de… | La respuesta suele ser… |
|---|---|
| "debe", "siempre", "nunca", dinero, identidad, PII, compliance | **Hook o prerrequisito en código** |
| cuándo escalar, qué casos son complejos, calibrar decisiones | **Criterios explícitos + few-shot en el prompt** |
| confianza autoinformada, sentimiento | **Distractor** |

### Cómo se une

Completa el Tema 5: el prompt sirve para **guiar el juicio**, y el código para **garantizar las reglas**.

---

# Parte 3 — Varios problemas y el traspaso a un humano

## Tema 13 — Pedidos con varios problemas: descomponer e investigar en paralelo

### Qué es

Los clientes no escriben de a un problema por vez. Un **multi-concern request** (pedido con varios problemas) es un mensaje con **más de un problema** a la vez. Si el agente lo trata como un solo pedido, resuelve uno y se olvida del resto; si los resuelve uno detrás de otro, el cliente espera de más. La guía pide tres pasos:
1. **descomponer** el pedido en ítems separados;
2. **investigar cada uno en paralelo**, usando un **contexto compartido** (el mismo cliente, la misma verificación de identidad);
3. **sintetizar una sola resolución** que responda todo junto.

El curso no trata este caso: sale solo de la guía.

### Ejemplo: Martín otra vez

Martín escribe: "El pedido TX-104233 llegó con una zapatilla rota, me cobraron dos veces el TX-104251 y quiero cambiar la dirección del TX-104300".

1. **Contexto compartido:** primero se verifica a Martín con `get_customer` una sola vez (es el prerrequisito del Tema 6). Cada rama recibe lo mismo: `{"customer_id": "C-5521", "verified": true, "nombre": "Martín"}`, más su ítem. Nadie vuelve a verificar.
2. **Descomponer:** (a) producto dañado, (b) cobro duplicado, (c) cambio de dirección.
3. **Investigar en paralelo:** se lanzan las tres investigaciones al mismo tiempo (varias llamadas a tools o a Task en una misma respuesta, como en 1A y 1C).
4. **Una sola respuesta:** "Martín: registramos el cambio de la zapatilla (te llega una etiqueta de envío), te devolvimos el cobro duplicado de USD 120 y el TX-104300 ya va a la nueva dirección".

### Para el examen

- Pedido con varios problemas → **descomponer en ítems + investigar en paralelo con contexto compartido + una resolución unificada**.
- No conviene usar subagents para un pedido de **un solo** problema: agrega costo sin beneficio (1C, Tema 9).

### Cómo se une

Es la descomposición de 1B y el paralelismo de 1C, aplicados a un caso de soporte. La novedad es el **contexto compartido**: la verificación se hace una vez y vale para todos los ítems.

---

## Tema 14 — Interruption points (puntos de pausa) y handoff (traspaso) a un humano

### Qué es un interruption point

Un **interruption point** es un lugar del flujo donde el agente **se detiene y espera** a un humano. Dónde ponerlo es una decisión de diseño: si la pausa llega tarde, ya no sirve; si hay pausas en todos lados, el agente no avanza. El curso propone tres lugares:
- **antes de acciones irreversibles**: es el lugar más importante, porque pausar **después** de borrar algo ya es tarde;
- **en los cambios de fase**, donde cambia el alcance o la autoridad;
- **cuando se detecta una anomalía**: datos raros, valores fuera de rango.

La documentación de Anthropic (*Building effective agents*) también dice que un agente puede pausar para pedir feedback humano en **checkpoints** o cuando se traba, pero no define dónde ponerlos. La lista de arriba es del curso.

*Ejemplos en SoporteBot:*
- **Antes de lo irreversible:** justo antes de `process_refund` por más de USD 500.
- **Cambio de fase:** cuando el agente termina de investigar un reclamo y va a pasar a **actuar** (reembolsar, reenviar): de "leer" pasa a "cambiar cosas".
- **Anomalía:** el cliente pide el reembolso número 6 en un mes.

### Qué tiene que tener el traspaso

Cuando el agente le pasa un caso a un humano, ese humano **no tiene acceso a la conversación**: no vio los mensajes ni los resultados de las tools. Si el traspaso no le cuenta lo esencial, tiene que empezar de cero. Por eso la guía pide un **structured handoff summary** (resumen estructurado de traspaso) con:
- **customer ID** (ID del cliente);
- **root cause** (causa raíz: qué pasó y por qué);
- **refund amount** (monto del reembolso, si aplica);
- **recommended action** (acción recomendada).

📘 **Curso:** el curso agrega cómo armar el mensaje para que el humano pueda decidir rápido:
- **Context** (contexto): qué estaba haciendo el agente y por qué se detuvo, en pocas palabras;
- **Decision required** (decisión que se pide): una pregunta **concreta**, no "fijate qué hacer";
- **Consequences** (consecuencias): qué pasa si aprueba y qué pasa si rechaza;
- **Deadline** (plazo): hasta cuándo puede esperar y qué pasa si nadie responde.

> ⚠️ **En el curso vas a escuchar otra cosa.** Jacob arma el traspaso con context, decision required, consequences y deadline. **Para el examen: la opción correcta es la que trae los cuatro campos de la guía** (`customer_id`, `root_cause`, `refund_amount` y `recommended_action`), aunque no tenga los del curso.

### Ejemplo: mal y bien

**Mal:** "Escalo el caso de Rosa. Adjunto la conversación completa (42 mensajes) y los resultados de las tools."
El supervisor tiene que leer todo y hacer el análisis que debería haber hecho el agente.

**Bien:**

```json
{
  "customer_id": "C-7788",
  "order_id": "TX-104512",
  "root_cause": "Pedido entregado incompleto: faltó 1 de 2 camperas (confirmado por logística)",
  "refund_amount": 900,
  "recommended_action": "Aprobar reembolso parcial de USD 900 por la campera faltante",
  "decision_required": "¿Aprobás el reembolso de USD 900?",
  "if_approved": "Se procesa el reembolso y se avisa a la clienta",
  "if_rejected": "Se ofrece reenvío de la campera",
  "deadline": "18/11 18:00; si no hay respuesta, se ofrece el reenvío"
}
```

El supervisor lee 10 líneas y decide. `customer_id`, `root_cause`, `refund_amount` y `recommended_action` son lo que pide la guía; `decision_required`, `if_approved`/`if_rejected` y `deadline` son el agregado del curso.

### Guardar el estado durante la pausa

📘 **Curso:** mientras espera, el agente **guarda su progreso afuera**: qué pasos completó, qué produjo y qué decidió. No lo deja solo en el contexto, que puede recortarse o perderse si termina la sesión (1C, Tema 10). Cuando llega la aprobación, **retoma desde el punto de pausa sin repetir los pasos ya hechos**, porque repetirlos gasta tiempo y puede dar resultados distintos.

### Sincrónico o asincrónico

📘 **Curso:** hay dos formas de esperar la decisión, y se elige según si el resto del trabajo depende de ella.

En la **synchronous escalation** (escalamiento sincrónico), el agente se detiene y espera. Es simple, pero bloquea todo, así que sirve cuando lo que sigue no puede avanzar sin la decisión.

En la **async escalation** (escalamiento asincrónico), el agente deja el pedido en una cola y sigue con otras tareas independientes. No bloquea, pero necesita dos cosas para no quedar esperando para siempre:
- un **timeout** (tiempo máximo de espera);
- una **acción al vencer**: escalar a otra persona, abortar o aplicar un valor seguro por defecto (por ejemplo, "retener el pedido").

*Ejemplos:*
- **Sincrónico:** el reembolso de Rosa. No hay nada más que hacer en ese caso hasta que el supervisor decida.
- **Asincrónico:** el caso de Martín. Mientras el supervisor revisa el reembolso, el agente sigue con el cambio de dirección, que no depende de esa decisión. Si en 2 horas no hay respuesta, avisa al supervisor de guardia.

Nunca se queda esperando para siempre sin hacer nada.

### Para el examen

- Al escalar → **resumen estructurado** (customer ID, causa raíz, monto, acción recomendada), porque **el humano no tiene el transcript**.
- Las opciones que tientan son "transferir con la conversación completa" y "un mensaje libre del tipo 'necesito ayuda con este caso'".

### Cómo se une

Es el handoff schema de 1C (task, context, output_format, constraints), pero dirigido a una persona en lugar de a otro agente. Y es la otra mitad del Tema 10: el hook **bloquea** el reembolso de Rosa, y este traspaso le da al supervisor todo lo que necesita para **decidir**.

---

## Cómo se une todo

Cuando algo falla, primero se **clasifica**: transitorio, permanente o de razonamiento (Tema 1). Los errores se **detectan entre pasos**, para que no se propaguen en silencio (Tema 2), y **solo lo transitorio se reintenta**, con espera creciente y un presupuesto máximo (Tema 3). Si una alternativa da un resultado peor, se **avisa** con una marca, y lo irreversible se **escala** (Tema 4).

El prompt **guía** y es probabilístico; las reglas que tienen que cumplirse siempre van en **código** (Tema 5). El **orden** obligatorio entre tools se asegura con **prerrequisitos programáticos** (Tema 6), y los controles en código actúan **antes**, **después** y **durante** la ejecución (Tema 7). Los **hooks** son la forma concreta de esos controles: **PreToolUse** previene y **PostToolUse** reacciona (Temas 8 y 9). Un hook PreToolUse **bloquea** el reembolso de USD 900 y **redirige** a escalamiento (Tema 10); un hook PostToolUse **normaliza** formatos distintos antes de que Claude los vea (Tema 11). Las reglas determinísticas van en hooks, pero **cuándo escalar** se calibra con criterios y few-shot en el prompt (Tema 12).

Los pedidos con varios problemas se **descomponen y se investigan en paralelo** con contexto compartido (Tema 13). Y cuando un humano tiene que decidir, recibe un **resumen estructurado**, mientras el agente guarda su estado para retomar sin repetir (Tema 14).

## Lo que viene

Con este capítulo termina el **módulo 1** (Agentic Architecture & Orchestration, 27% del examen). Sigue el módulo 2 con **2A · Tool Design**. Varias veces apareció la idea de que Claude elige tools leyendo su descripción, y que los errores de una tool tienen que traer categoría y si se pueden reintentar. En 2A se ve cómo diseñar bien esas tools.

---

## Las trampas del examen

Cada trampa tiene el mismo orden: la situación, **qué elegir en el examen (✅)**, las opciones que tientan (❌) con por qué tientan y por qué están mal, y una regla para recordar.

### Grupo: Hacer que las reglas se cumplan

#### Trampa 1 · El agente se saltea la verificación del cliente

**La situación.** En el 12% de los casos, SoporteBot llama a `lookup_order` sin haber llamado antes a `get_customer`, y hay reembolsos a la cuenta equivocada (Tema 6).

**✅ En el examen elegí:** un **prerrequisito programático** que bloquea `lookup_order` y `process_refund` hasta que `get_customer` devuelva un ID verificado.

**❌ Las que tientan:**

❌ **"Hacer obligatoria la verificación en el system prompt".**
- *Tienta porque:* es directo y barato.
- *Está mal porque:* es probabilístico. Con dinero en juego, un 12% (o incluso un 1%) de falla no es aceptable.

❌ **"Agregar few-shot que muestren llamar primero a `get_customer`".**
- *Tienta porque:* los ejemplos mejoran mucho el comportamiento.
- *Está mal porque:* sigue siendo probabilístico. No **garantiza** el orden.

❌ **"Un routing classifier que habilite las tools según el tipo de pedido".**
- *Tienta porque:* suena a una solución de arquitectura.
- *Está mal porque:* controla **qué tools hay**, no **en qué orden** se llaman.

> 🧠 **Para recordar:** si el orden importa y hay plata en juego, el orden lo impone el código.

#### Trampa 2 · Una regla de negocio que se cumple "casi siempre"

**La situación.** La regla "más de USD 500 necesita supervisor" está en el prompt y falla el 3% de las veces (Temas 5 y 10).

**✅ En el examen elegí:** un **hook PreToolUse** que intercepta `process_refund`, **bloquea** (`deny`) los montos de más de USD 500 y **redirige** a escalamiento humano.

**❌ Las que tientan:**

❌ **"Poner la regla en mayúsculas y al principio del prompt".**
- *Tienta porque:* sube la tasa de cumplimiento.
- *Está mal porque:* sigue siendo probabilístico, y en conversaciones largas la instrucción pierde peso.

❌ **"Bajar la temperature a 0".**
- *Tienta porque:* hace al modelo más predecible.
- *Está mal porque:* más predecible no es **garantizado**. La regla tiene que estar en código.

❌ **"Un hook PostToolUse que revise el monto".**
- *Tienta porque:* también es un hook.
- *Está mal porque:* PostToolUse corre **después**, cuando el reembolso ya se hizo. No puede prevenir.

> 🧠 **Para recordar:** lo que tiene que cumplirse siempre va en un hook PreToolUse, no en el prompt.

#### Trampa 3 · PreToolUse o PostToolUse

**La situación.** Hay que elegir en qué evento poner un hook (Temas 8 a 11).

**✅ En el examen elegí:**
- **PreToolUse** para **prevenir**: bloquear, exigir aprobación o corregir parámetros antes de ejecutar.
- **PostToolUse** para **transformar o reaccionar**: normalizar formatos, tapar datos personales, registrar. Siempre antes de que el modelo procese el resultado.

**❌ Las que tientan:**

❌ **"PostToolUse con exit 2 para frenar la acción".**
- *Tienta porque:* exit 2 bloquea en otros eventos.
- *Está mal porque:* en PostToolUse la tool ya corrió. El exit 2 solo le muestra un mensaje a Claude.

❌ **"Exit 1 para bloquear".**
- *Tienta porque:* en programación, 1 suele significar "error".
- *Está mal porque:* en los hooks de Claude Code, 1 es un error **no bloqueante**. Para bloquear es 2.

> 🧠 **Para recordar:** Pre previene, Post transforma; y para bloquear es exit 2.

#### Trampa 4 · Formatos de datos mezclados

**La situación.** Distintas tools MCP devuelven fechas en Unix timestamp e ISO 8601, y estados como números, y el agente compara mal (Tema 11).

**✅ En el examen elegí:** un **hook PostToolUse** que **normaliza** todo a un formato común antes de que el agente lo procese.

**❌ Las que tientan:**

❌ **"Explicarle al modelo en el prompt cómo interpretar cada formato".**
- *Tienta porque:* no hay que tocar código.
- *Está mal porque:* es probabilístico y repite el trabajo en cada respuesta. Un hook lo resuelve una vez y siempre igual.

❌ **"Pedirle a cada equipo que cambie su API para usar el mismo formato".**
- *Tienta porque:* ataca la "raíz".
- *Está mal porque:* no siempre controlás esos sistemas, y la normalización en el hook resuelve el problema ahora, en tu lado.

> 🧠 **Para recordar:** datos heterogéneos se normalizan en PostToolUse, antes de que Claude los vea.

### Grupo: Escalar y traspasar a un humano

#### Trampa 5 · Cuándo escalar

**La situación.** SoporteBot escala casos simples y se queda con casos complejos; la resolución en el primer contacto es del 55% (Tema 12).

**✅ En el examen elegí:** **criterios explícitos de escalamiento con few-shot** en el system prompt.

**❌ Las que tientan:**

❌ **"Que el modelo informe su nivel de confianza y escale si es bajo".**
- *Tienta porque:* parece una medida objetiva.
- *Está mal porque:* la confianza autoinformada está mal calibrada. El agente ya se siente seguro en los casos difíciles.

❌ **"Entrenar un clasificador con tickets históricos".**
- *Tienta porque:* suena robusto y con datos.
- *Está mal porque:* es sobreingeniería antes de probar lo simple.

❌ **"Escalar según el sentimiento del cliente".**
- *Tienta porque:* un cliente enojado parece un caso difícil.
- *Está mal porque:* el sentimiento no indica la complejidad del caso.

❌ **"Un hook que decida cuándo escalar".**
- *Tienta porque:* en este capítulo los hooks resuelven todo.
- *Está mal porque:* decidir si un caso es complejo es **juicio**, no una regla que se resuelva con un `if`.

> 🧠 **Para recordar:** reglas fijas en hooks; juicio con criterios y ejemplos en el prompt.

#### Trampa 6 · El traspaso al humano

**La situación.** SoporteBot tiene que pasarle el caso de Rosa a un supervisor (Tema 14).

**✅ En el examen elegí:** un **resumen estructurado**: customer ID, causa raíz, monto y acción recomendada, porque el humano **no tiene acceso a la conversación**.

**❌ Las que tientan:**

❌ **"Transferir con la conversación completa y los resultados de las tools".**
- *Tienta porque:* "tiene toda la información".
- *Está mal porque:* el humano tiene que hacer el análisis que debería haber hecho el agente. Y en muchos sistemas, el humano ni siquiera ve el transcript.

❌ **"Un mensaje breve: 'Necesito ayuda con el caso de Rosa'".**
- *Tienta porque:* es rápido.
- *Está mal porque:* no dice qué pasó, ni qué decisión se pide, ni qué se recomienda.

> 🧠 **Para recordar:** al humano, un resumen para decidir, no la conversación para leer.

### Grupo: Cuando algo falla

#### Trampa 7 · Reintentar todo

**La situación.** `process_refund` devuelve 400 "monto inválido", y el agente reintenta 5 veces (Temas 1 y 3).

**✅ En el examen elegí:** **no reintentar** errores permanentes (validación, permisos, negocio) ni de razonamiento: abortar y corregir o escalar. Reintentar, con backoff, **solo los transitorios**.

**❌ Las que tientan:**

❌ **"Reintentar con backoff exponencial, que es la buena práctica".**
- *Tienta porque:* backoff es lo correcto **para errores transitorios**.
- *Está mal porque:* este error es permanente. El mismo pedido va a fallar igual en cada intento.

❌ **"Subir el número de reintentos".**
- *Tienta porque:* parece más robusto.
- *Está mal porque:* no ataca la causa y suma costo.

> 🧠 **Para recordar:** solo se reintenta lo que podría salir distinto.

#### Trampa 8 · El resultado degradado que nadie sabe que es degradado

**La situación.** La API de precios falla, la cadena usa un precio guardado de hace una hora, y el resto del sistema lo toma como actual (Tema 4).

**✅ En el examen elegí:** **graceful degradation**: devolver el resultado **con una marca** (`degraded: true`, `source: cache`) para que el resto del sistema ajuste. Si la acción es de alto riesgo e irreversible, **escalar**.

**❌ Las que tientan:**

❌ **"Devolver el precio guardado sin marcar, para no complicar a los demás pasos".**
- *Tienta porque:* el flujo sigue limpio.
- *Está mal porque:* es una silent failure: el error aparece mucho después y cuesta rastrearlo.

> 🧠 **Para recordar:** si el resultado es peor, que lo diga.

### Grupo: Configurar hooks

#### Trampa 9 · El matcher que filtra por monto

**La situación.** Alguien configura un hook con `matcher` para que se aplique "solo a los reembolsos de más de USD 500" (Tema 9).

**✅ En el examen elegí:** el **matcher filtra por nombre de tool** (`process_refund`). La condición del monto va **dentro** de la función del hook.

**❌ Las que tientan:**

❌ **"Poner la condición del monto en el matcher".**
- *Tienta porque:* parece más prolijo.
- *Está mal porque:* los matchers solo miran el nombre de la tool, no sus argumentos.

> 🧠 **Para recordar:** el matcher elige la tool; la función decide el caso.

### Grupo: Pedidos con varios problemas

#### Trampa 10 · El cliente trae varios problemas juntos

**La situación.** Martín escribe con tres problemas en un mensaje (Tema 13).

**✅ En el examen elegí:** **descomponer** el pedido en ítems, **investigarlos en paralelo** con un **contexto compartido** (cliente verificado una sola vez) y responder con **una sola resolución** que cubra todo.

**❌ Las que tientan:**

❌ **"Resolver el problema más urgente y pedirle al cliente que escriba de nuevo por el resto".**
- *Tienta porque:* simplifica el flujo.
- *Está mal porque:* deja problemas sin resolver y obliga al cliente a volver a escribir.

❌ **"Resolverlos uno detrás de otro".**
- *Tienta porque:* parece más ordenado.
- *Está mal porque:* son independientes, así que en serie solo suma espera.

❌ **"Verificar la identidad de nuevo en cada ítem".**
- *Tienta porque:* parece más seguro.
- *Está mal porque:* la verificación ya está en el contexto compartido. Repetirla suma llamadas sin agregar seguridad.

> 🧠 **Para recordar:** varios problemas → partir, investigar en paralelo con lo compartido, responder todo junto.

---

## Checklist oficial

**Tarea 1.4 — Multi-step workflows with enforcement and handoff patterns**

*Knowledge of*
- [x] La diferencia entre enforcement programático (hooks, prerrequisitos) y guía por prompt para el orden de un flujo → **Temas 5 y 6** (Trampa 1)
- [x] Cuando se necesita cumplimiento determinístico (por ejemplo, verificar identidad antes de operaciones de dinero), las instrucciones del prompt tienen una tasa de falla mayor que cero → **Tema 5** (Trampas 1 y 2)
- [x] Protocolos de traspaso estructurado para escalar a mitad del proceso, con datos del cliente, análisis de causa raíz y acciones recomendadas → **Tema 14** (Trampa 6)

*Skills in*
- [x] Prerrequisitos programáticos que bloquean tools hasta que se completen los pasos previos (bloquear `process_refund` hasta que `get_customer` devuelva un ID verificado) → **Tema 6** (Trampa 1)
- [x] Descomponer pedidos con varios problemas en ítems, investigarlos en paralelo con contexto compartido y sintetizar una resolución unificada → **Tema 13** (Trampa 10)
- [x] Armar resúmenes de traspaso estructurados (customer ID, causa raíz, monto, acción recomendada) al escalar a humanos que no tienen acceso al transcript → **Tema 14** (Trampa 6)

**Tarea 1.5 — Agent SDK hooks for tool call interception and data normalization**

*Knowledge of*
- [x] Hooks (por ejemplo, PostToolUse) que interceptan resultados de tools para transformarlos antes de que el modelo los procese → **Temas 8, 9 y 11** (Trampas 3 y 4)
- [x] Hooks que interceptan llamadas salientes para hacer cumplir reglas (por ejemplo, bloquear reembolsos sobre un umbral) → **Temas 9 y 10** (Trampa 2)
- [x] La diferencia entre usar hooks para garantías determinísticas y confiar en el prompt para un cumplimiento probabilístico → **Temas 5 y 12** (Trampas 2 y 5)

*Skills in*
- [x] Hooks PostToolUse que normalizan formatos heterogéneos (Unix timestamps, ISO 8601, códigos de estado numéricos) de distintas tools MCP antes de que el agente los procese → **Tema 11** (Trampa 4)
- [x] Hooks de interceptación que bloquean acciones que violan la política (reembolsos de más de USD 500) y redirigen a flujos alternativos (escalamiento humano) → **Tema 10** (Trampa 2)
- [x] Elegir hooks en vez de enforcement por prompt cuando las reglas de negocio requieren cumplimiento garantizado → **Temas 5 y 12**

**📘 Curso (útil para entender; lecciones 21–26, 28 y deck 132):** tipos de error por origen, transient vs. permanent, códigos HTTP (Tema 1) · silent failures, output validation (schema, rango, completitud), schema vs. semantic, state verification, sanity checks, responsabilidades del validation gate, logging en cada frontera (Tema 2) · immediate/fixed/exponential backoff con jitter, políticas por tipo, retry budget, condiciones de aborto, `max_retries` (Tema 3) · fallback chains, pre-validación, graceful vs. silent degradation, marca de degradación, anti-patterns, parcial vs. falla total, degradar vs. escalar por riesgo y reversibilidad (Tema 4) · guidance vs. enforcement, tres modos de falla del prompt, casos suficientes e insuficientes, capas complementarias (Tema 5) · pre-execution, post-execution y runtime checks, hard block / soft warning / escalation, balance de rigidez (Tema 7) · eventos de hooks por frecuencia, bloquear vs. observar, exit codes 0/2/otro, PermissionRequest (Tema 8) · interruption points, contenido del handoff (context, decision, consequences, deadline), preservar el estado, escalamiento sincrónico vs. asincrónico, timeout, retomar sin repetir (Tema 14).

---

## Autoevaluación oral

1. ¿Por qué una regla escrita en el system prompt no alcanza para "nunca reembolsar más de USD 500 sin aprobación"? ¿Qué usás en su lugar y en qué evento?
2. ¿Qué diferencia hay entre PreToolUse y PostToolUse? Dame un uso de cada uno en SoporteBot.
3. El agente se saltea `get_customer` en el 12% de los casos. ¿Qué hacés? ¿Por qué no sirven el few-shot ni un routing classifier?
4. ¿Cuándo la respuesta correcta **sí** es el prompt y no un hook? Explicalo con el caso de cuándo escalar.
5. Tenés que pasarle el caso de Rosa a un supervisor. ¿Qué le mandás y por qué no la conversación completa?

---

## Preguntas tipo examen

Las preguntas tipo examen de este capítulo están en [`04-practica/modulo-1.md`](../04-practica/modulo-1.md), junto con las del resto del módulo 1. Hacelas cuando termines **todos** los capítulos del módulo, de a una y sin mirar la respuesta.

---

## Revisión contra el blueprint oficial

Qué puede salir en el examen de 1.4 y 1.5 que el curso de Jacob **no cubre o cubre flojo**, y dónde quedó explicado acá:

1. **Normalización de datos con PostToolUse** (1.5). El curso no la menciona: para el curso, PostToolUse solo reacciona o registra. La guía la pide como skill, con el ejemplo de timestamps Unix, ISO 8601 y códigos numéricos. → Tema 11 y Trampa 4.
2. **Pedidos con varios problemas** (1.4): descomponer en ítems, investigar en paralelo con contexto compartido y sintetizar una sola resolución. El curso no lo trata. → Tema 13 y Trampa 10.
3. **Contenido del handoff estructurado** (1.4): customer ID, root cause, refund amount y recommended action, porque el humano no tiene el transcript. El curso arma el mensaje con otros campos (context, decision, consequences, deadline). En el examen mandan los de la guía. → Tema 14 y Trampa 6.
4. **Hooks del Agent SDK, no de Claude Code** (1.5). El deck del curso es de Claude Code (scripts y exit codes) y no muestra cómo se registra un hook en el SDK: `HookMatcher` y `matcher` (que filtra solo por nombre de tool), `permissionDecision` con `permissionDecisionReason`, `updatedInput`, `updatedToolOutput`, `additionalContext` y la diferencia con `systemMessage`. → Temas 8 y 9; usos completos en Temas 10 y 11; Trampa 9.
5. **Bloquear y redirigir** (1.5): el curso tiene hard block y escalation por separado; la guía pide bloquear **y** mandar a otro flujo (escalamiento humano) en el mismo hook. → Temas 9 y 10, Trampa 2.
6. **Precedencia de hooks**: los hooks que aplican corren en paralelo y gana el más restrictivo (deny > defer > ask > allow); los hooks se evalúan antes que las reglas y los modos de permiso, y un `deny` vale incluso en `bypassPermissions`. Un `allow` de hook no se saltea las deny rules. Ojo con la comunidad que dice "en orden de registro". → Tema 9.
7. **Q1 de la guía** (prerrequisito programático): el curso no la trabaja con sus distractores (reforzar el prompt, few-shot, routing classifier). → Tema 6 y Trampa 1.
8. **Q3 de la guía** (cuándo escalar): la respuesta correcta **sí** es de prompt (criterios explícitos + few-shot), y es el contraste con Q1. El curso no la trabaja. → Tema 12 y Trampa 5.

No encontré otros huecos para estas dos tareas. Lo que el curso agrega por su cuenta (tool/reasoning/environment, backoff con jitter, retry budget, fallback chains, gates, interruption points, escalamiento sincrónico/asincrónico) queda marcado como 📘: es útil para razonar, pero no es la respuesta "oficial".

