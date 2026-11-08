"""把历史导读组装为自解释教程；所有说明与计算写入最终 ipynb。"""
from copy import deepcopy
import re

from history_factor_lessons import factor_foundations, ff5_lessons
from history_statistics_lessons import basics, matrix_keys, regression, diagnostics, fama_macbeth
from history_crypto_lessons import crypto_definitions, historical_definitions


def assemble(original, md, code):
    def take(prefix):
        found = [c for c in original if c.source.startswith(prefix)]
        if len(found) != 1:
            raise ValueError(f"Expected one original cell: {prefix}")
        return deepcopy(found[0])

    def marked(section, cell):
        cell = deepcopy(cell)
        cell.source = f'<a id="{section}"></a>\n\n' + cell.source
        return cell

    cells = [
        md(r"""
        # 从市场 β 到因子 zoo：可以独立阅读的资产定价实验课

        **阅读起点：会 Python 即可，不假设你已经懂金融缩写。**
        本课研究一个问题：为什么不同资产的预期收益不同，研究者怎样用数据检验解释？
        这里的“预期”指事前的平均结果；实际一期收益还包含意外消息。

        每个核心变量都按“定义 → 经济含义 → 选用理由 → 数值例子或代码”展开。
        公司特征、组合收益、回归系数和检验统计量分别解释；正文中的假设数字均标为教学例子。
        历史数据结果来自本地文件，已经保留运行输出。Boss 作答区不预填答案。

        **“自解释”指知识和变量释义完整放在这一本里。** 运行仍使用同一课程目录中的本地数据和公共读取函数，
        不需要先运行其他 Notebook；文末链接是进一步复现论文的入口。
        """),
        md("""
        ## 阅读路线与运行方式

        | 阅读入口 | 要弄懂的问题 |
        |---|---|
        | [收益和基本记号](#returns) | 收益、价格、超额收益、均值、协方差各是什么？ |
        | [市场 β](#capm) | 为什么组合选择会引出协方差定价？ |
        | [规模、B/M 与三因子](#ff3) | 公司特征怎样变成 SMB、HML 收益？ |
        | [真实数据实验](#real-data) | 如何读每一列，并估计 β、重建因子？ |
        | [盈利、投资与五因子](#ff5) | 新变量解决什么问题，为什么选择它们？ |
        | [模型检验](#model-tests) | α、R²、t 值、GRS 分别回答什么？ |
        | [因子 zoo](#zoo) | 找到很多变量后，怎样筛选和验证？ |
        | [加密资产支线](#crypto) | 同一种方法迁移到币市，需要重定义什么？ |

        在 VS Code 打开本项目，选择 <code>Python (Asset Pricing Quest)</code> 内核，
        或解释器 <code>E:/Eth data/asset_pricing_quest/.venv/Scripts/python.exe</code>。
        按 Shift+Enter 逐格执行，或 Restart Kernel and Run All 从头运行。
        股票实例使用 1963-07 至 2013-12 的 606 个月；币市文件使用作者自己的周标识。
        本课不混合月度股票收益与周度币市收益。
        """),
        code("""
        # 先导入工具；这里只准备环境，还没有估计任何经济模型。
        from pathlib import Path
        import sys
        ROOT = next((p for p in [Path.cwd(), *Path.cwd().parents]
                     if (p / "src/course.py").exists()), None)
        if ROOT is None:
            raise RuntimeError("请从 asset_pricing_quest 文件夹或 notebooks 子目录运行。")
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
        print("本地项目：", ROOT)
        """),
    ]
    base = basics(md)
    base[0] = marked("returns", base[0])
    cells += base
    cells += [
        md(r"""
        ### 教学例子：股价涨幅、总收益、超额收益

        假设一股股票月初 100 元，月末 102 元，当月另收到 1 元现金分红，
        同期无风险收益率为 0.2%。分红也是持有者获得的回报，所以不能只用价格涨幅代替总收益。
        下列数字是人为设定，用来核对收益的定义。
        """),
        code("""
        price_start, price_end, dividend = 100.0, 102.0, 1.0
        risk_free_return = 0.002
        price_return = price_end / price_start - 1
        total_return = (price_end + dividend) / price_start - 1
        excess_return = total_return - risk_free_return
        display(pd.DataFrame({
            "经济量": ["价格涨幅", "含分红总收益", "同期无风险收益", "超额收益"],
            "小数值": [price_return, total_return, risk_free_return, excess_return],
            "百分数（%/月）": np.array(
                [price_return, total_return, risk_free_return, excess_return]) * 100
        }).round(4))
        """),
        md("""
        **读数：** 总收益是 3%，比 0.2% 的无风险收益高出 2.8 个百分点，超额收益记为 2.8%。
        后续左侧的股票组合收益也要减去同月无风险收益；已经是多头减空头的因子收益不再重复减一次。
        这个“多头减空头”约定会在六组合例子中具体演示。
        """),
    ]
    cells.append(marked("capm", md(r"""
    ## β 的直觉：这项资产会怎样改变已有组合的风险？

    投资者关心的是全部持仓合在一起的结果。两只股票自身的波动即使一样大，
    如果一只经常在其他持仓亏损时也下跌，另一只在那些时候往往提供回报，它们对组合的作用就不同。
    因此要看资产与已有组合的协方差，而不是只看资产自己的方差。

    在 CAPM 的假设下，投资者共同持有的风险组合与市场组合联系起来。
    衡量资产对该组合的边际风险贡献，就会得到它与市场收益的协方差；
    再除以市场自身的方差，把市场的 β 规范成 1，得到每单位市场风险尺度上的敏感度。
    **为什么选 β？因为它来自组合风险与均衡条件，给出了可以检验的预期收益限制。**
    下一段用矩阵把这个逻辑写完整，随后回归段展示如何从历史数据估计。
    """)))
    keys = matrix_keys(md)
    cells += keys
    cells.append(take("## 2. 市场 β"))
    cells += regression(md)
    cells += [
        md("""
        ### 对照经济理论与估计方法

        CAPM 全称是 Capital Asset Pricing Model，即资本资产定价模型。
        “均衡”表示在价格调整后，投资者合计想持有的资产恰好等于可供持有的资产。
        “被定价”表示某项暴露与预期收益补偿存在模型规定的关系。
        下文估计的是常数 β 的样本内关系；允许 β 和风险溢价随信息变化的条件模型，是更一般的研究对象。
        """),
        take("## 3. β 的统计来源"),
    ]
    history_terms = historical_definitions(md)
    cells.append(history_terms[0])
    cells.append(take("## 4. 1952"))

    foundational = factor_foundations(md, code)
    foundational[0] = marked("ff3", foundational[0])
    cells += foundational
    cells += [
        take("## 1. 四种对象"),
        md(r"""
        ### 一个三因子回归究竟在“算什么”？

        对资产 $i$，三因子回归写成：

        $$
        R^e_{i,t}=\alpha_i+\beta_{i,M}(R_{M,t}-R_{f,t})
                  +\beta_{i,S}SMB_t+\beta_{i,H}HML_t+\varepsilon_{i,t}.
        $$

        $i$ 是资产或组合，$t$ 是月份；三个 $\beta$ 分别是对市场、规模和价值因子的回归斜率，
        都是无单位的敏感度。$\alpha_i$ 是模型未解释的平均超额收益，$\varepsilon_{i,t}$ 是当月残差。
        因子值是当月发生的组合收益，不是公司财报上的数值。
        下例**假设**某资产的三个暴露为 1.2、0.8、0.5，截距为 0.1%/月。
        该月三个因子收益分别为 1%、2%、3%，实际超额收益为 5%。
        """),
        code("""
        # 教学分解：斜率 × 当月因子收益 = 该项的拟合贡献；这不是历史估计结果。
        decomposition = pd.DataFrame({
            "因子": ["市场超额收益", "SMB：小盘减大盘", "HML：高B/M减低B/M"],
            "回归暴露（无单位）": [1.2, 0.8, 0.5],
            "当月因子收益（%）": [1.0, 2.0, 3.0]
        })
        decomposition["拟合贡献（百分点）"] = (
            decomposition["回归暴露（无单位）"] * decomposition["当月因子收益（%）"])
        display(decomposition)
        alpha_example_pct, observed_excess_pct = 0.1, 5.0
        fitted_excess_pct = alpha_example_pct + decomposition["拟合贡献（百分点）"].sum()
        display(pd.Series({
            "截距（%/月）": alpha_example_pct,
            "当月拟合超额收益（%）": fitted_excess_pct,
            "当月实际超额收益（%）": observed_excess_pct,
            "当月残差（百分点）": observed_excess_pct - fitted_excess_pct
        }).round(4).to_frame("教学假设结果"))
        """),
        md("""
        **读数：** SMB 的贡献是 0.8 × 2% = 1.6 个百分点。
        “资产对 SMB 的暴露为 0.8”与“该公司市值小”是不同的陈述：一个是收益共变关系，一个是公司特征。
        这里把当月实现收益代入回归得到拟合值，尚未进行未来收益预测。
        要用模型描述预期收益，需要对因子收益取期望，并检验截距是否符合相应限制。
        """),
        take("## 5. 异象"),
        marked("real-data", md("""
        ## 真实数据：先读懂每个文件和每一列

        下面调用 <code>load_returns</code> 读取已经下载的 French 官方数据。
        这个公共函数核对文件哈希、选择月度收益表、处理官方缺失标记，
        并把原文件的百分数转成小数；例如原文 2.50 读成 0.025。
        它执行数据读取，不替我们决定经济模型。

        | Python 对象／列 | 定义、单位与用途 |
        |---|---|
        | <code>ff3</code> | 三因子和无风险收益表；一行一个月，收益使用小数 |
        | <code>Mkt-RF</code> | 市场组合当月收益减无风险收益；用于测量广泛股票共同波动 |
        | <code>SMB</code>、<code>HML</code> | 刚才定义的规模、价值多空收益，用来代表这两类共同收益方向 |
        | <code>RF</code> | 同月无风险收益率，用于把普通持有收益转成超额收益 |
        | <code>portfolios</code> | 25 个规模×B/M组合的总收益，不是25家公司，也不是价格 |
        | <code>excess</code> | 上述25组合逐月减去 RF 的超额收益，是回归左侧的测试资产 |
        | <code>START</code>、<code>END</code> | 样本起止月份；固定后才能比较不同模型 |

        25 组合使用规模的五档和 B/M 的五档交叉分组；六组合使用两档规模和三档 B/M。
        六组合方便构造因子，25组合提供更细的测试对象，两者不要混为同一张表。
        <code>SMALL LoBM</code> 是“最小规模、最低B/M”组合，不表示某一股票的代码。
        """)),
        code("""
        START, END = "1963-07", "2013-12"
        ff3 = load_returns("ff3", START, END)
        portfolios = load_returns("bm25", START, END)
        assert ff3.index.equals(portfolios.index) and len(ff3) == 606
        excess = portfolios.sub(ff3["RF"], axis=0)
        assert np.isfinite(excess.to_numpy(dtype=float)).all()
        factor_labels = {
            "Mkt-RF": "市场超额收益（%/月）", "SMB": "规模因子（%/月）",
            "HML": "价值因子（%/月）", "RF": "无风险收益（%/月）"}
        display((ff3.head(4) * 100).rename(columns=factor_labels).round(3))
        display(pd.DataFrame({
            "对象": ["因子与无风险收益表", "25个测试组合"],
            "月份数": [len(ff3), len(excess)],
            "列数": [ff3.shape[1], excess.shape[1]],
            "起始月份": [str(ff3.index[0])] * 2,
            "结束月份": [str(ff3.index[-1])] * 2
        }))
        """),
        take("## 实验 A"),
    ]
    beta_cell = take('ASSET = "SMALL LoBM"')
    beta_cell.source = beta_cell.source.replace(
        'x = ff3["Mkt-RF"]', '# x 是市场超额收益，y 是待解释的组合超额收益，均为月度小数。\nx = ff3["Mkt-RF"]'
    ).replace(
        'beta_cov = np.cov', '# ddof=1 表示协方差和方差都用 T-1 作分母；比值不受共同分母影响。\nbeta_cov = np.cov'
    ).replace(
        'fitted = sm.OLS', '# add_constant 添加截距列；OLS 选择截距和斜率以最小化残差平方和。\nfitted = sm.OLS'
    )
    cells.append(beta_cell)
    cells += [
        md("""
        ## 实验 B：用真实六组合同时重建 SMB 和 HML

        上面的教学数字说明了算法。现在把数字换成官方六组合的月度收益。
        下面先把官方列名映射为中文角色，再用明确的组名计算，避免靠列位置猜测经济含义。
        原始组合与公布因子的保留小数位不同，所以允许出现很小的舍入差。
        这里用 bp（基点）报告核对误差：1 bp = 0.01 个百分点 = 小数收益 0.0001。
        """),
        code("""
        six_raw = load_returns("bm6", START, END)
        assert six_raw.shape[1] == 6 and six_raw.index.equals(ff3.index)
        roles = ["小盘低BM", "小盘中BM", "小盘高BM", "大盘低BM", "大盘中BM", "大盘高BM"]
        display(pd.DataFrame({"官方列名": six_raw.columns, "经济角色": roles}))
        six = six_raw.set_axis(roles, axis=1)
        rebuilt = pd.DataFrame({
            "SMB": six[roles[:3]].mean(axis=1) - six[roles[3:]].mean(axis=1),
            "HML": (six["小盘高BM"] + six["大盘高BM"]
                    - six["小盘低BM"] - six["大盘低BM"]) / 2
        })
        error_bp = (rebuilt - ff3[["SMB", "HML"]]) * 10000
        display(pd.DataFrame({
            "手工SMB（%/月）": rebuilt["SMB"].head(4) * 100,
            "官方SMB（%/月）": ff3["SMB"].head(4) * 100,
            "手工HML（%/月）": rebuilt["HML"].head(4) * 100,
            "官方HML（%/月）": ff3["HML"].head(4) * 100
        }).round(5))
        display(error_bp.abs().max().rename(index={
            "SMB": "SMB：规模因子", "HML": "HML：价值因子"
        }).to_frame("全样本最大绝对核对差（bp）").round(5))
        save_table(rebuilt, "PRELUDE_reconstructed_ff3_factors")
        """),
        md("""
        **怎样理解这一核对？** 它检查“多空组合的代数计算是否与官方定义一致”。
        即使重建误差很小，也还没有证明规模、价值得到的收益一定来自风险补偿。
        这需要接下来用其他测试组合检查模型，以及额外的经济机制证据。
        """),
    ]
    five = ff5_lessons(md, code)
    five[0] = marked("ff5", five[0])
    cells += five
    cells.append(take("## 6. 三因子之后"))
    checks = diagnostics(md)
    checks[0] = marked("model-tests", checks[0])
    cells += checks
    cells.append(take("## 实验 C"))
    cells.append(md("""
        **再核对实际输入：** 相同列名也应逐项比对。本地两个文件的 RF、HML 相同，
        Mkt-RF 的最大绝对差为 8 bp，SMB 则因构造来源不同而差异更大。
        下面先显示这一核对，再保留各自官方文件的三模型比较，不悄悄改写数据。
        若要单独识别新增 RMW、CMA 的作用，应把市场、SMB、HML 都固定为五因子文件中的相同三列。
        这里没有追溯 Mkt-RF 差异的生成原因，因此不会将差异一概解释成舍入。
        """))
    cells.append(code("""
        # 五因子定义已经在前文说明；这里才读取对应数据。
        ff5 = load_returns("ff5", START, END)
        assert ff5.index.equals(ff3.index)
        assert np.allclose(ff5["RF"], ff3["RF"])
        shared_column_diff_bp = (ff3[["RF", "Mkt-RF", "SMB", "HML"]]
                                 - ff5[["RF", "Mkt-RF", "SMB", "HML"]]).abs() * 10000
        display(pd.DataFrame({
            "两文件平均绝对差（bp）": shared_column_diff_bp.mean(),
            "两文件最大绝对差（bp）": shared_column_diff_bp.max()
        }).round(4))
        names3 = ["Mkt-RF", "SMB", "HML"]
        models = {
            "CAPM": ff3[["Mkt-RF"]],
            "FF3 classic": ff3[names3],
            "FF5": ff5[[*names3, "RMW", "CMA"]]
        }
        # model_summary：对每个资产做含截距 OLS，再汇总α、R²，并计算经典GRS。
        # 它不改变样本、不重新扣RF；公式和各项解释见上面的诊断说明。
        comparison = model_summary(excess, models)
        labels = {
            "mean_abs_alpha_pct_month": "平均绝对α（%/月）",
            "rms_alpha_pct_month": "α均方根（%/月）",
            "mean_r2": "平均R²",
            "grs_stat": "经典GRS统计量",
            "grs_pvalue": "GRS的p值",
            "T": "月份数T", "N": "资产数N", "K": "因子数K"
        }
        display(comparison.rename(columns=labels).style.format(precision=4, formatter={
            "GRS的p值": "{:.3g}", "月份数T": "{:.0f}",
            "资产数N": "{:.0f}", "因子数K": "{:.0f}"
        }))
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
        fig.suptitle("1963-07—2013-12；25 个规模 × B/M 组合")
        fig.tight_layout()
        plt.show()
        """))
    cells.append(take("c, t, v ="))
    cells += fama_macbeth(md)
    cells += [
        marked("zoo", take("## 8. 2011")),
        md("""
        ### 读懂 zoo 研究中的评价用语

        “异象”是相对于某个基准模型尚未解释的收益规律；“因子 zoo”描述候选因子很多的局面。
        “多重检验”指同时或反复检验许多候选变量，偶然显著结果更容易出现。
        “样本外”指用没有参与选择模型的数据评价它；按时间划分训练、验证、测试分别用于估计、
        选择设定、最后评价。它们回答的研究问题和样本内拟合有所不同。
        此处选择这些检查，是为了判断新增变量是否提供可重复的信息。
        """),
        take("## 9. 真正"),
        take("## 10. α"),
        history_terms[1],
    ]
    crypto = crypto_definitions(md)
    crypto[0] = marked("crypto", crypto[0])
    cells += crypto
    cells += [
        take("## 11. 支线"),
        take("## 12. 这条"),
        take("## 加密资料"),
        take("import hashlib"),
        md("""
        ## 变量查找与继续复现

        | 你在表格或代码中看到的量 | 回到哪一部分 |
        |---|---|
        | R、RF、超额收益、均值、方差、协方差 | [收益和基本记号](#returns) |
        | β、α、残差、OLS、风险厌恶、组合权重 | [市场 β](#capm) |
        | BE、ME、B/M、P/B、S/B、L/N/H、SMB、HML | [三因子基础与数值例子](#ff3) |
        | OP、Inv、RMW、CMA、GP/A、Mom、q 模型 | [盈利、投资与动量](#ff5) |
        | T/N/K、R²、标准误、t 值、p 值、HAC、GRS、λ | [模型诊断和两步检验](#model-tests) |
        | 币市市值、成交量、动量、CMKT、CSMB、CMOM、活跃地址/市值 | [加密变量定义](#crypto) |

        原文的表号与样本口径可在 [论文表格导航](../papers/TABLE_GUIDE.md) 查找。
        本课已经解释读懂这些变量所需的概念；分关 Notebook 用于进一步展开实证。
        """),
        take("## 接下来"),
        take("## Boss"),
    ]
    # 原导读的章节序号不再适合新顺序；保留标题文字和稳定的导航锚点。
    for cell in cells:
        if cell.cell_type == "markdown":
            cell.source = re.sub(r"(?m)^(## )\d+\.\s*", r"\1", cell.source)
    return cells
