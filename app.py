import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import pytz

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Activity Dashboard", layout="wide")

# ---------------- HEADER ----------------
st.markdown(
    """
    <h1 style='text-align:center;color:#2E86C1;'>
    📊 Activity Performance Dashboard
    </h1>
    """,
    unsafe_allow_html=True
)

# IST Time
ist = pytz.timezone("Asia/Kolkata")
now = datetime.now(ist)
st.markdown(f"<div style='text-align:right;font-size:16px;'>🕒 {now.strftime('%d-%m-%Y %H:%M:%S')}</div>", unsafe_allow_html=True)

# ---------------- GOOGLE SHEET CSV ----------------
sheet_url = "https://docs.google.com/spreadsheets/d/1XUAIJX6IzNkxbYCgCj3USfYcpECz6TjrLUZErFVsEo8/export?format=csv"

@st.cache_data(ttl=60)
def load_data():
    df = pd.read_csv(sheet_url)
    return df

df = load_data()

# ---------------- DATA MELT ----------------
df_long = df.melt(
    id_vars=["Activity", "Summary", "Target", "Sample"],
    var_name="Date",
    value_name="Value"
)

df_long["Date"] = pd.to_datetime(df_long["Date"], errors="coerce", dayfirst=True)
df_long = df_long.dropna(subset=["Date"])

# ---------------- SIDEBAR FILTER ----------------
st.sidebar.header("🔎 Filters")

# Activity sequence same as sheet
activity_list = df["Activity"].dropna().unique().tolist()
selected_activity = st.sidebar.selectbox("Select Activity", activity_list)

# Dependent Summary
summary_list = df[df["Activity"] == selected_activity]["Summary"].dropna().unique().tolist()
selected_summary = st.sidebar.selectbox("Select Summary", summary_list)

# Date Range
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
    st.dataframe(
        filtered_df,
        use_container_width=True,
        height=500
    )

# ---------------- 3D PIE CHART ----------------
if not filtered_df.empty:
    pie_df = filtered_df.copy()

    fig = px.pie(
        pie_df,
        names="Date",
        values=pd.to_numeric(pie_df["Value"], errors="coerce").fillna(0),
        hole=0.3
    )

    fig.update_traces(textinfo="percent+label")
    fig.update_layout(
        height=600
    )

    st.subheader("📊 3D Pie Chart View")
    st.plotly_chart(fig, use_container_width=True)
