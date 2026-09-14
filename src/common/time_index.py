# -*- coding: utf-8 -*-
"""把 144 个 10 min 格编成 ``HH:MM-HH:MM`` 标签，与附件5 填表列一致。

最后一格记为 ``23:50-24:00``。附件表头若从 ``00:10`` 起，对应本序列第 0 项
（区间 00:00–00:10）。
"""
from __future__ import annotations

from common.constants import N


def interval_labels() -> list[str]:
    labs = []
    for i in range(N):
        h0, m0 = divmod(i * 10, 60)
        h1, m1 = divmod((i + 1) * 10, 60)
        labs.append("23:50-24:00" if i + 1 == N else f"{h0:02d}:{m0:02d}-{h1:02d}:{m1:02d}")
    return labs
