import smtplib
from email.message import EmailMessage

from backend.app.core.config import settings


def enviar_email_recuperacao(destinatario: str, link: str) -> None:
    if not all(
        (
            settings.smtp_host,
            settings.smtp_username,
            settings.smtp_password,
            settings.smtp_from,
        )
    ):
        raise RuntimeError("SMTP não está configurado para recuperação de senha.")

    mensagem = EmailMessage()
    mensagem["Subject"] = "Recuperação de senha"
    mensagem["From"] = settings.smtp_from
    mensagem["To"] = destinatario
    mensagem.set_content(
        f"Use este link para redefinir sua senha. Ele expira em 30 minutos:\n\n{link}"
    )
    try:
        with smtplib.SMTP(
            settings.smtp_host,
            settings.smtp_port,
            timeout=15,
        ) as servidor:
            servidor.starttls()
            servidor.login(settings.smtp_username, settings.smtp_password)
            servidor.send_message(mensagem)
    except (OSError, smtplib.SMTPException) as exc:
        raise RuntimeError(
            "Não foi possível autenticar ou enviar o e-mail pelo servidor SMTP."
        ) from exc
