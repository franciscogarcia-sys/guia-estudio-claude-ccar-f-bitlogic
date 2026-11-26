# Capítulo 17 · 5C · Udemy 18 — Context Efficiency for Large Codebases (el contexto al explorar codebases grandes)

*Tarea oficial 5.4 · Tercer capítulo del módulo 5*

---

## Dónde estamos

Seguimos en el **módulo 5: Context Management & Reliability**. 5A y 5B ya están escritos. Este capítulo cubre una tarea, de 2,5%:
- **5.4** Manage context effectively in large codebase exploration (manejar bien el contexto al explorar un codebase grande).

### Cómo leer este capítulo

Todo lo que leés acá **vale para el examen**, salvo que diga lo contrario. Cuando algo sale solo del curso (útil para entender, pero no central), lo marco con **📘 Curso**. Cuando Jacob dice algo distinto de lo que evalúa la guía, aparece un recuadro así:

> ⚠️ **En el curso vas a escuchar otra cosa.** … **Para el examen: …**

### Un aviso sobre este capítulo

5A trataba de conversaciones largas con un cliente. Este trata de **sesiones largas de exploración de código** en Claude Code: entender un repo grande, rastrear un flujo, encontrar todos los tests. El curso explica bien el scratchpad y la delegación a subagentes. **Le faltan** el síntoma exacto que describe la guía, pasar un resumen entre fases, `/compact` por nombre y la recuperación después de un corte con **manifests**. Esos salen de la guía.

Varias piezas ya las viste: el **Explore subagent** y plan mode en 3A y 3C, y `--resume` frente a empezar una sesión nueva en 1C. Acá se juntan.

## De dónde venimos

En 5A viste que más contexto no es mejor y que los resúmenes pierden datos. En una exploración de código pasa lo mismo, pero con otra materia prima. Cada `Grep`, cada archivo leído y cada lista de resultados queda en el contexto. Después de una hora explorando, la sesión tiene miles de líneas de salida y lo importante se diluye.

## Mapa del capítulo

1. La degradación del contexto en sesiones largas.
2. Scratchpad files: guardar lo que encontraste.
3. Delegar la exploración a subagentes.
4. Pasar un resumen de una fase a la siguiente.
5. `/compact`, `/clear` o sesión nueva.
6. Recuperarse de un corte: manifests.
7. 📘 La memory tool y la coherencia en conversaciones largas (lección 114 y deck 139).

---

## Tema 1 — Context degradation (degradación del contexto) en sesiones largas

### Qué es

Cuando una sesión de exploración se alarga, el contexto se llena de salida verbosa: resultados de búsquedas, archivos leídos enteros, listas de rutas. Lo que Claude descubrió al principio queda enterrado bajo todo eso, y empieza a responder peor.

La guía describe el síntoma exacto, y el examen lo usa como pista:
- Claude da **respuestas inconsistentes** sobre cosas que ya había respondido bien.
- Habla de **"typical patterns"** (patrones típicos) en vez de las **clases específicas** que había encontrado.

Por ejemplo, en vez de decir "el reembolso pasa por `RefundService.process()` y `PaymentGateway.reverse()`", dice "normalmente estos sistemas tienen un servicio de reembolsos que llama al gateway de pago". Esa respuesta genérica es la señal: Claude ya no está usando lo que descubrió, está completando con conocimiento general.

La documentación lo llama **context rot**: a medida que crece la cantidad de tokens, la precisión cae, aunque la ventana tenga espacio de sobra. Por eso **agrandar la ventana no es la solución**.

### Para el examen

- "Respuestas inconsistentes" o "typical patterns en vez de las clases que ya encontró" → **degradación del contexto**.
- Distractores: modelo con más contexto, subir `max_tokens`, cargar toda la estructura del repo al principio (agrega más ruido).

### Cómo se une

Si lo descubierto se pierde en el contexto, hay que guardarlo afuera.

---

## Tema 2 — Scratchpad files (archivos de notas): guardar lo que encontraste

### Qué es

