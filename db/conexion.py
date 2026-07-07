import os
import psycopg2
import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv(override=True)

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
DATABASE_URL = os.environ.get("DATABASE_URL")

def get_supabase_client() -> Client:
    """Retorna un cliente de Supabase (inyectando la sesión activa si existe)."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("SUPABASE_URL o SUPABASE_KEY no están configuradas.")
    
    client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # Si estamos en Streamlit y hay una sesión, inyectamos los tokens para que no sea anónimo
    try:
        if "access_token" in st.session_state and "refresh_token" in st.session_state:
            client.auth.set_session(st.session_state["access_token"], st.session_state["refresh_token"])
    except Exception:
        pass
        
    return client

def get_db_connection():
    """Retorna una conexión directa a PostgreSQL usando psycopg2."""
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL no está configurada.")
    return psycopg2.connect(DATABASE_URL)
