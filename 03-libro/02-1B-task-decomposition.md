# Capítulo 2 · 1B · Udemy 3 — Task Decomposition & Planning (descomposición de tareas y planificación)

*Tarea oficial 1.6 · Segundo capítulo del módulo 1*

---

## Dónde estamos

Este capítulo cubre la tarea **1.6 Design task decomposition strategies for complex workflows** (diseñar estrategias de descomposición de tareas para workflows complejos). Es del Dominio 1 y pesa 3,86% del examen.

### Cómo leer este capítulo

Todo lo que leés acá **vale para el examen**, salvo que diga lo contrario. Cuando algo sale solo del curso (útil para entender, pero no central), lo marco con **📘 Curso**. Cuando Jacob dice algo distinto de lo que evalúa la guía, aparece un recuadro así:

> ⚠️ **En el curso vas a escuchar otra cosa.** … **Para el examen: …**

### Un aviso sobre este capítulo

En la tarea 1.6, la guía oficial evalúa tres cosas puntuales: **prompt chaining vs. descomposición dinámica**, **la revisión por archivo más una pasada de integración** y **cómo partir una tarea abierta** (el ejemplo de los tests en un legacy codebase). Eso está en los Temas 7 a 10, que son el corazón del capítulo. El curso, en cambio, dedica casi todo el bloque a teoría general de planificación (grafos de dependencias, fan-out/fan-in, replanning, ambigüedad), que la guía **no** nombra en 1.6. Esa teoría está en las Partes 1, 2 y 4, marcada como 📘 Curso: no te la van a preguntar por nombre, pero te da el vocabulario para razonar los escenarios.

## De dónde venimos

- En **1A** SoporteBot ganó su **agentic loop**: llama tools, devuelve los `tool_result` al historial, termina cuando `stop_reason` dice `end_turn` y escala cuando gira en falso. Viste también los patrones de workflow de Anthropic (prompt chaining, routing, parallelization, orchestrator-workers, evaluator-optimizer) y que no todo tiene que ser un agente: el reporte de los lunes y la clasificación de mails quedaron como workflows.
- Pero el capítulo terminó con un mensaje resuelto a medias. Martín escribió: "El pedido TX-104233 llegó con una zapatilla rota, me cobraron dos veces el TX-104251 y quiero cambiar la dirección de envío del TX-104300, que todavía no salió". SoporteBot resolvió el cobro doble y se olvidó del resto. El loop funcionaba. Lo que faltaba era **partir el trabajo**.

## Mapa del capítulo

**Parte 1 — Partir el trabajo (📘 Curso, con apoyo de la documentación).** Qué significa descomponer, cómo es una buena subtarea y cuánto partir.
1. Task decomposition: partir un objetivo compuesto.
2. Una buena subtarea y sus handoff points.
3. Cuánto partir: el costo de cada frontera, los anti-patterns y la descomposición jerárquica.

**Parte 2 — Ordenar las subtareas (📘 Curso, con apoyo de la documentación).** En qué orden se ejecutan las piezas.

4. Sequential execution y prompt chaining: uno detrás de otro.
5. Dependency graph: qué depende de qué.
6. Parallel execution: fan-out, fan-in y fallas parciales.

**Parte 3 — Elegir la estrategia (lo que evalúa la guía en 1.6).** Pipeline fijo o plan que se descubre en el camino.

7. Attention dilution: la revisión del PR de 14 archivos.
8. Fixed pipeline vs. dynamic decomposition: cuándo cada una.
9. Tareas abiertas: agregar tests a un legacy codebase.
10. Descomposición demasiado estrecha: el informe al que le faltaba cobertura.

**Parte 4 — Planes que cambian y objetivos poco claros (📘 Curso).**

11. Replanning y goal drift.
12. Ambigüedad: clarificar o asumir.

Cómo se conectan: los Temas 1–3 dicen **cómo partir**; los 4–6, **en qué orden correr** las piezas; los 7–10 aplican todo a la decisión que evalúa la guía (**¿pasos fijos o descubiertos?**); los 11–12 cuidan que un plan que se adapta **no pierda el objetivo**.

---

# Parte 1 — Partir el trabajo

> 📘 **Curso.** Los Temas 1 a 3 salen de las lecciones del curso. La guía no los nombra en 1.6, pero son la base para entender todo lo demás.

## Tema 1 — Task decomposition (descomposición de tareas)

### Qué es

Cuando un pedido trae varias cosas adentro, el agente puede atacarlo de dos maneras: como un solo bloque, o partido en piezas. **Task decomposition** (descomposición de tareas) es lo segundo: partir un objetivo de alto nivel en **subtasks** (subtareas) más chicas, que se pueden asignar a agentes, a tools o a pasos de un workflow. Se hace **antes** de empezar a actuar, porque una vez que el agente arrancó con todo junto, ya no hay piezas que manejar por separado.

La alternativa es tratar el objetivo como una **monolithic task** (tarea monolítica: un solo bloque). El problema es que todo queda atado. Si falla cualquier parte, **falla todo**. Y como no hay piezas, no podés **reintentar solo lo que se rompió**: el reintento vuelve a arrancar desde cero, incluso lo que ya había salido bien.

Una tarea descompuesta, en cambio, tiene piezas que se pueden **reintentar, delegar y probar por separado**. Cuesta más diseñarla al principio, pero esa inversión se recupera en resiliencia: cuando algo falla, el daño queda encerrado en una pieza.

El curso ordena esto en un **decomposability spectrum** (espectro de descomponibilidad). Sirve para ver que no se trata de partir siempre más, sino de encontrar el punto justo:

| Punto del espectro | Cómo es |
|---|---|
| **Monolithic** | Una tarea grande, difícil de reintentar y de delegar. |
| **Well-decomposed** (bien descompuesta) | Subtareas claras, con entradas y salidas definidas. |
| **Over-decomposed** (sobredescompuesta) | Tantos pasos chiquitos que la coordinación se come el presupuesto. |

Los dos extremos son malos. Lo bueno está en el medio (Tema 3).

Para saber cómo partir, el curso propone hacerse **tres preguntas** sobre el objetivo antes de cortar. Cada una detecta una razón distinta para separar piezas:
1. ¿Alguna parte puede correr **sin depender** del resto?
2. ¿La **salida** de un paso es la **entrada** de otro?
3. ¿Hay partes que necesitan **capacidades distintas** (por ejemplo, tools de pagos vs. tools de logística)?

### Ejemplo

SoporteBot leyó el mensaje de Martín como un solo problema. Empezó por lo que le pareció más urgente (el cobro doble), entró en un ida y vuelta largo con la tool de pagos y, cuando lo resolvió, respondió con `end_turn`. Para Claude, la tarea estaba terminada.

Lucas propuso agregar al system prompt: "Si el cliente menciona varios problemas, resolvelos todos". Ayudó un poco. Pero cuando el cobro doble falló a mitad de camino, el reintento volvió a arrancar todo de cero, incluida la zapatilla rota que ya estaba resuelta. Y en los logs no se podía ver qué parte había salido bien y cuál no.

Con las tres preguntas, el análisis cambia. Los tres problemas (zapatilla rota, cobro doble, cambio de dirección) son **independientes** entre sí; ninguno necesita la salida de otro; y cada uno usa **tools distintas** (cambios, pagos, logística). Son tres subtareas. Con la descomposición, cada una tiene su propio resultado, y si falla el cobro doble, se reintenta solo eso.

### Para el examen

- Un objetivo **compuesto** tratado como monolítico: si falla una parte, falla todo, y no se puede reintentar solo lo roto.
- Una instrucción en el prompt ("resolvé todos") **no** reemplaza partir la tarea: no da reintentos por partes ni trazabilidad.
- 📘 Las tres preguntas (independencia, salida→entrada, capacidades distintas) son del curso. La guía no las pide por nombre, pero sirven para razonar cualquier escenario.

### Cómo se une

Es lo que le faltaba al loop de 1A: el loop ejecuta, pero alguien tiene que decidir **qué** ejecutar y en qué piezas.

---

## Tema 2 — Good subtasks and handoff points (una buena subtarea y sus puntos de traspaso)

### Qué es

Partir no alcanza: las piezas tienen que estar bien cortadas. Una subtarea mal definida (que hace dos cosas, o que depende de datos que nadie le pasó) trae los mismos problemas que la tarea monolítica, pero repartidos. El curso da **cuatro propiedades** de una subtarea bien definida, y cada una evita un problema concreto:
- **Single responsibility** (responsabilidad única): hace una sola cosa y tiene una salida clara, que se puede probar y que otro paso puede usar. Si hace dos cosas, no sabés cuál falló.
- **Defined inputs** (entradas definidas): sabe exactamente qué datos recibe. No asume nada del **ambient state** (el "ambiente": lo que quedó suelto en el historial), porque lo que está suelto puede no estar la próxima vez.
- **Bounded scope** (alcance acotado): es lo bastante chica como para reintentarla sola, sin volver a correr todo el workflow.
- **Clean output** (salida limpia): devuelve algo estructurado, que el siguiente paso puede usar sin tener que interpretar texto libre.

(Detalle: la slide de resumen del curso, p. 69, lista solo tres y se olvida de *bounded scope*. Son cuatro.)

