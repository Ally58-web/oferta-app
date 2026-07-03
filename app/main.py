"""
API pentru generarea automată de oferte PDF pornind de la calculatorul
de scop/preț, cu opțiune de trimitere pe email către client.

Rulare locală:
    uvicorn app.main:app --reload

Documentație interactivă (Swagger): http://localhost:8000/docs
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, EmailStr, Field

from app.pricing import calculate_offer, PROJECT_TYPES, INTEGRATIONS
from app.pdf_generator import generate_offer_pdf
from app.email_sender import send_offer_email

app = FastAPI(title="Generator automat de oferte", version="1.0.0")
@app.get("/")
def root():
    return {
        "status": "online",
        "message": "Generator automat de oferte API",
        "docs": "/docs"
    }
# Permite calculatorului de pe site-ul tău să apeleze acest API din browser.
# Înlocuiește cu domeniul tău real înainte de a merge în producție —
# "*" e ok doar pentru testare locală.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://www.site-ul-tau.ro", "http://localhost:5500"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

FIRM_NAME = "Numele firmei tale"  # schimbă cu numele tău / al firmei


class OfferRequest(BaseModel):
    client_name: str = Field(..., min_length=2)
    company_name: str = Field(..., min_length=2)
    client_email: EmailStr | None = None
    project_type: str
    integrations: list[str] = []
    users: int = Field(default=20, ge=1, le=100000)
    maintenance: bool = False
    send_email: bool = False


@app.get("/options")
def get_options():
    """Returnează tipurile de proiect și integrările disponibile (pentru un formular frontend)."""
    return {"project_types": PROJECT_TYPES, "integrations": INTEGRATIONS}


@app.post("/generate-offer")
def generate_offer(req: OfferRequest):
    """Calculează prețul, generează PDF-ul de ofertă și, opțional, îl trimite pe email."""
    try:
        offer = calculate_offer(
            req.project_type, req.integrations, req.users, req.maintenance
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    pdf_path = generate_offer_pdf(
        client_name=req.client_name,
        company_name=req.company_name,
        offer=offer,
        firm_name=FIRM_NAME,
    )

    email_sent = False
    if req.send_email:
        if not req.client_email:
            raise HTTPException(status_code=400, detail="client_email este necesar pentru trimitere pe email.")
        send_offer_email(req.client_email, req.client_name, pdf_path, FIRM_NAME)
        email_sent = True

    return {
        "offer": offer,
        "pdf_filename": pdf_path.name,
        "email_sent": email_sent,
    }


@app.get("/download/{filename}")
def download_offer(filename: str):
    """Descarcă un PDF de ofertă generat anterior."""
    filepath = generate_offer_pdf.__globals__["OUTPUT_DIR"] / filename
    if not filepath.exists() or not filepath.is_relative_to(filepath.parent):
        raise HTTPException(status_code=404, detail="Fișierul nu a fost găsit.")
    return FileResponse(filepath, media_type="application/pdf", filename=filename)
