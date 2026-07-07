# Ejemplo de cómo otro proyecto importaría tu lógica pura como librería
import json
from agente.validador_normalizacion.scripts.core.parser import parse_schema
from agente.validador_normalizacion.scripts.core.diagnostico import diagnosticar_esquema

# 1. El sistema recibe un SQL de alguna fuente (un usuario, una página web, etc.)
sql_input = """
CREATE TABLE empleados (
    empleado_id INT PRIMARY KEY,
    nombre_y_apellidos VARCHAR(150),
    departamento_id INT,
    departamento_nombre VARCHAR(100)
);
"""

# 2. Tu motor lógico procesa la información
esquema = parse_schema(sql_input, 'sql')
reporte = diagnosticar_esquema(esquema)

# 3. El nuevo sistema utiliza los resultados
print("--- REPORTE DEL SISTEMA ---")
print(f"Nivel de Normalización: {reporte['nivel_actual']}")
print(f"Mejoras sugeridas: {json.dumps(reporte['mejoras_opcionales'], indent=2, ensure_ascii=False)}")
