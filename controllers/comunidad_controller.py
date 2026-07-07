from db.realtime import get_active_users, set_user_presence
import streamlit as st

def get_comunidad_data():
    """Obtiene y formatea los datos de los usuarios conectados."""
    users = get_active_users()
    return users

def update_current_user_activity():
    """Actualiza el timestamp de última actividad del usuario actual."""
    if "user" in st.session_state and st.session_state.user:
        user_id = st.session_state.user.id
        nombre = st.session_state.profile.get("nombre", "Usuario") if st.session_state.profile else "Usuario"
        set_user_presence(user_id, nombre)
