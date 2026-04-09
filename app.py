import streamlit as st
import pandas as pd

st.set_page_config(page_title="Activity Dashboard", layout="wide")

st.title("📊 Activity Performance Dashboard")

# 🔹 Google Sheet CSV Export Link
sheet_url = "https://docs.google.com/spreadsheets/d/1XUAIJX6IzNkxbYCgCj3USfYcpECz6TjrLUZErFVsEo8/export?format=csv"

@st.cache_data
def load_data():
    df = pd.read_csv(sheet_url)
    return df

df = load_data()

# ✅ Check if required columns exist
if "Date" in df.columns and "Value" in df.columns:

    st.subheader("📋 Activity Data Table")

    edited_df = st.data_editor(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Date": st.column_config.DateColumn(
                "Date",
                format="DD-MM-YYYY"
            ),
            "Value": st.column_config.NumberColumn(
                "Value",
                help="Activity numeric value",
                format="%d",
                width="large"
            )
        }
    )

else:
    st.error("Date or Value column not found in Google Sheet.")
