############################################################
#                    IMPORTAR LIBRERIAS                   #
############################################################

# Helpers
from helpers import notifications
from helpers import utils

# Librerias
import json

############################################################
#                    FUNCIONES (TOOLS)                   #
############################################################


def record_user_details(email, name="Nombre no indicado", notes="no proporcionadas"):
    notifications.push(f"Registrando detalle del usuario: {name} con email {email} y notas {notes}")
    return {"recorded": "ok"}


def record_unknown_question(question):
    notifications.push(f"Registrando pregunta sin respuesta: {question}")
    return {"recorded": "ok"}


# Mapa nombre -> funcion, para ejecutar la herramienta por su nombre
FUNCTIONS = {
    "record_user_details": record_user_details,
    "record_unknown_question": record_unknown_question,
}

############################################################
#            DEFINICIONES JSON (FORMATO OPENAI)          #
############################################################

record_user_details_json = {
    "name": "record_user_details",
    "description": "Utiliza esta herramienta para registrar que un usuario está interesado en estar en contacto y proporcionó una dirección de correo electrónico.",
    "parameters": {
        "type": "object",
        "properties": {
            "email": {
                "type": "string",
                "description": "La dirección de email del usuario",
            },
            "name": {
                "type": "string",
                "description": "El nombre del usuario, si se indica",
            },
            "notes": {
                "type": "string",
                "description": "¿Alguna información adicional sobre la conversación que valga la pena registrar para dar contexto?",
            },
        },
        "required": ["email", "name"],
        "additionalProperties": False
    }
}

record_unknown_question_json = {
    "name": "record_unknown_question",
    "description": "Utiliza siempre esta herramienta para registrar cualquier pregunta que no haya podido responder porque no se sabía la respuesta.",
    "parameters": {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "La pregunta no sabe responderse",
            },
        },
        "required": ["question"],
        "additionalProperties": False
    }
}

# Lista de herramientas en formato OpenAI (compatible con OpenAI, Groq y LangChain.bind_tools)
tools = [
    {"type": "function", "function": record_user_details_json},
    {"type": "function", "function": record_unknown_question_json}
]

############################################################
#                  EJECUTAR HERRAMIENTAS                 #
############################################################


def ejecutar(tool_name, arguments):
    """Ejecuta una herramienta por su nombre con sus argumentos (dict)."""
    function = FUNCTIONS.get(tool_name)                 # FUNCTIONS, permite acceder a las funciones de las tools
    result = function(**arguments) if function else {}  # Usar funcion de la tool
    return result


def handle_tool_call(tool_calls):
    """
    Procesa las tool_calls que devuelve el SDK de OpenAI/Groq.
    Devuelve la lista de mensajes con rol "tool" para reenviar al modelo.
    """
    results = []

    for tool_call in tool_calls:
        tool_name = tool_call.function.name                   # Obtener nombre de la funcion -- desde la tool
        arguments = json.loads(tool_call.function.arguments)  # Obtener argumentos de la funcion -- desde la tool
        print(f"tool_name: {tool_name}", flush=True)          # flush=True, fuerza a que el print se vea al instante
        print(f"arguments: {arguments}", flush=True)          # flush=True, fuerza a que el print se vea al instante

        result = ejecutar(tool_name, arguments)  # Usar funcion de la tool

        results.append(
            {
                "role": "tool",
                "content": json.dumps(result),
                "tool_call_id": tool_call.id,
            }
        )
    return results
