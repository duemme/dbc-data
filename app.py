import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide", page_title="Tuna Catch Dashboard")

# 1. Load data LOCALLY from your repo
@st.cache_data
def load_data():
    df = pd.read_csv('pescaTonnoRosso.csv')
    df['data_cattura'] = pd.to_datetime(df['data_cattura'])
    df['year'] = df['data_cattura'].dt.year.astype(str) # String prevents '2004.5' issue
    return df

df = load_data()

# 2. Precise Math (Calculated on the fly)
annual_totals = df.groupby('year')['peso_kg'].sum().reset_index(name='total_kg')
reg_annual = df.groupby(['year', 'regione'])['peso_kg'].sum().reset_index()
stats = reg_annual.merge(annual_totals, on='year')
stats['share_pct'] = (stats['peso_kg'] / stats['total_kg']) * 100

# 3. Visuals
st.title("🐟 Bluefin Tuna Recreational Dashboard")

# Chart 1: Absolute Weights
st.subheader("Regional Performance (Total kg)")
fig1 = px.bar(stats, x="regione", y="peso_kg", color="year", barmode="group")
st.plotly_chart(fig1, use_container_width=True)

# Chart 2: Quota Share (Guaranteed 100% per year)
st.subheader("Regional Share of Annual Quota (%)")
fig2 = px.bar(stats, x="year", y="share_pct", color="regione", barmode="stack")
fig2.update_layout(yaxis_title="Share (%)", yaxis_range=[0,100])
st.plotly_chart(fig2, use_container_width=True)
