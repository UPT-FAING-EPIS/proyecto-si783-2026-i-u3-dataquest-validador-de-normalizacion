import sys
import json
import argparse
import os

# Asegurar que el directorio raíz está en el path para las importaciones
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.parser import parse_schema
from core.diagnostico import diagnosticar_esquema
from core.corrector import generar_sugerencias
from core.generador_sql import aplicar_mejoras

def main():
    parser = argparse.ArgumentParser(description="Validador de Normalización de Bases de Datos por CLI")
    parser.add_argument('file', nargs='?', help="Ruta al archivo a analizar (SQL, TXT, etc.). Si no se provee, lee de stdin.")
    parser.add_argument('--target-nf', choices=['1FN', '2FN', '3FN'], help="Forma Normal objetivo para refactorizar automáticamente el esquema.")
    args = parser.parse_args()

    input_text = ""
    if args.file:
        if not os.path.exists(args.file):
            print(json.dumps({"error": f"El archivo {args.file} no existe."}))
            sys.exit(1)
        with open(args.file, 'r', encoding='utf-8') as f:
            input_text = f.read()
    else:
        # Leer de stdin
        input_text = sys.stdin.read()

    if not input_text.strip():
        print(json.dumps({"error": "No se proporcionó texto para analizar."}))
        sys.exit(1)

    try:
        # Parseamos asumiendo sintaxis SQL sin importar la extensión
        esquema_parseado = parse_schema(input_text, 'sql')
        reporte = diagnosticar_esquema(esquema_parseado)
        
        # Añadir las tablas parseadas al reporte para tener contexto adicional
        reporte["tablas_detectadas"] = [t["nombre"] for t in esquema_parseado.get("tablas", [])]
        
        # Si el usuario solicitó corrección automática
        if args.target_nf:
            todas_las_sugerencias = generar_sugerencias(reporte)
            sugerencias_aplicables = []
            
            niveles_permitidos = []
            if args.target_nf == '1FN':
                niveles_permitidos = ['1FN']
            elif args.target_nf == '2FN':
                niveles_permitidos = ['1FN', '2FN']
            elif args.target_nf == '3FN':
                niveles_permitidos = ['1FN', '2FN', '3FN']
                
            for sug in todas_las_sugerencias:
                if sug["nivel"] in niveles_permitidos or sug["nivel"] == "Opcional":
                    # Aplicamos las opcionales también si así lo desea el usuario (podría hacerse configurable en el futuro)
                    sugerencias_aplicables.append(sug)
                    
            if sugerencias_aplicables:
                nuevo_esquema, sql_corregido = aplicar_mejoras(esquema_parseado, sugerencias_aplicables)
                reporte["sql_corregido"] = sql_corregido.strip()
                reporte["correcciones_aplicadas"] = [s["accion"] + " en " + s.get("detalle", "") for s in sugerencias_aplicables]
            else:
                reporte["sql_corregido"] = input_text # No hubo cambios
                reporte["correcciones_aplicadas"] = []
                
        print(json.dumps(reporte, indent=2, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)

if __name__ == "__main__":
    main()
