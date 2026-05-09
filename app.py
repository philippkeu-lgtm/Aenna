import streamlit as st
import pandas as pd
import plotly.express as px
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from pytrends.request import TrendReq

# 1. Seiten-Konfiguration (Muss ganz oben stehen!)
st.set_page_config(page_title="Ghost Trend Lab", page_icon="👻", layout="wide")

# 2. Titel und Beschreibung
st.title("👻 Ghost-Tech & Nischen-Radar")

# WICHTIG: Hier sind die dreifachen Anführungszeichen korrekt geschlossen!
st.markdown("""
# --- ECHTE VORHERSAGE ---
                st.markdown("---")
                st.subheader("🔮 KI-Trend-Vorhersage (30 Tage)")
                
                try:
                    # Wir nehmen den ersten Suchbegriff aus der Liste für die Vorhersage
                    target_kw = kw_list[0]
                    
                    if target_kw in df.columns:
                        # Daten vorbereiten (wöchentliche Frequenz annehmen, um Rauschen zu filtern)
                        y = df[target_kw].resample('W').mean().fillna(method='ffill')
                        
                        # Das Machine-Learning Modell trainieren (Holt-Winters)
                        # Es sucht nach Trends und saisonalen Mustern
                        model = ExponentialSmoothing(
                            y, 
                            trend='add', 
                            seasonal='add', 
                            seasonal_periods=4 # Annahme: Monatliche Muster
                        ).fit()
                        
                        # 4 Wochen (ca. 1 Monat) in die Zukunft vorhersagen
                        forecast = model.forecast(4)
                        
                        # Vorhersage-Datenbank für das Diagramm erstellen
                        forecast_df = pd.DataFrame({
                            'Datum': forecast.index,
                            'Suchinteresse (0-100)': forecast.values,
                            'Typ': 'Vorhersage'
                        })
                        
                        # Historische Daten für das Diagramm anpassen
                        history_df = pd.DataFrame({
                            'Datum': y.index,
                            'Suchinteresse (0-100)': y.values,
                            'Typ': 'Vergangenheit'
                        })
                        
                        # Beide Datensätze zusammenfügen
                        combined_df = pd.concat([history_df, forecast_df])
                        
                        # Neues Diagramm mit Vorhersage zeichnen
                        fig_forecast = px.line(
                            combined_df, 
                            x='Datum', 
                            y='Suchinteresse (0-100)', 
                            color='Typ',
                            color_discrete_map={'Vergangenheit': '#1f77b4', 'Vorhersage': '#ff7f0e'},
                            title=f"Trend-Prognose für '{target_kw}'",
                            template="plotly_dark"
                        )
                        # Die Vorhersage gestrichelt darstellen
                        fig_forecast.update_traces(patch={"line": {"dash": "dot"}}, selector={"legendgroup": "Vorhersage"})
                        
                        st.plotly_chart(fig_forecast, use_container_width=True)
                        
                        # Handlungs-Empfehlung generieren
                        trend_direction = forecast.iloc[-1] - y.iloc[-1]
                        if trend_direction > 5:
                            st.success(f"📈 **Algorithmus-Tipp:** Das Interesse an '{target_kw}' wird im nächsten Monat stark steigen! Perfekter Zeitpunkt, um Content vorzuproduzieren.")
                        elif trend_direction < -5:
                            st.warning(f"📉 **Algorithmus-Tipp:** Der Trend für '{target_kw}' kühlt gerade ab. Versuche einen anderen Hook oder warte etwas ab.")
                        else:
                            st.info(f"➡️ **Algorithmus-Tipp:** Der Trend für '{target_kw}' bleibt stabil. Du kannst in deiner normalen Frequenz weiterposten.")
                            
                except Exception as e:
                    st.error(f"Vorhersage-Modell konnte nicht berechnet werden. (Zu wenig Datenpunkte oder Fehler: {e})")
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
