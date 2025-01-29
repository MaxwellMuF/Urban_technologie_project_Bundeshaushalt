import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import streamlit as st

# -------------------------------------------- Funktions ---------------------------------------------------------
def plot_5_positions(df, position_range=(1,5)):
    df_plot = df.iloc[position_range[0]-1:position_range[1]].set_index("Zweckbestimmung")[[f"Ist 20{year}" for year in range(12,24)]].T.copy() 
    # [[col for col in df.columns if col.startswith("Ist")]]
    # Setting a larger figure size and applying a style
    fig = plt.figure(figsize=(12, 8))  # Adjust the width and height as needed
    plt.style.use('ggplot')  # You can choose other styles like 'ggplot', 'fivethirtyeight', etc.

    # Plotting the DataFrame
    df_plot.plot(ax=plt.gca())  # Use the current Axes to apply size and style
    plt.title(f"Top {position_range[0]}-{position_range[1]} Positions", fontsize=16, fontweight='bold')  # Adding a title
    plt.xlabel("Years", fontsize=14)  # Customizing the x-axis label
    plt.ylabel("Booking value [€]", fontsize=14)  # Customizing the y-axis label

    # Customizing ticks and legend
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    plt.legend(fontsize=12, loc="best")  # Position the legend automatically

    # Show the plot
    st.pyplot(fig)
    return df_plot.T

def string_contains_ignore_first_capital(df: pd.DataFrame, criteria: str) -> pd.DataFrame:
    if not criteria:
        return df
    user_df_filtered_1 = df[df["Zweckbestimmung"].str.contains(user_buzzword)]
    user_df_filtered_2 = df[df["Zweckbestimmung"].str.contains(user_buzzword[0].lower()+user_buzzword[1:])]
    user_df_filtered_3 = df[df["Zweckbestimmung"].str.contains(user_buzzword[0].upper()+user_buzzword[1:])]
    user_df_filtered_all = pd.concat([user_df_filtered_1, user_df_filtered_2, user_df_filtered_3], axis=0)
    user_df_filtered_all.drop_duplicates(inplace=True)

    return user_df_filtered_all

def plot_kategory(df, str_kategory):
    # st.write(f"df_sub has {len(df[df['Zweckbestimmung'].str.contains(str_kategory)])} rows containing str: {str_kategory}")
    # Fix upper / lower case issue:
    user_df_filtered_all = string_contains_ignore_first_capital(df, str_kategory)

    # Print the number of rows
    st.write(f"df_sub has {len(user_df_filtered_all)} rows containing str: {str_kategory}")

    df_plot_all = user_df_filtered_all[["id", 'Epl.', 'Kap.', 'Tit.',"Zweckbestimmung"]+\
                                       [f"Ist 20{year}" for year in range(12,24)]] # use range f"" for right col order
    df_plot_sum = df_plot_all.drop(columns=["id",'Epl.','Kap.','Tit.',"Zweckbestimmung"])\
                             .sum(axis=0).rename(str_kategory)
    
    # Setting a larger figure size and applying a style
    fig = plt.figure(figsize=(12, 8))  # Adjust the width and height as needed
    plt.style.use('ggplot')  # You can choose other styles like 'ggplot', 'fivethirtyeight', etc.

    # Plotting the DataFrame
    df_plot_sum.plot(ax=plt.gca())  # Use the current Axes to apply size and style
    plt.title(f"Sum all positions containing \'{str_kategory}\'", fontsize=16, fontweight='bold')  # Adding a title
    plt.xlabel("Years", fontsize=14)  # Customizing the x-axis label
    plt.ylabel("Booking value [€]", fontsize=14)  # Customizing the y-axis label

    # Customizing ticks and legend
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    plt.legend(fontsize=12, loc="best")  # Position the legend automatically

    # Show the plot
    st.pyplot(fig)

    return df_plot_all

def filter_column_with_criteria(df, column, criteria):
    if criteria == "All":
        return df
    else:
        return df[df[column] == criteria].copy()

def filter_selector_ministry(df, column, label, helper_text, st_column):
    with st_column:
        selected_criteria= st.selectbox(label=label, 
                                               help=helper_text, 
                                               options=["All"]+[int(i) for i in df[column].unique() if not np.isnan(i)]) #.astype(int)
    return filter_column_with_criteria(df=df, column=column, criteria=selected_criteria)

