"""分析函数的实现检查。运行：python -B tests/test_analysis.py。"""

from pathlib import Path
import sys
import unittest

import numpy as np
import pandas as pd
from scipy.stats import f as f_distribution
import statsmodels.api as sm

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from analysis import fit_models, grs_test, model_summary


class AnalysisTests(unittest.TestCase):
    def setUp(self):
        rng = np.random.default_rng(20261108)
        observations, assets, factor_count = 240, 4, 3
        factor_values = rng.normal(0, 0.03, size=(observations, factor_count))
        factor_values += [0.006, 0.002, 0.003]
        design = np.column_stack([np.ones(observations), factor_values])
        self.expected_alpha = np.array([0.001, -0.002, 0.0005, 0.0])
        self.expected_beta = rng.normal(0.6, 0.3, size=(factor_count, assets))
        noise = rng.normal(0, 0.012, size=(observations, assets))
        # 正交残差让真实系数可精确恢复，同时保留非退化残差方差。
        residual = noise - design @ np.linalg.lstsq(design, noise, rcond=None)[0]
        values = self.expected_alpha + factor_values @ self.expected_beta + residual
        index = pd.period_range("2000-01", periods=observations, freq="M")
        self.factors = pd.DataFrame(factor_values, index=index, columns=["MKT", "SMB", "HML"])
        self.returns = pd.DataFrame(values, index=index, columns=["A", "B", "C", "D"])

    def test_known_coefficients_and_residuals(self):
        table, residuals = fit_models(self.returns, self.factors)
        np.testing.assert_allclose(table["alpha"], self.expected_alpha, atol=1e-13)
        np.testing.assert_allclose(table["alpha_pct_month"], 100 * self.expected_alpha, atol=1e-11)
        for position, factor in enumerate(self.factors.columns):
            np.testing.assert_allclose(table[f"beta_{factor}"], self.expected_beta[position], atol=1e-12)
        np.testing.assert_allclose(residuals.mean(axis=0), 0, atol=1e-13)
        self.assertTrue(residuals.index.equals(self.returns.index))
        self.assertTrue(residuals.columns.equals(self.returns.columns))
        self.assertTrue(np.isfinite(table.to_numpy()).all())

    def test_grs_matches_independent_ols_formula(self):
        design = sm.add_constant(self.factors)
        ols = sm.OLS(self.returns, design).fit()
        alpha = ols.params.iloc[0].to_numpy()
        sigma = np.cov(ols.resid.to_numpy(), rowvar=False, bias=True)
        omega = np.cov(self.factors.to_numpy(), rowvar=False, bias=True)
        mu = self.factors.mean().to_numpy()
        observations, assets = self.returns.shape
        factor_count = self.factors.shape[1]
        df2 = observations - assets - factor_count
        expected = df2 / assets * (alpha @ np.linalg.solve(sigma, alpha)) / (1 + mu @ np.linalg.solve(omega, mu))
        result = grs_test(self.returns, self.factors)
        self.assertAlmostEqual(result["stat"], expected, places=11)
        self.assertAlmostEqual(result["pvalue"], f_distribution.sf(expected, assets, df2), places=11)
        self.assertEqual((result["T"], result["N"], result["K"]), (240, 4, 3))
        self.assertEqual((result["df1"], result["df2"]), (4, 233))

    def test_grs_is_invariant_to_uniform_unit_change(self):
        original = grs_test(self.returns, self.factors)
        rescaled = grs_test(self.returns * 100, self.factors * 100)
        self.assertAlmostEqual(original["stat"], rescaled["stat"], places=10)
        self.assertAlmostEqual(original["pvalue"], rescaled["pvalue"], places=10)

    def test_rejects_misalignment_and_invalid_values(self):
        with self.assertRaises(ValueError):
            fit_models(self.returns, self.factors.iloc[::-1])
        for value in (np.nan, np.inf, -np.inf):
            broken = self.returns.copy()
            broken.iloc[3, 0] = value
            with self.assertRaises(ValueError):
                grs_test(broken, self.factors)
        with self.assertRaises(TypeError):
            fit_models(self.returns.astype("string"), self.factors)
        duplicate_index = self.returns.copy()
        duplicate_index.index = [duplicate_index.index[0]] * len(duplicate_index)
        with self.assertRaises(ValueError):
            fit_models(duplicate_index, self.factors)

    def test_rejects_rank_deficiency_and_insufficient_sample(self):
        bad_factors = self.factors.assign(duplicate=self.factors["MKT"])
        with self.assertRaises(ValueError):
            fit_models(self.returns, bad_factors)
        with self.assertRaises(ValueError):
            grs_test(self.returns.assign(duplicate=self.returns["A"]), self.factors)
        with self.assertRaises(ValueError):
            grs_test(self.returns.iloc[:7], self.factors.iloc[:7])

    def test_summary_uses_common_sample_and_correct_quantities(self):
        result = model_summary(self.returns, {"CAPM": self.factors[["MKT"]], "Three": self.factors})
        self.assertEqual(list(result.index), ["CAPM", "Three"])
        self.assertAlmostEqual(result.loc["Three", "mean_abs_alpha_pct_month"], np.abs(self.expected_alpha).mean() * 100, places=11)
        self.assertAlmostEqual(result.loc["Three", "rms_alpha_pct_month"], np.sqrt(np.mean(self.expected_alpha ** 2)) * 100, places=11)
        self.assertEqual(result.loc["CAPM", "K"], 1)
        self.assertEqual(result.loc["Three", "K"], 3)
        self.assertGreaterEqual(result.loc["Three", "mean_r2"], result.loc["CAPM", "mean_r2"])
        with self.assertRaises(ValueError):
            model_summary(self.returns, {"shifted": self.factors.iloc[1:]})

    def test_hac_lag_validation(self):
        for value in (-1, len(self.returns)):
            with self.assertRaises(ValueError):
                fit_models(self.returns, self.factors, hac_lags=value)
        for value in (1.5, True):
            with self.assertRaises(TypeError):
                fit_models(self.returns, self.factors, hac_lags=value)


if __name__ == "__main__":
    unittest.main(verbosity=2)
