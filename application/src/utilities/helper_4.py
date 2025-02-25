import time
import json
import txtai
import pandas           as pd
import streamlit        as st

from tqdm               import tqdm

import os
os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"
## Functions

# -------------------------------------------- Map years on id ---------------------------------------------------------
def data_clearing(df):
    col_ist = [col for col in df.columns if col.startswith("Ist")][0]
    df = df.dropna(subset=col_ist, ignore_index=True)
    df = df[df[col_ist] > 1000]
    df.reset_index(inplace=True)
    df[["Epl.", "Kap.", "Tit."]] = df[["Epl.", "Kap.", "Tit."]].astype(int, copy=False)
    df = df[["Epl.", "Kap.", "Tit.", col_ist, "Zweckbestimmung"]]
    return df

def make_id_col(df):
    df["Zweckbestimmung"] = df["Zweckbestimmung"].str.normalize("NFKC")
    df["id"] = df["Epl."].astype(str).str.zfill(2) + df["Kap."].astype(str).str.zfill(2) + df["Tit."].astype(str).str.zfill(5)
    df["id"] = df["id"] #.astype(int)
    return df


# Pipeline to make HR10y_on_id.csv, i.e. 12 years mapped to id column
def pipeline(range_years: tuple[int,int]):
    # Choose reference year and pro process it
    # streamlit process bar
    progress_text = "The dataset is being created. Please note that the creation of the dataset may take up to 30 seconds, depending on the number of years included."
    my_bar = st.progress(0, text=progress_text)
    my_bar_count = 0
    count_steps = 1 / (range_years[1] - range_years[0] +1)

    # process reference year
    df_result = pd.read_excel(f"infrastructure/data/data_raw/HR{range_years[-1]}.xlsx")
    df_result = data_clearing(df_result)
    df_result = make_id_col(df_result)[["id","Epl.", "Kap.", "Tit.", "Zweckbestimmung", f"Ist {range_years[-1]}"]]

    # streamlit process bar
    my_bar_count += count_steps
    my_bar.progress(my_bar_count, text=progress_text)
    # Iter all years and merge with reference year, safe every year id map
    for year in range(range_years[0], range_years[1]):
        df_i = pd.read_excel(f"infrastructure/data/data_raw/HR{year}.xlsx")
        df_i = data_clearing(df_i)
        df_i = make_id_col(df_i)[["id", "Zweckbestimmung", f"Ist {year}"]]
        df_i = df_i.rename(columns={"Zweckbestimmung" : f"{year} Zweckbestimmung"})
        df_result = pd.merge(df_result, df_i, on='id', how="inner")
        # streamlit process bar
        my_bar_count += count_steps
        my_bar.progress(my_bar_count, text=progress_text)
    time.sleep(1)
    my_bar.empty()
    return df_result


# -------------------------------------------- Map years on nlp ---------------------------------------------------------

def data_preparing(file_name, year_sort, ministry_dict, zahlen_dict):
    if file_name.endswith(".xlsx"):
        df = pd.read_excel(f"infrastructure/data/data_raw/{file_name}")
    elif file_name.endswith(".csv"):
        df = pd.read_csv(f"infrastructure/data/data_raw/{file_name}")
    df = data_clearing(df)
    df = make_id_col_nlp(df, year_sort, ministry_dict, zahlen_dict)
    df = df.sort_values(f"Ist {year_sort}", ascending=False)
    df.reset_index(inplace=True)
    return df

def make_id_col_nlp(df, year, ministry_dict, zahlen_dict):
    df["Zweckbestimmung"] = df["Zweckbestimmung"].str.normalize("NFKC")
    df["ministries"] = df["Epl."].astype(str).map(ministry_dict)
    df["id"] =  df["Tit."].astype(str).str.zfill(5) + df["Epl."].astype(str).str.zfill(2) + df["Kap."].astype(str).str.zfill(2)
    df["id_nlp_help"] =  df["Kap."].astype(str).str.zfill(2) + df["Tit."].astype(str).str.zfill(5)
    df["id_nlp_help"] =  df["ministries"]+" "+ df["id_nlp_help"].apply(map_numbers, args=(zahlen_dict,))
    # df["id_nlp_help"] = df["id"] + df[f"Ist {year}"].round(-3).div(1000).astype(int).astype(str)
    df["id_nlp"] = df["id_nlp_help"]+ " " + df["Zweckbestimmung"]
    df["id"] = df["id"].astype(int)
    return df

def load_json(path="DataBase_user_changes.json"):
    """Load json to python dict. Use encoding='utf-8' to handle german letters like 'ä' or 'ß' """
    with open(path, "r", encoding='utf-8') as file:
        dict_loaded = json.load(file)
    return dict_loaded

def map_numbers(string, zahlen_dict):
    string = "".join([zahlen_dict[int(dig)] for dig in str(string)]) + " "
    return string

# make number mapper
def make_zahlen_dict():
    zahlen = "null, eins, zwei, drei, vier, fünf, sechs, sieben, acht, neun".split(", ")
    zahlen_dict = { k:v for k,v in zip(range(10), zahlen)}
    return zahlen_dict

