import streamlit as st
from visualizacion.estilos import aplicar_estilos
from controllers.auth_controller import init_session, mostrar_logout_sidebar

st.set_page_config(
    page_title="DataQuest",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

aplicar_estilos()
init_session()
mostrar_logout_sidebar()

# Create pages
# Create pages
auth_page = st.Page("views/00_auth.py", title="Autenticación", icon="🔑", default=True)

inicio_page = st.Page("views/00_inicio.py", title="Inicio", icon="🏠", default=True)
validador_page = st.Page("views/04_validador.py", title="Validador", icon="🛡️")
resultados_page = st.Page("views/05_resultados.py", title="Resultados", icon="📊")
historial_page = st.Page("views/06_historial.py", title="Historial", icon="🕒")
comunidad_page = st.Page("views/03_comunidad.py", title="Comunidad", icon="👥")

# Routing based on auth state
if st.session_state.user:
    # Add absolute positioning to put it directly under the logo
    st.sidebar.markdown(
        f"""
        <div class="user-active-box">
            <span style='color:#64748b; font-size:0.7rem; font-weight:700;'>USUARIO ACTIVO</span><br>
            <span style='color:#06b6d4; font-weight:600;'>👤 {st.session_state.profile.get('nombre', 'Usuario')}</span>
        </div>
        """, unsafe_allow_html=True
    )
    
    # Flatten list to avoid "View more" grouping
    pg = st.navigation([inicio_page, validador_page, resultados_page, historial_page, comunidad_page])
else:
    pg = st.navigation([auth_page])

pg.run()
