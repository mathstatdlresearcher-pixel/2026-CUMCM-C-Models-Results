# -*- coding: utf-8 -*-
"""问题2 主流程：全年滚动 → 导出 result2。``max_days`` 可截断天数便于试跑。"""
from problems.q2.export import export_result2
from problems.q2.year import run_year


def main(max_days=None):
    recs = run_year(max_days=max_days)
    _, daily, year = export_result2(recs)
    print("问题2 全年", year)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
