# -*- coding: utf-8 -*-
"""问题3 日内滚动：在 0/6/12/18 点用最新预报重解，已过时段按实测执行。

三种策略（S1/S2/S3）对应不同的电价与负荷信息假设。
"""
from __future__ import annotations

import numpy as np

from common.constants import DT, ISSUE_HOURS, LAMBDA_EM, N, PRICE_DOWN, PRICE_UP, TAU
from common.io_data import hourly_to_10min
from common.storage import execute_window
from problems.q3.milp import solve_initial, solve_rolling


def simulate_day(price, price_next, load_e, pv_e, fc_day, pv_kw_day, E0, issue_hours=ISSUE_HOURS):
    dplus_all = np.zeros(N)
    dminus_all = np.zeros(N)
    adj_cost = 0.0
    C = np.zeros(N)
    D = np.zeros(N)
    H = np.zeros(N)
    Suse = np.zeros(N)
    E = np.zeros(N + 1)
    E[0] = float(E0)
    hat_kw = hourly_to_10min(fc_day[0], 0, float(pv_kw_day[0]))
    prh_next = price_next if price_next is not None else price
    # 初始计划用当日电价拼接次日电价
    from problems.q3.milp import solve_horizon

    Lh = np.concatenate([load_e, load_e])
    Ph = np.concatenate([hat_kw * DT, hat_kw * DT])
    prh = np.concatenate([price, prh_next])
    sol0 = solve_horizon(prh, Lh, Ph, E[0], G_prev=None, n_commit=2 * N)
    G = sol0["G"][:N].copy()
    G0 = G.copy()
    allowed = set(issue_hours)
    for k, (hour, t0) in enumerate(zip(ISSUE_HOURS, TAU)):
        t1 = TAU[k + 1] if k < 3 else N
        if k >= 1 and hour in allowed:
            hat_kw = hourly_to_10min(fc_day[k], hour, float(pv_kw_day[t0]))
            Lh = np.concatenate([load_e[t0:], load_e])
            Ph = np.concatenate([hat_kw[t0:] * DT, hat_kw * DT])
            prh = np.concatenate([price[t0:], prh_next])
            m = N - t0
            roll = solve_horizon(prh, Lh, Ph, E[t0], G_prev=G[t0:], n_commit=m)
            G = G.copy()
            G[t0:] = roll["G"][:m]
            dp, dm = np.zeros(N), np.zeros(N)
            dp[t0:] = roll["dplus"]
            dm[t0:] = roll["dminus"]
            dplus_all += dp
            dminus_all += dm
            adj_cost += float(np.dot(PRICE_UP * price, dp) - np.dot(PRICE_DOWN * price, dm))
        c_w, d_w, h_w, s_w, e_w = execute_window(G, load_e, pv_e, E[t0], t0, t1)
        C[t0:t1] = c_w[t0:t1]
        D[t0:t1] = d_w[t0:t1]
        H[t0:t1] = h_w[t0:t1]
        Suse[t0:t1] = s_w[t0:t1]
        E[t0 : t1 + 1] = e_w[t0 : t1 + 1]
    return {
        "G0": G0,
        "G_final": G.copy(),
        "C": C, "D": D, "H": H, "Suse": Suse, "E": E,
        "dplus": dplus_all, "dminus": dminus_all,
        "plan_cost": float(np.dot(price, G0)),
        "adj_cost": adj_cost,
        "em_cost": float(np.dot(LAMBDA_EM * price, H)),
        "total_cost": float(np.dot(price, G0) + adj_cost + np.dot(LAMBDA_EM * price, H)),
    }
