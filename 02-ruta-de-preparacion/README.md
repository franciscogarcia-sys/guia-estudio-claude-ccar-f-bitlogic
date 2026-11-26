# 02 · Ruta de preparación

Cómo prepararse: qué conviene saber antes, qué recursos usar (y cuáles no rindieron), en qué orden estudiar y cuánto tiempo calcular. Todo sale de una preparación real que terminó con el examen aprobado.

---

## Prerrequisitos recomendados

No hay prerrequisitos formales más allá de pertenecer a una organización del **Claude Partner Network** (ver [`01-el-examen`](../01-el-examen/README.md#cómo-se-inscribe-uno)). Pero el examen asume una base:

| Qué | Para qué | Nivel necesario |
|---|---|---|
| **Programación general** y APIs REST, JSON | Las preguntas muestran requests, respuestas, JSON schemas y fragmentos de configuración | Leer y entender, no escribir |
| **Git, pull requests y CI/CD** | Un escenario entero es Claude Code en un pipeline de CI | Saber qué es un pipeline, un PR y un job |
| **Inglés técnico de lectura** | El examen es en inglés y la dificultad está en los matices del enunciado | Leer textos técnicos con fluidez; no hace falta hablarlo |
| **Haber usado Claude Code** (deseable) | CLAUDE.md, skills, slash commands, plan mode y hooks se entienden mucho mejor si los viste funcionar | Unas horas de uso real ayudan mucho |
| **Nociones de LLMs** (deseable) | Contexto, tokens, prompts, tool use | Lo básico; el curso lo cubre |

**No hace falta** tener experiencia previa construyendo agentes ni haber usado la API de Anthropic: con el material de esta ruta alcanza. Esta preparación se hizo con poca experiencia previa usando Claude.

---

## Recursos

### Oficiales

| Recurso | Para qué sirvió | Valor para el examen |
|---|---|---|
| **Exam Guide oficial** (en la Anthropic Partner Academy) | Define las 30 tareas con sus *knowledge* y *skills*, los 6 escenarios y 12 preguntas de muestra. Es el temario real | ⭐⭐⭐ Imprescindible. Leela al principio y usala como checklist al final |
| **Documentación de Claude** ([platform.claude.com/docs](https://platform.claude.com/docs)) | Tool use, `tool_choice`, structured outputs, Message Batches, prompt engineering, context windows | ⭐⭐⭐ Para validar detalles y resolver dudas. No para leer de punta a punta |
| **Documentación de Claude Code** ([code.claude.com/docs](https://code.claude.com/docs)) | CLAUDE.md y memoria, rules, skills, subagents, hooks, plan mode, modo no interactivo, Agent SDK | ⭐⭐⭐ Muchas preguntas dependen de detalles de acá (cuándo se carga una rule, qué devuelve un subagente, flags de CI) |
| **Especificación de MCP** ([modelcontextprotocol.io](https://modelcontextprotocol.io)) | Tools frente a resources, transportes, errores | ⭐⭐ Para los conceptos, no para memorizar la spec |
| **Anthropic Academy**: el *preparation path* oficial (AI Fluency, Claude 101, Building with the Claude API, Claude with Amazon Bedrock, Claude on Google Cloud, Introduction to MCP, Claude Code in Action) | Base general de Claude | ⭐ Bajo para el examen. *AI Fluency* y *Claude 101* son introductorios y casi no tocan las tareas evaluadas. *Building with the Claude API*, *Introduction to MCP* y *Claude Code in Action* son los más útiles del path. Son gratuitos y buenos para empezar, pero no alcanzan para el nivel del examen |

### Complementarios

| Recurso | Para qué sirvió | Valor para el examen |
|---|---|---|
| **[Claude Certified Architect (CCA-F) – 2026 Exam Prep](https://www.udemy.com/course/certified-claude-architect-masterclass-2026/)**, de Jacob Bushong (Udemy) | El **hilo conductor** del estudio: 18 secciones que recorren los 5 dominios en un orden lógico, con companion en PDF, slides, glosario y flashcards | ⭐⭐⭐ Muy útil como columna vertebral. **Ojo:** en varios temas dice algo distinto de la guía oficial o de la documentación actual. Esas diferencias están marcadas en el libro y listadas en [`DIVERGENCES.md`](../DIVERGENCES.md) |
| **Practice exams de Udemy** (la sección de practice exams del curso anterior y el curso [Anthropic Claude Certified Architect: Full Practice Exams](https://www.udemy.com/course/anthropic-claude-certified-architect-3-full-practice-exams/)) | Simulacros cronometrados de 60 preguntas con explicación | ⭐⭐ **No son muy fieles al examen real** (algunas preguntas van a detalles de la documentación que el examen no pide con esa profundidad), **pero ayudan bastante**, sobre todo para **aprender cómo se escriben las preguntas**, entrenar el tiempo y descubrir temas flojos |
| **Este repo**: el [libro](../03-libro/00-indice.md), las [preguntas de práctica](../04-practica/README.md) y el [mapa de confusiones](../03-libro/19-mapa-de-confusiones.md) | Estudio a fondo de cada sección, con lo que vale para el examen separado de lo que es solo del curso | ⭐⭐⭐ Es el material con el que se aprobó |

### Lo que más aportó y lo que no

**Lo que más aportó**
- **El checklist oficial de cada tarea.** Estudiar contra los *knowledge* y *skills* de la guía, y no solo contra el curso, fue lo que cerró los huecos.
- **Las trampas del examen con sus distractores.** Entender **por qué tienta** cada opción incorrecta y **por qué está mal** rinde más que memorizar la correcta.
- **Las preguntas de práctica al cierre de cada módulo**, con una pista de lectura del enunciado en inglés.
- **El mapa de confusiones**: los pares de conceptos que el examen pone a competir, explicados lado a lado. Fue el mejor material para el repaso final.
- **Analizar cada error de los practice exams** y anotar la regla que lo evita.
- **Estudiar con Claude como tutor**: pedirle que arme el material a partir del curso y que lo valide contra la guía y la documentación (ver [`05-experiencia`](../05-experiencia/README.md#estudiar-con-claude-como-tutor)).

**Lo que aportó poco**
- **Los cursos introductorios de Anthropic Academy** (*AI Fluency*, *Claude 101*): buenos para alguien que nunca usó Claude, pero con poco impacto en el examen.
- **Ver los videos sin un material escrito al lado.** La primera pasada por el curso sirvió para el mapa general, pero sin un texto propio para repasar, los detalles se olvidan rápido.
- **Los resúmenes muy compactos.** Un resumen telegráfico ("X → Y") no alcanza para resolver preguntas de escenario: hace falta entender **por qué**.
- **Memorizar números y límites** (tamaños máximos, cantidad de pedidos por lote). Casi no aparecen; lo que aparece es **cuándo** usar cada cosa.
- **Las slides del curso leídas de punta a punta.** Son muchas y repiten el companion; conviene consultarlas por tema.

---

## Orden sugerido

Seguí el orden de secciones del curso. Es lógico (cada sección usa lo anterior) y es el mismo orden del libro.

| # | Sección del curso (Udemy) | Capítulo del libro | Tareas oficiales | Horas aprox. |
|---|---|---|---|---|
| 1 | 2 · Agentic Loops | [01 · 1A](../03-libro/01-1A-agentic-loops.md) | 1.1 | 2 |
| 2 | 3 · Task Decomposition & Planning | [02 · 1B](../03-libro/02-1B-task-decomposition.md) | 1.6 | 1,5 |
| 3 | 4 · Multi-Agent Orchestration | [03 · 1C](../03-libro/03-1C-multi-agent-orchestration.md) | 1.2, 1.3, 1.7 | 2,5 |
| 4 | 5 · Reliability & Human Oversight (hooks) | [04 · 1D](../03-libro/04-1D-reliability-hooks.md) | 1.4, 1.5 | 2,5 |
| — | **Preguntas del módulo 1** | [04-practica/modulo-1](../04-practica/modulo-1.md) | — | 1 |
| 5 | 6 · Tool Design Fundamentals | [05 · 2A](../03-libro/05-2A-tool-design.md) | 2.1, 2.2, 2.3 | 2 |
| 6 | 7 · MCP Server Configuration | [06 · 2B](../03-libro/06-2B-mcp-servers.md) | 2.4 | 2 |
| 7 | 8 · MCP Production & Built-in Tools | [07 · 2C](../03-libro/07-2C-mcp-production-builtin-tools.md) | 2.4, 2.5 | 2 |
| — | **Preguntas del módulo 2** | [04-practica/modulo-2](../04-practica/modulo-2.md) | — | 1 |
| 8 | 9 · Claude Code Fundamentals | [08 · 3A](../03-libro/08-3A-claude-code-fundamentals.md) | 3.1 | 1,5 |
| 9 | 10 · CLAUDE.md Configuration | [09 · 3B](../03-libro/09-3B-claude-md-hierarchy.md) | 3.1, 3.3 | 2 |
| 10 | 11 · Commands, Skills & Subagents | [10 · 3C](../03-libro/10-3C-commands-skills-subagents.md) | 3.2, 3.4, 3.5 | 2 |
| 11 | 12 · Hooks, SDK & CI/CD | [11 · 3D](../03-libro/11-3D-hooks-sdk-cicd.md) | 3.6 | 2 |
| — | **Preguntas del módulo 3** | [04-practica/modulo-3](../04-practica/modulo-3.md) | — | 1 |
| 12 | 13 · Core Prompt Engineering | [12 · 4A](../03-libro/12-4A-core-prompt-engineering.md) | 4.1 | 1,5 |
| 13 | 14 · Advanced Prompting | [13 · 4B](../03-libro/13-4B-advanced-prompting.md) | 4.2 | 1,5 |
| 14 | 15 · Structured Output & Evaluation | [14 · 4C](../03-libro/14-4C-structured-output-evaluation.md) | 4.3–4.6 | 3 |
| — | **Preguntas del módulo 4** | [04-practica/modulo-4](../04-practica/modulo-4.md) | — | 1 |
| 15 | 16 · Context Preservation | [15 · 5A](../03-libro/15-5A-context-preservation.md) | 5.1 | 1,5 |
| 16 | 17 · Escalation & Error Propagation | [16 · 5B](../03-libro/16-5B-escalation-error-propagation.md) | 5.2, 5.3 | 1,5 |
| 17 | 18 · Context in Large Codebases | [17 · 5C](../03-libro/17-5C-context-large-codebases.md) | 5.4 | 1 |
| 18 | 19 · Confidence, Sampling & Provenance | [18 · 5D](../03-libro/18-5D-oversight-confidence-provenance.md) | 5.5, 5.6 | 1,5 |
| — | **Preguntas del módulo 5** | [04-practica/modulo-5](../04-practica/modulo-5.md) | — | 1 |
| — | **Repaso:** mapa de confusiones + [repasos mixtos](../04-practica/repasos-mixtos.md) | [19 · Mapa](../03-libro/19-mapa-de-confusiones.md) | todas | 3 |
| — | **Practice exams** (2 o más, cronometrados) + análisis de errores | — | todas | 3 por simulacro |

Las horas son de estudio con el libro, sin contar los videos del curso (unas 15 horas más si los mirás todos).

## Plan de estudio

**Lo que se hizo.** Una primera pasada por los videos del curso y después **unas dos semanas intensivas, a unas 2 horas por día**: un capítulo por día (dos los días más livianos), las preguntas de cada módulo al terminarlo, y los últimos días para el mapa de confusiones y los practice exams.

**Lo que se recomienda** para alguien que trabaja y arranca de cero, con **5 a 6 horas por semana**:

| Semana | Qué hacer |
|---|---|
| 0 | Leer [`01-el-examen`](../01-el-examen/README.md) y la guía oficial. Mirar los videos del curso a velocidad 1,25–1,5×, sin tomar notas, para tener el mapa general |
| 1 | Módulo 1 (capítulos 01–04) + preguntas del módulo 1 |
| 2 | Módulo 2 (capítulos 05–07) + preguntas. Módulo 3 (capítulos 08–09) |
| 3 | Módulo 3 (capítulos 10–11) + preguntas. Módulo 4 (capítulos 12–14) + preguntas |
| 4 | Módulo 5 (capítulos 15–18) + preguntas. Repasos mixtos |
| 5 | Mapa de confusiones. Practice exam 1 + análisis de errores. Repaso de temas flojos. Practice exam 2 + análisis. **Examen** |

**Reglas que funcionaron**
- **Un capítulo a la vez**, y no avanzar hasta entenderlo.
- **Las preguntas, al terminar el módulo completo**, no después de cada capítulo: así se mezclan los temas, como en el examen.
- **Cada error se analiza**: qué decía el enunciado, por qué tentó la opción equivocada y qué regla lo evita.
- **Dos o tres días antes del examen, nada nuevo**: solo el mapa de confusiones y los errores.

## Prácticas realizadas

- **90 preguntas tipo examen** escritas imitando el estilo real (18 por módulo, con escenarios, *Select TWO* y propuestas a evaluar), más **4 de repaso mixto**. Todas están en [`04-practica`](../04-practica/README.md).
- **Autoevaluación oral** al final de cada capítulo: 5 preguntas abiertas para explicar los conceptos sin mirar.
- **Practice exams de Udemy** cronometrados (60 preguntas, 120 minutos), con análisis de cada error.
- **Mapa de confusiones** armado a partir de los errores: los pares de conceptos que más se mezclan.
- **Uso real de Claude Code** en el trabajo diario con Bitflow, el flujo de desarrollo de Bitlogic basado en skills (ver [`05-experiencia`](../05-experiencia/README.md#aplicación-práctica-en-bitflow)).