El punto donde una subtarea le pasa su resultado a la siguiente se llama **handoff point** (punto de traspaso). Es donde más fácil se pierde o se malinterpreta información, por eso conviene tratarlo como una **interfaz** (un contrato entre dos partes) y diseñarlo con tres cuidados:
- un **esquema explícito**, para que el que recibe no malinterprete los datos;
- **solo lo que el siguiente paso necesita** (payload chico: el paquete de datos que viaja);
- **documentado lo que NO se pasa**, para que nadie asuma algo que no recibió.

La documentación de Anthropic llega a lo mismo desde el lado del que delega. En su sistema de investigación multi-agente, Anthropic dice que cada subagente necesita **un objetivo, un formato de salida, una guía de qué tools y fuentes usar, y límites claros de su tarea**. Lo vas a ver aplicado en el Tema 10.

### Ejemplo

Así queda la subtarea del cambio de dirección de Martín:

```json
{
  "subtask": "change_shipping_address",
  "order_id": "TX-104300",
  "customer_id": "C-5521",
  "new_address": null,
  "not_included": "datos de pago y de los otros pedidos (no los necesita)"
}
```

`order_id` y `customer_id` son los datos que la subtarea necesita (**defined inputs**): no tiene que ir a buscarlos al historial. `new_address` está en `null` a propósito, porque Martín todavía no dijo cuál es (volvemos a esto en el Tema 12). Y `not_included` deja escrito qué se dejó afuera, así nadie espera encontrar ahí los datos de pago.

### Cómo se configura

📘 **Curso:** el curso muestra los contratos con Pydantic (una librería de Python que valida datos contra un modelo). Adaptado a SoporteBot:

```python
from pydantic import BaseModel

class ChangeAddressInput(BaseModel):   # single responsibility: cambiar UNA dirección
    order_id: str                      # defined inputs: nada sale del "ambiente"
    customer_id: str
    new_address: str | None            # puede faltar; el null es explícito

class ChangeAddressOutput(BaseModel):  # clean output: el orquestador lo rutea sin leer texto libre
    order_id: str
    status: str                        # "updated" | "needs_clarification" | "failed"
    detail: str

# El handoff pasa solo lo necesario y documenta lo que no pasa
NEXT_STEP_NEEDS = ("order_id", "status")
NOT_PASSED = ("raw_message", "chat_history")   # documentado a propósito

def handoff(result: dict) -> dict:
    payload = {k: result[k] for k in NEXT_STEP_NEEDS}
    payload["_omitted"] = list(NOT_PASSED)
    return payload
```

### Para el examen

- Una subtarea buena hace **una cosa**, recibe **datos explícitos**, es **reintentable sola** y devuelve algo **estructurado**.
- Un handoff es una interfaz: **esquema explícito**, **mínimo necesario**, y **lo que no se pasa, documentado**.
- Si la pregunta muestra subagentes que duplican trabajo o investigan otra cosa por instrucciones vagas, la respuesta es **mejorar la descripción de la subtarea** (objetivo, formato de salida, fuentes, límites).

### Cómo se une

Las cuatro propiedades son el criterio para saber **dónde** cortar. El Tema 3 dice **cuánto** cortar.

---

## Tema 3 — Cost of decomposition, anti-patterns and hierarchical decomposition (el costo de partir, los anti-patterns y la descomposición jerárquica)

### Qué es

Descomponer **no es gratis**. Cada frontera nueva entre dos subtareas significa otra llamada, otro traspaso de datos y otro lugar donde algo puede salir mal. Por eso partir de más es tan malo como partir de menos. El curso nombra cinco costos de cada frontera:
- más **llamadas al modelo**;
- más **tokens**;
- posibles **fallas en el handoff**;
- más **latencia** (tiempo de espera);
- más **tiempo de diseño**.

Además, un sistema muy partido es más difícil de rastrear y de depurar, porque un error puede venir de cualquiera de las muchas piezas.

De ahí salen tres **anti-patterns** (soluciones que parecen correctas pero son errores de diseño). Los dos primeros son los extremos del espectro del Tema 1; el tercero es un error al ordenar:
- **Under-decomposition** (quedarse corto): tareas tan grandes que no se pueden reintentar ni delegar bien. Es el SoporteBot del Tema 1.
- **Over-decomposition** (pasarse): tantos pasos que la coordinación cuesta más que el trabajo.
- **False parallelism** (falso paralelismo): tratar como independientes pasos que dependen entre sí. Lo vemos en el Tema 6.

También se puede partir en niveles, como un árbol: el objetivo se parte en subobjetivos, los subobjetivos en tareas, las tareas en pasos. Esto se llama **hierarchical decomposition** (descomposición jerárquica). Un orquestador arriba delega hacia abajo, y los resultados suben para sintetizarse. La ventaja es que cada nivel maneja solo su grado de complejidad.

¿Cuántos niveles? La regla del curso es bajar un nivel solo cuando las subtareas necesitan capacidades **fundamentalmente distintas**, y aplanar cuando las subtareas se parecen tanto que las puede hacer el mismo agente. El porqué: cada nivel extra es **otro lugar por donde se propaga un error**.

La documentación de Anthropic ("Building effective agents") empuja en la misma dirección: buscar **la solución más simple posible** y sumar complejidad **solo cuando mejora los resultados de forma demostrable**.

### Ejemplo

Después del Tema 1, Lucas quedó tan convencido que se fue al otro extremo. Dos semanas después, el cambio de dirección tarda 40 segundos y a veces falla en lugares raros. Lucas lo había partido en **doce pasos**: uno valida el formato del número de pedido, otro busca el pedido, otro valida la calle, otro el código postal, otro la ciudad…

Cada paso es una llamada al modelo con su propio handoff. Doce llamadas son doce veces la latencia y los tokens, y once handoffs donde algo se puede perder o malinterpretar. La mayor parte del tiempo se va en **coordinar**, no en trabajar.

La corrección: el cambio de dirección vuelve a ser **una sola subtarea**. Las validaciones de formato pasan a ser **código común dentro de la tool**, no llamadas al modelo.

### Para el examen

- Partir de menos (under) y partir de más (over) son los dos errores. Se parte **donde cambia la responsabilidad**, no donde se puede.
- Más niveles de jerarquía = más superficie de error. Solo se baja un nivel si cambia la capacidad necesaria.
- Si una opción agrega agentes, niveles o pasos "por prolijidad", sospechá: la doc pide lo más simple que funcione.
- 📘 Los nombres *over-decomposition*, *under-decomposition* y *false parallelism* son del curso, no de la guía. En el examen vas a ver el **síntoma** (lento y caro; no se puede reintentar; datos pisados), no necesariamente el nombre.

### Cómo se une

Ya sabés cortar en el lugar justo. Ahora falta decidir si las piezas corren una detrás de otra o al mismo tiempo.

---

# Parte 2 — Ordenar las subtareas

> 📘 **Curso.** Los Temas 4 a 6 salen sobre todo del curso. Lo que agrega la documentación de Anthropic (prompt chaining, parallelization) sí es central, porque lo usa la Parte 3.

## Tema 4 — Sequential execution and prompt chaining (ejecución secuencial y encadenamiento de prompts)

### Qué es

**Sequential execution** (ejecución secuencial) es correr las tareas **de a una, en un orden definido**. La razón de ir en orden es que cada paso puede depender de la salida del anterior: no podés arrancar el segundo si todavía no tenés lo que produce el primero.

Cuando la secuencia es **fija** y la salida de cada llamada al modelo es la entrada de la siguiente, Anthropic lo llama **prompt chaining** (encadenamiento de prompts). Lo viste en 1A como patrón de workflow. Lo que agrega la documentación es cuándo conviene y qué se gana:
- Es ideal cuando la tarea se puede partir **fácil y limpiamente en subtareas fijas**.
- Entre paso y paso se pueden poner **gates** (compuertas): chequeos en código que verifican la salida intermedia antes de seguir.
- Cambia **latencia por precisión**: cada llamada es más fácil, así que sale mejor, aunque el total tarde más.
- La documentación de prompting agrega que el chaining explícito (pasos como llamadas separadas a la API) sigue siendo útil **cuando necesitás inspeccionar las salidas intermedias** o **imponer una estructura fija** al pipeline: cada paso se puede registrar, evaluar o desviar.

📘 **Curso:** el curso también define prompt chaining (slide p. 81): "la salida de una llamada es la entrada de la siguiente; cada paso tiene una responsabilidad única y acotada". Pero no lo conecta con la elección "fijo vs. dinámico" ni con la revisión de código: eso lo pone la guía (Temas 7 y 8).

¿Cuándo tiene sentido ir en secuencia? El curso da cuatro motivos. Todos son casos donde el orden aporta algo que el paralelo no puede dar:
- **Data dependency** (dependencia de datos): el paso B necesita literalmente la salida del paso A.
- **State accumulation** (acumulación de estado): cada paso construye sobre un contexto que los anteriores fueron armando.
- **Ordered transforms** (transformaciones en orden): las operaciones tienen que ir en un orden fijo (parsear, después validar, después enriquecer).
- **Simplicity goal** (prioridad a la simplicidad): depurar y auditar importa más que la velocidad.

Lo secuencial tiene dos costos. El primero es el tiempo: el **tiempo total es la suma** de todos los pasos, y pasos que podrían correr juntos quedan esperando. El segundo es la fragilidad: si un paso falla, **se frena toda la cadena**, porque el paso siguiente no tiene con qué trabajar. A eso el curso lo llama **error cascade** (falla en cascada), y el riesgo crece con cada paso que agregás.

