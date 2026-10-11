# 00 — Prerequisites

Este bloque existe para que alguien sin experiencia previa pueda seguir el resto de la guía.

No forma parte directamente del blueprint.

## API

Una **API (Application Programming Interface)** permite que un programa interactúe con otro mediante un contrato definido.

Ejemplo:

```text
Application
    ↓ HTTP request
Claude API
    ↓ HTTP response
Application
```

## JSON

Formato de datos muy utilizado por APIs y tools.

```json
{
  "product_id": "ABC-123",
  "quantity": 2
}
```

## Schema

Un **schema** define la forma esperada de datos.

```text
quantity
→ integer
→ required
→ minimum = 1
```

## LLM

**Large Language Model**.

Recibe input/context y produce output probabilístico.

Un LLM por sí solo no implica:

- external tool execution;
- durable memory;
- database access;
- side effects.

## Token

Unidad utilizada para representar texto internamente.

El número de tokens afecta:

- context consumption;
- cost;
- latency.

## Context window

Cantidad máxima de información que puede mantenerse disponible para una inferencia.

## CLI

**Command-Line Interface**.

Ejemplo:

```bash
python app.py
```

## Runtime

Código que rodea al model y se encarga de tareas que el model no ejecuta por sí mismo:

- llamar tools;
- mantener state;
- imponer límites;
- manejar errores;
- validar outputs.

## Summary

El resto del curso parte de una idea clave:

```text
LLM
+
application/runtime
+
tools/data
=
AI system
```

El examen evalúa muchas decisiones sobre **cómo diseñar correctamente ese sistema alrededor del model**.
