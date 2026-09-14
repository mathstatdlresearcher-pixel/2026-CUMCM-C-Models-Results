# -*- coding: utf-8 -*-
"""命令行入口：求解问题4。``--part 2|3|both`` 选择 4-2、4-3 或两者。"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))
from problems.q4.run import main

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--part", default="both", choices=["2", "3", "both"])
    ap.add_argument("--max-days", type=int, default=None)
    args = ap.parse_args()
    raise SystemExit(main(part=args.part, max_days=args.max_days))
