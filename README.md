# 资产定价研究者：Notebook 通关课程 · asset-pricing-quest

资产定价复现实验课：从 CAPM、Fama–French 三因子与五因子到因子 zoo 和加密资产。含自解释 Jupyter Notebook、公开数据与保留结果。

[在线阅读课程](https://jontywu.github.io/asset-pricing-quest/) · [GitHub 仓库](https://github.com/jontywu/asset-pricing-quest) · [Notebook 入口](notebooks/START_HERE.ipynb) · [自解释导读](notebooks/PRELUDE_beta_to_factor_zoo.ipynb)

从 `notebooks/START_HERE.ipynb` 开始。10 关均有可运行代码、保留的执行结果、经济学解释与留空的 Boss 作答区。数据来自 Kenneth French 官方公开研究库，全部主线可以离线重跑。

想先建立历史与理论地图，可先读 `notebooks/PRELUDE_beta_to_factor_zoo.ipynb`。这本已扩写为自解释教程：先解释收益、账面权益、市值和 B/M，再用手算例子构造 SMB、HML；盈利、投资、动量、加密变量及回归统计量都有定义、经济含义和选用理由。目录可跳转，结果表使用中文列名，所有说明和示例都在同一本里，无需先读其他关卡。

导读仍保留 CAPM 到 factor zoo 的历史，以及 JF2022 加密三因子、MS2026 加密四因子支线。它是贯穿各关的导读，不占用关卡编号。运行使用项目内已下载的数据和公共函数，不需要联网下载。

## 在线阅读与本地运行

GitHub Pages 展示 Notebook 已保存的文字、代码和结果，不在浏览器里运行 Python。需要修改参数、重新估计或填写 Boss 作答区时，克隆仓库后在本地 VS Code 中打开 Notebook。网页展示以当前 `.ipynb` 为准。

使用 Python 3.12 创建独立环境。Windows PowerShell：

```powershell
git clone https://github.com/jontywu/asset-pricing-quest.git
Set-Location asset-pricing-quest
py -3.12 -m venv .venv
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt
& .\.venv\Scripts\python.exe -m ipykernel install --user --name asset-pricing-quest --display-name "Python (Asset Pricing Quest)"
```

macOS / Linux：

```bash
git clone https://github.com/jontywu/asset-pricing-quest.git
cd asset-pricing-quest
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m ipykernel install --user --name asset-pricing-quest --display-name "Python (Asset Pricing Quest)"
```

打开 `AssetPricingQuest.code-workspace`，然后打开 `notebooks/START_HERE.ipynb`。
选择内核 `Python (Asset Pricing Quest)`。Windows 解释器位于 `.venv/Scripts/python.exe`；macOS / Linux 位于 `.venv/bin/python`，如工作区默认路径不适用，请在 VS Code 中手动选择。
Python 与 Jupyter 扩展在工作区推荐列表中。逐格按 Shift+Enter；重跑整个实验可用 Restart Kernel and Run All。

仓库不包含本机 `.venv`。`requirements.txt` 用于新机器安装；`requirements-lock.txt` 是 2026-11-08 原 Windows 环境的版本记录，保留用于追溯，不能保证跨平台直接安装。数据快照与执行输出已包含在仓库中，主线计算可离线重跑。图中中文如显示方框，请为操作系统安装中文字体后重新运行绘图单元。

## 目录

| 路径 | 内容 |
|---|---|
| notebooks/ | 入口、历史导读与第00–09关。每本独立加载输入，不依赖前一本的内存状态 |
| data/raw/ | 14份原始ZIP及CSV、来源/UTC下载时间/SHA-256清单 |
| data/crypto_raw/ | 加密三因子作者原件、原值CSV与来源清单；单位尚未核实，只作读取展示 |
| papers/ | FF1993与FF2015表格导航、原文数字核对点和来源；PDF 可按来源下载至本地 |
| papers/crypto/ | LTW2019作者工作稿的来源，明确区别于JF2022正式版；MS2026正式附件尚未核验 |
| src/course.py | 读取、单位与样本处理、组合构造、图表等公共工具 |
| src/analysis.py | OLS、HAC和经典GRS的中文说明与实现 |
| results/ | Notebook运行生成的CSV结果表 |
| references/ | 开源替代说明、固定版本的GitHub构造代码参考，含原许可证 |
| scripts/ | 数据/论文下载、批量执行和网页导出脚本。旧 Notebook 生成脚本的覆盖风险见下文 |
| docs/ | 从当前 Notebook 已保存输出导出的 GitHub Pages 静态站点 |
| level00/ | 第0关的读取、下载和练习骨架；主线公共工具仍使用其读取模块 |
| THIRD_PARTY_NOTICES.md | 数据、论文及外部参考代码的来源与适用范围 |

**保留你编辑后的版本：** `build_intro_notebooks.py`、`build_advanced_notebooks.py`、`build_history_notebook.py` 及其 `history_*.py` 模块生成的是 2026-11-08 润色前的旧版文字，运行这些旧生成脚本会覆盖 `notebooks/` 中的当前版本。日常重算使用 `execute_course.py`；网页导出使用 `build_site.py`，它读取当前 Notebook，不重建课程内容。本机 `backup/`、缓存和浏览器预览未上传。

## 课程范围

FF1993 对照股票部分的 Table 2、4、6、9a；其债券部分未纳入。
FF2015 重点使用2×3因子，覆盖三套25组合与三套32组合的模型比较。
第01关是理论与模拟练习，第06关是Fama–MacBeth方法练习，第09关是样本后扩展。
这些练习不声称逐项恢复1973、1992或原始个股数据库。具体口径见 `papers/TABLE_GUIDE.md`。

French 的已完成组合收益足以理解本课程的经济学机制与实证检验。
`references/OPEN_DATA_ALTERNATIVES.md` 说明 GitHub 与 OpenSourceAP 能提供什么，哪些构造并不等同于FF2015。
教学个股数据明确标为人为设定，不混入真实历史结果。

## 重跑与复现

```powershell
# 在仓库根目录执行
# 只核验已下载快照；缺少的未下载数据才联网获取
& .\.venv\Scripts\python.exe -X utf8 .\scripts\download_all.py
# 从干净内核执行全部Notebook并保存输出
& .\.venv\Scripts\python.exe -X utf8 .\scripts\execute_course.py
# 核查核心统计实现
& .\.venv\Scripts\python.exe -X utf8 .\tests\test_analysis.py
```

macOS / Linux 将上述解释器替换为 `.venv/bin/python`，脚本路径使用 `/`。

不要修改 `data/raw/` 原始文件。要研究其他数据版本，另存一个新目录及来源记录。
原Notebook已有输出，不运行也可以浏览；本地`.venv`不适合跨机器直接复制。

## 下载本地论文

论文 PDF 不随 GitHub 仓库或 Pages 分发。原 Notebook 中的本地 PDF 链接在下载后可用；论文的 DOI、版本、页码和表格说明保留在仓库中。下载脚本读取现有来源清单，已存在的文件只校验、不覆盖；新文件须通过原 SHA-256 检查才保存。

```powershell
& .\.venv\Scripts\python.exe -X utf8 scripts/download_papers.py --list
& .\.venv\Scripts\python.exe -X utf8 scripts/download_papers.py
```

若来源失效或文件版本变化，脚本会报出失败并保留现有资料，不自动替换为其他版本。LTW 材料是 2019 工作稿，不能当作 2022 正式版。完整来源与第三方许可说明见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。

## 更新 Notebook 与网页

1. 在 VS Code 编辑 `.ipynb`，如需更新结果则运行有关单元并保存。不要用旧生成脚本覆盖内容。
2. 在仓库根目录运行下列命令，将当前已保存内容导出到 `docs/`。导出过程不执行 Notebook。
3. 查看 Git 差异后提交并推送。GitHub Pages 使用 `main` 分支的 `/docs` 目录，推送后等待站点构建完成。

```powershell
& .\.venv\Scripts\python.exe -X utf8 scripts/build_site.py
git status --short
git diff --stat
git add notebooks docs
# 若修改了 README、脚本或其他文件，再按实际路径 git add
git commit -m "Update asset pricing notebooks and reading site"
git push origin main
```

上述网址是静态阅读入口。GitHub 上的 `.ipynb` 也可直接预览，下载整个仓库后可以保留课程的相对链接和数据依赖。

Boss题保持留空。先阅读代码动机、运行并观察，再自己填写经济解释。
