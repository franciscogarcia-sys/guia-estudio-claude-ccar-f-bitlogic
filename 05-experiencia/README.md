# 05 · Experiencia: dificultades, recomendaciones y aprendizajes

Lo que no está en ningún curso: qué costó, qué errores se repiten, qué hacer el día del examen y qué queda después de aprobar.

---

## Principales dificultades

**1. El inglés no es el problema; los matices sí.** Las preguntas no son difíciles de traducir: son difíciles de **leer bien**. La respuesta suele depender de una frase de cinco palabras (*"while keeping…"*, *"already have clear, distinct descriptions"*, *"most reliably"*). Leer rápido y elegir "la que suena mejor" es la principal fuente de errores.

**2. Todas las opciones parecen correctas.** Los distractores son técnicas reales, que en otro contexto serían la respuesta. Sin entender **por qué** cada una está mal en **ese** escenario, se termina eligiendo por intuición.

**3. El curso y la guía no siempre dicen lo mismo.** El curso de Udemy es muy bueno como hilo conductor, pero en varios temas propone algo distinto de lo que evalúa la guía o de lo que dice la documentación actual (cómo se pasa el contexto a un subagente, qué campos lleva un handoff, cómo se usa el muestreo estratificado, cómo se resuelven fuentes en conflicto). Si no se detectan, se aprende la respuesta equivocada. Están listadas en [`DIVERGENCES.md`](../DIVERGENCES.md).

**4. Mucho detalle de la documentación en los dominios 2 y 3.** Varias preguntas dependen de detalles concretos: cómo se devuelven los resultados de varias tools, qué hace `strict` frente a `tool_choice`, cuándo se carga una rule con `paths`, que Grep usa regex, qué vuelve de un subagente. Son cosas que se entienden mejor habiéndolas visto funcionar.

**5. Conceptos que se mezclan.** Hook o prompt, `any` o forzado, rules o skills, `/compact` o `/clear`, confianza para escalar o para enrutar revisiones. Son pares que el examen pone a competir a propósito. Por eso existe el [mapa de confusiones](../03-libro/19-mapa-de-confusiones.md).

**6. Los cálculos de Batches.** El SLA de la Message Batches API (intervalo entre envíos + 24 horas ≤ SLA) es simple, pero las preguntas meten el dato trampa de "la mayoría de los lotes termina en menos de una hora".

## Errores frecuentes y la regla que los evita

Estos son los errores que más se repitieron durante la preparación, en las preguntas de práctica y en los practice exams.

| Error | Regla |
|---|---|
| Elegir una solución correcta en general que rompe una condición del enunciado | **Antes de elegir, buscá qué tiene que seguir funcionando** (*"while keeping…"*, *"without affecting…"*) y descartá lo que lo rompe |
| Agregar algo bueno pero dejar en su lugar lo que causó el problema | **Si el enunciado nombra la causa, la respuesta la tiene que sacar** |
| "Mejorar la descripción" o "agregar ejemplos" cuando el enunciado dice que las descripciones ya son buenas | Las descripciones arreglan **la elección entre tools parecidas**. Si ya son buenas, mirá el **system prompt** o la **interfaz de la tool** |
| Culpar a la descripción de una tool cuando el enunciado muestra el código del loop | **Si el enunciado muestra el loop, la causa suele estar en el loop.** Lo que no está en el historial, para Claude no existe |
| Retomar una sesión cuando el código cambió mucho | ¿Cuánto del contexto viejo sigue valiendo? **Poco → sesión nueva con un resumen.** Fork no limpia: copia lo viejo |
| Poner en el prompt una regla que se puede chequear con un `if` | **¿Se puede chequear con código (orden de tools, monto)? → hook o prerrequisito.** ¿Hace falta criterio? → prompt con criterios y ejemplos |
| Usar una skill cuando la convención tiene que aplicarse sí o sí en ciertos archivos | **Aplicación garantizada en ciertos archivos → rule con `paths:`.** Una skill depende de que Claude decida cargarla |
| Elegir el mecanismo "más fuerte" aunque rompa otros flujos | **El arreglo tiene el alcance del problema:** una skill → `allowed-tools` de esa skill; todo el repo → `deny` o hook |
| Pedir "be conservative" para bajar los falsos positivos | **Criterios explícitos: qué reportar y qué no.** Nunca "cuánta confianza" |
| Reintentar cuando el dato no está en el documento | Si el dato **no está**, reintentar no sirve, e inferirlo es **inventar** |
| Calcular el SLA de un lote con el caso típico | **Intervalo + 24 h ≤ SLA**, siempre con el peor caso |
| Reenviar todo el lote cuando fallaron algunos | **Solo los fallidos, por `custom_id`, corregidos según la causa** |
| Acertar una de las *Select TWO* y elegir la otra sin cuidado | **Evaluá cada opción por separado**, como verdadera o falsa |

