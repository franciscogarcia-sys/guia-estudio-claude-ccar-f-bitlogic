# Capítulo 18 · 5D · Udemy 19 — Human Oversight, Confidence, and Provenance (revisión humana, confianza y procedencia)

*Tareas oficiales 5.5 y 5.6 · Cuarto y último capítulo del módulo 5 y del libro*

---

## Dónde estamos

Seguimos en el **módulo 5: Context Management & Reliability**. 5A, 5B y 5C ya están escritos. Este capítulo cubre dos tareas, de 2,5% cada una:
- **5.5** Design human review workflows and confidence calibration (diseñar la revisión humana y calibrar la confianza).
- **5.6** Preserve information provenance and handle uncertainty in multi-source synthesis (conservar de dónde sale cada dato y manejar la incertidumbre cuando se combinan varias fuentes).

### Cómo leer este capítulo

Todo lo que leés acá **vale para el examen**, salvo que diga lo contrario. Cuando algo sale solo del curso (útil para entender, pero no central), lo marco con **📘 Curso**. Cuando Jacob dice algo distinto de lo que evalúa la guía, aparece un recuadro así:

> ⚠️ **En el curso vas a escuchar otra cosa.** … **Para el examen: …**

### Un aviso sobre este capítulo

El curso explica bien la confianza por campo, la calibración y el mapeo de cada dato a su fuente. Pero hay **dos diferencias importantes** con la guía:
- **Para qué sirve el muestreo estratificado.** El curso lo usa para encontrar más errores; la guía, para **medir** si lo que se automatiza sigue bien.
- **Qué hacer cuando dos fuentes se contradicen.** El curso propone reglas automáticas para elegir una; la guía dice **anotar el conflicto y que decida el coordinador**.

Además, al curso le faltan las fechas de las fuentes, separar lo establecido de lo disputado y el formato según el tipo de contenido.

5.5 cae en el escenario **6 (Structured Data Extraction)**, el de las facturas. 5.6 cae en el **3 (Multi-Agent Research System)**, el del informe de mercado.

## De dónde venimos

Ya viste varias piezas:
- **4C:** `conflict_detected` para un documento que se contradice, y la **confianza por hallazgo con umbrales calibrados** para enrutar revisiones.
- **5A:** los subagentes devuelven **metadatos** (fecha, fuente, método).
- **5B:** la confianza autoinformada **no** sirve para decidir cuándo escalar.

Este capítulo cierra esas ideas. Responde **cuándo se puede confiar en lo que Claude extrae sin que lo revise una persona**, y **cómo se conserva de dónde sale cada dato** cuando se juntan muchas fuentes.

## Mapa del capítulo

**Parte 1 — Revisión humana y confianza (tarea 5.5).**
1. Una accuracy alta puede esconder un segmento malo.
2. Confianza por campo, calibrada.
3. Muestreo estratificado de lo que se automatiza.
4. Qué va a revisión humana.

**Parte 2 — Procedencia en una síntesis (tarea 5.6).**

5. Claim-source mappings: cada dato con su fuente.
6. Fuentes que se contradicen: anotar, no elegir.
7. Fechas: no confundir un cambio con una contradicción.
8. Cómo se arma el informe final.

---

# Parte 1 — Revisión humana y confianza

## Tema 1 — Aggregate accuracy (accuracy agregada): un número alto puede esconder un segmento malo

### Qué es

Imaginá que el sistema de extracción de facturas de TiendaX tiene un **97% de accuracy** (aciertos) en total. Parece listo para dejar de revisar a mano. El problema es que ese número es un **promedio**. Si el 90% de los documentos son facturas de proveedores grandes (que salen casi perfectas) y el 10% son emails de proveedores chicos (que salen mal la mitad de las veces), el total igual da alto. El promedio **esconde** el segmento malo.

La guía pide **medir la accuracy por tipo de documento y por campo**, y verificar que el desempeño sea parejo en todos los segmentos **antes de automatizar** o reducir la revisión humana. Un **segmento** es un grupo con algo en común: un tipo de documento, un proveedor, un campo.

### Ejemplo

| Segmento | Documentos | Accuracy |
|---|---|---|
| Facturas PDF de proveedores grandes | 9.000 | 99,5% |
| Emails de proveedores chicos | 800 | 74% |
| Notas de crédito | 200 | 88% |
| **Total** | **10.000** | **97%** |

