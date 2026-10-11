# Guía de estudio para Claude CCAR-F - Bitlogic

> Un recorrido guiado, práctico y progresivo para aprender **Claude Certified Architect – Foundations (CCAR-F)** desde los fundamentos hasta el examen.

---

## Bienvenido

Este repositorio no está pensado como un machete, un catálogo de definiciones ni una colección de apuntes sueltos.

La idea es otra: que puedas abrir el primer capítulo y avanzar como si tuvieras a un profesor particular sentado enfrente, construyendo cada concepto sobre el anterior.

Vamos a empezar por preguntas muy simples:

- ¿qué es realmente un LLM?
- ¿qué puede hacer solo y qué no?
- ¿qué cambia cuando le damos acceso a tools?
- ¿cuándo un sistema pasa de ser un workflow a comportarse como un agent?
- ¿cómo controlamos esa autonomía para que siga siendo confiable?

Y a medida que avancemos, esas respuestas se van a conectar con temas más grandes como **MCP**, **Claude Code**, **subagents**, **structured outputs**, **context management**, **reliability**, **CI/CD** y **production architecture**.

El objetivo no es que memorices términos. El objetivo es que, cuando llegues a una pregunta del examen o a un problema real de arquitectura, puedas pensar:

> “Entiendo qué está pasando, qué alternativas tengo y por qué una solución es mejor que otra.”

---

# Cómo está construida esta guía

El material se apoya en tres capas:

1. **CCAR-F Exam Guide y documentación oficial de Anthropic** — son la fuente de verdad.
2. **Curso de Jacob Bushong** — funciona como backbone para asegurar amplitud y cobertura.
3. **Fuentes complementarias confiables** — se incorporan cuando permiten explicar mejor, actualizar o profundizar un concepto.

No se reproducen transcripciones de Udemy. Cada capítulo se vuelve a escribir desde cero, con un orden pedagógico propio.

## Para quién está pensada

Para **Software Engineers desde junior hasta senior**.

No asumimos conocimiento previo de Claude, agents o MCP. Incluso los conceptos básicos se explican desde el principio. Al mismo tiempo, cada capítulo profundiza hasta un nivel útil para un engineer experimentado.

---

# El hilo conductor: BitSupport

Durante todo el recorrido vamos a construir un proyecto ficticio llamado **BitSupport**.

BitSupport empieza siendo algo muy pequeño:

> un asistente interno que ayuda a un equipo de ingeniería a responder consultas técnicas.

Al principio sólo podrá conversar. Después necesitaremos que consulte datos. Más adelante tendrá que usar tools, manejar errores, coordinar tareas, trabajar con MCP, explorar código, utilizar Claude Code, validar outputs y operar con controles de producción.

De esta forma, cada concepto nuevo tendrá una razón para existir.

```text
Chatbot
   ↓
Workflow
   ↓
Tools
   ↓
Agentic loop
   ↓
Planning
   ↓
Subagents
   ↓
MCP
   ↓
Claude Code
   ↓
Structured outputs
   ↓
Context & reliability
   ↓
Production-ready system
```

Cuando terminemos la guía, no sólo habremos leído los conceptos del examen: habremos construido un proyecto que los conecta de punta a punta.

👉 [Ir al laboratorio BitSupport](lab-bit-support/README.md)

---

# Roadmap de lectura

> **La regla es simple:** empezá arriba y seguí los enlaces. El repositorio te va indicando qué leer y qué hacer después.

| Orden | Capítulo | Estado |
|---:|---|---|
| 0 | [Antes de empezar — el mapa mínimo para entender Claude](00-prerequisites/README.md) | ✅ |
| 1 | [El examen CCAR-F — qué estamos aprendiendo y para qué](01-exam-overview/README.md) | ✅ |
| 2 | [De un LLM a un Agent — Agentic Architecture Foundations](02-agentic-architecture-foundations/README.md) | ✅ |
| 3 | Task Decomposition & Planning | ⏳ Siguiente |
| 4 | Multi-Agent Orchestration | ⬜ |
| 5 | Reliability & Human Oversight | ⬜ |
| 6 | Tool Design Fundamentals | ⬜ |
| 7 | Building MCP Servers | ⬜ |
| 8 | MCP Production & Built-in Tools | ⬜ |
| 9 | Claude Code — Architecture & Setup | ⬜ |
| 10 | Claude Code — `CLAUDE.md` Configuration | ⬜ |
| 11 | Claude Code — Slash Commands, Skills & Subagents | ⬜ |
| 12 | Claude Code — Hooks, SDK & CI/CD | ⬜ |
| 13 | Writing Effective Prompts | ⬜ |
| 14 | Advanced Prompting Techniques | ⬜ |
| 15 | Structured Output & Evaluation | ⬜ |
| 16 | The Context Window | ⬜ |
| 17 | Multi-Agent Failure Modes | ⬜ |
| 18 | Cross-Session Knowledge & Coherence | ⬜ |
| 19 | Confidence, Sampling & Provenance | ⬜ |
| 20 | Practice Exams & Final Review | ⬜ |

👉 [Ver roadmap detallado](ROADMAP.md)

---

# Cómo se lee cada capítulo

Los capítulos están escritos como una explicación continua. Las definiciones aparecen **cuando la historia las necesita**, no como un diccionario.

Durante la lectura vas a encontrar cuatro tipos de bloques:

### 🔴 EXAM CRITICAL
Conceptos que tenés que poder reconocer, explicar y aplicar en un scenario del examen.

### 💭 Pensalo antes de seguir
Una pregunta conceptual corta. Intentá responder antes de desplegar la solución.

### 🧪 Probalo vos
Un ejercicio concreto que aplica lo que acabás de aprender al proyecto BitSupport.

### 🧩 Challenge
Un problema más abierto, parecido a una decisión real de arquitectura o a un scenario de examen.

Las respuestas se mantienen ocultas con bloques desplegables para que puedas pensar antes de verlas.

---

# Material de apoyo

Estos archivos acompañan el recorrido, pero **no reemplazan los capítulos**:

- [Blueprint Coverage](BLUEPRINT_COVERAGE.md) — qué task statements ya cubrimos.
- [Glossary](GLOSSARY.md) — términos técnicos para consulta rápida.
- [Common Mistakes](COMMON_MISTAKES.md) — errores recurrentes y exam traps.
- [Fast Review](FAST_REVIEW.md) — repaso para la etapa final, no material principal de aprendizaje.
- [Course Map](COURSE_MAP.md) — trazabilidad entre Jacob y esta guía.
- [Progress](PROGRESS.md) — estado actual del recorrido.
- [Study Protocol](STUDY_PROTOCOL.md) — estándar pedagógico y técnico que debe cumplir cada capítulo.

---

# Regla de calidad

Un capítulo no está terminado porque aparezcan todos los conceptos.

Está terminado cuando una persona puede leerlo de principio a fin y responder:

1. **¿qué problema estábamos tratando de resolver?**
2. **¿por qué apareció este concepto?**
3. **¿cómo funciona?**
4. **¿cómo se conecta con lo que aprendimos antes?**
5. **¿cuándo lo usaría y cuándo no?**
6. **¿qué podría salir mal?**
7. **¿cómo lo aplicaría en código o arquitectura?**
8. **¿cómo podría aparecer en CCAR-F?**

---

## Empezar

Si es tu primera vez en la guía:

### 👉 [Capítulo 0 — Antes de empezar](00-prerequisites/README.md)

Si ya conocés los fundamentos básicos de APIs, JSON y LLMs, igualmente recomendamos una lectura rápida porque allí presentamos el proyecto BitSupport y el mental model que usaremos durante todo el libro.
