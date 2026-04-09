import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="📊 Activity Performance Dashboard", layout="wide")

st.title("📊 Activity Performance Dashboard")

# --------------------------
# Load Google Sheet Data
# --------------------------

@st.cache_data(ttl=60)
def load_data():
    sheet_url = "https://docs.google.com/spreadsheets/d/1XUAIJX6IzNkxbYCgCj3USfYcpECz6TjrLUZErFVsEo8/export?format=csv"
    df = pd.read_csv(sheet_url)
    return df

df = load_data()

st.success("Google Sheet Connected Successfully ✅")

# --------------------------
# Sidebar Filters
# --------------------------

st.sidebar.header("🔎 Filters")

activities = ["All"] + df["Activity"].dropna().unique().tolist()
selected_activity = st.sidebar.selectbox("Select Activity", activities)

if selected_activity == "All":
    summaries = ["All"] + df["Summary"].dropna().unique().tolist()
else:
    summaries = ["All"] + df[df["Activity"] == selected_activity]["Summary"].dropna().unique().tolist()

selected_summary = st.sidebar.selectbox("Select Summary", summaries)

# --------------------------
# Filter Data
# --------------------------

filtered_df = df.copy()

if selected_activity != "All":
    filtered_df = filtered_df[filtered_df["Activity"] == selected_activity]

if selected_summary != "All":
    filtered_df = filtered_df[filtered_df["Summary"] == selected_summary]

# --------------------------
# Show Data
# --------------------------

st.dataframe(filtered_df)

# --------------------------
# Graph
# --------------------------

if "Date" in filtered_df.columns and "Value" in filtered_df.columns:
    filtered_df["Date"] = pd.to_datetime(filtered_df["Date"], errors="coerce")

    fig = px.line(
        filtered_df,
        x="Date",
        y="Value",
        color="Summary",
        markers=True
    )

    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Date or Value column not found.")
