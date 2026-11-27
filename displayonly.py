import sqlite3
import pandas as pd
import streamlit as st

st.title("Rugby Players")

with sqlite3.connect("rugby.db") as conn:
    # Show all players
    st.header("All players")
    table = pd.read_sql_query(
        "SELECT name, age, caps, position, country FROM player_details ORDER BY name",
        conn,
    )
    st.dataframe(table, hide_index=True)

    # Chart of average age per country
    st.header("Average age per country")
    chart_data = pd.read_sql_query(
        "SELECT country, ROUND(AVG(age), 1) AS average_age FROM player_details GROUP BY country",
        conn,
    )
    st.bar_chart(chart_data, x="country", y="average_age")
