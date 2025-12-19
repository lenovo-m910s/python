import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
import datetime

# Page configuration
st.set_page_config(page_title="Trucking Analytics", layout="wide")

# --- CSS TO REMOVE EMPTY SPACES & IMPROVE DARK LOOK ---
st.markdown("""
    <style>
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 0rem !important;
        background-color: #0e1117;
    }
    .stApp { background-color: #0e1117; color: #ffffff; }
    
    div[data-testid="stMetric"] {
        background-color: #1a1c24 !important;
        border: 1px solid #2d2f39 !important;
        padding: 15px !important;
        border-radius: 12px !important;
    }
    
    .filter-box {
        background-color: #1a1c24;
        padding: 15px;
        border-radius: 12px;
        border: 1px solid #2d2f39;
        margin-top: 10px;
        margin-bottom: 10px;
    }
    
    .element-container:has(div.stPlotlyChart) {
        background-color: #1a1c24;
        border-radius: 12px;
        border: 1px solid #2d2f39;
    }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_data():
    df = pd.read_excel("Load Data.xlsx")
    df['Pickup Date'] = pd.to_datetime(df['Pickup Date']).dt.date
    df['Net Profit'] = df['Amount'] - (df['Driver Pay'].fillna(0) + df['Lumper Paid'].fillna(0))
    return df

try:
    df = load_data()

    st.markdown("<h1 style='text-align: left;'>🚛 Trucking Analytics</h1>", unsafe_allow_html=True)

    # --- HORIZONTAL FILTERS (6 Columns) ---
    st.markdown('<div class="filter-box">', unsafe_allow_html=True)
    f1, f2, f3, f4, f5, f6 = st.columns(6) # 6 Columns now
    
    with f1: 
        sel_driver = st.multiselect("Driver", options=sorted(df["Driver"].unique()), placeholder="Drivers")
    with f2: 
        sel_status = st.multiselect("Status", options=sorted(df["Delivery Status"].unique()), placeholder="Status")
    with f3: 
        sel_truck = st.multiselect("Truck#", options=sorted(df["Truck#"].unique()), placeholder="Trucks")
    with f4: 
        sel_state = st.multiselect("State", options=sorted(df["Pickup State"].unique()), placeholder="States")
    with f5:
        opts = sorted(df[df["Pickup State"].isin(sel_state)]["PPickup City"].unique()) if sel_state else sorted(df["PPickup City"].unique())
        sel_city = st.multiselect("City", options=opts, placeholder="Cities")
    with f6:
        # Date Range Filter
        min_date = df['Pickup Date'].min()
        max_date = df['Pickup Date'].max()
        sel_dates = st.date_input("Date Range", value=(min_date, max_date), min_value=min_date, max_value=max_date)

    st.markdown('</div>', unsafe_allow_html=True)

    # --- FILTERING LOGIC ---
    filtered_df = df.copy()
    if sel_driver: filtered_df = filtered_df[filtered_df["Driver"].isin(sel_driver)]
    if sel_status: filtered_df = filtered_df[filtered_df["Delivery Status"].isin(sel_status)]
    if sel_truck:  filtered_df = filtered_df[filtered_df["Truck#"].isin(sel_truck)]
    if sel_state:  filtered_df = filtered_df[filtered_df["Pickup State"].isin(sel_state)]
    if sel_city:   filtered_df = filtered_df[filtered_df["PPickup City"].isin(sel_city)]
    
    # Date Filtering Logic (Check if both start and end dates are selected)
    if isinstance(sel_dates, tuple) and len(sel_dates) == 2:
        start_date, end_date = sel_dates
        filtered_df = filtered_df[(filtered_df["Pickup Date"] >= start_date) & (filtered_df["Pickup Date"] <= end_date)]

    # --- KPI METRICS ---
    m1, m2, m3, m4 = st.columns(4)
    with m1: st.metric("Revenue", f"${filtered_df['Amount'].sum():,.0f}")
    with m2: st.metric("Profit", f"${filtered_df['Net Profit'].sum():,.0f}")
    with m3: 
        val = filtered_df['Rate/Mile'].mean() if not filtered_df.empty else 0
        st.metric("Avg RPM", f"${val:.2f}")
    with m4: st.metric("Loads", len(filtered_df))

    # --- GRAPHS SECTION ---
    c1, c2 = st.columns(2)
    with c1:
        d_sum = filtered_df.groupby("Driver")["Amount"].sum().reset_index()
        fig1 = px.bar(d_sum, x="Driver", y="Amount", text_auto='.3s', color_discrete_sequence=['#00d4ff'], title="Revenue by Driver")
        fig1.update_layout(template="plotly_dark", height=300, margin=dict(l=20, r=20, t=40, b=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig1, use_container_width=True)

    with c2:
        t_sum = filtered_df.groupby('Pickup Date')['Amount'].sum().reset_index()
        fig2 = px.line(t_sum, x='Pickup Date', y='Amount', markers=True, title="Revenue Trend")
        fig2.update_traces(line_color='#00ff88', texttemplate='$%{y:.2s}', textposition="top center")
        fig2.update_layout(template="plotly_dark", height=300, margin=dict(l=20, r=20, t=40, b=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig2, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        # Check if 'count' column exists or needs creation for Bar Chart
        s_counts = filtered_df["Pickup State"].value_counts().reset_index()
        s_counts.columns = ['Pickup State', 'count']
        fig3 = px.bar(s_counts, x="Pickup State", y="count", text_auto=True, color_discrete_sequence=['#ffcc00'], title="Loads by State")
        fig3.update_layout(template="plotly_dark", height=300, margin=dict(l=20, r=20, t=40, b=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig3, use_container_width=True)

    with c4:
        b_sum = filtered_df.groupby("Broker Name")["Net Profit"].sum().reset_index()
        fig4 = px.pie(b_sum, values="Net Profit", names="Broker Name", hole=0.5, title="Broker Profit Share")
        fig4.update_layout(template="plotly_dark", height=300, margin=dict(l=20, r=20, t=40, b=20), paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig4, use_container_width=True)

    # --- DOWNLOAD DATA ---
    def to_excel(d):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            d.to_excel(writer, index=False)
        return output.getvalue()

    st.download_button("📥 Download Report", data=to_excel(filtered_df), file_name="Trucking_Report.xlsx", use_container_width=True)

except Exception as e:
    st.error(f"Error: {e}")
