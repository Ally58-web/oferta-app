# Generator automat de oferte

API Python (FastAPI) care ia rezultatul calculatorului de scop/preț și:
1. calculează prețul + durata estimată a proiectului,
2. generează un PDF de ofertă personalizat,
3. (opțional) îl trimite automat pe email către client.

## Instalare

```bash
pip install -r requirements.txt
cp .env.example .env   # completează cu datele tale SMTP
uvicorn app.main:app --reload
```

Deschide http://localhost:8000/docs pentru interfața Swagger interactivă.

## Exemplu de request

```bash
curl -X POST http://localhost:8000/generate-offer \
  -H "Content-Type: application/json" \
  -d '{
    "client_name": "Ion Popescu",
    "company_name": "Popescu SRL",
    "client_email": "ion@popescu-srl.ro",
    "project_type": "app",
    "integrations": ["anaf", "payments"],
    "users": 80,
    "maintenance": true,
    "send_email": false
  }'
```

Setează `"send_email": true` (și completează `.env`) ca oferta să fie
trimisă automat pe email-ul clientului, cu PDF-ul atașat.

## Structură

```
app/
  main.py            # endpoint-uri FastAPI
  pricing.py         # logica de calcul preț/durată (sincronizată cu calculatorul din chat)
  pdf_generator.py   # generare PDF cu reportlab
  email_sender.py     # trimitere email via SMTP (credențiale din .env, niciodată în cod)
  lead_scoring.py     # scorare/prioritizare a unei liste de lead-uri (CSV in -> CSV out)
frontend/
  calculator.html    # calculator de preț de pus pe site-ul tău, vorbește direct cu API-ul
output/               # PDF-urile generate apar aici
```

## Calculatorul de pe site (frontend/calculator.html)

E o pagină HTML de sine stătătoare, fără build step — o urci pe site-ul
tău (sau o încarci ca iframe) și apelează direct API-ul de mai sus din
browser.

1. Pornește backend-ul (`uvicorn app.main:app --reload`)
2. Actualizează `API_BASE` din `frontend/calculator.html` cu adresa reală
   a backend-ului (localhost pentru test, domeniul tău în producție)
3. Actualizează `allow_origins` din `app/main.py` cu domeniul real al
   site-ului tău, ca CORS să permită apelul din browser
4. Deschide `calculator.html` direct în browser pentru testare locală

## Scorarea lead-urilor (app/lead_scoring.py)

```bash
python app/lead_scoring.py leads.csv leads_scorati.csv
```

Primește un CSV cu firme candidate (adunate manual — târguri, recomandări,
directoare publice) și le prioritizează după probabilitatea de nevoie și
segmentul de preț estimat. Vezi exemplul de format CSV la finalul
fișierului.

**Important — legalitate**: acest script nu colectează și nu trimite
automat emailuri. Contactarea firmelor identificate se face prin canale
care nu necesită consimțământ prealabil (telefon cu operator uman,
LinkedIn, poștă) — Legea 506/2004 interzice și sancționează comunicările
comerciale nesolicitate prin email/SMS/sisteme automate, cu amenzi între
5.000 și 100.000 lei.

## Personalizare

- Schimbă `FIRM_NAME` din `app/main.py` cu numele firmei tale.
- Ajustează prețurile de bază din `app/pricing.py` pe măsură ce capeți
  date reale despre cât durează / costă fiecare tip de proiect.
- Pentru un formular frontend, folosește endpoint-ul `GET /options`
  ca să populezi dinamic tipurile de proiect și integrările disponibile.

## Securitate

- Credențialele SMTP vin exclusiv din variabile de mediu (`.env`), nu
  sunt hardcodate niciunde în cod.
- `.env` este exclus implicit din commit-uri — nu-l adăuga în git.
- Pentru producție, înlocuiește SMTP simplu cu un provider dedicat de
  email tranzacțional (SendGrid, Postmark, Amazon SES) care oferă și
  DKIM/SPF corect configurate, ca emailurile să nu ajungă în spam.
