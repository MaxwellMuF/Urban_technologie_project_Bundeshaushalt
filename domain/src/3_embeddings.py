import numpy as np
import pandas as pd
import txtai
from time import time
from tqdm import tqdm
import os
import json

# fix BERT model issue
os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"

def load_json(path="DataBase_user_changes.json"):
    """Load json to python dict. Use encoding='utf-8' to handle german letters like 'ä' or 'ß' """
    with open(path, "r", encoding='utf-8') as file:
        dict_loaded = json.load(file)
    return dict_loaded

## Functions
def data_clearing(df):
    col_ist = [col for col in df.columns if col.startswith("Ist")][0]
    df = df.dropna(subset=col_ist, ignore_index=True)
    df = df[df[col_ist] > 1000]
    df.reset_index(inplace=True, drop=True)
    df[["Epl.", "Kap.", "Tit."]] = df[["Epl.", "Kap.", "Tit."]].astype(int, copy=False)
    df = df[["Epl.", "Kap.", "Tit.", col_ist, "Zweckbestimmung"]]
    return df

def make_id_col(df, year, ministry_dict, zahlen_dict):
    df["Zweckbestimmung"] = df["Zweckbestimmung"].str.normalize("NFKC")
    df["ministries"] = df["Epl."].astype(str).map(ministry_dict)
    df["id"] =  df["Tit."].astype(str).str.zfill(5) + df["Epl."].astype(str).str.zfill(2) + df["Kap."].astype(str).str.zfill(2)
    df["id_nlp_help"] =  df["Kap."].astype(str).str.zfill(2) + df["Tit."].astype(str).str.zfill(5)
    df["id_nlp_help"] =  df["ministries"]+" "+ df["id_nlp_help"].apply(map_numbers)
    # df["id_nlp_help"] = df["id"] + df[f"Ist 20{year}"].round(-3).div(1000).astype(int).astype(str)
    df["id_nlp"] = df["id_nlp_help"]+ " " + df["Zweckbestimmung"]
    df["id"] = df["id"].astype(int)
    return df

def mapp_ministries(df, ministry_dict):
    df["ministries"] = df["Epl."].map(ministry_dict)
    return df

def map_numbers(string):
    string = "".join([zahlen_dict[int(dig)] for dig in str(string)]) + " "
    return string

def data_preparing(file_name, year_sort, ministry_dict, zahlen_dict):
    if file_name.endswith(".xlsx"):
        df = pd.read_excel(f"infrastructure/data/data_raw/{file_name}") # HR20{year}.xlsx
    elif file_name.endswith(".csv"):
        df = pd.read_csv(f"infrastructure/data/data_raw/{file_name}") # infrastructure/data/data_raw\HR2012.xlsx
    df = data_clearing(df)
    df = make_id_col(df, year_sort, ministry_dict, zahlen_dict)
    df = df.sort_values(f"Ist 20{year_sort}", ascending=False)
    df.reset_index(inplace=True ,drop=True)
    return df

# Pipeline to make HR10y_on_id.csv, i.e. 10 years mapped to id column
def pipeline(range_years, zahlen_dict):
    df_result = pd.read_excel(f"infrastructure/data/data_raw/HR20{range_years[-1]}.xlsx")
    df_result = data_clearing(df_result)
    df_result = make_id_col(df_result, range_years[-1], ministry_dict, zahlen_dict)[["id","Epl.", "Kap.", "Tit.", "Zweckbestimmung", f"Ist 20{range_years[-1]}"]]
    df_mapped_on_id_reference = df_result.copy()
    print("Make HR10y_on_id.csv, i.e. mapp 10 years excel on id column")
    for year in tqdm(range(range_years[0], range_years[1])):
        df_i = pd.read_excel(f"infrastructure/data/data_raw/HR20{year}.xlsx")
        df_i = data_clearing(df_i)
        df_i = make_id_col(df_i, year, ministry_dict, zahlen_dict)[["id", "Zweckbestimmung", f"Ist 20{year}"]]
        df_i = df_i.rename(columns={"Zweckbestimmung" : f"20{year} Zweck"})
        df_result = pd.merge(df_result, df_i, on='id', how="inner")
        df_mapped_on_id = pd.merge(df_mapped_on_id_reference, df_i, on='id', how="inner")
        # df_mapped_on_id.to_csv(f"domain/data/mapped_on_id/HR20{year}_id_mapped_to_HR20{range_years[-1]}.csv")
    return df_result

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