La defensa contra la cascada es **validar la salida en cada frontera** con un esquema (campos obligatorios, tipos, valores que pueden ser nulos). Así el error se detecta **antes** del paso siguiente y no viaja lejos. Lo que falla va a una **cola de errores** en vez de seguir de largo.

### Ejemplo

Dentro de la subtarea del cobro doble de Martín hay una dependencia real: primero hay que **confirmar** que el TX-104251 se cobró dos veces, y después **reembolsar** uno de los cobros. No se puede al revés, porque el reembolso necesita el ID del cobro duplicado que sale del primer paso.

### Cómo se configura

📘 **Curso:** la validación en la frontera, adaptada al cobro doble:

```python
from pydantic import BaseModel, ValidationError

class DuplicateChargeCheck(BaseModel):   # salida del paso 1 = contrato de entrada del paso 2
    order_id: str                        # obligatorio, con tipo
    duplicate_charge_id: str
    amount: float
    note: str | None = None              # puede ser nulo, y queda explícito

try:
    check = DuplicateChargeCheck.model_validate_json(step1_output)
except ValidationError as err:
    fail_at_boundary(err)                # se corta acá: el reembolso nunca corre con datos malos
else:
    refund(check.duplicate_charge_id, check.amount)
```

`fail_at_boundary` es el **gate**: si el paso 1 devolvió algo incompleto, el reembolso no se ejecuta.

### Para el examen

- **Prompt chaining** = pasos **fijos**, cada uno con la salida del anterior. Sirve para tareas que se parten limpio en pasos conocidos.
- Se pueden poner **gates** entre pasos; las salidas intermedias se pueden inspeccionar.
- Secuencial es correcto cuando la dependencia es **real**. Si no lo es, estás pagando latencia de más (Tema 5).
- Validar en cada frontera corta la cascada de errores.

### Cómo se une

El chaining es la mitad "fija" de la decisión central de 1.6 (Tema 8). Pero antes de encadenar todo, conviene ver qué depende realmente de qué.

---

## Tema 5 — Dependency graph (grafo de dependencias)

### Qué es

Muchas veces los pasos se ponen en fila sin pensar si de verdad dependen entre sí. Un **dependency graph** (grafo de dependencias) es un mapa que lo deja a la vista: qué pasos necesitan a cuáles. Dibujarlo sirve para descubrir qué puede ir al mismo tiempo y qué no.

Se arma con tres reglas simples. Se dibuja una flecha de A a B cuando B necesita la salida de A para correr. Los pasos a los que **no les llega ninguna flecha** pueden arrancar primero, y potencialmente en paralelo. Y los pasos a los que les llegan **varias flechas** son **synchronization points** (puntos de sincronización): tienen que esperar a que terminen todos los anteriores.

Al dibujarlo aparecen dos tipos de dependencia:
- **True dependency** (dependencia real): B lee un campo que produce A. El orden es obligatorio.
- **Artificial dependency** (dependencia artificial): los pasos van en orden **por costumbre**, no por necesidad.

Sacar las dependencias artificiales **habilita el paralelismo**, y suele ser la forma más barata de bajar la latencia: no hay que cambiar ningún paso, solo dejar de esperar sin motivo.

### Ejemplo

El primer SoporteBot resolvía las tres subtareas de Martín una detrás de otra: zapatilla, cobro, dirección. Martín esperaba 25 segundos.

Al dibujar el grafo se ve que la zapatilla, el cobro y la dirección **no tienen flechas entre sí**. La dirección esperaba al reembolso solo porque "siempre se hizo así": era una **dependencia artificial**. El único punto de sincronización es el final, porque **armar la respuesta** a Martín necesita los tres resultados.

Dentro del cobro, en cambio, la flecha de "confirmar" a "reembolsar" es real (Tema 4).

### Para el examen

- 📘 El grafo de dependencias, las dependencias artificiales y los puntos de sincronización son **del curso**. La guía no los nombra en 1.6.
- Lo que sí puede salir (y es coherente con la doc): **paralelizar solo lo realmente independiente**, y que un paso que usa los resultados de otros (como la pasada de integración del Tema 7) va **después** de ellos.

### Cómo se une

El grafo te dice qué puede ir en paralelo. El Tema 6 dice cómo correrlo en paralelo sin romper nada.

---

## Tema 6 — Parallel execution: fan-out, fan-in and partial failures (ejecución en paralelo: abrir, juntar y fallas parciales)

### Qué es

**Parallel execution** (ejecución en paralelo) es correr subtareas independientes **al mismo tiempo**. La ganancia es obvia: el tiempo total deja de ser la suma de los pasos. Pero trae dos problemas nuevos: hay que juntar los resultados en algún punto, y hay que decidir qué hacer cuando algunas ramas fallan y otras no.

Por eso tiene dos momentos. En el **fan-out** (abrir en abanico), desde **un solo punto de control** se mandan todas las ramas a correr al mismo tiempo; cada rama corre con sus propias entradas y contexto, y puede ser un agente, una llamada a una tool o un sub-workflow. En el **fan-in** (juntar), un paso recolecta los resultados de las ramas antes de seguir.

En 1A viste el patrón **parallelization** de Anthropic. Tiene dos variantes, y conviene no confundirlas porque resuelven cosas distintas:
- **Sectioning** (división en secciones): partir la tarea en subtareas **independientes** que corren en paralelo. Es exactamente este fan-out.
- **Voting** (votación): correr **la misma tarea varias veces** para tener varias respuestas.

**El test de independencia.** Antes del fan-out, el curso pide el **independence test** (test de independencia), porque correr juntas dos ramas que no son independientes rompe datos. Dos ramas son independientes si:
1. ninguna necesita la salida de la otra;
2. no escriben el mismo **shared state** (estado compartido: datos que las dos pueden modificar);
3. el resultado no cambia según cuál termine primero.

Si alguna de las tres falla, **va secuencial**. Esto es lo que evita el **false parallelism** (Tema 3). Cuando dos ramas que no son independientes corren juntas, aparece un **data hazard** (riesgo de datos): una rama pisa lo que escribió la otra, o trabaja con datos viejos.

**Qué hace el fan-in.** Juntar no es solo esperar. El fan-in tiene **cuatro responsabilidades**:
1. **Collect** (juntar): recolectar los resultados de las ramas que terminaron a tiempo.
2. **Handle failures** (manejar fallas): decidir qué hacer con las ramas que fallaron o se pasaron de tiempo.
3. **Order** (ordenar): reordenar si el orden importa después.
4. **Merge and continue** (combinar y seguir): unir los resultados y pasarlos al paso siguiente.

**Fallas parciales.** La regla más importante es **nunca descartar en silencio una rama que falló** (*never silently drop branches*). Si la descartás, el paso siguiente (o el cliente) cree que todo salió bien. Hay que elegir una **política explícita** de **partial failure** (falla parcial):
- **Abortar todo** (*fail the pipeline*).
- **Seguir con resultados parciales**, marcando qué falló (*proceed with partial results*).
- **Reintentar solo las ramas que fallaron** (*retry failed branches*).

**Cómo combinar.** Para unir los resultados, el curso da tres **merging strategies** (estrategias de combinación). La elección depende de qué devolvió cada rama:

| Qué devolvieron las ramas | Estrategia |
|---|---|
| Todas respondieron **la misma pregunta** | **Voting**: gana la mayoría |
| Cada una llenó **un campo distinto** de un objeto | **Structured aggregation** (agregación estructurada) |
| Ninguna de las anteriores | **Concatenation**: concatenar en una lista |

> ⚠️ **En el curso vas a escuchar otra cosa.** Jacob presenta la votación como "gana la mayoría", y eso sirve para **decidir o clasificar** (tres clasificaciones del mismo mail, gana la más repetida). **Para el examen:** cuando el objetivo es **detectar problemas**, alcanza con que **una** pasada marque el problema, como en el ejemplo de voting de Anthropic (revisar código buscando vulnerabilidades con varios prompts distintos). Si filtrás por mayoría, tirás hallazgos válidos que encontró una sola pasada. Es un distractor de una pregunta oficial (Tema 7).

**Cuánto cuesta.** El paralelo baja el tiempo de espera, pero **no los tokens**. Tres ramas al mismo tiempo gastan tres veces más tokens por segundo, y el costo total es **la suma de todas las ramas**. Además, los **rate limits** (límites de uso de la API) y las cuotas ponen un techo a cuántas ramas pueden correr juntas. Lo secuencial es más barato por corrida y no tiene fallas parciales.

La documentación de Anthropic sobre su sistema de investigación da números: el agente principal lanza **3 a 5 subagentes en paralelo** (en vez de uno por uno), y con eso el tiempo de investigación baja **hasta 90%** en consultas complejas. Pero avisa dos cosas: un sistema multi-agente gasta **unas 15 veces más tokens** que un chat, y **la mayoría de las tareas de programación tienen menos partes realmente paralelizables** que una investigación.

**Los patrones se combinan.** En la práctica, rara vez un sistema es solo secuencial o solo paralelo. Lo más común:
- **Jerárquico + secuencial:** el orquestador delega en subagentes que adentro corren un pipeline en orden.
- **Jerárquico + paralelo:** el orquestador abre en abanico hacia varios subagentes especializados.
- **Secuencial + paralelo:** etapas en orden, y dentro de cada etapa, subtareas independientes en paralelo.

### Ejemplo

SoporteBot ahora corre las tres subtareas de Martín con fan-out. La de la dirección falla, porque el servicio de logística está caído. El fan-in **no la descarta**. La respuesta dice:

