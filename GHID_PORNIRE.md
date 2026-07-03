# Ghid de pornire — ce trebuie să faci tu, pas cu pas

Tot ce ține de cod e gata. Restul sunt pași manuali, de business și
configurare, pe care trebuie să-i faci tu (nimeni nu poate să-i facă
în locul tău, pentru că implică datele/contul tău).

---

## Pas 1 — Cont email pentru trimiterea ofertelor

1. Dacă vrei să folosești Gmail: mergi în contul Google → Securitate →
   activează verificarea în 2 pași → generează o "parolă de aplicație"
   (nu parola normală de Gmail).
2. Alternativă mai fiabilă pentru volum mai mare: cont gratuit pe
   **SendGrid** sau **Postmark** (livrare mai bună, nu ajunge în spam).
3. Notează undeva sigur: host SMTP, port, user, parolă. Le pui la Pasul 4.

## Pas 2 — Găzduire pentru backend (API-ul Python)

Recomandare simplă: **Railway** sau **Render** (ambele au plan gratuit
suficient pentru început).

1. Creează cont pe [render.com](https://render.com) sau [railway.app](https://railway.app).
2. Urcă folderul `oferta-app` pe un repository GitHub (dacă nu ai deja
   Git instalat, spune-mi și te ajut cu pașii exacți).
3. Din Render/Railway: "New Web Service" → conectezi repo-ul GitHub →
   platforma detectează automat `Procfile`-ul / `render.yaml`-ul deja incluse.
4. La secțiunea de variabile de mediu, adaugi: `SMTP_HOST`, `SMTP_PORT`,
   `SMTP_USER`, `SMTP_PASSWORD` (cele de la Pasul 1).
5. După deploy, platforma îți dă un URL (ex: `https://oferta-app.onrender.com`).
   Notează-l — îl folosești la Pasul 3.

## Pas 3 — Conectarea calculatorului de pe site

1. Deschide `frontend/calculator.html`.
2. Găsește linia `const API_BASE = "http://localhost:8000";` și
   înlocuiește cu URL-ul real de la Pasul 2.
3. Deschide `app/main.py`, găsește `allow_origins` și înlocuiește
   `"https://www.site-ul-tau.ro"` cu domeniul real al site-ului tău.
4. Redeployează (Render/Railway redeployează automat la fiecare push pe GitHub).
5. Urcă `calculator.html` pe site-ul tău (ca pagină nouă, sau într-un
   `<iframe>` pe pagina de "Cere ofertă").

## Pas 4 — Personalizare

1. În `app/main.py`, schimbă `FIRM_NAME = "Numele firmei tale"` cu numele real.
2. În `app/pricing.py`, ajustează prețurile din `PROJECT_TYPES` și
   `INTEGRATIONS` dacă ai deja o idee mai precisă despre costurile tale reale.
3. (Opțional) Adaugă logo-ul tău în `app/pdf_generator.py` — spune-mi
   dacă vrei ajutor la asta, e un adaos simplu.

## Pas 5 — Testare înainte de lansare

1. Completează calculatorul de pe site cu date de test, folosind
   propriul tău email.
2. Verifică: primești oferta pe email? Arată bine PDF-ul? Ajunge în
   inbox sau în spam? (dacă ajunge în spam, ia în calcul SendGrid/Postmark)
3. Testează pe telefon mobil — pagina e responsive, dar merită verificat.

## Pas 6 — Discovery call

1. Printează sau ține la îndemână `discovery_script.md`.
2. La următorul apel cu un client, urmează structura — nu trebuie
   memorată, doar bifată pe parcurs.

## Pas 7 — Găsirea și scorarea lead-urilor

1. Adună manual o listă de firme candidate (recomandări, târguri,
   directoare publice de firme, LinkedIn) într-un fișier `leads.csv`,
   după formatul de exemplu din `app/lead_scoring.py`.
2. Rulează: `python app/lead_scoring.py leads.csv leads_scorati.csv`
3. Sună/contactează manual (telefon, LinkedIn) — **nu email nesolicitat**
   — începând cu cei cu prioritate ridicată.

---

## Ordinea recomandată dacă vrei să pornești azi

1. Pas 1 (email) — 15 minute
2. Pas 2 (hosting) — 30-40 minute, majoritatea e așteptare la deploy
3. Pas 3 + 4 (conectare + personalizare) — 20 minute
4. Pas 5 (testare) — 10 minute
5. Din ziua următoare: Pas 6 și 7 devin rutină, nu setup unic

Dacă te blochezi la oricare pas (mai ales Pas 2, cu Git/GitHub dacă nu
le-ai folosit până acum), spune-mi exact unde ești și continuăm de acolo.
