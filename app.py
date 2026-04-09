import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import pytz
import time

st.set_page_config(page_title="Activity Dashboard", layout="wide")

# =========================
# INDIA TIME (LIVE CLOCK)
# =========================
india = pytz.timezone("Asia/Kolkata")
now = datetime.now(india)

# =========================
# HEADER
# =========================
col1, col2 = st.columns([6,2])

with col1:
    st.markdown("<h1 style='margin-bottom:0;'>📊 Activity Performance Dashboard</h1>", unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div style='text-align:right; font-size:18px;'>
        🕒 {now.strftime('%d-%m-%Y')} <br>
        <b>{now.strftime('%I:%M:%S %p')}</b>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# =========================
# GOOGLE SHEET CSV LINK
# =========================
sheet_url = "https://docs.google.com/spreadsheets/d/1XUAIJX6IzNkxbYCgCj3USfYcpECz6TjrLUZErFVsEo8/export?format=csv"

@st.cache_data(ttl=60)
def load_data():
    df = pd.read_csv(sheet_url)
    return df

df = load_data()

# =========================
# DATA CLEANING
# =========================
df.columns = df.columns.str.strip()

# Melt date columns
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

# =========================
# SIDEBAR FILTERS
# =========================
st.sidebar.header("🔎 Filters")

activity_list = df_melt["Activity"].dropna().unique().tolist()
activity = st.sidebar.selectbox("Select Activity", activity_list)

filtered_summary = df_melt[df_melt["Activity"] == activity]["Summary"].dropna().unique().tolist()
summary = st.sidebar.selectbox("Select Summary", filtered_summary)

min_date = df_melt["Date"].min()
max_date = df_melt["Date"].max()

date_range = st.sidebar.date_input("Select Date Range", [min_date, max_date])

# =========================
# FILTER DATA
# =========================
filtered = df_melt[
    (df_melt["Activity"] == activity) &
    (df_melt["Summary"] == summary) &
    (df_melt["Date"] >= pd.to_datetime(date_range[0])) &
    (df_melt["Date"] <= pd.to_datetime(date_range[1]))
]

# =========================
# SHOW TABLE (FULL WIDTH VALUE COLUMN)
# =========================
st.subheader("📋 Filtered Data")

if not filtered.empty:
    st.dataframe(filtered, use_container_width=True)
else:
    st.warning("No data available for selected filters.")

# =========================
# 3D STYLE PIE CHART
# =========================
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
