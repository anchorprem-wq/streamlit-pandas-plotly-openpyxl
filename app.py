import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Activity Dashboard", layout="wide")

# -------- GOOGLE SHEET CSV LINK --------
sheet_id = "1XUAIJX6IzNkxbYCgCj3USfYcpECz6TjrLUZErFVsEo8"
sheet_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"

@st.cache_data(ttl=60)
def load_data():
    df = pd.read_csv(sheet_url)
    return df

df = load_data()

st.title("📊 Activity Performance Dashboard")

# ---------- CURRENT DATE TIME ----------
now = datetime.now()
st.markdown(f"🕒 {now.strftime('%d-%m-%Y %I:%M:%S %p')}")

# ---------- RESHAPE DATA ----------
date_columns = df.columns[4:]

df_melt = df.melt(
    id_vars=["Activity", "Summary", "Target", "Sample"],
    value_vars=date_columns,
    var_name="Date",
    value_name="Value"
)

df_melt["Date"] = pd.to_datetime(df_melt["Date"], dayfirst=True, errors="coerce")

# ---------- SIDEBAR FILTERS ----------
st.sidebar.header("Filters")

activity_list = df["Activity"].dropna().unique()
selected_activity = st.sidebar.selectbox("Select Activity", activity_list)

summary_list = df[df["Activity"] == selected_activity]["Summary"].dropna().unique()
selected_summary = st.sidebar.selectbox("Select Summary", summary_list)

min_date = df_melt["Date"].min()
max_date = df_melt["Date"].max()

selected_dates = st.sidebar.date_input(
    "Select Date Range",
    [min_date, max_date],
    min_value=min_date,
    max_value=max_date
)

# ---------- FILTER DATA ----------
filtered_df = df_melt[
    (df_melt["Activity"] == selected_activity) &
    (df_melt["Summary"] == selected_summary) &
    (df_melt["Date"] >= pd.to_datetime(selected_dates[0])) &
    (df_melt["Date"] <= pd.to_datetime(selected_dates[1]))
]

st.subheader("📋 Filtered Data")

st.dataframe(
    filtered_df,
    use_container_width=True,
    height=500
)

# ---------- PIE CHART ----------
st.subheader("📊 3D Style Pie Chart")

if not filtered_df.empty:

    chart_data = filtered_df.groupby("Date").size().reset_index(name="Count")

    fig = px.pie(
        chart_data,
        names="Date",
        values="Count",
        hole=0.3
    )

    fig.update_traces(textposition="inside", textinfo="percent+label")

    st.plotly_chart(fig, use_container_width=True)

else:
    st.warning("No data available for selected filters.")
