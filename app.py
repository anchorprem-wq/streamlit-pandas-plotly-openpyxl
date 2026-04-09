import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import pytz
import time
from io import BytesIO

st.set_page_config(page_title="Activity Dashboard PRO MAX", layout="wide")

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
# GLASSMORPHISM STYLE
# =========================
st.markdown(f"""
<style>
.stApp {{
    background: {bg_color};
    color: white;
}}

.glass-card {{
    background: {card_bg};
    backdrop-filter: blur(10px);
    border-radius: 20px;
    padding: 20px;
    box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
}}

.big-title {{
    font-size:40px;
    font-weight:bold;
    animation: fadeIn 2s ease-in;
}}

@keyframes fadeIn {{
    from {{opacity: 0;}}
    to {{opacity: 1;}}
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
    st.markdown("<div class='big-title'>🚀 Activity Performance Dashboard PRO MAX</div>", unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div style='text-align:right; font-size:18px;'>
        🕒 {now.strftime('%d-%m-%Y')} <br>
        <b>{now.strftime('%I:%M:%S %p')}</b>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# =========================
# GOOGLE SHEET
# =========================
sheet_url = "https://docs.google.com/spreadsheets/d/1XUAIJX6IzNkxbYCgCj3USfYcpECz6TjrLUZErFVsEo8/export?format=csv"

@st.cache_data(ttl=60)
def load_data():
    df = pd.read_csv(sheet_url)
    return df

df = load_data()
df.columns = df.columns.str.strip()

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

# =========================
# ANIMATED KPI CARDS
# =========================
st.subheader("📊 KPI Overview")

col1, col2, col3 = st.columns(3)

def animated_metric(title, value):
    st.markdown(f"""
    <div class='glass-card'>
        <h4>{title}</h4>
        <h2 style='color:#00FFCC'>{value}</h2>
    </div>
    """, unsafe_allow_html=True)

animated_metric("Total Records", len(filtered))
animated_metric("Active Dates", filtered["Date"].nunique())
animated_metric("Unique Values", filtered["Value"].nunique())

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
# DISTRICT WISE RANKING CHART
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
# DATA TABLE
# =========================
st.subheader("📋 Detailed Data")

if not filtered.empty:
    st.dataframe(filtered, use_container_width=True)
else:
    st.warning("No records found.")
