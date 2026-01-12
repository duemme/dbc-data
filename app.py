import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(layout="wide", page_title="Italy Bluefin Tuna Landings")

# Data path based on the repository structure
FILE_PATH = "data/pescaTonnoRosso/pescaTonnoRosso.csv"

# --- 2. DATA LOADING ---
@st.cache_data
def load_data(path):
    if not os.path.exists(path):
        st.error(f"Data file not found at: {path}")
        st.stop()
        
    df = pd.read_csv(path)
    df['data_cattura'] = pd.to_datetime(df['data_cattura'])
    # Force year to string for categorical axis
    df['year'] = df['data_cattura'].dt.year.astype(str) 
    return df

# --- 3. DATA PROCESSING ---
try:
    df = load_data(FILE_PATH)

    # Annual calculations
    annual_totals = df.groupby('year')['peso_kg'].sum().reset_index(name='total_kg')
    reg_annual = df.groupby(['year', 'regione']).agg(
        weight=('peso_kg', 'sum'),
        count=('peso_kg', 'count'),
        avg_weight=('peso_kg', 'mean')
    ).reset_index()
    stats = reg_annual.merge(annual_totals, on='year')
    stats['share_pct'] = (stats['weight'] / stats['total_kg']) * 100

    # Overall calculation (All-time share)
    reg_overall = df.groupby('regione')['peso_kg'].sum().reset_index()
    total_all_time = reg_overall['peso_kg'].sum()
    reg_overall['share_pct'] = (reg_overall['peso_kg'] / total_all_time) * 100
    reg_overall = reg_overall.sort_values('peso_kg', ascending=False)

    region_rank = reg_overall['regione'].tolist()
    years_sorted = sorted(df['year'].unique().tolist())

    # --- 4. DASHBOARD UI ---
    st.title("Italy Bluefin Tuna Recreational Landings Dashboard")
    st.markdown("---")

    # KPI Summary Indicators
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Landings (kg)", f"{df['peso_kg'].sum():,.0f}")
    col2.metric("Total Specimens", f"{len(df):,}")
    col3.metric("Avg Weight per Specimen", f"{df['peso_kg'].mean():.1f} kg")
    col4.metric("Active Regions", df['regione'].nunique())

    # --- TIPS SECTION ---
    with st.expander("💡 Pro Tips for Chart Interaction"):
        st.markdown("""
        * **Single Click on Legend:** Hides or shows a specific year or region.
        * **Double Click on Legend:** Isolates that specific year or region, hiding all others.
        * **Click and Drag:** Zooms into a specific area of the graph.
        * **Double Click on Graph:** Resets the zoom level to the original view.
        * **Hover:** View exact data points (kg, count, or percentages) in the tooltip.
        * **Modebar (Top Right):** Hover over the top of any chart to find the camera icon to download the chart as a PNG.
        """)

    # --- CHART 1: Overall Market Share ---
    st.subheader("All-Time Regional Share of Landings")
    st.markdown("This chart represents the total historical contribution of each region to the national landings.")
    
    fig_overall = px.pie(
        reg_overall, 
        values='peso_kg', 
        names='regione',
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Prism,
        labels={"peso_kg": "Total Weight (kg)", "regione": "Region"}
    )
    fig_overall.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig_overall, use_container_width=True)

    # --- CHART 2: Regional Performance (Toggle) ---
    st.subheader("Regional Performance Analysis")
    metric_choice = st.radio(
        "Select metric for the chart below:",
        ["Total Weight (kg)", "Number of Landings"],
        horizontal=True
