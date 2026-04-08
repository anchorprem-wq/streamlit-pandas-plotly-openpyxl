import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Activity Performance Dashboard PRO", layout="wide")
st.title("📊 Activity Performance Dashboard PRO")

# -----------------------------
# Load Excel
# -----------------------------
try:
    df = pd.read_excel("activity_data.xlsx", engine="openpyxl")
    st.success(f"Loaded file: activity_data.xlsx")
except Exception as e:
    st.error(f"Failed to load file: {e}")
    st.stop()

# -----------------------------
# Melt date columns
# -----------------------------
date_cols = df.columns[4:]  # First 4 columns: Activity, Summary, Target, Sample
df_long = df.melt(
    id_vars=["Activity","Summary","Target","Sample"],
    value_vars=date_cols,
    var_name="Date",
    value_name="Value"
)
df_long["Date"] = pd.to_datetime(df_long["Date"], dayfirst=True, errors="coerce")

# -----------------------------
# Sidebar Filters
# -----------------------------
st.sidebar.header("🔎 Filters")
activities = ["All"] + df_long["Activity"].dropna().unique().tolist()
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

# -----------------------------
# Filter DataFrame
# -----------------------------
filtered_df = df_long.copy()

if selected_activity != "All":
    filtered_df = filtered_df[filtered_df["Activity"] == selected_activity]

if selected_summary != "All":
    filtered_df = filtered_df[filtered_df["Summary"] == selected_summary]

filtered_df = filtered_df[
    (filtered_df["Date"] >= pd.to_datetime(start_date)) &
    (filtered_df["Date"] <= pd.to_datetime(end_date))
]

# -----------------------------
# Show Table (text + numeric)
# -----------------------------
st.subheader("Filtered Data")
if filtered_df.empty:
    st.warning("No data for selected filters.")
else:
    st.dataframe(filtered_df.pivot_table(
        index=["Activity","Summary","Target","Sample"],
        columns="Date",
        values="Value",
        aggfunc='first',
        fill_value=""
    ))

# -----------------------------
# Optional Graph (numeric only)
# -----------------------------
if not filtered_df.empty:
    numeric_df = filtered_df.copy()
    numeric_df["Value_numeric"] = pd.to_numeric(numeric_df["Value"].astype(str).str.replace("%",""), errors="coerce")

    if not numeric_df["Value_numeric"].isna().all():
        fig = px.line(
            numeric_df,
            x="Date",
            y="Value_numeric",
            color="Summary" if selected_summary=="All" else "Activity",
            markers=True,
            text="Value"
        )
        fig.update_traces(textposition="top center")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No numeric values available for graphing.")