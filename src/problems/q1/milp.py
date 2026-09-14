# -*- coding: utf-8 -*-
"""问题1 日前 MILP：已知全日负荷与光伏，最小化购电成本。

决策量为每格购电、充电、放电；储能能量守恒、SOC 上下限、充放互斥。
``solve_milp`` 可改 SOC 上下限与充放功率上限，供敏感性分析调用。
"""
from __future__ import annotations

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp

from common.constants import DT, E_INIT, E_MAX, E_MIN, ETA_C, ETA_D, N, Q_MAX


def solve_milp(price, load_kwh, pv_kwh, eta=None, e_min=None, e_max=None, q_max=None, lock_end=True, time_limit=120.0):
    eta = ETA_C if eta is None else eta
    e_min = E_MIN if e_min is None else e_min
    e_max = E_MAX if e_max is None else e_max
    q_max = Q_MAX if q_max is None else q_max
    nG, nC, nD, nS, nZ, nE = 0, N, 2 * N, 3 * N, 4 * N, 5 * N
    nv = 5 * N + N + 1

    def g(t):
        return nG + t

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

    c_obj = np.zeros(nv)
    c_obj[:N] = np.asarray(price, float)
    A_eq = np.zeros((2 * N, nv))
    b_eq = np.zeros(2 * N)
    for t in range(N):
        A_eq[t, [g(t), s(t), d(t)]] = 1.0
        A_eq[t, c(t)] = -1.0
        b_eq[t] = float(load_kwh[t])
        A_eq[N + t, e(t + 1)] = 1.0
        A_eq[N + t, e(t)] = -1.0
        A_eq[N + t, c(t)] = -eta
        A_eq[N + t, d(t)] = 1.0 / eta
    A_ub = np.zeros((2 * N, nv))
    b_ub = np.zeros(2 * N)
    for t in range(N):
        A_ub[t, c(t)] = 1.0
        A_ub[t, z(t)] = -q_max
        A_ub[N + t, d(t)] = 1.0
        A_ub[N + t, z(t)] = q_max
        b_ub[N + t] = q_max
    lb, ub = np.zeros(nv), np.full(nv, np.inf)
    for t in range(N):
        ub[c(t)] = ub[d(t)] = q_max
        ub[s(t)] = float(pv_kwh[t])
        ub[z(t)] = 1.0
    for k in range(N + 1):
        lb[e(k)], ub[e(k)] = e_min, e_max
    lb[e(0)] = ub[e(0)] = E_INIT
    if lock_end:
        lb[e(N)] = ub[e(N)] = E_INIT
    integ = np.zeros(nv, dtype=int)
    integ[nZ : nZ + N] = 1
    res = milp(
        c=c_obj,
        constraints=[LinearConstraint(A_eq, b_eq, b_eq), LinearConstraint(A_ub, -np.inf, b_ub)],
        bounds=Bounds(lb, ub),
        integrality=integ,
        options={"disp": False, "time_limit": time_limit, "mip_rel_gap": 1e-6},
    )
    if res.x is None:
        raise RuntimeError(res.message)
    x = res.x
    sol = {
        "G": np.maximum(x[nG : nG + N], 0),
        "C": np.maximum(x[nC : nC + N], 0),
        "D": np.maximum(x[nD : nD + N], 0),
        "Suse": np.maximum(x[nS : nS + N], 0),
        "z": x[nZ : nZ + N].copy(),
        "E": x[nE : nE + N + 1].copy(),
        "obj": float(np.dot(price, np.maximum(x[nG : nG + N], 0))),
        "message": str(res.message),
    }
    for k in ("G", "C", "D", "Suse"):
        sol[k][np.abs(sol[k]) < 1e-8] = 0.0
    return sol
