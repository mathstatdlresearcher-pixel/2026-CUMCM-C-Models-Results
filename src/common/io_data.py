# -*- coding: utf-8 -*-
"""读取 ``data/`` 中的附件 Excel，并换成程序用的数组。

- 附件1：一日电价、负荷、光伏（kW → kWh）
- 附件2：365 天负荷与光伏实际功率
- 附件3：每日 0/6/12/18 点发布的未来 24 h 整点光伏预报
- 附件4：365×144 实时电价
- ``hourly_to_10min``：把整点预报插成 10 min 功率
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from common.constants import DT, N
from common.paths import find_xlsx
from common.time_index import interval_labels


def load_attachment1() -> pd.DataFrame:
    df = pd.read_excel(find_xlsx("附件1"), sheet_name=0)
    df.columns = ["time_raw", "price", "load_kw", "pv_kw"]
    df["interval"] = interval_labels()
    df["hour"] = np.arange(N) * DT
    df["hour_end"] = df["hour"] + DT
    df["load_kwh"] = df["load_kw"].to_numpy(float) * DT
    df["pv_kwh"] = np.clip(df["pv_kw"].to_numpy(float), 0, None) * DT
    df["net_kw"] = df["load_kw"] - df["pv_kw"]
    return df


def load_price_att1() -> np.ndarray:
    return pd.to_numeric(load_attachment1()["price"], errors="coerce").to_numpy(float)[:N]


def load_attachment2():
    path = find_xlsx("附件2")
    xl = pd.ExcelFile(path)
    load_df = pd.read_excel(path, sheet_name=xl.sheet_names[0], header=0)
    pv_df = pd.read_excel(path, sheet_name=xl.sheet_names[1], header=0)
    dates = pd.to_datetime(load_df.iloc[:, 0]).dt.normalize()
    load = load_df.iloc[:, 1 : 1 + N].apply(pd.to_numeric, errors="coerce").to_numpy(float)
    pv = np.clip(pv_df.iloc[:, 1 : 1 + N].apply(pd.to_numeric, errors="coerce").to_numpy(float), 0.0, None)
    return dates, load, pv


def parse_issue_hour(v) -> int:
    if hasattr(v, "hour"):
        return int(v.hour)
    s = str(v).strip()
    if ":" in s:
        return int(s.split(":")[0])
    return int(float(s))


def load_attachment3(dates: pd.Series) -> np.ndarray:
    df = pd.read_excel(find_xlsx("附件3"), sheet_name=0)
    df.iloc[:, 0] = pd.to_datetime(df.iloc[:, 0]).ffill()
    hours = df.iloc[:, 1].map(parse_issue_hour).to_numpy()
    vals = df.iloc[:, 2:26].to_numpy(float)
    nd = len(dates)
    fc = np.zeros((nd, 4, 24))
    date_to_i = {pd.Timestamp(d).strftime("%Y-%m-%d"): i for i, d in enumerate(dates)}
    hour_to_k = {0: 0, 6: 1, 12: 2, 18: 3}
    for i in range(len(df)):
        ds = pd.Timestamp(df.iloc[i, 0]).strftime("%Y-%m-%d")
        if ds not in date_to_i:
            continue
        k = hour_to_k.get(int(hours[i]))
        if k is None:
            continue
        fc[date_to_i[ds], k] = np.clip(vals[i], 0.0, None)
    return fc


def hourly_to_10min(hourly_24: np.ndarray, issue_h: int, p_now: float) -> np.ndarray:
    P = np.zeros(25)
    P[0] = max(float(p_now), 0.0)
    P[1:] = np.clip(np.asarray(hourly_24, dtype=float), 0.0, None)
    out = np.zeros(N)
    issue_min = issue_h * 60
    for t in range(N):
        mid = t * 10 + 5
        u = (mid - issue_min) / 60.0
        if u < 0.0:
            continue
        if u >= 24.0:
            out[t] = P[24]
            continue
        h0 = int(np.floor(u))
        frac = u - h0
        out[t] = (1.0 - frac) * P[h0] + frac * P[h0 + 1]
    return np.clip(out, 0.0, None)


def load_attachment4(dates: pd.Series) -> np.ndarray:
    df = pd.read_excel(find_xlsx("附件4"))
    d4 = pd.to_datetime(df.iloc[:, 0]).dt.normalize()
    price = df.iloc[:, 1 : 1 + N].apply(pd.to_numeric, errors="coerce").to_numpy(float)
    mp = {pd.Timestamp(a).strftime("%Y-%m-%d"): i for i, a in enumerate(d4)}
    out = np.zeros((len(dates), N))
    for i, d in enumerate(dates):
        out[i] = price[mp[pd.Timestamp(d).strftime("%Y-%m-%d")]]
    return out
