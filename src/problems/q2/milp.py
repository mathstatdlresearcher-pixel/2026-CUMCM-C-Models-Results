# -*- coding: utf-8 -*-
"""问题2 随机 MILP：第一天购电对所有场景相同，第二天允许分场景。

目标为场景期望购电费 + 紧急购电惩罚；储能按场景演化。
"""
from __future__ import annotations

import numpy as np
from scipy.optimize import LinearConstraint, milp
from scipy.sparse import lil_matrix

from common.constants import E_MAX, E_MIN, ETA_C, ETA_D, LAMBDA_EM, Q_MAX


def solve_day_milp(price, load_s, pv_s, pi, E0, time_limit=25.0):
    S, n = load_s.shape
    nq, nC, nD, nz, nE = 0, n, 2 * n, 3 * n, 4 * n
    ng = 4 * n + (n + 1)
    nh = ng + S * n
    nr = nh + S * n
    nv = nr + S * n

    def q(t):
        return nq + t

    def C(t):
        return nC + t

    def D(t):
        return nD + t

    def z(t):
        return nz + t

    def E(k):
        return nE + k

    def g(s, t):
        return ng + s * n + t

    def h(s, t):
        return nh + s * n + t

    def r(s, t):
        return nr + s * n + t

    cobj = np.zeros(nv)
    for t in range(n):
        cobj[q(t)] = float(price[t])
        for s in range(S):
            cobj[h(s, t)] = LAMBDA_EM * float(price[t]) * float(pi[s])
    A_eq = lil_matrix((S * n + n, nv))
    b_eq = np.zeros(S * n + n)
    row = 0
    for s in range(S):
        for t in range(n):
            A_eq[row, g(s, t)] = 1
            A_eq[row, h(s, t)] = 1
            A_eq[row, r(s, t)] = -1
            A_eq[row, D(t)] = 1
            A_eq[row, C(t)] = -1
            b_eq[row] = float(load_s[s, t] - pv_s[s, t])
            row += 1
    for t in range(n):
        A_eq[row, E(t + 1)] = 1
        A_eq[row, E(t)] = -1
        A_eq[row, C(t)] = -ETA_C
        A_eq[row, D(t)] = 1.0 / ETA_D
        row += 1
    A_ub = lil_matrix((2 * n + S * n, nv))
    b_ub = np.zeros(2 * n + S * n)
    row = 0
    for t in range(n):
        A_ub[row, C(t)] = 1
        A_ub[row, z(t)] = -Q_MAX
        row += 1
    for t in range(n):
        A_ub[row, D(t)] = 1
        A_ub[row, z(t)] = Q_MAX
        b_ub[row] = Q_MAX
        row += 1
    for s in range(S):
        for t in range(n):
            A_ub[row, g(s, t)] = 1
            A_ub[row, q(t)] = -1
            row += 1
    lb, ub = np.zeros(nv), np.full(nv, np.inf)
    for t in range(n):
        ub[C(t)] = ub[D(t)] = Q_MAX
        ub[z(t)] = 1
    for k in range(n + 1):
        lb[E(k)], ub[E(k)] = E_MIN, E_MAX
    lb[E(0)] = ub[E(0)] = float(E0)
    integ = np.zeros(nv, dtype=int)
    integ[nz : nz + n] = 1
    res = milp(
        c=cobj,
        constraints=[LinearConstraint(A_eq.tocsr(), b_eq, b_eq), LinearConstraint(A_ub.tocsr(), -np.inf, b_ub)],
        bounds=(lb, ub),
        integrality=integ,
        options={"disp": False, "time_limit": time_limit, "mip_rel_gap": 2e-4},
    )
    if res.x is None:
        raise RuntimeError(res.message)
    x = res.x
    qq = np.maximum(x[nq : nq + n], 0)
    CC = np.maximum(x[nC : nC + n], 0)
    DD = np.maximum(x[nD : nD + n], 0)
    for a in (qq, CC, DD):
        a[np.abs(a) < 1e-8] = 0
    return {"q": qq, "C": CC, "D": DD, "E": x[nE : nE + n + 1].copy(), "obj": float(res.fun)}
