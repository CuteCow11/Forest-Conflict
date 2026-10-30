# Author: Krish Shukla
# Roll Number: 240101017
# Project: Wildlife Conflict Tracking System

import os
import sqlite3  # <-- ADDED for database support
import streamlit as st
from streamlit_autorefresh import st_autorefresh
import pandas as pd
from streamlit_folium import st_folium

from data.generate_data import generate_dataset
from model.train import train_model, predict, FEATURE_COLS
from utils.map_utils import (
    build_incident_map,
    build_heatmap,
    build_prediction_map,
)
from utils.filters import render_sidebar, render_stats

# ── Page config ──────────────────────────────────────
st.set_page_config(
    page_title="Chandrapur Wildlife Conflict Dashboard",
    page_icon="🐯",
    layout="wide"
)
st_autorefresh(interval=5000, key="data_refresh")
st.title("🐯 Chandrapur Wildlife Conflict Dashboard")
st.caption("Tadoba-Andhari Tiger Reserve — Conflict Tracking System")

COLOR_MAP = {
    "Tiger":      "red",
    "Leopard":    "orange",
    "Elephant":   "gray",
    "Wild Boar":  "green",
    "Sloth Bear": "purple",
}

EMOJI_MAP = {
    "Tiger":      "🐯",
    "Leopard":    "🐆",
    "Elephant":   "🐘",
    "Wild Boar":  "🐗",
    "Sloth Bear": "🐻",
}

# ── Load / generate data ─────────────────────────────
DATA_PATH = "data/wildlife.db"  # <-- CHANGED to point to the SQLite database

# THE FIX: Removed @st.cache_data so the dashboard reads live incoming calls
def load_data():
    # Read the live SQLite database every time the app reloads
    conn = sqlite3.connect(DATA_PATH)
    df = pd.read_sql_query("SELECT * FROM incidents", conn)
    conn.close()
    return df

df = load_data()

# ── Train model ──────────────────────────────────────
# Caching the model is safe because Streamlit will automatically 
# retrain it if it detects that the 'df' variable has new rows!
@st.cache_resource
def get_model(df):
    return train_model(df)

model, encoders, scores = get_model(df)

# ── Sidebar filters ──────────────────────────────────
fdf = render_sidebar(df)

# ── Stats row ────────────────────────────────────────
render_stats(fdf)

# ── View selector ────────────────────────────────────
view = st.radio(
    "Select View",
    ["📍 Incident Map", "🌡️ Heatmap", "📊 Data Table", "🔮 Hotspot Predictor"],
    horizontal=True,
    key="main_view"
)

# ── Incident Map ─────────────────────────────────────
if view == "📍 Incident Map":
    m = build_incident_map(fdf)
    st_folium(m, use_container_width=True, height=580, returned_objects=[])

# ── Heatmap ──────────────────────────────────────────
elif view == "🌡️ Heatmap":
    m = build_heatmap(fdf)
    st_folium(m, use_container_width=True, height=580, returned_objects=[])
    st.caption("🔴 Red = highest conflict density · 🔵 Blue = low density")

# ── Data Table ───────────────────────────────────────
elif view == "📊 Data Table":
    st.markdown(f"### Showing {len(fdf)} incidents")
    st.dataframe(
        fdf[["date", "village", "animal", "incident", "severity"]]
        .sort_values("date", ascending=False)
        .reset_index(drop=True),
        use_container_width=True,
        height=500
    )

# ── Hotspot Predictor ────────────────────────────────
elif view == "🔮 Hotspot Predictor":
    st.subheader("🔮 Predicted Conflict Hotspots")
    st.caption("Random Forest model trained on historical incident data")

    # Model accuracy info
    with st.expander("📊 Model accuracy"):
        a1, a2, a3 = st.columns(3)
        a1.metric("Training accuracy", f"{scores['train_acc']}%")
        a2.metric("Test accuracy",     f"{scores['test_acc']}%")
        a3.metric("Cross-val accuracy",f"{scores['cv_acc']}%")

    st.markdown("### Predict next likely conflict")
    col1, col2 = st.columns(2)

    with col1:
        pred_month    = st.slider("Month", 1, 12, 6, key="ml_month")
        pred_season   = st.selectbox("Season",
            ["Summer", "Monsoon", "Winter", "Spring"], key="ml_season")
        pred_severity = st.selectbox("Expected severity",
            ["Low", "Medium", "High"], key="ml_severity")

    with col2:
        # THE FIX: Added .dropna().astype(str) to the village list
        valid_villages = sorted(df["village"].dropna().astype(str).unique())
        
        pred_village = st.selectbox("Village", valid_villages, key="ml_village")
        pred_lat = df[df["village"] == pred_village]["lat"].mean()
        pred_lon = df[df["village"] == pred_village]["lon"].mean()
        st.info(f"📍 Location: {round(pred_lat, 4)}, {round(pred_lon, 4)}")
    
    # Run prediction
    pred_animal, confidence, all_probas = predict(
        model, encoders,
        pred_village, pred_month, pred_season, pred_severity,
        pred_lat, pred_lon
    )

    # Result
    st.markdown("---")
    st.markdown(
        f"### Prediction: {EMOJI_MAP.get(pred_animal, '')} {pred_animal}"
    )
    st.markdown(f"**Confidence: {confidence}%**")
    st.progress(int(confidence))

    # Per-animal probabilities
    st.markdown("#### Probability by animal")
    for animal, prob in all_probas:
        ca, cb = st.columns([2, 5])
        ca.write(f"{EMOJI_MAP.get(animal, '')} {animal}")
        cb.progress(int(prob))
        cb.caption(f"{prob}%")

    # Prediction map
    st.markdown("### Predicted hotspot location")
    village_history = fdf[fdf["village"] == pred_village]
    m_pred = build_prediction_map(
        pred_animal, pred_village, confidence,
        pred_lat, pred_lon,
        village_history, COLOR_MAP
    )
    st_folium(m_pred, use_container_width=True,
              height=450, returned_objects=[])

    # Feature importance
    st.markdown("### What drives conflict predictions?")
    features = ["Latitude", "Longitude", "Month", "Day of week",
                "Season", "Village", "Severity"]
    imp_df = pd.DataFrame({
        "Feature":    features,
        "Importance": [round(i * 100, 1)
                       for i in model.feature_importances_]
    }).sort_values("Importance", ascending=False)

    for _, row in imp_df.iterrows():
        c1, c2 = st.columns([2, 5])
        c1.write(row["Feature"])
        c2.progress(int(row["Importance"]))
        c2.caption(f"{row['Importance']}%")