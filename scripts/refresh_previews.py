"""仅重建保存输出的 HTML 预览，不重新计算或清空 Notebook 输出。"""
from pathlib import Path
import base64
import nbformat
from nbconvert import HTMLExporter

ROOT = Path(__file__).resolve().parents[1]
qa = ROOT/'.qa'
qa.mkdir(exist_ok=True)
for path in sorted((ROOT/'notebooks').glob('*.ipynb')):
    notebook = nbformat.read(path,as_version=4)
    html,_ = HTMLExporter().from_notebook_node(notebook)
    (qa/(path.stem+'.html')).write_text(html,encoding='utf-8')
    images = 0
    for cell in notebook.cells:
        for output in cell.get('outputs',[]):
            png = output.get('data',{}).get('image/png')
            if png:
                images += 1
                (qa/f'{path.stem}_figure{images}.png').write_bytes(base64.b64decode(png))
print('Refreshed previews without altering notebook output.')
