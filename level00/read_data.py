"""第 0 关读取骨架：预览文件、列出表格、读取原始字符串。

运行本文件不下载数据，不转换收益口径，不进行回归。
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parent
RAW = ROOT / "data" / "raw"


@dataclass
class TableBlock:
    title: str
    header_line: int
    date_digits: int
    columns: list[str]
    rows: list[list[str]]


def local_source(dataset: str) -> Path:
    manifest_path = RAW / "manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError("请先运行 download_data.py。")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    record = manifest["datasets"][dataset]
    path = RAW / record["csv_file"]
    if hashlib.sha256(path.read_bytes()).hexdigest() != record["csv_sha256"]:
        raise ValueError(f"原始 CSV 已变化，请先核查：{path}")
    return path


def preview_file(path: Path, n: int = 22) -> None:
    print(f"\n原始文件：{path.name}")
    for line_number, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines()[:n], 1):
        # 控制终端宽度；完整内容始终保留在原文件中。
        shown = line if len(line) <= 180 else line[:180] + " ..."
        print(f"{line_number:>3}: {shown}")


def scan_tables(path: Path) -> list[TableBlock]:
    """根据列头与连续日期行识别表格；不依赖固定 skiprows。"""
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    records = [[field.strip() for field in row] for row in csv.reader(lines)]
    blocks = []
    for i, header in enumerate(records):
        if len(header) < 2 or header[0] or not all(header[1:]):
            continue
        start = i + 1
        while start < len(records) and not any(records[start]):
            start += 1
        if start >= len(records) or not re.fullmatch(r"\d{4}|\d{6}", records[start][0]):
            continue
        digits = len(records[start][0])
        rows = []
        cursor = start
        while cursor < len(records):
            record = records[cursor]
            if not record or not re.fullmatch(rf"\d{{{digits}}}", record[0]):
                break
            if len(record) != len(header):
                raise ValueError(f"第 {cursor + 1} 行的列数与列头不同。")
            rows.append(record)
            cursor += 1
        context = []
        for line in reversed(lines[:i]):
            if not line.strip():
                if context:
                    break
                continue
            context.append(line.strip())
        context.reverse()
        title = next((line for line in context if line.startswith(
            ("Average ", "Value Weight Average", "Annual Factors", "Number of Firms")
        )), context[-1] if context else "未命名表格")
        if digits == 6 and header[1:] == ["Mkt-RF", "SMB", "HML", "RF"]:
            title = "Monthly factors（根据列头识别）"
        blocks.append(TableBlock(title, i + 1, digits, ["date_raw"] + header[1:], rows))
    if not blocks:
        raise ValueError(f"未找到预期格式的表格：{path}")
    return blocks


def show_catalog(blocks: list[TableBlock]) -> None:
    print("表格目录（编号从 0 开始）：")
    for number, block in enumerate(blocks):
        title = block.title if len(block.title) <= 85 else block.title[:85] + " ..."
        print(f"  [{number}] {title}")
        print(f"      列头行={block.header_line}; 行数={len(block.rows)}; "
              f"数据列数={len(block.columns) - 1}; "
              f"日期字段={block.rows[0][0]} 至 {block.rows[-1][0]}")


def read_block(blocks: list[TableBlock], number: int) -> pd.DataFrame:
    """读取指定表格；字段先保留为 string，索引名为 date_raw。"""
    if number < 0 or number >= len(blocks):
        raise IndexError(f"表格编号应在 0 至 {len(blocks) - 1} 之间。")
    block = blocks[number]
    frame = pd.DataFrame(block.rows, columns=block.columns, dtype="string")
    return frame.set_index("date_raw")


def load_raw_tables() -> tuple[pd.DataFrame, pd.DataFrame]:
    """当前课题使用的两张原始月度表；标题与列名同时校验。"""
    factor_blocks = scan_tables(local_source("ff3"))
    portfolio_blocks = scan_tables(local_source("size_bm_25"))
    factor_candidates = [block for block in factor_blocks
                         if block.date_digits == 6
                         and block.columns[1:] == ["Mkt-RF", "SMB", "HML", "RF"]]
    portfolio_candidates = [block for block in portfolio_blocks
                            if block.date_digits == 6
                            and block.title.casefold() == "average value weighted returns -- monthly"
                            and len(block.columns) == 26]
    if len(factor_candidates) != 1 or len(portfolio_candidates) != 1:
        raise ValueError("源文件结构变化，请先查看表格目录再修改定位条件。")
    return read_block(factor_candidates, 0), read_block(portfolio_candidates, 0)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--peek", action="store_true", help="先显示原始文件前 22 行")
    args = parser.parse_args()
    for dataset in ("ff3", "size_bm_25"):
        path = local_source(dataset)
        print(f"\n[{dataset}] {path.name}")
        if args.peek:
            preview_file(path)
        show_catalog(scan_tables(path))

    ff3_raw, portfolios_raw = load_raw_tables()
    for name, frame in (("ff3_raw", ff3_raw), ("portfolios_raw", portfolios_raw)):
        print(f"\n{name}: shape={frame.shape}")
        print(f"首尾索引：{frame.index[0]} / {frame.index[-1]}")
        print(f"索引类型：{frame.index.dtype}; 字段类型：{frame.dtypes.unique()}")
        print("前三行、前五个数据列：")
        print(frame.iloc[:3, :5].to_string())
    print("\n读取完成。当前为原始字符串表格；练习代码见 practice.py。")


if __name__ == "__main__":
    main()
