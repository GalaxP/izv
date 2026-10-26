#!/usr/bin/env python3
"""
IZV část 1 projektu 2026
Autor: Alex Petráš (xpetraa00)

Podrobné zadání projektu je v samostatném dokumentu v e-learningu.
Dodržujte pravidla pro formátování a dokumentaci kódu v Pythonu.

Můžete použít vestavěné knihovny a knihovny uvedené v zadání projektu.
"""
from typing import Any, Dict, List

from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import numpy as np
from numpy.typing import NDArray
import requests


AI_USAGE = """
TODO: Uveďte, zda jste při řešení použili AI nástroje. Pokud ano, napište
které nástroje, k jakému účelu a u kterých částí řešení jste je použili
(např. revize kódu, hledání dokumentace nebo vysvětlení funkcí).
Pokud jste AI nepoužili, napište: „AI nástroje jsem nepoužil/a.“
"""


def fourier_partial_sums_bad(
    t: NDArray[np.float64], n_terms: int
) -> NDArray[np.float64]:
    """
    Referencni implementace, ktera je pomala a nevyuziva numpy efektivne;
    nezasahujte do ni!
    """
    S = np.zeros((n_terms, t.shape[0]))
    for n in range(n_terms):
        for j in range(t.shape[0]):
            for k in range(n + 1):
                h = 2 * k + 1
                S[n, j] += 4 / np.pi * np.sin(h * t[j]) / h
    return S


def fourier_partial_sums(
    t: NDArray[np.float64], n_terms: int
) -> NDArray[np.float64]:
    """
    Vypocita castecne soucty Fourierovy rady obdelnikoveho signalu.

    Radek n vysledne matice obsahuje aproximaci signalu sign(sin(t))
    pomoci prvnich n + 1 lichych harmonickych slozek.

    Args:
        t: vektor casovych bodu (delka T).
        n_terms: pocet harmonickych slozek (pocet radku vysledku).

    Returns:
        Matice o rozmeru (n_terms, T).

    Výpočet vektorizujte pomocí NumPy; nepoužívejte cykly přes časové body
    ani harmonické složky.
    """

    odd = np.arange(n_terms) * 2 + 1
    terms = np.sin(t[np.newaxis, :] * odd[:, np.newaxis]) / odd[:, np.newaxis]
    summed = np.cumsum(terms, axis=0)

    return (summed * 4) / np.pi


def plot_fourier(
    S: NDArray[np.float64],
    t: NDArray[np.float64],
    show_figure: bool = True,
    save_path: str | None = None,
) -> None:
    """
    Vizualizuje matici castecnych souctu jako barevnou mapu.

    Args:
        S: matice castecnych souctu o rozmeru (n_terms, T).
        t: rovnomerne rozlozeny vektor alespon dvou casovych bodu (delka T).
        show_figure: zda se ma graf zobrazit.
        save_path: cesta pro ulozeni grafu (None = neukladat).

    Matici vykreslete pomocí imshow s časem na vodorovné ose a počtem
    harmonických složek od 1 do n_terms na svislé ose. Pro interval
    0 až 4π nastavte značky na násobky π/2 a popisky vysázejte v LaTeXu.
    """
    pass


def generate_approx(
    show_figure: bool = True, save_path: str | None = None
) -> None:
    """
    Vykresli aproximaci obdelnikoveho signalu a jeji chybu.

    Horni podgraf: idealni signal (carkovane) a aproximace 5 harmonickymi,
    zelene pro S >= f, cervene pro S < f. Dolni podgraf: chyba aproximace.

    Aproximaci y2 ziskate jako fourier_partial_sums(t, 5)[-1]: funkce vrati
    matici peti castecnych souctu a posledni radek obsahuje soucet vsech
    peti lichych harmonickych slozek (1., 3., 5., 7. a 9. harmonicke).

    Args:
        show_figure: zda se ma graf zobrazit.
        save_path: cesta pro ulozeni grafu (None = neukladat).
    """
    pass


def download_data() -> Dict[str, List[Any]]:
    """Stáhne tabulku meteorologických stanic a vrátí slovník se seznamy
    positions, lats, longs a heights."""
    pass


if __name__ == "__main__":
    # tady si můžete dělat libovolné změny. Nemodifikujte ale strukturu výše 
    # (přidávat funkce můžete, ale při importu se nesmí nic spoštět!)
    #fourier_partial_sums(np.arange(10), 2)
    # make sure no more code is executed after this point
    #exit()

    A = fourier_partial_sums(np.linspace(-10, 10, 200), 2)
    B = fourier_partial_sums_bad(np.linspace(-10, 10, 200), 2)
    np.testing.assert_allclose(A, B, rtol=1e-12, atol=1e-12, err_msg="Vektorizace nefunguje!")


    t = np.linspace(0, 4 * np.pi, 500)
    # Pro vizualizaci lze použít referenční pomalou implementaci.
    S = fourier_partial_sums_bad(t, 30)
    plot_fourier(S, t, show_figure=True, save_path="tmp_fourier.png")
    generate_approx(show_figure=True, save_path="tmp_approx.png")
