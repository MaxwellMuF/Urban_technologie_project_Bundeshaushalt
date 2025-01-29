import pandas as pd
import json
import openpyxl

df_2023 = pd.read_excel(f"infrastructure/data/data_raw/HR2023.xlsx", engine="openpyxl")

ministry_mapper_dict = {}

def mapper_number_name_to_number(ministry_mapper_dict):
    for ministry_idx in df_2023["Epl."].unique():
        ministry_name = df_2023[df_2023["Epl."] == ministry_idx].copy().reset_index(drop=True)
        for string in ["Bundesministerium ", "für ", "des ", "der ", "die ", "Der Bundesbeauftragte den ", " ."]:
            ministry_name.loc[:,"Zweckbestimmung"] = ministry_name["Zweckbestimmung"].str.replace(string, "")
        ministry_mapper_dict[str(ministry_name.loc[0,"Epl."])+" "+ministry_name.loc[0,"Zweckbestimmung"]] = int(ministry_name.loc[0,"Epl."])

    with open("application/data/ministry_mapper_dict.json", "w", encoding="utf-8") as file:
        json.dump(ministry_mapper_dict, file)

def mapper_name_to_number(ministry_mapper_dict):
    for ministry_idx in df_2023["Epl."].unique():
        ministry_name = df_2023[df_2023["Epl."] == ministry_idx].copy().reset_index(drop=True)
        ministry_mapper_dict[ministry_name.loc[0,"Zweckbestimmung"]] = int(ministry_name.loc[0,"Epl."])

    with open("application/data/ministry_mapper_dict.json", "w", encoding="utf-8") as file:
        json.dump(ministry_mapper_dict, file)

def mapper_number_to_name(ministry_mapper_dict):
    for ministry_idx in df_2023["Epl."].unique():
        ministry_name = df_2023[df_2023["Epl."] == ministry_idx].copy().reset_index(drop=True)
        ministry_mapper_dict[int(ministry_name.loc[0,"Epl."])] = ministry_name.loc[0,"Zweckbestimmung"]

    with open("domain/data/ministry_mapper_dict.json", "w", encoding="utf-8") as file:
        json.dump(ministry_mapper_dict, file)

# mapper_number_to_name(ministry_mapper_dict)
mapper_number_name_to_number(ministry_mapper_dict)