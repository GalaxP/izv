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
Antropic Sonnet - revizia kodu pred odovzdanim
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


def format_func(value, tick_number):
    """
    Major ticks formatting function for graphs. Source: IZV presentation 4
    """
    N = int(np.round(2 * value / np.pi))
    if N >= 0 and N < 3:
        return {0: "0", 1: r"$\pi/2$", 2: r"$\pi$"}[N]
    elif N % 2 > 0:
        return rf"${N}\pi/2$"
    else:
        return rf"${N // 2}\pi$"


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
    fig, ax = plt.subplots()
    img = ax.imshow(
        S,
        origin="lower",
        extent=[t[0], t[-1], 0.5, S.shape[0] + 0.5],
        aspect="auto",
        cmap="coolwarm"
    )
    ax.set_title("Částečné součty Fourierovy řady")

    ax.set_xlabel(r"$t$")

    ax.set_xlim(0, 4*np.pi)
    ax.xaxis.set_major_locator(plt.MultipleLocator(np.pi / 2))
    ax.xaxis.set_minor_locator(plt.MultipleLocator(np.pi / 4))
    ax.xaxis.set_major_formatter(plt.FuncFormatter(format_func))
    ax.set_ylabel(r"Počet harmonických zložek")

    cbar = fig.colorbar(img, ax=ax, pad=0.03, aspect=20)
    cbar.set_label('Amplituda')

    if show_figure:
        plt.show()

    if save_path is not None:
        fig.savefig(save_path, dpi=300)

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

    fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)

    t = np.linspace(0, 4 * np.pi, 500)
    S = fourier_partial_sums(t, 5)

    f = np.sign(np.sin(t))  # idealny obdlznikovy signal

    y2 = S[-1]
    ax1.plot(t, f, "k--", alpha=.5, linewidth=.7)
    ax1.plot(t, np.where(y2 >= f, y2, np.nan), color="green", linewidth=.9)
    ax1.plot(t, np.where(y2 < f, y2, np.nan), color="red", linewidth=.9)

    ax1.set_ylabel(r"f(t), S$_{5}$(t)")

    ax1.set_xlim(0, 4*np.pi)
    ax1.set_ylim(-1.5, 1.5)
    ax2.set_ylim(-1.5, 1.5)
    ax1.spines['top'].set_visible(False)
    ax2.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    ax1.xaxis.set_major_locator(plt.MultipleLocator(np.pi / 2))
    ax1.xaxis.set_major_formatter(plt.FuncFormatter(format_func))

    ax1.grid(color="black", alpha=.2, linewidth=.5, linestyle="--")
    ax2.grid(color="black", alpha=.2, linewidth=.5, linestyle="--")

    error = y2 - f
    ax2.plot(t, error, "k", alpha=.4, linewidth=.6)
    ax2.set_ylabel(r"S$_{5}$(t) - f(t)")
    ax2.fill_between(
        t,
        np.where(error >= 0, error, np.nan),
        color="green",
        alpha=0.4
    )
    ax2.fill_between(
        t,
        np.where(error < 0, error, np.nan),
        color="red",
        alpha=0.4
    )

    ax2.set_xlabel(r"$t$")

    if show_figure:
        plt.show()

    if save_path is not None:
        fig.savefig(save_path, dpi=300)


class HTTPError(Exception):
    """Exception is thrown, if the HTTP request fails"""
    pass


def download_data() -> Dict[str, List[Any]]:
    """Stáhne tabulku meteorologických stanic a vrátí slovník se seznamy
    positions, lats, longs a heights."""
    
    url = "https://ehw.fit.vutbr.cz/izv/st_zemepis_cz.html"
    response = requests.get(url)
    if (response.status_code != 200):
        raise HTTPError

    # force utf-8 encoding
    response.encoding = 'utf-8'
    response_text = response.text

    result = {
        "positions": [],
        "lats": [],
        "longs": [],
        "heights": []
    }

    soup = BeautifulSoup(response_text, 'html.parser')
    table_rows = soup.select('tr.nezvyraznit')
    for row in table_rows:
        #  filter out empty lines
        children = [child for child in row.children if child.name is not None]
        result["positions"].append(children[0].find('strong').text)
        lats_string = children[2].text[:-1]
        # replace comma with a dot, so we can convert to float
        lats_float = float(lats_string.replace(",", "."))
        result["lats"].append(lats_float)

        longs_string = children[4].text[:-1]
        longs_float = float(longs_string.replace(",", "."))
        result["longs"].append(longs_float)

        heights_string = children[-1].text
        heights_float = float(heights_string.replace(",", "."))
        result["heights"].append(heights_float)

    return result


if __name__ == "__main__":
    # tady si můžete dělat libovolné změny. Nemodifikujte ale strukturu výše
    # (přidávat funkce můžete, ale při importu se nesmí nic spoštět!)
    A = fourier_partial_sums(np.linspace(-10, 10, 200), 2)
    B = fourier_partial_sums_bad(np.linspace(-10, 10, 200), 2)
    np.testing.assert_allclose(
        A,
        B,
        rtol=1e-12,
        atol=1e-12,
        err_msg="Vektorizace nefunguje!"
    )

    t = np.linspace(0, 4 * np.pi, 500)
    # Pro vizualizaci lze použít referenční pomalou implementaci.
    S = fourier_partial_sums_bad(t, 30)
    plot_fourier(S, t, show_figure=False, save_path="tmp_fourier.png")
    generate_approx(show_figure=False, save_path="tmp_approx.png")
