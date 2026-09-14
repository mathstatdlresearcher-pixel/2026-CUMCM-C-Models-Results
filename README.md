# 社区微电网优化调度（CUMCM C 题）

本目录是可独立运行的求解包。赛题原始 `problem1`–`problem4` 仍留在上一级，此处不依赖目录联接。

## 目录

```
重构/
  data/                 已复制的 Excel（附件1–4 与 result 模板）
  src/
    common/             四问共用：常数、路径、读表、储能、画图
    problems/           四问求解（集中在一个文件夹）
      q1/ q2/ q3/ q4/
    analysis/           预处理、EDA、约束汇总、敏感性、报告收集
  outputs/              运行结果
    q1/ q2/ q3/ q4/
    analysis/
    reports/
  run_q1.py … run_q4.py
  run_analysis.py
  requirements.txt
```

## 运行

在 `重构/` 下使用 Anaconda Python（示例路径 `D:\Anaconda3\python.exe`）：

```text
python run_q1.py
python run_analysis.py
python run_q2.py --max-days 3
python run_q3.py --strategy S3 --max-days 3
python run_q4.py --part both --max-days 3
```

问题2/3/4 全年 MILP 较慢。正式提交用的 `result*.xlsx` 写在 `outputs/q*/`。

物理约定：能量单位 kWh，时间步 \(\Delta t=1/6\) h；储能效率 0.9，电量 \([1200,10800]\) kWh，充放功率上限 \(5000\,\mathrm{kW}\)，同一时段不充不放。

## 代码文件说明

### 根目录入口

| 文件 | 功能 |
|------|------|
| `run_q1.py` | 命令行启动问题1：日前确定型 MILP，结果写入 `outputs/q1/` |
| `run_q2.py` | 命令行启动问题2：全年随机规划；`--max-days` 可截断试跑 |
| `run_q3.py` | 命令行启动问题3：全年日内滚动；`--strategy S1\|S2\|S3` |
| `run_q4.py` | 命令行启动问题4：`--part 2\|3\|both` 选择 4-2 / 4-3 |
| `run_analysis.py` | 命令行启动分析：预处理、EDA、约束汇总、问题1 敏感性、收集 HTML |
| `requirements.txt` | Python 依赖：numpy、pandas、scipy、openpyxl、matplotlib |

### `src/common/`（共用）

| 文件 | 功能 |
|------|------|
| `__init__.py` | 公共子包入口，再导出常数与读表函数 |
| `constants.py` | 题目给定的时间步、储能、紧急购电倍率等常数 |
| `paths.py` | 定位 `data/` 中的 Excel 与 `outputs/` 输出目录 |
| `io_data.py` | 读取附件1–4，并把整点光伏预报插成 10 min 功率 |
| `time_index.py` | 把 144 个 10 min 格编成与附件5 一致的时段标签 |
| `storage.py` | 已知计划购电时，按实测负荷/光伏因果执行充放与紧急购电 |
| `plotting.py` | 中文字体、统一坐标轴与 PNG 保存 |

### `src/problems/q1/`（问题1：日前确定型）

| 文件 | 功能 |
|------|------|
| `__init__.py` | 问题1 包入口 |
| `data.py` | 读取 `data/附件1.xlsx` 的一日电价、负荷、光伏 |
| `milp.py` | 日前 MILP：最小化购电费，含 SOC 与充放互斥 |
| `validate.py` | 逐条核对功率平衡、SOC、互斥、目标值 |
| `export.py` | 写出 CSV/JSON，并按模板填写 `result1.xlsx` |
| `figures.py` | 电价与购电、净负荷、SOC、充放电图 |
| `run.py` | 读数据 → 求解 → 校验 → 出表出图 |

### `src/problems/q2/`（问题2：日前随机规划）

| 文件 | 功能 |
|------|------|
| `__init__.py` | 问题2 包入口 |
| `forecast.py` | 用决策日前的历史分位数凸组合生成 5 条 48 h 场景（无泄漏） |
| `milp.py` | 随机 MILP：第一天购电对各场景相同，第二天可分场景 |
| `backtest.py` | 把第一天计划拿到实测上执行，统计紧急购电 |
| `year.py` | 365 天滚动：附件1 电价 + 附件2 实测 |
| `export.py` | 日汇总与 `result2.xlsx`（2–12 月） |
| `run.py` | 全年滚动后导出 |

### `src/problems/q3/`（问题3：日内滚动）

| 文件 | 功能 |
|------|------|
| `__init__.py` | 问题3 包入口 |
| `forecast.py` | 读取附件3，整点预报插成 10 min |
| `milp.py` | 对一段未来窗口优化购电与储能 |
| `rolling.py` | 0/6/12/18 点重解；已过时段按实测执行；S1/S2/S3 策略 |
| `year.py` | 按日调用滚动调度（默认 S3） |
| `export.py` | 日汇总、紧急购电时段与 `result3.xlsx` |
| `run.py` | 全年滚动后导出 |

### `src/problems/q4/`（问题4：实时电价）

| 文件 | 功能 |
|------|------|
| `__init__.py` | 问题4 包入口 |
| `data.py` | 读取 `data/附件4.xlsx` 全年实时电价 |
| `run.py` | 用电价附件4 分别复用问题2、问题3 的全年算法 |
| `q42.py` | 4-2：随机规划 + 附件4，对应 `result4-2.xlsx` |
| `q43.py` | 4-3：滚动调度 + 附件4，对应 `result4-3.xlsx` |
| `compare.py` | 把问题2 计划放到附件4 上重算费用，与 4-2 对照 |

说明：附件4 电价波动更大（均值可与附件1 接近），官方全年费用 \(J_4\) 可以高于 \(J_2\)，不能据此说问题4 模型更差。

### `src/analysis/`

| 文件 | 功能 |
|------|------|
| `__init__.py` | 分析子包入口 |
| `preprocess.py` | 清点缺失值，说明夜间光伏为零是物理事实 |
| `eda.py` | 统计电价、负荷、光伏的均值与峰值 |
| `verify.py` | 重跑问题1 校验，并汇总问题2–4 已有检验结果 |
| `sensitivity.py` | 改 SOC 或功率上限后重解问题1 |
| `collect_reports.py` | 把原目录 HTML 报告复制到 `outputs/reports/` |
| `run.py` | 按顺序执行上述分析步骤 |

### 其它

| 文件 | 功能 |
|------|------|
| `src/__init__.py` | `src` 包根，供 `import common`、`import problems` |
| `src/problems/__init__.py` | 四问求解代码的总目录 |
| `data/README.md` | 本目录各 Excel 文件说明 |
