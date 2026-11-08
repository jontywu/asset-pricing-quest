"""把当前 Notebook 的保存结果导出为 GitHub Pages；不执行、不修改源 Notebook。

运行：python scripts/build_site.py
默认发布目录为 docs/，GitHub Pages 选择 main 分支的 /docs 目录即可。
重建会覆盖 docs/ 中的对应网页，不运行旧版课程生成脚本。
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import posixpath
import re
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit

import nbformat
from nbconvert import HTMLExporter

ROOT = Path(__file__).resolve().parents[1]
CHAPTERS = [
    ("START_HERE", "起点", "课程使用说明", "了解阅读路线、数据来源与本地运行方式。"),
    ("PRELUDE_beta_to_factor_zoo", "导读", "从市场 β 到因子 zoo", "从每个变量的定义出发，连接理论、构造方法与经济解释。"),
    ("00_data_lab", "00", "搭建数据实验台", "读入数据，核对单位、日期和样本。"),
    ("01_risk_and_capm", "01", "共同风险与 CAPM", "理解分散化，以及市场 β 从哪里来。"),
    ("02_portfolio_sorts", "02", "组合排序", "观察不同公司特征对应的平均收益。"),
    ("03_capm_test", "03", "检验市场 β", "检查市场单因子留下了哪些定价误差。"),
    ("04_build_ff3", "04", "构造三因子", "把规模和 B/M 特征转化为因子收益。"),
    ("05_ff3_replication", "05", "三因子实证", "比较模型结果，并对照原论文表格。"),
    ("06_fama_macbeth", "06", "风险暴露与风险价格", "用两步回归理解横截面定价检验。"),
    ("07_build_ff5", "07", "构造五因子", "加入盈利和投资，理解构造口径。"),
    ("08_ff5_replication", "08", "五因子的压力测试", "观察更多测试资产与模型涵盖检验。"),
    ("09_out_of_sample", "09", "离开原样本", "把模型带到新的时期，检查结论的边界。"),
]

CSS = r"""
:root{--book-ink:#142b37;--book-muted:#58717b;--book-accent:#087c78;--book-line:#dce6e6;--book-bg:#f3f7f6;--book-paper:#fff;scroll-behavior:smooth}
*{box-sizing:border-box}body{margin:0;background:var(--book-bg)!important;color:var(--book-ink);font-family:Inter,-apple-system,BlinkMacSystemFont,'Segoe UI','Microsoft YaHei','PingFang SC',sans-serif!important;font-size:16px;line-height:1.8}
a{color:var(--book-accent);text-decoration:none}a:hover{text-decoration:underline}a:focus-visible,button:focus-visible,summary:focus-visible{outline:3px solid #e5a847;outline-offset:4px}
.book-top{height:66px;background:rgba(255,255,255,.97);border-bottom:1px solid var(--book-line);position:sticky;top:0;z-index:100;display:flex;align-items:center;justify-content:space-between;padding:0 32px;gap:20px}
.book-brand{display:flex;align-items:center;gap:12px;font-size:16px;font-weight:750;color:var(--book-ink);white-space:nowrap}.book-mark{font-family:Georgia,serif;background:var(--book-ink);color:#fff;font-size:25px;width:34px;height:34px;line-height:34px;text-align:center;border-radius:8px}
.book-top-links{display:flex;align-items:center;gap:22px;font-size:13px}.book-top-links a{color:var(--book-muted)}.book-progress{position:fixed;left:0;top:64px;height:2px;background:var(--book-accent);width:0;z-index:101}
.book-layout{max-width:1450px;margin:auto;display:grid;grid-template-columns:235px minmax(0,1fr);gap:32px;padding:30px 32px 70px}
.book-sidebar{position:sticky;top:96px;align-self:start;max-height:calc(100vh - 116px);overflow:auto;padding-right:10px;font-size:13px}.book-sidebar summary{font-weight:700;letter-spacing:.08em;color:var(--book-muted);padding:8px 10px 18px;cursor:pointer}.book-sidebar nav{display:flex;flex-direction:column;gap:3px}.book-sidebar nav a{display:flex;gap:10px;align-items:baseline;color:var(--book-muted);padding:9px 10px;border-radius:7px;line-height:1.65}.book-sidebar nav a:hover{background:#e9f1ef;text-decoration:none}.book-sidebar nav a[aria-current=page]{color:#086a66;background:#e2efeb;font-weight:700}.book-num{font-family:ui-monospace,Consolas,monospace;min-width:28px;font-size:12px;opacity:.8}.book-side-note{margin:22px 10px;color:var(--book-muted);font-size:12px;border-top:1px solid var(--book-line);padding-top:16px}
.book-article{background:white;border:1px solid var(--book-line);border-radius:12px;min-width:0;box-shadow:0 4px 20px #183d3510;overflow:hidden}.book-tools{display:flex;justify-content:space-between;gap:20px;align-items:center;padding:18px 36px;background:#f8fbfa;border-bottom:1px solid var(--book-line);font-size:12px;color:var(--book-muted)}.book-tools .book-actions{display:flex;gap:16px;align-items:center;flex-wrap:wrap}.book-button{border:1px solid #b7ceca;background:white;color:#34665f;border-radius:5px;font:inherit;padding:3px 10px;cursor:pointer}.book-button:hover{background:#eaf4ef}.book-body{padding:22px 24px 30px}.book-article .jp-Notebook{padding:0!important;background:transparent!important}.book-article .jp-Cell{padding:8px 0!important}.book-article .jp-InputArea{padding:0!important}.book-article .jp-InputArea-editor{border:1px solid #dfe7e7!important;border-radius:6px;background:#f6f8f8!important}.book-article .highlight{padding:12px!important;background:#f6f8f8!important}.book-article .jp-InputPrompt,.book-article .jp-OutputPrompt{display:none!important}.book-article .jp-Cell-inputWrapper,.book-article .jp-Cell-outputWrapper{margin:0!important}.book-article .jp-RenderedHTMLCommon{font-family:inherit!important;color:var(--book-ink)!important;line-height:1.9!important;font-size:15px!important;padding:0 12px!important}.book-article h1{font-size:29px!important;font-weight:750!important;line-height:1.5!important;margin-top:10px!important;letter-spacing:-.025em}.book-article h2{font-size:23px!important;line-height:1.55!important;margin-top:38px!important;padding-top:18px;border-top:1px solid var(--book-line)}.book-article h3{font-size:19px!important;line-height:1.6!important;margin-top:26px!important}.book-article p{line-height:1.9!important}.book-article h1,.book-article h2,.book-article h3,.book-article [id]{scroll-margin-top:90px}.book-article table{font-size:13px!important;line-height:1.7!important;border-collapse:collapse!important;display:block;max-width:100%;overflow-x:auto;margin:16px 0!important}.book-article td,.book-article th{text-align:left!important;padding:9px 12px!important;border-bottom:1px solid #e1e8e6!important}.book-article th{background:#edf4f1!important;font-weight:650!important}.book-article tr:nth-child(2n){background:#f8faf9!important}.book-article .jp-RenderedText pre,.book-article .highlight pre{font-size:12px!important;line-height:1.7!important;overflow-x:auto}.book-article .jp-RenderedImage img{max-width:100%!important;height:auto!important;margin:8px auto!important}.book-article .MathJax_Display,.book-article mjx-container[display=true]{max-width:100%;overflow-x:auto;overflow-y:hidden;padding:5px 0}.book-article blockquote{border-left:3px solid #72a99a!important;background:#f1f7f4;padding:12px 18px!important;margin:18px 0!important;color:#34584e!important}.book-article code{font-size:.88em!important}.book-hide-code .jp-CodeCell .jp-Cell-inputWrapper{display:none!important}.book-page-nav{display:flex;justify-content:space-between;gap:20px;padding:24px 36px;border-top:1px solid var(--book-line);font-size:14px}.book-page-nav a{max-width:48%}.book-page-nav span{display:block;color:var(--book-muted);font-size:11px;letter-spacing:.08em}.book-footer{text-align:center;color:var(--book-muted);font-size:12px;padding:10px 20px 34px}.book-footer a{color:inherit}.book-top-of-page{display:block;margin-top:16px;font-size:12px}
.home{max-width:1150px;padding:62px 32px 70px;margin:auto}.eyebrow{text-transform:uppercase;color:var(--book-accent);font-size:12px;font-weight:700;letter-spacing:.16em}.home h1{font-size:clamp(34px,5vw,54px);line-height:1.3;letter-spacing:-.04em;margin:18px 0 23px;font-weight:750}.home .lead{font-size:18px;color:var(--book-muted);max-width:730px;line-height:1.9}.home .buttons{display:flex;gap:12px;flex-wrap:wrap;margin:28px 0 40px}.home .cta{display:inline-block;padding:10px 20px;border-radius:7px;background:var(--book-accent);color:white;font-size:14px;font-weight:600}.home .cta.secondary{background:#fff;color:var(--book-ink);border:1px solid var(--book-line)}.home .intro-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:28px;border-top:1px solid var(--book-line);padding:27px 0 30px}.home .intro-grid h2{font-size:15px;margin:0 0 7px}.home .intro-grid p{font-size:14px;color:var(--book-muted);margin:0;line-height:1.85}.home .section-heading{display:flex;justify-content:space-between;align-items:baseline;gap:20px;margin:26px 0 18px}.home .section-heading h2{font-size:24px;margin:0}.home .section-heading span{font-size:13px;color:var(--book-muted)}.chapter-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:13px}.chapter-card{display:flex;gap:20px;padding:24px;background:#fff;border:1px solid var(--book-line);border-radius:9px;color:var(--book-ink);transition:transform .15s,border-color .15s}.chapter-card:hover{text-decoration:none;border-color:#79aaa0;transform:translateY(-2px)}.chapter-card .number{font:18px ui-monospace,Consolas,monospace;color:var(--book-accent);width:38px;flex-shrink:0;padding-top:4px}.chapter-card h3{font-size:17px;margin:0 0 7px;line-height:1.5}.chapter-card p{font-size:13px;color:var(--book-muted);margin:0;line-height:1.7}.home .note{border-left:3px solid #7eb7a6;background:#eaf2ee;padding:18px 22px;font-size:13px;color:#36564c;margin-top:28px}.skip-link{position:absolute;left:-9999px;top:5px}.skip-link:focus{left:12px;z-index:200;background:white;padding:8px}
@media(max-width:900px){.book-layout{grid-template-columns:minmax(0,1fr);gap:18px;padding:20px 18px 45px}.book-sidebar{position:static;max-height:none;padding:0}.book-sidebar summary{padding:10px}.book-sidebar nav{display:grid;grid-template-columns:repeat(2,minmax(0,1fr))}.book-side-note{display:none}.book-tools{padding:16px 22px}.book-body{padding:18px 14px}.book-top{padding:0 20px}.book-top-links{gap:15px}.book-article h1{font-size:26px!important}.home{padding-top:40px}}
@media(max-width:560px){.book-top{padding:0 14px;gap:8px}.book-brand{font-size:14px;gap:8px}.book-top-links{font-size:12px;gap:12px}.book-top-links .optional{display:none}.book-layout{padding:12px 8px 35px}.book-tools{padding:12px 16px;align-items:flex-start;flex-direction:column;gap:8px}.book-body{padding:14px 5px}.book-article .jp-RenderedHTMLCommon{font-size:14px!important;padding:0 10px!important}.book-article h1{font-size:23px!important}.book-article h2{font-size:20px!important}.book-article h3{font-size:17px!important}.book-page-nav{padding:20px 17px;font-size:12px}.home{padding:32px 20px 45px}.home .lead{font-size:16px}.home .intro-grid{grid-template-columns:1fr;gap:18px}.chapter-grid{grid-template-columns:1fr}.chapter-card{padding:20px}.home .section-heading{display:block}.book-sidebar nav{grid-template-columns:1fr 1fr}.book-sidebar nav a{font-size:12px;padding:7px 5px}.book-num{min-width:24px}}
@media print{.book-top,.book-sidebar,.book-tools,.book-page-nav,.book-progress,.book-footer{display:none!important}.book-layout{display:block;padding:0}.book-article{border:0;box-shadow:none}.book-body{padding:0}body{background:#fff!important}.book-article h2{break-after:avoid}}
"""

JS = r"""
document.addEventListener('DOMContentLoaded',()=>{
 const menu=document.querySelector('.book-sidebar details');
 if(menu&&window.matchMedia('(max-width:900px)').matches)menu.open=false;
 const button=document.querySelector('[data-toggle-code]');
 if(button)button.addEventListener('click',()=>{const hidden=document.body.classList.toggle('book-hide-code');button.textContent=hidden?'显示代码':'隐藏代码';button.setAttribute('aria-pressed',String(hidden));});
 const bar=document.querySelector('.book-progress');
 if(bar){const update=()=>{const span=document.documentElement.scrollHeight-innerHeight;bar.style.width=(span>0?Math.min(100,scrollY/span*100):100)+'%';};addEventListener('scroll',update,{passive:true});update();}
});
"""


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def header(repo: str) -> str:
    return f'''<a class="skip-link" href="#book-content">跳到正文</a>
<header class="book-top"><a class="book-brand" href="index.html"><span class="book-mark" aria-hidden="true">β</span>资产定价研究者</a><nav class="book-top-links" aria-label="网站导航"><a href="index.html">课程目录</a><a class="optional" href="START_HERE.html">使用说明</a><a href="{html.escape(repo)}">GitHub ↗</a></nav></header><div class="book-progress" aria-hidden="true"></div>'''


def sidebar(current: str) -> str:
    links = ''.join(f'<a href="{stem}.html"'+(' aria-current="page"' if stem == current else '')+f'><span class="book-num">{num}</span><span>{title}</span></a>' for stem, num, title, _ in CHAPTERS)
    return f'<aside class="book-sidebar"><details open><summary>阅读路线</summary><nav aria-label="课程章节">{links}</nav></details><p class="book-side-note">先理解经济问题，再观察计算结果。<br>Boss 题留给你自己完成。<a class="book-top-of-page" href="#">↑ 回到顶部</a></p></aside>'


def footer(repo: str) -> str:
    return f'<footer class="book-footer">资产定价研究者 · 基于 Notebook 保存结果的阅读版 · <a href="{repo}">代码与数据</a></footer>'


def pdf_sources() -> dict[str, str]:
    paper_map = json.loads((ROOT / 'papers/paper_map.json').read_text(encoding='utf-8'))
    sources = {'papers/' + p['pdf_file']: p['pdf_url'] for p in paper_map['papers'].values()}
    crypto = json.loads((ROOT / 'papers/crypto/manifest.json').read_text(encoding='utf-8'))
    sources.update({'papers/crypto/' + p['file']: p['url'] for p in crypto['files'] if p.get('status') == 'downloaded'})
    return sources


def web_links(page: str, repo: str, sources: dict[str, str]) -> str:
    """Only presentation links change; source notebook content remains byte-identical."""
    stems = {c[0] for c in CHAPTERS}
    # Local machine links cannot work on another reader's computer. Keep their text.
    page = re.sub(r'<a\b[^>]*\bhref=["\']file:[^"\']*["\'][^>]*>(.*?)</a>', r'\1', page, flags=re.I | re.S)

    def replace(match: re.Match) -> str:
        value = html.unescape(match.group(2))
        parts = urlsplit(value)
        if parts.scheme or parts.netloc or not parts.path:
            return match.group(0)
        path = unquote(parts.path)
        fragment = ('#' + parts.fragment) if parts.fragment else ''
        if path.endswith('.ipynb') and Path(path).stem in stems:
            target = Path(path).stem + '.html' + fragment
        else:
            relative = posixpath.normpath(posixpath.join('notebooks', path))
            if relative.startswith('../'):
                return match.group(0)
            target = sources.get(relative) or f'{repo}/blob/main/{quote(relative, safe="/")}'
            target += fragment
        return match.group(1) + html.escape(target, quote=True) + match.group(3)

    return re.sub(r'(\bhref=["\'])(.*?)(["\'])', replace, page, flags=re.I)


def render_index(repo: str) -> str:
    cards = ''.join(f'<a class="chapter-card" href="{stem}.html"><span class="number">{num}</span><div><h3>{title}</h3><p>{desc}</p></div></a>' for stem, num, title, desc in CHAPTERS)
    return f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="从市场 beta 到因子 zoo，用可复现的 Python Notebook 理解资产定价理论、因子构造与实证检验。"><title>资产定价研究者 · 从市场 β 到因子 zoo</title><link rel="stylesheet" href="assets/book.css"></head><body>{header(repo)}<main class="home" id="book-content"><div class="eyebrow">Asset Pricing Quest · Notebook Course</div><h1>从一个 β 出发，<br>读懂资产定价的实证。</h1><p class="lead">从 CAPM、Fama–French 三因子到五因子与加密资产。把变量定义、经济直觉、Python 代码和实证结果放在一起，沿着 10 个关卡逐步学习。</p><div class="buttons"><a class="cta" href="PRELUDE_beta_to_factor_zoo.html">从自解释导读开始 →</a><a class="cta secondary" href="00_data_lab.html">直接进入第 00 关</a></div><div class="intro-grid"><section><h2>先看懂变量</h2><p>B/M 是什么，SMB 如何构造，β 又衡量了什么？沿着定义与算例理解每一步。</p></section><section><h2>代码紧挨着结果</h2><p>网页保留 Notebook 的表格、图形与输出；下载项目后，可以在 VS Code 逐格重跑。</p></section><section><h2>用问题检验理解</h2><p>每关的 Boss 题保留作答空间。比较模型、检查假设，再写下自己的经济解释。</p></section></div><div class="section-heading"><h2>选择你的下一关</h2><span>1 份使用说明 · 1 本导读 · 10 个实证关卡</span></div><div class="chapter-grid">{cards}</div><div class="note">阅读版展示已保存的执行结果，不在浏览器中运行 Python。需要修改参数或完成练习时，请到 <a href="{repo}">GitHub 仓库</a>下载完整项目，并按使用说明配置环境。论文链接跳转至原始来源；数据与论文版本的差异在各章中注明。</div></main>{footer(repo)}<script src="assets/book.js"></script></body></html>'''


def build(repo: str, output: Path) -> dict:
    paths = [ROOT / 'notebooks' / (chapter[0] + '.ipynb') for chapter in CHAPTERS]
    before = {p.name: sha256(p) for p in paths}
    output.mkdir(parents=True, exist_ok=True)
    (output / 'assets').mkdir(exist_ok=True)
    (output / 'assets/book.css').write_text(CSS, encoding='utf-8')
    (output / 'assets/book.js').write_text(JS, encoding='utf-8')
    exporter = HTMLExporter(template_name='lab')
    exporter.exclude_input_prompt = True
    exporter.exclude_output_prompt = True
    sources = pdf_sources()
    records = []
    for index, (stem, num, title, _) in enumerate(CHAPTERS):
        path = paths[index]
        notebook = nbformat.read(path, as_version=4)
        nbformat.validate(notebook)
        code = [c for c in notebook.cells if c.cell_type == 'code']
        errors = [o for c in code for o in c.get('outputs', []) if o.get('output_type') == 'error']
        if errors:
            raise ValueError(f'{path.name} contains saved error outputs; inspect before publishing.')
        page, _ = exporter.from_notebook_node(notebook)
        page = web_links(page, repo, sources)
        page = re.sub(r'<html\b[^>]*>', '<html lang="zh-CN">', page, count=1)
        page = re.sub(r'<title>.*?</title>', f'<title>{html.escape(title)} · 资产定价研究者</title>', page, count=1, flags=re.S)
        page = page.replace('</head>', '<link rel="stylesheet" href="assets/book.css">\n</head>')
        raw_url = repo.replace('https://github.com/', 'https://raw.githubusercontent.com/') + f'/main/notebooks/{stem}.ipynb'
        toolbar = f'<div class="book-tools"><span>{num} · 阅读与复现</span><div class="book-actions"><button class="book-button" type="button" data-toggle-code aria-pressed="false">隐藏代码</button><a href="{repo}/blob/main/notebooks/{stem}.ipynb">查看 Notebook ↗</a><a href="{raw_url}" download="{stem}.ipynb">下载 .ipynb</a></div></div>'
        opening = header(repo) + '<div class="book-layout">' + sidebar(stem) + '<article class="book-article" id="book-content">' + toolbar + '<div class="book-body">'
        page = re.sub(r'(<body\b[^>]*>)', r'\1' + opening, page, count=1)
        previous = CHAPTERS[index - 1] if index else None
        following = CHAPTERS[index + 1] if index + 1 < len(CHAPTERS) else None
        prev_link = f'<a href="{previous[0]}.html"><span>上一章</span>← {previous[2]}</a>' if previous else '<a href="index.html"><span>回到</span>← 课程目录</a>'
        next_link = f'<a href="{following[0]}.html"><span>下一章</span>{following[2]} →</a>' if following else '<a href="index.html"><span>回到</span>课程目录 →</a>'
        closing = '</div><nav class="book-page-nav" aria-label="章节翻页">' + prev_link + next_link + '</nav></article></div>' + footer(repo) + '<script src="assets/book.js"></script></body>'
        page = page.replace('</body>', closing)
        (output / f'{stem}.html').write_text(page, encoding='utf-8')
        records.append({'notebook': path.name, 'sha256': before[path.name], 'cells': len(notebook.cells), 'code_cells': len(code), 'executed_code_cells': sum(c.get('execution_count') is not None for c in code), 'saved_error_outputs': len(errors), 'html': f'{stem}.html'})
    (output / 'index.html').write_text(render_index(repo), encoding='utf-8')
    (output / '.nojekyll').write_text('', encoding='utf-8')
    after = {p.name: sha256(p) for p in paths}
    if before != after:
        raise RuntimeError('Notebook files changed during export; rebuild from a stable saved version.')
    report = {'source': 'Current saved notebook files; not re-executed by the site builder.', 'notebooks_unchanged': True, 'repo_url': repo, 'paper_links': sources, 'notebooks': records}
    (output / 'build-manifest.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    # Check all internal web pages/assets actually exist. No live network requests needed.
    for page in output.glob('*.html'):
        text = page.read_text(encoding='utf-8')
        for match in re.finditer(r'\b(?:href|src)=["\']([^"\']+)["\']', text):
            link = html.unescape(match.group(1))
            parts = urlsplit(link)
            if parts.scheme or parts.netloc or not parts.path:
                continue
            target = output / unquote(parts.path)
            if not target.exists():
                raise ValueError(f'Broken local website link: {page.name}: {link}')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo-url', default='https://github.com/jontywu/asset-pricing-quest')
    parser.add_argument('--output', type=Path, default=ROOT / 'docs')
    args = parser.parse_args()
    report = build(args.repo_url.rstrip('/'), args.output.resolve())
    print(json.dumps({'output': str(args.output.resolve()), 'pages': len(report['notebooks']) + 1, 'notebooks_unchanged': report['notebooks_unchanged'], 'saved_errors': sum(r['saved_error_outputs'] for r in report['notebooks'])}, ensure_ascii=False))
