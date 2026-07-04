"""
Generează un PDF de ofertă personalizat, pornind de la rezultatul
calculatorului de preț (vezi pricing.py).
"""

from datetime import date
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# Fontul stă în app/fonts/DejaVuSans.ttf — un singur nivel mai sus
# față de acest fișier (app/pdf_generator.py -> app/fonts/).
FONT_PATH = Path(__file__).resolve().parent / "fonts" / "DejaVuSans.ttf"
FONT_NAME = "DejaVuSans"

if not FONT_PATH.exists():
    raise FileNotFoundError(
        f"Nu găsesc fontul la {FONT_PATH}. Verifică să existe fișierul "
        f"DejaVuSans.ttf exact în acel folder (extensia trebuie să fie "
        f".ttf, nu .tff)."
    )

pdfmetrics.registerFont(TTFont(FONT_NAME, str(FONT_PATH)))


def generate_offer_pdf(client_name: str, company_name: str, offer: dict,
                        firm_name: str = "Numele firmei tale") -> Path:
    """Construiește PDF-ul de ofertă și returnează calea fișierului generat."""
    filename = f"oferta_{company_name.replace(' ', '_')}_{date.today().isoformat()}.pdf"
    filepath = OUTPUT_DIR / filename

    doc = SimpleDocTemplate(
        str(filepath), pagesize=A4,
        topMargin=25 * mm, bottomMargin=20 * mm,
        leftMargin=20 * mm, rightMargin=20 * mm,
    )

    styles = getSampleStyleSheet()
    # Setăm fontul cu diacritice PE stilurile existente, nu ca stil nou.
    for style_name in ("Normal", "Title", "Heading2"):
        styles[style_name].fontName = FONT_NAME

    title_style = ParagraphStyle(
        "OfferTitle", parent=styles["Title"], fontSize=20, spaceAfter=4
    )
    subtitle_style = ParagraphStyle(
        "OfferSubtitle", parent=styles["Normal"], textColor=colors.grey, spaceAfter=20
    )
    section_style = ParagraphStyle(
        "Section", parent=styles["Heading2"], spaceBefore=16, spaceAfter=8
    )

    story = []
    story.append(Paragraph(f"Ofertă de colaborare — {firm_name}", title_style))
    story.append(Paragraph(f"Pregătită pentru {client_name}, {company_name}", subtitle_style))
    story.append(Paragraph(f"Data: {date.today().strftime('%d.%m.%Y')}", styles["Normal"]))

    story.append(Paragraph("Scopul proiectului", section_style))
    for label in offer["labels"]:
        story.append(Paragraph(f"• {label}", styles["Normal"]))

    story.append(Paragraph("Estimare", section_style))
    table_data = [
        ["Preț estimat", f"{offer['price_min']:,} – {offer['price_max']:,} EUR".replace(",", ".")],
        ["Durată estimată", f"{offer['days']} zile lucrătoare"],
        ["Utilizatori concurenți estimați", str(offer["users"])],
        ["Mentenanță lunară",
         f"{offer['maintenance_fee']:,} EUR / lună".replace(",", ".") if offer["maintenance"] else "Neinclusă"],
    ]
    table = Table(table_data, colWidths=[70 * mm, 90 * mm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.whitesmoke),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ("FONTNAME", (0, 0), (-1, -1), FONT_NAME),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(table)

    story.append(Paragraph("Pașii următori", section_style))
    story.append(Paragraph(
        "Această estimare este orientativă și va fi confirmată în urma discuției "
        "de consultanță gratuită (15-20 minute), unde stabilim exact cerințele tehnice și "
        "de securitate ale proiectului tău.", styles["Normal"]
    ))

    story.append(Spacer(1, 20))
    story.append(Paragraph(
        "Notă: prețul final poate varia în funcție de complexitatea reală "
        "identificată la discovery și de eventuale cerințe suplimentare de "
        "conformitate (ex. ANAF, PCI DSS pentru plăți).",
        ParagraphStyle("Note", parent=styles["Normal"], fontSize=8, textColor=colors.grey)
    ))

    doc.build(story)
    return filepath
