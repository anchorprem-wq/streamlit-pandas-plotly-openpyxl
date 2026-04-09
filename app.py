import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import pytz

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Activity Performance Dashboard", layout="wide")

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>
.main {background-color:#f4f6f9;}
.stApp {background-color:#f4f6f9;}
.block-container {padding-top:1rem;}
h1 {color:#1f4e79;}
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
col1, col2 = st.columns([4,1])

with col1:
    st.title("📊 Activity Performance Dashboard")

with col2:
    ist = pytz.timezone("Asia/Kolkata")
    now = datetime.now(ist)
    st.markdown(f"### 🕒 {now.strftime('%d-%m-%Y %I:%M:%S %p')}")

# ---------------- GOOGLE SHEET CSV LINK ----------------
sheet_url = "https://docs.google.com/spreadsheets/d/1XUAIJX6IzNkxbYCgCj3USfYcpECz6TjrLUZErFVsEo8/export?format=csv"

@st.cache_data(ttl=60)
def load_data():
    df = pd.read_csv(sheet_url)
    return df

df = load_data()

# ---------------- CHECK BASIC STRUCTURE ----------------
required_cols = ["Activity", "Summary", "Target", "Sample"]

if not all(col in df.columns for col in required_cols):
    st.error("Google Sheet structure mismatch.")
    st.stop()

# ---------------- MELT DATE COLUMNS ----------------
date_columns = df.columns[4:]

df_long = df.melt(
    id_vars=["Activity", "Summary", "Target", "Sample"],
    value_vars=date_columns,
    var_name="Date",
    value_name="Value"
)

df_long["Date"] = pd.to_datetime(df_long["Date"], errors="coerce", dayfirst=True)
df_long = df_long.dropna(subset=["Date"])

# ---------------- SIDEBAR FILTERS ----------------
st.sidebar.header("🔎 Filters")

# Activity in original sequence
activities = df["Activity"].dropna().unique().tolist()
selected_activity = st.sidebar.selectbox("Select Activity", activities)

# Dependent Summary
summaries = df[df["Activity"] == selected_activity]["Summary"].dropna().unique().tolist()
selected_summary = st.sidebar.selectbox("Select Summary", summaries)

# Date Range (Full calendar)
min_date = df_long["Date"].min()
max_date = df_long["Date"].max()

date_range = st.sidebar.date_input(
    "Select Date Range",
    [min_date, max_date],
    min_value=min_date,
    max_value=max_date
)

if len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date = end_date = min_date

# ---------------- FILTER DATA ----------------
filtered_df = df_long[
    (df_long["Activity"] == selected_activity) &
    (df_long["Summary"] == selected_summary) &
    (df_long["Date"] >= pd.to_datetime(start_date)) &
    (df_long["Date"] <= pd.to_datetime(end_date))
]

# ---------------- DISPLAY DATA ----------------
st.subheader("📋 Filtered Data")
st.dataframe(filtered_df, use_container_width=True)

# ---------------- 3D PIE CHART ----------------
if not filtered_df.empty:

    pie_data = filtered_df.groupby("Date")["Value"].count().reset_index()

    fig = px.pie(
        pie_data,
        names=pie_data["Date"].dt.strftime("%d-%m-%Y"),
        values="Value",
        hole=0.3,
        color_discrete_sequence=px.colors.qualitative.Bold
    )

    fig.update_traces(textposition="inside", textinfo="percent+label")
    fig.update_layout(title="📊 Date Distribution (3D Style Look)")

    st.plotly_chart(fig, use_container_width=True)

    # Screenshot Download
    img_bytes = fig.to_image(format="png")
    st.download_button(
        label="📸 Download Chart as PNG",
        data=img_bytes,
        file_name="dashboard_chart.png",
        mime="image/png"
    )

else:
    st.warning("No data available for selected filters.")

# ---------------- AUTO REFRESH BUTTON ----------------
if st.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()
