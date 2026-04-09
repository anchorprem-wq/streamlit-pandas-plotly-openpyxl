import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import pytz

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Activity Dashboard", layout="wide")

# ---------------- HEADER ----------------
st.markdown(
    "<h1 style='text-align:center;color:#2E86C1;'>📊 Activity Performance Dashboard</h1>",
    unsafe_allow_html=True
)

# IST TIME
ist = pytz.timezone("Asia/Kolkata")
now = datetime.now(ist)
st.markdown(
    f"<div style='text-align:right;'>🕒 {now.strftime('%d-%m-%Y %I:%M:%S %p')}</div>",
    unsafe_allow_html=True
)

# ---------------- GOOGLE SHEET CSV ----------------
sheet_url = "https://docs.google.com/spreadsheets/d/1XUAIJX6IzNkxbYCgCj3USfYcpECz6TjrLUZErFVsEo8/export?format=csv"

@st.cache_data(ttl=60)
def load_data():
    return pd.read_csv(sheet_url)

df = load_data()

# ---------------- CONVERT WIDE TO LONG ----------------
df_long = df.melt(
    id_vars=["Activity", "Summary", "Target", "Sample"],
    var_name="Date",
    value_name="Value"
)

# Convert Date properly
df_long["Date"] = pd.to_datetime(df_long["Date"], errors="coerce", dayfirst=True)

# Remove invalid rows
df_long = df_long.dropna(subset=["Date"])

# Convert Value numeric safely
df_long["Value"] = pd.to_numeric(df_long["Value"], errors="coerce").fillna(0)

# ---------------- SIDEBAR FILTER ----------------
st.sidebar.header("🔎 Filters")

activity_list = df["Activity"].dropna().unique().tolist()
selected_activity = st.sidebar.selectbox("Select Activity", activity_list)

summary_list = df[df["Activity"] == selected_activity]["Summary"].dropna().unique().tolist()
selected_summary = st.sidebar.selectbox("Select Summary", summary_list)

min_date = df_long["Date"].min()
max_date = df_long["Date"].max()

date_range = st.sidebar.date_input(
    "Select Date Range",
    [min_date, max_date],
    min_value=min_date,
    max_value=max_date
)

# ---------------- FILTER DATA ----------------
filtered_df = df_long[
    (df_long["Activity"] == selected_activity) &
    (df_long["Summary"] == selected_summary) &
    (df_long["Date"] >= pd.to_datetime(date_range[0])) &
    (df_long["Date"] <= pd.to_datetime(date_range[1]))
]

# ---------------- DISPLAY TABLE ----------------
st.subheader("📋 Filtered Data")

if filtered_df.empty:
    st.warning("No data found for selected filters.")
else:
    st.dataframe(filtered_df, use_container_width=True, height=500)

# ---------------- PIE CHART ----------------
if not filtered_df.empty:

    chart_df = (
        filtered_df
        .groupby("Date")["Value"]
        .sum()
        .reset_index()
    )

    chart_df["Date"] = chart_df["Date"].dt.strftime("%d-%m-%Y")

    fig = px.pie(
        chart_df,
        names="Date",
        values="Value",
        hole=0.3,
        title="Date Distribution"
    )

    fig.update_traces(textinfo="percent+label")

    st.subheader("📊 3D Pie Chart View")
    st.plotly_chart(fig, use_container_width=True)