## Recomendaciones para el examen

**Para estudiar**
- **Estudiá contra la guía oficial**, no solo contra el curso. Al terminar cada tema, repasá su checklist de *knowledge* y *skills*.
- **No memorices respuestas: entendé por qué tientan los distractores.** El examen cambia el escenario, pero los anti-patterns se repiten.
- **Practicá leyendo en inglés** desde el principio. Las preguntas de [`04-practica`](../04-practica/README.md) traen una pista de lectura con la frase que decidía cada una.
- **Si podés, probá las cosas en Claude Code**: un hook, una skill, una rule con `paths`, `claude -p`. Lo que viste funcionar no se confunde.
- **Hacé al menos dos practice exams cronometrados** y analizá cada error. No te preocupes si el puntaje es más bajo que en el libro: suelen ser más exigentes en detalles que el examen real.

**Durante el examen**
- **Leé la pregunta del final primero** (*"What's the most effective way to…"*), después el enunciado completo buscando la condición de alcance y la causa nombrada, y recién después las opciones.
- **Descartá antes de elegir.** Casi siempre hay dos opciones que se descartan rápido; la decisión real es entre las otras dos.
- **Desconfiá de las opciones que agregan complejidad** (un clasificador, un modelo más grande, otro servicio) cuando hay una más simple que ataca la causa.
- **En las *Select TWO*, las dos correctas suelen atacar cosas distintas** (por ejemplo, la profundidad y la consistencia, o la ida y la vuelta).
- **Administrá el tiempo:** unos 2 minutos por pregunta. Si una se traba, elegí la mejor, marcala para revisar y seguí. Al final, volvé a las marcadas.
- **Respondé todas.** No se descuenta por error.

