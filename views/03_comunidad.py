import streamlit as st


from controllers.auth_controller import init_session, mostrar_logout_sidebar
from controllers.comunidad_controller import get_comunidad_data, update_current_user_activity
import time
from visualizacion.estilos import aplicar_estilos

aplicar_estilos()


# Opcional: st_autorefresh se eliminó porque causa parpadeos constantes en Streamlit
# Si deseas refrescar, usa el botón nativo o un st.button("Actualizar")
try:
    from streamlit_autorefresh import st_autorefresh
    # st_autorefresh(interval=5000, limit=100, key="comunidad_refresh") # COMENTADO PARA EVITAR PARPADEO
except ImportError:
    pass

init_session()
update_current_user_activity()

st.title("🌐 Comunidad en Vivo")
st.markdown("Usuarios conectados actualmente en el validador.")

usuarios = get_comunidad_data()

if not usuarios:
    st.info("No hay usuarios conectados en este momento.")
else:
    for u in usuarios:
        with st.container():
            col1, col2 = st.columns([1, 4])
            with col1:
                st.image("https://api.dicebear.com/7.x/avataaars/svg?seed=" + u.get("user_id", "default"), width=50)
            with col2:
                st.write(f"**{u.get('nombre', 'Anónimo')}**")
                st.caption(f"Activo desde: {u.get('conectado_en', '')[:16]}")
            st.divider()
