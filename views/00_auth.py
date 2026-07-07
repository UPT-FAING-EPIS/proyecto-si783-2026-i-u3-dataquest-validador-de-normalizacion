import streamlit as st
from controllers.auth_controller import handle_login, handle_register, init_session, mostrar_logout_sidebar
from visualizacion.estilos import aplicar_estilos

aplicar_estilos()
init_session()

# Custom CSS for Auth Page to match AnzenCore style
st.markdown("""
<style>
/* Center the main container */
[data-testid="block-container"] {
    max-width: 600px;
    padding-top: 4rem;
}

/* Auth Header Card */
.auth-header {
    background: #141c2c;
    border-radius: 20px;
    padding: 40px 20px;
    text-align: center;
    box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    margin-bottom: 30px;
    border: 1px solid rgba(255, 255, 255, 0.05);
}

.auth-header img {
    width: 64px;
    margin-bottom: 15px;
}

.auth-header h1 {
    font-size: 2rem !important;
    font-weight: 700 !important;
    background: linear-gradient(to right, #2dd4bf, #3b82f6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0 !important;
    padding: 0 !important;
    text-shadow: none;
}

.auth-header p {
    color: #64748b;
    font-size: 0.95rem;
    margin-top: 5px;
}

/* Custom Tabs Styling */
[data-baseweb="tab-list"] {
    gap: 0;
    border-bottom: 1px solid rgba(255,255,255,0.1);
    margin-bottom: 20px;
    background: transparent;
}

[data-baseweb="tab"] {
    background-color: transparent !important;
    border: none !important;
    padding: 12px 20px !important;
    color: #64748b !important;
    font-weight: 500 !important;
    font-size: 0.95rem !important;
}

[data-baseweb="tab"][aria-selected="true"] {
    color: #2dd4bf !important;
    border-bottom: 2px solid #2dd4bf !important;
}

/* Transparent Inputs */
.stTextInput > div > div > input {
    background-color: #141c2c !important;
    border: 1px solid #1e293b !important;
    border-radius: 8px !important;
    color: #f8fafc !important;
}

.stTextInput > div > div > input:focus {
    border-color: #2dd4bf !important;
    box-shadow: 0 0 0 1px #2dd4bf !important;
}

/* Outline Button */
[data-testid="stFormSubmitButton"] > button {
    background: transparent !important;
    border: 1px solid #2dd4bf !important;
    color: #2dd4bf !important;
    box-shadow: none !important;
    border-radius: 8px !important;
}

[data-testid="stFormSubmitButton"] > button:hover {
    background: rgba(45, 212, 191, 0.1) !important;
    box-shadow: 0 0 15px rgba(45, 212, 191, 0.2) !important;
    border: 1px solid #2dd4bf !important;
}

[data-testid="stFormSubmitButton"] > button::before {
    display: none;
}

/* Hide Streamlit Sidebar in Auth if desired */
[data-testid="stSidebar"] {
    display: none;
}
</style>

<div class="auth-header">
    <img src="https://img.icons8.com/color/96/000000/shield.png" alt="Logo">
    <h1>DataQuest</h1>
    <p>Plataforma de normalización de datos</p>
</div>
""", unsafe_allow_html=True)


if st.session_state.user:
    st.success(f"Sesión activa como: {st.session_state.profile.get('nombre', 'Usuario')}")
    if st.button("Cerrar Sesión"):
        from controllers.auth_controller import handle_logout
        handle_logout()
        st.rerun()
else:
    tab1, tab2, tab3 = st.tabs(["🔑 Iniciar sesión", "✨ Crear cuenta", "🌍 Dashboard Global"])
    
    with tab1:
        with st.form("login_form", clear_on_submit=False):
            st.caption("Usuario")
            username = st.text_input("Tu usuario", label_visibility="collapsed", placeholder="Tu usuario")
            st.caption("Contraseña")
            password = st.text_input("Tu contraseña", label_visibility="collapsed", type="password", placeholder="••••••••")
            submit_login = st.form_submit_button("Iniciar sesión")

            if submit_login:
                if not username or not password:
                    st.error("Por favor, ingresa credenciales.")
                else:
                    with st.spinner("Verificando..."):
                        exito, mensaje = handle_login(username, password)
                        if exito:
                            st.rerun()
                        else:
                            st.error(mensaje)
                            
    with tab2:
        with st.form("register_form", clear_on_submit=False):
            st.caption("Usuario")
            username_reg = st.text_input("Nuevo usuario", label_visibility="collapsed", placeholder="Elige un usuario")
            st.caption("Contraseña")
            password_reg = st.text_input("Nueva contraseña", label_visibility="collapsed", type="password", placeholder="••••••••")
            submit_reg = st.form_submit_button("Crear cuenta")

            if submit_reg:
                if not username_reg or not password_reg:
                    st.error("Todos los campos son obligatorios.")
                else:
                    with st.spinner("Creando cuenta..."):
                        exito, mensaje = handle_register(username_reg, password_reg)
                        if exito:
                            st.success(mensaje + " ¡Ahora puedes iniciar sesión!")
                        else:
                            st.error(mensaje)

    with tab3:
        st.subheader("Estadísticas Globales de Normalización")
        st.markdown("Vista general de las bases de datos analizadas por el sistema.")
        
        from controllers.dashboard_global_controller import get_global_metrics, format_data_for_charts
        metricas = get_global_metrics()
        df_inicial, df_final = format_data_for_charts(metricas)
        
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.metric("Total de Validaciones", metricas["total_validaciones"])
        with col_m2:
            st.metric("Usuarios Únicos", metricas["usuarios_unicos"])
            
        st.divider()
        
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            st.markdown("**Niveles Iniciales Detectados**")
            if not df_inicial.empty:
                import plotly.express as px
                fig_ini = px.pie(df_inicial, values='Cantidad', names='Nivel', hole=0.4, 
                                 color_discrete_sequence=px.colors.sequential.Blues_r, template="plotly_dark")
                fig_ini.update_traces(textposition='inside', textinfo='percent+label')
                fig_ini.update_layout(margin=dict(t=20, b=20, l=20, r=20), showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_ini, use_container_width=True)
            else:
                st.info("Sin datos aún.")
                
        with col_g2:
            st.markdown("**Niveles Finales Alcanzados**")
            if not df_final.empty:
                import plotly.express as px
                fig_fin = px.pie(df_final, values='Cantidad', names='Nivel', hole=0.4, 
                                 color_discrete_sequence=px.colors.sequential.Teal_r, template="plotly_dark")
                fig_fin.update_traces(textposition='inside', textinfo='percent+label')
                fig_fin.update_layout(margin=dict(t=20, b=20, l=20, r=20), showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_fin, use_container_width=True)
            else:
                st.info("Sin datos aún.")

