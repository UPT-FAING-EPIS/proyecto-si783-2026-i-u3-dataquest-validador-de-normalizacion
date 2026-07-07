from .conexion import get_supabase_client
from datetime import datetime

def set_user_presence(user_id, nombre):
    """Actualiza o inserta la presencia del usuario en la base de datos."""
    supabase = get_supabase_client()
    try:
        # Usamos upsert para actualizar la hora de actividad si ya existe, o insertar si es nuevo
        data = {
            "user_id": user_id,
            "nombre": nombre,
            "ultima_actividad": datetime.now().isoformat()
        }
        supabase.table("presencia").upsert(data, on_conflict="user_id").execute()
        return True
    except Exception as e:
        print(f"Error actualizando presencia: {e}")
        return False

def remove_user_presence(user_id):
    """Elimina al usuario de la tabla de presencia (usado en logout)."""
    supabase = get_supabase_client()
    try:
        supabase.table("presencia").delete().eq("user_id", user_id).execute()
        return True
    except Exception as e:
        print(f"Error eliminando presencia: {e}")
        return False

def get_active_users():
    """Obtiene la lista de usuarios conectados."""
    supabase = get_supabase_client()
    try:
        # Se asume que usuarios con actividad en los últimos N minutos están activos.
        # Por ahora traemos todos, en una app real filtraríamos por 'ultima_actividad'
        response = supabase.table("presencia").select("*").order("conectado_en", desc=True).execute()
        return response.data
    except Exception as e:
        print(f"Error obteniendo usuarios activos: {e}")
        return []
