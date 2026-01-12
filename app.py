import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 1. PAGE CONFIGURATION
st.set_page_config(layout="wide", page_title="Italy Bluefin Tuna Landings")

# Exact path based on your GitHub structure
FILE_PATH = "data/pescaTonnoRosso/pescaTonnoRosso.csv"

# 2. DATA LOADING
@st.cache_data
def load_data(path):
    if not os.path.exists(path):
        st.error(f"File not found at: {path}")
        st.stop()
    df = pd.read_csv(path)
    df['data_cattura'] = pd.to_datetime(df['data_cattura'])
    # Force year to string for categorical axis (removes the .5 decimals)
    df['year'] = df['data_cattura'].dt.year.astype(str)
    return df

# 3. DASHBOARD LOGIC
try:
    df = load_data(FILE_PATH)

    # Calculate overall stats
    total_weight = df['peso_kg'].sum()
    total_count = len(df)
    national_avg = df['peso_kg'].mean()

    # Pre-calculate data for charts
    reg_annual = df.groupby(['year', 'regione']).agg(
        weight=('peso_kg', 'sum'),
        count=('peso_kg', 'count'),
        avg_weight=('peso_kg', 'mean')
    ).reset_index()

    # Total historical weight per region for ranking
    reg_overall = df.groupby('regione')['peso_kg'].sum().reset_index()
    reg_overall = reg_overall.sort_values('peso_kg', ascending=False)
    region_rank = reg_overall['regione'].tolist()

    # UI: TITLE AND KPIs
    st.title("Italy Bluefin Tuna Recreational Landings Dashboard")
    st.markdown("---")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Weight", f"{total_weight:,.0f} kg")
    col2.metric("Total Landings", f"{total_count:,}")
    col3.metric("Avg Weight", f"{national_avg:.1f} kg")
    col4.metric("Active Regions", len(region_rank))

    # INTERACTIVE TIPS
    with st.expander("💡 Pro Tips for Chart Interaction"):
        st.markdown("""
        * **Single Click on Legend:** Hides/shows a specific year or region.
        * **Double Click on Legend:** Isolates that year or region.
        * **Click and Drag:** Zooms into a specific area.
        * **Double Click on Chart:** Resets zoom level.
        * **Modebar (Top Right):** Hover over a chart to see the Camera icon for PNG download.
        """)

    # CHART 1: OVERALL SHARE (DONUT)
    st.subheader("All-Time Regional Share of Landings")
    fig_donut = px.pie(
        reg_overall, values='peso_kg', names='regione', hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Prism,
        labels={"peso_kg": "Weight (kg)", "regione": "Region"}
    )
    fig_donut.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig_donut, use_container_width=True)

    # CHART 2: REGIONAL PERFORMANCE (TOGGLE)
    st.subheader("Regional Performance Comparison")
    metric_choice = st.radio(
        "Select metric to display:",
        ["Total Weight (kg)", "Number of Landings"],
        horizontal=True
    )

    y_val = 'weight' if metric_choice == "Total Weight (kg)" else 'count'
    y_label = "Weight (kg)" if metric_choice == "Total Weight (kg)" else "Number of Landings"

    fig_bar = px.bar(
        reg_annual, x="regione", y=y_val, color="year", barmode="group",
        category_orders={"regione": region_rank, "year": sorted(df['year'].unique())},
        labels={y_val: y_label, "regione": "Region", "year": "Year"}
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    # CHART 3: AVERAGE WEIGHT (WITH REFERENCE LINE)
    st.subheader("Average Landing Weight (kg) per Region")
    fig_avg = px.bar(
        reg_annual, x="regione", y="avg_weight", color="year", barmode="group",
        category_orders={"regione": region_rank, "year": sorted(df['year'].unique())},
        labels={"avg_weight": "Avg Weight (kg)", "regione": "Region", "year": "Year"}
    )
    fig_avg.add_hline(
        y=national_avg, line_dash="dash", line_color="red",
        annotation_text=f"National Avg: {national_avg:.1f}kg"
    )
    st.plotly_chart(fig_avg, use_container_width=True)

    # FOOTER
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: grey;'>Dashboard developed by: <b>Matteo Mannini</b></div>",
        unsafe_allow_html=True
    )

except Exception as e:
    st.error(f"Critical error: {e}")
