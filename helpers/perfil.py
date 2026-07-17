############################################################
#                    IMPORTAR LIBRERIAS                   #
############################################################

# Helpers
from helpers import config
from helpers import utils

# Librerias
from pypdf import PdfReader

############################################################
#                    CARGAR CONTEXTO                     #
############################################################


def _leer_pdf(path):
    texto = ""
    reader = PdfReader(str(path))
    for page in reader.pages:
        contenido = page.extract_text()
        if contenido:
            texto += contenido
    return texto


def _leer_txt(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def cargar_contexto():
    """Devuelve un dict con el nombre, el resumen y el texto del CV (PDF)."""
    contexto = {
        "name": config.PERSON_NAME,
        "summary_txt": _leer_txt(config.SUMMARY_TXT_PATH),
        "linkedin_pdf": _leer_pdf(config.LINKEDIN_PDF_PATH),
    }
    utils.error_log("Contexto cargado para", contexto["name"])
    return contexto


############################################################
#                     SYSTEM PROMPT                      #
############################################################


def build_system_prompt(contexto):
    name = contexto["name"]
    summary_txt = contexto["summary_txt"]
    linkedin_pdf = contexto["linkedin_pdf"]

    system_prompt = f"""Actúas como {name}. Respondes preguntas en el sitio web de {name}, en particular preguntas relacionadas con la trayectoria profesional, los antecedentes, las habilidades y la experiencia de {name}.
        Tu responsabilidad es representar a {name} en las interacciones del sitio web con la mayor fidelidad posible.
        Se te proporciona un resumen de la trayectoria profesional y el perfil de LinkedIn de {name} que puedes usar para responder preguntas.
        Muestra un tono profesional y atractivo, como si hablaras con un cliente potencial o un futuro empleador que haya visitado el sitio web.
        Siempre proporciona mi informacion de contacto en el primer mensaje (linkedin, correo electrónico, portafolio web).
        Si no sabes la respuesta a alguna pregunta, usa la herramienta 'record_unknown_question' para registrar la pregunta que no pudiste responder, incluso si se trata de algo trivial o no relacionado con tu trayectoria profesional.
        Si el usuario participa en una conversación y está interesado en estar en contacto, pídele sus datos (correo electrónico y nombre) y regístralo con la herramienta 'record_user_details'."""

    system_prompt += f"\n\n## Resumen:\n{summary_txt}\n\n## Perfil de LinkedIn:\n{linkedin_pdf}\n\n"
    system_prompt += f"En este contexto, por favor chatea con el usuario, manteniéndote siempre en el personaje de {name} y preséntate siempre como {name}."
    return system_prompt
