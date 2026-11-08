"""市场 beta 到 factor zoo 的前导课生成器；不修改其他课程文件。"""
from pathlib import Path
from textwrap import dedent
import re
import nbformat as nbf

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "notebooks/PRELUDE_beta_to_factor_zoo.ipynb"

def md(text):
    source = dedent(text).strip()
    # 中文标点邻接的 ** 在不同 Markdown 渲染器中可能被当作字面量。
    source = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", source, flags=re.S)
    return nbf.v4.new_markdown_cell(source)

def code(text):
    return nbf.v4.new_code_cell(dedent(text).strip())

def build():
    cells = [
        md(r"""
        # 前导课：市场 β 从哪里来，为什么走到 factor zoo？

        **学习目标：**把投资者为什么关心协方差、均衡如何给协方差定价，以及研究者怎样检验这些限制连起来。
        历史并不是“一个因子失败，于是不断往回归里加变量”的直线。
        **投资组合与均衡理论、收益的统计表示、经验异象和检验方法**一直并行发展。

        本课先推导市场 β，再沿这些线索追踪到大量候选因子的筛选问题。
        所有演示使用已经下载的公开数据；这是一堂教学实验，不声称复现各篇论文的全部表格。
        """),
        md(r"""
        ## 运行约定

        在 VS Code 中选择课程 Python 环境，依次执行所有单元，或点击 Run All。
        演示固定使用 1963-07 至 2013-12，收益均为月度小数。
        当前数据库会修订历史，相同样本日期不保证数字等于论文发表时的数据。
        三次小实验分别核对 β、构造 HML、比较定价模型。
        """),
        code("""
        from pathlib import Path
        import sys
        ROOT = next((p for p in [Path.cwd(), *Path.cwd().parents]
                     if (p / "src/course.py").exists()), None)
        if ROOT is None:
            raise RuntimeError("请在 asset_pricing_quest 项目或其 notebooks 文件夹启动。")
        if str(ROOT / "src") not in sys.path:
            sys.path.insert(0, str(ROOT / "src"))
        import numpy as np
        import pandas as pd
        import matplotlib.pyplot as plt
        import statsmodels.api as sm
        from IPython.display import display, Markdown
        from course import load_returns, style, save_table
        from analysis import model_summary
        style()
        START, END = "1963-07", "2013-12"
        ff3 = load_returns("ff3", START, END)
        ff5 = load_returns("ff5", START, END)
        portfolios = load_returns("bm25", START, END)
        assert ff3.index.equals(ff5.index) and ff3.index.equals(portfolios.index)
        assert len(ff3) == 606
        assert np.allclose(ff3["RF"], ff5["RF"])
        excess = portfolios.sub(ff3["RF"], axis=0)
        assert np.isfinite(excess.to_numpy(dtype=float)).all()
        display(pd.DataFrame({"对象": ["因子", "规模 × B/M 测试组合"],
                              "月份数": [len(ff3), len(excess)],
                              "起点": [str(ff3.index[0])]*2, "终点": [str(ff3.index[-1])]*2}))
        """),
        md(r"""
        ## 1. 四种对象不能混用

        | 对象 | 记号与例子 | 数据形式 |
        |---|---|---|
        | 公司特征 | $z_{i,t}$：市值、B/M、过去收益、盈利率 | 一家公司在一个时点的特征 |
        | 因子实现值 | $f_t$：市场超额收益、SMB、HML | 一个日期的共同收益或经济冲击 |
        | 风险暴露 | $\beta_{i,k}$：对第 $k$ 个因子的敏感度 | 资产对因子的斜率 |
        | 风险价格 | $\lambda_k$：每单位暴露对应的预期超额收益 | 定价关系中的价格 |

        “市值小”是一项特征，“SMB 本月上涨”是一项因子收益，“SMB 暴露为 0.8”是敏感度描述。
        若可交易因子是超额收益或规范化的自融资组合收益，且同一正确模型也为因子组合自身定价，
        则 $\lambda=E[f]$。对消费增长等非交易宏观因子，均值一般不等于风险价格。
        """),
        md(r"""
        ## 2. 市场 β 的经济来源：先最优，再市场出清

        考虑单期均值—方差投资者，风险厌恶系数 $\gamma>0$。$\mu^e$ 是风险资产预期超额收益向量，$\Sigma$ 是收益协方差矩阵，
        $w$ 是风险资产权重，剩余财富放在无风险资产。教学设定允许自由借贷且没有额外组合约束：

        $$
        \max_w\;w'\mu^e-\frac{\gamma}{2}w'\Sigma w
        \quad\Longrightarrow\quad
        \mu^e=\gamma\Sigma w.
        $$

        这只是**个人最优条件**。加入共同预期等 CAPM 假设，并令市场出清，
        共同风险组合在总量上必须等于市场组合。因此存在共同价格系数 $\kappa$：

        $$
        \mu^e=\kappa\Sigma w_M.
        $$

        第 $i$ 个分量是 $\mu_i^e=\kappa\operatorname{Cov}(R_i,R_M)$。
        左乘 $w_M'$ 得到 $\mu_M^e=\kappa\operatorname{Var}(R_M)$，消去 $\kappa$：

        $$
        E[R_i]-R_f
        =\underbrace{\frac{\operatorname{Cov}(R_i,R_M)}
        {\operatorname{Var}(R_M)}}_{\beta_{i,M}}
        \left(E[R_M]-R_f\right).
        $$

        β 衡量资产对市场财富组合边际共同风险的贡献；分母把它换算成每单位市场风险的尺度。
        两只股票即使总波动相同，对现有组合的风险贡献也可以不同：市场低迷时仍能提供收益的资产具有保险价值。
        举一个教学假设：若年无风险收益率为 2%、市场预期超额收益为 6%，β 为 1.5 的资产在 CAPM 下预期年收益为 11%。
        这个例子表达模型要求的预期回报，不保证某年的实际收益。
        理论市场组合包括全部风险资产，股票指数只是实证代理。
        只有一个被定价的市场协方差方向，**不意味着每只资产只受一个随机冲击**。
        参见 [Markowitz（1952）](https://doi.org/10.1111/j.1540-6261.1952.tb01525.x)、
        [Sharpe 的作者回顾](https://web.stanford.edu/~wfsharpe/art/djam/djam)。
        """),
        md(r"""
        ## 3. β 的统计来源与 CAPM 的额外限制

        给定市场代理，含截距的一元线性投影是

        $$
        R^e_{i,t}=\alpha_i+\beta_iR^e_{M,t}+\varepsilon_{i,t},
        \qquad
        \beta_i=\frac{\operatorname{Cov}(R^e_i,R^e_M)}{\operatorname{Var}(R^e_M)}.
        $$

        含截距 OLS 的正规方程使残差与解释变量正交，从而得到同一个协方差比率。
        **能够估出 β 是统计事实，预期收益满足 CAPM 则要求定价限制。**
        在本课常数参数、无条件规格中，CAPM 对资产要求 $\alpha_i=0$。

        Sharpe（1963）的单指数表示主要简化组合分析所需的协方差结构；
        Sharpe（1964）的 CAPM 从均衡讨论预期收益。两者不可混称。
        条件 CAPM 可以有时变 β 与时变风险溢价，它不能自动推出这里的常数 β 无条件回归限制。
        [1963 原论文](https://doi.org/10.1287/mnsc.9.2.277)；
        [1964 原论文](https://doi.org/10.1111/j.1540-6261.1964.tb02865.x)。
        """),
        md(r"""
        ## 实验 A：同一个 β，用三种写法计算

        选择“小规模、低 B/M”组合，市场代理使用官方 Mkt-RF。
        实际 RF 逐月变化，所以协方差比率中的两项都使用**超额收益**，不以原始收益替代。
        协方差和方差采用相同月份与自由度分母。
        """),
        code("""
        ASSET = "SMALL LoBM"
        x = ff3["Mkt-RF"].to_numpy(dtype=float)
        y = excess[ASSET].to_numpy(dtype=float)
        beta_cov = np.cov(y, x, ddof=1)[0, 1] / np.var(x, ddof=1)
        xc, yc = x-x.mean(), y-y.mean()
        beta_centered = np.dot(xc, yc) / np.dot(xc, xc)
        fitted = sm.OLS(y, sm.add_constant(x)).fit()
        beta_ols = float(fitted.params[1])
        assert np.allclose([beta_cov, beta_centered], beta_ols, rtol=1e-12, atol=1e-12)
        beta_check = pd.DataFrame({"beta": [beta_cov, beta_centered, beta_ols]},
                                 index=["Cov / Var", "中心化内积", "含截距 OLS"])
        display(beta_check.round(10))
        save_table(beta_check, "PRELUDE_beta_identity")

        fig, ax = plt.subplots(figsize=(8, 4.8))
        ax.scatter(x*100, y*100, s=18, alpha=0.45, color="#245b84", label="月度观测")
        grid = np.linspace(x.min(), x.max(), 100)
        ax.plot(grid*100, (fitted.params[0]+beta_ols*grid)*100,
                color="#a97725", linewidth=2, label="含截距 OLS")
        ax.set_xlabel("市场超额收益（% / 月）")
        ax.set_ylabel("小规模、低 B/M 组合超额收益（% / 月）")
        ax.set_title("β 是这条线的斜率，CAPM 还约束它的截距")
        ax.legend()
        fig.tight_layout()
        plt.show()
        display(Markdown(
            f"当前 β 为 **{beta_ols:.4f}**，三种计算在数值精度内一致。"
            f"截距为 **{fitted.params[0]*100:.4f}% / 月**，普通 $R^2$ 为 **{fitted.rsquared:.4f}**。"
            "这些数分别描述敏感度、未解释的平均超额收益与共同波动解释程度；"
            "这项回归没有把市场变化识别为可操纵的因果冲击。"))
        """),
        md(r"""
        ## 4. 1952—1979：理论与检验并行扩展

        | 文献节点 | 推进的问题 | 阅读要点 |
        |---|---|---|
        | [Markowitz 1952](https://doi.org/10.1111/j.1540-6261.1952.tb01525.x) | 组合如何权衡均值与方差？ | 风险取决于协方差 |
        | [Tobin 1958](https://doi.org/10.2307/2296205) | 加入无风险资产后如何分离风险组合选择与风险承受？ | 分离思想；再加入均衡才将共同风险组合联系到市场 |
        | [Sharpe 1963](https://doi.org/10.1287/mnsc.9.2.277) | 如何降低组合分析的计算维度？ | 单指数统计表示 |
        | [Sharpe 1964](https://doi.org/10.1111/j.1540-6261.1964.tb02865.x)、[Lintner 1965](https://doi.org/10.2307/1924119)、[Mossin 1966](https://doi.org/10.2307/1910098) | 市场出清时，何种风险获得报酬？ | 均衡与预期收益—β 关系 |
        | [Black–Jensen–Scholes 1972](https://ssrn.com/abstract=908569) | 如何用组合与回归检验 CAPM？ | β 排序、组合化与经验限制 |
        | [Fama–MacBeth 1973](https://doi.org/10.1086/260061) | 怎样估计风险价格与其不确定性？ | 每月截面回归与系数的时间平均；原文并非简单宣布 CAPM 被推翻 |
        | [Merton 1973](https://doi.org/10.2307/1913811) | 投资者还要对冲未来投资机会的变化时怎么办？ | 状态变量与跨期对冲需求 |
        | [Ross 1976](https://doi.org/10.1016/0022-0531(76)90046-6) | 多个共同收益方向受何种无套利约束？ | APT 的因子结构、分散化与近似线性定价；不自动指定因子名称 |
        | [Breeden 1979](https://doi.org/10.1016/0304-405X(79)90016-3) | 风险如何联系消费与边际效用？ | 消费 β |

        多因子理论早于 FF1993。FF 的贡献之一，是把可观察特征、可复算的组合收益与广泛的定价检验连接起来。
        """),
        md(r"""
        ## 5. 异象怎样推动新因子？

        如果控制市场 β 后，某些按特征排序的组合仍有系统性平均收益差，
        就需要追问遗漏风险、错定价、数据和检验问题，或者样本偶然。

        例如 [Banz（1981）](https://doi.org/10.1016/0304-405X(81)90018-0) 报告小公司相对于其市场风险的平均收益偏高。
        规模、估值的经验规律在 FF 之前已出现；FF1992 将多个候选解释放在一起比较。

        [FF1992](https://doi.org/10.1111/j.1540-6261.1992.tb04398.x) 重点考察公司特征与平均收益的截面关系；
        [FF1993 本地原文](../papers/ff1993_primary_reference.pdf) 用排序组合构造 SMB、HML 收益因子，
        再检验这些共同收益方向能否解释其他组合。
        1993 全文还研究 TERM、DEF 债券因子，它们与 2015 股票五因子不是同一组“五因子”。
        """),
        md(r"""
        ## 6. 三因子之后的几条路线

        | 节点 | 主要推进 | 与本课程的联系 |
        |---|---|---|
        | Fama–French 1993 | 市场、规模、价值因子，并分析股票与债券 | 第 04–05 关复算股票部分 |
        | [Jegadeesh–Titman 1993](https://doi.org/10.1111/j.1540-6261.1993.tb04702.x) | 过去赢家与输家的中期收益延续 | 动量是另一类排序方向 |
        | [Carhart 1997](https://doi.org/10.1111/j.1540-6261.1997.tb03808.x) | 在基金业绩持续性研究中加入动量 | 股票四因子回归不等于完整复现基金论文 |
        | [Novy-Marx 2013](https://doi.org/10.1016/j.jfineco.2013.01.003) | 毛盈利能力与平均收益的关系 | 毛利润/资产与 FF5 的营业盈利能力指标定义不同 |
        | [Fama–French 2015](../papers/ff2015_primary_reference.pdf) | 用盈利 RMW 与投资 CMA 扩展模型 | 第 07–08 关 |
        | [Hou–Xue–Zhang 2015](https://doi.org/10.1093/rfs/hhu068) | 市场、规模、投资与盈利的 q 模型 | 名称接近也不意味着理论和构造相同 |

        盈利与投资的估值动机有条件限制：给定 B/M 与投资，较高预期盈利对应较高预期收益；
        给定 B/M 与盈利，较高预期投资对应较低预期收益。
        不能省略这些条件，也不能直接把它说成“提高盈利造成未来股价上涨”。
        """),
        md(r"""
        ## 实验 B：特征怎样成为因子收益？

        B/M 用来给股票分组，HML 是分组后的多空**收益率**。
        使用官方六组合完成品，计算高 B/M 减低 B/M。大小规模两档使用相同权重，
        组内收益已经按官方规则市值加权。这个代数实验不重建个股财报。
        [官方六组合定义](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library/six_portfolios.html)

        $$
        HML_t=\frac{S_{H,t}+B_{H,t}}{2}-\frac{S_{L,t}+B_{L,t}}{2}.
        $$
        """),
        code("""
        six = load_returns("bm6", START, END)
        assert six.shape[1] == 6 and six.index.equals(ff3.index)
        display(pd.DataFrame({"列位置": range(6), "官方列名": six.columns,
                              "角色": ["S低", "S中", "S高", "B低", "B中", "B高"]}))
        hml_built = (six.iloc[:, 2]+six.iloc[:, 5]-six.iloc[:, 0]-six.iloc[:, 3])/2
        error_bp = (hml_built-ff3["HML"])*10000
        hml_check = pd.DataFrame({"手工HML（%/月）": hml_built.head(4)*100,
                                 "官方HML（%/月）": ff3["HML"].head(4)*100,
                                 "误差（bp）": error_bp.head(4)})
        display(hml_check.round(5))
        save_table(hml_check, "PRELUDE_hml_construction_preview")
        display(Markdown(
            f"606 个月最大绝对差为 **{error_bp.abs().max():.4f} bp / 月**。"
            "因子与基础组合文件的公布小数位不同，核对时应保留精度说明。"
            "完成 HML 构造后，它能否改善其他资产的定价仍需要检验。"))
        """),
        md(r"""
        ## 7. 多因子实证的两条主线

        **时间序列检验：**对每个测试组合估计

        $$
        R^e_{i,t}=\alpha_i+\beta_i'f_t+\varepsilon_{i,t}.
        $$

        观察 α 的经济量级、各自的标准误及一组 α 的联合检验。
        对可交易收益因子，零 α 限制是一种直接可用的定价检验。

        **两步截面检验：**先估计暴露，再逐期估计

        $$
        R^e_{i,t}=\lambda_{0,t}+\hat{\beta}_{i,t-1}'\lambda_t+u_{i,t}.
        $$

        这条教学写法使用过去窗口 β；明确标注的样本内研究也可能用全样本 β。
        真正声称事前预测或策略可实施时，不能用未来数据估计当时暴露。
        最后对各期 $\lambda_t$ 取时间平均，估计每单位暴露的平均补偿，并用系数时间序列进行推断。
        若右侧换成市值、B/M 等公司特征，估计的是特征与收益的关系，系数不会自动成为风险价格。
        推断还要考虑估计误差、时间依赖与生成解释变量问题，第 06 关会继续拆解。
        """),
        md(r"""
        ## 实验 C：相同资产与月份上的三模型比较

        CAPM、经典 FF3、FF5 共用样本与 25 个测试组合。
        FF3 使用三因子文件的 SMB，FF5 使用五因子文件的 SMB，两者构造不同。
        因此这**只是教学示范，不是 FF2015 Table 5 的原样复现**；
        对应该表的公共 SMB 规格已在 [第 08 关](08_ff5_replication.ipynb) 单列。

        平均绝对 α 关注平均定价误差，平均 $R^2$ 关注共同波动。
        相同样本、相同公共因子定义的嵌套 OLS 增加解释变量时，$R^2$ 会机械提高或不变；
        这个性质本身不构成经济解释。本例经典 FF3 与 FF5 因 SMB 不同而非严格嵌套。
        """),
        code("""
        names3 = ["Mkt-RF", "SMB", "HML"]
        models = {"CAPM": ff3[["Mkt-RF"]],
                  "FF3 classic": ff3[names3],
                  "FF5": ff5[[*names3, "RMW", "CMA"]]}
        comparison = model_summary(excess, models)
        columns = ["mean_abs_alpha_pct_month", "rms_alpha_pct_month",
                   "mean_r2", "grs_stat", "grs_pvalue", "T", "N", "K"]
        display(comparison[columns].style.format(precision=4,
                formatter={"grs_pvalue": "{:.3g}", "T": "{:.0f}", "N": "{:.0f}", "K": "{:.0f}"}))
        save_table(comparison, "PRELUDE_model_comparison")
        fig, axes = plt.subplots(1, 2, figsize=(10, 4.4))
        colors = ["#7b8994", "#c7953d", "#245b84"]
        axes[0].bar(comparison.index, comparison["mean_abs_alpha_pct_month"], color=colors)
        axes[0].set_ylabel("平均绝对 α（% / 月）")
        axes[0].set_ylim(bottom=0)
        axes[0].set_title("平均收益的定价误差")
        axes[1].bar(comparison.index, comparison["mean_r2"], color=colors)
        axes[1].set_ylabel("平均 R²")
        axes[1].set_ylim(0, 1)
        axes[1].set_title("时间序列拟合程度")
        fig.suptitle("1963-07—2013-12；同一组 25 个规模 × B/M 组合")
        fig.tight_layout()
        plt.show()
        """),
        code("""
        c, t, v = [comparison.loc[name] for name in ["CAPM", "FF3 classic", "FF5"]]
        display(Markdown(
            f"平均绝对 α 依次是 **{c['mean_abs_alpha_pct_month']:.4f}**、"
            f"**{t['mean_abs_alpha_pct_month']:.4f}**、**{v['mean_abs_alpha_pct_month']:.4f}% / 月**。"
            f"平均 $R^2$ 依次是 **{c['mean_r2']:.3f}**、**{t['mean_r2']:.3f}**、**{v['mean_r2']:.3f}**。"
            "这些是当前快照和这组排序组合上的样本内证据。"
            "GRS 的 p 值检验各自模型的联合零 α 假设，不是两个模型优劣差异的直接检验。"
            "这里还没有用交易成本、真实可交易性或跨市场表现来评价模型。"))
        """),
        md(r"""
        ## 8. 2011 以后：从发现因子到整理 factor zoo

        | 节点 | 新问题 | 实操含义 |
        |---|---|---|
        | [Cochrane 2011，Discount Rates](https://www.johnhcochrane.com/s/discount_rates_jf.pdf) | 大量折现率与横截面规律如何共同解释？ | 不能只报告一项新的显著相关性 |
        | [Harvey–Liu–Zhu 2016](https://people.duke.edu/~charvey/Research/Published_Papers/P118_and_the_cross.PDF) | 大量候选因子的多重检验 | 传统 t≈2 门槛不足以处理广泛搜索；具体调整取决于设计 |
        | [Hou–Xue–Zhang 2020，Replicating Anomalies](https://doi.org/10.1093/rfs/hhy131) | 在一致规则下复查异象 | 样本、微盘股、权重与实现细节影响复现 |
        | [Gu–Kelly–Xiu 2020，机器学习资产定价](https://dachxiu.chicagobooth.edu/download/ML.pdf) | 高维、非线性与交互如何预测收益？ | 训练/验证/测试分离；预测能力、定价能力、因果解释分别评价 |
        | [Open Source Asset Pricing](https://www.openassetpricing.com/) | 让信号和代码可检查 | 公开完成品也要记录定义与版本 |

        “Zoo” 概括候选变量繁多、相关且经过反复搜索的局面，
        不表示每个变量都已被证明是独立风险，也不表示所有经验研究都可归为同一种错误。
        """),
        md(r"""
        ## 9. 真正做一次多因子实证

        1. **固定研究对象。**检验平均收益、预测未来收益，还是评价基金业绩？预先写样本、资产集与模型。
        2. **建立时点可得信息。**财报年度不等于公告日期；处理退市、证券链接与存活者偏差。
        3. **明确排序。**断点使用哪类股票、独立还是条件排序、何时再平衡、等权还是市值加权？
        4. **明确因子定义。**记录多头/空头、规模控制、权重和版本；名字相同不保证实现相同。
        5. **安排独立检验证据。**测试组合与因子本身区分，加入未用于挑选因子的资产和预设留出期。
           “独立检验”指研究设计，而不要求测试资产与因子统计独立。
        6. **同时报告量级与不确定性。**α、标准误、联合检验、样本数和单位一起给出。
        7. **尝试可证伪扩展。**换资产、换时期、控制微盘股、考虑交易成本，记录成功与失败。

        本地官方完成品足以复算构造代数、回归和联合检验，同时尚未独立验证个股层面的全部数据工程。
        [French 官方数据库与定义](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html)。
        """),
        md(r"""
        ## 10. α 变小，还没有回答“为什么”

        新增因子吸收平均收益差，表明这些组合收益含有相关信息。
        风险补偿、错定价、共同特征代理、样本选择和过拟合，都可能产生类似回归改善。
        单凭 α 下降或 $R^2$ 上升，无法在这些机制之间作唯一选择。

        进一步解释机制，需要额外预测与证据：哪些经济状态表现不好、谁承受这些风险、
        限制套利何时更强，以及未参与构造的资产或预设留出期能否得到相应结果。
        经验模型的成功与机制的确认应分别表述。
        """),
        md(r"""
        ## 可选桥梁：贴现因子与“坏状态”

        设 $m_{t+1}$ 为随机贴现因子，期望都条件于时点 $t$ 的信息：

        $$
        E_t[m_{t+1}R^e_{i,t+1}]=0
        \quad\Longrightarrow\quad
        E_t[R^e_{i,t+1}]
        =-\frac{\operatorname{Cov}_t(m_{t+1},R^e_{i,t+1})}{E_t[m_{t+1}]}.
        $$

        边际效用高、资源匮乏的状态往往有较高的 $m$。
        能在这些状态支付较多的资产有保险价值；在这些状态同时受损的资产需要更高预期补偿。
        市场 β、消费 β、ICAPM 状态暴露，是在不同假设下刻画相关风险和对冲需求的方式。
        经验多空因子是否代表这些经济风险，还需专门证据。
        [Cochrane 折现率综述](https://www.johnhcochrane.com/news-op-eds-all/discount-rates)。
        """),
        md(r"""
        ## 11. 支线：股票因子的方法如何迁移到加密资产？

        与“加密三因子、MS 文章”最接近的是下面两篇。它们组成一条连续的研究支线。

        | 文章 | 发表信息 | 模型 |
        |---|---|---|
        | Liu、Tsyvinski、Wu，*Common Risk Factors in Cryptocurrency* | [Journal of Finance，2022](https://doi.org/10.1111/jofi.13119) | 币市市场、规模、动量三因子 |
        | Cong、Karolyi、Tang、Zhao，*Crypto Value, Factor Pricing, and Market Segmentation* | [Management Science，2026-06-05 在线发表](https://doi.org/10.1287/mnsc.2024.05875) | 上述三个方向加加密价值，共四因子 |

        JF 三因子沿用“先发现特征收益差，再用少数收益因子解释这些差异”的研究方法。
        它与股票 FF3 共享市场和规模的思想，第三项使用动量。三因子的数量相同，不代表经济对象和构造相同。

        $$
        R^e_{i,t}=\alpha_i+\beta_{i,M}CMKT_t+\beta_{i,S}CSMB_t
                   +\beta_{i,U}CMOM_t+\varepsilon_{i,t}.
        $$

        | 因子 | 基本构造思想 | 需要区分的对象 |
        |---|---|---|
        | CMKT | 广泛币种组合的市值加权超额收益 | 比特币收益不是整个币市组合收益 |
        | CSMB | 小市值币组合收益减大市值币组合收益 | 币种市值特征与它对 CSMB 的回归暴露不同 |
        | CMOM | 过去赢家组合收益减过去输家组合收益 | 排序使用过去信息，持有期收益随后发生 |

        “币市单因子基准”把相关市场代理限定在加密资产内部，解释时要考虑市场分割。
        标准 CAPM 的理论市场包含全部风险资产，因此不能仅把股票指数换成币市指数就宣称完整均衡理论已成立。
        [作者公开旧稿](https://economics.yale.edu/sites/default/files/2022-10/LiuTsyvinskiWu2019%20COMMON%20RISK%20FACTORS.pdf)
        展示了上述构造与检验思路；该 PDF 是 2019 稿，不能用于冒充 2022 正式版数字。
        """),
        md(r"""
        ## 12. 这条支线怎样做实证，经济问题如何变化？

        先整理当时可观察的币种价格、市值与交易量，按特征分组，计算随后持有期的多空收益；
        再比较仅有 CMKT 与加入 CSMB、CMOM 后的 α。JF 正式摘要报告，三因子解释了其识别出的十项显著策略。
        这是对应样本与检验对象的结果，需要继续检查其他币种、时期以及交易可实施性。

        MS 2026 进一步以“活跃地址数 / 市值”刻画加密价值，加入价值因子，并研究不同功能代币之间的市场分割。
        作者提出价值溢价可能补偿链上活动风险；机制解释应保留这个限定。
        [正式发表记录与摘要](https://pubsonline.informs.org/doi/10.1287/mnsc.2024.05875)。

        从经济概念看，股票 B/M 比较账面权益与市场定价；地址数/市值则比较链上活动与市场定价。
        地址不等于独立用户，更不等于股东现金流。复现时需要理解代理变量到底测量什么，
        并检查活动计量、币种功能、退市和失去流动性的币、做空条件及交易成本。
        这些是将同一实证方法迁移到新资产时要重新处理的问题。

        方法链条可以写成：
        **CAPM 的市场协方差 → FF 的特征排序与多因子检验 → 加密市场/规模/动量 → 链上价值与市场分割。**
        每个阶段仍需区分“拟合共同波动”“解释平均收益”与“确认经济机制”。
        """),
        md(r"""
        ## 加密资料的本地入口与版本说明

        作者通过 [研究主页](https://www.yukunliu.com/research/) 公开了三因子完成品。
        本地材料位于 `data/crypto_raw/` 和 `papers/crypto/`，与股票数据分别保留来源及版本。
        [原始工作簿](../data/crypto_raw/LTW_3factor.xlsx)、[CSV 原值](../data/crypto_raw/LTW_3factor_raw_values.csv)、
        [来源与核验清单](../data/crypto_raw/manifest.json)、[2019 作者工作稿](../papers/crypto/LTW_working_paper_20190415.pdf) 均已在本地。
        工作簿说明写“更新至 2022”，实际数据末行是 2023 年第 14 周，二者分别记录。
        单位在工作簿中未明确标注，下面保留原值，只演示读取与日期核验，不做缩放或定价回归。
        下载了因子收益不等于拥有全部测试资产，不能把因子自身回归到自身来检验定价能力。

        MS 官方页面列出 [附录和数据附件入口](https://pubsonline.informs.org/doi/suppl/10.1287/mnsc.2024.05875)，
        本课尚未取得并核验正式版完整附件，因此先纳入经济思想和研究设计，未声称复现其结果表。
        其 2022 年公开旧稿曾使用五因子版本；本课采用 2026 正式摘要的四因子定义，避免混用版本。
        """),
        code("""
        import hashlib
        import json
        crypto_dir = ROOT / "data/crypto_raw"
        crypto_meta = json.loads((crypto_dir / "manifest.json").read_text(encoding="utf-8"))
        raw_csv = crypto_dir / crypto_meta["derived_csv"]["filename"]
        assert hashlib.sha256(raw_csv.read_bytes()).hexdigest() == crypto_meta["derived_csv"]["sha256"]
        # 用字符串读取，保留原数值表示；确认收益单位后再转换成用于计算的数值列。
        crypto_raw = pd.read_csv(raw_csv, dtype=str)
        assert list(crypto_raw.columns) == ["yyww", "cmkt", "csize", "cmom"]
        assert crypto_raw["yyww"].is_unique and not crypto_raw.isna().any().any()
        week_code = crypto_raw["yyww"].astype(int)
        assert (week_code % 100).between(1, 52).all()
        author_week = (week_code // 100) * 52 + week_code % 100
        assert author_week.diff().dropna().eq(1).all()
        display(crypto_raw.head())
        print(f"作者表：{len(crypto_raw)} 周；首末周标识 {week_code.iloc[0]}—{week_code.iloc[-1]}")
        print("日历：每年固定 52 周，最后一周超过 7 天；不直接解释为 ISO 周。")
        print("单位：尚未由作者文件明确核实，展示原始数值，不作收益率换算。")
        print("作者说明：2020 年中起数据源改为 CoinGecko，扩展数据不等于原发表样本。")
        """),
        md(r"""
        ## 接下来读哪一关？

        - 市场 β：[第 01 关](01_risk_and_capm.ipynb)、[第 03 关](03_capm_test.ipynb)。
        - 特征到因子：[第 04 关](04_build_ff3.ipynb)、[第 07 关](07_build_ff5.ipynb)。
        - 原论文表格：[第 05 关](05_ff3_replication.ipynb)、[第 08 关](08_ff5_replication.ipynb)，
          配合 [论文表格导航](../papers/TABLE_GUIDE.md)。
        - β 与风险价格：[第 06 关](06_fama_macbeth.ipynb)。
        - 留出检验：[第 09 关](09_out_of_sample.ipynb)。

        本地原文：[FF1993](../papers/ff1993_primary_reference.pdf)、
        [FF2015](../papers/ff2015_primary_reference.pdf)。
        无需先读完全部文献才能动手，带着每关问题回到相关表格会更有效。
        """),
        md(r"""
        ## Boss 作答区

        先保留自己的预判，再设计检查；这里不预填答案。

        1. 换一只市场指数作代理，哪些统计量会变化？你将怎样界定结论的适用范围？
        2. 发现某特征排序组合的平均收益很高后，需要哪些步骤才能评价它作为候选因子？
        3. 怎样改进本课三模型实验，使“新增因子是否有效”的解释更清楚？

        **你的回答：**

        （运行后填写，引用本课至少一张表或图。）
        """),
    ]
    from history_self_explaining import assemble
    cells = assemble(cells, md, code)
    for cell in cells:
        assert not any(ord(ch) < 32 and ch not in "\n\r\t" for ch in cell.source)
        if cell.cell_type == "code":
            compile(cell.source, str(TARGET), "exec")
        else:
            assert cell.source.count("$$") % 2 == 0
    nb = nbf.v4.new_notebook(cells=cells, metadata={
        "kernelspec": {"display_name": "Asset Pricing Quest", "language": "python", "name": "asset-pricing-quest"},
        "language_info": {"name": "python", "version": "3.12"},
        "course": {"kind": "prelude", "boss_answers": "blank", "data": "existing local public-data snapshot"},
    })
    nbf.validate(nb)
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    nbf.write(nb, TARGET)
    print(f"Created {TARGET.name}: {len(cells)} cells")

if __name__ == "__main__":
    build()
