# -*- coding: utf-8 -*-
"""工程路径：定位 ``重构/data`` 里的 Excel，以及 ``重构/outputs`` 输出目录。

``find_xlsx(stem)`` 按文件名（不含后缀）查找，例如 ``附件1``、``result3``。
数据文件已复制进 ``data/``，不再使用目录联接。
"""
from __future__ import annotations

from pathlib import Path

# src/common/paths.py → 重构/
PKG_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = PKG_ROOT / "src"
LEGACY_ROOT = PKG_ROOT.parent
DATA_DIR = PKG_ROOT / "data"
OUTPUTS = PKG_ROOT / "outputs"


def problem_dir(problem: str) -> Path:
    """返回 ``outputs/<problem>/``，不存在则创建。"""
    p = OUTPUTS / problem
    p.mkdir(parents=True, exist_ok=True)
    return p


def figures_dir(problem: str) -> Path:
    """该问的图与表都写在同一目录 ``outputs/<problem>/``。"""
    return problem_dir(problem)


def tables_dir(problem: str) -> Path:
    """同 ``figures_dir``，表也落在 ``outputs/<problem>/``。"""
    return problem_dir(problem)


def analysis_dir() -> Path:
    """EDA、预处理、检验、敏感性的输出目录 ``outputs/analysis/``。"""
    p = OUTPUTS / "analysis"
    p.mkdir(parents=True, exist_ok=True)
    return p


def find_xlsx(stem: str) -> Path:
    """在 ``data/`` 中查找 ``{stem}.xlsx``，找不到再回退到原题 ``附件/``。"""
    name = f"{stem}.xlsx"
    direct = DATA_DIR / name
    if direct.is_file():
        return direct
    for p in DATA_DIR.glob("*.xlsx"):
        if p.stem == stem:
            return p
    hits = []
    for root in (DATA_DIR, LEGACY_ROOT / "附件", LEGACY_ROOT / "附件" / "附件5"):
        if not root.exists():
            continue
        for p in root.rglob("*.xlsx"):
            if p.name.startswith("~$"):
                continue
            if p.stem == stem:
                hits.append(p)
    if not hits:
        raise FileNotFoundError(f"未找到 {stem}.xlsx（已在 {DATA_DIR} 查找）")
    hits.sort(key=lambda p: (0 if DATA_DIR in p.parents else 1, len(p.parts)))
    return hits[0]
