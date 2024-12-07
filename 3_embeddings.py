import numpy as np
import pandas as pd
import txtai
from time import time
from tqdm import tqdm
import os

# fix BERT model issue
os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"

## Functions
def data_clearing(df):
    col_ist = [col for col in df.columns if col.startswith("Ist")][0]
    df = df.dropna(subset=col_ist, ignore_index=True)
    df = df[df[col_ist] > 1000]
    df.reset_index(inplace=True)
    df[["Epl.", "Kap.", "Tit."]] = df[["Epl.", "Kap.", "Tit."]].astype(int, copy=False)
    df = df[["Epl.", "Kap.", "Tit.", col_ist, "Zweckbestimmung"]]
    return df

def make_id_col(df, year, zahlen_dict):
    df["Zweckbestimmung"] = df["Zweckbestimmung"].str.normalize("NFKC")
    df["id"] = df["Tit."].astype(str).str.zfill(5) + df["Epl."].astype(str).str.zfill(2) + df["Kap."].astype(str).str.zfill(2)
    df["id_nlp_help"] = df["id"] + df[f"Ist 20{year}"].round(-3).div(1000).astype(int).astype(str)
    df["id_nlp"] = df["id_nlp_help"].apply(map_numbers)+ " " + df["Zweckbestimmung"]
    df["id"] = df["id"].astype(int)
    #df["id"] = df["Zweckbestimmung"].astype(str) +" "+ df["Tit."].astype(str).str.zfill(5) + df["Epl."].astype(str).str.zfill(2) + df["Kap."].astype(str).str.zfill(2)
    #df = df.drop(["Epl.", "Kap.", "Tit."], axis=1)
    return df


def map_numbers(string):
    string = "".join([zahlen_dict[int(dig)] for dig in str(string)]) + " "
    return string

def data_preparing(file_name, year_sort, zahlen_dict):
    if file_name.endswith(".xlsx"):
        df = pd.read_excel(f"data/data_raw/{file_name}") # HR20{year}.xlsx
    elif file_name.endswith(".csv"):
        df = pd.read_csv(f"data/data_raw/{file_name}")
    df = data_clearing(df)
    df = make_id_col(df, year_sort, zahlen_dict)
    df = df.sort_values(f"Ist 20{year_sort}", ascending=False)
    df.reset_index(inplace=True)
    return df

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
    df_2023 = data_preparing("HR2023.xlsx", year_sort="23", zahlen_dict=zahlen_dict)
    df_2023 = mapper_handmade(df_2023)
    df_2023 = make_id_col(df_2023.copy(), year="23", zahlen_dict=zahlen_dict) # make id_nlp column again after mapper_handmade
    df_merged_10y = pd.read_csv(f"data/HR10y_on_id.csv")
    df_2023_unmatched = df_2023[~df_2023["id"].isin(df_merged_10y["id"])].copy()

    try:
        # try to load embeddings if they exist
        index_embedded_id_nlp = txtai.Embeddings(path="sentence-transformers/all-MiniLM-L6-v2", attn_implementation="eager")
        index_embedded_id_nlp.load("data/embeddings/df_2023_unmatched_ist")
        print("Loaded embeddings:", index_embedded_id_nlp)

    except: # make embeddings if they not exist
        print("\nMake new embeddings \n")
        index_embedded_id_nlp = txtai.Embeddings(path="sentence-transformers/all-MiniLM-L6-v2", attn_implementation="eager")
        index_embedded_id_nlp.index(df_2023_unmatched["id_nlp"].tolist())

        print("Made embeddings:", index_embedded_id_nlp)
        index_embedded_id_nlp.save("data/embeddings/df_2023_unmatched_ist")

    # Load years and make batch search
    for year in tqdm(range(12,24)):
        print(f"Map index for year. {year}")
        df_i = data_preparing(f"HR20{year}.xlsx", year, zahlen_dict)
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
        print("Result[0] embedding search:", result_all[0])
        
        # user mapped index to add current year df to df_all
        print(df_2023_unmatched.iloc[0])
        if len(result_all) < len(df_2023_unmatched):
            result_all = result_all + [None] * (len(df_2023_unmatched) - len(result_all))
        df_i[f"Ist 20{year}"] = [df_2023_unmatched.iloc[idx,4] if idx != None else None for idx in result_all]
        df_i[f"20{year} Zweck"] = [df_2023_unmatched.iloc[idx,5] if idx != None else None for idx in result_all]
        df_i[f"20{year} id"] = [df_2023_unmatched.iloc[idx,6] if idx != None else None for idx in result_all].astype(int, copy=False)
        

        df_i.to_csv(f"data/vergleich_HR20{year}_s2_80_with_ist.csv")

        #test = pd.DataFrame(result_all).value_counts()
        #print(test)
        test2 = pd.DataFrame(result_all)[0].isna().sum()
        print("NaN number:", test2,"all_rows:", len(df_i))
        break


    time_end = time()
    print(f"Script Time: {round(time_end - time_start)}")