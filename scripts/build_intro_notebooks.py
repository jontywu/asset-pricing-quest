"""用 nbformat 生成入口与第 0–5 关。执行结果由 execute_course.py 填充。"""
from pathlib import Path
import textwrap
import nbformat as nbf

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'notebooks'
OUT.mkdir(exist_ok=True)


def md(text):
    source = textwrap.dedent(text).strip().replace('：**', '：** ')
    source = source.replace(r'\[', '\n\n$$\n').replace(r'\]', '\n$$\n\n')
    return nbf.v4.new_markdown_cell(source)


def code(text):
    return nbf.v4.new_code_cell(textwrap.dedent(text).strip())


SETUP = '''
from pathlib import Path
import sys
ROOT = next(p for p in [Path.cwd(), *Path.cwd().parents] if (p / 'src/course.py').exists())
sys.path.insert(0, str(ROOT / 'src'))
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import display, Markdown
from course import (load_raw, load_returns, raw_path, catalog, manifest, style,
                    build_ff3, build_ff5, heatmap25, save_table, paper_note)
from analysis import fit_models, grs_test, model_summary
style()
print('项目目录：', ROOT)
'''


def write(name, cells):
    nb = nbf.v4.new_notebook(cells=cells)
    nb.metadata.update(kernelspec={'name': 'asset-pricing-quest', 'display_name': 'Python (Asset Pricing Quest)', 'language': 'python'},
                       language_info={'name': 'python'}, asset_pricing_course={'status': 'guided_reference', 'boss_answers': False})
    nbf.validate(nb)
    nbf.write(nb, OUT / name)


def boss(question):
    return md('## Boss 作答区\n\n' + question + '\n\n**我的回答：**\n\n（由你填写；本课程未预填答案。）')


write('START_HERE.ipynb', [
    md('''
    # 资产定价研究者：本地 Notebook 课程
    目标是理解**作者提出了什么问题，如何把经济概念变成可检验对象，以及结果支持什么**。
    10 关均可独立从头运行，公开数据已在本地；预执行结果保留在单元格里。
    每关采用「经济动机 → 数据与代码 → 表格或图 → 解释与边界 → 自己作答」结构。

    ## 在 VS Code 中开始
    1. 用 VS Code 打开整个 `asset_pricing_quest` 文件夹，安装 Microsoft Python 与 Jupyter 扩展。
    2. 打开本 Notebook，右上角选择 `Python (Asset Pricing Quest)`，或本项目 `.venv/Scripts/python.exe`。
    3. 用 `Shift+Enter` 逐格执行；先读文字、预测结果，再运行。`Restart Kernel and Run All` 可检查可复现性。
    4. 输出已经保存；重新运行会更新结果表，但不会自动下载新版本的数据。

    ## 选择关卡
    建议先读 [自解释导读：变量定义、经济含义与实证](PRELUDE_beta_to_factor_zoo.ipynb)。从收益、B/M 和 SMB 的含义开始，用数值例子理解因子，再连接市场 β 到 factor zoo 的历史；无需先有金融术语基础。

    | 关卡 | 研究问题 | Notebook |
    |---|---|---|
    | 00 | 什么才算可比较的数据？ | [数据实验台](00_data_lab.ipynb) |
    | 01 | 为什么风险补偿关注共同风险？ | [风险、分散化与 CAPM](01_risk_and_capm.ipynb) |
    | 02 | 不同类型股票的平均收益是否不同？ | [排序组合与平均收益](02_portfolio_sorts.ipynb) |
    | 03 | 市场风险能解释这些差异吗？ | [CAPM 检验](03_capm_test.ipynb) |
    | 04 | 特征怎样变成因子收益？ | [构造三因子](04_build_ff3.ipynb) |
    | 05 | 三因子改善了什么？ | [FF1993 股票部分](05_ff3_replication.ipynb) |
    | 06 | 风险暴露和风险价格有什么联系？ | [Fama–MacBeth 方法练习](06_fama_macbeth.ipynb) |
    | 07 | 盈利、投资为什么进入模型？ | [构造五因子](07_build_ff5.ipynb) |
    | 08 | 五因子在哪些资产上表现更好？ | [FF2015 核心检验](08_ff5_replication.ipynb) |
    | 09 | 换时期和资产，结论如何变化？ | [样本后检验](09_out_of_sample.ipynb) |

    ## 你现在拥有的数据层级
    French 官方公开的因子、六组合、25/32 测试组合和行业收益，是已经完成清洗与排序的研究数据。
    它们足够运行本课程的全部主线。第 04 关另用**明确标注的教学假设数据**展示个股如何组成六组合。
    [公开替代与 GitHub 参考](../references/OPEN_DATA_ALTERNATIVES.md)补充了构造代码的来源。
    不需要为完成本课程申请 WRDS。原始个股级重建与原论文逐格一致，是另一层复现目标。

    ## 如何对照论文
    两篇核心论文 PDF 保存在 `papers/`；[表格导航](../papers/TABLE_GUIDE.md)标明原表号、页码与适用口径。
    Notebook 中展示的是用冻结数据重新计算的表格；少量原文核对值明确标为原文数值。
    FF1993 只复现股票核心部分；第 06 关是方法练习；第 09 关是扩展实验。
    当前 French 历史数据经过修订，不能把数值差异一概归为编程错误。
    ''') ,
    code(SETUP),
    md('## 本地数据清单\n下表来自本地文件实际读取，不依赖在线连接。'),
    code("display(catalog()[['数据','月数','列数','起点','终点']])"),
    md('''
    ## 推荐学习节奏
    一次完成一关。给每张结果表写三句话：**我看到什么；在模型假设下意味着什么；还不能据此断言什么。**
    Boss 作答区留空，你可以写完后带着 Notebook 输出来讨论。每关的通关依据是解释能被数据支持。

    数据、公共函数、回归实现分别放在 `data/`、`src/course.py`、`src/analysis.py`。
    详细中文注释在代码旁；`results/` 保存运行生成的表格。`level00/` 保留上一版原始练习。
    ''')
])

