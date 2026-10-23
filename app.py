
import streamlit as st
import requests
from decimal import Decimal

st.set_page_config(page_title="Halluin", page_icon="🎉")
st.title("🎉 Halluin")
st.write("Scegli cosa vuoi per la festa e scopri la tua quota!")

URL_FOGLIO = "https://script.google.com/macros/s/AKfycbyEQKa2nEI2JZ4KTkR9-w0XrY5jqHJ162nId5kIXGS9NYwMsm_nO1-o2nUaRJazQNbb7w/exec"

PRODOTTI = {
    "Disaronno": 11.90,
    "Jagermeister": 13.99,
    "Amaro del Capo": 11.90,
    "Montenegro": 14.20,
    "Bombay": 16.50,
    "Aperitivo Spritz": 2.90,
    "Vodka": 8.99,
    "Tonica": 2.00,
    "Coca Cola": 1.79,
    "Fanta": 1.89,
    "Lemon": 0.79,
    "Red Bull": 5.19,
    "Patatine": 1.99,
    "Pop corn": 1.45,
}

def leggi_voti():
    r = requests.get(URL_FOGLIO, timeout=20)
    r.raise_for_status()
    righe = r.json()
    voti = {}
    for riga in righe[1:]:
        if len(riga) >= 2 and str(riga[0]).strip():
            voti[str(riga[0]).strip()] = [
                p.strip() for p in str(riga[1]).split(",") if p.strip()
            ]
    return voti

def salva_voto(nome, prodotti):
    r = requests.post(
        URL_FOGLIO,
        json={"nome": nome, "prodotti": prodotti},
        timeout=30,
    )
    r.raise_for_status()
    if r.text.strip() != "OK":
        raise RuntimeError("Google Sheets non ha confermato il salvataggio.")

try:
    voti = leggi_voti()
except Exception as e:
    st.error("Non riesco a leggere Google Sheets. Controlla l'URL e la distribuzione Apps Script.")
    st.stop()

st.subheader("🗳️ Il tuo voto")
nome = st.text_input("Scrivi il tuo nome").strip()

if nome:
    scelte = st.multiselect(
        "Scegli i prodotti",
        list(PRODOTTI.keys()),
        default=voti.get(nome, []),
    )
    if st.button("Salva il mio voto"):
        try:
            salva_voto(nome, scelte)
            st.success("Voto salvato!")
            st.rerun()
        except Exception:
            st.error("Salvataggio non riuscito. Riprova.")

st.divider()
st.subheader("👀 Voti visibili a tutti")

if not voti:
    st.info("Ancora nessun voto.")
else:
    for persona, scelte_persona in voti.items():
        st.write(f"**{persona}:** {', '.join(scelte_persona) or 'Nessun prodotto'}")

    st.subheader("🛒 Spesa dei prodotti")
    totali = {persona: 0 for persona in voti}
    totale_prodotti = 0

    for prodotto, prezzo in PRODOTTI.items():
        interessati = [
            persona for persona, scelte_persona in voti.items()
            if prodotto in scelte_persona
        ]
        n = len(interessati)
        if not n:
            continue

        quantita = (n + 2) // 3
        costo_cent = round(prezzo * 100) * quantita
        totale_prodotti += costo_cent
        st.write(
            f"**{prodotto}:** {quantita} confezioni — "
            f"{n} votanti — € {costo_cent / 100:.2f}"
        )

        base, resto = divmod(costo_cent, n)
        for i, persona in enumerate(interessati):
            totali[persona] += base + (1 if i < resto else 0)

    st.subheader("💶 Spese comuni")
    comuni = st.number_input(
        "Inserisci il totale delle spese comuni (€)",
        min_value=0.0,
        value=0.0,
        step=1.0,
    )
    comuni_cent = round(comuni * 100)
    persone = list(voti)
    base, resto = divmod(comuni_cent, len(persone))
    for i, persona in enumerate(persone):
        totali[persona] += base + (1 if i < resto else 0)

    st.subheader("💰 Quanto paga ciascuno")
    for persona, cent in totali.items():
        st.write(f"**{persona}:** € {cent / 100:.2f}")

    st.write(f"**Totale prodotti:** € {totale_prodotti / 100:.2f}")
    st.write(f"**Spese comuni:** € {comuni_cent / 100:.2f}")

if st.button("🔄 Aggiorna voti"):
    st.rerun()
