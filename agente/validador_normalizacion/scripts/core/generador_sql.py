import copy
import re

def aplicar_mejoras(esquema_original, sugerencias_seleccionadas):
    """
    Aplica las mejoras seleccionadas al esquema original.
    Retorna (nuevo_esquema_dict, sql_generado)
    """
    nuevo_esquema = copy.deepcopy(esquema_original)
    tablas = nuevo_esquema.get("tablas", [])
    
    # Inicializar comentarios en las tablas
    for t in tablas:
        if "comentarios" not in t:
            t["comentarios"] = []
    
    # Nuevas tablas a crear (para 2FN y 3FN)
    nuevas_tablas_agregadas = []
    
    for sug in sugerencias_seleccionadas:
        nivel = sug.get("nivel")
        if nivel == "1FN":
            # Heurística simple: agregar id si falta
            for t in tablas:
                if t["nombre"] in sug.get("mensaje", ""):
                    if "id" not in t["columnas"] and f"id_{t['nombre']}" not in t["columnas"]:
                        t["columnas"].insert(0, f"id_{t['nombre']}")
                        if "pks" not in t: t["pks"] = []
                        t["pks"].append(f"id_{t['nombre']}")
                        t["comentarios"].append(f"Se añadió Clave Primaria 'id_{t['nombre']}' automáticamente para cumplir con 1FN.")
        elif nivel in ["2FN", "3FN"]:
            # Identificar qué dependientes se deben separar
            try:
                match_dep = re.search(r"atributos.*?\[(.*?)\]", sug.get("mensaje", ""))
                match_det = re.search(r"a través de \[.*?\]|atributo no clave \[(.*?)\]", sug.get("mensaje", ""))
                if match_dep:
                    deps = [x.strip().strip("'") for x in match_dep.group(1).split(",")]
                    
                    # Buscar la tabla afectada
                    for t in tablas:
                        if t["nombre"] in sug.get("mensaje", ""):
                            # Sacar las columnas dependientes
                            columnas_removidas = []
                            for d in deps:
                                if d in t["columnas"]:
                                    t["columnas"].remove(d)
                                    columnas_removidas.append(d)
                            
                            # Crear nueva tabla con los determinantes (simulado)
                            if match_det:
                                dets = [x.strip().strip("'") for x in match_det.group(1).split(",")]
                                # Añadir FK en la tabla original
                                if "fks" not in t: t["fks"] = []
                                nueva_tabla_nombre = f"{t['nombre']}_detalle"
                                if len(dets) == 1:
                                    # Tratar de nombrar mejor si es por ejemplo departamento_id -> departamentos
                                    nueva_tabla_nombre = dets[0].replace('_id', '').replace('id_', '') + "s"
                                
                                for d in dets:
                                    t["fks"].append({"columna": d, "tabla_destino": nueva_tabla_nombre})
                                    
                                if columnas_removidas:
                                    t["comentarios"].append(f"Se eliminaron las columnas [{', '.join(columnas_removidas)}] y se movieron a '{nueva_tabla_nombre}' para cumplir con {nivel}.")
                                    
                                nuevas_tablas_agregadas.append({
                                    "nombre": nueva_tabla_nombre,
                                    "columnas": dets + deps,
                                    "pks": dets,
                                    "fks": [],
                                    "sql_original": "",
                                    "comentarios": [f"Nueva tabla extraída de '{t['nombre']}' para resolver violaciones de {nivel}.",
                                                    f"Contiene las dependencias: [{', '.join(deps)}] determinadas por [{', '.join(dets)}]."]
                                })
            except Exception:
                pass
        elif nivel == "Opcional":
            # División semántica de columnas
            tabla_nombre = sug.get("tabla")
            columna_original = sug.get("columna")
            nuevas_cols = sug.get("sugerencia_columnas", [])
            
            for t in tablas:
                if t["nombre"] == tabla_nombre:
                    if columna_original in t["columnas"]:
                        idx = t["columnas"].index(columna_original)
                        t["columnas"].remove(columna_original)
                        # Insertar las nuevas columnas en el mismo lugar
                        for i, nc in enumerate(nuevas_cols):
                            t["columnas"].insert(idx + i, nc)
                        
                        t["comentarios"].append(f"Mejora Opcional: Se dividió la columna original '{columna_original}' en múltiples columnas: [{', '.join(nuevas_cols)}].")

    # Unir las tablas originales y las nuevas
    nuevo_esquema["tablas"] = tablas + nuevas_tablas_agregadas
    
    # Generar SQL
    sql_generado = ""
    for t in nuevo_esquema["tablas"]:
        sql_generado += f"-- Tabla: {t['nombre']}\n"
        
        # Inyectar comentarios descriptivos de los cambios
        if t.get("comentarios"):
            for comentario in t["comentarios"]:
                sql_generado += f"-- [Auto-Fix] {comentario}\n"
                
        sql_generado += f"CREATE TABLE {t['nombre']} (\n"
        
        cols_def = []
        for c in t["columnas"]:
            tipo = "INT" if c.startswith("id") or c.endswith("id") else "VARCHAR(255)"
            cols_def.append(f"    {c} {tipo}")
            
        if t.get("pks"):
            pk_str = ", ".join(t["pks"])
            cols_def.append(f"    PRIMARY KEY ({pk_str})")
            
        if t.get("fks"):
            for fk in t["fks"]:
                cols_def.append(f"    FOREIGN KEY ({fk['columna']}) REFERENCES {fk['tabla_destino']}({fk['columna']})")
            
        sql_generado += ",\n".join(cols_def)
        sql_generado += "\n);\n\n"
        
    return nuevo_esquema, sql_generado
