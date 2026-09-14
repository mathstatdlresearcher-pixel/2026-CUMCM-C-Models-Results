# -*- coding: utf-8 -*-
"""命令行入口：求解问题2（全年随机规划）。可用 ``--max-days`` 截断试跑。"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))
from problems.q2.run import main

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-days", type=int, default=None)
    args = ap.parse_args()
    raise SystemExit(main(max_days=args.max_days))
