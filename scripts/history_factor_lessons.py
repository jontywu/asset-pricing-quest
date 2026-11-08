"""可插入前导课的中文因子基础单元；md/code 由主生成器注入。"""


def factor_foundations(md, code):
    """8 个单元：从会计与市值变量走到 FF3 的六组合及做差。"""
    return [
        md(r"""
        ## 先认清原材料：BE 和 ME 到底是什么？

        一个公司的会计报表和股票市场，会给出两种不同的权益价值。

        | 符号 | 定义与单位 | 经济含义 |
        |---|---|---|
        | $BE$：Book Equity，账面普通股权益 | 入门时可理解为账面资产减负债后，归普通股股东的部分；金额 | 会计记录中的净资产，不是未来现金流的估值 |
        | $P$：Price，股价 | 每股价格；金额/股 | 买一股在市场上要付多少钱 |
        | $Q$：Shares Outstanding，发行在外股数 | 股数 | 普通股股权被分成多少股；用 Q 避免与测试资产数 N 混淆 |
        | $ME$：Market Equity，股票市值 | $ME=P\times Q$；金额 | 市场给全部普通股权益的价格；课程里 size 就指它 |

        **为什么同时需要 BE 和 ME？** BE 提供一个会计尺度，ME 提供市场愿意付的价格。比较两者能区分“相对于账面权益贵或便宜”，单看股价无法做到：拆股会降低每股价格，却不必改变公司总市值。

        **正式复现的 BE 比入门定义细。** French 的历史规则从股东权益出发，扣除优先股，并按数据版本处理递延税与投资税抵免；优先股有赎回价值、清算价值、面值的取值顺序，股东权益缺失也有替代字段。当前文件对 1993 年及以后结束的财年不再加回上述递延税项目。故不要直接把任何数据库的“净资产”列当作完全一致的 BE。本课先用已按研究规则加工的公开组合，手算例子只讲经济直觉。

        来源：[French 变量定义](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/Data_Library/variable_definitions.html)；
        [数据修订说明：2016 年 8 月的 BE 变化](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html)。
        """),
        md(r"""
        ### B/M：把“价格”放到一个可比较的尺度上

        $B/M$ 是 Book-to-Market，通常也写 $BE/ME$；$P/B$ 是 Price-to-Book，中文常叫市净率。

        $$
        B/M=\frac{BE}{ME},\qquad P/B=\frac{ME}{BE}=\frac{1}{B/M}.
        $$

        这里 $P/B$ 中的 $P$ 习惯上表示市场价格尺度；使用公司总量时分子是总市值 ME。用每股股价除以每股账面权益也会得到相同结果，前提是口径对应。

        - **高 B/M：** 每付 1 元市场价，买到的账面权益较多；也就是低 P/B，通常称 value（价值组）。
        - **低 B/M：** 每付 1 元市场价，买到的账面权益较少；也就是高 P/B，通常称 growth（成长组）。
        - **为什么选它？** 它把市场价格与会计尺度连接起来，是检验平均收益差异的一项可观测特征。成长预期、经营困难、风险补偿或定价偏差都可能影响该比率，命名本身不能区分这些解释。

        两个金额必须用**同一种货币、同一金额单位**；正式排序还必须遵守规定的财年和市场日期。上面的倒数关系针对正 BE，FF 的相关组合通常要求 BE 为正。**高 B/M 不是高股价，也不保证股票被低估；“growth”标签也不是对未来增长的承诺。**

        下一格用两家虚构公司把这些区别算清楚；它不使用实际股票，不构成收益预测。
        """),
        code(r"""
        # 模拟教学数据：金额均为人民币，股数以“亿股”为单位。
        import numpy as np
        import pandas as pd
        from IPython.display import Markdown, display

        demo_companies = pd.DataFrame({
            "公司（模拟）": ["甲公司", "乙公司"],
            "股价（元/股）": [10.0, 50.0],
            "股数（亿股）": [1.0, 1.0],
            "BE：账面权益（亿元）": [8.0, 10.0],
        }).set_index("公司（模拟）")
        demo_companies["ME：市值（亿元）"] = (
            demo_companies["股价（元/股）"] * demo_companies["股数（亿股）"]
        )
        demo_companies["B/M（倍）"] = (
            demo_companies["BE：账面权益（亿元）"] / demo_companies["ME：市值（亿元）"]
        )
        demo_companies["P/B（倍）"] = 1.0 / demo_companies["B/M（倍）"]
        display(demo_companies.round(3))
        assert np.allclose(
            demo_companies["B/M（倍）"] * demo_companies["P/B（倍）"], 1.0
        )
        display(Markdown(
            "甲的 B/M 为 **0.80**，乙为 **0.20**；每付 1 元市值，"
            "分别对应 0.80 元和 0.20 元账面权益。甲的股价更低，B/M 却更高。"
            "这说明比率在比较价格相对于账面尺度的位置，并没有告诉我们哪家公司一定值得买。"
        ))
        """),
        md(r"""
        ### 为什么再加入 size？如何读懂 S/L、B/H？

        **Size 指股票市值 ME，不是每股股价、营业收入或员工数。** 历史研究发现，小市值与大市值股票的平均收益存在 CAPM 难以完全吸收的差异，因而把 size 作为待检验特征；它也可能联系融资条件、流动性和经营风险。选择这个特征不等于已经证明“规模小导致收益高”。FF1992 将 size 和 B/M 放在横截面中考察，FF1993 进一步把它们变成可以逐月观察的组合收益因子。

        为避免把“小公司效应”和“高 B/M 效应”混在一起，先按两个维度**独立分类，再取交集**：

        | 市值类别 | 低 B/M：L（Low） | 中 B/M：N（Neutral） | 高 B/M：H（High） |
        |---|---|---|---|
        | 小市值：S（Small） | S/L：小盘、低 B/M | S/N：小盘、中 B/M | S/H：小盘、高 B/M |
        | 大市值：B（Big） | B/L：大盘、低 B/M | B/N：大盘、中 B/M | B/H：大盘、高 B/M |

        每一格包含一篮子股票；后文 $R_{SL,t}$ 表示 S/L 这一篮子在月份 $t$ 的收益率。标签里的 B 是 Big；比率 B/M 中的 B 是 Book，两者含义不同。L/H 说的是 B/M 高低，不是当月收益高低。

        来源：[Fama–French 1992，Journal of Finance](https://doi.org/10.1111/j.1540-6261.1992.tb04398.x)；
        [Fama–French 1993 原文](../papers/ff1993_primary_reference.pdf)。
        """),
        md(r"""
        ### 真正实操：何时分组，依据什么，怎样加权？

        按 French 美国 2×3 组合规则，用年份 $y$ 表示一次年度形成期：

        1. **找信息：** 用上一日历年 $y-1$ 结束财年的 BE，除以 $y-1$ 年 12 月底 ME，得到用于本次排序的 B/M；size 用 $y$ 年 6 月底 ME。会计滞后是给报表公布留时间，个股复现仍须核对当时实际可获得的信息。
        2. **设断点：** 用纽约证券交易所 NYSE 股票的 6 月市值中位数分 S/B，用 NYSE 的 B/M 第 30、70 百分位数分 L/N/H，再将适用股票放入交叉组合。NYSE 是断点基准，组合可包含符合条件的 NYSE、AMEX、NASDAQ 股票。这样能减少数量众多的微盘股主导分组边界的问题；不是对每家交易所各分一遍。
        3. **观测收益：** 从 $y$ 年 7 月到 $y+1$ 年 6 月使用这次分组，下一年重新分类。六格内部用市值加权收益，不是简单平均股票收益；不能把年度分组误写成所有权重一年不变。
        4. **合成因子：** 对六格已经算好的收益，按下一节公式等权平均、做差。**组内市值加权**与**组间等权**发生在两个层次。

        市值加权的直觉公式是 $R_{p,t}=\sum_{i\in p}w_{i,t-1}R_{i,t}$：$p$ 是组合，$i$ 是股票，$w$ 是收益实现前已知的市值权重，权重加总为 1，$R$ 是含分红的股票收益。不能用本月月底才知道的市值给本月收益加权。

        来源：[French 六组合形成说明](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/Data_Library/six_portfolios.html)。
        """),
        md(r"""
        ### SMB：Small Minus Big，把“小盘相对大盘”的月收益拿出来

        **定义：** 经典三因子模型的 SMB，先分别平均三种 B/M 类别的小盘收益和大盘收益，再用小盘减大盘。

        $$
        SMB_t^{(3)}=
        \frac{R_{SL,t}+R_{SN,t}+R_{SH,t}}{3}
        -\frac{R_{BL,t}+R_{BN,t}+R_{BH,t}}{3}.
        $$

        **为什么这样选、这样做差？** 我们想衡量 size 对应的收益维度。两边都包含低、中、高 B/M，能减少“只是小盘组恰好更多价值股”的混淆；把共同上涨的部分相减，可更直接观察两类股票相对表现。这是按特征进行平衡，并不保证 SMB 对市场 β、行业、价值或所有其他风险完全中性。

        **方向与单位：** SMB 当月为正，表示此定义下小盘一侧跑赢大盘一侧；为负则相反。SMB 是每个月一个数的**收益序列**，不是某公司的市值，也不是小盘股票数量。它可理解为做多小盘篮子、做空大盘篮子的收益差；实际交易还涉及融资、卖空与交易成本，公开研究因子不是扣完所有实施成本的账户回报。

        来源：[French 三因子定义](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library/f-f_factors.html)。
        """),
        md(r"""
        ### HML：High Minus Low，High/Low 指 B/M

        **定义：** 先把小盘和大盘中的高 B/M 组合平均，再减去两种规模中的低 B/M 平均收益。

        $$
        HML_t=
        \frac{R_{SH,t}+R_{BH,t}}{2}
        -\frac{R_{SL,t}+R_{BL,t}}{2}.
        $$

        **为什么这样选、这样做差？** 高、低 B/M 的平均收益差是价值效应的经验切入点；两边都放入小盘和大盘，减少规模分布差异造成的混淆。N 组不进入 HML，因为此因子专门比较两端。这样的双重排序不保证 HML 与 SMB 统计上不相关，更不保证高 B/M 公司只有一种风险。

        HML 当月为正，表示高 B/M 一侧跑赢低 B/M 一侧，不能解释成“市场发现了所有价值股的真实价值”。公司特征 B/M、因子收益 HML、资产对 HML 的回归暴露 $\beta_{HML}$ 是三个不同对象：**用特征分组，得到因子收益，再估计某资产对这条收益序列的敏感度。**

        下面六个收益是刻意设置的模拟数，专门用于看清等权和做差；没有任何真实样本结论。

        来源：[French HML 定义](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library/f-f_factors.html)。
        """),
        code(r"""
        # 六组合模拟月收益。计算使用小数；显示时乘 100 变成百分比数值。
        import numpy as np
        import pandas as pd
        from IPython.display import Markdown, display

        six_demo = pd.Series(
            {"SL": .01, "SN": .02, "SH": .03, "BL": .005, "BN": .01, "BH": .02},
            name="月收益（小数）",
        )
        six_labels = {
            "SL": "小盘/低B/M", "SN": "小盘/中B/M", "SH": "小盘/高B/M",
            "BL": "大盘/低B/M", "BN": "大盘/中B/M", "BH": "大盘/高B/M",
        }
        display(pd.DataFrame({
            "组合（模拟）": six_labels,
            "月收益（%）": six_demo * 100,
        }))
        small_mean = six_demo[["SL", "SN", "SH"]].mean()
        big_mean = six_demo[["BL", "BN", "BH"]].mean()
        high_mean = six_demo[["SH", "BH"]].mean()
        low_mean = six_demo[["SL", "BL"]].mean()
        demo_smb, demo_hml = small_mean - big_mean, high_mean - low_mean
        display(pd.DataFrame({
            "构造": ["SMB：小盘 − 大盘", "HML：高B/M − 低B/M"],
            "多头一侧月收益（%）": [100 * small_mean, 100 * high_mean],
            "空头一侧月收益（%）": [100 * big_mean, 100 * low_mean],
            "收益差（百分点/月）": [100 * demo_smb, 100 * demo_hml],
        }).round(4))
        assert np.isclose(demo_smb, 1 / 120)
        assert np.isclose(demo_hml, .0175)
        display(Markdown(
            f"小盘平均收益为 {100 * small_mean:.3f}%，大盘为 {100 * big_mean:.3f}%，"
            f"相减得到 **SMB = {100 * demo_smb:.3f} 个百分点/月**。"
            f"高 B/M 平均收益为 {100 * high_mean:.2f}%，低 B/M 为 {100 * low_mean:.2f}%，"
            f"因此 **HML = {100 * demo_hml:.2f} 个百分点/月**。\n\n"
            "数据文件通常将因子收益写成百分比，例如 HML=1.75；"
            "回归代码中转换成小数是 0.0175。两边收益率相减严格说是百分点差，"
            "不是“相对增长了 1.75%”；更不是把这六个百分比相乘。"
        ))
        """),
    ]


