import json
import os
from decimal import Decimal, ROUND_HALF_UP
import streamlit as st

st.set_page_config(page_title="Hallui", page_icon="🎉")
st.title("🎉 Halluin")
st.write("Scegli cosa vuoi per la festa e pagame purciaro!")

PRODOTTI = {
    "Disaronno": (11.90, "bottiglia"),
    "Jagermeister": (13.99, "bottiglia"),
    "Amaro del Capo": (11.90, "bottiglia"),
    "Montenegro": (14.20, "bottiglia"),
    "Bombay": (16.50, "bottiglia"),
    "Aperitivo Spritz": (2.90, "confezione"),
    "Vodka": (8.99, "bottiglia"),
    "Tonica": (2.00, "confezione"),
    "Coca Cola": (1.79, "confezione"),
    "Fanta": (1.89, "confezione"),
    "Lemon": (0.79, "confezione"),
    "Red Bull": (5.19, "confezione"),
    "Patatine": (1.99, "confezione"),
    "Pop corn": (1.45, "confezione"),
}

FILE_VOTI = "voti.json"

def carica_voti():
    if os.path.exists(FILE_VOTI):
        with open(FILE_VOTI, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

def salva_voti(voti):
    with open(FILE_VOTI, "w", encoding="utf-8") as f:
        json.dump(voti, f, ensure_ascii=False, indent=2)

voti_condivisi = carica_voti()

nome = st.text_input("Il tuo nome")
if nome.strip():
    nome = nome.strip()
    precedenti = voti_condivisi.get(nome, [])
    scelte = st.multiselect(
        "Cosa vuoi?", list(PRODOTTI.keys()), default=precedenti
    )
    if st.button("Salva / aggiorna il mio voto"):
        voti_condivisi[nome] = scelte
        salva_voti(voti_condivisi)
        st.success("Voto aggiornato!")
        st.rerun()

st.divider()
st.subheader("🗳️ Voti dei partecipanti")

if st.button("🔄 Aggiorna lista voti"):
    st.rerun()

if not voti_condivisi:
    st.info("Ancora nessun voto.")
else:
    for persona, scelte_persona in voti_condivisi.items():
        st.write(
            f"**{persona}**: {', '.join(scelte_persona) or 'Nessun prodotto'}"
        )

    # --- NUOVA SEZIONE: Elimina un partecipante ---
    with st.expander("⚙️ Gestisci / Rimuovi un partecipante"):
        da_eliminare = st.selectbox(
            "Seleziona il nome da rimuovere", 
            ["-- Seleziona --"] + list(voti_condivisi.keys())
        )
        if da_eliminare != "-- Seleziona --":
            if st.button("🗑️ Elimina questo utente"):
                del voti_condivisi[da_eliminare]
                salva_voti(voti_condivisi)
                st.success(f"Utente '{da_eliminare}' rimosso con successo!")
                st.rerun()
    # ---------------------------------------------

    comuni = st.number_input(
        "Spese comuni totali (€)", min_value=0.0, value=0.0, step=1.0
    )

    st.divider()
    st.subheader("🛒 Riepilogo acquisti")

    totali = {persona: 0 for persona in voti_condivisi}
    partecipanti = list(totali)
    dettagli = {}

    for prodotto, (prezzo, tipo) in PRODOTTI.items():
        interessati = [
            p
            for p, scelte_persona in voti_condivisi.items()
            if prodotto in scelte_persona
        ]
        if not interessati:
            continue

        quantita = (len(interessati) + 2) // 3
        costo = int(
            (Decimal(str(prezzo)) * quantita * 100).quantize(
                Decimal("1"), rounding=ROUND_HALF_UP
            )
        )
        dettagli[prodotto] = (len(interessati), quantita, costo, tipo)

        base, resto = divmod(costo, len(interessati))
        for i, persona in enumerate(interessati):
            totali[persona] += base + (1 if i < resto else 0)

    cent_comuni = int(round(comuni * 100))
    if partecipanti:
        base, resto = divmod(cent_comuni, len(partecipanti))
        for i, persona in enumerate(partecipanti):
            totali[persona] += base + (1 if i < resto else 0)

    for prodotto, (votanti, quantita, costo, tipo) in dettagli.items():
        st.write(
            f"- **{prodotto}**: {votanti} interessati, "
            f"{quantita} {tipo if quantita == 1 else tipo + 'e/i'}, € {costo / 100:.2f}"
        )

    st.subheader("💶 Quanto paga ciascuno")
    for persona, centesimi in totali.items():
        st.write(f"**{persona}**: € {centesimi / 100:.2f}")

    st.write(
        f"**Totale prodotti:** € {sum(x[2] for x in dettagli.values()) / 100:.2f}"
    )
    st.write(f"**Spese comuni:** € {cent_comuni / 100:.2f}")
    st.write(
        f"**Totale prodotti:** € {sum(x[2] for x in dettagli.values()) / 100:.2f}"
    )
    st.write(f"**Spese comuni:** € {cent_comuni / 100:.2f}")
