import numpy as np
import pandas as pd
import streamlit as st

# from domain.src import id_mapper

from application.src.utilities import helper_4 as helper4

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
    col1, col2 = st.columns(2)
    # Selectboxes
    with col1:
        begin_year = st.selectbox("Choose a year", [i for i in range(2012,2023)])
    with col2:
        end_year = st.selectbox("Choose a year", [i for i in range(int(begin_year)+1,2024)], index=2024-2-begin_year)

    if st.button("Make dataset", help="Please note: You can make as many dataset as you want, but just the last one is saved. Thus you can only analyse the last dataset on the other pages!"):
        st.session_state.own_dataset = helper4.pipeline((begin_year, end_year))

    if "own_dataset" in st.session_state:
        st.write(f"Here is your own dataset. It contains {st.session_state.own_dataset.shape[0]} positions:")
        st.dataframe(st.session_state.own_dataset)
