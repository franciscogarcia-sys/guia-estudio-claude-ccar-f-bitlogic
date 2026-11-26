# 01 · El examen

Todo lo que conviene saber del examen **antes** de empezar a estudiar: qué valida, cómo está armado, qué se evalúa, cómo se puntúa, cómo son las preguntas y cómo es rendirlo desde tu casa.

> Datos verificados en noviembre de 2026 contra la guía oficial del examen, la FAQ de certificaciones de Anthropic y la página de Anthropic en Pearson VUE. El programa cambia seguido: revisalos de nuevo antes de inscribirte.

---

## Qué valida

El **Claude Certified Architect – Foundations (CCAR-F)** evalúa si sabés **tomar decisiones de arquitectura** al construir soluciones reales con Claude: elegir el mecanismo correcto, entender sus trade-offs y reconocer los anti-patterns. No pide escribir código ni memorizar sintaxis, pero sí entender cómo funcionan las herramientas lo suficiente como para elegir bien entre opciones que parecen razonables.

Las herramientas que aparecen son:
- **Claude API** (Messages API, tool use, structured outputs, Message Batches API);
- **Claude Agent SDK** (agentic loops, subagents, hooks, sesiones);
- **Claude Code** (CLAUDE.md, rules, skills, slash commands, plan mode, uso en CI/CD);
- **Model Context Protocol (MCP)** (servidores, tools, resources, configuración).

Antes se lo llamaba **CCA-F**; desde julio de 2026 el código oficial en Pearson es **CCAR-F**. Es el mismo examen.

## Datos del examen

| Dato | Valor |
|---|---|
| Preguntas | **60** |
| Duración | **120 minutos** (unos 2 minutos por pregunta). Calculá **~135 minutos** frente a la computadora, contando check-in, instrucciones y una encuesta corta |
| Formato | **Multiple choice** (una correcta) y **multiple response** (*"Select TWO"*); cada pregunta dice cuántas elegir |
| Estructura | **4 escenarios** elegidos al azar de un banco de **6**; cada escenario enmarca un bloque de preguntas |
| Idioma | **Inglés**. No se permiten traductores |
| Material | Ninguno: sin documentación, sin notas, sin IA |
| Puntaje | Escala de **100 a 1000**; se aprueba con **720** |
| Precio | **USD 125** por intento (puede haber descuento según el nivel de partner) |
| Modalidad | **Online proctored** (Pearson OnVUE, desde tu casa) o en un **centro de Pearson VUE** |
| Validez | **12 meses**. La credencial digital se emite en Credly |

## Cómo se inscribe uno

1. La certificación está abierta a personas de organizaciones del **Claude Partner Network**. La inscripción empieza en la **Anthropic Partner Academy** (`anthropic-partners.skilljar.com`): ahí te registrás y pagás.
2. Llega un mail con el acceso a **Pearson VUE**. Si es tu primer examen en Pearson, también llegan usuario y contraseña (revisá spam).
3. En Pearson elegís fecha y modalidad: OnVUE (online) o centro de testeo.

**Políticas que conviene saber:**
- **El nombre del perfil de Pearson tiene que coincidir exactamente** con el del documento que vas a presentar. Si no coincide, no te dejan rendir y perdés el pago.
- **Cancelar o reprogramar:** hasta **48 horas** antes del turno. Después se pierde el pago.
- **Reintentos:** si no aprobás, esperás **14 días** para el segundo intento, **30** para el tercero y **90** para el cuarto. Máximo **4 intentos en 12 meses**, y cada uno se paga completo.

---

## El blueprint: 5 dominios y 30 tareas

La guía oficial divide el examen en cinco dominios, cada uno con un peso, y cada dominio en **task statements** (tareas oficiales). Cada tarea tiene una lista de *knowledge* (lo que tenés que saber) y *skills* (lo que tenés que saber hacer). **Esa lista es el temario real del examen.**

| Dominio | Peso | Tareas | Peso aprox. por tarea |
|---|---|---|---|
| **D1** Agentic Architecture & Orchestration | **27%** | 7 | 3,9% |
| **D2** Tool Design & MCP Integration | **18%** | 5 | 3,6% |
| **D3** Claude Code Configuration & Workflows | **20%** | 6 | 3,3% |
| **D4** Prompt Engineering & Structured Output | **20%** | 6 | 3,3% |
| **D5** Context Management & Reliability | **15%** | 6 | 2,5% |

