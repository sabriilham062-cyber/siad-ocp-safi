"""
🚂 SIAD OCP Safi — Système Interactif d'Aide à la Décision
Application Streamlit pour l'optimisation durable du transport ferroviaire.
"""
import streamlit as st
import pandas as pd
import numpy as np
import joblib
import json
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from pathlib import Path

# === CONFIGURATION ===
st.set_page_config(
    page_title="SIAD OCP Safi",
    page_icon="🚂",
    layout="wide",
    initial_sidebar_state="expanded"
)

# === STYLE PERSONNALISÉ ===
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1f3864 0%, #2e75b6 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: white;
        padding: 1.2rem;
        border-radius: 10px;
        border-left: 4px solid #2e75b6;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #f0f2f6;
        border-radius: 6px;
        padding: 8px 16px;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background-color: #2e75b6;
        color: white;
    }
    h1, h2, h3 {
        color: #1f3864;
    }
    .success-box {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        padding: 1rem;
        border-radius: 6px;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 1rem;
        border-radius: 6px;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #d1ecf1;
        border-left: 4px solid #17a2b8;
        padding: 1rem;
        border-radius: 6px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# === CHARGEMENT DES RESSOURCES (cache) ===
@st.cache_data
def load_data():
    df = pd.read_csv('data/transport_ocp_2025.csv')
    df['date'] = pd.to_datetime(df['date'])
    return df

@st.cache_resource
def load_model():
    return joblib.load('models/gradient_boosting.pkl')

@st.cache_data
def load_metrics():
    with open('models/metrics.json', 'r') as f:
        return json.load(f)

# === SIDEBAR ===
with st.sidebar:
    st.markdown("### 🚂 SIAD OCP Safi")
    st.markdown("---")
    st.markdown("**Mémoire de fin d'études**")
    st.markdown("Optimisation durable du transport ferroviaire interne")
    st.markdown("---")

    page = st.radio(
        "📍 Navigation",
        [
            "🏠 Tableau de bord",
            "🔮 Prédiction du tonnage",
            "⚙️ Optimisation & ordonnancement",
            "🌱 Impact économique & environnemental"
        ],
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.markdown("### 📊 Données")
    df = load_data()
    st.metric("Période analysée", f"{len(df)} jours")
    st.metric("Tonnage total", f"{df['tonnage'].sum()/1e6:.2f}M t")

    st.markdown("---")
    st.caption("© 2026 — SIAD OCP Safi")
    st.caption("Powered by Streamlit + Python")

# === ROUTAGE DES PAGES ===
if page == "🏠 Tableau de bord":
    from page_modules import dashboard
    dashboard.show(df, load_metrics())

elif page == "🔮 Prédiction du tonnage":
    from page_modules import prediction
    prediction.show(df, load_model(), load_metrics())

elif page == "⚙️ Optimisation & ordonnancement":
    from page_modules import optimization_page
    optimization_page.show(df)

elif page == "🌱 Impact économique & environnemental":
    from page_modules import impact
    impact.show(df)
