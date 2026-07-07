# DataQuest - Validador de Normalización (AI Agent Skill)

Bienvenido al repositorio de la **Skill de Validación de Normalización** de DataQuest. Este paquete proporciona a tu asistente virtual o agente de IA la capacidad de analizar esquemas de bases de datos relacionales, detectar infracciones de diseño y sugerir mejoras para alcanzar la Primera (1FN), Segunda (2FN) y Tercera Forma Normal (3FN).

---

## 🧠 ¿Qué hace esta Skill?

Esta skill actúa como un puente entre tu agente de IA y un motor heurístico escrito en Python. El motor no es una simple caja negra; realiza un análisis semántico y sintáctico profundo de un archivo de base de datos (`.sql`, `.txt`, etc.) simulando dependencias funcionales para determinar la calidad del diseño.

**Características principales:**
1. **Análisis de 1FN:** Verifica la atomicidad de los atributos.
2. **Análisis de 2FN:** Detecta dependencias parciales cuando existen claves primarias compuestas.
3. **Análisis de 3FN:** Encuentra dependencias transitivas infiriendo relaciones lógicas por nombres de campos (ej. `departamento_id` -> `departamento_nombre`).
4. **Sugerencias de Descomposición:** Identifica "tablas sábana" (tablas con demasiados atributos) y atributos compuestos que podrían dividirse (como `direccion` o `nombre_completo`).
5. **Autocorrección (Refactorización):** El motor puede devolver el código SQL `CREATE TABLE` corregido automáticamente al nivel de forma normal deseado.

---

## ⚙️ ¿Cómo implementarla en tu proyecto?

Para utilizar esta skill en tu entorno (como Antigravity, Cline, u otros frameworks que sigan este estándar de customización de agentes), debes hacer que la carpeta de la skill forme parte de tu directorio de agentes.

### Pasos de Instalación:

1. Clona o descarga este repositorio.
2. Copia la carpeta `validador_normalizacion/` dentro del directorio de personalizaciones de agentes de tu proyecto. Generalmente, este directorio es `.agents/skills/`.
   
   La estructura resultante en tu proyecto debería verse así:
   ```text
   TuProyecto/
   └── .agents/
       └── skills/
           └── validador_normalizacion/
               ├── SKILL.md
               └── scripts/
                   ├── core/
                   └── requirements.txt
   ```

3. Instala las dependencias necesarias de Python. El agente requerirá estas dependencias instaladas en tu entorno para poder ejecutar el motor localmente.
   ```bash
   pip install -r .agents/skills/validador_normalizacion/scripts/requirements.txt
   ```

---

## 🚀 ¿Cómo usarla?

Como usuario, **no necesitas ejecutar el código manualmente**. ¡Ese es el trabajo de tu agente de IA!

Una vez que la skill está instalada en el directorio `.agents/skills/`, tu agente descubrirá y leerá automáticamente el archivo `SKILL.md` y sabrá cómo invocar la herramienta.

### Flujo de uso:
1. Pídele a tu agente que valide un archivo con sentencias SQL, por ejemplo:
   > *"Por favor, valida la normalización de la base de datos en mi archivo `schema.sql` y explícame las fallas."*
2. El agente invocará la herramienta por detrás ejecutando el CLI de esta skill:
   `python scripts/core/cli.py schema.sql`
3. El agente recibirá un reporte en formato JSON con todas las infracciones.
4. **Magia de la IA:** Basándose en las instrucciones del `SKILL.md`, el agente traducirá este reporte técnico JSON en una explicación pedagógica e interactiva para ti, explicando el por qué de cada error y presentándote el SQL corregido de forma amigable.

---

## 🛠️ Estructura Interna del Proyecto

- `SKILL.md`: El cerebro de la operación. Aquí se definen las instrucciones detalladas que el agente debe leer y seguir estrictamente al momento de invocar el validador y de presentar la información.
- `scripts/core/`: Contiene el código en Python puro para el parsing heurístico y el análisis del esquema.
- `scripts/requirements.txt`: Archivo con las dependencias para que Python pueda parsear correctamente el código SQL (ej. `sqlparse`).
