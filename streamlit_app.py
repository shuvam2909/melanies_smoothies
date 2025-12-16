# Import python packages
import streamlit as st
import requests
import pandas as pd
from snowflake.snowpark.functions import col

# -----------------------------
# App Header
# -----------------------------
st.title("🥤 Customize Your Smoothie! 🥤")
st.write("Choose the fruits you want in your custom Smoothie!")

name_on_order = st.text_input("Name on Smoothie")
st.write("The name on your Smoothie will be:", name_on_order)

# -----------------------------
# Snowflake Connection
# -----------------------------
cnx = st.connection("snowflake")
session = cnx.session()

# -----------------------------
# Get Fruit Options
# -----------------------------
my_dataframe = (
    session
    .table("SMOOTHIES.PUBLIC.FRUIT_OPTIONS")
    .select(col("FRUIT_NAME"), col("SEARCH_ON"))
)

# Convert to Pandas
pd_df = my_dataframe.to_pandas()

# -----------------------------
# Multiselect (GUI shows FRUIT_NAME)
# -----------------------------
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    pd_df["FRUIT_NAME"].tolist(),
    max_selections=5
)

# -----------------------------
# Process Selection
# -----------------------------
if ingredients_list and name_on_order:

    ingredients_string = ""

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + " "

        # Get SEARCH_ON value
        search_on = pd_df.loc[
            pd_df["FRUIT_NAME"] == fruit_chosen, "SEARCH_ON"
        ].iloc[0]

        st.write(
            "The search value for",
            fruit_chosen,
            "is",
            search_on
        )

        # Call API using SEARCH_ON
        st.subheader(f"{fruit_chosen} Nutrition Information")
        smoothiefroot_response = requests.get(
            "https://my.smoothiefroot.com/api/fruit/" + search_on
        )

        st.dataframe(
            data=smoothiefroot_response.json(),
            use_container_width=True
        )

    st.write("### Ingredients:")
    st.write(ingredients_string)

    # -----------------------------
    # Insert Order
    # -----------------------------
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders (ingredients, NAME_ON_ORDER)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """

    time_to_insert = st.button("Submit Order")

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success("Your Smoothie is ordered! ✅")
