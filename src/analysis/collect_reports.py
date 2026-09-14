# -*- coding: utf-8 -*-
"""收集报告：把原题目录里已写好的 HTML 分析报告复制到 ``outputs/reports/``。"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from common.paths import LEGACY_ROOT, OUTPUTS

NAMES = [
    "问题1_变量关系分析.html",
    "问题2_建模求解与结果解读报告.html",
    "问题2_已知量关系分析.html",
    "问题3_建模求解与结果解读报告.html",
    "问题3_已知量关系分析.html",
    "问题4_波动电价下建模求解与结果.html",
    "问题4_已知量关系分析.html",
    "问题4_模型检验报告.html",
    "全体模型检验与敏感性.html",
]


def main():
    dst = OUTPUTS / "reports"
    dst.mkdir(parents=True, exist_ok=True)
    for name in NAMES:
        src = LEGACY_ROOT / name
        if src.exists():
            shutil.copy(src, dst / name)
            print("copy", name)
        else:
            print("skip", name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
