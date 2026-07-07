import re

def safe_name(name):
    """Limpia caracteres no válidos para Mermaid ER."""
    if not name: return "Desconocido"
    # Reemplazar espacios y guiones con guion bajo, y quitar cualquier otro especial
    limpio = re.sub(r'[^a-zA-Z0-9_]', '_', str(name))
    # Evitar nombres que empiecen con números si es posible, aunque mermaid lo soporta a veces
    return limpio

def generar_mermaid_er(esquema):
    """
    Genera un string con la sintaxis de Mermaid para un diagrama ER.
    Detecta automáticamente claves foráneas usando heurísticas de nombres
    (_id o id_).
    """
    tablas = esquema.get("tablas", [])
    nombres_tablas = [t['nombre'] for t in tablas]
    
    # Pre-calcular variantes singulares/plurales de nombres de tablas para búsqueda rápida
    tablas_map = {}
    for nombre in nombres_tablas:
        nombre_lower = nombre.lower()
        tablas_map[nombre_lower] = nombre
        # Si termina en s, la versión singular también mapea a esta tabla
        if nombre_lower.endswith('s'):
            tablas_map[nombre_lower[:-1]] = nombre
        # Si termina en es, la versión singular mapea a esta tabla
        if nombre_lower.endswith('es'):
            tablas_map[nombre_lower[:-2]] = nombre
            
    mermaid_code = ["erDiagram"]
    
    # 1. Generar Relaciones (Edges) y registrar FKs identificadas
    relaciones_agregadas = set()
    fks_identificadas = {} # map: (tabla, columna) -> tabla_destino
    
    for t in tablas:
        tabla_origen_raw = t['nombre']
        tabla_origen = safe_name(tabla_origen_raw)
        
        for col_raw in t['columnas']:
            col = safe_name(col_raw)
            col_lower = col_raw.lower()
            
            # Primero buscamos FK explícita
            ref_table_candidata = None
            explicit_fks = t.get("fks", [])
            for fk in explicit_fks:
                if fk.get("columna") == col_raw:
                    ref_table_candidata = fk.get("tabla_destino")
                    break
            
            # Si no hay FK explícita, usamos heurística
            if not ref_table_candidata:
                if col_lower.endswith('_id'):
                    ref_table_candidata = col_lower[:-3]
                elif col_lower.startswith('id_'):
                    ref_table_candidata = col_lower[3:]
                
            if ref_table_candidata:
                # Normalizar usando el mapa para manejar plurales/singulares
                if ref_table_candidata in tablas_map:
                    tabla_destino_raw = tablas_map[ref_table_candidata]
                else:
                    tabla_destino_raw = ref_table_candidata
                
                tabla_destino = safe_name(tabla_destino_raw)
                
                # Evitar auto-referencia si no estamos seguros (o permitirla si el usuario quiere)
                if tabla_destino != tabla_origen:
                    fks_identificadas[(tabla_origen_raw, col_raw)] = tabla_destino_raw
                    relacion = f'    {tabla_destino} ||--o{{ {tabla_origen} : "{col}"'
                    if relacion not in relaciones_agregadas:
                        mermaid_code.append(relacion)
                        relaciones_agregadas.add(relacion)
                    
    # 2. Generar Nodos (Tablas y Columnas)
    for t in tablas:
        tabla_segura = safe_name(t['nombre'])
        mermaid_code.append(f"    {tabla_segura} {{")
        for col_raw in t['columnas']:
            col_segura = safe_name(col_raw)
            es_pk = col_raw in t.get('pks', [])
            es_fk = (t['nombre'], col_raw) in fks_identificadas
            
            atributos = []
            if es_pk: atributos.append("PK")
            if es_fk: atributos.append("FK")
            
            attr_str = ", ".join(atributos)
            if attr_str:
                mermaid_code.append(f"        string {col_segura} {attr_str}")
            else:
                mermaid_code.append(f"        string {col_segura}")
                
        mermaid_code.append("    }")
        
    return "\n".join(mermaid_code)