write('00_data_lab.ipynb', [
    md('''
    # 第 0 关：建立可信的数据实验台
    **本关目标：**让两张表在时间、单位和研究对象上具有明确含义。完成后获得可重复使用的样本。
    本关对应 FF1993 的数据部分，为后续 Table 2、4、6 的股票结果准备输入，本身不是原论文的一张结果表。

    **经济动机：**一行观测必须对应同一个月。收益率、公司数量和估值特征是不同经济量；数据整理决定了回归究竟回答哪个问题。
    数据已下载；下面的单元格只读取冻结的本地快照。
    '''), code(SETUP),
    code("display(Markdown(paper_note('ff1993')))"),
    md('## 1. 查看原文件与来源\n先看文件说明再读表。数据来源、时间、校验值都可以追溯。'),
    code("for key in ['ff3','bm25']:\n    record = manifest()['datasets'][key]\n    print(key, record['source_header'], record['downloaded_at_utc'])\n    print('\\n'.join(raw_path(key).read_text(encoding='utf-8-sig').splitlines()[:9]))\n    print()"),
    md('## 2. 读取课题使用的两张月度表\n`load_raw` 只定位表格并读字符串；点开 `src/course.py` 可看具体定位条件。此时不改变任何经济量。'),
    code("ff_raw = load_raw('ff3')\np_raw = load_raw('bm25')\ndisplay(pd.DataFrame({'rows':[len(ff_raw),len(p_raw)],'columns':[ff_raw.shape[1],p_raw.shape[1]],'first':[ff_raw.index[0],p_raw.index[0]],'last':[ff_raw.index[-1],p_raw.index[-1]]},index=['factors','portfolios']))\ndisplay(ff_raw.head(3))\ndisplay(p_raw.iloc[:3,:5])"),
    md('''
    ## 3. 将数据整理为研究样本
    下面把原始文本转成数字，并明确处理文件中列出的缺失标记。计算阶段统一使用小数收益，展示阶段再转成月度百分数。
    日期使用月度 `PeriodIndex`，避免把“某月”误当成具体交易日。我们先选择论文的 342 个月。
    '''),
    code('''
    START, END = '1963-07', '1991-12'
    def prepare(raw):
        frame = raw.apply(pd.to_numeric, errors='raise')
        frame = frame.replace([-99.99, -999], np.nan).astype(float) / 100
        frame.index = pd.PeriodIndex(pd.to_datetime(raw.index, format='%Y%m'), freq='M', name='month')
        return frame.loc[START:END].copy()
    ff = prepare(ff_raw)
    portfolios = prepare(p_raw)
    expected = pd.period_range(START, END, freq='M', name='month')
    checks = pd.Series({
        '342 months': len(ff)==len(portfolios)==342,
        '4 factor-file columns': ff.shape[1]==4,
        '25 test portfolios': portfolios.shape[1]==25,
        'same monthly index': ff.index.equals(portfolios.index),
        'complete calendar': ff.index.equals(expected),
        'unique dates': ff.index.is_unique and portfolios.index.is_unique,
        'no missing values': not(ff.isna().any().any() or portfolios.isna().any().any()),
    })
    display(checks.to_frame('passed'))
    assert checks.all()
    '''),
    md('## 4. 形成后续回归使用的对象\n左边是测试资产收益，右边是因子收益。先在同一月份索引下构造，再进行估计。'),
    code("test_excess = portfolios.sub(ff['RF'], axis=0)\nfactors = ff[['Mkt-RF','SMB','HML']]\ndisplay(test_excess.iloc[:3,:5])\nsave_table(test_excess, '00_test_excess_1963_1991')\nsave_table(factors, '00_factors_1963_1991')"),
    md('''
    ## 怎样读这些输出
    25 列代表 25 类股票组合，每列是一条月度收益历史，不是某一家公司。
    后续要解释的是组合之间长期平均收益的差异，而每月实现收益还包含大量共同波动和特有噪声。
    这一步保证了可比较性，还没有对任何模型是否成立给出证据。

    **通关提交：**检查表、你对四个因子文件列与一个测试组合列的解释，以及任何你不能解释的数据处理选择。
    '''),
    boss('保留之前的四道数据 Boss 题。先写自己的理由，再决定是否需要提示。不要只以程序没有报错作为数据正确的依据。')
])

