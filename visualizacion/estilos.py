import streamlit as st

def aplicar_estilos():
    """
    Inyecta CSS personalizado para dar un aspecto premium, moderno y altamente responsivo.
    Incluye Glassmorphism, tipografía moderna, animaciones sutiles y diseño adaptable para la marca DataQuest.
    """
    css = """
    <style>
    /* Importar Google Fonts Premium */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@300;400;600;800&family=Space+Grotesk:wght@700&display=swap');

    /* Tipografía Global y Fondo Oscuro Premium Animado */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(-45deg, #09090b, #111827, #0f172a, #020617);
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite;
        color: #f4f4f5;
    }
    
    @keyframes gradientBG {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* Scrollbar Personalizado y Elegante */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #09090b; 
    }
    ::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.2); 
        border-radius: 10px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(255, 255, 255, 0.4); 
    }

    /* Encabezados Profesionales */
    h1 {
        font-family: 'Space Grotesk', sans-serif !important;
        font-size: 2.8rem !important;
        background: linear-gradient(to right, #38bdf8, #818cf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800 !important;
        letter-spacing: -0.04em;
        margin-bottom: 0.8rem !important;
        text-shadow: 0px 4px 20px rgba(129, 140, 248, 0.2);
    }

    h2, h3, h4, h5, h6 {
        font-family: 'Outfit', sans-serif !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        letter-spacing: -0.02em;
    }
    
    p, li {
        color: #a1a1aa;
        font-size: 1.05rem;
        line-height: 1.6;
    }

    /* Efecto Glassmorphism Ultra-Premium para Formatos, Tarjetas y Expansores */
    [data-testid="stForm"], .stExpander, [data-testid="stVerticalBlock"] > div > div > [data-testid="stVerticalBlock"] {
        background: rgba(17, 24, 39, 0.4) !important;
        backdrop-filter: blur(20px) saturate(180%) !important;
        -webkit-backdrop-filter: blur(20px) saturate(180%) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 16px !important;
        padding: 24px !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.05) !important;
        transition: transform 0.4s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.4s cubic-bezier(0.16, 1, 0.3, 1), border-color 0.4s ease;
    }

    /* Micro-animaciones en hover para tarjetas */
    [data-testid="stForm"]:hover, .stExpander:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 40px 0 rgba(0, 0, 0, 0.6), 0 0 20px rgba(56, 189, 248, 0.1), inset 0 1px 0 rgba(255, 255, 255, 0.1) !important;
        border: 1px solid rgba(56, 189, 248, 0.3) !important;
    }

    /* Botones Profesionales con Efecto Glow */
    .stButton > button {
        background: linear-gradient(135deg, #2563eb 0%, #6366f1 100%) !important;
        color: white !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 12px !important;
        padding: 12px 28px !important;
        font-weight: 600 !important;
        letter-spacing: 0.5px !important;
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
        width: 100%;
        box-shadow: 0 4px 14px 0 rgba(37, 99, 235, 0.4) !important;
        position: relative;
        overflow: hidden;
    }
    
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 0; left: -100%; width: 100%; height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        transition: all 0.5s ease;
    }

    .stButton > button:hover::before {
        left: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) scale(1.02) !important;
        box-shadow: 0 8px 25px rgba(99, 102, 241, 0.6) !important;
        filter: brightness(115%);
        border: 1px solid rgba(255,255,255,0.3) !important;
    }
    
    .stButton > button:active {
        transform: translateY(0) scale(0.98) !important;
    }

    /* Entradas de Texto Elegantes y Modernas */
    .stTextInput > div > div > input, .stTextArea > div > div > textarea, .stSelectbox > div > div > div {
        background-color: rgba(15, 23, 42, 0.6) !important;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 10px !important;
        padding: 14px !important;
        transition: all 0.3s ease;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.2);
    }

    .stTextInput > div > div > input:focus, .stTextArea > div > div > textarea:focus {
        border-color: #38bdf8 !important;
        box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.25), inset 0 2px 4px rgba(0,0,0,0.2) !important;
        background-color: rgba(15, 23, 42, 0.9) !important;
    }

    /* Ajustes para Sidebar Ultra-Profesional */
    [data-testid="stSidebar"] {
        background-color: rgba(9, 9, 11, 0.95) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
        box-shadow: 4px 0 15px rgba(0,0,0,0.5);
    }
    
    /* Branding en sidebar */
    [data-testid="stSidebarNav"]::before {
        content: "DataQuest";
        display: block;
        padding: 24px 30px;
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.6rem;
        font-weight: 800;
        background: linear-gradient(to right, #38bdf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 10px;
        text-shadow: 0px 2px 10px rgba(192, 132, 252, 0.3);
    }

    /* Estilización de DataFrames y Tablas */
    [data-testid="stDataFrame"] {
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid rgba(255, 255, 255, 0.08);
    }
    
    /* ---------------------------------------------------
       NUEVO: ESTILOS TIPO "ANZENCORE" PARA DASHBOARD
       --------------------------------------------------- */
       
    /* Caja de Usuario Activo bajo el Logo */
    .user-active-box {
        position: absolute;
        top: 90px;
        left: 20px;
        right: 20px;
        background: rgba(255, 255, 255, 0.03);
        padding: 12px 16px;
        border-radius: 8px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        z-index: 99;
    }

    /* Empujar navegación hacia abajo para dejar espacio a la caja de usuario */
    [data-testid="stSidebarNav"] {
        padding-top: 100px !important;
    }
    
    /* Etiqueta NAVEGACIÓN antes de la lista */
    [data-testid="stSidebarNav"] ul::before {
        content: "NAVEGACIÓN";
        display: block;
        padding: 0 20px 10px 20px;
        font-size: 0.7rem;
        font-weight: 700;
        color: #64748b;
        letter-spacing: 0.05em;
    }
    
    /* Transformar Enlaces del Sidebar en Botones Cyan */
    [data-testid="stSidebarNav"] ul {
        padding-top: 10px;
    }
    
    [data-testid="stSidebarNav"] li {
        margin-bottom: 8px;
        padding: 0 20px;
    }
    
    [data-testid="stSidebarNav"] li a {
        background-color: transparent !important;
        border: 1px solid #06b6d4 !important; /* Cyan border */
        border-radius: 8px !important;
        color: #e2e8f0 !important;
        padding: 10px 15px !important;
        text-align: center;
        display: flex;
        justify-content: center;
        align-items: center;
        transition: all 0.3s ease;
    }
    
    [data-testid="stSidebarNav"] li a:hover {
        background-color: rgba(6, 182, 212, 0.1) !important;
        box-shadow: 0 0 10px rgba(6, 182, 212, 0.2);
    }
    
    /* El elemento activo tiene fondo o brillo extra */
    [data-testid="stSidebarNav"] li a[aria-current="page"] {
        background-color: rgba(6, 182, 212, 0.15) !important;
        border-width: 2px !important;
        box-shadow: 0 0 15px rgba(6, 182, 212, 0.3);
    }
    
    /* Ocultar fondos grises nativos de Streamlit en hover del sidebar */
    [data-testid="stSidebarNav"] li div {
        background-color: transparent !important;
    }

    /* Estilos para las tarjetas de Métricas (KPIs) */
    [data-testid="metric-container"] {
        background: #141c2c !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 12px !important;
        padding: 20px !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    
    [data-testid="stMetricLabel"] {
        color: #94a3b8 !important; /* Texto gris claro */
        font-weight: 500 !important;
        font-size: 0.95rem !important;
    }
    
    [data-testid="stMetricValue"] {
        color: #06b6d4 !important; /* Número Cyan gigante */
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        font-family: 'Space Grotesk', sans-serif !important;
    }

    /* Mejoras de Responsividad Total */
    @media (max-width: 768px) {
        .stApp { padding: 0 !important; }
        [data-testid="stForm"], .stExpander { padding: 16px !important; border-radius: 12px !important; }
        h1 { font-size: 2.2rem !important; }
        h2 { font-size: 1.5rem !important; }
        button { width: 100% !important; }
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

