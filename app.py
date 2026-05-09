import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from pytrends.request import TrendReq
from statsmodels.tsa.holtwinters import ExponentialSmoothing
import warnings
from datetime import datetime, timedelta

# Warnungen unterdrücken
warnings.filterwarnings("ignore")

# ===== 1. SEITENKONFIGURATION =====
st.set_page_config(page_title="Professor Layton Analytics", page_icon="🎩", layout="wide", initial_sidebar_state="expanded")

# ===== 2. LAYTON CSS STYLES =====
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&family=Merriweather:wght@300;400;700&display=swap');

.stApp { background: linear-gradient(135deg, #F5E6D3 0%, #E8DCC4 100%); background-attachment: fixed; }
h1, h2, h3 { font-family: 'Cinzel', serif !important; color: #1A0F00 !important; font-weight: 700 !important; text-shadow: none !important; }
p, div, span, li { font-family: 'Merriweather', serif; color: #1A0F00; line-height: 1.6; }

/* Eingabefelder Fix */
div[data-baseweb="input"] > div, div[data-baseweb="select"] > div {
    background-color: #FFF8F0 !important; border: 2px solid #D4AF37 !important; border-radius: 6px !important;
}
div[data-baseweb="input"] input, div[data-baseweb="select"] span {
    color: #1A0F00 !important; font-weight: 900 !important; -webkit-text-fill-color: #1A0F00 !important;
}

/* Karten & Buttons */
.stMetric, div[data-testid="stMetric"] {
    background: linear-gradient(145deg, #FFF8F0, #F0E6D6) !important; border: 2px solid #8B4513 !important;
    border-radius: 12px !important; box-shadow: 3px 3px 10px rgba(139, 69, 19, 0.2) !important; padding: 20px !important;
}
.stButton > button {
    background: linear-gradient(145deg, #8B4513, #A0522D) !important; color: #F5E6D3 !important; font-family: 'Cinzel', serif !important;
    border: 2px solid #D4AF37 !important; border-radius: 8px !important; transition: all 0.3s ease !important;
}
.stButton > button:hover { transform: translateY(-2px) !important; background: linear-gradient(145deg, #A0522D, #8B4513) !important; }

/* Sidebar */
section[data-testid="stSidebar"] { background: linear-gradient(180deg, #2C1810 0%, #3E2723 100%) !important; border-right: 3px solid #D4AF37 !important; }
section[data-testid="stSidebar"] p, section[data-testid="stSidebar"] label { color: #FFFFFF !important; font-family: 'Merriweather', serif !important; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] { gap: 8px; background: transparent !important; }
.stTabs [data-baseweb="tab"] { background: linear-gradient(145deg, #D4AF37, #B8860B) !important; color: #1A0F00 !important; font-weight: bold !important; font-family: 'Cinzel', serif !important; border-radius: 8px 8px 0 0 !important; border: 2px solid #8B4513 !important; border-bottom: none !important; }
.stTabs [aria-selected="true"] { background: linear-gradient(145deg, #F5E6D3, #E8DCC4) !important; border-bottom: 2px solid #F5E6D3 !important; }
</style>
""", unsafe_allow_html=True)

# ===== 3. LAYTON UI KOMPONENTEN =====
def layton_header(title, subtitle=""):
    col1, col2 = st.columns([1, 4])
    with col1: st.markdown("<h1 style='font-size: 4em; text-align: center; margin: 0;'>🎩</h1>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div style="background: linear-gradient(145deg, #8B4513, #A0522D); padding: 20px; border-radius: 12px; border: 3px solid #D4AF37; box-shadow: 4px 4px 15px rgba(0,0,0,0.3); margin-bottom: 20px;">
            <h1 style="color: #F5E6D3 !important; font-family: 'Cinzel', serif; margin: 0; text-align: center; font-size: 2.5em;">{title}</h1>
            {f'<p style="color: #D4AF37; text-align: center; font-family: Merriweather; margin: 10px 0 0 0;">{subtitle}</p>' if subtitle else ''}
        </div>""", unsafe_allow_html=True)

def puzzle_metric(label, value, delta=None, icon="🧩"):
    delta_html = f'<p style="color: {"#4CAF50" if delta >= 0 else "#F44336"}; font-size: 0.9em; font-weight: bold; margin: 5px 0 0 0;">{"▲" if delta >= 0 else "▼"} {abs(delta):.1f}%</p>' if delta is not None else ""
    st.markdown(f"""
    <div style="background: linear-gradient(145deg, #FFF8F0, #F0E6D6); border: 2px solid #8B4513; border-radius: 12px; padding: 20px; text-align: center; margin-bottom: 15px;">
        <div style="font-size: 2em; margin-bottom: 10px;">{icon}</div>
        <p style="color: #5D4037; font-weight: bold; font-family: 'Cinzel', serif; font-size: 0.9em; margin: 0; text-transform: uppercase;">{label}</p>
        <h2 style="color: #1A0F00 !important; font-family: 'Cinzel', serif; margin: 10px 0; font-size: 2.2em;">{value}</h2>{delta_html}
    </div>""", unsafe_allow_html=True)

def puzzle_alert(message, type="success"):
    colors = {"success": ("#4CAF50", "#E8F5E9", "✅"), "warning": ("#FF9800", "#FFF3E0", "⚠️"), "error": ("#F44336", "#FFEBEE", "❌"), "info": ("#2196F3", "#E3F2FD", "💡")}
    b_col, bg_col, icon = colors.get(type)
    st.markdown(f'<div style="background: {bg_col}; border: 2px solid {b_col}; border-radius: 8px; padding: 15px; margin: 10px 0; display: flex; align-items: center; gap: 10px;"><span style="font-size: 1.5em;">{icon}</span><span style="color: #1A0F00; font-weight: bold;">{message}</span></div>', unsafe_allow_html=True)

# ===== 4. ROBUSTE DATENABFRAGE (Mit Fallback!) =====
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_trends_robust(keywords, time_range):
    try:
        # Versuch 1: Echte Google Trends
        pytrends = TrendReq(hl='de-DE', tz=360, timeout=(10,25))
        pytrends.build_payload(keywords, cat=0, timeframe=time_range, geo='DE')
        df = pytrends.interest_over_time()
        if not df.empty:
            if 'isPartial' in df.columns: df = df.drop(columns=['isPartial'])
            return df, "Echt"
    except Exception:
        pass
    
    # Versuch 2: Notfall-Simulation (Wenn Google blockiert)
    # Generiert realistische, algorithmische Daten für die Keywords
    dates = pd.date_range(end=datetime.today(), periods=52, freq='W')
    df_sim = pd.DataFrame(index=dates)
    for kw in keywords:
        base_trend = np.linspace(30, 60, 52) + np.random.normal(0, 5, 52)
        seasonality = np.sin(np.linspace(0, 4 * np.pi, 52)) * 15
        df_sim[kw] = np.clip(base_trend + seasonality, 0, 100)
    return df_sim, "Simuliert"

# ===== 5. DIE HAUPTANWENDUNG =====
layton_header("Die Detektei für digitale Rätsel", "Ein wahrer Gentleman lässt kein Rätsel ungelöst. ☕")

st.sidebar.header("🔍 Die Ermittlungsakte")
keywords = st.sidebar.text_input("Hinweise (mit Komma trennen)", "Momlife, Familienalltag, Basteln")
kw_list = [x.strip() for x in keywords.split(",")]
timeframe = st.sidebar.selectbox("Zeitraum der Untersuchung", ["today 3-m", "today 12-m", "today 5-y"], index=1)

if st.sidebar.button("🧩 Ermittlung beginnen"):
    with st.spinner('Wir kochen eine Kanne Tee und werten die Hinweise aus... ☕'):
        
        # Daten abrufen (Echt oder Simuliert)
        df, data_source = fetch_trends_robust(kw_list, timeframe)
        
        if data_source == "Echt":
            puzzle_alert("Die historischen Aufzeichnungen von Google wurden erfolgreich gesichert!", "success")
        else:
            puzzle_alert("Google verweigert den Zutritt (Fehler 429). Der Professor hat stattdessen den Detektiv-Modus aktiviert und Daten auf Basis von Algorithmen-Mustern simuliert!", "warning")
            
        target_kw = kw_list[0]
        
        if target_kw in df.columns:
            # Daten glätten und vorhersagen
            y = df[target_kw].resample('W').mean().fillna(method='ffill')
            model = ExponentialSmoothing(y, trend='add', seasonal='add', seasonal_periods=4).fit()
            forecast = model.forecast(4) 
            
            # Metriken
            current_val = y.iloc[-1]
            future_val = forecast.iloc[-1]
            growth_percent = ((future_val - current_val) / current_val) * 100 if current_val > 0 else 0
            
            st.markdown("### 🧩 Akten-Übersicht")
            col1, col2, col3 = st.columns(3)
            with col1: puzzle_metric("Haupt-Hinweis", target_kw, icon="🔍")
            with col2: puzzle_metric("Aktuelles Interesse", f"{current_val:.0f}", icon="📊")
            with col3: puzzle_metric("Prognose (4 Wochen)", f"{future_val:.0f}", delta=growth_percent, icon="🔮")
            
            st.markdown("---")
            st.markdown("### 📜 Die tiefe Analyse des Rätsels")
            
            # NEU: Drei Tabs für noch mehr Analyse
            tab1, tab2, tab3 = st.tabs(["Spurensuche (Historie)", "Vorhersage", "Tiefe Analyse (Trend vs. Hype)"])
            
            with tab1:
                fig_hist = px.line(df, labels={"value": "Interesse", "index": "Datum", "variable": "Hinweis"}, color_discrete_sequence=['#8B4513', '#DAA520', '#556B2F'])
                fig_hist.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_hist, use_container_width=True)
            
            with tab2:
                combined_df = pd.concat([
                    pd.DataFrame({'Datum': y.index, 'Interesse': y.values, 'Typ': 'Bisherige Spuren'}),
                    pd.DataFrame({'Datum': forecast.index, 'Interesse': forecast.values, 'Typ': 'Unsere Prognose'})
                ])
                fig_cast = px.line(combined_df, x='Datum', y='Interesse', color='Typ', color_discrete_map={'Bisherige Spuren': '#8B4513', 'Unsere Prognose': '#DAA520'})
                fig_cast.update_traces(patch={"line": {"dash": "dot"}}, selector={"legendgroup": "Unsere Prognose"})
                fig_cast.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_cast, use_container_width=True)
                
            with tab3:
                st.markdown(f"**Ist '{target_kw}' ein langfristiger Trend oder nur ein kurzer Hype?**")
                st.markdown("Hier trennen wir das 'Grundinteresse' vom kurzfristigen Rauschen.")
                # Einfache Trend-Zerlegung (Gleitender Durchschnitt)
                trend_line = y.rolling(window=4, center=True).mean()
                noise = y - trend_line
                
                deep_df = pd.DataFrame({'Datum': y.index, 'Langfristiger Trend': trend_line, 'Kurzfristiger Hype': noise})
                fig_deep = px.line(deep_df, x='Datum', y=['Langfristiger Trend', 'Kurzfristiger Hype'], color_discrete_sequence=['#8B4513', '#D4AF37'])
                fig_deep.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', legend_title_text="Analyse-Ebene")
                st.plotly_chart(fig_deep, use_container_width=True)
                
                st.info("💡 **Tipp des Professors:** Wenn die Linie 'Langfristiger Trend' steigt, solltest du das Thema fest in deine Content-Strategie aufnehmen. Schlägt nur der 'Hype' aus, mach schnell ein Reel dazu und widme dich dann wieder anderen Dingen.")

st.sidebar.markdown("---")
st.sidebar.caption("🔧 Apparatur gewartet von Luke Triton (Tech-Support)")
