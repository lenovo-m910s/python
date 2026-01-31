import streamlit as st
import pandas as pd
import plotly.express as px

# Page Configuration
st.set_page_config(page_title="Logistics Dashboard", layout="wide")

# --- Custom CSS for Dark Theme ---
st.markdown("""
    <style>
    .main {
        background-color: #121212;
        color: #e0e0e0;
    }
    div[data-testid="stMetric"] {
        background: #1e1e1e;
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.6);
        text-align: center;
        color: #e0e0e0;
    }
    div[data-testid="stMetric"] > label {
        font-size: 14px;
        color: #b0b0b0;
    }
    div[data-testid="stMetric"] > div {
        font-size: 18px;
        font-weight: bold;
        color: #ffffff;
    }
    div[data-testid="stSelectbox"], div[data-testid="stDateInput"] {
        background: #1e1e1e;
        padding: 8px;
        border-radius: 8px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.5);
        color: #e0e0e0;
    }
    h1, h2, h3 {
        color: #ffffff;
        font-family: 'Segoe UI', sans-serif;
    }
    div[data-testid="stDataFrame"] table {
        font-size: 16px;
    }
    div[data-testid="stDataFrame"] th {
        font-size: 16px;
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    file_path = 'Load Sheet.xlsx'
    df = pd.read_excel(file_path, sheet_name='Load Sheet')
    
    # Date columns formatting
    date_columns = ['Booked Date', 'Pickup Date', 'Delivery Date']
    for col in date_columns:
        df[col] = pd.to_datetime(df[col], errors='coerce').dt.date
    
    # Numeric conversion
    df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
    df['Total Miles'] = pd.to_numeric(df['Total Miles'], errors='coerce').fillna(0)
    df['Weight LBS'] = pd.to_numeric(df['Weight LBS'], errors='coerce').fillna(0)
        
    return df

try:
    df = load_data()

    st.title("🚛 Transport Load Dashboard")
    st.markdown("---")

    # --- TOP FILTERS ---
    row1_1, row1_2, row1_3, row1_4 = st.columns(4)
    with row1_1:
        carrier = st.selectbox("Carrier", ['All'] + sorted(df['Carrier'].dropna().unique().tolist()))
    with row1_2:
        dispatcher = st.selectbox("Dispatcher", ['All'] + sorted(df['Dispatcher'].dropna().unique().tolist()))
    with row1_3:
        driver = st.selectbox("Driver", ['All'] + sorted(df['Driver'].dropna().unique().tolist()))
    with row1_4:
        status = st.selectbox("Status", ['All'] + sorted(df['POD Status'].dropna().unique().tolist()))

    # --- DATE RANGE FILTERS ---
    row2_1, row2_2, row2_3 = st.columns(3)
    min_date = df[['Booked Date','Pickup Date','Delivery Date']].min().min()
    max_date = df[['Booked Date','Pickup Date','Delivery Date']].max().max()

    with row2_1:
        booked_range = st.date_input("Booked Date Range", value=(min_date, max_date),
                                     min_value=min_date, max_value=max_date)
    with row2_2:
        pickup_range = st.date_input("Pickup Date Range", value=(min_date, max_date),
                                     min_value=min_date, max_value=max_date)
    with row2_3:
        delivery_range = st.date_input("Delivery Date Range", value=(min_date, max_date),
                                       min_value=min_date, max_value=max_date)

    # --- CLEAR BUTTON ---
    if st.button("Clear Date Filters"):
        booked_range = (min_date, max_date)
        pickup_range = (min_date, max_date)
        delivery_range = (min_date, max_date)

    # --- FILTERING LOGIC ---
    filtered_df = df.copy()
    if carrier != 'All':
        filtered_df = filtered_df[filtered_df['Carrier'] == carrier]
    if dispatcher != 'All':
        filtered_df = filtered_df[filtered_df['Dispatcher'] == dispatcher]
    if driver != 'All':
        filtered_df = filtered_df[filtered_df['Driver'] == driver]
    if status != 'All':
        filtered_df = filtered_df[filtered_df['POD Status'] == status]

    if booked_range:
        start, end = booked_range
        filtered_df = filtered_df[(filtered_df['Booked Date'] >= start) & (filtered_df['Booked Date'] <= end)]
    if pickup_range:
        start, end = pickup_range
        filtered_df = filtered_df[(filtered_df['Pickup Date'] >= start) & (filtered_df['Pickup Date'] <= end)]
    if delivery_range:
        start, end = delivery_range
        filtered_df = filtered_df[(filtered_df['Delivery Date'] >= start) & (filtered_df['Delivery Date'] <= end)]

    # --- SUMMARY METRICS ---
    st.markdown("---")
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Total Loads", len(filtered_df))
    total_amt = filtered_df['Amount'].sum()
    m2.metric("Total Amount", f"${total_amt:,.2f}")
    total_revenue = total_amt * 0.03
    m3.metric("Total Revenue", f"${total_revenue:,.2f}")
    total_miles = filtered_df['Total Miles'].sum()
    rpm = total_amt / total_miles if total_miles > 0 else 0
    m4.metric("RPM", f"${rpm:,.2f}")
    total_weight = filtered_df['Weight LBS'].sum()
    carrier_count = filtered_df['Carrier'].count()
    avg_weight_per_load = total_weight / carrier_count if carrier_count > 0 else 0
    m5.metric("Avg Weight Per Load", f"{avg_weight_per_load:,.2f} lbs")

    # --- DATA TABLE ---
    st.markdown("### 📊 Load Details")
    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True,
        height=700,
        column_config={
            "Booked Date": st.column_config.DateColumn("Booked Date", format="YYYY-MM-DD"),
            "Pickup Date": st.column_config.DateColumn("Pickup Date", format="YYYY-MM-DD"),
            "Delivery Date": st.column_config.DateColumn("Delivery Date", format="YYYY-MM-DD"),
            "Amount": st.column_config.NumberColumn("Amount ($)", format="$%.2f"),
            "Total Miles": st.column_config.NumberColumn("Total Miles", format="%d mi"),
            "Weight LBS": st.column_config.NumberColumn("Weight (lbs)", format="%d"),
        }
    )

    # --- GRAPHS SECTION ---
    st.markdown("---")
    g1, g2 = st.columns(2)

    # Daily Revenue
    daily_revenue = filtered_df.groupby("Booked Date")["Amount"].sum().reset_index()
    daily_revenue["Revenue"] = daily_revenue["Amount"] * 0.03
    with g1:
        st.subheader("Daily Revenue (Date Wise)")
        fig_rev = px.bar(daily_revenue, x="Booked Date", y="Revenue", text="Revenue",
                         color="Revenue", color_continuous_scale="Blues")
        fig_rev.update_traces(texttemplate='$%{text:.2f}', textposition='outside')
        fig_rev.update_layout(yaxis_title="Revenue ($)", xaxis_title="Date",
                              template="plotly_dark",
                              xaxis=dict(type="category", categoryorder="category ascending"))
        st.plotly_chart(fig_rev, use_container_width=True)

    # Daily Total Amount
    daily_amount = filtered_df.groupby("Booked Date")["Amount"].sum().reset_index()
    with g2:
        st.subheader("Daily Total Amount (Date Wise)")
        fig_amt = px.bar(daily_amount, x="Booked Date", y="Amount", text="Amount",
                         color="Amount", color_continuous_scale="Greens")
        fig_amt.update_traces(texttemplate='$%{text:.2f}', textposition='outside')
        fig_amt.update_layout(yaxis_title="Total Amount ($)", xaxis_title="Date",
                              template="plotly_dark",
                              xaxis=dict(type="category", categoryorder="category ascending"))
        st.plotly_chart(fig_amt, use_container_width=True)

except Exception as e:
    st.error(f"Error: {e}")
