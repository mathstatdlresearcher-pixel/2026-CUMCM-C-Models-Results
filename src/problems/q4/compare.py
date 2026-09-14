# -*- coding: utf-8 -*-
"""对照分析：把问题2 已定计划放到附件4 电价上重算费用，再与问题4-2 对照。

用来说明「同一套运行计划」在尖峰电价下费用会升高，不能把 J4 直接和 J2 比优劣。
"""
from __future__ import annotations

import json

import numpy as np
import pandas as pd

from common.io_data import load_attachment2, load_attachment4, load_price_att1
from common.paths import LEGACY_ROOT, tables_dir


def main():
    dates, _, _ = load_attachment2()
    c1 = load_price_att1()
    c4 = load_attachment4(dates)
    out = tables_dir("q4")
    d2 = LEGACY_ROOT / "problem2" / "outputs" / "daily_summary.csv"
    d42 = LEGACY_ROOT / "problem4" / "outputs" / "daily_4_2.csv"
    info = {"note": "完整格子对照需 result 中的 G；此处汇总已有全年结果。"}
    if d2.exists() and d42.exists():
        a = pd.read_csv(d2)
        b = pd.read_csv(d42)
        info["J2"] = float(a["total_cost"].sum())
        info["J42"] = float(b["total_cost"].sum())
        info["dJ"] = info["J42"] - info["J2"]
    (out / "compare_note.json").write_text(json.dumps(info, ensure_ascii=False, indent=2), encoding="utf-8")
    print(info)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