**Logística** (detalle en [`01-el-examen`](../01-el-examen/README.md#rendir-desde-tu-casa-pearson-onvue))
- Corré el System Test de OnVUE **días antes**, en la misma computadora y red. Evitá la notebook del trabajo si tiene VPN o restricciones.
- Tené el **documento físico** a mano y el celular con batería para las fotos del check-in.
- Andá al baño antes: no hay descansos.

---

## Aprendizajes

Más allá del examen, la preparación deja ideas que sirven para trabajar todos los días con Claude:

- **Lo que no puede fallar va en código; lo que requiere juicio va en el prompt.** Un prompt se cumple casi siempre; un hook o una validación se cumplen siempre. Elegir bien dónde va cada regla es la decisión de diseño más repetida del examen.
- **El contexto es un recurso limitado.** Lo que no está en el historial, para el modelo no existe. Lo que sobra en el contexto le quita atención a lo importante. Subagentes, rules con `paths`, resúmenes y archivos de notas existen para administrarlo.
- **Una interfaz bien diseñada vale más que una instrucción bien escrita.** Un `input_schema` tipado, una tool acotada o un `enum` evitan errores que ningún prompt evita del todo.
- **Medir antes de confiar.** La confianza que el modelo se asigna no está calibrada; la accuracy total esconde los segmentos que fallan. Se mide por segmento, se calibra contra casos conocidos y se sigue muestreando lo automatizado.
- **Revisar con otra instancia.** La misma sesión que generó algo no lo revisa bien: hereda su propio razonamiento.
- **Especificar antes de implementar.** Un contrato escrito (criterios, ejemplos, tests que no se tocan) hace que el resultado sea predecible y verificable.

## Estudiar con Claude como tutor

Buena parte del material de este repo se armó **estudiando con Claude como tutor**. El método:

1. **Un proyecto con instrucciones fijas** (un CLAUDE.md o las instrucciones del proyecto): el rol de tutor, el examen, el formato de los capítulos, el idioma (español con los términos en inglés) y las reglas de fuentes.
2. **El curso como hilo conductor y la guía oficial como árbitro.** Para cada sección, Claude armaba el capítulo a partir del material del curso, lo validaba contra la guía y la documentación, y marcaba dónde el curso difería.
3. **Un formato fijo por capítulo:** temas explicados desde cero con un ejemplo, trampas del examen con sus distractores, checklist oficial y autoevaluación.
4. **Preguntas al final de cada módulo**, de a una y con corrección inmediata, imitando el estilo real.
5. **Un registro de errores**, con la regla que evita cada uno, que después se convirtió en el mapa de confusiones.

Funcionó muy bien con dos condiciones: **pedir siempre que se verifique contra la documentación oficial** (el curso y la memoria del modelo pueden estar desactualizados) y **pedir explicaciones completas**, no resúmenes telegráficos.

---

## Aplicación práctica en Bitflow

**Bitflow** es el plugin interno de Bitlogic que empaqueta el flujo de **Spec-Driven Development** (desarrollo guiado por especificaciones) como un conjunto de skills para Claude Code y Cursor: desde el descubrimiento y el pitch de una idea hasta la especificación, la implementación, el PR y la revisión. Su principio es que **no se escribe código sin un contrato verificable**.

Muchos conceptos del CCAR-F aparecen directamente en cómo está construido y en cómo se usa:

| Concepto del CCAR-F | Dominio | Cómo aparece en Bitflow |
|---|---|---|
| **Skills con frontmatter** (`name`, `description`, `disable-model-invocation`) | D3 · 3.2 | Cada fase del flujo es una skill que se invoca a pedido con `/nombre`. Las skills se marcan para que **solo las dispare la persona**, no Claude por su cuenta |
| **Distribución para el equipo y configuración administrada** | D3 · 3.1 | Las skills se instalan desde un marketplace de plugins y se pueden desplegar a toda la organización con *managed settings*, igual que el nivel *managed* de CLAUDE.md |
| **Jerarquía de instrucciones por carpeta** | D3 · 3.1, 3.3 | Las convenciones viven en archivos de instrucciones por capa del repo, y se aplica el **más cercano** al archivo que se modifica: la misma idea que los CLAUDE.md por carpeta y las rules por ruta |
| **Interview pattern → especificación → implementación** | D3 · 3.5 | El flujo entrevista antes de escribir, deja el contrato en un archivo de especificación y recién después implementa: el patrón *entrevista → `SPEC.md` → sesión nueva* |
| **Test-driven iteration** | D3 · 3.5 | La implementación se hace con TDD, a partir de los criterios de aceptación del contrato: el contrato define qué tiene que pasar y el código se ajusta a él |
| **Plan antes de ejecutar** | D3 · 3.4 | La descomposición en scopes y sub-issues técnicos antes de codificar cumple el rol de plan mode para cambios grandes |
| **Task decomposition** | D1 · 1.6 | Un proyecto se parte en scopes funcionales y cada scope en sub-issues técnicos, que se implementan de a uno |
| **Integración con MCP y su fallback** | D2 · 2.4 | Las skills leen y escriben en Linear a través de su servidor MCP; si el MCP no está disponible, hay un camino alternativo explícito en lugar de fallar en silencio |
| **Validación de prerrequisitos** | D1 · 1.4 | Cada skill verifica sus prerrequisitos al empezar y **se detiene** si falta algo, en vez de avanzar sobre un insumo a medias |
| **Human-in-the-loop y checkpoints** | D1 · 1.4, D5 · 5.5 | Antes de cualquier acción visible para el equipo (escribir en Linear, crear documentación) hay un checkpoint de confirmación; las decisiones clave (qué se apuesta, qué se mergea) son humanas |
| **Revisión independiente** | D4 · 4.6 | La revisión de un PR se hace contra el contrato, en un paso separado de la implementación, y la aprobación final es humana |
| **No inventar datos** | D4 · 4.3, 4.4 | Las skills tienen la instrucción explícita de no inventar contenido que no esté en el código, la especificación o el issue: la misma idea que los campos nullable en un schema de extracción |
| **Criterios explícitos** | D4 · 4.1 | Los criterios de aceptación de la especificación son verificables y cada uno dice cómo se verifica, en lugar de instrucciones vagas |

**Lo que deja la certificación para trabajar con Bitflow**
- **Entender por qué el flujo está diseñado así**: los checkpoints, la validación de prerrequisitos y el contrato antes del código son exactamente los patrones de confiabilidad que evalúa el examen.
- **Criterio para mejorar las skills**: qué conviene dejar como instrucción en la skill y qué conviene llevar a código (un hook o una validación), cómo escribir descripciones que no se pisen, y cómo darle a cada paso solo el contexto que necesita.
- **Un vocabulario común** con el resto del equipo para discutir el diseño de agentes, skills e integraciones MCP.
