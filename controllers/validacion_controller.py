import streamlit as st

# Módulos core a importar posteriormente:
# from core.parser import parse_schema
# from core.diagnostico import diagnosticar_esquema
# from core.validador_1fn import validar_1fn
# from core.validador_2fn import validar_2fn
# from core.validador_3fn import validar_3fn
# from core.corrector import generar_sugerencias

def procesar_esquema(input_data, formato, fds_input=""):
    """
    Controlador principal que orquesta el parsing y el diagnóstico inicial.
    """
    from core.parser import parse_schema
    # 1. Parsear esquema
    schema_parseado = parse_schema(input_data, formato, fds_input)
    
    # 2. Diagnóstico inicial (simulado por ahora)
    from core.diagnostico import diagnosticar_esquema
    diagnostico = diagnosticar_esquema(schema_parseado)
    
    return schema_parseado, diagnostico

def generar_sugerencias_para_nivel(schema_parseado, nivel_objetivo):
    """
    Orquesta la validación según el nivel objetivo y devuelve las sugerencias.
    """
    from core.diagnostico import diagnosticar_esquema
    from core.corrector import generar_sugerencias
    
    # Re-diagnosticamos para obtener las violaciones
    diagnostico = diagnosticar_esquema(schema_parseado)
    todas_sugerencias = generar_sugerencias(diagnostico)
    
    # Filtramos las sugerencias según el nivel objetivo
    sugerencias_filtradas = []
    
    niveles_map = {"1FN": 1, "2FN": 2, "3FN": 3}
    objetivo = niveles_map.get(nivel_objetivo, 3)
    
    for sug in todas_sugerencias:
        nivel_sug = niveles_map.get(sug["nivel"], 1)
        if nivel_sug <= objetivo:
            sugerencias_filtradas.append(sug)
            
    return sugerencias_filtradas

def guardar_historial(user_id, nombre_esquema, schema_parseado, diagnostico, formato="texto_pegado"):
    """
    Guarda el esquema y su resultado de diagnóstico en la base de datos de historial.
    Retorna el ID del historial insertado, o None si ocurre un error.
    """
    try:
        from db.conexion import get_supabase_client
        supabase = get_supabase_client()
        
        # Determinar nivel inicial
        nivel_inicial_raw = diagnostico.get("nivel_actual", "sin_normalizar").lower() if isinstance(diagnostico, dict) else "sin_normalizar"
        if nivel_inicial_raw not in ["sin_normalizar", "1fn", "2fn", "3fn"]:
            nivel_inicial_raw = "sin_normalizar"
        nivel_inicial = nivel_inicial_raw
            
        formato_db = formato
        if formato_db == "xlsx":
            formato_db = "xls"
        elif formato_db not in ["sql", "csv", "xls", "txt", "texto_pegado"]:
            formato_db = "texto_pegado"
            
        historial_data = {
            "user_id": user_id,
            "nombre_esquema": nombre_esquema,
            "formato_entrada": formato_db,
            "nivel_inicial": nivel_inicial,
            "esquema_original": schema_parseado,
            "dependencias": schema_parseado.get("dependencias_funcionales", []),
            "violaciones": diagnostico
        }
        
        res_historial = supabase.table("historial_validaciones").insert(historial_data).execute()
        
        if res_historial.data:
            return res_historial.data[0]['id']
        return None
    except Exception as e:
        print(f"Error guardando historial: {e}")
        return None

def actualizar_historial(historial_id, nivel_objetivo, nivel_final, sugerencias, esquema_final=None):
    """
    Actualiza un registro de historial con las sugerencias y el nivel objetivo/final.
    """
    try:
        from db.conexion import get_supabase_client
        supabase = get_supabase_client()
        
        update_data = {
            "nivel_objetivo": nivel_objetivo.lower() if nivel_objetivo else None,
            "nivel_final": nivel_final.lower() if nivel_final else None,
            "sugerencias": sugerencias
        }
        if esquema_final:
            update_data["esquema_final"] = esquema_final
            
        supabase.table("historial_validaciones").update(update_data).eq("id", historial_id).execute()
    except Exception as e:
        print(f"Error actualizando historial: {e}")
