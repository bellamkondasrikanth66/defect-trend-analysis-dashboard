import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# Page config
st.set_page_config(page_title="Defect Trend Analysis Dashboard", layout="wide")

# Check if data exists, if not generate it
if not os.path.exists('defects_mock_data.csv'):
    st.warning("Data file not found. Running generator script...")
    from generate_data import generate_mock_data
    generate_mock_data()

@st.cache_data
def load_data():
    df = pd.read_csv('defects_mock_data.csv')
    df['Creation_Date'] = pd.to_datetime(df['Creation_Date'])
    df['Resolution_Date'] = pd.to_datetime(df['Resolution_Date'])
    return df

df = load_data()

# --- SIDEBAR FILTERS ---
st.sidebar.header("📊 Dashboard Filters")

# Module Filter
all_modules = ["All"] + list(df['Module'].unique())
selected_module = st.sidebar.selectbox("Select Module", all_modules)

# Date Filter
min_date = df['Creation_Date'].min().date()
max_date = df['Creation_Date'].max().date()
date_range = st.sidebar.date_input("Select Date Range", [min_date, max_date], min_value=min_date, max_value=max_date)

# Apply Filter Logic
filtered_df = df.copy()
if selected_module != "All":
    filtered_df = filtered_df[filtered_df['Module'] == selected_module]

if len(date_range) == 2:
    start_date, end_date = date_range
    filtered_df = filtered_df[(filtered_df['Creation_Date'].dt.date >= start_date) & 
                               (filtered_df['Creation_Date'].dt.date <= end_date)]

# --- MAIN DASHBOARD ---
st.title("🐞 Defect Trend Analysis Dashboard")
st.markdown("Monitor and analyze software quality metrics, arrival rates, and cluster densities over time.")
st.markdown("---")

# KPI Summary Cards
total_defects = len(filtered_df)
open_defects = len(filtered_df[filtered_df['Status'].isin(['Open', 'In Progress'])])
closed_defects = len(filtered_df[filtered_df['Status'].isin(['Closed', 'Resolved'])])
resolution_rate = (closed_defects / total_defects * 100) if total_defects > 0 else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Defects Reported", total_defects)
col2.metric("Active / Open Defects", open_defects, delta_color="inverse")
col3.metric("Resolved / Closed", closed_defects)
col4.metric("Fix Resolution Rate", f"{resolution_rate:.1f}%")

st.markdown("---")

# --- VISUALIZATIONS ---

# Row 1: Trend 1 & Trend 2
row1_col1, row1_col2 = st.columns(2)

with row1_col1:
    st.subheader("📈 1. Defect Arrival vs. Fix Rate (Monthly)")
    # Aggregate counts by month
    arrival_trend = filtered_df.groupby('Creation_Month').size().reset_index(name='Arrivals')
    
    resolved_only = filtered_df.dropna(subset=['Resolution_Date']).copy()
    resolved_only['Resolution_Month'] = resolved_only['Resolution_Date'].dt.to_period('M').astype(str)
    fix_trend = resolved_only.groupby('Resolution_Month').size().reset_index(name='Fixes')
    
    # Merge metrics
    trend_merge = pd.merge(arrival_trend, fix_trend, left_on='Creation_Month', right_on='Resolution_Month', how='outer')
    trend_merge['Month'] = trend_merge['Creation_Month'].combine_first(trend_merge['Resolution_Month'])
    
    # Fill missing metric counts with 0 ONLY after the string Month column is built
    trend_merge[['Arrivals', 'Fixes']] = trend_merge[['Arrivals', 'Fixes']].fillna(0)
    
    # Now sorting will work perfectly because 'Month' contains 100% string values
    trend_merge = trend_merge.sort_values('Month')
    
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=trend_merge['Month'], y=trend_merge['Arrivals'], mode='lines+markers', name='Arrival Rate (New)', line=dict(color='#EF553B', width=3)))
    fig1.add_trace(go.Scatter(x=trend_merge['Month'], y=trend_merge['Fixes'], mode='lines+markers', name='Fix Rate (Resolved)', line=dict(color='#636EFA', width=3)))
    fig1.update_layout(xaxis_title="Timeline", yaxis_title="Count of Defects", legend_orientation="h")
    st.plotly_chart(fig1, use_container_width=True)

with row1_col2:
    st.subheader("🗂️ 2. Defect Density by Module & Severity")
    density_df = filtered_df.groupby(['Module', 'Severity']).size().reset_index(name='Count')
    fig2 = px.bar(density_df, x='Module', y='Count', color='Severity', 
                 title="Defect Concentration Per Module",
                 color_discrete_map={'Critical': '#D62728', 'High': '#FF7F0E', 'Medium': '#1F77B4', 'Low': '#2CA02C'})
    fig2.update_layout(barmode='stack', xaxis_title="Application Modules", yaxis_title="Defect Count")
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# Row 2: Trend 3 & Data View
row2_col1, row2_col2 = st.columns(2)

with row2_col1:
    st.subheader("⏳ 3. Backlog Aging / Current Status Split")
    status_df = filtered_df.groupby('Status').size().reset_index(name='Count')
    fig3 = px.pie(status_df, values='Count', names='Status', hole=0.4,
                  color_discrete_sequence=px.colors.qualitative.Pastel)
    fig3.update_traces(textinfo='percent+label')
    st.plotly_chart(fig3, use_container_width=True)

with row2_col2:
    st.subheader("📋 Filtered Dataset Peek")
    st.markdown("Drill down inspect sheet based on current interactive criteria selection:")
    st.dataframe(filtered_df[['Defect_ID', 'Creation_Date', 'Module', 'Severity', 'Status', 'Resolution_Date']].sort_values(by='Creation_Date', ascending=False), height=300)