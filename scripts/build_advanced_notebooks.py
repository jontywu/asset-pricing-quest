"""生成资产定价课程第 06–09 关；由课程执行器统一运行并保留输出。"""
from pathlib import Path
from textwrap import dedent

import nbformat as nbf

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "notebooks"


def md(text):
    source = dedent(text).strip().replace("：**", "：** ").replace("。**", "。** ")
    return nbf.v4.new_markdown_cell(source)


def code(text):
    return nbf.v4.new_code_cell(dedent(text).strip())


SETUP = r'''
from pathlib import Path
import sys

ROOT = next((p for p in [Path.cwd(), *Path.cwd().parents]
             if (p / "src" / "course.py").exists()), None)
if ROOT is None:
    raise RuntimeError("请在 asset_pricing_quest 项目或其 notebooks 文件夹中启动 Notebook。")
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
from IPython.display import display, Markdown
from course import load_returns, style, save_table, paper_note, build_ff5
from analysis import fit_models, model_summary

style()
pd.set_option("display.max_columns", 12)
pd.set_option("display.max_rows", 24)
'''
def write_notebook(filename, cells):
    nb = nbf.v4.new_notebook(cells=cells)
    nb.metadata.update({
        "kernelspec": {"display_name": "Asset Pricing Quest", "language": "python", "name": "asset-pricing-quest"},
        "language_info": {"name": "python", "version": "3.12"},
        "course": {"execution": "Run All; each notebook loads its own inputs", "boss_answers": "blank"},
    })
    nbf.validate(nb)
    DEST.mkdir(parents=True, exist_ok=True)
    nbf.write(nb, DEST / filename)
    print(filename)


