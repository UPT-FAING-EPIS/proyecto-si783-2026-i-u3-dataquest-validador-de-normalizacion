from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import traceback

# Importar lógica del validador existente
from core.parser import parse_schema
from core.diagnostico import diagnosticar_esquema

app = FastAPI(
    title="API de Normalización DataQuest",
    description="Servicio avanzado para diagnosticar la normalización de esquemas SQL (1FN, 2FN, 3FN).",
    version="1.0.0"
)

# Habilitar CORS para permitir consumo desde otros clientes web
app.add_middleware(
    CORSMiddleware,
    # nosemgrep: python.fastapi.security.wildcard-cors.wildcard-cors
    allow_origins=["*"],  # Permite a cualquier dominio público
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "status": "online",
        "message": "DataQuest API está funcionando correctamente.",
        "docs_url": "/docs"
    }

class RequestNormalizacion(BaseModel):
    sql: str = Field(..., description="Las sentencias CREATE TABLE que definen tu esquema relacional.")

@app.post("/api/normalizacion")
async def normalizar_esquema(request: RequestNormalizacion):
    try:
        sql = request.sql.strip()
        if not sql:
            return {
                "success": False,
                "error": {
                    "message": "El campo 'sql' no puede estar vacío.",
                    "code": 400
                }
            }

        # 1. Parsear el SQL usando la misma lógica que usa Streamlit
        esquema_parseado = parse_schema(sql, formato="sql")
        
        if not esquema_parseado.get("tablas"):
             return {
                "success": False,
                "error": {
                    "message": "No se encontraron tablas válidas. Revisa la sintaxis de tu CREATE TABLE.",
                    "code": 400
                }
            }

        # 2. Diagnosticar el nivel de normalización
        reporte = diagnosticar_esquema(esquema_parseado)
        
        # 3. Estructurar la respuesta como se documentó
        return {
            "success": True,
            "nivel_actual": reporte.get("nivel_actual"),
            "violaciones_1fn": reporte.get("violaciones_1fn", []),
            "violaciones_2fn": reporte.get("violaciones_2fn", []),
            "violaciones_3fn": reporte.get("violaciones_3fn", []),
            "mejoras_opcionales": reporte.get("mejoras_opcionales", []),
            "resumen": reporte.get("resumen")
        }
        
    except Exception as e:
        # Imprimir traceback en el servidor para debug
        traceback.print_exc()
        return {
            "success": False,
            "error": {
                "message": f"Error interno del servidor al procesar el esquema: {str(e)}",
                "code": 500
            }
        }
