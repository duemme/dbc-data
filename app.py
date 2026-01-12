import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- 1. GLOBAL SETTINGS ---
st.set_page_config(layout="wide", page_title="Tuna Catch Dashboard")

# Define path globally so the whole app can see it
FILE_PATH = "data/pescaTonnoRosso/pescaTonnoRosso.csv"

# --- 2. DATA LOADING ---
@st.cache_data
def load_data(path):
    if not os.path.exists(path):
        # If the path is wrong, show a diagnostic to help the user
        st.error(f"File not found at: {path}")
        st.write("Current directory contents:", os.listdir("."))
        st.stop()
        
    df = pd.read_csv(path)
    # Ensure date is correct
    df['data_cattura'] = pd.to_datetime(df['data_cattura'])
    # Force year to string to prevent '2004.5' on the X-axis
    df['year'] = df['data_cattura'].dt.year.astype(str)
    return df

# --- 3. MAIN LOGIC ---
try:
    # Load the data using the global path
    df = load_data(FILE_PATH)

    # DYNAMIC MATH: Calculate shares and totals directly from the dataframe
    # This ensures 2021 (and every year) adds up to exactly 100%
    annual_totals = df.groupby('year')['peso_kg'].sum().reset_index(name='total_kg')
    reg_annual = df.groupby(['year', 'regione'])['peso_kg'].sum().reset_index()
    stats = reg_annual.merge(annual_totals, on='year')
    stats['share_pct'] = (stats['peso_kg'] / stats['total_kg']) * 100

    # Sort regions by total historical weight for a consistent ranking
    region_rank = df.groupby('regione')['peso_kg'].sum().sort_values(ascending=False).index.tolist()

    # --- 4. DASHBOARD UI ---
    st.title("🐟 Bluefin Tuna Recreational Dashboard")
    st.info(f"Connected to: `{FILE_PATH}`")

    # KPI Row
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Weight (kg)", f"{df['peso_kg'].sum():,.0f}")
    col2.metric("Total Specimens", f"{len(df):,}")
    col3.metric("Avg Weight", f"{df['peso_kg'].mean():.1f} kg")
    col4.metric("Active Regions", df['regione'].nunique())

    # --- CHART 1: Absolute Weights ---
    st.subheader("Regional Performance (Total kg)")
    fig1 = px.bar(
        stats, 
        x="regione", 
        y="peso_kg", 
        color="year", 
        barmode="group",
        category_orders={"regione": region_rank, "year": sorted(df['year'].unique().tolist())},
        labels={"peso_kg": "Weight (kg)", "regione": "Region", "year": "Year"}
    )
    st.plotly_chart(fig1, use_container_width=True)

    # --- CHART 2: Percentage Share ---
    st.subheader("Regional Share of Annual Quota (%)")
    st.write("Each vertical bar represents 100% of that year's recreational catch.")
    fig2 = px.bar(
        stats, 
        x="year", 
        y="share_pct", 
        color="regione", 
        barmode="stack",
        category_orders={"regione": region_rank},
        labels={"share_pct": "Share of Yearly Total (%)", "year": "Year", "regione": "Region"}
    )
    # Ensure axis is categorical (no decimals)
    fig2.update_xaxes(type='category')
    fig2.update_layout(yaxis_range=[0, 100])
    st.plotly_chart(fig2, use_container_width=True)

    # --- DATA EXPLORER ---
    with st.expander("Show Detailed Yearly Statistics"):
        st.dataframe(stats.sort_values(['year', 'peso_kg'], ascending=[False, False]), use_container_width=True)

except Exception as e:
    st.error(f"An unexpected error occurred: {e}")
