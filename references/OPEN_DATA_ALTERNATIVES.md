# 公开数据与开源实现：本课程的使用路径

本课程主线直接使用 Kenneth French 已构造的因子收益和测试组合收益。它们足以完成排序组合观察、三因子与五因子回归、联合检验和样本外比较；无需先取得个股数据库，便能理解模型在解释什么、怎样被检验。

本地的 `github/OpenSourceAP_CrossSection/` 是一份小型阅读参考包，保存了公开项目的原始文件、许可证和固定 commit。它用于理解特征与组合构造，没有执行第三方流水线，也不是主线 Notebook 的运行依赖。

## 三种材料分别解决什么问题

| 材料 | 可做的研究 | 与本课程的关系 |
|---|---|---|
| [Kenneth French Data Library](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html) 的因子及组合收益 | 检验收益模型、比较定价误差、核对公开六组合与因子公式 | 主线数据已本地化，Notebook 默认使用这一套口径 |
| [Open Source Asset Pricing](https://www.openassetpricing.com/) 已构造的股票特征和组合收益 | 扩展到更多异常、信号和组合构造，研究实现差异 | 可选扩展；预计算数据可以替代自行跑完整上游流水线，但具体可做的分析取决于所下载文件 |
| 开源源码和有权限取得的 CRSP／Compustat 原始数据 | 重建每一步个股筛选、财务匹配、排序与权重 | 进阶副本；源码公开不表示原始商业数据库随仓库提供 |

OpenSourceAP 的官方入口目前提供 [Hugging Face 数据集](https://huggingface.co/datasets/OpenSourceAP/CrossSection)、Python/R 下载工具和 [Signal Browser](https://openassetpricing.com/SignalDoc-Browser.html)。本次仅保存下面的少量源码阅读材料，未下载大型股票面板；主线已有的 French 数据足以开始学习。

## 本地参考包的阅读顺序

所有路径均相对于 `references/github/OpenSourceAP_CrossSection/`。

| 文件 | 阅读重点 | 需要辨认的口径 |
|---|---|---|
| `README.md` | 股票特征生成、组合构造、公开数据发布这三层如何衔接 | 上游代码读取 WRDS 等来源；组合代码还需要 CRSP 收益与市值输入 |
| `Signals/pyCode/Predictors/Size.py` | 从市值构造规模特征，观察筛选和输出字段 | 这是 Banz 规模特征实现，包含自己的证券筛选；不能把该列直接当成 SMB 收益 |
| `Signals/pyCode/Predictors/BMdec.py` | 从财务项目组合出账面权益，匹配十二月市值和日历滞后 | 对应 FF1992 风格的个股特征；信号更新时间与组合形成规则是两个步骤 |
| `Signals/pyCode/Predictors/OperProf.py` | 收入减经营成本、管理费用与利息后相对权益的盈利度量 | 此文件标注 FF2006，使用 `ceq`，并排除最小规模三分组；它不是官方 FF2015 RMW 构造的逐项替代 |
| `Signals/pyCode/Predictors/AssetGrowth.py` | 按公司和月份计算总资产的年度增长 | 该实现引用 Cooper、Gulen、Schill（2008）；构造出的是信号，还要定义分组、持有期和多空方向 |
| `Portfolios/Code/32_Predictor2x3Ports.R` | 六月截面、NYSE 分位点、2×3 分组、滞后分组与加权收益 | 这是 FF1993 风格的组合构造参考；输入信号不同，最终收益也会不同 |
| `Portfolios/Code/01_PortfolioFunction.R` | 通用排序组合函数如何处理重分组、信号滞后、权重和多空腿 | 默认参数与每个信号的配置必须一起阅读 |

这几份文件不组成独立可执行的完整项目，因而不需要在 VS Code 中按“全部运行”。先运行主线 Notebook，再打开对应源码定位同一经济步骤，更容易分辨“理论概念”“变量定义”“投资组合实施”的层次。

## 预计算组合的替代边界

OpenSourceAP 的 FAQ 明确区分单变量 B/M 排序和规模平衡的 2×3 HML 构造。两种收益可以用于不同问题，不能仅凭名称相近就视为同一序列。它也提供 FF93 风格的 2×3 预计算组合扩展。

因此，后续选择公开替代数据时应记录：信号定义、分组断点、证券范围、加权方式、调仓规则、持有期、数据版本和收益单位。对于当前三因子／五因子课程，保留 French 数据作为主结果，其他公开实现用于解释和稳健性比较。

来源：[OpenSourceAP FAQ](https://www.openassetpricing.com/faq/)；[固定版本 README](https://github.com/OpenSourceAP/CrossSection/blob/9f053398c4995651d822e90d81526d0644c6f3e5/README.md)。

## 来源、许可证与复查

- 仓库：[OpenSourceAP/CrossSection](https://github.com/OpenSourceAP/CrossSection)。
- 固定 commit：`9f053398c4995651d822e90d81526d0644c6f3e5`，提交时间 `2026-10-27 20:27:06 UTC`。
- 原始许可文件保留为 `github/OpenSourceAP_CrossSection/LICENSE`（GPL-2.0），第三方文件内容未改写。
- 每个文件的固定版本 URL、下载 URL、字节数和 SHA-256 见同目录的 `SOURCE_MANIFEST.json`。
- 已通过 GitHub connector 核对仓库、README、commit 和选取源码；没有运行第三方代码。
- 如在自己的研究中使用 OpenSourceAP 的数据或代码，应按作者 README 引用 Chen and Zimmermann（2022），*Open Source Cross-Sectional Asset Pricing*, *Critical Finance Review*。

核验本地文件时，可在课程根目录运行：

```powershell
& .\.venv\Scripts\python.exe -X utf8 .\references\download_github_reference.py
```

已有文件会按来源清单校验，不更新成浮动分支的新版本。
