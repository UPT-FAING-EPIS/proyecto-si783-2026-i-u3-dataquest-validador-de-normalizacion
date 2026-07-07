from core.validador_1fn import validar_1fn
from core.validador_2fn import validar_2fn
from core.validador_3fn import validar_3fn

def inferir_dependencias_heuristica(tabla):
    """
    Infiere dependencias funcionales basadas en patrones de nombres de columnas.
    Esto permite al sistema auto-detectar violaciones 2FN y 3FN sin entrada del usuario.
    """
    fds = []
    columnas = tabla.get("columnas", [])
    pks = tabla.get("pks", [])
    
    # Heurística 1: Dependencias parciales (2FN)
    # Si la PK es compuesta, buscar atributos que parezcan pertenecer a solo una parte de la PK.
    # Ej: PK(curso_id, profesor_id), atributo: curso_nombre -> depende de curso_id
    if len(pks) > 1:
        for pk in pks:
            pk_base = pk.replace('_id', '').replace('id_', '')
            deps_parciales = []
            for col in columnas:
                if col not in pks and pk_base in col and col != pk:
                    deps_parciales.append(col)
            if deps_parciales:
                fds.append({"determinantes": [pk], "dependientes": deps_parciales})
                
    # Heurística 2: Dependencias transitivas (3FN)
    # Patrón A: columnas con prefijo/sufijo id (ej. departamento_id y departamento_nombre)
    for col in columnas:
        if col not in pks and (col.endswith('_id') or col.startswith('id_')):
            base = col.replace('_id', '').replace('id_', '')
            deps_transitivas = []
            for otra_col in columnas:
                if otra_col != col and otra_col not in pks and otra_col.startswith(base):
                    deps_transitivas.append(otra_col)
            if deps_transitivas:
                fds.append({"determinantes": [col], "dependientes": deps_transitivas})
                
    # Patrón B: Entidades conceptuales comunes que suelen requerir su propia tabla
    entidades_comunes = [
        "departamento", "ciudad", "pais", "marca", "categoria", "proveedor", 
        "carrera", "facultad", "sucursal", "autor", "editorial", "cliente",
        "paciente", "medico", "producto", "estado", "region", "tipo", "rol"
    ]
    for col in columnas:
        if col not in pks:
            col_lower = col.lower()
            for entidad in entidades_comunes:
                if entidad in col_lower:
                    # Encontramos una posible entidad transitiva. Veamos si hay otra que también la mencione.
                    deps = []
                    for otra_col in columnas:
                        if otra_col != col and otra_col not in pks and entidad in otra_col.lower():
                            deps.append(otra_col)
                    if deps:
                        existe = any(d["determinantes"] == [col] for d in fds)
                        if not existe:
                            fds.append({"determinantes": [col], "dependientes": deps})
                            
    # Patrón C: Heurística de demasiadas columnas (Tabla "Sábana")
    # Si una tabla tiene muchas columnas no-clave (ej. > 6), es muy probable que no esté en 3FN.
    # En ese caso, forzamos una dependencia simulada para sugerir separación.
    columnas_no_clave = [c for c in columnas if c not in pks]
    if len(columnas_no_clave) >= 6:
        # Tomar la mitad de las columnas no clave y simular que dependen de una columna inventada o de la primera
        det = columnas_no_clave[0]
        deps = columnas_no_clave[1:len(columnas_no_clave)//2 + 1]
        existe = any(d["determinantes"] == [det] for d in fds)
        if not existe:
            fds.append({"determinantes": [det], "dependientes": deps})
                
    return fds

def diagnosticar_esquema(esquema_parseado):
    """
    Analiza un esquema parseado y determina su nivel de normalización actual.
    Retorna: 'sin_normalizar', '1fn', '2fn', o '3fn' y un reporte de violaciones.
    """
    tablas = esquema_parseado.get("tablas", [])
    # Usar las FDs provistas o inferirlas heurísticamente si no hay
    fds_globales = esquema_parseado.get("dependencias_funcionales", [])
    
    violaciones_1fn = []
    violaciones_2fn = []
    violaciones_3fn = []
    
    # Reporte de mejoras opcionales
    mejoras_opcionales = []
    
    nivel_actual = "3FN" # Asumimos optimismo y vamos degradando
    
    for tabla in tablas:
        columnas = tabla.get("columnas", [])
        
        # Detectar mejoras opcionales (Semánticas)
        for col in columnas:
            col_lower = col.lower()
            if "nombrecompleto" in col_lower or "nombre_completo" in col_lower:
                mejoras_opcionales.append({
                    "tabla": tabla["nombre"],
                    "columna": col,
                    "tipo": "División Semántica",
                    "mensaje": f"El atributo '{col}' puede dividirse para mayor flexibilidad.",
                    "sugerencia_columnas": ["nombre", "apellido_paterno", "apellido_materno"]
                })
            elif col_lower == "direccion" or col_lower == "direccion_completa":
                mejoras_opcionales.append({
                    "tabla": tabla["nombre"],
                    "columna": col,
                    "tipo": "División Semántica",
                    "mensaje": f"El atributo '{col}' puede dividirse para mejorar las búsquedas geográficas.",
                    "sugerencia_columnas": ["calle", "ciudad", "estado", "codigo_postal"]
                })
        
        # Inferir FDs de la tabla si no se proveyeron globales
        fds_tabla = fds_globales if fds_globales else inferir_dependencias_heuristica(tabla)
        
        c1, v1 = validar_1fn(tabla)
        violaciones_1fn.extend(v1)
        if not c1:
            nivel_actual = "sin_normalizar"
            
        c2, v2 = validar_2fn(tabla, fds_tabla)
        violaciones_2fn.extend(v2)
        if not c2 and nivel_actual in ["3FN", "2FN", "1FN"]:
            if nivel_actual != "sin_normalizar":
                nivel_actual = "1FN" # Degrada a 1FN
            
        c3, v3 = validar_3fn(tabla, fds_tabla)
        violaciones_3fn.extend(v3)
        if not c3 and nivel_actual in ["3FN", "2FN"]:
            if nivel_actual not in ["sin_normalizar", "1FN"]:
                nivel_actual = "2FN" # Degrada a 2FN
            
    # Si llegó aquí y no hay violaciones_3fn, ni de 2fn ni 1fn, es 3FN
    
    reporte = {
        "nivel_actual": nivel_actual,
        "violaciones_1fn": violaciones_1fn,
        "violaciones_2fn": violaciones_2fn,
        "violaciones_3fn": violaciones_3fn,
        "mejoras_opcionales": mejoras_opcionales,
        "resumen": f"El esquema global se encuentra en nivel: {nivel_actual}"
    }
    
    return reporte
