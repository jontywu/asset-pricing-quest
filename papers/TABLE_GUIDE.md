# 论文与 Notebook 对照导览

先运行一个 Notebook，再带着它输出的一个问题看对应原文。每次只核对研究对象、样本、指标与少量关键结果，不需要逐格恢复论文所有表。目标是能说明：作者观察了什么现象，提出了什么解释，又用什么证据检验它。

本目录的 [FF1993](ff1993_primary_reference.pdf) 与 [FF2015](ff2015_primary_reference.pdf) 是论文全文。下方链接中的 `#page=N` 使用阅读器从 1 开始计数的 PDF 页码；若阅读器未自动跳页，手动输入这个数字即可。FF1993 的印刷页码比 PDF 页码大 2；FF2015 两者相同。

| 样本 | 期间 | 月数 | 本课程对应范围 |
|---|---|---:|---|
| FF1993 | 1963-07—1991-12 | 342 | 25 个股票组合及股票三因子部分 |
| FF2015 | 1963-07—2013-12 | 606 | 2×3 因子版本，配合 25/32 个股票测试组合 |

FF1993 全文同时研究股票和债券。只完成股票部分时，应明确写成“股票部分复现”。两个样本都使用当前冻结的数据版本重算；原论文数字保留为参照。

**按主线阅读**