Un **scratchpad file** (archivo de notas de trabajo) es un archivo donde el agente **anota los hallazgos clave** a medida que explora: qué clases intervienen, en qué archivo y línea, qué decisiones se tomaron. El archivo vive **fuera del contexto**, así que no se degrada ni se pierde cuando la sesión se compacta o se reinicia.

La guía pide dos cosas: que el agente **mantenga** el archivo con los hallazgos clave y que lo **consulte para las preguntas siguientes**. Esto último es importante: un archivo que se escribe pero no se lee no sirve.

📘 Curso: Jacob da reglas de "higiene" para el scratchpad:
- Guardar **referencias** (`src/refunds/RefundService.ts:42`, nombres de clases, valores exactos), no copiar bloques de código, que se desactualizan.
- Mantenerlo corto y podarlo: un scratchpad desactualizado engaña más que no tener ninguno.
- No guardar credenciales ni datos sensibles: es un archivo del repo.
- Nombrarlo en el CLAUDE.md para que Claude lo lea al arrancar.
- Si el scratchpad y el CLAUDE.md dicen cosas distintas, manda CLAUDE.md.
- El bloque de "estado actual" se **reescribe** en cada sesión; no se le van agregando entradas.
- Las notas viejas en las que el agente confía sin revisar (el **graveyard**, el cementerio) se cortan verificando contra el código.

**Cómo se garantiza que se lea y se escriba.** Para la lectura, Jacob propone nombrarlo en el CLAUDE.md o cargarlo con un hook `SessionStart` (que inyecta su contenido al arrancar). Para la escritura, conviene pedir que se actualice **antes de cerrar cada sesión**, porque si no, la próxima arranca con notas viejas. Un hook `SessionEnd` no puede frenar el cierre, así que esa parte depende de la instrucción.

### Cómo se configura

`notes/refund-exploration.md`:

```markdown
# Exploración: flujo de reembolsos (actualizado 24/11)

## Hallazgos
- Entrada: `src/api/refunds.ts:18` → `RefundService.process()` (`src/refunds/RefundService.ts:42`)
- El monto se valida en `RefundPolicy.check()`: tope de USD 500 sin aprobación.
- `PaymentGateway.reverse()` usa `priceCents` (centavos de peso), no pesos enteros.

## Pendiente
- ¿Quién llama a `RefundService.process()` desde los jobs nocturnos?
```

### Ejemplo

Sofía explora el flujo de reembolsos con Claude Code durante dos horas. A la hora y media, Claude empieza a hablar de "un servicio de reembolsos típico". Con el scratchpad, cada vez que Sofía pregunta algo nuevo, Claude lee primero `notes/refund-exploration.md` y responde con las clases y archivos concretos que ya había encontrado.

### Para el examen

- Degradación en una sesión larga → **scratchpad file con los hallazgos clave, que se consulta antes de cada pregunta nueva**.
- Distractores: escribirlo y no leerlo, o confiar en que Claude "se acuerde".

### Cómo se une

El scratchpad protege lo que ya se descubrió. Para que el contexto no se llene en primer lugar, la exploración pesada se delega.

---

## Tema 3 — Subagent delegation (delegar la exploración a subagentes)

### Qué es

Ya viste en 3C el **Explore subagent**: un subagente de solo lectura que Claude Code usa para explorar. La idea es la misma que en 1C. El subagente trabaja en **su propio contexto**, hace todas las búsquedas y lecturas que necesite, y le devuelve al agente principal **solo un resumen**. Toda la salida verbosa queda en el contexto del subagente, que se descarta al terminar.

La guía pide **lanzar subagentes para preguntas específicas** ("encontrá todos los archivos de test", "rastreá las dependencias del flujo de reembolsos"), mientras el agente principal **conserva la coordinación de alto nivel**: entiende el panorama general, decide qué preguntar después y no se llena de detalles.

