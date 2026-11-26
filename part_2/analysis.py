#!/usr/bin/env python3
# coding=utf-8

from matplotlib import pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import LogFormatterSciNotation, LogLocator, NullLocator
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
    df_copy['kraj'] = df_copy['p4a'].map(regions)
    df_copy = df_copy.drop_duplicates(subset='p1', keep='first')

    if verbose:
        size_mb = df_copy.memory_usage(deep=True).sum() / 1_000_000
        print(f"new_size={size_mb:.1f} MB")
    return df_copy

# Ukol 3: hlavni priciny nehod podle druhu vozidla
def plot_causes(df: pd.DataFrame, df_vehicles: pd.DataFrame,
                fig_location: str = None, show_figure: bool = False):
    """Docstring."""
    types = {2: "motocykl", 3: "osobní automobil",
         5: "nákladní automobil", 6: "nákladní automobil",
         7: "nákladní automobil"}
    causes = {1: "nezaviněná řidičem", 2: "nepřiměřená rychlost",
             3: "nesprávné předjíždění", 4: "nedání přednosti",
             5: "nesprávný způsob jízdy", 6: "technická závada"}
    df_vehicles = df_vehicles.assign(druh=df_vehicles["p44"].map(types))[["p1", "druh"]]
    df["pricina"] = df["p12"] // 100
    df["pricina"] = df["pricina"].map(causes)
    merged_df = pd.merge(df[["p1", "kraj", "pricina"]], df_vehicles, on="p1",
                         validate="1:m")
    merged_df = merged_df.dropna(subset="druh")

    grouped_df = merged_df.groupby(
        ["kraj", "pricina", "druh"])["p1"].agg("nunique")

    grouped_df = (grouped_df.rename("Počet nehod")).reset_index()

    kraje = ["PHA", "STC", "JHC", "PLK", "ULK", "HKK", "JHM",
             "MSK", "OLK", "ZLK", "VYS", "PAK", "LBK", "KVK"]
    druhy = ["motocykl", "osobní automobil", "nákladní automobil"]

    g = sns.catplot(
        data=grouped_df,
        x="kraj",
        y="Počet nehod",
        col="pricina",
        hue="druh",
        kind="bar",
        col_wrap=2,
        height=3.6,
        aspect=2.7,
        order=kraje,
        hue_order=druhy,
        col_order=list(causes.values()),
        sharex=False,
        sharey=False,
        palette=["#2a78d6", "#eb6834", "#1baf7a"],
    )
    g.set(yscale="log", xlabel="Kraj", ylabel="Počet nehod")
    sns.move_legend(g, "upper center", title=None, bbox_to_anchor=(0.5, 0.965), ncol=3)
    g.figure.subplots_adjust(top=0.85, wspace=0.25, hspace=0.45)
    g.set_titles("{col_name}")
    g.figure.suptitle("Hlavní příčiny nehod podle druhu vozidla", y=0.998)
    for ax in g.axes.flat:
        ax.tick_params(labelleft=True, labelbottom=True)
        ax.yaxis.set_major_locator(LogLocator(base=10, subs=(1.0, 0.2, 0.3, 0.6)))
        fmt = LogFormatterSciNotation(minor_thresholds=(12, 0.4))
        ax.yaxis.set_major_formatter(fmt)
        ax.yaxis.set_minor_locator(NullLocator())
        ax.tick_params(axis="y", which="both", labelsize=8)
        ax.grid(axis="y", which="major", color="0.8", linewidth=0.6)
        ax.set_axisbelow(True)
        ax.spines[["top", "right"]].set_visible(False)

    if fig_location:
        g.savefig(fig_location)
    if show_figure:
        plt.show()


