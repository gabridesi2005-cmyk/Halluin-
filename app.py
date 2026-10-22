
import streamlit as st
from decimal import Decimal, ROUND_HALF_UP

st.set_page_config(page_title="Halluin", page_icon="🎉")
st.title("🎉 Halluin")
st.write("Scegli cosa vuoi per la festa e scopri la tua quota! no rimborsi te attacchi")

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

if "voti" not in st.session_state:
    st.session_state.voti = {}

nome = st.text_input("Il tuo nome")
if nome.strip():
    nome = nome.strip()
    precedenti = st.session_state.voti.get(nome, [])
    scelte = st.multiselect(
        "Cosa vuoi?",
        list(PRODOTTI.keys()),
        default=precedenti
    )
    if st.button("Salva / aggiorna il mio voto"):
        st.session_state.voti[nome] = scelte
        st.success("Voto aggiornato!")

st.divider()
st.subheader("🗳️ Voti dei partecipanti")

if not st.session_state.voti:
    st.info("Ancora nessun voto.")
else:
    for persona, scelte_persona in st.session_state.voti.items():
        st.write(f"**{persona}**: {', '.join(scelte_persona) or 'Nessun prodotto'}")

    comuni = st.number_input(
        "Spese comuni totali (€)",
        min_value=0.0,
        value=0.0,
        step=1.0
    )

    st.divider()
    st.subheader("🛒 Riepilogo acquisti")

    totali = {persona: 0 for persona in st.session_state.voti}
    partecipanti = list(totali)
    dettagli = {}

    for prodotto, (prezzo, tipo) in PRODOTTI.items():
        interessati = [
            p for p, scelte_persona in st.session_state.voti.items()
            if prodotto in scelte_persona
        ]
        if not interessati:
            continue

        # Regola provvisoria: una bottiglia/confezione ogni 3 votanti.
        quantita = (len(interessati) + 2) // 3
        costo = int(
            (Decimal(str(prezzo)) * quantita * 100).quantize(
                Decimal("1"), rounding=ROUND_HALF_UP
            )
        )
        dettagli[prodotto] = (len(interessati), quantita, costo)

        base, resto = divmod(costo, len(interessati))
        for i, persona in enumerate(interessati):
            totali[persona] += base + (1 if i < resto else 0)

    cent_comuni = int(round(comuni * 100))
    if partecipanti:
        base, resto = divmod(cent_comuni, len(partecipanti))
        for i, persona in enumerate(partecipanti):
            totali[persona] += base + (1 if i < resto else 0)

    for prodotto, (votanti, quantita, costo) in dettagli.items():
        st.write(
            f"- **{prodotto}**: {votanti} interessati, "
            f"{quantita} confezioni, € {costo / 100:.2f}"
        )

    st.subheader("💶 Quanto paga ciascuno")
    for persona, centesimi in totali.items():
        st.write(f"**{persona}**: € {centesimi / 100:.2f}")

    st.write(f"**Totale prodotti:** € {sum(x[2] for x in dettagli.values()) / 100:.2f}")
    st.write(f"**Spese comuni:** € {cent_comuni / 100:.2f}")
