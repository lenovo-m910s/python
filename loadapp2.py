import streamlit as st
import pandas as pd

# Page Configuration
st.set_page_config(page_title="Logistics Dashboard", layout="wide")

@st.cache_data
def load_data():
    file_path = 'Load Sheet.xlsx'
    # 'Load Sheet' wali tab read karein
    df = pd.read_excel(file_path, sheet_name='Load Sheet')
    
    # Date columns formatting
    date_columns = ['Booked Date', 'Pickup Date', 'Delivery Date']
    for col in date_columns:
        df[col] = pd.to_datetime(df[col], errors='coerce').dt.date
    
    # Numeric conversion (Safety check taake calculation mein error na aaye)
    df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
    df['Total Miles'] = pd.to_numeric(df['Total Miles'], errors='coerce').fillna(0)
        
    return df

try:
    df = load_data()

    st.title("🚛 Transport Load Dashboard")
    st.markdown("---")

    # --- TOP FILTERS ---
    row1_1, row1_2, row1_3 = st.columns(3)
    with row1_1:
        carrier = st.selectbox("Carrier", ['All'] + sorted(df['Carrier'].dropna().unique().tolist()))
    with row1_2:
        dispatcher = st.selectbox("Dispatcher", ['All'] + sorted(df['Dispatcher'].dropna().unique().tolist()))
    with row1_3:
        driver = st.selectbox("Driver", ['All'] + sorted(df['Driver'].dropna().unique().tolist()))

    row2_1, row2_2, row2_3 = st.columns(3)
    with row2_1:
        booked_date = st.date_input("Booked Date", value=None)
    with row2_2:
        pickup_date = st.date_input("Pickup Date", value=None)
    with row2_3:
        delivery_date = st.date_input("Delivery Date", value=None)

    # --- FILTERING LOGIC ---
    filtered_df = df.copy()

    if carrier != 'All':
        filtered_df = filtered_df[filtered_df['Carrier'] == carrier]
    if dispatcher != 'All':
        filtered_df = filtered_df[filtered_df['Dispatcher'] == dispatcher]
    if driver != 'All':
        filtered_df = filtered_df[filtered_df['Driver'] == driver]

    if booked_date:
        filtered_df = filtered_df[filtered_df['Booked Date'] == booked_date]
    if pickup_date:
        filtered_df = filtered_df[filtered_df['Pickup Date'] == pickup_date]
    if delivery_date:
        filtered_df = filtered_df[filtered_df['Delivery Date'] == delivery_date]

    # --- SUMMARY METRICS (Including RPM) ---
    st.markdown("---")
    m1, m2, m3 = st.columns(3)
    
    # Total Loads
    m1.metric("Total Loads", len(filtered_df))
    
    # Total Amount
    total_amt = filtered_df['Amount'].sum()
    m2.metric("Total Amount", f"${total_amt:,.2f}")
    
    # RPM Calculation ($ / Miles)
    total_miles = filtered_df['Total Miles'].sum()
    # Zero division error se bachne ke liye condition
    rpm = total_amt / total_miles if total_miles > 0 else 0
    m3.metric("RPM", f"${rpm:,.2f}")

    # --- DATA TABLE ---
    st.dataframe(
        filtered_df, 
        use_container_width=True,
        hide_index=True,
        column_config={
            "Booked Date": st.column_config.DateColumn("Booked Date", format="YYYY-MM-DD"),
            "Pickup Date": st.column_config.DateColumn("Pickup Date", format="YYYY-MM-DD"),
            "Delivery Date": st.column_config.DateColumn("Delivery Date", format="YYYY-MM-DD"),
        }
    )

except Exception as e:
    st.error(f"Error: {e}")
