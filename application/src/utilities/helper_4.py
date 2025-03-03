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
    df_result = pd.read_excel(f"application/data/datasets/data_raw/HR{range_years[-1]}.xlsx")
    df_result = data_clearing(df_result)
    df_result = make_id_col(df_result)[["id","Epl.", "Kap.", "Tit.", "Zweckbestimmung", f"Ist {range_years[-1]}"]]

    # streamlit process bar
    my_bar_count += count_steps
    my_bar.progress(my_bar_count, text=progress_text)
    # Iter all years and merge with reference year, safe every year id map
    for year in range(range_years[0], range_years[1]):
        df_i = pd.read_excel(f"application/data/datasets/data_raw/HR{year}.xlsx")
        df_i = data_clearing(df_i)
        df_i = make_id_col(df_i)[["id", "Zweckbestimmung", f"Ist {year}"]]
        df_i = df_i.rename(columns={"Zweckbestimmung" : f"{year} Zweckbestimmung"})
        df_result = pd.merge(df_result, df_i, on="id", how="inner")
        # streamlit process bar
        my_bar_count += count_steps
        my_bar.progress(my_bar_count, text=progress_text)
    time.sleep(1)
    my_bar.empty()

    # label as id map
    df_result["Mapper"] = "id"
    df_result["Growth [%]"] = round(100 * df_result[f"Ist {range_years[1]}"] / df_result[f"Ist {range_years[0]}"])
    return df_result


# -------------------------------------------- Map years on nlp ---------------------------------------------------------

def data_preparing(file_name, year_sort, ministry_dict, zahlen_dict):
    if file_name.endswith(".xlsx"):
        df = pd.read_excel(f"application/data/datasets/data_raw/{file_name}")
    elif file_name.endswith(".csv"):
        df = pd.read_csv(f"application/data/datasets/data_raw/{file_name}")
    df = data_clearing(df)
    df = mapper_handmade(df)
    df = make_id_col_nlp(df, year_sort, ministry_dict, zahlen_dict)
    df = df.sort_values(f"Ist {year_sort}", ascending=False)
    df.reset_index(inplace=True)
    return df

def make_id_col_nlp(df, year, ministry_dict, zahlen_dict):
    df["Zweckbestimmung"] = df["Zweckbestimmung"].str.normalize("NFKC")
    df["ministries"] = df["Epl."].astype(str).map(ministry_dict)
    df["id"] = df["Epl."].astype(str).str.zfill(2) + df["Kap."].astype(str).str.zfill(2) + df["Tit."].astype(str).str.zfill(5)
    df["id_nlp_help"] =  df["Kap."].astype(str).str.zfill(2) +" "+ df["Tit."].astype(str).str.zfill(5)
    df["id_nlp_help"] = df["id_nlp_help"] # +" "+ df[f"Ist {year}"].round(-3).div(1000).astype(int).astype(str)
    df["id_nlp_help"] =  df["ministries"]+" "+ df["id_nlp_help"].apply(map_numbers, args=(zahlen_dict,))
    # df["id_nlp_help"] = df["id"] + df[f"Ist {year}"].round(-3).div(1000).astype(int).astype(str)
    df["id_nlp"] = df["id_nlp_help"]+ " " + df["Zweckbestimmung"]
    return df

def load_json(path="DataBase_user_changes.json"):
    """Load json to python dict. Use encoding='utf-8' to handle german letters like 'ä' or 'ß' """
    with open(path, "r", encoding="utf-8") as file:
        dict_loaded = json.load(file)
    return dict_loaded

def map_numbers(string, zahlen_dict):
    string = "".join([zahlen_dict[int(dig)] if dig != " " else " " for dig in str(string)]) + " "
    return string

# make number mapper
def make_zahlen_dict():
    zahlen = "null, eins, zwei, drei, vier, fünf, sechs, sieben, acht, neun".split(", ")
    zahlen_dict = { k:v for k,v in zip(range(10), zahlen)}
    return zahlen_dict

# Mapping dict hand made
def mapper_handmade(df):
    """Map hand made dict to df. continue if key is not in df."""
    mapper_dict_1 = {"Bürgergeld" : "Arbeitslosengeld Zwei"}
    mapper_dict_2 = {"Arbeitslosengeld II" : "Arbeitslosengeld Zwei"}
    # for key in mapper_dict:
    if df["Zweckbestimmung"].str.contains("Bürgergeld").any():
        idx = df[df["Zweckbestimmung"].str.contains("Bürgergeld")].index[0]
        df.loc[idx,"Zweckbestimmung"] = mapper_dict_1["Bürgergeld"]
    if df["Zweckbestimmung"].str.contains("Arbeitslosengeld II").any():
        idx = df[df["Zweckbestimmung"].str.contains("Arbeitslosengeld II")].index[0]
        df.loc[idx,"Zweckbestimmung"] = mapper_dict_2["Arbeitslosengeld II"]

    return df

