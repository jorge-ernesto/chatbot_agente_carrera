"""
Selector de proveedor LLM.

Que hace:
    Segun la variable config.LLM_PROVIDER ("openai" | "langchain" | "groq"),
    instancia y devuelve el proveedor correspondiente. Cambiar de backend es cambiar
    esa variable en el .env (o en st.secrets), sin tocar la UI ni el resto del codigo.
"""

# Helpers
from helpers import config

# Mapa nombre -> ruta de importacion (import perezoso para no cargar SDKs que no se usan)
PROVEEDORES_DISPONIBLES = ["openai", "langchain", "groq"]


def get_provider(nombre=None):
    nombre = (nombre or config.LLM_PROVIDER or "openai").strip().lower()

    if nombre == "openai":
        from helpers.providers.openai_provider import OpenAIProvider
        return OpenAIProvider()

    if nombre == "langchain":
        from helpers.providers.langchain_provider import LangChainProvider
        return LangChainProvider()

    if nombre == "groq":
        from helpers.providers.groq_provider import GroqProvider
        return GroqProvider()

    raise ValueError(
        f"LLM_PROVIDER no valido: '{nombre}'. Usa uno de: {PROVEEDORES_DISPONIBLES}"
    )
