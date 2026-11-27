import sqlite3

import pandas as pd
import streamlit as st

DB_FILE = "rugby.db"


# ---------- Helper functions to talk to the database ----------

def get_data(sql, params=()):
    """Run a SELECT query and return the results as a table (DataFrame)."""
    conn = sqlite3.connect(DB_FILE)
    table = pd.read_sql_query(sql, conn, params=params)
    conn.close()
    return table


def change_data(sql, params=()):
    """Run an INSERT query and save the change."""
    conn = sqlite3.connect(DB_FILE)
    conn.execute(sql, params)
    conn.commit()
    conn.close()


# ---------- Page layout ----------

st.title("Rugby Players Database")

page = st.sidebar.radio("Choose a page", ["View players", "Add player", "Add country"])


# ---------- Page 1: View players ----------

if page == "View players":
    st.header("Players")

    countries = get_data("SELECT country_name FROM countries ORDER BY country_name")
    country_choices = ["All countries"] + countries["country_name"].tolist()
    chosen_country = st.selectbox("Filter by country", country_choices)

    if chosen_country == "All countries":
        players = get_data("SELECT name, age, caps, position, country, nickname FROM player_details ORDER BY name")
    else:
        players = get_data(
            "SELECT name, age, caps, position, country, nickname FROM player_details WHERE country = ? ORDER BY name",
            (chosen_country,),
        )

    st.write(f"Showing {len(players)} players")
    st.dataframe(players, hide_index=True)


# ---------- Page 2: Add player ----------

elif page == "Add player":
    st.header("Add a new player")

    countries = get_data("SELECT country_id, country_name FROM countries ORDER BY country_name")
    positions = get_data("SELECT position_id, position_name FROM positions ORDER BY position_id")

    with st.form("player_form", clear_on_submit=True):
        name = st.text_input("Name")
        age = st.number_input("Age", min_value=16, max_value=50, value=25)
        caps = st.number_input("Caps", min_value=0, value=0)
        position_name = st.selectbox("Position", positions["position_name"])
        country_name = st.selectbox("Country", countries["country_name"])
        submitted = st.form_submit_button("Add player")

    if submitted:
        if name.strip() == "":
            st.error("Please enter a name.")
        else:
            # Look up the ID numbers that match the names the user picked
            position_id = int(positions.loc[positions["position_name"] == position_name, "position_id"].iloc[0])
            country_id = int(countries.loc[countries["country_name"] == country_name, "country_id"].iloc[0])

            change_data(
                "INSERT INTO players (name, age, caps, position_id, country_id) VALUES (?, ?, ?, ?, ?)",
                (name.strip(), int(age), int(caps), position_id, country_id),
            )
            st.success(f"Added {name} to the database!")


# ---------- Page 3: Add country ----------

elif page == "Add country":
    st.header("Add a new country")

    with st.form("country_form", clear_on_submit=True):
        country_name = st.text_input("Country name")
        nickname = st.text_input("Nickname")
        submitted = st.form_submit_button("Add country")

    if submitted:
        if country_name.strip() == "":
            st.error("Please enter a country name.")
        else:
            try:
                change_data(
                    "INSERT INTO countries (country_name, nickname) VALUES (?, ?)",
                    (country_name.strip(), nickname.strip()),
                )
                st.success(f"Added {country_name}!")
            except sqlite3.IntegrityError:
                st.error("That country already exists.")
