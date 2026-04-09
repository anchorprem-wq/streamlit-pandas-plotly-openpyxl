import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from zoneinfo import ZoneInfo
import io

st.set_page_config(page_title="Activity Dashboard", layout="wide")

# ---------------------------
# CUSTOM CSS (Professional UI)
# ---------------------------
st.markdown("""
<style>
.main {background-color: #f4f6f9;}
h1 {font-size:38px !important;}
[data-testid="stDataFrame"] div {
    font-size:14px;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------
# HEADER WITH LIVE IST TIME
# ---------------------------
col1, col2 = st.columns([3,1])

with col1:
    st.title("📊 Activity Performance Dashboard")

with col2:
    now = datetime.now(ZoneInfo("Asia/Kolkata"))
    st.markdown(f"### 🕒 {now.strftime('%d-%m-%Y %I:%M:%S %p')}")

# ---------------------------
# LOAD GOOGLE SHEET
# ---------------------------
@st.cache_data(ttl=60)
def load_data():
    sheet_id = "1XUAIJX6IzNkxbYCgCj3USfYcpECz6TjrLUZErFVsEo8"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    df = pd.read_csv(url)
    return df

df = load_data()

# ---------------------------
# CLEAN DATA
# ---------------------------
fixed_cols = ["Activity", "Summary", "Target", "Sample"]
date_cols = [col for col in df.columns if col not in fixed_cols]

df_long = df.melt(
    id_vars=fixed_cols,
    value_vars=date_cols,
    var_name="Date",
    value_name="Value"
)

df_long["Date"] = pd.to_datetime(df_long["Date"], errors="coerce")
df_long = df_long.dropna(subset=["Date"])

# Keep value as text (important)
df_long["Value"] = df_long["Value"].astype(str)

# ---------------------------
# SIDEBAR FILTERS
# ---------------------------
st.sidebar.header("🔎 Filters")

activities = df["Activity"].dropna().unique().tolist()
selected_activity = st.sidebar.selectbox("Select Activity", activities)

filtered_summary_df = df[df["Activity"] == selected_activity]
summaries = filtered_summary_df["Summary"].dropna().unique().tolist()

selected_summary = st.sidebar.selectbox("Select Summary", summaries)

filtered_df = df_long[
    (df_long["Activity"] == selected_activity) &
    (df_long["Summary"] == selected_summary)
]

# ---------------------------
# DATE RANGE FILTER
# ---------------------------
min_date = filtered_df["Date"].min()
max_date = filtered_df["Date"].max()

start_date, end_date = st.sidebar.date_input(
    "Select Date Range",
    [min_date, max_date],
    min_value=min_date,
    max_value=max_date
)

filtered_df = filtered_df[
    (filtered_df["Date"] >= pd.to_datetime(start_date)) &
    (filtered_df["Date"] <= pd.to_datetime(end_date))
]

# ---------------------------
# DISPLAY TABLE (AUTO WIDTH FIX)
# ---------------------------
st.subheader("📋 Filtered Data")

display_df = filtered_df.copy()
display_df["Date"] = display_df["Date"].dt.strftime("%d-%m-%Y")

st.dataframe(
    display_df,
    use_container_width=True,
    height=350
)

# ---------------------------
# 3D STYLE PIE CHART
# ---------------------------
st.subheader("📊 Date Distribution")

if not filtered_df.empty:
    pie_data = filtered_df.groupby("Date").size().reset_index(name="Count")

    fig = px.pie(
        pie_data,
        names=pie_data["Date"].dt.strftime("%d-%m-%Y"),
        values="Count",
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Bold
    )

    fig.update_traces(textinfo="percent+label")
    fig.update_layout(
        height=500
    )

    st.plotly_chart(fig, use_container_width=True)

    # Screenshot download
    img_bytes = fig.to_image(format="png")
    st.download_button(
        label="📸 Download Chart Screenshot",
        data=img_bytes,
        file_name="dashboard_chart.png",
        mime="image/png"
    )

else:
    st.warning("No data available for selected filters.")
