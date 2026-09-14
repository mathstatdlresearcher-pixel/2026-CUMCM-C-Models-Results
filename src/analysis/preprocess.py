# -*- coding: utf-8 -*-
"""数据预处理说明：清点缺失值，并注明夜间光伏为零是物理事实而非缺测。"""
from __future__ import annotations

import json

import numpy as np
import pandas as pd

from common.io_data import load_attachment2
from common.paths import analysis_dir, find_xlsx


def main():
    dates, L, P = load_attachment2()
    info = {
        "load_nan": int(np.isnan(L).sum()),
        "pv_nan": int(np.isnan(P).sum()),
        "pv_zero_share": float((P == 0).mean()),
        "note": "夜间光伏为 0 是物理事实，预处理中保留。附件3 日期空格为版式，不是数值缺失。",
        "附件": str(find_xlsx("附件2")),
    }
    out = analysis_dir()
    out.mkdir(parents=True, exist_ok=True)
    (out / "quality.json").write_text(json.dumps(info, ensure_ascii=False, indent=2), encoding="utf-8")
    print(info)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
