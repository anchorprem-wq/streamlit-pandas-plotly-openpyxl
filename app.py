import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from zoneinfo import ZoneInfo

st.set_page_config(page_title="Activity Dashboard", layout="wide")

# ------------------------
# HEADER
# ------------------------
col1, col2 = st.columns([3,1])

with col1:
    st.title("📊 Activity Performance Dashboard")

with col2:
    now = datetime.now(ZoneInfo("Asia/Kolkata"))
    st.markdown(f"### 🕒 {now.strftime('%d-%m-%Y %I:%M:%S %p')}")

# ------------------------
# LOAD GOOGLE SHEET
# ------------------------
@st.cache_data(ttl=60)
def load_data():
    sheet_id = "1XUAIJX6IzNkxbYCgCj3USfYcpECz6TjrLUZErFVsEo8"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    df = pd.read_csv(url)
    return df

df = load_data()

# ------------------------
# DATA CLEAN
# ------------------------
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
df_long["Value"] = df_long["Value"].astype(str)

# ------------------------
# SIDEBAR FILTERS
# ------------------------
st.sidebar.header("🔎 Filters")

activities = df["Activity"].dropna().unique().tolist()
selected_activity = st.sidebar.selectbox("Select Activity", activities)

summaries = df[df["Activity"] == selected_activity]["Summary"].dropna().unique().tolist()
selected_summary = st.sidebar.selectbox("Select Summary", summaries)

filtered_df = df_long[
    (df_long["Activity"] == selected_activity) &
    (df_long["Summary"] == selected_summary)
]

# ------------------------
# DATE FILTER
# ------------------------
min_date = filtered_df["Date"].min()
max_date = filtered_df["Date"].max()

start_date, end_date = st.sidebar.date_input(
    "Select Date Range",
    [min_date, max_date]
)

filtered_df = filtered_df[
    (filtered_df["Date"] >= pd.to_datetime(start_date)) &
    (filtered_df["Date"] <= pd.to_datetime(end_date))
]

# ------------------------
# TABLE DISPLAY (FULL WIDTH FIX)
# ------------------------
st.subheader("📋 Filtered Data")

display_df = filtered_df.copy()
display_df["Date"] = display_df["Date"].dt.strftime("%d-%m-%Y")

st.data_editor(
    display_df,
    use_container_width=True,
    disabled=True,
    height=400
)

# ------------------------
# PIE CHART
# ------------------------
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

    st.plotly_chart(fig, use_container_width=True)

    # Screenshot Button
    try:
        img_bytes = fig.to_image(format="png")
        st.download_button(
            label="📸 Download Chart Screenshot",
            data=img_bytes,
            file_name="dashboard_chart.png",
            mime="image/png"
        )
    except:
        st.info("Add 'kaleido' in requirements.txt for screenshot feature.")

else:
    st.warning("No data available.")
