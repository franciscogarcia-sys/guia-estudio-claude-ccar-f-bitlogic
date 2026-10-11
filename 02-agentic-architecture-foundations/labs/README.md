# Lab — Agentic Loop

Objetivo: llevar a código las ideas centrales de esta sección:

- `tool_use`;
- tool execution;
- `tool_result`;
- loop control;
- hard turn budget;
- finalización.

## Requisitos

```bash
python -m venv .venv
```

Activar el entorno virtual e instalar:

```bash
pip install anthropic
```

Definir:

```bash
ANTHROPIC_API_KEY=...
```

## Ejecutar

```bash
python agentic_loop.py
```

## Qué observar

1. Claude recibe una tool definition.
2. El model puede responder con `tool_use`.
3. Python ejecuta la función.
4. El resultado vuelve como `tool_result`.
5. El loop continúa.
6. `MAX_TURNS` se impone programáticamente.

> El objetivo del lab no es crear un production agent. Es visualizar correctamente el lifecycle.
