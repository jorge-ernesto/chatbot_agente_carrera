############################################################
#                    IMPORTAR LIBRERIAS                   #
############################################################

# Helpers
from helpers import config
from helpers import utils

# Librerias
import smtplib
from email.mime.text import MIMEText
import requests

############################################################
#                   REGISTRO DE ENVIOS                   #
############################################################

# Lista global con el resultado de cada notificacion (la UI la lee para verificar)
NOTIFICACIONES_LOG = []


def _registrar(canal, ok, detalle):
    entrada = {"canal": canal, "ok": ok, "detalle": detalle}
    NOTIFICACIONES_LOG.append(entrada)
    utils.error_log(f"NOTIFICACION [{canal}] ok={ok}", detalle)
    return entrada

############################################################
#                        CANALES                         #
############################################################


def _enviar_gmail(text):
    # Enviar notificacion por Gmail: https://gmail.com/
    if not (config.GMAIL_USER and config.GMAIL_PASSWORD):
        return _registrar("gmail", False, "GMAIL_USER / GMAIL_PASSWORD sin configurar")

    try:
        msg = MIMEText(text, "plain", "utf-8")
        msg["Subject"] = "Notificacion de chatbot (alter ego)"
        msg["From"] = config.GMAIL_USER
        msg["To"] = config.GMAIL_TO or config.GMAIL_USER

        # SMTP_SSL sobre el puerto 465 (SSL). Requiere contrasena de aplicacion de Gmail.
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=20) as server:
            server.login(config.GMAIL_USER, config.GMAIL_PASSWORD)
            server.send_message(msg)

        return _registrar("gmail", True, f"Enviado a {msg['To']}")
    except Exception as e:
        return _registrar("gmail", False, f"{type(e).__name__}: {e}")


def _enviar_pushover(text):
    # Enviar notificacion por Pushover: https://pushover.net/
    if not (config.PUSHOVER_USER and config.PUSHOVER_TOKEN):
        return _registrar("pushover", False, "PUSHOVER_USER / PUSHOVER_TOKEN sin configurar")

    try:
        r = requests.post(
            "https://api.pushover.net/1/messages.json",
            data={
                "user": config.PUSHOVER_USER,
                "token": config.PUSHOVER_TOKEN,
                "message": text,
            },
            timeout=20,
        )
        r.raise_for_status()
        return _registrar("pushover", True, "Enviado")
    except Exception as e:
        return _registrar("pushover", False, f"{type(e).__name__}: {e}")


def _enviar_telegram(text):
    # Enviar notificacion por Telegram: https://telegram.org/
    if not (config.TELEGRAM_TOKEN and config.TELEGRAM_CHAT_ID):
        return _registrar("telegram", False, "TELEGRAM_TOKEN / TELEGRAM_CHAT_ID sin configurar")

    try:
        r = requests.post(
            f"https://api.telegram.org/bot{config.TELEGRAM_TOKEN}/sendMessage",
            data={"chat_id": config.TELEGRAM_CHAT_ID, "text": text},
            timeout=20,
        )
        r.raise_for_status()
        return _registrar("telegram", True, "Enviado")
    except Exception as e:
        return _registrar("telegram", False, f"{type(e).__name__}: {e}")

############################################################
#                    FUNCION PRINCIPAL                   #
############################################################


def push(text):
    """
    Envia la notificacion por Gmail (principal) y Pushover (respaldo).
    Devuelve la lista de resultados de esta llamada.
    """
    resultados = []
    resultados.append(_enviar_gmail(text))       # Principal: lo que queremos verificar
    # resultados.append(_enviar_pushover(text))  # Opcional: descomentar para activar Pushover
    # resultados.append(_enviar_telegram(text))  # Opcional: descomentar para activar Telegram
    return resultados
