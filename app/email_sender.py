"""
Trimite oferta generată pe email, folosind credențiale SMTP din variabile
de mediu (niciodată hardcodate în cod).
"""

import os
import smtplib
from email.message import EmailMessage
from pathlib import Path


def send_offer_email(to_email: str, client_name: str, pdf_path: Path,
                      firm_name: str = "Numele firmei tale") -> None:
    """Trimite PDF-ul de ofertă ca atașament pe email-ul clientului."""
    smtp_host = os.environ.get("SMTP_HOST")
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))
    smtp_user = os.environ.get("SMTP_USER")
    smtp_password = os.environ.get("SMTP_PASSWORD")

    if not all([smtp_host, smtp_user, smtp_password]):
        raise RuntimeError(
            "Configurează SMTP_HOST, SMTP_USER și SMTP_PASSWORD în variabilele "
            "de mediu (vezi .env.example) înainte de a trimite emailuri."
        )

    msg = EmailMessage()
    msg["Subject"] = f"Oferta ta de la {firm_name}"
    msg["From"] = smtp_user
    msg["To"] = to_email
    msg.set_content(
        f"Bună, {client_name},\n\n"
        f"Îți atașăm oferta discutată. Estimarea este orientativă și o "
        f"confirmăm împreună la discuția de discovery.\n\n"
        f"Cu drag,\n{firm_name}"
    )

    with open(pdf_path, "rb") as f:
        msg.add_attachment(
            f.read(), maintype="application", subtype="pdf",
            filename=pdf_path.name
        )

    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.send_message(msg)