> "Ya registramos el cambio de la zapatilla y te devolvimos el cobro duplicado. El cambio de dirección no lo pudimos hacer ahora; lo reintentamos en 10 minutos y te avisamos."

Es la política "seguir con resultados parciales, marcando qué falló", más un reintento de la rama caída.

El caso de **false parallelism**: imaginá que Martín hubiera pedido "cambiá la dirección del TX-104300 y agregale un producto al mismo pedido". Las dos ramas escriben sobre **el mismo pedido**, así que fallan el test de independencia (punto 2) y van en secuencia.

El flujo completo de SoporteBot es una combinación **secuencial + paralelo**: primero parte el mensaje, después corre las tres subtareas en paralelo y al final arma una respuesta.

### Cómo se configura

📘 **Curso:** el fan-out con manejo explícito de fallas parciales, adaptado a Martín:

```python
import asyncio

async def fan_out(subtasks, message):
    # return_exceptions=True: una rama que falla no tumba a las otras
    results = await asyncio.gather(*(s(message) for s in subtasks),
                                   return_exceptions=True)
    ok = [r for r in results if not isinstance(r, Exception)]
    failed = [s.__name__ for s, r in zip(subtasks, results)
              if isinstance(r, Exception)]
    return ok, failed          # la falla parcial queda a la vista, no se descarta

# ok, failed = await fan_out([replace_item, refund_duplicate, change_address], msg)
# failed == ["change_address"]  -> se informa a Martín y se reintenta solo esa rama
```

### Para el examen

- Paralelizar **solo lo independiente** (sectioning). Usá el test de independencia: no necesita la salida de otra rama, no escribe el mismo estado, el orden no cambia el resultado.
- Una rama caída **nunca se descarta en silencio**: abortar, seguir parcial marcando qué falló, o reintentar esa rama.
- Votación por mayoría **no** sirve para detectar problemas: suprime hallazgos reales.
- El paralelo ahorra tiempo, **no tokens**. Y multi-agente cuesta mucho más en tokens: no se agrega sin necesidad.
- 📘 Fan-out/fan-in, data hazard y las estrategias de combinación son **del curso**; la guía no los evalúa en 1.6 por nombre.

### Cómo se une

Con los Temas 1–6 sabés partir, ordenar y paralelizar. La Parte 3 aplica todo eso a lo que la guía evalúa de verdad: **qué estrategia elegir** según la tarea.

---

# Parte 3 — Elegir la estrategia (lo que evalúa la guía)

## Tema 7 — Attention dilution (dilución de la atención): la revisión del PR de 14 archivos

### Qué es

**Attention dilution** (dilución de la atención) es lo que pasa cuando un solo pedido le pide al modelo analizar **mucho material a la vez**. La atención del modelo se reparte entre todo, y el análisis queda **desparejo**: unas partes se miran a fondo, otras casi nada, y aparecen contradicciones entre lo que dice de una parte y de otra.

Lo importante es que **no es un problema de espacio** en el context window (la cantidad de texto que el modelo puede recibir de una vez). Todo el material puede entrar con espacio de sobra y la dilución igual aparece. Es un problema de **cómo está partida la tarea**, y por eso se resuelve partiéndola distinto, no dándole más lugar.

La solución que pide la guía es descomponer la revisión con **prompt chaining**, en dos tipos de pasada:
1. **Per-file local analysis pass** (una pasada local por archivo): cada archivo se revisa solo, buscando problemas **dentro** de ese archivo. Como el modelo mira un archivo por vez, la atención no se reparte.
2. **Cross-file integration pass** (una pasada de integración entre archivos), **separada**: mira el **flujo de datos entre archivos**, que es justo lo que las pasadas locales no pueden ver.

Son pasos fijos y predecibles: siempre N pasadas locales y una de integración. Las pasadas locales son independientes entre sí, así que pueden correr en paralelo (Tema 6). La de integración va **después**, porque usa lo que encontraron las locales (Tema 5).

### Ejemplo

El equipo de desarrollo de TiendaX usa Claude para revisar los **pull requests** (PR: el pedido de incorporar un cambio de código al proyecto) en el **pipeline de CI** (el proceso automático que corre tests y chequeos en cada cambio de código). Sofía abre un PR que toca **14 archivos** del módulo de checkout. La revisión automática hace **una sola pasada** sobre los 14 archivos juntos.

El resultado sale desparejo en tres sentidos. Sobre los dos primeros archivos hay comentarios detallados, y sobre los últimos casi nada. Se escapa un bug claro en `CartTotals.cs`. Y hay comentarios **contradictorios**: en un archivo marca como problema un patrón que en otro archivo aprueba.

Aparecen cinco propuestas:
- "Usemos un modelo más grande, con más context window, así le entran los 14 archivos con espacio de sobra."
- "Corramos la revisión tres veces y marquemos solo lo que aparezca en al menos dos."
- "Pidamos a los desarrolladores que hagan PRs de 3 o 4 archivos."
- "Revisemos en lotes de 5 archivos."
- "Agreguemos al prompt: 'revisá todos los archivos con la misma profundidad'."

Ninguna ataca la causa. La correcta tiene dos pasos. Primero, **14 pasadas locales**, una por archivo, cada una buscando problemas solo en su archivo (así aparece el bug de `CartTotals.cs`). Después, **una pasada de integración** que mira si los archivos encajan entre sí (por ejemplo, si `CartTotals` y `CheckoutService` calculan los descuentos de forma compatible).

Por qué fallan las otras:
- **Modelo más grande o más contexto:** los 14 archivos ya entraban. Más espacio no cambia cómo se reparte la atención.
- **Consenso de 2 de 3:** exigir que un problema aparezca en varias pasadas **suprime bugs reales** que una sola pasada detectó. Y cada pasada completa sigue diluida.
- **PRs más chicos:** le pasa a los desarrolladores un problema de arquitectura, en vez de resolverlo en el sistema.
- **Lotes de 5 archivos:** baja la dilución dentro de cada lote, pero **nadie mira lo que pasa entre archivos de lotes distintos**. Falta la pasada de integración.
- **Instrucción en el prompt:** pedir "misma profundidad" no cambia la estructura que causa la dilución.

### La pregunta oficial de muestra

Es casi textual la pregunta de muestra de la guía (escenario *Claude Code for Continuous Integration*): un PR que modifica 14 archivos de un módulo de control de stock; la revisión en una pasada dio profundidad despareja, bugs no detectados y feedback contradictorio.
- **✅** Partir en pasadas enfocadas: analizar cada archivo por separado buscando problemas locales, y después una pasada separada de integración que examina el flujo de datos entre archivos.
- ❌ Exigir PRs de 3–4 archivos.
- ❌ Un modelo de nivel superior con un context window más grande.
- ❌ Tres pasadas completas y marcar solo lo que aparece en al menos dos.

La explicación oficial: partir en pasadas enfocadas **ataca la causa raíz, que es la attention dilution**.

(Algunas guías de la comunidad etiquetan esta pregunta como de la tarea 4.6, revisión en varias pasadas. Pero el texto es literalmente el segundo *skill* de 1.6. La revisión multi-pasada vuelve en 4C.)

### Para el examen

- Si **entra** pero sale **desparejo**, la causa es attention dilution, no falta de contexto.
- Respuesta fija: **pasada local por archivo + pasada de integración separada**.
- Los distractores son siempre los mismos cuatro tipos: más modelo/contexto, consenso entre pasadas, pasarle el problema a la gente, una instrucción en el prompt. Y su primo: lotes sin integración.

### Cómo se une

Es prompt chaining (Tema 4) con fan-out en las pasadas locales (Tema 6) y una dependencia real hacia la integración (Tema 5). Y funciona porque la tarea es **predecible**. El Tema 8 dice qué hacer cuando no lo es.

---

## Tema 8 — Fixed sequential pipeline vs. dynamic adaptive decomposition (pipeline fijo vs. descomposición dinámica y adaptativa)

### Qué es

Esta es **la decisión central de 1.6**. La pregunta es simple: ¿sabés de antemano qué pasos hay que hacer, o los vas a descubrir mientras trabajás? Según la respuesta, la guía distingue dos estrategias:
- **Fixed sequential pipeline** (pipeline secuencial fijo), es decir, **prompt chaining**: cuando los pasos **se conocen de antemano**. Sirve para **revisiones predecibles de varios aspectos**, como la del Tema 7.
- **Dynamic adaptive decomposition** (descomposición dinámica y adaptativa): cuando las subtareas **dependen de lo que se va descubriendo** (*based on intermediate findings*: según los hallazgos intermedios). Sirve para **tareas abiertas de investigación o exploración**.

La guía también pide entender **el valor de los adaptive investigation plans** (planes de investigación adaptativos): planes que **generan subtareas nuevas según lo que se descubre en cada paso**. El porqué es directo: en una tarea abierta, no podés escribir todos los pasos al principio porque todavía no sabés qué vas a encontrar.

El curso dice lo mismo en términos de planificación, y agrega el costo de cada opción:
- **Static planning** (plan estático): una secuencia fija de pasos escrita **en tiempo de diseño**, antes de ejecutar. Es **predecible, auditable y barata**: cada paso se puede probar por separado y las fallas son fáciles de ubicar. Ideal para tareas bien delimitadas y repetibles.
- **Dynamic planning** (plan dinámico): el modelo **genera o revisa** su plan **en tiempo de inferencia**, mientras trabaja, según los resultados intermedios. Se adapta, pero necesita **más monitoreo, más logs y caminos de salida explícitos** (*fallbacks*), porque los pasos siguientes no se auditaron de antemano.

