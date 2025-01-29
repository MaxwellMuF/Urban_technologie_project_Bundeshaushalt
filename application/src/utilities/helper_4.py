import pandas as pd
import streamlit as st
from tqdm import tqdm
import time

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
