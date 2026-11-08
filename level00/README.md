# 第 0 关：数据侦察兵

本轮目标：把官方数据读入 Python，观察表格结构。Boss 题答案不在本目录中。

## 文件

- `download_data.py`：官方下载、ZIP/CSV 校验与来源记录。再次运行会核验现有快照，保留原下载时间。
- `read_data.py`：原始文本预览、表格目录、两张课题用表格的读取。数值与日期先保留为字符串。
- `practice.py`：你的练习区。本轮只做任务 A，B/C/D 后续逐步完成。
- `data/raw/`：原始 ZIP、解出的原始 CSV，以及 `manifest.json` 来源记录。

## 本机直接运行

已确认下面的 Python 环境可使用 pandas。请在 PowerShell 中运行：

```powershell
Set-Location -LiteralPath 'E:\Eth data\asset_pricing_quest\level00'
& 'E:\Eth data\.venv-bigquery\Scripts\python.exe' -X utf8 .\read_data.py --peek
```

数据已经下载。需要重验本地快照时运行：

```powershell
& 'E:\Eth data\.venv-bigquery\Scripts\python.exe' -X utf8 .\download_data.py
```

填写任务 A 的 TODO 后运行：

```powershell
& 'E:\Eth data\.venv-bigquery\Scripts\python.exe' -X utf8 .\practice.py
```

在 VS Code 中可选择上述解释器，再按 `# %%` 分段执行。分段执行时把工作目录设为本目录。

其他机器使用 Python 3.10+，安装 `requirements.txt` 后用自己的解释器运行即可。

## 本轮交付

1. 两张表的 shape。
2. 两张表的列名、首尾索引和数据类型。
3. 你对一行、一列各代表什么的初步理解；不确定的地方直接写出来。

先不做回归，不必一次填完后续 TODO。原始文件保持不变，后续清洗在内存副本中进行。

## 来源

- 官方目录：https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html
- 三因子说明：https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library/f-f_factors.html
- 25 组合说明：https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library/tw_5_ports.html

下载时间、完整下载 URL、实际跳转 URL、文件大小、SHA-256 和源文件版本首行，均记录在 `data/raw/manifest.json`。本目录冻结的是当前官方下载快照，不是声称恢复了 1993 年的数据版本。