Por campo pasa lo mismo: `total_cents` puede tener 99,8% y `due_date` 81%. Con esta tabla, el equipo automatiza solo las facturas PDF y deja los emails y las notas de crédito con revisión.

### Para el examen

- "97% de accuracy, automaticemos" → primero **medir por tipo de documento y por campo**.
- Distractores: automatizar por el número global, o "subir el umbral" sin mirar los segmentos.

### Cómo se une

Para decidir documento por documento qué se revisa, hace falta saber qué tan seguro está el modelo de cada campo, y que esa seguridad sea confiable.

---

## Tema 2 — Field-level confidence (confianza por campo), calibrada

### Qué es

En lugar de un solo puntaje por documento, la guía pide que el modelo devuelva una **confianza por cada campo**. Un puntaje único esconde el campo débil: una factura puede tener el proveedor y el total seguros, y el vencimiento dudoso. Se hace en la misma extracción, agregando la confianza al schema.

Pero **esa confianza no se puede usar tal cual**. Ya lo viste en la Q3: la confianza que el modelo se asigna está mal calibrada. Un campo con confianza 0,9 puede estar bien solo el 60% de las veces. Por eso la guía pide **calibrar los umbrales con un labeled validation set**: un conjunto de documentos cuya respuesta correcta ya conocés (etiquetados por personas). Corrés el modelo sobre ellos, comparás su confianza con los aciertos reales y elegís el umbral con datos. Por ejemplo, "con confianza ≥ 0,93, `due_date` acierta el 99% de las veces".

**Cómo se cierra la tensión con 5B.** Usar la confianza **cruda** para decidir algo es un distractor (Q3). Usarla **por campo y con umbrales calibrados** para decidir qué extracciones revisa una persona es exactamente lo que pide 5.5. Pero ojo: para decidir **cuándo escalar** un caso de soporte (5.2), la respuesta de la Q3 **no** es calibrar la confianza, sino **criterios explícitos con ejemplos**. Y en un revisor de código (4.1), filtrar por confianza rinde menos que los criterios por categoría.

Un detalle técnico: la API no trae un campo nativo de confianza. Es un valor que Claude informa porque se lo pedís en el schema, no una probabilidad interna del modelo. Por eso hay que calibrarlo.

### Cómo se configura

```json
{
  "supplier":        {"value": "Distribuidora Norte", "confidence": 0.98},
  "total_cents":     {"value": 9000000, "confidence": 0.97},
  "due_date":        {"value": "2026-12-31", "confidence": 0.71}
}
```

📘 Curso: Jacob sugiere recalibrar después de cada cambio de modelo o de prompt. Es razonable, pero no está en la guía.

### Para el examen

- Confianza **por campo**, no un puntaje por documento.
- Umbrales **calibrados con un set etiquetado**; nunca la confianza cruda.

### Cómo se une

Con umbrales calibrados, lo de confianza alta se acepta solo. Pero ¿cómo sabés que lo que se acepta solo **sigue** estando bien con el tiempo?

---

## Tema 3 — Stratified random sampling (muestreo aleatorio estratificado) de lo que se automatiza

### Qué es

Una vez que las extracciones de confianza alta se aceptan sin revisión, **nadie las mira**. Si un proveedor cambia el formato de sus facturas y el modelo empieza a equivocarse con confianza alta, nadie se entera. La guía pide seguir **midiendo** ese tramo con un **muestreo aleatorio estratificado de las extracciones de alta confianza**, de forma continua. Sirve para dos cosas:
- **Medir la tasa de error real** de lo que se está aceptando solo.
- **Detectar patrones de error nuevos** que nadie había visto.

**Estratificado** significa que la muestra se toma por grupos (por tipo de documento, por proveedor, por campo) y al azar dentro de cada grupo. Así los grupos chicos o de más riesgo no quedan afuera, como podría pasar con una muestra al azar sobre todo el volumen.