La diferencia central es **cuándo se deciden los pasos**. Curso y guía coinciden; el costo de lo dinámico (monitoreo, logs, fallbacks) es coherente con lo que dice la documentación de Anthropic: en problemas abiertos, donde no se puede prever cuántos pasos hacen falta, conviene tener **condiciones de corte**.

¿Te acordás del patrón **orchestrator-workers** de 1A? Ahora tiene sentido. Un modelo central **decide las subtareas según el input** (no están predefinidas), se las reparte a *workers* (otras llamadas al modelo) y después sintetiza los resultados. Anthropic lo recomienda para **tareas complejas donde no se pueden prever las subtareas**, y da como ejemplo los productos de programación que hacen cambios complejos en varios archivos cada vez. La diferencia con **parallelization** (Tema 6) es quién define las subtareas: ahí están definidas de antemano; acá las decide el orquestador. Es la herramienta típica de la descomposición dinámica. Lo vemos a fondo en 1C.

### Ejemplo

En TiendaX hay dos tareas que parecen parecidas y se resuelven distinto. **Revisar los PRs** (Tema 7) siempre son N archivos y siempre los mismos dos tipos de pasada: los pasos se conocen, así que va **prompt chaining**. **Agregar tests al módulo de pagos legacy** (Tema 9) es distinto: no se sabe qué se va a encontrar adentro, así que va **descomposición dinámica**.

### Para el examen

- **Pasos conocidos y predecibles → prompt chaining.** **Alcance desconocido, investigación abierta → descomposición dinámica** (orchestrator-workers).
- "Dinámico" **no es mejor** por sí mismo: en una tarea predecible solo agrega costo, la vuelve menos auditable y más difícil de depurar.
- Un pipeline fijo en una tarea abierta **no reacciona** a lo que descubre.
- 📘 Static = design time; dynamic = inference time. Dinámico pide más monitoreo, logs y fallbacks.

### Cómo se une

El Tema 7 fue el caso fijo. El Tema 9 es el caso dinámico que la guía usa de ejemplo.

---

## Tema 9 — Decomposing open-ended tasks (partir tareas abiertas): tests en un legacy codebase

### Qué es

Una **open-ended task** (tarea abierta) es una tarea cuyo alcance no se conoce hasta que empezás. El ejemplo de la guía es **"add comprehensive tests to a legacy codebase"** (agregar tests completos a un código heredado). Un **legacy codebase** es código viejo, poco documentado y que nadie quiere tocar. Es abierta porque no sabés qué clases hay, cuáles dependen de cuáles ni qué obstáculos vas a encontrar hasta que lo mirás.

Por eso la guía describe una secuencia en tres pasos, y el orden importa: no podés priorizar lo que todavía no conocés.
1. **Map structure first** (mapear la estructura primero): qué clases hay, quién llama a quién, qué depende de qué.
2. **Identify high-impact areas** (identificar las áreas de alto impacto): dónde un error duele más.
3. **Create a prioritized plan that adapts as dependencies are discovered** (armar un plan priorizado que se adapta a medida que aparecen dependencias).

En Claude Code, el **plan mode** sirve para el paso 1: Claude lee y explora el código, propone un plan y **no edita nada** hasta que lo aprobás. La documentación lo recomienda justamente para explorar un codebase antes de cambiarlo. (Los detalles de cómo se activa los vemos en 3C.)

### Ejemplo

El módulo de pagos de TiendaX tiene ocho años y casi no tiene tests. La gerencia pide: "Que Claude agregue tests completos al módulo de pagos".

**Mal (pipeline fijo).** Lucas arma: "Paso 1, listar las clases. Paso 2, escribir tests para cada clase en orden alfabético. Paso 3, correr los tests". A la tercera clase, el plan se rompe: `RefundProcessor` depende de un **cliente HTTP estático** imposible de simular en un test. Los tests no compilan, y el pipeline sigue con la clase siguiente como si nada.

**Bien (descomposición dinámica).** El agente sigue los tres pasos:
1. **Mapear:** arranca en plan mode y arma un mapa de las clases y sus dependencias.
2. **Priorizar por impacto:** el cálculo de reembolsos y la conciliación de pagos **mueven plata**, así que van primero. El formateo de recibos puede esperar.
3. **Plan que se adapta:** cuando aparece el cliente HTTP estático, el plan **agrega una subtarea nueva** ("introducir una interfaz para poder simularlo") antes de seguir con los tests de `RefundProcessor`.

### Para el examen

- Tarea abierta → **mapear → priorizar por impacto → plan priorizado que se adapta**. El orden importa: primero el mapa.
- Distractores típicos: un orden fijo (alfabético, por carpeta) que no reacciona; o empezar a escribir tests directamente sin mapear.
- Plan mode = explorar y proponer sin editar; encaja con "mapear primero".

### Cómo se une

Es la descomposición dinámica del Tema 8 en acción. Pero partir sobre la marcha tiene su propio riesgo: partir mal. El Tema 10 muestra el error más común.

---

## Tema 10 — Too-narrow decomposition (descomposición demasiado estrecha): huecos de cobertura

### Qué es

En un sistema con un **coordinator** (coordinador, también llamado *orchestrator*: el agente que parte el objetivo, asigna las subtareas y sintetiza el resultado) y varios **subagents** (subagentes: agentes que el coordinador lanza para resolver cada subtarea; los vemos a fondo en 1C), la descomposición la hace el coordinador. Si la hace **demasiado estrecha**, las subtareas no cubren todo el tema, y el resultado final tiene **huecos de cobertura**, aunque cada subagente haya hecho bien su parte.

La regla para diagnosticar sale de ahí: si **cada subagente cumplió lo que se le asignó** y aun así falta algo, el error está en **lo que se les asignó**, es decir, en la descomposición del coordinador. No en los agentes de abajo, que hicieron exactamente lo que se les pidió.

Anthropic cuenta un caso real parecido en su sistema de investigación multi-agente. Con instrucciones vagas ("investigá la escasez de semiconductores"), un subagente investigó la crisis de chips automotrices de 2021, mientras otros dos **duplicaban** el mismo trabajo sobre las cadenas de suministro actuales. Su conclusión: cada subagente necesita **un objetivo, un formato de salida, una guía de qué tools y fuentes usar, y límites claros** de su tarea. Son las propiedades de una buena subtarea del Tema 2, vistas desde el que delega.

### Ejemplo

El equipo de marketing de TiendaX pidió un informe sobre "políticas de devolución de la competencia", hecho por un sistema de investigación con un coordinador y tres subagentes: uno que **busca** fuentes, uno que las **filtra** y uno que **sintetiza** el informe.

El coordinador partió el tema en tres subtareas, **las tres sobre tiendas de zapatillas**. El informe salió prolijo y completo… pero solo sobre zapatillas. No había nada de ropa ni de electrónica.

Cada subagente hizo bien lo que le asignaron. **El error estuvo en la descomposición**, que fue demasiado estrecha. La corrección: que el coordinador parta el tema cubriendo **todo el alcance** (zapatillas, ropa, electrónica…), con subtareas que tengan límites claros.

Fijate el contraste con el Tema 9: el plan de Lucas fue **rígido**; el de marketing fue flexible, pero **demasiado corto**.

### La pregunta oficial de muestra

La guía tiene esta pregunta (escenario *Multi-Agent Research System*): una investigación sobre "AI in creative industries"; el coordinador partió el tema en tres subtareas de **artes visuales**, y el informe final cubre solo artes visuales, sin música, escritura ni cine. ¿Cuál es la causa raíz?
- **✅** La descomposición del coordinador es **demasiado estrecha**, y las asignaciones de los subagentes no cubren todos los dominios del tema.
- ❌ El agente de síntesis no tiene instrucciones para detectar huecos de cobertura.
- ❌ Las búsquedas del agente de búsqueda no son lo bastante amplias.
- ❌ El agente que analiza documentos filtra las fuentes que no son visuales.

La explicación oficial: los logs del coordinador muestran la causa; **los subagentes ejecutaron correctamente, el problema es lo que se les asignó**. Las otras opciones culpan a agentes de abajo que funcionaron como estaban diseñados.

### Para el examen

- Informe con huecos + cada subagente cumplió → **la causa es la descomposición del coordinador**.
- Subagentes que duplican trabajo o se van de tema → **instrucciones de subtarea vagas**: falta objetivo, formato, fuentes o límites.
- No culpes al último agente que tocó el resultado (el de síntesis) solo porque el hueco se ve ahí.

### Cómo se une

Con este tema se cierra lo que la guía evalúa en 1.6. La Parte 4 trae lo que el curso agrega: cómo cuidar un plan dinámico mientras corre.

---

# Parte 4 — Planes que cambian y objetivos poco claros

> 📘 **Curso.** La guía **no** menciona en 1.6 el replanning, el goal drift ni el manejo de ambigüedad. Es contenido del curso, coherente con la documentación. Sirve para razonar escenarios, y hay un matiz con 1.1 que sí puede salir (el tope de iteraciones; ver Tema 11).

## Tema 11 — Replanning and goal drift (replanificar y la deriva del objetivo)

### Qué es

Un plan dinámico (Tema 8) no se escribe una vez y listo: se corrige mientras corre. **Replanning** (replanificación) es revisar el plan actual cuando un paso falla, una tool devuelve algo inesperado o cambió el entorno. Sin replanning, el agente seguiría ejecutando un plan que ya no sirve.

