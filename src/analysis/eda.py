# -*- coding: utf-8 -*-
"""EDA：统计附件1/2/4 的电价、负荷、光伏均值与峰值，写出 JSON 与 CSV。"""
from __future__ import annotations

import json

import numpy as np
import pandas as pd

from common.io_data import load_attachment1, load_attachment2, load_attachment4
from common.paths import analysis_dir


def main():
    a1 = load_attachment1()
    dates, L, P = load_attachment2()
    C4 = load_attachment4(dates)
    stats = {
        "att1_price": {"min": float(a1["price"].min()), "max": float(a1["price"].max()), "mean": float(a1["price"].mean())},
        "att1_load_kw_max": float(a1["load_kw"].max()),
        "att1_pv_kw_max": float(a1["pv_kw"].max()),
        "att2_load_mean": float(np.nanmean(L)),
        "att2_load_max": float(np.nanmax(L)),
        "att2_pv_max": float(np.nanmax(P)),
        "att4_price": {"min": float(np.nanmin(C4)), "max": float(np.nanmax(C4)), "mean": float(np.nanmean(C4))},
        "n_days": int(len(dates)),
    }
    out = analysis_dir()
    out.mkdir(parents=True, exist_ok=True)
    (out / "eda_stats.json").write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")
    pd.DataFrame([{**stats["att1_price"], "表": "附件1电价"}]).to_csv(out / "price_att1.csv", index=False, encoding="utf-8-sig")
    print(json.dumps(stats, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
