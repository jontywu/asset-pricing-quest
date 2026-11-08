"""第 0 关练习区。先完成任务 A，后续 TODO 随教学推进。

建议逐段运行（# %% 可用于 VS Code Python Interactive）。
这里不包含 Boss 题答案，也没有预填清洗实现。
"""

# %% 任务 A：载入并观察，不改数据
from pathlib import Path
import sys

import pandas as pd

# 普通脚本和 VS Code 分段执行均可定位 read_data.py。
SCRIPT_DIR = Path(__file__).resolve().parent if "__file__" in globals() else Path.cwd()
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))
from read_data import load_raw_tables

ff3_raw, portfolios_raw = load_raw_tables()

print("ff3_raw.shape:", ff3_raw.shape)
print("portfolios_raw.shape:", portfolios_raw.shape)

# TODO A1：打印两张表的所有列名。
# TODO A2：打印两张表的首尾索引、索引类型和字段类型。
# TODO A3：各查看前 3 行、后 3 行。


# %% 任务 B：观察原文件说明后再实现；本轮先不用填写
def clean_returns(raw: pd.DataFrame) -> pd.DataFrame:
    """处理数据类型、缺失标记与收益口径；保持 raw 不变。"""
    raise NotImplementedError("TODO B：等待下一小步，先完成任务 A。")


# %% 任务 C：构建月度索引、选取研究样本、检查和对齐
START = "1963-07"
END = "1991-12"


def prepare_sample(ff3: pd.DataFrame, portfolios: pd.DataFrame):
    """返回按月对齐的因子与测试组合，并提供检查结果。"""
    raise NotImplementedError("TODO C：下一阶段完成。")


# %% 任务 D：构造研究所需收益
def make_test_returns(ff3: pd.DataFrame, portfolios: pd.DataFrame):
    """返回用于后续资产定价检验的测试组合收益。"""
    raise NotImplementedError("TODO D：下一阶段完成。")
