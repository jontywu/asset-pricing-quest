"""课程公共工具：数据读取、作图、因子构造。核心回归在 analysis.py。"""
from pathlib import Path
import hashlib
import json
import sys

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from level00.read_data import scan_tables, read_block

LABELS = {'ff3': '三因子', 'ff5': '五因子', 'bm6': '规模×B/M 六组合',
          'op6': '规模×盈利 六组合', 'inv6': '规模×投资 六组合',
          'bm25': '规模×B/M 25组合', 'op25': '规模×盈利 25组合',
          'inv25': '规模×投资 25组合', 'bm_op32': '规模×B/M×盈利 32组合',
          'bm_inv32': '规模×B/M×投资 32组合', 'op_inv32': '规模×盈利×投资 32组合',
          'industry30': '30行业组合', 'mom': '动量因子', 'mom25': '规模×动量 25组合'}


def manifest():
    return json.loads((ROOT / 'data/raw/manifest.json').read_text(encoding='utf-8'))


def raw_path(key):
    record = manifest()['datasets'][key]
    path = ROOT / 'data/raw' / record['csv_file']
    if hashlib.sha256(path.read_bytes()).hexdigest() != record['csv_sha256']:
        raise ValueError(f'原始数据校验失败：{path}')
    return path


def load_raw(key):
    blocks = scan_tables(raw_path(key))
    if key in ('ff3', 'ff5', 'mom'):
        candidates = [b for b in blocks if b.date_digits == 6]
    else:
        candidates = [b for b in blocks if b.date_digits == 6 and 'value weighted returns' in b.title.casefold() and 'monthly' in b.title.casefold()]
    if len(candidates) != 1:
        raise ValueError(f'{key}: 找到 {len(candidates)} 个候选月度表，请核查原文件。')
    return read_block(candidates, 0)


def load_returns(key, start=None, end=None):
    """读取月度收益：小数单位，PeriodIndex，缺失值保留 NaN。"""
    raw = load_raw(key)
    result = (raw.apply(pd.to_numeric, errors='raise').replace([-99.99, -999.0], np.nan) / 100.0).astype(float)
    result.index = pd.PeriodIndex(pd.to_datetime(raw.index, format='%Y%m'), freq='M', name='month')
    if not result.index.is_unique or not result.index.is_monotonic_increasing:
        raise ValueError(f'{key}: 重复或未排序的月份。')
    expected = pd.period_range(result.index[0], result.index[-1], freq='M')
    if not result.index.equals(expected.rename('month')):
        raise ValueError(f'{key}: 月份不连续。')
    result = result.loc[start:end].copy()
    if result.empty:
        raise ValueError(f'{key}: 请求样本为空。')
    if start and result.index[0] != pd.Period(start, freq='M'):
        raise ValueError(f'{key}: 未覆盖请求起点 {start}。')
    if end and result.index[-1] != pd.Period(end, freq='M'):
        raise ValueError(f'{key}: 未覆盖请求终点 {end}。')
    return result


def catalog():
    rows = []
    for key, record in manifest()['datasets'].items():
        frame = load_raw(key)
        rows.append({'key': key, '数据': LABELS[key], '月数': len(frame), '列数': frame.shape[1],
                     '起点': frame.index[0], '终点': frame.index[-1], '源版本': record['source_header'],
                     '下载UTC': record['downloaded_at_utc']})
    return pd.DataFrame(rows).set_index('key')


def build_ff3():
    """六组合列序：S低/S中/S高/B低/B中/B高；小数收益。"""
    p = load_returns('bm6')
    if p.shape[1] != 6:
        raise ValueError('预期六组合。')
    return pd.DataFrame({'SMB': p.iloc[:, :3].mean(axis=1) - p.iloc[:, 3:].mean(axis=1),
                         'HML': (p.iloc[:, 2] + p.iloc[:, 5] - p.iloc[:, 0] - p.iloc[:, 3]) / 2})


def build_ff5():
    """从三套六组合构造 FF5 的四个非市场因子。"""
    a, b, c = [load_returns(k) for k in ('bm6', 'op6', 'inv6')]
    dates = a.index.intersection(b.index).intersection(c.index)
    a, b, c = [x.loc[dates] for x in (a, b, c)]
    if any(x.shape[1] != 6 or x.isna().any().any() for x in (a, b, c)):
        raise ValueError('六组合结构或数据完整性不符合预期。')
    small_big = lambda p: p.iloc[:, :3].mean(axis=1) - p.iloc[:, 3:].mean(axis=1)
    high_low = lambda p: (p.iloc[:, 2] + p.iloc[:, 5] - p.iloc[:, 0] - p.iloc[:, 3]) / 2
    return pd.DataFrame({'SMB': (small_big(a) + small_big(b) + small_big(c)) / 3,
                         'HML': high_low(a), 'RMW': high_low(b), 'CMA': -high_low(c)})


def style():
    plt.rcParams.update({'font.family': 'sans-serif', 'font.sans-serif': ['Microsoft YaHei', 'DejaVu Sans'],
                         'axes.unicode_minus': False, 'figure.figsize': (8.6, 4.6), 'figure.dpi': 110,
                         'axes.spines.top': False, 'axes.spines.right': False,
                         'axes.grid': False, 'font.size': 11, 'savefig.bbox': 'tight'})
    pd.set_option('display.max_rows', 35)
    pd.set_option('display.max_columns', 10)
    pd.set_option('display.precision', 4)


def heatmap25(series, title, unit='pct/month', ax=None, vmin=None, vmax=None):
    """保留官方规模优先、第二特征次序；输入已是要显示的单位。"""
    values = np.asarray(series, dtype=float).reshape(5, 5)
    if ax is None:
        _, ax = plt.subplots(figsize=(7, 5.3), layout='constrained')
    cmap = LinearSegmentedColormap.from_list('course_blue', ['#f2f5f9', '#98bad0', '#215b85'])
    im = ax.imshow(values, cmap=cmap, vmin=vmin, vmax=vmax, aspect='auto')
    ax.set_xticks(range(5), ['Low', '2', '3', '4', 'High'])
    ax.set_yticks(range(5), ['Small', '2', '3', '4', 'Big'])
    ax.set_xlabel('Second characteristic quintile')
    ax.set_ylabel('Size quintile')
    ax.set_title(title)
    for i in range(5):
        for j in range(5):
            ax.text(j, i, f'{values[i, j]:.2f}', ha='center', va='center',
                    color='white' if im.norm(values[i, j]) > .60 else '#172330')
    ax.figure.colorbar(im, ax=ax, label=unit, shrink=.8)
    return ax


def save_table(df, name):
    path = ROOT / 'results' / (name if name.endswith('.csv') else name + '.csv')
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, encoding='utf-8-sig')
    return path


def paper_note(key):
    references = {
        'ff1993': ('Fama & French (1993), Common risk factors in the returns on stocks and bonds', '../papers/ff1993_primary_reference.pdf'),
        'ff2015': ('Fama & French (2015), A five-factor asset pricing model', '../papers/ff2015_primary_reference.pdf'),
        'fama_macbeth': ('Fama & MacBeth (1973), Risk, Return, and Equilibrium: Empirical Tests', 'https://doi.org/10.1086/260061'),
    }
    label, path = references[key]
    return f'**论文对照：** [{label}]({path})。准确表号、PDF 页码和复现范围见 [论文表格导航](../papers/TABLE_GUIDE.md)。当前数据版本会与原文历史版本存在差异。'
