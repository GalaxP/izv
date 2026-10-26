#!/usr/bin/env python3
"""
Skript pro automaticke testovani prvni casti projektu.

Spousteni:
   pytest
nebo
   python3 -m pytest
"""
import part01
import numpy as np
import os
import pytest

def test_fourier_original():
    """Test puvodni referencni implementace"""
    A = part01.fourier_partial_sums_bad(np.linspace(-10, 10, 50), 5)

    assert A.shape == (5, 50)
    np.testing.assert_allclose(A[0, 0], 0.6926691915550987)
    np.testing.assert_allclose(A[2, 17], -0.3031533500352757)
    np.testing.assert_allclose(A[4, 25], 1.0355522070715575)

def test_fourier_your():
    """Test vase implementace"""
    A = part01.fourier_partial_sums(np.linspace(-10, 10, 50), 5)

    assert A.shape == (5, 50)
    np.testing.assert_allclose(A[0, 0], 0.6926691915550987)
    np.testing.assert_allclose(A[2, 17], -0.3031533500352757)
    np.testing.assert_allclose(A[4, 25], 1.0355522070715575)

def test_plot_fourier(tmp_path):
    """Test generovani grafu s castecnymi soucty Fourierovy rady"""
    t = np.linspace(0, 4 * np.pi, 500)
    A = part01.fourier_partial_sums_bad(t, 30)
    save_path = str(tmp_path / "tmp_fourier.png")
    part01.plot_fourier(A, t, show_figure=False, save_path=save_path)
    assert os.path.exists(save_path)


def test_generate_approx(tmp_path):
    """Test generovani grafu s aproximaci a jeji chybou"""
    save_path = str(tmp_path / "tmp_approx.png")
    part01.generate_approx(show_figure=False, save_path=save_path)
    assert os.path.exists(save_path)


def test_download():
    """Test stazeni dat"""
    data = part01.download_data()

    assert len(data["positions"]) == 40
    assert len(data["lats"]) == 40
    assert len(data["longs"]) == 40
    assert len(data["heights"]) == 40

    assert data["positions"][0] == "Cheb"
    assert data["lats"][0] == pytest.approx(50.0683)
    assert data["longs"][0] == pytest.approx(12.3913)
    assert data["heights"][0] == pytest.approx(483.0)