def notebook06():
    return [
        md(r'''
        # 第 06 关：从共同波动到风险价格

        **本关目标：**分清时间序列回归与横截面回归各自提出的问题。
        时间序列第一步估计“组合对因子变化有多敏感”，第二步观察“不同敏感度的组合，在同一个月的收益怎样不同”。

        本关使用官方 25 个规模×账面市值比组合，练习两步 Fama–MacBeth 方法。
        这是**公开组合数据上的教学实现**，没有重建 Fama–MacBeth（1973）的原始分组程序，
        也不是 Fama–French（1992）个股特征回归的逐表复现。
        因子暴露和公司特征是不同对象，本关第二步使用前者。

        运行顺序：设置 → 过去 60 个月的暴露 → 当月横截面 → 风险价格的时间平均 → 不确定性。
        ''') ,
        code(SETUP),
        code('display(Markdown(paper_note("fama_macbeth")))'),
        md(r'''
        ## 1. 先定义信息时间

        使用 1963-07 至 2013-12 的数据，预设滚动窗口为 60 个月。
        对月份 $t$，第一步只能使用 $t-60,\ldots,t-1$ 的收益。
        第一个可以做第二步回归的月份，因此要晚于样本起点。

        全部收益采用月度小数。第二步左侧为当月组合超额收益。
        这里把 RF 的处理写出来，让你能追踪“被解释变量”究竟是什么。
        '''),
        code('''
        START, END, WINDOW = "1963-07", "2013-12", 60
        factor_names = ["Mkt-RF", "SMB", "HML"]
        ff3 = load_returns("ff3", START, END)
        portfolios = load_returns("bm25", START, END)
        assert ff3.index.equals(portfolios.index)
        y = portfolios.sub(ff3["RF"], axis=0)
        f = ff3[factor_names]
        assert not y.isna().any().any() and not f.isna().any().any()
        display(pd.DataFrame({"起点": [str(y.index[0])], "终点": [str(y.index[-1])],
                              "月份数": [len(y)], "测试组合数": [y.shape[1]], "过去窗口": [WINDOW]}))
        '''),
        md(r'''
        ## 2. 在时间维度估计暴露，再在资产维度估计价格

        第一步对每个组合做过去窗口内的回归，保留斜率 $\hat{\beta}_{i,t-1}$。
        第二步在每个月用 25 个组合进行截面回归：

        $$
        R^e_{i,t}=\lambda_{0,t}+\hat{\beta}_{i,t-1}'\lambda_t+u_{i,t}.
        $$

        $\lambda_t$ 是这个月截面上的估计斜率。它的时间平均是本关的风险价格估计。
        截面常数项也要报告；不要在代码中先强制它为零。
        下面用矩阵最小二乘同时估计 25 个组合，等价于在同一个窗口对它们分别做 OLS。
        '''),
        code('''
        lambda_rows, dates, audit = [], [], []
        for t in range(WINDOW, len(y)):
            past_f = f.iloc[t-WINDOW:t]
            past_y = y.iloc[t-WINDOW:t]
            x_ts = np.column_stack([np.ones(WINDOW), past_f.to_numpy(dtype=float)])
            coeff, _, rank_ts, _ = np.linalg.lstsq(x_ts, past_y.to_numpy(dtype=float), rcond=None)
            assert rank_ts == x_ts.shape[1]
            betas = coeff[1:].T  # 行：25 个组合；列：3 个因子暴露
            x_cs = np.column_stack([np.ones(len(betas)), betas])
            lambdas, _, rank_cs, _ = np.linalg.lstsq(x_cs, y.iloc[t].to_numpy(dtype=float), rcond=None)
            assert rank_cs == x_cs.shape[1]
            lambda_rows.append(lambdas)
            dates.append(y.index[t])
            audit.append([past_y.index[0], past_y.index[-1], y.index[t]])

        risk_prices = pd.DataFrame(lambda_rows, index=pd.PeriodIndex(dates, freq="M"),
                                   columns=["Intercept", *factor_names])
        information_dates = pd.DataFrame(audit, columns=["窗口起点", "窗口终点", "被解释月份"])
        assert (information_dates["窗口终点"] < information_dates["被解释月份"]).all()
        display(information_dates.head(3))
        display(risk_prices.head(3))
        save_table(risk_prices, "06_monthly_risk_prices")
        '''),
        md(r'''
        ## 3. 在时间维度度量估计不确定性

        月度风险价格会波动。我们对每一列做“只有常数项”的回归，常数就是时间平均，
        采用 Newey–West / HAC 标准误，滞后阶数预设为 6。
        图中的区间是渐近 95% 区间，展示的是均值估计的不确定性。

        **方法边界：**本教学实现没有添加 Shanken 生成解释变量修正；
        HAC 处理时间依赖，并不自动消除估计 β 带来的误差。
        只有 25 个预先按规模和价值排序的资产，也会影响风险价格的识别与精度。
        '''),
        code('''
        rows = []
        for name in risk_prices:
            result = sm.OLS(risk_prices[name].to_numpy(dtype=float), np.ones((len(risk_prices), 1))).fit(
                cov_type="HAC", cov_kwds={"maxlags": 6, "use_correction": True})
            mean, se = float(result.params[0]), float(result.bse[0])
            rows.append({"term": name, "mean_pct_month": mean*100, "se_hac_pct": se*100,
                         "t_hac": float(result.tvalues[0]), "ci_low_pct": (mean-1.96*se)*100,
                         "ci_high_pct": (mean+1.96*se)*100, "months": len(risk_prices)})
        price_summary = pd.DataFrame(rows).set_index("term")
        display(price_summary.round(4))
        save_table(price_summary, "06_risk_price_summary")

        fig, ax = plt.subplots(figsize=(8, 4.3))
        pos = np.arange(len(price_summary))
        ax.errorbar(price_summary["mean_pct_month"], pos,
                    xerr=1.96*price_summary["se_hac_pct"], fmt="o", color="#245b84", capsize=4)
        ax.axvline(0, color="#666666", linewidth=1)
        ax.set_yticks(pos, price_summary.index)
        ax.set_xlabel("风险价格时间平均（% / 月）；HAC 渐近 95% 区间")
        ax.set_title("滚动暴露下的 Fama–MacBeth 估计")
        ax.invert_yaxis()
        fig.tight_layout()
        plt.show()
        '''),
        code('''
        m = price_summary.loc["Mkt-RF"]
        display(Markdown(
            f"当前运行使用 **{len(risk_prices)} 个第二步月份**，市场风险价格均值为 "
            f"**{m['mean_pct_month']:.3f}% / 月**，HAC 95% 区间为 "
            f"[{m['ci_low_pct']:.3f}, {m['ci_high_pct']:.3f}]。"
            "这是这组资产、窗口和截面规格下的估计。截面斜率的单位是每单位因子暴露所对应的月收益差，"
            "不等于持有某家公司特征的因果效果。判断时要同时观察经济量级与区间宽度。"))
        '''),
        md(r'''
        ## 4. 与可交易因子的历史平均收益放在一起看

        对可交易收益因子，线性定价框架给出了风险价格与因子预期收益的联系。
        本实验是有限样本、滚动估计、特定测试资产上的两步估计，不能要求两列机械相等。
        这张对照表能帮助定位“估计对象”与“样本误差”，不是自动通过或失败的判据。
        '''),
        code('''
        comparison = pd.DataFrame({
            "FMB_mean_pct_month": price_summary.loc[factor_names, "mean_pct_month"],
            "factor_mean_same_months_pct": f.loc[risk_prices.index].mean()*100,
        })
        display(comparison.round(4))
        save_table(comparison, "06_price_vs_factor_mean")
        '''),
        md('''
        ## 通关证据与 Boss 作答区

        提交：信息时间检查表、风险价格估计表，以及你对截面常数项和各斜率的解释。

        **Boss：**如果第一步某个组合的因子暴露估计很精确，你会怎样设计证据，评估第二步的风险价格？
        先写预判，再把 WINDOW 从 60 改成 120，观察样本长度和估计精度如何变化。

        **你的回答：**

        （留空，运行与思考后填写。）
        '''),
    ]


