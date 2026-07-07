def validar_2fn(tabla, fds):
    """
    Verifica si una tabla cumple con la Segunda Forma Normal (2FN).
    Reglas:
    1. Debe estar en 1FN.
    2. Ningún atributo no clave debe depender de solo una parte de una Clave Primaria Compuesta (Dependencia Parcial).
    """
    violaciones = []
    
    pks = tabla.get("pks", [])
    
    # Si la PK es de una sola columna o no hay PK (falló 1FN), no puede haber dependencia parcial de una PK compuesta.
    # Por definición matemática, si PK es simple, 1FN implica 2FN automáticamente.
    if len(pks) <= 1:
        return True, violaciones
        
    columnas_tabla = set(tabla.get("columnas", []))
    pks_set = set(pks)
    
    # Evaluar las dependencias funcionales dadas
    for fd in fds:
        determinantes = set(fd["determinantes"])
        dependientes = set(fd["dependientes"])
        
        # Ignorar si los atributos no pertenecen a esta tabla
        if not determinantes.issubset(columnas_tabla) or not dependientes.issubset(columnas_tabla):
            continue
            
        # Verificar dependencia parcial: 
        # El determinante es un subconjunto propio estricto de la clave primaria
        if determinantes.issubset(pks_set) and len(determinantes) < len(pks_set):
            # Encontramos que atributos dependen de solo una parte de la PK
            violaciones.append({
                "tipo": "Dependencia Parcial (2FN)",
                "mensaje": f"En la tabla '{tabla['nombre']}', los atributos {list(dependientes)} dependen parcialmente de la clave primaria a través de {list(determinantes)}.",
                "sql_original": tabla.get("sql_original", "")
            })
            
    cumple_2fn = len(violaciones) == 0
    return cumple_2fn, violaciones
