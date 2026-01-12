import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- 1. GLOBAL SETTINGS ---
st.set_page_config(layout="wide", page_title="Italy Bluefin Tuna Landings")

# Path based on your repository structure
FILE_PATH = "data/pescaTonnoRosso/pescaTonnoRosso.csv"

# --- 2. DATA LOADING ---
@st.cache_data
def load_data(path):
    if not os.path.exists(path):
        st.error(f"File not found at: {path}")
        st.stop()
        
    df = pd.read_csv(path)
    df['data_cattura'] = pd.to_datetime(df['data_cattura'])
    # Force year to string to ensure categorical axis (no decimals)
    df['year'] = df['data_cattura'].dt.year.astype(str) 
    return df

# --- 3. MAIN LOGIC ---
try:
    df = load_data(FILE_PATH)

    # Pre-calculate both Weight and Count for the regions
    annual_totals = df.groupby('year')['peso_kg'].sum().reset_index(name='total_kg')
    
    # Aggregating by year and region for both sum (weight) and count (landings)
    reg_annual = df.groupby(['year', 'regione']).agg(
        weight=('peso_kg', 'sum'),
        count=('peso_kg', 'count')
    ).reset_index()
    
    # Merge for the percentage calculation
    stats = reg_annual.merge(annual_totals, on='year')
    stats['share_pct'] = (stats['weight'] / stats['total_kg']) * 100

    # Sort regions by total weight for a consistent ranking
    region_rank = df.groupby('regione')['peso_kg'].sum().sort_values(ascending=False).index.tolist()

    # --- 4. DASHBOARD UI ---
    st.title("Italy Bluefin Tuna Recreational Landings Dashboard")
    st.markdown("---")

    # KPI Summary Row
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Landings (kg)", f"{df['peso_kg'].sum():,.0f}")
    col2.metric("Total Specimens", f"{len(df):,}")
    col3.metric("Avg Weight per Specimen", f"{df['peso_kg'].mean():.1f} kg")
    col4.metric("Active Regions", df['regione'].nunique())

    # --- CHART 1: Regional Performance (Switchable Metric) ---
    st.subheader("Regional Performance Analysis")
    
    # Add a radio button to toggle between Weight and Count
    metric_choice = st.radio(
        "Select metric to display:",
        ["Total Weight (kg)", "Number of Landings"],
        horizontal=True
    )
    
    # Map selection to the correct dataframe column and label
    if metric_choice == "Total Weight (kg)":
        selected_y = "weight"
        y_axis_label = "Weight (kg)"
    else:
        selected_y = "count"
        y_axis_label = "Number of Landings"

    fig1 = px.bar(
        stats, 
        x="regione", 
        y=selected_y, 
        color="year", 
        barmode="group",
        category_orders={"regione": region_rank, "year": sorted(df['year'].unique().tolist())},
        labels={selected_y: y_axis_label, "regione": "Region", "year": "Year"}
    )
    st.plotly_chart(fig1, use_container_width=True)

    # --- CHART 2: Percentage Share of Annual Landings ---
    st.subheader("Regional Share of Annual Landings (%)")
    st.info("Each vertical bar represents 100% of the recreational landings for that specific year.")
    fig2 = px.bar(
        stats, 
        x="year", 
        y="share_pct", 
        color="regione", 
        barm