# Mapping dict hand made
def mapper_handmade(df):
    mapper_dict = {"Bürgergeld" : "Arbeitslosengeld II"}
    for key in mapper_dict:
        idx = df[df["Zweckbestimmung"] == key].index[0]
        df.loc[idx,"Zweckbestimmung"] = mapper_dict[key]
    return df

def pipeline_nlp(range_years: tuple[int,int]) -> pd.DataFrame:
    progress_text = "The dataset is being created. Please note that the creation of the dataset may take up to 20 minutes, depending on the number of years included."
    my_bar = st.progress(0, text=progress_text)
    my_bar_count = 0
    count_steps = 1 / (range_years[1] - range_years[0] +1)

    # init zahlen_dict and refernce year 2023
    zahlen_dict = make_zahlen_dict()
    ministry_dict = load_json("domain/data/ministry_mapper_dict.json")
    df_reference = data_preparing("HR2023.xlsx", str(range_years[1]), ministry_dict, zahlen_dict)
    df_reference = mapper_handmade(df_reference)
    df_reference = make_id_col_nlp(df_reference.copy(), str(range_years[1]), ministry_dict, zahlen_dict) # make id_nlp column again after mapper_handmade
    #df_reference.to_csv(f"domain/data/mapped_on_nlp/HR2023_nlp_reference_year.csv")

    # Make or load HR10y_on_id.csv, i.e. 10 years mapped on id
    try:
        df_merged_10y = pd.read_csv("domain/data/HR10y_on_id.csv")
        print("Loaded HR10y_on_id.csv")
    except:
        print("Make HR10y_on_id.csv")
        df_merged_10y = pipeline((12,23), zahlen_dict)
        df_merged_10y.to_csv("domain/data/HR10y_on_id.csv")
    # Make df with unmatched rows only
    df_reference_unmatched = df_reference[~df_reference["id"].isin(df_merged_10y["id"])].copy()
    df_reference_unmatched.to_csv(f"domain/data/mapped_on_nlp/HR{range_years[1]}_nlp_reference_year.csv")

    try:
        # try to load embeddings if they exist
        index_embedded_id_nlp = txtai.Embeddings(path="sentence-transformers/all-MiniLM-L6-v2", attn_implementation="eager")
        index_embedded_id_nlp.load(f"domain/data/embeddings/df_reference_{range_years[1]}_unmatched")
        print("Loaded embeddings:", index_embedded_id_nlp)

    except: # make embeddings if they not exist
        print("\nMake new embeddings \n")
        index_embedded_id_nlp = txtai.Embeddings(path="sentence-transformers/all-MiniLM-L6-v2", attn_implementation="eager")
        index_embedded_id_nlp.index(df_reference_unmatched["id_nlp"].tolist())

        print("Made embeddings:", index_embedded_id_nlp)
        index_embedded_id_nlp.save(f"domain/data/embeddings/df_reference_{range_years[1]}_unmatched")

    df_all = df_reference_unmatched.copy()
    # Load years and make batch search
    print(f"Mapp all years with NLP:")

    # streamlit process bar
    my_bar_count += count_steps
    my_bar.progress(my_bar_count, text=progress_text)
    for year in tqdm(range(range_years[0],range_years[1])):
        df_i = data_preparing(f"HR{year}.xlsx", year, ministry_dict, zahlen_dict)
        df_i = df_i[~df_i["id"].isin(df_merged_10y["id"])]
        if len(df_i) > len(df_reference_unmatched):
            df_i = df_i[:len(df_reference_unmatched)] 

        # Map each row of current year to vector index of 2023
        index_list_id_nlp = df_i["id_nlp"].to_list()
        result_all = [None]*len(index_list_id_nlp)

        for idx in range(len(index_list_id_nlp)):
            results_i = index_embedded_id_nlp.search(index_list_id_nlp[idx], limit=5)
            for pred in results_i:
                if pred[0] not in result_all and pred[1] > 0.85:
                    result_all[idx] = pred[0]
                    break

        # add mapped columns to df_i
        # map Zweckbestimmung
        df_i[f"{year} Zweck"] = [df_reference_unmatched.iloc[idx,5] if idx != None else None for idx in result_all]
        df_i = df_i.rename(columns={"id" : f"{year} id"})
        # map id from reference year
        df_i["id"] = [int(df_reference_unmatched.iloc[idx,7]) if idx != None else None for idx in result_all]

        # df_i.to_csv(f"domain/data/mapped_on_nlp/HR{year}_nlp_mapped_to_HR2023.csv")

        df_i = df_i[["id", f"{year} id", f"{year} Zweck", f"Ist {year}"]]
        print("\ndf_all len:", len(df_all))
        df_all = pd.merge(df_all, df_i, on='id', how="inner")

        my_bar_count += count_steps
        my_bar.progress(my_bar_count, text=progress_text)
        #break

    # df_all.to_csv("domain/data/HR10y_on_nlp.csv")

    time.sleep(1)
    my_bar.empty() #3627
    return df_all