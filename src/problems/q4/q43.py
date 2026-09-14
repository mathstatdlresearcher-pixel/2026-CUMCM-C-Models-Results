# -*- coding: utf-8 -*-
"""问题4-3 入口：滚动调度 + 附件4 电价，对应 ``result4-3.xlsx``。"""
from problems.q4.run import run_43


def main(max_days=None):
    return run_43(max_days)[-1]
