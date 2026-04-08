import streamlit as st
import pandas as pd
import plotly.express as px

# Page config
st.set_page_config(page_title="Activity Performance Dashboard PRO", layout="wide")
st.title("📊 Activity Performance Dashboard PRO")

# Load Excel
try:
    df = pd.read_excel("activity_data.xlsx", engine="openpyxl")
    st.success("Loaded file: activity_data.xlsx")
except Exception as e:
    st.error(f"Failed to load file: {e}")
    st.stop()

# Melt date columns
date_cols = df.columns[4:]  # Assuming first 4 columns: Activity, Summary, Target, Sample
df_long = df.melt(
    id_vars=["Activity", "Summary", "Target", "Sample"],
    value_vars=date_cols,
    var_name="Date",
    value_name="Value"
)

# Convert Date to datetime
df_long["Date"] = pd.to_datetime(df_long["Date"], dayfirst=True, errors="coerce")

# Sidebar Filters
st.sidebar.header("🔎 Filters")
activities = ["All"] + df_long["Activity"].dropna().astype(str).unique().tolist()
selected_activity = st.sidebar.selectbox("Select Activity", activities)

# Dependent Summary Dropdown
if selected_activity == "All":
    summaries = ["All"] + df_long["Summary"].dropna().astype(str).unique().tolist()
else:
    summaries = ["All"] + df_long[df_long["Activity"] == selected_activity]["Summary"].dropna().astype(str).unique().tolist()
selected_summary = st.sidebar.selectbox("Select Summary", summaries)

# Date Picker
min_date = df_long["Date"].min()
max_date = df_long["Date"].max()
start_date, end_date = st.sidebar.date_input(
    "Select Date Range",
    [min_date, max_date],
    min_value=min_date,
    max_value=max_date
)

# Filter DataFrame
filtered_df = df_long.copy()
if selected_activity != "All":
    filtered_df = filtered_df[filtered_df["Activity"] == selected_activity]
if selected_summary != "All":
    filtered_df = filtered_df[filtered_df["Summary"] == selected_summary]
filtered_df = filtered_df[(filtered_df["Date"] >= pd.to_datetime(start_date)) &
                          (filtered_df["Date"] <= pd.to_datetime(end_date))]

# Show filtered data
st.dataframe(filtered_df)

# Plot Graph
if not filtered_df.empty:
    fig = px.line(
        filtered_df,
        x="Date",
        y="Value",
        color="Summary" if selected_summary == "All" else "Activity",
        markers=True
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No data for selected filters.")