Tres reglas prácticas:
- **Pregunta concreta**, con alcance y con la forma de la respuesta ("devolvé una lista de rutas con una línea de descripción cada una").
- **Herramientas de solo lectura** (Read, Grep, Glob): explorar no necesita escribir.
- **No delegar lo chico.** Un subagente arranca de cero. Para buscar una función puntual justo antes de editarla, un `Grep` directo es más rápido.

📘 Curso: Jacob arma el prompt del subagente con cuatro partes: **QUESTION** (la pregunta), **SCOPE** (dónde buscar y qué saltear), **RETURN** (la forma y el largo máximo de la respuesta) y **STOP** (cuándo cortar: "si después de revisar 30 archivos no lo encontrás, devolvé tu mejor respuesta y marcá la confianza como baja"). Sin eso aparecen dos fallas: el **wall of text** (devuelve páginas en vez de un resumen) y el **scope creep** (se pone a explorar de más).

**Lo que devuelve el subagente es una hipótesis.** El agente principal no ve cómo llegó a esa conclusión. Si la decisión que se va a tomar es crítica (borrar código, cambiar un flujo de pagos), conviene verificar el hallazgo con una lectura puntual antes de actuar. Para consultas de bajo riesgo no hace falta. El curso llama **blind trust** (confianza ciega) a actuar sin verificar.

> ⚠️ **En la documentación actual vas a leer otra cosa.** Las best practices actuales de Claude Code ponen como consejo "viejo" eso de "usá subagentes para proteger la ventana de contexto": con ventanas de 1M y compactación automática, quedarse sin contexto ya no suele ser el problema. **Para el examen:** respondé con la guía. Para una exploración verbosa en un codebase grande, la respuesta es **delegar a un subagente** (o Explore) que devuelva un resumen.

### Ejemplo

Sofía necesita saber qué tests cubren el flujo de reembolsos antes de refactorizarlo. En vez de pedirle al agente principal que busque (devolvería 300 rutas y leería decenas de archivos), Claude Code lanza un subagente con la consigna: "Encontrá todos los tests que ejercitan `RefundService`. Devolvé una lista de rutas con el caso que prueba cada uno. Solo lectura". El agente principal recibe 14 líneas y sigue con el plan.

### Para el examen

- Exploración verbosa (todos los tests, todas las dependencias de un flujo) → **subagente con una pregunta específica que devuelve un resumen**.
- El agente principal **coordina**; no hace la búsqueda pesada.
- Lookup puntual y chico → directo, sin subagente.
- Distractores: hacer la búsqueda enorme en el agente principal y compactar después, darle al subagente permisos de escritura, o usar subagentes "para ir más rápido" cuando el motivo real es aislar la salida verbosa.

### Cómo se une

Una exploración grande suele tener varias fases. Lo que descubrió una fase tiene que llegar a la siguiente.

---

## Tema 4 — Pasar un resumen de una fase a la siguiente

### Qué es

Los subagentes **no heredan la conversación** (salvo que se lancen como fork, que copia la del padre): arrancan con el contexto que vos les das. Si la fase 2 de la exploración lanza subagentes nuevos, no saben nada de lo que encontró la fase 1.

La guía pide **resumir los hallazgos clave de una fase antes de lanzar los subagentes de la siguiente**, e **inyectar ese resumen en su contexto inicial** (en su prompt). Así arrancan sabiendo lo importante, sin cargar toda la salida de la fase anterior.

Hay dos errores opuestos:
- **No pasar nada.** Los subagentes nuevos vuelven a descubrir lo mismo o contradicen lo anterior.
- **Pasar todo**: los reportes completos de la fase 1 o el transcript entero. Vuelve a llenar el contexto con ruido.

### Ejemplo

Fase 1: tres subagentes mapean el módulo de pagos, el de pedidos y el de reembolsos. El agente principal junta lo que devolvieron en un resumen de 20 líneas (clases clave, quién llama a quién, la regla de centavos). Fase 2: lanza dos subagentes para buscar los puntos donde se convierte de pesos a centavos de peso, y les pasa ese resumen al principio del prompt. Arrancan sabiendo dónde mirar.

### Para el examen