write('01_risk_and_capm.ipynb', [
    md(r'''
    # 第 1 关：分散化、共同风险与 CAPM
    **问题：**持有更多资产为什么能降低一部分风险？资本市场为什么可能只补偿不能被组合分散掉的部分？
    Markowitz 的选择问题是给定预期收益与协方差后怎样配置财富；CAPM 再加入均衡假设，导出预期超额收益与市场 beta 的关系。
    \[E(R_i-R_f)=\beta_i E(R_M-R_f).\]
    这是经济模型施加的限制。把实现收益对市场回归，则是估计和检验这个限制的一种方式。
    参考：[Markowitz 1952](https://doi.org/10.1111/j.1540-6261.1952.tb01525.x)、[Sharpe 1964](https://doi.org/10.1111/j.1540-6261.1964.tb02865.x)。本关是理论实验，不冒充原论文表格复现。
    '''), code(SETUP),
    md('## 1. 一个可控的分散化实验\n教学假设：所有资产的波动率均为 20%/年，两两相关系数固定为 0.20，等权配置。改变资产数量，观察组合风险。'),
    code('''
    n = np.arange(1, 101)
    sigma, rho = .20, .20
    portfolio_vol = sigma * np.sqrt(rho + (1-rho)/n)
    fig, ax = plt.subplots(layout='constrained')
    ax.plot(n, portfolio_vol*100, color='#245b85', label='Equally weighted portfolio')
    ax.axhline(sigma*np.sqrt(rho)*100, color='#825723', linestyle='--', label='Limit under the assumed correlation')
    ax.set(xlabel='Number of assets', ylabel='Annual volatility (%)', title='Diversification under a stated covariance model')
    ax.set_ylim(bottom=0); ax.legend(); plt.show()
    '''),
    md('相关性决定分散化的效果。图中的极限来自指定的协方差结构，是教学机制；它本身没有证明真实市场满足 CAPM，也没有说明共同风险都被市场组合捕捉。'),
    md('## 2. 用真实行业收益看风险—收益配置\n在固定历史样本中，从 30 行业选择前五个行业，生成只做多、权重和为 1 的随机配置。每个点对应一种配置，不是五千个独立经济实验。'),
    code('''
    industry = load_returns('industry30', '1963-07', '1991-12').iloc[:, :5]
    mu, cov = industry.mean().to_numpy(), industry.cov().to_numpy()
    rng = np.random.default_rng(1964)
    weights = rng.dirichlet(np.ones(5), 4000)
    mean_return = weights @ mu
    risk = np.sqrt(np.einsum('ij,jk,ik->i', weights, cov, weights))
    fig, ax = plt.subplots(layout='constrained')
    ax.scatter(risk*100, mean_return*100, s=8, alpha=.30, color='#245b85')
    ax.set(xlabel='Monthly standard deviation (%)', ylabel='Mean monthly return (%)', title='Sample moments: random long-only industry allocations')
    plt.show()
    display(pd.DataFrame({'mean_pct_month':industry.mean()*100,'sd_pct_month':industry.std()*100}))
    '''),
    md('这些点使用事后估计的均值和协方差。它们展示配置问题，但不是当时投资者知道的机会集，也不是严格求出的完整有效前沿。样本均值估计不稳定，是实际配置与理论图形之间的重要距离。'),
    md('## 3. 市场 beta 怎样从协动关系中估计\nbeta 的单位是资产超额收益对市场超额收益的敏感度。本例将每个行业的历史协动关系压缩成一个系数。'),
    code('''
    ff = load_returns('ff3','1963-07','1991-12')
    y = industry.sub(ff['RF'],axis=0)
    beta_cov = y.apply(lambda x: x.cov(ff['Mkt-RF']) / ff['Mkt-RF'].var())
    estimates, _ = fit_models(y,ff[['Mkt-RF']])
    compare = pd.DataFrame({'covariance_beta':beta_cov,'ols_beta':estimates['beta_Mkt-RF'],'alpha_pct_month':estimates['alpha_pct_month']})
    display(compare)
    assert np.allclose(compare.covariance_beta, compare.ols_beta)
    save_table(compare,'01_industry_beta')
    '''),
    md('协方差公式与带截距 OLS 得到相同 beta 是代数核对。是否有零定价误差，需要下一步检验截距及其不确定性。不要把估计敏感度本身当成经济模型已经通过检验。'),
    boss('选择两个行业：描述它们的波动率和 beta。你还需要哪些证据，才能解释它们平均收益的差异？')
])

