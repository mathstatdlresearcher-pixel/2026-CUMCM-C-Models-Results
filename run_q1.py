# -*- coding: utf-8 -*-
"""命令行入口：求解问题1（日前确定型 MILP），结果写入 ``outputs/q1/``。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))
from problems.q1.run import main

if __name__ == "__main__":
    raise SystemExit(main())
