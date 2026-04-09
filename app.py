import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import pytz
import time
from io import BytesIO

st.set_page_config(page_title="Activity Dashboard PRO", layout="wide")

# =========================
# AUTO REFRESH (30 sec)
# =========================
if "refresh" not in st.session_state:
    st.session_state.refresh = time.time()

if time.time() - st.session_state.refresh > 30:
    st.session_state.refresh = time.time()
    st.rerun()

# =========================
# DARK / LIGHT TOGGLE
# =========================
theme = st.sidebar.toggle("🌗 Dark Mode", value=True)

if theme:
    bg_color = "linear-gradient(135deg, #141E30, #243B55)"
    card_bg = "rgba(255,255,255,0.1)"
else:
    bg_color = "linear-gradient(135deg, #f5f7fa, #c3cfe2)"
    card_bg = "rgba(0,0,0,0.05)"

# =========================
# CUSTOM CSS
# =========================
st.markdown(f"""
<style>
.stApp {{
    background: {bg_color};
    color: white;
}}

.big-title {{
    font-size:38px;
    font-weight:bold;
}}

thead tr th {{
    background-color: #FFD700 !important;
    color: black !important;
    font-weight: bold !important;
}}

</style>
""", unsafe_allow_html=True)

# =========================
# INDIA TIME
# =========================
india = pytz.timezone("Asia/Kolkata")
now = datetime.now(india)

col1, col2 = st.columns([6,2])

with col1:
    st.markdown("<div class='big-title'>🚀 Activity Performance Dashboard</div>", unsafe_allow_html=True)

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
df.columns = df.columns.str.strip()

# Remove serial/index column if exists
if df.columns[0].lower() in ["unnamed: 0", "index", "sr no", "s.no", "serial"]:
    df = df.iloc[:, 1:]

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
# FILTERS
# =========================
st.sidebar.header("🔎 Filters")

activity = st.sidebar.selectbox("Select Activity", df_melt["Activity"].dropna().unique())

summary = st.sidebar.selectbox(
    "Select Summary",
    df_melt[df_melt["Activity"] == activity]["Summary"].dropna().unique()
)

date_range = st.sidebar.date_input(
    "Select Date Range",
    [df_melt["Date"].min(), df_melt["Date"].max()]
)

filtered = df_melt[
    (df_melt["Activity"] == activity) &
    (df_melt["Summary"] == summary) &
    (df_melt["Date"] >= pd.to_datetime(date_range[0])) &
    (df_melt["Date"] <= pd.to_datetime(date_range[1]))
]

st.markdown("---")

# =========================
# DOWNLOAD EXCEL BUTTON
# =========================
def to_excel(df):
    output = BytesIO()
    df.to_excel(output, index=False)
    return output.getvalue()

if not filtered.empty:
    excel_data = to_excel(filtered)

    st.download_button(
        label="⬇ Download Filtered Data (Excel)",
        data=excel_data,
        file_name="filtered_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

st.markdown("---")

# =========================
# DISTRICT RANKING CHART
# =========================
st.subheader("🏆 District Wise Ranking")

if not filtered.empty:
    ranking = filtered.groupby("Sample").size().reset_index(name="Count")

    fig_bar = px.bar(
        ranking.sort_values("Count", ascending=False),
        x="Sample",
        y="Count",
        text="Count",
    )

    fig_bar.update_layout(height=500)
    st.plotly_chart(fig_bar, use_container_width=True)

else:
    st.info("No data available.")

st.markdown("---")

# =========================
# DATA TABLE (NO SERIAL NUMBER)
# =========================
st.subheader("📋 Detailed Data")

if not filtered.empty:
    st.dataframe(filtered.reset_index(drop=True), use_container_width=True)
else:
    st.warning("No records found.")
