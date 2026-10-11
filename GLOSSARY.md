# Glossary

Este archivo es una referencia rápida. Los conceptos se aprenden en los capítulos, no acá.

## A

### Agent
Sistema donde el model participa dinámicamente en la selección de acciones necesarias para perseguir un goal.

### Agentic loop
Feedback loop donde el sistema alterna entre context/perception, reasoning/planning, action y observation.

### Augmented LLM
LLM combinado con capabilities como retrieval, tools y memory.

### Autonomy
Grado de libertad que tiene el model para decidir cómo perseguir un objetivo.

## C

### Client-executed tool
Tool cuya ejecución ocurre en la application/runtime del developer. Claude solicita su uso y la aplicación devuelve un `tool_result`.

### Context window
Información disponible para una inferencia/model turn dentro de los límites de contexto del model.

### Control flow
Orden y reglas que determinan qué paso del sistema se ejecuta a continuación.

## E

### Escalation
Handoff controlado hacia una persona o fallback system cuando el agent no debería o no puede continuar por sí mismo.

## H

### Hybrid architecture
Arquitectura que combina deterministic workflows con componentes agentic donde la autonomía agrega una capability necesaria.

## O

### Observation
Información que vuelve al model después de una acción y que puede modificar la siguiente decisión.

## R

### Runtime
Capa de software que rodea al model y ejecuta acciones, administra state, aplica guards y coordina nuevas model calls.

### Retry
Nuevo intento de una acción o estrategia ante un failure recoverable.

## S

### Schema
Contrato que describe la estructura y restricciones de datos.

### `stop_reason`
Metadata de una model response que indica por qué terminó ese turn. No equivale a una business-level termination condition.

### Spinning
Patrón donde el agent continúa consumiendo turns/tokens pero no produce meaningful progress hacia el goal.

## T

### Termination condition
Regla del sistema que determina cuándo un proceso/agent debe finalizar.

### Tool
Capability expuesta al model mediante una definición que describe qué hace y qué inputs acepta.

### `tool_result`
Bloque que devuelve al model el resultado asociado a una client tool invocation.

### `tool_use`
Bloque estructurado que expresa que Claude quiere utilizar una tool.

### Turn budget
Hard limit programático sobre la cantidad de turns/iterations permitidas.

## W

### Workflow
Sistema donde LLMs y tools siguen un control flow principalmente predefinido por el developer.

## Próximos términos

El glossary crece junto con los capítulos. No se agregan definiciones de temas que todavía no fueron enseñados sólo para “completar” una lista.
