# -*- coding: utf-8 -*-
"""问题1 插图：电价与购电、光伏/负荷/净负荷、SOC、充放电功率。"""
from __future__ import annotations

import numpy as np

from common.constants import DT, E_INIT, E_MAX, E_MIN, N, Q_MAX
from common.paths import figures_dir
from common.plotting import apply_style, hour_ticks, save_png


def draw_core_figures(df, sol, report, tab2):
    apply_style()
    figdir = figures_dir("q1")
    t = df["hour"].to_numpy() + DT / 2
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(10.6, 4.0))
    ax.plot(t, df["price"], color="#b91c1c", lw=1.6)
    hour_ticks(ax)
    ax.set_ylabel("元/kWh")
    ax.set_title("图1　电价", loc="left", fontweight="semibold")
    save_png(fig, figdir / "fig01_price.png")

    fig, ax = plt.subplots(figsize=(10.6, 4.0))
    ax.plot(t, df["load_kw"], color="#1f4e79", lw=1.2, label="负荷")
    ax.plot(t, df["pv_kw"], color="#c9a227", lw=1.2, label="光伏")
    hour_ticks(ax)
    ax.legend()
    ax.set_ylabel("kW")
    ax.set_title("图2　负荷与光伏", loc="left", fontweight="semibold")
    save_png(fig, figdir / "fig02_load_pv.png")

    fig, ax = plt.subplots(figsize=(10.6, 4.0))
    ax.bar(t, sol["G"], width=DT * 0.9, color="#2c5f8a")
    hour_ticks(ax)
    ax.set_ylabel("kWh")
    ax.set_title("图3　计划购电 $G_t$", loc="left", fontweight="semibold")
    save_png(fig, figdir / "fig03_grid.png")

    tn = np.arange(N + 1) * DT
    fig, ax = plt.subplots(figsize=(10.6, 4.2))
    ax.fill_between(tn, E_MIN, E_MAX, color="#eef2ff")
    ax.plot(tn, sol["E"], color="#4c3d8a", lw=1.8)
    ax.axhline(E_INIT, color="#64748b", ls="--")
    hour_ticks(ax)
    ax.set_ylabel("kWh")
    ax.set_ylim(0, 12000)
    ax.set_title("图4　储电量", loc="left", fontweight="semibold")
    save_png(fig, figdir / "fig04_soc.png")

    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    ax.bar(["无储能", "MILP"], [report["base_cost"], report["obj"]], color=["#94a3b8", "#2c5f8a"])
    ax.set_ylabel("元")
    ax.set_title("图5　购电费", loc="left", fontweight="semibold")
    save_png(fig, figdir / "fig05_cost.png")
