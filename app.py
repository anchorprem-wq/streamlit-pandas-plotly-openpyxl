import streamlit as st
import pandas as pd
from datetime import datetime
import base64
import time

st.set_page_config(
    page_title="Activity Dashboard PRO",
    page_icon="📊",
    layout="wide"
)

# ---------- Custom Professional Styling ----------
st.markdown("""
<style>
.main {
    background-color: #f4f6f9;
}
.big
