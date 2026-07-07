---
name: validador-normalizacion-db
description: Analiza y valida modelos de bases de datos relacionales (SQL o texto con CREATE TABLE) detectando si cumplen con 1FN, 2FN y 3FN basándose en un análisis profundo de dependencias funcionales heurísticas.
---

# Validador de Normalización de Bases de Datos Relacionales

Esta skill permite a los agentes de IA utilizar el motor de validación local en Python para analizar esquemas de bases de datos y proporcionar diagnósticos exhaustivos sobre Formas Normales. 

## Lógica Interna del Motor (Lo que debes saber para interpretar los resultados)

El motor (`core/`) no es una caja negra; utiliza algoritmos formales y heurísticas para validar la normalización de la base de datos. Como agente inteligente, debes usar este contexto para explicar las violaciones reportadas al usuario:

### 1. Inferencia Heurística de Dependencias Funcionales
El sistema detecta dependencias funcionales (FDs) automáticamente si el usuario no las provee:
*   **Dependencias Parciales (2FN):** Si hay claves primarias compuestas (ej. `curso_id`, `profesor_id`), el motor busca atributos que correspondan a solo una parte de la clave (ej. `curso_nombre` dependerá de `curso_id`).
*   **Dependencias Transitivas (3FN):** El motor busca columnas con prefijos/sufijos `_id` (ej. `departamento_id`) y otras columnas que tengan la misma raíz (ej. `departamento_nombre`), asumiendo una dependencia `departamento_id -> departamento_nombre`. También busca entidades conceptuales comunes en los nombres de las columnas (ej. ciudad, país, marca, categoría).
*   **Patrón "Tabla Sábana":** Si una tabla tiene demasiados atributos no clave (ej. 6 o más), el motor simulará dependencias para sugerir fuertemente su descomposición en 3FN, ya que tablas tan anchas rara vez están bien normalizadas.

### 2. Reglas de Normalización Aplicadas
*   **Primera Forma Normal (1FN):** El motor verifica que no existan atributos que violen la atomicidad (arreglos, listas, o nombres de columna que sugieran múltiples valores).
*   **Segunda Forma Normal (2FN):** (Requiere 1FN). Si la tabla tiene clave primaria compuesta, se detectan dependencias parciales donde atributos no-clave dependen de una fracción de la PK.
*   **Tercera Forma Normal (3FN):** (Requiere 2FN). Busca que ningún atributo no-clave dependa funcionalmente de otro atributo no-clave.

### 3. Sugerencias de División Semántica
El motor detecta atributos semánticamente divisibles (ej. `nombrecompleto`, `direccion`) y reporta "Mejoras Opcionales" para que sean divididos en partes más atómicas (ej. `calle`, `ciudad`, `estado`), incluso si estrictamente no violan 1FN desde una perspectiva sintáctica.

---

## Cómo Ejecutar el Validador

Para analizar el archivo del usuario o un bloque de texto SQL, ejecuta el siguiente comando CLI utilizando la ruta del motor en el repositorio:

```bash
python core/cli.py <ruta-al-archivo>
```

*(El archivo puede tener extensión `.sql`, `.txt`, `.csv` o no tener extensión, siempre y cuando contenga sentencias `CREATE TABLE` en su interior).*

### Estructura de Salida JSON

La salida estándar será un objeto JSON con esta estructura:

```json
{
  "nivel_actual": "sin_normalizar | 1FN | 2FN | 3FN",
  "violaciones_1fn": [ ... ],
  "violaciones_2fn": [ ... ],
  "violaciones_3fn": [ ... ],
  "mejoras_opcionales": [ ... ],
  "resumen": "...",
  "tablas_detectadas": ["tabla1", "tabla2"]
}
```

### Instrucciones para Formatear la Respuesta al Usuario

1.  **Ejecuta el CLI.** No intentes adivinar la normalización sin ejecutar el motor.
2.  **Analiza el JSON resultante.** Lee los arreglos de violaciones.
3.  **Explica de Forma Inteligente.** No te limites a imprimir el JSON. Usa tu conocimiento sobre la *Lógica Interna del Motor* (explicada arriba) para traducir el diagnóstico en una explicación pedagógica:
    *   *Por qué ocurre la violación.*
    *   *Cómo el motor la detectó (ej. dependencia transitiva inferida).*
    *   *Cómo solucionarlo.*
4.  **Inyecta o Proporciona el SQL Corregido.** Basándote en las violaciones detectadas, ofrécele al usuario las sentencias `CREATE TABLE` refactorizadas que cumplen con 3FN.
