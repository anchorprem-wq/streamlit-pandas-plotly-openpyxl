import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="📊 Activity Performance Dashboard", layout="wide")
st.title("📊 Activity Performance Dashboard")

# ===============================
# Load Google Sheet
# ===============================

@st.cache_data(ttl=60)
def load_data():
    sheet_url = "https://docs.google.com/spreadsheets/d/1XUAIJX6IzNkxbYCgCj3USfYcpECz6TjrLUZErFVsEo8/export?format=csv"
    df = pd.read_csv(sheet_url)
    return df

df = load_data()

# ===============================
# Convert Wide Date Columns to Long Format
# ===============================

fixed_cols = ["Activity", "Summary", "Target", "Sample"]

date_cols = [col for col in df.columns if col not in fixed_cols]

df_long = df.melt(
    id_vars=fixed_cols,
    value_vars=date_cols,
    var_name="Date",
    value_name="Value"
)

# Convert Date
df_long["Date"] = pd.to_datetime(df_long["Date"], dayfirst=True, errors="coerce")

# Remove blank values
df_long = df_long.dropna(subset=["Date"])

# ===============================
# Sidebar Filters
# ===============================

st.sidebar.header("🔎 Filters")

activities = df_long["Activity"].dropna().unique().tolist()
selected_activity = st.sidebar.selectbox("Select Activity", activities)

summaries = df_long[df_long["Activity"] == selected_activity]["Summary"].dropna().unique().tolist()
selected_summary = st.sidebar.selectbox("Select Summary", summaries)

# Date Range
min_date = df_long["Date"].min()
max_date = df_long["Date"].max()

start_date, end_date = st.sidebar.date_input(
    "Select Date Range",
    [min_date, max_date],
    min_value=min_date,
    max_value=max_date
)

# ===============================
# Filter Data
# ===============================

filtered_df = df_long[
    (df_long["Activity"] == selected_activity) &
    (df_long["Summary"] == selected_summary) &
    (df_long["Date"] >= pd.to_datetime(start_date)) &
    (df_long["Date"] <= pd.to_datetime(end_date))
]

# ===============================
# Show Data
# ===============================

st.dataframe(filtered_df)

# ===============================
# Graph
# ===============================

if not filtered_df.empty:

    fig = px.line(
        filtered_df,
        x="Date",
        y="Value",
        markers=True,
        title=f"{selected_activity} - {selected_summary}"
    )

    st.plotly_chart(fig, use_container_width=True)

else:
    st.warning("No data for selected filters.")
