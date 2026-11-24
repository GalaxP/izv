#!/usr/bin/env python3
# coding=utf-8

from matplotlib import pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import seaborn as sns
import numpy as np
import zipfile

# muzete pridat libovolnou zakladni knihovnu ci knihovnu predstavenou na prednaskach
# dalsi knihovny pak na dotaz

AI_USAGE = """
TODO: Uveďte, zda jste při řešení použili AI nástroje. Pokud ano, napište
které nástroje, k jakému účelu a u kterých částí řešení jste je použili
(např. revize kódu, hledání dokumentace nebo vysvětlení funkcí).
Pokud jste AI nepoužili, napište: „AI nástroje jsem nepoužil/a.“
"""

# Ukol 1: nacteni dat ze ZIP souboru


def load_data(filename: str, ds: str) -> pd.DataFrame:
    """Return a dataframe with data from {year}/I{ds}.xls,extracted from filename."""
    years = [2023, 2024, 2025, 2026]
    data = []
    with zipfile.ZipFile(filename, mode="r") as zip_file:
        for year in years:
            with zip_file.open(f'{year}/I{ds}.xls') as myfile:
                data.append(pd.read_html(myfile, encoding='cp1250')[0])
    df = pd.concat(data, ignore_index=True)
    return df.drop(columns=[c for c in df.columns if str(c).startswith('Unnamed')])

# Ukol 2: zpracovani dat


def parse_data(df: pd.DataFrame, verbose: bool = False) -> pd.DataFrame:
    """Return cleaned up dataframe."""
    regions = {0: "PHA", 1: "STC", 2: "JHC", 3: "PLK", 4: "ULK", 5: "HKK",
               6: "JHM", 7: "MSK", 14: "OLK", 15: "ZLK", 16: "VYS",
               17: "PAK", 18: "LBK", 19: "KVK"}

    df_copy = df.copy()
    converted = pd.to_datetime(df_copy['p2a'], format="%d.%m.%Y")
    df_copy['date'] = converted
    df_copy['region'] = df_copy['p4a'].map(regions)
    df_copy = df_copy.drop_duplicates(subset='p1', keep='first')

    if verbose:
        size_mb = df_copy.memory_usage(deep=True).sum() / 1_000_000
        print(f"new_size={size_mb:.1f} MB")
    return df_copy

# Ukol 3: hlavni priciny nehod podle druhu vozidla
def plot_causes(df: pd.DataFrame, df_vehicles: pd.DataFrame,
                fig_location: str = None, show_figure: bool = False):
    pass

# Ukol 4: vek osob a nasledky v jednotlivych letech
def plot_age(df: pd.DataFrame, df_consequences: pd.DataFrame,
             fig_location: str = None, show_figure: bool = False):
    pass

# Ukol 5: viditelnost (den / noc) v case
def plot_visibility(df: pd.DataFrame, fig_location: str = None,
                    show_figure: bool = False):
    pass


if __name__ == "__main__":
    # zde je ukazka pouziti, tuto cast muzete modifikovat podle libosti
    # skript nebude pri testovani pousten primo, ale budou volany konkreni
    # funkce.

    df = load_data("data_23_26.zip", "nehody")
    #print(df)
    #df_consequences = load_data("data_23_26.zip", "nasledky")
    #df_vehicles = load_data("data_23_26.zip", "Vozidla")
    df2 = parse_data(df, True)
    print(df2)

    #plot_causes(df2, df_vehicles, "01_causes.png")
    #plot_age(df2, df_consequences, "02_age.png", True)
    #plot_visibility(df2, "03_visibility.png")

# Poznamka:
# pro to, abyste se vyhnuli castemu nacitani muzete vyuzit napr
# VS Code a oznaceni jako bunky (radek #%%% )
# Pak muzete data jednou nacist a dale ladit jednotlive funkce
# Pripadne si muzete vysledny dataframe ulozit nekam na disk (pro ladici
# ucely) a nacitat jej naparsovany z disku