**D1 · Agentic Architecture & Orchestration (27%)**
- 1.1 Design and implement agentic loops for autonomous task execution
- 1.2 Orchestrate multi-agent systems with coordinator-subagent patterns
- 1.3 Configure subagent invocation, context passing, and spawning
- 1.4 Implement multi-step workflows with enforcement and handoff patterns
- 1.5 Apply Agent SDK hooks for tool call interception and data normalization
- 1.6 Design task decomposition strategies for complex workflows
- 1.7 Manage session state, resumption, and forking

**D2 · Tool Design & MCP Integration (18%)**
- 2.1 Design effective tool interfaces with clear descriptions and boundaries
- 2.2 Implement structured error responses for MCP tools
- 2.3 Distribute tools appropriately across agents and configure tool choice
- 2.4 Integrate MCP servers into Claude Code and agent workflows
- 2.5 Select and apply built-in tools (Read, Write, Edit, Bash, Grep, Glob) effectively

**D3 · Claude Code Configuration & Workflows (20%)**
- 3.1 Configure CLAUDE.md files with appropriate hierarchy, scoping, and modular organization
- 3.2 Create and configure custom slash commands and skills
- 3.3 Apply path-specific rules for conditional convention loading
- 3.4 Determine when to use plan mode vs direct execution
- 3.5 Apply iterative refinement techniques for progressive improvement
- 3.6 Integrate Claude Code into CI/CD pipelines

**D4 · Prompt Engineering & Structured Output (20%)**
- 4.1 Design prompts with explicit criteria to improve precision and reduce false positives
- 4.2 Apply few-shot prompting to improve output consistency and quality
- 4.3 Enforce structured output using tool use and JSON schemas
- 4.4 Implement validation, retry, and feedback loops for extraction quality
- 4.5 Design efficient batch processing strategies
- 4.6 Design multi-instance and multi-pass review architectures

**D5 · Context Management & Reliability (15%)**
- 5.1 Manage conversation context to preserve critical information across long interactions
- 5.2 Design effective escalation and ambiguity resolution patterns
- 5.3 Implement error propagation strategies across multi-agent systems
- 5.4 Manage context effectively in large codebase exploration
- 5.5 Design human review workflows and confidence calibration
- 5.6 Preserve information provenance and handle uncertainty in multi-source synthesis

En el [índice del libro](../03-libro/00-indice.md) está qué capítulo cubre cada tarea, y cada capítulo termina con el **checklist oficial** de sus tareas.

## Los 6 escenarios

Cada examen toma **4 de estos 6** al azar. Cada escenario describe, en 3 o 4 oraciones y en segunda persona, un sistema en producción con sus componentes; las preguntas del bloque parten de esa situación.

| Escenario | De qué trata | Dominios que más pesan |
|---|---|---|
| **Customer Support Resolution Agent** | Agente de soporte con el Agent SDK y tools MCP (`get_customer`, `lookup_order`, `process_refund`, `escalate_to_human`), con meta de resolución en el primer contacto | D1, D2, D5 |
| **Code Generation with Claude Code** | Equipo que usa Claude Code para generar, refactorizar y documentar código: CLAUDE.md, comandos, plan mode | D3 |
| **Multi-Agent Research System** | Coordinador con subagentes (búsqueda, análisis, síntesis, informes) que produce informes con citas | D1, D5 |
| **Developer Productivity with Claude** | Agente que explora codebases desconocidos con las built-in tools y servidores MCP | D2, D3, D5 |
| **Claude Code for Continuous Integration** | Claude Code en un pipeline de CI/CD: revisión de PRs, generación de tests | D3, D4 |
| **Structured Data Extraction** | Extracción de datos de documentos con JSON schemas, validación y procesamiento en lote | D4, D5 |

## Cómo se puntúa

- El puntaje es **escalado** (scaled score). **720 no significa 72% de respuestas correctas**: es el corte de aprobación en esa escala.
- **No se descuenta por error.** Una pregunta sin responder cuenta como incorrecta, así que **respondé todas**.
- El reporte de resultados muestra el desempeño **por dominio**.

---

## Cómo son las preguntas

Esto es lo que más conviene entender antes de estudiar, porque cambia **cómo** se estudia.