def notebook07():
    return [
        md(r'''
        # 第 07 关：五因子锻造台

        **本关目标：**把“企业盈利和投资有什么经济含义”连接到可以计算的组合收益。

        估值关系把当前价格与未来给股东的现金流联系起来。**给定 B/M 与投资，较高的预期盈利对应较高的预期收益；
        给定 B/M 与盈利，较高的预期投资对应较低的预期收益。**这些条件不能省略。
        Fama–French 用盈利与投资排序组合，
        检查这些方向是否有助于描述平均收益。这个动机并不等于已经识别了盈利或投资的因果效应。

        本关从官方公开的六组合收益构造因子。它让我们复现因子组合的代数，
        但没有重建每家公司的财报匹配与个股筛选。
        '''),
        code(SETUP),
        code('display(Markdown(paper_note("ff2015")))'),
        md(r'''
        ## 1. 先认识原材料

        三套 2×3 组合分别按规模与 B/M、经营盈利 OP、投资 Inv 排序。
        每套中都有小规模、大规模两行及三个特征档位。

        - RMW：高经营盈利组合减低经营盈利组合。
        - CMA：保守投资组合减积极投资组合；这里投资以资产增长刻画。

        个股特征决定组合归属；下面加载的是这些组合**已经实现的月收益**。
        2015 论文中 OP 的分母为账面权益 BE；官网从 2018 年起把分母改为 BE 加少数股东权益。
        因此本次公开组合使用的是更新后的历史数据，不能把它精确等同于 2015 年的 OP 定义。
        严格原样本原版本重建还需要相应版本的原始数据。
        [官方因子定义](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library/f-f_5_factors_2x3.html)
        '''),
        code('''
        START, END = "1963-07", "2013-12"
        bm6 = load_returns("bm6", START, END)
        op6 = load_returns("op6", START, END)
        inv6 = load_returns("inv6", START, END)
        for name, frame in [("B/M 六组合", bm6), ("OP 六组合", op6), ("Inv 六组合", inv6)]:
            display(Markdown(f"**{name}：** {frame.shape[0]} 个月，{frame.shape[1]} 个组合"))
            display(frame.head(2))
        '''),
        md(r'''
        ## 2. 把组合收益按论文规则相加减

        用 $S$ 与 $B$ 表示小、大规模，用 $R/W$ 表示高、低盈利，$C/A$ 表示保守、积极投资：

        $$
        RMW=\frac{1}{2}(S_R+B_R)-\frac{1}{2}(S_W+B_W).
        $$

        $$
        CMA=\frac{1}{2}(S_C+B_C)-\frac{1}{2}(S_A+B_A).
        $$

        五因子的规模收益来自三套排序中规模差的平均。
        函数实现可从 `src/course.py` 中的 `build_ff5` 查看；下面同时展示源码，方便逐项对照。
        所有操作都保留在相同月份，尚未进行资产定价回归。
        '''),
        code('''
        import inspect
        print(inspect.getsource(build_ff5))
        constructed = build_ff5().loc[START:END, ["SMB", "HML", "RMW", "CMA"]]
        official = load_returns("ff5", START, END)
        assert constructed.index.equals(official.index)
        display((constructed.head(3)*100).rename_axis("月；数值单位 %"))
        '''),
        md(r'''
        ## 3. 用官方序列做外部核对

        误差以 bp / 月表示，1 bp 为 0.01 个百分点。
        发布文件有各自的小数位数，比较时先看是否存在系统偏差，再看差异是否与四舍五入精度相当。
        不把相关系数接近 1 单独当成构造正确的证据。
        '''),
        code('''
        factor_names = ["SMB", "HML", "RMW", "CMA"]
        errors_bp = (constructed - official[factor_names])*10000
        comparison = pd.DataFrame({
            "mean_error_bp": errors_bp.mean(),
            "mean_abs_error_bp": errors_bp.abs().mean(),
            "max_abs_error_bp": errors_bp.abs().max(),
            "correlation": pd.Series({name: constructed[name].corr(official[name]) for name in factor_names}),
        })
        display(comparison.round(5))
        save_table(comparison, "07_ff5_reconstruction_check")
        save_table(constructed, "07_constructed_ff5_nonmarket_factors")
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.bar(comparison.index, comparison["max_abs_error_bp"], color="#245b84")
        ax.set_ylabel("最大绝对差（bp / 月）")
        ax.set_title("自行构造与官方因子的逐月核对")
        ax.set_ylim(bottom=0)
        fig.tight_layout()
        plt.show()
        '''),
        code('''
        worst = comparison["max_abs_error_bp"].idxmax()
        display(Markdown(f"当前快照的最大逐月偏差出现在 **{worst}**，为 "
            f"**{comparison.loc[worst, 'max_abs_error_bp']:.4f} bp / 月**。"
            "这是发布后组合收益重新相加减的核对结果。若差异明显超出发布精度，应先检查月份、"
            "组合顺序、做多与做空方向，以及输入文件版本，再解释经济含义。"))
        '''),
        md(r'''
        ## 4. 一个名字可能对应两套实现

        将三因子文件与五因子文件的 SMB 放在相同月份上直接比较。
        这一步建立下一关的模型比较口径：改变公共因子定义和增加新因子是两个不同的变动。
        '''),
        code('''
        ff3 = load_returns("ff3", START, END)
        smb_check = pd.DataFrame({"SMB_FF3": ff3["SMB"], "SMB_FF5": official["SMB"]})
        smb_diagnostic = pd.Series({
            "correlation": smb_check.corr().iloc[0, 1],
            "mean_FF3_pct_month": smb_check["SMB_FF3"].mean()*100,
            "mean_FF5_pct_month": smb_check["SMB_FF5"].mean()*100,
            "mean_abs_difference_bp": smb_check.diff(axis=1).iloc[:, 1].abs().mean()*10000,
        }, name="当前数据口径")
        display(smb_diagnostic.to_frame().round(4))
        save_table(smb_diagnostic.to_frame(), "07_smb_definition_comparison")
        '''),
        md(r'''
        ## 5. 因子均值是多空组合的历史报酬

        因子正收益意味着本月多头方向相对空头方向表现更好。
        它既不是对应特征在所有公司的“平均值”，也不保证未来每个月均为正。
        下表报告原研究样本内的均值及 HAC t 值，作为随后定价检验的背景。
        '''),
        code('''
        rows = []
        for name in factor_names:
            fit = sm.OLS(official[name].to_numpy(dtype=float), np.ones((len(official), 1))).fit(
                cov_type="HAC", cov_kwds={"maxlags": 6, "use_correction": True})
            rows.append({"factor": name, "mean_pct_month": official[name].mean()*100,
                         "sd_pct_month": official[name].std(ddof=1)*100,
                         "t_mean_hac": float(fit.tvalues[0])})
        factor_summary = pd.DataFrame(rows).set_index("factor")
        display(factor_summary.round(4))
        save_table(factor_summary, "07_factor_summary")
        '''),
        md('''
        ## 6. 与论文 Table 4 的原文数字并排看

        下面只使用已经逐页核实的 2×3 因子均值锚点。
        [打开原文 Table 4，第 7 页](../papers/ff2015_primary_reference.pdf#page=7)。
        原文值按其公布精度记录；“本次−原文”用于发现和解释差异，不作为必须归零的目标。
        '''),
        code('''
        import json
        paper_map = json.loads((ROOT / "papers" / "paper_map.json").read_text(encoding="utf-8"))
        factor_anchors = [a for a in paper_map["numeric_anchors"]
                          if a["paper"] == "ff2015" and a["table"] == "4"
                          and a["metric"] == "mean_factor_return"]
        anchor_rows = []
        for anchor in factor_anchors:
            current = official[anchor["key"]].mean()*100
            anchor_rows.append({"factor": anchor["key"], "paper_pct_month": anchor["paper_value"],
                                "current_pct_month": current,
                                "current_minus_paper_pp": current-anchor["paper_value"]})
        factor_paper_comparison = pd.DataFrame(anchor_rows).set_index("factor")
        display(factor_paper_comparison.round(4))
        save_table(factor_paper_comparison, "07_table4_paper_comparison")
        '''),
        md('''
        ## 通关证据与 Boss 作答区

        提交：构造公式与代码的对应关系、因子误差表、两种 SMB 的比较。

        **Boss：**如果有人把原三因子文件直接追加 RMW 和 CMA，
        你会要求他提供哪些证据来界定这个模型与标准五因子的关系？

        **你的回答：**

        （留空，运行与思考后填写。）
        '''),
    ]


