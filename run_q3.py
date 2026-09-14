# -*- coding: utf-8 -*-
"""命令行入口：求解问题3（全年日内滚动）。``--strategy S1|S2|S3``，``--max-days`` 试跑。"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))
from problems.q3.run import main

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-days", type=int, default=None)
    ap.add_argument("--strategy", default="S3")
    args = ap.parse_args()
    raise SystemExit(main(max_days=args.max_days, strategy=args.strategy))
