import streamlit as st
from controllers.auth_controller import require_auth, mostrar_logout_sidebar
from db.conexion import get_supabase_client
from visualizacion.estilos import aplicar_estilos


aplicar_estilos()


require_auth()

st.title("📜 Tu Historial de Validaciones")

supabase = get_supabase_client()
user_id = st.session_state.user.id

try:
    response = supabase.table("historial_validaciones").select("*").eq("user_id", user_id).order("fecha", desc=True).execute()
    historial = response.data
    
    if not historial:
        st.info("No tienes validaciones registradas aún.")
    else:
        for h in historial:
            with st.expander(f"🕒 {h['fecha'][:16]} - {h['nombre_esquema']}"):
                nivel_inicial = (h.get('nivel_inicial') or 'N/A').upper()
                nivel_objetivo = (h.get('nivel_objetivo') or 'No definido').upper()
                nivel_final = (h.get('nivel_final') or 'No definido').upper()
                
                st.markdown(f"**Nivel de Normalización:** Inicial: `{nivel_inicial}` ➔ Objetivo: `{nivel_objetivo}` ➔ Final: `{nivel_final}`")
                st.markdown(f"**Formato de entrada:** `{h.get('formato_entrada', 'N/A')}`")
                
                try:
                    from core.generador_pdf import generar_pdf_reporte
                    pdf_bytes = generar_pdf_reporte(
                        esquema_original=h.get('esquema_original'),
                        nivel_inicial=nivel_inicial,
                        nivel_objetivo=nivel_objetivo,
                        nivel_final=nivel_final,
                        violaciones=h.get('violaciones', {}),
                        sugerencias=h.get('sugerencias', []),
                        nombre_esquema=h.get('nombre_esquema', 'Desconocido')
                    )
                    st.download_button(
                        label="📄 Descargar Reporte PDF",
                        data=pdf_bytes,
                        file_name=f"reporte_{h.get('nombre_esquema', 'esquema')}.pdf",
                        mime="application/pdf",
                        key=f"dl_pdf_{h['id']}"
                    )
                except Exception as e:
                    st.error(f"Error generando PDF: {e}")
                
                st.divider()
                
                tab_sql, tab_mermaid, tab_viol, tab_sug = st.tabs(["📜 Consulta Original", "🧜‍♂️ Código Mermaid (Final)", "🚨 Errores", "💡 Soluciones"])
                
                with tab_sql:
                    esquema_original = h.get('esquema_original')
                    if esquema_original and 'tablas' in esquema_original:
                        for t in esquema_original['tablas']:
                            st.code(t.get('sql_original', f"CREATE TABLE {t.get('nombre', 'Desconocido')} (...);"), language="sql")
                    else:
                        st.info("No hay información de consulta SQL disponible.")
                        
                with tab_mermaid:
                    esquema_final = h.get('esquema_final')
                    if esquema_final:
                        from visualizacion.diagrama_er import generar_mermaid_er
                        mermaid_code = generar_mermaid_er(esquema_final)
                        st.markdown("Copia este código y pégalo en [Mermaid Live Editor](https://mermaid.live/) o en tu Markdown:")
                        st.code(mermaid_code, language="mermaid")
                    else:
                        st.info("No hay esquema final disponible. Asegúrate de haber aplicado sugerencias en el validador.")
                
                with tab_viol:
                    violaciones = h.get('violaciones', {})
                    hay_violaciones = False
                    
                    if violaciones:
                        for fn in ["violaciones_1fn", "violaciones_2fn", "violaciones_3fn"]:
                            for v in violaciones.get(fn, []):
                                hay_violaciones = True
                                st.error(f"**{v.get('tipo', 'Error')}**")
                                st.write(v.get('mensaje', ''))
                                if v.get('sql_original'):
                                    st.code(v['sql_original'], language='sql')
                                st.divider()
                                
                    if not hay_violaciones:
                        st.success("No se registraron violaciones críticas en este análisis.")
                        
                with tab_sug:
                    sugerencias = h.get('sugerencias')
                    if sugerencias:
                        for idx, sug in enumerate(sugerencias):
                            with st.container(border=True):
                                col_title, col_badge1, col_badge2 = st.columns([6, 2, 2])
                                with col_title:
                                    st.markdown(f"**[{sug.get('nivel', 'Opcional')}] {sug.get('accion', 'Sugerencia')}**")
                                with col_badge1:
                                    impacto = sug.get("impacto", "N/A")
                                    color = "red" if impacto == "Alto" else "green"
                                    st.markdown(f":{color}[**Impacto:** {impacto}]")
                                with col_badge2:
                                    st.markdown(f"**Confianza:** {sug.get('confianza', 'N/A')}")
                                
                                st.write(sug.get("detalle", ""))
                                
                                # Beneficios
                                if "beneficios" in sug and sug["beneficios"]:
                                    st.markdown("**Beneficios:**")
                                    for b in sug["beneficios"]:
                                        st.markdown(f"- ✓ {b}")
                                        
                                if sug.get("sql_original"):
                                    st.caption("SQL original afectado:")
                                    st.code(sug["sql_original"], language="sql")
                    else:
                        st.info("No hay sugerencias registradas.")
except Exception as e:
    st.error(f"No se pudo cargar el historial: {e}")
