# -*- coding: utf-8 -*-
"""储能因果执行：已知计划购电 G，按实际负荷/光伏决定充放与紧急购电。

``execute_slot`` 处理一个 10 min；``execute_window`` 处理一段区间；
``merge_emergency`` 把连续正紧急电量并成填表用的时间段。
"""
from __future__ import annotations

from common.constants import ETA_C, ETA_D, E_MAX, E_MIN, N, Q_MAX


def execute_slot(G, L, S, E):
    room = max((E_MAX - E) / ETA_C, 0.0)
    dmax = min(Q_MAX, ETA_D * max(E - E_MIN, 0.0))
    net = L - G - S
    if net > 1e-12:
        D = min(net, dmax)
        C = 0.0
        H = net - D
        suse = S
    else:
        sur = -net
        D = 0.0
        C = min(sur, Q_MAX, room)
        H = 0.0
        suse = min(S, max(L + C - G, 0.0))
    e2 = float(max(E_MIN, min(E_MAX, E + ETA_C * C - D / ETA_D)))
    return float(C), float(D), float(H), float(suse), e2


def execute_window(G, load_e, pv_e, E0, t0, t1):
    import numpy as np

    C = np.zeros(N)
    D = np.zeros(N)
    H = np.zeros(N)
    suse = np.zeros(N)
    E = np.zeros(N + 1)
    E[t0] = float(E0)
    for t in range(t0, t1):
        C[t], D[t], H[t], suse[t], E[t + 1] = execute_slot(G[t], load_e[t], pv_e[t], E[t])
    return C, D, H, suse, E


def merge_emergency(h, labels, eps=1e-6):
    segs = []
    t = 0
    n = len(h)
    while t < n:
        if h[t] <= eps:
            t += 1
            continue
        t0 = t
        s = 0.0
        while t < n and h[t] > eps:
            s += h[t]
            t += 1
        left = labels[t0].split("-")[0]
        right = labels[t - 1].split("-")[1]
        segs.append((f"{left}-{right}", float(s)))
    return segs
