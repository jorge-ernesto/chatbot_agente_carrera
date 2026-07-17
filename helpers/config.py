############################################################
#                    IMPORTAR LIBRERIAS                   #
############################################################

# Helpers
from helpers import utils

# Librerias
from dotenv import load_dotenv
from pathlib import Path
import os

############################################################
#              CONFIGURAR VARIABLES DE ENTORNO             #
############################################################

load_dotenv(override=True)  # Busca hacia atras el archivo ".env" desde donde se ejecuto el script


def get_secret(key, default=None):
    """
    Obtiene un secreto de forma segura.

    1) En local: desde variables de entorno (.env cargado por python-dotenv).
    2) En Streamlit Cloud: desde st.secrets (si esta disponible).
    """
    value = os.getenv(key)
    if value:
        return value

    # Respaldo: st.secrets (solo existe cuando se ejecuta dentro de Streamlit)
    try:
        import streamlit as st
        if key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass

    return default


############################################################
#                    RUTAS DEL PROYECTO                   #
############################################################

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent  # Carpeta raiz del proyecto
utils.error_log("BASE_DIR", str(BASE_DIR))

# Ficheros de contexto de la persona representada
ME_DIR = BASE_DIR / "me"
LINKEDIN_PDF_PATH = ME_DIR / "linkedin_jorgelachira.pdf"
SUMMARY_TXT_PATH = ME_DIR / "summary_jorgelachira.txt"

############################################################
#                 SELECCION DEL PROVEEDOR                 #
############################################################

# LLM_PROVIDER decide que backend se usa: "openai" | "langchain" | "groq"
# Basta con cambiar esta variable en el .env (o en st.secrets) para alternar.
LLM_PROVIDER = (get_secret("LLM_PROVIDER", "openai") or "openai").strip().lower()
utils.error_log("LLM_PROVIDER", LLM_PROVIDER)

############################################################
#                 CLAVES Y MODELOS POR API               #
############################################################

# OpenAI (usado por los proveedores "openai" y "langchain")
OPENAI_API_KEY = get_secret("OPENAI_API_KEY")
OPENAI_MODEL = get_secret("OPENAI_MODEL", "gpt-4o-mini")

# Groq (usado por el proveedor "groq") -- modelos: https://console.groq.com/docs/models
GROQ_API_KEY = get_secret("GROQ_API_KEY")
GROQ_MODEL = get_secret("GROQ_MODEL", "llama-3.3-70b-versatile")

# Temperatura comun
TEMPERATURE = float(get_secret("TEMPERATURE", "0.7"))

############################################################
#              PERSONA REPRESENTADA (ALTER EGO)          #
############################################################

PERSON_NAME = get_secret("PERSON_NAME", "Jorge Ernesto La Chira Gutiérrez")

############################################################
#                 NOTIFICACIONES (PUSH)                  #
############################################################

# Gmail (via smtplib) -- requiere una CONTRASENA DE APLICACION de Gmail (con 2FA activo)
GMAIL_USER = get_secret("GMAIL_USER")
GMAIL_PASSWORD = get_secret("GMAIL_PASSWORD")
GMAIL_TO = get_secret("GMAIL_TO", GMAIL_USER)  # Si no se define, se envia a uno mismo

# Pushover (respaldo) -- https://pushover.net/
PUSHOVER_USER = get_secret("PUSHOVER_USER")
PUSHOVER_TOKEN = get_secret("PUSHOVER_TOKEN")

# Telegram (respaldo opcional)
TELEGRAM_TOKEN = get_secret("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = get_secret("TELEGRAM_CHAT_ID")
