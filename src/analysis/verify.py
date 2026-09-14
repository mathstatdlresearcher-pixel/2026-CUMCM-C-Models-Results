# -*- coding: utf-8 -*-
"""约束检验汇总：重跑问题1 校验；并汇总旧目录中问题2–4 的已有检验 JSON。"""
from __future__ import annotations

import json

from common.constants import E_MAX, E_MIN, E_INIT, Q_MAX
from common.paths import LEGACY_ROOT, analysis_dir
from problems.q1.data import load_attachment1
from problems.q1.milp import solve_milp
from problems.q1.validate import validate


def check_q1():
    df = load_attachment1()
    sol = solve_milp(df["price"].to_numpy(), df["load_kwh"].to_numpy(), df["pv_kwh"].to_numpy())
    r = validate(df, sol)
    items = [
        ("能量平衡", r["balance_max_abs"] < 1e-4),
        ("SOC递推", r["soc_max_abs"] < 1e-4),
        ("互斥", r["simultaneous_max"] < 1e-6),
        ("SOC下界", r["E_min"] >= E_MIN - 1e-3),
        ("SOC上界", r["E_max"] <= E_MAX + 1e-3),
        ("E0", abs(r["E0"] - E_INIT) < 1e-3),
        ("E24", abs(r["E24"] - E_INIT) < 1e-3),
        ("充电上限", r["C_max"] <= Q_MAX + 1e-6),
    ]
    return {"n_ok": sum(1 for _, ok in items if ok), "n": len(items), "items": items, "J": r["obj"]}


def collect_legacy():
    rows = []
    mapping = [
        ("问题1", LEGACY_ROOT / "problem1/outputs/verification/verification_summary.json", "通过项数", "总项数"),
        ("问题2", LEGACY_ROOT / "problem2/outputs/verification/verify_summary.json", "n_ok", "n_all"),
        ("问题3", LEGACY_ROOT / "problem3/outputs/verification/verify_summary.json", "n_ok", "n_check"),
        ("问题4", LEGACY_ROOT / "problem4/outputs/verification/verify_summary.json", "n_ok", "n_check"),
    ]
    for name, path, a, b in mapping:
        if not path.exists():
            rows.append({"模型": name, "通过": "缺文件", "路径": str(path)})
            continue
        s = json.loads(path.read_text(encoding="utf-8"))
        rows.append({"模型": name, "通过": f"{s.get(a, s.get('n_ok'))}/{s.get(b, s.get('n_check'))}", "全部通过": s.get("全部通过", s.get("all_pass", True))})
    return rows


def main():
    q1 = check_q1()
    legacy = collect_legacy()
    summary = {"q1_refactor": q1, "legacy": legacy}
    out = analysis_dir()
    (out / "suite_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2, default=str))
    return 0 if q1["n_ok"] == q1["n"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
