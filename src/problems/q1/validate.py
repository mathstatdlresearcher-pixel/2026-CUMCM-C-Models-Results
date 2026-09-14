# -*- coding: utf-8 -*-
"""问题1 约束逐条核对：功率平衡、SOC 范围、充放互斥、目标值与模型一致。"""
from __future__ import annotations

import numpy as np
import pandas as pd

from common.constants import ETA_C, ETA_D, Q_MAX


def validate(df: pd.DataFrame, sol: dict) -> dict:
    L = df["load_kwh"].to_numpy()
    S = df["pv_kwh"].to_numpy()
    G, C, D, Suse, E = sol["G"], sol["C"], sol["D"], sol["Suse"], sol["E"]
    r_bal = G + Suse + D - L - C
    r_soc = E[1:] - E[:-1] - ETA_C * C + D / ETA_D
    gbase = np.maximum(L - S, 0.0)
    report = {
        "status": sol.get("message", ""),
        "obj": float(sol["obj"]),
        "grid_total": float(G.sum()),
        "charge_total": float(C.sum()),
        "discharge_total": float(D.sum()),
        "pv_use_total": float(Suse.sum()),
        "pv_avail_total": float(S.sum()),
        "pv_curt_total": float((S - Suse).sum()),
        "E0": float(E[0]),
        "E24": float(E[-1]),
        "E_min": float(E.min()),
        "E_max": float(E.max()),
        "C_max": float(C.max()),
        "D_max": float(D.max()),
        "simultaneous_max": float(np.minimum(C, D).max()),
        "balance_max_abs": float(np.abs(r_bal).max()),
        "soc_max_abs": float(np.abs(r_soc).max()),
        "G_min": float(G.min()),
        "battery_in": float(ETA_C * C.sum()),
        "battery_out": float(D.sum() / ETA_D),
        "base_grid": float(gbase.sum()),
        "base_cost": float((df["price"].to_numpy() * gbase).sum()),
        "Q_MAX": Q_MAX,
    }
    report["save_cost"] = report["base_cost"] - report["obj"]
    report["save_ratio"] = 100.0 * report["save_cost"] / max(report["base_cost"], 1e-9)
    return report