- Fase nueva con subagentes nuevos → **resumir los hallazgos de la fase anterior e inyectarlos en el prompt inicial**.
- Distractores: suponer que los subagentes heredan la conversación, o pasarles todos los reportes completos.

### Cómo se une

A veces la exploración se hace en una sola sesión que ya está llena. Ahí entra `/compact`.

---

## Tema 5 — `/compact`, `/clear` o una sesión nueva

### Qué es

Claude Code tiene tres formas de manejar una sesión cargada, y el examen las mezcla:
- **`/compact`**: resume la conversación y libera contexto, **en la misma sesión**. La guía lo pide para cuando, en una exploración larga, **el contexto se llenó de salida de descubrimiento** y querés seguir con la misma tarea. Podés darle un foco: `/compact conservá las clases del flujo de reembolsos y las rutas de los tests`.
- **`/clear`**: borra todo y empieza de cero. Sirve para pasar a una **tarea distinta**, no para seguir la misma.
- **Sesión nueva con un resumen estructurado** (lo viste en 1C): conviene cuando los resultados viejos **ya no son válidos**, por ejemplo porque el código cambió mucho desde la última sesión. Si el contexto sigue siendo válido, se retoma con `--resume`.

> ⚠️ **En el curso vas a escuchar otra cosa.** Jacob dice que, cuando la ventana se llena, los proveedores "truncan" los turnos viejos. **Para el examen:** la API no trunca: si te pasás de la ventana, da error. Claude Code primero limpia las salidas viejas de las herramientas y después **compacta** (resume). La consecuencia sí es la que dice Jacob: se pueden perder instrucciones del principio de la conversación.

Un detalle que conecta con 5A: `/compact` **es un resumen**, así que puede perder valores exactos. Lo que tiene que sobrevivir sí o sí (una ruta, un valor, una decisión) va al **scratchpad**, no se confía al resumen.

### Ejemplo

Después de una hora mapeando el flujo de reembolsos, el contexto de Sofía está lleno de resultados de `Grep`. Ella sigue con la misma tarea, así que corre `/compact` con foco en las clases del flujo. Los valores exactos ya estaban en el scratchpad. Al día siguiente, el equipo mergeó un refactor grande de pagos: en vez de `--resume`, Sofía abre una sesión nueva y le pasa el scratchpad como resumen.

### Para el examen

- Contexto lleno de salida de exploración y querés seguir con la misma tarea → **`/compact`**.
- Tarea nueva → `/clear`.
- Retomar con resultados que ya no valen → **sesión nueva con resumen**; si todavía valen → `--resume`.
- Valores que no se pueden perder → al **scratchpad**, no al resumen.

### Cómo se une

Hasta acá, una persona explorando con Claude Code. En un sistema de varios agentes que corre solo, aparece otro riesgo: que se corte a la mitad.

---

## Tema 6 — Crash recovery with manifests (recuperarse de un corte con manifests)

### Qué es

Imaginá un sistema multiagente que tarda horas en analizar un codebase: el coordinador lanzó 12 subagentes y, cuando 7 ya terminaron, se cae el proceso. Si al reiniciar el coordinador no sabe qué se hizo, tiene que relanzar todo. Peor: si intenta "recordar" lo que pasó, va a inventar.

La guía pide **persistencia estructurada del estado**:
1. **Cada agente exporta su estado** (qué hizo, qué encontró, si terminó) a un **lugar conocido**: un archivo por agente.
2. El coordinador mantiene un **manifest** (un índice en JSON con el estado de cada tarea).
3. Al reanudar, el coordinador **carga el manifest**, **saltea lo que ya terminó** e **inyecta** el estado exportado en los prompts de los agentes que tienen que seguir.

Es la misma idea de "retomar, no reiniciar" que viste en 1C y en 5B. El manifest conviene en **JSON** y no como checklist en Markdown: según Anthropic, el modelo es menos propenso a sobrescribir indebidamente un JSON, y además lo lee un programa.

### Cómo se configura

`state/manifest.json`:

```json
{
  "run_id": "audit-2026-11-24",
  "tasks": [
    {"id": "map-payments", "status": "done",    "export": "state/map-payments.json"},
    {"id": "map-orders",   "status": "done",    "export": "state/map-orders.json"},
    {"id": "map-refunds",  "status": "running", "export": null},
    {"id": "find-tests",   "status": "pending", "export": null}
  ]
}
```

### Ejemplo

El análisis nocturno de TiendaX se cae a las 3:40. Al reiniciar, el coordinador lee `manifest.json`. Ve que `map-payments` y `map-orders` terminaron, así que no los relanza. Relanza `map-refunds` y le inyecta los exports de los otros dos. Después sigue con `find-tests`. Se pierden 10 minutos de trabajo, no 3 horas.

### Para el examen

- Recuperarse de un corte en un sistema multiagente → **cada agente exporta su estado a un lugar conocido; el coordinador carga el manifest al reanudar y lo inyecta en los prompts**.
- Distractores: relanzar todo, reanudar el coordinador y "preguntarle qué recuerda", o confiar en la compactación automática para llevar el estado.

---

## Tema 7 — 📘 La memory tool y la coherencia en conversaciones largas (lección 114 y deck 139)

### Qué es

Esto es del curso y de la documentación; la guía no lo nombra, pero refuerza las mismas ideas.

En la lección 114, Jacob distingue dos tipos de memoria:
- **In-context**: todo vive en el historial. Se degrada y, cuando se compacta, se pierde detalle.
- **Externa**: lo importante se guarda afuera y se lee al empezar cada turno.

Lo recomendable es una mezcla: el historial reciente en contexto y los hechos durables afuera. También sugiere **re-anclar el objetivo** cada tanto ("seguimos con el mapeo del flujo de reembolsos"), para que la conversación no se desvíe.

El deck 139 presenta la **memory tool** de la API: una tool que le da a Claude un directorio de archivos (`/memories`) donde puede crear, leer y editar notas entre sesiones. Es la versión de la API del scratchpad. Corre del lado de tu aplicación (vos guardás los archivos), y la documentación recomienda que Claude **revise su memoria antes de empezar cualquier tarea**, asumiendo que la sesión puede cortarse en cualquier momento.

Jacob agrega dos cosas: la compactación **pierde detalle**, así que conviene evitarla donde cada palabra importa (un code review, una conversación legal o de compliance); y compactación y memory tool **se complementan**: una achica el historial y la otra guarda lo que tiene que sobrevivir.

**Para el examen:** la guía no evalúa la memory tool. Si aparece, es el equivalente del scratchpad en la API. En Claude Code, la respuesta de la guía es el **scratchpad file**.

---

## Cómo se une todo

En una exploración larga, el contexto se llena de salida verbosa y Claude empieza a responder con "patrones típicos" en vez de las clases que encontró (Tema 1). Lo descubierto se guarda en un **scratchpad file** que se consulta antes de cada pregunta (Tema 2). La búsqueda pesada se **delega a subagentes** con preguntas concretas, y el agente principal coordina (Tema 3). Entre fases, se pasa un **resumen** de los hallazgos a los subagentes nuevos (Tema 4). Si la sesión se llenó y la tarea sigue, **`/compact`**; si la tarea cambia, `/clear`; si el código cambió, sesión nueva con resumen (Tema 5). Y en sistemas multiagente, cada agente **exporta su estado** y el coordinador **carga el manifest** al reanudar (Tema 6).

## Lo que viene

**5D · Udemy 19 — Human Oversight, Confidence, and Provenance**, tareas 5.5 y 5.6, el último capítulo del libro: revisión humana, confianza calibrada, muestreo estratificado y cómo conservar de dónde sale cada dato en una síntesis.

---

## Las trampas del examen

Cada trampa tiene el mismo orden: la situación, **qué elegir en el examen (✅)**, las opciones que tientan (❌) con por qué tientan y por qué están mal, y una regla para recordar.

### Grupo: Sesiones largas

#### Trampa 1 · "Typical patterns"

