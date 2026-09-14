# -*- coding: utf-8 -*-
"""问题4-2 入口：随机规划 + 附件4 电价，对应 ``result4-2.xlsx``。"""
from problems.q4.run import run_42


def main(max_days=None):
    return run_42(max_days)[-1]
