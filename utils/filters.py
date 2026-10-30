# Author: Krish Shukla
# Roll Number: 240101017
# Project: Wildlife Conflict Tracking System

import pandas as pd
import streamlit as st

def render_sidebar(df: pd.DataFrame) -> pd.DataFrame:
    """
    Render sidebar filters and return filtered dataframe.
    """
    st.sidebar.title("Filters")

    # 1. Force 'date' to datetime BEFORE calling .min().date()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # 2. Safety check: if the dataframe is completely empty, skip building filters
    if df.empty:
        st.sidebar.warning("No data available to filter.")
        return df

    # Date range filter
    min_date = df["date"].min().date()
    max_date = df["date"].max().date()
    
    date_range = st.sidebar.date_input(
        "Date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        key="filter_date"
    )

    # 3. THE FIX: Drop blank values (NaN) and convert to string before sorting
    valid_animals = sorted(df["animal"].dropna().astype(str).unique())

    # Animal type filter
    animals = st.sidebar.multiselect(
        "Animal type",
        options=valid_animals,
        default=valid_animals,
        key="filter_animal"
    )

    # Severity filter
    severities = st.sidebar.multiselect(
        "Severity",
        options=["Low", "Medium", "High"],
        default=["Low", "Medium", "High"],
        key="filter_severity"
    )

    # Apply all filters to the dataframe
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date = pd.to_datetime(date_range[0])
        end_date = pd.to_datetime(date_range[1])
        
        filtered = df[
            (df["date"] >= start_date) &
            (df["date"] <= end_date) &
            (df["animal"].isin(animals)) &
            (df["severity"].isin(severities))
        ]
    else:
        # Fallback if the date range isn't fully selected yet
        filtered = df[
            (df["animal"].isin(animals)) &
            (df["severity"].isin(severities))
        ]

    return filtered


def render_stats(df: pd.DataFrame):
    """Render top-level metric cards."""
    # Safety check so the metric cards don't crash on an empty filtered view
    if df.empty:
        st.info("No incidents match the current filters.")
        return

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total",        len(df))
    c2.metric("Tigers",       len(df[df["animal"] == "Tiger"]))
    c3.metric("Leopards",     len(df[df["animal"] == "Leopard"]))
    c4.metric("Elephants",    len(df[df["animal"] == "Elephant"]))
    c5.metric("Sloth Bears",  len(df[df["animal"] == "Sloth Bear"]))