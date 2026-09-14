# -*- coding: utf-8 -*-
"""问题2 全年滚动：每天用附件1 电价 + 附件2 实测，求解 48 h 随机规划并回测。"""
from __future__ import annotations

import numpy as np
import pandas as pd

from common.constants import DT, E_INIT, N, PI_SCEN
from common.io_data import load_attachment1, load_attachment2, load_price_att1
from problems.q2.backtest import backtest
from problems.q2.forecast import fit_simplex_weights, forecast_day, residual_quantiles
from problems.q2.milp import solve_day_milp


def run_year(max_days=None, price=None):
    dates, load_kw, pv_kw = load_attachment2()
    if price is None:
        price = load_price_att1()
    load_e, pv_e = load_kw * DT, pv_kw * DT
    nd = load_e.shape[0] if max_days is None else min(max_days, load_e.shape[0])
    Lhat = np.zeros_like(load_e)
    Phat = np.zeros_like(pv_e)
    wL = np.array([0.40, 0.25, 0.25, 0.10])
    wP = np.array([0.45, 0.20, 0.20, 0.15])
    att1 = load_attachment1()
    recs = []
    E0 = E_INIT
    for d in range(nd):
        if d >= 29 and (d == 29 or d % 7 == 0):
            wL = fit_simplex_weights(load_kw, d, default=wL)
            wP = fit_simplex_weights(pv_kw, d, default=wP)
        if d == 0:
            Lhat[d] = att1["load_kw"].to_numpy(float)[:N]
            Phat[d] = np.clip(att1["pv_kw"].to_numpy(float)[:N], 0, None)
        else:
            Lhat[d] = forecast_day(load_kw, d, wL)
            Phat[d] = forecast_day(pv_kw, d, wP)
        Lhat_e, Phat_e = Lhat * DT, Phat * DT
        eL = residual_quantiles(load_e, Lhat_e, d)
        eP = residual_quantiles(pv_e, Phat_e, d)
        load_d = np.clip(Lhat_e[d] + eL, 0.0, None)
        pv_d = np.clip(Phat_e[d] - eP, 0.0, None)
        load_n = np.clip(Lhat_e[d] + 0.5 * eL, 0.0, None)
        pv_n = np.clip(Phat_e[d] - 0.5 * eP, 0.0, None)
        pr = price[d] if np.ndim(price) == 2 else price
        pr2 = np.concatenate([pr, price[d + 1] if np.ndim(price) == 2 and d + 1 < len(price) else pr])
        sol = solve_day_milp(pr2, np.hstack([load_d, load_n]), np.hstack([pv_d, pv_n]), PI_SCEN, E0)
        q, C, D = sol["q"][:N], sol["C"][:N], sol["D"][:N]
        E = sol["E"][: N + 1]
        bt = backtest(q, C, D, load_e[d], pv_e[d], pr)
        recs.append(
            {
                "date": pd.Timestamp(dates.iloc[d]).strftime("%Y-%m-%d"),
                "q": q, "C": C, "D": D, "E": E, "h": bt["h"],
                "plan_cost": bt["plan_cost"], "em_cost": bt["em_cost"], "total_cost": bt["total_cost"],
                "Lhat": Lhat[d], "Phat": Phat[d], "L": load_kw[d], "PV": pv_kw[d], "price": pr,
            }
        )
        E0 = float(E[-1])
        if d == 0 or d % 30 == 29 or d == nd - 1:
            print(f"  {recs[-1]['date']}  J={bt['total_cost']:.1f}")
    return recs
