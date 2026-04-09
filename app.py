import plotly.express as px

if not df.empty:

    # Numeric conversion
    df["Target"] = pd.to_numeric(df["Target"], errors="coerce").fillna(0)

    pie = px.pie(
        df,
        names="District",
        values="Target",
        hole=0.4
    )

    pie.update_traces(
        textinfo="percent+label+value"
    )

    st.plotly_chart(pie, use_container_width=True)

else:
    st.warning("No data available")