> ⚠️ **En el curso vas a escuchar otra cosa.** Jacob usa el muestreo estratificado para concentrar a los revisores en lo que "más probablemente esté mal" y "atrapar más errores por hora de revisor". **Para el examen:** el muestreo estratificado de la guía es de las extracciones **de alta confianza**, para **medir la tasa de error y detectar patrones nuevos** en lo que se automatiza. Mandar lo dudoso a revisión es otra cosa (Tema 4). Si una opción dice "revisar solo las de baja confianza", es un distractor: los errores confiados nunca se verían.

### Ejemplo

TiendaX acepta sin revisión las facturas PDF con confianza alta. Arma estratos por tipo de documento y proveedor, y cada semana toma al azar 20 extracciones de cada estrato para que una persona las revise. En noviembre aparecen 6 errores en un mismo proveedor, todos en `due_date`: cambió el formato de su factura. Sin el muestreo, esos errores habrían seguido entrando al sistema de pagos.

### Para el examen

- ¿Cómo saber si lo que se acepta solo sigue bien, o detectar errores nuevos? → **muestreo aleatorio estratificado de las extracciones de alta confianza**, continuo.
- Distractores: revisar solo las de baja confianza, una muestra al azar sin estratos, o validar una sola vez antes del lanzamiento.

### Cómo se une

El muestreo mide el tramo automático. El tramo dudoso va directo a una persona.

---

## Tema 4 — Routing to human review (qué va a revisión humana)

### Qué es

Los revisores son pocos y su tiempo es limitado. La guía pide **mandar a revisión humana** dos tipos de casos, **priorizando** esa capacidad limitada:
- Las extracciones con **confianza baja** (según los umbrales calibrados del Tema 2).
- Los documentos con **fuentes ambiguas o contradictorias**: aunque el modelo esté seguro, si el propio documento se contradice (dos fechas de vencimiento distintas), lo tiene que ver una persona. Es el `conflict_detected` de 4C.

Mandar **todo** a revisión no escala, y repartir el tiempo de los revisores en orden de llegada desperdicia su atención en casos fáciles.

📘 Curso: Jacob arma una **cola de revisión** donde cada corrección de una persona queda registrada. Las correcciones se convierten en pares etiquetados para recalibrar, y los rechazos muestran qué tipos de documento maneja mal el sistema.

### Ejemplo

Cada mañana, la cola de revisión de TiendaX se arma así:
1. Primero, las facturas con `conflict_detected`.
2. Después, los campos con confianza por debajo del umbral calibrado, empezando por los montos más grandes.

Las facturas de confianza alta y sin conflictos pasan solas, y el muestreo del Tema 3 las vigila.

### Para el examen

- A revisión humana → **confianza baja (calibrada)** o **fuentes ambiguas o contradictorias**, priorizando la capacidad de los revisores.
- Distractores: revisar todo, revisar en orden de llegada o usar la confianza cruda.

### Cómo se une

Hasta acá, cómo se confía en un dato extraído. La tarea 5.6 pregunta otra cosa: cuando el dato viene de **muchas fuentes**, cómo se sabe **de dónde** salió cada uno.

---

# Parte 2 — Procedencia en una síntesis

## Tema 5 — Claim-source mappings (cada afirmación con su fuente)

### Qué es

En el sistema de investigación, los subagentes leen fuentes y el agente de síntesis arma el informe. En cada paso donde algo **se resume o se comprime**, se puede perder **de dónde salió cada dato**. Un subagente que devuelve "el mercado de heladeras creció un 12%", sin decir de qué fuente salió, ya perdió la **procedencia** (provenance).

La guía pide dos cosas:
1. Los subagentes devuelven **claim-source mappings** estructurados: cada afirmación con su fuente (**la URL, el nombre del documento y el fragmento relevante**).
2. El agente de síntesis **conserva y combina** esos mappings al juntar los hallazgos. No los descarta al redactar.

Una **lista de fuentes al final** del informe no alcanza: dice qué se leyó, pero no qué dato salió de cada fuente.

### Cómo se configura

```json
{
  "claim": "Las ventas de heladeras no frost crecieron un 12% interanual.",
  "source_url": "https://ejemplo.org/informe-q3",
  "document": "Informe de consumo Q3 — Cámara de Comercio",
  "excerpt": "…las unidades vendidas de heladeras no frost aumentaron 12% respecto del mismo trimestre…",
  "published": "2026-10-05"
}
```

