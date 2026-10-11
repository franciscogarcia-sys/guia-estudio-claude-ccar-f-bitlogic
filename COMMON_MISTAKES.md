# Common Mistakes / Exam Traps

## 1. “Si usa un LLM, es un agent”

Falso.

Un workflow puede usar muchos LLM calls y seguir siendo determinista si el developer define el control flow.

## 2. “Más autonomy siempre es mejor”

Falso.

Autonomy agrega capability, pero también cost, latency, auditability problems y failure surface.

## 3. “`tool_use` significa que Claude ejecutó la función”

Falso para client tools.

Claude solicita el uso. El runtime/application ejecuta la implementación.

## 4. “Un límite escrito en el prompt es un hard guard”

Falso.

Las invariants importantes deben enforced programmatically.

## 5. “Retry siempre es mejor que escalation”

Falso.

Retry sin nueva información puede convertirse en spinning.

## 6. “`stop_reason=end_turn` garantiza éxito de negocio”

Falso.

Sólo indica que terminó naturalmente ese model turn. La aplicación debe validar sus propios success criteria.

## 7. Regla inconsistente en la lecture `Choosing the Right Architecture`

La transcripción mezcla preguntas donde `yes` apunta a workflow con preguntas donde `yes` apunta a agent.

No memorizar la cuenta de respuestas. Usar señales conceptuales:

- steps predefinibles → workflow;
- output bien especificado → workflow;
- dynamic tool selection → agent;
- dynamic replanning → agent;
- mezcla de señales → hybrid.