def notebook08():
    return [
        md(r'''
        # 第 08 关：五因子的压力测试

        **本关目标：**检查新增因子在哪些测试资产上减少平均定价误差，以及哪些误差仍然存在。

        范围是 FF2015 的美国股票核心检验，固定使用 1963-07 至 2013-12 的 606 个月。
        我们使用当前公开数据版本及 2×3 构造因子，比较三套 25 组合和三套 32 组合。
        原论文还比较其他因子构造方式；本 Notebook 不声称重做了它的全部规格。
        本地 PDF 与下面的表格映射用于逐项对照，当前版本差异不应被隐瞒成代码误差。
        '''),
        code(SETUP),
        code('display(Markdown(paper_note("ff2015")))'),
        md(r'''
        ## 1. 先把模型比较定义清楚

        - **FF3 standard**：使用三因子文件中的 Mkt-RF、SMB、HML。
        - **FF3 common SMB**：从五因子文件取同名三列，与 FF5 保持公共因子完全相同。
        - **FF5**：使用五因子文件的全部五列。

        第二组比较用来观察固定公共因子后，加入 RMW、CMA 的变化。
        第一组则保留两套标准公开模型之间的比较。所有模型使用完全一致的测试月份与组合。
        '''),
        code('''
        START, END = "1963-07", "2013-12"
        ff3 = load_returns("ff3", START, END)
        ff5 = load_returns("ff5", START, END)
        assert ff3.index.equals(ff5.index) and len(ff5) == 606
        assert np.allclose(ff3["RF"], ff5["RF"])
        names3 = ["Mkt-RF", "SMB", "HML"]
        names5 = [*names3, "RMW", "CMA"]
        models = {"FF3 standard": ff3[names3],
                  "FF3 common SMB": ff5[names3],
                  "FF5": ff5[names5]}
        assets = {"Size × B/M (25)": "bm25", "Size × OP (25)": "op25", "Size × Inv (25)": "inv25",
                  "Size × B/M × OP (32)": "bm_op32", "Size × B/M × Inv (32)": "bm_inv32",
                  "Size × OP × Inv (32)": "op_inv32"}
        '''),
        md(r'''
        ## 2. 每组资产都检验相同的问题

        平均绝对 α 与 α 的均方根均以 **% / 月** 表示，概括误差的经济量级。
        $R^2$ 概括共同波动解释程度。GRS 的原假设是该组资产的所有 α 同时为零；
        本课程实现经典 GRS，使用它所对应的协方差和 F 分布假设。

        组内回归另报 HAC t 值，但不会把 HAC 协方差直接代入经典 GRS 公式。
        不同测试资产集有不同数量和不同残差相关结构，因此不要只按 p 值给模型排名。
        '''),
        code('''
        results, excess_by_set = [], {}
        for label, key in assets.items():
            returns = load_returns(key, START, END)
            assert returns.index.equals(ff5.index)
            excess = returns.sub(ff5["RF"], axis=0)
            assert not excess.isna().any().any()
            excess_by_set[label] = excess
            comparison = model_summary(excess, models)
            comparison["asset_set"] = label
            results.append(comparison.reset_index(names="model"))
        summary = pd.concat(results, ignore_index=True).set_index(["asset_set", "model"])
        columns = ["mean_abs_alpha_pct_month", "rms_alpha_pct_month", "mean_r2", "grs_stat", "grs_pvalue"]
        display(summary.loc[list(assets)[:3], columns].style.format(
            precision=4, formatter={"grs_pvalue": "{:.3g}"}))
        display(summary.loc[list(assets)[3:], columns].style.format(
            precision=4, formatter={"grs_pvalue": "{:.3g}"}))
        save_table(summary, "08_models_all_test_assets")
        '''),
        code('''
        error_chart = summary["mean_abs_alpha_pct_month"].unstack("model")
        error_chart = error_chart.loc[list(assets), list(models)]
        fig, ax = plt.subplots(figsize=(10, 5))
        error_chart.plot.barh(ax=ax, color=["#7b8994", "#c7953d", "#245b84"], width=0.78)
        ax.set_xlabel("平均绝对 α（% / 月）")
        ax.set_ylabel("")
        ax.set_title("同一原样本下，不同资产集的定价误差")
        ax.set_xlim(left=0)
        ax.legend(title="模型", loc="best")
        ax.invert_yaxis()
        fig.tight_layout()
        plt.show()
        '''),
        code('''
        delta = error_chart["FF3 common SMB"] - error_chart["FF5"]
        improvement_count = int((delta > 0).sum())
        display(Markdown(f"当前数据中，保持公共因子一致后，FF5 在 **{improvement_count}/{len(delta)}** "
            "组测试资产上的平均绝对 α 更小。这个统计描述的是同一样本中的误差变化，"
            "没有证明模型在其他资产、时期或样本外一定更好。"
            "请把图中的量级与上表的联合检验放在一起阅读。"))
        '''),
        md(r'''
        ## 3. 从汇总指标返回具体组合

        一项模型改进可能集中在少数组合。下面按 FF5 下绝对 α 排序，
        展示规模×盈利组合中误差最大的五个。方向、量级和估计精度都需要保留。
        这里的 t 值仍是逐个组合检验，不能替代联合检验。
        '''),
        code('''
        portfolio_results, residuals = fit_models(excess_by_set["Size × OP (25)"], models["FF5"])
        worst_names = portfolio_results["alpha"].abs().nlargest(5).index
        display(portfolio_results.loc[worst_names, ["alpha_pct_month", "t_alpha_ols", "t_alpha_hac", "r2"]].round(4))
        save_table(portfolio_results, "08_ff5_size_op_individual_regressions")
        '''),
        md(r'''
        ## 4. HML 的增量作用

        将 HML 的收益对其余四个因子回归，检查它是否还有未被解释的均值部分。
        这里 HML 已是多空因子收益，保持其原有定义作为被解释变量。

        $$
        HML_t=a+b\,MKT_t+s\,SMB_t+r\,RMW_t+c\,CMA_t+e_t.
        $$

        这检验的是指定样本和因子集合下的增量平均收益，
        还应与含 HML / 不含 HML 的测试资产定价结果一起看。
        '''),
        code('''
        other4 = ff5[["Mkt-RF", "SMB", "RMW", "CMA"]]
        hml_result, hml_residual = fit_models(ff5[["HML"]], other4)
        display(hml_result[["alpha_pct_month", "t_alpha_ols", "t_alpha_hac", "r2"]].round(4))
        four_five = model_summary(excess_by_set["Size × B/M (25)"], {"FF4 without HML": other4, "FF5": models["FF5"]})
        display(four_five[columns].style.format(precision=4, formatter={"grs_pvalue": "{:.3g}"}))
        save_table(hml_result, "08_hml_incremental_regression")
        save_table(four_five, "08_four_vs_five_size_bm")
        '''),
        code('''
        h = hml_result.loc["HML"]
        display(Markdown(f"本次 HML 增量回归的截距为 **{h['alpha_pct_month']:.4f}% / 月**，"
            f"HAC t 值为 **{h['t_alpha_hac']:.3f}**。这是当前样本与四个解释因子共同决定的估计，"
            "描述的是条件增量表现。它不识别价值特征为何与收益相关，也不能直接外推到未来。"))
        '''),
        md(r'''
        ## 5. 对照详细系数表时，重建 HMLO

        [原文 Table 7，第 13 页](../papers/ff2015_primary_reference.pdf#page=13)
        的五因子详细系数使用 **HMLO**。在前面的 HML 回归中，令 HMLO 为“截距 + 残差”，
        即从 HML 中减去其他四个因子的线性斜率部分，而不删除常数。
        Table 9、10、11、A2、A3 的详细五因子回归也采用这种表示。

        这种重参数化改变了部分斜率的解释，保留了同一个五因子模型的拟合值。
        下面通过数值核验 α、残差和 $R^2$ 的一致性，再展示规模×价值 25 组合的详细系数。
        系数是无量纲暴露，α 列仍为 % / 月；t 值标为常规 OLS，HAC 结果另列。
        '''),
        code('''
        hmlo = hml_result.loc["HML", "alpha"] + hml_residual["HML"]
        orthogonal_factors = ff5[["Mkt-RF", "SMB", "RMW", "CMA"]].copy()
        orthogonal_factors.insert(2, "HMLO", hmlo)
        bm_excess = excess_by_set["Size × B/M (25)"]
        original_details, original_residuals = fit_models(bm_excess, models["FF5"])
        hmlo_details, hmlo_errors = fit_models(bm_excess, orthogonal_factors)
        equivalence = pd.Series({
            "max_alpha_difference": (hmlo_details["alpha"]-original_details["alpha"]).abs().max(),
            "max_r2_difference": (hmlo_details["r2"]-original_details["r2"]).abs().max(),
            "max_residual_difference": (hmlo_errors-original_residuals).abs().to_numpy(dtype=float).max(),
            "max_HML_loading_difference": (hmlo_details["beta_HMLO"]-original_details["beta_HML"]).abs().max(),
        }, name="重参数化核验")
        assert (equivalence < 1e-10).all()
        display(equivalence.to_frame().style.format("{:.3g}"))
        x_hmlo = sm.add_constant(orthogonal_factors)
        for asset in bm_excess:
            detailed_fit = sm.OLS(bm_excess[asset], x_hmlo).fit()
            for name in orthogonal_factors:
                hmlo_details.loc[asset, "t_ols_" + name] = detailed_fit.tvalues[name]
        detail_columns = ["alpha_pct_month", "t_alpha_ols", "beta_Mkt-RF", "beta_SMB", "beta_HMLO", "beta_RMW", "beta_CMA"]
        display(hmlo_details[detail_columns].style.format(precision=4))
        save_table(hmlo_details, "08_table7_hmlo_detailed_coefficients")
        save_table(equivalence.to_frame(), "08_hmlo_equivalence_checks")
        '''),
        md('''
        ## 6. 原文数字与当前快照重算值

        [Table 5，第 9 页](../papers/ff2015_primary_reference.pdf#page=9) 对照两个资产面板的
        联合检验与平均绝对 α；三因子一栏取“FF3 common SMB”，保持原文 2×3 因子集合的口径。
        [Table 6，第 11 页](../papers/ff2015_primary_reference.pdf#page=11) 对照 HML 的增量回归。
        原文 t 值匹配常规 OLS，不把 HAC t 值与它混比。

        下面的原文数字来自本地已核实的论文导航文件。数据修订、OP 定义更新和 CRSP 收益处理变化，
        都可能带来差异；这张表保留差值，便于你定位，而不会为了匹配原文调节结果。
        '''),
        code('''
        import json
        paper_map = json.loads((ROOT / "papers" / "paper_map.json").read_text(encoding="utf-8"))
        asset_lookup = {"25 Size-B/M": "Size × B/M (25)", "32 Size-OP-Inv": "Size × OP × Inv (32)"}
        model_lookup = {"FF3_FF5_SMB": "FF3 common SMB", "FF5": "FF5"}
        metric_lookup = {"GRS": "grs_stat", "mean_absolute_alpha": "mean_abs_alpha_pct_month"}
        spanning_lookup = {"spanning_alpha": "alpha_pct_month", "spanning_alpha_t": "t_alpha_ols", "r_squared": "r2"}
        anchor_rows = []
        for anchor in paper_map["numeric_anchors"]:
            if anchor["paper"] != "ff2015" or anchor["table"] not in ("5", "6"):
                continue
            if anchor["table"] == "5":
                current = summary.loc[(asset_lookup[anchor["key"]], model_lookup[anchor["model"]]), metric_lookup[anchor["metric"]]]
                item = f"Table 5{anchor['panel']} / {anchor['model']} / {anchor['metric']}"
            else:
                current = hml_result.loc["HML", spanning_lookup[anchor["metric"]]]
                item = "Table 6 / HML / " + anchor["metric"]
            anchor_rows.append({"item": item, "paper_value": anchor["paper_value"],
                                "current_value": current, "current_minus_paper": current-anchor["paper_value"],
                                "unit": anchor["unit"]})
        paper_comparison = pd.DataFrame(anchor_rows).set_index("item")
        display(paper_comparison.style.format(precision=4))
        save_table(paper_comparison, "08_table5_table6_paper_comparison")
        '''),
        md('''
        ## 通关证据与 Boss 作答区

        提交：六组测试资产的比较表、一个误差较大组合的分析、HML 增量检验与删因子比较。

        **Boss：**如果 HML 回归的截距不显著，你将怎样表述结论，哪些更强的说法需要额外证据？

        **你的回答：**

        （留空，运行与思考后填写。）
        '''),
    ]