📘 Curso: Jacob propone poner el puntero a la fuente **junto a cada afirmación** en el texto, no al final del párrafo, y auditar una muestra de las citas para detectar fuentes inventadas. (La documentación tiene además una **citations API**, que hace que Claude cite partes exactas de los documentos que le pasás. La guía no la nombra, y no se puede usar junto con structured outputs: la API devuelve error 400.)

### Para el examen

- La atribución se pierde en el informe final → los subagentes devuelven **claim-source mappings** (URL, documento, fragmento) y la síntesis **los conserva y combina**.
- Distractores: una bibliografía al final, o que los subagentes devuelvan un resumen en prosa.

### Cómo se une

Con cada dato atado a su fuente, aparece la situación difícil: dos fuentes confiables que dicen cosas distintas.

---

## Tema 6 — Conflicting sources (fuentes que se contradicen): anotar, no elegir

### Qué es

Dos fuentes creíbles dan cifras distintas: una dice que el mercado creció un 12% y otra un 8%. La guía es clara: **anotar el conflicto con la atribución de cada fuente**, en vez de **elegir un valor arbitrariamente**. Lo que se prohíbe es que alguien elija en silencio y descarte el otro valor; el coordinador sí puede reconciliar, con criterio y dejando a la vista las dos fuentes. Y dice **quién** decide. El subagente que analiza los documentos **completa su análisis con los dos valores incluidos y marcados como conflicto**, y el **coordinador** decide cómo reconciliarlos antes de pasarlos a la síntesis.

Hay tres errores típicos:
- **Elegir uno**: "el más reciente", "el de la fuente más prestigiosa".
- **Promediar**: inventa un 10% que ninguna fuente dijo.
- **Que el subagente se frene** hasta que alguien resuelva el conflicto.

Es la misma idea que `conflict_detected` en 4C, pero entre fuentes: **los conflictos se marcan, no se resuelven en silencio**.

> ⚠️ **En el curso vas a escuchar otra cosa.** Jacob propone aplicar una estrategia de resolución explícita: "prefer-newer" (quedarse con el más nuevo), "prefer-authoritative" (con el de la fuente más autorizada) o escalar a una persona. **Para el examen:** la guía pide **no elegir arbitrariamente**. Se incluyen los dos con su fuente, se anotan como conflicto y decide el coordinador. Lo que choca con la guía es aplicar "prefer-newer" o "prefer-authoritative" como **regla automática**; escalar a una persona no la contradice. Además, quedarse con el más nuevo puede ser un error: a veces los dos valores no se contradicen, son de fechas distintas (Tema 7). Lo que sí coincide con el curso es "nunca promediar en silencio" y "registrar cada conflicto".

### Ejemplo

El subagente de análisis devuelve:

```json
{
  "metric": "crecimiento de ventas de heladeras 2026",
  "values": [
    {"value": "12%", "source": "Cámara de Comercio, Informe Q3", "published": "2026-10-05", "method": "relevamiento de 40 comercios"},
    {"value": "8%",  "source": "Consultora Delta", "published": "2026-10-20", "method": "datos de facturación de 3 cadenas"}
  ],
  "conflict": true
}
```

El coordinador ve que las dos fuentes miden cosas distintas (comercios relevados vs. facturación de cadenas). Decide presentar los dos valores en la sección de hallazgos disputados, explicando la diferencia de método.

### Para el examen

- Dos fuentes creíbles con cifras distintas → **los dos valores, con su fuente, anotados como conflicto; decide el coordinador**.
- Distractores: elegir el más nuevo o el más autorizado, promediar, o que el subagente resuelva o se frene.

### Cómo se une

Antes de llamar "conflicto" a dos cifras distintas, hay que mirar **cuándo** se midió cada una.

---

## Tema 7 — Temporal data (datos con fecha): no confundir un cambio con una contradicción

### Qué es

Una fuente dice que la participación de mercado de una marca es del 30%, y otra dice 22%. Parece una contradicción. Pero si una es de 2024 y la otra de 2026, **no se contradicen**: la marca perdió mercado. Sin las fechas, el sistema puede marcar como conflicto lo que en realidad es una **tendencia**, o mezclar datos viejos con nuevos como si fueran del mismo momento.

