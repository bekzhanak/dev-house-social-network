import os
import logging
from fastapi import APIRouter, BackgroundTasks
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig

# Enable logging for debugging
logging.basicConfig(level=logging.DEBUG)

conf = ConnectionConfig(
    MAIL_USERNAME="b.orynbay@karbil.kz",
    MAIL_PASSWORD=os.getenv("EMAIL_PASSWORD"),  # Ensure this variable is set correctly
    MAIL_FROM="b.orynbay@karbil.kz",
    MAIL_PORT=465,  # Change to 587 if needed
    MAIL_SERVER="smtp.yandex.kz",
    MAIL_STARTTLS=False,  # Set to True if using 587
    MAIL_SSL_TLS=True,  # Set to False if using 587
    MAIL_FROM_NAME="DevHouse FastAPI"
)

async def send_email(background_tasks: BackgroundTasks, recipient: str, body: str):
    recipients = [recipient] if isinstance(recipient, str) else recipient

    message = MessageSchema(
        subject="Email verification",
        recipients=recipients,
        body=body,
        subtype="plain"
    )

    fm = FastMail(conf)
    try:
        background_tasks.add_task(fm.send_message, message)
        logging.info("✅ Email sent successfully!")
        return {"message": "Email sent successfully!"}
    except Exception as e:
        logging.error(f"❌ Email sending failed: {e}")
        return {"message": f"Failed to send email: {e}"}
