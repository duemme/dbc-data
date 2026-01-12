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
    # Force year to string to ensure categorical X-axis (no decimals like 2024.5)
    df['year'] = df['data_cattura'].dt.year.astype(str) 
    return df

# --- 3. DATA PROCESSING ---
try:
    df = load_data(FILE_PATH)

    # Calculate Annual National Totals
    annual_totals = df.groupby('year')['peso_kg'].sum().reset_index(name='total_kg')
    
    # Aggregate by Year and Region (Sum, Count, and Mean)
    reg_annual = df.groupby(['year', 'regione']).agg(
        weight=('peso_kg', 'sum'),
        count=('peso_kg', 'count'),
        avg_weight=('peso_kg', 'mean')
    ).reset_index()
    
    # Merge for Quota Share calculations
    stats = reg_annual.merge(annual_totals, on='year')
    stats['share_pct'] = (stats['weight'] / stats['total_kg']) * 100

    # Sort regions by total historical weight for consistent ranking
    region_rank = df.groupby('regione')['peso_kg'].sum().sort_values(ascending=False).index.tolist()
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

    # --- CHART 1: Regional Volume / Landings Count Toggle ---
    st.subheader("Regional Performance Analysis")
    metric_choice = st.radio(
        "Select metric for the chart below:",
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
    st.markdown("This chart analyzes the average size of specimens landed in each region relative to the national average.")
    
    fig_avg = px.bar(
        stats, x="regione", y="avg_weight", color="year", barmode="group",
        category_orders={"regione": region_rank, "year": years_sorted},
        labels={"avg_weight": "Average Weight (kg)", "regione": "Region", "year": "Year"}
    )
    
    # Add National Average Reference Line
    national_avg = df['peso_kg'].mean()
    fig_avg.add_hline(
        y=national_avg, 
        line_dash="dash", 
        line_color="red", 
        annotation_text=f"National Avg: {national_avg:.1f}kg"
    )
    
    st.plotly_chart(fig_avg, use_container_width=True)

    # --- CHART 3: Regional Quota Share (%) ---
    st.subheader("Regional Share of Annual Landings (%)")
    st.markdown("Distribution of the total annual recreational catch across regions.")
    
    fig2 = px.bar(
        stats, x="year", y="share_pct", color="regione", barmode="stack",
        category_orders={"regione": region_rank},
        labels={"share_pct": "Share of Annual Total (%)", "year": "Year", "regione": "Region"}
    )
    fig2.update_xaxes(type='category')
    fig2.update_layout(yaxis_range=[0, 100])
    st.plotly_chart(fig2, use_container_width=True)

except Exception as e:
    st.error(f"An unexpected error occurred: {e}")
