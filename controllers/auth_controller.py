import streamlit as st
from db.auth import login_user, register_user, logout_user, get_user_profile
from db.realtime import set_user_presence, remove_user_presence

def init_session():
    """Inicializa las variables de estado de la sesión si no existen."""
    if "user" not in st.session_state:
        st.session_state.user = None
def handle_login(username, password):
    """Maneja el flujo de login desde la vista usando la autenticación manual."""
    res = login_user(username, password)
    if isinstance(res, dict) and "error" in res:
        return False, res["error"]
    
    # Login exitoso
    user = res.user
    st.session_state.user = user
    st.session_state.access_token = res.session.access_token
    st.session_state.refresh_token = res.session.refresh_token
    
    # Obtener perfil y actualizar presencia
    profile = get_user_profile(user.id)
    st.session_state.profile = profile
    
    nombre = profile.get("nombre", username) if profile else username
    set_user_presence(user.id, nombre)
    
    return True, "Login exitoso"

def handle_register(username, password):
    """Maneja el flujo de registro desde la vista usando autenticación manual."""
    res = register_user(username, password)
    if isinstance(res, dict) and "error" in res:
        return False, res["error"]
    
    return True, "Registro exitoso. Por favor, inicia sesión."

def handle_logout():
    """Maneja el flujo de logout."""
    if st.session_state.user:
        remove_user_presence(st.session_state.user.id)
        logout_user()
        st.session_state.user = None
        if "profile" in st.session_state:
            st.session_state.profile = None

def require_auth():
    """Verifica si el usuario está autenticado, sino detiene la ejecución."""
    init_session()
    if not st.session_state.user:
        st.warning("Debes iniciar sesión para acceder a esta página.")
        st.stop()

def mostrar_logout_sidebar():
    """Muestra un botón de cerrar sesión en la barra lateral si el usuario está activo."""
    init_session()
    if st.session_state.user:
        with st.sidebar:
            st.divider()
            nombre = st.session_state.profile.get("nombre", "Usuario") if st.session_state.profile else "Usuario"
            st.write(f"👤 **{nombre}**")
            if st.button("Cerrar Sesión", key="btn_logout_sidebar"):
                handle_logout()
                st.rerun()
