import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(layout="wide", page_title="Italy Bluefin Tuna Landings")

# Path to your file
FILE_PATH = "data/pescaTonnoRosso/pescaTonnoRosso.csv"

# --- 2. DATA LOADING ---
@st.cache_data
def load_data(path):
    if not os.path.exists(path):
        st.error(f"Data file not found at: {path}")
        st.stop()
    
    df = pd.read_csv(path)
    df['data_cattura'] = pd.to_datetime(df['data_cattura'])
    # Force year to string for a clean categorical X-axis
    df['year'] = df['data_cattura'].dt.year.astype(str)
    return df

# --- 3. DATA PROCESSING ---
try:
    df = load_data(FILE_PATH)

    # Annual national totals for share calculation
    annual_totals = df.groupby('year')['peso_kg'].sum().reset_index(name='total_kg')
    
    # Regional annual stats
    reg_annual = df.groupby(['year', 'regione']).agg(
        weight=('peso_kg', 'sum'),
        count=('peso_kg', 'count'),
        avg_weight=('peso_kg', 'mean')
    ).reset_index()
    
    # Merge for Quota Share
    stats = reg_annual.merge(annual_totals, on='year')
    stats['share_pct'] = (stats['weight'] / stats['total_kg']) * 100

    # Overall All-Time Share
    reg_overall = df.groupby('regione')['peso_kg'].sum().reset_index()
    total_sum = reg_overall['peso_kg'].sum()
    reg_overall['share_pct'] = (reg_overall['peso_kg'] / total_sum) * 100
    reg_overall = reg_overall.sort_values('peso_kg', ascending=False)

    region_rank = reg_overall['regione'].tolist()
    years_sorted = sorted(df['year'].unique().tolist())

    # --- 4. DASHBOARD UI ---
    st.title("Italy Bluefin Tuna Recreational Landings Dashboard")
    st.markdown("---")

    # KPI Summary Row
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Landings (kg)", f"{df['peso_kg'].sum():,.0f}")
    c2.metric("Total Specimens", f"{len(df):,}")
    c3.metric("Avg Weight/Specimen", f"{df['peso_kg'].mean():.1f} kg")
    c4.metric("Active Regions", df['regione'].nunique())

    # --- TIPS SECTION ---
    with st.expander("💡 Pro Tips for Chart Interaction"):
        st.markdown("""
        * **Single Click on Legend:** Hides/shows a specific year or region.
        * **Double Click on Legend:** Isolates that specific year or region.
        * **Click and Drag:** Zooms into a specific area of the graph.
        * **Double Click on Graph:** Resets the zoom level.
        * **Camera Icon (Modebar):** Hover over the top-right of any chart to download it as a PNG image.
        """)
    
    [Image of the Plotly modebar with the camera icon highlighted]

    # --- CHART 1: Overall Market Share (Donut) ---
    st.subheader("All-Time Regional Share of Landings")
    fig_pie = px.pie(
        reg_overall, values='peso_kg', names='regione', hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Prism,
        labels={"peso_kg": "Weight (kg)", "regione": "Region"}
    )
    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig_pie, use_container_width=True)

    # --- CHART 2: Performance Comparison (Toggle) ---
    st.subheader("Regional Performance Analysis")
    metric = st.radio(
        "Select metric:", 
        ["Total Weight (kg)", "Number of Landings"], 
        horizontal=True
    )
    
    y_col = "weight" if metric == "Total Weight (kg)" else "count"
    y_label = "Weight (kg)" if metric == "Total Weight (kg)" else "Number of Landings"

    fig_bar = px.bar(
        stats, x="regione", y=y_col, color="year", barmode="group",
        category_orders={"regione": region_rank, "year": years_sorted},
        labels={y_col: y_label, "regione": "Region", "year": "Year"}
    )
    st.plotly_chart(fig_bar, use_container
