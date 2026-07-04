"""
Trimite oferta generată pe email, folosind API-ul web al SendGrid
(HTTPS, port 443) — NU protocolul SMTP clasic.

De ce: platformele de găzduire gratuite (Render, Railway free tier etc.)
blochează frecvent porturile SMTP (25, 465, 587) ca măsură anti-spam.
API-ul web merge peste HTTPS, exact ca orice alt apel către un site —
nu poate fi blocat fără să blocheze internetul serviciului în sine.
"""

import base64
import os
from pathlib import Path

import requests

SENDGRID_API_URL = "https://api.sendgrid.com/v3/mail/send"


def send_offer_email(to_email: str, client_name: str, pdf_path: Path,
                      firm_name: str = "Numele firmei tale") -> None:
    """Trimite PDF-ul de ofertă ca atașament pe email-ul clientului, prin SendGrid API."""
    api_key = os.environ.get("SMTP_PASSWORD")  # cheia SendGrid, stocată în aceeași variabilă ca înainte
    sender_email = os.environ.get("SENDER_EMAIL")

    if not api_key:
        raise RuntimeError(
            "Lipsește SMTP_PASSWORD (cheia API SendGrid) din variabilele de mediu."
        )
    if not sender_email:
        raise RuntimeError(
            "Lipsește SENDER_EMAIL din variabilele de mediu — trebuie să fie exact "
            "adresa pe care ai verificat-o la SendGrid (Single Sender Verification)."
        )

    with open(pdf_path, "rb") as f:
        pdf_base64 = base64.b64encode(f.read()).decode()

    payload = {
        "personalizations": [{"to": [{"email": to_email}]}],
        "from": {"email": sender_email, "name": firm_name},
        "subject": f"Oferta ta de la {firm_name}",
        "content": [{
            "type": "text/plain",
            "value": (
                f"Bună, {client_name},\n\n"
                f"Îți atașăm oferta discutată. Estimarea este orientativă și o "
                f"confirmăm împreună la discuția de consultanță gratuită.\n\n"
                f"Cu drag,\n{firm_name}"
            ),
        }],
        "attachments": [{
            "content": pdf_base64,
            "filename": pdf_path.name,
            "type": "application/pdf",
            "disposition": "attachment",
        }],
    }

    response = requests.post(
        SENDGRID_API_URL,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=15,
    )

    if response.status_code >= 300:
        raise RuntimeError(
            f"SendGrid a refuzat trimiterea (cod {response.status_code}): {response.text}"
        )