Por eso la guía pide que los subagentes incluyan en su salida estructurada la **fecha de publicación o de recolección de los datos** de cada fuente. Ojo: es la fecha **de la fuente**, no la fecha en que corrió el sistema.

### Ejemplo

Sin fechas, el informe de TiendaX decía: "Hay datos contradictorios sobre la participación de la Marca X (30% vs. 22%)". Con fechas: "La participación de la Marca X bajó del 30% (relevamiento 2024) al 22% (relevamiento 2026)". Es un hallazgo útil, no un conflicto.

### Para el examen

- Cifras distintas que podrían ser de momentos distintos → **exigir fechas de publicación o recolección** en la salida de los subagentes.
- Distractores: tratarlas como contradicción, quedarse con la más nueva sin mirar, o usar la fecha de la corrida.

### Cómo se une

Con datos atribuidos, conflictos anotados y fechas, queda armar el informe final de forma que todo eso se vea.

---

## Tema 8 — Cómo se arma el informe final

### Qué es

La guía pide dos cosas sobre el informe.

**Separar lo establecido de lo disputado.** El informe tiene **secciones explícitas** para los hallazgos **bien establecidos** (varias fuentes coinciden) y para los **disputados** (las fuentes no coinciden). Un hallazgo que tiene **una sola fuente** no se borra: se presenta como menos respaldado. Además, el informe **conserva cómo la fuente caracterizó el dato** y el **contexto metodológico**: si la fuente dijo "estimación preliminar", el informe no lo convierte en un hecho firme. No se reescribe todo con una voz segura ni se borran los hallazgos de una sola fuente: van a la sección que corresponde.

**El formato según el tipo de contenido.** No todo se presenta igual:
- Los **datos financieros** van en **tablas**.
- Las **noticias**, en **prosa**.
- Los **hallazgos técnicos**, en **listas estructuradas**.

Convertir todo a un único formato (todo en viñetas, todo en párrafos) hace que cada tipo de información se lea peor.

Esto se suma a las **anotaciones de cobertura** que viste en 5B: qué temas tienen huecos porque faltó una fuente.

### Ejemplo

El informe de mercado de TiendaX queda así:
1. **Hallazgos establecidos** (en lista): "Las heladeras no frost lideran las ventas del segmento (4 fuentes)".
2. **Hallazgos disputados**: el crecimiento del 12% vs. 8%, con la fuente, la fecha y el método de cada uno.
3. **Precios por marca** (en tabla).
4. **Novedades del sector** (en prosa): la apertura de una nueva cadena.
5. **Cobertura**: aires acondicionados sin datos, porque la fuente principal no respondió.

### Para el examen

- Informe con fuentes que coinciden y otras que no → **secciones de hallazgos establecidos y disputados**, conservando cómo lo dijo cada fuente y su metodología.
- Formato → **según el tipo de contenido**: tablas para finanzas, prosa para noticias, listas para hallazgos técnicos.
- Distractores: un formato uniforme para todo, o reescribir los hallazgos con más certeza de la que tenía la fuente.

---

## Cómo se une todo

Una accuracy total alta puede esconder un tipo de documento o un campo malo: hay que **medir por segmento antes de automatizar** (Tema 1). La confianza se pide **por campo** y los umbrales se **calibran con un set etiquetado**, nunca con la confianza cruda (Tema 2). Lo que se acepta solo se vigila con **muestreo estratificado de las de alta confianza**, para medir el error y detectar patrones nuevos (Tema 3). Y a revisión humana va lo de **baja confianza** y lo de **fuentes ambiguas o contradictorias**, priorizando a los revisores (Tema 4).

En una síntesis, cada dato viaja con su fuente (**claim-source mappings**) y la síntesis los conserva (Tema 5). Si dos fuentes se contradicen, se **anotan las dos** y decide el coordinador (Tema 6). Las **fechas** evitan confundir un cambio con una contradicción (Tema 7). Y el informe separa lo **establecido** de lo **disputado**, con el formato adecuado para cada tipo de contenido (Tema 8).

## Lo que viene

Con este capítulo **termina el libro**. Lo que sigue son las **preguntas de fin del módulo 5** (5A a 5D, tareas 5.1 a 5.6). Después: el repaso con el [mapa de confusiones](19-mapa-de-confusiones.md) y los practice exams (ver [`02-ruta-de-preparacion`](../02-ruta-de-preparacion/README.md)).

