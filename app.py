import streamlit as st
import pandas as pd
import plotly.express as px
from pytrends.request import TrendReq

# 1. Seiten-Konfiguration (Muss ganz oben stehen!)
st.set_page_config(page_title="Ghost Trend Lab", page_icon="👻", layout="wide")

# 2. Titel und Beschreibung
st.title("👻 Ghost-Tech & Nischen-Radar")

# WICHTIG: Hier sind die dreifachen Anführungszeichen korrekt geschlossen!
st.markdown("""
Willkommen im **Data-Dashboard**. 
Hiermit analysieren wir Suchtrends (Google Trends) für die Nische 'Momlife & Spuk', 
um vorherzusagen, welche Themen als Nächstes viral gehen könnten.
""")

# 3. Google Trends Setup
# hl='de-DE' setzt die Sprache auf Deutsch, tz=360 ist die Zeitzone (Mitteleuropa)
pytrends = TrendReq(hl='de-DE', tz=360)

# 4. Sidebar (Seitenleiste für Einstellungen)
st.sidebar.header("🔍 Trend-Parameter")
st.sidebar.markdown("Gib hier die Begriffe ein, die du vergleichen möchtest.")

# Eingabefeld für Keywords
keywords = st.sidebar.text_input("Keywords (mit Komma trennen)", "Geister, Spuk, Momlife")

# Die eingegebenen Wörter säubern und in eine Liste packen
kw_list = [x.strip() for x in keywords.split(",")]

# Dropdown für den Zeitraum
timeframe = st.sidebar.selectbox(
    "Zeitraum auswählen", 
    ["today 3-m", "today 12-m", "today 5-y"],
    index=1 # Wählt standardmäßig "today 12-m" aus
)

# 5. Hauptbereich: Daten abrufen und visualisieren
if st.sidebar.button("📊 Daten analysieren"):
    
    # Lade-Animation anzeigen
    with st.spinner('Hole Daten von Google Trends... Das kann kurz dauern.'):
        
        try:
            # Anfrage an Google Trends senden (geo='DE' für Deutschland)
            pytrends.build_payload(kw_list, cat=0, timeframe=timeframe, geo='DE')
            df = pytrends.interest_over_time()
            
            # Prüfen, ob Daten gefunden wurden
            if not df.empty:
                # Die Spalte 'isPartial' löschen, falls vorhanden (brauchen wir nicht)
                if 'isPartial' in df.columns:
                    df = df.drop(columns=['isPartial'])
                
                # Erfolgsmeldung
                st.success("Daten erfolgreich geladen!")
                
                # Diagramm zeichnen
                st.subheader("📈 Suchinteresse über die Zeit")
                fig = px.line(
                    df, 
                    labels={"value": "Suchinteresse (0-100)", "date": "Datum", "variable": "Suchbegriff"},
                    template="plotly_dark" # Sieht cool und "spooky" aus
                )
                # Den Chart anzeigen
                st.plotly_chart(fig, use_container_width=True)
                
                # TimesFM Platzhalter für später
                st.markdown("---")
                st.subheader("🤖 KI-Vorhersage (TimesFM)")
                st.info("""
                Die historischen Daten sind bereit. Im nächsten Schritt wird das **TimesFM-Modell** 
                diese Kurven analysieren und den nächsten Peak vorhersagen. 
                *(Modell-Integration in Vorbereitung)*
                """)
                
            else:
                st.warning("Keine ausreichenden Daten für diese Begriffe gefunden. Versuche allgemeinere Wörter.")
                
        except Exception as e:
            # Falls Google Trends uns blockiert (passiert manchmal bei zu vielen Anfragen)
            st.error(f"Es gab einen Fehler beim Abrufen der Daten. Detail: {e}")

# 6. Footer (kleiner Gag für die Frau)
st.sidebar.markdown("---")
st.sidebar.caption("Made with ❤️ by deinem Tech-Support")