# Ukol 4: vek osob a nasledky v jednotlivych letech
def plot_age(df: pd.DataFrame, df_consequences: pd.DataFrame,
             fig_location: str = None, show_figure: bool = False):
    """Plot consequences of car crashes by age and year."""
    consequences = {1: "usmrcení", 2: "těžké zranění", 3: "lehké zranění"}

    cleaned_consequences = df_consequences.copy()
    cleaned_consequences["nasledek"] = cleaned_consequences["p59g"].map(consequences)
    cleaned_consequences = cleaned_consequences.dropna(subset=["nasledek"])

    vek = pd.to_numeric(cleaned_consequences["p59d"], errors="coerce")
    cleaned_consequences = cleaned_consequences[vek.notna() & (vek >= 0)]
    cleaned_consequences["vekova_skupina"] = pd.cut(cleaned_consequences["vek"]
        if "vek" in cleaned_consequences else vek,
        bins=[0, 18, 25, 45, 65, np.inf],
        labels=["0-17", "18-24", "25-44", "45-64", "65+"],
        right=False)


    cleaned_df = df.copy()
    cleaned_df['rok'] = cleaned_df['date'].dt.year

    merged_df = (
        cleaned_consequences[
            ["p1", "vekova_skupina", "nasledek"]]
            .merge(cleaned_df[["p1", "rok"]], on="p1", validate="m:1")
    )

    merged_df = merged_df[merged_df["rok"] < 2026]
    merged_df["pocet_osob"] = 1
    merged_df = (
        merged_df.groupby(["vekova_skupina", "rok", "nasledek"])["pocet_osob"]
        .sum()
    )

    merged_df = (merged_df.rename("Počet osob")).reset_index()

    g = sns.catplot(
        data=merged_df,
        x="vekova_skupina",
        y="Počet osob",
        col="nasledek",
        hue="rok",
        kind="bar",
        height=4,
        aspect=1,
        #order=kraje,
        #hue_order=druhy,
        col_order=list(consequences.values()),
        sharex=False,
        sharey=False,
        palette="flare"
    )
    g.set_titles("Následek: {col_name}")
    g.set(xlabel="Věk osoby", ylabel="Počet osob")
    for ax in g.axes.flat:
        ax.tick_params(labelleft=True, labelbottom=True)
        ax.grid(axis="y", which="major", color="0.8", linewidth=0.6)
        ax.set_axisbelow(True)

    g.figure.subplots_adjust(wspace=0.25)

    if fig_location:
        g.savefig(fig_location)
    if show_figure:
        plt.show()


# Ukol 5: viditelnost (den / noc) v case
def plot_visibility(df: pd.DataFrame, fig_location: str = None,
                    show_figure: bool = False):
    pass


if __name__ == "__main__":
    # zde je ukazka pouziti, tuto cast muzete modifikovat podle libosti
    # skript nebude pri testovani pousten primo, ale budou volany konkreni
    # funkce.

    #df = load_data("data_23_26.zip", "nehody")
    #df_consequences = load_data("data_23_26.zip", "nasledky")
    #df_vehicles = load_data("data_23_26.zip", "Vozidla")
    #df2 = parse_data(df, True)
    #df_consequences.to_pickle("nasledky.pkl")
    #df_vehicles.to_pickle("vozidla.pkl")
    #df2.to_pickle("nehody_parsed.pkl")
    df_consequences = pd.read_pickle("nasledky.pkl")
    df_vehicles = pd.read_pickle("vozidla.pkl")
    df2 = pd.read_pickle("nehody_parsed.pkl")

    #plot_causes(df2, df_vehicles, "01_causes.png", True)
    plot_age(df2, df_consequences, "02_age.png", False)
    #plot_visibility(df2, "03_visibility.png")

# Poznamka:
# pro to, abyste se vyhnuli castemu nacitani muzete vyuzit napr
# VS Code a oznaceni jako bunky (radek #%%% )
# Pak muzete data jednou nacist a dale ladit jednotlive funkce
# Pripadne si muzete vysledny dataframe ulozit nekam na disk (pro ladici
# ucely) a nacitat jej naparsovany z disku
