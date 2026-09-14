# -*- coding: utf-8 -*-
"""问题1 主流程：读附件1 → 求解 MILP → 校验 → 出表出图。"""
from __future__ import annotations

from problems.q1.data import load_attachment1
from problems.q1.export import export_tables
from problems.q1.figures import draw_core_figures
from problems.q1.milp import solve_milp
from problems.q1.validate import validate


def main():
    df = load_attachment1()
    sol = solve_milp(df["price"].to_numpy(), df["load_kwh"].to_numpy(), df["pv_kwh"].to_numpy())
    report = validate(df, sol)
    _, tab2 = export_tables(df, sol, report)
    draw_core_figures(df, sol, report, tab2)
    print(f"J1={report['obj']:.4f}  Q={report['grid_total']:.4f}  节省 {report['save_ratio']:.2f}%")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