El curso da **cuatro replanning triggers** (disparadores de replanificación), es decir, las señales de que el plan quedó desactualizado:
- **Tool call failure** (falla de una tool): devuelve error, timeout o un resultado vacío que el plan no esperaba.
- **Unexpected output** (salida inesperada): un paso devuelve algo válido, pero que **contradice lo que el paso siguiente suponía**.
- **State change** (cambio de estado): el entorno cambió durante la ejecución y pasos anteriores del plan ya no valen.
- **Constraint violation** (violación de restricción): la próxima acción violaría una restricción del objetivo o un límite de seguridad.

(Detalle: la slide de resumen, p. 107, lista solo tres y se olvida de *constraint violation*. Son cuatro.)

Pero **no toda sorpresa merece replanificar**: replanificar cuesta, y hacerlo por cualquier cosa vuelve al agente inestable. El curso da una decisión en tres preguntas. Si se cayó una **suposición central** (*core assumption*) del plan, se replanifica. Si el objetivo **ya no es alcanzable** por este camino, también se replanifica. Si la desviación es **chica y recuperable**, se sigue con el plan.

El riesgo de replanificar sin control se llama **goal drift** (deriva del objetivo): cada replan se aleja un poco del objetivo original, hasta que el agente termina haciendo otra cosa. El curso lo llama "un modo de falla peligroso", porque cada paso por separado parece razonable. Pide dos defensas:
- **Maximum iterations** (máximo de iteraciones): un tope duro de ciclos de replanificación.
- **Goal constraint check** (chequeo contra el objetivo): cada plan nuevo se compara contra el **objetivo original**, no contra el plan anterior. Si ya no lo cumple, se **escala** a un humano.

> ⚠️ **En el curso vas a escuchar otra cosa.** Jacob pide acotar el replanning con un máximo de iteraciones como defensa. **Para el examen:** en la tarea 1.1, la guía marca como anti-pattern **usar un tope arbitrario de iteraciones como mecanismo principal** para terminar. No es una contradicción de fondo, porque "Building effective agents" sí acepta un máximo de iteraciones como **condición de corte para mantener el control**: el tope es una **red de seguridad**, y lo que de verdad evita el drift es el **chequeo contra el objetivo**. Es la misma idea del turn budget de 1A.

### Ejemplo

Mientras agrega tests (Tema 9), el agente descubre que la pasarela de pagos que usa `RefundProcessor` está **deprecada**. Replanifica: "Primero migro a la pasarela nueva". Después descubre que la migración rompe la conciliación, y vuelve a replanificar: "Primero arreglo la conciliación". Al cuarto replan, el agente está **reescribiendo el módulo de conciliación**. Nadie le pidió eso. El objetivo era **agregar tests**.

Cada replan, mirado solo, parecía razonable: cada uno se parecía al anterior. Pero el último ya no se parecía al objetivo. Por eso el chequeo se hace **contra el objetivo original**.

Con las defensas, la historia cambia en dos pasos. Primero, el agente se da cuenta de que "migrar la pasarela" no es "agregar tests". Después, escala: "Para testear `RefundProcessor` hace falta migrar la pasarela, que está deprecada. ¿Lo hago o sigo con las otras clases?".

### Cómo se configura

📘 **Curso:** detectar si hace falta replanificar (los cuatro triggers):

```python
def needs_replan(result, plan, env, next_action) -> bool:
    if result.get("is_error") or not result.get("content"):
        return True                      # tool call failure
    if not plan.assumption_holds(result):
        return True                      # unexpected output
    if env.version != plan.env_version:
        return True                      # state change
    return violates_constraints(next_action)  # constraint violation
```

Replanificar con límites:

```python
MAX_REPLANS = 3
plan = make_plan(goal)
for attempt in range(MAX_REPLANS + 1):
    outcome = execute(plan)
    if outcome.ok:
        break
    plan = replan(goal, plan, outcome)
    if not satisfies_goal(plan, goal):      # ¿el plan nuevo sigue cumpliendo el objetivo ORIGINAL?
        escalate("revised plan abandons the goal")
        break
```

`MAX_REPLANS` es el tope de ciclos: con `range(MAX_REPLANS + 1)` hay hasta **cuatro ejecuciones**, la original más tres replans. `satisfies_goal` compara cada plan nuevo con `goal` (el objetivo original), **no** con el plan anterior, antes de ejecutarlo. Si el plan nuevo ya no cumple el objetivo, `escalate` lo pasa a un humano.

### Para el examen

- Se replanifica cuando se cae una suposición central o el objetivo deja de ser alcanzable; si la desviación es chica, se sigue.
- Replan acotado = **tope** (red de seguridad) + **chequeo contra el objetivo original** + **escalar** si se desvía.
- Un tope de iteraciones **no** es el mecanismo principal de terminación (anti-pattern de 1.1).
- ❌ "Comparar con el plan anterior": el drift es acumulativo y pasa desapercibido.

### Cómo se une

El tope y la escalada ya los viste en 1A (turn budget y escalar cuando gira en falso). Acá se aplican al plan, no a los turnos.

---

## Tema 12 — Handling ambiguity (manejar la ambigüedad): clarificar o asumir

### Qué es

Un **ambiguous goal** (objetivo ambiguo) es un pedido que no define del todo el resultado esperado: deja varias interpretaciones válidas. Frente a eso, el agente tiene que elegir entre dos estrategias, y ninguna sirve siempre:
- **Clarify-first** (clarificar primero): frenar y pedirle información a un humano antes de seguir.
- **Assume-and-proceed** (asumir y seguir): hacer una inferencia razonable y continuar sin preguntar.

El criterio del curso depende de **cuánto cuesta equivocarse**. Hay que **clarificar antes de actuar** cuando la acción es **irreversible** (borrar, enviar, confirmar algo externo), **cara** (llamadas costosas a la API, procesos largos en lote) o de **alcance incierto** (el agente no sabe qué entra y qué no, y podría trabajar sobre los datos equivocados). En esos casos, un error no se arregla fácil. En cambio, conviene **asumir y seguir** cuando la acción es de **bajo riesgo** y **reversible**, y el contexto deja clara la interpretación correcta: preguntar todo vuelve al agente lento y molesto.

> ⚠️ **En el curso vas a escuchar otra cosa.** En algunas slides (p. 109, 111 y 112), "asumir y seguir" vale si la tarea es de bajo riesgo, reversible **o** urgente (*time-sensitive*). El diagrama de decisión de la p. 113 exige que sea reversible **y** de bajo riesgo **y** con alcance claro, y no menciona la urgencia. **Para el examen:** quedate con el **criterio fuerte**: si algo es irreversible, caro o de alcance incierto, se clarifica, **aunque sea urgente**.

Cuando el agente asume, **lo deja escrito**, por ejemplo con un campo `assumptions` en su salida. Esto tiene tres ventajas: un humano puede **revisar la suposición** sin volver a correr todo; si estaba mal, se **reejecuta solo el paso afectado**; y queda un registro de auditoría.

El curso cierra la lección con el patrón **evaluator-optimizer** de 1A, aplicado a refinar un resultado. Funciona como un ciclo de corrección:
- un **generator** (generador) produce la salida;
- un **evaluator** (evaluador) la puntúa contra una **rúbrica** y devuelve una crítica;
- se repite hasta un **criterio de convergencia**: llegar a una nota mínima de calidad **o** a un tope de iteraciones.

En el ejemplo de las slides, el generador y el evaluador son **modelos distintos**.

Anthropic recomienda evaluator-optimizer cuando hay **criterios de evaluación claros**. El porqué: sin una rúbrica clara, el evaluador no tiene contra qué medir.

### Ejemplo

**Preguntar.** Para el cambio de dirección, Martín escribió: "Mandalo a la dirección de mi oficina". SoporteBot no la tiene. Despachar el TX-104300 a una dirección adivinada es **caro y difícil de deshacer**, así que pregunta. (Por eso `new_address` estaba en `null` en el Tema 2.)

**Asumir y documentar.** Si Martín pregunta "¿cuándo llega?" sin decir de qué pedido, y tiene **un solo pedido en camino**, SoporteBot asume ese, responde, y lo deja escrito:

```json
{
  "answer": "Tu pedido TX-104300 llega el jueves.",
  "assumptions": ["El cliente se refiere al TX-104300, su único pedido en camino"]
}
```

### Cómo se configura

📘 **Curso:** forzar la pregunta en código, antes de las tools riesgosas:

```python
IRREVERSIBLE = {"delete_records", "send_email", "git_push"}
EXPENSIVE = {"bulk_reindex"}

def before_tool(call):
    if call.name in IRREVERSIBLE | EXPENSIVE:
        if ask_human(f"Confirm {call.name} with {call.input}?") != "yes":
            return {"type": "tool_result", "tool_use_id": call.id,
                    "content": "User declined. Ask what they intended.",
                    "is_error": True}
    return None   # se puede seguir
```

Tres cosas para notar. Si el humano dice que no, se devuelve **igual** un `tool_result` con `is_error: True` y un mensaje que le dice a Claude qué hacer, porque es la regla de 1A: **todo `tool_use` recibe su `tool_result`**. Este guard cubre lo **irreversible o caro**; el **alcance incierto** no se detecta por el nombre de la tool, así que ahí la decisión de preguntar queda en el diseño del agente. Y interceptar tools con código antes de ejecutarlas es el tema central de 1D.

El loop evaluator-optimizer, en su forma mínima:

