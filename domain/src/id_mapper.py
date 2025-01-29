import numpy as np
import pandas as pd
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

def make_id_col(df):
    df["Zweckbestimmung"] = df["Zweckbestimmung"].str.normalize("NFKC")
    df["id"] = df["Epl."].astype(str).str.zfill(2) + df["Kap."].astype(str).str.zfill(2) + df["Tit."].astype(str).str.zfill(5)
    df["id"] = df["id"] #.astype(int)
    return df

def data_preparing(file_name, year_sort):
    if file_name.endswith(".xlsx"):
        df = pd.read_excel(f"infrastructure/data/data_raw/{file_name}")
    elif file_name.endswith(".csv"):
        df = pd.read_csv(f"infrastructure/data/data_raw/{file_name}")
    df = data_clearing(df)
    df = make_id_col(df)
    df = df.sort_values(f"Ist {year_sort}", ascending=False)
    df.reset_index(inplace=True)
    return df

# Pipeline to make HR10y_on_id.csv, i.e. 12 years mapped to id column
def pipeline(range_years):
    # Choose reference year and pro process it
    df_result = pd.read_excel(f"infrastructure/data/data_raw/HR{range_years[-1]}.xlsx")
    df_result = data_clearing(df_result)
    df_result = make_id_col(df_result)[["id","Epl.", "Kap.", "Tit.", "Zweckbestimmung", f"Ist {range_years[-1]}"]]
    df_mapped_on_id_reference = df_result.copy()
    print("Make HR10y_on_id.csv, i.e. mapp 10 years excel on id column")
    # Iter all years and merge with reference year, safe every year id map
    for year in tqdm(range(range_years[0], range_years[1])):
        df_i = pd.read_excel(f"infrastructure/data/data_raw/HR{year}.xlsx")
        df_i = data_clearing(df_i)
        df_i = make_id_col(df_i)[["id", "Zweckbestimmung", f"Ist {year}"]]
        df_i = df_i.rename(columns={"Zweckbestimmung" : f"{year} Zweckbestimmung"})
        df_result = pd.merge(df_result, df_i, on='id', how="inner")
        df_mapped_on_id = pd.merge(df_mapped_on_id_reference, df_i, on='id', how="inner")
        df_mapped_on_id.to_csv(f"domain/data/mapped_on_id/HR{year}_id_mapped_to_HR{range_years[-1]}.csv")
    return df_result

if __name__ == "__main__":
    time_start = time()

    # Make HR10y_on_id.csv, i.e. 10 years mapped on id
    df_merged_10y = pipeline((2012,2023))
    df_merged_10y.to_csv("domain/data/HR10y_on_id.csv")
    # Make df with unmatched rows only
    # df_2023_unmatched = df_2023[~df_2023["id"].isin(df_merged_10y["id"])].copy()

    
    time_end = time()
    time_script = time_end - time_start
    print(f"Script Time: {round(time_script//60)} [m] {round(time_script%60)} [s]")