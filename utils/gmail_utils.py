# utils/gmail_utils.py

import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
from utils.logger import get_logger

logger = get_logger("GmailUtils")

env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
load_dotenv(dotenv_path=env_path)

GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS")
GMAIL_PASSWORD = os.getenv("GMAIL_PASSWORD")

if not GMAIL_ADDRESS or not GMAIL_PASSWORD:
    logger.warning("⚠️ Gmail credentials not fully set in .env")

def send_email(to_address: str, subject: str, body: str) -> bool:
    try:
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = GMAIL_ADDRESS
        msg["To"] = to_address
        msg.set_content(body)

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(GMAIL_ADDRESS, GMAIL_PASSWORD)
            smtp.send_message(msg)

        logger.info(f"📤 Email sent to {to_address}")
        return True

    except Exception as e:
        logger.error(f"❌ Failed to send email to {to_address}: {e}")
        return False
