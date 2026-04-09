import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Activity Performance Dashboard", layout="wide")

# ---------------- STYLE ----------------
st.markdown("""
<style>
.stApp {background-color:#f4f6f9;}
h1 {color:#1f4e79;}
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
col1, col2 = st.columns([4,1])

with col1:
    st.title("📊 Activity Performance Dashboard")

with col2:
    now = datetime.now()
    st.markdown(f"### 🕒 {now.strftime('%d-%m-%Y %I:%M:%S %p')}")

# ---------------- GOOGLE SHEET CSV ----------------
sheet_url = "https://docs.google.com/spreadsheets/d/1XUAIJX6IzNkxbYCgCj3USfYcpECz6TjrLUZErFVsEo8/export?format=csv"

@st.cache_data(ttl=60)
def load_data():
    return pd.read_csv(sheet_url)

df = load_data()

# ---------------- CHECK STRUCTURE ----------------
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

activities = df["Activity"].dropna().unique().tolist()
selected_activity = st.sidebar.selectbox("Select Activity", activities)

summaries = df[df["Activity"] == selected_activity]["Summary"].dropna().unique().tolist()
selected_summary = st.sidebar.selectbox("Select Summary", summaries)

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

# ---------------- DATA TABLE ----------------
st.subheader("📋 Filtered Data")
st.dataframe(filtered_df, use_container_width=True)

# ---------------- PIE CHART ----------------
if not filtered_df.empty:

    pie_data = filtered_df.groupby("Date")["Value"].count().reset_index()

    fig = px.pie(
        pie_data,
        names=pie_data["Date"].dt.strftime("%d-%m-%Y"),
        values="Value",
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Bold
    )

    fig.update_traces(textposition="inside", textinfo="percent+label")
    fig.update_layout(title="📊 Date Distribution")

    st.plotly_chart(fig, use_container_width=True)

else:
    st.warning("No data available for selected filters.")

# ---------------- REFRESH BUTTON ----------------
if st.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()
