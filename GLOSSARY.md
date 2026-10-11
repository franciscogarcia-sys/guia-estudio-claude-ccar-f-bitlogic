# Glossary

## A

### Agent
Sistema en el que el modelo participa en la selección dinámica de acciones para perseguir un objetivo, normalmente dentro de un feedback loop.

### Agentic loop
Ciclo repetido de observar contexto, razonar/planificar, actuar y observar el resultado.

### Augmented LLM
LLM combinado con capacidades como retrieval, tools y memory.

## C

### Client tool
Tool cuya ejecución es responsabilidad de la aplicación del usuario.

### Context window
Conjunto de tokens disponibles para la inferencia actual del modelo.

## O

### Observation
Resultado de una acción/tool que vuelve al contexto y puede influir la siguiente decisión.

## S

### `stop_reason`
Campo de una model response que indica por qué terminó esa respuesta concreta. No es equivalente a una business-level termination condition.

### Spinning
Patrón donde el agent consume turns/tokens pero no reduce de forma significativa la distancia al objetivo.

## T

### `tool_result`
Bloque que devuelve al modelo el resultado de un `tool_use`.

### `tool_use`
Bloque estructurado emitido cuando Claude solicita utilizar una tool.

### Turn budget
Límite programático sobre la cantidad de iteraciones/turns permitidas.

## W

### Workflow
Control flow principalmente definido por el developer at design time, aun cuando use uno o varios LLM calls.
