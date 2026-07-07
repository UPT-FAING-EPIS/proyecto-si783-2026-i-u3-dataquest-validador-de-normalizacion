def validar_3fn(tabla, fds):
    """
    Verifica si una tabla cumple con la Tercera Forma Normal (3FN).
    Reglas:
    1. Debe estar en 2FN.
    2. No debe haber dependencias transitivas entre atributos no clave.
       (X -> Y, donde X no es superclave y Y no es parte de una clave candidata)
    """
    violaciones = []
    
    pks_set = set(tabla.get("pks", []))
    columnas_tabla = set(tabla.get("columnas", []))
    
    # Evaluar las dependencias funcionales dadas
    for fd in fds:
        determinantes = set(fd["determinantes"])
        dependientes = set(fd["dependientes"])
        
        # Ignorar si los atributos no pertenecen a esta tabla
        if not determinantes.issubset(columnas_tabla) or not dependientes.issubset(columnas_tabla):
            continue
            
        # Para cada dependencia funcional X -> Y en la tabla
        # Se viola 3FN si se cumplen TODAS estas condiciones:
        # 1. X NO es una superclave (en nuestro modelo simple, X no contiene a la PK)
        # Si no hay PK, nada es superclave. Si hay PK, verificamos si X la contiene.
        es_superclave = len(pks_set) > 0 and pks_set.issubset(determinantes)
        
        # 2. Y NO es un atributo primo (Y no es subconjunto de PK)
        es_primo = len(pks_set) > 0 and dependientes.issubset(pks_set)
        
        if not es_superclave:
            if not es_primo:
                # Es una dependencia transitiva
                # Y no es atributo primo
                # Es una dependencia transitiva
                violaciones.append({
                    "tipo": "Dependencia Transitiva (3FN)",
                    "mensaje": f"En la tabla '{tabla['nombre']}', los atributos no clave {list(dependientes)} dependen funcionalmente del atributo no clave {list(determinantes)}.",
                    "sql_original": tabla.get("sql_original", "")
                })
                
    cumple_3fn = len(violaciones) == 0
    return cumple_3fn, violaciones
