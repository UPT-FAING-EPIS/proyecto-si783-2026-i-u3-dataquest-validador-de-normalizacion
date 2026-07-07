import streamlit as st
from controllers.auth_controller import require_auth, mostrar_logout_sidebar
from controllers.validacion_controller import procesar_esquema
from visualizacion.estilos import aplicar_estilos


aplicar_estilos()


require_auth()

st.title("🔍 Validador de Esquemas")
st.markdown("Sube tu esquema de base de datos o pega el código SQL directamente para analizarlo.")

opcion = st.radio("Método de entrada", ["Pegar SQL", "Subir archivo (.sql, .csv, .xls, .txt)"])

input_data = None
formato = None

if opcion == "Pegar SQL":
    input_data = st.text_area("Pega tus sentencias CREATE TABLE aquí:", height=200)
    formato = "texto_pegado"
else:
    archivo = st.file_uploader("Sube tu archivo", type=["sql", "csv", "xlsx", "txt"])
    if archivo:
        # Para simplificar en esta fase, leemos el contenido como texto si es sql/txt
        if archivo.name.endswith(('.sql', '.txt', '.csv')):
            input_data = archivo.getvalue().decode('utf-8')
        else:
            input_data = archivo
        formato = archivo.name.split('.')[-1]

if st.button("Analizar Esquema", type="primary"):
    if input_data:
        with st.spinner("Parseando y analizando..."):
            schema_parseado, diagnostico = procesar_esquema(input_data, formato, "")
            st.session_state.schema_actual = schema_parseado
            st.session_state.diagnostico = diagnostico
            
            # Guardar historial si hay un usuario autenticado
            if st.session_state.user:
                from controllers.validacion_controller import guardar_historial
                nombre_esquema = archivo.name if opcion != "Pegar SQL" and archivo else "Esquema_SQL_Pegado"
                historial_id = guardar_historial(st.session_state.user.id, nombre_esquema, schema_parseado, diagnostico, formato)
                if historial_id:
                    st.session_state.historial_id = historial_id
            
            st.success("Análisis completado. Redirigiendo a Resultados...")
            st.switch_page("views/05_resultados.py")
    else:
        st.warning("Por favor, proporciona el esquema antes de analizar.")
