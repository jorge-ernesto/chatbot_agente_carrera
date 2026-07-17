"""
Interfaz comun de los proveedores LLM.

Que hace:
    Define el contrato que cumplen los tres backends (OpenAI, LangChain, Groq).
    Cada proveedor recibe una lista de mensajes [{"role","content"}] (system + historial
    + usuario) y devuelve el texto final del asistente, resolviendo internamente el bucle
    de function calling (herramientas) hasta que el modelo deja de pedir tools.
"""


class BaseProvider:

    # Nombre legible del backend (se muestra en el sidebar)
    nombre = "base"

    # Modelo en uso (se muestra en el sidebar)
    model = None

    def chat(self, messages):
        """
        messages: list[dict] con {"role": "system|user|assistant", "content": str}
        return: str -> respuesta final del asistente
        """
        raise NotImplementedError