def notebook09():
    return [
        md(r'''
        # 第 09 关：离开原样本

        **本关目标：**在固定研究设计下，区分原样本后的定价检验与冻结估计后的平均收益预测。

        训练区间预设为 1963-07—2013-12，留出区间为 2014-01—2025-12。
        测试资产包括 25 个规模×账面市值比组合，以及另一类公开的 30 个行业组合。
        不依据结果挑选起止日期，也不为改善结果临时删除组合。

        **边界：**这是相对 FF2015 原样本的留出设计。模型于 2015 年发表，且我们使用当前修订数据，
        因此从 2014 年开始的实验并不是当时已可实施的实时交易回测。
        它也没有计算换手、交易成本或做空约束。
        '''),
        code(SETUP),
        code('display(Markdown(paper_note("ff2015")))'),
        md(r'''
        ## 1. 固定比较对象与期间

        行业组合的形成维度与规模/价值排序不同，能提供另一种检验角度。
        同时保留这两类资产，有助于观察结论是否依赖测试资产的选取。
        官方收益组合中每个月的成分可能变化；我们直接使用公布收益，不把今天的公司名单套回历史。
        '''),
        code('''
        PERIODS = {"原样本 1963-2013": ("1963-07", "2013-12"),
                   "留出期 2014-2025": ("2014-01", "2025-12")}
        ASSETS = {"Size × B/M (25)": "bm25", "Industries (30)": "industry30"}
        names3 = ["Mkt-RF", "SMB", "HML"]
        names5 = [*names3, "RMW", "CMA"]
        display(pd.DataFrame([{"时期": label, "开始": start, "结束": end,
                               "预期月份数": len(pd.period_range(start, end, freq="M"))}
                              for label, (start, end) in PERIODS.items()]))
        '''),
        md(r'''
        ## 2. 实验 A：在每个时期内重新检验定价

        对两个时期分别估计暴露与 α。这回答“模型能否解释这个时期的平均收益”，
        并没有用训练期的参数去预测后面的收益。
        原样本与留出期长度不同，因此 p 值和检验功效不能直接当作可比较的模型分数。
        '''),
        code('''
        comparisons = []
        for period_label, (start, end) in PERIODS.items():
            ff3 = load_returns("ff3", start, end)
            ff5 = load_returns("ff5", start, end)
            assert ff3.index.equals(ff5.index)
            assert len(ff5) == len(pd.period_range(start, end, freq="M"))
            assert np.allclose(ff3["RF"], ff5["RF"])
            models = {"FF3 standard": ff3[names3], "FF5": ff5[names5]}
            for label, key in ASSETS.items():
                returns = load_returns(key, start, end)
                assert returns.index.equals(ff5.index)
                excess = returns.sub(ff5["RF"], axis=0)
                result = model_summary(excess, models).reset_index(names="model")
                result["period"], result["asset_set"] = period_label, label
                comparisons.append(result)
        within_period = pd.concat(comparisons, ignore_index=True).set_index(["period", "asset_set", "model"])
        fields = ["mean_abs_alpha_pct_month", "mean_r2", "grs_stat", "grs_pvalue", "T", "N"]
        display(within_period[fields].style.format(precision=4,
            formatter={"grs_pvalue": "{:.3g}", "T": "{:.0f}", "N": "{:.0f}"}))
        save_table(within_period, "09_reestimated_period_pricing_tests")
        '''),
        md(r'''
        ## 3. 实验 B：只用训练期信息形成平均收益预测

        训练期估计每个组合的暴露 $\hat{\beta}_{i,\mathrm{train}}$，同时估计因子的训练期均值 $\bar{f}_{\mathrm{train}}$。
        线性定价模型在 α=0 的约束下，给出冻结的月均超额收益预测：

        $$
        \widehat{E}[R_i^e]=\hat{\beta}_{i,\mathrm{train}}'\bar{f}_{\mathrm{train}}.
        $$

        后面只拿留出期实际平均超额收益来评价这份预测，不重新估计暴露、不加入训练期 α。
        这是一份静态平均收益预测，仍依赖暴露和风险溢价在两个时期之间足够稳定。
        留出期只有有限月份，它的实现均值也具有抽样不确定性。
        '''),
        code('''
        train_start, train_end = PERIODS["原样本 1963-2013"]
        test_start, test_end = PERIODS["留出期 2014-2025"]
        train3 = load_returns("ff3", train_start, train_end)
        train5 = load_returns("ff5", train_start, train_end)
        test5 = load_returns("ff5", test_start, test_end)
        train_models = {"FF3 standard": train3[names3], "FF5": train5[names5]}
        prediction_frames, scores = {}, []
        for label, key in ASSETS.items():
            train_returns = load_returns(key, train_start, train_end)
            test_returns = load_returns(key, test_start, test_end)
            assert train_returns.index.equals(train5.index)
            assert test_returns.index.equals(test5.index)
            assert train_returns.columns.equals(test_returns.columns)
            train_excess = train_returns.sub(train5["RF"], axis=0)
            observed = test_returns.sub(test5["RF"], axis=0).mean()
            for model_name, factors in train_models.items():
                fit_table, _ = fit_models(train_excess, factors)
                beta_columns = ["beta_" + name for name in factors]
                predicted = pd.Series(fit_table[beta_columns].to_numpy(dtype=float) @ factors.mean().to_numpy(dtype=float),
                                      index=fit_table.index)
                observed_for_model = observed.reindex(predicted.index)
                error = observed_for_model - predicted
                frame = pd.DataFrame({"predicted_pct_month": predicted*100,
                                      "observed_pct_month": observed_for_model*100,
                                      "prediction_error_pct_month": error*100})
                prediction_frames[(label, model_name)] = frame
                scores.append({"asset_set": label, "model": model_name,
                               "mae_pct_month": error.abs().mean()*100,
                               "rmse_pct_month": np.sqrt(np.mean(error**2))*100,
                               "mean_error_pct_month": error.mean()*100})
        prediction_scores = pd.DataFrame(scores).set_index(["asset_set", "model"])
        display(prediction_scores.round(4))
        save_table(prediction_scores, "09_frozen_expected_return_prediction_scores")
        for (label, model_name), frame in prediction_frames.items():
            key = "bm25" if "B/M" in label else "industry30"
            model_key = "ff3" if "FF3" in model_name else "ff5"
            save_table(frame, f"09_frozen_predictions_{key}_{model_key}")
        '''),
        code('''
        frames = [prediction_frames[("Size × B/M (25)", name)] for name in train_models]
        all_values = np.concatenate([frame[["predicted_pct_month", "observed_pct_month"]].to_numpy(dtype=float).ravel()
                                     for frame in frames])
        lo, hi = all_values.min(), all_values.max()
        pad = max((hi-lo)*0.1, 0.02)
        limits = [lo-pad, hi+pad]
        fig, axes = plt.subplots(1, 2, figsize=(10, 4.6), sharex=True, sharey=True)
        for ax, (name, frame) in zip(axes, zip(train_models, frames)):
            ax.scatter(frame["predicted_pct_month"], frame["observed_pct_month"],
                       color="#245b84", edgecolors="#243440", alpha=0.85)
            ax.plot(limits, limits, color="#666666", linewidth=1)
            ax.set_xlim(limits); ax.set_ylim(limits)
            ax.set_title(name)
            ax.set_xlabel("训练期冻结预测（% / 月）")
        axes[0].set_ylabel("2014–2025 实现均值（% / 月）")
        fig.suptitle("25 个规模×价值组合：静态平均超额收益预测")
        fig.tight_layout()
        plt.show()
        '''),
        code('''
        reference = prediction_scores.loc[("Size × B/M (25)", "FF5")]
        display(Markdown(f"在固定的 25 个规模×价值组合上，FF5 的训练期冻结预测对应 "
            f"**{reference['mae_pct_month']:.3f}% / 月**的平均绝对预测误差，"
            f"均值误差为 **{reference['mean_error_pct_month']:.3f}% / 月**。"
            "这列误差是留出期实现均值减冻结预测，不能命名为重新估计得到的样本外 α。"
            "它同时可能反映风险溢价变化、暴露变化、模型设定误差与有限样本噪声；"
            "单独这张图不能识别各项贡献。"))
        '''),
        md('''
        ## 4. 写你的研究结论

        用下面五个问题组织一页报告，并为每句经验判断指出对应输出：

        1. 原样本中，三因子与五因子的平均定价误差各有多大？
        2. 换到留出期后，哪些结果发生变化？
        3. 换成行业组合，比较是否仍然相同？
        4. 实验 A 与实验 B 分别识别什么，哪些数字不能混称？
        5. 当前公开数据版本与原论文数据版本的差异，如何限制“逐表复现”的说法？

        **报告正文：**

        （在此填写，引用前面的表或图。）
        '''),
        md('''
        ## 最终 Boss 作答区

        **Boss：**如果五因子在原样本的排序组合上表现较好，但在留出期行业组合上的证据较弱，
        你会如何给出一个不超出证据的模型评价？下一项检验会是什么，为什么？

        **你的回答：**

        （留空，运行与思考后填写。）

        通关证据：可重跑的完整 Notebook、原样本与留出期比较表、冻结预测表，以及你的一页研究结论。
        '''),
    ]


def main():
    write_notebook("06_fama_macbeth.ipynb", notebook06())
    write_notebook("07_build_ff5.ipynb", notebook07())
    write_notebook("08_ff5_replication.ipynb", notebook08())
    write_notebook("09_out_of_sample.ipynb", notebook09())


if __name__ == "__main__":
    main()
