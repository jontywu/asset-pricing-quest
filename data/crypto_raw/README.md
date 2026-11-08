# 加密货币三因子：作者公开数据快照

原始文件 `LTW_3factor.xlsx` 来自 [Yukun Liu 作者研究页](https://www.yukunliu.com/research/) 下的 “3-Factor Data” 链接，关联论文为 Liu、Tsyvinski、Wu（2022），*Common Risk Factors in Cryptocurrency*，*The Journal of Finance*，DOI [10.1111/jofi.13119](https://doi.org/10.1111/jofi.13119)。

`LTW_3factor_raw_values.csv` 是原始 XLSX 中 `Sheet1!A6:D485` 的直接导出，保留列名与原始数值，没有乘除 100、填补缺失或构造模型。

- 列名：`yyww`、`cmkt`、`csize`、`cmom`。
- 479 个观测，从 `201404` 至 `202314`，周标识唯一且按作者每年 52 周的日历连续。
- 作者在 `A2` 说明：每年固定 52 周，最后一周长于 7 天。因此不能直接当作 ISO 周号处理。
- 作者在 `A3` 写“更新至 2022 年”，但实际末行为 `202314`；来源说明与实际覆盖分别记录。
- 同一行说明，自 2020 年中开始使用 CoinGecko 数据；跨版本比较应保留该来源变化。
- **单位尚未核实**：工作簿没有明确写出小数收益或百分数收益。这里仅展示原始数值，不据量级猜测、不转换单位、不估计模型结果。

来源 URL、下载 UTC 时间、SHA-256、工作簿修改时间、行列检查和导出过程均在 `manifest.json` 中。`inspect_author_data.py` 可复查原始 XLSX 并重建此原始值 CSV，只需项目已有的 Python 与 pandas，不依赖 openpyxl。

论文目录中保存的是作者机构网站公开的 **2019-04-15 工作稿**，共 47 页。它不是 2022 年正式期刊版；表号、样本期与策略数量应按版本分别核对。正式 PDF、2021 年 SSRN 修订稿及期刊复现代码 ZIP 的公开下载端点本次均返回 HTTP 403，具体记录在 `../../papers/crypto/download_attempts.json`。
