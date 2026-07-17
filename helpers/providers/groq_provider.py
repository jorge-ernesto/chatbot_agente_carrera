"""
Proveedor Groq.

Que hace:
    Usa el cliente Groq (API compatible con OpenAI) con function calling. El bucle es
    identico al de OpenAI: llamar -> ejecutar tools si se piden -> reenviar -> respuesta.
    Modelos con soporte de tools: p.ej. llama-3.3-70b-versatile.
"""

############################################################
#                    IMPORTAR LIBRERIAS                   #
############################################################

# Helpers
from helpers import config
from helpers import tools as tools_mod
from helpers.providers.base import BaseProvider

# Librerias
from groq import Groq

############################################################
#                       PROVEEDOR                        #
############################################################


class GroqProvider(BaseProvider):

    nombre = "Groq"

    def __init__(self):
        self.model = config.GROQ_MODEL
        self.client = Groq(api_key=config.GROQ_API_KEY)

    def chat(self, messages):
        messages = list(messages)  # Crear copia y convertir a lista o array, para no mutar el historial de session_state
        done = False
        while not done:
            response = self.client.chat.completions.create(model=self.model, messages=messages, tools=tools_mod.tools, temperature=config.TEMPERATURE)
            if response.choices[0].finish_reason == "tool_calls":
                message = response.choices[0].message
                results = tools_mod.handle_tool_call(message.tool_calls)
                messages.append(message)
                messages.extend(results)  # extend, agrega cada elemento del array -- mientras que append, agregaria el array completo como un solo elemento
            else:
                done = True

        return response.choices[0].message.content
