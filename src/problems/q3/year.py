# -*- coding: utf-8 -*-
"""问题3 全年仿真：按日调用滚动调度，默认策略 S3。"""
from __future__ import annotations

import pandas as pd

from common.constants import DT, E_INIT, STRATEGIES
from common.io_data import load_attachment2, load_attachment3, load_price_att1
from problems.q3.rolling import simulate_day


def run_year(max_days=None, strategy="S3", price_mat=None):
    dates, load_kw, pv_kw = load_attachment2()
    fc = load_attachment3(dates)
    c1 = load_price_att1()
    load_e, pv_e = load_kw * DT, pv_kw * DT
    nd = load_e.shape[0] if max_days is None else min(max_days, load_e.shape[0])
    recs = []
    E0 = E_INIT
    hours = STRATEGIES[strategy]
    for d in range(nd):
        price = price_mat[d] if price_mat is not None else c1
        price_next = price_mat[d + 1] if price_mat is not None and d + 1 < len(price_mat) else price
        rec = simulate_day(price, price_next, load_e[d], pv_e[d], fc[d], pv_kw[d], E0, issue_hours=hours)
        rec["date"] = pd.Timestamp(dates.iloc[d]).strftime("%Y-%m-%d")
        recs.append(rec)
        E0 = float(rec["E"][-1])
        if d == 0 or d % 20 == 19 or d == nd - 1:
            print(f"  {rec['date']}  J={rec['total_cost']:.1f}")
    return recs