write('02_portfolio_sorts.ipynb', [
    md('''
    # 第 2 关：发现平均收益的横截面模式
    **问题：**公司规模与账面市值比为什么值得进入研究？先检查它们对应的组合是否存在平均收益模式。
    排序把大量个股压缩成经济含义明确的组合，也降低个股特有噪声。五个规模组与五个 B/M 组独立交叉，得到 25 个测试资产。
    高 B/M 表示账面权益相对市场估值较高。它不自动等同于低风险、高质量或必然低估。
    本关对照 FF1993 Table 2 的股票描述统计，使用月度超额收益，1963-07 至 1991-12。
    '''), code(SETUP), code("display(Markdown(paper_note('ff1993')))"),
    md('## 1. 计算每类股票的平均超额收益\n原论文排序的价值在于让模式可见。先保留全部 25 个组合，而不只挑收益最高的角落。'),
    code('''
    ff = load_returns('ff3','1963-07','1991-12')
    p = load_returns('bm25','1963-07','1991-12')
    excess = p.sub(ff.RF, axis=0)
    mean_grid = pd.DataFrame((excess.mean()*100).to_numpy().reshape(5,5),
        index=['Small','2','3','4','Big'],columns=['Low BM','2','3','4','High BM'])
    display(mean_grid)
    heatmap25(excess.mean()*100,'Mean excess returns, 1963-07 to 1991-12','% per month')
    plt.show()
    descriptive = pd.DataFrame({'mean_excess_pct_month':excess.mean()*100,'sd_pct_month':excess.std()*100,
                                't_mean_iid':excess.mean()/(excess.std()/np.sqrt(len(excess)))})
    save_table(descriptive,'02_ff1993_table2_stock_descriptives')
    '''),
    code('''
    value_spread = mean_grid.iloc[:, -1] - mean_grid.iloc[:, 0]
    size_spread = mean_grid.iloc[0] - mean_grid.iloc[-1]
    display(pd.DataFrame({'High-minus-Low BM (pct/month)':value_spread}))
    display(Markdown(f'**如何读表：**在最小规模组，高 B/M 与低 B/M 的平均超额收益差为 **{value_spread.iloc[0]:.3f} 个百分点/月**；最大规模组对应差为 **{value_spread.iloc[-1]:.3f}**。这些是样本中的平均差异，尚未控制市场暴露。'))
    '''),
    md('## 2. 给平均差异加上不确定性\n构造小股票中的高 B/M 减低 B/M 收益序列，然后对常数项回归，用 HAC 标准误衡量均值估计的不确定性。'),
    code('''
    import statsmodels.api as sm
    spread = p.iloc[:,4] - p.iloc[:,0]
    mean_fit = sm.OLS(spread.to_numpy(), np.ones((len(spread),1))).fit(cov_type='HAC',cov_kwds={'maxlags':6})
    ci = mean_fit.conf_int()[0]*100
    display(pd.DataFrame({'mean_pct_month':[mean_fit.params[0]*100], 't_HAC6':[mean_fit.tvalues[0]],
                          'ci95_low':[ci[0]],'ci95_high':[ci[1]]}))
    '''),
    md('平均差异可以是风险补偿、错误定价、样本偶然性或测量口径的结果。排序描述统计不能单独区分这些机制；下一关先检验最简单的市场风险解释。HAC 是本课程加入的稳健推断，未把它伪装成原文所有 t 值的计算方式。'),
    boss('选取热力图中两个组合，提出一个能解释它们收益差异的假说，并说明下一关怎样检验其中一部分。')
])

