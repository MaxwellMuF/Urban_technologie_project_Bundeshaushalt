import numpy as np
import pandas as pd
import streamlit as st



# -------------------------------------------- Funktions ---------------------------------------------------------
def string_contains_ignore_first_capital(df: pd.DataFrame, criteria: str) -> pd.DataFrame:
    if not criteria:
        return df
    user_df_filtered_1 = df[df["Zweckbestimmung"].str.contains(user_buzzword)]
    user_df_filtered_2 = df[df["Zweckbestimmung"].str.contains(user_buzzword[0].lower()+user_buzzword[1:])]
    user_df_filtered_3 = df[df["Zweckbestimmung"].str.contains(user_buzzword[0].upper()+user_buzzword[1:])]
    user_df_filtered_all = pd.concat([user_df_filtered_1, user_df_filtered_2, user_df_filtered_3], axis=0)
    user_df_filtered_all.drop_duplicates(inplace=True)

    return user_df_filtered_all


# -------------------------------------------- Streamlit page ---------------------------------------------------------

st.title("Look at raw data of every year", help="Why raw data? The processed data is particularly \
         interesting because it shows positions over several years. The raw data only shows one year. \
         However, as the same positions do not occur every year, the raw data shows more, i.e. \
         the entire budget for the year.\
         \nAnd where have the nice graphs gone? Well, if you only look at one year, you can't draw a timeline, right?")

with st.container(border=True):
    # Subtitle
    st.subheader("Which year do you want to look at?")
    # Selectbox 
    user_year = st.selectbox("Choose a year", [i for i in range(2012,2024)], index=11)
    # Load data
    user_df_year = pd.read_excel(f"infrastructure/data/data_raw/HR{user_year}.xlsx")
    # Show data
    st.dataframe(user_df_year)


st.header("Lets search for some buzzwords in raw data")
with st.container(border=True):
    user_buzzword = st.text_input("String Filter. Use words like: 'Verwaltung', 'Steuer', 'Kirche', 'IT', 'Digital', 'Zuschüsse'...",
                                value="", help='Search for positions that contain your word.\
                                Capitalization is not taken into account, i.e. "Steuer" and "steuer"\
                                are the same and vice versa. \
                                Note "IT" searches for "iT" and "IT" but not "it" (try "it" and find out why).')
    # Drop None rows
    user_df_year.dropna(subset="Zweckbestimmung", inplace=True)

    # Filter by column "Zweckbestimmung" with user-criteria-string
    user_df_year_filtered_all = string_contains_ignore_first_capital(df=user_df_year, criteria=user_buzzword)
    st.write(f"df_sub has {len(user_df_year_filtered_all)} rows containing str: {user_buzzword}")
  
    st.subheader(body="Here is the plotted data", 
                 help='If you do not enter a word, you will get the same table as above with one difference: \
                       we had to remove the None lines from "Zweckbestimmung". However, the row index remains the same, \
                       which is why row 1, that was displayed above, is missing here.')
    st.dataframe(user_df_year_filtered_all)



