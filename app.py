import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Activity Dashboard", layout="wide")

st.title("📊 Activity Performance Dashboard")

# -----------------------------
# 🔹 GOOGLE SHEET CSV LINK DAALO
# -----------------------------
sheet_url = "YAHAN_APNA_CSV_LINK_DALO"

# Data Load Function (Live Update)
@st.cache_data(ttl=60)
def load_data():
    df = pd.read_csv(sheet_url)
    return df

df = load_data()

# -----------------------------
# 🔹 DATE COLUMN FORMAT
# -----------------------------
if "Date" in df.columns:
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

# -----------------------------
# 🔹 FILTER SECTION
# -----------------------------
st.sidebar.header("🔍 Filter Options")

# Date Filter
if "Date" in df.columns:
    min_date = df["Date"].min()
    max_date = df["Date"].max()

    start_date, end_date = st.sidebar.date_input(
        "Select Date Range",
        [min_date, max_date]
    )

    df = df[(df["Date"] >= pd.to_datetime(start_date)) &
            (df["Date"] <= pd.to_datetime(end_date))]

# Activity Dropdown (Sorted)
if "Activity" in df.columns:
    activity_list = sorted(df["Activity"].dropna().unique())
    selected_activity = st.sidebar.selectbox(
        "Select Activity",
        ["All"] + activity_list
    )

    if selected_activity != "All":
        df = df[df["Activity"] == selected_activity]

# -----------------------------
# 🔹 DATA VIEW
# -----------------------------
st.subheader("📄 Data Table")
st.dataframe(df, use_container_width=True)

# -----------------------------
# 🔹 SUMMARY SECTION
# -----------------------------
if "Summary" in df.columns:
    st.subheader("📈 Summary Chart")

    summary_data = df["Summary"].value_counts().sort_index()

    fig, ax = plt.subplots()
    summary_data.plot(kind="bar", ax=ax)

    st.pyplot(fig)

st.success("✅ Data Auto Refresh Every 60 Seconds")
