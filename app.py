import streamlit as st
import pandas as pd
import plotly.express as px
from pytrends.request import TrendReq
from statsmodels.tsa.holtwinters import ExponentialSmoothing
import warnings
from datetime import datetime

# Warnungen unterdrücken
warnings.filterwarnings("ignore")

# ===== 1. SEITENKONFIGURATION =====
st.set_page_config(
    page_title="Professor Layton Analytics",
    page_icon="🎩",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===== 2. LAYTON CSS STYLES (Mit Fix für die Eingabefelder) =====
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&family=Merriweather:wght@300;400;700&display=swap');

/* Hintergrund wie altes Pergament */
.stApp {
    background: linear-gradient(135deg, #F5E6D3 0%, #E8DCC4 100%);
    background-attachment: fixed;
}

/* Überschriften im Layton-Stil */
h1, h2, h3 {
    font-family: 'Cinzel', serif !important;
    color: #1A0F00 !important; 
    font-weight: 700 !important;
    text-shadow: none !important; 
}

/* Fließtext allgemein */
p, div, span, li {
    font-family: 'Merriweather', serif;
    color: #1A0F00;
    line-height: 1.6;
}

/* ---------------------------------------------------
   NEU: FIX FÜR DIE EINGABEFELDER (Suchtext & Dropdown) 
   --------------------------------------------------- */

/* Das Text-Eingabefeld (Hintergrund und Rahmen) */
div[data-baseweb="input"] > div {
    background-color: #FFF8F0 !important; /* Helles Pergament */
    border: 2px solid #D4AF37 !important; /* Goldener Rahmen */
    border-radius: 6px !important;
}

/* Der eingegebene Text im Suchfeld (Tinte) */
div[data-baseweb="input"] input {
    color: #1A0F00 !important; /* Tiefschwarz/Braun */
    font-weight: 900 !important; /* Extra dick */
    font-size: 1.1em !important;
    -webkit-text-fill-color: #1A0F00 !important; /* Zwingt Browser zur Farbe */
}

/* Das Dropdown-Feld (Zeitraum) */
div[data-baseweb="select"] > div {
    background-color: #FFF8F0 !important;
    border: 2px solid #D4AF37 !important;
    border-radius: 6px !important;
}

/* Der ausgewählte Text im Dropdown */
div[data-baseweb="select"] span {
    color: #1A0F00 !important;
    font-weight: bold !important;
}

/* --------------------------------------------------- */

/* Karten/Container wie Puzzle-Boxen */
.stMetric, div[data-testid="stMetric"] {
    background: linear-gradient(145deg, #FFF8F0, #F0E6D6) !important;
    border: 2px solid #8B4513 !important;
    border-radius: 12px !important;
    box-shadow: 3px 3px 10px rgba(139, 69, 19, 0.2) !important;
    padding: 20px !important;
}

/* Buttons wie Layton's Hut */
.stButton > button {
    background: linear-gradient(145deg, #8B4513, #A0522D) !important;
    color: #F5E6D3 !important;
    font-family: 'Cinzel', serif !important;
    border: 2px solid #D4AF37 !important;
    border-radius: 8px !important;
    box-shadow: 2px 2px 5px rgba(0,0,0,0.3) !important;
    transition: all 0.3s ease !important;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 4px 4px 12px rgba(0,0,0,0.4) !important;
    background: linear-gradient(145deg, #A0522D, #8B4513) !important;
}

/* Sidebar wie ein altes Buch */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #2C1810 0%, #3E2723 100%) !important;
    border-right: 3px solid #D4AF37 !important;
}

/* Sidebar Labels/Text - Weiß für perfekten Kontrast zum dunklen Holz */
section[data-testid="stSidebar"] p, section[data-testid="stSidebar"] label {
    color: #FFFFFF !important; 
    font-family: 'Merriweather', serif !important;
    text-shadow: none !important;
}

/* Tabs wie Kapitel */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background: transparent !important;
}

.stTabs [data-baseweb="tab"] {
    background: linear-gradient(145deg, #D4AF37, #B8860B) !important;
    color: #1A0F00 !important;
    font-weight: bold !important;
    font-family: 'Cinzel', serif !important;
    border-radius: 8px 8px 0 0 !important;
    border: 2px solid #8B4513 !important;
    border-bottom: none !important;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(145deg, #F5E6D3, #E8DCC4) !important;
    border-bottom: 2px solid #F5E6D3 !important;
}
</style>
""", unsafe_allow_html=True)

# ===== 3. LAYTON UI KOMPONENTEN =====
def layton_header(title, subtitle=""):
    col1, col2 = st.columns([1, 4])
    with col1:
        st.markdown("<h1 style='font-size: 4em; text-align: center; margin: 0;'>🎩</h1>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div style="
            background: linear-gradient(145deg, #8B4513, #A0522D);
            padding: 20px;
            border-radius: 12px;
            border: 3px solid #D4AF37;
            box-shadow: 4px 4px 15px rgba(0,0,0,0.3);
            margin-bottom: 20px;
        ">
            <h1 style="color: #F5E6D3 !important; font-family: 'Cinzel', serif; margin: 0; text-align: center; font-size: 2.5em;">{title}</h1>
            {f'<p style="color: #D4AF37; text-align: center; font-family: Merriweather; margin: 10px 0 0 0;">{subtitle}</p>' if subtitle else ''}
        </div>
        """, unsafe_allow_html=True)

def puzzle_metric(label, value, delta=None, icon="🧩"):
    delta_html = ""
    if delta is not None:
        color = "#4CAF50" if delta >= 0 else "#F44336"
        arrow = "▲" if delta >= 0 else "▼"
        delta_html = f'<p style="color: {color}; font-size: 0.9em; font-weight: bold; margin: 5px 0 0 0;">{arrow} {abs(delta):.1f}%</p>'
    
    st.markdown(f"""
    <div style="
        background: linear-gradient(145deg, #FFF8F0, #F0E6D6);
        border: 2px solid #8B4513; border-radius: 12px; padding: 20px; text-align: center;
        box-shadow: 3px 3px 10px rgba(139, 69, 19, 0.2); margin-bottom: 15px;
    ">
        <div style="font-size: 2em; margin-bottom: 10px;">{icon}</div>
        <p style="color: #5D4037; font-weight: bold; font-family: 'Cinzel', serif; font-size: 0.9em; margin: 0; text-transform: uppercase;">{label}</p>
        <h2 style="color: #1A0F00 !important; font-family: 'Cinzel', serif; margin: 10px 0; font-size: 2.2em;">{value}</h2>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)

def mystery_expander(title, content):
    with st.expander(f"🔍 {title}"):
        st.markdown(f"""
        <div style="
            background: #FFF8F0; border-left: 4px solid #D4AF37; padding: 15px;
            margin: 10px 0; font-family: 'Merriweather', serif; color: #1A0F00;
        ">
            {content}
        </div>
        """, unsafe_allow_html=True)

def puzzle_alert(message, type="success"):
    colors = {
        "success": ("#4CAF50", "#E8F5E9", "✅"),
        "warning": ("#FF9800", "#FFF3E0", "⚠️"),
        "error": ("#F44336", "#FFEBEE", "❌"),
        "info": ("#2196F3", "#E3F2FD", "💡")
    }
    border_color, bg_color, icon = colors.get(type, colors["info"])
    st.markdown(f"""
    <div style="
        background: {bg_color}; border: 2px solid {border_color}; border-radius: 8px;
        padding: 15px; margin: 10px 0; font-family: 'Merriweather', serif; display: flex; align-items: center; gap: 10px;
    ">
        <span style="font-size: 1.5em;">{icon}</span><span style="color: #1A0F00; font-weight: bold;">{message}</span>
    </div>
    """, unsafe_allow_html=True)

# ===== 4. DATENABFRAGE MIT CACHE =====
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_google_trends_data(keywords, time_range):
    pytrends = TrendReq(hl='de-DE', tz=360)
    pytrends.build_payload(keywords, cat=0, timeframe=time_range, geo='DE')
    return pytrends.interest_over_time()


# ===== 5. DIE HAUPTANWENDUNG (DETEKTEI-LOGIK) =====

layton_header("Die Detektei für digitale Rätsel", "Ein wahrer Gentleman lässt kein Rätsel ungelöst. ☕")

st.sidebar.header("🔍 Die Ermittlungsakte")
st.sidebar.markdown("Welche Hinweise sollen wir heute untersuchen?")
keywords = st.sidebar.text_input("Hinweise (mit Komma trennen)", "Momlife, Familienalltag, Basteln")
kw_list = [x.strip() for x in keywords.split(",")]
timeframe = st.sidebar.selectbox("Zeitraum der Untersuchung", ["today 3-m", "today 12-m", "today 5-y"], index=1)

if st.sidebar.button("🧩 Ermittlung beginnen"):
    with st.spinner('Wir kochen eine Kanne Tee und werten die Hinweise aus... ☕'):
        try:
            # Abfrage über die Cache-Funktion
            df = fetch_google_trends_data(kw_list, timeframe)
            
            if not df.empty:
                if 'isPartial' in df.columns:
                    df = df.drop(columns=['isPartial'])
                
                puzzle_alert("Die historischen Aufzeichnungen wurden erfolgreich gesichert!", "success")
                
                target_kw = kw_list[0]
                
                if target_kw in df.columns:
                    # Daten für Prognose vorbereiten
                    y = df[target_kw].resample('W').mean().fillna(method='ffill')
                    model = ExponentialSmoothing(y, trend='add', seasonal='add', seasonal_periods=4).fit()
                    forecast = model.forecast(4) 
                    
                    # Metriken berechnen
                    current_val = y.iloc[-1]
                    future_val = forecast.iloc[-1]
                    growth_percent = ((future_val - current_val) / current_val) * 100 if current_val > 0 else 0
                    
                    # Layout Metriken
                    st.markdown("### 🧩 Akten-Übersicht")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        puzzle_metric("Haupt-Hinweis", target_kw, icon="🔍")
                    with col2:
                        puzzle_metric("Aktuelles Interesse", f"{current_val:.0f}", icon="📊")
                    with col3:
                        puzzle_metric("Prognose (4 Wochen)", f"{future_val:.0f}", delta=growth_percent, icon="🔮")
                    
                    st.markdown("---")
                    st.markdown("### 📜 Die Analyse des Rätsels")
                    
                    # Tabs und Charts
                    tab1, tab2 = st.tabs(["Historische Spuren", "Deduktive Vorhersage"])
                    
                    with tab1:
                        fig_history = px.line(df, labels={"value": "Interesse (0-100)", "date": "Datum", "variable": "Hinweis"}, color_discrete_sequence=['#8B4513', '#DAA520', '#556B2F', '#4682B4'])
                        fig_history.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
                        st.plotly_chart(fig_history, use_container_width=True)
                    
                    with tab2:
                        forecast_df = pd.DataFrame({'Datum': forecast.index, 'Interesse': forecast.values, 'Typ': 'Unsere Prognose'})
                        history_df = pd.DataFrame({'Datum': y.index, 'Interesse': y.values, 'Typ': 'Bisherige Spuren'})
                        combined_df = pd.concat([history_df, forecast_df])
                        
                        fig_forecast = px.line(combined_df, x='Datum', y='Interesse', color='Typ', color_discrete_map={'Bisherige Spuren': '#8B4513', 'Unsere Prognose': '#DAA520'})
                        fig_forecast.update_traces(patch={"line": {"dash": "dot"}}, selector={"legendgroup": "Unsere Prognose"})
                        fig_forecast.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
                        st.plotly_chart(fig_forecast, use_container_width=True)
                    
                    # Ratschlag
                    trend_direction = forecast.iloc[-1] - y.iloc[-1]
                    if trend_direction > 5:
                        advice = f"<b>Ausgezeichnet!</b> Die Zeichen stehen auf Sturm. Das Interesse an '{target_kw}' wird wachsen. Bereite deinen nächsten Content zu diesem Thema vor!"
                    elif trend_direction < -5:
                        advice = f"<b>Vorsicht, mein Freund.</b> Das Interesse an '{target_kw}' scheint abzukühlen. Wir sollten unsere Energie vorerst auf andere Rätsel lenken."
                    else:
                        advice = f"<b>Ein solider Fall.</b> Der Trend für '{target_kw}' bleibt bemerkenswert stabil. Du kannst in deinem gewohnten Rhythmus fortfahren."
                    
                    mystery_expander("Die Schlussfolgerung des Professors", advice)

            else:
                puzzle_alert("Unsere Bibliothek hat keine ausreichenden Spuren für diese Begriffe gefunden.", "warning")
                
        except Exception as e:
            puzzle_alert(f"Ein unerwartetes Hindernis ist aufgetreten! (Möglicherweise blockiert Google temporär. Versuche es später erneut.) Detail: {e}", "error")

# Footer
st.sidebar.markdown("---")
st.sidebar.caption("🔧 Apparatur gewartet von Luke Triton (Tech-Support)")
