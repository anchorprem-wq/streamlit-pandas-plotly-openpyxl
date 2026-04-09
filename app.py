st.subheader("📋 Filtered Data")

display_df = filtered_df.copy()
display_df["Date"] = display_df["Date"].dt.strftime("%d-%m-%Y")

html_table = display_df.to_html(index=False)

st.markdown("""
<style>
table {
    width: 100%;
}
th, td {
    white-space: normal !important;
    word-wrap: break-word;
}
</style>
""", unsafe_allow_html=True)

st.markdown(html_table, unsafe_allow_html=True)