```python
draft, feedback = None, ""
for i in range(3):                                   # tope de iteraciones
    draft = generate(f"Write the summary.\n{feedback}\nPrevious: {draft}")
    score, feedback = evaluate(draft, RUBRIC)        # nota contra una rúbrica + crítica
    if score >= 8:                                   # nota mínima de calidad
        break
```

### Para el examen

- **Clarificar** si es irreversible, caro o de alcance incierto. **Asumir** si es de bajo riesgo y reversible, y **documentar** lo asumido.
- Ni "preguntar siempre" (lento y molesto) ni "nunca preguntar" (acciones irreversibles a ciegas).
- Si el humano rechaza en el guard, igual va un `tool_result` con `is_error: true`.
- Evaluator-optimizer necesita **criterios claros**; termina por nota mínima o por tope.

### Cómo se une

Cierra el círculo con el Tema 2: el `null` en `new_address` era una ambigüedad documentada en el handoff, y acá se decide qué hacer con ella.

---

## Cómo se une todo

1. Un objetivo compuesto se **parte en subtareas** antes de actuar; si no, falla todo junto y no se puede reintentar por partes (Tema 1).
2. Cada subtarea hace **una cosa**, con **entradas explícitas**, **reintentable sola** y con **salida estructurada**; los **handoffs** son interfaces con esquema (Tema 2).
3. Partir cuesta: se corta **donde cambia la responsabilidad**, sin quedarse corto ni pasarse (Tema 3).
4. Lo que tiene **dependencia real** va en secuencia (**prompt chaining**, con validación en cada frontera) (Tema 4); el **grafo de dependencias** muestra qué es real y qué es costumbre (Tema 5); lo **independiente** va en paralelo, y una rama caída **nunca se descarta en silencio** (Tema 6).
5. Si mucho material **entra pero sale desparejo**, es **attention dilution**: pasada local por archivo + pasada de integración (Tema 7).
6. **Pasos conocidos → prompt chaining; alcance desconocido → descomposición dinámica** (Tema 8). Para una tarea abierta: **mapear, priorizar por impacto, plan que se adapta** (Tema 9).
7. Si todos los subagentes cumplieron y falta algo, la descomposición del coordinador fue **demasiado estrecha** (Tema 10).
8. Un plan dinámico se **replanifica con límites** y se chequea contra el **objetivo original** (Tema 11), y ante la ambigüedad se **pregunta cuando equivocarse sale caro** y se **documenta lo que se asume** (Tema 12).

## Lo que viene

Todo lo de este capítulo lo hizo **un solo agente** que se partía el trabajo a sí mismo. Funciona, pero se nota el peso: para el mensaje de Martín, el context window de SoporteBot carga los datos de pagos, los de logística y los de productos al mismo tiempo; el agente de tests carga el mapa entero del módulo de pagos mientras escribe un test chiquito.

La propuesta lógica es que cada subtarea la resuelva **otro agente**, especializado, con sus propias tools: un coordinador que reparte y agentes que ejecutan. Pero en el primer prototipo, el agente de reembolsos recibe "reembolsar el cobro duplicado" y lo primero que hace es preguntarle a Martín: "¿Cuál es tu número de pedido?". Martín ya lo había dicho. El coordinador lo sabía. El agente de reembolsos, no. ¿Qué ve un subagent, qué hay que pasarle y quién decide cuándo lanzarlo? Eso es **1C · Multi-Agent Orchestration**.

---

## Las trampas del examen

Cada trampa tiene el mismo orden: la situación, **qué elegir en el examen (✅)**, las opciones que tientan (❌) con por qué tientan y por qué están mal, y una regla para recordar.

### Grupo: Elegir la estrategia (lo que evalúa la guía)

#### Trampa 1 · La revisión de un PR grande sale despareja

**La situación.** La revisión automática de un PR de 14 archivos comenta en detalle los primeros, casi nada los últimos, deja pasar un bug y se contradice (Tema 7).

**✅ En el examen elegí:** partir la revisión en **una pasada local por archivo** más **una pasada de integración separada** que mira el flujo de datos entre archivos. La causa es la **attention dilution**, y se ataca cambiando la estructura de la tarea.

**❌ Las que tientan:**

❌ **"Usar un modelo más grande, con más context window".**
- *Tienta porque:* el síntoma parece de capacidad: "no le alcanza para todo".
- *Está mal porque:* los archivos ya entraban. Tener más espacio no cambia cómo se reparte la atención.

❌ **"Correr tres pasadas completas y marcar solo lo que aparezca en al menos dos".**
- *Tienta porque:* suena robusto, parece que filtra falsos positivos.
- *Está mal porque:* tira bugs reales que encontró una sola pasada, y cada pasada completa sigue diluida.

❌ **"Pedirles a los desarrolladores PRs de 3 o 4 archivos".**
- *Tienta porque:* el síntoma desaparece sin tocar el sistema.
- *Está mal porque:* le pasa a la gente un problema de arquitectura, y los cambios entre archivos siguen necesitando una mirada de integración.

❌ **"Revisar en lotes de 5 archivos".**
- *Tienta porque:* baja la dilución dentro de cada lote y parece una descomposición.
- *Está mal porque:* nadie mira lo que pasa entre archivos de lotes distintos. Falta la pasada de integración.

❌ **"Agregar al prompt: 'revisá todos los archivos con la misma profundidad'".**
- *Tienta porque:* es un cambio de una línea que va directo al síntoma.
- *Está mal porque:* una instrucción no cambia la estructura que causa la dilución.

> 🧠 **Para recordar:** si entra pero sale desparejo, partí la tarea: por archivo y después integración.

#### Trampa 2 · Al informe le falta cobertura y cada agente hizo su parte

**La situación.** El informe de marketing sobre devoluciones de la competencia solo habla de zapatillas. Los subagentes de búsqueda, filtrado y síntesis hicieron bien lo que les asignaron (Tema 10).

**✅ En el examen elegí:** la causa es la **descomposición del coordinador**, que fue demasiado estrecha. Se corrige cómo el coordinador parte el tema para que cubra todo el alcance.

**❌ Las que tientan:**

❌ **"El agente de síntesis no detecta los huecos" / "las búsquedas no son amplias" / "el filtro descarta fuentes".**
- *Tienta porque:* el hueco se ve en el resultado final, y lo natural es culpar al último agente que lo tocó.
- *Está mal porque:* esos agentes cumplieron con lo que se les asignó. El problema fue lo que recibieron.

> 🧠 **Para recordar:** si todos cumplieron y falta algo, el error está en el reparto.

#### Trampa 3 · ¿Pipeline fijo o descomposición dinámica?

**La situación.** Hay dos tareas: revisar PRs (siempre los mismos pasos) y agregar tests a un módulo legacy (no se sabe qué se va a encontrar) (Temas 7, 8 y 9).

**✅ En el examen elegí:** **prompt chaining** (pipeline fijo) para las tareas **predecibles** de varios aspectos, como la revisión. **Descomposición dinámica** para las tareas **abiertas**, como los tests del legacy: primero mapear la estructura, después identificar las áreas de alto impacto y armar un plan priorizado que se adapta cuando aparecen dependencias.

**❌ Las que tientan:**

❌ **"Descomposición dinámica para todo, que es más inteligente".**
- *Tienta porque:* suena más flexible y moderna.
- *Está mal porque:* en una tarea predecible solo agrega costo, la vuelve menos auditable y más difícil de depurar.

❌ **"Un pipeline fijo para la tarea abierta"** (por ejemplo, "tests a cada clase en orden alfabético").
- *Tienta porque:* es simple y predecible.
- *Está mal porque:* no reacciona a lo que descubre. Sigue de largo cuando aparece una dependencia que rompe el plan.

> 🧠 **Para recordar:** si sabés los pasos, encadenalos; si los vas a descubrir, planificá en el camino.

### Grupo: Ordenar las subtareas

#### Trampa 4 · Ramas en paralelo

**La situación.** SoporteBot corre en paralelo las subtareas de Martín (Tema 6).

**✅ En el examen elegí:** paralelizar solo lo que pasa el **test de independencia**: ninguna rama necesita la salida de otra, no escriben el mismo estado y el resultado no depende del orden. En el fan-in hay que tener una **política explícita** para las ramas que fallan: abortar, seguir con resultado parcial marcando qué falló, o reintentar solo esa rama.

**❌ Las que tientan:**

❌ **"Correr en paralelo dos cambios sobre el mismo pedido".**
- *Tienta porque:* son dos pedidos del cliente y en paralelo se tarda menos.
- *Está mal porque:* las dos ramas escriben el mismo estado. Es false parallelism, con riesgo de data hazard.

❌ **"Responder con las ramas que salieron bien y no mencionar la que falló".**
- *Tienta porque:* la respuesta queda limpia y "casi todo" se resolvió.
- *Está mal porque:* el cliente cree que todo se hizo. Una rama caída nunca se descarta en silencio.

> 🧠 **Para recordar:** paralelo solo si no comparten nada que se escriba; una rama caída se informa.

### Grupo: Planes que cambian y objetivos poco claros

#### Trampa 5 · El plan que se fue desviando

**La situación.** El agente de tests replanificó cuatro veces y terminó reescribiendo la conciliación, que nadie le pidió (Tema 11).

**✅ En el examen elegí:** un **tope de replans** como red de seguridad, un **chequeo de cada plan nuevo contra el objetivo original** (para detectar el goal drift) y **escalar** a un humano si el plan nuevo ya no cumple el objetivo.

