import sqlparse
from sqlparse.sql import IdentifierList, Identifier
from sqlparse.tokens import Keyword, DDL
import re

def parse_fds(fds_input):
    """
    Parsea el texto de dependencias funcionales.
    Ejemplo de entrada:
    "A, B -> C"
    Retorna: [ {"determinantes": ["A", "B"], "dependientes": ["C"]} ]
    """
    fds = []
    if not fds_input or not fds_input.strip():
        return fds
        
    lineas = fds_input.split('\n')
    for linea in lineas:
        if '->' in linea:
            izq, der = linea.split('->')
            determinantes = [x.strip() for x in izq.split(',') if x.strip()]
            dependientes = [x.strip() for x in der.split(',') if x.strip()]
            if determinantes and dependientes:
                fds.append({
                    "determinantes": determinantes,
                    "dependientes": dependientes
                })
    return fds

def parse_sql(sql_text):
    """
    Parsea sentencias CREATE TABLE y extrae nombre de tabla, columnas y PKs básicas.
    Es un parser rudimentario basado en expresiones regulares para mayor robustez
    frente a diferentes dialectos SQL.
    """
    tablas = []
    
    # Normalizar espacios
    sql_clean = re.sub(r'\s+', ' ', sql_text)
    
    # En lugar de finditer con regex complejo, partimos por CREATE TABLE
    parts = re.split(r'(?i)CREATE\s+TABLE\s+', sql_clean)
    
    for part in parts:
        part = part.strip()
        if not part: continue
        
        # Opcional IF NOT EXISTS
        part = re.sub(r'(?i)^IF\s+NOT\s+EXISTS\s+', '', part).strip()
        
        # Ignorar cualquier cosa después del primer punto y coma (ej. INSERT INTO posteriores)
        part = part.split(';')[0]
        
        match = re.search(r'^([^\s\(]+)\s*\((.*)\)', part)
        if match:
            tabla_nombre = match.group(1).replace('"', '').replace('`', '').split('.')[-1]
            cuerpo = match.group(2)
            
            columnas = []
            pks = []
            fks = []
            
            # Dividir por comas, pero no las que están dentro de paréntesis (ej. DECIMAL(10,2))
            partes = re.split(r',\s*(?![^()]*\))', cuerpo)
            
            for p in partes:
                p = p.strip()
                if not p: continue
                
                # Chequear si es PRIMARY KEY a nivel de tabla: PRIMARY KEY (col1, col2)
                pk_match = re.search(r"(?i)PRIMARY\s+KEY\s*\((.*?)\)", p)
                if pk_match:
                    cols_pk = [c.strip().replace('"', '').replace('`', '') for c in pk_match.group(1).split(',')]
                    pks.extend(cols_pk)
                    continue
                
                # Chequear si es FOREIGN KEY a nivel de tabla: CONSTRAINT fk FOREIGN KEY (col) REFERENCES table (col)
                fk_match = re.search(r"(?i)FOREIGN\s+KEY\s*\((.*?)\)\s*REFERENCES\s*([^\s\(]+)", p)
                if fk_match:
                    cols_fk = [c.strip().replace('"', '').replace('`', '') for c in fk_match.group(1).split(',')]
                    ref_table = fk_match.group(2).replace('"', '').replace('`', '').split('.')[-1]
                    for col in cols_fk:
                        fks.append({"columna": col, "tabla_destino": ref_table})
                    continue
                
                p_upper = p.upper()
                # Ignorar otros constraints (UNIQUE, KEY, INDEX)
                if p_upper.startswith("UNIQUE") or p_upper.startswith("CONSTRAINT") or p_upper.startswith("KEY") or p_upper.startswith("INDEX"):
                    continue
                    
                # Si es columna: nombre_columna TIPO [CONSTRAINT]
                tokens = p.split()
                if not tokens: continue
                
                col_name = tokens[0].replace('"', '').replace('`', '')
                columnas.append(col_name)
                
                # Ver si tiene PRIMARY KEY a nivel de columna
                if "PRIMARY KEY" in p.upper():
                    pks.append(col_name)
                    
                # Ver si tiene REFERENCES a nivel de columna (inline FK)
                inline_fk_match = re.search(r"(?i)REFERENCES\s+([^\s\(]+)", p)
                if inline_fk_match:
                    ref_table = inline_fk_match.group(1).replace('"', '').replace('`', '').split('.')[-1]
                    fks.append({"columna": col_name, "tabla_destino": ref_table})
                    
            tablas.append({
                "nombre": tabla_nombre,
                "columnas": columnas,
                "pks": list(set(pks)), # eliminar duplicados
                "fks": fks,
                "sql_original": f"CREATE TABLE {tabla_nombre} ({cuerpo});"
            })
            
    return tablas

def parse_csv(file_stream):
    """
    Parsea un archivo CSV. Simulado por ahora.
    """
    return []

def parse_schema(input_data, formato, fds_input=""):
    """
    Función principal de entrada al parser.
    Retorna un diccionario estructurado del esquema y las FDs.
    """
    tablas = []
    if formato in ['sql', 'texto_pegado', 'txt']:
        tablas = parse_sql(input_data)
    elif formato == 'csv':
        tablas = parse_csv(input_data)
        
    fds = parse_fds(fds_input)
    
    return {
        "tablas": tablas,
        "dependencias_funcionales": fds
    }
