import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(layout="wide", page_title="Tuna Catch Dashboard")

# 1. LOAD DATA WITH CORRECT FOLDER PATH
@st.cache_data
def load_data():
    # This matches your GitHub structure: data -> pescaTonnoRosso -> file
    path = "data/pescaTonnoRosso/pescaTonnoRosso.csv"
    
    if not os.path.exists(path):
        st.error(f"Cannot find file at {path}")
        st.stop()
        
    df = pd.read_csv(path)
    df['data_cattura'] = pd.to_datetime(df['data_cattura'])
    # Force year to string to avoid "2004.5" on the charts
    df['year'] = df['data_cattura'].dt.year.astype(str)
    return df

try:
    df = load_data()

    # 2. PRECISE CALCULATIONS (Verified Math)
    annual_totals = df.groupby('year')['peso_kg'].sum().reset_index(name='total_kg')
    reg_annual = df.groupby(['year', 'regione'])['peso_kg'].sum().reset_index()
    stats = reg_annual.merge(annual_totals, on='year')
    stats['share_pct'] = (stats['peso_kg'] / stats['total_kg']) * 100

    # 3. DASHBOARD UI
    st.title("🐟 Bluefin Tuna Recreational Dashboard")
    st.markdown(f"**Data Source:** `{os.path.basename(path)}` verified.")

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Weight (kg)", f"{df['peso_kg'].sum():,.0f}")
    col2.metric("Total Specimens", f"{len(df):,}")
    col3.metric("Avg Weight", f"{df['peso_kg'].mean():.1f} kg")

    # --- Chart 1: Absolute Weights ---
    st.subheader("Regional Performance (Total kg)")
    fig1 = px.bar(stats, x="regione", y="peso_kg", color="year", barmode="group",
                 category_orders={"year": sorted(df['year'].unique().tolist())})
    st.plotly_chart(fig1, use_container_width=True)

    # --- Chart 2: Percentage Share (Quota Slice) ---
    st.subheader("Regional Share of Annual Quota (%)")
    st.info("Each year adds up to exactly 100%.")
    fig2 = px.bar(stats, x="year", y="share_pct", color="regione", barmode="stack")
    fig2.update_layout(yaxis_title="Share (%)", yaxis_range=[0,100])
    st.plotly_chart(fig2, use_container_width=True)

    # --- Data Table for Verification ---
    with st.expander("View Raw Regional Totals"):
        st.dataframe(stats.sort_values(['year', 'peso_kg'], ascending=[False, False]))

except Exception as e:
    st.error(f"Critical Error: {e}")
