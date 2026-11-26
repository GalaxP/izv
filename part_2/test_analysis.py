"""Focused tests for the data loading and plotting functions in analysis.py."""

import zipfile

import matplotlib

matplotlib.use("Agg")

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import analysis


def test_load_data_reads_years_and_drops_unnamed_columns(tmp_path):
    archive_path = tmp_path / "input.zip"
    with zipfile.ZipFile(archive_path, "w") as archive:
        for year in (2023, 2024, 2025, 2026):
            archive.writestr(
                f"{year}/Inehody.xls",
                "<table><tr><th>p1</th><th>value</th><th>Unnamed: 2</th></tr>"
                f"<tr><td>{year}</td><td>ok</td><td></td></tr></table>",
            )

    result = analysis.load_data(str(archive_path), "nehody")

    assert result["p1"].tolist() == [2023, 2024, 2025, 2026]
    assert result["value"].tolist() == ["ok"] * 4
    assert "Unnamed: 2" not in result.columns


def test_parse_data_converts_dates_deduplicates_and_preserves_input(capsys):
    source = pd.DataFrame(
        {
            "p1": [10, 10, 11],
            "p2a": ["01.01.2023", "02.01.2023", "03.01.2023"],
            "p4a": [6, 6, 19],
        }
    )
    original = source.copy(deep=True)

    result = analysis.parse_data(source, verbose=True)

    assert source.equals(original)
    assert result["p1"].tolist() == [10, 11]
    assert pd.api.types.is_datetime64_any_dtype(result["date"])
    assert result["date"].dt.strftime("%Y-%m-%d").tolist() == [
        "2023-01-01",
        "2023-01-03",
    ]
    assert "region" in result.columns
    assert result["region"].tolist() == ["JHM", "KVK"]
    assert capsys.readouterr().out.startswith("new_size=")


def _capture_plot_data(monkeypatch, seaborn_function):
    captured = {}
    original = getattr(analysis.sns, seaborn_function)

    def capture(*args, **kwargs):
        captured["data"] = kwargs["data"].copy()
        grid = original(*args, **kwargs)
        captured["grid"] = grid
        return grid

    monkeypatch.setattr(analysis.sns, seaborn_function, capture)
    return captured


def test_plot_causes_counts_unique_crashes_per_vehicle_type(monkeypatch):
    causes = pd.DataFrame(
        {
            "p1": range(1, 7),
            "p12": [100, 200, 300, 400, 500, 600],
            "region": ["PHA"] * 6,
        }
    )
    vehicles = pd.DataFrame(
        {
            "p1": [1, 1, 2, 3, 4, 5, 6],
            "p44": [3, 3, 2, 3, 5, 6, 7],
        }
    )
    captured = _capture_plot_data(monkeypatch, "catplot")

    try:
        analysis.plot_causes(causes, vehicles)
        grouped = captured["data"]
        passenger_cars = grouped[grouped["druh"] == "osobní automobil"]
        assert passenger_cars["Počet nehod"].sum() == 2
        assert len(grouped["pricina"].unique()) == 6
    finally:
        plt.close("all")


def test_plot_age_counts_people_in_valid_years_and_age_groups(monkeypatch):
    accidents = pd.DataFrame(
        {
            "p1": [1, 2, 3, 4],
            "date": pd.to_datetime(
                ["2023-01-01", "2024-01-01", "2025-01-01", "2026-01-01"]
            ),
        }
    )
    people = pd.DataFrame(
        {
            "p1": [1, 1, 2, 3, 4, 2, 3, 3],
            "p59d": ["17", "18", "24", "30", "65", "XX", "-1", "45"],
            "p59g": [1, 2, 2, 3, 1, 2, 2, 3],
        }
    )
    captured = _capture_plot_data(monkeypatch, "catplot")

    try:
        analysis.plot_age(accidents, people)
        grouped = captured["data"]
        assert grouped["Počet osob"].sum() == 5
        assert set(grouped["rok"]) == {2023, 2024, 2025}
        assert set(grouped["vekova_skupina"].astype(str)) == {
            "0-17",
            "18-24",
            "25-44",
            "45-64",
        }
    finally:
        plt.close("all")


def test_plot_visibility_aggregates_monthly_and_limits_regions(monkeypatch):
    dates = pd.to_datetime(
        [
            "2023-01-01",
            "2023-01-01",
            "2023-01-03",
            "2023-01-04",
            "2023-02-01",
            "2023-02-02",
            "2023-02-03",
            "2023-01-01",
            "2023-01-01",
            "2026-01-01",
            "2023-01-01",
        ]
    )
    data = pd.DataFrame(
        {
            "p1": [1, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            "date": dates,
            "region": ["JHM"] * 7 + ["MSK", "OLK", "JHM", "ZLK"],
            "p19": [1, 1, 2, 4, 3, 5, 7, 6, 2, 1, 4],
        }
    )
    captured = _capture_plot_data(monkeypatch, "relplot")

    try:
        analysis.plot_visibility(data)
        monthly = captured["data"]
        jhm_january = monthly[
            (monthly["region"] == "JHM")
            & (monthly["date"] == pd.Timestamp("2023-01-31"))
        ].set_index("viditelnost")["count"]

        assert jhm_january["den - nezhoršená"] == 1
        assert jhm_january["den - zhoršená"] == 1
        assert jhm_january["noc - s osvětlením"] == 1
        assert set(monthly["region"]) == {"JHM", "MSK", "OLK", "ZLK"}
        assert monthly["date"].max() < pd.Timestamp("2026-01-01")
        grid = captured["grid"]
        assert len(grid.axes) == 4
        expected_xlim = (
            mdates.date2num(pd.Timestamp("2023-01-01")),
            mdates.date2num(pd.Timestamp("2026-01-01")),
        )
        assert [text.get_text() for text in grid._legend.get_texts()] == [
            "den - nezhoršená",
            "den - zhoršená",
            "noc - s osvětlením",
            "noc - bez osvětlení",
        ]
        for axis in grid.axes:
            np.testing.assert_allclose(axis.get_xlim(), expected_xlim)
    finally:
        plt.close("all")
