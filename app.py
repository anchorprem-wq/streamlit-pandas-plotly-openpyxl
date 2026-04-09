import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
import time

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Activity Performance Dashboard",
    page_icon="📊",
    layout="wide"
)

# ---------------- PROFESSIONAL STYLE ----------------
st.markdown("""
<style>
.main {
    background-color: #f2f6fc;
}
.header-box {
    background: linear-gradient(90deg,#0f2027,#203a43,#2c5364);
    padding: 15px;
    border-radius: 10px;
    color: white;
    text-align: center;
    font-size: 26px;
    font-weight: bold;
}
.time-box {
    text-align: right;
    font-size: 14px;
    color: gray;
}
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
col1, col2 = st.columns([6,2])

with col1:
    st.markdown('<div class="header-box">📊 Activity Performance Dashboard PRO</div>', unsafe_allow_html=True)

with col2:
    now = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    st.markdown(f'<div class="time-box">🕒 {now}</div>', unsafe_allow_html=True)

st.markdown("---")

# ---------------- GOOGLE SHEET CSV LINK ----------------
sheet_url = "https://docs.google.com/spreadsheets/d/1XUAIJX6IzNkxbYCgCj3USfYcpECz6TjrLUZErFVsEo8/export?format=csv"

@st.cache_data(ttl=60)
def load_data():
    df = pd.read_csv(sheet_url)
    return df

df = load_data()

# ---------------- DATA PROCESS ----------------
if df.shape[1] > 4:
    df_long = df.melt(
        id_vars=df.columns[:4],
        var_name="Date",
        value_name="Value"
    )

    df_long["Date"] = pd.to_datetime(df_long["Date"], errors="coerce")
    df_long = df_long.dropna(subset=["Date"])

else:
    st.error("Date or Value column not found in Google Sheet.")
    st.stop()

# ---------------- SIDEBAR FILTERS ----------------
st.sidebar.header("🔎 Filters")

activities = df_long["Activity"].dropna().unique().tolist()
activities.sort()
selected_activity = st.sidebar.selectbox("Select Activity", activities)

filtered_activity = df_long[df_long["Activity"] == selected_activity]

summaries = filtered_activity["Summary"].dropna().unique().tolist()
summaries.sort()
selected_summary = st.sidebar.selectbox("Select Summary", summaries)

filtered_summary = filtered_activity[filtered_activity["Summary"] == selected_summary]

min_date = filtered_summary["Date"].min()
max_date = filtered_summary["Date"].max()

selected_dates = st.sidebar.date_input(
    "Select Date Range",
    [min_date, max_date]
)

if len(selected_dates) == 2:
    start_date, end_date = selected_dates
    filtered_final = filtered_summary[
        (filtered_summary["Date"] >= pd.to_datetime(start_date)) &
        (filtered_summary["Date"] <= pd.to_datetime(end_date))
    ]
else:
    filtered_final = filtered_summary

# ---------------- TABLE ----------------
st.subheader("📋 Data Table")
st.dataframe(filtered_final, use_container_width=True)

# ---------------- GRAPH ----------------
st.subheader("📈 Trend Graph")

if not filtered_final.empty:
    fig = px.line(
        filtered_final,
        x="Date",
        y="Value",
        markers=True,
        title=f"{selected_activity} - {selected_summary}"
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("No data available for selected filter.")

# ---------------- SCREENSHOT INFO ----------------
st.markdown("---")
st.info("📸 Screenshot lene ke liye browser me Right Click → Save as PDF ya Snipping Tool use karein.")