---

## Las trampas del examen

Cada trampa tiene el mismo orden: la situación, **qué elegir en el examen (✅)**, las opciones que tientan (❌) con por qué tientan y por qué están mal, y una regla para recordar.

### Grupo: Revisión humana y confianza (tarea 5.5)

#### Trampa 1 · El 97% que esconde un problema

**La situación.** La extracción de facturas tiene 97% de accuracy en total. El gerente quiere dejar de revisar las extracciones de confianza alta (Tema 1).

**✅ En el examen elegí:** **medir primero la accuracy por tipo de documento y por campo**, y automatizar solo los segmentos que rinden parejo.

**❌ Las que tientan:**

❌ **"Automatizar, porque el 97% supera el objetivo del 95%".**
- *Tienta porque:* el número cumple la meta.
- *Está mal porque:* el promedio puede esconder un tipo de documento o un campo con resultados malos.

❌ **"Automatizar y subir el umbral de confianza a 0,99 para estar seguros".**
- *Tienta porque:* parece más conservador.
- *Está mal porque:* sigue sin mirar los segmentos ni calibrar el umbral.

> 🧠 **Para recordar:** antes de automatizar, **medir por segmento**.

#### Trampa 2 · La confianza tal como viene

**La situación.** El modelo devuelve una confianza por campo. Proponen aceptar automáticamente todo lo que tenga 0,9 o más (Tema 2).

**✅ En el examen elegí:** **calibrar el umbral con un set de documentos etiquetados** (comparar la confianza con los aciertos reales).

**❌ Las que tientan:**

❌ **"Usar 0,9 directamente: el modelo sabe cuándo está seguro".**
- *Tienta porque:* el número parece una probabilidad.
- *Está mal porque:* la confianza autoinformada está mal calibrada; 0,9 puede acertar mucho menos.

> 🧠 **Para recordar:** confianza = **por campo + calibrada**.

#### Trampa 3 · Revisar solo lo dudoso

**La situación.** Las extracciones de confianza alta se aceptan solas y las de baja van a revisión. El equipo quiere detectar si aparecen errores nuevos (Tema 3).

**✅ En el examen elegí:** **muestreo aleatorio estratificado de las extracciones de alta confianza**, de forma continua.

**❌ Las que tientan:**

❌ **"Seguir revisando solo las de baja confianza, que es donde están los errores".**
- *Tienta porque:* es donde más errores hay.
- *Está mal porque:* los errores con confianza alta nunca se verían.

❌ **"Tomar una muestra al azar del 2% de todo el volumen".**
- *Tienta porque:* es simple y aleatoria.
- *Está mal porque:* los grupos chicos o de más riesgo pueden quedar afuera; hay que estratificar.

❌ **"Validar bien una vez antes del lanzamiento".**
- *Tienta porque:* parece suficiente.
- *Está mal porque:* los documentos cambian; el muestreo tiene que ser continuo.

> 🧠 **Para recordar:** lo que se automatiza **se sigue midiendo**.

#### Trampa 4 · La cola de revisión

**La situación.** Hay dos revisores y 400 extracciones por día. Hay que decidir qué ven (Tema 4).

**✅ En el examen elegí:** **mandar las de confianza baja (con umbral calibrado) y las de documentos ambiguos o contradictorios**, priorizando esos casos.

**❌ Las que tientan:**

❌ **"Que revisen todo en orden de llegada".**
- *Tienta porque:* es justo y simple.
- *Está mal porque:* desperdicia su tiempo en casos fáciles.

❌ **"Mandar solo las de confianza baja".**
- *Tienta porque:* parece lo esencial.
- *Está mal porque:* un documento que se contradice puede tener confianza alta y necesita una persona igual.

> 🧠 **Para recordar:** a revisión = **confianza baja + fuente ambigua**.

### Grupo: Procedencia (tarea 5.6)

#### Trampa 5 · La bibliografía al final

**La situación.** El informe final tiene datos sin atribución clara. Los subagentes devuelven resúmenes en prosa (Tema 5).

**✅ En el examen elegí:** **que los subagentes devuelvan claim-source mappings** (afirmación, URL, documento, fragmento) **y que la síntesis los conserve**.