write('03_capm_test.ipynb', [
    md(r'''
    # 第 3 关：市场风险能否解释平均收益差异？
    对每个测试组合估计：
    \[R_{i,t}-R_{f,t}=\alpha_i+\beta_i(R_{M,t}-R_{f,t})+\varepsilon_{i,t}.\]
    **经济动机：**如果组合之间的平均收益差异都可以由市场风险补偿解释，模型对平均收益施加的限制就应与截距估计相容。
    这里因子与资产收益使用同一个月；这是定价检验，不是预测下个月收益的交易规则。
    对照 FF1993 Table 4 的股票面板；该表报告的 R² 做了自由度调整。
    '''), code(SETUP), code("display(Markdown(paper_note('ff1993')))"),
    md('## 1. 先完整写出一个组合的回归\n常数项对应截距，斜率对应市场暴露。其余 24 个组合使用完全相同的估计流程。'),
    code('''
    import statsmodels.api as sm
    ff = load_returns('ff3','1963-07','1991-12')
    p = load_returns('bm25','1963-07','1991-12')
    y = p.sub(ff.RF,axis=0)
    market = ff[['Mkt-RF']]
    asset = y.columns[0]
    fit = sm.OLS(y[asset],sm.add_constant(market)).fit()
    robust = fit.get_robustcov_results(cov_type='HAC',maxlags=6)
    display(pd.DataFrame({'coefficient':fit.params,'t_OLS':fit.tvalues,'t_HAC6':robust.tvalues}))
    '''),
    md('## 2. 在全部 25 个测试资产上运行\n`fit_models` 返回每个资产的估计及同步残差矩阵。OLS 和 HAC 只改变标准误估计；系数来自同一个 OLS 拟合。'),
    code('''
    table, residuals = fit_models(y,market)
    display(table[['alpha_pct_month','beta_Mkt-RF','t_alpha_ols','t_alpha_hac','adj_r2']])
    heatmap25(table.alpha_pct_month,'CAPM intercepts, 1963-07 to 1991-12','% per month')
    plt.show()
    save_table(table,'03_ff1993_table4_capm')
    '''),
    md('## 3. 用平均收益关系读回归结果\n带截距 OLS 的样本均值满足“资产平均超额收益 = 截距 + beta × 平均市场超额收益”。这使得截距可以被读作模型留下的平均差额。'),
    code('''
    model_mean = table['beta_Mkt-RF'] * market['Mkt-RF'].mean()
    observed_mean = y.mean()
    assert np.allclose(observed_mean - model_mean, table.alpha)
    fig, ax = plt.subplots(layout='constrained')
    ax.scatter(model_mean*100,observed_mean*100,color='#245b85')
    lim = [min(model_mean.min(),observed_mean.min())*100-.1, max(model_mean.max(),observed_mean.max())*100+.1]
    ax.plot(lim,lim,color='#825723',linestyle='--')
    ax.set(xlabel='Model-implied mean excess return (%/month)',ylabel='Observed mean excess return (%/month)',title='CAPM mean-return comparison')
    plt.show()
    display(Markdown(f'本样本平均绝对截距为 **{table.alpha_pct_month.abs().mean():.3f} 个百分点/月**。散点相对对角线的位置对应各组合的定价差额。经济量级需要结合估计不确定性和组合含义共同判断。'))
    '''),
    md('市场因子是总体财富市场组合的代理。拒绝此经验模型时，要同时考虑理论限制与代理选择；本结果不能单独判定“投资者是否理性”。本关不通过增加变量来追求统计显著性。'),
    boss('从结果中挑一个你认为需要进一步解释的组合。写出证据、经济假说，以及你希望三因子模型改善的具体指标。')
])

