"""
App Importante (UI): Chatbot IA - Alter Ego Profesional con Streamlit (OpenAI / LangChain / Groq) y Tools

Que hace:
    Version en Streamlit del chatbot que actua como si fuera Jorge Ernesto La Chira Gutierrez y
    responde preguntas sobre su trayectoria, experiencia, habilidades y perfil profesional. Usa como
    contexto un resumen en texto y un PDF de LinkedIn (carpeta me/) para construir el system prompt.
    Mantiene el historial en session_state, integra function calling para registrar correos de
    interesados (record_user_details) y preguntas sin respuesta (record_unknown_question), y envia
    una notificacion por Gmail (principal, a verificar en Streamlit Cloud) con Pushover de respaldo.

    El backend LLM se elige con una unica variable (LLM_PROVIDER en .env / st.secrets):
    "openai" | "langchain" | "groq". La interfaz es la misma para los tres.

Tecnologias:
    Streamlit (set_page_config, sidebar, chat_message, chat_input, session_state, expander, rerun, cache_resource),
    OpenAI / LangChain (ChatOpenAI + bind_tools) / Groq (function calling), pypdf (PDF de LinkedIn),
    smtplib (Gmail) + requests (Pushover), python-dotenv (variables de entorno), helpers (config, perfil, tools, providers, notifications).

Ejecutar:
    cd 2-python-agentes-ia/3-chatbot-streamlit-openai-tools-streamlitcloud-agentecarrera-prod
    streamlit run app.py
"""

############################################################
#                    IMPORTAR LIBRERIAS                   #
############################################################

# Streamlit
import streamlit as st

# Helpers
from helpers import config
from helpers import perfil
from helpers import notifications
from helpers import providers

############################################################
#                      CONFIGURAR APP                     #
############################################################

# ****************** Configurar pagina ******************

# Configurar pagina
st.set_page_config(
    page_title="Alter Ego Profesional",
    page_icon="🤖",
    layout="centered"
)

# Título h1
st.title(f"😎✌️Chatbot IA - Alter Ego de {config.PERSON_NAME}")

# Descripción p
st.write("Pregunta sobre mi trayectoria, experiencia, habilidades y perfil profesional.")

# ****************** Cargar contexto y proveedor (cacheados) ******************


# Obtener contexto -- se lee una sola vez y se reutiliza
@st.cache_resource(show_spinner="Cargando contexto...")
def cargar_contexto():
    return perfil.cargar_contexto()


# Obtener proveedor LLM -- se instancia una sola vez por tipo (openai/langchain/groq) y se reutiliza
@st.cache_resource(show_spinner="Inicializando modelo...")
def cargar_proveedor(nombre_proveedor):
    return providers.get_provider(nombre_proveedor)


try:
    contexto = cargar_contexto()
    provider = cargar_proveedor(config.LLM_PROVIDER)
    SYSTEM_PROMPT = perfil.build_system_prompt(contexto)
except Exception as e:
    st.error(f"Error al inicializar la app: {e}")
    st.stop()


# ****************** Sidebar ******************

# Sidebar
with st.sidebar:
    # Header h1
    st.header("⚙️ Configuración")

    # Información de la persona
    st.markdown(f"**Persona:** {contexto['name']}")

    # Información del proveedor LLM y de los modelos LLM
    st.info(f"Proveedor LLM: **{provider.nombre}**\n\nModelo: **{provider.model}**")
    # st.caption("Cambia el backend con la variable LLM_PROVIDER en el .env (o en Secrets de Streamlit Cloud).")

    # Separador hr
    st.divider()

    # Registro de notificaciones (para verificar Gmail / Pushover)
    st.subheader("📨 Notificaciones enviadas")
    if notifications.NOTIFICACIONES_LOG:
        for n in notifications.NOTIFICACIONES_LOG:
            icono = "✅" if n["ok"] else "❌"
            st.write(f"{icono} **{n['canal']}** — {n['detalle']}")
    else:
        st.caption("Aun no se ha enviado ninguna notificacion.")

    # Separador hr
    st.divider()

    # Nueva conversación
    if st.button("🗑️ Nueva conversacion", use_container_width=True):
        st.session_state.messages = []  # Limpiar historial de mensajes
        st.rerun()  # Recargar pagina

# ****************** Inicializar el historial de mensajes en "session_state.messages" ******************

# Inicializar el historial de mensajes en "session_state.messages"
if "messages" not in st.session_state:
    st.session_state.messages = []

# ****************** Renderizar historial de mensajes ******************

# Renderizar historial de mensajes
for msg in st.session_state.messages:  # Lista de dicts: {"role": "user"|"assistant", "content": ...}
    # Mostrar el mensaje en el chat
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ****************** Input de usuario ******************

# chat_input: Es el widget de entrada de chat, esta pensado para ir fijo en la parte inferior de la pantalla como en WhatsApp o Telegram
pregunta = st.chat_input("Escribe tu mensaje...")

if pregunta:
    # Agregar el mensaje del usuario (user) al historial de mensajes
    st.session_state.messages.append({"role": "user", "content": pregunta})

    # Mostrar el mensaje en el chat -- usuario (user)
    with st.chat_message("user"):
        st.markdown(pregunta)

    # Mostrar el mensaje en el chat -- asistente ia (assistant)
    with st.chat_message("assistant"):

        # Spinner
        # Obtener respuesta
        with st.spinner("Pensando..."):

            # Obtener respuesta
            try:
                messages = [{"role": "system", "content": SYSTEM_PROMPT}]
                messages.extend(st.session_state.messages)
                respuesta = provider.chat(messages)
            except Exception as e:
                respuesta = f"Error al generar respuesta:\n\n`{str(e)}`"
                # respuesta = f"Error al generar respuesta: {str(e)}"

            # Mostrar el mensaje en el chat -- asistente ia (asistant)
            st.markdown(respuesta)

            # Agregar el mensaje del asistente (assistant) al historial de mensajes
            st.session_state.messages.append({"role": "assistant", "content": respuesta})

        # Recargar pagina -- para mostrar los mensajes nuevos y para refrescar el sidebar (log de notificaciones) tras posibles tool calls
        st.rerun()