def config_edit_df_user_posts() -> dict[str:st.column_config]:
    """Define the configuration of the columns for the editable dataframes"""
    config = {
        'Epl.' : st.column_config.NumberColumn('Epl.', width='small'),
        'Kap.' : st.column_config.NumberColumn('Kap.', width='small'),
        'Tit.' : st.column_config.NumberColumn('Tit.', width='small'),
        'Zweckbestimmung' : st.column_config.TextColumn('Zweckbestimmung', width='medium'),
        'Ist' : st.column_config.NumberColumn('Ist', width='medium'),
        'Seite' : st.column_config.NumberColumn('Seite', width='small'),
        'Zweck' : st.column_config.TextColumn('Zweck', width='medium')}
    
    return config
# -------------------------------------------- Streamlit page ---------------------------------------------------------

if "df_12y" not in st.session_state:
    # Load data
    df_2023 = pd.read_excel("infrastructure/data/data_raw/HR2023.xlsx", engine="openpyxl")
    df_id = pd.read_csv("domain/data/HR10y_on_id.csv", index_col="Unnamed: 0")
    df_nlp = pd.read_csv("domain/data/HR10y_on_nlp.csv", index_col="Unnamed: 0")

    # Data processing
    df_nlp.drop(["id_nlp_help", "id_nlp"], axis=1, inplace=True)
    df_12y = pd.concat([df_id, df_nlp], axis=0, ignore_index=True)

    st.session_state["df_2023"] = df_2023
    st.session_state["df_12y"] = df_12y.sort_values("Ist 2023", ascending=False)

if "df_12y_round" not in st.session_state:
    price_cols = [col for col in st.session_state.df_12y.columns if col.startswith("Ist")]
    st.session_state.df_12y_round = st.session_state.df_12y.round({price_col:0 for price_col in price_cols}).astype({price_col:"int64" for price_col in price_cols}, copy=True)


# Check how much volumn of booking 2023 are mapped and round checkbox
st.title("Bundeshaushalt over 12 years")
with st.container(border=True):
    # money_mapped = round(st.session_state.df_12y["Ist 2023"].sum() / st.session_state.df_2023["Ist 2023"].sum(), 3)
    # st.write(f"Persentage of Budget 23_mapped / 23_all: {money_mapped}")
    # st.write(f"Rufly {round(money_mapped*100)}% of the money is mapped")
    st.subheader("Round the price columns")
    # Round the 'Ist' columns if round selected
    user_round_df = st.checkbox(label='Round all the price columns "Ist ..." of dataframe (recommended)',
                                value=True, 
                                help="The values are easier to compare if you round the decimal places. \
                                      If you want to have the exact data, e.g. because you want to download the table, \
                                      just uncheck this box.")
    if user_round_df:
        df_12y = st.session_state.df_12y_round
    else:
        df_12y = st.session_state.df_12y


# Select top 1-5 or 6-10 etc.
with st.container(border=True):
    st.header("The biggest Positions:")
    user_top_positions = st.select_slider(label="Choose 5 of the biggest positions",
                                          options=[f"{i}-{i+4}" for i in range(1,50,5)],
                                          help="Select the 1-5 or 6-10 or 11-15 biggest positions. \
                                                These selected positions are visualized. \
                                                Below the graph you will find the visualized table.")
    st.write(f"Selected: {user_top_positions}")
    user_top_positions_first_num = int(user_top_positions[:2].replace("-",""))
    user_df_plotted_1 = plot_5_positions(df_12y, (user_top_positions_first_num, 4 + user_top_positions_first_num))
    st.subheader(body="Here is the plotted data", 
                 help="This table behaves almost like a pivot excel. You can sort a column by click on it and so on.\
                       If you hover over the table, you will see three functions at the top right above the table: \
                       Download, Search and Fullscreen.")
    # [[col for col in df.columns if col.startswith("Ist")]]
    column_config_plot_1 = {col : st.column_config.NumberColumn(width=110) for col in user_df_plotted_1.columns if col.startswith("Ist")}
    column_config_plot_1["Zweckbestimmung"] = st.column_config.TextColumn(width=150)
    st.dataframe(user_df_plotted_1, column_config=column_config_plot_1, use_container_width=True)


