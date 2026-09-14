# -*- coding: utf-8 -*-
"""命令行入口：跑数据预处理、EDA、约束汇总与问题1 敏感性，输出到 ``outputs/analysis/``。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))
from analysis.run import main

if __name__ == "__main__":
    raise SystemExit(main())
