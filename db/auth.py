import hashlib
import uuid
from .conexion import get_supabase_client

def hash_password(password):
    """Genera un hash SHA-256 básico para la contraseña."""
    return hashlib.sha256(password.encode()).hexdigest()

def login_user(username, password):
    """Autentica un usuario validando el hash en la tabla usuarios."""
    supabase = get_supabase_client()
    try:
        # Buscar usuario
        res = supabase.table("usuarios").select("*").eq("username", username).execute()
        if not res.data:
            return {"error": "Usuario o contraseña incorrectos."}
        
        user_record = res.data[0]
        if user_record["password_hash"] != hash_password(password):
            return {"error": "Usuario o contraseña incorrectos."}
            
        # Simular el objeto "user" que antes daba Supabase Auth
        class DummyUser:
            def __init__(self, id):
                self.id = id
        class DummySession:
            def __init__(self):
                self.access_token = "dummy_token"
                self.refresh_token = "dummy_token"
        class DummyResponse:
            def __init__(self, user):
                self.user = user
                self.session = DummySession()
                
        return DummyResponse(DummyUser(user_record["id"]))
    except Exception as e:
        return {"error": str(e)}

def register_user(username, password):
    """Registra un nuevo usuario en la tabla usuarios y su perfil."""
    supabase = get_supabase_client()
    try:
        # Verificar si ya existe
        check = supabase.table("usuarios").select("id").eq("username", username).execute()
        if check.data:
            return {"error": "Este nombre de usuario ya está en uso. Por favor, elige otro."}
            
        # Insertar en usuarios
        hashed_pw = hash_password(password)
        new_user_res = supabase.table("usuarios").insert({
            "username": username,
            "password_hash": hashed_pw
        }).execute()
        
        if not new_user_res.data:
            return {"error": "No se pudo crear el usuario."}
            
        new_user_id = new_user_res.data[0]["id"]
        
        # Insertar en perfiles
        supabase.table("perfiles").insert({
            "id": new_user_id,
            "nombre": username
        }).execute()
        
        return {"success": True}
    except Exception as e:
        return {"error": str(e)}

def logout_user():
    """Para el login manual, el logout solo es local en session_state."""
    return True

def get_user_profile(user_id):
    """Obtiene el perfil público del usuario desde la tabla 'perfiles'."""
    supabase = get_supabase_client()
    try:
        response = supabase.table("perfiles").select("*").eq("id", user_id).execute()
        if response.data:
            return response.data[0]
        return None
    except Exception as e:
        return None
