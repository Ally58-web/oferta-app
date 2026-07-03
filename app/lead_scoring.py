"""
Scorează și prioritizează o listă de firme candidate (lead-uri), pornind
de la semnale publice observabile (site vechi, fără site, industrie etc.)

Input: CSV cu firme (vezi exemplu la finalul fișierului)
Output: CSV sortat descrescător după scor, cu segment de preț estimat

Rulare:
    python lead_scoring.py leads.csv leads_scorati.csv

NOTĂ LEGALĂ: acest script NU trimite emailuri și NU colectează automat
date de contact. E gândit pentru liste pe care le-ai adunat tu (târguri,
recomandări, directoare publice de firme, LinkedIn manual). Contactarea
lor se face prin canale care nu necesită consimțământ prealabil (telefon
cu operator uman, LinkedIn, poștă) — nu prin email nesolicitat, interzis
de Legea 506/2004.
"""

import csv
import sys

# Ponderi — ajustează în funcție de ce a funcționat cel mai bine la tine.
WEIGHTS = {
    "no_website": 25,       # nu are deloc site -> nevoie clară
    "outdated_website": 20,  # are site, dar pare vechi/nefuncțional
    "growing_team": 15,      # semne de creștere (angajări, extindere)
    "has_budget_signal": 20,  # ex: face reclame plătite, are birou nou etc.
    "relevant_industry": 20,  # se potrivește cu nișa ta (ex: retail, servicii)
}

INDUSTRY_TIER = {
    # industrie -> (segment de preț orientativ, folosind pricing.py din API)
    "restaurant": "shop",
    "magazin": "shop",
    "cabinet": "app",
    "producție": "complex",
    "servicii": "app",
}


def score_lead(row: dict) -> dict:
    score = 0
    for key, weight in WEIGHTS.items():
        if row.get(key, "").strip().lower() in ("1", "true", "da", "yes"):
            score += weight

    industry = row.get("industry", "").strip().lower()
    tier = INDUSTRY_TIER.get(industry, "app")

    priority = "ridicată" if score >= 60 else "medie" if score >= 30 else "scăzută"

    return {**row, "scor": score, "prioritate": priority, "segment_estimat": tier}


def process_file(input_path: str, output_path: str) -> None:
    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = [score_lead(row) for row in reader]

    rows.sort(key=lambda r: r["scor"], reverse=True)

    fieldnames = list(rows[0].keys()) if rows else []
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"{len(rows)} lead-uri scorate -> {output_path}")
    if rows:
        print("\nTop 5 prioritare:")
        for r in rows[:5]:
            print(f"  {r.get('company_name', '?'):30s} scor={r['scor']:3d}  "
                  f"prioritate={r['prioritate']:8s}  segment={r['segment_estimat']}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Utilizare: python lead_scoring.py input.csv output.csv")
        sys.exit(1)
    process_file(sys.argv[1], sys.argv[2])

# Exemplu de CSV de input (leads.csv):
#
# company_name,industry,no_website,outdated_website,growing_team,has_budget_signal
# Popescu SRL,restaurant,1,0,1,0
# Ionescu Servicii,servicii,0,1,0,1
# Fabrica Nord,producție,0,0,1,1