def pipeline_nlp(df_all_id, range_years: tuple[int,int]) -> pd.DataFrame:
    path_tests = ""

    col_bar, col_spinner = st.columns([0.7,0.3])
    progress_text = "The dataset is being created. Please note that the creation of the dataset may take up to 25 minutes, \
                     depending on the number of years included"
    with col_bar:
        my_bar = st.progress(0, text=progress_text+".")
    my_bar_count = 0
    count_steps = 1 / (range_years[1] - range_years[0] +1)

    # init zahlen_dict and refernce year 2023
    zahlen_dict = make_zahlen_dict()
    ministry_dict = load_json("application/data/ministry_mapper_num_name.json")
    df_reference = data_preparing(f"HR{range_years[1]}.xlsx", str(range_years[1]), ministry_dict, zahlen_dict)
    df_reference = mapper_handmade(df_reference)
    df_reference = make_id_col_nlp(df_reference.copy(), str(range_years[1]), ministry_dict, zahlen_dict) # make id_nlp column again after mapper_handmade
    # df_reference.to_csv(f"domain/data/mapped_on_nlp/HR{range_years[1]}_nlp_reference_year_{path_tests}.csv")

    # Make or load HR10y_on_id.csv, i.e. 10 years mapped on id
    # try:
    #     df_merged_10y = pd.read_csv("domain/data/HR10y_on_id.csv")
    #     print("Loaded HR10y_on_id.csv")
    # except:
    #     print("Make HR10y_on_id.csv")
    #     df_merged_10y = pipeline((12,23), zahlen_dict)
    #     df_merged_10y.to_csv("domain/data/HR10y_on_id.csv")
    # Make df with unmatched rows only
    df_reference_unmatched = df_reference[~df_reference["id"].isin(df_all_id["id"])].copy()
    # df_reference_unmatched.to_csv(f"domain/data/mapped_on_nlp/HR{range_years[1]}_nlp_reference_year_{path_tests}_unmatch.csv")
    df_all_id.to_csv(f"domain/data/HR12y_on_id{path_tests}.csv")

    # try:
    #     # try to load embeddings if they exist
    #     index_embedded_id_nlp = txtai.Embeddings(path="sentence-transformers/all-MiniLM-L6-v2", attn_implementation="eager")
    #     index_embedded_id_nlp.load(f"domain/data/embeddings/df_reference_{range_years[1]}_unmatched")
    #     print("Loaded embeddings:", index_embedded_id_nlp)

    # except: # make embeddings if they not exist

    # Make new embeddings because unmatched changes with range of years
    print("\nMake new embeddings \n")
    with col_spinner:
        with st.spinner(f"Vector Index reference year {range_years[1]}", show_time=True):
            index_embedded_id_nlp = txtai.Embeddings(path="sentence-transformers/all-MiniLM-L6-v2", attn_implementation="eager")
            index_embedded_id_nlp.index(df_reference_unmatched["id_nlp"].tolist())

    print("Made embeddings:", index_embedded_id_nlp) # application\data\embeddings
    # index_embedded_id_nlp.save(f"application/data/embeddings/df_reference_{range_years[1]}_{range_years[1]}_unmatched_{path_tests}")

    df_all = df_reference_unmatched.copy()
    # Load years and make batch search
    print(f"Mapp all years with NLP:")

    # streamlit process bar
    my_bar_count += count_steps
    with col_bar:
        my_bar.progress(my_bar_count, text=progress_text+f" ({round(my_bar_count*100,2)}% done).")
    for year in tqdm(range(range_years[0],range_years[1])):
        df_i = data_preparing(f"HR{year}.xlsx", year, ministry_dict, zahlen_dict)
        df_i = df_i[~df_i["id"].isin(df_all_id["id"])]
        if len(df_i) > len(df_reference_unmatched):
            df_i = df_i[:len(df_reference_unmatched)] 

        # Map each row of current year to vector index of 2023
        index_list_id_nlp = df_i["id_nlp"].to_list()
        result_all = [None]*len(index_list_id_nlp)

        with col_spinner:
            with st.spinner(f"Embedd and map year {year}", show_time=True):
                for idx in range(len(index_list_id_nlp)):
                    results_i = index_embedded_id_nlp.search(index_list_id_nlp[idx], limit=10)
                    # if "Arbeitslosengeld" in index_list_id_nlp[idx]:
                    #     print(f"\n Map year: {year}")
                    #     print(results_i, [df_reference_unmatched.iloc[idx[0],5] if idx[0] != None else None for idx in results_i])
                    for pred in results_i:
                        if pred[0] not in result_all and pred[1] > 0.90:
                            result_all[idx] = pred[0]
                            break

        # add mapped columns to df_i
        # map Zweckbestimmung
        df_i[f"{year} Zweckbestimmung"] = [df_reference_unmatched.iloc[idx,5] if idx != None else None for idx in result_all]
        df_i = df_i.rename(columns={"id" : f"{year} id"})
        # map id from reference year
        df_i["id"] = [df_reference_unmatched.iloc[idx,7] if idx != None else None for idx in result_all]

        # df_i.to_csv(f"domain/data/mapped_on_nlp/HR{year}_nlp_mapped_to_HR2023_{path_tests}.csv")

        df_i = df_i[["id", f"{year} id", f"{year} Zweckbestimmung", f"Ist {year}"]]
        print("\ndf_all len:", len(df_all))
        df_all = pd.merge(df_all, df_i, on="id", how="inner")

        my_bar_count += count_steps
        with col_bar:
            my_bar.progress(my_bar_count, text=progress_text+f" ({round(my_bar_count*100,2)}% done).")
        #break

    
    # Lable mapper
    df_all["Growth [%]"] = round(100 * df_all[f"Ist {range_years[1]}"] / df_all[f"Ist {range_years[0]}"])
    df_all["Mapper"] = "id"
    df_all.to_csv(f"domain/data/HR12y_on_nlp{path_tests}.csv")

    time.sleep(1)
    my_bar.empty() #3627
    return df_all