**El enunciado** tiene casi siempre tres partes:
1. **Una situación o evidencia**, con datos concretos: *"Production logs show…"*, *"Your agent achieves 55% first-contact resolution…"*, *"A pull request modifies 14 files…"*.
2. **Un detalle que importa**: porcentajes, nombres de tools, una frase literal del prompt o del usuario, una restricción.
3. **Una pregunta corta**: *"What's the most effective way to address this?"*, *"What is the most likely root cause?"*, *"How should you evaluate this proposal?"*.

**Las opciones** tienen largos parecidos (entre 13 y 24 palabras) y casi siempre son **todas técnicamente posibles**. Los distractores no son disparates: son **anti-patterns que parecen razonables**, como reforzar el prompt cuando hace falta código, agregar ejemplos cuando el problema es la descripción, filtrar por la confianza que el modelo se asigna, o una solución más sofisticada que no ataca la causa.

**Las frases que deciden la respuesta** suelen ser:
- **Condiciones de alcance:** *"while keeping…"*, *"without affecting…"*, *"without losing…"*. Descartan las opciones que rompen algo que tiene que seguir funcionando.
- **La causa nombrada:** si el enunciado dice que alguien agregó algo y después apareció el problema, la respuesta tiene que sacar eso.
- **Superlativos:** *"most reliably"* apunta a lo determinista (código, schema, hook); *"most efficient"* a lo que resuelve en menos pasos; *"first step"* a lo más simple que ataca la causa.
- **Propuestas:** *"Your teammate proposes… How should you evaluate this proposal?"*. La propuesta casi siempre tiene un problema.

La guía oficial trae **12 preguntas de muestra** (tres por escenario, de cuatro escenarios). Son la mejor referencia del estilo real; el libro las trabaja en los capítulos que corresponden.

En el [mapa de confusiones](../03-libro/19-mapa-de-confusiones.md) están los errores de lectura más comunes y cómo evitarlos.

---

## Rendir desde tu casa (Pearson OnVUE)

**Antes del día del examen**
- Corré el **System Test** de OnVUE **en la misma computadora y la misma red** que vas a usar.
- Requisitos: Windows 10 o macOS 14 o superior (sin máquinas virtuales), webcam, micrófono y parlante (**sin auriculares**), **una sola pantalla**, al menos 6 Mbps de bajada y 2 Mbps de subida.
- **Evitá VPN, proxies y redes corporativas.** Si vas a usar una notebook de la empresa, probala antes: las restricciones de red o de seguridad pueden impedir que OnVUE funcione.

**El lugar**
- Una habitación silenciosa, con la puerta cerrada, en la que estés solo todo el examen.
- Escritorio vacío: solo la computadora y, si querés, una bebida en un recipiente sin etiquetas. Sin papeles, lapiceras, libros, relojes ni otros dispositivos al alcance.
- Pizarras borradas o tapadas.

**Documento**
- Un documento de identidad **vigente, físico y con foto** (DNI tarjeta o pasaporte), con el mismo nombre que el perfil de Pearson. No sirven versiones digitales (como la de la app Mi Argentina) ni copias.

**El check-in** (se habilita 30 minutos antes)
1. Abrís OnVUE en la computadora y arrancás el check-in.
2. OnVUE te manda un **link al celular** (por SMS o con un código QR). Se abre en el navegador del celular: **no hace falta instalar ninguna app**.
3. Con el celular sacás una selfie, fotos del documento (DNI: frente y dorso) y **cuatro fotos del lugar** (adelante, atrás, izquierda, derecha).
4. Dejás el celular **en silencio y fuera de tu alcance** (pero cerca: si hay un problema, el proctor puede llamarte).
5. Una persona revisa las fotos y habilita el examen.

**Durante el examen**
- No se puede leer en voz alta (ni en voz baja), mirar el celular ni salir del cuadro de la cámara.
- Contá con que **no hay descansos**: andá al baño antes.
- Si la aplicación se congela o se corta, cerrala y volvé a abrirla desde la carpeta de descargas.

Más recomendaciones para el día del examen en [`05-experiencia`](../05-experiencia/README.md#recomendaciones-para-el-examen).

## Fuentes oficiales

- [Exam Guide y página de la certificación](https://anthropic-partners.skilljar.com/) (Anthropic Partner Academy, requiere cuenta de partner)
- [FAQ de certificaciones de Anthropic](https://anthropic-partners.skilljar.com/page/faq-certifications)
- [Anthropic en Pearson VUE](https://www.pearsonvue.com/us/en/anthropic.html)
- [Requisitos de OnVUE](https://www.pearsonvue.com/us/en/onvue/requirements.html)
