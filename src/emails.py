from pathlib import Path

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema

from src.models import User


email_configuration = ConnectionConfig(
    USE_CREDENTIALS=True,
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_TLS=True,
    MAIL_SSL=False,
    TEMPLATE_FOLDER=Path("email_templates")
)
fast_mail = FastMail(email_configuration)


async def send_multi_factor_authentication_jwt(
    user: User,
    jwt: str,
    subject: str = "Your multi-factor authentication token",
    template_name="mfa_message.txt"
) -> None:
    message = MessageSchema(
        subject=subject,
        recipients=[user.email_address],
        template_body={"user": user, "jwt": jwt}
    )
    await fast_mail.send_message(message, template_name=template_name)
