# Roadmap — el recorrido completo

Este archivo es el mapa de lectura de la guía.

No hace falta saltar entre carpetas buscando qué estudiar. Seguí el recorrido en orden.

---

# Parte 0 — Prepararnos para aprender

## Capítulo 0 — Antes de empezar

👉 [Leer capítulo](00-prerequisites/README.md)

Vamos a construir un mental model mínimo:

- LLM;
- API;
- JSON;
- schema;
- context;
- runtime;
- tools.

También presentamos **BitSupport**, el proyecto que evolucionará durante toda la guía.

---

# Parte 1 — Entender el examen

## Capítulo 1 — CCAR-F Exam Overview

👉 [Leer capítulo](01-exam-overview/README.md)

Antes de estudiar tecnología, entendemos qué intenta medir el examen, cómo están organizados los domains y por qué CCAR-F evalúa trade-offs en scenarios.

---

# Parte 2 — Agentic Architecture & Orchestration

Este domain representa **27%** del blueprint.

## Capítulo 2 — De un LLM a un Agent

👉 [Leer capítulo](02-agentic-architecture-foundations/README.md)

Aprendemos:

- workflow vs agent;
- augmented LLM;
- tools;
- agentic loop;
- observations;
- loop control;
- retry;
- escalation;
- cuándo no usar agents.

## Capítulo 3 — Task Decomposition & Planning

**Siguiente capítulo.**

Vamos a aprender cómo convertir un goal grande en subtasks ejecutables y cuándo usar sequential, parallel o adaptive planning.

## Capítulo 4 — Multi-Agent Orchestration

Coordinator, subagents, isolation, handoffs y session continuity.

## Capítulo 5 — Reliability & Human Oversight

Retries, fallbacks, validation, hooks, safety boundaries y human review.

---

# Parte 3 — Tool Design & MCP

## Capítulo 6 — Tool Design Fundamentals

Cómo diseñar tools que Claude pueda seleccionar y usar confiablemente.

## Capítulo 7 — Building MCP Servers

De una tool local a una integración reusable mediante MCP.

## Capítulo 8 — MCP in Production & Built-in Tools

Transports, authentication, least privilege, versioning y production reliability.

---

# Parte 4 — Claude Code

## Capítulo 9 — Architecture & Setup
## Capítulo 10 — `CLAUDE.md`
## Capítulo 11 — Slash Commands, Skills & Subagents
## Capítulo 12 — Hooks, Agent SDK & CI/CD

---

# Parte 5 — Prompt Engineering & Structured Output

## Capítulo 13 — Writing Effective Prompts
## Capítulo 14 — Advanced Prompting
## Capítulo 15 — Structured Output & Evaluation

---

# Parte 6 — Context Management & Reliability

## Capítulo 16 — The Context Window
## Capítulo 17 — Multi-Agent Failure Modes
## Capítulo 18 — Cross-Session Knowledge & Coherence
## Capítulo 19 — Confidence, Sampling & Provenance

---

# Parte 7 — Cierre

## Capítulo 20 — Practice Exams & Final Review

Cuando lleguemos acá:

1. auditaremos los 30 task statements;
2. revisaremos weak areas;
3. haremos mocks;
4. actualizaremos el error log;
5. usaremos Fast Review;
6. simularemos el examen.

---

# El laboratorio corre en paralelo

Cada parte modifica el mismo sistema:

👉 [BitSupport Lab](lab-bit-support/README.md)

La intención es que el libro y el proyecto terminen juntos.

```text
leer
↓
entender
↓
aplicar
↓
romper
↓
corregir
↓
conectar con el examen
↓
seguir
```
