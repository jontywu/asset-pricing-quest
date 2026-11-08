"""资产定价课程共用的时间序列回归与模型检验。

输入约定
--------
``excess_returns`` 的列是测试资产，``factors`` 的列是因子收益，两者
都使用小数形式的月收益率，并具有完全相同的月度索引。测试资产的
超额收益须由调用者事先构造。本模块不会再次扣减无风险收益，也不会
自动删行、补值、截取交集或替调用者改变样本。

个别截距的 HAC 标准误与经典 GRS 联合检验是两种不同的推断。这里分别
计算和标注；GRS 不使用 HAC 协方差，其有限样本 F 分布依赖经典假设。
"""

from __future__ import annotations

from collections.abc import Mapping
from numbers import Integral

import numpy as np
import pandas as pd
from pandas.api.types import is_complex_dtype, is_numeric_dtype
from scipy.stats import f as f_distribution
import statsmodels.api as sm


def _validate_inputs(
    excess_returns: pd.DataFrame, factors: pd.DataFrame
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """拒绝不明确的样本处理，返回 Y、F 和含截距的 X。"""
    for name, frame in (("excess_returns", excess_returns), ("factors", factors)):
        if not isinstance(frame, pd.DataFrame):
            raise TypeError(f"{name} 必须是 pandas DataFrame。")
        if frame.empty or frame.shape[1] == 0:
            raise ValueError(f"{name} 不能为空。")
        if not frame.index.is_unique or frame.index.hasnans:
            raise ValueError(f"{name} 的日期索引必须唯一且非空。")
        if not frame.columns.is_unique:
            raise ValueError(f"{name} 的列名必须唯一。")
        if any(not is_numeric_dtype(dtype) or is_complex_dtype(dtype)
               for dtype in frame.dtypes):
            raise TypeError(f"{name} 必须先转换成实数数值类型。")

    if not excess_returns.index.equals(factors.index):
        raise ValueError("测试资产与因子的索引必须完全相同且顺序一致；请显式对齐样本。")
    if len(set(map(str, factors.columns))) != len(factors.columns):
        raise ValueError("因子列名转换为字符串后不得重复。")

    returns_array = excess_returns.to_numpy(dtype=float, na_value=np.nan)
    factor_array = factors.to_numpy(dtype=float, na_value=np.nan)
    if not np.isfinite(returns_array).all() or not np.isfinite(factor_array).all():
        raise ValueError("输入含有缺失值或无穷值；请先检查，不能静默删行。")

    observations, factor_count = factor_array.shape
    if observations <= factor_count + 1:
        raise ValueError("观测数必须大于因子数加截距，才能估计残差方差。")
    design = np.column_stack([np.ones(observations), factor_array])
    if np.linalg.matrix_rank(design) != factor_count + 1:
        raise ValueError("含截距的因子矩阵不满秩；检查常数列和共线因子。")
    return returns_array, factor_array, design


def fit_models(
    excess_returns: pd.DataFrame,
    factors: pd.DataFrame,
    hac_lags: int = 6,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """逐列估计 Rᵉᵢ,ₜ = αᵢ + βᵢ′fₜ + εᵢ,ₜ。

    返回 ``(回归表, 残差表)``。``alpha`` 与输入同为月收益小数，
    ``alpha_pct_month`` 为月度百分点；例如 0.001 对应 0.1。
    ``t_alpha_ols`` 使用普通 OLS 标准误，``t_alpha_hac`` 使用 Bartlett
    核 Newey–West HAC 标准误，最大滞后默认 6，带 T/(T-K-1) 小样本修正。
    HAC 列不会改变 OLS 系数，也不会被传入经典 GRS 检验。

    调用者应根据研究设计说明滞后阶数；默认值不是原论文的统一设定。
    """
    returns_array, _, design = _validate_inputs(excess_returns, factors)
    if isinstance(hac_lags, bool) or not isinstance(hac_lags, Integral):
        raise TypeError("hac_lags 必须是非负整数。")
    if hac_lags < 0 or hac_lags >= len(excess_returns):
        raise ValueError("hac_lags 必须满足 0 <= hac_lags < 样本月数。")

    rows: list[dict] = []
    residual_columns: list[np.ndarray] = []
    for asset_number, asset in enumerate(excess_returns.columns):
        fitted = sm.OLS(returns_array[:, asset_number], design).fit()
        robust = fitted.get_robustcov_results(
            cov_type="HAC", maxlags=int(hac_lags), use_correction=True
        )
        row = {
            "asset": asset,
            "alpha": float(fitted.params[0]),
            "alpha_pct_month": float(fitted.params[0] * 100),
            "t_alpha_ols": float(fitted.tvalues[0]),
            "t_alpha_hac": float(robust.tvalues[0]),
            "r2": float(fitted.rsquared),
            "adj_r2": float(fitted.rsquared_adj),
        }
        row.update({f"beta_{name}": float(fitted.params[position + 1])
                    for position, name in enumerate(factors.columns)})
        rows.append(row)
        residual_columns.append(fitted.resid)

    table = pd.DataFrame(rows).set_index("asset")
    residuals = pd.DataFrame(
        np.column_stack(residual_columns),
        index=excess_returns.index.copy(),
        columns=excess_returns.columns.copy(),
    )
    return table, residuals


def grs_test(excess_returns: pd.DataFrame, factors: pd.DataFrame) -> dict:
    """经典 Gibbons–Ross–Shanken 联合截距检验。

    原假设为所有测试资产的 α 同时为零。令 T 为月份数、N 为资产数、
    K 为因子数；本实现固定使用分母 T：

        Σ = E′E / T
        Ω = (F - F̄)′(F - F̄) / T
        GRS = (T-N-K)/N * (α′Σ⁻¹α) / (1 + F̄′Ω⁻¹F̄)

    在经典条件（包括同方差、时间独立的多元正态误差等）下，统计量
    服从 F(N, T-N-K)。HAC t 值不能赋予这个 F 检验稳健性。
    不对协方差加岭、不使用伪逆；不可识别时明确报错。
    """
    returns_array, factor_array, design = _validate_inputs(excess_returns, factors)
    observations, asset_count = returns_array.shape
    factor_count = factor_array.shape[1]
    denominator_df = observations - asset_count - factor_count
    if denominator_df <= 0:
        raise ValueError("经典 GRS 要求 T > N + K。")

    coefficients, _, _, _ = np.linalg.lstsq(design, returns_array, rcond=None)
    alpha = coefficients[0, :]
    residuals = returns_array - design @ coefficients
    factor_mean = factor_array.mean(axis=0)
    centered_factors = factor_array - factor_mean
    residual_cov = residuals.T @ residuals / observations
    factor_cov = centered_factors.T @ centered_factors / observations

    if np.linalg.matrix_rank(residual_cov) != asset_count:
        raise ValueError("残差协方差矩阵不满秩；检查重复资产或因子完全张成的测试资产。")
    if np.linalg.matrix_rank(factor_cov) != factor_count:
        raise ValueError("因子协方差矩阵不满秩。")
    try:
        # Cholesky 将正定性与二次型计算放在同一步，避免显式求逆。
        residual_cholesky = np.linalg.cholesky(residual_cov)
        factor_cholesky = np.linalg.cholesky(factor_cov)
        alpha_scaled = np.linalg.solve(residual_cholesky, alpha)
        mean_scaled = np.linalg.solve(factor_cholesky, factor_mean)
    except np.linalg.LinAlgError as error:
        raise ValueError("协方差矩阵非正定，不能进行经典 GRS 检验。") from error

    statistic = float(
        denominator_df / asset_count
        * np.dot(alpha_scaled, alpha_scaled)
        / (1.0 + np.dot(mean_scaled, mean_scaled))
    )
    return {
        "stat": statistic,
        "pvalue": float(f_distribution.sf(statistic, asset_count, denominator_df)),
        "T": observations,
        "N": asset_count,
        "K": factor_count,
        "df1": asset_count,
        "df2": denominator_df,
    }


def model_summary(
    excess_returns: pd.DataFrame,
    model_factors: Mapping[str, pd.DataFrame],
    hac_lags: int = 6,
) -> pd.DataFrame:
    """在同一组资产、完全相同月份上比较多种因子模型。

    ``mean_abs_alpha_pct_month`` 和 ``rms_alpha_pct_month`` 衡量定价误差
    的月度百分点量级，``mean_r2`` 描述时间序列拟合程度。GRS 的 p 值
    对应每个模型各自的联合原假设，不是两个模型优劣差异的直接检验。
    """
    if not isinstance(model_factors, Mapping) or not model_factors:
        raise ValueError("model_factors 必须是非空的 模型名 -> 因子表 映射。")
    summaries = []
    for name, factors in model_factors.items():
        table, _ = fit_models(excess_returns, factors, hac_lags=hac_lags)
        joint_test = grs_test(excess_returns, factors)
        alpha_pct = table["alpha_pct_month"].to_numpy()
        summaries.append({
            "model": name,
            "mean_abs_alpha_pct_month": float(np.mean(np.abs(alpha_pct))),
            "rms_alpha_pct_month": float(np.sqrt(np.mean(alpha_pct ** 2))),
            "mean_r2": float(table["r2"].mean()),
            "grs_stat": joint_test["stat"],
            "grs_pvalue": joint_test["pvalue"],
            "T": joint_test["T"],
            "N": joint_test["N"],
            "K": joint_test["K"],
        })
    return pd.DataFrame(summaries).set_index("model")
