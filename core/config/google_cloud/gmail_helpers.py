"""Tutorial rápido para enviar correos con Gmail y Python.

Este módulo usa la configuración compartida de Google OAuth desde
core.config.google_cloud.google_cloud para construir un servicio de Gmail.

Requisitos:
- Tener configuradas CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN, ACCESS_TOKEN y TOKEN_EXPIRY en .env
- Tener habilitada la API de Gmail en Google Cloud Console
- Tener el scope:
    https://www.googleapis.com/auth/gmail.send
"""

import base64
from email.message import EmailMessage

from googleapiclient.discovery import build

from core.config.google_cloud.google_cloud import get_credentials, log_and_raise_google_error


def get_gmail_service():
    """Support function."""
    creds = get_credentials()
    return build("gmail", "v1", credentials=creds)


def create_message(to: str, subject: str, message_text: str):
    """gmail requires an encoded message, this function creates it."""
    message = EmailMessage()
    message["To"] = to
    message["Subject"] = subject
    message.set_content(message_text)

    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
    return {"raw": encoded_message}


def send_email(to: str, subject: str, message_text: str):
    """sends a simple mail using Gmail API."""
    try:
        service = get_gmail_service()
        message = create_message(to, subject, message_text)
        result = (
            service.users()
            .messages()
            .send(userId="me", body=message)
            .execute()
        )
        return result
    except Exception as exc:
        log_and_raise_google_error("send_email", exc)


if __name__ == "__main__":
    result = send_email(
        "juanmunozr@unicauca.edu.co",
        "Prueba desde Python",
        "Hola, este es un correo de prueba enviado con Gmail API.",
    )
    print(result)