**La situación.** Después de dos horas explorando, Claude responde sobre "los patrones típicos de un sistema de reembolsos" en vez de nombrar `RefundService`, que había encontrado al principio (Temas 1 y 2).

**✅ En el examen elegí:** **mantener un scratchpad file con los hallazgos clave y consultarlo antes de cada pregunta nueva**.

**❌ Las que tientan:**

❌ **"Usar un modelo con una ventana de contexto más grande".**
- *Tienta porque:* parece que se quedó sin espacio.
- *Está mal porque:* es degradación por cantidad de tokens, no falta de espacio.

❌ **"Cargar toda la estructura del repo al principio de la sesión".**
- *Tienta porque:* Claude tendría todo a mano.
- *Está mal porque:* agrega más contenido verboso y empeora la degradación.

❌ **"Reiniciar la sesión para que explore con el contexto limpio".**
- *Tienta porque:* el contexto queda vacío.
- *Está mal porque:* sin guardar antes lo encontrado, se pierde todo.

> 🧠 **Para recordar:** "typical patterns" = degradación → **scratchpad**.

#### Trampa 2 · El scratchpad que nadie lee

**La situación.** El agente escribe sus hallazgos en `notes.md`, pero sigue respondiendo de forma inconsistente (Tema 2).

**✅ En el examen elegí:** **que el agente consulte el scratchpad antes de responder cada pregunta nueva**.

**❌ Las que tientan:**

❌ **"Agregar más detalle a lo que se escribe en el scratchpad".**
- *Tienta porque:* más información parece mejor.
- *Está mal porque:* el problema no es lo que se escribe, es que no se lee.

> 🧠 **Para recordar:** el scratchpad se **escribe y se lee**.

### Grupo: Delegar y pasar contexto

#### Trampa 3 · Buscar todo en el agente principal

**La situación.** Antes de un refactor, hay que encontrar todos los tests que tocan el flujo de reembolsos en un monorepo enorme (Tema 3).

**✅ En el examen elegí:** **lanzar un subagente con esa pregunta concreta y de solo lectura, que devuelva una lista resumida**.

**❌ Las que tientan:**

❌ **"Que el agente principal haga la búsqueda y después corra `/compact`".**
- *Tienta porque:* libera el contexto al final.
- *Está mal porque:* compacta después del daño y puede perder las rutas exactas.

❌ **"Limitar la búsqueda del agente principal a los primeros 50 resultados".**
- *Tienta porque:* controla el tamaño.
- *Está mal porque:* deja un inventario incompleto.

> 🧠 **Para recordar:** exploración verbosa = **subagente con pregunta concreta**.

#### Trampa 4 · Un subagente para todo

**La situación.** Justo antes de editar una función, Claude necesita confirmar en qué archivo está `formatPriceCents` (Tema 3).

**✅ En el examen elegí:** **un `Grep` directo** desde el agente principal.

**❌ Las que tientan:**

❌ **"Delegar la búsqueda a un subagente para proteger el contexto".**
- *Tienta porque:* es la regla del tema.
- *Está mal porque:* el subagente arranca de cero y es más lento para algo chico; el resultado ocupa una línea.

> 🧠 **Para recordar:** se delega lo **verboso**, no lo puntual.

#### Trampa 5 · La fase 2 que no sabe nada

**La situación.** La fase 1 mapeó los módulos. Los subagentes de la fase 2 vuelven a descubrir lo mismo y contradicen algunos hallazgos (Tema 4).

**✅ En el examen elegí:** **resumir los hallazgos de la fase 1 e inyectarlos en el prompt inicial de los subagentes de la fase 2**.

**❌ Las que tientan:**

❌ **"Pasarles los reportes completos de la fase 1".**
- *Tienta porque:* no se pierde nada.
- *Está mal porque:* vuelve a llenar su contexto con ruido.

❌ **"Lanzarlos desde la misma conversación para que hereden lo anterior".**
- *Tienta porque:* parece que tendrían todo el contexto.
- *Está mal porque:* un subagente normal arranca con el contexto que le pasás; y aunque se lo lance como fork para que herede todo, cargaría toda la salida de la fase 1, que es justo lo que había que evitar.

