import streamlit as st
import pandas as pd

st.set_page_config(page_title="Activity Dashboard", layout="wide")
st.title("📊 Activity Performance Dashboard")

# ✅ Google Sheet CSV Link
sheet_url = "https://docs.google.com/spreadsheets/d/1XUAIJX6IzNkxbYCgCj3USfYcpECz6TjrLUZErFVsEo8/export?format=csv"

@st.cache_data(ttl=60)
def load_data():
    df = pd.read_csv(sheet_url)
    return df

df = load_data()

# Clean column names
df.columns = df.columns.str.strip()

# First 4 fixed columns
fixed_cols = ["Activity", "Summary", "Target", "Sample"]

# Date columns automatically detect
date_cols = [col for col in df.columns if col not in fixed_cols]

# Convert wide → long
df_long = df.melt(
    id_vars=fixed_cols,
    value_vars=date_cols,
    var_name="Date",
    value_name="Value"
)

# Convert Date properly
df_long["Date"] = pd.to_datetime(df_long["Date"], dayfirst=True, errors="coerce")

# Keep Value as text (important)
df_long["Value"] = df_long["Value"].astype(str)

df_long = df_long.dropna(subset=["Date"])

# ---------------- Sidebar Filters ----------------
st.sidebar.header("🔎 Filters")

activities = df_long["Activity"].dropna().unique().tolist()
selected_activity = st.sidebar.selectbox("Select Activity", activities)

filtered_activity_df = df_long[df_long["Activity"] == selected_activity]

summaries = filtered_activity_df["Summary"].dropna().unique().tolist()
selected_summary = st.sidebar.selectbox("Select Summary", summaries)

min_date = df_long["Date"].min()
max_date = df_long["Date"].max()

start_date, end_date = st.sidebar.date_input(
    "Select Date Range",
    [min_date, max_date]
)

# Final filter
final_df = df_long[
    (df_long["Activity"] == selected_activity) &
    (df_long["Summary"] == selected_summary) &
    (df_long["Date"] >= pd.to_datetime(start_date)) &
    (df_long["Date"] <= pd.to_datetime(end_date))
]

# ---------------- Table ----------------
st.subheader("📋 Data Table")
st.data_editor(final_df, use_container_width=True, hide_index=True)

# ---------------- Graph ----------------
st.subheader("📈 Trend Graph")

numeric_df = final_df.copy()
numeric_df["Value"] = pd.to_numeric(numeric_df["Value"], errors="coerce")

if not numeric_df["Value"].isna().all():
    st.line_chart(numeric_df.set_index("Date")["Value"])
else:
    st.info("Selected data contains text/remarks only.")
