import streamlit as st
from controllers.auth_controller import require_auth, mostrar_logout_sidebar
from controllers.validacion_controller import generar_sugerencias_para_nivel
from visualizacion.estilos import aplicar_estilos
# from visualizacion.diagrama_er import render_er
# from visualizacion.diagrama_schema import render_schema


aplicar_estilos()


require_auth()

st.title("📊 Resultados de Normalización")

if "schema_actual" not in st.session_state or not st.session_state.schema_actual:
    st.warning("Aún no has analizado ningún esquema. Ve a la pestaña **Validador** primero.")
    st.stop()

diagnostico = st.session_state.diagnostico
nivel_objetivo = st.session_state.get("nivel_objetivo", "1FN")

st.markdown(f"### Estado actual: `{diagnostico.get('nivel_actual', 'Desconocido').upper()}`")

with st.expander("🔍 Ver esquema extraído (Datos analizados)", expanded=True):
    tablas = st.session_state.schema_actual.get("tablas", [])
    if not tablas:
        st.warning("No se detectó ninguna tabla en el archivo subido. Verifica el formato del SQL.")
    else:
        st.success(f"Se extrajeron {len(tablas)} tabla(s) exitosamente.")
        for t in tablas:
            st.markdown(f"**Tabla:** `{t['nombre']}`")
            st.markdown(f"- **Columnas:** {', '.join(t['columnas'])}")
            if t['pks']:
                st.markdown(f"- **Llave(s) Primaria(s):** {', '.join(t['pks'])}")
            st.divider()

col_obj_1, col_obj_2 = st.columns([1, 3])
with col_obj_1:
    nivel_objetivo = st.selectbox("🎯 Selecciona tu nivel objetivo", ["1FN", "2FN", "3FN"], index=2)
    st.session_state.nivel_objetivo = nivel_objetivo

st.divider()

col1, col2 = st.columns(2)

with col1:
    st.subheader("💡 Sugerencias de Corrección")
    
    sugerencias = generar_sugerencias_para_nivel(st.session_state.schema_actual, nivel_objetivo)
    
    # Inicializar estado para checkboxes
    if "mejoras_seleccionadas" not in st.session_state:
        st.session_state.mejoras_seleccionadas = []
        
    sugerencias_marcadas = []
    
    if not sugerencias:
        st.info("No hay sugerencias disponibles o el esquema ya cumple el nivel.")
    else:
        criticas = [s for s in sugerencias if s.get("tipo_mejora") == "critica"]
        opcionales = [s for s in sugerencias if s.get("tipo_mejora") == "opcional"]
        
        st.success(f"**Análisis completado.** Se encontraron: ✓ {len(criticas)} problemas críticos. ✓ {len(opcionales)} mejoras recomendadas.")
        st.write("Selecciona las mejoras que deseas aplicar para verlas reflejadas en el diagrama.")
        
        for idx, sug in enumerate(sugerencias):
            with st.container(border=True):
                col_chk, col_badge1, col_badge2 = st.columns([6, 2, 2])
                with col_chk:
                    checked = st.checkbox(
                        f"**[{sug['nivel']}] {sug['accion']}**", 
                        value=True, # Por defecto marcadas
                        key=f"chk_sug_{idx}"
                    )
                    if checked:
                        sugerencias_marcadas.append(sug)
                with col_badge1:
                    color = "red" if sug.get("impacto") == "Alto" else "green"
                    st.markdown(f":{color}[**Impacto:** {sug.get('impacto', 'Medio')}]")
                with col_badge2:
                    st.markdown(f"**Confianza:** {sug.get('confianza', '100%')}")
                
                st.write(sug["detalle"])
                
                # Beneficios
                if "beneficios" in sug and sug["beneficios"]:
                    st.markdown("**Beneficios:**")
                    for b in sug["beneficios"]:
                        st.markdown(f"- ✓ {b}")
                
                if sug.get("sql_original"):
                    with st.expander("Ver código SQL original afectado"):
                        st.code(sug["sql_original"], language="sql")
                
    st.session_state.mejoras_seleccionadas = sugerencias_marcadas
    
    st.subheader("🛠️ Aplicar Normalización")
    
    # Calcular en tiempo real el esquema y el SQL
    from core.generador_sql import aplicar_mejoras
    nuevo_esquema, sql_nuevo = aplicar_mejoras(st.session_state.schema_actual, st.session_state.mejoras_seleccionadas)
    
    # Descargar y Confirmar
    st.markdown("### 3. Descargar y Confirmar")
    
    col_btn_aplicar, _ = st.columns([1, 1])
    with col_btn_aplicar:
        if st.button("✅ Aplicar Sugerencias y Guardar en Historial", type="primary", use_container_width=True):
            if "historial_id" in st.session_state and st.session_state.historial_id:
                from controllers.validacion_controller import actualizar_historial
                actualizar_historial(
                    st.session_state.historial_id, 
                    nivel_objetivo, 
                    nivel_objetivo, 
                    st.session_state.mejoras_seleccionadas,
                    nuevo_esquema
                )
            st.success("¡Cambios aplicados y guardados en tu historial!")
            
    col_dl1, col_dl2, col_dl3 = st.columns(3)
    with col_dl1:
        st.download_button(
            label="Descargar Script (.sql)",
            data=sql_nuevo,
            file_name="schema_normalizado.sql",
            mime="text/plain",
            use_container_width=True
        )
    with col_dl2:
        st.download_button(
            label="Descargar Script (.txt)",
            data=sql_nuevo,
            file_name="schema_normalizado.txt",
            mime="text/plain",
            use_container_width=True
        )
    with col_dl3:
        try:
            from core.generador_pdf import generar_pdf_reporte
            pdf_bytes = generar_pdf_reporte(
                esquema_original=st.session_state.schema_actual,
                nivel_inicial=diagnostico.get('nivel_actual', 'Desconocido'),
                nivel_objetivo=nivel_objetivo,
                nivel_final=nivel_objetivo, # Aprox
                violaciones=diagnostico,
                sugerencias=st.session_state.mejoras_seleccionadas,
                nombre_esquema="Esquema Validado"
            )
            st.download_button(
                label="Descargar Reporte (.pdf)",
                data=pdf_bytes,
                file_name="reporte_normalizacion.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"Error PDF: {e}")
        
    with st.expander("Ver SQL Generado"):
        st.code(sql_nuevo, language="sql")

with col2:
    st.subheader("🖼️ Vista Previa del Nuevo Esquema")
    
    if nuevo_esquema:
        from visualizacion.diagrama_er import generar_mermaid_er
        import streamlit.components.v1 as components
        
        mermaid_code = generar_mermaid_er(nuevo_esquema)
        
        html_code = f"""
<div id="mermaid-container" style="background: white; width: 100%; height: 100%; position: relative; overflow: auto; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
    <button onclick="document.getElementById('mermaid-container').requestFullscreen()" style="position: absolute; top: 10px; right: 10px; z-index: 9999; padding: 10px; background: #f0f2f6; border: 1px solid #ccc; border-radius: 5px; cursor: pointer; box-shadow: 0 2px 5px rgba(0,0,0,0.2);">
        ⛶ Pantalla Completa
    </button>
    <div class="mermaid" style="display: flex; justify-content: center; align-items: center; min-width: 100%; min-height: 100%; padding-top: 50px;">
{mermaid_code}
    </div>
</div>
<script type="module">
    import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
    mermaid.initialize({{ startOnLoad: true, theme: 'default' }});
</script>
"""
        components.html(html_code, height=600, scrolling=True)
    else:
        st.write("No hay datos para mostrar.")