if __name__ == "__main__":
    time_start = time()

    # init zahlen_dict and refernce year 2023
    zahlen_dict = make_zahlen_dict()
    ministry_dict = load_json("domain/data/ministry_mapper_dict.json")
    df_2023 = data_preparing("HR2023.xlsx", year_sort="23",ministry_dict=ministry_dict, zahlen_dict=zahlen_dict)
    df_2023 = mapper_handmade(df_2023)
    df_2023 = make_id_col(df_2023.copy(), year="23", ministry_dict=ministry_dict, zahlen_dict=zahlen_dict) # make id_nlp column again after mapper_handmade
    #df_2023.to_csv(f"domain/data/mapped_on_nlp/HR2023_nlp_reference_year.csv")

    # Make or load HR10y_on_id.csv, i.e. 10 years mapped on id
    try:
        df_merged_10y = pd.read_csv("domain/data/HR10y_on_id.csv")
        print("Loaded HR10y_on_id.csv")
    except:
        print("Make HR10y_on_id.csv")
        df_merged_10y = pipeline((12,23), zahlen_dict)
        df_merged_10y.to_csv("domain/data/HR10y_on_id.csv")
    # Make df with unmatched rows only
    df_2023_unmatched = df_2023[~df_2023["id"].isin(df_merged_10y["id"])].copy()
    df_2023_unmatched.to_csv(f"domain/data/mapped_on_nlp/HR2023_nlp_reference_year.csv")

    try:
        # try to load embeddings if they exist
        index_embedded_id_nlp = txtai.Embeddings(path="sentence-transformers/all-MiniLM-L6-v2", attn_implementation="eager")
        index_embedded_id_nlp.load("domain/data/embeddings/df_2023_unmatched_ist")
        print("Loaded embeddings:", index_embedded_id_nlp)

    except: # make embeddings if they not exist
        print("\nMake new embeddings \n")
        index_embedded_id_nlp = txtai.Embeddings(path="sentence-transformers/all-MiniLM-L6-v2", attn_implementation="eager")
        index_embedded_id_nlp.index(df_2023_unmatched["id_nlp"].tolist())

        print("Made embeddings:", index_embedded_id_nlp)
        index_embedded_id_nlp.save("domain/data/embeddings/df_2023_unmatched_ist")

    df_all = df_2023_unmatched.copy()
    # Load years and make batch search
    print(f"Mapp all years with NLP:")
    for year in tqdm(range(12,23)):
        df_i = data_preparing(f"HR20{year}.xlsx", year, ministry_dict, zahlen_dict)
        df_i = df_i[~df_i["id"].isin(df_merged_10y["id"])]
        if len(df_i) > len(df_2023_unmatched):
            df_i = df_i[:len(df_2023_unmatched)] 

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
        df_i[f"20{year} Zweck"] = [df_2023_unmatched.iloc[idx,5] if idx != None else None for idx in result_all]
        df_i = df_i.rename(columns={"id" : f"20{year} id"})
        df_i["id"] = [int(df_2023_unmatched.iloc[idx,6]) if idx != None else None for idx in result_all]

        df_i.to_csv(f"domain/data/mapped_on_nlp/HR20{year}_nlp_mapped_to_HR2023.csv")

        df_i = df_i[["id", f"20{year} id", f"20{year} Zweck", f"Ist 20{year}"]]
        print("\ndf_all len:", len(df_all))
        df_all = pd.merge(df_all, df_i, on='id', how="inner")
        #break
    
    df_all.to_csv("domain/data/HR10y_on_nlp.csv")
    time_end = time()
    time_script = time_end - time_start
    print(f"Script Time: {round(time_script//60)} [m] {round(time_script%60)} [s]")