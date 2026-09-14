# -*- coding: utf-8 -*-
"""问题1 参数敏感性：改 SOC 上下限或充放功率上限后重解 MILP，记录目标值变化。"""
from __future__ import annotations

import json

import pandas as pd

from common.constants import DT, P_MAX, Q_MAX
from common.paths import analysis_dir
from problems.q1.data import load_attachment1
from problems.q1.milp import solve_milp


def main():
    df = load_attachment1()
    price, load, pv = df["price"].to_numpy(), df["load_kwh"].to_numpy(), df["pv_kwh"].to_numpy()
    base = solve_milp(price, load, pv)
    J0 = base["obj"]
    rows = []
    for eta in (0.8, 0.9, 1.0):
        sol = solve_milp(price, load, pv, eta=eta, time_limit=18)
        rows.append({"实验": "η", "取值": eta, "J": sol["obj"], "相对%": 100 * (sol["obj"] / J0 - 1)})
    for pmax in (3000, 5000, 8000):
        sol = solve_milp(price, load, pv, q_max=pmax * DT, time_limit=18)
        rows.append({"实验": "Pmax_kW", "取值": pmax, "J": sol["obj"], "相对%": 100 * (sol["obj"] / J0 - 1)})
    for emax in (6000, 10800, 14000):
        sol = solve_milp(price, load, pv, e_max=emax, time_limit=18)
        rows.append({"实验": "Emax", "取值": emax, "J": sol["obj"], "相对%": 100 * (sol["obj"] / J0 - 1)})
    out = analysis_dir()
    out.mkdir(parents=True, exist_ok=True)
    tab = pd.DataFrame(rows)
    tab.to_csv(out / "q1_sensitivity.csv", index=False, encoding="utf-8-sig")
    (out / "q1_sensitivity.json").write_text(json.dumps({"J0": J0, "rows": rows}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(tab.to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