**❌ Las que tientan:**

❌ **"Dejarlo replanificar todas las veces que haga falta" o "subirle el tope".**
- *Tienta porque:* cada replan, mirado solo, parece razonable.
- *Está mal porque:* sin el chequeo contra el objetivo, el plan se va desviando de a poco.

❌ **"Comparar cada plan nuevo con el plan anterior".**
- *Tienta porque:* parece un control de cambios razonable.
- *Está mal porque:* el drift es acumulativo. Cada paso se parece al anterior, pero el último ya no se parece al objetivo.

> 🧠 **Para recordar:** cada plan nuevo se compara con el objetivo, no con el plan anterior.

#### Trampa 6 · ¿Preguntar o asumir?

**La situación.** Martín pide mandar el pedido "a la dirección de mi oficina", y SoporteBot no sabe cuál es (Tema 12).

**✅ En el examen elegí:** **clarificar antes** si la acción es **irreversible**, **cara** o de **alcance incierto**. **Asumir y seguir** si es de bajo riesgo y reversible, y **dejar documentado** lo que se asumió (por ejemplo, en un campo `assumptions`).

**❌ Las que tientan:**

❌ **"Preguntar siempre que haya ambigüedad".**
- *Tienta porque:* parece lo más seguro.
- *Está mal porque:* el agente se vuelve lento y molesto, y no aporta nada en las tareas reversibles de bajo riesgo.

❌ **"No preguntar nunca, para no molestar al cliente".**
- *Tienta porque:* la experiencia es más fluida.
- *Está mal porque:* termina haciendo acciones irreversibles a ciegas, como despachar a una dirección adivinada.

❌ **"Asumir y no dejarlo escrito".**
- *Tienta porque:* la respuesta queda más limpia.
- *Está mal porque:* nadie puede revisar la suposición sin volver a correr todo.

> 🧠 **Para recordar:** preguntá cuando equivocarse sale caro; si no, asumí y dejalo escrito.

### Grupo: Partir el trabajo

#### Trampa 7 · Partir de más o de menos

**La situación.** Primero SoporteBot trató el mensaje de Martín como un solo problema. Después Lucas partió el cambio de dirección en doce pasos (Temas 1, 2 y 3).

**✅ En el examen elegí:** subtareas con **una sola responsabilidad**, entradas definidas, alcance chico como para reintentarlas solas y salida estructurada. Bajar un nivel solo si las subtareas necesitan capacidades **fundamentalmente distintas**.

**❌ Las que tientan:**

❌ **"Una sola tarea grande, y una instrucción en el prompt para que resuelva todo".**
- *Tienta porque:* es simple.
- *Está mal porque:* si falla una parte falla todo, y no se puede reintentar solo lo que se rompió (under-decomposition).

❌ **"Partir todo lo más posible, que es más prolijo".**
- *Tienta porque:* cada paso queda chico y fácil de entender.
- *Está mal porque:* cada frontera cuesta llamadas, tokens, latencia y posibles fallas en el handoff (over-decomposition).

> 🧠 **Para recordar:** partí donde cambia la responsabilidad, no donde podés.

---

## Checklist oficial

**Tarea 1.6 — Design task decomposition strategies for complex workflows**

*Knowledge of*
- [x] Cuándo usar pipelines secuenciales fijos (prompt chaining) y cuándo descomposición dinámica y adaptativa basada en hallazgos intermedios → **Tema 8** (y Temas 4 y 9; Trampa 3)
- [x] Patrones de prompt chaining que parten las revisiones en pasos secuenciales (analizar cada archivo por separado y después una pasada de integración entre archivos) → **Tema 7** (y Tema 4)
- [x] El valor de los planes de investigación adaptativos que generan subtareas según lo que se descubre en cada paso → **Temas 8 y 9** (y Tema 10)

*Skills in*
- [x] Elegir el patrón de descomposición adecuado: prompt chaining para revisiones predecibles de varios aspectos, descomposición dinámica para investigaciones abiertas → **Tema 8** (Trampa 3)
- [x] Partir revisiones de código grandes en pasadas locales por archivo más una pasada separada de integración entre archivos, para evitar la attention dilution → **Tema 7** (Trampa 1)
- [x] Descomponer tareas abiertas (por ejemplo, "agregar tests completos a un legacy codebase") mapeando primero la estructura, identificando las áreas de alto impacto y armando un plan priorizado que se adapta a medida que aparecen dependencias → **Tema 9** (Trampa 3)

**De la documentación, no de la guía** (vale saberlo; la guía no lo pregunta directo): la solución más simple posible (Tema 3) · gates y chaining para inspeccionar salidas intermedias (Tema 4) · sectioning vs. voting y los números del sistema de investigación: 3–5 subagentes, hasta 90% menos tiempo, unas 15 veces más tokens (Tema 6) · orchestrator-workers como herramienta de la descomposición dinámica (Tema 8) · plan mode para explorar antes de cambiar (Tema 9) · objetivo, formato, fuentes y límites de cada subagente (Temas 2 y 10) · evaluator-optimizer con criterios claros (Tema 12).

**📘 Curso (útil para entender; lecciones 7–12):** las tres preguntas para analizar un objetivo, monolítico vs. descompuesto, el espectro de descomponibilidad (Tema 1) · las cuatro propiedades de una buena subtarea, handoff points con esquema explícito y lo que no se pasa documentado (Tema 2) · los cinco costos de partir, over-decomposition, under-decomposition, descomposición jerárquica y cuándo profundizar o aplanar (Tema 3) · los cuatro motivos para ir en secuencia, error cascade y validación en las fronteras (Tema 4) · dependency graph, puntos de sincronización, dependencias reales vs. artificiales (Tema 5) · fan-out, fan-in y sus cuatro responsabilidades, sectioning vs. voting, test de independencia, false parallelism y data hazard, fallas parciales, estrategias de combinación, costo del paralelo, combinación de patrones (Tema 6) · plan estático vs. dinámico (Tema 8) · error de cobertura por descomposición demasiado estrecha (Tema 10) · los cuatro triggers de replanning, replanificar vs. seguir, tope de replans, chequeo contra el objetivo y goal drift (Tema 11) · clarificar vs. asumir, guard antes de tools riesgosas, documentar supuestos, evaluator-optimizer acotado (Tema 12).

---

## Autoevaluación oral

1. Martín manda tres problemas en un mensaje. ¿Qué tres preguntas te hacés antes de partirlo, y qué hace que cada subtarea esté bien definida?
2. ¿Qué es la attention dilution? ¿Por qué no la resuelve un modelo más grande, y cuál es la arquitectura correcta para revisar un PR de 14 archivos?
3. ¿Cuándo elegís prompt chaining y cuándo descomposición dinámica? Dame un ejemplo de TiendaX para cada una, y los tres pasos para agregar tests a un legacy codebase.
4. ¿Qué es el false parallelism? ¿Qué test hacés antes de un fan-out y qué tiene que hacer el fan-in si una rama falla?
5. Un agente replanificó cuatro veces y ahora hace algo que nadie pidió. ¿Qué le faltaba? ¿Y cuándo debería preguntar antes de actuar?

---

## Preguntas tipo examen

Las preguntas tipo examen de este capítulo están en [`04-practica/modulo-1.md`](../04-practica/modulo-1.md), junto con las del resto del módulo 1. Hacelas cuando termines **todos** los capítulos del módulo, de a una y sin mirar la respuesta.

---

## Revisión contra el blueprint oficial

Qué puede salir en el examen sobre 1.6 que el curso de Jacob **no cubre o cubre flojo**, y dónde quedó explicado acá:

1. **Prompt chaining como estrategia de 1.6.** El companion del bloque 1B no lo nombra, y las slides solo lo definen al pasar (p. 81), sin conectarlo con la elección "fijo vs. dinámico". Para la guía es la mitad de la decisión central: pasos conocidos → prompt chaining. → Temas 4 y 8.
2. **Attention dilution.** El curso no la nombra en 1B. Es la causa raíz que la guía quiere que reconozcas: el material entra, pero el análisis sale desparejo. → Tema 7.
3. **Revisión por archivo + pasada de integración separada.** No aparece en el bloque 1B del curso. Es un *skill* literal de 1.6 y la respuesta fija a la pregunta del PR. → Tema 7.
4. **El ejemplo de los tests en un legacy codebase** (mapear → priorizar por impacto → plan que se adapta). No aparece en el bloque 1B. Es el tercer *skill* de 1.6. → Tema 9.
5. **La pregunta de muestra del PR de 14 archivos (Q12)**, con sus distractores (PRs chicos, modelo más grande, consenso 2 de 3) y el primo de la comunidad (lotes sin integración). → Tema 7 y Trampa 1.
6. **La pregunta de muestra de cobertura incompleta (Q7)**: la causa es la descomposición del coordinador, no los agentes de abajo. El curso no la trabaja con sus distractores. → Tema 10 y Trampa 2.
7. **Matiz del tope de iteraciones.** El curso pide acotar el replanning con un máximo; la guía (1.1) marca como anti-pattern usar el tope como mecanismo **principal**. Respuesta: el tope es red de seguridad; el control real es el chequeo contra el objetivo. → Tema 11.

Lo que el curso agrega por su cuenta (grafo de dependencias, fan-out/fan-in, replanning, ambigüedad) queda marcado como 📘: sirve para razonar, pero la guía no lo evalúa en 1.6 por nombre. No encontré otros huecos para esta tarea.

