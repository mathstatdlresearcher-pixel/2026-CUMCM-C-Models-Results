# -*- coding: utf-8 -*-
"""问题4 主流程：用电价附件4 分别复用问题2、问题3 的全年算法，写出 result4-2 / result4-3。"""
from __future__ import annotations

from common.io_data import load_attachment2, load_attachment4
from problems.q2.export import export_result2
from problems.q2.year import run_year as run_q2
from problems.q3.export import export_result3
from problems.q3.year import run_year as run_q3


def run_42(max_days=None):
    dates, _, _ = load_attachment2()
    C = load_attachment4(dates)
    recs = run_q2(max_days=max_days, price=C)
    # 写到 q4 tables：临时改 export 目录太耦合，这里调用后复制
    from pathlib import Path
    import shutil
    from common.paths import tables_dir
    dst, daily, year = export_result2(recs)
    q4 = tables_dir("q4")
    shutil.copy(dst, q4 / "result4-2.xlsx")
    daily.to_csv(q4 / "daily_4_2.csv", index=False, encoding="utf-8-sig")
    (q4 / "year_4_2.json").write_text(__import__("json").dumps(year, ensure_ascii=False, indent=2), encoding="utf-8")
    return recs, year


def run_43(max_days=None):
    dates, _, _ = load_attachment2()
    C = load_attachment4(dates)
    recs = run_q3(max_days=max_days, strategy="S3", price_mat=C)
    import shutil
    from common.paths import tables_dir
    dst, daily, year = export_result3(recs)
    q4 = tables_dir("q4")
    shutil.copy(dst, q4 / "result4-3.xlsx")
    daily.to_csv(q4 / "daily_4_3.csv", index=False, encoding="utf-8-sig")
    (q4 / "year_4_3.json").write_text(__import__("json").dumps(year, ensure_ascii=False, indent=2), encoding="utf-8")
    return recs, year


def main(part="both", max_days=None):
    y2 = y3 = None
    if part in {"2", "both"}:
        _, y2 = run_42(max_days)
        print("4-2", y2)
    if part in {"3", "both"}:
        _, y3 = run_43(max_days)
        print("4-3", y3)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
