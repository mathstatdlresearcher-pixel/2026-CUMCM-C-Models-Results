# -*- coding: utf-8 -*-
"""问题3 主流程：全年滚动调度 → 导出 result3。可指定策略与截断天数。"""
from problems.q3.export import export_result3
from problems.q3.year import run_year


def main(max_days=None, strategy="S3"):
    recs = run_year(max_days=max_days, strategy=strategy)
    _, _, year = export_result3(recs)
    print("问题3", strategy, year)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
