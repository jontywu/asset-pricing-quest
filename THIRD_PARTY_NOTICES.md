# 数据、论文与参考代码来源

本仓库是资产定价教学与实证练习。课程代码、公开数据、论文引用和外部参考代码是不同的材料；本文件不为它们设定统一的新许可证。第三方材料的权利与适用条件归其各自权利人，公开下载不等于获得任意再许可权。

## Kenneth French 数据库

`data/raw/` 保存从 [Kenneth French Data Library](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html) 下载的 14 份因子与组合收益快照，以及对应的原始 ZIP、CSV。来源 URL、下载时间、源版本和 SHA-256 见 `data/raw/manifest.json`；原文件中的来源文字保留。使用这些资料时应注明数据库来源，并查阅来源网站的使用条件。

这些是已构造的组合收益，并非 CRSP/Compustat 个股数据的再分发。数据下载于 2026-11-08，可能包含官方对历史数据的后续修订；课程重算不声称逐数恢复原论文发表时的数据版本。`results/` 和 Notebook 输出是基于该快照的教学计算结果。

## 加密资产作者数据

`data/crypto_raw/LTW_3factor.xlsx` 来自 [Yukun Liu 的作者研究页面](https://www.yukunliu.com/research/)，用于 Liu、Tsyvinski、Wu 的 *Common Risk Factors in Cryptocurrency*（[Journal of Finance, 2022](https://doi.org/10.1111/jofi.13119)）。CSV 是作者工作簿的原值导出，来源、转换说明和哈希见 `data/crypto_raw/manifest.json`。

作者采用每年 52 周的自定义周历，末周可超过七天。工作簿说明写“更新至 2022”，实际记录止于周代码 `202314`，两者均保留。收益是小数还是百分数尚未从作者说明核实；课程只读取展示原值，不据此估计加密因子回归。作者说明自 2020 年中起使用 CoinGecko 数据。本仓库不为该作者数据另授开放许可证。

## 论文

仓库与 GitHub Pages 不托管第三方论文 PDF。`papers/paper_map.json`、`papers/crypto/manifest.json` 保存来源与版本，`papers/TABLE_GUIDE.md` 提供阅读导航。`python scripts/download_papers.py` 可按已记录的公开来源下载到本地，并校验原有 SHA-256；下载失败不会改用其他版本。

- Fama、French（1993）：*Common risk factors in the returns on stocks and bonds*，[DOI](https://doi.org/10.1016/0304-405X(93)90023-5)。
- Fama、French（2015）：*A five-factor asset pricing model*，[DOI](https://doi.org/10.1016/j.jfineco.2014.10.010)。
- Liu、Tsyvinski、Wu：本地可下载材料是 [Yale Cowles 托管的 2019-04-15 工作稿](https://cowles.yale.edu/sites/default/files/2022-10/LiuTsyvinskiWu2019%20COMMON%20RISK%20FACTORS.pdf)，不能当作 2022 正式刊物版本。

MS2026 加密支线是文献讲解；正式附件尚未核验，不声称完整复现。课程对论文表格的重算、少量对照数字与经济解释须结合各 Notebook 的范围说明阅读。

## OpenSourceAP 参考代码

`references/github/OpenSourceAP_CrossSection/` 保存 [OpenSourceAP/CrossSection](https://github.com/OpenSourceAP/CrossSection) 的固定版本参考文件。上游版本、文件路径与来源见该目录的 `SOURCE_MANIFEST.json`，原有 **GNU GPL version 2** 许可文本完整保留在该目录的 `LICENSE`。这些文件用于阅读构造方式，不是本课程执行链的一部分。引用和再分发这些文件时须保留其原许可证与来源，不应将整个参考目录改标为其他许可证。
