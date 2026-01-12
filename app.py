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
    # Force year to string for categorical axis
    df['year'] = df['data_cattura'].dt.year.astype(str) 
    return df

# --- 3. MAIN LOGIC ---
try:
    df = load_data(FILE_PATH)

    # Pre-calculate Metrics
    annual_totals = df.groupby('year')['peso_kg'].sum().reset_index(name='total_kg')
    
    # Aggregating by year and region for Sum, Count, and Mean
    reg_annual = df.groupby(['year', 'regione']).agg(
        weight=('peso_kg', 'sum'),
        count=('peso_kg', 'count'),
        avg_weight=('peso_kg', 'mean')
    ).reset_index()
    
    # Merge for percentage calculation
    stats = reg_annual.merge(annual_totals, on='year')
    stats['share_pct'] = (stats['weight'] / stats['total_kg']) * 100

    # Sort regions by total historical weight for consistent ranking
    region_rank = df.groupby('regione')['peso_kg'].sum().sort_values(ascending=False).index.tolist()
    years_sorted = sorted(df['year'].unique().tolist())

    # --- 4. DASHBOARD UI ---
    st.title("Italy Bluefin Tuna Recreational Landings Dashboard")
    st.markdown("---")

    # KPI Summary Row
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Landings (kg)", f"{df['peso_kg'].sum():,.0f}")
    col2.metric("Total Specimens", f"{len(df):,}")
    col3.metric("Avg Weight per Specimen", f"{df['peso_kg'].mean():.1f} kg")
    col4.metric("Active Regions", df['regione'].nunique())

    # --- CHART 1: Regional Volume/Landings (Toggleable) ---
    st.subheader("Regional Performance Analysis")
    metric_choice = st.radio(
        "Select metric for first chart:",
        ["Total Weight (kg)", "Number of Landings"],
        horizontal=True
    )
    
    if metric_choice == "Total Weight (kg)":
        selected_y, y_label = "weight", "Weight (kg)"
    else:
        selected_y, y_label = "count", "Number of Landings"

    fig1 = px.bar(
        stats, x="regione", y=selected_y, color="year", barmode="group",
        category_orders={"regione": region_rank, "year": years_sorted},
        labels={selected_y: y_label, "regione": "Region", "year": "Year"}
    )
    st.plotly_chart(fig1, use_container_width=True)

    # --- CHART 2: Average Weight per Region ---
    st.subheader("Average Landing Weight (kg) per Region")
    st.markdown("This chart reveals regional variations in the typical size of specimens landed.")
    
    fig_avg = px.bar(
        stats, x="regione", y="avg_weight", color="year", barmode="group",
        category_orders={"regione": region_rank, "year": years_sorted},
        labels={"avg_weight": "Average Weight (kg)", "regione": "Region", "year": "Year"}
    )
    # Add a horizontal line for the national average for reference
    fig_avg.add_hline(y=df['peso_kg'].mean(), line_dash="dash", line_color="red", 
                      annotation_text=f"National Avg: {df['peso_kg'].
