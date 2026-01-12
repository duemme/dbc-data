import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from datetime import datetime

# 1. PAGE CONFIGURATION
st.set_page_config(layout="wide", page_title="Italy Bluefin Tuna Landings - Enhanced", page_icon="🐟")

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 3.5rem;
        font-weight: bold;
        color: #0066cc;
        text-align: center;
        margin-bottom: 0.2rem;
        margin-top: 1rem;
    }
    .sub-header {
        text-align: center;
        color: #666;
        font-size: 1.3rem;
        margin-bottom: 2rem;
    }
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# Data path based on your repository structure
FILE_PATH = "data/pescaTonnoRosso/pescaTonnoRosso.csv"

# 2. DATA LOADING
@st.cache_data
def load_data(path):
    if not os.path.exists(path):
        st.error(f"Data file not found at: {path}")
        st.info("💡 Tip: Make sure the data file is in the correct directory structure.")
        st.stop()
    
    with st.spinner("Loading data..."):
        df = pd.read_csv(path)
        df['data_cattura'] = pd.to_datetime(df['data_cattura'])
        df['year'] = df['data_cattura'].dt.year
        df['month'] = df['data_cattura'].dt.month
        df['month_name'] = df['data_cattura'].dt.strftime('%B')
        df['year_month'] = df['data_cattura'].dt.to_period('M').astype(str)
        return df

