import streamlit as st

# 1. Seiten-Konfiguration
st.set_page_config(page_title="moms of hamburg", page_icon="🧡", layout="centered")

# 2. Das CSS-Styling einschleusen
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    @import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,700;1,9..144,400;1,9..144,700&family=Titan+One&display=swap');

    .stApp {
        background-color: #f46d24;
        color: #ffffff;
        font-family: 'Fraunces', serif;
        text-align: center;
    }

    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        max-width: 800px;
    }

    .section {
        min-height: 80vh;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        padding: 60px 0;
        border-bottom: 2px dashed rgba(255, 255, 255, 0.3);
    }
    .section:last-child {
        border-bottom: none;
    }

    .hero-text {
        font-size: 4rem;
        line-height: 1.1;
        margin-bottom: 40px;
        font-weight: 700;
    }
    .hero-text span.italic {
        font-style: italic;
        font-weight: 400;
    }
    .section-title {
        font-size: 2.8rem;
        font-style: italic;
        margin-bottom: 40px;
        font-weight: 700;
        line-height: 1.2;
    }
    .section-title .regular {
        font-style: normal;
    }
    .text-p {
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 15px;
    }

    .logo-container {
        margin-top: 50px;
        margin-bottom: 20px;
    }
    .logo-text {
        font-family: 'Titan One', sans-serif;
        font-size: 3rem;
        letter-spacing: -1px;
        line-height: 0.9;
    }
    .logo-subtext {
        font-size: 0.8rem;
        font-family: sans-serif;
        text-transform: uppercase;
        font-weight: bold;
        letter-spacing: 1px;
        margin-left: 120px;
        margin-top: -15px;
    }
    
    div.stButton > button {
        background-color: #ffffff;
        color: #f46d24;
        font-family: sans-serif;
        font-weight: bold;
        font-size: 1.2rem;
        border-radius: 50px;
        border: none;
        padding: 10px 30px;
    }
    div.stButton > button:hover {
        background-color: #ffeee5;
        color: #f46d24;
    }

    /* Styling für die Tabs und interaktiven Elemente */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        justify-content: center;
    }
    .stTabs [data-basew