write('04_build_ff3.ipynb', [
    md(r'''
    # 第 4 关：把公司特征变成因子收益
    **经济动机：**我们希望用可形成组合的收益序列代表规模和价值相关的共同变动。公司市值与 B/M 用于决定持仓，SMB/HML 则是持仓之后的收益。
    [官方六组合说明](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library/six_portfolios.html)与[官方因子公式](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library/f-f_factors.html)给出了排序与组合规则。
    原始个股排序的时间顺序：上一财年账面权益与上一年十二月市值形成 B/M；六月规模决定规模分组；七月至次年六月观察持有收益。
    这套年度滞后是数据安排的一部分；严格历史可得性还需结合原始财报披露记录。
    '''), code(SETUP),
    md('## 1. 一个月的个股→组合示例\n下列 12 家公司是人为设定的教学数据，全部假定来自用于确定断点的 NYSE 样本。数字用于追踪持仓和权重，不是历史实证结果。'),
    code('''
    toy = pd.DataFrame({'stock':list('ABCDEFGHIJKL'),
        'june_me':[10,20,30,40,50,60,100,120,140,160,180,200],
        'bm':[.2,.4,.6,.8,1.0,1.2,.2,.4,.6,.8,1.0,1.2],
        'july_return':[.01,.02,-.01,.03,.04,.02,.005,.01,-.02,.02,.03,.015]})
    size_cut = toy.june_me.median()
    low_cut, high_cut = toy.bm.quantile([.3,.7])
    toy['size_group'] = np.where(toy.june_me <= size_cut,'S','B')
    toy['bm_group'] = np.select([toy.bm<=low_cut,toy.bm<=high_cut],['L','N'],default='H')
    toy['group'] = toy.size_group + '/' + toy.bm_group
    toy['weight_in_group'] = toy.june_me / toy.groupby('group').june_me.transform('sum')
    toy['contribution'] = toy.weight_in_group * toy.july_return
    display(toy)
    toy_ports = toy.groupby('group').contribution.sum().reindex(['S/L','S/N','S/H','B/L','B/N','B/H'])
    display((toy_ports*100).to_frame('toy_july_return_pct'))
    assert np.allclose(toy.groupby('group').weight_in_group.sum(),1)
    '''),
    md('组合收益是组内持仓收益的加权和。分组依据发生在持有收益之前；改变断点或权重就会改变所测量的投资策略。这里仅展示七月首月，完整年度持有期还涉及权重随价格变化及公司行动而更新。'),
    md('## 2. 使用真实公开六组合构造因子\n六列顺序先小后大，每个规模内按 B/M 从低到高排列。先显示列名，让公式中的组合身份可核查。'),
    code('''
    six = load_returns('bm6')
    display(pd.DataFrame({'position':range(6),'portfolio':six.columns}))
    constructed = pd.DataFrame(index=six.index)
    constructed['SMB'] = six.iloc[:,:3].mean(axis=1)-six.iloc[:,3:].mean(axis=1)
    constructed['HML'] = (six.iloc[:,2]+six.iloc[:,5]-six.iloc[:,0]-six.iloc[:,3])/2
    official = load_returns('ff3')[['SMB','HML']]
    diff = constructed-official
    checks = pd.DataFrame({'corr':[constructed[c].corr(official[c]) for c in constructed],
        'mean_diff_pct_month':diff.mean()*100,'max_abs_diff_pct':diff.abs().max()*100},index=constructed.columns)
    display(checks)
    assert (diff.abs().max() < 0.000051).all()
    save_table(checks,'04_factor_reconstruction_checks')
    '''),
    md('核对阈值来自公开文件显示精度：因子通常保留较少的小数位，六组合文件保留更多位。重建的目的是验证构造流程；极高的相关系数不证明因子具有经济解释力。'),
    code('''
    fig, axes = plt.subplots(1,2,figsize=(10,4.3),layout='constrained')
    for ax,c in zip(axes,['SMB','HML']):
        ax.scatter(official[c]*100,constructed[c]*100,s=8,alpha=.35,color='#245b85')
        lo,hi = official[c].min()*100,official[c].max()*100
        ax.plot([lo,hi],[lo,hi],color='#825723',linestyle='--')
        ax.set(title=c,xlabel='Official (%/month)',ylabel='Reconstructed (%/month)')
    plt.show()
    '''),
    md('SMB 的规模比较跨越三个 B/M 组，HML 的价值比较跨越两个规模组，这样能在构造上缓和另一维度的混杂。但这并不保证因子彼此统计独立，也不构成因果识别。下一关检验这些收益序列是否降低测试资产的定价误差。'),
    boss('改变教学示例中一只股票的市值，观察哪些权重和组合收益变化。说明这个变化如何传到因子；不要只汇报最终数值。')
])

