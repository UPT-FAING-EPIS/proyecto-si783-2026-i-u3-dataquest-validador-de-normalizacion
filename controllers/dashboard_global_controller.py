from db.conexion import get_supabase_client
import pandas as pd

def get_global_metrics():
    """
    Obtiene métricas globales de todas las validaciones usando supabase client.
    """
    try:
        supabase = get_supabase_client()
        
        # Total validaciones
        res_val = supabase.table("historial_validaciones").select("id", count="exact").execute()
        total_validaciones = res_val.count if res_val.count else 0
        
        # Fetch all for metrics
        res_all = supabase.table("historial_validaciones").select("user_id, nivel_inicial, nivel_final").execute()
        datos = res_all.data
        
        usuarios_unicos = len(set([d["user_id"] for d in datos if d.get("user_id")]))
        
        niveles_iniciales = {}
        niveles_finales = {}
        for d in datos:
            ini = d.get("nivel_inicial") or "Desconocido"
            fin = d.get("nivel_final") or "Pendiente"
            niveles_iniciales[ini] = niveles_iniciales.get(ini, 0) + 1
            niveles_finales[fin] = niveles_finales.get(fin, 0) + 1

        return {
            "total_validaciones": total_validaciones,
            "usuarios_unicos": usuarios_unicos,
            "niveles_iniciales": niveles_iniciales,
            "niveles_finales": niveles_finales
        }
    except Exception as e:
        print(f"Error obteniendo métricas globales: {e}")
        return {
            "total_validaciones": 0,
            "usuarios_unicos": 0,
            "niveles_iniciales": {},
            "niveles_finales": {}
        }

def format_data_for_charts(metricas):
    """
    Formatea la salida de get_global_metrics en DataFrames para Streamlit.
    """
    df_inicial = pd.DataFrame(list(metricas["niveles_iniciales"].items()), columns=["Nivel", "Cantidad"])
    df_final = pd.DataFrame(list(metricas["niveles_finales"].items()), columns=["Nivel", "Cantidad"])
    
    # Asegurarnos de que los niveles se vean bien
    df_inicial["Nivel"] = df_inicial["Nivel"].str.upper()
    df_final["Nivel"] = df_final["Nivel"].str.upper()
    
    return df_inicial, df_final
