# -*- coding: utf-8 -*-
"""问题2 场景构造：用历史日负荷/光伏的分位数凸组合生成 5 条 48 h 场景。

拟合只用决策日之前的样本，避免把当天实测泄漏进预报。
"""
from __future__ import annotations

import numpy as np
from scipy.optimize import nnls

from common.constants import N, PCTS


def feat_row(arr: np.ndarray, j: int) -> np.ndarray:
    x1 = arr[j - 1]
    x2 = arr[j - 7] if j >= 7 else arr[j - 1]
    x3 = arr[max(0, j - 7) : j].mean(axis=0)
    x4 = arr[max(0, j - 28) : j].mean(axis=0)
    return np.vstack([x1, x2, x3, x4])


def fit_simplex_weights(arr: np.ndarray, d: int, default=None) -> np.ndarray:
    if default is None:
        default = np.array([0.40, 0.25, 0.25, 0.10])
    train = list(range(max(28, d - 60), d))
    if len(train) < 8:
        return default
    xs, ys = [], []
    for j in train:
        xs.append(feat_row(arr, j).T)
        ys.append(arr[j])
    a, _ = nnls(np.vstack(xs), np.concatenate(ys))
    s = a.sum()
    return default if s <= 1e-12 else a / s


def forecast_day(arr: np.ndarray, d: int, w: np.ndarray) -> np.ndarray:
    if d <= 0:
        return arr[0].copy()
    return np.clip((w[:, None] * feat_row(arr, d)).sum(axis=0), 0.0, None)


def residual_quantiles(actual: np.ndarray, pred: np.ndarray, d: int, pcts=PCTS) -> np.ndarray:
    hist = list(range(max(1, d - 21), d))
    if len(hist) < 5:
        return np.zeros((len(pcts), N))
    return np.percentile(actual[hist] - pred[hist], pcts, axis=0)