write('05_ff3_replication.ipynb', [
    md(r'''
    # 第 5 关：三因子模型改善了什么？
    **研究问题：**在市场因子之外加入规模和价值因子后，25 类股票组合的平均收益差额是否缩小？
    对照 FF1993 Table 6 的股票回归，1963-07 至 1991-12。原文 Table 9c 还包含债券；本关 25 股票组合的 GRS 是股票子集检验，不复制该表的数值。
    三因子模型把预期超额收益写成三个暴露与因子平均收益的线性组合。其风险解释需要额外经济论证，不能由回归显著性直接推出。
    '''), code(SETUP), code("display(Markdown(paper_note('ff1993')))"),
    md('## 1. 在相同测试资产和样本上比较模型\n固定样本后再比较，避免把换样本的影响误记为加因子的贡献。'),
    code('''
    ff = load_returns('ff3','1963-07','1991-12')
    p = load_returns('bm25','1963-07','1991-12')
    y = p.sub(ff.RF,axis=0)
    models = {'CAPM':ff[['Mkt-RF']],'FF3':ff[['Mkt-RF','SMB','HML']]}
    summary = model_summary(y,models)
    display(summary)
    capm,_ = fit_models(y,models['CAPM'])
    ff3,residuals = fit_models(y,models['FF3'])
    display(ff3[['alpha_pct_month','beta_Mkt-RF','beta_SMB','beta_HML','t_alpha_ols','t_alpha_hac','adj_r2']])
    save_table(summary,'05_capm_vs_ff3')
    save_table(ff3,'05_ff1993_table6_ff3')
    '''),
    md('## 2. 看改善发生在哪些组合\n两幅图使用相同色阶和单位，保留全部组合。每个格子的数值是截距，不是该组合的总平均收益。'),
    code('''
    fig, axes = plt.subplots(1,2,figsize=(11,5),layout='constrained')
    lo = min(capm.alpha_pct_month.min(),ff3.alpha_pct_month.min())
    hi = max(capm.alpha_pct_month.max(),ff3.alpha_pct_month.max())
    heatmap25(capm.alpha_pct_month,'CAPM alpha','% per month',ax=axes[0],vmin=lo,vmax=hi)
    heatmap25(ff3.alpha_pct_month,'FF3 alpha','% per month',ax=axes[1],vmin=lo,vmax=hi)
    plt.show()
    a,b = summary.loc['CAPM','mean_abs_alpha_pct_month'],summary.loc['FF3','mean_abs_alpha_pct_month']
    display(Markdown(f'**当前快照的结果：**平均绝对截距由 **{a:.3f}** 变为 **{b:.3f} 个百分点/月**。这衡量平均定价差额的量级变化；各格子的方向和检验结果仍需分别阅读。'))
    '''),
    md(r'''
    ## 3. 联合定价检验
    GRS 检验所有测试资产截距同时为零。公共实现采用
    \[G=\frac{T-N-K}{N}\frac{\hat\alpha'\hat\Sigma^{-1}\hat\alpha}{1+\bar f'\hat\Omega^{-1}\bar f},\]
    其中残差与因子协方差均以 T 为分母。经典假设下参考 F(N,T−N−K) 分布；表中 p 值是右尾概率。
    模块将这个经典检验与 HAC 单个截距推断分开。可打开 `src/analysis.py` 逐行看矩阵计算。
    '''),
    code('''
    joint = grs_test(y,models['FF3'])
    display(pd.Series(joint).to_frame('FF3 joint test'))
    decision = '拒绝' if joint['pvalue']<.05 else '未拒绝'
    display(Markdown(f'按经典 GRS 的 5% 阈值，当前样本**{decision}**零截距联合限制（p={joint["pvalue"]:.4g}）。这评价的是给定因子、资产和样本的限制；未拒绝也不等于证明模型正确。'))
    '''),
    md('## 原论文对照与经济解释\n对照 Table 6 时使用 `adj_r2`，并先核对月份、组合身份和收益单位。表中显著因子暴露描述共同变动；定价检验进一步关心平均收益限制。一个模型可能改善平均误差而仍无法解释所有测试资产。'),
    boss('写一段不超过 200 字的审稿意见：三因子相对 CAPM 的证据有哪些？还缺哪一种证据，才能把统计改善解释为风险补偿机制？')
])