# 3. DATA PROCESSING
try:
    df = load_data(FILE_PATH)
    
    # Sidebar filters
    st.sidebar.title("🎛️ Filters")
    
    years_available = sorted(df['year'].unique().tolist())
    regions_available = sorted(df['regione'].unique().tolist())
    
    selected_years = st.sidebar.multiselect(
        "Select Years",
        years_available,
        default=years_available,
        help="Filter data by year"
    )
    
    selected_regions = st.sidebar.multiselect(
        "Select Regions",
        regions_available,
        default=regions_available,
        help="Filter data by region"
    )
    
    # Apply filters
    if not selected_years or not selected_regions:
        st.warning("⚠️ Please select at least one year and one region to view the dashboard.")
        st.stop()
    
    df_filtered = df[df['year'].isin(selected_years) & df['regione'].isin(selected_regions)].copy()
    
    if len(df_filtered) == 0:
        st.warning("⚠️ No data available for the selected filters.")
        st.stop()
    
    # Calculate statistics
    # FAO zone common names mapping
    fao_zone_names = {
        '37.1.3': 'Ligurian Sea & Tyrrhenian Sea',
        '37.2.1': 'Adriatic Sea',
        '37.2.2': 'Ionian Sea'
    }
    df_filtered['fao_common'] = df_filtered['zona_FAO'].map(fao_zone_names).fillna(df_filtered['zona_FAO'])
    
    # All-time stats per region
    reg_overall = df_filtered.groupby('regione')['peso_kg'].sum().reset_index()
    total_all_time = reg_overall['peso_kg'].sum()
    reg_overall['share_pct'] = (reg_overall['peso_kg'] / total_all_time) * 100
    reg_overall = reg_overall.sort_values('peso_kg', ascending=False)
    region_rank = reg_overall['regione'].tolist()
    
    # Yearly stats per region
    annual_totals = df_filtered.groupby('year')['peso_kg'].sum().reset_index(name='total_kg')
    reg_annual = df_filtered.groupby(['year', 'regione']).agg(
        weight=('peso_kg', 'sum'),
        count=('peso_kg', 'count'),
        avg_weight=('peso_kg', 'mean')
    ).reset_index()
    
    # Merged stats for yearly shares
    stats = reg_annual.merge(annual_totals, on='year')
    stats['share_pct'] = (stats['weight'] / stats['total_kg']) * 100
    stats['year_str'] = stats['year'].astype(str)
    years_sorted = sorted(df_filtered['year'].unique().tolist())
    years_sorted_str = [str(y) for y in years_sorted]
    
    # Calculate YoY growth
    annual_totals_sorted = annual_totals.sort_values('year')
    annual_totals_sorted['yoy_growth'] = annual_totals_sorted['total_kg'].pct_change() * 100
    
    # 4. DASHBOARD UI
    st.markdown("<h1 style='text-align: center;'>Italy Bluefin Tuna Recreational Landings Dashboard</h1>", unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Comprehensive Analysis of Recreational Fishing Data</p>', unsafe_allow_html=True)
    st.markdown("---")
    
    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Weight", f"{total_all_time:,.0f} kg")
    with col2:
        st.metric("Total Landings", f"{len(df_filtered):,}")
    with col3:
        st.metric("Avg Weight/Specimen", f"{df_filtered['peso_kg'].mean():.1f} kg")
    with col4:
        st.metric("Active Regions", len(region_rank))
    
    # INTERACTIVE TIPS
    with st.expander("💡 Pro Tips for Chart Interaction"):
        st.markdown("""
        * **Single Click on Legend:** Hides/shows a specific year or region.
        * **Double Click on Legend:** Isolates that specific year or region.
        * **Click and Drag:** Zooms into an area. Double-click chart to reset.
        * **Modebar (Top Right):** Hover to find icons for pan, zoom, and download as PNG.
        * **Filters (Left Sidebar):** Use year and region filters to focus your analysis.
        """)
    
    st.markdown("---")
    
    # === TABS FOR BETTER ORGANIZATION ===
    tab1, tab2, tab3 = st.tabs([
        "📊 Overview", 
        "🗺️ Geographic Analysis",
        "📋 Data Explorer"
    ])
    
    # ========== TAB 1: OVERVIEW ==========
    with tab1:
        st.subheader("Regional Performance Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            metric_choice = st.radio(
                "Select metric for chart:",
                ["Total Weight (kg)", "Number of Landings"],
                horizontal=True
            )
        
        with col2:
            chart_type = st.radio(
                "Chart type:",
                ["Grouped", "Stacked"],
                horizontal=True
            )
        
        y_col = 'weight' if metric_choice == "Total Weight (kg)" else 'count'
        y_label = "Weight (kg)" if metric_choice == "Total Weight (kg)" else "Number of Landings"
        barmode = "group" if chart_type == "Grouped" else "stack"
        
        fig_perf = px.bar(
            stats, x="regione", y=y_col, color="year_str", barmode=barmode,
            category_orders={"regione": region_rank, "year_str": years_sorted_str},
            labels={y_col: y_label, "regione": "Region", "year_str": "Year"},
            title=f"{metric_choice} by Region and Year"
        )
        fig_perf.update_layout(height=500)
        st.plotly_chart(fig_perf, use_container_width=True)
        
        # Average Weight Chart
        st.subheader("Average Landing Weight (kg) per Region")
        fig_avg = px.bar(
            stats, x="regione", y="avg_weight", color="year_str", barmode="group",
            category_orders={"regione": region_rank, "year_str": years_sorted_str},
            labels={"avg_weight": "Avg Weight (kg)", "regione": "Region", "year_str": "Year"}
        )
        nat_avg = df_filtered['peso_kg'].mean()
        fig_avg.add_hline(
            y=nat_avg, line_dash="dash", line_color="red",
            annotation_text=f"Overall Avg: {nat_avg:.1f}kg"
        )
        fig_avg.update_layout(height=500)
        st.plotly_chart(fig_avg, use_container_width=True)
        
        # Distribution box plot
        st.subheader("Weight Distribution by Region")
        fig_box = px.box(
            df_filtered, x="regione", y="peso_kg",
            category_orders={"regione": region_rank},
            labels={"peso_kg": "Weight (kg)", "regione": "Region"},
            color="regione"
        )
        fig_box.update_layout(height=500, showlegend=False)
        st.plotly_chart(fig_box, use_container_width=True)
        
        # Pie chart
        st.markdown("### Regional Distribution")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Regional Share (by Weight)")
            # Add percentage column for proper display
            reg_overall_display = reg_overall.copy()
            reg_overall_display['percentage_text'] = reg_overall_display['share_pct'].round(1).astype(str) + '%'
            
            # Create pie chart with go.Pie for better control
            fig_pie = go.Figure(data=[go.Pie(
                labels=reg_overall_display['regione'],
                values=reg_overall_display['peso_kg'],
                hole=0.4,
                texttemplate='%{label}<br>%{text}',
                text=reg_overall_display['percentage_text'],
                textposition='inside',
                hovertemplate='<b>%{label}</b><br>Weight: %{value:,.0f} kg<br>Percentage: %{text}<extra></extra>',
                marker=dict(colors=px.colors.qualitative.Set3)
            )])
            
            fig_pie.update_layout(
                height=500,
                showlegend=True
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            st.subheader("Regional Share (by Count)")
            reg_count = df_filtered.groupby('regione').size().reset_index(name='count')
            total_count_val = reg_count['count'].sum()
            reg_count['percentage_text'] = ((reg_count['count'] / total_count_val) * 100).round(1).astype(str) + '%'
            
            fig_pie_count = go.Figure(data=[go.Pie(
                labels=reg_count['regione'],
                values=reg_count['count'],
                hole=0.4,
                texttemplate='%{label}<br>%{text}',
                text=reg_count['percentage_text'],
                textposition='inside',
                hovertemplate='<b>%{label}</b><br>Count: %{value:,}<br>Percentage: %{text}<extra></extra>',
                marker=dict(colors=px.colors.qualitative.Pastel)
            )])
            
            fig_pie_count.update_layout(
                height=500,
                showlegend=True
            )
            st.plotly_chart(fig_pie_count, use_container_width=True)
    
    # ========== TAB 2: GEOGRAPHIC ANALYSIS ==========
    with tab2:
        st.subheader("Geographic Distribution Analysis")
        
        # FAO Zone analysis
        st.markdown("### FAO Fishing Zones")
        
        fao_stats = df_filtered.groupby('fao_common').agg(
            total_weight=('peso_kg', 'sum'),
            total_count=('peso_kg', 'count'),
            avg_weight=('peso_kg', 'mean')
        ).reset_index().sort_values('total_weight', ascending=False)
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_fao = px.bar(
                fao_stats, x='fao_common', y='total_weight',
                labels={'fao_common': 'Fishing Zone', 'total_weight': 'Total Weight (kg)'},
                title="Total Catch by Fishing Zone",
                color='total_weight',
                color_continuous_scale='Blues'
            )
            fig_fao.update_layout(height=400)
            fig_fao.update_xaxes(tickangle=30)
            st.plotly_chart(fig_fao, use_container_width=True)
        
        with col2:
            fig_fao_count = px.bar(
                fao_stats, x='fao_common', y='total_count',
                labels={'fao_common': 'Fishing Zone', 'total_count': 'Number of Landings'},
                title="Number of Landings by Fishing Zone",
                color='total_count',
                color_continuous_scale='Greens'
            )
            fig_fao_count.update_layout(height=400)
            fig_fao_count.update_xaxes(tickangle=30)
            st.plotly_chart(fig_fao_count, use_container_width=True)
        
        # Region-FAO cross-analysis
        st.markdown("### Region × Fishing Zone Analysis")
        
        region_fao = df_filtered.groupby(['regione', 'fao_common'])['peso_kg'].sum().reset_index()
        
        fig_heatmap = px.density_heatmap(
            region_fao, x='fao_common', y='regione', z='peso_kg',
            labels={'peso_kg': 'Total Weight (kg)', 'regione': 'Region', 'fao_common': 'Fishing Zone'},
            title="Catch Distribution: Region vs Fishing Zone",
            color_continuous_scale='YlOrRd'
        )
        fig_heatmap.update_layout(height=500)
        st.plotly_chart(fig_heatmap, use_container_width=True)
        
        # Yearly contribution share
        st.markdown("### Yearly Contribution to National Total")
        st.markdown("This chart shows how the 100% of each year's landings were split among regions.")
        
        fig_share = px.bar(
            stats, x="year", y="share_pct", color="regione", barmode="stack",
            category_orders={"regione": region_rank},
            labels={"share_pct": "Share of Yearly Total (%)", "year": "Year", "regione": "Region"}
        )
        fig_share.update_xaxes(type='category')
        fig_share.update_layout(yaxis_range=[0, 100], height=500)
        st.plotly_chart(fig_share, use_container_width=True)
    
    # ========== TAB 3: DATA EXPLORER ==========
    with tab3:
        st.subheader("Data Explorer & Download")
        
        # Summary statistics
        st.markdown("### Summary Statistics")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**Weight Statistics**")
            st.write(df_filtered['peso_kg'].describe().round(2))
        
        with col2:
            st.markdown("**Regional Breakdown**")
            regional_counts = df_filtered['regione'].value_counts()
            st.write(regional_counts)
        
        with col3:
            st.markdown("**Yearly Breakdown**")
            yearly_summary = df_filtered.groupby('year').agg(
                count=('peso_kg', 'count'),
                total_kg=('peso_kg', 'sum')
            ).sort_index()
            yearly_summary['total_kg'] = yearly_summary['total_kg'].apply(lambda x: f"{x:,.0f} kg")
            st.write(yearly_summary)
        
        # Top catches
        st.markdown("### 🏆 Top 10 Largest Catches")
        top_catches = df_filtered.nlargest(10, 'peso_kg')[
            ['data_cattura', 'peso_kg', 'regione', 'zona_FAO', 'identificativo_natante']
        ].reset_index(drop=True)
        top_catches.index += 1
        st.dataframe(top_catches, use_container_width=True)
        
        # Raw data viewer
        st.markdown("### 📋 Raw Data Viewer")
        
        show_all = st.checkbox("Show all data (may be slow for large datasets)")
        
        if show_all:
            st.dataframe(df_filtered, use_container_width=True, height=400)
        else:
            st.dataframe(df_filtered.head(100), use_container_width=True, height=400)
            st.caption(f"Showing first 100 rows of {len(df_filtered)} total records. Check the box above to see all.")
        
        # Download section
        st.markdown("### 💾 Download Data")
        
        col1, col2 = st.columns(2)
        
        with col1:
            csv = df_filtered.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Filtered Data (CSV)",
                data=csv,
                file_name=f"tuna_landings_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        
        with col2:
            summary_csv = reg_overall.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Regional Summary (CSV)",
                data=summary_csv,
                file_name=f"regional_summary_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    # FOOTER
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: grey;'>
            <b>Enhanced Dashboard</b> | Developed by: <b>Matteo Mannini</b> | Enhanced with ❤️ by Claude
        </div>
        """,
        unsafe_allow_html=True
    )

except Exception as e:
    st.error(f"❌ Error encountered: {e}")
    st.exception(e)