**❌ Las que tientan:**

❌ **"Agregar una lista de todas las fuentes consultadas al final del informe".**
- *Tienta porque:* el informe tendría fuentes.
- *Está mal porque:* no dice qué dato sale de qué fuente.

> 🧠 **Para recordar:** cada afirmación **con su fuente**, de punta a punta.

#### Trampa 6 · El 12% y el 8%

**La situación.** Dos fuentes creíbles dan cifras distintas de crecimiento del mercado (Tema 6).

**✅ En el examen elegí:** **incluir los dos valores con su fuente, anotados como conflicto, y que el coordinador decida** cómo reconciliarlos.

**❌ Las que tientan:**

❌ **"Quedarse con el valor de la fuente más reciente".**
- *Tienta porque:* el curso lo propone como "prefer-newer".
- *Está mal porque:* es una regla automática que descarta el otro valor; la guía pide anotar el conflicto y que decida el coordinador.

❌ **"Promediar las dos cifras".**
- *Tienta porque:* parece equilibrado.
- *Está mal porque:* inventa un número que ninguna fuente dijo.

❌ **"Que el subagente de análisis frene hasta que alguien resuelva el conflicto".**
- *Tienta porque:* evita propagar un dato dudoso.
- *Está mal porque:* tiene que completar el análisis con los dos valores anotados.

> 🧠 **Para recordar:** conflicto = **los dos valores, anotados; decide el coordinador**.

#### Trampa 7 · ¿Contradicción o tendencia?

**La situación.** Una fuente dice 30% de participación y otra 22%. El sistema las marca como contradictorias (Tema 7).

**✅ En el examen elegí:** **exigir la fecha de publicación o recolección en la salida de los subagentes**, para distinguir un cambio en el tiempo de una contradicción.

**❌ Las que tientan:**

❌ **"Usar la fecha en que corrió el sistema para ordenar los datos".**
- *Tienta porque:* es una fecha que siempre está.
- *Está mal porque:* no dice cuándo se midió el dato.

> 🧠 **Para recordar:** sin **fecha de la fuente**, una tendencia parece contradicción.

#### Trampa 8 · El informe parejo

**La situación.** El informe convierte todo a viñetas: los precios, las noticias y los hallazgos técnicos. Además, presenta como firme una estimación preliminar (Tema 8).

**✅ En el examen elegí:** **secciones de hallazgos establecidos y disputados, conservando cómo lo dijo la fuente**, y **formato según el contenido**: tablas para lo financiero, prosa para noticias, listas para lo técnico.

**❌ Las que tientan:**

❌ **"Un formato uniforme para que el informe sea consistente".**
- *Tienta porque:* parece más prolijo.
- *Está mal porque:* cada tipo de contenido se lee mejor en su formato.

❌ **"Reescribir todo con un tono seguro para que el informe sea claro".**
- *Tienta porque:* el lector quiere conclusiones.
- *Está mal porque:* pierde las advertencias y el método de la fuente.

> 🧠 **Para recordar:** **establecido vs. disputado**, y **cada contenido en su formato**.

---

## Checklist oficial

**Tarea 5.5 — Design human review workflows and confidence calibration**

*Knowledge of*
- [x] El riesgo de que una accuracy agregada (97%) esconda mal desempeño en ciertos tipos de documento o campos → **Tema 1** (Trampa 1)
- [x] Muestreo aleatorio estratificado para medir la tasa de error de las extracciones de alta confianza y detectar patrones de error nuevos → **Tema 3** (Trampa 3)
- [x] Confianza por campo calibrada con un set de validación etiquetado para dirigir la revisión → **Tema 2** (Trampa 2)
- [x] Validar la accuracy por tipo de documento y por campo antes de automatizar las extracciones de alta confianza → **Tema 1** (Trampa 1)

*Skills in*
- [x] Muestreo aleatorio estratificado continuo de las extracciones de alta confianza → **Tema 3** (Trampa 3)
- [x] Analizar la accuracy por tipo de documento y campo antes de reducir la revisión humana → **Tema 1** (Trampa 1)
- [x] Que el modelo devuelva confianza por campo y calibrar los umbrales con un set etiquetado → **Tema 2** (Trampa 2)
- [x] Enviar a revisión humana las extracciones de confianza baja o con documentos ambiguos o contradictorios, priorizando la capacidad limitada → **Tema 4** (Trampa 4)

