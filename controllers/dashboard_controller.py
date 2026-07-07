from db.conexion import get_supabase_client

def get_dashboard_metrics(user_id):
    """
    Obtiene las métricas principales para el dashboard del usuario actual.
    """
    try:
        supabase = get_supabase_client()
        
        # 1. Total validaciones realizadas
        res_val = supabase.table("historial_validaciones").select("id", count="exact").eq("user_id", user_id).execute()
        total_validaciones = res_val.count if res_val.count else 0
        
        # 2. Total tablas analizadas (aproximación sumando las tablas del esquema_original)
        res_tablas = supabase.table("historial_validaciones").select("esquema_original").eq("user_id", user_id).execute()
        total_tablas = 0
        for row in res_tablas.data:
            if row.get("esquema_original") and "tablas" in row["esquema_original"]:
                total_tablas += len(row["esquema_original"]["tablas"])
                
        # 3. Reportes / Errores encontrados (sumando violaciones)
        res_viol = supabase.table("historial_validaciones").select("violaciones").eq("user_id", user_id).execute()
        total_reportes = 0
        for row in res_viol.data:
            if row.get("violaciones") and "lista" in row["violaciones"]:
                total_reportes += len(row["violaciones"]["lista"])
                
        # 4. Usuarios online ahora
        res_online = supabase.table("presencia").select("id", count="exact").execute()
        online_ahora = res_online.count if res_online.count else 1
        
        return {
            "validaciones": total_validaciones,
            "tablas_analizadas": total_tablas,
            "reportes_generados": total_reportes,
            "online": online_ahora
        }
    except Exception as e:
        print(f"Error obteniendo métricas del dashboard: {e}")
        return {
            "validaciones": 0,
            "tablas_analizadas": 0,
            "reportes_generados": 0,
            "online": 1
        }

def get_ultimos_escaneos(user_id, limit=5):
    """
    Obtiene las validaciones más recientes para la tabla del dashboard.
    """
    try:
        supabase = get_supabase_client()
        res = supabase.table("historial_validaciones").select("*").eq("user_id", user_id).order("fecha", desc=True).limit(limit).execute()
        return res.data
    except Exception as e:
        print(f"Error obteniendo últimos escaneos: {e}")
        return []

def get_user_charts_data(user_id):
    """
    Obtiene métricas específicas del usuario para mostrar en gráficos en el dashboard personal.
    """
    try:
        supabase = get_supabase_client()
        res = supabase.table("historial_validaciones").select("fecha, nivel_inicial, nivel_final").eq("user_id", user_id).execute()
        
        datos = res.data
        if not datos:
            return {"fechas": [], "niveles_iniciales": {}, "niveles_finales": {}}
            
        niveles_iniciales = {}
        niveles_finales = {}
        
        for fila in datos:
            n_ini = fila.get("nivel_inicial") or "Desconocido"
            n_fin = fila.get("nivel_final") or "Pendiente"
            
            niveles_iniciales[n_ini] = niveles_iniciales.get(n_ini, 0) + 1
            niveles_finales[n_fin] = niveles_finales.get(n_fin, 0) + 1
            
        import pandas as pd
        df_inicial = pd.DataFrame(list(niveles_iniciales.items()), columns=["Nivel", "Cantidad"])
        df_final = pd.DataFrame(list(niveles_finales.items()), columns=["Nivel", "Cantidad"])
        
        if not df_inicial.empty:
            df_inicial["Nivel"] = df_inicial["Nivel"].str.upper()
        if not df_final.empty:
            df_final["Nivel"] = df_final["Nivel"].str.upper()
            
        return {
            "df_inicial": df_inicial,
            "df_final": df_final
        }
    except Exception as e:
        print(f"Error obteniendo datos para gráficos de usuario: {e}")
        import pandas as pd
        return {"df_inicial": pd.DataFrame(), "df_final": pd.DataFrame()}
