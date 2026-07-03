"""
Logica de calcul preț / durată pentru oferte, sincronizată cu calculatorul
interactiv folosit în discuția cu clientul.
"""

PROJECT_TYPES = {
    "site": {"label": "Site de prezentare", "min": 300, "max": 800, "days": 3},
    "shop": {"label": "Magazin online", "min": 1500, "max": 4000, "days": 10},
    "app": {"label": "Aplicație internă / business", "min": 3000, "max": 10000, "days": 20},
    "complex": {"label": "Aplicație cu integrări complexe", "min": 8000, "max": 25000, "days": 45},
}

INTEGRATIONS = {
    "anaf": {"label": "ANAF e-Factura", "min": 1500, "max": 3000, "days": 10},
    "payments": {"label": "Procesator de plăți", "min": 1000, "max": 2500, "days": 7},
    "auth": {"label": "Autentificare utilizatori", "min": 800, "max": 2000, "days": 5},
    "api": {"label": "API extern (ERP, curier etc.)", "min": 500, "max": 1500, "days": 4},
}


def calculate_offer(project_type: str, integrations: list[str], users: int, maintenance: bool) -> dict:
    """Calculează prețul, durata și taxa de mentenanță pentru un proiect."""
    if project_type not in PROJECT_TYPES:
        raise ValueError(f"Tip de proiect necunoscut: {project_type}")

    base = PROJECT_TYPES[project_type]
    price_min, price_max, days = base["min"], base["max"], base["days"]
    labels = [base["label"]]

    for key in integrations:
        if key not in INTEGRATIONS:
            continue
        integ = INTEGRATIONS[key]
        price_min += integ["min"]
        price_max += integ["max"]
        days += integ["days"]
        labels.append(integ["label"])

    if users > 200:
        price_min += 3000
        price_max += 6000
        days += 7
    elif users > 50:
        price_min += 1000
        price_max += 3000
        days += 4

    maintenance_fee = round(price_min * 0.06) if maintenance else 0

    return {
        "labels": labels,
        "price_min": round(price_min),
        "price_max": round(price_max),
        "days": round(days),
        "users": users,
        "maintenance": maintenance,
        "maintenance_fee": maintenance_fee,
    }