> 🧠 **Para recordar:** entre fases, **un resumen**, ni nada ni todo.

### Grupo: Sesiones y cortes

#### Trampa 6 · `/clear` para seguir la misma tarea

**La situación.** El contexto está lleno de resultados de búsquedas y Sofía quiere seguir con el mismo mapeo (Tema 5).

**✅ En el examen elegí:** **`/compact`**, idealmente con un foco.

**❌ Las que tientan:**

❌ **"`/clear` para liberar todo el contexto".**
- *Tienta porque:* libera más espacio.
- *Está mal porque:* borra todo el trabajo; es para empezar una tarea distinta.

> 🧠 **Para recordar:** misma tarea = **`/compact`**; tarea nueva = `/clear`.

#### Trampa 7 · Confiar el valor exacto al resumen

**La situación.** En la exploración apareció un valor que no puede perderse (el tope de USD 500 en `RefundPolicy`). Van a compactar la sesión (Temas 2 y 5).

**✅ En el examen elegí:** **anotarlo en el scratchpad** antes de compactar.

**❌ Las que tientan:**

❌ **"Pedirle a `/compact` que conserve ese valor".**
- *Tienta porque:* `/compact` acepta un foco.
- *Está mal porque:* sigue siendo un resumen y puede desdibujarlo.

> 🧠 **Para recordar:** lo que **no se puede perder** va a un **archivo**.

#### Trampa 8 · El coordinador que se cayó

**La situación.** Un análisis multiagente se cae cuando 7 de 12 subagentes terminaron (Tema 6).

**✅ En el examen elegí:** **que cada agente exporte su estado a un lugar conocido y que el coordinador cargue el manifest al reanudar**, salteando lo terminado e inyectando los exports en los que faltan.

**❌ Las que tientan:**

❌ **"Relanzar todo el análisis desde el principio".**
- *Tienta porque:* asegura un resultado consistente.
- *Está mal porque:* repite horas de trabajo que ya estaba hecho.

❌ **"Reanudar el coordinador y pedirle que reconstruya qué tareas terminaron".**
- *Tienta porque:* el coordinador "estuvo ahí".
- *Está mal porque:* su memoria de la conversación no es confiable; el estado tiene que estar escrito.

> 🧠 **Para recordar:** corte = **manifest + estado exportado**.

#### Trampa 9 · Retomar con el código cambiado

**La situación.** Sofía retoma una exploración del día anterior, pero el equipo mergeó un refactor grande de pagos a la mañana (Tema 5).

**✅ En el examen elegí:** **empezar una sesión nueva con un resumen estructurado** (por ejemplo, el scratchpad actualizado).

**❌ Las que tientan:**

❌ **"`--resume` de la sesión de ayer".**
- *Tienta porque:* conserva todo el contexto.
- *Está mal porque:* trae resultados de herramientas que ya no son válidos.

> 🧠 **Para recordar:** contexto válido = `--resume`; contexto **viejo** = **sesión nueva + resumen**.

### Grupo: Confiar en el subagente

#### Trampa 10 · Borrar por lo que dijo el subagente

**La situación.** Un subagente de exploración reporta que `LegacyRefundAdapter` no se usa en ningún lado. El plan es borrarlo junto con sus tests (Tema 3).

**✅ En el examen elegí:** **verificar el hallazgo con una búsqueda puntual antes de borrar**, porque la decisión es crítica.

**❌ Las que tientan:**

❌ **"Borrarlo directamente: para eso se delegó la exploración".**
- *Tienta porque:* el subagente hizo la búsqueda completa.
- *Está mal porque:* lo que devuelve es una hipótesis; el agente principal no vio cómo llegó a esa conclusión.

> 🧠 **Para recordar:** decisión crítica = **verificar** lo que devolvió el subagente.

---

## Checklist oficial

**Tarea 5.4 — Manage context effectively in large codebase exploration**