# 将少量已经核实的原文数字与当前重算值并排展示，避免以版本差异作为报错。
anchor_setup = '''
import json
anchors = json.loads((ROOT/'papers/paper_map.json').read_text(encoding='utf-8'))['numeric_anchors']
'''
additions = {
    '02_portfolio_sorts.ipynb': [
        md('## 与原文 Table 2 对照\n下表展示已逐页核实的少量原文数值和本次重算值，单位均为百分比/月。完整原表见本地 PDF 第12–13页。差值用于定位样本、口径与数据版本差异，不设强制相等断言。'),
        code(anchor_setup + '''
rows = []
for a in anchors:
    if a['paper']=='ff1993' and a['table']=='2':
        current = ff[a['key']].mean()*100 if a['metric']=='mean_factor_return' else excess[a['key']].mean()*100
        rows.append({'对象':a['key'],'原文':a['paper_value'],'当前快照':current,'当前减原文':current-a['paper_value']})
comparison = pd.DataFrame(rows)
display(comparison)
save_table(comparison,'02_original_table2_anchors')
''')],
    '03_capm_test.ipynb': [
        md('## 原文斜率与截距分在两张表\n斜率、调整 R² 对照 **Table 4（PDF第18页）**；α 对照 **Table 9a(ii)（PDF第34页）**。下面选择同一个 SMALL LoBM 组合演示逐项对照。'),
        code(anchor_setup + '''
rows = []
for a in anchors:
    if a['paper']=='ff1993' and a.get('model')=='CAPM':
        field = {'market_beta':'beta_Mkt-RF','adjusted_r_squared':'adj_r2','alpha':'alpha_pct_month'}[a['metric']]
        current = table.loc[a['key'],field]
        rows.append({'原表':a['table'],'指标':field,'原文':a['paper_value'],'当前快照':current,'当前减原文':current-a['paper_value']})
display(pd.DataFrame(rows))
''')],
    '05_ff3_replication.ipynb': [
        md('## 与原文 Table 6、9a(iv) 对照\n**Table 6（PDF第22–23页）**提供斜率及调整 R²；本关 α 热力图对应 **Table 9a(iv)（PDF第35页）**。同一组合的比较如下；量纲见指标列。'),
        code(anchor_setup + '''
rows = []
for a in anchors:
    if a['paper']=='ff1993' and a.get('model')=='FF3_classic':
        field = {'market_beta':'beta_Mkt-RF','adjusted_r_squared':'adj_r2','alpha':'alpha_pct_month'}[a['metric']]
        current = ff3.loc[a['key'],field]
        rows.append({'原表':a['table'],'指标':field,'原文':a['paper_value'],'当前快照':current,'当前减原文':current-a['paper_value']})
display(pd.DataFrame(rows))
save_table(pd.DataFrame(rows),'05_original_ff3_anchors')
''')],
}
for name, new_cells in additions.items():
    notebook = nbf.read(OUT/name,as_version=4)
    notebook.cells[-1:-1] = new_cells
    nbf.write(notebook,OUT/name)

print('Created START_HERE and notebooks 00–05.')
