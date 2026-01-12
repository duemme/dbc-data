import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 1. PAGE CONFIGURATION
st.set_page_config(layout="wide", page_title="Italy Bluefin Tuna Landings")

# Data path based on your repository structure
FILE_PATH = "data/pescaTonnoRosso/pescaTonnoRosso.csv"

# 2. DATA LOADING
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

# 3. DATA PROCESSING
try:
    df = load_data(FILE_PATH)

    # All-time stats per region
    reg_overall = df.groupby('regione')['peso_kg'].sum().reset_index()
    total_all_time = reg_overall['peso_kg'].sum()
    reg_overall['share_pct'] = (reg_overall['peso_kg'] / total_all_time) * 100
    reg_overall = reg_overall.sort_values('peso_kg', ascending=False)
    region_rank = reg_overall['regione'].tolist()

    # Yearly stats per region
    annual_totals = df.groupby('year')['peso_kg'].sum().reset_index(name='total_kg')
    reg_annual = df.groupby(['year', 'regione']).agg(
        weight=('peso_kg', 'sum'),
        count=('peso_kg', 'count'),
        avg_weight=('peso_kg', 'mean')
    ).reset_index()
    
    # Merged stats for yearly shares
    stats = reg_annual.merge(annual_totals, on='year')
    stats['share_pct'] = (stats['weight'] / stats['total_kg']) * 100
    years_sorted = sorted(df['year'].unique().tolist())

    # 4. DASHBOARD UI
    st.title("Italy Bluefin Tuna Recreational Landings Dashboard")
    st.markdown("---")

    # KPIs
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Weight", f"{total_all_time:,.0f} kg")
    c2.metric("Total Landings", f"{len(df):,}")
    c3.metric("Avg Weight/Specimen", f"{df['peso_kg'].mean():.1f} kg")
    c4.metric("Active Regions", len(region_rank))

    # INTERACTIVE TIPS
    with st.expander("💡 Pro Tips for Chart Interaction"):
        st.markdown("""
        * **Single Click on Legend:** Hides/shows a specific year or region.
        * **Double Click on Legend:** Isolates that specific year or region.
        * **Click and Drag:** Zooms into a area. Double-click chart to reset.
        * **Modebar (Top Right):** Hover to find the camera icon to save as PNG.
        """)

    # CHART 1: ALL-TIME SHARE
    st.subheader("All-Time Regional Share of Landings")
    fig_pie = px.pie(
        reg_overall, values='peso_kg', names='regione', hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Prism,
        labels={"peso_kg": "Total Weight (kg)", "regione": "Region"}
    )
    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig_pie, use_container_width=True)

    # CHART 2: REGIONAL PERFORMANCE (TOGGLE)
    st.subheader("Regional Performance Comparison")
    metric_choice = st.radio(
        "Select metric for chart below:",
        ["Total Weight (kg)", "Number of Landings"],
        horizontal=True
    )
    y_col = 'weight' if metric_choice == "Total Weight (kg)" else 'count'
    y_label = "Weight (kg)" if metric_choice == "Total Weight (kg)" else "Number of Landings"

    fig_perf = px.bar(
        stats, x="regione", y=y_col, color="year", barmode="group",
        category_orders={"regione": region_rank, "year": years_sorted},
        labels={y_col: y_label, "regione": "Region", "year": "Year"}
    )
    st.plotly_chart(fig_perf, use_container_width=True)

    # CHART 3: AVERAGE WEIGHT (WITH LINE)
    st.subheader("Average Landing Weight (kg) per Region")
    fig_avg = px.bar(
        stats, x="regione", y="avg_weight", color="year", barmode="group",
        category_orders={"regione": region_rank, "year": years_sorted},
        labels={"avg_weight": "Avg Weight (kg)", "regione": "Region", "year": "Year"}
    )
    nat_avg = df['peso_kg'].mean()
    fig_avg.add_hline(
        y=nat_avg, line_dash="dash", line_color="red",
        annotation_text=f"National Avg: {nat_avg:.1f}kg"
    )
    st.plotly_chart(fig_avg, use_container_width=True)

    # CHART 4: YEARLY CONTRIBUTION SHARE
    st.subheader("Yearly Contribution to National Total (%)")
    st.markdown("This chart shows how the 100% of each year's landings were split among regions.")
    fig_share = px.bar(
        stats, x="year", y="share_pct", color="regione", barmode="stack",
        category_orders={"regione": region_rank},
        labels={"share_pct": "Share of Yearly Total (%)", "year": "Year", "regione": "Region"}
    )
    fig_share.update_xaxes(type='category')
    fig_share.update_layout(yaxis_range=[0, 100])
    st.plotly_chart(fig_share, use_container_width=True)

    # FOOTER
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: grey;'>Dashboard developed by: <b>Matteo Mannini</b></div>",
        unsafe_allow_html=True
    )

except Exception as e:
    st.error(f"Error encountered: {e}")
