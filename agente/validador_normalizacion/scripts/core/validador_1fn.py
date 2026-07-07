def validar_1fn(tabla):
    """
    Verifica si una tabla cumple con la Primera Forma Normal (1FN).
    Reglas a nivel de esquema:
    1. Debe tener una clave primaria (Primary Key) definida.
    2. (Heurística) No debe tener columnas que parezcan arreglos o listas.
    """
    violaciones = []
    
    # Regla 1: Debe tener PK
    if not tabla.get("pks"):
        violaciones.append({
            "tipo": "Sin Primary Key",
            "mensaje": f"La tabla '{tabla['nombre']}' no tiene definida una Clave Primaria (Primary Key). Esto viola la 1FN.",
            "sql_original": tabla.get("sql_original", "")
        })
        
    # Regla 2: Sin grupos repetitivos (heurística simple por nombre de columna)
    import re
    for col in tabla.get("columnas", []):
        col_lower = col.lower()
        # Detectar palabras plurales comunes o sufijos numéricos (ej. telefono1, telefono2)
        if "lista" in col_lower or "array" in col_lower or "grupo" in col_lower or \
           "telefonos" in col_lower or "direcciones" in col_lower or "emails" in col_lower or \
           re.search(r'\d+$', col_lower): # Termina en número
            violaciones.append({
                "tipo": "Grupo Repetitivo (1FN)",
                "mensaje": f"La columna '{col}' en la tabla '{tabla['nombre']}' parece ser un grupo repetitivo o contener múltiples valores. Separar atributos multivaluados para cumplir 1FN.",
                "sql_original": tabla.get("sql_original", "")
            })
            
    cumple_1fn = len(violaciones) == 0
    return cumple_1fn, violaciones
