import datetime
from fpdf import FPDF

class ReportePDF(FPDF):
    def header(self):
        # Logo placeholder (optional, can be skipped or use a text logo)
        self.set_font("helvetica", "B", 20)
        self.set_text_color(45, 212, 191) # #2dd4bf Teal
        self.cell(0, 10, "DataQuest", ln=True, align="C")
        
        self.set_font("helvetica", "B", 14)
        self.set_text_color(100, 116, 139) # #64748b Slate
        self.cell(0, 10, "Reporte de Normalizacion de Base de Datos", ln=True, align="C")
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f"Pagina {self.page_no()}/{{nb}}", align="C", ln=1)

def safe_multi_cell(pdf, w, h, txt):
    import textwrap
    lines = []
    for line in str(txt).split("\n"):
        if not line.strip():
            lines.append("")
        else:
            lines.extend(textwrap.wrap(line, width=100, break_long_words=True))
    for wrapped_line in lines:
        pdf.cell(w, h, wrapped_line, ln=1)

def generar_pdf_reporte(esquema_original, nivel_inicial, nivel_objetivo, nivel_final, violaciones, sugerencias, nombre_esquema="Esquema de Base de Datos"):
    pdf = ReportePDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    
    # Enable automatic page breaking
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Metadata
    pdf.set_font("helvetica", "", 11)
    pdf.set_text_color(0, 0, 0)
    fecha_actual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    pdf.cell(0, 8, f"Fecha de generacion: {fecha_actual}", ln=True)
    pdf.cell(0, 8, f"Nombre del Esquema: {nombre_esquema}", ln=True)
    pdf.ln(5)
    
    # Resumen de Normalización
    pdf.set_font("helvetica", "B", 14)
    pdf.set_fill_color(240, 248, 255)
    pdf.cell(0, 10, "1. Resumen de Niveles de Normalizacion", ln=True, fill=True)
    pdf.set_font("helvetica", "", 11)
    pdf.cell(0, 8, f"Nivel Inicial Detectado: {str(nivel_inicial).upper()}", ln=True)
    pdf.cell(0, 8, f"Nivel Objetivo Seleccionado: {str(nivel_objetivo).upper()}", ln=True)
    pdf.cell(0, 8, f"Nivel Final Alcanzado: {str(nivel_final).upper() if nivel_final else 'Pendiente'}", ln=True)
    pdf.ln(5)
    
    # Esquema Original Analizado
    pdf.set_font("helvetica", "B", 14)
    pdf.cell(0, 10, "2. Esquema Original Analizado", ln=True, fill=True)
    pdf.set_font("helvetica", "", 10)
    
    if esquema_original and "tablas" in esquema_original:
        for tabla in esquema_original["tablas"]:
            nombre = tabla.get("nombre", "Desconocido")
            columnas = ", ".join(tabla.get("columnas", []))
            pks = ", ".join(tabla.get("pks", []))
            
            # Using multi_cell for wrapping long text
            pdf.set_font("helvetica", "B", 10)
            pdf.cell(0, 6, f"Tabla: {nombre}", ln=True)
            pdf.set_font("helvetica", "", 10)
            safe_multi_cell(pdf, 0, 6, f"Columnas: {columnas}")
            if pks:
                pdf.cell(0, 6, f"Llave Primaria: {pks}", ln=True)
            pdf.ln(2)
    else:
        pdf.cell(0, 8, "No se encontro informacion del esquema original.", ln=True)
    pdf.ln(5)
    
    # Violaciones Encontradas
    pdf.set_font("helvetica", "B", 14)
    pdf.cell(0, 10, "3. Problemas y Violaciones Detectadas", ln=True, fill=True)
    
    hay_violaciones = False
    if violaciones:
        for fn in ["violaciones_1fn", "violaciones_2fn", "violaciones_3fn"]:
            lista_v = violaciones.get(fn, [])
            if lista_v:
                pdf.set_font("helvetica", "B", 12)
                pdf.set_text_color(220, 38, 38) # Red
                pdf.cell(0, 8, f"En {fn.split('_')[1].upper()}:", ln=True)
                pdf.set_text_color(0, 0, 0)
                pdf.set_font("helvetica", "", 10)
                
                for v in lista_v:
                    hay_violaciones = True
                    tipo = v.get("tipo", "Problema")
                    msj = v.get("mensaje", "")
                    
                    msj = msj.encode('latin-1', 'replace').decode('latin-1')
                    pdf.set_font("helvetica", "B", 10)
                    pdf.cell(0, 6, f"- {tipo}", ln=True)
                    pdf.set_font("helvetica", "", 10)
                    safe_multi_cell(pdf, 0, 6, f"  {msj}")
                    pdf.ln(2)
    
    if not hay_violaciones:
        pdf.set_font("helvetica", "I", 10)
        pdf.cell(0, 8, "No se detectaron violaciones en los niveles evaluados.", ln=True)
    pdf.ln(5)
    
    # Sugerencias / Mejoras
    pdf.set_font("helvetica", "B", 14)
    pdf.cell(0, 10, "4. Sugerencias de Normalizacion", ln=True, fill=True)
    
    if sugerencias:
        for idx, sug in enumerate(sugerencias, 1):
            nivel = sug.get("nivel", "")
            accion = sug.get("accion", "").encode('latin-1', 'replace').decode('latin-1')
            detalle = sug.get("detalle", "").encode('latin-1', 'replace').decode('latin-1')
            impacto = sug.get("impacto", "")
            
            pdf.set_font("helvetica", "B", 11)
            pdf.cell(0, 8, f"{idx}. [{nivel}] {accion}", ln=True)
            
            pdf.set_font("helvetica", "", 10)
            pdf.cell(0, 6, f"Impacto: {impacto}", ln=True)
            safe_multi_cell(pdf, 0, 6, detalle)
            
            if "beneficios" in sug and sug["beneficios"]:
                pdf.set_font("helvetica", "I", 10)
                pdf.cell(0, 6, "Beneficios:", ln=True)
                for b in sug["beneficios"]:
                    b_str = str(b).encode('latin-1', 'replace').decode('latin-1')
                    safe_multi_cell(pdf, 0, 6, f" - {b_str}")
            pdf.ln(3)
    else:
        pdf.set_font("helvetica", "I", 10)
        pdf.cell(0, 8, "No hay sugerencias registradas o aplicadas.", ln=True)
        
    return bytes(pdf.output())
