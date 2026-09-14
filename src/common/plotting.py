# -*- coding: utf-8 -*-
"""中文字体、统一坐标轴与 PNG 保存，供各问画图调用。"""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib import font_manager


def setup_font():
    for fp in [
        Path(r"E:\msyh.ttc"),
        Path(r"C:\Windows\Fonts\msyh.ttc"),
        Path(r"C:\Windows\Fonts\simhei.ttf"),
    ]:
        if fp.exists():
            font_manager.fontManager.addfont(str(fp))
            name = font_manager.FontProperties(fname=str(fp)).get_name()
            plt.rcParams["font.family"] = name
            plt.rcParams["axes.unicode_minus"] = False
            return name
    plt.rcParams["axes.unicode_minus"] = False
    return None


def apply_style(dpi: int = 150):
    setup_font()
    plt.rcParams.update(
        {
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": True,
            "grid.color": "#e6edf3",
            "axes.axisbelow": True,
            "savefig.dpi": dpi,
            "savefig.bbox": "tight",
            "axes.unicode_minus": False,
        }
    )


def hour_ticks(ax):
    ticks = list(range(0, 25, 2))
    ax.set_xticks(ticks)
    ax.set_xticklabels([f"{h:02d}:00" for h in ticks])
    ax.set_xlim(0, 24)
    ax.set_xlabel("时刻")


def save_png(fig, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path)
    plt.close(fig)