**Tarea 5.6 — Preserve information provenance and handle uncertainty in multi-source synthesis**

*Knowledge of*
- [x] Cómo se pierde la atribución al resumir si no se conservan los mappings afirmación-fuente → **Tema 5** (Trampa 5)
- [x] La importancia de mappings estructurados que el agente de síntesis conserve y combine → **Tema 5** (Trampa 5)
- [x] Manejar estadísticas en conflicto de fuentes creíbles anotando el conflicto con atribución en vez de elegir un valor → **Tema 6** (Trampa 6)
- [x] Datos temporales: exigir fechas de publicación o recolección para no confundir diferencias temporales con contradicciones → **Tema 7** (Trampa 7)

*Skills in*
- [x] Que los subagentes devuelvan claim-source mappings (URL, nombre del documento, fragmento) que se conservan en la síntesis → **Tema 5** (Trampa 5)
- [x] Informes con secciones que separan hallazgos establecidos de disputados, conservando la caracterización de la fuente y el contexto metodológico → **Tema 8** (Trampa 8)
- [x] Completar el análisis con los valores en conflicto incluidos y anotados, dejando que el coordinador decida → **Tema 6** (Trampa 6)
- [x] Que los subagentes incluyan fechas de publicación o recolección en su salida estructurada → **Tema 7** (Trampa 7)
- [x] Presentar cada tipo de contenido en su formato: finanzas en tablas, noticias en prosa, hallazgos técnicos en listas → **Tema 8** (Trampa 8)

**Complementa otras tareas:** confianza calibrada para enrutar de 4.6 (Tema 2) · `conflict_detected` de 4.4 (Temas 4 y 6) · metadatos de los subagentes de 5.1 (Temas 5 y 7) · anotaciones de cobertura de 5.3 (Tema 8).

**De la documentación, no de la guía** (vale saberlo; la guía no lo pregunta directo): citations API (Tema 5).

**📘 Curso (útil para entender):** recalibrar después de cambios (Tema 2) · cola de revisión que registra correcciones (Tema 4) · puntero a la fuente junto a cada afirmación y auditoría de citas (Tema 5).

---

## Autoevaluación oral

1. ¿Por qué un 97% de accuracy total no alcanza para automatizar? ¿Qué medís antes?
2. ¿Por qué la confianza tiene que ser por campo? ¿Cómo se calibra el umbral y por qué no se usa la confianza cruda?
3. ¿Para qué sirve el muestreo estratificado según la guía, y de qué extracciones se toma? ¿Qué va a revisión humana?
4. ¿Qué es un claim-source mapping? ¿Qué hacés cuando dos fuentes creíbles dan cifras distintas, y quién decide?
5. ¿Por qué importan las fechas de las fuentes? ¿Cómo se estructura el informe final y en qué formato va cada tipo de contenido?

---

## Preguntas tipo examen

Las preguntas tipo examen de este capítulo están en [`04-practica/modulo-5.md`](../04-practica/modulo-5.md), junto con las del resto del módulo 5. Hacelas cuando termines **todos** los capítulos del módulo, de a una y sin mirar la respuesta.

---

## Revisión contra el blueprint oficial

Qué puede salir en el examen de 5.5 y 5.6 que el curso de Jacob **no cubre o cubre flojo**, y dónde quedó explicado:

1. **Accuracy por tipo de documento**, no solo por campo, y validar **antes** de automatizar. → Tema 1.
2. **El propósito del muestreo estratificado**: medir lo que se automatiza, no buscar más errores en lo dudoso. → Tema 3.
3. **Enviar a revisión los documentos ambiguos o contradictorios**, además de los de baja confianza. → Tema 4.
4. **No elegir entre fuentes en conflicto** (el curso propone "prefer-newer" o "prefer-authoritative") y que **decida el coordinador**. → Tema 6.
5. **Fechas de publicación o recolección.** → Tema 7.
6. **Establecido vs. disputado** y **formato según el contenido.** → Tema 8.

No encontré otros huecos para 5.5 y 5.6.