def ff5_lessons(md, code):
    """6 个单元：盈利、投资、FF5 的 SMB、估值逻辑和动量。"""
    return [
        md(r"""
        ## 盈利 OP：公司怎样赚钱，如何量化？

        OP 是 Operating Profitability（经营盈利能力），是**公司会计特征**。当前 French 口径为：

        $$
        OP=
        \frac{\text{营业收入}-\text{销售成本}-\text{销售、一般及管理费用}-\text{利息费用}}
        {BE+\text{少数股东权益}}.
        $$

        分子从卖产品和服务的收入，依次扣去生产或采购成本、销管开支和借款利息，得到这一研究定义下的利润尺度；它不等于净利润，也不是毛利率。少数股东权益指合并报表中归子公司其他股东的权益。分母将利润按权益规模标准化，使大公司利润金额大这件事不直接决定排名；比率无量纲，0.20 可写为 20%。

        **为什么选它？** 只看价格相对账面权益，尚未直接区分公司从这些权益中创造利润的能力。盈利特征为检验收益差异提供另一条信息。高 OP 是“给定权益尺度，报告的经营利润高”，并不自动表示股价便宜或下一期股票收益高。

        **复现必须区分版本：** FF2015 论文使用 BE 作分母；French 在 2018 年 8 月将少数股东权益加入分母。当前公开文件应按后者理解。官网某些旧的六组合详情页仍保留“除以 BE”的文字，此处依据已更新的变量定义总页和修订说明，而不把两种口径强行说成一致。

        来源：[French 当前变量定义](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/Data_Library/variable_definitions.html)；
        [2018 年口径修订](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html)；
        [FF2015 原文](../papers/ff2015_primary_reference.pdf)。
        """),
        md(r"""
        ### Inv：这里的“投资”指公司资产扩张，不是投资者买股票

        Inv 是 Investment（投资强度）。以 $y$ 年 6 月的分组为例，$AT$ 表示 Total Assets（资产负债表中的总资产金额），定义为：

        $$
        Inv_y=\frac{AT_{y-1}-AT_{y-2}}{AT_{y-2}}.
        $$

        $AT_{y-1}$ 是在上一日历年结束的财年的总资产；$AT_{y-2}$ 是再前一个财年的总资产。例如总资产从 100 亿元增至 120 亿元，Inv=0.20，即增长 20%。它是资产存量的增长率，**不是资本开支金额，不是股票成交量，也不是投资者仓位**；并购、营运资本等变化都可能影响它。

        **为什么选它？** 投资决定公司把多少资源投入未来经营。在投资与估值框架下，预期利润与资本成本共同影响扩张选择，因而资产增长可能包含有关预期股票收益的信息。经验上要检验这种联系能否超出市场、规模、价值和盈利信息，不能只凭“扩张很快”判断回报好坏。

        French 每年 6 月按 size 和 Inv 独立排序：NYSE 市值中位数分 S/B，Inv 的 NYSE 30/70 分位数分低、中、高。Conservative（C，保守投资）只指资产增长较低；Aggressive（A，激进投资）只指资产增长较高，并非对管理层行为或会计质量的评价。

        来源：[French 投资六组合说明](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/Data_Library/six_portfolios_me_inv.html)。
        """),
        md(r"""
        ### RMW 与 CMA：把两个公司特征变成可回归的收益序列

        构造方式沿用 size×另一特征的 2×3 排序，每格内部市值加权，两个规模组之间等权。
        对 OP，使用 NYSE 市值中位数及 OP 的 30/70 百分位数形成大小、弱中强六组；投资组按上一节规则形成。

        **RMW = Robust Minus Weak（强盈利减弱盈利）。** R 表示高 OP，W 表示低 OP；S/B 仍表示小/大市值。$R_{SR,t}$ 是“小盘且高 OP”组合的月收益，$R_{BR,t}$ 是“大盘且高 OP”，SW/BW 同理。

        $$
        RMW_t=\frac{R_{SR,t}+R_{BR,t}}{2}
        -\frac{R_{SW,t}+R_{BW,t}}{2}.
        $$

        **CMA = Conservative Minus Aggressive（低投资减高投资）。** C/A 指上节定义的低/高资产增长率，SC/BC 是小盘/大盘低投资组合，SA/BA 是小盘/大盘高投资组合。

        $$
        CMA_t=\frac{R_{SC,t}+R_{BC,t}}{2}
        -\frac{R_{SA,t}+R_{BA,t}}{2}.
        $$

        选择这些方向，是为了表达文献关注的“强盈利相对弱盈利”“低投资相对高投资”的收益差。RMW 为正只说明强盈利一侧当月跑赢；CMA 为正只说明低投资一侧当月跑赢。**OP、Inv 是形成组合时的特征，RMW、CMA 是组合形成后实现的收益，不要把会计增长率直接当作因子收益。** 加入模型后再问：它们能否吸收测试资产原来剩下的平均超额收益？

        来源：[French 五因子构造公式](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library/f-f_5_factors_2x3.html)。
        """),
        md(r"""
        ### 一个容易漏掉的实现差别：FF5 的 SMB 也变了

        三因子的 SMB 只来自 size×B/M 六组合。五因子另算 size×OP 六组合、size×Inv 六组合中的“小减大”，再把三条规模收益差平均：

        $$
        SMB^{(5)}_t=\frac{SMB_{B/M,t}+SMB_{OP,t}+SMB_{Inv,t}}{3}.
        $$

        每条 $SMB_{X,t}$ 都是：特征 $X$ 的低、中、高三类小盘平均收益，减去对应三类大盘平均收益。因此五因子 SMB 是九个小盘组合对九个大盘组合的平均差；它扩大了规模因子的构造来源，仍不保证对其他因子完全中性。

        **为什么这影响模型比较？** “官方 FF3 对官方 FF5”的比较，除了新增 RMW、CMA，还改变了 SMB 序列。如果想单独问“新增两个因子的作用”，应在同一份五因子数据中先只取市场、SMB、HML，再与全部五列比较；同时保留经典 FF3 作为独立基准。后面的实证格会明确是哪一种比较。

        来源：[French 五因子 SMB 的三组均值](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library/f-f_5_factors_2x3.html)。
        """),
        md(r"""
        ### 为什么盈利、投资可能与预期收益有关？先带上条件

        股价把未来支付折现到今天。FF2015 将估值关系与会计关系连接后，得到的比较逻辑是：**给定 B/M 与投资，较高的预期盈利对应较高的预期收益；给定 B/M 与盈利，较高的预期投资对应较低的预期收益。** 这里预期收益是与当前价格一致的折现率概念；用于排序的历史 OP、Inv 只是预期量的经验代理。

        “给定”不能删掉。盈利很好也可能早已对应很高的股价；扩张也可能伴随更高的未来盈利。条件估值关系不等于“盈利高因而下一月必涨”，也没有单独识别风险补偿还是市场错误定价。这个条件逻辑才是选择盈利与投资变量的经济动机之一。[FF2015 原文](../papers/ff2015_primary_reference.pdf)

        **同样叫盈利，分子、分母和频率仍可能不同：**

        | 指标 | 具体量度 | 为何不能互换 |
        |---|---|---|
        | FF 的 OP | 上述年度经营利润尺度 /（BE + 少数股东权益）；原论文分母为 BE | 包含销管费用、利息扣除，按权益规模标准化 |
        | Novy-Marx 的 GP/A | 毛利润 Gross Profits = 收入 − 销售成本；除以总资产 Assets | 毛利润还未扣上述销管费用、利息；衡量每单位资产的毛利创造能力 |
        | q-model 的 ROE：Return on Equity，权益回报率 | 季度非常项目前利润（income before extraordinary items）/ 上季度账面权益 | 更接近季度权益盈利信息；频率及利润口径不同 |

        q-model 的 I/A（Investment-to-Assets）也用年度总资产变化除以上年总资产，与 FF Inv 的经济概念相近，但 q 因子采用 size×I/A×ROE 的三重排序，不能把它的因子列直接改名为 CMA/RMW。它从企业投资决策出发选择投资与盈利；FF5 则使用自己的估值动机、变量与组合方案，二者可以比较，不能预设等价。

        来源：[Novy-Marx 2013，Journal of Financial Economics](https://doi.org/10.1016/j.jfineco.2013.01.003)；
        [Hou–Xue–Zhang 2015，Review of Financial Studies](https://doi.org/10.1093/rfs/hhu068)；
        [q 因子作者技术定义](https://global-q.org/uploads/1/2/2/6/122679606/factorstd_2025feb.pdf)。
        """),
        md(r"""
        ### Mom / WML：过去涨得多，是否还能在随后跑赢？

        动量 Momentum 用**过去股票收益**作排序特征，和会计变量不同。French 月度 Mom 的形成信号是 prior (2–12) return：对持有月份 $t$，累计 $t-12$ 到 $t-2$ 这 11 个月的收益，跳过最近的 $t-1$ 月：

        $$
        z^{mom}_{i,t}=\prod_{j=2}^{12}(1+R_{i,t-j})-1.
        $$

        $z^{mom}_{i,t}$ 是股票 $i$ 在形成时可观察的历史累计收益信号，不是持有月收益；
        $j$ 是回溯月数，$\prod$ 表示把各月的 $1+R$ 连乘，$R_{i,t-j}$ 是对应过去月份的含分红股票收益。
        月末按 size 和这个信号形成六组合，用过去赢家（Winners，W）的后续收益减过去输家（Losers，L）的后续收益：

        $$
        Mom_t=\frac{R_{SW,t}+R_{BW,t}}{2}
        -\frac{R_{SL,t}+R_{BL,t}}{2}.
        $$

        这一格 W 是 Winner，上一节 RMW 的 W 是 Weak，符号要跟着所排序的特征读。WML 是 Winner Minus Loser 的常见名字，但不同数据源的持有期、断点、加权可能不同，不能只看列名就认定是同一序列。

        **为什么选过去收益？** 文献发现中期赢家与输家的后续平均收益存在可研究的差异。跳过最近一个月有助于减少短期反转等现象的混入；这是一项明示的设计选择，不是证明动量永远有效。它补充的是“价格历史”维度，不是会计利润或市场 β。

        French 这条序列每月形成组合，使用 NYSE 市值中位数及历史收益 30/70 断点。这里的“2–12”是股票**月**收益的约定；迁移到加密资产时，连续交易、样本存续、流动性和形成/持有窗口都需重新定义，不能把同样数字直接解释为 2–12 天。

        来源：[French 月度 Mom 定义](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/Data_Library/det_mom_factor.html)；
        [Jegadeesh–Titman 1993，Journal of Finance](https://doi.org/10.1111/j.1540-6261.1993.tb04702.x)。
        """),
    ]
