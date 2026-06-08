import smtplib
import ssl
from email.message import EmailMessage

from flask import current_app


def send_email(*, recipients, subject, body, reply_to=None):
    if isinstance(recipients, str):
        recipient_list = [recipients]
    else:
        recipient_list = [item.strip() for item in recipients if item and item.strip()]

    if not recipient_list:
        current_app.logger.warning("Email send skipped because no recipients were provided.")
        return False

    sender = current_app.config.get("MAIL_DEFAULT_SENDER")
    if not sender:
        current_app.logger.warning("Email send skipped because MAIL_DEFAULT_SENDER is not configured.")
        return False

    message = EmailMessage()
    message["From"] = sender
    message["To"] = ", ".join(recipient_list)
    message["Subject"] = subject
    if reply_to:
        message["Reply-To"] = reply_to
    message.set_content(body)

    if current_app.config.get("MAIL_SUPPRESS_SEND"):
        outbox = current_app.extensions.setdefault("mail_outbox", [])
        outbox.append(message)
        return True

    mail_server = current_app.config.get("MAIL_SERVER")
    if not mail_server:
        current_app.logger.warning("Email send skipped because MAIL_SERVER is not configured.")
        return False

    port = current_app.config.get("MAIL_PORT", 465)
    use_ssl = current_app.config.get("MAIL_USE_SSL", True)
    use_tls = current_app.config.get("MAIL_USE_TLS", False)
    username = current_app.config.get("MAIL_USERNAME") or ""
    password = current_app.config.get("MAIL_PASSWORD") or ""
    timeout = current_app.config.get("MAIL_TIMEOUT", 30)
    context = ssl.create_default_context()

    try:
        if use_ssl:
            with smtplib.SMTP_SSL(mail_server, port, timeout=timeout, context=context) as smtp:
                if username and password:
                    smtp.login(username, password)
                smtp.send_message(message)
        else:
            with smtplib.SMTP(mail_server, port, timeout=timeout) as smtp:
                if use_tls:
                    smtp.starttls(context=context)
                if username and password:
                    smtp.login(username, password)
                smtp.send_message(message)
    except Exception:
        current_app.logger.exception("Failed to send email to %s", recipient_list)
        return False

    return True
