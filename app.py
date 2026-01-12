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
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        text-align: center;
        color: #666;
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
    st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2965/2965414.png", width=100)
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
    st.markdown('<p class="main-header">🐟 Italy Bluefin Tuna Recreational Landings Dashboard</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Comprehensive Analysis of Recreational Fishing Data</p>', unsafe_allow_html=True)
    st.markdown("---")
    
    # KPIs
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total Weight", f"{total_all_time:,.0f} kg")
    with col2:
        st.metric("Total Landings", f"{len(df_filtered):,}")
    with col3:
        st.metric("Avg Weight/Specimen", f"{df_filtered['peso_kg'].mean():.1f} kg")
    with col4:
        st.metric("Active Regions", len(region_rank))
    with col5:
        if len(annual_totals_sorted) > 1 and not pd.isna(annual_totals_sorted['yoy_growth'].iloc[-1]):
            latest_growth = annual_totals_sorted['yoy_growth'].iloc[-1]
            st.metric("Latest YoY Growth", f"{latest_growth:+.1f}%", delta=f"{latest_growth:.1f}%")
        else:
            st.metric("Latest YoY Growth", "N/A")
    
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
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Overview", 
        "📈 Time Series", 
        "🗺️ Geographic Analysis",
        "📅 Seasonality",
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
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Regional Share (by Weight)")
            fig_pie = px.pie(
                reg_overall, values='peso_kg', names='regione', hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Set3,
                labels={"peso_kg": "Total Weight (kg)", "regione": "Region"}
            )
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            fig_pie.update_layout(height=500)
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            st.subheader("Regional Share (by Count)")
            reg_count = df_filtered.groupby('regione').size().reset_index(name='count')
            fig_pie_count = px.pie(
                reg_count, values='count', names='regione', hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Pastel,
                labels={"count": "Number of Landings", "regione": "Region"}
            )
            fig_pie_count.update_traces(textposition='inside', textinfo='percent+label')
            fig_pie_count.update_layout(height=500)
            st.plotly_chart(fig_pie_count, use_container_width=True)
    
    # ========== TAB 2: TIME SERIES ==========
    with tab2:
        st.subheader("Trends Over Time")
        
        # Monthly aggregation
        monthly_data = df_filtered.groupby(['year_month', 'year', 'month']).agg(
            total_weight=('peso_kg', 'sum'),
            total_count=('peso_kg', 'count'),
            avg_weight=('peso_kg', 'mean')
        ).reset_index().sort_values('year_month')
        
        # Time series selector
        ts_metric = st.selectbox(
            "Select metric to visualize over time:",
            ["Total Weight (kg)", "Number of Landings", "Average Weight (kg)"]
        )
        
        if ts_metric == "Total Weight (kg)":
            y_col_ts = 'total_weight'
            y_label_ts = 'Total Weight (kg)'
        elif ts_metric == "Number of Landings":
            y_col_ts = 'total_count'
            y_label_ts = 'Number of Landings'
        else:
            y_col_ts = 'avg_weight'
            y_label_ts = 'Average Weight (kg)'
        
        fig_ts = px.line(
            monthly_data, x='year_month', y=y_col_ts,
            markers=True,
            labels={'year_month': 'Month', y_col_ts: y_label_ts},
            title=f"{ts_metric} - Monthly Trend"
        )
        fig_ts.update_xaxes(tickangle=45)
        fig_ts.update_layout(height=500)
        st.plotly_chart(fig_ts, use_container_width=True)
        
        # Regional time series
        st.subheader("Regional Trends Over Time")
        
        top_n = st.slider("Show top N regions by total weight:", 3, len(region_rank), min(5, len(region_rank)))
        top_regions = region_rank[:top_n]
        
        monthly_regional = df_filtered[df_filtered['regione'].isin(top_regions)].groupby(
            ['year_month', 'regione']
        )['peso_kg'].sum().reset_index()
        
        fig_ts_reg = px.line(
            monthly_regional, x='year_month', y='peso_kg', color='regione',
            markers=True,
            labels={'year_month': 'Month', 'peso_kg': 'Total Weight (kg)', 'regione': 'Region'},
            title=f"Top {top_n} Regions - Monthly Weight Trends"
        )
        fig_ts_reg.update_xaxes(tickangle=45)
        fig_ts_reg.update_layout(height=500)
        st.plotly_chart(fig_ts_reg, use_container_width=True)
        
        # Year over Year comparison
        st.subheader("Year-over-Year Comparison")
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_yoy = go.Figure()
            fig_yoy.add_trace(go.Bar(
                x=annual_totals_sorted['year'],
                y=annual_totals_sorted['total_kg'],
                name='Total Weight',
                marker_color='steelblue'
            ))
            fig_yoy.update_layout(
                title="Total Annual Landings (kg)",
                xaxis_title="Year",
                yaxis_title="Weight (kg)",
                height=400
            )
            st.plotly_chart(fig_yoy, use_container_width=True)
        
        with col2:
            if len(annual_totals_sorted) > 1:
                fig_growth = go.Figure()
                fig_growth.add_trace(go.Bar(
                    x=annual_totals_sorted['year'].iloc[1:],
                    y=annual_totals_sorted['yoy_growth'].iloc[1:],
                    marker_color=annual_totals_sorted['yoy_growth'].iloc[1:].apply(
                        lambda x: 'green' if x > 0 else 'red'
                    )
                ))
                fig_growth.update_layout(
                    title="Year-over-Year Growth Rate (%)",
                    xaxis_title="Year",
                    yaxis_title="Growth (%)",
                    height=400
                )
                fig_growth.add_hline(y=0, line_dash="dash", line_color="black")
                st.plotly_chart(fig_growth, use_container_width=True)
            else:
                st.info("Need at least 2 years of data to show growth rates.")
    
    # ========== TAB 3: GEOGRAPHIC ANALYSIS ==========
    with tab3:
        st.subheader("Geographic Distribution Analysis")
        
        # FAO Zone analysis
        st.markdown("### FAO Fishing Zones")
        
        fao_stats = df_filtered.groupby('zona_FAO').agg(
            total_weight=('peso_kg', 'sum'),
            total_count=('peso_kg', 'count'),
            avg_weight=('peso_kg', 'mean')
        ).reset_index().sort_values('total_weight', ascending=False)
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_fao = px.bar(
                fao_stats, x='zona_FAO', y='total_weight',
                labels={'zona_FAO': 'FAO Zone', 'total_weight': 'Total Weight (kg)'},
                title="Total Catch by FAO Zone",
                color='total_weight',
                color_continuous_scale='Blues'
            )
            fig_fao.update_layout(height=400)
            st.plotly_chart(fig_fao, use_container_width=True)
        
        with col2:
            fig_fao_count = px.bar(
                fao_stats, x='zona_FAO', y='total_count',
                labels={'zona_FAO': 'FAO Zone', 'total_count': 'Number of Landings'},
                title="Number of Landings by FAO Zone",
                color='total_count',
                color_continuous_scale='Greens'
            )
            fig_fao_count.update_layout(height=400)
            st.plotly_chart(fig_fao_count, use_container_width=True)
        
        # Region-FAO cross-analysis
        st.markdown("### Region × FAO Zone Analysis")
        
        region_fao = df_filtered.groupby(['regione', 'zona_FAO'])['peso_kg'].sum().reset_index()
        
        fig_heatmap = px.density_heatmap(
            region_fao, x='zona_FAO', y='regione', z='peso_kg',
            labels={'peso_kg': 'Total Weight (kg)', 'regione': 'Region', 'zona_FAO': 'FAO Zone'},
            title="Catch Distribution: Region vs FAO Zone",
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
    
    # ========== TAB 4: SEASONALITY ==========
    with tab4:
        st.subheader("Seasonal Patterns Analysis")
        
        # Month analysis
        month_order = ['January', 'February', 'March', 'April', 'May', 'June',
                      'July', 'August', 'September', 'October', 'November', 'December']
        
        monthly_pattern = df_filtered.groupby('month_name').agg(
            total_weight=('peso_kg', 'sum'),
            total_count=('peso_kg', 'count'),
            avg_weight=('peso_kg', 'mean')
        ).reset_index()
        
        # Ensure proper ordering
        monthly_pattern['month_name'] = pd.Categorical(
            monthly_pattern['month_name'], 
            categories=month_order, 
            ordered=True
        )
        monthly_pattern = monthly_pattern.sort_values('month_name')
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_month = px.bar(
                monthly_pattern, x='month_name', y='total_weight',
                labels={'month_name': 'Month', 'total_weight': 'Total Weight (kg)'},
                title="Total Catch by Month",
                color='total_weight',
                color_continuous_scale='Blues'
            )
            fig_month.update_xaxes(tickangle=45)
            fig_month.update_layout(height=400)
            st.plotly_chart(fig_month, use_container_width=True)
        
        with col2:
            fig_month_count = px.bar(
                monthly_pattern, x='month_name', y='total_count',
                labels={'month_name': 'Month', 'total_count': 'Number of Landings'},
                title="Number of Landings by Month",
                color='total_count',
                color_continuous_scale='Greens'
            )
            fig_month_count.update_xaxes(tickangle=45)
            fig_month_count.update_layout(height=400)
            st.plotly_chart(fig_month_count, use_container_width=True)
        
        # Seasonality heatmap
        st.markdown("### Seasonal Heatmap: Region × Month")
        
        # Create month-region heatmap
        df_filtered['month_num'] = df_filtered['month']
        month_region = df_filtered.groupby(['month_name', 'regione'])['peso_kg'].sum().reset_index()
        month_region['month_name'] = pd.Categorical(
            month_region['month_name'],
            categories=month_order,
            ordered=True
        )
        month_region = month_region.sort_values('month_name')
        
        # Pivot for heatmap
        heatmap_data = month_region.pivot(index='regione', columns='month_name', values='peso_kg').fillna(0)
        heatmap_data = heatmap_data.loc[region_rank]  # Order by total weight
        
        fig_season_heatmap = px.imshow(
            heatmap_data,
            labels=dict(x="Month", y="Region", color="Weight (kg)"),
            aspect="auto",
            color_continuous_scale='RdYlGn',
            title="Catch Intensity: Month × Region"
        )
        fig_season_heatmap.update_layout(height=600)
        st.plotly_chart(fig_season_heatmap, use_container_width=True)
        
        # Insights
        st.markdown("### 📊 Seasonal Insights")
        peak_month = monthly_pattern.loc[monthly_pattern['total_weight'].idxmax(), 'month_name']
        peak_weight = monthly_pattern['total_weight'].max()
        st.info(f"🔥 **Peak Month:** {peak_month} with {peak_weight:,.0f} kg landed")
    
    # ========== TAB 5: DATA EXPLORER ==========
    with tab5:
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
            yearly_counts = df_filtered['year'].value_counts().sort_index()
            st.write(yearly_counts)
        
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
