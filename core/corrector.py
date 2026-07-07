def generar_sugerencias(diagnostico):
    """
    Genera sugerencias enriquecidas (formato Copiloto) para normalizar el esquema.
    Incluye impacto, confianza y beneficios para asistir al usuario.
    """
    sugerencias = []
    
    # Sugerencias 1FN
    for violacion in diagnostico.get("violaciones_1fn", []):
        if "Primary Key" in violacion["tipo"]:
            sugerencias.append({
                "nivel": "1FN",
                "accion": "Añadir Clave Primaria",
                "detalle": violacion["mensaje"] + " Agrega un campo 'id' autoincremental o define una Primary Key lógica.",
                "sql_original": violacion.get("sql_original", ""),
                "impacto": "Alto",
                "confianza": "100%",
                "beneficios": ["Asegura unicidad de registros.", "Cumple la 1FN indispensable.", "Permite crear relaciones."],
                "tipo_mejora": "critica"
            })
        else:
            # Grupo repetitivo
            sugerencias.append({
                "nivel": "1FN",
                "accion": "Separar atributos multivaluados",
                "detalle": violacion["mensaje"],
                "sql_original": violacion.get("sql_original", ""),
                "impacto": "Alto",
                "confianza": "90%",
                "beneficios": ["Cumple la 1FN.", "Evita redundancia y espacios nulos.", "Facilita búsquedas exactas."],
                "tipo_mejora": "critica"
            })
            
    # Sugerencias 2FN
    for violacion in diagnostico.get("violaciones_2fn", []):
        sugerencias.append({
            "nivel": "2FN",
            "accion": "Crear nueva tabla (Dependencia Parcial)",
            "detalle": violacion["mensaje"],
            "sql_original": violacion.get("sql_original", ""),
            "impacto": "Alto",
            "confianza": "100%",
            "beneficios": ["Cumple 2FN.", "Elimina anomalías de actualización.", "Reduce espacio almacenado redundante."],
            "tipo_mejora": "critica"
        })
        
    # Sugerencias 3FN
    for violacion in diagnostico.get("violaciones_3fn", []):
        sugerencias.append({
            "nivel": "3FN",
            "accion": "Mover a tabla de catálogo (Dependencia Transitiva)",
            "detalle": violacion["mensaje"],
            "sql_original": violacion.get("sql_original", ""),
            "impacto": "Alto",
            "confianza": "95%",
            "beneficios": ["Cumple 3FN.", "Evita anomalías de inserción y borrado.", "Independiza la gestión de catálogos."],
            "tipo_mejora": "critica"
        })
        
    # Mejoras opcionales (Semánticas)
    for opcional in diagnostico.get("mejoras_opcionales", []):
        sugerencias.append({
            "nivel": "Opcional",
            "accion": f"Dividir columna '{opcional['columna']}'",
            "detalle": opcional["mensaje"],
            "sql_original": "",
            "impacto": "Bajo",
            "confianza": "50%",
            "beneficios": ["Mayor flexibilidad.", "Búsquedas más precisas y filtros avanzados."],
            "tipo_mejora": "opcional",
            "tabla": opcional["tabla"],
            "columna": opcional["columna"],
            "sugerencia_columnas": opcional["sugerencia_columnas"]
        })
        
    return sugerencias
