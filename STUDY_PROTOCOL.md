# Protocolo editorial y de estudio

Este documento define cómo se escribe cada capítulo de la guía.

La principal regla es:

> **No estamos escribiendo apuntes. Estamos escribiendo un libro técnico guiado.**

---

# 1. Para quién escribimos

El lector es un Software Engineer, desde junior hasta senior.

Eso implica dos cosas simultáneamente:

- no asumir conocimiento previo de Claude, agents, MCP o Claude Code;
- no simplificar tanto que el material pierda precisión técnica.

Cada concepto debe poder ser entendido por alguien que recién empieza y seguir siendo útil para alguien experimentado.

---

# 2. La narrativa manda sobre el índice

No se empieza una sección diciendo:

```text
Definición A
Definición B
Definición C
```

Se empieza con un problema o una necesidad.

Ejemplo:

> “BitSupport ya puede responder preguntas, pero ahora un usuario quiere saber si un deploy falló. Claude no tiene acceso al pipeline. ¿Qué necesitamos agregar?”

Sólo entonces aparece el concepto de **tool use**.

La secuencia preferida es:

```text
problema
→ intuición
→ concepto
→ mecanismo
→ ejemplo
→ aplicación
→ trade-off
→ conexión con lo anterior
```

---

# 3. Cada concepto debe tener una causa

Antes de introducir una palabra nueva, el texto debe responder implícita o explícitamente:

> **¿por qué necesitamos aprender esto ahora?**

Si un término puede eliminarse sin romper la comprensión del capítulo, probablemente todavía no sea el momento de introducirlo.

---

# 4. Proyecto transversal: BitSupport

Todos los capítulos deben intentar conectar el contenido con **BitSupport**, el laboratorio principal.

BitSupport evoluciona junto con el libro.

```text
simple assistant
→ tools
→ workflows
→ agent
→ planning
→ subagents
→ MCP
→ Claude Code
→ reliability
→ production
```

Los ejemplos independientes están permitidos cuando ayudan a explicar mejor una idea, pero el lector siempre debe poder volver al proyecto central.

---

# 5. Anatomía de un capítulo

No es una plantilla rígida, pero un buen capítulo suele tener:

1. apertura narrativa;
2. problema que motiva el tema;
3. construcción progresiva del mental model;
4. diagramas;
5. ejemplos concretos;
6. conexión con BitSupport;
7. código o pseudocódigo cuando corresponda;
8. 💭 **Pensalo antes de seguir**;
9. 🧪 **Probalo vos**;
10. 🧩 **Challenge**;
11. 🔴 **EXAM CRITICAL**;
12. trade-offs y failure modes;
13. exam traps;
14. summary narrativo end-to-end;
15. preguntas finales con respuestas ocultas;
16. transición explícita al próximo capítulo.

---

# 6. Respuestas ocultas

GitHub permite utilizar:

```html
<details>
<summary>Ver respuesta</summary>

Respuesta y explicación.

</details>
```

Cuando una pregunta es multiple-choice, la explicación debe cubrir:

- por qué la correcta es mejor;
- por qué cada distractor es peor;
- qué señal del scenario permite decidir.

---

# 7. Visuales

Usar el formato que mejor explique la idea:

- **Mermaid** para arquitecturas, flows y sequence diagrams;
- diagramas propios cuando Mermaid no alcance;
- screenshots cuando la UI sea parte del aprendizaje;
- imágenes externas sólo si agregan valor y su uso es apropiado.

Una imagen nunca debe estar sólo para decorar.

---

# 8. Código

Lenguaje principal: **Python**.

El código debe aparecer cuando ayuda a entender el mecanismo.

Primero se explica la idea. Después se muestra el código.

No asumir que el lector entiende una API sólo porque ve un snippet.

---

# 9. Jerarquía de fuentes

1. **CCAR-F Exam Guide**
2. documentación oficial y engineering material de Anthropic
3. curso de Jacob Bushong
4. fuentes complementarias confiables

Jacob es el backbone de cobertura, pero no es la source of truth.

Si hay:

- información desactualizada;
- una simplificación excesiva;
- una contradicción;
- un gap importante;

se corrige o complementa y se registra cuando corresponde.

---

# 10. Distinción de importancia

### 🔴 EXAM CRITICAL
Hay que dominarlo.

### 🟠 IMPORTANT
Necesario para razonar correctamente.

### 🟡 CONTEXT
Ayuda a formar el mental model, pero tiene menor prioridad de memorización.

No abusar de estas etiquetas. Si todo es crítico, nada es crítico.

---

# 11. Summary end-to-end

El cierre no debe ser una lista de definiciones.

Debe reconstruir la historia.

Ejemplo:

> “Empezamos con un LLM que sólo podía generar una respuesta. Cuando quisimos consultar información externa apareció el action–environment gap. Las tools cerraron ese gap, pero necesitamos un runtime que ejecutara las acciones y devolviera observations. Esa realimentación creó el agentic loop…”

El lector debe terminar sintiendo que puede volver a contar el capítulo con sus propias palabras.

---

# 12. Criterio de cierre

Un capítulo pasa a **COMPLETO** sólo si:

- [ ] el contenido base fue procesado;
- [ ] la documentación oficial fue contrastada;
- [ ] se completaron gaps relevantes;
- [ ] existe un hilo narrativo;
- [ ] los conceptos se conectan entre sí;
- [ ] hay ejemplos;
- [ ] hay visuales cuando aportan;
- [ ] existe aplicación a BitSupport;
- [ ] hay ejercicios;
- [ ] hay preguntas con respuestas razonadas;
- [ ] existe summary end-to-end;
- [ ] está clara la transición al próximo capítulo;
- [ ] Blueprint Coverage fue actualizado;
- [ ] Glossary fue actualizado;
- [ ] Fast Review fue actualizado.
