"""
Proveedor LangChain + OpenAI.

Que hace:
    Usa ChatOpenAI con .bind_tools() para el function calling. Convierte los mensajes
    (dicts role/content) a mensajes de LangChain, invoca el modelo y, mientras el
    AIMessage traiga tool_calls, ejecuta las herramientas y adjunta los ToolMessage,
    repitiendo hasta obtener la respuesta final.
"""

############################################################
#                    IMPORTAR LIBRERIAS                   #
############################################################

# Helpers
from helpers import config
from helpers import tools as tools_mod
from helpers.providers.base import BaseProvider

# LangChain
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage

############################################################
#                       PROVEEDOR                        #
############################################################


class LangChainProvider(BaseProvider):

    nombre = "LangChain + OpenAI"

    def __init__(self):
        self.model = config.OPENAI_MODEL
        llm = ChatOpenAI(model=self.model, temperature=config.TEMPERATURE, api_key=config.OPENAI_API_KEY)
        self.chat_model = llm.bind_tools(tools_mod.tools)  # bind_tools, acepta las definiciones en formato OpenAI (mismas que usan los otros providers)

    def mensajes_langchain(self, messages):
        """Convierte los dicts {role, content} a mensajes de LangChain."""
        convertidos = []
        for m in messages:
            role = m["role"]
            content = m["content"]
            if role == "system":
                convertidos.append(SystemMessage(content=content))
            elif role == "assistant":
                convertidos.append(AIMessage(content=content))
            else:  # user
                convertidos.append(HumanMessage(content=content))
        return convertidos

    def chat(self, messages):
        mensajes_lc = self.mensajes_langchain(messages)
        done = False
        while not done:
            mensaje_ai = self.chat_model.invoke(mensajes_lc)
            mensajes_lc.append(mensaje_ai)
            if mensaje_ai.tool_calls:
                for tool_call in mensaje_ai.tool_calls:
                    resultado = tools_mod.ejecutar(tool_call["name"], tool_call["args"])
                    mensajes_lc.append(
                        ToolMessage(
                            content=str(resultado),
                            tool_call_id=tool_call["id"]
                        )
                    )
            else:
                done = True

        return mensaje_ai.content
