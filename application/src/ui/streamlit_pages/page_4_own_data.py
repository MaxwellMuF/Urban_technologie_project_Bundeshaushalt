import numpy as np
import pandas as pd
import streamlit as st



# -------------------------------------------- Funktions ---------------------------------------------------------
def round_df(df):
    st.subheader("Round the price column")
    # Round the 'Ist' columns if round selected
    user_round_df = st.checkbox(label='Round the price column "Ist ..." of dataframe (recommended)',
                                value=True, 
                                help="The values are easier to compare if you round the decimal places. \
                                      If you want to have the exact data, e.g. because you want to download the table, \
                                      just uncheck this box.")
    # perform round if selected
    if user_round_df:
        ist_col = [col for col in df.columns if col.startswith("Ist")][0]
        return df.round({ist_col:0})
    else:
        return df

def string_contains_ignore_first_capital(df: pd.DataFrame, criteria: str) -> pd.DataFrame:
    if not criteria:
        return df
    user_df_filtered_1 = df[df["Zweckbestimmung"].str.contains(user_buzzword)]
    user_df_filtered_2 = df[df["Zweckbestimmung"].str.contains(user_buzzword[0].lower()+user_buzzword[1:])]
    user_df_filtered_3 = df[df["Zweckbestimmung"].str.contains(user_buzzword[0].upper()+user_buzzword[1:])]
    user_df_filtered_all = pd.concat([user_df_filtered_1, user_df_filtered_2, user_df_filtered_3], axis=0)
    user_df_filtered_all.drop_duplicates(inplace=True)

    return user_df_filtered_all

def filter_column_with_criteria(df, column, criteria):
    if criteria == "All":
        return df
    else:
        return df[df[column] == criteria].copy()

def filter_selector_ministry(df, column, label, helper_text, st_column):
    with st_column:
        selected_criteria= st.selectbox(label=label, 
                                               help=helper_text,
            # sorry for this list comp: several event catching if 'Tgr.' in title of some early years (e.g. 2012)
            options=["All"]+[int(float(str(i).replace("Tgr.", ""))) for i in df[column].unique() if not np.isnan(float(str(i).replace("Tgr.", "")))]) #.astype(int)
    return filter_column_with_criteria(df=df, column=column, criteria=selected_criteria)

def config_edit_df_user_posts() -> dict[str:st.column_config]:
    """Define the configuration of the columns for the editable dataframes"""
    config = {
        'Epl.' : st.column_config.NumberColumn('Epl.', width='small'),
        'Kap.' : st.column_config.NumberColumn('Kap.', width='small'),
        'Tit.' : st.column_config.NumberColumn('Tit.', width='small'),
        'Zweckbestimmung' : st.column_config.TextColumn('Zweckbestimmung', width='medium'),
        'Ist' : st.column_config.NumberColumn('Ist', width='medium'),
        'Seite' : st.column_config.NumberColumn('Seite', width='small')}
    
    return config

# -------------------------------------------- Streamlit page ---------------------------------------------------------

st.title("Look at raw data of every year", help="Why raw data? The processed data is particularly \
         interesting because it shows positions over several years. The raw data only shows one year. \
         However, as the same positions do not occur every year, the raw data shows more, i.e. \
         the entire budget for the year.\
         \nAnd where have the nice graphs gone? Well, if you only look at one year, you can't draw a timeline, right?")

# Widget with year selector and df show
with st.container(border=True):
    # Subtitle
    st.header("Which year do you want to look at?")
    # Selectbox 
    user_year = st.selectbox("Choose a year", [i for i in range(2012,2024)], index=11)
    # Load data
    user_df_year = pd.read_excel(f"infrastructure/data/data_raw/HR{user_year}.xlsx", engine="openpyxl")
    # Round if selected
    user_df_year = round_df(user_df_year)
    # Show data
    st.dataframe(user_df_year)


# Widget with string search and df show
with st.container(border=True):
    st.header("Lets search for some buzzwords in raw data")
    # User input for string search
    user_buzzword = st.text_input("String Filter. Use words like: 'Verwaltung', 'Steuer', 'Kirche', 'IT', 'Digital', 'Zuschüsse'...",
                                placeholder="Enter a search word here", help='Search for positions that contain your word.\
                                Capitalization is not taken into account, i.e. "Steuer" and "steuer"\
                                are the same and vice versa. \
                                Note "IT" searches for "iT" and "IT" but not "it" (try "it" and find out why).')
    # Drop None rows, needed to perform string search
    user_df_year.dropna(subset="Zweckbestimmung", inplace=True)

    # Filter by column "Zweckbestimmung" with user-criteria-string
    user_df_year_filtered_all = string_contains_ignore_first_capital(df=user_df_year, criteria=user_buzzword)
    st.write(f"df_sub has {len(user_df_year_filtered_all)} rows containing str: {user_buzzword}")
  
    st.subheader(body="Here is the plotted data", 
                 help='If you do not enter a word, you will get the same table as above with one difference: \
                       we had to remove the None lines from "Zweckbestimmung". However, the row index remains the same, \
                       which is why row 1, that was displayed above, is missing here.')
    # Show filtered df
    st.dataframe(user_df_year_filtered_all, use_container_width=True)

# Widget with ministry filter and df show
with st.container(border=True):
    st.header("Let's take a look at the individual ministries.")
    st.write("Here you can choose which ministry you would like to look at. \
             You can also select individual chapters and titles of this ministry.")
    # Make 3 streamlit columns, i.e. 3 elements horizontally next to each other
    select_einzelplan, select_kapitel, select_titel = st.columns(3)

    # Filters as user selected
    user_df_year_filtered = filter_selector_ministry(user_df_year, column="Epl.", label="Einzelplan (Epl.)", 
                             helper_text="This is the ministry", st_column=select_einzelplan)
    user_df_year_filtered = filter_selector_ministry(user_df_year_filtered, column="Kap.", label="Kapitel (Kap.)", 
                             helper_text="This is the chapter of the ministry", st_column=select_kapitel)
    user_df_year_filtered = filter_selector_ministry(user_df_year_filtered, column="Tit.", label="Titel (Tit.)", 
                             helper_text="This is the title for the booking. Repeating positions \
                                                (e.g. Vermischte Verwaltungsausgaben) have the same title and only occur \
                                                    once per chapter.", st_column=select_titel)
    # Show filter df
    st.dataframe(user_df_year_filtered, column_config=config_edit_df_user_posts(), use_container_width=True)
