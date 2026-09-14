# -*- coding: utf-8 -*-
"""分析总入口：依次跑预处理、EDA、约束汇总、问题1 敏感性，并收集 HTML 报告。"""
from analysis.eda import main as eda
from analysis.preprocess import main as preprocess
from analysis.verify import main as verify
from analysis.sensitivity import main as sensitivity
from analysis.collect_reports import main as collect_reports


def main():
    preprocess()
    eda()
    verify()
    sensitivity()
    collect_reports()
    return 0