*Knowledge of*
- [x] La degradación del contexto en sesiones largas: respuestas inconsistentes y "typical patterns" en vez de las clases específicas encontradas → **Tema 1** (Trampa 1)
- [x] El rol de los scratchpad files para persistir hallazgos clave más allá del contexto → **Tema 2** (Trampas 1 y 2)
- [x] Delegar a subagentes para aislar la salida verbosa de la exploración mientras el agente principal coordina → **Tema 3** (Trampas 3 y 10)
- [x] Persistencia estructurada del estado para recuperarse de un corte: cada agente exporta su estado a un lugar conocido y el coordinador carga un manifest al reanudar → **Tema 6** (Trampa 8)

*Skills in*
- [x] Lanzar subagentes para investigar preguntas específicas ("encontrá todos los tests", "rastreá las dependencias del flujo de reembolsos") mientras el agente principal coordina → **Tema 3** (Trampas 3 y 4)
- [x] Mantener scratchpad files con los hallazgos clave y consultarlos en las preguntas siguientes → **Tema 2** (Trampa 2)
- [x] Resumir los hallazgos de una fase antes de lanzar los subagentes de la siguiente e inyectar ese resumen en su contexto inicial → **Tema 4** (Trampa 5)
- [x] Diseñar la recuperación con exports de estado (manifests) que el coordinador carga al reanudar e inyecta en los prompts → **Tema 6** (Trampa 8)
- [x] Usar `/compact` para reducir el contexto en exploraciones largas cuando se llena de salida de descubrimiento → **Tema 5** (Trampas 6 y 7)

**Complementa otras tareas:** Explore subagent de 3.4 (Tema 3) · `--resume` vs. sesión nueva de 1.7 (Tema 5) · resúmenes que pierden datos de 5.1 (Temas 5 y 7).

**De la documentación, no de la guía** (vale saberlo; la guía no lo pregunta directo): context rot (Tema 1) · subagentes como consejo "viejo" en las best practices actuales (Tema 3) · memory tool (Tema 7).

**📘 Curso (útil para entender):** higiene del scratchpad y hooks de lectura (Tema 2) · prompt QUESTION/SCOPE/RETURN/STOP y blind trust (Tema 3) · memoria in-context vs. externa y re-anclar el objetivo (Tema 7).

---

## Autoevaluación oral

1. ¿Cuál es el síntoma de la degradación del contexto según la guía? ¿Por qué agrandar la ventana no lo arregla?
2. ¿Qué es un scratchpad file, qué se guarda ahí y qué tiene que hacer el agente con él?
3. ¿Cuándo delegás la exploración a un subagente y cuándo no? ¿Qué le pasás a los subagentes de la fase siguiente?
4. ¿Cuándo usás `/compact`, cuándo `/clear` y cuándo una sesión nueva con resumen?
5. ¿Cómo se recupera un sistema multiagente después de un corte? ¿Qué es el manifest?

---

## Preguntas tipo examen

Las preguntas tipo examen de este capítulo están en [`04-practica/modulo-5.md`](../04-practica/modulo-5.md), junto con las del resto del módulo 5. Hacelas cuando termines **todos** los capítulos del módulo, de a una y sin mirar la respuesta.

---

## Revisión contra el blueprint oficial

Qué puede salir en el examen de 5.4 que el curso de Jacob **no cubre o cubre flojo**, y dónde quedó explicado:

1. **El síntoma literal** ("typical patterns" en vez de clases específicas). → Tema 1.
2. **Resumir y pasar los hallazgos entre fases.** → Tema 4.
3. **`/compact` por nombre** y la diferencia con `/clear` y con una sesión nueva. → Tema 5.
4. **Crash recovery con manifests** (2 de los 9 puntos de la guía). → Tema 6.
5. **Explore subagent** (la guía lo pone en 3.4; el curso no lo nombra en esta sección). → Tema 3.
6. **"Providers truncate older turns"** (lección 114): impreciso. La API da error y Claude Code compacta. → Tema 5.

No encontré otros huecos para 5.4.

