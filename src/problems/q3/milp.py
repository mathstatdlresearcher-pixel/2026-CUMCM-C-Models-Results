# -*- coding: utf-8 -*-
"""问题3 滚动窗口 MILP：对给定电价/负荷/光伏预报，优化一段未来区间的购电与储能。"""
from __future__ import annotations

import numpy as np
from scipy.optimize import LinearConstraint, milp
from scipy.sparse import lil_matrix

from common.constants import E_MAX, E_MIN, ETA_C, ETA_D, N, PRICE_DOWN, PRICE_UP, Q_MAX


def clean(x):
    x = np.asarray(x, dtype=float)
    x[np.abs(x) < 1e-8] = 0.0
    return np.maximum(x, 0.0)


def solve_horizon(price_h, load_h, pv_h, E0, G_prev=None, n_commit=None):
    n = int(len(load_h))
    if n_commit is None:
        n_commit = n if G_prev is None else len(G_prev)
    rolling = G_prev is not None
    nG = 0
    nP = n
    nM = n + (n_commit if rolling else 0)
    nC = nM + (n_commit if rolling else 0)
    nD = nC + n
    nS = nD + n
    nZ = nS + n
    nE = nZ + n
    nv = nE + n + 1

    def g(t):
        return nG + t

    def dp(t):
        return nP + t

    def dm(t):
        return nM + t

    def c(t):
        return nC + t

    def d(t):
        return nD + t

    def s(t):
        return nS + t

    def z(t):
        return nZ + t

    def e(k):
        return nE + k

    cobj = np.zeros(nv)
    if rolling:
        for t in range(n_commit):
            cobj[dp(t)] = PRICE_UP * float(price_h[t])
            cobj[dm(t)] = -PRICE_DOWN * float(price_h[t])
        for t in range(n_commit, n):
            cobj[g(t)] = float(price_h[t])
    else:
        for t in range(n):
            cobj[g(t)] = float(price_h[t])
    n_eq = (2 * n) + (n_commit if rolling else 0)
    A_eq = lil_matrix((n_eq, nv))
    b_eq = np.zeros(n_eq)
    row = 0
    if rolling:
        Gp = np.asarray(G_prev, float)
        for t in range(n_commit):
            A_eq[row, g(t)] = 1
            A_eq[row, dp(t)] = -1
            A_eq[row, dm(t)] = 1
            b_eq[row] = float(Gp[t])
            row += 1
    for t in range(n):
        A_eq[row, g(t)] = 1
        A_eq[row, s(t)] = 1
        A_eq[row, d(t)] = 1
        A_eq[row, c(t)] = -1
        b_eq[row] = float(load_h[t])
        row += 1
    for t in range(n):
        A_eq[row, e(t + 1)] = 1
        A_eq[row, e(t)] = -1
        A_eq[row, c(t)] = -ETA_C
        A_eq[row, d(t)] = 1.0 / ETA_D
        row += 1
    A_ub = lil_matrix((2 * n, nv))
    b_ub = np.zeros(2 * n)
    for t in range(n):
        A_ub[t, c(t)] = 1
        A_ub[t, z(t)] = -Q_MAX
        A_ub[n + t, d(t)] = 1
        A_ub[n + t, z(t)] = Q_MAX
        b_ub[n + t] = Q_MAX
    lb, ub = np.zeros(nv), np.full(nv, np.inf)
    for t in range(n):
        ub[c(t)] = ub[d(t)] = Q_MAX
        ub[s(t)] = float(max(pv_h[t], 0.0))
        ub[z(t)] = 1
    for k in range(n + 1):
        lb[e(k)], ub[e(k)] = E_MIN, E_MAX
    lb[e(0)] = ub[e(0)] = float(E0)
    integ = np.zeros(nv, dtype=int)
    integ[nZ : nZ + n] = 1
    res = milp(
        c=cobj,
        constraints=[LinearConstraint(A_eq.tocsr(), b_eq, b_eq), LinearConstraint(A_ub.tocsr(), -np.inf, b_ub)],
        bounds=(lb, ub),
        integrality=integ,
        options={"disp": False, "time_limit": 12.0, "mip_rel_gap": 5e-4},
    )
    if res.x is None:
        raise RuntimeError(res.message)
    x = res.x
    out = {"G": clean(x[nG : nG + n]), "E": x[nE : nE + n + 1].copy(), "obj": float(res.fun)}
    if rolling:
        out["dplus"] = clean(x[nP : nP + n_commit])
        out["dminus"] = clean(x[nM : nM + n_commit])
    return out


def solve_initial(price, load_e, pv_hat_e, E0):
    Lh = np.concatenate([load_e, load_e])
    Ph = np.concatenate([pv_hat_e, pv_hat_e])
    prh = np.concatenate([price, price])
    sol = solve_horizon(prh, Lh, Ph, E0, G_prev=None, n_commit=2 * N)
    return {"G": sol["G"][:N], "E": sol["E"][: N + 1], "obj": sol["obj"]}


def solve_rolling(price, load_e, pv_hat_e, G_prev, E0, t0: int):
    Lh = np.concatenate([load_e[t0:], load_e])
    Ph = np.concatenate([pv_hat_e[t0:], pv_hat_e])
    prh = np.concatenate([price[t0:], price])
    m = N - t0
    sol = solve_horizon(prh, Lh, Ph, E0, G_prev=G_prev[t0:], n_commit=m)
    G_new = G_prev.copy()
    G_new[t0:] = sol["G"][:m]
    dplus, dminus = np.zeros(N), np.zeros(N)
    dplus[t0:] = sol["dplus"]
    dminus[t0:] = sol["dminus"]
    return {"G": G_new, "dplus": dplus, "dminus": dminus}
