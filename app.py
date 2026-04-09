import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import pytz
import time

# ================= PAGE CONFIG =================
st.set_page_config(page_title="Activity Dashboard", layout="wide")

# ================= AUTO REFRESH SAFE METHOD =================
time.sleep(1)
st.rerun()

# ================= BACKGROUND =================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #141E30, #243B55);
    color: white;
}
h1, h2, h3, h4 {
    color: #FFD700 !important;
}
thead tr th {
    background-color: #FFD700 !important;
    color: black !important;
}
</style>
""", unsafe_allow_html=True)

# ================= GOOGLE SHEET LOAD =================
sheet_id = "1XUAIJX6IzNkxbYCgCj3USfYcpECz6TjrLUZErFVsEo8"
sheet_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"

@st.cache_data(ttl=60)
def load_data():
    df = pd.read_csv(sheet_url)
    return df

df = load_data()

# ================= INDIA TIME =================
india = pytz.timezone("Asia/Kolkata")
current_time = datetime.now(india).strftime("%d-%m-%Y %I:%M:%S %p")

st.markdown(f"### 🕒 {current_time}")

# ================= DROPDOWNS =================
activities = df["Activity"].dropna().unique()
selected_activity = st.selectbox("Select Activity", activities)

filtered_activity = df[df["Activity"] == selected_activity]

summaries = filtered_activity["Summary"].dropna().unique()
selected_summary = st.selectbox("Select Summary", summaries)

filtered_df = filtered_activity[filtered_activity["Summary"] == selected_summary]

# ================= DATE COLUMNS =================
date_columns = df.columns[4:]
selected_date = st.selectbox("Select Date", date_columns)

# ================= VALUE EXTRACTION =================
filtered_df["Value"] = pd.to_numeric(filtered_df[selected_date], errors="coerce").fillna(0)

# ================= DISPLAY TABLE =================
st.subheader("📋 Filtered Data")

display_df = filtered_df[["Activity", "Summary", "Target", "Sample", "Value"]]

st.dataframe(display_df, use_container_width=True)

# ================= DOWNLOAD BUTTON =================
excel_file = "filtered_data.xlsx"
display_df.to_excel(excel_file, index=False)

with open(excel_file, "rb") as f:
    st.download_button(
        label="⬇ Download Excel",
        data=f,
        file_name="filtered_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# ================= 3D PIE CHART =================
st.subheader("📊 3D Pie Chart View")

fig = go.Figure(data=[go.Pie(
    labels=filtered_df["Sample"],
    values=filtered_df["Value"],
    hole=0.3
)])

fig.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)"
)

st.plotly_chart(fig, use_container_width=True)
