import streamlit as st
import pandas as pd
from controllers.auth_controller import init_session
from controllers.dashboard_controller import get_dashboard_metrics, get_ultimos_escaneos
from visualizacion.estilos import aplicar_estilos

aplicar_estilos()
init_session()

if not st.session_state.user:
    st.warning("Debes iniciar sesión para ver el dashboard.")
    st.stop()

user_name = st.session_state.profile.get("nombre", "Usuario")
user_id = st.session_state.user.id

# Breadcrumb
st.markdown('<p style="color: #64748b; font-size: 0.85rem;">🛡️ DataQuest > <span style="color: #06b6d4;">Inicio</span></p>', unsafe_allow_html=True)

# Título y Subtítulo
st.markdown(f'<h1>Bienvenido, {user_name} 🚀</h1>', unsafe_allow_html=True)
st.markdown('<p>Resumen de actividad de normalización y seguridad de base de datos.</p>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Métricas (KPIs)
metrics = get_dashboard_metrics(user_id)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Validaciones realizadas", metrics["validaciones"])
with col2:
    st.metric("Tablas analizadas", metrics["tablas_analizadas"])
with col3:
    st.metric("Reportes / Hallazgos", metrics["reportes_generados"])
with col4:
    st.metric("Online ahora", metrics["online"])

st.markdown("<br><br>", unsafe_allow_html=True)

# Gráficos del usuario
st.markdown("<h3>Tus Estadísticas de Normalización</h3>", unsafe_allow_html=True)
from controllers.dashboard_controller import get_user_charts_data
charts_data = get_user_charts_data(user_id)

col_chart1, col_chart2 = st.columns(2)
with col_chart1:
    st.markdown("**Niveles Iniciales (Tus Esquemas)**")
    df_inicial = charts_data.get("df_inicial")
    if df_inicial is not None and not df_inicial.empty:
        import plotly.express as px
        fig_ini = px.pie(df_inicial, values='Cantidad', names='Nivel', hole=0.4, 
                         color_discrete_sequence=px.colors.sequential.Blues_r, template="plotly_dark")
        fig_ini.update_traces(textposition='inside', textinfo='percent+label')
        fig_ini.update_layout(margin=dict(t=20, b=20, l=20, r=20), showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_ini, use_container_width=True)
    else:
        st.info("Aún no tienes datos suficientes para este gráfico.")
        
with col_chart2:
    st.markdown("**Niveles Finales Alcanzados**")
    df_final = charts_data.get("df_final")
    if df_final is not None and not df_final.empty:
        import plotly.express as px
        fig_fin = px.pie(df_final, values='Cantidad', names='Nivel', hole=0.4, 
                         color_discrete_sequence=px.colors.sequential.Teal_r, template="plotly_dark")
        fig_fin.update_traces(textposition='inside', textinfo='percent+label')
        fig_fin.update_layout(margin=dict(t=20, b=20, l=20, r=20), showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_fin, use_container_width=True)
    else:
        st.info("Aún no tienes datos suficientes para este gráfico.")

st.markdown("<br><br>", unsafe_allow_html=True)

# Últimos Escaneos
st.markdown("<h3>Últimas validaciones</h3>", unsafe_allow_html=True)

escaneos = get_ultimos_escaneos(user_id, limit=5)

if not escaneos:
    st.info("No tienes validaciones recientes. Ve a la herramienta de Validador para empezar.")
else:
    # Preparar datos para la tabla
    tabla_datos = []
    for escaneo in escaneos:
        nombre = escaneo.get("nombre_esquema", "Esquema sin nombre")
        estado = "completed" if escaneo.get("nivel_final") else "pending"
        
        # Determinar "Severidad" o Estado basado en si tiene nivel_objetivo alcanzado
        nivel_ini = escaneo.get("nivel_inicial", "")
        nivel_fin = escaneo.get("nivel_final", "")
        if nivel_fin == "3fn":
            severidad = "Bajo"
        elif nivel_fin == "2fn":
            severidad = "Medio"
        else:
            severidad = "Alto"
            
        fecha = escaneo.get("fecha", "")[:19].replace("T", " ")
        
        tabla_datos.append({
            "Esquema / Base de Datos": nombre,
            "Estado": estado,
            "Severidad Restante": severidad,
            "Fecha": fecha
        })
        
    df = pd.DataFrame(tabla_datos)
    st.dataframe(df, use_container_width=True, hide_index=True)