| Notebook | 带着什么问题读 | 原文定位 |
|---|---|---|
| [00 数据实验台](../notebooks/00_data_lab.ipynb) | 每列是什么经济量，月份、单位与样本怎样对应？ | FF1993 数据与组合说明，[PDF 第 6–8 页](ff1993_primary_reference.pdf#page=6)，印刷第 8–10 页。本关尚无结果表要复现。 |
| [01 风险与 CAPM](../notebooks/01_risk_and_capm.ipynb) | 分散化怎样改变风险，beta 衡量什么协动关系？ | 理论与教学实验，为读单因子回归做准备；不是 FF 论文某一表的复现。 |
| [02 组合排序](../notebooks/02_portfolio_sorts.ipynb) | 25 类股票之间有什么平均收益模式？ | FF1993 **Table 2**：[因子统计 PDF 第 12 页](ff1993_primary_reference.pdf#page=12)、[股票组合统计第 13 页](ff1993_primary_reference.pdf#page=13)，印刷第 14–15 页。 |
| [03 CAPM 检验](../notebooks/03_capm_test.ipynb) | 市场暴露能否解释这些平均收益差异？ | 斜率与调整 R² 看 **Table 4**，[PDF 第 18 页](ff1993_primary_reference.pdf#page=18)，印刷第 20 页；**α 看 Table 9a(ii)**，[PDF 第 34 页](ff1993_primary_reference.pdf#page=34)，印刷第 36 页。 |
| [04 构造三因子](../notebooks/04_build_ff3.ipynb) | 股票特征如何经过分组、持仓与加权，变成因子收益？ | FF1993 Section 2.1.2，[PDF 第 6–8 页](ff1993_primary_reference.pdf#page=6)，印刷第 8–10 页。先跟踪一条收益计算，再核对公开六组合与官方因子。 |
| [05 三因子检验](../notebooks/05_ff3_replication.ipynb) | 加入 SMB/HML 后，平均收益差额与共同波动的解释各怎样变化？ | 斜率、调整 R² 看 **Table 6**，[PDF 第 22–23 页](ff1993_primary_reference.pdf#page=22)，印刷第 24–25 页；**α 看 Table 9a(iv)**，[PDF 第 35 页](ff1993_primary_reference.pdf#page=35)，印刷第 37 页。 |
| [06 Fama–MacBeth](../notebooks/06_fama_macbeth.ipynb) | 时间序列暴露与横截面的风险价格怎样联系？ | 方法扩展。FF1993 主检验采用时间序列回归，不把本关的两步回归冒充它某张表的重算。 |
| [07 构造五因子](../notebooks/07_build_ff5.ipynb) | 盈利与投资特征如何形成组合，SMB 的构造有什么变化？ | FF2015 **Table 3**，[第 6 页](ff2015_primary_reference.pdf#page=6)；因子统计 **Table 4**，[第 7 页](ff2015_primary_reference.pdf#page=7)。基础组合统计可选看 **Table A1**，[第 20 页](ff2015_primary_reference.pdf#page=20)。 |
| [08 五因子检验](../notebooks/08_ff5_replication.ipynb) | 新增因子改善哪些测试组合，模型还留下哪些误差？ | 先看模型比较 **Table 5**，[第 9 页](ff2015_primary_reference.pdf#page=9)，再按下表选一组详细回归；因子涵盖检验看 **Table 6**，[第 11 页](ff2015_primary_reference.pdf#page=11)。 |
| [09 样本外检验](../notebooks/09_out_of_sample.ipynb) | 论文样本之后，原有描述与模型表现是否保持？ | 本课程的后续研究，不对应原论文表格。区分“新期间重新估计”与“只使用当时可得信息进行预测”。 |

**五因子论文的测试组合怎么找**

先读描述统计，确定模型试图解释的差异，再读 Table 5 的总体比较；需要理解某个异常格子时，才打开详细回归。`2×3` 是因子的构造方式，`5×5` 或 `2×4×4` 是测试组合的划分，两者可以不同。

| 测试组合 | 平均收益模式 | Table 5 面板 | 详细回归 |
|---|---|---|---|
| 25 Size×B/M | [Table 1A，第 3 页](ff2015_primary_reference.pdf#page=3) | A | [Table 7，第 13 页](ff2015_primary_reference.pdf#page=13) |
| 25 Size×OP | [Table 1B，第 3 页](ff2015_primary_reference.pdf#page=3) | B | [Table 9，第 16 页](ff2015_primary_reference.pdf#page=16) |
| 25 Size×Inv | [Table 1C，第 3 页](ff2015_primary_reference.pdf#page=3) | C | [Table 10，第 17 页](ff2015_primary_reference.pdf#page=17) |
| 32 Size×B/M×OP | [Table 2，第 5 页](ff2015_primary_reference.pdf#page=5) | D | [Table A2，第 20 页](ff2015_primary_reference.pdf#page=20) |
| 32 Size×B/M×Inv | [Table 2，第 5 页](ff2015_primary_reference.pdf#page=5) | E | [Table A3，第 21 页](ff2015_primary_reference.pdf#page=21) |
| 32 Size×OP×Inv | [Table 2，第 5 页](ff2015_primary_reference.pdf#page=5) | F | [Table 11，第 18 页](ff2015_primary_reference.pdf#page=18) |

**四个会改变读表结论的细节**

1. **斜率表与 α 表回答不同问题。**FF1993 Table 6 展示因子暴露、调整 R²及残差标准误；α 矩阵在 Table 9a。高 R²说明收益随时间的波动得到较好解释，不能代替平均收益限制的检验。Table 4、6 的 R²均做了自由度调整。
2. **比较新增因子时固定 SMB 口径。**对照 FF2015 Table 5 的 2×3 列，三因子规格取同一份五因子数据的 Mkt-RF、SMB、HML，再加入 RMW、CMA。这里的 SMB 是三套排序所得规模差的平均。独立经典三因子文件的 SMB 可以另作比较，但应标明：这时既增加了因子，也改变了规模因子的定义。
3. **详细五因子系数表使用 HMLO。**在原样本中回归 `HML = 截距 + 其他四因子的线性组合 + 残差`，令 `HMLO = 截距 + 残差`。它是同一模型的重新表达。替换后 α、残差和 R²不变，HML/HMLO 的斜率相同，其他四因子的斜率通常改变。若代码使用普通 HML，可直接比较 α；要逐项比较 Table 7/9/10/11/A2/A3 的斜率，需要先统一这个表达方式。只取残差会漏掉截距。
4. **收益口径和检验范围要一致。**FF2015 Table 1、2 是月度超额收益，Table A1 是基础组合的原始收益。FF1993 Table 9c 联合检验 25 股票和 7 债券，不能拿 25 股票的 GRS 逐数匹配；它列出的概率还是左尾累计概率，而课程代码通常报告右尾 p 值。

代码里若收益以小数存储，乘 100 后才与论文的“百分比/月”对照；beta、t 值、R²与 GRS 不乘 100。常规 OLS 与 HAC 推断也应分别标明。模型在某组资产上误差较小，不自动证明它已解释所有资产或识别了风险补偿的经济机制。

**怎样判断自己读懂了这一关**

保存一份输出，写清样本、测试组合与模型；选一个结果，用自己的话说明它支持哪项判断、尚不能排除哪种解释；再提出一个能区分这些解释的检查。代码正常运行、出现显著性、或把数字调到原文附近，都不单独构成通关证据。

原文少量数字及精确页码见 [paper_map.json](paper_map.json)。它们用于查单位、样本与模型规格，并展示当前结果与原文的差值。历史数据修订、市场代理和特征定义更新都可能造成差异。作者的数据变更说明见[官方数据目录](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html)；原始 PDF 地址和 SHA256 也记录在 JSON 中。
