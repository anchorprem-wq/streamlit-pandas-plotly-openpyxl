import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import pytz
import time

st.set_page_config(page_title="Activity Dashboard PRO", layout="wide")

# ==============================
# AUTO REFRESH (30 sec)
# ==============================
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = time.time()

if time.time() - st.session_state.last_refresh > 30:
    st.session_state.last_refresh = time.time()
    st.rerun()

# ==============================
# GRADIENT BACKGROUND + STYLE
# ==============================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #1f4037, #99f2c8);
    color: white;
}

.big-title {
    font-size:40px;
    font-weight:bold;
    animation: fadeIn 2s ease-in;
}

@keyframes fadeIn {
    from {opacity: 0;}
    to {opacity: 1;}
}

.kpi-card {
    background: rgba(255,255,255,0.15);
    padding:20px;
    border-radius:15px;
    text-align:center;
    font-size:20px;
    font-weight:bold;
}
</style>
""", unsafe_allow_html=True)

# ==============================
# INDIA TIME
# ==============================
india = pytz.timezone("Asia/Kolkata")
now = datetime.now(india)

# ==============================
# HEADER
# ==============================
col1, col2 = st.columns([6,2])

with col1:
    st.markdown("<div class='big-title'>📊 Activity Performance Dashboard PRO</div>", unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div style='text-align:right; font-size:18px;'>
        🕒 {now.strftime('%d-%m-%Y')} <br>
        <b>{now.strftime('%I:%M:%S %p')}</b>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ==============================
# GOOGLE SHEET CSV LINK
# ==============================
sheet_url = "https://docs.google.com/spreadsheets/d/1XUAIJX6IzNkxbYCgCj3USfYcpECz6TjrLUZErFVsEo8/export?format=csv"

@st.cache_data(ttl=60)
def load_data():
    df = pd.read_csv(sheet_url)
    return df

df = load_data()
df.columns = df.columns.str.strip()

# ==============================
# DATA TRANSFORM
# ==============================
fixed_cols = ["Activity", "Summary", "Target", "Sample"]
date_cols = [col for col in df.columns if "/" in col]

df_melt = df.melt(
    id_vars=fixed_cols,
    value_vars=date_cols,
    var_name="Date",
    value_name="Value"
)

df_melt["Date"] = pd.to_datetime(df_melt["Date"], dayfirst=True)
df_melt["Value"] = df_melt["Value"].astype(str)

# ==============================
# SIDEBAR FILTERS
# ==============================
st.sidebar.header("🔎 Filters")

activity_list = df_melt["Activity"].dropna().unique().tolist()
activity = st.sidebar.selectbox("Select Activity", activity_list)

filtered_summary = df_melt[df_melt["Activity"] == activity]["Summary"].dropna().unique().tolist()
summary = st.sidebar.selectbox("Select Summary", filtered_summary)

min_date = df_melt["Date"].min()
max_date = df_melt["Date"].max()

date_range = st.sidebar.date_input("Select Date Range", [min_date, max_date])

# ==============================
# FILTER DATA
# ==============================
filtered = df_melt[
    (df_melt["Activity"] == activity) &
    (df_melt["Summary"] == summary) &
    (df_melt["Date"] >= pd.to_datetime(date_range[0])) &
    (df_melt["Date"] <= pd.to_datetime(date_range[1]))
]

# ==============================
# KPI CARDS
# ==============================
st.subheader("📈 Key Performance Indicators")

col1, col2, col3 = st.columns(3)

total_records = len(filtered)
unique_dates = filtered["Date"].nunique()
unique_values = filtered["Value"].nunique()

with col1:
    st.markdown(f"<div class='kpi-card'>Total Records<br>{total_records}</div>", unsafe_allow_html=True)

with col2:
    st.markdown(f"<div class='kpi-card'>Active Dates<br>{unique_dates}</div>", unsafe_allow_html=True)

with col3:
    st.markdown(f"<div class='kpi-card'>Unique Values<br>{unique_values}</div>", unsafe_allow_html=True)

st.markdown("---")

# ==============================
# TABLE VIEW
# ==============================
st.subheader("📋 Filtered Data")

if not filtered.empty:
    st.dataframe(filtered, use_container_width=True)
else:
    st.warning("No data available.")

# ==============================
# 3D STYLE PIE CHART
# ==============================
st.subheader("📊 3D Pie Chart View")

if not filtered.empty:

    pie_data = filtered.groupby("Date").size().reset_index(name="Count")

    fig = px.pie(
        pie_data,
        values="Count",
        names=pie_data["Date"].dt.strftime("%d-%m-%Y"),
        hole=0.3
    )

    fig.update_traces(textinfo="percent+label")
    fig.update_layout(height=500)

    st.plotly_chart(fig, use_container_width=True)

else:
    st.info("No chart data available.")