# String Filer: strings containing buzzword
with st.container(border=True):
    st.header("Lets search for some buzzwords")
    user_buzzword = st.text_input(label='Enter words like: "Steuer", "Kirche", "IT", "Digital", "Zuschüsse"...',
                                  value='Verwaltung', 
                                  help='Search for positions that contain your word.\
                                        Capitalization is not taken into account, i.e. "Steuer" and "steuer"\
                                        are the same and vice versa. \
                                        Note "IT" searches for "iT" and "IT" but not "it" (try "it" and find out why).')

    user_df_plotted_2 = plot_kategory(df_12y, user_buzzword)
    st.subheader("Here is the plotted data")
    column_config_plot_1 = {col : st.column_config.NumberColumn(width=110) for col in user_df_plotted_1.columns if col.startswith("Ist")}
    column_config_plot_1["Zweckbestimmung"] = st.column_config.TextColumn(width=150)
    st.dataframe(user_df_plotted_2, column_config=column_config_plot_1, use_container_width=True)


# Widget with ministry filter and df show
with st.container(border=True):
    st.header("Let's take a look at the individual ministries.")
    st.write("Here you can choose which ministry you would like to look at. \
             You can also select individual chapters and titles of this ministry.")
    # Make 3 streamlit columns, i.e. 3 elements horizontally next to each other
    select_einzelplan, select_kapitel, select_titel = st.columns(3)

    df_12y_filter = df_12y.drop([f"{year} id" for year in range(2012,2023)], axis=1) #.copy()
    # Filters as user selected
    user_df_year_filtered = filter_selector_ministry(df_12y_filter, column="Epl.", label="Einzelplan (Epl.)", 
                             helper_text="This is the ministry", st_column=select_einzelplan)
    user_df_year_filtered = filter_selector_ministry(user_df_year_filtered, column="Kap.", label="Kapitel (Kap.)", 
                             helper_text="This is the chapter of the ministry", st_column=select_kapitel)
    user_df_year_filtered = filter_selector_ministry(user_df_year_filtered, column="Tit.", label="Titel (Tit.)", 
                             helper_text="This is the title for the booking. Repeating positions \
                                                (e.g. Vermischte Verwaltungsausgaben) have the same title and only occur \
                                                    once per chapter.", st_column=select_titel)
    # Show filter df
    for year in range(2012,2023):
        column_config_plot_1[f'{year} Zweck'] = st.column_config.TextColumn(f'{year} Zweck', width='medium')
    st.dataframe(user_df_year_filtered, column_config=column_config_plot_1, use_container_width=True,
                 column_order=["Epl.","Kap.","Tit.", "Zweckbestimmung"]+\
                              [f"Ist {year}" for year in range(2012,2024)]+\
                              [f"{year} Zweck" for year in range(2012,2023)])
    ist_col = "Ist 2023" #[col for col in user_df_year_filtered.columns if col.startswith("Ist")][0]
    sum_all_positions = int(user_df_year_filtered[ist_col].sum())
    st.write(f"The table above shows a total of {user_df_year_filtered.shape[0]:4} selected positions with a total budget of {sum_all_positions:15}, \
             \nthat means {int(sum_all_positions//1e9)} billions {int(sum_all_positions%1e9//1e6)} millions and {int(sum_all_positions%1e6//1e3)} thousands. \
             Note, this is the sum of the reference year 2023.")

    plot_kategory(user_df_year_filtered, "")

with st.container(border=True):
    st.subheader("Quick Calculator")
    c1, c2, c3, c4, c5 = st.columns([3,3,3,1,3])

    with c1:
        value_1 = st.text_input("First Number", placeholder="5")
    with c3:
        value_2 = st.text_input("Second Number", placeholder="10")
    with c2:
        operator = st.selectbox("Operator", options=["+", "-", "*", "/"], placeholder="+")
    with c4:
        st.text_input("is",value="=")
    with c5:
        try:
            if operator == "+":
                result = float(value_1)+float(value_2)
            elif operator == "-":
                result = float(value_1)-float(value_2)
            elif operator == "*":
                result = float(value_1)*float(value_2)
            elif operator == "/":
                result = float(value_1)/float(value_2)
            else:
                result = 15
        except:
            result = "15"
        st.text_input("Result",value=str(result), placeholder="15")