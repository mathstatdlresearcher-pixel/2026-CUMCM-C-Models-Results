# -*- coding: utf-8 -*-
"""问题2 日回测：把第一天计划购电拿到实测负荷/光伏上执行，统计紧急购电。"""
from __future__ import annotations

import numpy as np

from common.constants import LAMBDA_EM
from common.storage import merge_emergency


def backtest(q, C, D, load_kwh, pv_kwh, price):
    demand = load_kwh + C - pv_kwh - D
    h = np.maximum(demand - q, 0.0)
    g = np.minimum(q, np.maximum(demand, 0.0))
    plan = float(np.dot(price, q))
    em = float(np.dot(LAMBDA_EM * price, h))
    return {
        "h": h,
        "g": g,
        "surplus": np.maximum(-demand, 0.0),
        "demand": demand,
        "plan_cost": plan,
        "em_cost": em,
        "total_cost": plan + em,
    }
