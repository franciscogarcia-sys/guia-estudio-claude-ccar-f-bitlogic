# Protocolo de estudio y calidad

Cada sección debe cumplir estas reglas antes de considerarse completa.

## 1. Fuente de verdad

Prioridad:

1. **CCAR-F Exam Guide**
2. documentación oficial de Anthropic
3. curso de Jacob Bushong
4. fuentes complementarias de alta calidad

## 2. Estructura pedagógica fija

Cada capítulo técnico debe seguir, cuando aplique:

1. Objetivo
2. Por qué importa
3. Intuición
4. Conceptos
5. Terminología en English
6. Ejemplo concreto
7. Diagrama
8. Implementación / pseudocódigo
9. Trade-offs
10. Anti-patterns
11. 🔴 EXAM CRITICAL
12. Exam traps
13. Summary end-to-end
14. Preguntas de repaso
15. Respuestas ocultas con `<details>`
16. Fuentes

## 3. Criterio de claridad

Una persona con poca experiencia debe poder seguir el hilo sin conocer el tema previamente.

Se prioriza:

- ejemplos concretos antes que abstracciones;
- definiciones breves antes que excepciones;
- una idea por sección;
- diagramas para mecanismos con varias etapas;
- tablas sólo cuando comparan conceptos;
- términos en English siempre visibles.

## 4. Validación

Antes de consolidar una sección:

- verificar conceptos técnicos con documentación oficial;
- detectar información potencialmente desactualizada;
- separar claramente información del curso de complementos propios;
- corregir contradicciones;
- evitar memorizar detalles no incluidos en el scope del examen.

## 5. Práctica

Se agrega un lab cuando la experiencia hands-on ayuda materialmente.

Lenguaje principal: **Python**.

No se crean labs artificiales para contenido puramente conceptual.

## 6. Preguntas

Las respuestas quedan ocultas en GitHub:

```html
<details>
<summary>Ver respuesta</summary>

Respuesta y explicación.

</details>
```

Así se puede intentar responder antes de revelar la solución.

## 7. Cierre de sección

Checklist:

- [ ] contenido del curso procesado;
- [ ] documentación oficial contrastada;
- [ ] gaps relevantes completados;
- [ ] ejemplos claros;
- [ ] diagrama cuando aporta;
- [ ] trade-offs;
- [ ] exam traps;
- [ ] summary end-to-end;
- [ ] preguntas;
- [ ] glossary actualizado;
- [ ] blueprint coverage actualizado;
- [ ] fast review actualizado.
